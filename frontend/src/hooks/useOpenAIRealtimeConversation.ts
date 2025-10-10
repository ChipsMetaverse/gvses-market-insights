import { useState, useRef, useCallback, useEffect } from 'react';
import { OpenAIRealtimeService } from '../services/OpenAIRealtimeService';
import { getApiUrl } from '../utils/apiConfig';
import { useOpenAIAudioProcessor } from './useOpenAIAudioProcessor';

interface OpenAIMessage {
  id: string;
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
  console.log('%c🎯 [HOOK INIT] useOpenAIRealtimeConversation HOOK CALLED', 'background: #222; color: #bada55; font-size: 16px; font-weight: bold;');

  const {
    onUserTranscript,
    onAgentResponse,
    onAudioChunk,
    onConnectionChange,
    onToolCall,
    onToolResult,
    apiUrl = getApiUrl(),
    sessionId,
    relayServerUrl
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  console.log('%c🎯 [HOOK INIT] Initial isConnected state:', 'background: #222; color: #bada55', isConnected);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<OpenAIMessage[]>([]);

  // Log whenever isConnected changes
  useEffect(() => {
    console.log('%c🔔 [STATE CHANGE] isConnected changed to:', 'background: #ff6b6b; color: white; font-size: 14px; font-weight: bold;', isConnected);
  }, [isConnected]);

  const serviceRef = useRef<OpenAIRealtimeService | null>(null);
  const audioQueueRef = useRef<Int16Array[]>([]);
  const isPlayingRef = useRef(false);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Microphone audio processor for OpenAI Realtime
  const audioProcessor = useOpenAIAudioProcessor({
    onAudioData: (audioData: Int16Array) => {
      // Send microphone audio to OpenAI
      if (serviceRef.current && isConnected) {
        console.log('🎤 Sending', audioData.length, 'audio samples to OpenAI');
        serviceRef.current.sendAudioData(audioData);
      }
    },
    onError: (err) => {
      console.error('Microphone error:', err);
      setError(err.message);
    }
  });
  
  // Store current callback refs to prevent re-renders
  const callbacksRef = useRef({
    onUserTranscript,
    onAgentResponse,
    onAudioChunk,
    onConnectionChange,
    onToolCall,
    onToolResult
  });
  
  // Update callback refs when they change
  useEffect(() => {
    callbacksRef.current = {
      onUserTranscript,
      onAgentResponse,
      onAudioChunk,
      onConnectionChange,
      onToolCall,
      onToolResult
    };
  });

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
      console.log('🔊 playNextAudio: Skipping - isPlaying:', isPlayingRef.current, 'queueLength:', audioQueueRef.current.length);
      return;
    }

    console.log('🔊 playNextAudio: Starting playback');
    isPlayingRef.current = true;
    const audioData = audioQueueRef.current.shift();

