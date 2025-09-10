import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { LoadingMessage } from './components/LoadingMessage';
import { ChatMessage as ChatMessageType, ToolCall, AgentMessage } from './types';
import './App.css';

function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [currentToolCalls, setCurrentToolCalls] = useState<ToolCall[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const handleMessage = useCallback((data: AgentMessage) => {
    console.log('Received message:', data);
    
    switch (data.type) {
      case 'start':
        setIsProcessing(true);
        setCurrentToolCalls([]);
        break;
        
      case 'tool_called':
        if (data.tool_name) {
          setCurrentToolCalls(prev => [
            ...prev,
            { name: data.tool_name!, args: data.tool_args || '' }
          ]);
        }
        break;
        
      case 'tool_output':
        if (data.output) {
          setCurrentToolCalls(prev => 
            prev.map((tool, index) => 
              index === prev.length - 1 ? { ...tool, output: data.output } : tool
            )
          );
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

  const { isConnected, isConnecting, connect, sendMessage } = useWebSocket(handleMessage);

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

  const getToolCallsForMessage = (messageIndex: number): ToolCall[] => {
    if (messageIndex === messages.length - 1 && isProcessing) {
      return currentToolCalls;
    }
    return [];
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Accta Agent Chat</h1>
      </header>
      
      <main className="chat-container">
        <div className="messages">
          {messages.map((message, index) => (
            <ChatMessage
              key={message.id}
              message={message}
              toolCalls={getToolCallsForMessage(index)}
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
  );
}

export default App;