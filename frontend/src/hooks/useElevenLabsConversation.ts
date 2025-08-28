import { useState, useRef, useCallback, useEffect } from 'react';

interface ElevenLabsMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface UseElevenLabsConfig {
  onUserTranscript?: (transcript: string) => void;
  onAgentResponse?: (response: string) => void;
  onAudioChunk?: (audioBase64: string) => void;
  onConnectionChange?: (connected: boolean) => void;
  apiUrl?: string;
}

export const useElevenLabsConversation = (config: UseElevenLabsConfig = {}) => {
  const {
    onUserTranscript,
    onAgentResponse,
    onAudioChunk,
    onConnectionChange,
    apiUrl = 'http://localhost:8000'
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ElevenLabsMessage[]>([]);
  
  const websocketRef = useRef<WebSocket | null>(null);
  const audioQueueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);

  // Get signed URL from backend
  const getSignedUrl = async (agentId?: string): Promise<string> => {
    const params = agentId ? `?agent_id=${agentId}` : '';
    const response = await fetch(`${apiUrl}/elevenlabs/signed-url${params}`);
    
    if (!response.ok) {
      throw new Error('Failed to get signed URL');
    }
    
    const data = await response.json();
    return data.signed_url;
  };

  // Play audio queue - handles PCM audio from ElevenLabs
  const playNextAudio = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isPlayingRef.current = true;
    const audioBase64 = audioQueueRef.current.shift();
    
    if (audioBase64) {
      try {
        // Decode base64 to binary
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

        // "RIFF" chunk descriptor
        const writeString = (offset: number, string: string) => {
          for (let i = 0; i < string.length; i++) {
            view.setUint8(offset + i, string.charCodeAt(i));
          }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, fileSize - 8, true);
        writeString(8, 'WAVE');
        
        // "fmt " sub-chunk
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
        view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
        view.setUint16(22, numChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, byteRate, true);
        view.setUint16(32, blockAlign, true);
        view.setUint16(34, bitsPerSample, true);
        
        // "data" sub-chunk
        writeString(36, 'data');
        view.setUint32(40, dataSize, true);
        
        // Write PCM data
        const dataArray = new Uint8Array(wavBuffer, 44);
        dataArray.set(bytes);

        // Create blob with WAV MIME type
        const audioBlob = new Blob([wavBuffer], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          isPlayingRef.current = false;
          playNextAudio(); // Play next in queue
        };
        
        audio.onerror = (e) => {
          console.error('Audio playback error:', e);
          URL.revokeObjectURL(audioUrl);
          isPlayingRef.current = false;
          playNextAudio(); // Try next audio even if this one failed
        };
        
        await audio.play();
      } catch (err) {
        console.error('Error playing audio:', err);
        isPlayingRef.current = false;
        playNextAudio(); // Try next audio even if this one failed
      }
    } else {
      isPlayingRef.current = false;
    }
  }, []);

  // Start conversation
  const startConversation = useCallback(async (agentId?: string) => {
    if (isConnected) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      // Get signed URL from backend
      const signedUrl = await getSignedUrl(agentId);
      
      // Create WebSocket connection
      const ws = new WebSocket(signedUrl);
      
      ws.onopen = () => {
        console.log('ElevenLabs WebSocket connected!');
        setIsConnected(true);
        setIsLoading(false);
        onConnectionChange?.(true);
        
        // Send initialization message
        const initMessage = {
          type: 'conversation_initiation_client_data'
        };
        console.log('Sending init message:', initMessage);
        ws.send(JSON.stringify(initMessage));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log('ElevenLabs message:', data.type);
        
        switch (data.type) {
          case 'user_transcript':
            const userTranscript = data.user_transcription_event?.user_transcript;
            if (userTranscript) {
              const message: ElevenLabsMessage = {
                role: 'user',
                content: userTranscript,
                timestamp: new Date().toISOString()
              };
              setMessages(prev => [...prev, message]);
              onUserTranscript?.(userTranscript);
            }
            break;
            
          case 'agent_response':
            const agentResponse = data.agent_response_event?.agent_response;
            if (agentResponse) {
              const message: ElevenLabsMessage = {
                role: 'assistant',
                content: agentResponse,
                timestamp: new Date().toISOString()
              };
              setMessages(prev => [...prev, message]);
              onAgentResponse?.(agentResponse);
            }
            break;
            
          case 'agent_response_correction':
            const correctedResponse = data.agent_response_correction_event?.corrected_agent_response;
            if (correctedResponse) {
              // Update the last assistant message
              setMessages(prev => {
                const updated = [...prev];
                for (let i = updated.length - 1; i >= 0; i--) {
                  if (updated[i].role === 'assistant') {
                    updated[i].content = correctedResponse;
                    break;
                  }
                }
                return updated;
              });
              onAgentResponse?.(correctedResponse);
            }
            break;
            
          case 'audio':
            const audioBase64 = data.audio_event?.audio_base_64;
            if (audioBase64) {
              audioQueueRef.current.push(audioBase64);
              playNextAudio();
              onAudioChunk?.(audioBase64);
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
            console.log('Conversation interrupted:', data.interruption_event?.reason);
            break;
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Connection error occurred');
      };
      
      ws.onclose = () => {
        setIsConnected(false);
        onConnectionChange?.(false);
        websocketRef.current = null;
      };
      
      websocketRef.current = ws;
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start conversation');
      setIsLoading(false);
    }
  }, [isConnected, apiUrl, onUserTranscript, onAgentResponse, onAudioChunk, onConnectionChange, playNextAudio]);

  // Stop conversation
  const stopConversation = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
    setIsConnected(false);
    onConnectionChange?.(false);
    audioQueueRef.current = [];
  }, [onConnectionChange]);

  // Send text message (corrected format per API docs)
  const sendTextMessage = useCallback((text: string) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify({
        type: 'user_message',
        text: text
      }));
    }
  }, []);

  // Send audio chunk
  const sendAudioChunk = useCallback((audioBase64: string) => {
    if (websocketRef.current?.readyState === WebSocket.OPEN) {
      websocketRef.current.send(JSON.stringify({
        user_audio_chunk: audioBase64
      }));
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (websocketRef.current) {
        websocketRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    isLoading,
    error,
    messages,
    startConversation,
    stopConversation,
    sendTextMessage,
    sendAudioChunk,
  };
};