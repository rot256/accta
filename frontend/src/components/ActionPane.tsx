import React from 'react';

interface ActionPaneProps {
  actions: ActionItem[];
}

export interface ActionItem {
  id: string;
  name: string;
  args: string;
  timestamp: Date;
  status: 'active';
}

export const ActionPane: React.FC<ActionPaneProps> = ({ actions }) => {
  const formatActionName = (name: string) => {
    const actionMap: { [key: string]: string } = {
      'new_client': 'Create Client',
      'new_supplier': 'Create Supplier',
      'create_invoice': 'Create Invoice',
      'reconcile_transactions': 'Reconcile'
    };

    return actionMap[name] || name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatFieldLabel = (key: string): string => {
    const labelMap: { [key: string]: string } = {
      'name': 'Name',
      'email': 'Email',
      'phone': 'Phone',
      'address': 'Address',
      'country': 'Country',
      'country_code': 'Country',
      'vat_number': 'VAT Number',
      'client_id': 'Client',
      'supplier_id': 'Supplier',
      'amount': 'Amount',
      'currency': 'Currency',
      'description': 'Description',
      'due_date': 'Due Date',
      'bank_txs': 'Bank Transactions',
      'receipts': 'Receipts'
    };
    return labelMap[key] || key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
  };

  const renderArgValue = (key: string, value: any): React.ReactNode => {
    if (value === null || value === undefined) return <span className="arg-null">Not specified</span>;

    // Handle ID fields specially
    if (key.endsWith('_id') || key === 'client' || key === 'supplier') {
      return <span className="arg-id">{String(value).substring(0, 8)}...</span>;
    }

    // Handle arrays
    if (Array.isArray(value)) {
      if (value.length === 0) return <span className="arg-empty">None</span>;
      return (
        <div className="arg-array">
          {value.map((item, index) => (
            <span key={index} className="arg-array-item">
              {String(item).substring(0, 8)}...
              {index < value.length - 1 ? ', ' : ''}
            </span>
          ))}
        </div>
      );
    }

    // Handle dates
    if (key.includes('date')) {
      return <span className="arg-date">{String(value)}</span>;
    }

    // Handle amounts
    if (key === 'amount') {
      return <span className="arg-amount">{value}</span>;
    }

    // Handle regular strings/numbers
    if (typeof value === 'object') {
      return <pre className="arg-object">{JSON.stringify(value, null, 2)}</pre>;
    }

    return <span className="arg-text">{String(value)}</span>;
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
            <div key={action.id} className="action-item">
              <div className="action-item-header">
                <span className="action-name">{formatActionName(action.name)}</span>
              </div>

              <div className="action-arguments">
                {typeof parsedArgs === 'object' && !Array.isArray(parsedArgs) ? (
                  <div className="args-list">
                    {Object.entries(parsedArgs).map(([key, value]) => (
                      <div key={key} className="arg-item">
                        <div className="arg-label">{formatFieldLabel(key)}:</div>
                        <div className="arg-value">{renderArgValue(key, value)}</div>
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