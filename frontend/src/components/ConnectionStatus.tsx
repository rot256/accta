import React from 'react';

interface ConnectionStatusProps {
  isConnected: boolean;
  isConnecting: boolean;
  onConnect: () => void;
  onDisconnect: () => void;
}

export const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  isConnected,
  isConnecting,
  onConnect,
  onDisconnect,
}) => {
  return (
    <div className="connection-status">
      <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}>
        {isConnecting ? '🔄' : isConnected ? '🟢' : '🔴'}
        <span>
          {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
      <button onClick={isConnected ? onDisconnect : onConnect} disabled={isConnecting}>
        {isConnected ? 'Disconnect' : 'Connect'}
      </button>
    </div>
  );
};