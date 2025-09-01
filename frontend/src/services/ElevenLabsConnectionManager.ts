/**
 * Singleton WebSocket Connection Manager for ElevenLabs
 * Ensures only one WebSocket connection is created and properly managed
 * Implements architecture-compliant singleton pattern as specified in mermaid.md
 */

export interface ConnectionConfig {
  apiUrl: string;
  agentId?: string;
  onUserTranscript?: (transcript: string) => void;
  onAgentResponse?: (response: string) => void;
  onAudioChunk?: (audioBase64: string) => void;
  onConnectionChange?: (connected: boolean) => void;
}

export class ElevenLabsConnectionManager {
  private static instance: ElevenLabsConnectionManager | null = null;
  private websocket: WebSocket | null = null;
  private signedUrlPromise: Promise<string> | null = null;
  private connectionPromise: Promise<WebSocket> | null = null;
  private signedUrlCache: { url: string; timestamp: number } | null = null;
  private listeners: Map<string, ConnectionConfig> = new Map();
  
  private constructor() {
    // Private constructor ensures singleton pattern
  }
  
  /**
   * Get the singleton instance
   */
  static getInstance(): ElevenLabsConnectionManager {
    if (!this.instance) {
      this.instance = new ElevenLabsConnectionManager();
    }
    return this.instance;
  }
  
  /**
   * Add a listener for WebSocket events
   */
  addListener(id: string, config: ConnectionConfig): void {
    this.listeners.set(id, config);
  }
  
  /**
   * Remove a listener
   */
  removeListener(id: string): void {
    this.listeners.delete(id);
  }
  
  /**
   * Get or create a WebSocket connection
   * This ensures only one connection exists at any time
   */
  async getConnection(apiUrl: string, agentId?: string): Promise<WebSocket> {
    // Return existing open connection
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      console.log('[ConnectionManager] Returning existing open WebSocket');
      return this.websocket;
    }
    
    // Return existing connection attempt if in progress
    if (this.connectionPromise) {
      console.log('[ConnectionManager] Connection already in progress, returning existing promise');
      return this.connectionPromise;
    }
    
    // Create new connection (only once!)
    console.log('[ConnectionManager] Creating new WebSocket connection');
    this.connectionPromise = this.createConnection(apiUrl, agentId);
    
