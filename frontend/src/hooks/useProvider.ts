/**
 * useProvider Hook
 * React hook for easy provider system integration
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  providerManager,
  providerConfigManager,
  type BaseProvider,
  type ProviderConfig,
  type Message,
  type AudioChunk,
  type ConnectionState,
  type ProviderEventHandlers
} from '../providers';

export interface UseProviderOptions {
  autoConnect?: boolean;
  defaultProvider?: string;
  eventHandlers?: Partial<ProviderEventHandlers>;
}

export interface UseProviderReturn {
  // Provider state
  currentProvider: BaseProvider | null;
  connectionState: ConnectionState | null;
  isConnected: boolean;
  isConnecting: boolean;
  error: string | null;
  
  // Provider management
  switchProvider: (config: ProviderConfig) => Promise<void>;
  switchToElevenLabs: (agentId: string, apiUrl?: string) => Promise<void>;
  switchToOpenAI: (apiKey: string, model?: string) => Promise<void>;
  switchToClaude: (apiKey: string, model?: string) => Promise<void>;
  disconnect: () => Promise<void>;
  connect: () => Promise<void>;
  
  // Messaging
  sendMessage: (message: string, context?: string[]) => Promise<void>;
  streamMessage: (message: string, context?: string[]) => AsyncGenerator<string>;
  
  // Voice functionality
  startVoiceConversation: () => Promise<void>;
  stopVoiceConversation: () => Promise<void>;
  sendAudio: (audioChunk: AudioChunk) => Promise<void>;
  
  // Provider info
  availableProviders: Array<{ type: string; name: string; available: boolean }>;
  providerCapabilities: any;
  providerInfo: any;
  
  // Configuration
  allowProviderSwitching: boolean;
  showProviderSelector: boolean;
  
  // Event handling
  messages: Message[];
  clearMessages: () => void;
}

export function useProvider(options: UseProviderOptions = {}): UseProviderReturn {
  const {
    autoConnect = true,
    defaultProvider,
    eventHandlers = {}
  } = options;

  // State
  const [currentProvider, setCurrentProvider] = useState<BaseProvider | null>(null);
  const [connectionState, setConnectionState] = useState<ConnectionState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);

  // Refs for stable callbacks
  const eventHandlersRef = useRef(eventHandlers);
  eventHandlersRef.current = eventHandlers;

  // Initialize provider system
  useEffect(() => {
    const initializeProvider = async () => {
      try {
        // Set up event handlers
        providerManager.setEventHandlers({
          onMessage: (message: Message) => {
            setMessages(prev => [...prev, message]);
            eventHandlersRef.current.onMessage?.(message);
          },
          onAudio: (audio: AudioChunk) => {
            eventHandlersRef.current.onAudio?.(audio);
          },
          onTranscript: (transcript: string) => {
            eventHandlersRef.current.onTranscript?.(transcript);
          },
          onConnectionChange: (state: ConnectionState) => {
            setConnectionState(state);
            eventHandlersRef.current.onConnectionChange?.(state);
          },
          onError: (errorMessage: string) => {
            setError(errorMessage);
            eventHandlersRef.current.onError?.(errorMessage);
          }
        });

        // Initialize with default provider if specified
        let defaultConfig: ProviderConfig | null = null;
        
        if (defaultProvider) {
          defaultConfig = providerConfigManager.getProviderConfig(defaultProvider);
        }
        
        if (!defaultConfig) {
          defaultConfig = providerConfigManager.getDefaultProviderConfig();
        }
        
        if (!defaultConfig) {
          defaultConfig = providerConfigManager.getFirstAvailableProvider();
        }

        if (defaultConfig && autoConnect) {
          await providerManager.initialize(defaultConfig);
          setCurrentProvider(providerManager.getCurrentProvider());
        }

        setIsInitialized(true);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to initialize provider';
        setError(errorMessage);
        console.error('Provider initialization error:', err);
      }
    };

    initializeProvider();
  }, [defaultProvider, autoConnect]);

  // Provider management functions
  const switchProvider = useCallback(async (config: ProviderConfig) => {
    setError(null);
    try {
      await providerManager.switchProvider(config);
      setCurrentProvider(providerManager.getCurrentProvider());
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to switch provider';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const switchToElevenLabs = useCallback(async (agentId: string, apiUrl?: string) => {
    await providerManager.switchToElevenLabs(agentId, apiUrl);
    setCurrentProvider(providerManager.getCurrentProvider());
  }, []);

  const switchToOpenAI = useCallback(async (apiKey: string, model?: string) => {
    await providerManager.switchToOpenAI(apiKey, model);
    setCurrentProvider(providerManager.getCurrentProvider());
  }, []);

  const switchToClaude = useCallback(async (apiKey: string, model?: string) => {
    await providerManager.switchToClaude(apiKey, model);
    setCurrentProvider(providerManager.getCurrentProvider());
  }, []);

  const connect = useCallback(async () => {
    setError(null);
    try {
      await providerManager.connect();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const disconnect = useCallback(async () => {
    try {
      await providerManager.disconnect();
    } catch (err) {
      console.error('Disconnect error:', err);
    }
  }, []);

  // Messaging functions
  const sendMessage = useCallback(async (message: string, context?: string[]) => {
    setError(null);
    try {
      await providerManager.sendMessage(message, context);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const streamMessage = useCallback(async function* (message: string, context?: string[]) {
    setError(null);
    try {
      yield* providerManager.streamMessage(message, context);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to stream message';
      setError(errorMessage);
      throw err;
    }
  }, []);

  // Voice functions
  const startVoiceConversation = useCallback(async () => {
    setError(null);
    try {
      await providerManager.startVoiceConversation();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start voice conversation';
      setError(errorMessage);
      throw err;
    }
  }, []);

  const stopVoiceConversation = useCallback(async () => {
    try {
      await providerManager.stopVoiceConversation();
    } catch (err) {
      console.error('Stop voice conversation error:', err);
    }
  }, []);

  const sendAudio = useCallback(async (audioChunk: AudioChunk) => {
    setError(null);
    try {
      await providerManager.sendAudio(audioChunk);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send audio';
      setError(errorMessage);
      throw err;
    }
  }, []);

  // Utility functions
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Derived state
  const isConnected = connectionState === 'connected';
  const isConnecting = connectionState === 'connecting';
  const availableProviders = providerConfigManager.getAvailableProviders();
  const providerCapabilities = providerManager.getProviderCapabilities();
  const providerInfo = providerManager.getCurrentProviderInfo();
  const allowProviderSwitching = providerConfigManager.isProviderSwitchingAllowed();
  const showProviderSelector = providerConfigManager.shouldShowProviderSelector();

  return {
    // Provider state
    currentProvider,
    connectionState,
    isConnected,
    isConnecting,
    error,
    
    // Provider management
    switchProvider,
    switchToElevenLabs,
    switchToOpenAI,
    switchToClaude,
    disconnect,
    connect,
    
    // Messaging
    sendMessage,
    streamMessage,
    
    // Voice functionality
    startVoiceConversation,
    stopVoiceConversation,
    sendAudio,
    
    // Provider info
    availableProviders,
    providerCapabilities,
    providerInfo,
    
    // Configuration
    allowProviderSwitching,
    showProviderSelector,
    
    // Event handling
    messages,
    clearMessages
  };
}

// Additional hooks for specific use cases
export function useVoiceProvider(options: UseProviderOptions = {}) {
  const provider = useProvider(options);
  
  return {
    ...provider,
    // Voice-specific helpers
    hasVoiceCapability: provider.providerCapabilities?.voiceConversation || false,
    canRecord: provider.providerCapabilities?.speechToText || false,
    canSpeak: provider.providerCapabilities?.textToSpeech || false
  };
}

export function useChatProvider(options: UseProviderOptions = {}) {
  const provider = useProvider(options);
  
  return {
    ...provider,
    // Chat-specific helpers
    hasChatCapability: provider.providerCapabilities?.textChat || false,
    hasStreamingCapability: provider.providerCapabilities?.streaming || false,
    hasToolsCapability: provider.providerCapabilities?.tools || false
  };
}