export interface AgentMessage {
  type: 'start' | 'tool_called' | 'tool_output' | 'text_delta' | 'text_done' | 'complete' | 'error';
  message?: string;
  tool_name?: string;
  tool_args?: string;
  output?: string;
  delta?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ToolCall {
  name: string;
  args: string;
  output?: string;
}