import { useState, useEffect, useCallback, useMemo } from 'react';
import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { AgentResponseParser } from '../services/agentResponseParser';
import { useDataPersistence } from '../hooks/useDataPersistence';
import { getApiUrl } from '../utils/apiConfig';
import {
  normalizeChartCommandPayload,
  type ChartCommandPayload,
} from '../utils/chartCommandUtils';
import { TechnicalLevelsInline } from './widgets/TechnicalLevelsInline';
import { PatternDetectionInline } from './widgets/PatternDetectionInline';
import { parseAgentResponse, type WidgetDefinition } from '../utils/widgetParser';
import { ChatKitWidgetRenderer } from './ChatKitWidgetRenderer';
import type { WidgetAction, WidgetActionHandler } from '../hooks/useWidgetActions';

interface RealtimeChatKitProps {
  onMessage?: (message: Message) => void;
  onChartCommand?: (command: ChartCommandPayload) => void;
  onWidgetAction?: WidgetActionHandler;
  symbol?: string;
  timeframe?: string;
  snapshotId?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  provider?: string;
}

export function RealtimeChatKit({
  onMessage,
  onChartCommand,
  onWidgetAction,
  symbol,
  timeframe,
  snapshotId
}: RealtimeChatKitProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [chatKitControl, setChatKitControl] = useState<any>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // CRITICAL FIX: Make ChatKit opt-in to prevent automatic OpenAI session creation
  const [shouldInitChatKit, setShouldInitChatKit] = useState(false);

  // MCP widget state
  const [technicalLevelsData, setTechnicalLevelsData] = useState<any>(null);
  const [patternDetectionData, setPatternDetectionData] = useState<any>(null);

  // ChatKit widget state (from Agent Builder responses)
  const [chatKitWidgets, setChatKitWidgets] = useState<WidgetDefinition[] | null>(null);

  // Initialize data persistence
  const {
    conversationId,
    conversationHistory,
    isSaving,
    createConversation,
    queueMessage
  } = useDataPersistence({
    autoSave: true,
    saveInterval: 1000,
    maxBatchSize: 5
  });

  // Use the existing Agent Voice conversation hook for proper integration
  const agentVoice = useAgentVoiceConversation({
    chartContext: { symbol, timeframe, snapshot_id: snapshotId },  // Pass chart context
    onMessage: (agentMessage) => {
      // DEBUG: Log full agent message structure
      console.log('[ChatKit DEBUG] Full agentMessage received:', JSON.stringify(agentMessage, null, 2));
      console.log('[ChatKit DEBUG] agentMessage.data:', agentMessage.data);
      console.log('[ChatKit DEBUG] agentMessage.data?.chart_commands:', agentMessage.data?.chart_commands);
      
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
      
      // UPDATE DEBUG INFO - Production-safe visual debugging
      const payload = normalizeChartCommandPayload(
        {
          chart_commands: agentMessage.data?.chart_commands,
          chart_commands_structured: agentMessage.data?.chart_commands_structured,
        },
        agentMessage.content,
      );

      // Handle chart commands if present
      if (payload.legacy.length > 0 || payload.structured.length > 0) {
        console.log('[ChatKit] Processing chart commands:', payload);
        onChartCommand?.(payload);
      } else {
        console.log('[ChatKit DEBUG] NO chart_commands in agentMessage.data');
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
        const backendUrl = getApiUrl();

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

          const { client_secret, session_id } = await res.json();
          localStorage.setItem('chatkit_device_id', deviceId);
          
          // Store session ID for chart context updates
          if (session_id) {
            setSessionId(session_id);
            console.log('✅ ChatKit session established with Agent Builder, session_id:', session_id);
          } else {
            console.log('✅ ChatKit session established with Agent Builder');
          }
          
          return client_secret;
        } catch (err) {
          console.error('❌ ChatKit session error:', err);
          throw err;
        }
      },
    },
    onMessage: (message: any) => {
      console.log('🔥🔥🔥 [ChatKit CONFIG] onMessage CALLED!!!', message);

      // CRITICAL FIX: Extract human-readable text from JSON responses BEFORE displaying
      let displayContent = message.content;
      let isJsonResponse = false;

      // Check if content is JSON and extract text field for display
      if (message.role === 'assistant' && message.content) {
        try {
          const jsonResponse = JSON.parse(message.content);
          isJsonResponse = true;

          // Parse for ChatKit widgets first
          const parsedResponse = parseAgentResponse(message.content);
          if (parsedResponse.hasWidgets && parsedResponse.parsedResponse?.widgets) {
            console.log('[ChatKit] ✅ Detected ChatKit widgets:', parsedResponse.parsedResponse.widgets);
            setChatKitWidgets(parsedResponse.parsedResponse.widgets);
            // Use widget response text if available
            if (parsedResponse.displayText) {
              displayContent = parsedResponse.displayText;
            }
          }

          // Extract human-readable text from JSON
          if (jsonResponse.text) {
            displayContent = jsonResponse.text;
            console.log('[ChatKit] ✅ Extracted text from JSON:', displayContent);
          } else if (jsonResponse.message) {
            displayContent = jsonResponse.message;
            console.log('[ChatKit] ✅ Extracted message from JSON:', displayContent);
          } else if (jsonResponse.response_text) {
            displayContent = jsonResponse.response_text;
            console.log('[ChatKit] ✅ Extracted response_text from JSON:', displayContent);
          } else {
            // If no text/message field, keep original (might be chart commands only)
            console.log('[ChatKit] ⚠️ JSON has no text field, using original content');
          }
        } catch (e) {
          // Not JSON, use content as-is (normal text message)
          console.log('[ChatKit] Content is plain text, not JSON');
        }
      }

      const msg: Message = {
        id: `chatkit-${Date.now()}`,
        role: message.role,
        content: displayContent,  // ✅ FIXED: Use extracted text, not raw JSON
        timestamp: new Date().toISOString(),
        provider: 'chatkit-agent-builder'
      };
      onMessage?.(msg);

      // Persist the message
      queueMessage(msg);

      // Enhanced agent response processing
      if (message.role === 'assistant' && message.content) {
        console.log('[ChatKit] Processing agent response:', message.content);

        // PRIORITY 1: Check if response is JSON with chart_commands or MCP tool results
        if (isJsonResponse) {
          try {
            const jsonResponse = JSON.parse(message.content);

            // Check for MCP tool results (technical levels or patterns)
            if (jsonResponse.technical_levels || jsonResponse.sell_high_level) {
              console.log('[ChatKit] Found technical levels data:', jsonResponse);
              setTechnicalLevelsData({
                sell_high_level: jsonResponse.sell_high_level,
                buy_low_level: jsonResponse.buy_low_level,
                btd_level: jsonResponse.btd_level,
                symbol: jsonResponse.symbol || symbol
              });
            }

            if (jsonResponse.patterns && Array.isArray(jsonResponse.patterns)) {
              console.log('[ChatKit] Found pattern detection data:', jsonResponse);
              setPatternDetectionData({
                patterns: jsonResponse.patterns,
                symbol: jsonResponse.symbol || symbol
              });
            }

            // Check for chart commands
            const payload = normalizeChartCommandPayload(jsonResponse, message.content);
            if (payload.legacy.length > 0 || payload.structured.length > 0) {
              console.log('[ChatKit] Found JSON with chart_commands:', payload);
              onChartCommand?.(payload);
              return; // Stop processing if we found and executed JSON commands
            }
          } catch (e) {
            console.log('[ChatKit] Error re-parsing JSON:', e);
          }
        }

        // PRIORITY 2: Check for drawing commands using the new parser
        if (AgentResponseParser.containsDrawingCommands(message.content)) {
          const chartCommands = AgentResponseParser.parseResponse(message.content);

          if (chartCommands.length > 0) {
            const payload = normalizeChartCommandPayload({ legacy: chartCommands }, message.content);
            console.log('[ChatKit] Parsed chart commands:', payload);
            onChartCommand?.(payload);
          } else {
            console.log('[ChatKit] No chart commands found in drawing response');
          }
        }

        // PRIORITY 3: Legacy fallback for basic chart/symbol commands
        const content = message.content.toLowerCase();
        if (content.includes('chart') || content.includes('symbol')) {
          console.log('[ChatKit] Legacy chart command detection:', message.content);
          const payload = normalizeChartCommandPayload({ legacy: [message.content] }, message.content);
          onChartCommand?.(payload);
        }
      }
    }
  }), [onMessage, onChartCommand]);

  // CRITICAL FIX: Only initialize ChatKit when user explicitly requests it
  // This prevents automatic OpenAI Agent Builder session creation on page load
  const chatKitHookResult = shouldInitChatKit
    ? (useChatKit(chatKitConfig) as { control?: any; error?: unknown })
    : { control: null, error: null };

  // Update control when ChatKit hook result changes
  useEffect(() => {
    if (chatKitHookResult?.control) {
      setChatKitControl(chatKitHookResult.control);
      setIsLoading(false);
      console.log('✅ RealtimeChatKit initialized with Agent Builder integration');
    } else if (shouldInitChatKit) {
      // Only show loading if user requested ChatKit
      setIsLoading(true);
    } else {
      // User hasn't requested ChatKit yet
      setIsLoading(false);
    }
  }, [chatKitHookResult, shouldInitChatKit]);
  
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

  // CRITICAL FIX: DISABLED automatic context updates to prevent excessive OpenAI API calls
  // Context now only updates when user sends a message, not on every symbol/timeframe change
  // This prevents 10+ OpenAI calls every time user switches between TSLA -> AAPL -> NVDA
  /*
  useEffect(() => {
    const updateChartContext = async () => {
      if (!sessionId || !symbol) {
        return;
      }

      try {
        const backendUrl = getApiUrl();

        const response = await fetch(`${backendUrl}/api/chatkit/update-context`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            symbol: symbol,
            timeframe: timeframe || '1D',
            snapshot_id: snapshotId || null
          })
        });

        if (response.ok) {
          console.log(`✅ [ChatKit] Updated chart context: ${symbol} @ ${timeframe || '1D'}`);
        } else {
          console.error(`❌ [ChatKit] Failed to update chart context: ${response.status}`);
        }
      } catch (error) {
        console.error('❌ [ChatKit] Error updating chart context:', error);
      }
    };

    updateChartContext();
  }, [sessionId, symbol, timeframe, snapshotId]);
  */

  // Widget action handler - routes widget actions to appropriate callbacks
  const handleWidgetAction = useCallback((action: WidgetAction) => {
    console.log('[ChatKit] Widget action received:', action);

    // If parent provided a widget action handler, use it
    if (onWidgetAction) {
      onWidgetAction(action);
      return;
    }

    // Default handling for chart-related actions
    if (action.type.startsWith('chart.')) {
      // Convert widget action to chart command format
      const chartCommand = {
        action: action.type,
        ...action.payload
      };
      const payload = normalizeChartCommandPayload({ legacy: [JSON.stringify(chartCommand)] }, '');
      onChartCommand?.(payload);
    }

    // Browser actions (open URL)
    if (action.type === 'browser.openUrl' && action.payload?.url) {
      window.open(action.payload.url, '_blank', 'noopener,noreferrer');
    }

    // Refresh actions - could trigger data refetch
    if (action.type.includes('.refresh')) {
      console.log('[ChatKit] Refresh action - data refetch would go here');
      // Future: Call widgetDataService to refetch data
    }
  }, [onWidgetAction, onChartCommand]);

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

  // Show "Start Chat" button if ChatKit not initialized yet
  if (!shouldInitChatKit) {
    return (
      <div className="realtime-chatkit">
        <div className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
          AI Assistant
        </div>
        <div className="border rounded-lg p-6 bg-gradient-to-br from-blue-50 to-indigo-50 text-center">
          <div className="mb-4">
            <svg className="w-16 h-16 mx-auto text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-800 mb-2">
            Chat Assistant Ready
          </h3>
          <p className="text-sm text-gray-600 mb-4">
            Start a conversation with the AI trading assistant for market insights and analysis.
          </p>
          <button
            onClick={() => setShouldInitChatKit(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-md hover:shadow-lg"
          >
            Start Chat Session
          </button>
          <p className="text-xs text-gray-500 mt-3">
            💡 Voice control available after connecting
          </p>
        </div>
      </div>
    );
  }

  // Loading state (only shown after user clicks "Start Chat")
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
          <p className="text-sm text-gray-600 mt-2">Initializing chat session...</p>
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
            G'sves Trading Assistant
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

      {/* MCP Tool Widgets - Display when data is available */}
      {(technicalLevelsData || patternDetectionData) && (
        <div className="mb-2 space-y-2 max-h-96 overflow-y-auto">
          {technicalLevelsData && <TechnicalLevelsInline data={technicalLevelsData} />}
          {patternDetectionData && <PatternDetectionInline data={patternDetectionData} />}
        </div>
      )}

      {/* ChatKit Visual Widgets - Display when agent returns widgets */}
      {chatKitWidgets && chatKitWidgets.length > 0 && (
        <div className="mb-2 max-h-96 overflow-y-auto">
          <ChatKitWidgetRenderer widgets={chatKitWidgets} onAction={handleWidgetAction} />
        </div>
      )}

      {/* Unified ChatKit + Agent Builder Interface */}
      <div className="flex-grow border rounded-lg overflow-hidden shadow-sm" style={{ minHeight: '200px', display: 'flex', flexDirection: 'column' }}>
        {chatKitControl ? (
          <ChatKit 
            control={chatKitControl}
            className="h-full w-full"
            style={{
              height: '100%',
              minHeight: '200px',
              width: '100%',
              flex: '1 1 auto',
              display: 'flex',
              flexDirection: 'column',
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