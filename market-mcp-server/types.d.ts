// Type definitions for Market MCP Server

export interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
  dayHigh: number;
  dayLow: number;
  yearHigh: number;
  yearLow: number;
  pe?: number;
  eps?: number;
  dividend?: number;
  dividendYield?: number;
  beta?: number;
  timestamp: string;
  preMarket?: {
    price: number;
    change: number;
    changePercent: number;
  };
  postMarket?: {
    price: number;
    change: number;
    changePercent: number;
  };
}

export interface CryptoPrice {
  id: string;
  price: number;
  marketCap: number;
  volume24h: number;
  change24h: number;
  lastUpdated: string;
}

export interface MarketOverview {
  indices: {
    sp500: MarketIndex;
    nasdaq: MarketIndex;
    dow: MarketIndex;
    vix: MarketIndex;
  };
  bonds: {
    '10year': number;
    '30year': number;
    '5year': number;
  };
  commodities: {
    gold: number;
    silver: number;
    oil: number;
    naturalGas: number;
  };
  timestamp: string;
}

export interface MarketIndex {
  value: number;
  change: number;
  changePercent: number;
}

export interface TechnicalIndicators {
  symbol: string;
  currentPrice: number;
  indicators: {
    rsi?: number;
    macd?: {
      macd: number;
      signal: number;
      histogram: number;
    };
    bollingerBands?: {
      upper: number;
      middle: number;
      lower: number;
    };
    sma?: {
      sma20: number;
      sma50: number;
      sma200: number;
    };
    ema?: {
      ema12: number;
      ema26: number;
    };
    stochastic?: {
      k: number;
      d: number;
    };
  };
  interpretation: string[];
  timestamp: string;
}

export interface NewsArticle {
  source: string;
  title: string;
  summary: string;
  url: string;
  timestamp: string;
}

export interface PortfolioHolding {
  symbol: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  totalValue: number;
  totalCost: number;
  gainLoss: number;
  gainLossPercent: number;
  dayChange: number;
  dayChangePercent: number;
}

export interface PriceAlert {
  symbol: string;
  targetPrice: number;
  condition: 'above' | 'below';
  created: string;
  triggered: boolean;
}

export interface StreamUpdate {
  timestamp: string;
  data: any;
}

export interface OptionsChain {
  symbol: string;
  expirationDates: string[];
  strikes: number[];
  calls: Option[];
  puts: Option[];
  timestamp: string;
}

export interface Option {
  strike: number;
  lastPrice: number;
  bid: number;
  ask: number;
  volume: number;
  openInterest: number;
  impliedVolatility: number;
  inTheMoney: boolean;
}

export interface FearGreedIndex {
  value: number;
  classification: string;
  timestamp: string;
  interpretation: string;
}

export interface SectorPerformance {
  sector: string;
  symbol: string;
  change: number;
  price: number;
  volume: number;
}

export interface EconomicEvent {
  date: string;
  event: string;
  importance: 'high' | 'medium' | 'low';
  forecast?: string;
  previous?: string;
}

export interface SupportResistance {
  symbol: string;
  currentPrice: number;
  support: number[];
  resistance: number[];
  pivotPoints: {
    pivot: number;
    r1: number;
    r2: number;
    s1: number;
    s2: number;
  };
  strength: {
    support?: string;
    resistance?: string;
  };
  timestamp: string;
}

export interface CorrelationMatrix {
  period: string;
  symbols: string[];
  correlationMatrix: { [key: string]: { [key: string]: number } };
  interpretation: string[];
  timestamp: string;
}

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, any>;
    required?: string[];
  };
}

export interface MCPResponse {
  content: Array<{
    type: 'text';
    text: string;
  }>;
}

export interface StreamConfig {
  duration: number;
  interval: number;
  symbols?: string[];
  ids?: string[];
  keywords?: string[];
}
