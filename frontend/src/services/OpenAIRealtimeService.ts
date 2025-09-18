/**
 * OpenAI Realtime Service using Official SDK
 * ==========================================
 * Uses the official @openai/realtime-api-beta SDK with RealtimeClient
 * following OpenAI's recommended patterns for voice agents.
 */

import { RealtimeClient } from '@openai/realtime-api-beta';
import type { ItemType } from '@openai/realtime-api-beta/dist/lib/client.js';
import { getApiUrl } from '../utils/apiConfig';

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

export class OpenAIRealtimeService {
  private client: RealtimeClient;
  private config: VoiceConnectionConfig;
  private connected: boolean = false;
  private sessionId: string;
  
  constructor(config: VoiceConnectionConfig) {
    this.config = config;
    this.sessionId = config.sessionId || `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Store config for later use in connect()
    console.log('🌐 OpenAIRealtimeService initialized');
    console.log('🔍 Config.relayServerUrl:', config.relayServerUrl);
    
    // Client will be created in connect() after fetching session
    this.client = null as any;
  }
  
  private setupEventHandlers(): void {
    // FIXED: Use correct RealtimeClient events from official docs
    
    // Error events (connection failures, etc.)
    this.client.on('error', (event) => {
      console.error('🔴 RealtimeClient error:', event);
      this.connected = false;
      this.config.onError?.(event);
      this.config.onDisconnected?.();
    });
    
    // Raw server/client events for debugging
    this.client.on('realtime.event', ({ time, source, event }) => {
      console.log('📡 RealtimeEvent:', source, event.type, event);
      
      // Handle session.created as connection confirmation
      if (source === 'server' && event.type === 'session.created') {
        console.log('🚀 OpenAI session created - connection established!');
        console.log('🔧 DEBUG: About to set connected=true and call onConnected callback');
        this.connected = true;
        console.log('🔧 DEBUG: this.connected is now:', this.connected);
        console.log('🔧 DEBUG: this.config.onConnected exists?', typeof this.config.onConnected);
        if (this.config.onConnected) {
          console.log('🔧 DEBUG: Calling onConnected callback now...');
          this.config.onConnected();
          console.log('🔧 DEBUG: onConnected callback completed');
        } else {
          console.warn('🔧 DEBUG: onConnected callback is missing!');
        }
      }
      
      // Handle session.updated
      if (source === 'server' && event.type === 'session.updated') {
        console.log('⚙️ OpenAI session updated:', event.session);
      }
      
      // Handle connection errors
      if (source === 'server' && event.type === 'error') {
        console.error('❌ OpenAI server error:', event?.error?.message || JSON.stringify(event?.error));
        this.connected = false;
        this.config.onError?.(event.error);
        this.config.onDisconnected?.();
      }
    });
    
    // Track current message being built up from deltas
    const currentMessages = new Map<string, { role: string; content: string }>();
    
    // Conversation flow events
    this.client.on('conversation.interrupted', () => {
      console.log('Conversation interrupted (user started speaking)');
      // Stop any current audio playback
    });
    
    this.client.on('conversation.updated', ({ item, delta }) => {
      const items = this.client.conversation.getItems();
      
      switch (item.type) {
        case 'message':
          if (delta?.transcript) {
            // Accumulate transcript deltas
            const messageKey = `${item.role}-${item.id}`;
            
            if (!currentMessages.has(messageKey)) {
              currentMessages.set(messageKey, {
                role: item.role,
                content: ''
              });
            }
            
            const message = currentMessages.get(messageKey)!;
            message.content += delta.transcript;
            
            // Send the accumulated transcript (updating the same message)
            if (item.role === 'user') {
              // User transcripts: final=false during speaking (for UI updates)
              this.config.onTranscript?.(message.content, false, item.id);
            }
            // Don't emit assistant transcripts - they're not needed for agent processing
            // The agent will provide its own response text
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
    
    // Clear message when completed
    this.client.on('conversation.item.completed', ({ item }) => {
      if (item.type === 'message') {
        const messageKey = `${item.role}-${item.id}`;
        
        // Emit final transcript for user messages before clearing
        if (item.role === 'user') {
          const finalMessage = currentMessages.get(messageKey);
          if (finalMessage && finalMessage.content) {
            console.log('📝 User speech completed, emitting final transcript:', finalMessage.content);
            // Emit as final (true) so agent hook will process it
            this.config.onTranscript?.(finalMessage.content, true, item.id);
          }
        }
        // Note: We don't emit assistant transcripts at all - the agent provides responses
        
        currentMessages.delete(messageKey);
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
  
  async connect(): Promise<void> {
    try {
      console.log('🎤 Connecting to OpenAI Realtime API...');
      
      // Use standardized API URL utility
      const apiUrl = getApiUrl();
      
      // First, create a session to get the relay URL
      const sessionResponse = await fetch(`${apiUrl}/openai/realtime/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!sessionResponse.ok) {
        throw new Error(`Failed to create session: ${sessionResponse.statusText}`);
      }
      
      const sessionData = await sessionResponse.json();
      
      // Build dynamic WebSocket URL from session
      let relayUrl: string = sessionData.ws_url;
      if (!relayUrl) {
        // Construct from apiUrl and session_id if not provided
        const wsUrl = apiUrl.replace(/^http/, 'ws');
        relayUrl = `${wsUrl}/realtime-relay/${sessionData.session_id}`;
      } else if (!relayUrl.startsWith('ws')) {
        // If it's a relative path, build full URL from apiUrl
        const wsUrl = apiUrl.replace(/^http/, 'ws');
        relayUrl = `${wsUrl}${relayUrl}`;
      }
      console.log('🌐 Creating RealtimeClient with relay URL:', relayUrl);
      
      // Now create the client with the relay URL (this will execute tools!)
      this.client = new RealtimeClient({ 
        url: relayUrl
      });
      
      // Set up event handlers on the new client
      this.setupEventHandlers();
      
      console.log('🔗 Connecting to relay server:', relayUrl);
      
      // FIXED: RealtimeClient.connect() handles connection internally
      // Success is indicated by session.created event, not explicit return
      await this.client.connect();
      
      console.log('✅ RealtimeClient.connect() completed - waiting for session.created');
      
      // Note: Connection success confirmed via 'realtime.event' with session.created
      
    } catch (error) {
      console.error('❌ Failed to connect to OpenAI Realtime API:', error);
      this.connected = false;
      this.config.onError?.(error);
      this.config.onDisconnected?.();
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
    
    console.log('📤 Sending text for TTS:', text);
    
    // With turn_detection disabled in the relay server, this won't auto-generate responses
    // The text will be sent for TTS only, as configured by the relay
    this.client.sendUserMessageContent([
      { type: 'input_text', text }
    ]);
    
    // Explicitly request audio response for TTS
    // Since turn_detection is disabled, we need to manually trigger the response
    this.createResponse();
    
    console.log('✅ TTS request sent');
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
  
  getSessionId(): string {
    return this.sessionId;
  }
}

/**
 * Factory function to create a configured OpenAI Realtime Service
 */
export function createOpenAIRealtimeService(config: Partial<VoiceConnectionConfig> = {}): OpenAIRealtimeService {
  const defaultConfig: VoiceConnectionConfig = {
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
