import axios from 'axios';
import { 
  ApiResponse, 
  DashboardData, 
  ChartData, 
  TechnicalOverview, 
  RelatedNews, 
  StrategicInsights 
} from '../types/dashboard';
import getApiUrl, { getWebSocketUrl } from '../utils/apiConfig';

// Make API_URL dynamic to handle Computer Use Docker access
const BASE = '/api/v1';

type ApiGlobal = typeof globalThis & {
  getApiUrl?: () => string;
  __API_URL__?: string;
};

type ApiWindow = Window & {
  getApiUrl?: () => string;
  __API_URL__?: string;
};

const DEFAULT_FALLBACK_URL = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';

function resolveApiUrl(): string {
  const globalScope = globalThis as ApiGlobal;
  const candidates: Array<string | (() => string) | undefined> = [];

  if (typeof window !== 'undefined') {
    const win = window as ApiWindow;
    candidates.push(win.__API_URL__);
    if (typeof win.getApiUrl === 'function') {
      candidates.push(win.getApiUrl);
    }
  }

  candidates.push(globalScope.__API_URL__);
  if (typeof globalScope.getApiUrl === 'function') {
    candidates.push(globalScope.getApiUrl);
  }

  candidates.push(getApiUrl);

  for (const candidate of candidates) {
    if (!candidate) continue;
    try {
      if (typeof candidate === 'string' && candidate.length > 0) {
        return candidate;
      }
      if (typeof candidate === 'function') {
        const value = candidate();
        if (typeof value === 'string' && value.length > 0) {
          return value;
        }
      }
    } catch (error) {
      console.warn('API URL resolver failed; continuing to next candidate', error);
    }
  }

  return DEFAULT_FALLBACK_URL;
}

const resolveWebSocketUrl = (): string => {
  try {
    return getWebSocketUrl();
  } catch (error) {
    console.warn('Falling back to default WebSocket URL', error);
    const httpUrl = resolveApiUrl();
    return httpUrl.replace(/^http/, 'ws');
  }
};

export interface StockPrice {
  symbol: string;
  company_name?: string;
  price: number;
  change: number;
  change_percent: number;
  previous_close?: number;
  open?: number;
  day_low?: number;
  day_high?: number;
  year_low?: number;
  year_high?: number;
  volume?: number;
  avg_volume?: number;
  market_cap?: number;
  pe_ratio?: number;
  eps?: number;
  dividend_yield?: number;
  beta?: number;
  timestamp: string;
  source?: string;
}

export interface StockCandle {
  date: string;
  time: number; // Unix timestamp for TradingChart compatibility
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockHistory {
  symbol: string;
  candles: StockCandle[];
  period: string;
}

export interface StockNews {
  title: string;
  link?: string;
  source?: string;
  published?: string;
  summary?: string;
  tickers?: string[];
}

export interface AnalystRating {
  firm?: string;
  rating?: string;
  price_target?: number;
  date?: string;
}

export interface MarketOverview {
  indices: {
    sp500: { value: number; change: number; change_percent: number };
    nasdaq: { value: number; change: number; change_percent: number };
    dow: { value: number; change: number; change_percent: number };
  };
  top_gainers: Array<{ symbol: string; change_percent: number }>;
  top_losers: Array<{ symbol: string; change_percent: number }>;
  timestamp: string;
}

export interface TechnicalLevels {
  sell_high_level?: number;      // Sell High
  buy_low_level?: number; // Buy Low
  btd_level?: number;     // Buy The Dip
  retest_level?: number;  // Retest
}

export interface SwingTradeLevels extends TechnicalLevels {
  entry_points?: number[];     // Swing trade entry levels
  stop_loss?: number;          // Stop loss level
  targets?: number[];          // Take profit targets
  risk_reward?: number;        // Risk/reward ratio
  support_levels?: number[];   // Support levels
  resistance_levels?: number[]; // Resistance levels
}

export interface SymbolSearchResult {
  symbol: string;
  name: string;
  exchange: string;
  asset_class: string;
  tradable: boolean;
  status: string;
}

export interface SymbolSearchResponse {
  query: string;
  results: SymbolSearchResult[];
  total: number;
  data_source: string;
}

class MarketDataService {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private cacheTimeout = 10000; // 10 seconds cache

