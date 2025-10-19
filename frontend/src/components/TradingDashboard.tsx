"use client"

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Mic, TrendingUp, TrendingDown, Volume2, Brain, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react'
import { TradingChart } from './TradingChart'
import { EnhancedMarketInsights } from './EnhancedMarketInsights'
import { ChartAnalysis } from './ChartAnalysis'
import { VoiceInterface } from './VoiceInterface'
import { getMultipleMarketData, getCachedMarketData } from '@/services/marketDataService.browser'
import { LiveStreamingBadge } from '@/components/ui/live-streaming-badge'
import { StreamingStatusIndicator } from '@/components/ui/streaming-status-indicator'
import type { IChartApi } from 'lightweight-charts'
import type { MarketData } from '../types'

export function TradingDashboard() {
  const [isListening, setIsListening] = useState(false)
  const [currentSymbol, setCurrentSymbol] = useState('TSLA')
  const [chartTimeframe, setChartTimeframe] = useState('1D')
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [loading, setLoading] = useState(true)
  const chartRef = useRef<IChartApi | null>(null)

  // Default symbols to track
  const defaultSymbols = ['TSLA', 'AAPL', 'NVDA', 'SPY'];

  // Fetch initial market data
  useEffect(() => {
    const fetchMarketData = async () => {
      setLoading(true);
      try {
        const dataObject = await getMultipleMarketData(defaultSymbols);
        // Convert object to array and filter out null values
        const dataArray = Object.entries(dataObject)
          .filter(([_, data]) => data !== null)
          .map(([_, data]) => data as MarketData);
        
        if (dataArray.length > 0) {
          setMarketData(dataArray);
        } else {
          // Use fallback if no data
          throw new Error('No market data available');
        }
      } catch (error) {
        console.error('Error fetching market data:', error);
        // Fallback to mock data if API fails
        setMarketData([
          { symbol: 'TSLA', price: 245.67, change: 5.29, signal: 'ST', analysis: 'Loading real data...' },
          { symbol: 'AAPL', price: 189.43, change: -1.12, signal: 'LTB', analysis: 'Loading real data...' },
          { symbol: 'NVDA', price: 421.88, change: 2.16, signal: 'QE', analysis: 'Loading real data...' },
          { symbol: 'SPY', price: 445.23, change: 0.78, signal: 'ST', analysis: 'Loading real data...' },
        ]);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchMarketData, 30000);
    
    return () => clearInterval(interval);
  }, []);

  // Update current symbol data when voice query is made
  const handleVoiceMarketData = async (symbol: string) => {
    try {
      const data = await getCachedMarketData(symbol);
      if (data) {
        // Update or add to market data
        setMarketData(prev => {
          const existing = prev.findIndex(m => m.symbol === symbol);
          if (existing >= 0) {
            const updated = [...prev];
            updated[existing] = data;
            return updated;
          } else {
            return [...prev, data];
          }
        });
        setCurrentSymbol(symbol);
      }
    } catch (error) {
      console.error('Error updating market data from voice:', error);
    }
  };

  const recentInsights = marketData.slice(0, 3).map((data, index) => ({
    symbol: data.symbol,
    insight: data.analysis || 'Analyzing...',
    time: `${(index + 1) * 3} min ago`
  }))

  const handleVoiceToggle = () => {
    setIsListening(!isListening)
  }

  const handleChartReady = (chart: IChartApi) => {
    chartRef.current = chart
  }

  const handleSymbolChange = (symbol: string) => {
    setCurrentSymbol(symbol)
  }

  const handleTimeframeChange = (timeframe: string) => {
    setChartTimeframe(timeframe)
  }

  const handleChartAction = (action: string) => {
    if (!chartRef.current) return

    switch (action) {
      case 'zoomIn':
        chartRef.current.timeScale().scrollToRealTime()
        break
      case 'zoomOut':
        chartRef.current.timeScale().fitContent()
        break
      case 'reset':
        chartRef.current.timeScale().resetTimeScale()
        break
    }
  }

  return (
    <div className="h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="border-b border-gray-100 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center">
              <Brain className="w-3 h-3 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-medium text-black">GVSES</h1>
              <p className="text-xs text-gray-500">AI Market Analysis Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-6">
            <LiveStreamingBadge />
            <div className="text-right">
              <p className="text-sm text-gray-600">Interactive Charts</p>
              <p className="text-xs text-green-600">Voice + Manual Control</p>
            </div>
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-5 gap-6 p-6 overflow-hidden">
        {/* Left Column - Market Insights */}
        <EnhancedMarketInsights
          marketData={marketData}
          currentSymbol={currentSymbol}
          onSymbolChange={handleSymbolChange}
          enableStreaming={true}
        />

        {/* Center Columns - Chart and Voice Interface */}
        <div className="col-span-3 space-y-6">
          {/* Chart Controls */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-lg font-medium text-black">{currentSymbol}</h2>
              <div className="flex items-center space-x-2">
                {['1H', '4H', '1D', '1W'].map((tf) => (
                  <Button
                    key={tf}
                    variant={chartTimeframe === tf ? 'default' : 'outline'}
                    size="sm"
                    className="h-7 px-3 text-xs"
                    onClick={() => handleTimeframeChange(tf)}
                  >
                    {tf}
                  </Button>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2 bg-transparent"
                onClick={() => handleChartAction('zoomIn')}
              >
                <ZoomIn className="w-3 h-3" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2 bg-transparent"
                onClick={() => handleChartAction('zoomOut')}
              >
                <ZoomOut className="w-3 h-3" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="h-7 px-2 bg-transparent"
                onClick={() => handleChartAction('reset')}
              >
                <RotateCcw className="w-3 h-3" />
              </Button>
            </div>
          </div>

          {/* Interactive Chart */}
          <div className="bg-white border border-gray-200 rounded-lg p-4">
            <TradingChart symbol={currentSymbol} onChartReady={handleChartReady} />
          </div>

          {/* Voice Interface */}
          <div className="bg-gray-50 rounded-lg p-6">
            <VoiceInterface
              isListening={isListening}
              currentSymbol={currentSymbol}
              onVoiceToggle={handleVoiceToggle}
            />
          </div>
        </div>

        {/* Right Column - Analysis */}
        <ChartAnalysis
          recentInsights={recentInsights}
          currentSymbol={currentSymbol}
        />
      </div>

      {/* Bottom Status Bar */}
      <div className="border-t border-gray-100 px-6 py-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-4">
            <span>Interactive Charts</span>
            <span>•</span>
            <span>Voice + Manual Control</span>
            <span>•</span>
            <span>Educational Analysis</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
            <span>Chart Ready</span>
          </div>
        </div>
      </div>
    </div>
  )
}