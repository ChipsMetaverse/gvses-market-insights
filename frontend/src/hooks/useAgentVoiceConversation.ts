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
import {
  normalizeChartCommandPayload,
  type ChartCommandPayload,
} from '../utils/chartCommandUtils';
import { getApiUrl } from '../utils/apiConfig';
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

  const executeChartCommands = useCallback(async (payload: ChartCommandPayload) => {
    if (!payload.responseText && payload.legacy.length === 0 && payload.structured.length === 0) {
      return;
    }

    try {
      await enhancedChartControl.processEnhancedResponse(
        payload.responseText || '',
        payload.legacy,
        payload.structured
      );
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

      const userMessage: AgentVoiceMessage = {
        id: `user-${Date.now()}-${Math.random()}`,
        role: 'user',
        content: userTranscript,
        timestamp: new Date().toISOString(),
        source
      };

      setMessages(prev => [...prev, userMessage]);
      callbacksRef.current.onMessage?.(userMessage);

      conversationHistoryRef.current.push({
        role: 'user',
        content: userTranscript
      });

      const history = conversationHistoryRef.current.slice(-10);

      const assistantMessageId = `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const placeholderMessage: AgentVoiceMessage = {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        source,
        toolsUsed: [],
        data: {}
      };

      setMessages(prev => [...prev, placeholderMessage]);

      const updateAssistantMessage = (updater: (msg: AgentVoiceMessage) => AgentVoiceMessage) => {
        setMessages(prev => prev.map(msg => (msg.id === assistantMessageId ? updater(msg) : msg)));
      };

      let streamingText = '';
      let structuredOutput: any = null;
      let chartPayloadFromStream: ChartCommandPayload | null = null;
      const streamingTools = new Set<string>();
      let streamingData: Record<string, any> = {};
      let streamingSucceeded = false;

      try {
        await agentOrchestratorService.streamQuery(
          userTranscript,
          history,
          chartContext,
          (chunk) => {
            if (!chunk) return;

            switch (chunk.type) {
              case 'content':
                if (chunk.text) {
                  streamingText += chunk.text;
                  updateAssistantMessage(prev => ({
                    ...prev,
                    content: streamingText,
                  }));
                }
                break;

              case 'structured':
                structuredOutput = chunk.data;
                streamingData = {
                  ...streamingData,
                  structured_output: structuredOutput,
                };
                updateAssistantMessage(prev => ({
                  ...prev,
                  data: streamingData,
                }));
                break;

              case 'tool_start':
              case 'tool_result':
                // Tool telemetry is emitted by BackendAgentProvider; log for debugging if needed
                break;

              case 'done':
                chartPayloadFromStream = normalizeChartCommandPayload(
                  {
                    chart_commands: chunk.chart_commands,
                    chart_commands_structured: chunk.chart_commands_structured,
                  },
                  streamingText,
                );

                if (chunk.tools_used) {
                  chunk.tools_used.forEach(tool => streamingTools.add(tool));
                }

                if (chartPayloadFromStream.legacy.length) {
                  streamingData = {
                    ...streamingData,
                    chart_commands: chartPayloadFromStream.legacy,
                  };
                }

                if (chartPayloadFromStream.structured.length) {
                  streamingData = {
                    ...streamingData,
                    chart_commands_structured: chartPayloadFromStream.structured,
                  };
                }

                updateAssistantMessage(prev => ({
                  ...prev,
                  data: streamingData,
                }));
                break;
            }
          }
        );

        streamingSucceeded = true;
      } catch (streamErr) {
        console.error('Agent streaming failed, falling back to non-streaming response:', streamErr);
      }

      let finalAssistantMessage: AgentVoiceMessage | null = null;
      let finalChartPayload: ChartCommandPayload | null = null;

      if (streamingSucceeded) {
        const finalTools = Array.from(streamingTools);

        if (structuredOutput) {
          streamingData = {
            ...streamingData,
            structured_output: structuredOutput,
          };
        }

        if (!chartPayloadFromStream) {
          chartPayloadFromStream = normalizeChartCommandPayload(null, streamingText);
        }

        if (chartPayloadFromStream.legacy.length) {
          streamingData = {
            ...streamingData,
            chart_commands: chartPayloadFromStream.legacy,
          };
        }

        if (chartPayloadFromStream.structured.length) {
          streamingData = {
            ...streamingData,
            chart_commands_structured: chartPayloadFromStream.structured,
          };
        }

        const finalizedMessage: AgentVoiceMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: streamingText,
          timestamp: new Date().toISOString(),
          source,
          toolsUsed: finalTools.length ? finalTools : undefined,
          data: streamingData,
        };

        updateAssistantMessage(() => finalizedMessage);
        finalAssistantMessage = finalizedMessage;
        finalChartPayload = chartPayloadFromStream;
      } else {
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));

        const agentResponse: AgentResponse = await agentOrchestratorService.sendQuery(
          userTranscript,
          history,
          chartContext
        );

        const fallbackPayload = normalizeChartCommandPayload(
          {
            legacy: agentResponse.chart_commands || agentResponse.data?.chart_commands,
            chart_commands_structured:
              agentResponse.chart_commands_structured || agentResponse.data?.chart_commands_structured,
          },
          agentResponse.text,
        );

        const mergedData = { ...(agentResponse.data || {}) };
        if (fallbackPayload.legacy.length) {
          mergedData.chart_commands = fallbackPayload.legacy;
        }
        if (fallbackPayload.structured.length) {
          mergedData.chart_commands_structured = fallbackPayload.structured;
        }

        const fallbackMessage: AgentVoiceMessage = {
          id: assistantMessageId,
          role: 'assistant',
          content: agentResponse.text,
          timestamp: new Date().toISOString(),
          source,
          toolsUsed: agentResponse.tools_used,
          data: mergedData
        };

        setMessages(prev => [...prev, fallbackMessage]);
        finalAssistantMessage = fallbackMessage;
        finalChartPayload = fallbackPayload;
      }

      if (!finalAssistantMessage) {
        throw new Error('Agent response unavailable');
      }

      await executeChartCommands(
        finalChartPayload ?? { legacy: [], structured: [], responseText: finalAssistantMessage.content }
      );

      callbacksRef.current.onMessage?.(finalAssistantMessage);

      conversationHistoryRef.current.push({
        role: 'assistant',
        content: finalAssistantMessage.content
      });

      const actuallyConnected = openAIServiceRef.current?.isConnected() || false;
      if (source === 'voice' && openAIServiceRef.current && actuallyConnected) {
        openAIServiceRef.current.sendTextMessage(finalAssistantMessage.content);
      } else if (source === 'voice' && openAIServiceRef.current && !actuallyConnected) {
        setTimeout(() => {
          const retryConnected = openAIServiceRef.current?.isConnected() || false;
          if (retryConnected) {
            openAIServiceRef.current?.sendTextMessage(finalAssistantMessage.content);
          }
        }, 100);
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
  }, [chartContext, executeChartCommands, isConnected]);

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
        onError: (error: unknown) => {
          console.error('Agent Voice: OpenAI error:', error);
          const errorMessage = error instanceof Error
            ? error.message
            : typeof error === 'string'
              ? error
              : 'Voice connection error';
          setError(errorMessage);
          setIsLoading(false);
          setIsConnected(false);
          callbacksRef.current.onConnectionChange?.(false);
          callbacksRef.current.onError?.(errorMessage);
        },
        onTranscript: (text: string, final: boolean) => {
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
        const errorMessage = err instanceof Error ? err.message : String(err ?? 'Connection failed');
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
