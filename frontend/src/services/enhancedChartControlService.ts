/**
 * Enhanced Chart Control Service with improved voice navigation
 * Features:
 * - Multi-command parsing and execution
 * - Command history with undo/redo support
 * - Context-aware command processing
 * - Natural language understanding via GPT-5
 * - Improved error recovery and feedback
 */

import { marketDataService, SymbolSearchResult } from './marketDataService';
import { chartControlService, ChartCommand, ChartControlCallbacks } from './chartControlService';

export interface EnhancedChartCommand extends ChartCommand {
  rawText?: string;
  confidence?: number;
  context?: {
    previousSymbol?: string;
    previousTimeframe?: string;
    commandIndex?: number;
  };
}

export interface CommandHistory {
  commands: EnhancedChartCommand[];
  currentIndex: number;
  maxHistory: number;
}

export interface NLPParsedCommand {
  intent: string;
  entities: {
    symbol?: string;
    timeframe?: string;
    indicator?: string;
    action?: string;
    value?: any;
  };
  confidence: number;
  multiCommand?: NLPParsedCommand[];
}

class EnhancedChartControlService {
  private commandHistory: CommandHistory = {
    commands: [],
    currentIndex: -1,
    maxHistory: 50
  };
  
  private contextState = {
    currentSymbol: 'TSLA',
    currentTimeframe: '1D',
    previousSymbol: '',
    previousTimeframe: '',
    lastCommandTime: Date.now(),
    sessionCommands: 0
  };
  
  private callbacks: ChartControlCallbacks = {};
  private chartRef: any = null;
  
