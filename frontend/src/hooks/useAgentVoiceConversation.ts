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
import { useOpenAIAudioProcessor } from './useOpenAIAudioProcessor';

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
  chartContext?: {       // NEW: Chart context to pass to agent
    symbol?: string;
    timeframe?: string;
    snapshot_id?: string;
  };
}

export const useAgentVoiceConversation = (config: UseAgentVoiceConfig = {}) => {
  const {
    onMessage,
    onConnectionChange,
    onError,
    onThinking,
    apiUrl = getApiUrl(),
    sessionId,
    chartContext  // Extract chart context
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

  // Microphone audio processor for capturing user voice
  const audioProcessor = useOpenAIAudioProcessor({
    onAudioData: (audioData: Int16Array) => {
      // Send microphone audio to OpenAI Realtime for STT
      if (openAIServiceRef.current && isConnected) {
        openAIServiceRef.current.sendAudioData(audioData);
      }
    },
    onError: (err) => {
      console.error('Agent Voice: Microphone error:', err);
      const errorMessage = err.message || 'Microphone access failed';
      setError(errorMessage);
      callbacksRef.current.onError?.(errorMessage);
    }
  });

  const { isRecording, startRecording, stopRecording } = audioProcessor;

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
      console.warn('Enhanced chart command processing failed (non-critical):', err);
      // Chart commands are optional - don't block voice assistant if they fail
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
      console.log('[AGENT VOICE] 🚀 Calling agentOrchestratorService.sendQuery() with:', {
        userTranscript,
        historyLength: conversationHistoryRef.current.length
      });

      const agentResponse: AgentResponse = await agentOrchestratorService.sendQuery(
        userTranscript,
        conversationHistoryRef.current.slice(-10), // Last 10 messages for context
        chartContext  // Pass chart context to backend
      );

      console.log('[AGENT VOICE] 📦 Received agent response:', {
        hasText: !!agentResponse.text,
        textLength: agentResponse.text?.length || 0,
        textPreview: agentResponse.text?.substring(0, 100),
        toolsUsed: agentResponse.tools_used,
        hasData: !!agentResponse.data,
        hasChartCommands: !!(agentResponse.chart_commands || agentResponse.data?.chart_commands)
      });

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
      // CRITICAL FIX: Check the OpenAI service's actual connection state, not React state
      const actuallyConnected = openAIServiceRef.current?.isConnected() || false;
      console.log('🚨 [TTS CHECK] source:', source, 'hasRef:', !!openAIServiceRef.current, 'reactState:', isConnected, 'actualConnection:', actuallyConnected);
      
      if (source === 'voice' && openAIServiceRef.current && actuallyConnected) {
        console.log('[AGENT VOICE] 🔊 Sending to TTS:', agentResponse.text.substring(0, 100));

        // Send to Realtime API for TTS
        openAIServiceRef.current.sendTextMessage(agentResponse.text);
      } else if (source === 'voice' && openAIServiceRef.current && !actuallyConnected) {
        // Handle race condition: sometimes connection succeeds but state hasn't updated yet
        console.log('⏳ [TTS CHECK] Connection state may be updating, retrying in 100ms...');
        setTimeout(() => {
          const retryConnected = openAIServiceRef.current?.isConnected() || false;
          console.log('🔄 [TTS RETRY] actualConnection after delay:', retryConnected);
          if (retryConnected) {
            console.log('[AGENT VOICE] 🔊 Sending to TTS (retry):', agentResponse.text.substring(0, 100));
            openAIServiceRef.current?.sendTextMessage(agentResponse.text);
          } else {
            console.log('🚨 [TTS RETRY] Still not connected after retry');
          }
        }, 100);
      } else {
        console.log('🚨 [TTS CHECK] TTS SKIPPED - Condition not met');
        console.log('🚨 [TTS CHECK] Reason - source:', source, 'hasRef:', !!openAIServiceRef.current, 'actuallyConnected:', actuallyConnected);
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
          console.log('🚨 [AGENT VOICE HOOK] onConnected callback FIRED');
          console.log('🚨 [AGENT VOICE HOOK] About to call setIsConnected(true)');
          
          // Force state update with React's batching
          setIsConnected(true);
          setIsLoading(false);
          setError(null);
          
          console.log('🚨 [AGENT VOICE HOOK] React state updates called');
          
          // Use setTimeout to ensure React state has updated before calling external callback
          setTimeout(() => {
            console.log('🚨 [AGENT VOICE HOOK] Delayed callback execution - state should be synchronized');
            callbacksRef.current.onConnectionChange?.(true);
            console.log('🚨 [AGENT VOICE HOOK] onConnected callback COMPLETED');
          }, 0);
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
          console.log(`🎤 [AGENT VOICE] Transcript received - Final: ${final}, Text: "${text}"`);
          if (final) {
            // User spoke - send FINAL transcript to agent orchestrator
            console.log('✅ [AGENT VOICE] User final transcript received, sending to agent:', text);
            sendToAgent(text, 'voice');
          } else {
            console.log('⏳ [AGENT VOICE] Partial transcript (waiting for final)');
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
    console.log('🚨 [CONNECT] ==================== connect() CALLED ====================');
    console.log('🚨 [CONNECT] backendHealthy:', backendHealthy);
    console.log('🚨 [CONNECT] openAIServiceRef.current exists:', !!openAIServiceRef.current);
    console.log('🚨 [CONNECT] isConnected:', isConnected);
    console.log('🚨 [CONNECT] isLoading:', isLoading);

    // Check backend health before attempting connection
    if (backendHealthy === false) {
      console.error('🚨 [CONNECT] BLOCKED: Backend not healthy');
      const errorMessage = 'Backend not ready. Please check server status.';
      setError(errorMessage);
      callbacksRef.current.onError?.(errorMessage);
      return;
    }

    console.log('🚨 [CONNECT] Backend health check PASSED');

    if (openAIServiceRef.current && !isConnected && !isLoading) {
      console.log('🚨 [CONNECT] All conditions MET - proceeding with connection');
      setIsLoading(true);
      setError(null);

      console.log('🎙️ [AGENT VOICE] Step 1: Requesting microphone access...');

      try {
        // CRITICAL: Request microphone FIRST, before connecting to OpenAI
        await startRecording();
        console.log('✅ [AGENT VOICE] Microphone access granted and recording started');

        // Now connect to OpenAI Realtime for voice I/O
        console.log('🌐 [AGENT VOICE] Step 2: Connecting to OpenAI Realtime...');
        await openAIServiceRef.current.connect();
        console.log('✅ [AGENT VOICE] Connected to OpenAI Realtime');

      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Connection failed';
        console.error('❌ [AGENT VOICE] Connection failed:', err);
        setError(errorMessage);
        setIsLoading(false);

        // Clean up microphone if it was started
        if (isRecording) {
          stopRecording();
        }

        callbacksRef.current.onError?.(errorMessage);
      }
    } else {
      console.error('🚨 [CONNECT] BLOCKED: Conditions not met');
      console.error('🚨 [CONNECT] - openAIServiceRef.current exists:', !!openAIServiceRef.current);
      console.error('🚨 [CONNECT] - isConnected (should be false):', isConnected);
      console.error('🚨 [CONNECT] - isLoading (should be false):', isLoading);
      if (!openAIServiceRef.current) {
        console.error('🚨 [CONNECT] ERROR: OpenAI service ref is null!');
      }
      if (isConnected) {
        console.error('🚨 [CONNECT] ERROR: Already connected!');
      }
      if (isLoading) {
        console.error('🚨 [CONNECT] ERROR: Already loading!');
      }
    }
  }, [isConnected, isLoading, backendHealthy, startRecording, stopRecording, isRecording]);

  const disconnect = useCallback(() => {
    console.log('🛑 [AGENT VOICE] Disconnecting...');

    // Stop microphone recording
    if (isRecording) {
      console.log('🛑 [AGENT VOICE] Stopping microphone recording');
      stopRecording();
    }

    // Disconnect OpenAI WebSocket
    if (openAIServiceRef.current && isConnected) {
      console.log('🛑 [AGENT VOICE] Closing OpenAI connection');
      openAIServiceRef.current.disconnect();
    }

    // Clear audio playback queue
    audioQueueRef.current = [];
    isPlayingRef.current = false;

    console.log('✅ [AGENT VOICE] Disconnected successfully');
  }, [isConnected, isRecording, stopRecording]);

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
    isRecording,
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
