/**
 * Enhanced Chart Control Service
 * Extends chartControlService with full indicator control capabilities
 * Allows agent to manipulate all chart features while speaking to users
 */

import { IChartApi, ISeriesApi, SeriesType, LineSeries } from 'lightweight-charts';
import { chartControlService } from './chartControlService';

interface IndicatorCommand {
  action: 'enable' | 'disable' | 'configure' | 'preset' | 'explain';
  indicator?: string;
  parameters?: any;
  preset?: 'basic' | 'advanced' | 'momentum' | 'trend' | 'volatility';
}

interface DrawingCommand {
  action: 'trendline' | 'horizontal' | 'support' | 'resistance' | 'annotation' | 'clear';
  points?: Array<{ time: number; price: number }>;
  text?: string;
  style?: {
    color?: string;
    lineWidth?: number;
    lineStyle?: number;
  };
}

class EnhancedChartControl {
  private chartRef: IChartApi | null = null;
  private mainSeriesRef: ISeriesApi<SeriesType> | null = null;
  private indicatorDispatch: any = null;
  private drawingsMap: Map<string, any> = new Map();
  private annotationsMap: Map<string, ISeriesApi<SeriesType>> = new Map();
  
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
      // Using v5 API with addSeries
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
      
      return `Drew ${label ? label + ' ' : ''}trend line from $${startPrice.toFixed(2)} to $${endPrice.toFixed(2)}`;
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
  private parseDrawingCommands(response: string): any[] {
    const commands = [];
    const lines = response.split(/\s+/);
    
    for (const line of lines) {
      if (line.startsWith('SUPPORT:')) {
        const price = parseFloat(line.substring(8));
        if (!isNaN(price)) {
          commands.push({ action: 'support', price });
        }
      } else if (line.startsWith('RESISTANCE:')) {
        const price = parseFloat(line.substring(11));
        if (!isNaN(price)) {
          commands.push({ action: 'resistance', price });
        }
      } else if (line.startsWith('FIBONACCI:')) {
        const parts = line.substring(10).split(':');
        if (parts.length === 2) {
          const high = parseFloat(parts[0]);
          const low = parseFloat(parts[1]);
          if (!isNaN(high) && !isNaN(low)) {
            commands.push({ action: 'fibonacci', high, low });
          }
        }
      } else if (line.startsWith('TRENDLINE:')) {
        const parts = line.substring(10).split(':');
        if (parts.length >= 4) {
          commands.push({
            action: 'trendline',
            startPrice: parseFloat(parts[0]),
            startTime: parseInt(parts[1]),
            endPrice: parseFloat(parts[2]),
            endTime: parseInt(parts[3])
          });
        }
      }
    }
    
    return commands;
  }
  
  /**
   * Execute a drawing command
   */
  private executeDrawingCommand(drawing: any): string | null {
    try {
      switch(drawing.action) {
        case 'support':
          this.highlightLevel(drawing.price, 'support');
          return `Support level at ${drawing.price}`;
          
        case 'resistance':
          this.highlightLevel(drawing.price, 'resistance');
          return `Resistance level at ${drawing.price}`;
        
        case 'entry':
          this.highlightLevel(drawing.price, 'pivot', 'Entry');
          return `Entry level at ${drawing.price}`;
        
        case 'target':
          this.highlightLevel(drawing.price, 'pivot', 'Target');
          return `Target level at ${drawing.price}`;
        
        case 'stoploss':
          this.highlightLevel(drawing.price, 'pivot', 'Stop');
          return `Stop loss at ${drawing.price}`;
          
        case 'fibonacci':
          // Calculate and draw Fibonacci levels
          const fibLevels = [
            { level: 0, price: drawing.low },
            { level: 0.236, price: drawing.low + (drawing.high - drawing.low) * 0.236 },
            { level: 0.382, price: drawing.low + (drawing.high - drawing.low) * 0.382 },
            { level: 0.5, price: drawing.low + (drawing.high - drawing.low) * 0.5 },
            { level: 0.618, price: drawing.low + (drawing.high - drawing.low) * 0.618 },
            { level: 0.786, price: drawing.low + (drawing.high - drawing.low) * 0.786 },
            { level: 1, price: drawing.high }
          ];
          
          fibLevels.forEach(fib => {
            this.highlightLevel(
              parseFloat(fib.price.toFixed(2)),
              'pivot',
              `Fib ${(fib.level * 100).toFixed(1)}%`
            );
          });
          return `Fibonacci levels from ${drawing.low} to ${drawing.high}`;
          
        case 'trendline':
          this.drawTrendLine(
            drawing.startTime,
            drawing.startPrice,
            drawing.endTime,
            drawing.endPrice
          );
          return `Trend line drawn`;
          
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
