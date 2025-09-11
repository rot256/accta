import { useState, useRef, useCallback, useEffect } from "react";
import { AgentMessage } from "../types";

export const useWebSocket = (onMessage?: (message: AgentMessage) => void) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const messageHandlerRef = useRef<
    ((message: AgentMessage) => void) | undefined
  >(onMessage);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);
  const reconnectAttemptsRef = useRef(0);

  // Update the message handler ref when the callback changes
  useEffect(() => {
    messageHandlerRef.current = onMessage;
  }, [onMessage]);

  const clearReconnectTimeout = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const scheduleReconnect = useCallback(() => {
    if (!shouldReconnectRef.current) return;

    clearReconnectTimeout();

    // Exponential backoff: 1s, 2s, 4s, 8s, max 30s
    const delay = 10000;
    reconnectAttemptsRef.current++;


    reconnectTimeoutRef.current = setTimeout(() => {
      if (
        shouldReconnectRef.current &&
        (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED)
      ) {
        connect();
      }
    }, delay);
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    clearReconnectTimeout();
    setIsConnecting(true);

    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const ws = new WebSocket(`${protocol}//${host}/ws/agent`);

    ws.onopen = () => {
      setIsConnected(true);
      setIsConnecting(false);
      reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection
    };

    ws.onclose = () => {
      setIsConnected(false);
      setIsConnecting(false);

      // Schedule reconnect if we should reconnect
      if (shouldReconnectRef.current) {
        scheduleReconnect();
      }
    };

    ws.onerror = (error) => {
      setIsConnecting(false);
      console.error("WebSocket error:", error);
    };

    ws.onmessage = (event) => {
      try {
        const data: AgentMessage = JSON.parse(event.data);
        if (messageHandlerRef.current) {
          messageHandlerRef.current(data);
        }
      } catch (error) {
        console.error("Failed to parse WebSocket message:", error);
      }
    };

    wsRef.current = ws;
  }, [clearReconnectTimeout, scheduleReconnect]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false; // Stop auto-reconnection
    clearReconnectTimeout();

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setIsConnected(false);
    }
  }, [clearReconnectTimeout]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      shouldReconnectRef.current = false;
      clearReconnectTimeout();
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [clearReconnectTimeout]);

  const sendMessage = useCallback((message: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const payload = JSON.stringify({ message });
      wsRef.current.send(payload);
    } else {
      console.error("WebSocket not open. State:", wsRef.current?.readyState);
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
