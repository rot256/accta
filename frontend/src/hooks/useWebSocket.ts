import { useState, useRef, useCallback } from 'react';
import { AgentMessage } from '../types';

export const useWebSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

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
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message }));
    }
  }, []);

  const onMessage = useCallback((callback: (message: AgentMessage) => void) => {
    if (wsRef.current) {
      wsRef.current.onmessage = (event) => {
        try {
          const data: AgentMessage = JSON.parse(event.data);
          callback(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
    }
  }, []);

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    sendMessage,
    onMessage,
  };
};