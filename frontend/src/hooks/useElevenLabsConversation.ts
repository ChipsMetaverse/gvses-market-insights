import { useState, useRef, useCallback, useEffect } from 'react';
import { ElevenLabsConnectionManager } from '../services/ElevenLabsConnectionManager';

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
  
  const connectionManager = useRef(ElevenLabsConnectionManager.getInstance());
  const listenerId = useRef(crypto.randomUUID());
  const audioQueueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);

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

  // Register callbacks with connection manager
  useEffect(() => {
    const id = listenerId.current;
    
    connectionManager.current.addListener(id, {
      apiUrl: apiUrl,
      onUserTranscript: (transcript) => {
        const message: ElevenLabsMessage = {
          role: 'user',
          content: transcript,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, message]);
        onUserTranscript?.(transcript);
      },
      onAgentResponse: (response) => {
        const message: ElevenLabsMessage = {
          role: 'assistant',
          content: response,
          timestamp: new Date().toISOString()
        };
        setMessages(prev => [...prev, message]);
        onAgentResponse?.(response);
      },
      onAudioChunk: (audioBase64) => {
        audioQueueRef.current.push(audioBase64);
        playNextAudio();
        onAudioChunk?.(audioBase64);
      },
      onConnectionChange: (connected) => {
        setIsConnected(connected);
        onConnectionChange?.(connected);
        if (!connected) {
          setIsLoading(false);
        }
      }
    });
    
    // Check if already connected
    if (connectionManager.current.isConnected()) {
      setIsConnected(true);
    }
    
    return () => {
      connectionManager.current.removeListener(id);
    };
  }, [apiUrl, onUserTranscript, onAgentResponse, onAudioChunk, onConnectionChange, playNextAudio]);

  // Start conversation
  const startConversation = useCallback(async (agentId?: string) => {
    if (isConnected) {
      console.log('Already connected');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    // Add timeout to prevent stuck loading state
    const timeoutId = setTimeout(() => {
      console.warn('ElevenLabs connection timeout - clearing loading state');
      setIsLoading(false);
      setError('Connection timeout - please try again');
    }, 15000); // 15 second timeout
    
    try {
      await connectionManager.current.getConnection(apiUrl, agentId);
      clearTimeout(timeoutId);
      // Connection status will be updated via the listener
      setIsLoading(false); // Clear loading state after successful connection
    } catch (err) {
      clearTimeout(timeoutId);
      setError(err instanceof Error ? err.message : 'Failed to start conversation');
      setIsLoading(false);
    }
  }, [isConnected, apiUrl]);

  // Stop conversation
  const stopConversation = useCallback(() => {
    connectionManager.current.closeConnection();
    audioQueueRef.current = [];
  }, []);

  // Send text message
  const sendTextMessage = useCallback((text: string) => {
    connectionManager.current.sendTextMessage(text);
  }, []);

  // Send audio chunk
  const sendAudioChunk = useCallback((audioBase64: string) => {
    connectionManager.current.sendAudioChunk(audioBase64);
  }, []);

  // No cleanup needed - connection persists via singleton

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