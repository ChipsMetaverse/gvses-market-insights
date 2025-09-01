/**
 * OpenAI Realtime Provider Implementation
 * Connects to unified WebSocket relay for voice conversation
 */

import { AbstractBaseProvider } from './BaseProvider';
import { 
  VoiceProvider, 
  ProviderConfig, 
  AudioChunk, 
  Message,
  ProviderCapabilities
} from './types';

export class OpenAIRealtimeProvider extends AbstractBaseProvider implements VoiceProvider {
  private websocket: WebSocket | null = null;
  private audioQueue: ArrayBuffer[] = [];
  private isPlaying: boolean = false;
  private currentVoice: string;
  private relayUrl: string;
  private sessionId: string | null = null;

  constructor(config: ProviderConfig) {
    super(config);
    // Use the WebSocket relay URL from environment or config
    this.relayUrl = import.meta.env.VITE_WEBSOCKET_RELAY_URL || 
                    config.apiUrl || 
                    'ws://localhost:3004';
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
    this._isInitialized = true;

    this.emit('initialized', { provider: 'openai' });
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected' || this._connectionState === 'connecting') {
      return;
    }

    this.updateConnectionState('connecting');

    try {
      // Generate a session ID
      this.sessionId = this.generateSessionId();
      
      // Connect to unified WebSocket relay
      this.websocket = new WebSocket(this.relayUrl);
      
      this.websocket.onopen = () => {
        console.log('Connected to unified WebSocket relay');
        
        // Send initialization message for OpenAI provider
        this.sendWebSocketMessage({
          type: 'init',
          provider: 'openai',
          config: {
            sessionId: this.sessionId,
            model: this._config.model || 'gpt-4o-realtime-preview',
            voice: this.currentVoice,
            instructions: 'You are a helpful assistant with real-time voice capabilities.'
          }
        });
        
        this.updateConnectionState('connected');
      };
      
      this.websocket.onmessage = (event) => {
        this.handleWebSocketMessage(event);
      };
      
      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.handleError('WebSocket connection failed');
      };
      
