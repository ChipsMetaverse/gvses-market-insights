import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { TradingChart } from './TradingChart';
import { marketDataService, SymbolSearchResult } from '../services/marketDataService';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
import { useOpenAIRealtimeConversation } from '../hooks/useOpenAIRealtimeConversation';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { useSymbolSearch } from '../hooks/useSymbolSearch';
// import { ProviderSelector } from './ProviderSelector'; // Removed - conflicts with useElevenLabsConversation
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';
import { useIndicatorContext } from '../contexts/IndicatorContext';
import { CommandToast } from './CommandToast';
import { VoiceCommandHelper } from './VoiceCommandHelper';
import StructuredResponse from './StructuredResponse';
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
  provider?: 'agent' | 'elevenlabs' | 'openai';  // Track message source
  data?: Record<string, any>;
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

export const TradingDashboardSimple: React.FC = () => {
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
  const [stockNews, setStockNews] = useState<any[]>([]);
  const [technicalLevels, setTechnicalLevels] = useState<any>({});
  const [detectedPatterns, setDetectedPatterns] = useState<any[]>([]);
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [expandedNews, setExpandedNews] = useState<number | null>(null);
  const [toastCommand, setToastCommand] = useState<{ command: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [chartStyle, setChartStyle] = useState<'candles' | 'line' | 'area'>('candles');
  const [chartTimeframe, setChartTimeframe] = useState('1D');
  const [assetType, setAssetType] = useState<'stock' | 'crypto'>('stock');
  const [voiceProvider, setVoiceProvider] = useState<'elevenlabs' | 'agent'>('agent');
  
  // Dynamic watchlist with localStorage persistence
  const [watchlist, setWatchlist] = useState<string[]>(() => {
    const saved = localStorage.getItem('marketWatchlist');
    return saved ? JSON.parse(saved) : ['TSLA', 'AAPL', 'NVDA', 'SPY', 'PLTR'];
  });
  const [searchSymbol, setSearchSymbol] = useState('');
  const [isAddingSymbol, setIsAddingSymbol] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);

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
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Use the symbol search hook with debouncing
  const { searchResults, isSearching, searchError } = useSymbolSearch(searchSymbol, 300);

  // Save watchlist to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('marketWatchlist', JSON.stringify(watchlist));
  }, [watchlist]);

  // Show/hide search dropdown based on input focus and results
  useEffect(() => {
    const shouldShow = searchSymbol.length >= 1 && (searchResults.length > 0 || isSearching);
    setShowSearchDropdown(shouldShow);
  }, [searchSymbol, searchResults, isSearching]);

  // Handle clicking outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchInputRef.current && !searchInputRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Handle selecting a symbol from search results
  const handleSelectSymbol = (result: SymbolSearchResult) => {
    setSearchSymbol('');
    setShowSearchDropdown(false);
    addToWatchlist(result.symbol);
  };

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
    
    setIsAddingSymbol(true);
    
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
      setSearchSymbol('');
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
      setIsAddingSymbol(false);
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

  const handleConnectionChange = useCallback((connected: boolean) => {
    if (!connected) {
      setIsRecording(false);
      setIsListening(false);
      stopVoiceRecording();
    }
  }, []);

  // Track previous provider for cleanup
  const previousProviderRef = useRef<string>(voiceProvider);
  
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
  const agentVoiceHook = voiceProvider === 'agent' ? useAgentVoiceConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onMessage: (message) => {
      const msg: Message = {
        id: message.id,
        role: message.role,
        content: message.content,
        timestamp: new Date(message.timestamp).toLocaleTimeString(),
        provider: 'agent' as const,  // Add provider tracking
        data: message.data
      };
      setMessages(prev => [...prev, msg]);
      
      // Show tools used in toast for assistant messages
      if (message.role === 'assistant' && message.toolsUsed && message.toolsUsed.length > 0) {
        setToastCommand({ command: `🔧 Tools: ${message.toolsUsed.join(', ')}`, type: 'info' });
        setTimeout(() => setToastCommand(null), 3000);
      }

      if (message.role === 'assistant') {
        const chartCommands = message.data?.chart_commands as string[] | undefined;
        if (Array.isArray(chartCommands) && chartCommands.length > 0) {
          enhancedChartControl.processEnhancedResponse(chartCommands.join(' ')).catch(err => {
            console.error('Failed to execute chart commands from message data:', err);
          });
        }
      }
    },
    onConnectionChange: handleConnectionChange,
    onError: (error) => {
      setToastCommand({ command: `❌ Error: ${error}`, type: 'error' });
      setTimeout(() => setToastCommand(null), 4000);
    },
    onThinking: (thinking) => {
      // Show thinking indicator in UI if needed
      console.log('Agent thinking:', thinking);
    }
  }) : null;

  // ElevenLabs conversation hook - only mount when active
  const elevenLabsHook = voiceProvider === 'elevenlabs' ? useElevenLabsConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: handleUserTranscript,
    onAgentResponse: handleAgentResponse,
    onConnectionChange: handleConnectionChange
  }) : null;

  // OpenAI Realtime conversation hook - only mount when active
  const openAIHook = voiceProvider === 'openai' ? useOpenAIRealtimeConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: handleUserTranscript,
    onAgentResponse: handleAgentResponse,
    onConnectionChange: handleConnectionChange,
    onToolCall: (toolName: string, args: any) => {
      console.log('OpenAI tool call:', toolName, args);
      setToastCommand({ command: `🔧 Tool: ${toolName}`, type: 'info' });
      setTimeout(() => setToastCommand(null), 2000);
    },
    onToolResult: (toolName: string, result: any) => {
      console.log('OpenAI tool result:', toolName, result);
      setToastCommand({ command: `✅ Tool completed: ${toolName}`, type: 'success' });
      setTimeout(() => setToastCommand(null), 2000);
    }
  }) : null;

  // Use the appropriate provider hook (with fallback to avoid null errors)
  const currentHook = agentVoiceHook || elevenLabsHook || openAIHook || {
    isConnected: false,
    isLoading: false,
    sendTextMessage: () => {},
    messages: [],
    connect: () => {},
    disconnect: () => {},
    startConversation: () => {},
    stopConversation: () => {},
    sendAudioChunk: () => {}
  };
  
  // Handle different function names from different hooks
  const {
    isConnected,
    isLoading: isConnecting,
    sendTextMessage,
    messages: hookMessages
  } = currentHook;
  
  // Map function names (agent hook uses connect/disconnect, others use startConversation/stopConversation)
  const startConversation = voiceProvider === 'agent' ? 
    (currentHook as any).connect : 
    (currentHook as any).startConversation;
  
  const stopConversation = voiceProvider === 'agent' ? 
    (currentHook as any).disconnect : 
    (currentHook as any).stopConversation;
  
  const sendAudioChunk = (currentHook as any).sendAudioChunk;

  // Create unified message thread with provider-aware deduplication
  const unifiedMessages = useMemo(() => {
    if (voiceProvider === 'agent') {
      // Agent voice hook manages its own unified messages
      return messages;
    } else {
      // Legacy providers: combine local text messages and voice transcripts
      const allMessages = [...messages, ...hookMessages];
      
      // Provider-aware deduplication: only dedupe same provider + exact content within 2 seconds
      const deduplicatedMessages = allMessages.filter((message, index, array) => {
        const isDuplicate = array.findIndex((other, otherIndex) => {
          if (otherIndex >= index) return false; // Only check earlier messages
          
          const messageTime = new Date(message.timestamp).getTime();
          const otherTime = new Date(other.timestamp).getTime();
          const timeDiff = Math.abs(messageTime - otherTime);
          
          // Only dedupe if same provider (or both missing provider) AND same content
          const sameProvider = message.provider === other.provider || 
                              (!message.provider && !other.provider);
          
          return sameProvider &&
                 message.role === other.role && 
                 message.content === other.content && 
                 timeDiff < 2000; // Within 2 seconds
        });
        
        return isDuplicate === -1; // Keep if no duplicate found
      });
    
      // Sort by timestamp for chronological order
      return deduplicatedMessages.sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );
    }
  }, [messages, hookMessages, voiceProvider]);

  // Track previous provider to only disconnect on actual provider changes
  const prevProviderRef = useRef(voiceProvider);
  
  // Reset states when voice provider changes (prevent stuck loading states)
  useEffect(() => {
    const prevProvider = prevProviderRef.current;
    const currentProvider = voiceProvider;
    
    console.log(`Voice provider switched from ${prevProvider} to: ${currentProvider}`);
    
    // Only disconnect if provider actually changed AND we're connected
    if (prevProvider !== currentProvider && isConnected) {
      console.log('Disconnecting from previous provider due to provider switch');
      stopConversation();
    }
    
    // Update ref for next comparison
    prevProviderRef.current = currentProvider;
    
    // Clear any lingering UI states only on actual provider change
    if (prevProvider !== currentProvider) {
      setIsRecording(false);
      setIsListening(false);
      setInputText('');
    }
  }, [voiceProvider, stopConversation, isConnected]);

  // Convert Float32 PCM to Int16 PCM (required by ElevenLabs)
  const convertFloat32ToInt16 = (float32Array: Float32Array): Int16Array => {
    const int16Array = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
      const s = Math.max(-1, Math.min(1, float32Array[i]));
      int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
  };

  // Start voice recording
  const startVoiceRecording = useCallback(async () => {
    if (!isConnected) {
      console.log('Cannot start recording - not connected to ElevenLabs');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      
      // Load the AudioWorklet module
      await audioContextRef.current.audioWorklet.addModule('/audio-processor.js');
      
      // Create AudioWorklet node
      audioWorkletRef.current = new AudioWorkletNode(audioContextRef.current, 'audio-processor');
      
      // Set up message handling from the audio processor
      audioWorkletRef.current.port.onmessage = (event) => {
        if (event.data.type === 'audio') {
          // Process audio buffer
          const inputData = event.data.buffer;
          
          // Only send audio if there's actual sound (not silence)
          const sum = inputData.reduce((acc, val) => acc + Math.abs(val), 0);
          const level = sum / inputData.length;
          
          if (level > 0.001) {
            // Convert and send audio
            const pcm16 = convertFloat32ToInt16(inputData);
            const base64 = btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)));
            sendAudioChunk(base64);
          }
        } else if (event.data.type === 'volume') {
          // Update audio level visualization
          setAudioLevel(event.data.level);
        }
      };
      
      // Connect audio nodes
      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);
      sourceRef.current.connect(audioWorkletRef.current);
      audioWorkletRef.current.connect(audioContextRef.current.destination);
      
      setIsRecording(true);
      setIsListening(true);
      
      // Start recording timer
      let seconds = 0;
      recordingTimerRef.current = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        setRecordingTime(`${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`);
      }, 1000);
    } catch (error) {
      console.error('Failed to start recording:', error);
      alert('Failed to access microphone. Please check your permissions.');
    }
  }, [isConnected, startConversation, sendAudioChunk]);

  // Stop voice recording
  const stopVoiceRecording = useCallback(() => {
    // Clean up audio nodes
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
    
    // Stop media stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // Clear timer
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    
    setIsRecording(false);
    setIsListening(false);
    setRecordingTime('00:00');
    setAudioLevel(0);
  }, []);

  
  // Single connect/disconnect handler with debounce
  const handleConnectToggle = async () => {
    console.log('🎯 handleConnectToggle called, voiceProvider:', voiceProvider, 'isConnected:', isConnected);
    
    const now = Date.now();
    
    // Debounce rapid clicks (minimum 1 second between attempts)
    if (now - connectionAttemptTimeRef.current < 1000) {
      console.log('Debouncing rapid connection attempt');
      return;
    }
    
    connectionAttemptTimeRef.current = now;
    
    if (isConnected) {
      console.log('Disconnecting...');
      // Disconnect everything
      stopVoiceRecording();
      stopConversation();
      hasStartedRecordingRef.current = false;
    } else {
      const providerName = voiceProvider === 'elevenlabs' ? 'ElevenLabs' : 'OpenAI Realtime';
      console.log(`🚀 Connecting to ${providerName}...`);
      console.log('📞 About to call startConversation()...');
      
      // Connect (voice recording will auto-start via useEffect when connected)
      try {
        await startConversation();
        console.log('✅ startConversation() completed');
      } catch (error) {
        console.error('❌ Failed to connect:', error);
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
        await startConversation();
      } catch (error) {
        console.error('Failed to connect to OpenAI:', error);
        alert('Failed to connect to OpenAI Realtime. Please check your connection and try again.');
      }
    }, 100);
  };

  // Handle text message sending - route ONLY to active provider
  const handleSendTextMessage = () => {
    console.log('🎯 handleSendTextMessage called');
    console.log('📝 Input text:', inputText);
    console.log('🔌 Is connected:', isConnected);
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
        provider: voiceProvider as 'agent' | 'elevenlabs' | 'openai'
      };

      // Add to local messages for immediate UI feedback
      setMessages(prev => [...prev, userMessage]);
      console.log('💬 Added user message to chat thread');

      // Clear input immediately for better UX
      const messageText = trimmedQuery;
      setInputText('');
      
      // Route ONLY to the active provider
      switch(voiceProvider) {
        case 'agent':
          // Agent text should work immediately (no voice connection required)
          fetch((import.meta.env.VITE_API_URL || window.location.origin) + '/api/agent/orchestrate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: messageText })
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
          if (isConnected) {
            sendTextMessage(messageText);
          } else {
            setTimeout(() => {
              const offlineMessage = {
                id: `assistant-${Date.now()}-${Math.random()}`,
                role: 'assistant' as const,
                content: 'Please connect the voice assistant (mic) to use voice providers.',
                timestamp: new Date().toISOString(),
                provider: voiceProvider
              } as any;
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
    
    // Register with enhanced service
    enhancedChartControl.registerCallbacks({
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
            if (metadata?.assetType) {
              setAssetType(metadata.assetType);
            }
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
        if (metadata?.assetType) {
          setAssetType(metadata.assetType);
        }
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
        setChartStyle(style);
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
  }, []);

  // Track if we've already started recording to prevent duplicates
  const hasStartedRecordingRef = useRef(false);
  const connectionAttemptTimeRef = useRef<number>(0);
  const isMountedRef = useRef(true);
  
  // Auto-start voice recording when connected - DISABLED to prevent text/audio conflicts
  // Users should manually start voice recording when needed
  useEffect(() => {
    let isMounted = true;
    let timer: NodeJS.Timeout;
    
    // DISABLED: Auto-start causes conflicts when user wants to type text
    // if (isConnected && !isRecording && !hasStartedRecordingRef.current) {
    //   console.log('Connection established, starting voice recording...');
    //   hasStartedRecordingRef.current = true;
    //   
    //   // Small delay to ensure everything is ready
    //   timer = setTimeout(() => {
    //     if (isMounted && isConnected && !isRecording) {
    //       startVoiceRecording();
    //     }
    //   }, 500);
    // }
    
    // Reset flag when disconnected
    if (!isConnected) {
      hasStartedRecordingRef.current = false;
    }
    
    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [isConnected, isRecording, startVoiceRecording]); // Include all dependencies

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
          <span className="subtitle">AI Market Analysis Assistant</span>
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
            {isConnected ? '🟢' : '⚪'}
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
                  {detectedPatterns.length === 0 ? (
                    <div className="pattern-empty">No high-confidence patterns detected right now.</div>
                  ) : (
                    detectedPatterns.map((pattern, index) => (
                      <div key={`${pattern.type}-${index}`} className="pattern-box">
                        <div className="pattern-name">{pattern.description || pattern.type}</div>
                        <div className="pattern-conf">
                          Confidence: {pattern.confidence ? `${Math.round(pattern.confidence)}%` : 'N/A'}
                        </div>
                        {pattern.agent_explanation && (
                          <div className="pattern-desc">{pattern.agent_explanation}</div>
                        )}
                      </div>
                    ))
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
            <div className="chart-wrapper">
              <TradingChart 
                symbol={selectedSymbol} 
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
          {isConnected && (
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
          {/* Voice Conversation Section */}
          <div className="voice-conversation-section" style={{ height: '100%' }}>
            <h2 className="panel-title">VOICE ASSISTANT</h2>
            <div className="conversation-messages-compact">
              {unifiedMessages.length === 0 ? (
                <div className="no-messages-state">
                  <p>🎤 {isConnected ? 'Listening...' : 'Click mic to start'}</p>
                </div>
                ) : (
                  unifiedMessages.map((msg) => (
                    <div key={msg.id} className="conversation-message-enhanced">
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
                placeholder={isConnected ? "Type a message..." : "Connect to send messages"}
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
        </aside>
      </div>

      
      {/* Floating Voice Action Button */}
      <button 
        className={`voice-fab ${isConnected ? 'active' : ''} ${isConnecting ? 'connecting' : ''}`}
        onClick={handleConnectToggle}
        title={isConnected ? 'Disconnect Voice' : 'Connect Voice'}
        data-testid="voice-fab"
      >
        {isConnecting ? '⌛' : isConnected ? '🎤' : '🎙️'}
      </button>
      
      {/* Voice Command Helper - Shows command history and suggestions */}
      <VoiceCommandHelper 
        isVisible={isConnected}
        position="right"
        maxHeight={400}
      />
    </div>
  );
};
