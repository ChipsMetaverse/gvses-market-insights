import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff } from 'lucide-react';
import { TradingChart } from './TradingChart';
import { TimeRangeSelector } from './TimeRangeSelector';
import { marketDataService } from '../services/marketDataService';
import { useAgentVoiceConversation } from '../hooks/useAgentVoiceConversation';
import { chartControlService } from '../services/chartControlService';
import { enhancedChartControl } from '../services/enhancedChartControl';
import { useIndicatorContext } from '../contexts/IndicatorContext';
import { TimeRange } from '../types/dashboard';
import './SimpleVoiceTrader.css';

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
  data?: Record<string, any>;
}

export function SimpleVoiceTrader() {
  // Core state
  const [currentSymbol, setCurrentSymbol] = useState('TSLA');
  const [timeRange, setTimeRange] = useState<TimeRange>('1D');
  const [stockData, setStockData] = useState<StockData[]>([]);
  const [aiResponse, setAiResponse] = useState<string>('');
  const [showResponse, setShowResponse] = useState(false);
  
  // Voice conversation integration
  const agentVoice = useAgentVoiceConversation({
    onMessage: (message) => {
      if (message.role === 'assistant') {
        setAiResponse(message.content);
        setShowResponse(true);
        // Auto-hide after 10 seconds
        setTimeout(() => setShowResponse(false), 10000);
      }
    },
    onError: (error) => {
      console.error('Voice error:', error);
    }
  });

  // Chart indicators context
  const { indicators } = useIndicatorContext();

  // Initialize stock data for ticker
  useEffect(() => {
    const loadStockData = async () => {
      try {
        const symbols = ['TSLA', 'AAPL', 'NVDA', 'SPY', 'PLTR'];
        const stockPromises = symbols.map(async (symbol) => {
          const data = await marketDataService.getStockPrice(symbol);
          return {
            symbol: data.symbol,
            price: data.price,
            change: data.change,
            changePercent: data.changePercent,
            label: symbol,
            description: data.companyName || symbol
          };
        });
        
        const stocks = await Promise.all(stockPromises);
        setStockData(stocks);
      } catch (error) {
        console.error('Failed to load stock data:', error);
      }
    };

    loadStockData();
    // Refresh every 30 seconds
    const interval = setInterval(loadStockData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Handle chart symbol changes from voice commands
  const handleChartCommand = useCallback(async (command: any) => {
    try {
      if (command.symbol && command.symbol !== currentSymbol) {
        setCurrentSymbol(command.symbol);
      }
      
      if (command.timeframe) {
        const timeRangeMap: { [key: string]: TimeRange } = {
          '1m': '1D', '5m': '1D', '15m': '1D', '1h': '1D', '4h': '1D',
          '1d': '1W', '1w': '1M', '1M': '3M'
        };
        setTimeRange(timeRangeMap[command.timeframe] || '1D');
      }
      
      // Process enhanced chart commands
      if (command.enhanced_response) {
        await enhancedChartControl.processEnhancedResponse(command.enhanced_response);
      }
    } catch (error) {
      console.error('Chart command error:', error);
    }
  }, [currentSymbol]);

  // Voice connection handlers
  const handleVoiceToggle = useCallback(async () => {
    if (agentVoice.isConnected) {
      agentVoice.disconnect();
    } else {
      await agentVoice.connect();
    }
  }, [agentVoice]);

  // Handle stock ticker clicks
  const handleStockClick = useCallback((symbol: string) => {
    setCurrentSymbol(symbol);
  }, []);

  return (
    <div className="simple-voice-trader">
      {/* Header with stock ticker and voice button */}
      <header className="trader-header">
        <div className="brand">
          <h1>GVSES</h1>
          <span className="subtitle">Voice Trader</span>
        </div>
        
        {/* Horizontal stock ticker */}
        <div className="stock-ticker">
          {stockData.map((stock) => (
            <button
              key={stock.symbol}
              className={`stock-item ${currentSymbol === stock.symbol ? 'active' : ''}`}
              onClick={() => handleStockClick(stock.symbol)}
            >
              <div className="stock-symbol">{stock.symbol}</div>
              <div className="stock-price">${stock.price.toFixed(2)}</div>
              <div className={`stock-change ${stock.change >= 0 ? 'positive' : 'negative'}`}>
                {stock.change >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
              </div>
            </button>
          ))}
        </div>

        {/* Single voice button */}
        <div className="voice-controls">
          <div className="connection-status">
            <div className={`status-dot ${agentVoice.isConnected ? 'connected' : 'disconnected'}`}></div>
            <span className="status-text">
              {agentVoice.isLoading ? 'Connecting...' : 
               agentVoice.isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          
          <button
            className={`voice-button ${agentVoice.isConnected ? 'connected' : ''} ${agentVoice.isRecording ? 'recording' : ''}`}
            onClick={handleVoiceToggle}
            disabled={agentVoice.isLoading}
            title={agentVoice.isConnected ? 'Click to disconnect voice' : 'Click to start voice trading'}
          >
            {agentVoice.isConnected ? <Mic size={24} /> : <MicOff size={24} />}
          </button>
        </div>
      </header>

      {/* Full-width chart area */}
      <main className="chart-container">
        <div className="chart-header">
          <h2 className="current-symbol">{currentSymbol}</h2>
          <TimeRangeSelector 
            selectedRange={timeRange}
            onRangeChange={setTimeRange}
          />
        </div>
        
        <div className="chart-wrapper">
          <TradingChart
            symbol={currentSymbol}
            timeRange={timeRange}
            indicators={indicators}
            onChartCommand={handleChartCommand}
          />
        </div>
      </main>

      {/* Slide-up AI response panel */}
      {showResponse && (
        <div className="ai-response-panel">
          <div className="response-header">
            <span>AI Analysis</span>
            <button 
              className="close-btn"
              onClick={() => setShowResponse(false)}
            >
              ×
            </button>
          </div>
          <div className="response-content">
            {aiResponse}
          </div>
        </div>
      )}
    </div>
  );
}