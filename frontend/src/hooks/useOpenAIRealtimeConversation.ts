import { useState, useRef, useCallback, useEffect } from 'react';
import { OpenAIRealtimeService } from '../services/OpenAIRealtimeService';

interface OpenAIMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface UseOpenAIRealtimeConfig {
  onUserTranscript?: (transcript: string) => void;
  onAgentResponse?: (response: string) => void;
  onAudioChunk?: (audioBase64: string) => void;
  onConnectionChange?: (connected: boolean) => void;
  onToolCall?: (toolName: string, arguments: any) => void;
  onToolResult?: (toolName: string, result: any) => void;
  apiUrl?: string;
  sessionId?: string;
  relayServerUrl?: string;
}

export const useOpenAIRealtimeConversation = (config: UseOpenAIRealtimeConfig = {}) => {
  const {
    onUserTranscript,
    onAgentResponse,
    onAudioChunk,
    onConnectionChange,
    onToolCall,
    onToolResult,
    apiUrl = 'http://localhost:8000',
    sessionId,
    relayServerUrl
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<OpenAIMessage[]>([]);
  
  const serviceRef = useRef<OpenAIRealtimeService | null>(null);
  const audioQueueRef = useRef<Int16Array[]>([]);
  const isPlayingRef = useRef(false);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Initialize audio context
  const initAudioContext = useCallback(async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext({ sampleRate: 24000 });
      
      // Resume context if suspended (required by many browsers)
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }
    }
    return audioContextRef.current;
  }, []);

  // Play audio queue - handles Int16Array PCM audio from OpenAI
  const playNextAudio = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isPlayingRef.current = true;
    const audioData = audioQueueRef.current.shift();
    
    if (audioData) {
      try {
        const audioContext = await initAudioContext();
        
        // Convert Int16 PCM to Float32 for Web Audio API
        const floatArray = new Float32Array(audioData.length);
        for (let i = 0; i < audioData.length; i++) {
          floatArray[i] = audioData[i] / 32768.0; // Convert from Int16 to Float32
        }

        // Create audio buffer
        const audioBuffer = audioContext.createBuffer(1, floatArray.length, 24000);
        audioBuffer.copyToChannel(floatArray, 0);

        // Create and play audio source
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        
        source.onended = () => {
          isPlayingRef.current = false;
          playNextAudio(); // Play next in queue
        };
        
        source.start();
      } catch (err) {
        console.error('Error playing OpenAI audio:', err);
        isPlayingRef.current = false;
        playNextAudio(); // Try next audio even if this one failed
      }
    } else {
      isPlayingRef.current = false;
    }
  }, [initAudioContext]);

  // Initialize OpenAI Realtime Service
  useEffect(() => {
    if (!serviceRef.current) {
      const finalRelayUrl = relayServerUrl || `${apiUrl.replace('http', 'ws')}/openai/realtime/ws`;
      
      serviceRef.current = new OpenAIRealtimeService({
        sessionId: sessionId,
        relayServerUrl: finalRelayUrl,
        onConnected: () => {
          setIsConnected(true);
          setIsLoading(false);
          onConnectionChange?.(true);
        },
        onDisconnected: () => {
          setIsConnected(false);
          setIsLoading(false);
          onConnectionChange?.(false);
        },
        onError: (error) => {
          console.error('OpenAI Realtime error:', error);
          setError(error?.message || 'OpenAI connection error');
          setIsLoading(false);
          setIsConnected(false);
          onConnectionChange?.(false);
        },
        onTranscript: (text, final) => {
          if (final) {
            // Assistant transcript (final)
            const message: OpenAIMessage = {
              role: 'assistant',
              content: text,
              timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, message]);
            onAgentResponse?.(text);
          } else {
            // User transcript (interim)
            const message: OpenAIMessage = {
              role: 'user',
              content: text,
              timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, message]);
            onUserTranscript?.(text);
          }
        },
        onAudioResponse: (audioData: Int16Array) => {
          // Queue audio for playback
          audioQueueRef.current.push(audioData);
          playNextAudio();
          
          // Convert to base64 for compatibility with existing interface
          if (onAudioChunk) {
            const audioBase64 = btoa(String.fromCharCode(...new Uint8Array(audioData.buffer)));
            onAudioChunk(audioBase64);
          }
        },
        onToolCall: (toolName: string, args: any) => {
          console.log('OpenAI tool called:', toolName, args);
          onToolCall?.(toolName, args);
        },
        onToolResult: (toolName: string, result: any) => {
          console.log('OpenAI tool result:', toolName, result);
          onToolResult?.(toolName, result);
        }
      });
    }

    return () => {
      // Cleanup on unmount
      if (serviceRef.current) {
        serviceRef.current.disconnect();
        serviceRef.current = null;
      }
    };
  }, [apiUrl, sessionId, relayServerUrl, onUserTranscript, onAgentResponse, onAudioChunk, onConnectionChange, onToolCall, onToolResult, playNextAudio]);

  // Start conversation
  const startConversation = useCallback(async (agentId?: string) => {
    if (isConnected) {
      console.log('Already connected to OpenAI Realtime');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      if (serviceRef.current) {
        await serviceRef.current.connect();
        // Connection status will be updated via the onConnected callback
      } else {
        throw new Error('OpenAI service not initialized');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect to OpenAI Realtime';
      setError(errorMessage);
      setIsLoading(false);
      console.error('Failed to start OpenAI conversation:', err);
    }
  }, [isConnected]);

  // Stop conversation
  const stopConversation = useCallback(() => {
    if (serviceRef.current) {
      serviceRef.current.disconnect();
    }
    audioQueueRef.current = [];
    isPlayingRef.current = false;
  }, []);

  // Send text message
  const sendTextMessage = useCallback((text: string) => {
    if (serviceRef.current && isConnected) {
      serviceRef.current.sendTextMessage(text);
    } else {
      console.warn('Cannot send text message - not connected to OpenAI Realtime');
    }
  }, [isConnected]);

  // Send audio chunk (expects base64 encoded audio for compatibility)
  const sendAudioChunk = useCallback((audioBase64: string) => {
    if (serviceRef.current && isConnected) {
      try {
        // Convert base64 back to Int16Array for OpenAI
        const binaryString = atob(audioBase64);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }
        const int16Array = new Int16Array(bytes.buffer);
        serviceRef.current.sendAudioData(int16Array);
      } catch (err) {
        console.error('Failed to decode audio chunk:', err);
      }
    } else {
      console.warn('Cannot send audio chunk - not connected to OpenAI Realtime');
    }
  }, [isConnected]);

  // Additional OpenAI-specific methods
  const createResponse = useCallback(() => {
    if (serviceRef.current && isConnected) {
      serviceRef.current.createResponse();
    }
  }, [isConnected]);

  const interruptResponse = useCallback(() => {
    if (serviceRef.current && isConnected) {
      serviceRef.current.interruptResponse();
    }
  }, [isConnected]);

  const getConversationHistory = useCallback(() => {
    if (serviceRef.current) {
      return serviceRef.current.getConversationHistory();
    }
    return [];
  }, []);

  const getAvailableTools = useCallback(() => {
    if (serviceRef.current) {
      return serviceRef.current.getAvailableTools();
    }
    return [];
  }, []);

  return {
    // Standard interface (compatible with useElevenLabsConversation)
    isConnected,
    isLoading,
    error,
    messages,
    startConversation,
    stopConversation,
    sendTextMessage,
    sendAudioChunk,
    
    // OpenAI-specific additional methods
    createResponse,
    interruptResponse,
    getConversationHistory,
    getAvailableTools,
    
    // Service instance for advanced usage
    service: serviceRef.current
  };
};