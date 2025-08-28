/**
 * ElevenLabs Provider Implementation
 * Implements voice conversation using ElevenLabs Conversational AI
 */

import { AbstractBaseProvider } from './BaseProvider';
import { 
  VoiceProvider, 
  ProviderConfig, 
  AudioChunk, 
  Message,
  ProviderCapabilities
} from './types';

export class ElevenLabsProvider extends AbstractBaseProvider implements VoiceProvider {
  private websocket: WebSocket | null = null;
  private audioQueue: string[] = [];
  private isPlaying: boolean = false;
  private currentVoiceId?: string;
  private apiUrl: string;

  constructor(config: ProviderConfig) {
    super(config);
    this.apiUrl = config.apiUrl || window.location.origin;
    this.currentVoiceId = config.voice;
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
    
    if (!config.agentId) {
      throw new Error('ElevenLabs agent ID is required');
    }

    this._config = config;
    this._capabilities = config.capabilities || ElevenLabsProvider.getDefaultCapabilities();
    this._isInitialized = true;

    this.emit('initialized', { provider: 'elevenlabs' });
  }

  async connect(): Promise<void> {
    if (this._connectionState === 'connected' || this._connectionState === 'connecting') {
      return;
    }

    this.updateConnectionState('connecting');

    try {
      // Get signed URL from backend
      const signedUrl = await this.getSignedUrl();
      
      // Create WebSocket connection
      this.websocket = new WebSocket(signedUrl);
      
      this.websocket.onopen = () => {
        console.log('ElevenLabs WebSocket connected');
        this.updateConnectionState('connected');
        
        // Send initialization message
        this.sendWebSocketMessage({
          type: 'conversation_initiation_client_data'
        });
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
      throw new Error('Not connected to ElevenLabs');
    }

    this.sendWebSocketMessage({
      user_audio_chunk: audioChunk.data
    });
  }

  async sendMessage(message: string): Promise<void> {
    if (this._connectionState !== 'connected' || !this.websocket) {
      throw new Error('Not connected to ElevenLabs');
    }

    this.sendWebSocketMessage({
      type: 'user_message',
      text: message
    });

    // Emit user message event
    const userMessage = this.createMessage('user', message);
    this.emit('message', userMessage);
  }

  async setVoice(voiceId: string): Promise<void> {
    this.currentVoiceId = voiceId;
    // ElevenLabs voice is set during agent configuration, not runtime
    // This would require updating the agent configuration
  }

  async getAvailableVoices(): Promise<Array<{ id: string; name: string; }>> {
    // This would require an API call to ElevenLabs to get available voices
    // For now, return a default set
    return [
      { id: 'default', name: 'Default Voice' }
    ];
  }

  // Private methods
  private async getSignedUrl(agentId?: string): Promise<string> {
    const params = agentId ? `?agent_id=${agentId}` : 
                  this._config.agentId ? `?agent_id=${this._config.agentId}` : '';
    
    const response = await fetch(`${this.apiUrl}/elevenlabs/signed-url${params}`);
    
    if (!response.ok) {
      throw new Error('Failed to get signed URL from backend');
    }
    
    const data = await response.json();
    return data.signed_url;
  }

  private sendWebSocketMessage(message: any): void {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }

  private handleWebSocketMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);
      console.log('ElevenLabs message:', data.type);
      
      switch (data.type) {
        case 'user_transcript':
          this.handleUserTranscript(data);
          break;
          
        case 'agent_response':
          this.handleAgentResponse(data);
          break;
          
        case 'agent_response_correction':
          this.handleAgentResponseCorrection(data);
          break;
          
        case 'audio':
          this.handleAudioChunk(data);
          break;
          
        case 'ping':
          this.handlePing(data);
          break;
          
        case 'interruption':
          this.handleInterruption(data);
          break;
          
        case 'conversation_initiation_metadata':
          this.emit('conversationInitialized', data);
          break;
          
        default:
          console.log('Unknown message type:', data.type);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleUserTranscript(data: any): void {
    const transcript = data.user_transcription_event?.user_transcript;
    if (transcript) {
      const message = this.createMessage('user', transcript);
      this.emit('message', message);
      this.emit('transcript', transcript);
    }
  }

  private handleAgentResponse(data: any): void {
    const response = data.agent_response_event?.agent_response;
    if (response) {
      const message = this.createMessage('assistant', response);
      this.emit('message', message);
    }
  }

  private handleAgentResponseCorrection(data: any): void {
    const correctedResponse = data.agent_response_correction_event?.corrected_agent_response;
    if (correctedResponse) {
      const message = this.createMessage('assistant', correctedResponse, { 
        type: 'correction' 
      });
      this.emit('message', message);
    }
  }

  private handleAudioChunk(data: any): void {
    const audioBase64 = data.audio_event?.audio_base_64;
    if (audioBase64) {
      this.audioQueue.push(audioBase64);
      this.playNextAudio();
      
      const audioChunk: AudioChunk = {
        data: audioBase64,
        format: 'pcm',
        sampleRate: 16000,
        channels: 1
      };
      
      this.emit('audio', audioChunk);
    }
  }

  private handlePing(data: any): void {
    const eventId = data.ping_event?.event_id;
    const pingMs = data.ping_event?.ping_ms || 0;
    
    setTimeout(() => {
      if (this.websocket?.readyState === WebSocket.OPEN) {
        this.sendWebSocketMessage({
          type: 'pong',
          event_id: eventId
        });
      }
    }, pingMs);
  }

  private handleInterruption(data: any): void {
    console.log('Conversation interrupted:', data.interruption_event?.reason);
    this.emit('interruption', data.interruption_event);
  }

  private async playNextAudio(): Promise<void> {
    if (this.isPlaying || this.audioQueue.length === 0) {
      return;
    }

    this.isPlaying = true;
    const audioBase64 = this.audioQueue.shift();
    
    if (audioBase64) {
      try {
        await this.playAudioChunk(audioBase64);
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

  private async playAudioChunk(audioBase64: string): Promise<void> {
    // Convert base64 PCM to WAV and play
    const binaryString = atob(audioBase64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Create WAV header for PCM audio (16kHz, 16-bit, mono)
    const sampleRate = 16000;
    const numChannels = 1;
    const bitsPerSample = 16;
    const byteRate = sampleRate * numChannels * (bitsPerSample / 8);
    const blockAlign = numChannels * (bitsPerSample / 8);
    const dataSize = bytes.length;
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
    dataArray.set(bytes);

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