import { useState, useEffect, useCallback, useMemo } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { AgentResponseParser } from '../services/agentResponseParser';
import { useDataPersistence } from '../hooks/useDataPersistence';
import '../styles/chatkit-branding.css';

interface RealtimeChatKitProps {
  className?: string;
  onMessage?: (message: Message) => void;
  onChartCommand?: (command: any) => void;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  provider?: string;
}

export function RealtimeChatKit({ 
  className = "h-[600px] w-full", 
  onMessage,
  onChartCommand 
}: RealtimeChatKitProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [chatKitControl, setChatKitControl] = useState<any>(null);
  const [showHistory, setShowHistory] = useState(false);
  
  // Initialize data persistence
  const {
    conversationId,
    conversationHistory,
    isSaving,
    createConversation,
    queueMessage,
    loadConversationHistory,
    getRecentConversations,
    flushMessages
  } = useDataPersistence({
    autoSave: true,
    saveInterval: 1000,
    maxBatchSize: 5
  });

  // Use the existing Agent Voice conversation hook for proper integration
  const agentVoice = useAgentVoiceConversation({
    onMessage: (agentMessage) => {
      // Convert AgentVoiceMessage to Message format for compatibility
      const message: Message = {
        id: agentMessage.id,
        role: agentMessage.role,
        content: agentMessage.content,
        timestamp: agentMessage.timestamp,
        provider: 'agent-builder'
      };
      onMessage?.(message);
      
      // Persist the message
      queueMessage(message);
      
      // Handle chart commands if present
      if (agentMessage.data?.chart_commands) {
        onChartCommand?.(agentMessage.data.chart_commands);
      }
    },
    onError: (errorMsg) => {
      setError(errorMsg);
    },
    onConnectionChange: (connected) => {
      if (!connected && !error) {
        setError('Voice connection lost');
      }
    }
  });

  const chatKitConfig = useMemo(() => ({
    api: {
      async getClientSecret(existing: any) {
        const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        try {
          const deviceId = localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`;

          const res = await fetch(`${backendUrl}/api/chatkit/session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              device_id: deviceId,
              existing_session: existing || null
            }),
          });

          if (!res.ok) {
            throw new Error(`Session failed: ${res.status} ${await res.text()}`);
          }

          const { client_secret } = await res.json();
          localStorage.setItem('chatkit_device_id', deviceId);
          console.log('✅ ChatKit session established with Agent Builder');
          return client_secret;
        } catch (err) {
          console.error('❌ ChatKit session error:', err);
          throw err;
        }
      },
    },
    onMessage: (message: any) => {
      const msg: Message = {
        id: `chatkit-${Date.now()}`,
        role: message.role,
        content: message.content,
        timestamp: new Date().toISOString(),
        provider: 'chatkit-agent-builder'
      };
      onMessage?.(msg);
      
      // Persist the message
      queueMessage(msg);

      // Enhanced agent response processing
      if (message.role === 'assistant' && message.content) {
        console.log('[ChatKit] Processing agent response:', message.content);
        
        // Check for drawing commands using the new parser
        if (AgentResponseParser.containsDrawingCommands(message.content)) {
          const chartCommands = AgentResponseParser.parseResponse(message.content);
          
          if (chartCommands.length > 0) {
            console.log('[ChatKit] Parsed chart commands:', chartCommands);
            // Send each command to the chart
            chartCommands.forEach(command => {
              console.log('[ChatKit] Sending chart command:', command);
              onChartCommand?.(command);
            });
          } else {
            console.log('[ChatKit] No chart commands found in drawing response');
          }
        }
        
        // Legacy fallback for basic chart/symbol commands
        const content = message.content.toLowerCase();
        if (content.includes('chart') || content.includes('symbol')) {
          console.log('[ChatKit] Legacy chart command detection:', message.content);
          onChartCommand?.(message.content);
        }
      }
    }
  }), [onMessage, onChartCommand]);

  const chatKitHookResult = useChatKit(chatKitConfig) as { control?: any; error?: unknown };

  // Update control when ChatKit hook result changes
  useEffect(() => {
    if (chatKitHookResult?.control) {
      setChatKitControl(chatKitHookResult.control);
      setIsLoading(false);
      console.log('✅ RealtimeChatKit initialized with Agent Builder integration');
    } else {
      setIsLoading(true);
    }
  }, [chatKitHookResult]);
  
  // Create conversation on mount if none exists
  useEffect(() => {
    if (!conversationId && !isLoading) {
      createConversation(undefined, { source: 'realtime-chatkit' });
    }
  }, [conversationId, isLoading, createConversation]);

  // Handle ChatKit hook errors
  useEffect(() => {
    if (chatKitHookResult?.error) {
      console.error('❌ ChatKit hook error:', chatKitHookResult.error);
      const errorMessage = chatKitHookResult.error instanceof Error 
        ? chatKitHookResult.error.message 
        : typeof chatKitHookResult.error === 'string'
          ? chatKitHookResult.error
          : 'ChatKit hook failed';
      setError(errorMessage);
      setIsLoading(false);
    }
  }, [chatKitHookResult]);

  // Voice connection handlers
  const handleVoiceConnect = useCallback(async () => {
    try {
      await agentVoice.connect();
    } catch (err) {
      console.error('Voice connection failed:', err);
      setError(err instanceof Error ? err.message : 'Voice connection failed');
    }
  }, [agentVoice.connect]);

  const handleVoiceDisconnect = useCallback(() => {
    agentVoice.disconnect();
  }, [agentVoice.disconnect]);

  // Error state
  if (error) {
    return (
      <div className="realtime-chatkit">
        <div className="mb-2 text-sm font-medium text-red-600">
          AI Assistant - Error
        </div>
        <div className="border rounded-lg p-4 bg-red-50 border-red-200">
          <p className="text-sm text-red-700">Failed to load ChatKit:</p>
          <p className="text-xs text-red-600 mt-1">{error}</p>
          <p className="text-xs text-gray-500 mt-2">
            The voice and chat interface will load once the connection is established.
          </p>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="realtime-chatkit">
        <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          AI Assistant
        </div>
        <div className="border rounded-lg p-4 bg-gray-50">
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          </div>
          <p className="text-sm text-gray-600 mt-2">Initializing voice and chat...</p>
        </div>
      </div>
    );
  }

  // Main interface with unified Voice + ChatKit integration
  return (
    <div className="realtime-chatkit h-full flex flex-col">
      {/* Header with Voice Controls */}
      <div className="mb-2 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
            AI Trading Assistant
          </div>
          {conversationId && (
            <div className="text-xs text-gray-500">
              {isSaving && '💾 Saving...'}
              {!isSaving && conversationHistory.length > 0 && `📝 ${conversationHistory.length} messages`}
            </div>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Voice Status Indicators */}
          {agentVoice.isThinking && (
            <div className="flex items-center gap-1 text-xs text-orange-600">
              <div className="w-2 h-2 bg-orange-500 rounded-full animate-pulse"></div>
              Thinking
            </div>
          )}
          {agentVoice.isRecording && (
            <div className="flex items-center gap-1 text-xs text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              Listening
            </div>
          )}
          {agentVoice.isConnected && (
            <div className="flex items-center gap-1 text-xs text-blue-600">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              Connected
            </div>
          )}
          
          {/* Voice Control Button */}
          <button
            onClick={agentVoice.isConnected ? handleVoiceDisconnect : handleVoiceConnect}
            className={`p-1 rounded-full transition-colors ${
              agentVoice.isConnected 
                ? 'bg-green-500 text-white hover:bg-green-600' 
                : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
            }`}
            title={agentVoice.isConnected ? 'Disconnect voice' : 'Connect voice'}
            disabled={agentVoice.isLoading}
          >
            {agentVoice.isLoading ? (
              <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            )}
          </button>
        </div>
      </div>

      {/* Backend Health Status */}
      {agentVoice.backendHealthy === false && (
        <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
          ⚠️ Backend not ready. Voice features unavailable.
        </div>
      )}

      {/* Voice/Agent Error Display */}
      {(agentVoice.error || error) && (
        <div className="mb-2 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
          Error: {agentVoice.error || error}
        </div>
      )}

      {/* Unified ChatKit + Agent Builder Interface */}
      <div className="flex-grow border rounded-lg overflow-hidden shadow-sm chatkit-container">
        {chatKitControl ? (
          <ChatKit 
            control={chatKitControl}
            domainPublicKey={import.meta.env.VITE_CHATKIT_DOMAIN_PK || "domain_pk_68f817e0d8c08190922b1575cf3ffd760e268e4f4191db83"}
            className="h-full w-full"
            style={{
              height: '100%',
              width: '100%',
              colorScheme: 'light',
              backgroundColor: '#ffffff',
              fontFamily: 'system-ui, -apple-system, sans-serif'
            }}
          />
        ) : (
          <div className="p-4 bg-blue-50 border-blue-200">
            <div className="animate-pulse">
              <div className="h-4 bg-blue-200 rounded mb-2"></div>
              <div className="h-3 bg-blue-200 rounded w-3/4"></div>
            </div>
            <p className="text-sm text-blue-700 mt-2">
              Connecting to Agent Builder...
            </p>
          </div>
        )}
      </div>
      
      {/* Enhanced Usage Hints */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 space-y-1">
        <div>💬 Type: "AAPL price", "news for Tesla", "chart NVDA"</div>
        <div>🎤 Voice: Click mic button and speak naturally</div>
        <div className="flex items-center gap-1">
          <div className={`w-2 h-2 rounded-full ${agentVoice.isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span>{agentVoice.isConnected ? 'Voice Ready' : 'Voice Disconnected'}</span>
        </div>
      </div>
    </div>
  );
}