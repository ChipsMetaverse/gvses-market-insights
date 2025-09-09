import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TradingChart } from './TradingChart';
import { marketDataService, SymbolSearchResult } from '../services/marketDataService';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
import { useOpenAIRealtimeConversation } from '../hooks/useOpenAIRealtimeConversation';
import { useSymbolSearch } from '../hooks/useSymbolSearch';
// import { ProviderSelector } from './ProviderSelector'; // Removed - conflicts with useElevenLabsConversation
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControlService';
import { CommandToast } from './CommandToast';
import { VoiceCommandHelper } from './VoiceCommandHelper';
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
}

export const TradingDashboardSimple: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'charts' | 'voice'>('charts');
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
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [expandedNews, setExpandedNews] = useState<number | null>(null);
  const [toastCommand, setToastCommand] = useState<{ command: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [chartStyle, setChartStyle] = useState<'candles' | 'line' | 'area'>('candles');
  const [chartTimeframe, setChartTimeframe] = useState('1D');
  const [assetType, setAssetType] = useState<'stock' | 'crypto'>('stock');
  const [voiceProvider, setVoiceProvider] = useState<'elevenlabs' | 'openai'>('elevenlabs');
  
  // Dynamic watchlist with localStorage persistence
  const [watchlist, setWatchlist] = useState<string[]>(() => {
    const saved = localStorage.getItem('marketWatchlist');
    return saved ? JSON.parse(saved) : ['TSLA', 'AAPL', 'NVDA', 'SPY', 'PLTR'];
  });
  const [searchSymbol, setSearchSymbol] = useState('');
  const [isAddingSymbol, setIsAddingSymbol] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
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
  
  // Common callback functions for both providers
  const handleUserTranscript = useCallback((transcript: string) => {
    const message: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: transcript,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, message]);
  }, []);

  const handleAgentResponse = useCallback(async (response: string) => {
    const message: Message = {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: response,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, message]);
    
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

  // ElevenLabs conversation hook
  const elevenLabsHook = useElevenLabsConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: handleUserTranscript,
    onAgentResponse: handleAgentResponse,
    onConnectionChange: handleConnectionChange
  });

  // OpenAI Realtime conversation hook
  const openAIHook = useOpenAIRealtimeConversation({
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
  });

  // Use the appropriate provider
  const currentHook = voiceProvider === 'elevenlabs' ? elevenLabsHook : openAIHook;
  const {
    isConnected,
    isLoading: isConnecting,
    startConversation,
    stopConversation,
    sendTextMessage,
    sendAudioChunk
  } = currentHook;

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
      console.log(`Connecting to ${providerName}...`);
      // Connect (voice recording will auto-start via useEffect when connected)
      try {
        await startConversation();
      } catch (error) {
        console.error('Failed to connect:', error);
        alert(`Failed to connect to ${providerName} voice assistant. Please check your connection and try again.`);
      }
    }
  };

  // Handle text message sending with pre-processing
  const handleSendTextMessage = () => {
    if (inputText.trim() && isConnected) {
      // Stop voice recording before sending text to prevent conflicts
      if (isRecording) {
        console.log('Stopping voice recording before sending text message');
        stopVoiceRecording();
      }
      
      // Use the unified sendTextMessage from the provider hook
      sendTextMessage(inputText);
      setInputText('');
    } else if (!isConnected) {
      alert('Please connect to the voice assistant first');
    }
  };

  const handleTabChange = (tab: 'charts' | 'voice') => {
    setActiveTab(tab);
    console.log('Tab changed to:', tab);
  };

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
      }
    } catch (error) {
      console.error('Error fetching comprehensive data:', error);
      // Technical levels will just remain undefined/empty if this fails
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
      
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1 className="brand">GVSES</h1>
          <span className="subtitle">AI Market Analysis Assistant</span>
        </div>
        
        <div className="header-tabs">
          <button 
            className={`tab-btn ${activeTab === 'charts' ? 'active' : ''}`}
            onClick={() => handleTabChange('charts')}
            data-testid="charts-tab"
          >
            Interactive Charts
          </button>
          <button 
            className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => handleTabChange('voice')}
            data-testid="voice-tab"
          >
            Voice + Manual Control
          </button>
        </div>

        <button className="back-btn" onClick={handleBackToClassic}>Back to Classic</button>
      </header>

      {/* Main Layout */}
      <div className="dashboard-layout">
        {/* Left Panel - Market Insights */}
        <aside className="insights-panel">
          <h2 className="panel-title">MARKET INSIGHTS</h2>
          <div style={{ padding: '10px 15px', borderBottom: '1px solid #3a3a3a', position: 'relative' }}>
            <div style={{ display: 'flex', gap: '8px', position: 'relative' }} ref={searchInputRef}>
              <div style={{ flex: 1, position: 'relative' }}>
                <input
                  type="text"
                  placeholder="Search symbols (e.g., Microsoft, MSFT)"
                  value={searchSymbol}
                  onChange={(e) => setSearchSymbol(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && searchSymbol) {
                      // If there's an exact match, use it; otherwise add the raw input
                      const exactMatch = searchResults.find(
                        r => r.symbol.toLowerCase() === searchSymbol.toLowerCase()
                      );
                      if (exactMatch) {
                        handleSelectSymbol(exactMatch);
                      } else {
                        addToWatchlist(searchSymbol);
                      }
                    }
                  }}
                  onFocus={() => setShowSearchDropdown(searchSymbol.length >= 1 && (searchResults.length > 0 || isSearching))}
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    paddingRight: isSearching ? '32px' : '12px',
                    borderRadius: '4px',
                    border: '1px solid #3a3a3a',
                    backgroundColor: '#1a1a1a',
                    color: '#ffffff',
                    fontSize: '14px'
                  }}
                  disabled={isAddingSymbol}
                />
                {isSearching && (
                  <div style={{
                    position: 'absolute',
                    right: '8px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    fontSize: '12px',
                    color: '#888'
                  }}>
                    ...
                  </div>
                )}
                
                {/* Search Results Dropdown */}
                {showSearchDropdown && (
                  <div style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    backgroundColor: '#1a1a1a',
                    border: '1px solid #3a3a3a',
                    borderTop: 'none',
                    borderRadius: '0 0 4px 4px',
                    maxHeight: '200px',
                    overflowY: 'auto',
                    zIndex: 1000
                  }}>
                    {isSearching && searchResults.length === 0 ? (
                      <div style={{ padding: '12px', color: '#888', fontSize: '14px' }}>
                        Searching...
                      </div>
                    ) : searchError ? (
                      <div style={{ padding: '12px', color: '#ff6b6b', fontSize: '14px' }}>
                        {searchError}
                      </div>
                    ) : searchResults.length > 0 ? (
                      searchResults.map((result) => (
                        <div
                          key={result.symbol}
                          onClick={() => handleSelectSymbol(result)}
                          style={{
                            padding: '12px',
                            cursor: 'pointer',
                            borderBottom: '1px solid #2a2a2a',
                            fontSize: '14px'
                          }}
                          onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#2a2a2a'}
                          onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                        >
                          <div style={{ fontWeight: 'bold', color: '#4a9eff' }}>
                            {result.symbol}
                          </div>
                          <div style={{ color: '#ccc', fontSize: '12px', marginTop: '2px' }}>
                            {result.name} • {result.exchange}
                          </div>
                        </div>
                      ))
                    ) : searchSymbol.length >= 1 && (
                      <div style={{ padding: '12px', color: '#888', fontSize: '14px' }}>
                        No symbols found for "{searchSymbol}"
                      </div>
                    )}
                  </div>
                )}
              </div>
              <button
                onClick={() => {
                  if (searchSymbol) {
                    const exactMatch = searchResults.find(
                      r => r.symbol.toLowerCase() === searchSymbol.toLowerCase()
                    );
                    if (exactMatch) {
                      handleSelectSymbol(exactMatch);
                    } else {
                      addToWatchlist(searchSymbol);
                    }
                  }
                }}
                disabled={!searchSymbol || isAddingSymbol}
                style={{
                  padding: '8px 16px',
                  borderRadius: '4px',
                  backgroundColor: searchSymbol && !isAddingSymbol ? '#4a9eff' : '#3a3a3a',
                  color: '#ffffff',
                  border: 'none',
                  cursor: searchSymbol && !isAddingSymbol ? 'pointer' : 'not-allowed',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                {isAddingSymbol ? '...' : 'Add'}
              </button>
            </div>
          </div>
          <div className="insights-content">
            {isLoadingStocks ? (
              <div className="loading-spinner">Loading market data...</div>
            ) : (
              stocksData.map((stock) => (
                <div 
                  key={stock.symbol} 
                  className={`stock-item ${selectedSymbol === stock.symbol ? 'selected' : ''}`}
                  onClick={() => setSelectedSymbol(stock.symbol)}
                  style={{ cursor: 'pointer', position: 'relative' }}
                >
                  <div className="stock-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span className="stock-symbol">{stock.symbol}</span>
                    {watchlist.length > 1 && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeFromWatchlist(stock.symbol);
                        }}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#666',
                          cursor: 'pointer',
                          padding: '2px 6px',
                          fontSize: '16px',
                          lineHeight: '1'
                        }}
                        title="Remove from watchlist"
                      >
                        ×
                      </button>
                    )}
                  </div>
                  <div className="stock-price">
                    <span className="price">${stock.price.toFixed(2)}</span>
                    <span className={`change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                      {stock.change >= 0 ? '↑' : '↓'} {Math.abs(stock.changePercent).toFixed(2)}%
                    </span>
                  </div>
                  {stock.volume && (
                    <div className="stock-volume">Vol: {(stock.volume / 1000000).toFixed(1)}M</div>
                  )}
                </div>
              ))
            )}
          </div>
        </aside>

        {/* Center - Chart and Voice */}
        <main className="main-content">
          {/* Chart */}
          <div className="chart-section">
            <div className="chart-wrapper">
              <TradingChart 
                symbol={selectedSymbol} 
                technicalLevels={technicalLevels}
                chartStyle={chartStyle}
                timeframe={chartTimeframe}
                assetType={assetType}
                data-testid="trading-chart"
                onChartReady={(chart: any) => {
                  chartRef.current = chart;
                  chartControlService.setChartRef(chart);
                  enhancedChartControl.setChartRef(chart);
                  console.log('Chart ready for enhanced agent control');
                }}
              />
            </div>
          </div>

          {/* Voice Assistant */}
          <div className="voice-section" data-testid="voice-interface">
            {/* Voice Provider Switcher - Simplified */}
            {!isConnected && (
              <div className="provider-switcher" data-testid="provider-switcher">
                <div className="provider-switcher-header">
                  <span className="provider-label">Select Voice Provider:</span>
                  <div className="provider-options">
                    <button 
                      className={`provider-btn ${voiceProvider === 'elevenlabs' ? 'active' : ''}`}
                      onClick={() => setVoiceProvider('elevenlabs')}
                      disabled={isConnected}
                      data-testid="provider-elevenlabs"
                    >
                      🎤 ElevenLabs
                    </button>
                    <button 
                      className={`provider-btn ${voiceProvider === 'openai' ? 'active' : ''}`}
                      onClick={() => setVoiceProvider('openai')}
                      disabled={isConnected}
                      data-testid="provider-openai"
                    >
                      🤖 OpenAI Realtime
                    </button>
                  </div>
                  <div className="provider-info">
                    {voiceProvider === 'elevenlabs' ? (
                      <span className="provider-status">Conversational AI with natural voices</span>
                    ) : (
                      <span className="provider-status">Speech-to-speech with function calling</span>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {/* Main Connect Button - Single prominent button */}
            {!isConnected && (
              <div style={{ padding: '20px', textAlign: 'center' }}>
                <button 
                  className="primary-connect-btn"
                  onClick={handleConnectToggle}
                  disabled={isConnecting}
                  style={{
                    width: '80%',
                    fontSize: '18px',
                    padding: '16px 24px',
                    borderRadius: '8px',
                    border: 'none',
                    background: isConnecting ? '#666' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    cursor: isConnecting ? 'wait' : 'pointer',
                    fontWeight: 'bold',
                    boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
                    transition: 'all 0.3s ease'
                  }}
                  data-testid="main-connect-button"
                >
                  {isConnecting ? '⏳ Connecting...' : '🎤 Connect Voice Assistant'}
                </button>
              </div>
            )}
            
            {/* Disconnect Button - Shows when connected */}
            {isConnected && (
              <div style={{ padding: '10px 20px', textAlign: 'center' }}>
                <button 
                  className="disconnect-btn"
                  onClick={handleConnectToggle}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '6px',
                    border: '1px solid #ff4444',
                    background: 'transparent',
                    color: '#ff4444',
                    cursor: 'pointer',
                    fontSize: '14px',
                    transition: 'all 0.3s ease'
                  }}
                  data-testid="disconnect-button"
                >
                  🔴 Disconnect
                </button>
              </div>
            )}
            
            {/* Listening Interface */}
            <div className="listening-interface">
              <div className="listening-animation">
                <div 
                  className={`mic-icon ${isListening ? 'listening' : ''}`}
                >
                  <div className="pulse-ring"></div>
                  <div className="pulse-ring"></div>
                  <div className="pulse-ring"></div>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <path d="M12 14C13.66 14 15 12.66 15 11V5C15 3.34 13.66 2 12 2C10.34 2 9 3.34 9 5V11C9 12.66 10.34 14 12 14Z" fill="currentColor"/>
                    <path d="M17 11C17 14.03 14.53 16.5 11.5 16.5C8.47 16.5 6 14.03 6 11H4C4 14.41 6.72 17.23 10 17.72V21H14V17.72C17.28 17.23 20 14.41 20 11H17Z" fill="currentColor"/>
                  </svg>
                </div>
                <div className="listening-text">
                  {isConnected ? 
                    '🎧 Listening... (speak anytime)' : 
                    isConnecting ? '⏳ Connecting...' :
                    '🔌 Click mic to connect'}
                </div>
                {isRecording && (
                  <div className="recording-timer" data-testid="recording-timer">{recordingTime}</div>
                )}
              </div>
              
              <div className="audio-visualizer" data-testid="audio-level">
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 600)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
              </div>
              
              <div className="connection-status" data-testid="connection-status">
                <span className="status-dot"></span>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>

            {/* Voice Conversation */}
            <div className="voice-conversation">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h3 style={{ margin: 0 }}>Voice Conversation</h3>
                {/* ProviderSelector removed - conflicts with useElevenLabsConversation */}
              </div>
              <div className="conversation-messages" data-testid="messages-container">
                {messages.length === 0 ? (
                  <div className="no-messages">
                    <p style={{ fontSize: '14px', color: '#666' }}>Click mic to connect • Speak anytime when connected</p>
                    <div style={{ marginTop: '10px', padding: '10px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
                      <p style={{ fontSize: '12px', margin: '5px 0', color: '#888' }}>Try these commands:</p>
                      <p style={{ fontSize: '11px', margin: '3px 0', color: '#666' }}>"What's the price of Tesla?"</p>
                      <p style={{ fontSize: '11px', margin: '3px 0', color: '#666' }}>"Show me Apple's chart"</p>
                      <p style={{ fontSize: '11px', margin: '3px 0', color: '#666' }}>"What's the market sentiment?"</p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg) => (
                    <div key={msg.id} className="conversation-message">
                      <div className="message-icon">
                        {msg.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="message-content">
                        <div className="message-text">{msg.content}</div>
                        {msg.timestamp && (
                          <div className="message-time">{msg.timestamp}</div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
              
              <div className="conversation-footer">
                <span className="footer-text">
                  {messages.length} message{messages.length !== 1 ? 's' : ''} • 
                  {isConnected ? 'Connected' : isConnecting ? 'Connecting...' : 'Disconnected'}
                </span>
              </div>
              
              
              {/* Text Input Section - Only shown when connected */}
              {isConnected && (
                <div className="text-input-section">
                  <div className="text-input-group">
                    <input
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendTextMessage()}
                      onFocus={() => {
                        // Stop voice recording when focusing on text input
                        if (isRecording) {
                          console.log('Stopping voice recording - text input focused');
                          stopVoiceRecording();
                        }
                      }}
                      placeholder="Type a message (or just speak)..."
                      className="text-input"
                      data-testid="message-input"
                    />
                    <button 
                      onClick={handleSendTextMessage}
                      disabled={!inputText.trim()}
                      className="send-button"
                      data-testid="send-button"
                    >
                      Send
                    </button>
                  </div>
                </div>
              )}
              
              <div className="voice-commands">
                <strong>Try these commands:</strong>
                <ul>
                  <li>"What's the price of Tesla?"</li>
                  <li>"Show me Apple's chart"</li>
                  <li>"What's the market sentiment?"</li>
                  <li>"Any news on {selectedSymbol}?"</li>
                </ul>
              </div>
            </div>
          </div>
        </main>

        {/* Right Panel - Chart Analysis */}
        <aside className="analysis-panel">
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
                    <span>QE Level</span>
                    <span className="level-val qe">
                      ${technicalLevels.qe_level ? technicalLevels.qe_level.toFixed(2) : '---'}
                    </span>
                  </div>
                  <div className="level-row">
                    <span>ST Level</span>
                    <span className="level-val st">
                      ${technicalLevels.st_level ? technicalLevels.st_level.toFixed(2) : '---'}
                    </span>
                  </div>
                  <div className="level-row">
                    <span>LTB Level</span>
                    <span className="level-val ltb">
                      ${technicalLevels.ltb_level ? technicalLevels.ltb_level.toFixed(2) : '---'}
                    </span>
                  </div>
                </div>

                <div className="pattern-section">
                  <h4>PATTERN DETECTION</h4>
                  <div className="pattern-box">
                    <div className="pattern-name">
                      {stocksData.find(s => s.symbol === selectedSymbol)?.changePercent > 0 ? 'Bullish Flag' : 'Consolidation'}
                    </div>
                    <div className="pattern-conf">
                      Confidence: {Math.floor(65 + Math.random() * 25)}%
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </aside>
      </div>

      {/* Footer */}
      <footer className="dashboard-footer">
        <div className="footer-tabs">
          <button 
            className={`footer-tab ${activeTab === 'charts' ? 'active' : ''}`}
            onClick={() => handleTabChange('charts')}
          >
            Interactive Charts
          </button>
          <button 
            className={`footer-tab ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => handleTabChange('voice')}
          >
            Voice + Manual Control
          </button>
          <button className="footer-tab">Educational Analysis</button>
        </div>
        <button className="chart-ready">📊 Chart Ready</button>
      </footer>
      
      {/* Voice Command Helper - Shows command history and suggestions */}
      <VoiceCommandHelper 
        isVisible={activeTab === 'voice' || isConnected}
        position="right"
        maxHeight={400}
      />
    </div>
  );
};