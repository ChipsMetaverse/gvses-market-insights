export type TimeRange =
  | '1m' | '5m' | '15m'
  | '1H'
  | '1D' | '1W' | '1M'
  | 'YTD' | '1Y' | 'MAX';
export type CandleInterval = '1m' | '5m' | '15m' | '1h' | '1d' | '1w';

export interface ApiResponse<T> {
  status: 'ok' | 'error';
  data: T;
  meta: {
    symbol: string;
    requested_range: TimeRange;
    server_time: string; // ISO
    timezone: string;    // "UTC"
    version: string;     // "1.0.0"
  };
  error?: {
    code: string;
    message: string;
  };
}

export interface Candle {
  time: number; // unix seconds UTC
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

export interface VolumeBar {
  time: number;
  value: number;
}

export interface IndicatorPoint {
  time: number;
  value: number;
}

export interface PriceHeader {
  symbol: string;
  company_name: string;
  exchange: string;
  currency: string;
  last_price: number;
  change_abs: number;
  change_pct: number;
  is_market_open: boolean;
  as_of: string;
  last_price_formatted: string;
  change_abs_formatted: string;
  change_pct_formatted: string;
}

export interface MarketSnapshot {
  open_price: number;
  day_high: number;
  day_low: number;
  prev_close: number;
  volume: number;
  avg_volume_3m?: number;
  market_cap?: number;
  pe_ttm?: number;
  dividend_yield_pct?: number;
  beta?: number;
  week52_high?: number;
  week52_low?: number;
  volume_formatted?: string;
  avg_volume_3m_formatted?: string;
  market_cap_formatted?: string;
  pe_ttm_formatted?: string;
  dividend_yield_pct_formatted?: string;
  week52_range_formatted?: string;
}

export interface ChartData {
  range: TimeRange;
  interval: CandleInterval;
  timezone: string;
  candles: Candle[];
  volume_bars?: VolumeBar[];
  price_min?: number;
  price_max?: number;
}

export interface BollingerBandsSeries {
  upper: IndicatorPoint[];
  middle: IndicatorPoint[];
  lower: IndicatorPoint[];
  period: number;
  stddev: number;
}

export interface MACDSeries {
  macd_line: IndicatorPoint[];
  signal_line: IndicatorPoint[];
  histogram: IndicatorPoint[];
  fast_period: number;
  slow_period: number;
  signal_period: number;
  last_macd?: number;
  last_signal?: number;
  last_histogram?: number;
}

export interface FibonacciLevel {
  level: number;
  price: number;
}

export interface FibonacciLevels {
  high_anchor_time: number;
  low_anchor_time: number;
  levels: FibonacciLevel[];
}

export type TechnicalRating = 'Bullish' | 'Neutral' | 'Bearish';

export interface TechnicalOverview {
  rating: TechnicalRating;
  rating_score: number; // -1..1
  macd?: MACDSeries;
  bollinger_bands?: BollingerBandsSeries;
  fibonacci?: FibonacciLevels;
  notes?: string[];
}

export interface SummaryTableItem {
  key: string;
  label: string;
  value_raw?: number;
  value_formatted: string;
  delta_pct?: number;
  delta_formatted?: string;
  tooltip?: string;
}

export interface SummaryTable {
  rows: SummaryTableItem[];
}

export type OptionRight = 'CALL' | 'PUT';
export type OptionAction = 'BUY' | 'SELL';

export interface OptionLeg {
  right: OptionRight;
  action: OptionAction;
  strike: number;
  expiry: string; // YYYY-MM-DD
  quantity: number;
}

export type StrategyCode =
  | 'covered_call'
  | 'protective_put'
  | 'long_call'
  | 'long_put'
  | 'bull_call_spread'
  | 'bear_put_spread'
  | 'iron_condor'
  | 'iron_butterfly'
  | 'straddle'
  | 'strangle'
  | 'calendar_call'
  | 'calendar_put'
  | 'diagonal_call'
  | 'diagonal_put'
  | 'collar'
  | 'risk_reversal'
  | 'butterfly_call'
  | 'butterfly_put';

export interface StrategyInsight {
  strategy_code: StrategyCode;
  title: string;
  rationale: string;
  recommended_legs: OptionLeg[];
  net_debit_credit: number;
  max_profit?: number;
  max_profit_text?: string;
  max_loss?: number;
  max_loss_text?: string;
  breakevens?: number[];
  probability_of_profit_pct?: number;
  greeks_delta?: number;
  greeks_gamma?: number;
  greeks_theta?: number;
  greeks_vega?: number;
  greeks_rho?: number;
  time_horizon_days?: number;
  tags?: string[];
}

export interface StrategicInsights {
  iv_rank?: number;
  iv_percentile?: number;
  skew_25d?: number;
  spot_price: number;
  items: StrategyInsight[];
}

export interface NewsItem {
  id: string;
  title: string;
  source: string;
  published_at: string; // ISO
  url: string;
  image_url: string;
  description?: string;
  tickers?: string[];
}

export interface RelatedNews {
  items: NewsItem[];
}

export interface DashboardData {
  price_header: PriceHeader;
  market_snapshot: MarketSnapshot;
  chart: ChartData;
  technical_overview: TechnicalOverview;
  summary_table: SummaryTable;
  strategic_insights: StrategicInsights;
  related_news: RelatedNews;
}