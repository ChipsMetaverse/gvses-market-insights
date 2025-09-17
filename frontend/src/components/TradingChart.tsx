import { useEffect, useRef, useState, useCallback } from 'react'
import { createChart, ColorType, CandlestickSeries, Time, IChartApi, ISeriesApi } from 'lightweight-charts'
import { marketDataService } from '../services/marketDataService'
import { chartControlService } from '../services/chartControlService'

interface TradingChartProps {
  symbol: string
  technicalLevels?: any
  onChartReady?: (chart: any) => void
}

export function TradingChart({ symbol, technicalLevels, onChartReady }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [levelPositions, setLevelPositions] = useState<{ sell_high?: number; buy_low?: number; btd?: number }>({})
  const [isChartReady, setIsChartReady] = useState(false)
  
  // Lifecycle management refs
  const isMountedRef = useRef(true)
  const isChartDisposedRef = useRef(false)
  const abortControllerRef = useRef<AbortController | null>(null)
  const priceLineRefsRef = useRef<Array<any>>([])
  const currentSymbolRef = useRef(symbol)
  
  // Update label positions to sync with chart
  const updateLabelPositions = useCallback(() => {
    if (isChartDisposedRef.current || !chartRef.current || !candlestickSeriesRef.current) {
      return
    }
    
    try {
      const newPositions: any = {}
      
      // Use actual technical levels instead of deprecated QE/ST/LTB
      if (technicalLevels?.sell_high_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.sell_high_level)
        if (coord !== null && coord !== undefined && !isNaN(coord)) {
          newPositions.sell_high = coord
        }
      }
      if (technicalLevels?.buy_low_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.buy_low_level)
        if (coord !== null && coord !== undefined && !isNaN(coord)) {
          newPositions.buy_low = coord
        }
      }
      if (technicalLevels?.btd_level) {
        const coord = candlestickSeriesRef.current.priceToCoordinate(technicalLevels.btd_level)
        if (coord !== null && coord !== undefined && !isNaN(coord)) {
          newPositions.btd = coord
        }
      }
      
      if (isMountedRef.current) {
        setLevelPositions(newPositions)
      }
    } catch (error) {
      console.debug('Error updating label positions:', error)
    }
  }, [technicalLevels])
  
  // Create a ref to always have the latest updateLabelPositions function
  const updateLabelPositionsRef = useRef(updateLabelPositions)
  useEffect(() => {
    updateLabelPositionsRef.current = updateLabelPositions
  }, [updateLabelPositions])
  
  // Fetch chart data with proper cancellation
  const fetchChartData = useCallback(async (symbolToFetch: string) => {
    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    
    // Create new abort controller for this request
    abortControllerRef.current = new AbortController()
    
    setIsLoading(true)
    setError(null)
    
    try {
      const history = await marketDataService.getStockHistory(symbolToFetch, 100)
      
      // Check if component is still mounted and request wasn't aborted
      if (!isMountedRef.current || abortControllerRef.current.signal.aborted) {
        return null
      }
      
      // Check if we have actual candle data
      if (!history.candles || history.candles.length === 0) {
        throw new Error(`No historical data available for ${symbolToFetch}`)
      }
      
      // Convert to lightweight-charts format
      const chartData = history.candles.map(candle => ({
        time: (candle.time || candle.date) as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close
      })).sort((a, b) => (a.time as number) - (b.time as number))
      
      return chartData
    } catch (error: any) {
      if (error.name === 'AbortError' || !isMountedRef.current) {
        return null
      }
      
      console.error('Error fetching chart data:', error)
      const errorMsg = error?.response?.data?.detail?.message || error?.message || 'Failed to load chart data'
      
      if (isMountedRef.current) {
        setError(errorMsg)
      }
      return null
    } finally {
      if (isMountedRef.current) {
        setIsLoading(false)
      }
    }
  }, [])
  
  // Update only the chart data without recreating the chart
  const updateChartData = useCallback(async (symbolToUpdate: string) => {
    if (isChartDisposedRef.current || !candlestickSeriesRef.current) {
      return
    }
    
    const chartData = await fetchChartData(symbolToUpdate)
    
    if (chartData && chartData.length > 0 && !isChartDisposedRef.current && candlestickSeriesRef.current) {
      try {
        candlestickSeriesRef.current.setData(chartData)
        
        if (chartRef.current) {
          chartRef.current.timeScale().fitContent()
        }
      } catch (error) {
        console.debug('Error updating chart data:', error)
      }
    }
  }, [fetchChartData])
  
  // Update technical level lines without recreating the chart
  const updateTechnicalLevels = useCallback(() => {
    if (isChartDisposedRef.current || !candlestickSeriesRef.current) {
      return
    }
    
    try {
      // Remove old price lines
      priceLineRefsRef.current.forEach(priceLine => {
        try {
          candlestickSeriesRef.current?.removePriceLine(priceLine)
        } catch (e) {
          // Ignore errors when removing lines
        }
      })
      priceLineRefsRef.current = []
      
      // Add new price lines for actual technical levels
      if (technicalLevels?.sell_high_level) {
        const line = candlestickSeriesRef.current.createPriceLine({
          price: technicalLevels.sell_high_level,
          color: '#10b981',  // Green for sell high
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: '',
        })
        priceLineRefsRef.current.push(line)
      }
      
      if (technicalLevels?.buy_low_level) {
        const line = candlestickSeriesRef.current.createPriceLine({
          price: technicalLevels.buy_low_level,
          color: '#eab308',  // Yellow/amber for buy low
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: '',
        })
        priceLineRefsRef.current.push(line)
      }
      
      if (technicalLevels?.btd_level) {
        const line = candlestickSeriesRef.current.createPriceLine({
          price: technicalLevels.btd_level,
          color: '#3b82f6',  // Blue for BTD (Buy the Dip)
          lineWidth: 2,
          lineStyle: 2,
          axisLabelVisible: true,
          title: '',
        })
        priceLineRefsRef.current.push(line)
      }
      
      // Update label positions after adding lines
      setTimeout(() => updateLabelPositionsRef.current(), 100)
    } catch (error) {
      console.debug('Error updating technical levels:', error)
    }
  }, [technicalLevels])
  
  // Handle resize
  const handleResize = useCallback(() => {
    if (isChartDisposedRef.current || !chartRef.current || !chartContainerRef.current) {
      return
    }
    
    try {
      chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth })
      updateLabelPositionsRef.current()
    } catch (error) {
      console.debug('Error handling resize:', error)
    }
  }, [])
  
  // Create and initialize the chart (only once per symbol)
  useEffect(() => {
    if (!chartContainerRef.current) return
    
    // Mark as mounted
    isMountedRef.current = true
    isChartDisposedRef.current = false
    currentSymbolRef.current = symbol
    
    // Create the chart
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
    
    // Mark chart as ready for event subscriptions
    setIsChartReady(true)
    
    // Add resize listener
    window.addEventListener('resize', handleResize)
    
    // Load initial data
    updateChartData(symbol).then(() => {
      updateTechnicalLevels()
      setTimeout(() => updateLabelPositionsRef.current(), 200)
    })
    
    // Notify parent that chart is ready
    if (onChartReady && !isChartDisposedRef.current) {
      onChartReady(chart)
    }
    
    // Cleanup function
    return () => {
      isMountedRef.current = false
      isChartDisposedRef.current = true
      setIsChartReady(false)
      
      // Cancel any pending requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
      
      // Remove event listener
      window.removeEventListener('resize', handleResize)
      
      // Clear price lines
      priceLineRefsRef.current = []
      
      // Clear chart control service reference
      if (chartControlService) {
        chartControlService.setChartRef(null)
      }
      
      // Dispose the chart
      try {
        chart.remove()
      } catch (e) {
        // Ignore errors during disposal
      }
      
      chartRef.current = null
      candlestickSeriesRef.current = null
    }
  }, [symbol]) // Only recreate chart when symbol changes
  
  // Subscribe to chart events for label synchronization
  useEffect(() => {
    if (!isChartReady || !chartRef.current || isChartDisposedRef.current) {
      return
    }
    
    const chart = chartRef.current
    const timeScale = chart.timeScale()
    
    // Event handler that uses the ref to get the latest function
    const handleChartUpdate = () => {
      if (!isChartDisposedRef.current && isMountedRef.current) {
        updateLabelPositionsRef.current()
      }
    }
    
    // Subscribe to chart events
    timeScale.subscribeVisibleLogicalRangeChange(handleChartUpdate)
    chart.subscribeCrosshairMove(handleChartUpdate)
    timeScale.subscribeVisibleTimeRangeChange(handleChartUpdate)
    
    // Cleanup not needed since chart disposal handles event cleanup
  }, [isChartReady]) // Re-subscribe when chart is ready
  
  // Update data when symbol changes (without recreating chart)
  useEffect(() => {
    if (currentSymbolRef.current !== symbol && chartRef.current && !isChartDisposedRef.current) {
      currentSymbolRef.current = symbol
      updateChartData(symbol)
    }
  }, [symbol, updateChartData])
  
  // Update technical levels when they change (without recreating chart)
  useEffect(() => {
    if (chartRef.current && !isChartDisposedRef.current) {
      updateTechnicalLevels()
    }
  }, [technicalLevels, updateTechnicalLevels])
  
  // Update label positions when technical levels change
  useEffect(() => {
    if (chartRef.current && !isChartDisposedRef.current && technicalLevels) {
      // Multiple retries to ensure labels appear
      const timeouts: NodeJS.Timeout[] = []
      timeouts.push(setTimeout(() => updateLabelPositionsRef.current(), 100))
      timeouts.push(setTimeout(() => updateLabelPositionsRef.current(), 300))
      timeouts.push(setTimeout(() => updateLabelPositionsRef.current(), 600))
      
      return () => {
        timeouts.forEach(timeout => clearTimeout(timeout))
      }
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
          {levelPositions.sell_high !== undefined && technicalLevels?.sell_high_level && (
            <div
              style={{
                position: 'absolute',
                left: '2px',
                top: `${levelPositions.sell_high}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.75)',
                color: '#10b981',
                padding: '2px 8px',
                border: '1px solid #10b981',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '700',
                zIndex: 10,
                whiteSpace: 'nowrap',
              }}
            >
              Sell High
            </div>
          )}
          {levelPositions.buy_low !== undefined && technicalLevels?.buy_low_level && (
            <div
              style={{
                position: 'absolute',
                left: '2px',
                top: `${levelPositions.buy_low}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.75)',
                color: '#eab308',
                padding: '2px 8px',
                border: '1px solid #eab308',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '700',
                zIndex: 10,
                whiteSpace: 'nowrap',
              }}
            >
              Buy Low
            </div>
          )}
          {levelPositions.btd !== undefined && technicalLevels?.btd_level && (
            <div
              style={{
                position: 'absolute',
                left: '2px',
                top: `${levelPositions.btd}px`,
                transform: 'translateY(-50%)',
                backgroundColor: 'rgba(255, 255, 255, 0.75)',
                color: '#3b82f6',
                padding: '2px 8px',
                border: '1px solid #3b82f6',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '700',
                zIndex: 10,
                whiteSpace: 'nowrap',
              }}
            >
              BTD
            </div>
          )}
        </>
      )}
    </div>
  )
}