/**
 * Provider Types and Interfaces
 * Modular architecture for swapping AI/Voice providers
 */

// Core message types
export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

// Audio/Voice types
export interface AudioChunk {
  data: string; // base64 encoded audio data
  format: 'pcm' | 'wav' | 'mp3';
  sampleRate: number;
  channels: number;
}

// Connection states
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';

// Provider capabilities
export interface ProviderCapabilities {
  voiceConversation: boolean;
  textChat: boolean;
  textToSpeech: boolean;
  speechToText: boolean;
  streaming: boolean;
  tools: boolean;
}

// Provider configuration
export interface ProviderConfig {
  type: 'elevenlabs' | 'openai' | 'openai-realtime' | 'claude' | 'custom';
  name: string;
  apiKey?: string;
  apiUrl?: string;
  model?: string;
  voice?: string;
  agentId?: string;
  capabilities: ProviderCapabilities;
  settings?: Record<string, any>;
}

// Event types for provider communication
export interface ProviderEvent {
  type: 'message' | 'audio' | 'transcript' | 'connection' | 'error';
  data: any;
  timestamp: string;
}

// Provider event handlers
export interface ProviderEventHandlers {
  onMessage?: (message: Message) => void;
  onAudio?: (audio: AudioChunk) => void;
  onTranscript?: (transcript: string) => void;
  onConnectionChange?: (state: ConnectionState) => void;
  onError?: (error: string) => void;
}

// Base provider interface that all providers must implement
export interface BaseProvider {
  readonly config: ProviderConfig;
  readonly capabilities: ProviderCapabilities;
  readonly connectionState: ConnectionState;
  
  // Lifecycle methods
  initialize(config: ProviderConfig): Promise<void>;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  destroy(): Promise<void>;
  
  // Event handling
  on(event: string, handler: Function): void;
  off(event: string, handler: Function): void;
  emit(event: string, data: any): void;
}

// Voice conversation provider interface
export interface VoiceProvider extends BaseProvider {
  // Voice conversation methods
  startConversation(): Promise<void>;
  stopConversation(): Promise<void>;
  sendAudio(audioChunk: AudioChunk): Promise<void>;
  sendMessage(message: string): Promise<void>;
  
  // Voice-specific capabilities
  setVoice(voiceId: string): Promise<void>;
  getAvailableVoices(): Promise<Array<{ id: string; name: string; }>>;
}

// Text chat provider interface  
export interface ChatProvider extends BaseProvider {
  // Chat methods
  sendMessage(message: string, context?: string[]): Promise<Message>;
  streamMessage(message: string, context?: string[]): AsyncGenerator<string>;
  
  // Chat-specific capabilities
  setModel(model: string): Promise<void>;
  getAvailableModels(): Promise<Array<{ id: string; name: string; }>>;
}

// Text-to-speech provider interface
export interface TTSProvider extends BaseProvider {
  // TTS methods
  synthesize(text: string, voice?: string): Promise<AudioChunk>;
  streamSynthesize(text: string, voice?: string): AsyncGenerator<AudioChunk>;
  
  // TTS-specific capabilities
  setVoice(voiceId: string): Promise<void>;
  getAvailableVoices(): Promise<Array<{ id: string; name: string; }>>;
}

// Speech-to-text provider interface
export interface ASRProvider extends BaseProvider {
  // ASR methods
  transcribe(audioChunk: AudioChunk): Promise<string>;
  startTranscription(): Promise<void>;
  stopTranscription(): Promise<void>;
  
  // ASR-specific capabilities
  setLanguage(language: string): Promise<void>;
  getSupportedLanguages(): Promise<Array<{ code: string; name: string; }>>;
}

// Combined provider interface (for providers that support multiple capabilities)
export interface CombinedProvider extends VoiceProvider, ChatProvider, TTSProvider, ASRProvider {
  // Additional combined provider methods if needed
}

// Provider factory interface
export interface ProviderFactory {
  createProvider<T extends BaseProvider>(config: ProviderConfig): Promise<T>;
  registerProvider(type: string, providerClass: any): void;
  getSupportedProviders(): ProviderConfig[];
}

// Provider manager interface
export interface ProviderManager {
  getCurrentProvider(): BaseProvider | null;
  switchProvider(config: ProviderConfig): Promise<void>;
  getAvailableProviders(): ProviderConfig[];
  registerProvider(provider: ProviderConfig): void;
}