  private getCached<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data as T;
    }
    return null;
  }

  private setCache(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  async getStockPrice(symbol: string): Promise<StockPrice> {
    const cacheKey = `price-${symbol}`;
    const cached = this.getCached<StockPrice>(cacheKey);
    if (cached) return cached;

    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/stock-price`, {
        params: { symbol }
      });
      this.setCache(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching stock price for ${symbol}:`, error);
      // Throw error to surface backend issues during testing
      throw new Error(`Failed to fetch stock price for ${symbol}: ${error}`);
    }
  }

  async getMultipleStockPrices(symbols: string[]): Promise<StockPrice[]> {
    const promises = symbols.map(symbol => this.getStockPrice(symbol));
    return Promise.all(promises);
  }

  async getStockHistory(symbol: string, days: number = 50): Promise<StockHistory> {
    const cacheKey = `history-${symbol}-${days}`;
    const cached = this.getCached<StockHistory>(cacheKey);
    if (cached) return cached;

    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/stock-history`, {
        params: { symbol, days }
      });
      this.setCache(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching stock history for ${symbol}:`, error);
      throw error;
    }
  }

  async getComprehensiveData(symbol: string): Promise<any> {
    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/comprehensive-stock-data`, {
        params: { symbol }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching comprehensive data for ${symbol}:`, error);
      throw error;
    }
  }

  async getStockNews(symbol: string): Promise<StockNews[]> {
    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/stock-news`, {
        params: { symbol }
      });
      const payload = response.data ?? {};
      const articles =
        payload.articles ||
        payload.items ||
        payload.news ||
        []; // accommodate legacy formats

      return Array.isArray(articles) ? articles : [];
    } catch (error) {
      console.error(`Error fetching news for ${symbol}:`, error);
      throw error;
    }
  }

  async getAnalystRatings(symbol: string): Promise<AnalystRating[]> {
    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/analyst-ratings`, {
        params: { symbol }
      });
      return response.data.ratings || [];
    } catch (error) {
      console.error(`Error fetching analyst ratings for ${symbol}:`, error);
      return [];
    }
  }

  async getMarketOverview(): Promise<MarketOverview> {
    const cacheKey = 'market-overview';
    const cached = this.getCached<MarketOverview>(cacheKey);
    if (cached) return cached;

    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/market-overview`);
      const data = response.data;
      
      // Map movers to top_gainers/top_losers if needed
      if (data.movers && !data.top_gainers) {
        data.top_gainers = data.movers.gainers || [];
        data.top_losers = data.movers.losers || [];
      }
      
      this.setCache(cacheKey, data);
      return data;
    } catch (error) {
      console.error('Error fetching market overview:', error);
      throw error;
    }
  }

  async searchSymbols(query: string, limit: number = 20): Promise<SymbolSearchResponse> {
    const cacheKey = `search-${query}-${limit}`;
    const cached = this.getCached<SymbolSearchResponse>(cacheKey);
    if (cached) {
      return cached;
    }

    const apiUrl = resolveApiUrl();
    const response = await axios.get(`${apiUrl}/api/symbol-search`, {
      params: { query, limit },
      timeout: 5000
    });

    this.setCache(cacheKey, response.data);
    return response.data;
  }

  async getMarketMovers(): Promise<any> {
    try {
      const apiUrl = resolveApiUrl();
      const response = await axios.get(`${apiUrl}/api/market-movers`);
      return response.data;
    } catch (error) {
      console.error('Error fetching market movers:', error);
      return { trending: [] };
    }
  }

  // Calculate technical levels based on price data
  calculateTechnicalLevels(candles: StockCandle[]): TechnicalLevels {
    if (!candles || candles.length === 0) {
      return {};
    }

    const prices = candles.map(c => c.close);
    const highs = candles.map(c => c.high);
    const lows = candles.map(c => c.low);
    
    // Use 20-day period for technical levels
    const recentHigh = Math.max(...highs.slice(-20));
    const recentLow = Math.min(...lows.slice(-20));
    
    // Quick Entry: 2% below recent high (buy on pullback)
    const qe_level = recentHigh * 0.98;
    
    // Swing Trade: Mid-point of recent range
    const st_level = (recentHigh + recentLow) / 2;
    
    // Load The Boat: Near recent low with small buffer
    const ltb_level = recentLow * 1.02;

    return {
      qe_level: Math.round(qe_level * 100) / 100,
      st_level: Math.round(st_level * 100) / 100,
      ltb_level: Math.round(ltb_level * 100) / 100
    };
  }

  // Determine which level badge to show
  getLevelBadge(price: number, levels: TechnicalLevels): 'QE' | 'ST' | 'LTB' | null {
    if (!levels) return null;
    
    const { qe_level, st_level, ltb_level } = levels;
    
    // Find closest level
    const distances = [
      { level: 'QE' as const, distance: Math.abs(price - (qe_level || 0)) },
      { level: 'ST' as const, distance: Math.abs(price - (st_level || 0)) },
      { level: 'LTB' as const, distance: Math.abs(price - (ltb_level || 0)) }
    ];
    
    const closest = distances.reduce((min, curr) => 
      curr.distance < min.distance ? curr : min
    );
    
    // Only show badge if price is within 5% of level
    if (closest.distance / price < 0.05) {
      return closest.level;
    }
    
    return null;
  }

  // Clear cache
  clearCache(): void {
    this.cache.clear();
  }
}

// New dashboard API functions
export const getDashboard = async (symbol: string, range: TimeRange = '1D'): Promise<ApiResponse<DashboardData>> => {
  const apiUrl = resolveApiUrl();
  const res = await axios.get(`${apiUrl}${BASE}/dashboard`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getChart = async (symbol: string, range: TimeRange): Promise<ApiResponse<ChartData>> => {
  const apiUrl = resolveApiUrl();
  const res = await axios.get(`${apiUrl}${BASE}/chart`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getTechnical = async (symbol: string, range: TimeRange): Promise<ApiResponse<TechnicalOverview>> => {
  const apiUrl = resolveApiUrl();
  const res = await axios.get(`${apiUrl}${BASE}/technical`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getNews = async (symbol: string, limit = 6): Promise<ApiResponse<RelatedNews>> => {
  const apiUrl = resolveApiUrl();
  const res = await axios.get(`${apiUrl}${BASE}/news`, {
    params: { symbol, limit }
  });
  return res.data;
};

export const getStrategicInsights = async (symbol: string, horizonDays = 30): Promise<ApiResponse<StrategicInsights>> => {
  const apiUrl = resolveApiUrl();
  const res = await axios.get(`${apiUrl}${BASE}/options/strategic-insights`, {
    params: { symbol, horizon_days: horizonDays }
  });
  return res.data;
};

export const subscribeQuotes = (symbol: string, onMessage: (msg: any) => void): WebSocket => {
  const wsBase = resolveWebSocketUrl();
  const wsUrl = `${wsBase}${BASE}/ws/quotes?symbol=${encodeURIComponent(symbol)}`;
  const ws = new WebSocket(wsUrl);
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'quote') {
      onMessage(data);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  return ws;
};

export const marketDataService = new MarketDataService();
