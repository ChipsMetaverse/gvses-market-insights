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

  // Fetch real historical data
  const fetchChartData = async (symbol: string) => {
    setIsLoading(true)
    try {
      const history = await marketDataService.getStockHistory(symbol, 100)
      
      // Convert to lightweight-charts format
      const chartData = history.candles.map(candle => ({
        time: Date.parse(candle.date) / 1000,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close
      })).sort((a, b) => a.time - b.time)
      
      // Calculate technical levels from real data
      const levels = marketDataService.calculateTechnicalLevels(history.candles)
      setTechnicalLevels(levels)
      
      return chartData
    } catch (error) {
      console.error('Error fetching chart data:', error)
      // Fall back to sample data if API fails
      return generateSampleData()
    } finally {
      setIsLoading(false)
    }
  }

  // Fallback sample data generator
  const generateSampleData = () => {
    const data = []
    let basePrice = symbol === 'TSLA' ? 240 : symbol === 'AAPL' ? 185 : symbol === 'NVDA' ? 420 : 440

    for (let i = 0; i < 100; i++) {
      const time = Math.floor(Date.now() / 1000) - (100 - i) * 86400
      const volatility = 0.02
      const change = (Math.random() - 0.5) * volatility * basePrice

      const open = basePrice
      const close = basePrice + change
      const high = Math.max(open, close) + Math.random() * volatility * basePrice * 0.5
      const low = Math.min(open, close) - Math.random() * volatility * basePrice * 0.5

      data.push({
        time: time as any,
        open,
        high,
        low,
        close,
      })

      basePrice = close
    }

    return data
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
      <div ref={chartContainerRef} className="w-full" style={{ opacity: isLoading ? 0.5 : 1 }} />
    </div>
  )
}