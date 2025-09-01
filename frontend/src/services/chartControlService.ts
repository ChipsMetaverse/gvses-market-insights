/**
 * Chart Control Service
 * Processes agent commands to control TradingView Lightweight Charts
 */

export interface ChartCommand {
  type: 'symbol' | 'timeframe' | 'indicator' | 'zoom' | 'scroll' | 'style';
  value: any;
  timestamp?: number;
}

export interface ChartControlCallbacks {
  onSymbolChange?: (symbol: string) => void;
  onTimeframeChange?: (timeframe: string) => void;
  onIndicatorToggle?: (indicator: string, enabled: boolean) => void;
  onZoomChange?: (level: number) => void;
  onScrollToTime?: (time: number) => void;
  onStyleChange?: (style: 'candles' | 'line' | 'area') => void;
  onCommandExecuted?: (command: ChartCommand, success: boolean, message: string) => void;
  onCommandError?: (error: string) => void;
}

class ChartControlService {
  private callbacks: ChartControlCallbacks = {};
  private currentSymbol: string = 'TSLA';
  private chartRef: any = null;
  
  // Command patterns for parsing agent responses
  private commandPatterns = {
    symbol: /(?:CHART|SHOW|DISPLAY|SWITCH TO|CHANGE TO)[:\s]+([A-Z]{1,5}(?:-USD)?)/i,
    timeframe: /(?:TIMEFRAME|TIME|PERIOD)[:\s]+(1D|5D|1M|3M|6M|1Y|YTD|ALL)/i,
    indicator: /(?:ADD|SHOW|HIDE|REMOVE)[:\s]+(MA|EMA|RSI|MACD|VOLUME|BOLLINGER)/i,
    zoom: /(?:ZOOM)[:\s]+(IN|OUT|\d+%?)/i,
    scroll: /(?:SCROLL|GO TO)[:\s]+(\d{4}-\d{2}-\d{2}|\w+)/i,
    style: /(?:STYLE|VIEW)[:\s]+(CANDLES?|LINE|AREA|BARS?)/i
  };

