import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { TradingChart } from './TradingChart';
import { TimeRangeSelector } from './TimeRangeSelector';
import { marketDataService } from '../services/marketDataService';
import { agentOrchestratorService, ChartSnapshot } from '../services/agentOrchestratorService';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
import { useOpenAIRealtimeConversation } from '../hooks/useOpenAIRealtimeConversation';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { useRealtimeSDKConversation } from '../hooks/useRealtimeSDKConversation';
import { RealtimeChatKit } from './RealtimeChatKit';
// import { ProviderSelector } from './ProviderSelector'; // Removed - conflicts with useElevenLabsConversation
// FIXED: Microphone now requested BEFORE connection (following official OpenAI pattern)
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';
import { useIndicatorContext } from '../contexts/IndicatorContext';
import { CommandToast } from './CommandToast';
import { VoiceCommandHelper } from './VoiceCommandHelper';
import StructuredResponse from './StructuredResponse';
import { DebugWidget } from './DebugWidget';
import { TimeRange } from '../types/dashboard';
import './TradingDashboardSimple.css';

interface StockData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  label: string;
  description: string;
  volume?: number;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  provider?: 'agent' | 'elevenlabs' | 'openai' | 'realtime-sdk' | 'chatkit';  // Track message source
  data?: Record<string, any>;
}

type ConversationProviderKey = 'agent' | 'elevenlabs' | 'openai' | 'realtime-sdk' | 'chatkit';

interface ConversationProviderState {
  provider: ConversationProviderKey;
  isConnected: boolean;
  isLoading: boolean;
  messages: Message[];
  startConversation: () => Promise<void>;
  stopConversation: () => void;
  sendTextMessage: (text: string) => Promise<void> | void;
  sendAudioChunk: (audioBase64: string) => void;
}

// Panel Divider Component for resizable panels
const PanelDivider: React.FC<{
  onDrag: (delta: number) => void;
  orientation?: 'vertical' | 'horizontal';
}> = ({ onDrag, orientation = 'vertical' }) => {
  const [isDragging, setIsDragging] = useState(false);
  const startPosRef = useRef(0);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    startPosRef.current = orientation === 'vertical' ? e.clientX : e.clientY;
    document.body.style.cursor = orientation === 'vertical' ? 'col-resize' : 'row-resize';
  };

  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      const currentPos = orientation === 'vertical' ? e.clientX : e.clientY;
      const delta = currentPos - startPosRef.current;
      startPosRef.current = currentPos;
      onDrag(delta);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      document.body.style.cursor = '';
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, onDrag, orientation]);

  return (
    <div
      className={`panel-divider ${orientation} ${isDragging ? 'dragging' : ''}`}
      onMouseDown={handleMouseDown}
    >
      <div className="divider-handle" />
    </div>
  );
};

// Helper function to convert TimeRange to number of days
const timeframeToDays = (timeframe: TimeRange): number => {
  const map: Record<TimeRange, number> = {
    // Intraday (all map to 1 day of data)
    '10S': 1, '30S': 1, '1m': 1, '3m': 1, '5m': 1,
    '10m': 1, '15m': 1, '30m': 1,
    // Hours (2-7 days for sufficient context)
    '1H': 2, '2H': 3, '3H': 3, '4H': 5, '6H': 5, '8H': 7, '12H': 7,
    // Days
    '1D': 1, '2D': 2, '3D': 3, '5D': 5, '1W': 7,
    // Months
    '1M': 30, '6M': 180,
    // Years - Multi-year support
    '1Y': 365, '2Y': 730, '3Y': 1095, '5Y': 1825,
    // Special
    'YTD': Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 1).getTime()) / (1000 * 60 * 60 * 24)),
    'MAX': 3650 // 10 years
  };
  return map[timeframe] || 30;
};

