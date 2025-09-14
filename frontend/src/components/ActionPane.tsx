import React from 'react';

interface ActionPaneProps {
  actions: ActionItem[];
}

export interface ActionItem {
  id: string;
  name: string;
  args: string;
  timestamp: Date;
  status: 'active' | 'removed';
}

export const ActionPane: React.FC<ActionPaneProps> = ({ actions }) => {
  const formatActionName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const renderArgValue = (value: any): string => {
    if (value === null || value === undefined) return 'null';
    if (typeof value === 'object') {
      if (Array.isArray(value)) {
        return `[${value.length} items]`;
      }
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  const parseArgs = (args: string) => {
    try {
      return JSON.parse(args);
    } catch {
      return args;
    }
  };

  return (
    <div className="action-pane">
      <div className="action-pane-header">
        <h3>Actions</h3>
      </div>

      <div className="action-pane-list">
        {actions.map((action) => {
          const parsedArgs = parseArgs(action.args);

          return (
            <div key={action.id} className={`action-item ${action.status}`}>
              <div className="action-item-header">
                <span className="action-name">{formatActionName(action.name)}</span>
              </div>

              {action.status === 'removed' && (
                <div className="action-removed-badge">REMOVED</div>
              )}

              <div className="action-arguments">
                {typeof parsedArgs === 'object' && !Array.isArray(parsedArgs) ? (
                  <div className="args-list">
                    {Object.entries(parsedArgs).map(([key, value]) => (
                      <div key={key} className="arg-item">
                        <span className="arg-key">{key}:</span>
                        <span className="arg-value">{renderArgValue(value)}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="args-raw">
                    <pre>{typeof parsedArgs === 'string' ? parsedArgs : JSON.stringify(parsedArgs, null, 2)}</pre>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};