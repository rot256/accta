import React from 'react';

export const LoadingMessage: React.FC = () => {
  return (
    <div className="loading-message">
      <div className="loading-content">
        <span>Assistant is thinking</span>
        <span className="loading-dots"></span>
      </div>
    </div>
  );
};