import React from 'react';
import { ChatMessage as ChatMessageType, ToolCall } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
  toolCalls?: ToolCall[];
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message, toolCalls }) => {
  return (
    <div className={`message ${message.role}`}>
      <div className="message-header">
        <span className="role">{message.role === 'user' ? 'You' : 'Assistant'}</span>
        <span className="timestamp">{message.timestamp.toLocaleTimeString()}</span>
      </div>
      <div className="message-content">
        {message.content}
        {message.isStreaming && <span className="cursor">|</span>}
      </div>
      {toolCalls && toolCalls.length > 0 && (
        <div className="tool-calls">
          {toolCalls.map((tool, index) => (
            <div key={index} className="tool-call">
              <div className="tool-header">🔧 {tool.name}</div>
              {tool.args && tool.args !== '{}' && (
                <div className="tool-args">Args: {tool.args}</div>
              )}
              {tool.output && (
                <div className="tool-output">Output: {tool.output}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};