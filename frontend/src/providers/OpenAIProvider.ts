/**
 * OpenAI Provider Implementation
 * Implements chat and voice capabilities using OpenAI APIs
 */

import { AbstractBaseProvider } from './BaseProvider';
import { 
  ChatProvider, 
  VoiceProvider, 
  ProviderConfig, 
  AudioChunk, 
  Message,
  ProviderCapabilities
} from './types';

export class OpenAIProvider extends AbstractBaseProvider implements ChatProvider, VoiceProvider {
  private apiKey: string;
  private baseUrl: string;
  private model: string;
  private voice: string;
  private websocket: WebSocket | null = null;
  private conversationHistory: Message[] = [];

  constructor(config: ProviderConfig) {
    super(config);
    this.apiKey = config.apiKey || '';
    this.baseUrl = config.apiUrl || 'https://api.openai.com/v1';
    this.model = config.model || 'gpt-4';
    this.voice = config.voice || 'alloy';
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
    
    if (!config.apiKey) {
      throw new Error('OpenAI API key is required');
    }

    this._config = config;
    this._capabilities = config.capabilities || OpenAIProvider.getDefaultCapabilities();
    this.apiKey = config.apiKey;
    this._isInitialized = true;

    this.emit('initialized', { provider: 'openai' });
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected' || this._connectionState === 'connecting') {
      return;
    }

    this.updateConnectionState('connecting');

    try {
      // For OpenAI, we'll simulate connection since REST API doesn't maintain persistent connections
      // In a real implementation, this might connect to OpenAI's real-time API
      this.updateConnectionState('connected');
    } catch (error) {
      this.handleError(error instanceof Error ? error.message : 'Failed to connect');
    }
  }

  async disconnect(): Promise<void> {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.updateConnectionState('disconnected');
  }

  // Chat Provider Implementation
  async sendMessage(message: string, context?: string[]): Promise<Message> {
    if (!this._isInitialized) {
      throw new Error('Provider not initialized');
    }

    const userMessage = this.createMessage('user', message);
    this.conversationHistory.push(userMessage);
    this.emit('message', userMessage);

    try {
      const messages = [
        ...(context ? context.map(c => ({ role: 'system' as const, content: c })) : []),
        ...this.conversationHistory.map(m => ({ role: m.role, content: m.content }))
      ];

      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.model,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1000
        }),
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.statusText}`);
      }

      const data = await response.json();
      const assistantContent = data.choices[0]?.message?.content || '';
      
      const assistantMessage = this.createMessage('assistant', assistantContent);
      this.conversationHistory.push(assistantMessage);
      this.emit('message', assistantMessage);

      return assistantMessage;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      this.handleError(errorMessage);
      throw new Error(errorMessage);
    }
  }

  async *streamMessage(message: string, context?: string[]): AsyncGenerator<string> {
    if (!this._isInitialized) {
      throw new Error('Provider not initialized');
    }

    const userMessage = this.createMessage('user', message);
    this.conversationHistory.push(userMessage);
    this.emit('message', userMessage);

    try {
      const messages = [
        ...(context ? context.map(c => ({ role: 'system' as const, content: c })) : []),
        ...this.conversationHistory.map(m => ({ role: m.role, content: m.content }))
      ];

      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.model,
          messages: messages,
          temperature: 0.7,
          max_tokens: 1000,
          stream: true
        }),
      });

      if (!response.ok) {
        throw new Error(`OpenAI API error: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      let assistantContent = '';

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6);
              if (data === '[DONE]') {
                break;
              }

              try {
                const parsed = JSON.parse(data);
                const content = parsed.choices[0]?.delta?.content || '';
                if (content) {
                  assistantContent += content;
                  yield content;
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      } finally {
        reader.releaseLock();
      }

      // Store the complete assistant message
      if (assistantContent) {
        const assistantMessage = this.createMessage('assistant', assistantContent);
        this.conversationHistory.push(assistantMessage);
        this.emit('message', assistantMessage);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to stream message';
      this.handleError(errorMessage);
      throw new Error(errorMessage);
    }
  }

  async setModel(model: string): Promise<void> {
    this.model = model;
    await this.updateConfig({ ...this._config, model });
  }

  async getAvailableModels(): Promise<Array<{ id: string; name: string; }>> {
    return [
      { id: 'gpt-5', name: 'GPT-5' },
      { id: 'gpt-5-mini', name: 'GPT-5 Mini' },
    ];
  }

  // Voice Provider Implementation (using OpenAI's real-time API)
  async startConversation(): Promise<void> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }

    // This would connect to OpenAI's real-time API when it becomes available
    // For now, we'll simulate voice conversation using TTS + STT + Chat
    this.emit('conversationStarted', { timestamp: new Date().toISOString() });
  }

  async stopConversation(): Promise<void> {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.emit('conversationStopped', { timestamp: new Date().toISOString() });
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    // This would implement OpenAI's Whisper API for speech-to-text
    // For now, throw an error as it requires backend integration
    throw new Error('Audio processing requires backend integration with OpenAI Whisper API');
  }

  // Note: VoiceProvider's sendMessage is handled by the ChatProvider implementation
  // When OpenAI real-time voice is available, we'll implement this properly

  async setVoice(voiceId: string): Promise<void> {
    this.voice = voiceId;
    await this.updateConfig({ ...this._config, voice: voiceId });
  }

  async getAvailableVoices(): Promise<Array<{ id: string; name: string; }>> {
    return [
      { id: 'alloy', name: 'Alloy' },
      { id: 'echo', name: 'Echo' },
      { id: 'fable', name: 'Fable' },
      { id: 'onyx', name: 'Onyx' },
      { id: 'nova', name: 'Nova' },
      { id: 'shimmer', name: 'Shimmer' },
    ];
  }

  // TTS functionality (would require backend integration)
  async synthesizeText(text: string): Promise<AudioChunk> {
    try {
      const response = await fetch(`${this.baseUrl}/audio/speech`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'tts-1',
          input: text,
          voice: this.voice,
          response_format: 'mp3'
        }),
      });

      if (!response.ok) {
        throw new Error(`OpenAI TTS error: ${response.statusText}`);
      }

      const audioData = await response.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(audioData)));

      return {
        data: base64Audio,
        format: 'mp3',
        sampleRate: 24000,
        channels: 1
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to synthesize speech';
      this.handleError(errorMessage);
      throw new Error(errorMessage);
    }
  }

  // Conversation management
  clearConversationHistory(): void {
    this.conversationHistory = [];
    this.emit('conversationCleared', { timestamp: new Date().toISOString() });
  }

  getConversationHistory(): Message[] {
    return [...this.conversationHistory];
  }
}
