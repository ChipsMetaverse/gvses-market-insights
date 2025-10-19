/**
 * OpenAI Realtime SDK Service
 * 
 * Integrates OpenAI Realtime API with Agents SDK workflow for end-to-end voice processing.
 * This provides:
 * - Audio-in to audio-out through single model
 * - Native tool calling with asynchronous execution
 * - Lower latency, more fluid conversations
 * - Professional responses from Agent Builder workflow
 */

interface RealtimeSDKConfig {
  apiUrl: string;
  workflowId: string;
  voice?: string;
  debug?: boolean;
}

interface ToolCall {
  id: string;
  name: string;
  parameters: Record<string, unknown>;
}

interface AudioChunk {
  data: ArrayBuffer;
  timestamp: number;
}

export class OpenAIRealtimeSDKService {
  private wsConnection: WebSocket | null = null;
  private sessionId: string | null = null;
  private audioQueue: AudioChunk[] = [];
  private isConnected = false;
  private config: RealtimeSDKConfig;
  
  // Event handlers
  private onConnectedHandler?: () => void;
  private onDisconnectedHandler?: () => void;
  private onTranscriptHandler?: (text: string) => void;
  private onAudioResponseHandler?: (audio: ArrayBuffer) => void;
  private onToolCallHandler?: (tool: ToolCall) => void;
  private onErrorHandler?: (error: Error) => void;

  constructor(config: RealtimeSDKConfig) {
    this.config = {
      voice: 'marin',
      debug: false,
      ...config
    };
  }

  /**
   * Initialize connection to backend Realtime API + Agents SDK endpoint
   */
  async connect(): Promise<void> {
    if (this.isConnected) {
      console.warn('Already connected to Realtime SDK');
      return;
    }

    try {
      // Get ephemeral token from backend
      const response = await fetch(`${this.config.apiUrl}/api/agent/realtime-token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: this.config.workflowId,
          voice: this.config.voice
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to get realtime token: ${response.statusText}`);
      }

      const { token, session_id } = await response.json();
      this.sessionId = session_id;

      // Connect via WebSocket to backend relay
      const wsUrl = this.config.apiUrl.replace('http', 'ws') + '/ws/realtime-sdk';
      this.wsConnection = new WebSocket(wsUrl);

      this.wsConnection.onopen = () => {
        if (this.config.debug) console.log('🔌 [Realtime SDK] WebSocket connected');
        
        // Authenticate session
        this.sendMessage({
          type: 'session.init',
          token,
          session_id: this.sessionId,
          workflow_id: this.config.workflowId,
          voice: this.config.voice
        });
      };

      this.wsConnection.onmessage = (event) => {
        this.handleMessage(JSON.parse(event.data));
      };

      this.wsConnection.onerror = (error) => {
        console.error('❌ [Realtime SDK] WebSocket error:', error);
        this.onErrorHandler?.(new Error('WebSocket connection error'));
      };

      this.wsConnection.onclose = () => {
        if (this.config.debug) console.log('🔌 [Realtime SDK] WebSocket closed');
        this.isConnected = false;
        this.onDisconnectedHandler?.();
      };

      // Wait for session ready
      await this.waitForConnection();

    } catch (error) {
      console.error('❌ [Realtime SDK] Connection failed:', error);
      throw error;
    }
  }

  /**
   * Disconnect from Realtime API
   */
  async disconnect(): Promise<void> {
    if (this.wsConnection) {
      this.sendMessage({ type: 'session.end' });
      this.wsConnection.close();
      this.wsConnection = null;
    }
    this.isConnected = false;
    this.sessionId = null;
  }

  /**
   * Send audio chunk to Realtime API
   */
  async sendAudio(audioData: ArrayBuffer): Promise<void> {
    if (!this.isConnected) {
      throw new Error('Not connected to Realtime SDK');
    }

    // Convert to base64 for JSON transmission
    const base64Audio = this.arrayBufferToBase64(audioData);
    
    this.sendMessage({
      type: 'input_audio_buffer.append',
      audio: base64Audio
    });
  }

  /**
   * Commit audio buffer (signal end of user speech)
   */
  async commitAudio(): Promise<void> {
    this.sendMessage({
      type: 'input_audio_buffer.commit'
    });
  }

  /**
   * Send text message (alternative to audio)
   */
  async sendText(text: string): Promise<void> {
    if (!this.isConnected) {
      throw new Error('Not connected to Realtime SDK');
    }

    this.sendMessage({
      type: 'conversation.item.create',
      item: {
        type: 'message',
        role: 'user',
        content: [{ type: 'input_text', text }]
      }
    });

    // Trigger response
    this.sendMessage({ type: 'response.create' });
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: any): void {
    if (this.config.debug) {
      console.log('📨 [Realtime SDK] Message:', message.type);
    }

    switch (message.type) {
      case 'session.created':
        this.isConnected = true;
        this.onConnectedHandler?.();
        break;

      case 'conversation.item.input_audio_transcription.completed':
        // User speech transcribed
        this.onTranscriptHandler?.(message.transcript);
        break;

      case 'response.audio.delta':
        // Streaming audio response from model
        const audioData = this.base64ToArrayBuffer(message.delta);
        this.onAudioResponseHandler?.(audioData);
        break;

      case 'response.function_call_arguments.done':
        // Agent called a tool
        this.onToolCallHandler?.({
          id: message.call_id,
          name: message.name,
          parameters: JSON.parse(message.arguments)
        });
        break;

      case 'response.done':
        // Response complete
        if (this.config.debug) console.log('✅ [Realtime SDK] Response complete');
        break;

      case 'error':
        console.error('❌ [Realtime SDK] Error:', message.error);
        this.onErrorHandler?.(new Error(message.error.message));
        break;
    }
  }

  /**
   * Send message to backend via WebSocket
   */
  private sendMessage(message: any): void {
    if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message: WebSocket not open');
      return;
    }

    this.wsConnection.send(JSON.stringify(message));
  }

  /**
   * Wait for connection to be established
   */
  private async waitForConnection(timeout = 10000): Promise<void> {
    const startTime = Date.now();
    while (!this.isConnected && Date.now() - startTime < timeout) {
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    if (!this.isConnected) {
      throw new Error('Connection timeout');
    }
  }

  /**
   * Event handlers
   */
  onConnected(handler: () => void): void {
    this.onConnectedHandler = handler;
  }

  onDisconnected(handler: () => void): void {
    this.onDisconnectedHandler = handler;
  }

  onTranscript(handler: (text: string) => void): void {
    this.onTranscriptHandler = handler;
  }

  onAudioResponse(handler: (audio: ArrayBuffer) => void): void {
    this.onAudioResponseHandler = handler;
  }

  onToolCall(handler: (tool: ToolCall) => void): void {
    this.onToolCallHandler = handler;
  }

  onError(handler: (error: Error) => void): void {
    this.onErrorHandler = handler;
  }

  /**
   * Utility: ArrayBuffer to base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  /**
   * Utility: base64 to ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
  }

  /**
   * Get connection status
   */
  get connected(): boolean {
    return this.isConnected;
  }

  /**
   * Get current session ID
   */
  get session(): string | null {
    return this.sessionId;
  }
}

