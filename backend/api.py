import asyncio
import json
import os
import logging
import uuid
import datetime
from pathlib import Path
from typing import Dict, Any
from pydantic.json import pydantic_encoder
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner
from agent import create_agent
from agents import SQLiteSession
from messages import (
    BaseMessage,
    SessionInitMessage,
    SessionClearedMessage,
    ConversationHistoryMessage,
    ErrorMessage,
    StartMessage,
    CompleteMessage,
    ToolCalledMessage,
    ToolOutputMessage,
    TextDeltaMessage,
    TextDoneMessage
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add TRACE level for very verbose logging
TRACE = 5
logging.addLevelName(TRACE, "TRACE")
def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE):
        self._log(TRACE, message, args, **kwargs)
logging.Logger.trace = trace

app = FastAPI(title="Accta Agent API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the frontend build directory
current_dir = Path(__file__).parent
frontend_build_path = current_dir.parent / "frontend" / "build"

class ConnectionManager:
    def __init__(self):
        self.websocket_sessions: Dict[WebSocket, SQLiteSession] = {}
        self.websocket_agents: Dict[WebSocket, Any] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        session_id = str(uuid.uuid4())
        session = SQLiteSession(session_id=session_id, db_path=":memory:")
        agent = create_agent()  # Create fresh agent with new state per connection
        self.websocket_sessions[websocket] = session
        self.websocket_agents[websocket] = agent
        return session_id, session

    def disconnect(self, websocket: WebSocket):
        self.websocket_sessions.pop(websocket, None)
        self.websocket_agents.pop(websocket, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message(self, message: BaseMessage, websocket: WebSocket):
        """Send a Pydantic dataclass message as JSON to the websocket."""
        await websocket.send_text(json.dumps(message, default=pydantic_encoder))

    def get_session(self, websocket: WebSocket) -> SQLiteSession:
        return self.websocket_sessions.get(websocket)

    def get_agent(self, websocket: WebSocket):
        return self.websocket_agents.get(websocket)

manager = ConnectionManager()

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    logger.debug(f"WebSocket connection from {websocket.client}")
    session_id, session = await manager.connect(websocket)
    logger.trace(f"WebSocket connected with session ID: {session_id}")

    # Send session ID to client
    await manager.send_message(
        SessionInitMessage(session_id=session_id),
        websocket
    )

    try:
        while True:
            logger.trace("Waiting for message...")
            data = await websocket.receive_text()
            logger.trace(f"Received data: {data}")

            try:
                message_data = json.loads(data)
                logger.trace(f"Parsed message: {message_data}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await manager.send_message(
                    ErrorMessage(message="Invalid JSON format"),
                    websocket
                )
                continue

            # Handle session management commands
            if message_data.get("type") == "session_command":
                command = message_data.get("command")
                if command == "clear_session":
                    await session.clear_session()
                    # Create new agent with fresh state
                    manager.websocket_agents[websocket] = create_agent()
                    await manager.send_message(
                        SessionClearedMessage(session_id=session_id),
                        websocket
                    )
                    continue
                elif command == "get_conversation":
                    conversation_history = await session.get_items()
                    await manager.send_message(
                        ConversationHistoryMessage(history=conversation_history),
                        websocket
                    )
                    continue

            user_input = message_data.get("message", "")
            logger.trace(f"User input: '{user_input}'")

            if not user_input:
                logger.trace("No message provided")
                await manager.send_message(
                    ErrorMessage(message="No message provided"),
                    websocket
                )
                continue

            logger.trace("Starting agent processing...")
            agent = manager.get_agent(websocket)
            result = Runner.run_streamed(
                agent,
                input=user_input,
                session=session,
            )

            await manager.send_message(
                StartMessage(),
                websocket
            )
            logger.trace("Sent start message")

            logger.trace("Starting event stream...")
            async for event in result.stream_events():
                if event.type == 'run_item_stream_event':
                    logger.trace(f"Received event: {event.type} - {event.name}")
                    if event.name == 'tool_called':
                        tool_name = event.item.raw_item.name
                        tool_args = event.item.raw_item.arguments
                        logger.debug(f"Tool called: {tool_name}")
                        logger.trace(f"Tool args: {tool_args}")

                        await manager.send_message(
                            ToolCalledMessage(
                                tool_name=tool_name,
                                tool_args=tool_args
                            ),
                            websocket
                        )

                    elif event.name == 'tool_output':
                        output = event.item.output
                        logger.trace(f"Tool output: {output}")

                        # Use Pydantic's built-in encoder for clean serialization
                        await manager.send_message(
                            ToolOutputMessage(output=output),
                            websocket
                        )

                elif event.type == 'raw_response_event':
                    if event.data.type == 'response.output_text.delta':
                        logger.trace(f"Text delta: {event.data.delta}")
                        await manager.send_message(
                            TextDeltaMessage(delta=event.data.delta),
                            websocket
                        )

                    elif event.data.type == 'response.output_text.done':
                        logger.trace("Text done")
                        await manager.send_message(
                            TextDoneMessage(),
                            websocket
                        )

            logger.trace("Event stream completed")
            await manager.send_message(
                CompleteMessage(),
                websocket
            )
            logger.trace("Sent complete message")

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# Mount static files for frontend (this must come after all API routes)
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")
