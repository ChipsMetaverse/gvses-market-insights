import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { TradingChart } from './TradingChart';
import { TimeRangeSelector } from './TimeRangeSelector';
import { marketDataService } from '../services/marketDataService';
import { agentOrchestratorService, ChartSnapshot } from '../services/agentOrchestratorService';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
import { useOpenAIRealtimeConversation } from '../hooks/useOpenAIRealtimeConversation';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { useRealtimeSDKConversation } from '../hooks/useRealtimeSDKConversation';
import { useAgentChartIntegration } from '../hooks/useAgentChartIntegration';
import { BackendAgentProvider } from '../providers/BackendAgentProvider';
import { RealtimeChatKit } from './RealtimeChatKit';
// import { ProviderSelector } from './ProviderSelector'; // Removed - conflicts with useElevenLabsConversation
// FIXED: Microphone now requested BEFORE connection (following official OpenAI pattern)
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';
import { useChartCommandPolling } from '../hooks/useChartCommandPolling';
import { getSessionId } from '../utils/session';
import { useIndicatorContext } from '../contexts/IndicatorContext';
import { CommandToast } from './CommandToast';
import { VoiceCommandHelper } from './VoiceCommandHelper';
import StructuredResponse from './StructuredResponse';
import { Tooltip } from './Tooltip';
import { Toaster } from './ui/toaster';
import { OnboardingTour } from './OnboardingTour';
import { EconomicCalendar } from './EconomicCalendar';
import { TimeRange } from '../types/dashboard';
import {
  normalizeChartCommandPayload,
  type ChartCommandPayload,
} from '../utils/chartCommandUtils';
import type { StructuredChartCommand as ChartControlStructuredCommand } from '../services/chartControlService';
import type { ProviderConfig } from '../providers/types';
import './TradingDashboardSimple.css';
import './TradingDashboardMobile.css';
import { useSymbolSearch } from '../hooks/useSymbolSearch';
import { Search } from 'lucide-react';
// Widget Testing Imports
import {
  EconomicCalendarWidget,
  MarketNewsFeedWidget,
  TechnicalLevelsWidget,
  PatternDetectionWidget,
  TradingChartDisplayWidget,
  type WidgetType,
} from './widgets';
import { useWidgetActions } from '../hooks/useWidgetActions';

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
// Two distinct categories:
// - Intraday (<1D): Recent high-resolution data (1-7 days)
// - Daily+ (>=1D): Historical long-term data (3+ years)
const timeframeToDays = (timeframe: TimeRange): { fetch: number, display: number } => {
  const map: Record<TimeRange, { fetch: number, display: number }> = {
    // Intraday - Alpaca-native intervals only
    '1m': { fetch: 2, display: 2 },      // 700 bars: 700min ÷ 390min/day = ~2 days
    '5m': { fetch: 9, display: 9 },      // 700 bars: 3500min ÷ 390min/day = ~9 days
    '15m': { fetch: 7, display: 7 },     // Initial load only - lazy loading handles more

    // Hours
    '1H': { fetch: 150, display: 150 }, // 700 bars: 700hrs ÷ 6.5hrs/day × 1.4 = ~150 days

    // Daily+
    '1D': { fetch: 1000, display: 1000 }, // 700 bars: 700 trading days ≈ 1000 calendar days
    '1W': { fetch: 3650, display: 3650 }, // ~10 years for weekly candles
    '1M': { fetch: 7300, display: 7300 }, // ~20 years for monthly candles

    // Long-term (yearly aggregation)
    '1Y': { fetch: 18250, display: 18250 },   // ~50 years → aggregated to yearly bars (Yahoo Finance has decades of data)

    // Special
    'YTD': (() => {
      const ytdDays = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 1).getTime()) / (1000 * 60 * 60 * 24));
      return { fetch: Math.max(ytdDays + 50, 250), display: ytdDays };  // Fetch extra for indicators
    })(),
    'MAX': { fetch: 9125, display: 9125 }   // 25 years
  };
  return map[timeframe] || { fetch: 365, display: 365 };
};

// Helper function to convert TimeRange to data interval for API
const timeframeToInterval = (timeframe: TimeRange): string => {
  const map: Record<TimeRange, string> = {
    // Intraday - Alpaca-native intervals only
    '1m': '1m',
    '5m': '5m',
    '15m': '15m',

    // Hours
    '1H': '1h',

    // Daily+
    '1D': '1d',
    '1W': '1w',   // Weekly candles (Alpaca-native)
    '1M': '1mo',  // Monthly candles (Alpaca-native)

    // Long-term
    '1Y': '1y',   // Yearly candles (monthly → yearly aggregation)
    'YTD': '1d',
    'MAX': '1d'
  };
  return map[timeframe] || '1d';
};

