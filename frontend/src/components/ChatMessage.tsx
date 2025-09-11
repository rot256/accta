import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChatMessage as ChatMessageType, ToolCall } from '../types';

// Global state to track expanded tools across re-renders
const expandedTools = new Set<string>();

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
        {message.role === 'assistant' ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        ) : (
          message.content
        )}
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
  const toolKey = `${tool.name}-${tool.id || tool.args}`;
  const [forceUpdate, setForceUpdate] = useState(0);
  const isExpanded = expandedTools.has(toolKey);
  
  const toggleExpanded = () => {
    const currentlyExpanded = expandedTools.has(toolKey);
    if (currentlyExpanded) {
      expandedTools.delete(toolKey);
    } else {
      expandedTools.add(toolKey);
    }
    setForceUpdate(prev => prev + 1);
  };
  
  return (
    <div className={`tool-call-container ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="tool-header">
        <span className="tool-icon">⚙</span> {tool.name}
        {tool.output && (
          <button 
            type="button"
            className="tool-output-toggle"
            onClick={toggleExpanded}
          >
            {isExpanded ? '▼' : '▶'} Result
          </button>
        )}
      </div>
      
      {isExpanded && (
        <div className="tool-expanded-content">
          {tool.args && tool.args !== '{}' && (
            <div className="tool-args">Arguments: {tool.args}</div>
          )}
          {tool.output && (
            <div className="tool-output">{tool.output}</div>
          )}
        </div>
      )}
    </div>
  );
};