  /**
   * Register callbacks for chart control events
   */
  registerCallbacks(callbacks: ChartControlCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Set the chart reference for direct control
   */
  setChartRef(chart: any) {
    this.chartRef = chart;
  }

  /**
   * Parse agent response for chart commands
   */
  parseAgentResponse(response: string): ChartCommand[] {
    const commands: ChartCommand[] = [];
    
    // Check for symbol changes
    const symbolMatch = response.match(this.commandPatterns.symbol);
    if (symbolMatch) {
      commands.push({
        type: 'symbol',
        value: symbolMatch[1].toUpperCase(),
        timestamp: Date.now()
      });
    }

    // Check for timeframe changes
    const timeframeMatch = response.match(this.commandPatterns.timeframe);
    if (timeframeMatch) {
      commands.push({
        type: 'timeframe',
        value: timeframeMatch[1],
        timestamp: Date.now()
      });
    }

    // Check for indicator toggles
    const indicatorMatch = response.match(this.commandPatterns.indicator);
    if (indicatorMatch) {
      const action = indicatorMatch[0].split(/[:\s]+/)[0].toUpperCase();
      const enabled = action === 'ADD' || action === 'SHOW';
      commands.push({
        type: 'indicator',
        value: { name: indicatorMatch[1], enabled },
        timestamp: Date.now()
      });
    }

    // Check for zoom commands
    const zoomMatch = response.match(this.commandPatterns.zoom);
    if (zoomMatch) {
      let zoomValue = 0;
      if (zoomMatch[1] === 'IN') zoomValue = 1.2;
      else if (zoomMatch[1] === 'OUT') zoomValue = 0.8;
      else zoomValue = parseFloat(zoomMatch[1]) / 100;
      
      commands.push({
        type: 'zoom',
        value: zoomValue,
        timestamp: Date.now()
      });
    }

    // Check for scroll commands
    const scrollMatch = response.match(this.commandPatterns.scroll);
    if (scrollMatch) {
      commands.push({
        type: 'scroll',
        value: scrollMatch[1],
        timestamp: Date.now()
      });
    }

    // Check for style changes
    const styleMatch = response.match(this.commandPatterns.style);
    if (styleMatch) {
      const styleMap: { [key: string]: 'candles' | 'line' | 'area' } = {
        'CANDLE': 'candles',
        'CANDLES': 'candles',
        'LINE': 'line',
        'AREA': 'area',
        'BAR': 'candles',
        'BARS': 'candles'
      };
      
      commands.push({
        type: 'style',
        value: styleMap[styleMatch[1].toUpperCase()] || 'candles',
        timestamp: Date.now()
      });
    }

    return commands;
  }

  /**
   * Execute a chart command
   */
  executeCommand(command: ChartCommand): boolean {
    let message = '';
    let success = false;
    
    try {
      switch (command.type) {
        case 'symbol':
          if (this.callbacks.onSymbolChange) {
            this.currentSymbol = command.value;
            this.callbacks.onSymbolChange(command.value);
            message = `Switched to ${command.value}`;
            success = true;
          } else {
            message = 'Symbol change not available';
          }
          break;
          
        case 'timeframe':
          if (this.callbacks.onTimeframeChange) {
            this.callbacks.onTimeframeChange(command.value);
            message = `Timeframe: ${command.value}`;
            success = true;
          } else {
            message = 'Timeframe change not available';
          }
          break;
          
        case 'indicator':
          if (this.callbacks.onIndicatorToggle) {
            this.callbacks.onIndicatorToggle(
              command.value.name,
              command.value.enabled
            );
            message = `${command.value.enabled ? 'Added' : 'Removed'} ${command.value.name}`;
            success = true;
          } else {
            message = 'Indicator toggle not available';
          }
          break;
          
        case 'zoom':
          if (this.callbacks.onZoomChange && this.chartRef) {
            const timeScale = this.chartRef.timeScale();
            if (command.value > 1) {
              timeScale.zoomIn();
              message = 'Zoomed in';
            } else {
              timeScale.zoomOut();
              message = 'Zoomed out';
            }
            success = true;
          } else {
            message = 'Zoom control not available';
          }
          break;
          
        case 'scroll':
          if (this.callbacks.onScrollToTime && this.chartRef) {
            // Parse date or relative time
            let targetTime: number;
            if (command.value.match(/\d{4}-\d{2}-\d{2}/)) {
              targetTime = new Date(command.value).getTime() / 1000;
              message = `Scrolled to ${command.value}`;
            } else {
              // Handle relative times like "yesterday", "last week"
              const now = new Date();
              switch (command.value.toLowerCase()) {
                case 'yesterday':
                  targetTime = (now.getTime() - 86400000) / 1000;
                  message = 'Scrolled to yesterday';
                  break;
                case 'last week':
                  targetTime = (now.getTime() - 604800000) / 1000;
                  message = 'Scrolled to last week';
                  break;
                case 'last month':
                  targetTime = (now.getTime() - 2592000000) / 1000;
                  message = 'Scrolled to last month';
                  break;
                default:
                  targetTime = now.getTime() / 1000;
                  message = 'Scrolled to current time';
              }
            }
            
            this.chartRef.timeScale().scrollToPosition(targetTime, false);
            success = true;
          } else {
            message = 'Scroll control not available';
          }
          break;
          
        case 'style':
          if (this.callbacks.onStyleChange) {
            this.callbacks.onStyleChange(command.value);
            const styleNames = {
              'candles': 'Candlestick',
              'line': 'Line',
              'area': 'Area'
            };
            message = `Style: ${styleNames[command.value] || command.value}`;
            success = true;
          } else {
            message = 'Style change not available';
          }
          break;
          
        default:
          message = `Unknown command: ${command.type}`;
      }
      
      // Trigger callback with result
      if (this.callbacks.onCommandExecuted) {
        this.callbacks.onCommandExecuted(command, success, message);
      }
      
      console.log(`Chart Command: ${message} (${success ? 'Success' : 'Failed'})`);
      
    } catch (error: any) {
      const errorMsg = `Error: ${error.message || 'Command failed'}`;
      console.error('Error executing chart command:', error);
      
      if (this.callbacks.onCommandError) {
        this.callbacks.onCommandError(errorMsg);
      }
      
      if (this.callbacks.onCommandExecuted) {
        this.callbacks.onCommandExecuted(command, false, errorMsg);
      }
      
      return false;
    }
    
    return success;
  }

  /**
   * Process agent response and execute any chart commands
   */
  processAgentResponse(response: string): ChartCommand[] {
    const commands = this.parseAgentResponse(response);
    const executedCommands: ChartCommand[] = [];
    
    for (const command of commands) {
      if (this.executeCommand(command)) {
        executedCommands.push(command);
      }
    }
    
    return executedCommands;
  }

  /**
   * Get current chart state
   */
  getChartState() {
    return {
      symbol: this.currentSymbol,
      hasChart: !!this.chartRef
    };
  }

  /**
   * Helper to format command for agent prompt
   */
  static formatCommandExample(type: string, value: string): string {
    switch (type) {
      case 'symbol':
        return `CHART:${value}`;
      case 'timeframe':
        return `TIMEFRAME:${value}`;
      case 'indicator':
        return `ADD:${value}`;
      case 'zoom':
        return `ZOOM:${value}`;
      case 'scroll':
        return `SCROLL:${value}`;
      case 'style':
        return `STYLE:${value}`;
      default:
        return '';
    }
  }
}

// Export singleton instance
export const chartControlService = new ChartControlService();

// Export types and class for testing
export { ChartControlService };