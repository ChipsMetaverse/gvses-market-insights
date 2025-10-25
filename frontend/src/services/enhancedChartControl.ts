/**
 * Enhanced Chart Control Service
 * Extends chartControlService with full indicator control capabilities
 * Allows agent to manipulate all chart features while speaking to users
 */

import { IChartApi, ISeriesApi, SeriesType, LineSeries } from 'lightweight-charts';
import { chartControlService } from './chartControlService';
import { DrawingPrimitive } from './DrawingPrimitive';

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
  | { action: 'stoploss'; price: number };

class EnhancedChartControl {
  private chartRef: IChartApi | null = null;
  private mainSeriesRef: ISeriesApi<SeriesType> | null = null;
  private indicatorDispatch: any = null;
  private drawingsMap: Map<string, any> = new Map();
  private annotationsMap: Map<string, ISeriesApi<SeriesType>> = new Map();
  private drawingPrimitive: DrawingPrimitive | null = null;
  
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
  initialize(chart: IChartApi, mainSeries: ISeriesApi<SeriesType>, indicatorDispatch: any) {
    this.chartRef = chart;
    this.mainSeriesRef = mainSeries;
    this.indicatorDispatch = indicatorDispatch;
    this.baseService.setChartRef(chart);
    console.log('Enhanced chart control initialized');
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

  /**
   * Set the DrawingPrimitive for drawing tools support
   */
  setDrawingPrimitive(primitive: DrawingPrimitive) {
    this.drawingPrimitive = primitive;
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
    
    const colors = {
      support: '#22c55e',
      resistance: '#ef4444',
      pivot: '#f59e0b'
    };
    
    try {
      const priceLine = this.mainSeriesRef.createPriceLine({
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
   * Draw a trendline between two points
   */
  drawTrendline(startTime: number, startPrice: number, endTime: number, endPrice: number, color: string = '#3b82f6'): string {
    if (!this.chartRef || !this.seriesRef) {
      return 'Chart not initialized';
    }

    try {
      // Create line series for the trendline
      const lineSeries = this.chartRef.addLineSeries({
        color: color,
        lineWidth: 2,
        lineStyle: 0, // Solid line
        priceLineVisible: false,
        lastValueVisible: false,
      });

      // Set data points for the trendline
      lineSeries.setData([
        { time: startTime, value: startPrice },
        { time: endTime, value: endPrice }
      ]);

      // Store reference for cleanup
      const lineId = `trendline_${Date.now()}`;
      this.annotationsMap.set(lineId, lineSeries);

      return `Trendline drawn from ${startTime} to ${endTime}`;
    } catch (error) {
      console.error('Error drawing trendline:', error);
      return 'Failed to draw trendline';
    }
  }

  /**
   * Draw a horizontal line at a specific price level
   */
  drawHorizontalLine(price: number, color: string = '#ef4444', label?: string): string {
    if (!this.chartRef || !this.seriesRef) {
      return 'Chart not initialized';
    }

    try {
      // Create price line
      const priceLine = this.seriesRef.createPriceLine({
        price: price,
        color: color,
        lineWidth: 2,
        lineStyle: 2, // Dashed line
        axisLabelVisible: true,
        title: label || `Level ${price.toFixed(2)}`,
      });

      // Store reference for cleanup
      const lineId = `horizontal_${Date.now()}`;
      this.drawingsMap.set(lineId, priceLine);

      return `Horizontal line drawn at ${price.toFixed(2)}`;
    } catch (error) {
      console.error('Error drawing horizontal line:', error);
      return 'Failed to draw horizontal line';
    }
  }

  /**
   * Clear all drawings and annotations
   */
  clearDrawings(): string {
    // Remove price lines
    this.drawingsMap.forEach((line) => {
      if (line && line.remove) {
        line.remove();
      }
    });
    this.drawingsMap.clear();
    
    // Remove annotation series
    if (this.chartRef) {
      this.annotationsMap.forEach(series => {
        try {
          this.chartRef!.removeSeries(series);
        } catch (error) {
          console.error('Error removing series:', error);
        }
      });
    }
    this.annotationsMap.clear();
    this.overlayControls.clearOverlays?.();
    
    return 'Cleared all drawings';
  }

  /**
   * Clear a specific pattern's overlays
   */
  clearPattern(patternId: string): string {
    // Remove all drawings/annotations associated with this pattern
    // For now, we clear everything since we don't track per-pattern
    return this.clearDrawings();
  }
  
  /**
   * Highlight detected patterns on the chart
   * @param patternId - Unique pattern identifier
   * @param candles - Array of candle indices involved in the pattern
   * @param patternType - Type of pattern for styling
   */
  highlightPattern(patternId: string, candles: number[], patternType: string): void {
    if (!this.chartRef || !this.mainSeriesRef) return;
    
    // For now, add markers to highlight pattern candles
    // This is a simplified visualization approach
    const markers = candles.map(index => {
      let color = '#3b82f6'; // Default blue
      let text = '';
      
      // Color and label based on pattern type
      if (patternType.includes('bullish')) {
        color = '#22c55e'; // Green
        text = '↑';
      } else if (patternType.includes('bearish')) {
        color = '#ef4444'; // Red
        text = '↓';
      } else if (patternType === 'doji') {
        color = '#f59e0b'; // Orange
        text = '•';
      } else if (patternType === 'breakout') {
        color = '#8b5cf6'; // Purple
        text = '⚡';
      }
      
      return {
        time: index, // This should be the actual timestamp
        position: 'aboveBar' as const,
        color,
        shape: 'circle' as const,
        text
      };
    });
    
    // Note: setMarkers would need the actual time values from candle data
    // This is a simplified example - in production, you'd map indices to timestamps
    this.overlayControls.highlightPattern?.(patternType, { title: patternType });
  }
  
  /**
   * Draw support and resistance levels on the chart
   * @param levels - Object with support and resistance arrays
   */
  drawSupportResistanceLevels(levels: { support: number[], resistance: number[] }): void {
    if (!this.chartRef || !this.mainSeriesRef) return;
    
    // Draw support levels
    levels.support?.forEach((level, index) => {
      const priceLine = this.mainSeriesRef.createPriceLine({
        price: level,
        color: '#22c55e',
        lineWidth: 1,
        lineStyle: 2, // Dashed
        title: `S${index + 1}`,
        axisLabelVisible: true
      });
      this.drawingsMap.set(`support_${index}`, priceLine);
    });
    
    // Draw resistance levels
    levels.resistance?.forEach((level, index) => {
      const priceLine = this.mainSeriesRef.createPriceLine({
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
   */
  async processEnhancedResponse(response: string): Promise<any[]> {
    const commands = [];
    
    // Process drawing commands first (SUPPORT:, RESISTANCE:, FIBONACCI:, TRENDLINE:)
    const drawingCommands = this.parseDrawingCommands(response);
    for (const drawCmd of drawingCommands) {
      const result = this.executeDrawingCommand(drawCmd);
      if (result) {
        commands.push({ type: 'drawing', command: drawCmd, result });
      }
    }
    
    // Process indicator commands
    const indicatorResult = await this.processIndicatorCommand(response);
    if (indicatorResult) {
      commands.push({ type: 'indicator', result: indicatorResult });
    }
    
    // Process standard chart commands
    const chartCommands = await this.baseService.parseAgentResponse(response);
    for (const command of chartCommands) {
      if (this.baseService.executeCommand(command)) {
        commands.push(command);
      }
    }
    
    return commands;
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
          if (this.drawingPrimitive) {
            this.drawingPrimitive.addHorizontalLine(drawing.price, 'Support', '#4CAF50');
          } else {
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
          
        case 'clear_all':
          if (this.drawingPrimitive) {
            this.drawingPrimitive.clearAllDrawings();
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
