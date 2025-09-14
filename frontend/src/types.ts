export interface AgentMessage {
  type: 'start' | 'tool_called' | 'tool_output' | 'text_delta' | 'text_done' | 'complete' | 'error' | 'action_created' | 'action_removed' | 'action_clear';
  message?: string;
  tool_name?: string;
  tool_args?: string;
  output?: string | object;
  delta?: string;
  // Action-related fields
  action_id?: string;
  action_type?: string;
  action_args?: any;
  timestamp?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'tool';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  toolCalls?: ToolCall[];
  toolCall?: ToolCall; // For individual tool call messages
}

export interface ToolCall {
  id?: string;
  name: string;
  args: string;
  output?: string;
}