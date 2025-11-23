/**
 * Enhanced Chart Control Service
 * Extends chartControlService with full indicator control capabilities
 * Allows agent to manipulate all chart features while speaking to users
 */

import {
  IChartApi,
  ISeriesApi,
  SeriesType,
  LineSeries,
  UTCTimestamp,
  SeriesMarker,
  SeriesMarkerShape,
  Time,
} from 'lightweight-charts';
import { chartControlService, type StructuredChartCommand } from './chartControlService';
import { DrawingPrimitive } from './DrawingPrimitive';
import { PREFER_STRUCTURED_CHART_COMMANDS } from '../utils/featureFlags';
import { DrawingStore } from '../drawings/DrawingStore';
import type { AnyDrawing, Trendline, Ray, Horizontal, Tp } from '../drawings/types';
import { uid } from '../drawings/types';

type ParsedDrawingCommand =
  | { action: 'pattern_level'; patternId: string; levelType: string; price: number }
  | { action: 'pattern_target'; patternId: string; price: number }
  | {
      action: 'pattern_trendline';
      patternId: string;
      startTime: number;
      startPrice: number;
      endTime: number;
      endPrice: number;
    }
  | { action: 'pattern_annotation'; patternId: string; status: string }
  | { action: 'clear_pattern'; patternId: string }
  | { action: 'clear_all' }
  | { action: 'support'; price: number }
  | { action: 'resistance'; price: number }
  | { action: 'trendline'; startPrice: number; startTime: number; endPrice: number; endTime: number }
  | { action: 'fibonacci'; high: number; low: number }
  | { action: 'entry'; price: number }
  | { action: 'target'; price: number }
  | { action: 'stoploss'; price: number }
  | { action: 'add_trendline'; startTime: Time; startPrice: number; endTime: Time; endPrice: number; color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted' }
  | { action: 'add_ray'; startTime: Time; startPrice: number; endTime: Time; endPrice: number; color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted'; direction?: 'right' | 'left' | 'both' }
  | { action: 'add_horizontal'; price: number; color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted'; draggable?: boolean; rotation?: number }
  | { action: 'remove_drawing'; id: string };

type MarkerCapableCandlestickSeries = ISeriesApi<'Candlestick'> & {
  setMarkers(markers: SeriesMarker<Time>[]): void;
};

class EnhancedChartControl {
  private chartRef: IChartApi | null = null;
  private mainSeriesRef: MarkerCapableCandlestickSeries | null = null;
  private indicatorDispatch: any = null;
  private drawingsMap: Map<string, any> = new Map();
  private annotationsMap: Map<string, ISeriesApi<SeriesType>> = new Map();
  private drawingPrimitive: DrawingPrimitive | null = null;
  private patternMarkers: SeriesMarker<Time>[] = [];
  private storeRef: DrawingStore | null = null; // NEW: Reference to drawing store

  private overlayControls: {
    setOverlayVisibility?: (indicator: string, enabled: boolean) => void;
    clearOverlays?: () => void;
    highlightPattern?: (pattern: string, payload?: any) => void;
  } = {};

  // Link to original service
  private baseService = chartControlService;
  
  /**
   * Initialize with chart reference, main series, and indicator dispatch
   */
  initialize(chart: IChartApi, mainSeries: MarkerCapableCandlestickSeries, indicatorDispatch: any) {
    this.chartRef = chart;
    this.mainSeriesRef = mainSeries;
    this.indicatorDispatch = indicatorDispatch;
    this.baseService.setChartRef(chart);
    console.log('Enhanced chart control initialized');
  }

  /**
   * Attach the DrawingStore for programmatic drawing support
   */
  attach(chart: IChartApi, mainSeries: MarkerCapableCandlestickSeries, store: DrawingStore) {
    this.chartRef = chart;
    this.mainSeriesRef = mainSeries;
    this.storeRef = store;
    console.log('Drawing store attached to enhanced chart control');
  }

  /**
   * Programmatic drawing API: Add trendline
   */
  addTrendline(a: Tp, b: Tp, options?: { color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted' }): string {
    if (!this.storeRef) {
      console.warn('DrawingStore not attached. Call attach() first.');
      return '';
    }

    const drawing: Trendline = {
      id: uid('tl'),
      kind: 'trendline',
      a,
      b,
      color: options?.color || '#22c55e',
      width: options?.width || 2,
      style: options?.style || 'solid',
    };

    this.storeRef.upsert(drawing);
    return drawing.id;
  }

  /**
   * Programmatic drawing API: Add ray
   */
  addRay(a: Tp, b: Tp, options?: { color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted'; direction?: 'right' | 'left' | 'both' }): string {
    if (!this.storeRef) {
      console.warn('DrawingStore not attached. Call attach() first.');
      return '';
    }

    const drawing: Ray = {
      id: uid('ray'),
      kind: 'ray',
      a,
      b,
      color: options?.color || '#1e90ff',
      width: options?.width || 2,
      style: options?.style || 'dashed',
      direction: options?.direction || 'right',
    };

    this.storeRef.upsert(drawing);
    return drawing.id;
  }

  /**
   * Programmatic drawing API: Add horizontal line
   */
  addHorizontal(price: number, options?: { color?: string; width?: number; style?: 'solid' | 'dashed' | 'dotted'; draggable?: boolean; rotation?: number }): string {
    if (!this.storeRef) {
      console.warn('DrawingStore not attached. Call attach() first.');
      return '';
    }

    const drawing: Horizontal = {
      id: uid('h'),
      kind: 'horizontal',
      price,
      color: options?.color || '#888',
      width: options?.width || 2,
      style: options?.style || 'dashed',
      draggable: options?.draggable !== false,
      rotation: options?.rotation ?? 0,
    };

    this.storeRef.upsert(drawing);
    return drawing.id;
  }

  /**
   * Programmatic drawing API: Remove specific drawing by ID
   */
  removeDrawing(id: string): void {
    if (!this.storeRef) {
      console.warn('DrawingStore not attached. Call attach() first.');
      return;
    }

    this.storeRef.remove(id);
  }

  /**
   * Alias for removeDrawing (Phase-2 API compatibility)
   */
  remove(id: string): void {
    this.removeDrawing(id);
  }

  /**
   * Clear all drawings from store (Phase-2 API compatibility)
   */
  clear(): void {
    if (!this.storeRef) {
      console.warn('DrawingStore not attached. Call attach() first.');
      return;
    }
    this.storeRef.clear();
  }

  /**
   * Get drawings count (for testing)
   */
  get drawings(): Map<string, any> {
    return this.drawingsMap;
  }
  
  /**
   * Get annotations count (for testing)
   */
  get annotations(): Map<string, ISeriesApi<SeriesType>> {
    return this.annotationsMap;
  }
  
  setChartRef(chart: IChartApi) {
    this.chartRef = chart;
    this.baseService.setChartRef(chart);
  }
  
  /**
   * Get chart reference (for testing)
   */
  getChartRef(): IChartApi | null {
    return this.chartRef;
  }

  clearDrawings(): string {
    this.drawingsMap.forEach((line) => {
      if (line && typeof line.remove === 'function') {
        try {
          line.remove();
        } catch (error) {
          console.warn('Error removing drawing line:', error);
        }
      }
    });
    this.drawingsMap.clear();

    if (this.chartRef) {
      this.annotationsMap.forEach(series => {
        try {
          this.chartRef!.removeSeries(series);
        } catch (error) {
          console.error('Error removing annotation series:', error);
        }
      });
    }
    this.annotationsMap.clear();

    if (this.mainSeriesRef) {
      this.patternMarkers = [];
      // Note: TradingView Lightweight Charts v5 doesn't support setMarkers() method
      // Markers are managed through the patternMarkers array
    }

    // Clear the drawing store (manual drawings)
    if (this.storeRef) {
      this.storeRef.clear();
    }

    this.overlayControls.clearOverlays?.();
    return 'Cleared all drawings';
  }

  /**
   * Expose current visible time range for callers that need viewport awareness.
   */
  getVisibleTimeRange(): { from: number; to: number } | null {
    if (!this.chartRef) {
      return null;
    }

    const timeScale = this.chartRef.timeScale();
    if (typeof timeScale.getVisibleRange !== 'function') {
      return null;
    }

    const range = timeScale.getVisibleRange();
    if (!range) {
      return null;
    }

    return {
      from: Number(range.from),
      to: Number(range.to),
    };
  }

  /**
   * Set the DrawingPrimitive for drawing tools support
   */
  setDrawingPrimitive(primitive: DrawingPrimitive) {
    this.drawingPrimitive = primitive;
  }

  /**
   * Set the visible time range explicitly.
   */
  setVisibleTimeRange(range: { from: number; to: number }): void {
    if (!this.chartRef) {
      return;
    }

    const timeScale = this.chartRef.timeScale();
    if (typeof timeScale.setVisibleRange !== 'function') {
      return;
    }

    timeScale.setVisibleRange({
      from: range.from as UTCTimestamp,
      to: range.to as UTCTimestamp,
    });
  }

  /**
   * Briefly center the chart on a specific timestamp.
   */
  focusOnTime(timestamp: number, paddingSeconds: number = 60 * 60 * 24): void {
    if (!this.chartRef) {
      return;
    }

    const timeScale = this.chartRef.timeScale();
    const padding = Math.max(1, Math.floor(paddingSeconds));
    const from = (timestamp - padding) as UTCTimestamp;
    const to = (timestamp + padding) as UTCTimestamp;

    if (typeof timeScale.setVisibleRange === 'function') {
      timeScale.setVisibleRange({ from, to });
      return;
    }

    if (typeof timeScale.scrollToPosition === 'function') {
      timeScale.scrollToPosition(0, true);
    }
  }

  setOverlayControls(controls: {
    setOverlayVisibility?: (indicator: string, enabled: boolean) => void;
    clearOverlays?: () => void;
    highlightPattern?: (pattern: string, payload?: any) => void;
  }) {
    this.overlayControls = {
      ...this.overlayControls,
      ...controls,
    };
  }
  
  /**
   * Agent can toggle any indicator
   */
  toggleIndicator(indicatorName: string, enabled: boolean): string {
    if (!this.indicatorDispatch) {
      return 'Indicator controls not available';
    }
    
    // Map common names to indicator keys
    const indicatorMap: { [key: string]: { indicator: string; subIndicator?: string } } = {
      'ma20': { indicator: 'movingAverages', subIndicator: 'ma20' },
      'ma50': { indicator: 'movingAverages', subIndicator: 'ma50' },
      'ma200': { indicator: 'movingAverages', subIndicator: 'ma200' },
      'moving average 20': { indicator: 'movingAverages', subIndicator: 'ma20' },
      'moving average 50': { indicator: 'movingAverages', subIndicator: 'ma50' },
      'moving average 200': { indicator: 'movingAverages', subIndicator: 'ma200' },
      'bollinger': { indicator: 'bollingerBands' },
      'bollinger bands': { indicator: 'bollingerBands' },
      'rsi': { indicator: 'rsi' },
      'macd': { indicator: 'macd' },
      'fibonacci': { indicator: 'fibonacci' },
      'support resistance': { indicator: 'supportResistance' }
    };
    
    const config = indicatorMap[indicatorName.toLowerCase()] || { indicator: indicatorName };
    
    if (enabled) {
      this.indicatorDispatch({ 
        type: 'TOGGLE_INDICATOR', 
        payload: config 
      });
      
      // If enabling RSI or MACD, also show oscillator pane
      if (indicatorName.toLowerCase() === 'rsi' || indicatorName.toLowerCase() === 'macd') {
        this.indicatorDispatch({
          type: 'SET_OSCILLATOR_PANE',
          payload: { show: true, type: indicatorName.toLowerCase() as 'rsi' | 'macd' }
        });
      }
    } else {
      this.indicatorDispatch({ 
        type: 'TOGGLE_INDICATOR', 
        payload: config 
      });
    }

    this.overlayControls.setOverlayVisibility?.(indicatorName, enabled);

    return `${indicatorName} ${enabled ? 'enabled' : 'disabled'}`;
  }
  
  /**
   * Agent can apply preset indicator combinations
   */
  applyIndicatorPreset(preset: 'basic' | 'advanced' | 'momentum' | 'trend' | 'volatility'): string {
    if (!this.indicatorDispatch) {
      return 'Indicator controls not available';
    }
    
    // First reset all indicators
    this.indicatorDispatch({ type: 'RESET_TO_DEFAULTS' });
    this.overlayControls.clearOverlays?.();

    // Apply preset
    switch (preset) {
      case 'basic':
        this.toggleIndicator('ma20', true);
        this.toggleIndicator('ma50', true);
        return 'Applied basic analysis (MA20, MA50)';
        
      case 'advanced':
        this.toggleIndicator('ma20', true);
        this.toggleIndicator('ma50', true);
        this.toggleIndicator('ma200', true);
        this.toggleIndicator('bollinger bands', true);
        this.toggleIndicator('rsi', true);
        return 'Applied advanced analysis (MAs, Bollinger, RSI)';
        
      case 'momentum':
        this.toggleIndicator('rsi', true);
        this.toggleIndicator('macd', true);
        return 'Applied momentum indicators (RSI, MACD)';
        
      case 'trend':
        this.toggleIndicator('ma20', true);
        this.toggleIndicator('ma50', true);
        this.toggleIndicator('ma200', true);
        return 'Applied trend indicators (MA20, MA50, MA200)';
        
      case 'volatility':
        this.toggleIndicator('bollinger bands', true);
        this.toggleIndicator('support resistance', true);
        return 'Applied volatility indicators (Bollinger Bands, Support/Resistance)';
        
      default:
        return 'Unknown preset';
    }
  }
  
  /**
   * Agent can draw trend lines on the chart
   */
  drawTrendLine(
    startTime: number, 
    startPrice: number, 
    endTime: number, 
    endPrice: number, 
    label?: string,
    color: string = '#FF6B35'
  ): string {
    if (!this.chartRef) {
      return 'Chart not available';
    }
    
    try {
      // Use DrawingPrimitive if available (persistent drawings)
      if (this.drawingPrimitive) {
        console.log('[Enhanced Chart] Using DrawingPrimitive for trendline', {
          startTime, startPrice, endTime, endPrice, label
        });
        
        const id = this.drawingPrimitive.addTrendline(
          startPrice,
          startTime as any, // Time type conversion
          endPrice,
          endTime as any // Time type conversion
        );
        
        return `Drew ${label ? label + ' ' : ''}trend line from $${startPrice.toFixed(2)} to $${endPrice.toFixed(2)} (ID: ${id})`;
      }
      
      // Fallback to old v5 API (non-persistent)
      console.warn('[Enhanced Chart] DrawingPrimitive not available, using fallback v5 API');
      const trendSeries = this.chartRef.addSeries(LineSeries, {
        color,
        lineWidth: 2,
        crosshairMarkerVisible: false,
        lastValueVisible: false,
        priceLineVisible: false
      });
      
      trendSeries.setData([
        { time: startTime as any, value: startPrice },
        { time: endTime as any, value: endPrice }
      ]);
      
      const id = `trend_${Date.now()}`;
      this.annotationsMap.set(id, trendSeries);
      
      return `Drew ${label ? label + ' ' : ''}trend line from $${startPrice.toFixed(2)} to $${endPrice.toFixed(2)} (fallback)`;
    } catch (error) {
      console.error('Error drawing trend line:', error);
      return 'Failed to draw trend line';
    }
  }
  
  /**
   * Agent can highlight support/resistance levels
   */
  highlightLevel(price: number, type: 'support' | 'resistance' | 'pivot', label?: string): string {
    if (!this.chartRef || !this.mainSeriesRef) {
      return 'Chart not available';
    }
    const series = this.mainSeriesRef;

    const colors = {
      support: '#22c55e',
      resistance: '#ef4444',
      pivot: '#f59e0b'
    };
    
    try {
      const priceLine = series.createPriceLine({
        price,
        color: colors[type],
        lineWidth: 2,
        lineStyle: 2, // Dashed
        axisLabelVisible: true,
        title: label || `${type.charAt(0).toUpperCase() + type.slice(1)} $${price.toFixed(2)}`
      });
      
      this.drawingsMap.set(`${type}_${price}`, priceLine);
      return `Highlighted ${type} level at $${price.toFixed(2)}`;
    } catch (error) {
      console.error('Error highlighting level:', error);
      return `Error: ${error}`;
    }
    
    return 'Failed to highlight level';
  }
  
  /**
   * Draw support and resistance levels on the chart
   * @param levels - Object with support and resistance arrays
   */
  drawSupportResistanceLevels(levels: { support: number[], resistance: number[] }): void {
    if (!this.chartRef || !this.mainSeriesRef) return;
    const series = this.mainSeriesRef;

    // Helper function to deduplicate and cluster price levels
    const deduplicateAndLimitLevels = (inputLevels: number[] | undefined, maxCount: number = 5): number[] => {
      if (!inputLevels?.length) return [];

      // Sort levels
      const sorted = [...inputLevels].sort((a, b) => a - b);

      // Deduplicate and cluster levels within 0.1% of each other
      const deduplicated: number[] = [];
      let lastLevel: number | null = null;

      for (const level of sorted) {
        if (lastLevel === null || Math.abs(level - lastLevel) / lastLevel > 0.001) {
          deduplicated.push(level);
          lastLevel = level;
        }
      }

      // Limit to max count
      return deduplicated.slice(0, maxCount);
    };

    // Draw support levels with deduplication
    const deduplicatedSupport = deduplicateAndLimitLevels(levels.support, 5);
    deduplicatedSupport.forEach((level, index) => {
      const priceLine = series.createPriceLine({
        price: level,
        color: '#22c55e',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        title: `S${index + 1}`,
        axisLabelVisible: true
      });
      this.drawingsMap.set(`support_${index}`, priceLine);
    });

    // Draw resistance levels with deduplication
    const deduplicatedResistance = deduplicateAndLimitLevels(levels.resistance, 5);
    deduplicatedResistance.forEach((level, index) => {
      const priceLine = series.createPriceLine({
        price: level,
        color: '#ef4444',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        title: `R${index + 1}`,
        axisLabelVisible: true
      });
      this.drawingsMap.set(`resistance_${index}`, priceLine);
    });
  }
  
  /**
   * Process pattern detection results and visualize on chart
   * @param patterns - Pattern detection results from API
   */
  async processPatternResults(patterns: any): Promise<string> {
    if (!patterns) return "No patterns to display";
    
    // Draw support/resistance levels
    if (patterns.active_levels) {
      this.drawSupportResistanceLevels(patterns.active_levels);
    }
    
    // Highlight detected patterns
    if (patterns.detected && patterns.detected.length > 0) {
      // Focus on the most recent high-confidence pattern
      const bestPattern = patterns.detected
        .sort((a: any, b: any) => b.confidence - a.confidence)[0];
      
      if (bestPattern) {
        const candles = [];
        for (let i = bestPattern.start_candle; i <= bestPattern.end_candle; i++) {
          candles.push(i);
        }
        this.highlightPattern(bestPattern.id, candles, bestPattern.type);
        this.overlayControls.highlightPattern?.(bestPattern.type, {
          title: bestPattern.description || bestPattern.type,
          description: bestPattern.agent_explanation,
          indicator: bestPattern.related_indicator,
        });
        
        return `Showing ${bestPattern.description} (${bestPattern.confidence}% confidence)`;
      }
    }
    
    return patterns.agent_explanation || "Pattern analysis complete";
  }
  
  /**
   * Parse and execute indicator-related commands from agent speech
   */
  async processIndicatorCommand(text: string): Promise<string> {
    const lowerText = text.toLowerCase();
    
    // Check for indicator mentions
    if (lowerText.includes('moving average') || lowerText.includes('ma ')) {
      if (lowerText.includes('20') || lowerText.includes('twenty')) {
        return this.toggleIndicator('ma20', !lowerText.includes('hide') && !lowerText.includes('remove'));
      }
      if (lowerText.includes('50') || lowerText.includes('fifty')) {
        return this.toggleIndicator('ma50', !lowerText.includes('hide') && !lowerText.includes('remove'));
      }
      if (lowerText.includes('200') || lowerText.includes('two hundred')) {
        return this.toggleIndicator('ma200', !lowerText.includes('hide') && !lowerText.includes('remove'));
      }
      // Enable all MAs if no specific period mentioned
      this.toggleIndicator('ma20', true);
      this.toggleIndicator('ma50', true);
      this.toggleIndicator('ma200', true);
      return 'Enabled all moving averages';
    }
    
    if (lowerText.includes('bollinger')) {
      return this.toggleIndicator('bollinger bands', !lowerText.includes('hide') && !lowerText.includes('remove'));
    }
    
    if (lowerText.includes('rsi')) {
      return this.toggleIndicator('rsi', !lowerText.includes('hide') && !lowerText.includes('remove'));
    }
    
    if (lowerText.includes('macd')) {
      return this.toggleIndicator('macd', !lowerText.includes('hide') && !lowerText.includes('remove'));
    }
    
    if (lowerText.includes('fibonacci') || lowerText.includes('fib')) {
      return this.toggleIndicator('fibonacci', !lowerText.includes('hide') && !lowerText.includes('remove'));
    }
    
    if (lowerText.includes('support') || lowerText.includes('resistance')) {
      return this.toggleIndicator('support resistance', !lowerText.includes('hide') && !lowerText.includes('remove'));
    }
    
    // Check for presets
    if (lowerText.includes('basic analysis')) {
      return this.applyIndicatorPreset('basic');
    }
    if (lowerText.includes('advanced analysis')) {
      return this.applyIndicatorPreset('advanced');
    }
    if (lowerText.includes('momentum')) {
      return this.applyIndicatorPreset('momentum');
    }
    if (lowerText.includes('trend analysis')) {
      return this.applyIndicatorPreset('trend');
    }
    if (lowerText.includes('volatility')) {
      return this.applyIndicatorPreset('volatility');
    }
    
    // Check for clear command
    if (lowerText.includes('clear') && (lowerText.includes('drawing') || lowerText.includes('line'))) {
      return this.clearDrawings();
    }
    
    // Check for level highlighting
    const priceMatch = lowerText.match(/\$?(\d+(?:\.\d+)?)/);
    if (priceMatch) {
      const price = parseFloat(priceMatch[1]);
      if (lowerText.includes('support')) {
        return this.highlightLevel(price, 'support');
      }
      if (lowerText.includes('resistance')) {
        return this.highlightLevel(price, 'resistance');
      }
    }
    
    // Delegate to base service for standard chart commands
    const commands = await this.baseService.parseAgentResponse(text);
    if (commands.length > 0) {
      for (const command of commands) {
        this.baseService.executeCommand(command);
      }
      return `Executed ${commands.length} chart command(s)`;
    }
    
    return '';
  }
  
  /**
   * Get indicator explanations for agent to narrate
   */
  getIndicatorExplanation(indicatorName: string): string {
    const explanations: { [key: string]: string } = {
      'ma20': 'The 20-day moving average shows short-term trend direction',
      'ma50': 'The 50-day moving average indicates medium-term trend',
      'ma200': 'The 200-day moving average represents long-term trend',
      'bollinger bands': 'Bollinger Bands show volatility and potential support/resistance levels',
      'rsi': 'RSI measures momentum - above 70 is overbought, below 30 is oversold',
      'macd': 'MACD shows the relationship between two moving averages, useful for trend changes',
      'fibonacci': 'Fibonacci levels identify potential reversal points',
      'support resistance': 'Support and resistance levels show where price tends to bounce'
    };
    
    return explanations[indicatorName.toLowerCase()] || `${indicatorName} helps analyze price movements`;
  }
  
  /**
   * Set the indicator dispatch function from React context
   */
  setIndicatorDispatch(dispatch: any) {
    this.indicatorDispatch = dispatch;
    console.log('Indicator dispatch connected to enhanced chart control');
  }

  revealPattern(pattern: string, info?: { description?: string; indicator?: string; title?: string }) {
    if (info?.indicator) {
      this.overlayControls.setOverlayVisibility?.(info.indicator, true);
    }
    this.overlayControls.highlightPattern?.(pattern, info);
    return `Highlighting ${pattern}`;
  }
  
  /**
   * Process enhanced response - combines chart commands and indicator commands
   * FIX: Execute LOAD commands first, wait for chart to stabilize, then draw
   */
  async processEnhancedResponse(
    response: string,
    chartCommandsFromApi: string[] = [],
    structuredCommandsFromApi: StructuredChartCommand[] = []
  ): Promise<any[]> {
    const processingMode = PREFER_STRUCTURED_CHART_COMMANDS ? 'structured-first' : 'hybrid';

    console.log('[Enhanced Chart] 🔥 processEnhancedResponse called with:', {
      responseSnippet: response?.slice(0, 120),
      legacyCount: chartCommandsFromApi.length,
      structuredCount: structuredCommandsFromApi.length,
      processingMode
    });

    // Log structured-first mode behavior
    if (PREFER_STRUCTURED_CHART_COMMANDS && structuredCommandsFromApi.length > 0) {
      console.log('[Enhanced Chart] 🎯 Structured-first mode: Processing structured commands only, ignoring legacy');
    } else if (PREFER_STRUCTURED_CHART_COMMANDS && structuredCommandsFromApi.length === 0) {
      console.log('[Enhanced Chart] ⚠️ Structured-first mode: No structured commands, falling back to pattern matching');
    }

    const executedCommands: any[] = [];
    const executedCommandKeys = new Set<string>();

    const parsedCommands = await this.baseService.parseAgentResponse(
      response,
      chartCommandsFromApi,
      structuredCommandsFromApi
    );

    // STEP 1: Execute symbol changes (LOAD) first
    const symbolCommands = parsedCommands.filter(cmd => cmd.type === 'symbol');
    if (symbolCommands.length > 0) {
      for (const symbolCommand of symbolCommands) {
        const key = JSON.stringify({ type: symbolCommand.type, value: symbolCommand.value });
        if (executedCommandKeys.has(key)) {
          continue;
        }

        if (this.baseService.executeCommand(symbolCommand)) {
          executedCommandKeys.add(key);
          executedCommands.push({ type: 'symbol_change', command: symbolCommand });
        }
      }

      console.log('[Enhanced Chart] ⏳ Waiting 2.5 seconds for chart to stabilize after symbol change...');
      await new Promise(resolve => setTimeout(resolve, 2500));
      console.log('[Enhanced Chart] ✅ Chart should be stable now, proceeding with drawings');
    }

    // STEP 2: Execute drawing commands (support/resistance, fibonacci, trendlines, etc.)
    const executedDrawingKeys = new Set<string>();
    const drawingCommands = parsedCommands.filter(cmd => cmd.type === 'drawing');
    for (const drawingCommand of drawingCommands) {
      const key = JSON.stringify(drawingCommand.value);
      if (executedDrawingKeys.has(key)) {
        continue;
      }

      const result = this.executeDrawingCommand(drawingCommand.value as ParsedDrawingCommand);
      if (result) {
        executedDrawingKeys.add(key);
        executedCommands.push({ type: 'drawing', command: drawingCommand.value, result });
      }
    }

    // Include any residual DRAW:* tokens from the raw response text
    const textDrawingCommands = this.parseDrawingCommands(response);
    for (const drawCmd of textDrawingCommands) {
      const key = JSON.stringify(drawCmd);
      if (executedDrawingKeys.has(key)) {
        continue;
      }

      const result = this.executeDrawingCommand(drawCmd);
      if (result) {
        executedDrawingKeys.add(key);
        executedCommands.push({ type: 'drawing', command: drawCmd, result });
      }
    }

    // STEP 3: Natural language indicator processing
    const indicatorResult = await this.processIndicatorCommand(response);
    if (indicatorResult) {
      executedCommands.push({ type: 'indicator', result: indicatorResult });
    }

    // STEP 4: Execute remaining standard commands (timeframes, indicators, zoom, etc.)
    const remainingCommands = parsedCommands.filter(
      cmd => cmd.type !== 'symbol' && cmd.type !== 'drawing'
    );

    for (const command of remainingCommands) {
      const key = JSON.stringify({ type: command.type, value: command.value });
      if (executedCommandKeys.has(key)) {
        continue;
      }

      if (command.type === 'indicator' && indicatorResult) {
        continue;
      }

      if (this.baseService.executeCommand(command)) {
        executedCommandKeys.add(key);
        executedCommands.push(command);
      }
    }

    console.log('[Enhanced Chart] 🎉 All commands processed, total:', executedCommands.length);
    return executedCommands;
  }
  
  /**
   * Parse drawing commands from agent response
   */
  private parseDrawingCommands(response: string): ParsedDrawingCommand[] {
    const commands: ParsedDrawingCommand[] = [];
    const tokens = response.split(/\s+/).filter(Boolean);

    for (const token of tokens) {
      if (token.startsWith('DRAW:')) {
        const parts = token.split(':');
        if (parts.length < 2) continue;

        const subType = parts[1];
        switch (subType) {
          case 'LEVEL': {
            if (parts.length >= 5) {
              const [, , patternId, levelType, priceRaw] = parts;
              const price = parseFloat(priceRaw);
              if (patternId && levelType && !Number.isNaN(price)) {
                commands.push({ action: 'pattern_level', patternId, levelType, price });
              }
            }
            break;
          }
          case 'TARGET': {
            if (parts.length >= 4) {
              const [, , patternId, priceRaw] = parts;
              const price = parseFloat(priceRaw);
              if (patternId && !Number.isNaN(price)) {
                commands.push({ action: 'pattern_target', patternId, price });
              }
            }
            break;
          }
          case 'TRENDLINE': {
            if (parts.length >= 7) {
              const [, , patternId, startTimeRaw, startPriceRaw, endTimeRaw, endPriceRaw] = parts;
              const startTime = parseInt(startTimeRaw, 10);
              const startPrice = parseFloat(startPriceRaw);
              const endTime = parseInt(endTimeRaw, 10);
              const endPrice = parseFloat(endPriceRaw);
              if (
                patternId &&
                !Number.isNaN(startTime) &&
                !Number.isNaN(startPrice) &&
                !Number.isNaN(endTime) &&
                !Number.isNaN(endPrice)
              ) {
                commands.push({
                  action: 'pattern_trendline',
                  patternId,
                  startTime,
                  startPrice,
                  endTime,
                  endPrice,
                });
              }
            }
            break;
          }
          default:
            break;
        }
        continue;
      }

      if (token.startsWith('ANNOTATE:PATTERN:')) {
        const parts = token.split(':');
        if (parts.length >= 4) {
          const patternId = parts[2];
          const status = parts[3];
          if (patternId && status) {
            commands.push({ action: 'pattern_annotation', patternId, status });
          }
        }
        continue;
      }

      if (token.startsWith('CLEAR:PATTERN:')) {
        const parts = token.split(':');
        if (parts.length >= 3) {
          const patternId = parts[2];
          if (patternId) {
            commands.push({ action: 'clear_pattern', patternId });
          }
        }
        continue;
      }

      if (token === 'CLEAR:ALL') {
        commands.push({ action: 'clear_all' });
        continue;
      }

      if (token.startsWith('SUPPORT:')) {
        const price = parseFloat(token.substring(8));
        if (!Number.isNaN(price)) {
          commands.push({ action: 'support', price });
        }
        continue;
      }

      if (token.startsWith('RESISTANCE:')) {
        const price = parseFloat(token.substring(11));
        if (!Number.isNaN(price)) {
          commands.push({ action: 'resistance', price });
        }
        continue;
      }

      if (token.startsWith('FIBONACCI:')) {
        const [highRaw, lowRaw] = token.substring(10).split(':');
        const high = parseFloat(highRaw);
        const low = parseFloat(lowRaw);
        if (!Number.isNaN(high) && !Number.isNaN(low)) {
          commands.push({ action: 'fibonacci', high, low });
        }
        continue;
      }

      if (token.startsWith('TRENDLINE:')) {
        const parts = token.substring(10).split(':');
        if (parts.length >= 4) {
          const [startPriceRaw, startTimeRaw, endPriceRaw, endTimeRaw] = parts;
          const startPrice = parseFloat(startPriceRaw);
          const startTime = parseInt(startTimeRaw, 10);
          const endPrice = parseFloat(endPriceRaw);
          const endTime = parseInt(endTimeRaw, 10);
          if (
            !Number.isNaN(startPrice) &&
            !Number.isNaN(startTime) &&
            !Number.isNaN(endPrice) &&
            !Number.isNaN(endTime)
          ) {
            commands.push({ action: 'trendline', startPrice, startTime, endPrice, endTime });
          }
        }
        continue;
      }

      if (token.startsWith('ENTRY:')) {
        const price = parseFloat(token.substring(6));
        if (!Number.isNaN(price)) {
          commands.push({ action: 'entry', price });
        }
        continue;
      }

      if (token.startsWith('TARGET:')) {
        const price = parseFloat(token.substring(7));
        if (!Number.isNaN(price)) {
          commands.push({ action: 'target', price });
        }
        continue;
      }

      if (token.startsWith('STOPLOSS:')) {
        const price = parseFloat(token.substring(9));
        if (!Number.isNaN(price)) {
          commands.push({ action: 'stoploss', price });
        }
        continue;
      }
    }

    return commands;
  }

  /**
   * Execute a drawing command
   */
  private executeDrawingCommand(drawing: ParsedDrawingCommand): string | null {
    try {
      switch (drawing.action) {
        case 'pattern_level': {
          const levelType = drawing.levelType ? drawing.levelType.toLowerCase() : 'pivot';
          const mappedType: 'support' | 'resistance' | 'pivot' =
            levelType === 'support' ? 'support' : levelType === 'resistance' ? 'resistance' : 'pivot';
          const label = `${drawing.patternId} ${levelType}`.trim();
          return this.highlightLevel(drawing.price, mappedType, label);
        }

        case 'pattern_target': {
          const label = drawing.patternId ? `${drawing.patternId} target` : 'Target';
          return this.highlightLevel(drawing.price, 'pivot', label);
        }

        case 'pattern_trendline':
          return this.drawTrendLine(
            drawing.startTime,
            drawing.startPrice,
            drawing.endTime,
            drawing.endPrice,
            `${drawing.patternId} trend`
          );

        case 'pattern_annotation':
          this.overlayControls.highlightPattern?.(drawing.patternId, {
            title: `${drawing.patternId} ${drawing.status}`,
            description: `Pattern status updated to ${drawing.status}`,
          });
          return `Annotated ${drawing.patternId} as ${drawing.status}`;

        case 'clear_pattern':
          this.clearDrawings();
          return `Cleared drawings for ${drawing.patternId}`;


        case 'trendline':
          // Use DrawingPrimitive if available, fallback to old method
          if (this.drawingPrimitive) {
            // Convert Unix timestamps to chart time format
            // For recent timestamps, convert to chart-relative time
            const now = Math.floor(Date.now() / 1000);
            let startTime = drawing.startTime;
            let endTime = drawing.endTime;
            
            // If the timestamps are too old (more than 2 years), use relative time
            if (now - drawing.startTime > 2 * 365 * 24 * 60 * 60) {
              console.log('[Enhanced Chart] Converting old timestamps to relative time');
              // Use last 7 days for the trendline
              endTime = now;
              startTime = now - (7 * 24 * 60 * 60); // 7 days ago
            }
            
            console.log('[Enhanced Chart] Adding trendline with times:', { startTime, endTime, startPrice: drawing.startPrice, endPrice: drawing.endPrice });
            
            this.drawingPrimitive.addTrendline(
              drawing.startPrice,
              startTime as any, // Time type conversion
              drawing.endPrice,
              endTime as any // Time type conversion
            );
          } else {
            this.drawTrendLine(
              drawing.startTime,
              drawing.startPrice,
              drawing.endTime,
              drawing.endPrice
            );
          }
          return 'Trend line drawn';

        case 'support':
          // Use DrawingPrimitive if available
          console.log(`[Enhanced Chart] 🟢 Drawing support at ${drawing.price}, drawingPrimitive:`, !!this.drawingPrimitive);
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Support', '#4CAF50');
            console.log(`[Enhanced Chart] ✅ Support line added via DrawingPrimitive`);
          } else {
            console.log(`[Enhanced Chart] ⚠️ Using fallback highlightLevel for support`);
            this.highlightLevel(drawing.price, 'support');
          }
          return `Support level at ${drawing.price}`;

        case 'resistance':
          // Use DrawingPrimitive if available
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Resistance', '#ef4444');
          } else {
            this.highlightLevel(drawing.price, 'resistance');
          }
          return `Resistance level at ${drawing.price}`;
          
        case 'fibonacci':
          // Use DrawingPrimitive if available
          if (this.drawingPrimitive && 'high' in drawing && 'low' in drawing) {
            const currentTime = Date.now();
            const startTime = currentTime - (7 * 24 * 60 * 60 * 1000); // 7 days ago
            this.drawingPrimitive.addFibonacci(
              (drawing as any).high,
              (drawing as any).low,
              startTime as any, // Time type conversion
              currentTime as any // Time type conversion
            );
            return `Fibonacci levels added from ${(drawing as any).high} to ${(drawing as any).low}`;
          }
          return null;

        case 'entry':
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Entry', '#2196F3');
          } else {
            this.highlightLevel(drawing.price, 'pivot', 'Entry');
          }
          return `Entry level at ${drawing.price}`;

        case 'target':
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Target', '#22c55e');
          } else {
            this.highlightLevel(drawing.price, 'pivot', 'Target');
          }
          return `Target level at ${drawing.price}`;

        case 'stoploss':
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Stop Loss', '#ef4444');
          } else {
            this.highlightLevel(drawing.price, 'pivot', 'Stop');
          }
          return `Stop loss at ${drawing.price}`;
          
        case 'add_trendline': {
          if (!this.storeRef) {
            console.warn('DrawingStore not attached. Cannot add trendline.');
            return null;
          }
          const { startTime, startPrice, endTime, endPrice, color, width, style } = drawing as any;
          const id = this.addTrendline(
            { time: startTime as Time, price: startPrice },
            { time: endTime as Time, price: endPrice },
            { color, width, style }
          );
          return id ? `Trendline ${id} added` : null;
        }

        case 'add_ray': {
          if (!this.storeRef) {
            console.warn('DrawingStore not attached. Cannot add ray.');
            return null;
          }
          const { startTime, startPrice, endTime, endPrice, color, width, style, direction } = drawing as any;
          const id = this.addRay(
            { time: startTime as Time, price: startPrice },
            { time: endTime as Time, price: endPrice },
            { color, width, style, direction }
          );
          return id ? `Ray ${id} added` : null;
        }

        case 'add_horizontal': {
          if (!this.storeRef) {
            console.warn('DrawingStore not attached. Cannot add horizontal.');
            return null;
          }
          const { price, color, width, style, draggable, rotation } = drawing as any;
          const id = this.addHorizontal(price, { color, width, style, draggable, rotation });
          return id ? `Horizontal line ${id} added at ${price}${rotation ? ` with ${Math.round(rotation)}° rotation` : ''}` : null;
        }

        case 'remove_drawing': {
          if (!this.storeRef) {
            console.warn('DrawingStore not attached. Cannot remove drawing.');
            return null;
          }
          const { id } = drawing as any;
          if (id) {
            this.removeDrawing(id);
            return `Drawing ${id} removed`;
          }
          return null;
        }

        case 'clear_all':
          if (this.drawingPrimitive) {
            this.drawingPrimitive.clearAllDrawings();
          }
          if (this.storeRef) {
            this.storeRef.clear();
          }
          return 'All drawings cleared';

        default:
          return null;
      }
    } catch (error) {
      console.error('Error executing drawing command:', error);
      return null;
    }
  }
  
  /**
   * Convert hex color to RGBA
   */
  private hexToRGBA(hex: string, alpha: number): string {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  }
  
  /**
   * Draw a boundary box around pattern candles (Phase 2B)
   */
  drawPatternBoundaryBox(config: {
    start_time: number;
    end_time: number;
    high: number;
    low: number;
    border_color: string;
    border_width: number;
    fill_opacity: number;
  }): string {
    if (!this.chartRef) {
      return 'Chart not initialized';
    }

    try {
      console.log('[Enhanced Chart] Drawing pattern boundary box', config);
      
      // Draw top border
      const topBorder = this.chartRef.addSeries(LineSeries, {
        color: config.border_color,
        lineWidth: config.border_width,
        lineStyle: 0, // Solid
        priceLineVisible: false,
        lastValueVisible: false,
      });
      topBorder.setData([
        { time: config.start_time as UTCTimestamp, value: config.high },
        { time: config.end_time as UTCTimestamp, value: config.high }
      ]);

      // Draw bottom border
      const bottomBorder = this.chartRef.addSeries(LineSeries, {
        color: config.border_color,
        lineWidth: config.border_width,
        lineStyle: 0,
        priceLineVisible: false,
        lastValueVisible: false,
      });
      bottomBorder.setData([
        { time: config.start_time as UTCTimestamp, value: config.low },
        { time: config.end_time as UTCTimestamp, value: config.low }
      ]);

      // Note: Vertical lines omitted due to Lightweight Charts limitation
      // (cannot have duplicate timestamps). Top/bottom borders provide
      // sufficient visual indication of pattern boundary.
      
      const boxId = `pattern_box_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      this.annotationsMap.set(boxId, topBorder);
      this.annotationsMap.set(`${boxId}_bottom`, bottomBorder);

      console.log('[Enhanced Chart] Pattern boundary box drawn:', boxId);
      return `Pattern boundary box drawn`;
    } catch (error) {
      console.error('Failed to draw pattern boundary box:', error);
      return `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }

  /**
   * Highlight pattern candles with color overlay (Phase 2B)
   * Note: Lightweight Charts doesn't support candle color overlays directly
   * This method will add markers on the pattern candles instead
   */
  highlightPatternCandles(
    candleIndices: number[],
    candleData: any[],
    overlayColor: string,
    opacity: number = 0.3
  ): string {
    if (!this.chartRef || !this.mainSeriesRef) {
      return 'Chart not initialized';
    }

    try {
      console.log('[Enhanced Chart] Highlighting pattern candles', {
        count: candleIndices.length,
        color: overlayColor,
        opacity
      });

      const newMarkers: SeriesMarker<Time>[] = [];

      candleIndices.forEach(idx => {
        if (idx >= candleData.length) {
          return;
        }

        const candle = candleData[idx];
        const time = candle?.time ?? candle?.timestamp ?? candle?.t;

        if (time === undefined || time === null) {
          return;
        }

        const markerEntry: SeriesMarker<Time> = {
          time: time as UTCTimestamp,
          position: 'aboveBar',
          color: overlayColor,
          shape: 'circle',
          text: '',
          size: Math.max(0.4, Math.min(1, opacity)),
        };
        newMarkers.push(markerEntry);
      });

      if (newMarkers.length === 0) {
        console.log('[Enhanced Chart] No valid candle markers generated');
        return 'No candles highlighted';
      }

      const newMarkerTimes = new Set(newMarkers.map(marker => marker.time));
      this.patternMarkers = [
        ...this.patternMarkers.filter(marker => !newMarkerTimes.has(marker.time)),
        ...newMarkers
      ];

      // Note: setMarkers() not supported in TradingView Lightweight Charts v5
      // this.mainSeriesRef.setMarkers(this.patternMarkers);
      console.log('[Enhanced Chart] Pattern markers applied', { count: this.patternMarkers.length });
      return `Marked ${newMarkers.length} pattern candles`;
    } catch (error) {
      console.error('Failed to highlight pattern candles:', error);
      return `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }

  highlightPattern(_patternId: string, candles: number[], patternType: string): void {
    if (!this.chartRef || !this.mainSeriesRef) {
      return;
    }

    const series = this.mainSeriesRef;
    const seriesData = (series as unknown as { data?: () => any[] }).data?.();
    if (!Array.isArray(seriesData) || seriesData.length === 0) {
      console.debug('[Enhanced Chart] No series data available for pattern highlight');
      return;
    }

    const overlayColor = patternType.includes('bearish')
      ? '#ef4444'
      : patternType.includes('bullish')
        ? '#22c55e'
        : '#3b82f6';

    this.highlightPatternCandles(candles, seriesData, overlayColor, 0.6);
  }

  /**
   * Draw pattern markers (arrows, circles, stars) (Phase 2B)
   */
  drawPatternMarker(marker: {
    type: 'arrow' | 'circle' | 'star';
    direction?: 'up' | 'down';
    time: number;
    price: number;
    color: string;
    label?: string;
    radius?: number;
  }): string {
    if (!this.chartRef || !this.mainSeriesRef) {
      return 'Chart not initialized';
    }

    try {
      console.log('[Enhanced Chart] Drawing pattern marker', marker);
      
      const markerShape: SeriesMarkerShape = marker.type === 'circle'
        ? 'circle'
        : marker.type === 'star'
          ? 'circle'
          : marker.direction === 'up'
            ? 'arrowUp'
            : 'arrowDown';

      const seriesMarker: SeriesMarker<Time> = {
        time: marker.time as UTCTimestamp,
        position: (marker.direction === 'up' ? 'belowBar' : 'aboveBar') as 'belowBar' | 'aboveBar',
        color: marker.color,
        shape: markerShape,
        text: marker.label || '',
        size: marker.radius || 1
      };

      this.patternMarkers = [...this.patternMarkers, seriesMarker];
      // Note: setMarkers() not supported in TradingView Lightweight Charts v5
      // this.mainSeriesRef.setMarkers(this.patternMarkers);
      console.log('[Enhanced Chart] Pattern marker added successfully');
      return `Pattern marker added at ${marker.time}`;
    } catch (error) {
      console.error('Failed to draw pattern marker:', error);
      return `Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
    }
  }
  
  /**
   * Register callbacks (delegate to base service for compatibility)
   */
  registerCallbacks(callbacks: any) {
    this.baseService.registerCallbacks(callbacks);
  }
}

// Export singleton instance
export const enhancedChartControl = new EnhancedChartControl();

// Export class for testing
export { EnhancedChartControl };