    try {
      const ws = await this.connectionPromise;
      return ws;
    } catch (error) {
      // Clear promise on error so retry is possible
      this.connectionPromise = null;
      throw error;
    }
  }
  
  /**
   * Get signed URL from backend (with caching to prevent duplicate requests)
   */
  private async getSignedUrl(apiUrl: string, agentId?: string): Promise<string> {
    // Cache signed URL for 5 minutes to prevent duplicate requests
    if (this.signedUrlCache && Date.now() - this.signedUrlCache.timestamp < 300000) {
      console.log('[ConnectionManager] Using cached signed URL');
      return this.signedUrlCache.url;
    }
    
    // Prevent concurrent signed URL requests
    if (this.signedUrlPromise) {
      console.log('[ConnectionManager] Signed URL request already in progress');
      return this.signedUrlPromise;
    }
    
    console.log('[ConnectionManager] Fetching new signed URL');
    this.signedUrlPromise = fetch(`${apiUrl}/elevenlabs/signed-url${agentId ? `?agent_id=${agentId}` : ''}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to get signed URL');
        return res.json();
      })
      .then(data => {
        this.signedUrlCache = { url: data.signed_url, timestamp: Date.now() };
        this.signedUrlPromise = null;
        console.log('[ConnectionManager] Signed URL cached successfully');
        return data.signed_url;
      })
      .catch(error => {
        this.signedUrlPromise = null;
        throw error;
      });
    
    return this.signedUrlPromise;
  }
  
  /**
   * Create a new WebSocket connection
   */
  private async createConnection(apiUrl: string, agentId?: string): Promise<WebSocket> {
    try {
      // Get signed URL (will use cache if available)
      const signedUrl = await this.getSignedUrl(apiUrl, agentId);
      
      // Create WebSocket
      const ws = new WebSocket(signedUrl);
      
      // Set up event handlers
      ws.onopen = () => {
        console.log('[ConnectionManager] WebSocket connected!');
        this.websocket = ws;
        this.connectionPromise = null;
        
        // Notify all listeners
        this.listeners.forEach(listener => {
          listener.onConnectionChange?.(true);
        });
        
        // Send initialization message
        const initMessage = {
          type: 'conversation_initiation_client_data'
        };
        console.log('[ConnectionManager] Sending init message:', initMessage);
        ws.send(JSON.stringify(initMessage));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('[ConnectionManager] Message type:', data.type);
        
        switch (data.type) {
          case 'user_transcript':
            const userTranscript = data.user_transcription_event?.user_transcript;
            if (userTranscript) {
              this.listeners.forEach(listener => {
                listener.onUserTranscript?.(userTranscript);
              });
            }
            break;
            
          case 'agent_response':
            const agentResponse = data.agent_response_event?.agent_response;
            if (agentResponse) {
              this.listeners.forEach(listener => {
                listener.onAgentResponse?.(agentResponse);
              });
            }
            break;
            
          case 'agent_response_correction':
            const correctedResponse = data.agent_response_correction_event?.corrected_agent_response;
            if (correctedResponse) {
              this.listeners.forEach(listener => {
                listener.onAgentResponse?.(correctedResponse);
              });
            }
            break;
            
          case 'audio':
            const audioBase64 = data.audio_event?.audio_base_64;
            if (audioBase64) {
              this.listeners.forEach(listener => {
                listener.onAudioChunk?.(audioBase64);
              });
            }
            break;
            
          case 'ping':
            // Respond to ping to keep connection alive
            const eventId = data.ping_event?.event_id;
            const pingMs = data.ping_event?.ping_ms || 0;
            
            setTimeout(() => {
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                  type: 'pong',
                  event_id: eventId
                }));
              }
            }, pingMs);
            break;
            
          case 'interruption':
            console.log('[ConnectionManager] Conversation interrupted:', data.interruption_event?.reason);
            break;
        }
      };
      
      ws.onerror = (error) => {
        console.error('[ConnectionManager] WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('[ConnectionManager] WebSocket closed');
        this.websocket = null;
        this.connectionPromise = null;
        
        // Notify all listeners
        this.listeners.forEach(listener => {
          listener.onConnectionChange?.(false);
        });
      };
      
      // Wait for connection to open
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          if (ws.readyState !== WebSocket.OPEN) {
            ws.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);
        
        ws.addEventListener('open', () => {
          clearTimeout(timeout);
          resolve(ws);
        });
        
        ws.addEventListener('error', () => {
          clearTimeout(timeout);
          reject(new Error('WebSocket connection failed'));
        });
      });
      
    } catch (error) {
      this.connectionPromise = null;
      throw error;
    }
  }
  
  /**
   * Send text message through WebSocket
   */
  sendTextMessage(text: string): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        type: 'user_message',
        text: text
      }));
    } else {
      console.warn('[ConnectionManager] Cannot send text - WebSocket not connected');
    }
  }
  
  /**
   * Send audio chunk through WebSocket
   */
  sendAudioChunk(audioBase64: string): void {
    if (this.websocket?.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify({
        user_audio_chunk: audioBase64
      }));
    }
  }
  
  /**
   * Close the WebSocket connection
   */
  closeConnection(): void {
    console.log('[ConnectionManager] Closing WebSocket connection');
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.connectionPromise = null;
    
    // Notify all listeners
    this.listeners.forEach(listener => {
      listener.onConnectionChange?.(false);
    });
  }
  
  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.websocket?.readyState === WebSocket.OPEN;
  }
  
  /**
   * Clear the signed URL cache (useful for forcing a new URL)
   */
  clearCache(): void {
    this.signedUrlCache = null;
  }
}