export const TradingDashboardSimple: React.FC = () => {
  console.log('%c📺 [COMPONENT RENDER] TradingDashboardSimple rendering...', 'background: #4CAF50; color: white; font-size: 16px; font-weight: bold;');

  // Removed tab system - using unified interface
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState('00:00');
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [isLoadingStocks, setIsLoadingStocks] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('TSLA');
  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeRange>('1D');
  const [stockNews, setStockNews] = useState<any[]>([]);
  const [technicalLevels, setTechnicalLevels] = useState<any>({});
  const [detectedPatterns, setDetectedPatterns] = useState<any[]>([]);
  const [backendPatterns, setBackendPatterns] = useState<any[]>([]);
  const [patternValidations, setPatternValidations] = useState<Record<string, 'accepted' | 'rejected'>>({});
  const [currentSnapshot, setCurrentSnapshot] = useState<ChartSnapshot | null>(null);
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [expandedNews, setExpandedNews] = useState<number | null>(null);
  const [toastCommand, setToastCommand] = useState<{ command: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [chartTimeframe, setChartTimeframe] = useState('1D');
  const [voiceProvider, setVoiceProvider] = useState<ConversationProviderKey>('chatkit');
  
  // Dynamic watchlist with localStorage persistence
  const [watchlist, setWatchlist] = useState<string[]>(() => {
    const saved = localStorage.getItem('marketWatchlist');
    return saved ? JSON.parse(saved) : ['TSLA', 'AAPL', 'NVDA', 'SPY', 'PLTR'];
  });
  // Panel widths state for resizable panels
  const [leftPanelWidth, setLeftPanelWidth] = useState(() => {
    const saved = localStorage.getItem('leftPanelWidth');
    return saved ? parseInt(saved) : 240;
  });
  const [rightPanelWidth, setRightPanelWidth] = useState(() => {
    const saved = localStorage.getItem('rightPanelWidth');
    return saved ? parseInt(saved) : 350;
  });

  // Update CSS variables when panel widths change
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--left-panel-width', `${leftPanelWidth}px`);
    root.style.setProperty('--right-panel-width', `${rightPanelWidth}px`);
    
    // Save to localStorage
    localStorage.setItem('leftPanelWidth', leftPanelWidth.toString());
    localStorage.setItem('rightPanelWidth', rightPanelWidth.toString());
  }, [leftPanelWidth, rightPanelWidth]);

  // Panel resize handlers
  const handleLeftPanelResize = useCallback((delta: number) => {
    setLeftPanelWidth(prev => Math.max(200, Math.min(400, prev + delta)));
  }, []);

  const handleRightPanelResize = useCallback((delta: number) => {
    setRightPanelWidth(prev => Math.max(300, Math.min(500, prev - delta)));
  }, []);

  // Message persistence storage keys
  const STORAGE_KEYS = {
    messages: 'trading-assistant-messages',
    session: 'trading-assistant-session'
  };

  // Load persisted messages on component mount
  useEffect(() => {
    try {
      const savedMessages = localStorage.getItem(STORAGE_KEYS.messages);
      if (savedMessages) {
        const parsedMessages = JSON.parse(savedMessages);
        // Only load messages that are less than 24 hours old
        const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
        const recentMessages = parsedMessages.filter((msg: Message) => 
          new Date(msg.timestamp).getTime() > oneDayAgo
        );
        setMessages(recentMessages);
        console.log(`💾 Loaded ${recentMessages.length} persisted messages from localStorage`);
      }
    } catch (error) {
      console.error('Error loading persisted messages:', error);
      // Clear corrupted data
      localStorage.removeItem(STORAGE_KEYS.messages);
    }
  }, []);

  // Save messages to localStorage whenever messages change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(messages));
      console.log(`💾 Saved ${messages.length} messages to localStorage`);
    } catch (error) {
      console.error('Error saving messages to localStorage:', error);
      // If storage is full, clear old messages and try again
      if (error instanceof Error && error.name === 'QuotaExceededError') {
        const recentMessages = messages.slice(-20); // Keep only last 20 messages
        try {
          localStorage.setItem(STORAGE_KEYS.messages, JSON.stringify(recentMessages));
          setMessages(recentMessages);
          console.log('💾 Storage full - reduced to 20 most recent messages');
        } catch (retryError) {
          console.error('Failed to save even reduced message set:', retryError);
        }
      }
    }
  }, [messages]);
  // Save watchlist to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('marketWatchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  // Add symbol to watchlist
  const addToWatchlist = async (symbol: string) => {
    const upperSymbol = symbol.toUpperCase().trim();
    
    // Popular cryptocurrency symbols that should be allowed
    const CRYPTO_SYMBOLS = new Set([
      'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'MATIC', 'AVAX', 'LTC', 
      'XRP', 'DOGE', 'SHIB', 'UNI', 'LINK', 'BCH', 'XLM'
    ]);
    
    // Basic format validation
    const isStockFormat = /^[A-Z]{1,5}$/.test(upperSymbol);
    const isCryptoFormat = /^[A-Z]{2,5}-USD$/.test(upperSymbol);
    const isKnownCrypto = CRYPTO_SYMBOLS.has(upperSymbol);
    
    if (!upperSymbol || (!isStockFormat && !isCryptoFormat && !isKnownCrypto)) {
      setToastCommand({ command: '❌ Invalid symbol format', type: 'error' });
      setTimeout(() => setToastCommand(null), 3000);
      return;
    }
    
    // Check if already in watchlist
    if (watchlist.includes(upperSymbol)) {
      setToastCommand({ command: `⚠️ ${upperSymbol} already in watchlist`, type: 'info' });
      setTimeout(() => setToastCommand(null), 3000);
      return;
    }
    
    try {
      // Verify symbol exists by fetching its data and checking quality
      const data = await marketDataService.getStockPrice(upperSymbol);
      
      // Validate we got real market data (price > 0)
      if (!data || data.price === 0 || data.price === undefined) {
        throw new Error('No valid market data');
      }
      
      // Add to watchlist
      const newWatchlist = [...watchlist, upperSymbol];
      setWatchlist(newWatchlist);
      setToastCommand({ command: `✅ Added ${upperSymbol} to watchlist`, type: 'success' });
      setTimeout(() => setToastCommand(null), 3000);
      
      // Fetch data for the new watchlist
      fetchStocksData(newWatchlist);
    } catch (error: any) {
      console.error(`Failed to add ${upperSymbol}:`, error);
      // Check if it's a 404 (symbol not found)
      const message = error.response?.status === 404 || error.message?.includes('404')
        ? `❌ Symbol ${upperSymbol} not found or invalid`
        : `❌ Failed to add ${upperSymbol}`;
      setToastCommand({ command: message, type: 'error' });
      setTimeout(() => setToastCommand(null), 3000);
    } finally {
    }
  };

  // Remove symbol from watchlist
  const removeFromWatchlist = (symbol: string) => {
    if (watchlist.length <= 1) {
      setToastCommand({ command: '⚠️ Must keep at least one symbol', type: 'info' });
      setTimeout(() => setToastCommand(null), 3000);
      return;
    }
    
    const newWatchlist = watchlist.filter(s => s !== symbol);
    setWatchlist(newWatchlist);
    setToastCommand({ command: `🗑️ Removed ${symbol} from watchlist`, type: 'info' });
    setTimeout(() => setToastCommand(null), 3000);
    
    // If we removed the selected symbol, select the first one
    if (selectedSymbol === symbol && newWatchlist.length > 0) {
      setSelectedSymbol(newWatchlist[0]);
    }
  };
  
  // Audio processing refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletRef = useRef<AudioWorkletNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Chart control ref
  const chartRef = useRef<any>(null);
  
  // Common callback functions for both providers with provider tracking
  const handleUserTranscript = useCallback((transcript: string) => {
    const message: Message = {
      id: `user-${voiceProvider}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: 'user',
      content: transcript,
      timestamp: new Date().toLocaleTimeString(),
      provider: voiceProvider as 'agent' | 'elevenlabs' | 'openai'
    };
    setMessages(prev => [...prev, message]);
  }, [voiceProvider]);

  const handleAgentResponse = useCallback(async (response: string) => {
    console.log(`🤖 ${voiceProvider} response received:`, response);
    
    const message: Message = {
      id: `assistant-${voiceProvider}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      role: 'assistant',
      content: response,
      timestamp: new Date().toLocaleTimeString(),
      provider: voiceProvider as 'agent' | 'elevenlabs' | 'openai'
    };
    setMessages(prev => [...prev, message]);
    console.log(`💬 Added ${voiceProvider} response to chat thread`);
    
    // Process response as potential chart commands
    try {
      const commands = await chartControlService.parseAgentResponse(response);
      if (commands.length > 0) {
        console.log('[Enhanced] Processing voice response chart commands:', commands);
        commands.forEach(cmd => chartControlService.executeCommand(cmd));
      }
    } catch (error) {
      console.log('Chart command processing failed:', error);
    }
    // Process agent response for chart commands with enhanced multi-command support
    try {
      const commands = await enhancedChartControl.processEnhancedResponse(response);
      if (commands.length > 0) {
        console.log('Enhanced chart commands executed:', commands);
        // Show feedback for each command
        commands.forEach(cmd => {
          const message = `${cmd.type}: ${typeof cmd.value === 'object' ? JSON.stringify(cmd.value) : cmd.value}`;
          setToastCommand({ command: message, type: 'success' });
        });
      }
    } catch (error) {
      console.error('Error processing chart commands:', error);
    }
  }, []);

  const stopVoiceRecording = useCallback(() => {
    if (audioWorkletRef.current) {
      audioWorkletRef.current.disconnect();
      audioWorkletRef.current.port.close();
      audioWorkletRef.current = null;
    }

    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }

    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }

    setIsRecording(false);
    setIsListening(false);
    setRecordingTime('00:00');
    setAudioLevel(0);
  }, []);

  const handleConnectionChange = useCallback((connected: boolean) => {
    if (!connected) {
      setIsRecording(false);
      setIsListening(false);
      stopVoiceRecording();
    }
  }, [stopVoiceRecording]);

  // Track previous provider for cleanup
  const previousProviderRef = useRef<ConversationProviderKey>(voiceProvider);

  // Function to fetch and apply chart snapshot
  const fetchAndApplySnapshot = useCallback(async (symbol: string) => {
    try {
      const snapshot = await agentOrchestratorService.getChartSnapshot(symbol, chartTimeframe);
      
      if (snapshot && snapshot.analysis) {
        setCurrentSnapshot(snapshot);
        
        // Extract and apply backend patterns
        if (snapshot.analysis?.patterns) {
          const patternsWithIds = snapshot.analysis.patterns.map((pattern, index) => ({
            ...pattern,
            id: `backend-${symbol}-${index}-${Date.now()}`,
            source: 'backend',
            timestamp: snapshot.captured_at
          }));
          setBackendPatterns(patternsWithIds);
          
          // Show summary in toast
          if (snapshot.analysis.summary) {
            setToastCommand({ 
              command: `📊 Analysis: ${snapshot.analysis.summary}`, 
              type: 'info' 
            });
            setTimeout(() => setToastCommand(null), 5000);
          }
        }
        const patterns = snapshot.analysis?.patterns ?? [];
        if (snapshot.analysis?.summary || patterns.length > 0) {
          const analysisMessage: Message = {
            id: `snapshot-${Date.now()}`,
            role: 'assistant',
            content: `📈 Chart Analysis:\n${snapshot.analysis?.summary || ''}\n\nDetected ${patterns.length} patterns with ${snapshot.vision_model || 'vision model'}`,
            timestamp: new Date().toLocaleTimeString(),
            provider: 'agent',
            data: { snapshot: snapshot.analysis }
          };
          setMessages(prev => [...prev, analysisMessage]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch chart snapshot:', error);
    }
  }, [chartTimeframe]);

  // Function to validate a pattern
  const validatePattern = useCallback((patternId: string, validation: 'accepted' | 'rejected') => {
    setPatternValidations(prev => ({
      ...prev,
      [patternId]: validation
    }));
    
    // Show feedback
    setToastCommand({ 
      command: `Pattern ${validation === 'accepted' ? '✅ Accepted' : '❌ Rejected'}`, 
      type: validation === 'accepted' ? 'success' : 'info' 
    });
    setTimeout(() => setToastCommand(null), 2000);
  }, []);
  
  // Cleanup on provider switch
  useEffect(() => {
    const previousProvider = previousProviderRef.current;
    
    // Cleanup previous provider before switching
    if (previousProvider !== voiceProvider) {
      console.log(`Switching from ${previousProvider} to ${voiceProvider}, cleaning up...`);
      
      if (previousProvider === 'elevenlabs') {
        // Disconnect ElevenLabs singleton
        import('../services/ElevenLabsConnectionManager').then(module => {
          const manager = module.ElevenLabsConnectionManager.getInstance();
          manager.disconnect();
        });
      } else if (previousProvider === 'openai') {
        // Disconnect OpenAI service
        import('../services/OpenAIRealtimeService').then(module => {
          const service = module.OpenAIRealtimeService.getInstance();
          service.disconnect();
        });
      }
      
      previousProviderRef.current = voiceProvider;
    }
  }, [voiceProvider]);

  // Conditional hook mounting - only mount the active provider
  const agentVoice = useAgentVoiceConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onMessage: (message) => {
      const formattedMessage: Message = {
        id: message.id,
        role: message.role,
        content: message.content,
        timestamp: new Date(message.timestamp).toLocaleTimeString(),
        provider: 'agent',
        data: message.data,
      };
      setMessages(prev => [...prev, formattedMessage]);

      if (message.role === 'assistant' && message.toolsUsed?.length) {
        setToastCommand({ command: `🔧 Tools: ${message.toolsUsed.join(', ')}`, type: 'info' });
        setTimeout(() => setToastCommand(null), 3000);
      }

      if (message.role === 'assistant') {
        const rawCommands = message.data?.chart_commands;
        const chartCommands = Array.isArray(rawCommands) ? rawCommands : [];
        if (chartCommands.length > 0) {
          enhancedChartControl.processEnhancedResponse(chartCommands.join(' ')).catch(err => {
            console.error('Failed to execute chart commands from message data:', err);
          });

          const loadCommand = chartCommands.find(cmd => cmd.startsWith('LOAD:'));
          if (loadCommand) {
            const symbol = loadCommand.split(':')[1];
            if (symbol) {
              setTimeout(() => {
                fetchAndApplySnapshot(symbol);
              }, 1000);
            }
          }
        }
      }
    },
    onConnectionChange: handleConnectionChange,
    onError: (error) => {
      setToastCommand({ command: `❌ Error: ${error}`, type: 'error' });
      setTimeout(() => setToastCommand(null), 4000);
    },
    onThinking: (thinking) => {
      console.log('Agent thinking:', thinking);
    }
  });

  const elevenLabs = useElevenLabsConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: handleUserTranscript,
    onAgentResponse: handleAgentResponse,
    onConnectionChange: handleConnectionChange,
  });

  const openAIRealtime = useOpenAIRealtimeConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: handleUserTranscript,
    onAgentResponse: handleAgentResponse,
    onConnectionChange: handleConnectionChange,
    onToolCall: (toolName: string, args: Record<string, unknown>) => {
      console.log('OpenAI tool call:', toolName, args);
      setToastCommand({ command: `🔧 Tool: ${toolName}`, type: 'info' });
      setTimeout(() => setToastCommand(null), 2000);
    },
    onToolResult: (toolName: string, result: unknown) => {
      console.log('OpenAI tool result:', toolName, result);
      setToastCommand({ command: `✅ Tool completed: ${toolName}`, type: 'success' });
      setTimeout(() => setToastCommand(null), 2000);
    }
  });

  const realtimeSDK = useRealtimeSDKConversation({
    onMessage: (message) => {
      const formattedMessage: Message = {
        id: message.id,
        role: message.role,
        content: message.content,
        timestamp: message.timestamp,
        provider: 'realtime-sdk' as any, // Will need to update Message type later
        data: message.data
      };
      
      setMessages(prev => [...prev, formattedMessage]);
      
      if (message.role === 'user') {
        handleUserTranscript(message.content);
      } else {
        handleAgentResponse(message.content);
      }
    },
    onConnectionChange: handleConnectionChange,
    onError: (error: string) => {
      console.error('RealtimeSDK error:', error);
      setToastCommand({ command: `❌ RealtimeSDK: ${error}`, type: 'error' });
      setTimeout(() => setToastCommand(null), 3000);
    },
    onThinking: (thinking: boolean) => {
      setToastCommand(thinking ? { command: '🤔 AI thinking...', type: 'info' } : null);
      if (!thinking) {
        setTimeout(() => setToastCommand(null), 1000);
      }
    }
  });

  // ChatKit conversation (Agent Builder workflow)
  const [chatKitReady, setChatKitReady] = useState(false);
  const [chatKitError, setChatKitError] = useState<string | null>(null);
  const [chatKitControl, setChatKitControl] = useState<any>(null);
  const [chatKitInitAttempts, setChatKitInitAttempts] = useState(0);
  const [chatKitInitMessageShown, setChatKitInitMessageShown] = useState(false);
  const MAX_CHATKIT_INIT_ATTEMPTS = 3;

  const chatKitConfig = useMemo(() => ({
    api: {
      async getClientSecret(existing: any) {
        const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        
        try {
          const deviceId = localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`;
          
          console.log('🔑 Requesting ChatKit session from backend...');
          const res = await fetch(`${backendUrl}/api/chatkit/session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              device_id: deviceId,
              existing_session: existing || null
            }),
          });
          
          if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Session failed: ${res.status} - ${errorText}`);
          }
          
          const { client_secret } = await res.json();
          localStorage.setItem('chatkit_device_id', deviceId);
          console.log('✅ ChatKit session established with Agent Builder');
          setChatKitError(null);
          return client_secret;
        } catch (err: any) {
          const errorMsg = err.message || 'ChatKit session failed';
          console.error('❌ ChatKit session error:', errorMsg);
          setChatKitError(errorMsg);
          setChatKitReady(false);
          throw err;
        }
      },
    },
    onMessage: (message: any) => {
      console.log('📨 ChatKit message received:', message);
      const msg: Message = {
        id: `chatkit-${Date.now()}`,
        role: message.role,
        content: message.content,
        timestamp: new Date().toISOString(),
        provider: 'chatkit'
      };
      setMessages(prev => [...prev, msg]);
      
      // Process chart commands if present
      if (message.role === 'assistant' && message.content) {
        handleAgentResponse(message.content);
      }
    },
  }), []);

  // ChatKit is now handled by RealtimeChatKit component
  // const chatKitHookResult = useChatKit(chatKitConfig) as { control?: any; error?: unknown };
  
  // Monitor ChatKit initialization and readiness
  // Commented out - now handled by RealtimeChatKit component
  /*
  useEffect(() => {
    if (chatKitHookResult?.control) {
      console.log('✅ ChatKit control available - ready to send messages');
      setChatKitControl(chatKitHookResult.control);
      setChatKitReady(true);
      setChatKitError(null);
      // Reset initialization tracking on successful connection
      setChatKitInitAttempts(0);
      setChatKitInitMessageShown(false);
    } else if (chatKitHookResult?.error) {
      const errorMessage = chatKitHookResult.error instanceof Error 
        ? chatKitHookResult.error.message 
        : typeof chatKitHookResult.error === 'string'
          ? chatKitHookResult.error
          : 'ChatKit initialization failed';
      console.error('❌ ChatKit hook error:', errorMessage);
      setChatKitError(errorMessage);
      setChatKitReady(false);
      setChatKitControl(null);
    }
  }, [chatKitHookResult]);
  */

  const conversationProviders: Record<ConversationProviderKey, ConversationProviderState> = useMemo(() => ({
    agent: {
      provider: 'agent',
      isConnected: agentVoice.isConnected,
      isLoading: agentVoice.isLoading,
      messages: messages.filter(message => message.provider === 'agent'),
      startConversation: async () => {
        await agentVoice.connect();
      },
      stopConversation: agentVoice.disconnect,
      sendTextMessage: agentVoice.sendTextMessage,
      sendAudioChunk: () => {},
    },
    elevenlabs: {
      provider: 'elevenlabs',
      isConnected: elevenLabs.isConnected,
      isLoading: elevenLabs.isLoading,
      messages: messages.filter(message => message.provider === 'elevenlabs'),
      startConversation: () => elevenLabs.startConversation(),
      stopConversation: elevenLabs.stopConversation,
      sendTextMessage: elevenLabs.sendTextMessage,
      sendAudioChunk: elevenLabs.sendAudioChunk,
    },
    openai: {
      provider: 'openai',
      isConnected: openAIRealtime.isConnected,
      isLoading: openAIRealtime.isLoading,
      messages: messages.filter(message => message.provider === 'openai'),
      startConversation: () => openAIRealtime.startConversation(),
      stopConversation: openAIRealtime.stopConversation,
      sendTextMessage: openAIRealtime.sendTextMessage,
      sendAudioChunk: openAIRealtime.sendAudioChunk,
    },
    'realtime-sdk': {
      provider: 'realtime-sdk',
      isConnected: realtimeSDK.isConnected,
      isLoading: realtimeSDK.isLoading,
      messages: messages.filter(message => message.provider === 'realtime-sdk'),
      startConversation: () => realtimeSDK.startConversation(),
      stopConversation: realtimeSDK.stopConversation,
      sendTextMessage: realtimeSDK.sendTextMessage,
      sendAudioChunk: () => {}, // Not needed for direct realtime connection
    },
    'chatkit': {
      provider: 'chatkit',
      isConnected: chatKitReady && !chatKitError,
      isLoading: !chatKitReady && !chatKitError,
      messages: messages.filter(message => message.provider === 'chatkit'),
      startConversation: async () => {
        console.log('ChatKit session auto-connects on initialization');
      },
      stopConversation: () => {
        console.log('ChatKit session persistent (no explicit disconnect)');
      },
      sendTextMessage: async (text: string) => {
        if (chatKitControl?.sendMessage) {
          console.log('📤 Sending text to ChatKit Agent Builder:', text);
          try {
            await chatKitControl.sendMessage(text);
            console.log('✅ Message sent to ChatKit Agent Builder');
          } catch (error) {
            console.error('❌ ChatKit send error:', error);
            throw error;
          }
        } else {
          console.error('ChatKit control not available');
          throw new Error('ChatKit not initialized - control unavailable');
        }
      },
      sendAudioChunk: () => {
        console.warn('ChatKit: Audio chunks not supported in text mode');
      },
    },
  }), [agentVoice.connect, agentVoice.disconnect, agentVoice.isConnected, agentVoice.isLoading, agentVoice.sendTextMessage, messages, elevenLabs.isConnected, elevenLabs.isLoading, elevenLabs.sendAudioChunk, elevenLabs.sendTextMessage, elevenLabs.startConversation, elevenLabs.stopConversation, openAIRealtime.isConnected, openAIRealtime.isLoading, openAIRealtime.sendAudioChunk, openAIRealtime.sendTextMessage, openAIRealtime.startConversation, openAIRealtime.stopConversation, realtimeSDK.isConnected, realtimeSDK.isLoading, realtimeSDK.sendTextMessage, realtimeSDK.startConversation, realtimeSDK.stopConversation, chatKitReady, chatKitError, chatKitControl]);

  const currentConversation = conversationProviders[voiceProvider];
  const isConversationConnected = currentConversation.isConnected;
  const isConversationConnecting = currentConversation.isLoading && !currentConversation.isConnected;

  const unifiedMessages = useMemo(() => {
    return [...messages].sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  }, [messages]);

  // Track previous provider to only disconnect on actual provider changes
  const prevProviderRef = useRef(voiceProvider);
  
  // Reset states when voice provider changes (prevent stuck loading states)
  useEffect(() => {
    const prevProvider = prevProviderRef.current;
    const currentProvider = voiceProvider;

    console.log(`Voice provider switched from ${prevProvider} to: ${currentProvider}`);

    if (prevProvider !== currentProvider && conversationProviders[prevProvider].isConnected) {
      console.log('Disconnecting from previous provider due to provider switch');
      conversationProviders[prevProvider].stopConversation();
    }

    prevProviderRef.current = currentProvider;

    if (prevProvider !== currentProvider) {
      setIsRecording(false);
      setIsListening(false);
      setInputText('');
    }
  }, [voiceProvider, conversationProviders]);

  // Single connect/disconnect handler with debounce
  const handleConnectToggle = async () => {
    console.log('🚨 [DASHBOARD] ==================== handleConnectToggle CLICKED ====================');
    console.log('🚨 [DASHBOARD] voiceProvider:', voiceProvider);
    console.log('🚨 [DASHBOARD] currentConversation.isConnected:', currentConversation.isConnected);
    console.log('🚨 [DASHBOARD] currentConversation.provider:', currentConversation.provider);

    const now = Date.now();

    // Debounce rapid clicks (minimum 1 second between attempts)
    if (now - connectionAttemptTimeRef.current < 1000) {
      console.log('🚨 [DASHBOARD] DEBOUNCED: Too soon since last attempt');
      return;
    }

    connectionAttemptTimeRef.current = now;

    if (currentConversation.isConnected) {
      console.log('🚨 [DASHBOARD] Already connected - DISCONNECTING');
      // Disconnect everything
      stopVoiceRecording();
      currentConversation.stopConversation();
      hasStartedRecordingRef.current = false;
    } else {
      const providerName = voiceProvider === 'elevenlabs' ? 'ElevenLabs' : 
                        voiceProvider === 'agent' ? 'Agent Voice' : 
                        voiceProvider === 'realtime-sdk' ? 'OpenAI Realtime + SDK' :
                        'OpenAI Realtime';
      console.log(`🚨 [DASHBOARD] Not connected - CONNECTING to ${providerName}...`);
      console.log('🚨 [DASHBOARD] About to call currentConversation.startConversation()...');
      console.log('🚨 [DASHBOARD] startConversation function:', typeof currentConversation.startConversation);

      // Connect (voice recording will auto-start via useEffect when connected)
      try {
        await currentConversation.startConversation();
        console.log('🚨 [DASHBOARD] ✅ startConversation() COMPLETED');
      } catch (error) {
        console.error('🚨 [DASHBOARD] ❌ Failed to connect:', error);
        alert(`Failed to connect to ${providerName} voice assistant. Please check your connection and try again.`);
      }
    }
  };

  // Direct OpenAI connection handler - simplified single click
  const handleOpenAIConnect = async () => {
    const now = Date.now();
    
    // Debounce rapid clicks
    if (now - connectionAttemptTimeRef.current < 1000) {
      console.log('Debouncing rapid OpenAI connection attempt');
      return;
    }
    
    connectionAttemptTimeRef.current = now;
    
    // Set provider to OpenAI and connect immediately
    setVoiceProvider('openai');
    
    // Small delay to ensure state update
    setTimeout(async () => {
      console.log('Connecting directly to OpenAI Realtime...');
      try {
        await currentConversation.startConversation();
      } catch (error) {
        console.error('Failed to connect to OpenAI:', error);
        alert('Failed to connect to OpenAI Realtime. Please check your connection and try again.');
      }
    }, 100);
  };

  // Handle text message sending - route ONLY to active provider
  const handleSendTextMessage = async () => {
    console.log('🎯 handleSendTextMessage called');
    console.log('📝 Input text:', inputText);
    console.log('🔌 Is connected:', currentConversation.isConnected);
    console.log('🎤 Voice provider:', voiceProvider);
    
    if (inputText.trim()) {
      // Stop voice recording before sending text to prevent conflicts
      if (isRecording) {
        console.log('Stopping voice recording before sending text message');
        stopVoiceRecording();
      }
      
      const trimmedQuery = inputText.trim();

      // Generate unique ID with provider prefix
      const messageId = `${voiceProvider}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      const dispatchTimestamp = new Date().toISOString();
      console.info(`[agent] query_dispatch`, JSON.stringify({
        timestamp: dispatchTimestamp,
        provider: voiceProvider,
        messageId,
        query: trimmedQuery
      }));

      // Add user message to chat thread immediately (regardless of connection status)
      const userMessage: Message = {
        id: `user-${messageId}`,
        role: 'user' as const,
        content: trimmedQuery,
        timestamp: dispatchTimestamp,
        provider: voiceProvider as 'agent' | 'elevenlabs' | 'openai' | 'realtime-sdk' | 'chatkit'
      };

      // Add to local messages for immediate UI feedback
      setMessages(prev => [...prev, userMessage]);
      console.log('💬 Added user message to chat thread');

      // Clear input immediately for better UX
      const messageText = trimmedQuery;
      setInputText('');
      
      // Route ONLY to the active provider
      switch(voiceProvider) {
        case 'chatkit':
          // ChatKit uses Agent Builder workflow on OpenAI's servers
          console.log('🤖 Sending text to ChatKit Agent Builder');
          if (chatKitControl?.sendMessage) {
            try {
              // Don't use await here as we're not in an async context
              chatKitControl.sendMessage(messageText);
              console.log('✅ Message sent to ChatKit Agent Builder');
              // Reset init state on successful send
              setChatKitInitMessageShown(false);
            } catch (error) {
              console.error('❌ ChatKit send error:', error);
              const errorMessage: Message = {
                id: `error-${Date.now()}`,
                role: 'assistant',
                content: `Error sending message to Agent Builder: ${error}`,
                timestamp: new Date().toISOString(),
                provider: 'chatkit',
              };
              setMessages(prev => [...prev, errorMessage]);
            }
          } else {
            console.error('ChatKit not ready - control unavailable');
            
            // Increment attempts each time we try to send while ChatKit is not ready
            setChatKitInitAttempts(prev => prev + 1);
            
            // Check if we've exceeded max attempts
            if (chatKitInitAttempts >= MAX_CHATKIT_INIT_ATTEMPTS) {
              // After max attempts, show unavailable message
              const failedMessage: Message = {
                id: `chatkit-failed-${Date.now()}`,
                role: 'assistant',
                content: 'ChatKit is currently unavailable. Please try using voice or another provider.',
                timestamp: new Date().toISOString(),
                provider: 'chatkit',
              };
              setMessages(prev => [...prev, failedMessage]);
            } else if (!chatKitInitMessageShown) {
              // Show initialization message only once
              const offlineMessage: Message = {
                id: `offline-init-single`,  // Use fixed ID to prevent duplicates
                role: 'assistant',
                content: 'ChatKit Agent Builder is initializing. Please wait a moment...',
                timestamp: new Date().toISOString(),
                provider: 'chatkit',
              };
              
              // Check if this message already exists
              setMessages(prev => {
                const exists = prev.some(m => m.id === 'offline-init-single');
                if (!exists) {
                  setChatKitInitMessageShown(true);
                  return [...prev, offlineMessage];
                }
                return prev;
              });
            }
            // If message already shown and still under limit, just silently fail
          }
          break;
          
        case 'agent':
          // Agent text using Agents SDK workflow (unified architecture)
          fetch((import.meta.env.VITE_API_URL || window.location.origin) + '/api/agent/sdk-orchestrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: messageText, conversation_history: [] })
          })
          .then(res => res.json())
          .then(data => {
            const responseTimestamp = new Date().toISOString();
            console.info('[agent] query_response', JSON.stringify({
              timestamp: responseTimestamp,
              provider: 'agent',
              messageId,
              toolsUsed: data?.tools_used,
              chartCommands: data?.chart_commands
            }));
            if (data.text) {
              const agentMessage: Message = {
                id: `assistant-agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                role: 'assistant',
                content: data.text,
                timestamp: new Date().toISOString(),
                provider: 'agent'
              };
              setMessages(prev => [...prev, agentMessage]);
              console.log('✅ Added backend agent response to chat');

              if (Array.isArray(data.chart_commands) && data.chart_commands.length > 0) {
                console.info('[agent] executing_chart_commands', JSON.stringify({
                  timestamp: responseTimestamp,
                  messageId,
                  chartCommands: data.chart_commands
                }));
                enhancedChartControl.processEnhancedResponse(data.chart_commands.join(' ')).catch(err => {
                  console.error('Failed to execute chart commands from agent response:', err);
                });
              }

              // Extract and apply swing trade levels if present in response
              try {
                // Look for JSON structure in the response
                const jsonMatch = data.text.match(/```json\s*({[\s\S]*?})\s*```/);
                if (jsonMatch && jsonMatch[1]) {
                  const parsedData = JSON.parse(jsonMatch[1]);
                  if (parsedData.swing_trade) {
                    const swingData = parsedData.swing_trade;
                    console.log('🎯 Found swing trade data:', swingData);
                    
                    // Update technical levels with swing trade data
                    setTechnicalLevels((prev: any) => ({
                      ...prev,
                      entry_points: swingData.entry_points,
                      stop_loss: swingData.stop_loss,
                      targets: swingData.targets,
                      risk_reward: swingData.risk_reward,
                      support_levels: swingData.support_levels,
                      resistance_levels: swingData.resistance_levels
                    }));
                    
                    // Show toast notification
                    setToastCommand({
                      command: `Swing trade levels updated for ${selectedSymbol}`,
                      type: 'success'
                    });
                  }
                }
              } catch (error) {
                console.log('No swing trade JSON found in response:', error);
              }
            }
          })
          .catch(err => {
            const errorTimestamp = new Date().toISOString();
            console.error('[agent] query_error', JSON.stringify({
              timestamp: errorTimestamp,
              provider: 'agent',
              messageId,
              error: err?.message || err
            }));
            console.error('Backend agent error:', err);
          });
          break;

        case 'elevenlabs':
        case 'openai':
          // Voice providers require a live connection
          if (currentConversation.isConnected) {
            currentConversation.sendTextMessage(messageText);
          } else {
            setTimeout(() => {
              const offlineMessage = {
                id: `assistant-${Date.now()}-${Math.random()}`,
                role: 'assistant' as const,
                content: 'Please connect the voice assistant (mic) to use voice providers.',
                timestamp: new Date().toISOString(),
                provider: voiceProvider,
              };
              setMessages(prev => [...prev, offlineMessage]);
            }, 300);
          }
          break;

        default:
          console.warn('Unknown provider:', voiceProvider);
      }
    } else {
      console.log('❌ Cannot send message - no text entered');
    }
  };

  // Tab system removed - voice is always available via FAB

  const handleNewsToggle = (index: number) => {
    setExpandedNews(expandedNews === index ? null : index);
  };

  const handleBackToClassic = () => {
    console.log('Back to classic view');
    // Add navigation logic here if needed
  };

  // Fetch stock prices for watchlist
  const fetchStocksData = async (symbolsToFetch?: string[]) => {
    const symbols = symbolsToFetch || watchlist;
    setIsLoadingStocks(true);
    try {
      const promises = symbols.map(async (symbol) => {
        const stockPrice = await marketDataService.getStockPrice(symbol);
        
        // Determine label based on price momentum
        let label = 'ST';
        let description = 'Neutral momentum';
        
        const changePercent = stockPrice.change_percent || stockPrice.change_pct || 0;
        
        if (changePercent > 2) {
          label = 'QE';
          description = 'Bullish momentum';
        } else if (changePercent < -2) {
          label = 'LTB';
          description = 'Support level';
        } else if (Math.abs(changePercent) < 0.5) {
          label = 'ST';
          description = 'Consolidation';
        } else if (changePercent > 0) {
          label = 'ST';
          description = 'Upward trend';
        } else {
          label = 'LTB';
          description = 'Downward pressure';
        }
        
        return {
          symbol: stockPrice.symbol,
          price: stockPrice.price || stockPrice.last || 0,
          change: stockPrice.change || stockPrice.change_abs || 0,
          changePercent: stockPrice.change_percent || stockPrice.change_pct || 0,
          label,
          description,
          volume: stockPrice.volume || 0
        };
      });
      
      const stocks = await Promise.all(promises);
      setStocksData(stocks);
    } catch (error) {
      console.error('Error fetching stock data:', error);
      // Set fallback data if API fails
      setStocksData([
        { symbol: 'TSLA', price: 245.67, change: 5.29, changePercent: 2.21, label: 'QE', description: 'Bullish momentum' },
        { symbol: 'AAPL', price: 189.43, change: -2.12, changePercent: -1.11, label: 'LTB', description: 'Support level' },
        { symbol: 'NVDA', price: 421.88, change: 8.90, changePercent: 2.15, label: 'QE', description: 'Breakout pattern' },
        { symbol: 'SPY', price: 445.23, change: 3.47, changePercent: 0.79, label: 'ST', description: 'Consolidation' }
      ]);
    }
    setIsLoadingStocks(false);
  };

  // Fetch news and analysis for selected stock
  const fetchStockAnalysis = async (symbol: string) => {
    setIsLoadingNews(true);
    
    // Fetch news independently
    try {
      const news = await marketDataService.getStockNews(symbol);
      setStockNews(news); // Show all available news items
    } catch (error) {
      console.error('Error fetching news:', error);
      // Set fallback news only if news fetch fails
      setStockNews([
        { title: `${symbol} shows bullish flag pattern forming`, time: '2 min ago' },
        { title: `Price testing key support levels`, time: '5 min ago' },
        { title: `Volume breakout above resistance`, time: '8 min ago' }
      ]);
    }
    
    // Fetch comprehensive data separately
    try {
      const comprehensive = await marketDataService.getComprehensiveData(symbol);
      if (comprehensive.technical_levels) {
        setTechnicalLevels(comprehensive.technical_levels);
      } else {
        setTechnicalLevels({});
      }

      const patterns = comprehensive.patterns?.detected || [];
      if (patterns.length > 0) {
        // Sort by confidence descending and take top 3
        const sortedPatterns = [...patterns].sort((a: any, b: any) => (b.confidence || 0) - (a.confidence || 0));
        setDetectedPatterns(sortedPatterns.slice(0, 3));

        const primary = sortedPatterns[0];
        enhancedChartControl.clearDrawings();
        enhancedChartControl.revealPattern(primary?.type || 'Pattern', {
          title: primary?.description || primary?.type,
          description: primary?.agent_explanation || primary?.summary,
          indicator: primary?.related_indicator,
        });
      } else {
        setDetectedPatterns([]);
        enhancedChartControl.clearDrawings();
      }
    } catch (error) {
      console.error('Error fetching comprehensive data:', error);
      // Technical levels will just remain undefined/empty if this fails
      setTechnicalLevels({});
      setDetectedPatterns([]);
      enhancedChartControl.clearDrawings();
    }
    
    setIsLoadingNews(false);
  };

  // Fetch data when watchlist changes and set up refresh interval
  useEffect(() => {
    fetchStocksData(watchlist);
    
    // Refresh every 30 seconds
    const interval = setInterval(() => fetchStocksData(watchlist), 30000);
    
    return () => clearInterval(interval);
  }, [watchlist]);

  // Fetch analysis when selected symbol changes
  useEffect(() => {
    fetchStockAnalysis(selectedSymbol);
  }, [selectedSymbol]);
  
  // Register chart control callbacks for both services
  useEffect(() => {
    // Connect indicator dispatch if available
    try {
      const { dispatch } = useIndicatorContext();
      enhancedChartControl.setIndicatorDispatch(dispatch);
      console.log('Indicator controls connected to agent');
    } catch (error) {
      console.log('IndicatorContext not available - agent indicator control disabled');
    }
    
    // Register with enhanced service (TODO: Implement registerCallbacks method)
    if (typeof (enhancedChartControl as any).registerCallbacks === 'function') {
    (enhancedChartControl as any).registerCallbacks({
      onSymbolChange: (symbol: string, metadata?: { assetType?: 'stock' | 'crypto' }) => {
        console.log('Voice command: Changing symbol to', symbol, 'Type:', metadata?.assetType);
        
        // Validate symbol before processing
        const upperSymbol = symbol.toUpperCase();
        
        // Check if it's a valid symbol format
        const isValidFormat = /^[A-Z]{1,5}(-USD)?$/.test(upperSymbol) || /^BRK\.[AB]$/.test(upperSymbol);
        
        // Check if it's in the watchlist or is a known crypto symbol
        const isInWatchlist = watchlist.includes(upperSymbol.replace('-USD', ''));
        const isCrypto = metadata?.assetType === 'crypto' || upperSymbol.endsWith('-USD');
        
        if (!isValidFormat) {
          console.warn(`Invalid symbol format rejected: ${symbol}`);
          setToastCommand({ command: `❌ Invalid symbol: ${symbol}`, type: 'error' });
          setTimeout(() => setToastCommand(null), 3000);
          return;
        }
        
        // For stocks, check if it's in the watchlist (unless it's crypto)
        if (!isCrypto && !isInWatchlist) {
          // Try to add it to the watchlist first
          addToWatchlist(upperSymbol.replace('-USD', '')).then(() => {
            // If successfully added, then select it
            setSelectedSymbol(upperSymbol);
            fetchStockAnalysis(upperSymbol);
          }).catch(() => {
            // If failed to add, show error
            setToastCommand({ command: `❌ Symbol not found: ${symbol}`, type: 'error' });
            setTimeout(() => setToastCommand(null), 3000);
          });
          return;
        }
        
        // Valid symbol, proceed with update
        setSelectedSymbol(upperSymbol);
        fetchStockAnalysis(upperSymbol);
        const icon = metadata?.assetType === 'crypto' ? '₿' : '📈';
        setToastCommand({ command: `${icon} Symbol: ${upperSymbol}`, type: 'success' });
        setTimeout(() => setToastCommand(null), 3000);
      },
      onTimeframeChange: (timeframe: string) => {
        console.log('Voice command: Changing timeframe to', timeframe);
        setChartTimeframe(timeframe);
        setToastCommand({ command: `Timeframe: ${timeframe}`, type: 'success' });
        setTimeout(() => setToastCommand(null), 3000);
      },
      onIndicatorToggle: (indicator: string, enabled: boolean) => {
        console.log(`Voice command: ${indicator} ${enabled ? 'enabled' : 'disabled'}`);
        setToastCommand({ command: `${indicator} ${enabled ? 'enabled' : 'disabled'}`, type: 'info' });
        setTimeout(() => setToastCommand(null), 3000);
      },
      onZoomChange: (level: number) => {
        console.log('Voice command: Zoom level', level);
        setToastCommand({ command: level > 1 ? 'Zoomed in' : 'Zoomed out', type: 'info' });
        setTimeout(() => setToastCommand(null), 3000);
      },
      onScrollToTime: (time: number) => {
        console.log('Voice command: Scrolling to time', time);
        // Handled directly by chart ref in service
      },
      onStyleChange: (style: 'candles' | 'line' | 'area') => {
        console.log('Voice command: Chart style changed to', style);
        const styleNames = {
          'candles': 'Candlestick',
          'line': 'Line Chart',
          'area': 'Area Chart'
        };
        setToastCommand({ command: `Style: ${styleNames[style]}`, type: 'success' });
        setTimeout(() => setToastCommand(null), 3000);
        // Future: Add chart style state
      },
      onPatternHighlight: (pattern: string, info?: { description?: string }) => {
        console.log('Voice command: highlight pattern', pattern);
        const message = enhancedChartControl.revealPattern(pattern, info);
        setToastCommand({ command: message, type: 'info' });
        setTimeout(() => setToastCommand(null), 3000);
      },
      onCommandExecuted: (command, success, message) => {
        // Show toast notification for command execution
        setToastCommand({
          command: message,
          type: success ? 'success' : 'error'
        });
      },
      onCommandError: (error) => {
        // Show error toast
        setToastCommand({
          command: error,
          type: 'error'
        });
      }
    });
    }
  }, []);

  // Track if we've already started recording to prevent duplicates
  const hasStartedRecordingRef = useRef(false);
  const connectionAttemptTimeRef = useRef<number>(0);
  const isMountedRef = useRef(true);
  
  // Process backend chart commands when snapshot is updated
  useEffect(() => {
    if (currentSnapshot?.chart_commands?.length > 0) {
      console.log('Executing backend chart commands:', currentSnapshot.chart_commands);
      enhancedChartControl.processEnhancedResponse(
        currentSnapshot.chart_commands.join(' ')
      ).catch(err => {
        console.error('Failed to execute backend chart commands:', err);
      });
    }
  }, [currentSnapshot]);
  
  // Auto-start voice recording when connected - DISABLED to prevent text/audio conflicts
  // Users should manually start voice recording when needed
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;

    if (!currentConversation.isConnected) {
      hasStartedRecordingRef.current = false;
    }

    return () => {
      if (timer) {
        clearTimeout(timer);
      }
    };
  }, [currentConversation.isConnected]);

  // Note: No cleanup on unmount for WebSocket connection
  // The ConnectionManager is a singleton that persists across component re-renders
  // and handles its own lifecycle. Cleaning up here causes issues with React StrictMode
  // which double-invokes effects in development.

  return (
    <div className="trading-dashboard-simple" data-testid="trading-dashboard">
      {/* Command Toast Notifications */}
      {toastCommand && (
        <CommandToast
          command={toastCommand.command}
          type={toastCommand.type}
          duration={2500}
          onClose={() => setToastCommand(null)}
        />
      )}
      
      {/* Header with Integrated Ticker Cards */}
      <header className="dashboard-header-with-tickers">
        <div className="header-left">
          <h1 className="brand">GVSES</h1>
          <span className="subtitle">Market Assistant</span>
        </div>
        
        {/* Compact Ticker Cards in Header */}
        <div className="header-tickers">
          {isLoadingStocks ? (
            <div className="ticker-loading">Loading...</div>
          ) : (
            stocksData.slice(0, 5).map((stock) => (
              <div 
                key={stock.symbol} 
                className={`ticker-compact ${selectedSymbol === stock.symbol ? 'selected' : ''}`}
                onClick={() => setSelectedSymbol(stock.symbol)}
                title={`${stock.symbol}: ${stock.label}`}
              >
                <div className="ticker-compact-left">
                  <div className="ticker-symbol-compact">{stock.symbol}</div>
                  <div className="ticker-price-compact">${stock.price.toFixed(2)}</div>
                </div>
                <div className="ticker-compact-right">
                  <div className={`ticker-change-compact ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(1)}%
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        
        <div className="header-controls">
          <span className="status-indicator">
            {isConversationConnected ? '🟢' : '⚪'}
          </span>
        </div>
      </header>


      {/* Main Layout */}
      <div className="dashboard-layout">
        {/* Left Panel - Chart Analysis */}
        <aside className="analysis-panel-left" style={{ width: `${leftPanelWidth}px` }}>

          <h2 className="panel-title">CHART ANALYSIS</h2>
          <div className="analysis-content">
            {isLoadingNews ? (
              <div className="loading-spinner">Loading analysis...</div>
            ) : (
              <>
                {/* Scrollable news section */}
                <div className="news-scroll-container">
                  {stockNews.map((news, index) => (
                    <div key={index} className="analysis-item clickable-news">
                      <div 
                        className="news-header"
                        onClick={() => handleNewsToggle(index)}
                      >
                        <div className="analysis-header">
                          <h3>{selectedSymbol}</h3>
                          <span className="time">{news.published || news.time || `${index * 3 + 2} min ago`}</span>
                        </div>
                        <p className="news-title">{news.title}</p>
                        <div className="news-source">
                          <span className="source-name">{news.source || 'Market News'}</span>
                          <span className="expand-icon">{expandedNews === index ? '▼' : '▶'}</span>
                        </div>
                      </div>
                      
                      {expandedNews === index && (
                        <div className="news-expanded">
                          {news.description && (
                            <p className="news-description">{news.description}</p>
                          )}
                          {news.url && (
                            <a 
                              href={news.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="news-link"
                              onClick={(e) => e.stopPropagation()}
                            >
                              Read Full Article →
                            </a>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Fixed Technical Levels section */}
                <div className="technical-section">
                  <h4>TECHNICAL LEVELS</h4>
                  <div className="level-row">
                    <span>Sell High</span>
                    <span className="level-val qe">
                      ${technicalLevels.sell_high_level ? technicalLevels.sell_high_level.toFixed(2) : '---'}
                    </span>
                  </div>
                  <div className="level-row">
                    <span>Buy Low</span>
                    <span className="level-val st">
                      ${technicalLevels.buy_low_level ? technicalLevels.buy_low_level.toFixed(2) : '---'}
                    </span>
                  </div>
                  <div className="level-row">
                    <span>BTD</span>
                    <span className="level-val ltb">
                      ${technicalLevels.btd_level ? technicalLevels.btd_level.toFixed(2) : '---'}
                    </span>
                  </div>
                </div>

                <div className="pattern-section">
                  <h4>PATTERN DETECTION</h4>
                  
                  {/* Local Patterns */}
                  {detectedPatterns.length > 0 && (
                    <>
                      <div className="pattern-source-label">Local Analysis</div>
                      {detectedPatterns.map((pattern, index) => (
                        <div key={`local-${pattern.type}-${index}`} className="pattern-box">
                          <div className="pattern-name">{pattern.description || pattern.type}</div>
                          <div className="pattern-conf">
                            Confidence: {pattern.confidence ? `${Math.round(pattern.confidence)}%` : 'N/A'}
                          </div>
                          {pattern.agent_explanation && (
                            <div className="pattern-desc">{pattern.agent_explanation}</div>
                          )}
                        </div>
                      ))}
                    </>
                  )}
                  
                  {/* Backend Patterns with Validation */}
                  {backendPatterns.length > 0 && (
                    <>
                      <div className="pattern-source-label">Server Analysis</div>
                      {backendPatterns.map((pattern) => {
                        const validation = patternValidations[pattern.id];
                        return (
                          <div 
                            key={pattern.id} 
                            className={`pattern-box backend-pattern ${validation ? `pattern-${validation}` : ''}`}
                          >
                            <div className="pattern-header">
                              <div className="pattern-name">{pattern.type}</div>
                              <div className="pattern-validation-controls">
                                <button 
                                  className={`pattern-btn accept ${validation === 'accepted' ? 'active' : ''}`}
                                  onClick={() => validatePattern(pattern.id, 'accepted')}
                                  title="Accept pattern"
                                >
                                  ✓
                                </button>
                                <button 
                                  className={`pattern-btn reject ${validation === 'rejected' ? 'active' : ''}`}
                                  onClick={() => validatePattern(pattern.id, 'rejected')}
                                  title="Reject pattern"
                                >
                                  ✗
                                </button>
                              </div>
                            </div>
                            <div className="pattern-conf">
                              Confidence: {pattern.confidence ? `${Math.round(pattern.confidence * 100)}%` : 'N/A'}
                            </div>
                            {pattern.description && (
                              <div className="pattern-desc">{pattern.description}</div>
                            )}
                            {pattern.targets && pattern.targets.length > 0 && (
                              <div className="pattern-targets">
                                Targets: {pattern.targets.map((t: number) => `$${t.toFixed(2)}`).join(', ')}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </>
                  )}
                  
                  {detectedPatterns.length === 0 && backendPatterns.length === 0 && (
                    <div className="pattern-empty">No patterns detected. Try asking for chart analysis.</div>
                  )}
                </div>
              </>
            )}
          </div>
        </aside>

        {/* Left Panel Divider */}
        <PanelDivider onDrag={handleLeftPanelResize} />

        {/* Center - Chart Always Visible */}
        <main className="main-content">
          {/* Chart Section - Always Visible */}
          <div className="chart-section">
            {/* Timeframe Selector */}
            <TimeRangeSelector
              selected={selectedTimeframe}
              options={['1D', '5D', '1M', '6M', '1Y', '2Y', '3Y', 'YTD', 'MAX']}
              onChange={(range) => setSelectedTimeframe(range)}
            />
            <div className="chart-wrapper">
              <TradingChart
                symbol={selectedSymbol}
                days={timeframeToDays(selectedTimeframe)}
                technicalLevels={technicalLevels}
                onChartReady={(chart: any) => {
                  chartRef.current = chart;
                  chartControlService.setChartRef(chart);
                  enhancedChartControl.setChartRef(chart);
                  console.log('Chart ready for enhanced agent control');
                }}
              />
            </div>
          </div>

          {/* Voice Status Bar - Minimal */}
          {isConversationConnected && (
            <div className="voice-status-bar" data-testid="voice-interface">
              <div className="audio-level-mini">
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 600)}%` }}></div>
              </div>
              <span className="voice-status-text">{isListening ? 'Listening...' : 'Connected'}</span>
            </div>
          )}
        </main>

        {/* Right Panel Divider */}
        <PanelDivider onDrag={handleRightPanelResize} />

        {/* Right Panel - Voice Assistant Only */}
        <aside className="voice-panel-right" style={{ width: `${rightPanelWidth}px` }}>
          {voiceProvider === 'chatkit' ? (
            // Render RealtimeChatKit when using ChatKit provider - no wrapper needed
            <RealtimeChatKit 
              className="h-full w-full"
              onMessage={(message) => {
                console.log('ChatKit message:', message);
                // Add message to messages array
                const newMessage: Message = {
                  ...message,
                  provider: 'chatkit'
                };
                setMessages((prev: Message[]) => [...prev, newMessage]);
              }}
              onChartCommand={(command) => {
                console.log('ChatKit chart command:', command);
                enhancedChartControl.processEnhancedResponse(command).catch(err => {
                  console.error('Failed to execute ChatKit chart command:', err);
                });
              }}
            />
          ) : (
            // Original voice conversation UI for other providers
            <div className="voice-conversation-section" style={{ height: '100%' }}>
              <h2 className="panel-title">VOICE ASSISTANT</h2>
              <div className="conversation-messages-compact">
                {unifiedMessages.length === 0 ? (
                  <div className="no-messages-state">
                    <p>🎤 {isConversationConnected ? 'Listening...' : 'Click mic to start'}</p>
                  </div>
                  ) : (
                    unifiedMessages.map((msg) => (
                      <div key={msg.id} className="conversation-message-enhanced" data-role={msg.role}>
                        <div className="message-avatar">
                          {msg.role === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-bubble">
                          {msg.role === 'assistant' ? (
                            <StructuredResponse content={msg.content} className="message-text-enhanced" />
                          ) : (
                            <div className="message-text-enhanced">{msg.content}</div>
                          )}
                          {msg.timestamp && (
                            <div className="message-timestamp">
                              {new Date(msg.timestamp).toLocaleTimeString([], { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </div>
                          )}
                        </div>
                      </div>
                    ))
                  )}
              </div>
              
              {/* Text Input Controls */}
              <div className="voice-input-container">
                <input
                  type="text"
                  className="voice-text-input"
                  placeholder={isConversationConnected ? "Type a message..." : "Connect to send messages"}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendTextMessage();
                    }
                  }}
                  disabled={false}
                />
                <button
                  className="voice-send-button"
                  onClick={handleSendTextMessage}
                  disabled={!inputText.trim()}
                  title="Send message"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M22 2L11 13M22 2L15 22L11 13L2 9L22 2Z" />
                  </svg>
                </button>
              </div>
            </div>
          )}
        </aside>
      </div>

      
      {/* Floating Voice Action Button */}
      <button
        className={`voice-fab ${isConversationConnected ? 'active' : ''} ${isConversationConnecting ? 'connecting' : ''}`}
        onClick={() => {
          console.log('🚨 [BUTTON] ==================== MICROPHONE BUTTON CLICKED ====================');
          console.log('🚨 [BUTTON] Step 1: Click registered');
          console.log('🚨 [BUTTON] Step 2: Checking handleConnectToggle...');
          console.log('🚨 [BUTTON] handleConnectToggle type:', typeof handleConnectToggle);
          console.log('🚨 [BUTTON] handleConnectToggle exists:', !!handleConnectToggle);
          console.log('🚨 [BUTTON] Step 3: About to call handleConnectToggle()');
          try {
            handleConnectToggle();
            console.log('🚨 [BUTTON] Step 4: handleConnectToggle() completed successfully');
          } catch (err) {
            console.error('🚨 [BUTTON] ERROR in handleConnectToggle:', err);
            console.error('🚨 [BUTTON] Error details:', String(err));
          }
        }}
        title={isConversationConnected ? 'Disconnect Voice' : 'Connect Voice'}
        data-testid="voice-fab"
      >
        {isConversationConnecting ? '⌛' : isConversationConnected ? '🎤' : '🎙️'}
      </button>
      
      {/* Voice Command Helper - Shows command history and suggestions */}
      <VoiceCommandHelper
        isVisible={isConversationConnected}
        position="right"
        maxHeight={400}
      />

      {/* Debug Widget - Real-time diagnostics */}
      <DebugWidget
        isConnected={isConversationConnected}
        isLoading={isConversationConnecting}
        voiceProvider={voiceProvider}
        openAIConnected={openAIRealtime.isConnected}
        agentVoiceConnected={agentVoice.isConnected}
        realtimeSDKConnected={realtimeSDK.isConnected}
        isBetaMode={voiceProvider === 'realtime-sdk'}
      />
    </div>
  );
};
