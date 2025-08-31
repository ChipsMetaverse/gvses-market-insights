import { useEffect, useRef, useState } from 'react'
import { createChart, ColorType, CandlestickSeries, Time } from 'lightweight-charts'
import { marketDataService } from '../services/marketDataService'

interface TradingChartProps {
  symbol: string
  technicalLevels?: any
  onChartReady?: (chart: any) => void
}

export function TradingChart({ symbol, technicalLevels, onChartReady }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)
  const candlestickSeriesRef = useRef<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [levelPositions, setLevelPositions] = useState<{ qe?: number; st?: number; ltb?: number }>({})

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
        time: (candle.time || candle.date) as Time, // API returns 'time' field with Unix timestamp
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close
      })).sort((a, b) => (a.time as number) - (b.time as number))
      
      // Technical levels now come from parent component props
      
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
        
        // Add technical levels as price lines (with price values on right)
        if (technicalLevels.qe_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.qe_level,
            color: '#10b981',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,  // Show price value on right
            title: '',  // No text label, just the price
          })
        }
        
        if (technicalLevels.st_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.st_level,
            color: '#eab308',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,  // Show price value on right
            title: '',  // No text label, just the price
          })
        }
        
        if (technicalLevels.ltb_level) {
          candlestickSeries.createPriceLine({
            price: technicalLevels.ltb_level,
            color: '#3b82f6',
            lineWidth: 2,
            lineStyle: 2,
            axisLabelVisible: true,  // Show price value on right
            title: '',  // No text label, just the price
          })
        }
        
        // Subscribe to chart updates for label position synchronization
        const updateLabelPositions = () => {
          if (chartRef.current && candlestickSeriesRef.current) {
            const positions: any = {}
            if (technicalLevels.qe_level) {
              const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.qe_level)
              if (coord !== null) positions.qe = coord
            }
            if (technicalLevels.st_level) {
              const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.st_level)
              if (coord !== null) positions.st = coord
            }
            if (technicalLevels.ltb_level) {
              const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.ltb_level)
              if (coord !== null) positions.ltb = coord
            }
            setLevelPositions(positions)
          }
        }

        // Initial update
        setTimeout(updateLabelPositions, 100)
        
        // Subscribe to visible range changes for continuous updates
        const timeScale = chart.timeScale()
        timeScale.subscribeVisibleLogicalRangeChange(updateLabelPositions)
        
        // Also subscribe to crosshair for real-time updates during interactions
        chart.subscribeCrosshairMove(updateLabelPositions)
        
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
  }, [symbol, technicalLevels, onChartReady])

  // Update positions when window resizes
  useEffect(() => {
    if (!chartRef.current || !candlestickSeriesRef.current || !technicalLevels) return
    
    const updatePositions = () => {
      const positions: any = {}
      if (technicalLevels.qe_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.qe_level)
        if (coord !== null) positions.qe = coord
      }
      if (technicalLevels.st_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.st_level)
        if (coord !== null) positions.st = coord
      }
      if (technicalLevels.ltb_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.ltb_level)
        if (coord !== null) positions.ltb = coord
      }
      setLevelPositions(positions)
    }
    
    // Listen for window resize
    window.addEventListener('resize', updatePositions)
    
    // Initial update
    const timeoutId = setTimeout(updatePositions, 200)
    
    return () => {
      clearTimeout(timeoutId)
      window.removeEventListener('resize', updatePositions)
    }
  }, [technicalLevels])

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
      
      {/* Custom left-side labels */}
      {!isLoading && !error && (
        <>
          {levelPositions.qe !== undefined && technicalLevels?.qe_level && (
            <div
              style={{
                position: 'absolute',
                left: '0px',
                top: `${levelPositions.qe}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                color: '#10b981',  // Green text
                padding: '2px 6px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '600',
                zIndex: 5,
                whiteSpace: 'nowrap',
                border: '1px solid #10b981',
              }}
            >
              QE Level
            </div>
          )}
          {levelPositions.st !== undefined && technicalLevels?.st_level && (
            <div
              style={{
                position: 'absolute',
                left: '0px',
                top: `${levelPositions.st}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                color: '#eab308',  // Yellow text
                padding: '2px 6px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '600',
                zIndex: 5,
                whiteSpace: 'nowrap',
                border: '1px solid #eab308',
              }}
            >
              ST Level
            </div>
          )}
          {levelPositions.ltb !== undefined && technicalLevels?.ltb_level && (
            <div
              style={{
                position: 'absolute',
                left: '0px',
                top: `${levelPositions.ltb}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.9)',
                color: '#3b82f6',  // Blue text
                padding: '2px 6px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '600',
                zIndex: 5,
                whiteSpace: 'nowrap',
                border: '1px solid #3b82f6',
              }}
            >
              LTB Level
            </div>
          )}
        </>
      )}
    </div>
  )
}