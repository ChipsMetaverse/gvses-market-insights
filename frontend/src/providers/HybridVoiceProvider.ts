/**
 * Hybrid Voice Provider
 * Combines ElevenLabs voice I/O with backend agent reasoning for
 * the best of both worlds: high-quality voice with intelligent responses.
 */

import { AbstractBaseProvider } from './BaseProvider';
import { ElevenLabsProvider } from './ElevenLabsProvider';
import { BackendAgentProvider } from './BackendAgentProvider';
import {
  ProviderConfig,
  Message,
  ConnectionState,
  ProviderCapabilities,
  VoiceProvider,
  ChatProvider,
  AudioChunk,
} from './types';

export class HybridVoiceProvider extends AbstractBaseProvider implements VoiceProvider, ChatProvider {
  private elevenLabs: ElevenLabsProvider | null = null;
  private backendAgent: BackendAgentProvider | null = null;
  private isProcessing: boolean = false;
  private conversationHistory: Message[] = [];
  private sessionId: string;

  constructor(config: ProviderConfig) {
    super(config);
    this.sessionId = this.generateSessionId();
  }

  static getDefaultCapabilities(): ProviderCapabilities {
    return {
      voiceConversation: true,  // Full voice support via ElevenLabs
      textChat: true,           // Text support via backend
      textToSpeech: true,       // ElevenLabs TTS
      speechToText: true,       // ElevenLabs ASR
      streaming: true,          // Backend streaming
      tools: true,              // Backend function calling
    };
  }

  async initialize(config: ProviderConfig): Promise<void> {
    this.config = config;
    this.connectionState = 'disconnected';

    try {
      // Initialize ElevenLabs for voice I/O
      this.elevenLabs = new ElevenLabsProvider({
        ...config,
        type: 'elevenlabs',
        name: 'ElevenLabs Voice I/O',
      });
      await this.elevenLabs.initialize(config);

      // Initialize Backend Agent for reasoning
      this.backendAgent = new BackendAgentProvider({
        ...config,
        type: 'backend-agent',
        name: 'Backend Agent Reasoning',
      });
      await this.backendAgent.initialize(config);

      // Set up event forwarding from ElevenLabs
      this.setupElevenLabsEvents();

    } catch (error) {
      this.connectionState = 'error';
      throw error;
    }
  }

  async connect(): Promise<void> {
    if (this.connectionState === 'connected') {
      return;
    }

    this.connectionState = 'connecting';
    this.emit('connection', { state: 'connecting' });

    try {
      // Connect backend agent first (for health check)
      if (this.backendAgent) {
        await this.backendAgent.connect();
      }

      // Then connect ElevenLabs for voice
      if (this.elevenLabs) {
        await this.elevenLabs.connect();
      }

      this.connectionState = 'connected';
      this.emit('connection', { state: 'connected' });
    } catch (error) {
      this.connectionState = 'error';
      this.emit('connection', { state: 'error' });
      this.emit('error', { error: error instanceof Error ? error.message : 'Connection failed' });
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.connectionState === 'disconnected') {
      return;
    }

    // Disconnect both providers
    if (this.elevenLabs) {
      await this.elevenLabs.disconnect();
    }
    if (this.backendAgent) {
      await this.backendAgent.disconnect();
    }

    this.connectionState = 'disconnected';
    this.emit('connection', { state: 'disconnected' });
  }

  // Voice conversation methods (VoiceProvider)
  async startConversation(): Promise<void> {
    if (!this.elevenLabs) {
      throw new Error('ElevenLabs not initialized');
    }
    await this.elevenLabs.startConversation();
  }

  async stopConversation(): Promise<void> {
    if (!this.elevenLabs) {
      throw new Error('ElevenLabs not initialized');
    }
    await this.elevenLabs.stopConversation();
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    if (!this.elevenLabs) {
      throw new Error('ElevenLabs not initialized');
    }
    await this.elevenLabs.sendAudio(audioChunk);
  }

  // Text chat methods (ChatProvider)
  async sendMessage(message: string, context?: string[]): Promise<Message> {
    if (!this.backendAgent) {
      throw new Error('Backend agent not initialized');
    }

    // Send to backend for processing
    const response = await this.backendAgent.sendMessage(message, context);
    
    // Also speak the response if voice is active
    if (this.elevenLabs && this.elevenLabs.connectionState === 'connected') {
      // Send text to ElevenLabs for TTS
      await this.sendTextToVoice(response.content);
    }

    return response;
  }

