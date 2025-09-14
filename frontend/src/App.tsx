import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { LoadingMessage } from './components/LoadingMessage';
import { ActionPane, ActionItem } from './components/ActionPane';
import { ChatMessage as ChatMessageType, AgentMessage } from './types';
import './App.css';

function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [actions, setActions] = useState<ActionItem[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const handleMessage = useCallback((data: AgentMessage) => {
    
    switch (data.type) {
      case 'start':
        setIsProcessing(true);
        break;
        
      case 'tool_called':
        if (data.tool_name) {
          // Create a separate tool call message
          const toolCallId = `tool-${Date.now()}-${Math.random()}`;
          const toolCallMessage: ChatMessageType = {
            id: toolCallId,
            role: 'tool',
            content: `Called ${data.tool_name}`,
            timestamp: new Date(),
            toolCall: {
              id: toolCallId,
              name: data.tool_name,
              args: data.tool_args || ''
            }
          };

          setMessages(prev => [...prev, toolCallMessage]);
        }
        break;
        
      case 'tool_output':
        if (data.output) {
          const convertedOutput = typeof data.output === 'string' ? data.output : JSON.stringify(data.output, null, 2);
          // Update the last tool message with the output
          setMessages(prev => {
            // Find the first tool message that doesn't have output yet
            const firstPendingToolIndex = prev.findIndex(m => 
              m.role === 'tool' && m.toolCall && !m.toolCall.output
            );
            
            if (firstPendingToolIndex !== -1) {
              const toolMessage = prev[firstPendingToolIndex];
              const updatedToolMessage = {
                ...toolMessage,
                toolCall: toolMessage.toolCall ? 
                  { 
                    ...toolMessage.toolCall, 
                    output: convertedOutput
                  } : 
                  undefined
              };
              return [
                ...prev.slice(0, firstPendingToolIndex),
                updatedToolMessage,
                ...prev.slice(firstPendingToolIndex + 1)
              ];
            }
            return prev;
          });
        }
        break;
        
      case 'text_delta':
        if (data.delta) {
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.role === 'assistant' && lastMessage.isStreaming) {
              return [
                ...prev.slice(0, -1),
                { ...lastMessage, content: lastMessage.content + data.delta }
              ];
            } else {
              return [
                ...prev,
                {
                  id: Date.now().toString(),
                  role: 'assistant',
                  content: data.delta || '',
                  timestamp: new Date(),
                  isStreaming: true
                }
              ];
            }
          });
        }
        break;
        
      case 'text_done':
        setMessages(prev => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.isStreaming) {
            return [
              ...prev.slice(0, -1),
              { ...lastMessage, isStreaming: false }
            ];
          }
          return prev;
        });
        break;
        
      case 'complete':
        setIsProcessing(false);
        break;

      case 'action_created':
        if (data.action_id && data.action_type && data.timestamp) {
          const newAction: ActionItem = {
            id: data.action_id,
            name: data.action_type,
            args: JSON.stringify(data.action_args || {}),
            timestamp: new Date(data.timestamp),
            status: 'active'
          };
          setActions(prev => [...prev, newAction]);
        }
        break;

      case 'action_removed':
        if (data.action_id) {
          setActions(prev => prev.map(action =>
            action.id === data.action_id ? { ...action, status: 'removed' } : action
          ));
        }
        break;

      case 'action_clear':
        setActions([]);
        break;

      case 'error':
        setIsProcessing(false);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now().toString(),
            role: 'assistant',
            content: `Error: ${data.message || 'Unknown error occurred'}`,
            timestamp: new Date()
          }
        ]);
        break;
    }
  }, []);

  const { isConnected, connect, sendMessage } = useWebSocket(handleMessage);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Auto-connect when component mounts
    connect();
  }, [connect]);

  const handleSendMessage = (message: string) => {
    if (!isConnected) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    sendMessage(message);
  };


  return (
    <div className="App">
      <div className="app-container">
        {actions.length > 0 && <ActionPane actions={actions} />}

        <main className="chat-container">
          <div className="messages">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
              />
            ))}
            {isProcessing && messages.length > 0 && !messages[messages.length - 1]?.isStreaming && (
              <LoadingMessage />
            )}
            <div ref={messagesEndRef} />
          </div>

          <ChatInput
            onSendMessage={handleSendMessage}
            disabled={!isConnected || isProcessing}
          />
        </main>
      </div>
    </div>
  );
}

export default App;