// Helper function to format news timestamps to relative time
const formatNewsTime = (publishedAt: string | number): string => {
  try {
    const now = Date.now();
    const published = typeof publishedAt === 'number' ? publishedAt * 1000 : new Date(publishedAt).getTime();
    const diffMs = now - published;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays}d ago`;
    } else if (diffHours > 0) {
      return `${diffHours}h ago`;
    } else {
      const diffMins = Math.floor(diffMs / (1000 * 60));
      return diffMins > 0 ? `${diffMins}m ago` : 'Just now';
    }
  } catch {
    return 'Recently';
  }
};

const CRYPTO_SYMBOLS = new Set([
  'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'MATIC', 'AVAX', 'LTC',
  'XRP', 'DOGE', 'SHIB', 'UNI', 'LINK', 'BCH', 'XLM',
]);

export const TradingDashboardSimple: React.FC = () => {
  console.log('%c📺 [COMPONENT RENDER] TradingDashboardSimple rendering...', 'background: #4CAF50; color: white; font-size: 16px; font-weight: bold;');

  // Removed tab system - using unified interface
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [audioLevel, setAudioLevel] = useState(0);
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [isLoadingStocks, setIsLoadingStocks] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('TSLA');
  const [selectedTimeframe, setSelectedTimeframe] = useState<TimeRange>('1Y');
  const [stockNews, setStockNews] = useState<any[]>([]);
  const [newsError, setNewsError] = useState<string | null>(null);
  const [technicalLevels, setTechnicalLevels] = useState<any>({});
  const [isLoadingTechnicalLevels, setIsLoadingTechnicalLevels] = useState(false);
  const [technicalLevelsError, setTechnicalLevelsError] = useState<string | null>(null);
  const [detectedPatterns, setDetectedPatterns] = useState<any[]>([]);
  const [isSearchExpanded, setIsSearchExpanded] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Widget Testing State
  const [activeWidget, setActiveWidget] = useState<WidgetType | null>(null);

  // Streaming news state
  const [streamingNews] = useState<any[]>([]);
  const [isStreaming] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const [backendPatterns, setBackendPatterns] = useState<any[]>([]);
  const [currentSnapshot, setCurrentSnapshot] = useState<ChartSnapshot | null>(null);
  const pendingPatternFocusRef = useRef<number | null>(null);
  const searchContainerRef = useRef<HTMLDivElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const { searchResults, isSearching, searchError, hasSearched } = useSymbolSearch(searchQuery);
  const shouldShowSearchResults = isSearchExpanded && searchQuery.trim().length > 0;

  // Technical Levels are now fetched in fetchStockAnalysis() to avoid duplicate systems

  // Pattern visualization state - Phase 1: Smart Visibility Controls
  const [patternVisibility, setPatternVisibility] = useState<{ [patternId: string]: boolean }>({});
  const [hoveredPatternId, setHoveredPatternId] = useState<string | null>(null);
  const [showAllPatterns, setShowAllPatterns] = useState(false);
  const [showMorePatterns, setShowMorePatterns] = useState(false);
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  const [expandedNews, setExpandedNews] = useState<number | null>(null);
  const [isCalendarCollapsed, setIsCalendarCollapsed] = useState(false);
  const [toastCommand, setToastCommand] = useState<{ command: string; type: 'success' | 'error' | 'info' } | null>(null);
  const [chartTimeframe, setChartTimeframe] = useState('1Y');
  const [voiceProvider] = useState<ConversationProviderKey>('chatkit');
  const [showOnboarding, setShowOnboarding] = useState(() => {
    const completed = localStorage.getItem('gvses_onboarding_completed');
    return completed !== 'true';
  });
  
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
  
  // Mobile chart/chat split ratio (percentage for chart)
  const [mobileChartRatio, setMobileChartRatio] = useState(() => {
    const saved = localStorage.getItem('mobileChartRatio');
    return saved ? parseFloat(saved) : 35;
  });

  // Desktop chart/analysis split ratio (percentage for chart)
  const [chartPanelRatio, setChartPanelRatio] = useState(() => {
    const saved = localStorage.getItem('chartPanelRatio');
    return saved ? parseFloat(saved) : 60; // Default 60% for chart, 40% for analysis
  });

  // Dragging state for chart divider
  const [isDraggingDivider, setIsDraggingDivider] = useState(false);

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

  useEffect(() => {
    if (isSearchExpanded && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchExpanded]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      if (!isSearchExpanded) return;
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setIsSearchExpanded(false);
        setSearchQuery('');
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('touchstart', handleClickOutside);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('touchstart', handleClickOutside);
    };
  }, [isSearchExpanded]);

  const handleRightPanelResize = useCallback((delta: number) => {
    setRightPanelWidth(prev => Math.max(300, Math.min(500, prev - delta)));
  }, []);

  // Desktop chart/analysis divider resize handler
  const handleChartDividerDrag = useCallback((delta: number) => {
    const mainContentElement = document.querySelector('.main-content') as HTMLElement;
    if (!mainContentElement) return;

    const containerHeight = mainContentElement.clientHeight;
    const deltaPercent = (delta / containerHeight) * 100;

    setChartPanelRatio(prev => {
      const newRatio = Math.max(30, Math.min(90, prev + deltaPercent)); // 30-90% range
      localStorage.setItem('chartPanelRatio', newRatio.toString());
      return newRatio;
    });
  }, []);

  // Mobile chart/chat divider resize handler
  const handleMobileDividerDrag = useCallback((startY: number) => {
    const containerHeight = window.innerHeight - 200; // Account for header and tab bar

    const handleMove = (moveEvent: TouchEvent | MouseEvent) => {
      const currentY = 'touches' in moveEvent ? (moveEvent as TouchEvent).touches[0].clientY : (moveEvent as MouseEvent).clientY;
      const deltaY = currentY - startY;
      const deltaPercent = (deltaY / containerHeight) * 100;

      setMobileChartRatio(prev => {
        const newRatio = Math.max(20, Math.min(70, prev + deltaPercent));
        localStorage.setItem('mobileChartRatio', newRatio.toString());
        return newRatio;
      });
    };

    const handleEnd = () => {
      document.removeEventListener('mousemove', handleMove as any);
      document.removeEventListener('mouseup', handleEnd);
      (document as any).removeEventListener('touchmove', handleMove as any);
      document.removeEventListener('touchend', handleEnd);
    };

    document.addEventListener('mousemove', handleMove as any);
    document.addEventListener('mouseup', handleEnd);
    (document as any).addEventListener('touchmove', handleMove as any, { passive: false });
    document.addEventListener('touchend', handleEnd);
  }, []);

  // Chart Command Polling - NEW cursor-based system with CommandBus
  useChartCommandPolling({
    sessionId: getSessionId(),
    enabled: true,
    intervalMs: 2000,
    onCommands: useCallback((envelopes) => {
      console.log(`[TradingDashboardSimple] Received ${envelopes.length} chart command(s)`);

      for (const { seq, command } of envelopes) {
        console.log(`[TradingDashboardSimple] Processing command #${seq}:`, command.type, command.payload);

        try {
          const p: any = command.payload || {};

          switch (command.type) {
            case 'change_symbol': {
              const symbol = String(p.symbol || p.ticker || '').toUpperCase();
              if (symbol) {
                setSelectedSymbol(symbol);
                setToastCommand({ command: `📈 Symbol: ${symbol}`, type: 'success' });
                setTimeout(() => setToastCommand(null), 3000);
              }
              break;
            }

            case 'set_timeframe': {
              const timeframe = String(p.timeframe || p.interval || '');
              if (timeframe) {
                setChartTimeframe(timeframe);
                setToastCommand({ command: `⏱️ Timeframe: ${timeframe}`, type: 'success' });
                setTimeout(() => setToastCommand(null), 3000);
              }
              break;
            }

            case 'toggle_indicator': {
              const name = String(p.name || p.indicator || '');
              const enabled = Boolean(p.enabled ?? true);
              if (name) {
                enhancedChartControl.toggleIndicator(name, enabled);
                setToastCommand({
                  command: `${name} ${enabled ? 'enabled' : 'disabled'}`,
                  type: 'info'
                });
                setTimeout(() => setToastCommand(null), 3000);
              }
              break;
            }

            case 'highlight_pattern': {
              const pattern = String(p.pattern || '');
              if (pattern) {
                const message = enhancedChartControl.revealPattern(pattern, p.info);
                setToastCommand({ command: message, type: 'info' });
                setTimeout(() => setToastCommand(null), 3000);
              }
              break;
            }

            default:
              console.warn('[TradingDashboardSimple] Unknown command type:', command.type);
          }
        } catch (error) {
          console.error('[TradingDashboardSimple] Error executing command #' + seq, error);
          setToastCommand({
            command: `❌ Command failed: ${command.type}`,
            type: 'error'
          });
          setTimeout(() => setToastCommand(null), 3000);
        }
      }
    }, [])
  });

  // Message persistence storage keys
  const STORAGE_KEYS = {
    messages: 'trading-assistant-messages',
    session: 'trading-assistant-session'
  };

  // Mobile responsiveness state (inline, no helper hooks)
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window === 'undefined') {
      return false;
    }
    return window.innerWidth <= 768;
  });
  const [activePanel, setActivePanel] = useState<'analysis' | 'chart' | 'voice'>('chart');
  const containerRef = useRef<HTMLDivElement | null>(null);
  const tabBarRef = useRef<HTMLElement | null>(null);

  // Streaming Chart Commands: BackendAgentProvider for chart command streaming
  const backendProviderRef = useRef<BackendAgentProvider | null>(null);
  const [streamingProvider, setStreamingProvider] = useState<BackendAgentProvider | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return undefined;
    }

    const handleResize = () => {
      const mobile = window.innerWidth <= 1024;
      setIsMobile(mobile);
      if (!mobile) {
        setActivePanel('chart');
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    const element = containerRef.current;
    if (!isMobile || !element) {
      return undefined;
    }

    // Mobile tabs: only 2 tabs now (analysis | chart+voice merged)
    const tabs: Array<'analysis' | 'chart' | 'voice'> = ['analysis', 'chart'];
    let touchStartX: number | null = null;
    let touchStartedInTabBar = false;

    const handleTouchStart = (event: TouchEvent) => {
      if (event.touches.length > 0) {
        const touch = event.touches[0];
        touchStartX = touch.clientX;

        // Check if touch started inside the tab bar
        if (tabBarRef.current) {
          const tabBarRect = tabBarRef.current.getBoundingClientRect();
          const touchY = touch.clientY;
          touchStartedInTabBar = touchY >= tabBarRect.top && touchY <= tabBarRect.bottom;
        } else {
          touchStartedInTabBar = false;
        }
      }
    };

    const handleTouchEnd = (event: TouchEvent) => {
      if (touchStartX === null || event.changedTouches.length === 0 || !touchStartedInTabBar) {
        touchStartX = null;
        touchStartedInTabBar = false;
        return;
      }

      const deltaX = event.changedTouches[0].clientX - touchStartX;
      const threshold = 40;
      if (Math.abs(deltaX) >= threshold) {
        const currentIndex = tabs.indexOf(activePanel);
        if (deltaX < 0 && currentIndex < tabs.length - 1) {
          setActivePanel(tabs[currentIndex + 1]);
        } else if (deltaX > 0 && currentIndex > 0) {
          setActivePanel(tabs[currentIndex - 1]);
        }
      }

      touchStartX = null;
      touchStartedInTabBar = false;
    };

    element.addEventListener('touchstart', handleTouchStart, { passive: true });
    element.addEventListener('touchend', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchend', handleTouchEnd);
    };
  }, [isMobile, activePanel]);

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

  // removeFromWatchlist removed - unused function
  
  // Audio processing refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletRef = useRef<AudioWorkletNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  
  // Chart control ref
  const chartRef = useRef<any>(null);

  // Widget actions hook
  const { handleAction } = useWidgetActions({
    chartRef,
    onClose: () => setActiveWidget(null),
  });

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
      const commands = await enhancedChartControl.processEnhancedResponse(response, [], []);
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


    setIsRecording(false);
    setIsListening(false);
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

  const applyChartSnapshot = async (snapshot: ChartSnapshot | null) => {
    if (!snapshot) {
      return;
    }

    const legacyCommands = snapshot.chart_commands ?? [];
    const structuredCommands = snapshot.chart_commands_structured ?? [];

    if (legacyCommands.length > 0 || structuredCommands.length > 0) {
      console.log('Executing backend chart commands:', { legacyCommands, structuredCommands });
      enhancedChartControl
        .processEnhancedResponse('', legacyCommands, structuredCommands)
        .catch(err => {
          console.error('Failed to execute backend chart commands:', err);
        });
    }
  };

  // Phase 1: Pattern Visibility Control Helpers
  const getPatternId = useCallback((pattern: any): string => {
    // Generate unique pattern ID from pattern properties
    return `${pattern.pattern_type}_${pattern.start_time}_${pattern.confidence || pattern.strength || 75}`;
  }, []);

  const shouldDrawPattern = useCallback((pattern: any): boolean => {
    const patternId = getPatternId(pattern);
    
    // Pattern should be drawn if:
    // 1. It's currently being hovered (preview mode)
    // 2. It's explicitly selected/toggled on (persistent visibility)
    // 3. "Show All" is enabled
    const isHovered = hoveredPatternId === patternId;
    const isSelected = patternVisibility[patternId] === true;
    const showAll = showAllPatterns;
    
    const shouldDraw = isHovered || isSelected || showAll;
    
    if (shouldDraw) {
      console.log(`[Pattern Visibility] Drawing pattern ${patternId}:`, {
        isHovered,
        isSelected,
        showAll,
      });
    }
    
    return shouldDraw;
  }, [hoveredPatternId, patternVisibility, showAllPatterns, getPatternId]);

  const handlePatternCardHover = useCallback((pattern: any) => {
    const patternId = getPatternId(pattern);
    console.log(`[Pattern Interaction] Hover ENTER: ${patternId}`);
    setHoveredPatternId(patternId);
  }, [getPatternId]);

  const handlePatternCardLeave = useCallback(() => {
    console.log(`[Pattern Interaction] Hover LEAVE`);
    setHoveredPatternId(null);
  }, []);

  const handlePatternToggle = useCallback((pattern: any) => {
    const patternId = getPatternId(pattern);
    const currentState = patternVisibility[patternId] || false;
    console.log(`[Pattern Interaction] Toggle ${patternId}: ${currentState} → ${!currentState}`);
    
    setPatternVisibility(prev => ({
      ...prev,
      [patternId]: !currentState
    }));
  }, [patternVisibility, getPatternId]);

  const handleShowAllToggle = useCallback(() => {
    console.log(`[Pattern Interaction] Show All: ${showAllPatterns} → ${!showAllPatterns}`);
    setShowAllPatterns(prev => !prev);
  }, [showAllPatterns]);

  // Pattern visualization handlers
  const drawPatternOverlay = useCallback((pattern: any) => {
    const patternTimestamp: number | null = pattern.start_time ?? null;
    
    console.log('[Pattern] Drawing overlay:', {
      pattern_type: pattern.pattern_type,
      has_visual_config: !!pattern.visual_config,
      has_chart_metadata: !!pattern.chart_metadata,
      timestamp: patternTimestamp,
    });

    // Verify pattern sits inside the visible range; if not, schedule a focus
    if (patternTimestamp) {
      const visibleRange = enhancedChartControl.getVisibleTimeRange?.();
      if (visibleRange) {
        if (patternTimestamp < visibleRange.from || patternTimestamp > visibleRange.to) {
          console.warn('[Pattern] Pattern outside visible range - scheduling focus');
          pendingPatternFocusRef.current = patternTimestamp;
        }
      }
    }

    // PHASE 2C: Use visual_config if available (new enhanced rendering)
    const visualConfig = pattern.visual_config;
    if (visualConfig) {
      console.log('[Pattern] Using visual_config for enhanced rendering');
      
      // Draw boundary box around pattern
      if (visualConfig.boundary_box) {
        console.log('[Pattern] Drawing boundary box');
        enhancedChartControl.drawPatternBoundaryBox(visualConfig.boundary_box);
      }
      
      // Note: Candle highlighting omitted as it requires chart data access
      // and Lightweight Charts has limited support for candle color overlays.
      // The boundary box and markers provide sufficient visual indication.
      
      // Draw pattern markers (arrows, circles, etc.)
      if (visualConfig.markers && visualConfig.markers.length > 0) {
        console.log('[Pattern] Drawing', visualConfig.markers.length, 'markers');
        visualConfig.markers.forEach((marker: any) => {
          enhancedChartControl.drawPatternMarker(marker);
        });
      }
    }

    // Draw trendlines and levels from chart_metadata (existing Phase 1 behavior)
    if (pattern.chart_metadata) {
      const { trendlines, levels } = pattern.chart_metadata;
      
      trendlines?.forEach((trendline: any, idx: number) => {
        const color = trendline.type === 'upper_trendline' ? '#ef4444' : '#3b82f6';
        console.log('[Pattern] Drawing trendline', idx, trendline);
        enhancedChartControl.drawTrendLine(
          trendline.start.time,
          trendline.start.price,
          trendline.end.time,
          trendline.end.price,
          color
        );
      });

      levels?.forEach((level: any, idx: number) => {
        const label = level.type === 'support' ? 'Support' : 'Resistance';
        console.log('[Pattern] Drawing level', idx, level);
        
        // Fix for single-day patterns: ensure endTime > startTime
        const startTime = pattern.start_time || patternTimestamp || Date.now() / 1000;
        let endTime = pattern.end_time || startTime;
        if (endTime <= startTime) {
          endTime = startTime + 86400; // Add 1 day for single-day patterns
        }
        
        console.log(`[Pattern] Time range for level: ${new Date(startTime * 1000).toISOString()} → ${new Date(endTime * 1000).toISOString()}`);
        enhancedChartControl.highlightLevel(level.price, label.toLowerCase() === 'support' ? 'support' : 'resistance', label);
      });
    }

    const chartControl = enhancedChartControl as any;
    try {
      if (typeof chartControl.update === 'function') {
        chartControl.update();
      } else if (typeof chartControl.render === 'function') {
        chartControl.render();
      } else if (typeof chartControl.invalidate === 'function') {
        chartControl.invalidate();
      } else if (chartControl.timeScale && typeof chartControl.timeScale().fitContent === 'function') {
        chartControl.timeScale().fitContent();
      }
    } catch (error) {
      console.error('[Pattern] Error triggering chart refresh:', error);
    }
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
          manager.closeConnection();
        });
      } else if (previousProvider === 'openai') {
        // OpenAI service cleanup is handled by the hook internally
        // No manual disconnect needed
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
        const rawLegacy = message.data?.chart_commands;
        const legacyCommands = Array.isArray(rawLegacy) ? rawLegacy : [];
        const structuredCommands = Array.isArray(message.data?.chart_commands_structured)
          ? message.data!.chart_commands_structured
          : [];

        if (legacyCommands.length > 0 || structuredCommands.length > 0) {
          enhancedChartControl
            .processEnhancedResponse(message.content, legacyCommands, structuredCommands)
            .catch(err => {
              console.error('Failed to execute chart commands from message data:', err);
            });

          const loadCommand = legacyCommands.find(cmd => cmd.startsWith('LOAD:'));
          const structuredSymbol = structuredCommands.find(cmd => cmd.type === 'symbol');
          const nextSymbol = loadCommand?.split(':')[1] || structuredSymbol?.payload?.symbol;

          if (nextSymbol) {
            setTimeout(() => {
              fetchAndApplySnapshot(nextSymbol as string);
            }, 1000);
          }
        }
      }
    },
    onConnectionChange: handleConnectionChange,
    onError: (error: string) => {
      setToastCommand({ command: `❌ Error: ${error}`, type: 'error' });
      setTimeout(() => setToastCommand(null), 4000);
    },
    onThinking: (thinking: boolean) => {
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

  // Streaming Chart Commands: Initialize BackendAgentProvider
  useEffect(() => {
    const initProvider = async () => {
      if (!backendProviderRef.current) {
        const apiUrl = import.meta.env.VITE_API_URL || window.location.origin;
        const providerConfig: ProviderConfig = {
          type: 'custom',
          name: 'Backend Agent',
          apiUrl,
          capabilities: BackendAgentProvider.getDefaultCapabilities(),
        };

        const provider = new BackendAgentProvider(providerConfig);

        await provider.initialize(providerConfig);

        backendProviderRef.current = provider;
        setStreamingProvider(provider);
        console.log('[TradingDashboardSimple] BackendAgentProvider initialized for chart streaming');
      }
    };

    initProvider().catch(err => {
      console.error('[TradingDashboardSimple] Failed to initialize BackendAgentProvider:', err);
    });

    // Cleanup on unmount
    return () => {
      if (backendProviderRef.current) {
        backendProviderRef.current.destroy().catch(err => {
          console.error('[TradingDashboardSimple] Error destroying provider:', err);
        });
        backendProviderRef.current = null;
        setStreamingProvider(null);
      }
    };
  }, []);

  // Streaming Chart Commands: Enable chart integration with provider
  useAgentChartIntegration({
    provider: streamingProvider || undefined,
  });

  // ChatKit conversation (Agent Builder workflow)
  const [chatKitReady] = useState(false);
  const [chatKitError] = useState<string | null>(null);
  const [chatKitControl] = useState<any>(null);
  const [chatKitInitAttempts, setChatKitInitAttempts] = useState(0);
  const [chatKitInitMessageShown, setChatKitInitMessageShown] = useState(false);
  const MAX_CHATKIT_INIT_ATTEMPTS = 3;

  // chatKitConfig removed - now handled by RealtimeChatKit component

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
            // Don't use await here as we're not in an async context
            chatKitControl.sendMessage(text);
            console.log('✅ Message sent to ChatKit Agent Builder');
          } catch (error) {
            console.error('❌ ChatKit send error:', error);
            throw error;
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

    // Only disconnect if provider actually changed
    if (prevProvider !== currentProvider) {
      // Access stopConversation directly to avoid dependency on conversationProviders object
      const providers = conversationProviders;
      if (providers[prevProvider]?.isConnected) {
        console.log('Disconnecting from previous provider due to provider switch');
        providers[prevProvider].stopConversation();
      }

      setIsRecording(false);
      setIsListening(false);
      setInputText('');
    }

    prevProviderRef.current = currentProvider;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [voiceProvider]); // Removed conversationProviders to prevent infinite re-render loop

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

  // handleOpenAIConnect removed - unused function

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

              const legacyCommands = Array.isArray(data.chart_commands) ? data.chart_commands : [];
              const structuredCommands = Array.isArray(data.chart_commands_structured)
                ? data.chart_commands_structured
                : [];

              if (legacyCommands.length > 0 || structuredCommands.length > 0) {
                console.info('[agent] executing_chart_commands', JSON.stringify({
                  timestamp: responseTimestamp,
                  messageId,
                  legacyCommands,
                  structuredCommands
                }));
                enhancedChartControl
                  .processEnhancedResponse(data.text || '', legacyCommands, structuredCommands)
                  .catch(err => {
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

  // startNewsStream removed - unused streaming function

  // stopNewsStream and handleBackToClassic removed - unused functions

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
        
        const changePercent = stockPrice.change_percent || 0;
        
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
          price: stockPrice.price || 0,
          change: stockPrice.change || 0,
          changePercent: stockPrice.change_percent || 0,
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
      setNewsError(null);
    } catch (error: any) {
      console.error('Error fetching news:', error);
      setStockNews([]);
      setNewsError('Unable to load news at this time. Please try again later.');
    }
    
    // Fetch pattern detection data for trendlines and technical levels
    setIsLoadingTechnicalLevels(true);
    setTechnicalLevelsError(null);
    try {
      const patternData = await marketDataService.getPatternDetection(symbol);
      const patterns = patternData.patterns || [];
      console.log(`[Pattern API] Fetched ${patterns.length} patterns from backend for ${symbol}`);

      // Extract technical levels from trendlines (same data displayed on chart)
      if (patternData.trendlines && patternData.trendlines.length > 0) {
        const blLine = patternData.trendlines.find((t: any) => t.label === 'BL');
        const shLine = patternData.trendlines.find((t: any) => t.label === 'SH');
        const btdLine = patternData.trendlines.find((t: any) => t.label === 'BTD (200 SMA)');
        const pdhLine = patternData.trendlines.find((t: any) => t.label === 'PDH');
        const pdlLine = patternData.trendlines.find((t: any) => t.label === 'PDL');

        setTechnicalLevels({
          sell_high_level: shLine?.start?.price || null,
          buy_low_level: blLine?.start?.price || null,
          btd_level: btdLine?.start?.price || null,
          pdh_level: pdhLine?.start?.price || null,
          pdl_level: pdlLine?.start?.price || null,
          data_source: 'pattern_detection'
        });
        setTechnicalLevelsError(null);
        console.log('📊 [TECHNICAL LEVELS] Extracted from trendlines:', {
          SH: shLine?.start?.price,
          BL: blLine?.start?.price,
          BTD: btdLine?.start?.price,
          PDH: pdhLine?.start?.price,
          PDL: pdlLine?.start?.price
        });
      } else {
        setTechnicalLevels({});
        setTechnicalLevelsError('No technical levels available');
      }
      setIsLoadingTechnicalLevels(false);

      if (patterns.length > 0) {
        const now = Date.now();
        const filterDays = 365;
        const filterDate = now - filterDays * 24 * 60 * 60 * 1000;

        const recentPatterns = patterns.filter((p: any) => {
          if (!p.start_time) return true;
          const patternTime = p.start_time * 1000;
          return patternTime >= filterDate;
        });

        console.log('[Pattern API] Retained', recentPatterns.length, 'patterns out of', patterns.length, 'within', filterDays, 'days');

        const sortedPatterns = [...recentPatterns].sort((a: any, b: any) => (b.confidence || 0) - (a.confidence || 0));
        setBackendPatterns(sortedPatterns);
        setDetectedPatterns(sortedPatterns.slice(0, 3));

        // Patterns will be drawn by the pattern rendering useEffect based on visibility state
      } else {
        setBackendPatterns([]);
        setDetectedPatterns([]);
        enhancedChartControl.clearDrawings();
      }
    } catch (error: any) {
      console.error('Error fetching pattern detection data:', error);
      setBackendPatterns([]);
      setDetectedPatterns([]);
      enhancedChartControl.clearDrawings();
      // Also handle technical levels error
      setTechnicalLevels({});
      setTechnicalLevelsError(error.message || 'Unable to load technical levels');
      setIsLoadingTechnicalLevels(false);
    }
    
    setIsLoadingNews(false);
  };

  // Handle technical levels update from chart component
  // This callback is triggered when the chart fetches new pattern detection data
  // (e.g., when interval/timeframe changes)
  const handleTechnicalLevelsUpdate = useCallback((patternData: any) => {
    if (!patternData || !patternData.trendlines || patternData.trendlines.length === 0) {
      console.log('[TECH LEVELS CALLBACK] No trendlines in pattern data');
      setTechnicalLevels({});
      return;
    }

    // Extract technical levels from trendlines (same logic as fetchStockAnalysis)
    const blLine = patternData.trendlines.find((t: any) => t.label === 'BL');
    const shLine = patternData.trendlines.find((t: any) => t.label === 'SH');
    const btdLine = patternData.trendlines.find((t: any) => t.label === 'BTD (200 SMA)');
    const pdhLine = patternData.trendlines.find((t: any) => t.label === 'PDH');
    const pdlLine = patternData.trendlines.find((t: any) => t.label === 'PDL');

    const updatedLevels = {
      sell_high_level: shLine?.start?.price || null,
      buy_low_level: blLine?.start?.price || null,
      btd_level: btdLine?.start?.price || null,
      pdh_level: pdhLine?.start?.price || null,
      pdl_level: pdlLine?.start?.price || null,
      data_source: 'chart_callback'
    };

    setTechnicalLevels(updatedLevels);
    setTechnicalLevelsError(null);

    console.log('📊 [TECH LEVELS CALLBACK] Updated from chart:', {
      SH: updatedLevels.sell_high_level,
      BL: updatedLevels.buy_low_level,
      BTD: updatedLevels.btd_level,
      PDH: updatedLevels.pdh_level,
      PDL: updatedLevels.pdl_level
    });
  }, []);

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
  
  // Cleanup streaming connection on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);
  
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
        const isKnownCrypto = CRYPTO_SYMBOLS.has(upperSymbol);
        
        if (!isValidFormat) {
          console.warn(`Invalid symbol format rejected: ${symbol}`);
          setToastCommand({ command: `❌ Invalid symbol: ${symbol}`, type: 'error' });
          setTimeout(() => setToastCommand(null), 3000);
          return;
        }
        
        // For stocks, check if it's in the watchlist (unless it's crypto)
        if (!isKnownCrypto && !watchlist.includes(upperSymbol.replace('-USD', ''))) {
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
        const icon = isKnownCrypto ? '₿' : '📈';
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
      onCommandExecuted: (_command: string, success: boolean, message: string) => {
        // Show toast notification for command execution
        setToastCommand({
          command: message,
          type: success ? 'success' : 'error'
        });
      },
      onCommandError: (error: string) => {
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
  
  // Process backend chart commands when snapshot is updated
  useEffect(() => {
    applyChartSnapshot(currentSnapshot);
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

  // Phase 1: Smart pattern drawing based on visibility state
  useEffect(() => {
    console.log('[Pattern Rendering] Re-rendering patterns based on visibility state');
    
    // Clear all existing pattern overlays
    enhancedChartControl.clearDrawings();
    
    if (backendPatterns.length === 0) {
      return;
    }

    // Draw only patterns that should be visible
    backendPatterns.forEach(pattern => {
      if (shouldDrawPattern(pattern)) {
        const patternId = getPatternId(pattern);
        const isHovered = hoveredPatternId === patternId;
        
        console.log(`[Pattern Rendering] Drawing pattern ${patternId} (hovered: ${isHovered})`);
        drawPatternOverlay(pattern);
      }
    });
  }, [backendPatterns, hoveredPatternId, patternVisibility, showAllPatterns, shouldDrawPattern, drawPatternOverlay, getPatternId]);

  useEffect(() => {
    if (pendingPatternFocusRef.current !== null) {
      enhancedChartControl.focusOnTime?.(pendingPatternFocusRef.current, 60 * 60 * 24 * 5);
      pendingPatternFocusRef.current = null;
    }
  }, [backendPatterns, enhancedChartControl]);

  return (
    <div ref={containerRef} className="trading-dashboard-simple" data-testid="trading-dashboard">
      {/* Command Toast Notifications */}
      {toastCommand && (
        <CommandToast
          command={toastCommand.command}
          type={toastCommand.type}
          duration={2500}
          onClose={() => setToastCommand(null)}
        />
      )}

      {/* UI Toasts for Network/Error Notifications */}
      <Toaster />

      {/* Header with Integrated Ticker Cards */}
      <header className="dashboard-header-with-tickers header-container">
        <div className="header-left">
          <h1 className="brand">GVSES</h1>
          <span className="subtitle">Market Assistant</span>
        </div>

        <div className={`header-search ${isSearchExpanded ? 'expanded' : ''}`} ref={searchContainerRef}>
          <button
            type="button"
            className="search-toggle"
            aria-label="Search symbols"
            onClick={() => setIsSearchExpanded(prev => !prev)}
          >
            <Search size={18} />
          </button>

          {isSearchExpanded && (
            <>
              <input
                ref={searchInputRef}
                type="text"
                className="search-input"
                placeholder="Search tickers or companies"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                aria-label="Search tickers or companies"
              />
              {shouldShowSearchResults && (
                <div className="search-results" role="listbox">
                  {isSearching && <div className="search-status">Searching...</div>}
                  {searchError && <div className="search-status error">{searchError}</div>}
                  {!isSearching && !searchError && hasSearched && searchResults.length === 0 && (
                    <div className="search-status">No matches found</div>
                  )}
                  {searchResults.map((result) => (
                    <button
                      key={result.symbol}
                      type="button"
                      className="search-result-item"
                      onMouseDown={() => {
                        setSelectedSymbol(result.symbol);
                        setIsSearchExpanded(false);
                        setSearchQuery('');
                      }}
                    >
                      <div className="search-result-content">
                        <span className="result-symbol">{result.symbol}</span>
                        <span className="result-name">{result.name}</span>
                        <span className={`asset-class-badge ${result.asset_class || 'stock'}`}>
                          {(result.asset_class || 'stock').toUpperCase()}
                        </span>
                      </div>
                      <span className="result-exchange">{result.exchange}</span>
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>

        {/* Ticker Display - Desktop cards or Mobile dropdown */}
        {isMobile ? (
          <div className="mobile-ticker-select">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
            >
              {stocksData.map((stock) => (
                <option key={stock.symbol} value={stock.symbol}>
                  {stock.symbol} - ${stock.price.toFixed(2)} ({stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(1)}%)
                </option>
              ))}
            </select>
          </div>
        ) : (
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
        )}

        <div className="header-controls">
          <span className="status-indicator">
            {isConversationConnected ? '🟢' : '⚪'}
          </span>
        </div>
      </header>


      {/* Main Layout */}
      <div className="dashboard-layout">
        {/* Center - Chart + Chart Analysis (stacked vertically) */}
        <main
          className={`main-content panel ${isMobile ? 'mobile-chart-voice-merged' : ''}`}
          data-panel="chart"
          data-active={!isMobile || activePanel === 'chart' || activePanel === 'analysis'}
        >
          {/* Chart Section */}
          <div
            className="chart-section chart-container"
            data-active={!isMobile || activePanel === 'chart'}
            style={isMobile
              ? { flex: `0 0 ${mobileChartRatio}%`, maxHeight: `${mobileChartRatio}%` }
              : { flex: `0 0 ${chartPanelRatio}%`, minHeight: '300px' }
            }
          >
            {/* Timeframe Selector - Alpaca-native intervals only */}
            <TimeRangeSelector
              selected={selectedTimeframe}
              options={['1m', '5m', '15m', '1H', '1D', '1W', '1M', '1Y', 'YTD', 'MAX']}
              onChange={(range) => setSelectedTimeframe(range)}
              showAdvancedMenu={false}
            />
            <div className="chart-wrapper">
              <TradingChart
                symbol={selectedSymbol}
                initialDays={timeframeToDays(selectedTimeframe).fetch}
                displayDays={timeframeToDays(selectedTimeframe).display}
                interval={timeframeToInterval(selectedTimeframe)}
                // technicalLevels removed - now provided by pattern-detection API via drawAutoTrendlines
                // This prevents duplicate SH/BL/BTD lines (pattern-detection already draws these as key levels)
                enableLazyLoading={true}
                showCacheInfo={false}
                onChartReady={(chart: any) => {
                  chartRef.current = chart;
                  chartControlService.setChartRef(chart);
                  enhancedChartControl.setChartRef(chart);
                  console.log('Chart ready for enhanced agent control with lazy loading');
                }}
                onTechnicalLevelsUpdate={handleTechnicalLevelsUpdate}
              />
            </div>

            {/* Voice Status Indicator (desktop only - minimal) */}
            {!isMobile && isConversationConnected && (
              <div className="voice-status-bar" data-testid="voice-interface">
                <div className="audio-level-mini">
                  <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
                  <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                  <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 600)}%` }}></div>
                </div>
                <span className="voice-status-text">{isListening ? 'Listening...' : 'Connected'}</span>
              </div>
            )}

            {/* Technical Levels - Bottom of Chart Panel */}
            <div className="technical-levels-chart-bottom">
              {isLoadingTechnicalLevels ? (
                <div className="level-loading">Loading...</div>
              ) : technicalLevelsError ? (
                <div className="level-error">{technicalLevelsError}</div>
              ) : (
                <div className="levels-grid">
                  <div className="level-row-compact">
                    <Tooltip content="Resistance level - Consider taking profits near this price">
                      <span>Sell High</span>
                    </Tooltip>
                    <span className="level-val qe">
                      ${technicalLevels.sell_high_level ? technicalLevels.sell_high_level.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="level-row-compact">
                    <Tooltip content="Support level - Potential buying opportunity near this price">
                      <span>Buy Low</span>
                    </Tooltip>
                    <span className="level-val st">
                      ${technicalLevels.buy_low_level ? technicalLevels.buy_low_level.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="level-row-compact">
                    <Tooltip content="Buy The Dip - Strong support level for accumulation">
                      <span>BTD</span>
                    </Tooltip>
                    <span className="level-val ltb">
                      ${technicalLevels.btd_level ? technicalLevels.btd_level.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  {technicalLevels.pdh_level && (
                    <div className="level-row-compact">
                      <Tooltip content="Previous Day High - Intraday resistance from yesterday's trading">
                        <span>PDH</span>
                      </Tooltip>
                      <span className="level-val qe">
                        ${technicalLevels.pdh_level.toFixed(2)}
                      </span>
                    </div>
                  )}
                  {technicalLevels.pdl_level && (
                    <div className="level-row-compact">
                      <Tooltip content="Previous Day Low - Intraday support from yesterday's trading">
                        <span>PDL</span>
                      </Tooltip>
                      <span className="level-val st">
                        ${technicalLevels.pdl_level.toFixed(2)}
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Draggable Divider for Chart/Analysis resize */}
          {!isMobile && (
            <PanelDivider
              onDrag={handleChartDividerDrag}
              orientation="horizontal"
            />
          )}

          {/* Chart Analysis Panel - Now Below Chart */}
          <aside
            className="analysis-panel-below"
            data-panel="analysis"
            data-active={!isMobile || activePanel === 'analysis'}
            style={!isMobile
              ? { flex: `1 1 ${100 - chartPanelRatio}%`, minHeight: '200px', overflow: 'auto' }
              : undefined
            }
          >
          <h2 className="panel-title">CHART ANALYSIS</h2>
          <div className="analysis-content">
            <div className="calendar-card">
              <button
                type="button"
                className="calendar-card__header"
                onClick={() => setIsCalendarCollapsed(prev => !prev)}
                aria-expanded={!isCalendarCollapsed}
              >
                <span>ECONOMIC CALENDAR</span>
                <span className="calendar-card__toggle" aria-hidden="true">
                  {isCalendarCollapsed ? 'Show' : 'Hide'}
                </span>
              </button>
              {!isCalendarCollapsed && (
                <div className="calendar-card__body">
                  <EconomicCalendar />
                </div>
              )}
            </div>

            {/* Two-column layout: Pattern Detection + News Feed */}
            <div className="analysis-grid-two-column">
              {/* Left Column: Pattern Detection */}
              <div className="pattern-section">
                  <h4>PATTERN DETECTION</h4>
                  
                  {backendPatterns.length === 0 && detectedPatterns.length === 0 ? (
                    <div className="pattern-empty">No patterns detected. Try different timeframes or symbols.</div>
                  ) : (
                    <>
                      {/* Phase 1: Master "Show All" Toggle */}
                      <div style={{ 
                        marginBottom: '12px', 
                        display: 'flex', 
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px',
                        background: 'rgba(59, 130, 246, 0.1)',
                        borderRadius: '4px',
                        border: '1px solid rgba(59, 130, 246, 0.3)'
                      }}>
                        <label style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '6px',
                          cursor: 'pointer',
                          fontSize: '13px',
                          fontWeight: '600',
                          flex: 1
                        }}>
                          <input
                            type="checkbox"
                            checked={showAllPatterns}
                            onChange={handleShowAllToggle}
                            style={{ cursor: 'pointer' }}
                          />
                          <span>Show All Patterns</span>
                        </label>
                        <span style={{ fontSize: '11px', color: '#666' }}>
                          {backendPatterns.length} detected
                        </span>
                      </div>
                      
                      {/* Organize patterns by category */}
                      {(() => {
                        const reversalPatterns = backendPatterns.filter(p => p.category === 'Reversal');
                        const continuationPatterns = backendPatterns.filter(p => p.category === 'Continuation');
                        const neutralPatterns = backendPatterns.filter(p => p.category === 'Neutral');
                        const INITIAL_VISIBLE = 5;
                        const totalPatterns = backendPatterns.length;
                        const visiblePatterns = showMorePatterns ? backendPatterns : backendPatterns.slice(0, INITIAL_VISIBLE);
                        
                        const renderPattern = (pattern: any) => {
                          const patternId = getPatternId(pattern);
                          const isVisible = patternVisibility[patternId] || false;
                          const isHovered = hoveredPatternId === patternId;
                          const signal = pattern.signal || 'neutral';
                          
                          return (
                            <div
                              key={patternId}
                              className={`pattern-item ${isHovered ? 'hovered' : ''} ${isVisible ? 'selected' : ''}`}
                              onMouseEnter={() => handlePatternCardHover(pattern)}
                              onMouseLeave={handlePatternCardLeave}
                              onClick={() => handlePatternToggle(pattern)}
                              style={{
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                border: isHovered ? '1px solid rgba(59, 130, 246, 0.5)' : undefined,
                                background: isHovered ? 'rgba(59, 130, 246, 0.05)' : undefined
                              }}
                            >
                              <div className="pattern-header">
                                <span className="pattern-name">{pattern.pattern_type || pattern.type}</span>
                                <span className={`pattern-signal ${signal}`}>
                                  {signal === 'bullish' ? '↑' : signal === 'bearish' ? '↓' : '•'} {signal}
                                </span>
                                <label className="pattern-toggle" onClick={(e) => e.stopPropagation()}>
                                  <input
                                    type="checkbox"
                                    checked={isVisible}
                                    onChange={() => handlePatternToggle(pattern)}
                                  />
                                </label>
                              </div>
                              <div className="pattern-details">
                                <span className="confidence">
                                  {pattern.confidence ? `${Math.round(pattern.confidence)}%` : 'N/A'}
                                </span>
                                {pattern.entry_guidance && (
                                  <Tooltip content={pattern.entry_guidance}>
                                    <span className="guidance-label">Entry</span>
                                  </Tooltip>
                                )}
                                {pattern.risk_notes && (
                                  <Tooltip content={pattern.risk_notes}>
                                    <span className="risk-icon">⚠️</span>
                                  </Tooltip>
                                )}
                              </div>
                              {!isVisible && !isHovered && (
                                <div style={{ fontSize: '10px', color: '#999', marginTop: '4px', fontStyle: 'italic' }}>
                                  Hover to preview · Click to pin
                                </div>
                              )}
                            </div>
                          );
                        };
                        
                        return (
                          <div className="pattern-list">
                            {/* Reversal Patterns */}
                            {reversalPatterns.length > 0 && (
                              <div style={{ marginBottom: '16px' }}>
                                <div style={{ 
                                  fontSize: '12px', 
                                  fontWeight: '700', 
                                  color: '#ef4444',
                                  marginBottom: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px'
                                }}>
                                  🔄 REVERSAL ({reversalPatterns.length})
                                </div>
                                {reversalPatterns.filter(p => visiblePatterns.includes(p)).map(renderPattern)}
                              </div>
                            )}
                            
                            {/* Continuation Patterns */}
                            {continuationPatterns.length > 0 && (
                              <div style={{ marginBottom: '16px' }}>
                                <div style={{ 
                                  fontSize: '12px', 
                                  fontWeight: '700', 
                                  color: '#10b981',
                                  marginBottom: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px'
                                }}>
                                  ➡️ CONTINUATION ({continuationPatterns.length})
                                </div>
                                {continuationPatterns.filter(p => visiblePatterns.includes(p)).map(renderPattern)}
                              </div>
                            )}
                            
                            {/* Neutral Patterns */}
                            {neutralPatterns.length > 0 && (
                              <div style={{ marginBottom: '16px' }}>
                                <div style={{ 
                                  fontSize: '12px', 
                                  fontWeight: '700', 
                                  color: '#6b7280',
                                  marginBottom: '8px',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px'
                                }}>
                                  ⚪ NEUTRAL ({neutralPatterns.length})
                                </div>
                                {neutralPatterns.filter(p => visiblePatterns.includes(p)).map(renderPattern)}
                              </div>
                            )}
                            
                            {/* Show More / Show Less Button */}
                            {totalPatterns > INITIAL_VISIBLE && (
                              <button
                                onClick={() => setShowMorePatterns(!showMorePatterns)}
                                style={{
                                  width: '100%',
                                  padding: '8px',
                                  marginTop: '8px',
                                  background: 'rgba(59, 130, 246, 0.1)',
                                  color: '#3b82f6',
                                  border: '1px solid rgba(59, 130, 246, 0.3)',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontWeight: '600',
                                  fontSize: '12px',
                                  transition: 'all 0.2s'
                                }}
                                onMouseEnter={(e) => {
                                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                                  e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                                }}
                                onMouseLeave={(e) => {
                                  e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)';
                                  e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                                }}
                              >
                                {showMorePatterns ? 'Show Less' : `Show ${totalPatterns - INITIAL_VISIBLE} More Patterns`}
                              </button>
                            )}
                          </div>
                        );
                      })()}
                    </>
                  )}
                </div>

              {/* Right Column: News Feed */}
              <div className="news-section">
                <h4>📰 NEWS FEED - {selectedSymbol}</h4>
                {isLoadingNews ? (
                  <div className="loading-spinner-small">Loading news...</div>
                ) : newsError ? (
                  <div className="news-error">{newsError}</div>
                ) : (isStreaming ? streamingNews : stockNews).length > 0 ? (
                  <div className="news-list">
                    {(isStreaming ? streamingNews : stockNews).map((news, index) => (
                      <div key={index} className="news-item">
                        <a
                          href={news.url || '#'}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="news-link"
                        >
                          <div className="news-title">{news.title}</div>
                          <div className="news-time">
                            {formatNewsTime(news.published || news.time || news.published_at || Date.now() / 1000)}
                          </div>
                        </a>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="no-news">No news available</div>
                )}
              </div>
            </div>
          </div>
        </aside>

          {/* Mobile: Voice/Chat Section (below chart on mobile only) */}
          {isMobile && activePanel === 'chart' && (
            <>
              {/* Mobile Divider for Chart/Chat Split */}
              <div 
                className="mobile-divider"
                onTouchStart={(e) => {
                  e.preventDefault();
                  const startY = e.touches[0].clientY;
                  handleMobileDividerDrag(startY);
                }}
                onMouseDown={(e) => {
                  e.preventDefault();
                  const startY = e.clientY;
                  handleMobileDividerDrag(startY);
                }}
                style={{
                  height: '12px',
                  background: 'linear-gradient(to bottom, #e5e7eb 0%, #d1d5db 50%, #e5e7eb 100%)',
                  cursor: 'ns-resize',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                  touchAction: 'none',
                  userSelect: 'none',
                  WebkitUserSelect: 'none',
                  position: 'relative',
                  zIndex: 10
                }}
              >
                <div style={{
                  width: '40px',
                  height: '4px',
                  background: '#9ca3af',
                  borderRadius: '2px'
                }} />
              </div>
              
              <div 
                className="mobile-chat-section"
                style={{ flex: `1 1 ${100 - mobileChartRatio}%`, maxHeight: `${100 - mobileChartRatio}%`, minHeight: '200px' }}
              >
              {voiceProvider === 'chatkit' ? (
                <div className="h-full w-full">
                  <RealtimeChatKit
                    symbol={selectedSymbol}
                    timeframe={selectedTimeframe}
                    snapshotId={currentSnapshot?.symbol === selectedSymbol ? currentSnapshot?.metadata?.snapshot_id : undefined}
                    onMessage={(message) => {
                      console.log('ChatKit message:', message);
                      const newMessage: Message = {
                        ...message,
                        provider: 'chatkit'
                      };
                      setMessages((prev: Message[]) => [...prev, newMessage]);
                    }}
                    onChartCommand={(command: ChartCommandPayload) => {
                      console.log('ChatKit chart command:', command);
                      const normalized = normalizeChartCommandPayload(command);
                      const legacyCommands = normalized.legacy ?? [];
                      const structuredCommands = (normalized.structured ?? []).map(item => ({
                        type: item.type,
                        payload: { ...(item.payload ?? {}) },
                        description: item.description ?? null,
                        legacy: item.legacy ?? null,
                      })) as ChartControlStructuredCommand[];

                      if (legacyCommands.length === 0 && structuredCommands.length === 0) {
                        return;
                      }

                      enhancedChartControl
                        .processEnhancedResponse(normalized.responseText ?? '', legacyCommands, structuredCommands)
                        .catch(err => {
                          console.error('Failed to execute ChatKit chart command:', err);
                        });
                    }}
                  />
                </div>
              ) : (
                <div className="voice-conversation-section" style={{ height: '100%' }}>
                  <h2 className="panel-title">VOICE ASSISTANT</h2>
                  <div className="conversation-messages-compact">
                    {unifiedMessages.length === 0 ? (
                      <div className="no-messages-state">
                        <p>{isConversationConnected ? 'Listening...' : 'Click mic to start'}</p>
                      </div>
                    ) : (
                      unifiedMessages.map((msg) => (
                        <div key={msg.id} className="conversation-message-enhanced" data-role={msg.role}>
                          <div className="message-avatar">
                            {msg.role === 'user' ? '' : ''}
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
              </div>
            </>
          )}
        </main>

        {/* Right Panel Divider - Desktop only */}
        {!isMobile && <PanelDivider onDrag={handleRightPanelResize} />}

        {/* Right Panel - Voice Assistant Only */}
        <aside
          className="voice-panel-right chatkit-container panel"
          style={{ width: isMobile ? '100%' : `${rightPanelWidth}px` }}
          data-panel="voice"
          data-active={!isMobile || activePanel === 'voice'}
        >
          {voiceProvider === 'chatkit' ? (
            // Render RealtimeChatKit when using ChatKit provider - no wrapper needed
            <div className="h-full w-full">
              <RealtimeChatKit
                symbol={selectedSymbol}
                timeframe={selectedTimeframe}
                snapshotId={currentSnapshot?.symbol === selectedSymbol ? currentSnapshot?.metadata?.snapshot_id : undefined}
                onMessage={(message) => {
                  console.log('ChatKit message:', message);
                  const newMessage: Message = {
                    ...message,
                    provider: 'chatkit'
                  };
                  setMessages((prev: Message[]) => [...prev, newMessage]);
                }}
                onChartCommand={(command: ChartCommandPayload) => {
                  console.log('ChatKit chart command:', command);
                  const normalized = normalizeChartCommandPayload(command);
                  const legacyCommands = normalized.legacy ?? [];
                  const structuredCommands = (normalized.structured ?? []).map(item => ({
                    type: item.type,
                    payload: { ...(item.payload ?? {}) },
                    description: item.description ?? null,
                    legacy: item.legacy ?? null,
                  })) as ChartControlStructuredCommand[];

                  if (legacyCommands.length === 0 && structuredCommands.length === 0) {
                    return;
                  }

                  enhancedChartControl
                    .processEnhancedResponse(normalized.responseText ?? '', legacyCommands, structuredCommands)
                    .catch(err => {
                      console.error('Failed to execute ChatKit chart command:', err);
                    });
                }}
                onWidgetAction={handleAction}
              />
            </div>
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

      
      {/* Voice FAB - Hidden on mobile chart+voice tab (chat already visible), shown on desktop */}
        <button
          className={`voice-fab ${isConversationConnected ? 'active' : ''} ${isConversationConnecting ? 'connecting' : ''} ${isMobile ? 'mobile-position' : ''}`}
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
          style={(isMobile && activePanel === 'chart') ? { display: 'none' } : undefined}
        >
          {isConversationConnecting ? '⌛' : isConversationConnected ? '🎤' : '🎙️'}
        </button>

      
      {/* Voice Command Helper - Shows command history and suggestions */}
      <VoiceCommandHelper
        isVisible={isConversationConnected}
        position="right"
        maxHeight={400}
      />
      {/* Onboarding Tour - First-time user walkthrough */}
      {showOnboarding && (
        <OnboardingTour onComplete={() => setShowOnboarding(false)} />
      )}
      
      {/* Mobile Tab Bar - Fixed at bottom (2 tabs: Analysis | Chart+Voice) */}
        {isMobile && (
          <nav ref={tabBarRef} className="mobile-tab-bar" aria-label="Dashboard navigation">
            <ul className="mobile-tab-bar__list mobile-tab-bar__list--two-tabs">
              <li>
                <button
                  type="button"
                  className={`mobile-tab-bar__button ${activePanel === 'analysis' ? 'mobile-tab-bar__button--active' : ''}`}
                  aria-pressed={activePanel === 'analysis'}
                  aria-label="Analysis"
                  onClick={() => setActivePanel('analysis')}
                >
                  <span>📊 Analysis</span>
                  {stockNews.length > 0 && (
                    <span className="mobile-tab-bar__badge">{stockNews.length > 9 ? '9+' : stockNews.length}</span>
                  )}
                </button>
              </li>
              <li>
                <button
                  type="button"
                  className={`mobile-tab-bar__button ${activePanel === 'chart' ? 'mobile-tab-bar__button--active' : ''}`}
                  aria-pressed={activePanel === 'chart'}
                  aria-label="Chart + Voice"
                  onClick={() => setActivePanel('chart')}
                >
                  <span>📈 Chart + Voice</span>
                  {unifiedMessages.length > 0 && (
                    <span className="mobile-tab-bar__badge">{unifiedMessages.length > 9 ? '9+' : unifiedMessages.length}</span>
                  )}
                </button>
              </li>
            </ul>
          </nav>
        )}


      {/* Widget Modal Renders */}
      {activeWidget === 'economic-calendar' && (
        <EconomicCalendarWidget
          onClose={() => setActiveWidget(null)}
          onAction={handleAction}
        />
      )}
      {activeWidget === 'market-news' && (
        <MarketNewsFeedWidget
          symbol={selectedSymbol}
          onClose={() => setActiveWidget(null)}
          onAction={handleAction}
        />
      )}
      {activeWidget === 'technical-levels' && (
        <TechnicalLevelsWidget
          symbol={selectedSymbol}
          onClose={() => setActiveWidget(null)}
          onAction={handleAction}
        />
      )}
      {activeWidget === 'pattern-detection' && (
        <PatternDetectionWidget
          symbol={selectedSymbol}
          onClose={() => setActiveWidget(null)}
          onAction={handleAction}
        />
      )}
      {activeWidget === 'trading-chart' && (
        <TradingChartDisplayWidget
          symbol={selectedSymbol}
          currentPrice={stocksData.find(s => s.symbol === selectedSymbol)?.price}
          priceChange={stocksData.find(s => s.symbol === selectedSymbol)?.change}
          percentChange={stocksData.find(s => s.symbol === selectedSymbol)?.changePercent}
          onClose={() => setActiveWidget(null)}
          onAction={handleAction}
        />
      )}
      </div>
    );
  };
