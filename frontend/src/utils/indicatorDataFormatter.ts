/**
 * IndicatorDataFormatter - Utility for converting API indicator data to Lightweight Charts format
 * Handles data normalization, alignment, and type conversions for all technical indicators
 */

import { Time } from 'lightweight-charts';

// Lightweight Charts data point format
export interface ChartDataPoint {
  time: Time;  // Unix timestamp in seconds
  value: number;
}

export interface OHLCDataPoint {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface IndicatorApiResponse {
  symbol: string;
  timestamp: number;
  current_price: number;
  indicators: {
    moving_averages?: {
      ma20?: Array<{ time: number; value: number }>;
      ma50?: Array<{ time: number; value: number }>;
      ma200?: Array<{ time: number; value: number }>;
    };
    bollinger?: {
      upper: Array<{ time: number; value: number }>;
      middle: Array<{ time: number; value: number }>;
      lower: Array<{ time: number; value: number }>;
    };
    rsi?: {
      values: Array<{ time: number; value: number }>;
      current: number;
      overbought: number;
      oversold: number;
      signal: string;
    };
    macd?: {
      macd_line: Array<{ time: number; value: number }>;
      signal_line: Array<{ time: number; value: number }>;
      histogram: Array<{ time: number; value: number }>;
    };
    fibonacci?: {
      fib_0: number;
      fib_236: number;
      fib_382: number;
      fib_500: number;
      fib_618: number;
      fib_786: number;
      fib_1000: number;
      swing_high: number;
      swing_low: number;
    };
    support_resistance?: {
      support_levels: number[];
      resistance_levels: number[];
    };
  };
  data_source: string;
  calculation_period: number;
}

export class IndicatorDataFormatter {
  /**
   * Convert API time series data to Lightweight Charts format
   * Ensures timestamps are in seconds and sorted chronologically
   */
  static formatTimeSeries(
    data: Array<{ time: number; value: number }> | undefined,
    type: 'line' | 'histogram' | 'area' = 'line'
  ): ChartDataPoint[] {
    if (!data || !Array.isArray(data)) {
      return [];
    }

    return data
      .map(point => ({
        time: this.normalizeTimestamp(point.time) as Time,
        value: parseFloat(point.value?.toString() || '0')
      }))
      .sort((a, b) => (a.time as number) - (b.time as number));
  }

  /**
   * Normalize timestamp to seconds (Lightweight Charts requirement)
   * Handles both milliseconds and seconds input
   */
  private static normalizeTimestamp(timestamp: number): number {
    // If timestamp is likely in milliseconds (> year 2100 in seconds)
    if (timestamp > 4102444800) {
      return Math.floor(timestamp / 1000);
    }
    return Math.floor(timestamp);
  }

  /**
   * Format moving averages data for chart rendering
   */
  static formatMovingAverages(maData: IndicatorApiResponse['indicators']['moving_averages']) {
    if (!maData) return {};

    return {
      ma20: maData.ma20 ? this.formatTimeSeries(maData.ma20, 'line') : [],
      ma50: maData.ma50 ? this.formatTimeSeries(maData.ma50, 'line') : [],
      ma200: maData.ma200 ? this.formatTimeSeries(maData.ma200, 'line') : []
    };
  }

  /**
   * Format Bollinger Bands data
   */
  static formatBollingerBands(bbData: IndicatorApiResponse['indicators']['bollinger']) {
    if (!bbData) return null;

    return {
      upper: this.formatTimeSeries(bbData.upper, 'line'),
      middle: this.formatTimeSeries(bbData.middle, 'line'),
      lower: this.formatTimeSeries(bbData.lower, 'line')
    };
  }

  /**
   * Format RSI data for oscillator chart
   */
  static formatRSI(rsiData: IndicatorApiResponse['indicators']['rsi']) {
    if (!rsiData) return null;

    return {
      values: this.formatTimeSeries(rsiData.values, 'line'),
      current: rsiData.current,
      overbought: rsiData.overbought || 70,
      oversold: rsiData.oversold || 30,
      signal: rsiData.signal
    };
  }

  /**
   * Format MACD data for histogram and line series
   */
  static formatMACD(macdData: IndicatorApiResponse['indicators']['macd']) {
    if (!macdData) return null;

    return {
      macdLine: this.formatTimeSeries(macdData.macd_line, 'line'),
      signalLine: this.formatTimeSeries(macdData.signal_line, 'line'),
      histogram: this.formatTimeSeries(macdData.histogram, 'histogram')
    };
  }

