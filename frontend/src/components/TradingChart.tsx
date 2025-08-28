import { useEffect, useRef, useState } from 'react'
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts'
import { marketDataService } from '../services/marketDataService'

interface TradingChartProps {
  symbol: string
  onChartReady?: (chart: any) => void
}

export function TradingChart({ symbol, onChartReady }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const candlestickSeriesRef = useRef<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [technicalLevels, setTechnicalLevels] = useState<any>({})
  const [error, setError] = useState<string | null>(null)

  // Fetch real historical data
  const fetchChartData = async (symbol: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const history = await marketDataService.getStockHistory(symbol, 100)
      
      // Check if we have actual candle data
      if (!history.candles || history.candles.length === 0) {
        throw new Error(`No historical data available for ${symbol}`)
      }
      
      // Convert to lightweight-charts format (using Unix timestamps from API)
      const chartData = history.candles.map(candle => ({
        time: candle.time || candle.date, // API returns 'time' field with Unix timestamp
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close
      })).sort((a, b) => a.time - b.time)
      
      // Calculate technical levels from real data
      const levels = marketDataService.calculateTechnicalLevels(history.candles)
      setTechnicalLevels(levels)
      
      return chartData
    } catch (error: any) {
      console.error('Error fetching chart data:', error)
      // Set error message for display
      const errorMsg = error?.response?.data?.detail?.message || error?.message || 'Failed to load chart data'
      setError(errorMsg)
      return null
    } finally {
      setIsLoading(false)
    }
  }


  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'white' },
        textColor: '#333',
      },
      width: chartContainerRef.current.clientWidth,
      height: 300,
      grid: {
        vertLines: { color: '#f0f0f0' },
        horzLines: { color: '#f0f0f0' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#e0e0e0',
      },
      timeScale: {
        borderColor: '#e0e0e0',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      wickUpColor: '#22c55e',
    })

    chartRef.current = chart
    candlestickSeriesRef.current = candlestickSeries

    // Load real chart data
    const loadChartData = async () => {
      const chartData = await fetchChartData(symbol)
      
      if (chartData && chartData.length > 0) {
        candlestickSeries.setData(chartData)
        
        // Add technical levels as price lines using real calculated levels
        if (technicalLevels.qe_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.qe_level,
            color: '#10b981',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'QE Level',
          })
        }
        
        if (technicalLevels.st_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.st_level,
            color: '#eab308',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'ST Level',
          })
        }
        
        if (technicalLevels.ltb_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.ltb_level,
            color: '#3b82f6',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'LTB Level',
          })
        }
        
        chart.timeScale().fitContent()
      }
      // If chartData is null, error state is already set in fetchChartData
    }

    loadChartData()

    if (onChartReady) {
      onChartReady(chart)
    }

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chart) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [symbol, onChartReady])

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      {isLoading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 10,
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '10px 20px',
          borderRadius: '4px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          Loading chart data...
        </div>
      )}
      
      {error && !isLoading && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 10,
          background: 'rgba(255, 255, 255, 0.95)',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
          border: '2px solid #ef4444',
          maxWidth: '400px',
          textAlign: 'center' as const
        }}>
          <div style={{ color: '#ef4444', fontWeight: 'bold', marginBottom: '10px' }}>
            Chart Error
          </div>
          <div style={{ color: '#666', fontSize: '14px', lineHeight: '1.4' }}>
            {error}
          </div>
        </div>
      )}
      
      <div 
        ref={chartContainerRef} 
        className="w-full" 
        style={{ 
          opacity: (isLoading || error) ? 0.3 : 1,
          height: '100%'
        }} 
      />
    </div>
  )
}