import asyncio
import json
import os
import logging
import uuid
from pathlib import Path
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner
from agent import agent
from agents import SQLiteSession

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        session_id = str(uuid.uuid4())
        session = SQLiteSession(session_id=session_id, db_path=":memory:")
        self.websocket_sessions[websocket] = session
        return session_id, session

    def disconnect(self, websocket: WebSocket):
        self.websocket_sessions.pop(websocket, None)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    def get_session(self, websocket: WebSocket) -> SQLiteSession:
        return self.websocket_sessions.get(websocket)

manager = ConnectionManager()

@app.websocket("/ws/agent")
async def websocket_endpoint(websocket: WebSocket):
    logger.debug(f"WebSocket connection attempt from {websocket.client}")
    session_id, session = await manager.connect(websocket)
    logger.debug(f"WebSocket connected successfully with session ID: {session_id}")
    
    # Send session ID to client
    await manager.send_personal_message(
        json.dumps({"type": "session_init", "session_id": session_id}),
        websocket
    )
    
    try:
        while True:
            logger.debug("Waiting for message...")
            data = await websocket.receive_text()
            logger.debug(f"Received data: {data}")
            
            try:
                message_data = json.loads(data)
                logger.debug(f"Parsed message: {message_data}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket
                )
                continue
            
            # Handle session management commands
            if message_data.get("type") == "session_command":
                command = message_data.get("command")
                if command == "clear_session":
                    await session.clear_session()
                    await manager.send_personal_message(
                        json.dumps({"type": "session_cleared", "session_id": session_id}),
                        websocket
                    )
                    continue
                elif command == "get_conversation":
                    conversation_history = await session.get_items()
                    await manager.send_personal_message(
                        json.dumps({"type": "conversation_history", "history": conversation_history}),
                        websocket
                    )
                    continue
                
            user_input = message_data.get("message", "")
            logger.debug(f"User input: '{user_input}'")
            
            if not user_input:
                logger.debug("No message provided")
                await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "No message provided"}),
                    websocket
                )
                continue
            
            logger.debug("Starting agent processing...")
            result = Runner.run_streamed(
                agent, 
                input=user_input,
                session=session,
            )
            
            await manager.send_personal_message(
                json.dumps({"type": "start", "message": "Agent is processing..."}),
                websocket
            )
            logger.debug("Sent start message")
            
            logger.debug("Starting event stream...")
            async for event in result.stream_events():
                logger.debug(f"Received event: {event.type} - {getattr(event, 'name', 'N/A')}")
                
                if event.type == 'run_item_stream_event':
                    if event.name == 'tool_called':
                        tool_name = event.item.raw_item.name
                        tool_args = event.item.raw_item.arguments
                        logger.debug(f"Tool called: {tool_name} with args: {tool_args}")
                        
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "tool_called",
                                "tool_name": tool_name,
                                "tool_args": tool_args
                            }),
                            websocket
                        )
                        
                    elif event.name == 'tool_output':
                        output = event.item.output
                        logger.debug(f"Tool output: {output}")
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "tool_output",
                                "output": output
                            }),
                            websocket
                        )
                        
                elif event.type == 'raw_response_event':
                    if event.data.type == 'response.output_text.delta':
                        logger.debug(f"Text delta: {event.data.delta}")
                        await manager.send_personal_message(
                            json.dumps({
                                "type": "text_delta",
                                "delta": event.data.delta
                            }),
                            websocket
                        )
                        
                    elif event.data.type == 'response.output_text.done':
                        logger.debug("Text done")
                        await manager.send_personal_message(
                            json.dumps({"type": "text_done"}),
                            websocket
                        )
            
            logger.debug("Event stream completed")
            await manager.send_personal_message(
                json.dumps({"type": "complete"}),
                websocket
            )
            logger.debug("Sent complete message")
                        
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/api/health")
async def health():
    return {"status": "healthy"}

# Mount static files for frontend (this must come after all API routes)
if frontend_build_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_build_path), html=True), name="frontend")