  /**
   * Format Fibonacci levels for price lines
   */
  static formatFibonacciLevels(fibData: IndicatorApiResponse['indicators']['fibonacci']) {
    if (!fibData) return [];

    const levels = [
      { level: 0, value: fibData.fib_0, label: '0%' },
      { level: 0.236, value: fibData.fib_236, label: '23.6%' },
      { level: 0.382, value: fibData.fib_382, label: '38.2%' },
      { level: 0.5, value: fibData.fib_500, label: '50%' },
      { level: 0.618, value: fibData.fib_618, label: '61.8%' },
      { level: 0.786, value: fibData.fib_786, label: '78.6%' },
      { level: 1, value: fibData.fib_1000, label: '100%' }
    ];

    return levels.map(({ level, value, label }) => ({
      price: value,
      color: this.getFibonacciColor(level),
      lineWidth: 1,
      lineStyle: 2, // Dashed
      title: `Fib ${label}`,
      axisLabelVisible: true
    }));
  }

  /**
   * Get color for Fibonacci level
   */
  private static getFibonacciColor(level: number): string {
    const colors = {
      0: 'rgba(255, 82, 82, 0.8)',      // Red
      0.236: 'rgba(255, 152, 0, 0.7)',   // Orange
      0.382: 'rgba(255, 193, 7, 0.7)',   // Amber
      0.5: 'rgba(76, 175, 80, 0.7)',     // Green
      0.618: 'rgba(33, 150, 243, 0.7)',  // Blue
      0.786: 'rgba(103, 58, 183, 0.7)',  // Purple
      1: 'rgba(96, 125, 139, 0.8)'       // Blue Grey
    };
    return colors[level as keyof typeof colors] || 'rgba(128, 128, 128, 0.5)';
  }

  /**
   * Format support and resistance levels
   */
  static formatSupportResistance(srData: IndicatorApiResponse['indicators']['support_resistance']) {
    if (!srData) return { support: [], resistance: [] };

    const formatLevels = (levels: number[], type: 'support' | 'resistance') => {
      return levels.map((price, index) => ({
        price,
        color: type === 'support' ? 'rgba(76, 175, 80, 0.5)' : 'rgba(244, 67, 54, 0.5)',
        lineWidth: 1,
        lineStyle: 1, // Solid
        title: `${type === 'support' ? 'S' : 'R'}${index + 1}`,
        axisLabelVisible: true
      }));
    };

    return {
      support: formatLevels(srData.support_levels || [], 'support'),
      resistance: formatLevels(srData.resistance_levels || [], 'resistance')
    };
  }

  /**
   * Align multiple time series to the same time axis
   * Useful for combining indicators on the same chart
   */
  static alignTimeSeries(series: Record<string, ChartDataPoint[]>): Record<string, ChartDataPoint[]> {
    // Get all unique timestamps
    const allTimes = new Set<number>();
    Object.values(series).forEach(s => {
      s.forEach(point => allTimes.add(point.time as number));
    });

    // Sort timestamps
    const sortedTimes = Array.from(allTimes).sort((a, b) => a - b);

    // Align each series to have the same timestamps
    const aligned: Record<string, ChartDataPoint[]> = {};
    
    Object.entries(series).forEach(([key, data]) => {
      const dataMap = new Map(data.map(p => [p.time as number, p.value]));
      
      aligned[key] = sortedTimes.map(time => {
        const value = dataMap.get(time);
        if (value !== undefined) {
          return { time: time as Time, value };
        }
        // Interpolate missing values (simple forward fill)
        const prevTime = sortedTimes[sortedTimes.indexOf(time) - 1];
        const prevValue = prevTime ? dataMap.get(prevTime) : undefined;
        return { time: time as Time, value: prevValue || 0 };
      });
    });

    return aligned;
  }

  /**
   * Format complete indicator response for chart consumption
   */
  static formatIndicatorResponse(response: IndicatorApiResponse) {
    return {
      symbol: response.symbol,
      currentPrice: response.current_price,
      timestamp: response.timestamp,
      dataSource: response.data_source,
      period: response.calculation_period,
      indicators: {
        movingAverages: this.formatMovingAverages(response.indicators.moving_averages),
        bollingerBands: this.formatBollingerBands(response.indicators.bollinger),
        rsi: this.formatRSI(response.indicators.rsi),
        macd: this.formatMACD(response.indicators.macd),
        fibonacci: this.formatFibonacciLevels(response.indicators.fibonacci),
        supportResistance: this.formatSupportResistance(response.indicators.support_resistance)
      }
    };
  }

  /**
   * Check if data needs refresh based on TTL
   */
  static isDataStale(timestamp: number, ttlSeconds: number = 30): boolean {
    const now = Date.now() / 1000;
    const dataAge = now - timestamp;
    return dataAge > ttlSeconds;
  }
}