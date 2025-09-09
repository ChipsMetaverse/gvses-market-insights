/**
 * OpenAI Realtime Service using Official SDK
 * ==========================================
 * Uses the official @openai/realtime-api-beta SDK with RealtimeClient
 * following OpenAI's recommended patterns for voice agents.
 */

import { RealtimeClient } from '@openai/realtime-api-beta';
import type { ItemType } from '@openai/realtime-api-beta/dist/lib/client.js';

interface VoiceConnectionConfig {
  sessionId?: string;
  relayServerUrl?: string;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: any) => void;
  onTranscript?: (text: string, final: boolean) => void;
  onAudioResponse?: (audioData: Int16Array) => void;
  onToolCall?: (toolName: string, arguments: any) => void;
  onToolResult?: (toolName: string, result: any) => void;
}

interface MarketDataTool {
  name: string;
  description: string;
  parameters: any;
  handler: (args: any) => Promise<any>;
}

export class OpenAIRealtimeService {
  private client: RealtimeClient;
  private config: VoiceConnectionConfig;
  private connected: boolean = false;
  private sessionId: string;
  private tools: Map<string, MarketDataTool> = new Map();
  
  constructor(config: VoiceConnectionConfig) {
    this.config = config;
    this.sessionId = config.sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Initialize RealtimeClient with relay server URL
    const relayUrl = config.relayServerUrl || `ws://localhost:8000/openai/realtime/ws`;
    
    this.client = new RealtimeClient({ 
      url: relayUrl
    });
    
    this.setupEventHandlers();
    this.setupMarketDataTools();
  }
  
  private setupEventHandlers(): void {
    // Connection events
    this.client.on('error', (event) => {
      console.error('RealtimeClient error:', event);
      this.config.onError?.(event);
    });
    
    // Conversation flow events
    this.client.on('conversation.interrupted', () => {
      console.log('Conversation interrupted (user started speaking)');
      // Stop any current audio playback
    });
    
    this.client.on('conversation.updated', ({ item, delta }) => {
      const items = this.client.conversation.getItems();
      
      switch (item.type) {
        case 'message':
          if (item.role === 'user' && delta?.transcript) {
            // User speech transcription
            this.config.onTranscript?.(delta.transcript, false);
          } else if (item.role === 'assistant' && delta?.transcript) {
            // Assistant response transcription
            this.config.onTranscript?.(delta.transcript, true);
          }
          break;
          
        case 'function_call':
          if (delta?.arguments) {
            // Function call arguments being populated
            console.log(`Tool ${item.name} arguments:`, delta.arguments);
          }
          break;
          
        case 'function_call_output':
          // Tool execution result
          console.log('Tool execution result:', item.output);
          break;
      }
      
      // Handle audio delta
      if (delta?.audio) {
        this.config.onAudioResponse?.(delta.audio);
      }
    });
    
    this.client.on('conversation.item.appended', ({ item }) => {
      console.log('Item appended:', item.type, item.status);
    });
    
    this.client.on('conversation.item.completed', ({ item }) => {
      console.log('Item completed:', item.type);
      
      if (item.type === 'function_call') {
        // Tool call completed, notify UI
        this.config.onToolCall?.(item.name || 'unknown', item.arguments);
      }
    });
    
    // Raw event access for debugging
    this.client.on('realtime.event', ({ time, source, event }) => {
      if (source === 'server') {
        console.log('Server event:', event.type);
        
        // Handle custom relay events
        switch (event.type) {
          case 'tool_call_start':
            console.log(`Starting tool: ${event.tool_name}`);
            this.config.onToolCall?.(event.tool_name, event.arguments);
            break;
            
          case 'tool_call_complete':
            console.log(`Tool completed: ${event.tool_name}`, event.success);
            this.config.onToolResult?.(event.tool_name, event.result);
            break;
            
          case 'tool_call_error':
            console.error(`Tool error: ${event.tool_name}`, event.error);
            this.config.onError?.(event);
            break;
        }
      }
    });
  }
  