      this.websocket.onclose = () => {
        console.log('WebSocket closed');
        this.updateConnectionState('disconnected');
        this.websocket = null;
        this.sessionId = null;
      };
      
    } catch (error) {
      this.handleError(error instanceof Error ? error.message : 'Failed to connect');
    }
  }

  async disconnect(): Promise<void> {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    
    this.sessionId = null;
    this.audioQueue = [];
    this.isPlaying = false;
    this.updateConnectionState('disconnected');
  }

  // Voice conversation methods
  async startConversation(): Promise<void> {
    if (this._connectionState !== 'connected') {
      await this.connect();
    }
    
    this.emit('conversationStarted', { timestamp: new Date().toISOString() });
  }

  async stopConversation(): Promise<void> {
    await this.disconnect();
    this.emit('conversationStopped', { timestamp: new Date().toISOString() });
  }

  async sendAudio(audioChunk: AudioChunk): Promise<void> {
    if (this._connectionState !== 'connected' || !this.websocket) {
      throw new Error('Not connected to OpenAI Realtime');
    }

    // Convert audio to PCM16 24kHz if needed
    const pcmData = await this.convertAudioToPCM16_24kHz(audioChunk);
    
    // Send audio to OpenAI
    this.sendWebSocketMessage({
      type: 'input_audio_buffer.append',
      audio: this.arrayBufferToBase64(pcmData)
    });
  }

  async sendMessage(message: string): Promise<void> {
    if (this._connectionState !== 'connected' || !this.websocket) {
      throw new Error('Not connected to OpenAI Realtime');
    }

    // Send text message
    this.sendWebSocketMessage({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [
          {
            type: 'input_text',
            text: message
          }
        ]
      }
    });

    // Trigger response generation
    this.sendWebSocketMessage({
      type: 'response.create'
    });

    // Emit user message event
    const userMessage = this.createMessage('user', message);
    this.emit('message', userMessage);
  }

  async setVoice(voiceId: string): Promise<void> {
    this.currentVoice = voiceId;
    
    if (this._connectionState === 'connected' && this.websocket) {
      // Update voice in current session
      this.sendWebSocketMessage({
        type: 'session.update',
        session: {
          voice: voiceId
        }
      });
    }
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

  // Private methods
  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sendWebSocketMessage(message: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }

  private async handleWebSocketMessage(event: MessageEvent): Promise<void> {
    try {
      // Handle binary audio data
      if (event.data instanceof Blob) {
        const arrayBuffer = await event.data.arrayBuffer();
        await this.handleAudioData(arrayBuffer);
        return;
      } else if (event.data instanceof ArrayBuffer) {
        await this.handleAudioData(event.data);
        return;
      }

      // Handle JSON messages
      const data = JSON.parse(event.data);
      console.log('Relay message:', data.type || data.t);
      
      // Unified relay uses 'type' field
      const messageType = data.type || data.t;
      
      switch (messageType) {
        case 'init_success':
          console.log('OpenAI Realtime session initialized');
          this.emit('sessionUpdated', { provider: 'openai' });
          break;
          
        case 'transcript':
          // User transcript from speech recognition
          if (data.text) {
            const message = this.createMessage('user', data.text);
            this.emit('message', message);
            this.emit('transcript', data.text);
          }
          break;
          
        case 'partial_text':
          // Assistant partial response
          if (data.text) {
            this.emit('partialResponse', data.text);
          }
          break;
          
        case 'final_text':
        case 'agent_response':
          // Assistant final response
          if (data.text) {
            const message = this.createMessage('assistant', data.text);
            this.emit('message', message);
          }
          break;
          
        case 'audio':
          // Audio data (base64 encoded in message)
          if (data.data) {
            await this.handleAudioData(data.data);
          }
          break;
          
        case 'tool_call':
          // Tool/function call from assistant
          console.log('Tool call:', data.tool_name, data.arguments);
          this.emit('toolCall', { 
            name: data.tool_name, 
            arguments: data.arguments 
          });
          break;
          
        case 'error':
          this.handleError(data.message || data.msg || 'Unknown error');
          break;
          
        default:
          console.log('Unknown message type:', messageType, data);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private async handleAudioData(audioData: ArrayBuffer | string): Promise<void> {
    try {
      // Convert to ArrayBuffer if it's base64 string
      const audioBuffer = typeof audioData === 'string' 
        ? this.base64ToArrayBuffer(audioData)
        : audioData;
      
      // Add to queue and play
      this.audioQueue.push(audioBuffer);
      await this.playNextAudio();
      
      // Emit audio event
      const audioChunk: AudioChunk = {
        data: this.arrayBufferToBase64(audioBuffer),
        format: 'pcm',
        sampleRate: 24000, // OpenAI uses 24kHz
        channels: 1
      };
      
      this.emit('audio', audioChunk);
    } catch (error) {
      console.error('Error handling audio data:', error);
    }
  }

  private async convertAudioToPCM16_24kHz(audioChunk: AudioChunk): Promise<ArrayBuffer> {
    // If already in correct format, return as-is
    if (audioChunk.format === 'pcm' && audioChunk.sampleRate === 24000) {
      return this.base64ToArrayBuffer(audioChunk.data);
    }
    
    // Convert from 16kHz to 24kHz if needed
    if (audioChunk.format === 'pcm' && audioChunk.sampleRate === 16000) {
      return this.resamplePCM(
        this.base64ToArrayBuffer(audioChunk.data), 
        16000, 
        24000
      );
    }
    
    // For other formats, would need more complex conversion
    throw new Error(`Unsupported audio format: ${audioChunk.format} at ${audioChunk.sampleRate}Hz`);
  }

  private resamplePCM(buffer: ArrayBuffer, fromRate: number, toRate: number): ArrayBuffer {
    // Simple linear interpolation resampling
    const ratio = toRate / fromRate;
    const inputSamples = new Int16Array(buffer);
    const outputLength = Math.floor(inputSamples.length * ratio);
    const outputSamples = new Int16Array(outputLength);
    
    for (let i = 0; i < outputLength; i++) {
      const srcIndex = i / ratio;
      const srcIndexFloor = Math.floor(srcIndex);
      const srcIndexCeil = Math.ceil(srcIndex);
      
      if (srcIndexCeil >= inputSamples.length) {
        outputSamples[i] = inputSamples[inputSamples.length - 1];
      } else {
        const weight = srcIndex - srcIndexFloor;
        outputSamples[i] = Math.round(
          inputSamples[srcIndexFloor] * (1 - weight) + 
          inputSamples[srcIndexCeil] * weight
        );
      }
    }
    
    return outputSamples.buffer;
  }

  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  private async playNextAudio(): Promise<void> {
    if (this.isPlaying || this.audioQueue.length === 0) {
      return;
    }

    this.isPlaying = true;
    const audioBuffer = this.audioQueue.shift();
    
    if (audioBuffer) {
      try {
        await this.playAudioBuffer(audioBuffer);
      } catch (error) {
        console.error('Error playing audio:', error);
      }
    }
    
    this.isPlaying = false;
    
    // Play next audio if queue has more
    if (this.audioQueue.length > 0) {
      this.playNextAudio();
    }
  }

  private async playAudioBuffer(audioBuffer: ArrayBuffer): Promise<void> {
    // Create WAV header for PCM audio (24kHz, 16-bit, mono)
    const sampleRate = 24000; // OpenAI uses 24kHz
    const numChannels = 1;
    const bitsPerSample = 16;
    const byteRate = sampleRate * numChannels * (bitsPerSample / 8);
    const blockAlign = numChannels * (bitsPerSample / 8);
    const dataSize = audioBuffer.byteLength;
    const fileSize = 44 + dataSize;

    // Create WAV file with header
    const wavBuffer = new ArrayBuffer(fileSize);
    const view = new DataView(wavBuffer);

    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    // WAV header
    writeString(0, 'RIFF');
    view.setUint32(4, fileSize - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bitsPerSample, true);
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);

    // Copy PCM data
    const dataArray = new Uint8Array(wavBuffer, 44);
    dataArray.set(new Uint8Array(audioBuffer));

    // Play audio
    const audioBlob = new Blob([wavBuffer], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    return new Promise((resolve, reject) => {
      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };
      
      audio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        reject(error);
      };
      
      audio.play().catch(reject);
    });
  }
}