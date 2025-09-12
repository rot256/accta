"""Pydantic dataclasses for WebSocket messages"""
from typing import Any, List
from pydantic.dataclasses import dataclass
from dataclasses import field


# Base message class
@dataclass
class BaseMessage:
    pass


# Session management messages
@dataclass
class SessionInitMessage(BaseMessage):
    session_id: str
    type: str = field(default="session_init", init=False)


@dataclass
class SessionClearedMessage(BaseMessage):
    session_id: str
    type: str = field(default="session_cleared", init=False)


@dataclass
class ConversationHistoryMessage(BaseMessage):
    history: List[Any]
    type: str = field(default="conversation_history", init=False)


# Error messages
@dataclass
class ErrorMessage(BaseMessage):
    message: str
    type: str = field(default="error", init=False)


# Agent processing messages
@dataclass
class StartMessage(BaseMessage):
    message: str = "Agent is processing..."
    type: str = field(default="start", init=False)


@dataclass
class CompleteMessage(BaseMessage):
    type: str = field(default="complete", init=False)


# Tool-related messages
@dataclass
class ToolCalledMessage(BaseMessage):
    tool_name: str
    tool_args: Any
    type: str = field(default="tool_called", init=False)


@dataclass
class ToolOutputMessage(BaseMessage):
    output: Any
    type: str = field(default="tool_output", init=False)


# Text streaming messages
@dataclass
class TextDeltaMessage(BaseMessage):
    delta: str
    type: str = field(default="text_delta", init=False)


@dataclass
class TextDoneMessage(BaseMessage):
    type: str = field(default="text_done", init=False)