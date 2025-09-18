/**
 * OpenAI Realtime Provider Implementation
 * Uses official @openai/realtime-api-beta SDK with relay server
 */

import { AbstractBaseProvider } from './BaseProvider';
import { 
  VoiceProvider, 
  ProviderConfig, 
  AudioChunk, 
  Message,
  ProviderCapabilities
} from './types';
import { OpenAIRealtimeService } from '../services/OpenAIRealtimeService';

export class OpenAIRealtimeProvider extends AbstractBaseProvider implements VoiceProvider {
  private service: OpenAIRealtimeService | null = null;
  private currentVoice: string;
  private sessionId: string;
  private isConversationActive: boolean = false;

  constructor(config: ProviderConfig) {
    super(config);
    this.sessionId = this.generateSessionId();
    this.currentVoice = config.voice || 'alloy';
  }

  static getDefaultCapabilities(): ProviderCapabilities {
    return {
      voiceConversation: true,
      textChat: true,
      textToSpeech: true,
      speechToText: true,
      streaming: true,
      tools: true
    };
  }

  async initialize(config: ProviderConfig): Promise<void> {
    this.validateConfig(config);
    
    this._config = config;
    this._capabilities = config.capabilities || OpenAIRealtimeProvider.getDefaultCapabilities();
    
    // Initialize OpenAI Realtime Service with official SDK
    this.service = new OpenAIRealtimeService({
      sessionId: this.sessionId,
      onConnected: () => {
        this.updateConnectionState('connected');
        this.emit('connected', { provider: 'openai-realtime' });
      },
      onDisconnected: () => {
        this.updateConnectionState('disconnected');
        this.emit('disconnected', { provider: 'openai-realtime' });
      },
      onError: (error: any) => {
        console.error('OpenAI Realtime Service error:', error);
        this.handleError(error?.message || 'OpenAI connection error');
      },
      onTranscript: (text: string, final: boolean) => {
        if (final) {
          // Assistant response (final)
          const message = this.createMessage('assistant', text);
          this.emit('message', message);
        } else {
          // User transcript (interim)
          const message = this.createMessage('user', text);
          this.emit('message', message);
          this.emit('transcript', text);
        }
      },
      onAudioResponse: (audioData: Int16Array) => {
        // Convert to AudioChunk format for compatibility
        const audioChunk: AudioChunk = {
          data: btoa(String.fromCharCode(...new Uint8Array(audioData.buffer))),
          format: 'pcm',
          sampleRate: 24000,
          channels: 1
        };
        this.emit('audio', audioChunk);
      },
      onToolCall: (toolName: string, args: any) => {
        console.log('OpenAI tool called:', toolName, args);
        this.emit('toolCall', { name: toolName, arguments: args });
      },
      onToolResult: (toolName: string, result: any) => {
        console.log('OpenAI tool result:', toolName, result);
        this.emit('toolResult', { name: toolName, result });
      }
    });
    
    this._isInitialized = true;
    this.emit('initialized', { provider: 'openai-realtime' });
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected' || this._connectionState === 'connecting') {
      return;
    }

    this.updateConnectionState('connecting');

    try {
      if (!this.service) {
        throw new Error('OpenAI service not initialized');
      }
      
      await this.service.connect();
      // Connection state will be updated via the onConnected callback
      
    } catch (error) {
      this.handleError(error instanceof Error ? error.message : 'Failed to connect');
    }
  }

  async disconnect(): Promise<void> {
    if (this.service) {
      await this.service.disconnect();
    }
    
    this.isConversationActive = false;
    // Connection state will be updated via the onDisconnected callback
  }

  // Voice conversation methods
  async startConversation(): Promise<void> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }
    
    this.isConversationActive = true;
    this.emit('conversationStarted', { timestamp: new Date().toISOString() });
  }

  async stopConversation(): Promise<void> {
    this.isConversationActive = false;
    this.emit('conversationStopped', { timestamp: new Date().toISOString() });
    await this.disconnect();
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    if (this._connectionState !== 'connected' || !this.service) {
      throw new Error('Not connected to OpenAI Realtime');
    }

    // Convert base64 audio to Int16Array for OpenAI service
    try {
      const binaryString = atob(audioChunk.data);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      const int16Array = new Int16Array(bytes.buffer);
      
      await this.service.sendAudioData(int16Array);
    } catch (error) {
      console.error('Failed to send audio:', error);
      throw new Error('Failed to send audio data');
    }
  }

  async sendMessage(message: string): Promise<void> {
    if (this._connectionState !== 'connected' || !this.service) {
      throw new Error('Not connected to OpenAI Realtime');
    }

    // Send text message via the service
    this.service.sendTextMessage(message);
    
    // Emit user message event
    const userMessage = this.createMessage('user', message);
    this.emit('message', userMessage);
  }

  async setVoice(voiceId: string): Promise<void> {
    this.currentVoice = voiceId;
    
    // Note: Voice changes would require reconnection with new session configuration
    // in the current OpenAI Realtime API implementation
    console.log('Voice set to:', voiceId, '(requires reconnection to take effect)');
  }

  async getAvailableVoices(): Promise<Array<{ id: string; name: string; }>> {
    // OpenAI Realtime API provides 6 preset voices
    return [
      { id: 'alloy', name: 'Alloy' },
      { id: 'echo', name: 'Echo' },
      { id: 'fable', name: 'Fable' },
      { id: 'onyx', name: 'Onyx' },
      { id: 'nova', name: 'Nova' },
      { id: 'shimmer', name: 'Shimmer' }
    ];
  }

  // Additional OpenAI-specific methods
  async createResponse(): Promise<void> {
    if (this.service) {
      this.service.createResponse();
    }
  }

  async interruptResponse(): Promise<void> {
    if (this.service) {
      this.service.interruptResponse();
    }
  }

  getConversationHistory(): any[] {
    return this.service?.getConversationHistory() || [];
  }

  getAvailableTools(): any[] {
    return this.service?.getAvailableTools() || [];
  }

  // Private methods
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }







}
