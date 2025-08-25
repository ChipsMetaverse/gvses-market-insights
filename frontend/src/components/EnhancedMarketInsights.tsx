"use client"

import React, { useEffect, useState, useCallback } from 'react'
import { TrendingUp, TrendingDown, Loader2, RefreshCw, AlertCircle, Activity, Wifi, WifiOff } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { MarketSentimentIndicator } from '@/components/ui/market-sentiment-indicator'
import { DataSourceBadges } from '@/components/ui/data-source-badges'
import { hybridMarketDataService, HybridMarketData } from '@/services/hybridMarketDataService'
import { cn } from '@/lib/utils'

interface EnhancedMarketInsightsProps {
  symbols?: string[]
  currentSymbol: string
  onSymbolChange: (symbol: string) => void
  autoRefresh?: boolean
  refreshInterval?: number
  showSentiment?: boolean
  showDataSources?: boolean
  showStreamingStatus?: boolean
}

export function EnhancedMarketInsights({ 
  symbols = ['AAPL', 'TSLA', 'MSFT', 'GOOGL', 'AMZN'],
  currentSymbol, 
  onSymbolChange,
  autoRefresh = true,
  refreshInterval = 30000, // 30 seconds
  showSentiment = true,
  showDataSources = true,
  showStreamingStatus = true
}: EnhancedMarketInsightsProps) {
  const [marketData, setMarketData] = useState<Map<string, HybridMarketData>>(new Map())
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load market data for all symbols
  const loadMarketData = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true)
    } else {
      setLoading(true)
    }
    setError(null)

    try {
      const dataArray = await hybridMarketDataService.getMultipleHybridData(symbols)
      const newDataMap = new Map<string, HybridMarketData>()
      
      dataArray.forEach(data => {
        if (data) {
          newDataMap.set(data.symbol, data)
        }
      })
      
      setMarketData(newDataMap)
      
      // Subscribe to streaming updates
      hybridMarketDataService.subscribeToStreaming(symbols)
    } catch (err) {
      console.error('Error loading market data:', err)
      setError('Failed to load market data. Please check your API keys.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [symbols])

  // Initial load
  useEffect(() => {
    loadMarketData()
    
    // Cleanup on unmount
    return () => {
      hybridMarketDataService.unsubscribeFromStreaming(symbols)
    }
  }, [symbols, loadMarketData])

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      loadMarketData(true)
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, loadMarketData])

  // Listen for streaming updates
  useEffect(() => {
    const handleUpdate = (data: HybridMarketData) => {
      setMarketData(prev => {
        const newMap = new Map(prev)
        newMap.set(data.symbol, data)
        return newMap
      })
    }

    hybridMarketDataService.on('dataUpdated', handleUpdate)
    
    return () => {
      hybridMarketDataService.off('dataUpdated', handleUpdate)
    }
  }, [])

  const getSignalColor = (signal?: string) => {
    switch (signal) {
      case 'LTB': return 'bg-green-100 text-green-800 border-green-300'
      case 'ST': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'QE': return 'bg-orange-100 text-orange-800 border-orange-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(price)
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Market Insights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <AlertCircle className="w-8 h-8 text-red-500 mb-2" />
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              className="mt-4"
              onClick={() => loadMarketData()}
            >
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const marketDataArray = Array.from(marketData.values())

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Market Insights</CardTitle>
          <div className="flex items-center gap-2">
            {showStreamingStatus && (
              <div className="flex items-center gap-1">
                <Activity className={cn(
                  "w-4 h-4",
                  marketDataArray.some(d => d.isStreaming) ? "text-green-500 animate-pulse" : "text-gray-400"
                )} />
                <span className="text-xs text-gray-500">
                  {marketDataArray.some(d => d.isStreaming) ? 'Live' : 'Static'}
                </span>
              </div>
            )}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => loadMarketData(true)}
              disabled={refreshing}
            >
              <RefreshCw className={cn(
                "w-4 h-4",
                refreshing && "animate-spin"
              )} />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        {showSentiment && marketDataArray.length > 0 && (
          <div className="mb-4">
            <MarketSentimentIndicator
              sentiment={
                marketDataArray.filter(d => d.marketSentiment === 'bullish').length > 
                marketDataArray.filter(d => d.marketSentiment === 'bearish').length 
                  ? 'bullish' 
                  : marketDataArray.filter(d => d.marketSentiment === 'bearish').length > 
                    marketDataArray.filter(d => d.marketSentiment === 'bullish').length
                    ? 'bearish'
                    : 'neutral'
              }
              compact
              className="mb-3"
            />
          </div>
        )}
        
        <ScrollArea className="h-[400px] pr-4">
          <div className="space-y-3">
            {marketDataArray.map((stock) => (
              <div
                key={stock.symbol}
                className={cn(
                  "space-y-2 p-4 rounded-lg cursor-pointer transition-all",
                  "border hover:shadow-md",
                  currentSymbol === stock.symbol 
                    ? 'bg-blue-50 border-blue-300 shadow-sm' 
                    : 'bg-white hover:bg-gray-50 border-gray-200'
                )}
                onClick={() => onSymbolChange(stock.symbol)}
              >
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-lg">{stock.symbol}</span>
                    {stock.isStreaming && (
                      <Wifi className="w-3 h-3 text-green-500 animate-pulse" />
                    )}
                  </div>
                  <Badge 
                    variant="outline" 
                    className={cn("font-medium", getSignalColor(stock.signal))}
                  >
                    {stock.signal || 'N/A'}
                  </Badge>
                </div>
                
                {/* Price and Change */}
                <div className="flex items-center justify-between">
                  <span className="text-xl font-bold">
                    {formatPrice(stock.streamingPrice || stock.price)}
                  </span>
                  <div className={cn(
                    "text-sm font-medium flex items-center gap-1",
                    stock.changePercent >= 0 ? 'text-green-600' : 'text-red-600'
                  )}>
                    {stock.changePercent >= 0 ? (
                      <TrendingUp className="w-4 h-4" />
                    ) : (
                      <TrendingDown className="w-4 h-4" />
                    )}
                    <span>{Math.abs(stock.change).toFixed(2)}</span>
                    <span>({Math.abs(stock.changePercent || 0).toFixed(2)}%)</span>
                  </div>
                </div>
                
                {/* Analysis Summary */}
                {stock.newsAnalysis && (
                  <p className="text-sm text-muted-foreground line-clamp-2">
                    {stock.newsAnalysis}
                  </p>
                )}
                
                {/* Market Sentiment */}
                {stock.marketSentiment && (
                  <div className="flex items-center gap-2 pt-1">
                    <span className="text-xs text-muted-foreground">Sentiment:</span>
                    <Badge 
                      variant="secondary" 
                      className={cn(
                        "text-xs capitalize",
                        stock.marketSentiment === 'bullish' && "text-green-700 bg-green-100",
                        stock.marketSentiment === 'bearish' && "text-red-700 bg-red-100"
                      )}
                    >
                      {stock.marketSentiment}
                    </Badge>
                  </div>
                )}
                
                {/* Data Sources */}
                {showDataSources && stock.dataSource && (
                  <div className="pt-2 border-t">
                    <DataSourceBadges 
                      sources={stock.dataSource} 
                      size="sm"
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}