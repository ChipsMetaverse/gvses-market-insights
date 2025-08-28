// Export all types from dashboard
export * from './dashboard';

// Additional types used by components that were missing
export interface Insight {
  symbol: string;
  time: string;
  pattern: string;
  confidence: number;
  description: string;
  type: 'bullish' | 'bearish' | 'neutral';
}

// Market data types that might be needed
export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
  volume?: number;
  market_cap?: number;
  timestamp: string;
}

// Voice-related types
export interface VoiceMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

// Enhanced market insights props
export interface EnhancedMarketInsightsProps {
  marketData: MarketData[];
  currentSymbol: string;
  onSymbolChange: (symbol: string) => void;
  enableStreaming: boolean;
}