    if (audioData) {
      try {
        console.log('🔊 playNextAudio: Got audio data with', audioData.length, 'samples');
        const audioContext = await initAudioContext();
        console.log('🔊 playNextAudio: Audio context initialized, state:', audioContext.state);

        // Ensure AudioContext is running (required for browser autoplay policies)
        if (audioContext.state === 'suspended') {
          console.log('🔊 playNextAudio: AudioContext suspended, attempting to resume...');
          await audioContext.resume();
          console.log('🔊 playNextAudio: AudioContext resumed, new state:', audioContext.state);
        }

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
          console.log('🔊 playNextAudio: Playback ended');
          isPlayingRef.current = false;
          playNextAudio(); // Play next in queue
        };

        console.log('🔊 playNextAudio: Starting audio playback now...');
        source.start();
        console.log('🔊 playNextAudio: Audio playback started!');
      } catch (err) {
        console.error('🔊 Error playing OpenAI audio:', err);
        isPlayingRef.current = false;
        playNextAudio(); // Try next audio even if this one failed
      }
    } else {
      console.log('🔊 playNextAudio: No audio data, clearing playing flag');
      isPlayingRef.current = false;
    }
  }, [initAudioContext]);

  // Extract recording functions from audioProcessor
  const { isRecording, startRecording, stopRecording } = audioProcessor;

  console.log('🔄 [RENDER] Component rendered with isConnected:', isConnected, 'isRecording:', isRecording);

  // Initialize OpenAI Realtime Service
  useEffect(() => {
    if (!serviceRef.current) {
      serviceRef.current = new OpenAIRealtimeService({
        sessionId: sessionId,
        onConnected: () => {
          console.log('🔧 [HOOK onConnected] ========== CALLBACK RECEIVED ==========');
          console.log('🔧 [HOOK onConnected] About to call setIsConnected(true)');
          setIsConnected(true);
          console.log('🔧 [HOOK onConnected] setIsConnected(true) COMPLETED');
          console.log('🔧 [HOOK onConnected] Setting isLoading to false');
          setIsLoading(false);
          console.log('🔧 [HOOK onConnected] About to call external onConnectionChange callback');
          callbacksRef.current.onConnectionChange?.(true);
          console.log('🔧 [HOOK onConnected] ========== CALLBACK COMPLETED ==========');
        },
        onDisconnected: () => {
          setIsConnected(false);
          setIsLoading(false);
          callbacksRef.current.onConnectionChange?.(false);
        },
        onError: (error) => {
          console.error('OpenAI Realtime error:', error);
          setError(error?.message || 'OpenAI connection error');
          setIsLoading(false);
          setIsConnected(false);
          callbacksRef.current.onConnectionChange?.(false);
        },
        onTranscript: (text, final, messageId) => {
          if (final) {
            // Assistant transcript (final) - accumulated from deltas
            const msgId = messageId || `assistant-${Date.now()}-${Math.random()}`;
            
            setMessages(prev => {
              // Check if message already exists
              const existingIndex = prev.findIndex(m => m.id === msgId);
              
              if (existingIndex >= 0) {
                // Update existing message
                const updated = [...prev];
                updated[existingIndex] = {
                  ...updated[existingIndex],
                  content: text
                };
                return updated;
              } else {
                // Create new message
                const newMessage: OpenAIMessage = {
                  id: msgId,
                  role: 'assistant',
                  content: text,
                  timestamp: new Date().toISOString()
                };
                return [...prev, newMessage];
              }
            });
            
            callbacksRef.current.onAgentResponse?.(text);
          } else {
            // User transcript (interim) - accumulated from deltas
            const msgId = messageId || `user-${Date.now()}-${Math.random()}`;
            
            setMessages(prev => {
              // Check if message already exists
              const existingIndex = prev.findIndex(m => m.id === msgId);
              
              if (existingIndex >= 0) {
                // Update existing message
                const updated = [...prev];
                updated[existingIndex] = {
                  ...updated[existingIndex],
                  content: text
                };
                return updated;
              } else {
                // Create new message
                const newMessage: OpenAIMessage = {
                  id: msgId,
                  role: 'user',
                  content: text,
                  timestamp: new Date().toISOString()
                };
                return [...prev, newMessage];
              }
            });
            
            callbacksRef.current.onUserTranscript?.(text);
          }
        },
        onAudioResponse: (audioData: Int16Array) => {
          console.log('🔊 HOOK: Audio received, queuing for playback:', audioData.length, 'samples');
          console.log('🔊 HOOK: Current queue length:', audioQueueRef.current.length);
          console.log('🔊 HOOK: Is playing:', isPlayingRef.current);

          // Queue audio for playback
          audioQueueRef.current.push(audioData);
          playNextAudio();

          // Convert to base64 for compatibility with existing interface
          if (callbacksRef.current.onAudioChunk) {
            const audioBase64 = btoa(String.fromCharCode(...new Uint8Array(audioData.buffer)));
            callbacksRef.current.onAudioChunk(audioBase64);
          }
        },
        onToolCall: (toolName: string, args: any) => {
          console.log('OpenAI tool called:', toolName, args);
          callbacksRef.current.onToolCall?.(toolName, args);
        },
        onToolResult: (toolName: string, result: any) => {
          console.log('OpenAI tool result:', toolName, result);
          callbacksRef.current.onToolResult?.(toolName, result);
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
  }, [sessionId]); // Service builds URLs dynamically via session endpoint

  // Start conversation
  const startConversation = useCallback(async (agentId?: string) => {
    if (isConnected) {
      console.log('Already connected to OpenAI Realtime');
      return;
    }

    setIsLoading(true);
    setError(null);

    console.log('🎙️ [START] Step 1: Requesting microphone access BEFORE connecting...');

    // CRITICAL: Request microphone FIRST, before connecting to OpenAI
    // This follows the official OpenAI Realtime API pattern
    try {
      await startRecording();
      console.log('✅ [START] Microphone access granted and recording started');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Microphone access denied';
      setError(errorMessage);
      setIsLoading(false);
      console.error('❌ [START] Failed to start microphone:', err);
      return; // Don't proceed with connection if microphone fails
    }

    // Initialize and resume AudioContext on user interaction (required for browser autoplay policies)
    try {
      const audioContext = await initAudioContext();
      if (audioContext.state === 'suspended') {
        console.log('🔊 Resuming AudioContext on user interaction...');
        await audioContext.resume();
        console.log('🔊 AudioContext state after resume:', audioContext.state);
      }
    } catch (err) {
      console.warn('Failed to initialize AudioContext:', err);
    }

    console.log('🌐 [START] Step 2: Connecting to OpenAI Realtime API...');

    // Add timeout to prevent stuck loading state
    const timeoutId = setTimeout(() => {
      console.warn('OpenAI Realtime connection timeout - clearing loading state');
      setIsLoading(false);
      setError('Connection timeout - please try again');
    }, 15000); // 15 second timeout

    try {
      if (serviceRef.current) {
        await serviceRef.current.connect();
        clearTimeout(timeoutId);
        console.log('✅ [START] Connected to OpenAI Realtime API');
        // Connection status will be updated via the onConnected callback
      } else {
        clearTimeout(timeoutId);
        throw new Error('OpenAI service not initialized');
      }
    } catch (err) {
      clearTimeout(timeoutId);
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect to OpenAI Realtime';
      setError(errorMessage);
      setIsLoading(false);
      // Stop recording if connection fails
      stopRecording();
      console.error('Failed to start OpenAI conversation:', err);
    }
  }, [isConnected, startRecording, stopRecording, initAudioContext]);

  // Stop conversation
  const stopConversation = useCallback(() => {
    // Stop microphone recording
    if (isRecording) {
      stopRecording();
    }

    // Disconnect service
    if (serviceRef.current) {
      serviceRef.current.disconnect();
    }

    // Clear audio playback queue
    audioQueueRef.current = [];
    isPlayingRef.current = false;
  }, [isRecording, stopRecording]);

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
