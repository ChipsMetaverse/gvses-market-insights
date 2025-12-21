/**
 * TrendlineChart Component - Enhanced with Draggable Endpoints
 * Modular, reusable chart component with agent-driven trendline support + drag editing
 */

import { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time, LineStyle } from 'lightweight-charts';
import type { Trendline, CandleData, TrendlineOptions } from './types';

interface TrendlineChartProps {
  symbol: string;
  apiBase?: string;
  onTrendlineCreated?: (id: string) => void;
  onTrendlineDeleted?: (id: string) => void;
  enableInteractiveDrawing?: boolean;
}

interface TrendlineVisual {
  line: ISeriesApi<'Line'>;
  handleA: ISeriesApi<'Line'>;
  handleB: ISeriesApi<'Line'>;
  coordinates: { a: { time: number; price: number }; b: { time: number; price: number } };
  color: string;
}

export const TrendlineChart = ({
  symbol,
  apiBase = 'http://localhost:8001',
  onTrendlineCreated,
  onTrendlineDeleted,
  enableInteractiveDrawing = true
}: TrendlineChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const trendlinesRef = useRef<Map<string, TrendlineVisual>>(new Map());

  const [drawingMode, setDrawingMode] = useState(false);
  const drawingModeRef = useRef(false); // Ref for event handlers to avoid closure issues
  const [drawingPoints, setDrawingPoints] = useState<Array<{ time: number; price: number }>>([]);
  const drawingPointsRef = useRef<Array<{ time: number; price: number }>>([]); // Ref for event handlers to avoid closure issues
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<Array<{ time: string; message: string; type: string }>>([]);
  const [selectedTrendlineId, setSelectedTrendlineId] = useState<string | null>(null);
  
  // Edit state (drag system)
  const editStateRef = useRef<{
    isDragging: boolean;
    trendlineId: string | null;
    handleType: 'a' | 'b' | null;
    anchorPoint: { time: number; price: number } | null;
  }>({ isDragging: false, trendlineId: null, handleType: null, anchorPoint: null });


  const previewLineRef = useRef<ISeriesApi<'Line'> | null>(null);
  const lastDragPositionRef = useRef<{ time: number; price: number } | null>(null);
  const documentMouseUpHandlerRef = useRef<(() => void) | null>(null);

  // PDH/PDL lines (Previous Day High/Low)
  const pdhLineRef = useRef<ISeriesApi<'Line'> | null>(null);
  const pdlLineRef = useRef<ISeriesApi<'Line'> | null>(null);

  // Sync drawingMode ref with state to avoid closure issues in event handlers
  useEffect(() => {
    drawingModeRef.current = drawingMode;
  }, [drawingMode]);

  // Sync drawingPoints ref with state to avoid closure issues in event handlers
  useEffect(() => {
    drawingPointsRef.current = drawingPoints;
  }, [drawingPoints]);

  // Helper: Calculate distance from point to line segment
  const distanceToLineSegment = (
    px: number, py: number,
    x1: number, y1: number,
    x2: number, y2: number
  ): number => {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;

    if (lenSq !== 0) param = dot / lenSq;

    let xx, yy;

    if (param < 0) {
      xx = x1;
      yy = y1;
    } else if (param > 1) {
      xx = x2;
      yy = y2;
    } else {
      xx = x1 + param * C;
      yy = y1 + param * D;
    }

    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
  };

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: chartContainerRef.current.clientHeight,
      layout: {
        background: { color: '#0a0a0a' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: '#1a1a1a' },
        horzLines: { color: '#1a1a1a' },
      },
      timeScale: {
        borderColor: '#333',
        timeVisible: true,
      },
      rightPriceScale: {
        borderColor: '#333',
      },
      crosshair: {
        mode: 0,
      },
    });

    const series = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    chartRef.current = chart;
    seriesRef.current = series;

    // Capture container reference for event listeners
    const container = chartContainerRef.current;

    // Global click handler for drawing mode AND handle detection
    if (enableInteractiveDrawing) {
      chart.subscribeClick((param) => {
        if (!param.time || !param.point) return;

        const price = series.coordinateToPrice(param.point.y);
        if (price === null) return;

        // Drawing mode takes priority
        if (drawingModeRef.current) {
          const newPoint = { time: param.time as number, price };
          setDrawingPoints(prev => {
            const updated = [...prev, newPoint];

            // Update ref immediately so crosshair handler sees the new value
            drawingPointsRef.current = updated;

            if (updated.length === 2) {
              createTrendlineAPI(updated[0].time, updated[0].price, updated[1].time, updated[1].price, {
                name: 'Manual Trendline',
                color: '#2196F3'
              });

              // Clean up preview line
              if (previewLineRef.current && chartRef.current) {
                chartRef.current.removeSeries(previewLineRef.current);
                previewLineRef.current = null;
              }

              setDrawingMode(false);
              drawingPointsRef.current = []; // Clear ref too
              return [];
            }

            return updated;
          });
        } else {
          // Check if clicking on a handle (for drag initiation)
          const clickedTime = param.time as number;
          const clickedPrice = price;

          const pixelTolerance = 30;
          const visiblePriceRange = Math.abs(
            (series.coordinateToPrice(0) || 0) - (series.coordinateToPrice(600) || 0)
          );
          const priceTolerance = (visiblePriceRange / 600) * pixelTolerance;

          for (const [id, trendline] of trendlinesRef.current.entries()) {
            const coords = trendline.coordinates;

            // Check handle A
            const logicalClickTime = chart.timeScale().timeToCoordinate(clickedTime);
            const logicalHandleA = chart.timeScale().timeToCoordinate(coords.a.time);

            if (logicalClickTime !== null && logicalHandleA !== null) {
              const logicalTimeDiff = Math.abs(logicalClickTime - logicalHandleA);
              const priceDiff = Math.abs(clickedPrice - coords.a.price);

              if (logicalTimeDiff < pixelTolerance && priceDiff < priceTolerance) {
                editStateRef.current = {
                  isDragging: true,
                  trendlineId: id,
                  handleType: 'a',
                  anchorPoint: { time: coords.b.time, price: coords.b.price }
                };
                console.log('🎯 Clicked handle A - drag mode active');
                addLog(`🎯 Editing handle A`, 'info');
                return;
              }
            }

            // Check handle B
            const logicalHandleB = chart.timeScale().timeToCoordinate(coords.b.time);

            if (logicalClickTime !== null && logicalHandleB !== null) {
              const logicalTimeDiff = Math.abs(logicalClickTime - logicalHandleB);
              const priceDiff = Math.abs(clickedPrice - coords.b.price);

              if (logicalTimeDiff < pixelTolerance && priceDiff < priceTolerance) {
                editStateRef.current = {
                  isDragging: true,
                  trendlineId: id,
                  handleType: 'b',
                  anchorPoint: { time: coords.a.time, price: coords.a.price }
                };
                console.log('🎯 Clicked handle B - drag mode active');
                addLog(`🎯 Editing handle B`, 'info');
                return;
              }
            }
          }

          // No handle was clicked - check if clicking on a trendline body
          const lineClickTolerance = 10; // pixels
          for (const [id, trendline] of trendlinesRef.current.entries()) {
            const coords = trendline.coordinates;

            // Convert to pixel coordinates
            const x1 = chart.timeScale().timeToCoordinate(coords.a.time);
            const y1 = series.priceToCoordinate(coords.a.price);
            const x2 = chart.timeScale().timeToCoordinate(coords.b.time);
            const y2 = series.priceToCoordinate(coords.b.price);

            if (x1 !== null && y1 !== null && x2 !== null && y2 !== null) {
              const distance = distanceToLineSegment(
                param.point.x,
                param.point.y,
                x1,
                y1,
                x2,
                y2
              );

              if (distance < lineClickTolerance) {
                setSelectedTrendlineId(id);
                console.log('📍 Selected trendline:', id);
                addLog(`📍 Trendline selected`, 'info');
                return;
              }
            }
          }

          // No trendline was clicked - deselect
          if (selectedTrendlineId !== null) {
            setSelectedTrendlineId(null);
            console.log('⭕ Deselected trendline');
            addLog(`⭕ Selection cleared`, 'info');
          }
        }
      });

      // Crosshair move handler for drag preview, drawing preview, and position tracking
      chart.subscribeCrosshairMove((param) => {
        if (!param.time || !param.point) return;

        const price = series.coordinateToPrice(param.point.y);
        if (price === null) return;

        // PRIORITY 1: Handle drag preview (editing existing trendline)
        if (editStateRef.current.isDragging) {
          const { anchorPoint } = editStateRef.current;
          if (!anchorPoint) return;

          // Store last position for when drag ends
          lastDragPositionRef.current = { time: param.time as number, price };

          // Remove old preview line
          if (previewLineRef.current && chartRef.current) {
            chartRef.current.removeSeries(previewLineRef.current);
          }

          // Create new preview line from anchor to cursor
          const preview = chartRef.current!.addLineSeries({
            color: '#00ff00',  // Green preview for visibility
            lineWidth: 3,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
          });

          preview.setData([
            { time: anchorPoint.time as Time, value: anchorPoint.price },
            { time: param.time, value: price }
          ]);

          previewLineRef.current = preview;
          return;  // Exit after handling drag
        }

        // PRIORITY 2: Handle drawing preview (creating new trendline)
        if (drawingModeRef.current && drawingPointsRef.current.length === 1) {
          const firstPoint = drawingPointsRef.current[0];

          // Create preview line if it doesn't exist yet
          if (!previewLineRef.current && chartRef.current) {
            const preview = chartRef.current.addLineSeries({
              color: '#2196F3',  // Blue to match final trendline
              lineWidth: 2,
              lineStyle: LineStyle.Dashed,  // Dashed for "ghost" effect
              priceLineVisible: false,
              lastValueVisible: false,
            });
            previewLineRef.current = preview;
          }

          // Update preview line data (much faster than recreating)
          if (previewLineRef.current) {
            previewLineRef.current.setData([
              { time: firstPoint.time as Time, value: firstPoint.price },
              { time: param.time, value: price }
            ]);
          }

          return;  // Exit after handling drawing
        }
      });

      // Document-level mouseup to end drag operations
      const handleDocumentMouseUp = () => {
        if (!editStateRef.current.isDragging) return;

        const { trendlineId, handleType, anchorPoint } = editStateRef.current;
        const lastPos = lastDragPositionRef.current;

        if (trendlineId && handleType && anchorPoint && lastPos) {
          const trendline = trendlinesRef.current.get(trendlineId);
          if (trendline) {
            // Update coordinates with new endpoint
            const newCoords = { ...trendline.coordinates };
            newCoords[handleType] = { time: lastPos.time, price: lastPos.price };

            // Update in database and visual
            updateTrendlineInDB(trendlineId, newCoords);
            updateTrendlineVisual(trendlineId, newCoords, trendline.color);
          }
        }

        // Reset drag state
        editStateRef.current = {
          isDragging: false,
          trendlineId: null,
          handleType: null,
          anchorPoint: null
        };

        lastDragPositionRef.current = null;

        // Clean up preview line
        if (previewLineRef.current && chartRef.current) {
          chartRef.current.removeSeries(previewLineRef.current);
          previewLineRef.current = null;
        }

        addLog('✅ Handle position updated', 'success');
      };

      // Store handler in ref for cleanup
      documentMouseUpHandlerRef.current = handleDocumentMouseUp;

      // Attach to document to catch mouseup anywhere
      document.addEventListener('mouseup', handleDocumentMouseUp);
    }

    // Auto-resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);

    addLog('Chart initialized - Click handles to edit');

    return () => {
      window.removeEventListener('resize', handleResize);

      // Clean up document mouseup listener
      if (documentMouseUpHandlerRef.current) {
        document.removeEventListener('mouseup', documentMouseUpHandlerRef.current);
      }

      // Clean up preview line if exists
      if (previewLineRef.current && chartRef.current) {
        chartRef.current.removeSeries(previewLineRef.current);
      }

      // Clean up PDH/PDL lines if they exist
      try {
        if (pdhLineRef.current && chartRef.current) {
          chartRef.current.removeSeries(pdhLineRef.current);
        }
      } catch (e) {
        // Series may have already been removed
      }
      try {
        if (pdlLineRef.current && chartRef.current) {
          chartRef.current.removeSeries(pdlLineRef.current);
        }
      } catch (e) {
        // Series may have already been removed
      }

      chart.remove();
    };
  }, []); // Chart initializes once on mount - drawing mode is checked in handlers

  // Re-render trendlines when selection changes
  useEffect(() => {
    if (!chartRef.current) return;

    // Re-render all trendlines with updated selection state
    for (const [id, trendline] of trendlinesRef.current.entries()) {
      updateTrendlineVisual(id, trendline.coordinates, trendline.color);
    }
  }, [selectedTrendlineId]);

  // Keyboard handler for deleting selected trendline
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Delete on Backspace or Delete key
      if ((e.key === 'Backspace' || e.key === 'Delete') && selectedTrendlineId) {
        e.preventDefault(); // Prevent browser back navigation on Backspace
        deleteSelectedTrendline();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedTrendlineId]); // Re-attach when selection changes

  // Load sample data
  useEffect(() => {
    if (!seriesRef.current) return;

    const data: CandlestickData<Time>[] = [];
    let base = 150;
    const now = Math.floor(Date.now() / 1000);

    for (let i = 100; i >= 0; i--) {
      const time = (now - (i * 86400)) as Time;
      const change = (Math.random() - 0.5) * 5;
      base += change;

      const open = base;
      const close = base + (Math.random() - 0.5) * 3;
      const high = Math.max(open, close) + Math.random() * 2;
      const low = Math.min(open, close) - Math.random() * 2;

      data.push({ time, open, high, low, close });
    }

    seriesRef.current.setData(data);
    addLog(`Loaded ${data.length} candles`);

    // Calculate and display PDH (Previous Day High) and PDL (Previous Day Low)
    if (data.length >= 2 && chartRef.current) {
      // Get yesterday's data (second to last day)
      const yesterdayData = data.filter((candle, index) => {
        const yesterdayTime = now - 86400; // Yesterday in seconds
        const candleTime = typeof candle.time === 'number' ? candle.time : 0;
        // Get all candles from yesterday (within 24 hours of yesterday)
        return candleTime >= yesterdayTime - 43200 && candleTime < yesterdayTime + 43200;
      });

      if (yesterdayData.length > 0) {
        // Calculate PDH and PDL from yesterday's candles
        const pdh = Math.max(...yesterdayData.map(c => c.high));
        const pdl = Math.min(...yesterdayData.map(c => c.low));

        // Remove old PDH/PDL lines if they exist
        try {
          if (pdhLineRef.current) {
            chartRef.current.removeSeries(pdhLineRef.current);
            pdhLineRef.current = null;
          }
        } catch (e) {
          // Series may have already been removed
        }
        try {
          if (pdlLineRef.current) {
            chartRef.current.removeSeries(pdlLineRef.current);
            pdlLineRef.current = null;
          }
        } catch (e) {
          // Series may have already been removed
        }

        // Create PDH line (Previous Day High)
        const pdhLine = chartRef.current.addLineSeries({
          color: '#22c55e',  // Green for high
          lineWidth: 1,
          priceLineVisible: false,
          lastValueVisible: false,
          title: 'PDH',
        });

        pdhLine.setData([
          { time: data[0].time as Time, value: pdh },
          { time: data[data.length - 1].time as Time, value: pdh }
        ]);

        // Create PDL line (Previous Day Low)
        const pdlLine = chartRef.current.addLineSeries({
          color: '#ef4444',  // Red for low
          lineWidth: 1,
          priceLineVisible: false,
          lastValueVisible: false,
          title: 'PDL',
        });

        pdlLine.setData([
          { time: data[0].time as Time, value: pdl },
          { time: data[data.length - 1].time as Time, value: pdl }
        ]);

        pdhLineRef.current = pdhLine;
        pdlLineRef.current = pdlLine;

        addLog(`PDH: $${pdh.toFixed(2)}, PDL: $${pdl.toFixed(2)}`, 'info');
      }
    }
  }, [symbol]);

  // Load saved trendlines
  useEffect(() => {
    // loadSavedTrendlines(); // Disabled - start with clean chart
    checkAPI();
  }, [symbol, apiBase]);

  const addLog = (message: string, type: string = 'info') => {
    setLogs(prev => [...prev, {
      time: new Date().toLocaleTimeString(),
      message,
      type
    }]);
  };

  const checkAPI = async () => {
    try {
      const res = await fetch(`${apiBase}/health`);
      setIsConnected(res.ok);
    } catch {
      setIsConnected(false);
    }
  };

  const loadSavedTrendlines = async () => {
    try {
      const response = await fetch(`${apiBase}/api/drawings?symbol=${symbol}`);
      if (!response.ok) return;

      const data = await response.json();

      for (const drawing of data.drawings) {
        renderTrendlineWithHandles(drawing.id, drawing.data.coordinates, drawing.data.color);
      }

      addLog(`Loaded ${data.total} saved trendlines`, 'success');
    } catch (error) {
      addLog(`Error loading: ${error}`, 'error');
    }
  };

  const renderTrendlineWithHandles = (id: string, coordinates: any, color: string, isSelected = false) => {
    if (!chartRef.current) return;

    // Main trendline (thicker when selected)
    const lineSeries = chartRef.current.addLineSeries({
      color: isSelected ? '#FFD700' : color, // Gold color when selected
      lineWidth: isSelected ? 4 : 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    lineSeries.setData([
      { time: coordinates.a.time as Time, value: coordinates.a.price },
      { time: coordinates.b.time as Time, value: coordinates.b.price },
    ]);

    // Handle A (draggable endpoint)
    const handleA = chartRef.current.addLineSeries({
      color: color,
      lineWidth: 8,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    handleA.setData([{ time: coordinates.a.time as Time, value: coordinates.a.price }]);

    // Handle B (draggable endpoint)
    const handleB = chartRef.current.addLineSeries({
      color: color,
      lineWidth: 8,
      lineStyle: LineStyle.Solid,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    handleB.setData([{ time: coordinates.b.time as Time, value: coordinates.b.price }]);

    // Store reference (no per-handle click subscriptions needed - using global handler)
    trendlinesRef.current.set(id, {
      line: lineSeries,
      handleA,
      handleB,
      coordinates,
      color
    });
  };

  const updateTrendlineVisual = (id: string, newCoords: any, color: string) => {
    const existing = trendlinesRef.current.get(id);
    if (!existing || !chartRef.current) return;

    // Remove old series
    chartRef.current.removeSeries(existing.line);
    chartRef.current.removeSeries(existing.handleA);
    chartRef.current.removeSeries(existing.handleB);

    // Render with new coordinates (check if this trendline is selected)
    const isSelected = selectedTrendlineId === id;
    renderTrendlineWithHandles(id, newCoords, color, isSelected);
  };

  const updateTrendlineInDB = async (id: string, coordinates: any) => {
    try {
      await fetch(`${apiBase}/api/drawings/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: { coordinates } })
      });
    } catch (error) {
      addLog(`Error updating: ${error}`, 'error');
    }
  };

  const createTrendlineAPI = async (
    startTime: number,
    startPrice: number,
    endTime: number,
    endPrice: number,
    options: TrendlineOptions = {}
  ): Promise<string | null> => {
    const drawing: Omit<Trendline, 'id'> = {
      symbol,
      type: 'trendline',
      data: {
        name: options.name || 'Trendline',
        color: options.color || '#4CAF50',
        width: options.width || 2,
        style: 'solid',
        visible: true,
        coordinates: {
          a: { time: startTime, price: startPrice },
          b: { time: endTime, price: endPrice },
        },
      },
    };

    try {
      const response = await fetch(`${apiBase}/api/drawings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(drawing),
      });

      if (!response.ok) throw new Error('Failed to save drawing');

      const saved = await response.json();
      renderTrendlineWithHandles(saved.id, saved.data.coordinates, saved.data.color);
      addLog(`Agent created: ${saved.data.name}`, 'success');
      
      onTrendlineCreated?.(saved.id);
      return saved.id;
    } catch (error) {
      addLog(`Error: ${error}`, 'error');
      return null;
    }
  };

  const deleteSelectedTrendline = async () => {
    if (!selectedTrendlineId) return;

    try {
      // Delete from database
      await fetch(`${apiBase}/api/drawings/${selectedTrendlineId}`, { method: 'DELETE' });

      // Remove from chart
      const visual = trendlinesRef.current.get(selectedTrendlineId);
      if (visual && chartRef.current) {
        chartRef.current.removeSeries(visual.line);
        chartRef.current.removeSeries(visual.handleA);
        chartRef.current.removeSeries(visual.handleB);
      }

      // Remove from ref
      trendlinesRef.current.delete(selectedTrendlineId);

      // Call callback
      onTrendlineDeleted?.(selectedTrendlineId);

      addLog('Trendline deleted', 'success');
      console.log('🗑️ Deleted trendline:', selectedTrendlineId);

      // Clear selection
      setSelectedTrendlineId(null);
    } catch (error) {
      addLog(`Error deleting: ${error}`, 'error');
    }
  };

  const clearAllTrendlines = async () => {
    if (!confirm('Clear all trendlines?')) return;

    try {
      await fetch(`${apiBase}/api/drawings?symbol=${symbol}`, { method: 'DELETE' });

      trendlinesRef.current.forEach((visual, id) => {
        chartRef.current?.removeSeries(visual.line);
        chartRef.current?.removeSeries(visual.handleA);
        chartRef.current?.removeSeries(visual.handleB);
        onTrendlineDeleted?.(id);
      });
      trendlinesRef.current.clear();

      addLog('All trendlines cleared', 'success');
    } catch (error) {
      addLog(`Error clearing: ${error}`, 'error');
    }
  };

  // Expose API
  useEffect(() => {
    (window as any).trendlineChartAPI = {
      createTrendline: createTrendlineAPI,
      clearAll: clearAllTrendlines,
    };
  }, [symbol, apiBase]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#0a0a0a', color: '#fff' }}>
      {/* Status Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', padding: '15px 20px', borderBottom: '1px solid #1a1a1a' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'center' }}>
          <div style={{ padding: '8px 16px', background: '#1a1a1a', borderRadius: '8px' }}>
            <span style={{ fontWeight: 600, fontSize: '14px' }}>{symbol}</span>
            <span style={{ fontSize: '14px', marginLeft: '8px' }}>$277.60</span>
            <span style={{ fontSize: '12px', marginLeft: '8px', padding: '2px 6px', borderRadius: '4px', background: 'rgba(34, 197, 94, 0.2)', color: '#22c55e' }}>+0.3%</span>
          </div>
        </div>
        <div style={{ fontSize: '12px', padding: '8px 16px', background: 'rgba(26, 26, 26, 0.95)', borderRadius: '20px', border: `1px solid ${isConnected ? '#4CAF50' : '#333'}`, color: isConnected ? '#4CAF50' : '#888' }}>
          ● {isConnected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {/* Toolbar */}
      <div style={{ display: 'flex', gap: '10px', padding: '15px 20px', borderBottom: '1px solid #1a1a1a', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '5px' }}>
          {['1D', '5D', '1M', '6M', '1Y'].map((period, i) => (
            <button
              key={period}
              style={{
                padding: '6px 12px',
                background: i === 0 ? '#2196F3' : '#1a1a1a',
                color: '#fff',
                border: `1px solid ${i === 0 ? '#2196F3' : '#333'}`,
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 500,
              }}
            >
              {period}
            </button>
          ))}
        </div>

        {enableInteractiveDrawing && (
          <div style={{ display: 'flex', gap: '8px', paddingLeft: '20px', borderLeft: '1px solid #333' }}>
            <button
              onClick={() => setDrawingMode(!drawingMode)}
              style={{
                padding: '6px 14px',
                background: drawingMode ? 'rgba(76, 175, 80, 0.2)' : '#1a1a1a',
                color: '#fff',
                border: '1px solid #4CAF50',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              ↗️ Trendline
            </button>
            <button
              onClick={() => {
                // Clean up preview line when canceling
                if (previewLineRef.current && chartRef.current) {
                  chartRef.current.removeSeries(previewLineRef.current);
                  previewLineRef.current = null;
                }
                setDrawingMode(false);
                setDrawingPoints([]);
                drawingPointsRef.current = [];
              }}
              style={{
                padding: '6px 14px',
                background: '#1a1a1a',
                color: '#fff',
                border: '1px solid #ef4444',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
              }}
            >
              ✕ Cancel
            </button>
            <button
              onClick={clearAllTrendlines}
              style={{
                padding: '6px 14px',
                background: '#1a1a1a',
                color: '#fff',
                border: '1px solid #f59e0b',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '13px',
                marginLeft: '10px',
              }}
            >
              🗑️ Clear All
            </button>
          </div>
        )}

      </div>

      {/* Chart */}
      <div ref={chartContainerRef} style={{ flex: 1, padding: '0 20px 20px' }} />

      {/* Drawing/Dragging Mode Indicators */}
      {drawingMode && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '12px 24px',
          background: 'rgba(33, 150, 243, 0.95)',
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: 500,
          zIndex: 1000,
        }}>
          Click two points to draw trendline {drawingPoints.length > 0 && `(${drawingPoints.length}/2)`}
        </div>
      )}
      
      {editStateRef.current.isEditing && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          padding: '12px 24px',
          background: 'rgba(59, 130, 246, 0.95)',
          borderRadius: '20px',
          fontSize: '14px',
          fontWeight: 500,
          zIndex: 1000,
        }}>
          ✏️ Editing endpoint... Click again to save
        </div>
      )}

      {/* Console Log */}
      <div style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        width: '300px',
        maxHeight: '200px',
        background: 'rgba(26, 26, 26, 0.95)',
        border: '1px solid #333',
        borderRadius: '8px',
        padding: '12px',
        fontFamily: 'monospace',
        fontSize: '11px',
        overflowY: 'auto',
        zIndex: 1000,
      }}>
        {logs.slice(-10).map((log, i) => (
          <div key={i} style={{ marginBottom: '4px', color: log.type === 'success' ? '#4CAF50' : log.type === 'error' ? '#ef4444' : '#888' }}>
            {log.time}: {log.message}
          </div>
        ))}
      </div>
    </div>
  );
};
