import { useState, useRef, useCallback, useEffect } from 'react';
import { AgentMessage } from '../types';

export const useWebSocket = (onMessage?: (message: AgentMessage) => void) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messageHandlerRef = useRef<((message: AgentMessage) => void) | undefined>(onMessage);

  // Update the message handler ref when the callback changes
  useEffect(() => {
    messageHandlerRef.current = onMessage;
  }, [onMessage]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setIsConnecting(true);
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/ws/agent`);
    
    ws.onopen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      console.log('WebSocket connected');
    };

    ws.onclose = () => {
      setIsConnected(false);
      setIsConnecting(false);
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      setIsConnecting(false);
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      console.log('Raw WebSocket message received:', event.data);
      try {
        const data: AgentMessage = JSON.parse(event.data);
        console.log('Parsed message:', data);
        if (messageHandlerRef.current) {
          messageHandlerRef.current(data);
        } else {
          console.warn('No message handler set');
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    wsRef.current = ws;
  }, []);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const sendMessage = useCallback((message: string) => {
    console.log('sendMessage called with:', message);
    console.log('WebSocket state:', wsRef.current?.readyState);
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = JSON.stringify({ message });
      console.log('Sending payload:', payload);
      wsRef.current.send(payload);
      console.log('Message sent successfully');
    } else {
      console.error('WebSocket not open. State:', wsRef.current?.readyState);
    }
  }, []);

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    sendMessage,
  };
};