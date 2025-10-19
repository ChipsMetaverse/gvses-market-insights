/**
 * Realtime SDK Conversation Hook
 * Uses the new RealtimeSDKProvider for end-to-end voice evaluation
 * Provides direct OpenAI Realtime + Agents SDK integration
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { RealtimeSDKProvider } from '../providers/RealtimeSDKProvider';
import { ProviderFactory } from '../providers/ProviderFactory';
import { useOpenAIAudioProcessor } from './useOpenAIAudioProcessor';
import { AudioChunk } from '../providers/types';
import { chartControlService } from '../services/chartControlService';

interface RealtimeSDKMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  source: 'voice' | 'text';
  toolsUsed?: string[];
  data?: Record<string, any>;
}

interface UseRealtimeSDKConfig {
  onMessage?: (message: RealtimeSDKMessage) => void;
  onConnectionChange?: (connected: boolean) => void;
  onError?: (error: string) => void;
  onThinking?: (thinking: boolean) => void;
  voice?: string;
}

export const useRealtimeSDKConversation = (config: UseRealtimeSDKConfig = {}) => {
  const {
    onMessage,
    onConnectionChange,
    onError,
    onThinking,
    voice = 'alloy'
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<RealtimeSDKMessage[]>([]);

  const providerRef = useRef<RealtimeSDKProvider | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<Int16Array[]>([]);
  const isPlayingRef = useRef(false);

  // Microphone audio processor
  const audioProcessor = useOpenAIAudioProcessor({
    onAudioData: (audioData: Int16Array) => {
      if (providerRef.current && isConnected) {
        // Convert Int16Array to base64 AudioChunk
        const audioChunk: AudioChunk = {
          data: btoa(String.fromCharCode(...new Uint8Array(audioData.buffer))),
          format: 'pcm',
          sampleRate: 24000,
          channels: 1
        };
        providerRef.current.sendAudio(audioChunk);
      }
    },
    onError: (err) => {
      console.error('RealtimeSDK: Microphone error:', err);
      const errorMessage = err.message || 'Microphone access failed';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  });

  const { isRecording, startRecording, stopRecording } = audioProcessor;

  // Initialize audio context
  const initializeAudioContext = useCallback(async () => {
    if (!audioContextRef.current) {
      try {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        if (audioContextRef.current.state === 'suspended') {
          await audioContextRef.current.resume();
        }
      } catch (error) {
        console.error('Failed to initialize audio context:', error);
        setError('Audio initialization failed');
        onError?.('Audio initialization failed');
      }
    }
  }, [onError]);

  // Play audio chunk
  const playAudioChunk = useCallback(async (audioData: Int16Array) => {
    if (!audioContextRef.current) return;

    try {
      const audioBuffer = audioContextRef.current.createBuffer(1, audioData.length, 24000);
      const channelData = audioBuffer.getChannelData(0);
      
      // Convert Int16Array to Float32Array
      for (let i = 0; i < audioData.length; i++) {
        channelData[i] = audioData[i] / 32768.0;
      }

      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      source.start();
    } catch (error) {
      console.error('Audio playback error:', error);
    }
  }, []);

  // Process audio queue
  const processAudioQueue = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) return;
    
    isPlayingRef.current = true;
    
    while (audioQueueRef.current.length > 0) {
      const audioData = audioQueueRef.current.shift();
      if (audioData) {
        await playAudioChunk(audioData);
        await new Promise(resolve => setTimeout(resolve, 50)); // Small delay between chunks
      }
    }
    
    isPlayingRef.current = false;
  }, [playAudioChunk]);

  // Start conversation
  const startConversation = useCallback(async () => {
    if (isConnected || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      console.log('🎙️ Starting RealtimeSDK conversation...');
      
      await initializeAudioContext();
      
      // Create provider if not exists
      if (!providerRef.current) {
        const factory = ProviderFactory.getInstance();
        const config = factory.createRealtimeSDKConfig(undefined, voice);
        providerRef.current = await factory.createProvider<RealtimeSDKProvider>(config);

        // Set up event listeners
        providerRef.current.on('connected', () => {
          console.log('✅ RealtimeSDK provider connected');
          setIsConnected(true);
          setIsLoading(false);
          onConnectionChange?.(true);
        });

        providerRef.current.on('disconnected', () => {
          console.log('❌ RealtimeSDK provider disconnected');
          setIsConnected(false);
          setIsLoading(false);
          onConnectionChange?.(false);
        });

        providerRef.current.on('message', (message: any) => {
          console.log('📨 RealtimeSDK message:', message);
          
          const newMessage: RealtimeSDKMessage = {
            id: message.id,
            role: message.role,
            content: message.content,
            timestamp: message.timestamp,
            source: 'voice',
            data: message.metadata
          };

          setMessages(prev => [...prev, newMessage]);
          onMessage?.(newMessage);
        });

        providerRef.current.on('transcript', (text: string) => {
          console.log('📝 RealtimeSDK transcript:', text);
          // User transcript already handled in message event
        });

        providerRef.current.on('audio', (audioChunk: AudioChunk) => {
          // Convert base64 audio to Int16Array and queue for playback
          try {
            const binaryString = atob(audioChunk.data);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
              bytes[i] = binaryString.charCodeAt(i);
            }
            const int16Array = new Int16Array(bytes.buffer);
            
            audioQueueRef.current.push(int16Array);
            processAudioQueue();
          } catch (error) {
            console.error('Audio processing error:', error);
          }
        });

        providerRef.current.on('toolCall', ({ name, arguments: args }: any) => {
          console.log('🔧 RealtimeSDK tool call:', name, args);
          setIsThinking(true);
          onThinking?.(true);
        });

        providerRef.current.on('toolResult', ({ name, result }: any) => {
          console.log('✅ RealtimeSDK tool result:', name, result);
          setIsThinking(false);
          onThinking?.(false);
        });

        providerRef.current.on('error', (errorMsg: string) => {
          console.error('❌ RealtimeSDK error:', errorMsg);
          setError(errorMsg);
          setIsLoading(false);
          onError?.(errorMsg);
        });
      }

      // Start the conversation
      await providerRef.current.startConversation();
      
      // Start microphone recording
      await startRecording();

    } catch (error) {
      console.error('Failed to start RealtimeSDK conversation:', error);
      const errorMessage = error instanceof Error ? error.message : 'Connection failed';
      setError(errorMessage);
      setIsLoading(false);
      onError?.(errorMessage);
    }
  }, [isConnected, isLoading, voice, initializeAudioContext, onConnectionChange, onMessage, onError, onThinking, startRecording, processAudioQueue]);

  // Stop conversation
  const stopConversation = useCallback(async () => {
    console.log('🛑 Stopping RealtimeSDK conversation...');
    
    try {
      // Stop microphone
      await stopRecording();
      
      // Stop provider
      if (providerRef.current) {
        await providerRef.current.stopConversation();
      }
      
      setIsConnected(false);
      setIsLoading(false);
      setIsThinking(false);
      onConnectionChange?.(false);
      onThinking?.(false);
    } catch (error) {
      console.error('Error stopping RealtimeSDK conversation:', error);
    }
  }, [stopRecording, onConnectionChange, onThinking]);

  // Send text message
  const sendTextMessage = useCallback(async (text: string) => {
    if (!providerRef.current || !isConnected) {
      console.warn('Cannot send text: not connected to RealtimeSDK');
      return;
    }

    try {
      await providerRef.current.sendMessage(text);
      
      // Process chart commands if present
      try {
        const result = await chartControlService.parseAgentResponse(text);
        if (result.commands.length > 0) {
          console.log('🎯 RealtimeSDK extracted chart commands:', result.commands);
          // Chart commands will be executed automatically by the service
        }
      } catch (chartError) {
        console.warn('Chart command parsing failed:', chartError);
        // Non-critical error, continue normally
      }
    } catch (error) {
      console.error('Failed to send text message:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      setError(errorMessage);
      onError?.(errorMessage);
    }
  }, [isConnected, onError]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Get conversation history
  const getConversationHistory = useCallback((): Array<{ role: string; content: string }> => {
    return messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));
  }, [messages]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (providerRef.current) {
        providerRef.current.disconnect();
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  return {
    // State
    isConnected,
    isLoading,
    isThinking,
    isRecording,
    error,
    messages,
    
    // Actions
    startConversation,
    stopConversation,
    sendTextMessage,
    clearMessages,
    getConversationHistory,
    
    // Provider access
    provider: providerRef.current
  };
};