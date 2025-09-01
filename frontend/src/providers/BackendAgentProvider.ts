/**
 * Backend Agent Provider
 * Connects to the backend OpenAI agent orchestrator for intelligent
 * query processing with function calling and tool execution.
 */

import { AbstractBaseProvider } from './BaseProvider';
import {
  ProviderConfig,
  Message,
  ConnectionState,
  ProviderCapabilities,
  ChatProvider,
} from './types';

interface AgentResponse {
  text: string;
  tools_used: string[];
  data: Record<string, any>;
  timestamp: string;
  model: string;
  cached: boolean;
  session_id?: string;
}

interface StreamChunk {
  type: 'metadata' | 'content' | 'done';
  text?: string;
  session_id?: string;
  model?: string;
}

export class BackendAgentProvider extends AbstractBaseProvider implements ChatProvider {
  private conversationHistory: Message[] = [];
  private sessionId: string;
  private abortController: AbortController | null = null;
  private eventSource: EventSource | null = null;

  constructor(config: ProviderConfig) {
    super(config);
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

      // Call backend agent orchestrator
      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/orchestrate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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
        },
      };

      this.conversationHistory.push(assistantMessage);
      this.emit('message', assistantMessage);

      // Emit tool data for UI updates (charts, prices, etc.)
      if (data.tools_used.length > 0) {
        this.emit('toolData', {
          tools: data.tools_used,
          data: data.data,
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
      const response = await fetch(`${this._config.apiUrl || ''}/api/agent/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
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
                
                if (chunk.type === 'content' && chunk.text) {
                  fullResponse += chunk.text;
                  yield chunk.text;
                } else if (chunk.type === 'done') {
                  // Streaming complete
                  break;
                }
              } catch (e) {
                console.error('Error parsing stream chunk:', e);
              }
            }
          }
        }
      }

      // Add complete response to history
      const assistantMessage: Message = {
        id: this.generateMessageId(),
        role: 'assistant',
        content: fullResponse,
        timestamp: new Date().toISOString(),
      };
      this.conversationHistory.push(assistantMessage);
      this.emit('message', assistantMessage);

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
      { id: 'gpt-4o', name: 'GPT-4 Optimized' },
      { id: 'gpt-4', name: 'GPT-4' },
      { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
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