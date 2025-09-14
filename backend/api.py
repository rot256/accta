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
    TextDoneMessage,
    ActionCreatedMessage,
    ActionRemovedMessage,
    ActionClearMessage,
    ActionsStateMessage
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
        self.websocket_actions: Dict[WebSocket, List[Dict]] = {}  # Track actions per connection

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        session_id = str(uuid.uuid4())
        session = SQLiteSession(session_id=session_id, db_path=":memory:")

        # Create action callback for this websocket
        def action_callback(event_type: str, data: Dict):
            asyncio.create_task(self._handle_action_event(websocket, event_type, data))

        agent = create_agent(action_callback)  # Create fresh agent with action callback
        self.websocket_sessions[websocket] = session
        self.websocket_agents[websocket] = agent
        self.websocket_actions[websocket] = []
        logger.info(f"WebSocket connected: {websocket.client} (session: {session_id[:8]}..., total connections: {len(self.websocket_sessions)})")
        return session_id, session

    def disconnect(self, websocket: WebSocket):
        session = self.websocket_sessions.pop(websocket, None)
        self.websocket_agents.pop(websocket, None)
        self.websocket_actions.pop(websocket, None)
        session_id = session.session_id if session else "unknown"
        logger.info(f"WebSocket disconnected: {websocket.client} (session: {session_id[:8] if session else 'unknown'}..., remaining connections: {len(self.websocket_sessions)})")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message(self, message: BaseMessage, websocket: WebSocket):
        """Send a Pydantic dataclass message as JSON to the websocket."""
        await websocket.send_text(json.dumps(message, default=pydantic_encoder))

    def get_session(self, websocket: WebSocket) -> SQLiteSession:
        return self.websocket_sessions.get(websocket)

    def get_agent(self, websocket: WebSocket):
        return self.websocket_agents.get(websocket)

    async def _handle_action_event(self, websocket: WebSocket, event_type: str, data: Dict):
        """Handle action events from the backend and send to frontend"""
        try:
            if event_type == 'action_created':
                # Add to local actions list
                if websocket in self.websocket_actions:
                    self.websocket_actions[websocket].append({
                        'id': data['action_id'],
                        'type': data['action_type'],
                        'args': data['action_args'],
                        'timestamp': data['timestamp'],
                        'status': 'active'
                    })

                # Send to frontend
                await self.send_message(
                    ActionCreatedMessage(
                        action_id=data['action_id'],
                        action_type=data['action_type'],
                        action_args=data['action_args'],
                        timestamp=data['timestamp']
                    ),
                    websocket
                )

            elif event_type == 'action_removed':
                # Update local actions list
                if websocket in self.websocket_actions:
                    for action in self.websocket_actions[websocket]:
                        if action['id'] == data['action_id']:
                            action['status'] = 'removed'
                            break

                # Send to frontend
                await self.send_message(
                    ActionRemovedMessage(action_id=data['action_id']),
                    websocket
                )

            elif event_type == 'action_clear':
                # Clear all actions
                if websocket in self.websocket_actions:
                    self.websocket_actions[websocket] = []

                # Send to frontend
                await self.send_message(
                    ActionClearMessage(),
                    websocket
                )

        except Exception as e:
            logger.error(f"Error handling action event: {e}")

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
                    # Create action callback for this websocket
                    def action_callback(event_type: str, data: Dict):
                        asyncio.create_task(manager._handle_action_event(websocket, event_type, data))

                    # Create new agent with fresh state
                    manager.websocket_agents[websocket] = create_agent(action_callback)
                    manager.websocket_actions[websocket] = []  # Clear actions
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
        logger.debug(f"WebSocket disconnected unexpectedly: {websocket.client}")
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# Mount static files for frontend (this must come after all API routes)
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")
