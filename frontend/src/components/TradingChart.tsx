import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import { createChart, ColorType, Time, IChartApi, ISeriesApi, CandlestickSeries } from 'lightweight-charts'
import { marketDataService } from '../services/marketDataService'
import { chartControlService } from '../services/chartControlService'
import { enhancedChartControl } from '../services/enhancedChartControl'
import { useIndicatorState } from '../hooks/useIndicatorState'
import { useIndicatorContext } from '../contexts/IndicatorContext'
import { useChartSeries } from '../hooks/useChartSeries'
import { ChartToolbar } from './ChartToolbar'
import { DrawingStore } from '../drawings/DrawingStore'
import { createDrawingOverlay } from '../drawings/DrawingOverlay'
import { createToolbox } from '../drawings/ToolboxManager'
import './TradingChart.css'

interface TradingChartProps {
  symbol: string
  days?: number  // Number of days of historical data to FETCH (for indicators)
  displayDays?: number  // Number of days to DISPLAY on chart
  interval?: string  // Data interval: '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
  technicalLevels?: any
  onChartReady?: (chart: any) => void
}

export function TradingChart({ symbol, days = 100, displayDays, interval = "1d", technicalLevels, onChartReady }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const oscillatorChartRef = useRef<IChartApi | null>(null)
  const oscillatorContainerRef = useRef<HTMLDivElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [levelPositions, setLevelPositions] = useState<{ sell_high?: number; buy_low?: number; btd?: number }>({})
  const [isChartReady, setIsChartReady] = useState(false)

  // Indicator state and series management
  const { state: indicatorState, actions: indicatorActions } = useIndicatorState()
  const { dispatch: indicatorDispatch } = useIndicatorContext()
  const mainChartSeries = useChartSeries(isChartReady ? chartRef.current : null)
  const oscillatorSeries = useChartSeries(isChartReady ? oscillatorChartRef.current : null)

  const [overlayVisibility, setOverlayVisibility] = useState({
    movingAverages: false,
    bollinger: false,
    rsi: false,
    macd: false,
  })

  const [patternHighlight, setPatternHighlight] = useState<{ title: string; description?: string } | null>(null)

  // Drawing toolbox state (singleton store, lives outside React lifecycle)
  const store = useMemo(() => new DrawingStore(), [])
  const toolboxRef = useRef<ReturnType<typeof createToolbox> | null>(null)
  const overlayRef = useRef<ReturnType<typeof createDrawingOverlay> | null>(null)

  const showOscillatorPane =
    (overlayVisibility.rsi && indicatorState.indicators.rsi.enabled) ||
    (overlayVisibility.macd && indicatorState.indicators.macd.enabled)

  const mapIndicatorToOverlayKey = useCallback((indicator: string) => {
    const name = indicator.toLowerCase();
    if (name.includes('bollinger')) return 'bollinger' as const;
    if (name.includes('macd')) return 'macd' as const;
    if (name.includes('rsi')) return 'rsi' as const;
    if (name.includes('ma') || name.includes('moving average')) return 'movingAverages' as const;
    if (['ma20', 'ma50', 'ma200'].includes(name)) return 'movingAverages' as const;
    return null;
  }, [])

  const setOverlayVisibilityForIndicator = useCallback((indicator: string, enabled: boolean) => {
    const key = mapIndicatorToOverlayKey(indicator)
    if (!key) return
    setOverlayVisibility(prev => (prev[key] === enabled ? prev : { ...prev, [key]: enabled }))
  }, [mapIndicatorToOverlayKey])

  const clearAllOverlays = useCallback(() => {
    setOverlayVisibility({ movingAverages: false, bollinger: false, rsi: false, macd: false })
    setPatternHighlight(null)
  }, [])

  useEffect(() => {
    enhancedChartControl.setOverlayControls({
      setOverlayVisibility: setOverlayVisibilityForIndicator,
      clearOverlays: clearAllOverlays,
      highlightPattern: (pattern: string, info?: { description?: string; indicator?: string; title?: string }) => {
        if (info?.indicator) {
          setOverlayVisibilityForIndicator(info.indicator, true)
        }
        setPatternHighlight({
          title: info?.title || pattern,
          description: info?.description,
        })
      },
    })
    return () => {
      enhancedChartControl.setOverlayControls({
        setOverlayVisibility: undefined,
        clearOverlays: undefined,
        highlightPattern: undefined,
      })
    }
  }, [setOverlayVisibilityForIndicator, clearAllOverlays])

  useEffect(() => {
    if (!patternHighlight) return
    const timer = setTimeout(() => setPatternHighlight(null), 6000)
    return () => clearTimeout(timer)
  }, [patternHighlight])

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
      const history = await marketDataService.getStockHistory(symbolToFetch, days, interval)

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

      // Add white space padding for linear scaling (from TradingView tutorial)
      // Calculate time interval between candles
      if (chartData.length > 1) {
        const timeInterval = (chartData[1].time as number) - (chartData[0].time as number)
        const whiteSpaceCount = 100

        // Create leading white spaces
        const leadingSpaces = Array(whiteSpaceCount).fill(null).map((_, i) => ({
          time: ((chartData[0].time as number) - (timeInterval * (whiteSpaceCount - i))) as Time,
          open: chartData[0].open,
          high: chartData[0].open,
          low: chartData[0].open,
          close: chartData[0].open
        }))

        // Create trailing white spaces
        const lastIndex = chartData.length - 1
        const trailingSpaces = Array(whiteSpaceCount).fill(null).map((_, i) => ({
          time: ((chartData[lastIndex].time as number) + (timeInterval * (i + 1))) as Time,
          open: chartData[lastIndex].close,
          high: chartData[lastIndex].close,
          low: chartData[lastIndex].close,
          close: chartData[lastIndex].close
        }))

        // Combine: leading spaces + actual data + trailing spaces
        const paddedData = [...leadingSpaces, ...chartData, ...trailingSpaces]
        return paddedData
      }

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
  }, [days])
  
  // Apply timeframe-based zoom after loading data
  const applyTimeframeZoom = useCallback((chartData: any[]) => {
    if (!chartRef.current || !chartData || chartData.length === 0) {
      return
    }

    const chart = chartRef.current
    const now = Math.floor(Date.now() / 1000)

    // Use displayDays if provided, otherwise fall back to days
    const daysToDisplay = displayDays !== undefined ? displayDays : days

    // Convert display days to seconds
    const timeframeInSeconds = (() => {
      if (daysToDisplay <= 0) return null // Show all data
      return daysToDisplay * 86400 // Convert days to seconds
    })()

    if (timeframeInSeconds) {
      // Filter to specific timeframe
      const fromTime = now - timeframeInSeconds
      const firstValidIndex = chartData.findIndex(d => d.time >= fromTime)
      
      if (firstValidIndex >= 0) {
        try {
          chart.timeScale().setVisibleLogicalRange({
            from: firstValidIndex,
            to: chartData.length - 1
          })
          console.log(`✅ Applied ${daysToDisplay}-day timeframe: showing ${chartData.length - firstValidIndex} of ${chartData.length} candles (fetched ${days} days for indicators)`)
        } catch (error) {
          console.warn('Failed to set visible range, falling back to fitContent:', error)
          chart.timeScale().fitContent()
        }
      } else {
        // If no data in range, show all
        console.log(`⚠️  No data in ${daysToDisplay}-day range, showing all available data`)
        chart.timeScale().fitContent()
      }
    } else {
      // For MAX/YTD or large ranges, show all data
      console.log(`📊 Showing all available data (${chartData.length} candles)`)
      chart.timeScale().fitContent()
    }
  }, [days, displayDays])

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
          // Apply smart timeframe-based zoom instead of fitContent()
          applyTimeframeZoom(chartData)
        }
      } catch (error) {
        console.debug('Error updating chart data:', error)
      }
    }
  }, [fetchChartData, applyTimeframeZoom])
  
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
          color: '#ef4444',  // Red for sell high
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
      
      // Add swing trade levels if available
      const swingLevels = technicalLevels as any // Type will be SwingTradeLevels
      
      // Entry points - green dashed lines
      if (swingLevels?.entry_points?.length) {
        swingLevels.entry_points.forEach((entry: number, index: number) => {
          const line = candlestickSeriesRef.current.createPriceLine({
            price: entry,
            color: '#22c55e',  // Bright green for entries
            lineWidth: 2,
            lineStyle: 1,  // Dashed
            axisLabelVisible: true,
            title: `Entry ${index + 1}`,
          })
          priceLineRefsRef.current.push(line)
        })
      }
      
      // Stop loss - red solid line
      if (swingLevels?.stop_loss) {
        const line = candlestickSeriesRef.current.createPriceLine({
          price: swingLevels.stop_loss,
          color: '#ef4444',  // Red for stop loss
          lineWidth: 2,
          lineStyle: 0,  // Solid
          axisLabelVisible: true,
          title: 'Stop',
        })
        priceLineRefsRef.current.push(line)
      }
      
      // Targets - purple dashed lines
      if (swingLevels?.targets?.length) {
        swingLevels.targets.forEach((target: number, index: number) => {
          const line = candlestickSeriesRef.current.createPriceLine({
            price: target,
            color: '#a855f7',  // Purple for targets
            lineWidth: 2,
            lineStyle: 1,  // Dashed
            axisLabelVisible: true,
            title: `T${index + 1}`,
          })
          priceLineRefsRef.current.push(line)
        })
      }
      
      // Helper function to deduplicate and cluster price levels
      const deduplicateAndLimitLevels = (levels: number[], maxCount: number = 5): number[] => {
        if (!levels?.length) return []

        // Sort levels
        const sorted = [...levels].sort((a, b) => a - b)

        // Deduplicate and cluster levels within 0.1% of each other
        const deduplicated: number[] = []
        let lastLevel: number | null = null

        for (const level of sorted) {
          if (lastLevel === null || Math.abs(level - lastLevel) / lastLevel > 0.001) {
            deduplicated.push(level)
            lastLevel = level
          }
        }

        // Limit to max count
        return deduplicated.slice(0, maxCount)
      }

      // Support levels - orange dotted lines
      if (swingLevels?.support_levels?.length) {
        const deduplicatedSupport = deduplicateAndLimitLevels(swingLevels.support_levels, 5)
        deduplicatedSupport.forEach((support: number, index: number) => {
          const line = candlestickSeriesRef.current.createPriceLine({
            price: support,
            color: '#fb923c',  // Orange for support
            lineWidth: 1,
            lineStyle: 3,  // Dotted
            axisLabelVisible: true,
            title: `S${index + 1}`,
          })
          priceLineRefsRef.current.push(line)
        })
      }

      // Resistance levels - cyan dotted lines
      if (swingLevels?.resistance_levels?.length) {
        const deduplicatedResistance = deduplicateAndLimitLevels(swingLevels.resistance_levels, 5)
        deduplicatedResistance.forEach((resistance: number, index: number) => {
          const line = candlestickSeriesRef.current.createPriceLine({
            price: resistance,
            color: '#06b6d4',  // Cyan for resistance
            lineWidth: 1,
            lineStyle: 3,  // Dotted
            axisLabelVisible: true,
            title: `R${index + 1}`,
          })
          priceLineRefsRef.current.push(line)
        })
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
        mode: 0, // Normal mode - free movement without snapping to data points
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
    
    // Store references
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

      // Capture chart snapshot 500ms after data loads for pattern detection
      setTimeout(async () => {
        try {
          const canvas = chartContainerRef.current?.querySelector('canvas')
          if (canvas) {
            const imageBase64 = canvas.toDataURL('image/png').split(',')[1]

            // Send to backend for potential pattern detection
            await fetch(`${import.meta.env.VITE_API_URL || window.location.origin}/api/agent/chart-snapshot`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                symbol,
                timeframe: '1D',
                image_base64: imageBase64,
                auto_analyze: true // Enable automatic pattern detection on chart load
              })
            })
            console.log(`Chart snapshot captured for ${symbol}`)
          }
        } catch (error) {
          console.warn('Failed to capture chart snapshot:', error)
        }
      }, 500)
    })

    // Connect enhanced chart control to indicator system
    enhancedChartControl.initialize(chart, candlestickSeries, indicatorDispatch)

    // Attach drawing store to enhanced chart control for programmatic API
    enhancedChartControl.attach(chart, candlestickSeries as any, store)

    // Initialize drawing overlay with callbacks
    overlayRef.current = createDrawingOverlay({
      chart,
      series: candlestickSeries,
      container: chartContainerRef.current,
      store,
      onUpdate: (d) => {
        console.log('Drawing updated:', d)
        // TODO: PATCH /api/drawings/:id
      },
      onDelete: (id) => {
        console.log('Drawing deleted:', id)
        // TODO: DELETE /api/drawings/:id
      },
    })

    // Initialize toolbox with callbacks
    toolboxRef.current = createToolbox({
      chart,
      series: candlestickSeries,
      container: chartContainerRef.current,
      store,
      onCreate: (d) => {
        console.log('Drawing created:', d)
        // TODO: POST /api/drawings
      },
      onUpdate: (d) => {
        console.log('Drawing updated (toolbox):', d)
        // TODO: PATCH /api/drawings/:id
      },
      onDelete: (id) => {
        console.log('Drawing deleted (toolbox):', id)
        // TODO: DELETE /api/drawings/:id
      },
    })

    // Expose to window for agent access
    ;(window as any).enhancedChartControl = enhancedChartControl
    ;(window as any).enhancedChartControlReady = true
    ;(window as any).chartRef = chart
    ;(window as any).candlestickSeriesRef = candlestickSeries
    
    // Notify parent that chart is ready
    if (onChartReady && !isChartDisposedRef.current) {
      onChartReady(chart)
    }
    
    // Cleanup function
    return () => {
      isMountedRef.current = false
      isChartDisposedRef.current = true
      setIsChartReady(false)
      
      // Clean up window references
      ;(window as any).enhancedChartControlReady = false
      
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

      clearAllOverlays()

      // Clean up drawing toolbox and overlay
      if (toolboxRef.current) {
        toolboxRef.current.destroy()
        toolboxRef.current = null
      }
      if (overlayRef.current) {
        overlayRef.current.destroy()
        overlayRef.current = null
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
  }, [symbol, days, interval]) // Recreate chart when symbol, days, or interval changes
  
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

  // Re-apply zoom when days/timeframe changes (without fetching new data)
  useEffect(() => {
    if (chartRef.current && candlestickSeriesRef.current && !isChartDisposedRef.current) {
      const currentData = (candlestickSeriesRef.current as any).data?.()
      if (currentData && currentData.length > 0) {
        const daysToDisplay = displayDays !== undefined ? displayDays : days
        console.log(`⏱️  Timeframe changed to ${daysToDisplay} days (fetching ${days} days), re-applying zoom...`)
        applyTimeframeZoom(currentData)
      }
    }
  }, [days, displayDays, applyTimeframeZoom])
  
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
  
  // Update indicators when data changes
  useEffect(() => {
    if (!chartRef.current || !indicatorState.data) return;
    
    const { indicators } = indicatorState.data;
    if (!indicators) return;
    
    // Update Moving Averages
    const { movingAverages } = indicatorState.indicators;
    const showMovingAverages = overlayVisibility.movingAverages && (
      movingAverages.ma20.enabled || movingAverages.ma50.enabled || movingAverages.ma200.enabled
    );

    if (showMovingAverages && indicators.movingAverages?.ma20) {
      mainChartSeries.addOrUpdateSeries('ma20', indicators.movingAverages.ma20, {
        type: 'line',
        color: movingAverages.ma20.color,
        lineWidth: movingAverages.ma20.lineWidth
      });
    } else {
      mainChartSeries.removeSeries('ma20');
    }
    
    if (showMovingAverages && indicators.movingAverages?.ma50) {
      mainChartSeries.addOrUpdateSeries('ma50', indicators.movingAverages.ma50, {
        type: 'line',
        color: movingAverages.ma50.color,
        lineWidth: movingAverages.ma50.lineWidth
      });
    } else {
      mainChartSeries.removeSeries('ma50');
    }
    
    if (showMovingAverages && indicators.movingAverages?.ma200) {
      mainChartSeries.addOrUpdateSeries('ma200', indicators.movingAverages.ma200, {
        type: 'line',
        color: movingAverages.ma200.color,
        lineWidth: movingAverages.ma200.lineWidth
      });
    } else {
      mainChartSeries.removeSeries('ma200');
    }
    
    // Update Bollinger Bands
    const showBollinger = overlayVisibility.bollinger && indicatorState.indicators.bollingerBands.enabled;
    if (showBollinger && indicators.bollingerBands) {
      mainChartSeries.addOrUpdateSeries('bb-upper', indicators.bollingerBands.upper, {
        type: 'line',
        color: indicatorState.indicators.bollingerBands.color,
        lineWidth: 1
      });
      mainChartSeries.addOrUpdateSeries('bb-middle', indicators.bollingerBands.middle, {
        type: 'line',
        color: indicatorState.indicators.bollingerBands.color,
        lineWidth: 1
      });
      mainChartSeries.addOrUpdateSeries('bb-lower', indicators.bollingerBands.lower, {
        type: 'line',
        color: indicatorState.indicators.bollingerBands.color,
        lineWidth: 1
      });
    } else {
      mainChartSeries.removeSeries('bb-upper');
      mainChartSeries.removeSeries('bb-middle');
      mainChartSeries.removeSeries('bb-lower');
    }
  }, [indicatorState.data, indicatorState.indicators, mainChartSeries, overlayVisibility]);
  
  // Create/destroy oscillator chart based on RSI/MACD
  useEffect(() => {
    const showRSI = overlayVisibility.rsi && indicatorState.indicators.rsi.enabled
    const showMACD = overlayVisibility.macd && indicatorState.indicators.macd.enabled
    const needsOscillator = showRSI || showMACD
    
    if (needsOscillator && !oscillatorChartRef.current && oscillatorContainerRef.current) {
      // Create oscillator chart
      const oscChart = createChart(oscillatorContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: 'white' },
          textColor: '#333',
        },
        width: oscillatorContainerRef.current.clientWidth,
        height: 150,
        grid: {
          vertLines: { color: '#f0f0f0' },
          horzLines: { color: '#f0f0f0' },
        },
        rightPriceScale: {
          borderColor: '#e0e0e0',
        },
        timeScale: {
          borderColor: '#e0e0e0',
          visible: false, // Hide time axis (synced with main chart)
        },
      });
      
      oscillatorChartRef.current = oscChart;
      
      // Sync time scale with main chart
      if (chartRef.current) {
        chartRef.current.timeScale().subscribeVisibleLogicalRangeChange((range) => {
          if (range && oscillatorChartRef.current) {
            oscillatorChartRef.current.timeScale().setVisibleLogicalRange(range);
          }
        });
      }
    } else if (!needsOscillator && oscillatorChartRef.current) {
      // Destroy oscillator chart
      oscillatorChartRef.current.remove();
      oscillatorChartRef.current = null;
    }
  }, [indicatorState.indicators.rsi.enabled, indicatorState.indicators.macd.enabled, overlayVisibility]);

  // Update oscillator indicators
  useEffect(() => {
    if (!oscillatorChartRef.current || !indicatorState.data) {
      oscillatorSeries.removeSeries('rsi');
      oscillatorSeries.removeSeries('macd-line');
      oscillatorSeries.removeSeries('macd-signal');
      oscillatorSeries.removeSeries('macd-histogram');
      return;
    }
    
    const { indicators } = indicatorState.data;
    if (!indicators) return;
    
    // Update RSI
    if (overlayVisibility.rsi && indicatorState.indicators.rsi.enabled && indicators.rsi) {
      oscillatorSeries.addOrUpdateSeries('rsi', indicators.rsi.values, {
        type: 'line',
        color: indicatorState.indicators.rsi.color,
        lineWidth: 2
      });
      
      // Add overbought/oversold lines
      const rsiSeries = oscillatorSeries.getSeries('rsi');
      if (rsiSeries) {
        rsiSeries.createPriceLine({
          price: indicatorState.indicators.rsi.overbought || 70,
          color: 'rgba(255, 0, 0, 0.3)',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: 'Overbought'
        });
        rsiSeries.createPriceLine({
          price: indicatorState.indicators.rsi.oversold || 30,
          color: 'rgba(0, 255, 0, 0.3)',
          lineWidth: 1,
          lineStyle: 2,
          axisLabelVisible: true,
          title: 'Oversold'
        });
      }
    } else {
      oscillatorSeries.removeSeries('rsi');
    }
    
    // Update MACD
    if (overlayVisibility.macd && indicatorState.indicators.macd.enabled && indicators.macd) {
      oscillatorSeries.addOrUpdateSeries('macd-line', indicators.macd.macdLine, {
        type: 'line',
        color: '#2962FF',
        lineWidth: 2
      });
      oscillatorSeries.addOrUpdateSeries('macd-signal', indicators.macd.signalLine, {
        type: 'line',
        color: '#FF6B35',
        lineWidth: 2
      });
      oscillatorSeries.addOrUpdateSeries('macd-histogram', indicators.macd.histogram, {
        type: 'histogram',
        color: '#26A69A'
      });
    } else {
      oscillatorSeries.removeSeries('macd-line');
      oscillatorSeries.removeSeries('macd-signal');
      oscillatorSeries.removeSeries('macd-histogram');
    }
  }, [indicatorState.data, indicatorState.indicators, overlayVisibility, oscillatorSeries]);
  
  return (
    <div className="trading-chart-container">
      <ChartToolbar setTool={(tool) => toolboxRef.current?.setTool(tool)} />

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
      
      {patternHighlight && !isLoading && !error && (
        <div className="pattern-highlight-banner">
          <strong>{patternHighlight.title}</strong>
          {patternHighlight.description && <span>{patternHighlight.description}</span>}
        </div>
      )}

      <div 
        ref={chartContainerRef} 
        className="main-chart" 
        style={{ 
          opacity: (isLoading || error) ? 0.3 : 1,
          height: showOscillatorPane ? 'calc(100% - 160px)' : '100%'
        }} 
      />
      
      {/* Oscillator Chart (RSI/MACD) */}
      {showOscillatorPane && (
        <div className="oscillator-chart" ref={oscillatorContainerRef} />
      )}
      
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
                color: '#ef4444',
                padding: '2px 8px',
                border: '1px solid #ef4444',
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
