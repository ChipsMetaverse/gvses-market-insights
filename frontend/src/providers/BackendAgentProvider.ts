/**
 * Backend Agent Provider
 * Connects to the backend OpenAI agent orchestrator for intelligent
 * query processing with function calling and tool execution.
 */

import { AbstractBaseProvider } from './BaseProvider';
import {
  ProviderConfig,
  Message,
  ProviderCapabilities,
  ChatProvider,
} from './types';
import { normalizeChartCommandPayload } from '../utils/chartCommandUtils';

const generateRequestId = (): string => {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID();
    }
  } catch (err) {
    // Ignore and fall back to manual generation
  }
  return `req_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
};

interface AgentResponse {
  text: string;
  tools_used: string[];
  data: Record<string, any>;
  timestamp: string;
  model: string;
  cached: boolean;
  session_id?: string;
  request_id?: string;
}

interface StreamChunk {
  type: 'metadata' | 'content' | 'tool_start' | 'tool_result' | 'structured' | 'done' | 'error';
  text?: string;
  session_id?: string;
  model?: string;
  // Chart commands (in 'done' event) - Phase 2: Streaming chart command support
  chart_commands?: string[];
  chart_commands_structured?: Array<{
    type: string;
    payload: Record<string, any>;
    description?: string | null;
    legacy?: string | null;
  }>;
  // Tool data
  tool?: string;
  arguments?: Record<string, any>;
  data?: Record<string, any>;
  tools_used?: string[];
  request_id?: string;
  // Error message
  message?: string;
}

export class BackendAgentProvider extends AbstractBaseProvider implements ChatProvider {
  private conversationHistory: Message[] = [];
  private sessionId: string;
  private abortController: AbortController | null = null;
  private eventSource: EventSource | null = null;

  constructor(config: ProviderConfig) {
    const capabilities = config.capabilities ?? BackendAgentProvider.getDefaultCapabilities();
    super({
      ...config,
      type: config.type ?? 'custom',
      name: config.name ?? 'Backend Agent',
      capabilities,
    });
    this._capabilities = capabilities;
    this.sessionId = this.generateSessionId();
  }

  static getDefaultCapabilities(): ProviderCapabilities {
    return {
      voiceConversation: false, // Text only, but can be combined with voice
      textChat: true,
      textToSpeech: false,
      speechToText: false,
      streaming: true,
      tools: true, // Supports function calling
    };
  }

  async initialize(config: ProviderConfig): Promise<void> {
    this._config = config;
    this._connectionState = 'disconnected';
    this._isInitialized = true;
    
    // Backend agent doesn't need explicit connection
    // It's ready as soon as the backend is available
    await this.checkBackendHealth();
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected') {
      return;
    }

    this._connectionState = 'connecting';
    this.emit('connection', { state: 'connecting' });

    try {
      // Check if backend agent is healthy
      await this.checkBackendHealth();
      
      this._connectionState = 'connected';
      this.emit('connection', { state: 'connected' });
    } catch (error) {
      this._connectionState = 'error';
      this.emit('connection', { state: 'error' });
      this.emit('error', { error: error instanceof Error ? error.message : 'Connection failed' });
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this._connectionState === 'disconnected') {
      return;
    }

    // Cancel any ongoing requests
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }

    // Close event source if streaming
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }

    this._connectionState = 'disconnected';
    this.emit('connection', { state: 'disconnected' });
  }

  async sendMessage(message: string): Promise<Message> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }

    // Add user message to history
    const userMessage: Message = {
      id: this.generateMessageId(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    this.conversationHistory.push(userMessage);
    this.emit('message', userMessage);

    try {
      // Create abort controller for this request
      this.abortController = new AbortController();

      // Prepare conversation history for API
      const historyForApi = this.conversationHistory.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const requestId = generateRequestId();

      // Call backend agent orchestrator
      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify({
          query: message,
          conversation_history: historyForApi.slice(-10), // Last 10 messages
          session_id: this.sessionId,
          stream: false,
        }),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        throw new Error(`Backend agent error: ${response.statusText}`);
      }

      const data: AgentResponse = await response.json();
      const responseRequestId = data.request_id || requestId;

      // Create assistant message
      const assistantMessage: Message = {
        id: this.generateMessageId(),
        role: 'assistant',
        content: data.text,
        timestamp: data.timestamp,
        metadata: {
          tools_used: data.tools_used,
          data: data.data,
          model: data.model,
          cached: data.cached,
          request_id: responseRequestId,
        },
      };

      this.conversationHistory.push(assistantMessage);
      this.emit('message', assistantMessage);

      // Emit tool data for UI updates (charts, prices, etc.)
      if (data.tools_used.length > 0) {
        this.emit('toolData', {
          tools: data.tools_used,
          data: data.data,
          request_id: responseRequestId,
        });
      }

      return assistantMessage;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      this.emit('error', { error: errorMessage });
      throw error;
    } finally {
      this.abortController = null;
    }
  }

  async *streamMessage(message: string): AsyncGenerator<string> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }

    // Add user message to history
    const userMessage: Message = {
      id: this.generateMessageId(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    this.conversationHistory.push(userMessage);
    this.emit('message', userMessage);

    try {
      // Prepare conversation history for API
      const historyForApi = this.conversationHistory.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      // Use Server-Sent Events for streaming
      const requestId = generateRequestId();

      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
        },
        body: JSON.stringify({
          query: message,
          conversation_history: historyForApi.slice(-10),
          session_id: this.sessionId,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend agent error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let fullResponse = '';
      // Streaming Chart Commands: Capture all metadata from streaming
      let chartCommands: string[] | undefined;
      let chartCommandsStructured: Array<any> | undefined;
      let toolsUsed: string[] | undefined;
      let structuredData: any | undefined;
      const toolStartTimes = new Map<string, number>();
      let streamRequestId: string = requestId;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonStr = line.slice(6);
            if (jsonStr.trim()) {
              try {
                const chunk: StreamChunk = JSON.parse(jsonStr);

                if (chunk.type === 'metadata') {
                  if (chunk.request_id) {
                    streamRequestId = chunk.request_id;
                  }
                }

                if (chunk.type === 'content' && chunk.text) {
                  fullResponse += chunk.text;
                  yield chunk.text;
                }
                else if (chunk.type === 'tool_start') {
                  // Telemetry: Track tool execution start time
                  const startTime = Date.now();
                  if (chunk.tool) {
                    toolStartTimes.set(chunk.tool, startTime);
                  }
                  // Emit tool start event for UI telemetry
                  this.emit('toolData', {
                    type: 'start',
                    tool: chunk.tool,
                    arguments: chunk.arguments,
                    timestamp: startTime,
                  });
                }
                else if (chunk.type === 'tool_result') {
                  // Telemetry: Calculate tool execution duration
                  const endTime = Date.now();
                  const startTime = chunk.tool ? toolStartTimes.get(chunk.tool) : undefined;
                  const duration = startTime ? endTime - startTime : undefined;

                  // Emit tool result event for UI telemetry
                  this.emit('toolData', {
                    type: 'result',
                    tool: chunk.tool,
                    data: chunk.data,
                    timestamp: endTime,
                    duration,
                  });
                }
                else if (chunk.type === 'structured') {
                  // Capture structured analysis payload
                  structuredData = chunk.data;
                }
                else if (chunk.type === 'error') {
                  // Handle streaming errors
                  const errorMsg = chunk.message || 'Streaming error occurred';
                  console.error('[BackendAgentProvider] Streaming error:', errorMsg);
                  this.emit('error', { error: errorMsg });
                }
                else if (chunk.type === 'done') {
                  // Streaming complete: Extract chart commands from done event
                  chartCommands = chunk.chart_commands;
                  chartCommandsStructured = chunk.chart_commands_structured;
                  toolsUsed = chunk.tools_used;
                  if (chunk.request_id) {
                    streamRequestId = chunk.request_id;
                  }
                  break;
                }
              } catch (e) {
                console.error('Error parsing stream chunk:', e);
                this.emit('error', { error: 'Failed to parse stream chunk' });
              }
            }
          }
        }
      }

      // Streaming Chart Commands: Normalize before emitting
      const normalizedCommands = normalizeChartCommandPayload(
        {
          legacy: chartCommands,
          chart_commands_structured: chartCommandsStructured,
        },
        fullResponse
      );

      // Add complete response to history
      const assistantMessage: Message = {
        id: this.generateMessageId(),
        role: 'assistant',
        content: fullResponse,
        timestamp: new Date().toISOString(),
        // Include normalized chart commands and metadata
        metadata: {
          chart_commands: normalizedCommands.legacy,
          chart_commands_structured: normalizedCommands.structured,
          tools_used: toolsUsed,
          structured_output: structuredData,
          request_id: streamRequestId,
        },
      };
      this.conversationHistory.push(assistantMessage);
      this.emit('message', assistantMessage);

      // Emit normalized chart commands separately for chart integration hooks
      if (normalizedCommands.legacy.length > 0 || normalizedCommands.structured.length > 0) {
        console.log('[BackendAgentProvider] Emitting chart commands:', {
          legacyCount: normalizedCommands.legacy.length,
          structuredCount: normalizedCommands.structured.length,
        });

        this.emit('chartCommands', {
          legacy: normalizedCommands.legacy,
          structured: normalizedCommands.structured,
          responseText: fullResponse,
          request_id: streamRequestId,
        });
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to stream message';
      this.emit('error', { error: errorMessage });
      throw error;
    }
  }

  async destroy(): Promise<void> {
    await this.disconnect();
    this.conversationHistory = [];
    this._eventHandlers.clear();
  }

  // ChatProvider methods
  async setModel(model: string): Promise<void> {
    this._config.model = model;
  }

  async getAvailableModels(): Promise<{ id: string; name: string }[]> {
    return [
      { id: 'gpt-5-mini', name: 'GPT-5 Mini' },
      { id: 'gpt-5', name: 'GPT-5' },
    ];
  }

  // Helper methods
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;
  }

  private async checkBackendHealth(): Promise<void> {
    const response = await fetch(`${this._config.apiUrl || ''}/api/agent/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Backend agent service is not available');
    }

    const health = await response.json();
    if (health.status !== 'healthy') {
      throw new Error('Backend agent service is unhealthy');
    }
  }

  // Additional methods for tool information
  async getAvailableTools(): Promise<any[]> {
    try {
      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/tools`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch available tools');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching tools:', error);
      return [];
    }
  }

  async clearCache(): Promise<void> {
    try {
      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/clear-cache`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to clear cache');
      }
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }

  // Get conversation history
  getConversationHistory(): Message[] {
    return [...this.conversationHistory];
  }

  // Clear conversation history
  clearHistory(): void {
    this.conversationHistory = [];
    this.sessionId = this.generateSessionId();
  }
}