  // Natural language patterns for more flexible parsing
  private nlpPatterns = {
    // Multi-command patterns
    multiCommand: /\b(and|then|also|plus|with|while)\b/gi,
    
    // Relative commands
    relative: {
      previous: /(?:go |switch |return )?(?:back|previous|last|prior)/i,
      next: /(?:go |switch )?(?:forward|next)/i,
      more: /(?:zoom |scroll )?(?:more|further|deeper)/i,
      less: /(?:zoom |scroll )?(?:less|out|wider)/i
    },
    
    // Contextual commands
    contextual: {
      comparison: /compare (?:with|to|against) (\w+)/i,
      correlation: /correlate (?:with|to) (\w+)/i,
      overlay: /overlay (?:with)? (\w+)/i,
      split: /split (?:screen|view) (?:with)? (\w+)/i
    },
    
    // Time-based navigation
    temporal: {
      today: /today(?:'s)?|current day/i,
      yesterday: /yesterday(?:'s)?/i,
      thisWeek: /this week/i,
      lastWeek: /last week/i,
      thisMonth: /this month/i,
      lastMonth: /last month/i,
      thisYear: /this year|year to date|ytd/i,
      lastYear: /last year/i,
      earnings: /(?:last|next|recent) earnings/i,
      dividend: /(?:last|next) (?:dividend|ex-div)/i
    },
    
    // Advanced chart operations
    advanced: {
      fibonacci: /(?:add|show|draw) (?:fibonacci|fib)/i,
      trendline: /(?:add|draw) (?:trend ?line|support|resistance)/i,
      pattern: /(?:find|show|detect) (?:pattern|formation|setup)/i,
      alert: /(?:set|create) (?:alert|notification) (?:at|when) ([\d.]+)/i,
      annotation: /(?:add|place) (?:note|annotation|comment)/i
    }
  };

  constructor() {
    // Inherit base functionality from original service
    this.setupBaseCallbacks();
  }

  private setupBaseCallbacks() {
    // Register with the original chartControlService for backward compatibility
    chartControlService.registerCallbacks({
      onCommandExecuted: (cmd, success, msg) => {
        if (success) {
          this.addToHistory(cmd as EnhancedChartCommand);
        }
      }
    });
  }

  /**
   * Use GPT-5 for natural language understanding
   */
  private async parseWithGPT5(text: string): Promise<NLPParsedCommand[]> {
    try {
      // This would integrate with GPT-5 MCP server for better NLP
      const prompt = `Parse this trading command into structured format:
"${text}"

Extract:
- intent (symbol_change, timeframe_change, indicator_add, zoom, etc.)
- entities (symbol name, timeframe value, indicator type, etc.)
- confidence score (0-1)
- multiple commands if present

Current context:
- Current symbol: ${this.contextState.currentSymbol}
- Current timeframe: ${this.contextState.currentTimeframe}
- Previous symbol: ${this.contextState.previousSymbol}

Return as JSON.`;

      // For now, fall back to enhanced regex parsing
      return this.enhancedRegexParse(text);
    } catch (error) {
      console.error('GPT-5 parsing failed, using fallback:', error);
      return this.enhancedRegexParse(text);
    }
  }

  /**
   * Enhanced regex parsing with multi-command support
   */
  private enhancedRegexParse(text: string): NLPParsedCommand[] {
    const commands: NLPParsedCommand[] = [];
    
    // Split on multi-command indicators
    const segments = text.split(this.nlpPatterns.multiCommand);
    
    for (const segment of segments) {
      if (!segment || segment.length < 2) continue;
      
      // Check for relative commands
      if (this.nlpPatterns.relative.previous.test(segment)) {
        commands.push({
          intent: 'symbol_change',
          entities: { symbol: this.contextState.previousSymbol },
          confidence: 0.9
        });
      }
      
      // Check for temporal navigation
      for (const [key, pattern] of Object.entries(this.nlpPatterns.temporal)) {
        if (pattern.test(segment)) {
          commands.push({
            intent: 'temporal_navigation',
            entities: { action: key },
            confidence: 0.85
          });
        }
      }
      
      // Check for advanced operations
      for (const [key, pattern] of Object.entries(this.nlpPatterns.advanced)) {
        if (pattern.test(segment)) {
          commands.push({
            intent: 'advanced_operation',
            entities: { action: key },
            confidence: 0.8
          });
        }
      }
      
      // Fall back to original parsing for standard commands
      // This would integrate with the existing chartControlService patterns
    }
    
    return commands;
  }

  /**
   * Process voice response with enhanced capabilities
   */
  async processEnhancedResponse(response: string): Promise<EnhancedChartCommand[]> {
    console.log('[Enhanced] Processing voice response:', response);
    
    // Parse with enhanced NLP
    const nlpCommands = await this.parseWithGPT5(response);
    
    // Convert to enhanced chart commands
    const enhancedCommands: EnhancedChartCommand[] = [];
    
    for (const nlpCmd of nlpCommands) {
      const command = await this.nlpToChartCommand(nlpCmd);
      if (command) {
        command.rawText = response;
        command.confidence = nlpCmd.confidence;
        command.context = {
          previousSymbol: this.contextState.previousSymbol,
          previousTimeframe: this.contextState.previousTimeframe,
          commandIndex: enhancedCommands.length
        };
        enhancedCommands.push(command);
      }
    }
    
    // Execute commands in sequence
    for (const cmd of enhancedCommands) {
      await this.executeEnhancedCommand(cmd);
    }
    
    // Update session stats
    this.contextState.sessionCommands += enhancedCommands.length;
    this.contextState.lastCommandTime = Date.now();
    
    return enhancedCommands;
  }

  /**
   * Convert NLP parsed command to chart command
   */
  private async nlpToChartCommand(nlpCmd: NLPParsedCommand): Promise<EnhancedChartCommand | null> {
    switch (nlpCmd.intent) {
      case 'symbol_change':
        if (nlpCmd.entities.symbol) {
          // Try semantic search first
          const searchResult = await this.resolveSymbolSemantically(nlpCmd.entities.symbol);
          if (searchResult) {
            return {
              type: 'symbol',
              value: searchResult.symbol,
              metadata: {
                assetType: searchResult.type,
                companyName: searchResult.name
              },
              timestamp: Date.now()
            };
          }
        }
        break;
        
      case 'timeframe_change':
        if (nlpCmd.entities.timeframe) {
          return {
            type: 'timeframe',
            value: this.normalizeTimeframe(nlpCmd.entities.timeframe),
            timestamp: Date.now()
          };
        }
        break;
        
      case 'temporal_navigation':
        return this.handleTemporalNavigation(nlpCmd.entities.action || '');
        
      case 'advanced_operation':
        return this.handleAdvancedOperation(nlpCmd.entities.action || '');
        
      default:
        // Fall back to original service for standard commands
        const baseCommands = await chartControlService.parseAgentResponse(nlpCmd.entities.symbol || '');
        return baseCommands[0] as EnhancedChartCommand || null;
    }
    
    return null;
  }

  /**
   * Semantic symbol resolution with caching
   */
  private async resolveSymbolSemantically(query: string): Promise<{ symbol: string; type: 'stock' | 'crypto'; name?: string } | null> {
    // Cache check
    const cacheKey = `symbol_${query.toLowerCase()}`;
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
    
    try {
      // Use Alpaca search API
      const searchResponse = await marketDataService.searchSymbols(query, 5);
      
      if (searchResponse.results.length > 0) {
        const result = {
          symbol: searchResponse.results[0].symbol,
          type: 'stock' as const,
          name: searchResponse.results[0].name
        };
        
        // Cache the result
        sessionStorage.setItem(cacheKey, JSON.stringify(result));
        
        return result;
      }
    } catch (error) {
      console.error('Semantic symbol resolution failed:', error);
    }
    
    return null;
  }

  /**
   * Handle temporal navigation commands
   */
  private handleTemporalNavigation(action: string): EnhancedChartCommand {
    const now = new Date();
    let targetDate: Date;
    
    switch (action) {
      case 'today':
        targetDate = now;
        break;
      case 'yesterday':
        targetDate = new Date(now.getTime() - 86400000);
        break;
      case 'thisWeek':
        targetDate = new Date(now.getTime() - (now.getDay() * 86400000));
        break;
      case 'lastWeek':
        targetDate = new Date(now.getTime() - ((now.getDay() + 7) * 86400000));
        break;
      case 'thisMonth':
        targetDate = new Date(now.getFullYear(), now.getMonth(), 1);
        break;
      case 'lastMonth':
        targetDate = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        break;
      default:
        targetDate = now;
    }
    
    return {
      type: 'scroll',
      value: targetDate.toISOString().split('T')[0],
      timestamp: Date.now()
    };
  }

  /**
   * Handle advanced chart operations
   */
  private handleAdvancedOperation(action: string): EnhancedChartCommand | null {
    // These would be expanded with actual chart library integration
    switch (action) {
      case 'fibonacci':
        return {
          type: 'indicator',
          value: { name: 'FIBONACCI', enabled: true },
          timestamp: Date.now()
        };
        
      case 'trendline':
        // Would trigger trendline drawing mode
        console.log('Trendline drawing requested');
        return null;
        
      case 'pattern':
        // Would trigger pattern recognition
        console.log('Pattern detection requested');
        return null;
        
      default:
        return null;
    }
  }

  /**
   * Execute enhanced command with context tracking
   */
  private async executeEnhancedCommand(command: EnhancedChartCommand): Promise<boolean> {
    // Update context before execution
    if (command.type === 'symbol') {
      this.contextState.previousSymbol = this.contextState.currentSymbol;
      this.contextState.currentSymbol = command.value;
    } else if (command.type === 'timeframe') {
      this.contextState.previousTimeframe = this.contextState.currentTimeframe;
      this.contextState.currentTimeframe = command.value;
    }
    
    // Execute via base service
    const success = chartControlService.executeCommand(command);
    
    if (success) {
      this.addToHistory(command);
    }
    
    return success;
  }

  /**
   * Add command to history for undo/redo support
   */
  private addToHistory(command: EnhancedChartCommand) {
    // Remove any commands after current index (for redo consistency)
    this.commandHistory.commands = this.commandHistory.commands.slice(0, this.commandHistory.currentIndex + 1);
    
    // Add new command
    this.commandHistory.commands.push(command);
    this.commandHistory.currentIndex++;
    
    // Limit history size
    if (this.commandHistory.commands.length > this.commandHistory.maxHistory) {
      this.commandHistory.commands.shift();
      this.commandHistory.currentIndex--;
    }
  }

  /**
   * Undo last command
   */
  async undo(): Promise<boolean> {
    if (this.commandHistory.currentIndex > 0) {
      this.commandHistory.currentIndex--;
      const prevCommand = this.commandHistory.commands[this.commandHistory.currentIndex];
      
      // Restore previous state
      if (prevCommand.context?.previousSymbol) {
        await chartControlService.executeCommand({
          type: 'symbol',
          value: prevCommand.context.previousSymbol,
          timestamp: Date.now()
        });
      }
      
      return true;
    }
    return false;
  }

  /**
   * Redo command
   */
  async redo(): Promise<boolean> {
    if (this.commandHistory.currentIndex < this.commandHistory.commands.length - 1) {
      this.commandHistory.currentIndex++;
      const nextCommand = this.commandHistory.commands[this.commandHistory.currentIndex];
      
      return await this.executeEnhancedCommand(nextCommand);
    }
    return false;
  }

  /**
   * Get command history for display
   */
  getHistory(): EnhancedChartCommand[] {
    return this.commandHistory.commands.slice(0, this.commandHistory.currentIndex + 1);
  }

  /**
   * Get current context state
   */
  getContext() {
    return {
      ...this.contextState,
      historyLength: this.commandHistory.commands.length,
      canUndo: this.commandHistory.currentIndex > 0,
      canRedo: this.commandHistory.currentIndex < this.commandHistory.commands.length - 1
    };
  }

  /**
   * Normalize timeframe values
   */
  private normalizeTimeframe(timeframe: string): string {
    const tfMap: { [key: string]: string } = {
      'day': '1D',
      '1 day': '1D',
      'one day': '1D',
      'daily': '1D',
      '5 days': '5D',
      'five days': '5D',
      'week': '1W',
      '1 week': '1W',
      'one week': '1W',
      'weekly': '1W',
      'month': '1M',
      '1 month': '1M',
      'one month': '1M',
      'monthly': '1M',
      '3 months': '3M',
      'three months': '3M',
      'quarter': '3M',
      '6 months': '6M',
      'six months': '6M',
      'half year': '6M',
      'year': '1Y',
      '1 year': '1Y',
      'one year': '1Y',
      'yearly': '1Y',
      'annual': '1Y',
      'ytd': 'YTD',
      'year to date': 'YTD',
      'all': 'ALL',
      'all time': 'ALL',
      'max': 'ALL',
      'maximum': 'ALL',
      // Intraday hours
      '1h': 'H1',
      'one hour': 'H1',
      'hour': 'H1',
      '2h': 'H2',
      'two hours': 'H2',
      '3h': 'H3',
      'three hours': 'H3',
      '4h': 'H4',
      'four hours': 'H4',
      '6h': 'H6',
      'six hours': 'H6',
      '8h': 'H8',
      'eight hours': 'H8',
      // Intraday minutes
      '30m': 'M30',
      '30 min': 'M30',
      '30 minutes': 'M30',
      '15m': 'M15',
      '15 min': 'M15',
      '15 minutes': 'M15',
      '5m': 'M5',
      '5 min': 'M5',
      '5 minutes': 'M5',
      '1m': 'M1',
      '1 min': 'M1',
      'one minute': 'M1',
      // Seconds
      '10s': 'S10',
      '10 sec': 'S10',
      '10 seconds': 'S10'
    };
    
    const key = timeframe.trim().toLowerCase();
    const normalized = tfMap[key];
    // If looks like raw patterns (e.g., 4h/15m etc.), map programmatically
    if (!normalized) {
      const hMatch = key.match(/^(\d+)\s*h$/);
      const mMatch = key.match(/^(\d+)\s*m(in|inute|inutes)?$/);
      const sMatch = key.match(/^(\d+)\s*s(ec|econd|econds)?$/);
      if (hMatch) return `H${hMatch[1]}`;
      if (mMatch) return `M${mMatch[1]}`;
      if (sMatch) return `S${sMatch[1]}`;
    }
    return normalized || timeframe.toUpperCase();
  }

  /**
   * Register callbacks (pass through to base service)
   */
  registerCallbacks(callbacks: ChartControlCallbacks) {
    this.callbacks = { ...this.callbacks, ...callbacks };
    chartControlService.registerCallbacks(callbacks);
  }

  /**
   * Set chart reference (pass through to base service)
   */
  setChartRef(chart: any) {
    this.chartRef = chart;
    chartControlService.setChartRef(chart);
  }

  /**
   * Get suggestions based on partial input
   */
  async getSuggestions(partialInput: string): Promise<string[]> {
    const suggestions: string[] = [];
    
    // Symbol suggestions
    if (partialInput.length >= 2) {
      try {
        const searchResults = await marketDataService.searchSymbols(partialInput, 5);
        searchResults.results.forEach(result => {
          suggestions.push(`Show ${result.name} (${result.symbol})`);
        });
      } catch (error) {
        console.error('Failed to get symbol suggestions:', error);
      }
    }
    
    // Command suggestions
    const commandSuggestions = [
      'zoom in',
      'zoom out',
      'reset view',
      'add moving average',
      'show RSI',
      'switch to line chart',
      'go to last month',
      'compare with SPY',
      'show me Apple',
      'display Microsoft chart'
    ];
    
    commandSuggestions.forEach(cmd => {
      if (cmd.toLowerCase().includes(partialInput.toLowerCase())) {
        suggestions.push(cmd);
      }
    });
    
    return suggestions.slice(0, 10); // Limit to 10 suggestions
  }
}

// Export singleton instance
export const enhancedChartControl = new EnhancedChartControlService();

// Export types
export { EnhancedChartControlService };
