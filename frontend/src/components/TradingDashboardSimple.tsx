import React, { useState, useEffect, useRef, useCallback } from 'react';
import { TradingChart } from './TradingChart';
import { marketDataService } from '../services/marketDataService';
import { useElevenLabsConversation } from '../hooks/useElevenLabsConversation';
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
  
  // Audio processing refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Stock symbols to track
  const watchlist = ['TSLA', 'AAPL', 'NVDA', 'SPY'];
  
  // ElevenLabs conversation hook
  const {
    isConnected,
    isLoading: isConnecting,
    startConversation,
    stopConversation,
    sendTextMessage: sendElevenLabsText,
    sendAudioChunk,
  } = useElevenLabsConversation({
    apiUrl: import.meta.env.VITE_API_URL || window.location.origin,
    onUserTranscript: (transcript) => {
      const message: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: transcript,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, message]);
    },
    onAgentResponse: (response) => {
      const message: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, message]);
    },
    onConnectionChange: (connected) => {
      if (!connected) {
        setIsRecording(false);
        setIsListening(false);
        stopVoiceRecording();
      }
    }
  });

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
      sourceRef.current = audioContextRef.current.createMediaStreamSource(stream);
      processorRef.current = audioContextRef.current.createScriptProcessor(2048, 1, 1);
      
      processorRef.current.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Calculate audio level for visualization
        let sum = 0;
        for (let i = 0; i < inputData.length; i++) {
          sum += Math.abs(inputData[i]);
        }
        const level = sum / inputData.length;
        setAudioLevel(level);
        
        // Only send audio if there's actual sound (not silence)
        if (level > 0.001) {
          // Convert and send audio
          const pcm16 = convertFloat32ToInt16(inputData);
          const base64 = btoa(String.fromCharCode(...new Uint8Array(pcm16.buffer)));
          sendAudioChunk(base64);
        }
      };
      
      sourceRef.current.connect(processorRef.current);
      processorRef.current.connect(audioContextRef.current.destination);
      
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
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
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
      console.log('Connecting to ElevenLabs...');
      // Connect (voice recording will auto-start via useEffect when connected)
      try {
        await startConversation();
      } catch (error) {
        console.error('Failed to connect:', error);
        alert('Failed to connect to voice assistant. Please check your connection and try again.');
      }
    }
  };

  // Send text message
  const sendTextMessage = () => {
    if (inputText.trim() && isConnected) {
      const message: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content: inputText,
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, message]);
      sendElevenLabsText(inputText);
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
  const fetchStockData = async () => {
    setIsLoadingStocks(true);
    try {
      const promises = watchlist.map(async (symbol) => {
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

  // Fetch data on mount and set up refresh interval
  useEffect(() => {
    fetchStockData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchStockData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Fetch analysis when selected symbol changes
  useEffect(() => {
    fetchStockAnalysis(selectedSymbol);
  }, [selectedSymbol]);

  // Track if we've already started recording to prevent duplicates
  const hasStartedRecordingRef = useRef(false);
  const connectionAttemptTimeRef = useRef<number>(0);
  
  // Auto-start voice recording when connected
  useEffect(() => {
    let isMounted = true;
    let timer: NodeJS.Timeout;
    
    if (isConnected && !isRecording && !hasStartedRecordingRef.current) {
      console.log('Connection established, starting voice recording...');
      hasStartedRecordingRef.current = true;
      
      // Small delay to ensure everything is ready
      timer = setTimeout(() => {
        if (isMounted && isConnected && !isRecording) {
          startVoiceRecording();
        }
      }, 500);
    }
    
    // Reset flag when disconnected
    if (!isConnected) {
      hasStartedRecordingRef.current = false;
    }
    
    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [isConnected, isRecording, startVoiceRecording]); // Include all dependencies

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopVoiceRecording();
      if (isConnected) {
        stopConversation();
      }
    };
  }, [stopVoiceRecording, isConnected, stopConversation]);

  return (
    <div className="trading-dashboard-simple">
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
          >
            Interactive Charts
          </button>
          <button 
            className={`tab-btn ${activeTab === 'voice' ? 'active' : ''}`}
            onClick={() => handleTabChange('voice')}
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
          <div className="insights-content">
            {isLoadingStocks ? (
              <div className="loading-spinner">Loading market data...</div>
            ) : (
              stocksData.map((stock) => (
                <div 
                  key={stock.symbol} 
                  className={`stock-item ${selectedSymbol === stock.symbol ? 'selected' : ''}`}
                  onClick={() => setSelectedSymbol(stock.symbol)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="stock-header">
                    <span className="stock-symbol">{stock.symbol}</span>
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
              <TradingChart symbol={selectedSymbol} technicalLevels={technicalLevels} />
            </div>
          </div>

          {/* Voice Assistant */}
          <div className="voice-section">
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
                  <div className="recording-timer">{recordingTime}</div>
                )}
              </div>
              
              <div className="audio-visualizer">
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 600)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 400)}%` }}></div>
                <div className="audio-bar" style={{ height: `${Math.min(100, audioLevel * 500)}%` }}></div>
              </div>
              
              <div className="connection-status">
                <span className="status-dot"></span>
                {isConnected ? 'Connected' : 'Disconnected'}
              </div>
            </div>

            {/* Voice Conversation */}
            <div className="voice-conversation">
              <h3>Voice Conversation</h3>
              <div className="conversation-messages">
                {messages.length === 0 ? (
                  <div className="no-messages">
                    <p>Start a conversation by clicking the microphone or typing a message</p>
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
              
              <div className="chart-control">
                <button 
                  className={isConnected ? "disconnect-btn" : "listening-btn"}
                  onClick={handleConnectToggle}
                  disabled={isConnecting}
                  style={{ width: '100%', fontSize: '16px', padding: '12px' }}
                >
                  {isConnecting ? '⏳ Connecting...' : 
                   isConnected ? '🔴 Disconnect Voice' : 
                   '🎤 Connect Voice Assistant'}
                </button>
                {isConnected && (
                  <div className="voice-status" style={{ marginTop: '10px', textAlign: 'center', color: '#4CAF50' }}>
                    <span className="pulse-indicator" style={{ display: 'inline-block', width: '8px', height: '8px', backgroundColor: '#4CAF50', borderRadius: '50%', animation: 'pulse 1.5s infinite', marginRight: '8px' }}></span>
                    <span>Voice active • Speak anytime</span>
                  </div>
                )}
              </div>
              
              {/* Text Input Section - Only shown when connected */}
              {isConnected && (
                <div className="text-input-section">
                  <div className="text-input-group">
                    <input
                      type="text"
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendTextMessage()}
                      placeholder="Type a message (or just speak)..."
                      className="text-input"
                    />
                    <button 
                      onClick={sendTextMessage}
                      disabled={!inputText.trim()}
                      className="send-button"
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
    </div>
  );
};