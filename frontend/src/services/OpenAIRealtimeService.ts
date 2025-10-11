/**
 * OpenAI Realtime Service using Official SDK
 * ==========================================
 * Uses the official @openai/realtime-api SDK with RealtimeClient
 * following OpenAI's recommended patterns for voice agents.
 */

import { RealtimeClient } from 'openai-realtime-api';
import { getApiUrl } from '../utils/apiConfig';

interface VoiceConnectionConfig {
  sessionId?: string;
  relayServerUrl?: string;
  onConnected?: () => void;
  onDisconnected?: () => void;
  onError?: (error: any) => void;
  onTranscript?: (text: string, final: boolean, itemId?: string) => void;
  onAudioResponse?: (audioData: Int16Array) => void;
  onToolCall?: (toolName: string, args: any) => void;
  onToolResult?: (toolName: string, result: any) => void;
}

type ConversationHistory = Array<Record<string, unknown>>;
interface BasicConversationItem {
  id?: string;
  type?: string;
  status?: string;
  role?: string;
  name?: string;
  arguments?: any;
}

export class OpenAIRealtimeService {
  private client: RealtimeClient;
  private config: VoiceConnectionConfig;
  private connected: boolean = false;
  private sessionId: string;
  private apiKey: string = '';
  private relaySessionId: string | null = null;

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
    const client = this.client as any;
    
    // Error events (connection failures, etc.)
    client.on('error', (event: any) => {
      console.error('🔴 RealtimeClient error:', event);
      this.connected = false;
      this.config.onError?.(event);
      this.config.onDisconnected?.();
    });
    
