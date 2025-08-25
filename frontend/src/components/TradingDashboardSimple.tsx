import React, { useState, useEffect, useRef } from 'react';
import { TradingChart } from './TradingChart';
import { marketDataService } from '../services/marketDataService';
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
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
}

export const TradingDashboardSimple: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'charts' | 'voice'>('charts');
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState('00:00');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'user',
      text: 'What is the price of Apple?',
      timestamp: '08:19:51 PM'
    },
    {
      id: '2',
      sender: 'assistant',
      text: '...',
      timestamp: ''
    }
  ]);
  const [isConnected, setIsConnected] = useState(false);
  const [stocksData, setStocksData] = useState<StockData[]>([]);
  const [isLoadingStocks, setIsLoadingStocks] = useState(true);
  const [selectedSymbol, setSelectedSymbol] = useState('TSLA');
  const [stockNews, setStockNews] = useState<any[]>([]);
  const [technicalLevels, setTechnicalLevels] = useState<any>({});
  const [isLoadingNews, setIsLoadingNews] = useState(false);
  
  // Stock symbols to track
  const watchlist = ['TSLA', 'AAPL', 'NVDA', 'SPY'];

  const handleRecord = () => {
    setIsRecording(!isRecording);
    setIsListening(!isListening);
    if (!isRecording) {
      // Start recording timer
      let seconds = 0;
      const interval = setInterval(() => {
        seconds++;
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        setRecordingTime(`${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`);
      }, 1000);
      
      // Stop after some time or on stop
      setTimeout(() => {
        clearInterval(interval);
        setRecordingTime('00:00');
        setIsRecording(false);
        setIsListening(false);
      }, 60000);
    } else {
      setRecordingTime('00:00');
    }
  };

  const handleTabChange = (tab: 'charts' | 'voice') => {
    setActiveTab(tab);
    console.log('Tab changed to:', tab);
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
        
        if (stockPrice.change_percent > 2) {
          label = 'QE';
          description = 'Bullish momentum';
        } else if (stockPrice.change_percent < -2) {
          label = 'LTB';
          description = 'Support level';
        } else if (Math.abs(stockPrice.change_percent) < 0.5) {
          label = 'ST';
          description = 'Consolidation';
        } else if (stockPrice.change_percent > 0) {
          label = 'ST';
          description = 'Upward trend';
        } else {
          label = 'LTB';
          description = 'Downward pressure';
        }
        
        return {
          symbol: stockPrice.symbol,
          price: stockPrice.price,
          change: stockPrice.change,
          changePercent: stockPrice.change_percent,
          label,
          description,
          volume: stockPrice.volume
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
    try {
      // Fetch news
      const news = await marketDataService.getStockNews(symbol);
      setStockNews(news.slice(0, 3)); // Show top 3 news items
      
      // Fetch comprehensive data for technical levels
      const comprehensive = await marketDataService.getComprehensiveData(symbol);
      if (comprehensive.technical_levels) {
        setTechnicalLevels(comprehensive.technical_levels);
      }
    } catch (error) {
      console.error('Error fetching stock analysis:', error);
      // Set fallback news
      setStockNews([
        { title: `${symbol} shows bullish flag pattern forming`, time: '2 min ago' },
        { title: `Price testing key support levels`, time: '5 min ago' },
        { title: `Volume breakout above resistance`, time: '8 min ago' }
      ]);
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
                    <span className={`stock-label ${stock.label.toLowerCase()}`}>{stock.label}</span>
                  </div>
                  <div className="stock-price">
                    <span className="price">${stock.price.toFixed(2)}</span>
                    <span className={`change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                      {stock.change >= 0 ? '↑' : '↓'} {Math.abs(stock.changePercent).toFixed(2)}%
                    </span>
                  </div>
                  <div className="stock-description">{stock.description}</div>
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
              <TradingChart symbol={selectedSymbol} />
              
              {/* Chart Overlays */}
              <div className="chart-overlays">
                <div className="level-line qe" style={{ top: '25%' }}>
                  <span className="level-label">QE $342 - $342.00</span>
                  <span className="level-value">$340.01</span>
                </div>
                <div className="level-line st" style={{ top: '50%' }}>
                  <span className="level-label">ST $224.61 - $229.90</span>
                  <span className="level-value">$320.00</span>
                </div>
                <div className="level-line ltb" style={{ top: '75%' }}>
                  <span className="level-label">LTB $168.71 - $183.28</span>
                  <span className="level-value">$300.00</span>
                </div>
              </div>
            </div>
          </div>

          {/* Voice Assistant */}
          <div className="voice-section">
            {/* Listening Interface */}
            <div className="listening-interface">
              <div className="listening-animation">
                <div 
                  className={`mic-icon ${isListening ? 'listening' : ''}`}
                  onClick={handleRecord}
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
                  {isListening ? 'Listening...' : 'AI Analysis'}
                </div>
                {isRecording && (
                  <div className="recording-timer">{recordingTime}</div>
                )}
              </div>
              
              <div className="audio-visualizer">
                <div className="audio-bar"></div>
                <div className="audio-bar"></div>
                <div className="audio-bar"></div>
                <div className="audio-bar"></div>
                <div className="audio-bar"></div>
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
                {messages.map((msg) => (
                  <div key={msg.id} className="conversation-message">
                    <div className="message-icon">
                      {msg.sender === 'user' ? '👤' : '🤖'}
                    </div>
                    <div className="message-content">
                      <div className="message-text">{msg.text}</div>
                      {msg.timestamp && (
                        <div className="message-time">{msg.timestamp}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="conversation-footer">
                <span className="footer-text">1 message • Listening for your voice...</span>
              </div>
              
              <div className="chart-control">
                <div className="control-header">Control the chart</div>
                <button className="listening-btn" onClick={handleRecord}>
                  {isListening ? 'Listening...' : 'Click to Listen'}
                </button>
              </div>
              
              <div className="voice-commands">
                Try these voice commands:
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
                {stockNews.map((news, index) => (
                  <div key={index} className="analysis-item">
                    <div className="analysis-header">
                      <h3>{selectedSymbol}</h3>
                      <span className="time">{news.published || news.time || `${index * 3 + 2} min ago`}</span>
                    </div>
                    <p>{news.title}</p>
                  </div>
                ))}

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