  private setupMarketDataTools(): void {
    // Market data tools are handled by the relay server
    // But we can define them here for type safety and documentation
    const marketTools: MarketDataTool[] = [
      {
        name: 'get_stock_quote',
        description: 'Get real-time stock quote with detailed metrics',
        parameters: {
          type: 'object',
          properties: {
            symbol: { type: 'string', description: 'Stock symbol (e.g., TSLA, AAPL)' }
          },
          required: ['symbol']
        },
        handler: async (args) => {
          // Tools are executed by relay server, this is just for reference
          throw new Error('Tools are executed by relay server');
        }
      },
      {
        name: 'get_market_overview',
        description: 'Get overall market overview including major indices',
        parameters: { type: 'object', properties: {} },
        handler: async () => {
          throw new Error('Tools are executed by relay server');
        }
      },
      {
        name: 'get_technical_indicators',
        description: 'Calculate technical indicators for a stock',
        parameters: {
          type: 'object',
          properties: {
            symbol: { type: 'string', description: 'Stock symbol' },
            indicators: { 
              type: 'array', 
              items: { type: 'string' },
              description: 'Technical indicators to calculate'
            }
          },
          required: ['symbol', 'indicators']
        },
        handler: async () => {
          throw new Error('Tools are executed by relay server');
        }
      }
    ];
    
    marketTools.forEach(tool => {
      this.tools.set(tool.name, tool);
    });
  }
  
  async connect(): Promise<void> {
    try {
      console.log(`Connecting to relay server: ${this.config.relayServerUrl}`);
      
      // Connect to relay server FIRST
      await this.client.connect();
      
      this.connected = true;
      this.config.onConnected?.();
      
      console.log('Connected to OpenAI Realtime API via relay server');
      
      // Note: Session configuration including tools is now handled by the relay server
      // after receiving session.created from OpenAI. This ensures proper timing
      // and the correct Realtime API tool format is used.
      
    } catch (error) {
      console.error('Failed to connect to OpenAI Realtime API:', error);
      this.config.onError?.(error);
      throw error;
    }
  }
  
  async disconnect(): Promise<void> {
    try {
      if (this.connected) {
        this.client.disconnect();
        this.connected = false;
        this.config.onDisconnected?.();
        console.log('Disconnected from OpenAI Realtime API');
      }
    } catch (error) {
      console.error('Error disconnecting from OpenAI Realtime API:', error);
      this.config.onError?.(error);
    }
  }
  
  isConnected(): boolean {
    return this.connected;
  }
  
  sendTextMessage(text: string): void {
    if (!this.connected) {
      throw new Error('Not connected to OpenAI Realtime API');
    }
    
    this.client.sendUserMessageContent([
      { type: 'input_text', text }
    ]);
  }
  
  sendAudioData(audioData: Int16Array): void {
    if (!this.connected) {
      throw new Error('Not connected to OpenAI Realtime API');
    }
    
    this.client.appendInputAudio(audioData);
  }
  
  createResponse(): void {
    if (!this.connected) {
      throw new Error('Not connected to OpenAI Realtime API');
    }
    
    // Trigger model response (when turn_detection is disabled)
    this.client.createResponse();
  }
  
  interruptResponse(): void {
    if (!this.connected) {
      return;
    }
    
    // Get current conversation items to find the active response
    const items = this.client.conversation.getItems();
    const activeItem = items.find(item => item.status === 'in_progress');
    
    if (activeItem?.id) {
      // Interrupt the current response
      this.client.cancelResponse(activeItem.id, 0);
    }
  }
  
  getConversationHistory(): ItemType[] {
    return this.client.conversation.getItems();
  }
  
  getAvailableTools(): MarketDataTool[] {
    return Array.from(this.tools.values());
  }
  
  getSessionId(): string {
    return this.sessionId;
  }
}

/**
 * Factory function to create a configured OpenAI Realtime Service
 */
export function createOpenAIRealtimeService(config: Partial<VoiceConnectionConfig> = {}): OpenAIRealtimeService {
  const defaultConfig: VoiceConnectionConfig = {
    relayServerUrl: `ws://localhost:8000/realtime-relay/${config.sessionId || `session_${Date.now()}`}`,
    onConnected: () => console.log('Voice assistant connected'),
    onDisconnected: () => console.log('Voice assistant disconnected'),
    onError: (error) => console.error('Voice assistant error:', error),
    onTranscript: (text, final) => console.log(final ? 'Assistant:' : 'User:', text),
    onAudioResponse: (audio) => console.log('Received audio response:', audio.length, 'samples'),
    onToolCall: (name, args) => console.log('Tool called:', name, args),
    onToolResult: (name, result) => console.log('Tool result:', name, result),
    ...config
  };
  
  return new OpenAIRealtimeService(defaultConfig);
}

export default OpenAIRealtimeService;