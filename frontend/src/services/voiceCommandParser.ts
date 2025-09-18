/**
 * Voice Command Parser Service
 * Parses voice commands for chart and application control
 */

export interface VoiceCommand {
  type: 'chart' | 'symbol' | 'period' | 'news' | 'unknown';
  action: string;
  params?: any;
}

export class VoiceCommandParser {
  private static instance: VoiceCommandParser;

  // Command patterns for different actions
  private commandPatterns = {
    // Symbol commands
    symbol: [
      /show\s+(?:me\s+)?(\w+)/i,
      /switch\s+to\s+(\w+)/i,
      /change\s+to\s+(\w+)/i,
      /display\s+(\w+)/i,
      /look\s+at\s+(\w+)/i,
      /pull\s+up\s+(\w+)/i,
    ],
    
    // Period/timeframe commands
    period: [
      /show\s+(?:me\s+)?(?:the\s+)?last\s+(\d+)\s+days?/i,
      /show\s+(?:me\s+)?(?:the\s+)?past\s+(\d+)\s+days?/i,
      /(?:one|1)\s+week/i,
      /(?:one|1)\s+month/i,
      /(?:three|3)\s+months?/i,
      /(?:six|6)\s+months?/i,
      /(?:one|1)\s+year/i,
      /year\s+to\s+date/i,
      /ytd/i,
    ],
    
    // Chart control commands
    chart: [
      /zoom\s+in/i,
      /zoom\s+out/i,
      /reset\s+(?:the\s+)?chart/i,
      /show\s+volume/i,
      /hide\s+volume/i,
      /add\s+moving\s+average/i,
      /remove\s+moving\s+average/i,
      /show\s+indicators/i,
      /hide\s+indicators/i,
      /candlestick/i,
      /line\s+chart/i,
      /area\s+chart/i,
    ],
    
    // News commands
    news: [
      /show\s+(?:me\s+)?(?:the\s+)?news/i,
      /what'?s?\s+(?:the\s+)?news/i,
      /latest\s+news/i,
      /hide\s+news/i,
      /close\s+news/i,
    ],
  };

  // Stock symbol aliases
  private symbolAliases: { [key: string]: string } = {
    'tesla': 'TSLA',
    'apple': 'AAPL',
    'nvidia': 'NVDA',
    'amazon': 'AMZN',
    'google': 'GOOGL',
    'microsoft': 'MSFT',
    'meta': 'META',
    'facebook': 'META',
    'spy': 'SPY',
    'nasdaq': 'QQQ',
    'palantir': 'PLTR',
    'coinbase': 'COIN',
    'bitcoin': 'BTC-USD',
  };

  private constructor() {}

  static getInstance(): VoiceCommandParser {
    if (!VoiceCommandParser.instance) {
      VoiceCommandParser.instance = new VoiceCommandParser();
    }
    return VoiceCommandParser.instance;
  }

  /**
   * Parse a voice command string into a structured command
   */
  parseCommand(text: string): VoiceCommand {
    const normalizedText = text.toLowerCase().trim();
    
    // Check for symbol commands
    for (const pattern of this.commandPatterns.symbol) {
      const match = normalizedText.match(pattern);
      if (match) {
        const symbolOrName = match[1].toUpperCase();
        const symbol = this.resolveSymbol(symbolOrName);
        return {
          type: 'symbol',
          action: 'change',
          params: { symbol }
        };
      }
    }
    
    // Check for period commands
    if (normalizedText.includes('week')) {
      return { type: 'period', action: 'change', params: { days: 7, label: '1W' } };
    }
    if (normalizedText.includes('month') && !normalizedText.includes('months')) {
      return { type: 'period', action: 'change', params: { days: 30, label: '1M' } };
    }
    if (normalizedText.includes('3 month') || normalizedText.includes('three month')) {
      return { type: 'period', action: 'change', params: { days: 90, label: '3M' } };
    }
    if (normalizedText.includes('6 month') || normalizedText.includes('six month')) {
      return { type: 'period', action: 'change', params: { days: 180, label: '6M' } };
    }
    if (normalizedText.includes('year') && !normalizedText.includes('year to date')) {
      return { type: 'period', action: 'change', params: { days: 365, label: '1Y' } };
    }
    if (normalizedText.includes('year to date') || normalizedText.includes('ytd')) {
      const days = Math.floor((Date.now() - new Date(new Date().getFullYear(), 0, 1).getTime()) / (1000 * 60 * 60 * 24));
      return { type: 'period', action: 'change', params: { days, label: 'YTD' } };
    }
    
    // Check for specific day count
    const dayMatch = normalizedText.match(/(\d+)\s+days?/);
    if (dayMatch) {
      const days = parseInt(dayMatch[1]);
      return { type: 'period', action: 'change', params: { days, label: `${days}D` } };
    }
    
    // Check for chart commands
    if (normalizedText.includes('zoom in')) {
      return { type: 'chart', action: 'zoom_in' };
    }
    if (normalizedText.includes('zoom out')) {
      return { type: 'chart', action: 'zoom_out' };
    }
    if (normalizedText.includes('reset') && normalizedText.includes('chart')) {
      return { type: 'chart', action: 'reset' };
    }
    if (normalizedText.includes('candlestick')) {
      return { type: 'chart', action: 'style', params: { style: 'candles' } };
    }
    if (normalizedText.includes('line chart')) {
      return { type: 'chart', action: 'style', params: { style: 'line' } };
    }
    if (normalizedText.includes('area chart')) {
      return { type: 'chart', action: 'style', params: { style: 'area' } };
    }
    
    // Check for news commands
    if (normalizedText.includes('news') && normalizedText.includes('show')) {
      return { type: 'news', action: 'show' };
    }
    if (normalizedText.includes('news') && (normalizedText.includes('hide') || normalizedText.includes('close'))) {
      return { type: 'news', action: 'hide' };
    }
    
    // Unknown command
    return { type: 'unknown', action: 'unknown' };
  }

  /**
   * Resolve a symbol name or alias to a stock ticker
   */
  private resolveSymbol(input: string): string {
    const lower = input.toLowerCase();
    
    // Check if it's an alias
    if (this.symbolAliases[lower]) {
      return this.symbolAliases[lower];
    }
    
    // Otherwise return as uppercase (assume it's already a ticker)
    return input.toUpperCase();
  }

  /**
   * Get suggested commands based on partial input
   */
  getSuggestions(partialText: string): string[] {
    const suggestions: string[] = [];
    const lower = partialText.toLowerCase();
    
    // Suggest common commands
    const commonCommands = [
      'Show me Tesla',
      'Switch to Apple',
      'Show last 30 days',
      'Show one month',
      'Show year to date',
      'Zoom in',
      'Zoom out',
      'Show news',
      'Line chart',
      'Candlestick chart',
    ];
    
    return commonCommands.filter(cmd => 
      cmd.toLowerCase().includes(lower) || lower.includes(cmd.toLowerCase())
    );
  }
}

export const voiceCommandParser = VoiceCommandParser.getInstance();