  async *streamMessage(message: string, context?: string[]): AsyncGenerator<string> {
    if (!this.backendAgent) {
      throw new Error('Backend agent not initialized');
    }

    let fullResponse = '';
    
    // Stream from backend
    for await (const chunk of this.backendAgent.streamMessage(message, context)) {
      fullResponse += chunk;
      yield chunk;
    }

    // Speak complete response after streaming
    if (this.elevenLabs && this.elevenLabs.connectionState === 'connected') {
      await this.sendTextToVoice(fullResponse);
    }
  }

  // Hybrid-specific methods
  private setupElevenLabsEvents(): void {
    if (!this.elevenLabs || !this.backendAgent) {
      return;
    }

    // When ElevenLabs gets a transcript, process it through backend
    this.elevenLabs.on('transcript', async (transcript: string) => {
      if (this.isProcessing) {
        return; // Prevent overlapping processing
      }

      this.isProcessing = true;
      this.emit('transcript', transcript);

      try {
        // Process transcript through backend agent
        const response = await this.backendAgent.sendMessage(transcript);
        
        // ElevenLabs will automatically speak the response
        // since we're using it in conversation mode
        
        // Emit the response message
        this.emit('message', response);
        
        // Emit tool data if any tools were used
        if (response.metadata?.tools_used?.length > 0) {
          this.emit('toolData', {
            tools: response.metadata.tools_used,
            data: response.metadata.data,
          });
        }
      } catch (error) {
        console.error('Error processing transcript:', error);
        this.emit('error', { error: error instanceof Error ? error.message : 'Processing failed' });
      } finally {
        this.isProcessing = false;
      }
    });

    // Forward other ElevenLabs events
    this.elevenLabs.on('audio', (audio: AudioChunk) => {
      this.emit('audio', audio);
    });

    this.elevenLabs.on('error', (error: any) => {
      this.emit('error', error);
    });

    // Forward backend agent events
    this.backendAgent.on('toolData', (data: any) => {
      this.emit('toolData', data);
    });
  }

  private async sendTextToVoice(text: string): Promise<void> {
    if (!this.elevenLabs) {
      return;
    }

    try {
      // In hybrid mode, we need to send the text as if it's the agent's response
      // This depends on how ElevenLabs is configured
      
      // If ElevenLabs is in conversation mode, it might not accept direct text
      // In that case, we'd need to use a different approach
      
      // For now, we'll emit an event that the UI can handle
      this.emit('speakText', { text });
      
    } catch (error) {
      console.error('Error sending text to voice:', error);
    }
  }

  async destroy(): Promise<void> {
    await this.disconnect();
    
    if (this.elevenLabs) {
      await this.elevenLabs.destroy();
      this.elevenLabs = null;
    }
    
    if (this.backendAgent) {
      await this.backendAgent.destroy();
      this.backendAgent = null;
    }
    
    this.conversationHistory = [];
    this.removeAllListeners();
  }

  getProviderInfo() {
    return {
      type: 'hybrid-voice',
      name: 'Hybrid Voice (ElevenLabs + Backend Agent)',
      capabilities: HybridVoiceProvider.getDefaultCapabilities(),
      connectionState: this.connectionState,
      metadata: {
        sessionId: this.sessionId,
        elevenLabsConnected: this.elevenLabs?.connectionState === 'connected',
        backendConnected: this.backendAgent?.connectionState === 'connected',
        isProcessing: this.isProcessing,
      },
    };
  }

  // Helper methods
  private generateSessionId(): string {
    return `hybrid_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // Get available tools from backend
  async getAvailableTools(): Promise<any[]> {
    if (!this.backendAgent) {
      return [];
    }
    return await this.backendAgent.getAvailableTools();
  }

  // Clear backend cache
  async clearCache(): Promise<void> {
    if (this.backendAgent) {
      await this.backendAgent.clearCache();
    }
  }

  // Get conversation history from backend
  getConversationHistory(): Message[] {
    if (this.backendAgent) {
      return this.backendAgent.getConversationHistory();
    }
    return this.conversationHistory;
  }

  // Clear conversation history
  clearHistory(): void {
    this.conversationHistory = [];
    this.sessionId = this.generateSessionId();
    
    if (this.backendAgent) {
      this.backendAgent.clearHistory();
    }
  }

  // Check if currently in voice mode
  isVoiceActive(): boolean {
    return this.elevenLabs?.connectionState === 'connected' || false;
  }

  // Switch between voice and text mode
  async setVoiceMode(enabled: boolean): Promise<void> {
    if (!this.elevenLabs) {
      return;
    }

    if (enabled && this.elevenLabs.connectionState !== 'connected') {
      await this.elevenLabs.connect();
      await this.elevenLabs.startConversation();
    } else if (!enabled && this.elevenLabs.connectionState === 'connected') {
      await this.elevenLabs.stopConversation();
      await this.elevenLabs.disconnect();
    }
  }
}