    // Raw server/client events for debugging
    client.on('realtime.event', ({ source, event }: { source: string; event: any }) => {
      // Handle session.created as connection confirmation
      if (source === 'server' && event.type === 'session.created') {
        this.connected = true;
        if (this.config.onConnected) {
          this.config.onConnected();
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
    client.on('conversation.interrupted', () => {
      console.log('Conversation interrupted (user started speaking)');
      // Stop any current audio playback
    });

    // CORRECT STT Events: User speech transcription (input audio)
    client.on('conversation.item.input_audio_transcription.delta', (event: { item_id: string; delta?: string }) => {
      if (!event.delta) {
        return;
      }

      console.log('📝 [STT DELTA] User speech transcription:', event.delta);
      const messageKey = `user-${event.item_id}`;
      const existing = currentMessages.get(messageKey) ?? { role: 'user', content: '' };
      existing.content += event.delta;
      currentMessages.set(messageKey, existing);

      this.config.onTranscript?.(existing.content, false, event.item_id);
    });

    client.on('conversation.item.input_audio_transcription.completed', (event: { item_id: string; transcript?: string }) => {
      if (!event.transcript) {
        return;
      }

      console.log('✅ [STT COMPLETE] Final user transcript:', event.transcript);
      const messageKey = `user-${event.item_id}`;
      currentMessages.set(messageKey, { role: 'user', content: event.transcript });
      this.config.onTranscript?.(event.transcript, true, event.item_id);
    });

    client.on('conversation.item.input_audio_transcription.failed', (event: { error?: unknown }) => {
      console.error('❌ [STT FAILED]', event.error);
    });

    // TTS Events: Assistant speech output
    client.on('response.output_audio_transcript.delta', (event: { delta?: string }) => {
      console.log('🔊 [TTS TRANSCRIPT] Assistant speech:', event.delta);
      // Transcript only - actual audio comes from response.audio.delta
    });

    // CRITICAL: TTS Audio Data - This is what we actually play back! (GA event)
    client.on('response.output_audio.delta', (event: { delta?: string }) => {
      if (event.delta) {
        console.log('🔊 [TTS AUDIO] Received audio chunk:', event.delta.length, 'bytes');
        // Convert base64 to Int16Array for playback
        const audioData = this.base64ToInt16Array(event.delta);
        console.log('🔊 [TTS AUDIO] Converted to Int16Array:', audioData.length, 'samples');
        console.log('🔊 [TTS AUDIO] Calling onAudioResponse callback');
        this.config.onAudioResponse?.(audioData);
        console.log('🔊 [TTS AUDIO] onAudioResponse callback completed');
      }
    });

    client.on('response.output_audio.done', (_event: any) => {
      console.log('✅ [TTS AUDIO] Complete');
    });
    client.on('response.done', (_event: any) => {
      console.log('✅ [TTS RESPONSE] Complete');
    });

    // Conversation item events (for monitoring)
    // Legacy VAD events (may not fire in passive mode with turn_detection: none)
    client.on('input_audio_buffer.speech_started', () => {
      console.log('🎤 [VAD] User started speaking');
    });
    client.on('input_audio_buffer.speech_stopped', () => {
      console.log('🛑 [VAD] User stopped speaking');
      // In passive mode (turn_detection: none), we may need to manually commit
      // But GA events should handle transcription automatically
    });

    // Clear messages when completed to avoid stale partial transcripts
    client.on('conversation.item.completed', ({ item }: { item: BasicConversationItem }) => {
      console.log(`✅ [COMPLETED] Item completed - Type: ${item.type}, Role: ${item.role}, Status: ${item.status}`);

      if (item.type === 'message') {
        const messageKey = `${item.role}-${item.id}`;

        if (item.role === 'user') {
          const finalMessage = currentMessages.get(messageKey);
          if (finalMessage?.content) {
            this.config.onTranscript?.(finalMessage.content, true, item.id);
          }
        }

        currentMessages.delete(messageKey);
      }

      if (item.type === 'function_call') {
        this.config.onToolCall?.(item.name || 'unknown', item.arguments);
      }
    });
    
  }

  /**
   * Configure session with server-side voice activity detection
   * This enables automatic turn detection so the model responds when user stops speaking
   */
  private async updateSession(): Promise<void> {
    if (!this.client) {
    }

    console.log('⚙️ Configuring session with server_vad turn detection...');

    try {
      const client: any = this.client as any;
      if (typeof client.updateSession === 'function') {
        await client.updateSession({
          turn_detection: {
            type: 'server_vad',
            threshold: 0.5,              // Voice activity detection sensitivity (0.0-1.0)
            silence_duration_ms: 500,    // Silence duration before ending turn (ms)
            prefix_padding_ms: 100       // Audio to include before speech starts (ms)
          },
          modalities: ['text', 'audio'],  // Enable both text and audio responses
          voice: 'alloy',                 // OpenAI voice model
          input_audio_transcription: {    // Enable user speech transcription
            model: 'whisper-1'
          }
        });
      } else if (client.session && typeof client.session.update === 'function') {
        await client.session.update({
          turn_detection: {
            type: 'server_vad',
            threshold: 0.5,
            silence_duration_ms: 500,
            prefix_padding_ms: 100
          },
          modalities: ['text', 'audio'],
          voice: 'alloy',
          input_audio_transcription: {
            model: 'whisper-1'
          }
        });
      } else {
        console.warn('⚠️ RealtimeClient instance does not expose updateSession API; skipping configuration');
      }

      console.log('✅ Session configured successfully with automatic turn detection');
    } catch (error) {
      console.error('❌ Failed to update session:', error);
      throw error;
    }
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

      // Track relay session identifier so orchestrator queries can align
      this.relaySessionId = sessionData.session_id || sessionData.id || null;
      if (this.relaySessionId) {
        this.sessionId = this.relaySessionId;
      }

      // Store API key for TTS endpoint
      this.apiKey = sessionData.api_key || sessionData.client_secret?.value || '';

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
      // Now create the client with the relay URL
      // We pass a dummy API key since the relay server handles the real API key
      // The SDK requires an API key to create proper WebSocket subprotocols
      this.client = new RealtimeClient({
        url: relayUrl,
        apiKey: this.apiKey || 'relay-server',  // Use real key if available
        dangerouslyAllowAPIKeyInBrowser: true  // Allow API key in browser context
      });
      
      // Set up event handlers on the new client
      this.setupEventHandlers();

      // FIXED: RealtimeClient.connect() handles connection internally
      // Success is indicated by session.created event, not explicit return
      await this.client.connect();

      // Configure session with automatic turn detection after connection
      await this.updateSession();

    } catch (error: any) {
      console.error('❌ Failed to connect to OpenAI Realtime API:', error);
      console.error('ℹ️  OpenAI Realtime API requires beta access. Visit https://platform.openai.com/settings');

      // Enhanced error message for user
      const enhancedError = new Error(
        error.message + '\n\n' +
        '⚠️ OpenAI Realtime API requires beta access.\n' +
        'Please visit https://platform.openai.com/settings to request access.'
      );

      this.connected = false;
      this.relaySessionId = null;
      this.config.onError?.(enhancedError);
      this.config.onDisconnected?.();
      throw enhancedError;
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
      console.error('❌ Cannot send TTS: Not connected to OpenAI');
      throw new Error('Not connected to OpenAI Realtime API');
    }

    console.log('🔊 [TTS] Creating assistant message for TTS');

    // Step 1: Add assistant message to conversation
    (this.client as any).realtime.send('conversation.item.create', {
      item: {
        type: 'message',
        role: 'assistant',
        content: [{ type: 'text', text }]
      }
    });

    // Step 2: Trigger audio-only response with conversation: "none"
    // This generates TTS for the assistant message without GPT adding its own response
    (this.client as any).realtime.send('response.create', {
      response: {
        output_modalities: ['audio'],  // GA parameter
        instructions: 'Generate audio output for the previous assistant message exactly as written.',
        conversation: 'none'
      }
    } as any);

    console.log('✅ [TTS] Waiting for response.audio.delta events');
  }
  
  sendAudioData(audioData: Int16Array): void {
    if (!this.connected) {
      throw new Error('Not connected to OpenAI Realtime API');
    }

    console.log('📤 Sending', audioData.length, 'audio samples to OpenAI Realtime API');
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

    // GA-compliant: Only cancel active RESPONSE items (not other in-progress items)
    const items = this.client.conversation.getItems() as BasicConversationItem[];
    const activeResponse = items.find((item: BasicConversationItem) =>
      item.type === 'response' && item.status === 'in_progress'
    );

    if (activeResponse?.id) {
      try {
        this.client.cancelResponse(activeResponse.id, 0);
        console.log('🛑 Cancelled active response:', activeResponse.id);
      } catch (err) {
        // Ignore "response_cancel_not_active" errors (race condition)
        console.warn('⚠️ Cancel failed (response may have completed):', err);
      }
    } else {
      console.log('ℹ️ No active response to cancel');
    }
  }

  /**
   * Convert base64 encoded PCM16 audio to Int16Array for playback
   */
  private base64ToInt16Array(base64: string): Int16Array {
    // Decode base64 to binary string
    const binaryString = atob(base64);

    // Create Uint8Array from binary string
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    // Convert to Int16Array (PCM16 format)
    const int16Array = new Int16Array(bytes.buffer);

    return int16Array;
  }

  getConversationHistory(): ConversationHistory {
    return this.client.conversation.getItems() as unknown as ConversationHistory;
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
