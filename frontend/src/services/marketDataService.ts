import axios from 'axios';
import { 
  ApiResponse, 
  DashboardData, 
  ChartData, 
  TechnicalOverview, 
  RelatedNews, 
  StrategicInsights, 
  TimeRange 
} from '../types/dashboard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const BASE = '/api/v1';

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
  qe_level?: number;  // Quick Entry
  st_level?: number;  // Swing Trade
  ltb_level?: number; // Load The Boat
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
      const response = await axios.get(`${API_URL}/api/stock-price`, {
        params: { symbol }
      });
      this.setCache(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching stock price for ${symbol}:`, error);
      // Return mock data as fallback
      return {
        symbol: symbol.toUpperCase(),
        price: 100 + Math.random() * 100,
        change: Math.random() * 10 - 5,
        change_percent: Math.random() * 4 - 2,
        timestamp: new Date().toISOString()
      };
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
      const response = await axios.get(`${API_URL}/api/stock-history`, {
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
      const response = await axios.get(`${API_URL}/api/comprehensive-stock-data`, {
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
      const response = await axios.get(`${API_URL}/api/stock-news`, {
        params: { symbol }
      });
      return response.data.news || [];
    } catch (error) {
      console.error(`Error fetching news for ${symbol}:`, error);
      return [];
    }
  }

  async getAnalystRatings(symbol: string): Promise<AnalystRating[]> {
    try {
      const response = await axios.get(`${API_URL}/api/analyst-ratings`, {
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
      const response = await axios.get(`${API_URL}/api/market-overview`);
      this.setCache(cacheKey, response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching market overview:', error);
      throw error;
    }
  }

  async getMarketMovers(): Promise<any> {
    try {
      const response = await axios.get(`${API_URL}/api/market-movers`);
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
  const res = await axios.get(`${API_URL}${BASE}/dashboard`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getChart = async (symbol: string, range: TimeRange): Promise<ApiResponse<ChartData>> => {
  const res = await axios.get(`${API_URL}${BASE}/chart`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getTechnical = async (symbol: string, range: TimeRange): Promise<ApiResponse<TechnicalOverview>> => {
  const res = await axios.get(`${API_URL}${BASE}/technical`, {
    params: { symbol, range }
  });
  return res.data;
};

export const getNews = async (symbol: string, limit = 6): Promise<ApiResponse<RelatedNews>> => {
  const res = await axios.get(`${API_URL}${BASE}/news`, {
    params: { symbol, limit }
  });
  return res.data;
};

export const getStrategicInsights = async (symbol: string, horizonDays = 30): Promise<ApiResponse<StrategicInsights>> => {
  const res = await axios.get(`${API_URL}${BASE}/options/strategic-insights`, {
    params: { symbol, horizon_days: horizonDays }
  });
  return res.data;
};

export const subscribeQuotes = (symbol: string, onMessage: (msg: any) => void): WebSocket => {
  const wsUrl = `${API_URL.replace('http', 'ws')}${BASE}/ws/quotes?symbol=${encodeURIComponent(symbol)}`;
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