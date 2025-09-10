import React, { useState } from 'react';
import { ChatMessage as ChatMessageType, ToolCall } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  if (message.role === 'tool') {
    return <ToolMessage message={message} />;
  }
  
  return (
    <div className={`message ${message.role}`}>
      <div className="message-content">
        {message.content}
        {message.isStreaming && <span className="cursor">|</span>}
      </div>
    </div>
  );
};

interface ToolMessageProps {
  message: ChatMessageType;
}

const ToolMessage: React.FC<ToolMessageProps> = ({ message }) => {
  if (!message.toolCall) return null;
  
  return (
    <div className="message tool">
      <ToolCallDisplay tool={message.toolCall} />
    </div>
  );
};

interface ToolCallDisplayProps {
  tool: ToolCall;
}

const ToolCallDisplay: React.FC<ToolCallDisplayProps> = ({ tool }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  return (
    <div className="tool-call">
      <div className="tool-header">🔧 Called {tool.name}</div>
      {tool.args && tool.args !== '{}' && (
        <div className="tool-args">Arguments: {tool.args}</div>
      )}
      {tool.output && (
        <div className="tool-output">
          <button 
            className="tool-output-toggle"
            onClick={() => setIsExpanded(!isExpanded)}
          >
            {isExpanded ? '▼' : '▶'} Result
          </button>
          {isExpanded && (
            <div className="tool-output-content">{tool.output}</div>
          )}
        </div>
      )}
    </div>
  );
};