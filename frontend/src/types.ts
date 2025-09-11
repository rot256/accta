export interface AgentMessage {
  type: 'start' | 'tool_called' | 'tool_output' | 'text_delta' | 'text_done' | 'complete' | 'error';
  message?: string;
  tool_name?: string;
  tool_args?: string;
  output?: string | object;
  delta?: string;
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