/**
 * Agent Voice Conversation Hook
 * Integrates OpenAI Realtime API (for voice I/O) with our internal agent orchestrator (for intelligence)
 * 
 * Flow:
 * 1. User speaks → OpenAI STT → transcript
 * 2. Transcript → Agent Orchestrator → intelligent response
 * 3. Response → OpenAI TTS → voice output
 * 4. Both transcript and response displayed in chat
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { agentOrchestratorService, type AgentResponse } from '../services/agentOrchestratorService';
import { OpenAIRealtimeService } from '../services/OpenAIRealtimeService';
import { getApiUrl } from '../utils/apiConfig';
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';

interface AgentVoiceMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  source: 'voice' | 'text';
  toolsUsed?: string[];
  data?: Record<string, any>;
}

interface UseAgentVoiceConfig {
  onMessage?: (message: AgentVoiceMessage) => void;
  onConnectionChange?: (connected: boolean) => void;
  onError?: (error: string) => void;
  onThinking?: (thinking: boolean) => void;
  apiUrl?: string;
  sessionId?: string;
}

export const useAgentVoiceConversation = (config: UseAgentVoiceConfig = {}) => {
  const {
    onMessage,
    onConnectionChange,
    onError,
    onThinking,
    apiUrl = getApiUrl(),
    sessionId
  } = config;

  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<AgentVoiceMessage[]>([]);
  const [backendHealthy, setBackendHealthy] = useState<boolean | null>(null);
  
  const openAIServiceRef = useRef<OpenAIRealtimeService | null>(null);
  const audioQueueRef = useRef<Int16Array[]>([]);
  const isPlayingRef = useRef(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const conversationHistoryRef = useRef<Array<{ role: string; content: string }>>([]);

  // Store current callback refs to prevent re-renders
  const callbacksRef = useRef({
    onMessage,
    onConnectionChange,
    onError,
    onThinking
  });


  // Update callback refs
  useEffect(() => {
    callbacksRef.current = {
      onMessage,
      onConnectionChange,
      onError,
      onThinking
    };
  }, [onMessage, onConnectionChange, onError, onThinking]);

  // Check backend health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${apiUrl}/health`);
        if (response.ok) {
          const data = await response.json();
          // Check if openai_relay.active is true
          setBackendHealthy(data.openai_relay?.active === true);
        } else {
          setBackendHealthy(false);
        }
      } catch (err) {
        console.error('Health check failed:', err);
        setBackendHealthy(false);
      }
    };
    
    checkHealth();
    // Recheck health every 30 seconds
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [apiUrl]);

  // Initialize audio context
  const initAudioContext = useCallback(async () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new AudioContext();
      if (audioContextRef.current.state === 'suspended') {
        await audioContextRef.current.resume();
      }
    }
    return audioContextRef.current;
  }, []);

  // Play audio queue
  const playNextAudio = useCallback(async () => {
    if (isPlayingRef.current || audioQueueRef.current.length === 0) {
      return;
    }

    isPlayingRef.current = true;
    const audioData = audioQueueRef.current.shift();
    
    if (audioData) {
      try {
        const audioContext = await initAudioContext();
        const floatArray = new Float32Array(audioData.length);
        
        // Convert Int16Array to Float32Array
        for (let i = 0; i < audioData.length; i++) {
          floatArray[i] = audioData[i] / 32768.0;
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
        console.error('Error playing agent voice audio:', err);
        isPlayingRef.current = false;
        playNextAudio(); // Try next audio even if this one failed
      }
    } else {
      isPlayingRef.current = false;
    }
  }, [initAudioContext]);

  const executeChartCommands = useCallback(async (commands?: string[]) => {
    if (!commands || commands.length === 0) {
      return;
    }

    const serialized = commands.join(' ');
    try {
      await enhancedChartControl.processEnhancedResponse(serialized);
    } catch (err) {
      console.error('Enhanced chart command processing failed:', err);
      try {
        const parsed = await chartControlService.parseAgentResponse(serialized);
        for (const command of parsed) {
          chartControlService.executeCommand(command);
        }
      } catch (fallbackErr) {
        console.error('Fallback chart command execution failed:', fallbackErr);
      }
    }
  }, []);

  // Send text to agent and get TTS response
  const sendToAgent = useCallback(async (userTranscript: string, source: 'voice' | 'text' = 'voice') => {
    try {
      setIsThinking(true);
      callbacksRef.current.onThinking?.(true);

      // Add user message immediately
      const userMessage: AgentVoiceMessage = {
        id: `user-${Date.now()}-${Math.random()}`,
        role: 'user',
        content: userTranscript,
        timestamp: new Date().toISOString(),
        source
      };
      
      setMessages(prev => [...prev, userMessage]);
      callbacksRef.current.onMessage?.(userMessage);

      // Update conversation history
      conversationHistoryRef.current.push({
        role: 'user',
        content: userTranscript
      });

      // Send to agent orchestrator
      const agentResponse: AgentResponse = await agentOrchestratorService.sendQuery(
        userTranscript,
        conversationHistoryRef.current.slice(-10) // Last 10 messages for context
      );

      await executeChartCommands(agentResponse.chart_commands || agentResponse.data?.chart_commands);

      const mergedData = { ...(agentResponse.data || {}) };
      if (agentResponse.chart_commands?.length) {
        mergedData.chart_commands = agentResponse.chart_commands;
      }

      // Add agent message
      const assistantMessage: AgentVoiceMessage = {
        id: `assistant-${Date.now()}-${Math.random()}`,
        role: 'assistant',
        content: agentResponse.text,
        timestamp: new Date().toISOString(),
        source,
        toolsUsed: agentResponse.tools_used,
        data: mergedData
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      callbacksRef.current.onMessage?.(assistantMessage);

      // Update conversation history
      conversationHistoryRef.current.push({
        role: 'assistant',
        content: agentResponse.text
      });

      // If this was a voice interaction, send response to TTS
      if (source === 'voice' && openAIServiceRef.current && isConnected) {
        try {
          console.log('Sending agent response to OpenAI for TTS:', agentResponse.text);
          openAIServiceRef.current.sendTextMessage(agentResponse.text);
        } catch (ttsError) {
          console.warn('TTS failed, but text response is available:', ttsError);
        }
      }

    } catch (err) {
      console.error('Agent orchestrator error:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to get agent response';
      setError(errorMessage);
      callbacksRef.current.onError?.(errorMessage);
    } finally {
      setIsThinking(false);
      callbacksRef.current.onThinking?.(false);
    }
  }, [isConnected, executeChartCommands]);

  // Initialize OpenAI Realtime Service (voice I/O only)
  useEffect(() => {
    if (!openAIServiceRef.current) {
      openAIServiceRef.current = new OpenAIRealtimeService({
        sessionId: sessionId,
        onConnected: () => {
          console.log('Agent Voice: OpenAI connected for voice I/O');
          setIsConnected(true);
          setIsLoading(false);
          callbacksRef.current.onConnectionChange?.(true);
        },
        onDisconnected: () => {
          console.log('Agent Voice: OpenAI disconnected');
          setIsConnected(false);
          setIsLoading(false);
          callbacksRef.current.onConnectionChange?.(false);
        },
        onError: (error) => {
          console.error('Agent Voice: OpenAI error:', error);
          const errorMessage = error?.message || 'Voice connection error';
          setError(errorMessage);
          setIsLoading(false);
          setIsConnected(false);
          callbacksRef.current.onConnectionChange?.(false);
          callbacksRef.current.onError?.(errorMessage);
        },
        onTranscript: (text, final) => {
          if (final) {
            // User spoke - send FINAL transcript to agent orchestrator
            console.log('Agent Voice: User final transcript received:', text);
            sendToAgent(text, 'voice');
          }
          // We ignore partial transcripts and assistant transcripts
        },
        onAudioResponse: (audioData: Int16Array) => {
          // Queue audio for playback
          audioQueueRef.current.push(audioData);
          playNextAudio();
        },
        // Tool calls are handled by the agent orchestrator, not OpenAI directly
        onToolCall: () => {},
        onToolResult: () => {}
      });
    }

    return () => {
      // Cleanup
      if (openAIServiceRef.current) {
        openAIServiceRef.current.disconnect();
        openAIServiceRef.current = null;
      }
    };
  }, [sessionId]); // Removed sendToAgent and playNextAudio to prevent unnecessary re-renders

  // Connect/disconnect functions
  const connect = useCallback(async () => {
    // Check backend health before attempting connection
    if (backendHealthy === false) {
      const errorMessage = 'Backend not ready. Please check server status.';
      setError(errorMessage);
      callbacksRef.current.onError?.(errorMessage);
      return;
    }
    
    if (openAIServiceRef.current && !isConnected && !isLoading) {
      setIsLoading(true);
      setError(null);
      try {
        await openAIServiceRef.current.connect();
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Connection failed';
        setError(errorMessage);
        setIsLoading(false);
        callbacksRef.current.onError?.(errorMessage);
      }
    }
  }, [isConnected, isLoading, backendHealthy]);

  const disconnect = useCallback(() => {
    if (openAIServiceRef.current && isConnected) {
      openAIServiceRef.current.disconnect();
    }
  }, [isConnected]);

  // Send text message (for text-only interactions)
  const sendTextMessage = useCallback(async (text: string) => {
    await sendToAgent(text, 'text');
  }, [sendToAgent]);

  // Clear conversation
  const clearConversation = useCallback(() => {
    setMessages([]);
    conversationHistoryRef.current = [];
    agentOrchestratorService.newSession();
  }, []);

  return {
    // State
    isConnected,
    isLoading,
    isThinking,
    error,
    messages,
    backendHealthy,
    
    // Actions
    connect,
    disconnect,
    sendTextMessage,
    clearConversation,
    
    // Utility
    sessionId: agentOrchestratorService.getSessionId()
  };
};
