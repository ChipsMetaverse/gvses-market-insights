from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ---------- Enums ----------

class TimeRange(str, Enum):
    D1 = "1D"
    D5 = "5D"
    M1 = "1M"
    M6 = "6M"
    YTD = "YTD"
    Y1 = "1Y"
    Y5 = "5Y"
    MAX = "MAX"


class CandleInterval(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    D1 = "1d"
    W1 = "1w"


class OptionRight(str, Enum):
    CALL = "CALL"
    PUT = "PUT"


class OptionAction(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class StrategyCode(str, Enum):
    COVERED_CALL = "covered_call"
    PROTECTIVE_PUT = "protective_put"
    LONG_CALL = "long_call"
    LONG_PUT = "long_put"
    BULL_CALL_SPREAD = "bull_call_spread"
    BEAR_PUT_SPREAD = "bear_put_spread"
    IRON_CONDOR = "iron_condor"
    IRON_BUTTERFLY = "iron_butterfly"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    CALENDAR_CALL = "calendar_call"
    CALENDAR_PUT = "calendar_put"
    DIAGONAL_CALL = "diagonal_call"
    DIAGONAL_PUT = "diagonal_put"
    COLLAR = "collar"
    RISK_REVERSAL = "risk_reversal"
    BUTTERFLY_CALL = "butterfly_call"
    BUTTERFLY_PUT = "butterfly_put"


# ---------- Core common models ----------

class ResponseMeta(BaseModel):
    symbol: str
    requested_range: TimeRange
    server_time: datetime
    timezone: str = "UTC"
    version: str = "1.0.0"


class ErrorDetail(BaseModel):
    code: str
    message: str


class Candle(BaseModel):
    time: int  # unix epoch seconds UTC
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = None


class VolumeBar(BaseModel):
    time: int  # unix epoch seconds UTC
    value: int


class IndicatorPoint(BaseModel):
    time: int
    value: float


# ---------- Dashboard sections ----------

class PriceHeader(BaseModel):
    symbol: str
    company_name: str
    exchange: str
    currency: str = "USD"
    last_price: float
    change_abs: float
    change_pct: float  # percentage, e.g., -1.23 for -1.23%
    is_market_open: bool
    as_of: datetime
    # Preformatted strings for immediate rendering
    last_price_formatted: str
    change_abs_formatted: str
    change_pct_formatted: str


class MarketSnapshot(BaseModel):
    open_price: float
    day_high: float
    day_low: float
    prev_close: float
    volume: int
    avg_volume_3m: Optional[int] = None
    market_cap: Optional[float] = None
    pe_ttm: Optional[float] = None
    dividend_yield_pct: Optional[float] = None
    beta: Optional[float] = None
    week52_high: Optional[float] = None
    week52_low: Optional[float] = None
    # Preformatted values
    volume_formatted: Optional[str] = None
    avg_volume_3m_formatted: Optional[str] = None
    market_cap_formatted: Optional[str] = None
    pe_ttm_formatted: Optional[str] = None
    dividend_yield_pct_formatted: Optional[str] = None
    week52_range_formatted: Optional[str] = None  # e.g. "125.12 - 242.34"


class ChartData(BaseModel):
    range: TimeRange
    interval: CandleInterval
    timezone: str = "UTC"
    candles: List[Candle]
    volume_bars: Optional[List[VolumeBar]] = None  # if not using volume in Candle
    # Optional precomputed extents for chart
    price_min: Optional[float] = None
    price_max: Optional[float] = None


class BollingerBandsSeries(BaseModel):
    upper: List[IndicatorPoint]
    middle: List[IndicatorPoint]
    lower: List[IndicatorPoint]
    period: int = 20
    stddev: float = 2.0


class MACDSeries(BaseModel):
    macd_line: List[IndicatorPoint]
    signal_line: List[IndicatorPoint]
    histogram: List[IndicatorPoint]
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    last_macd: Optional[float] = None
    last_signal: Optional[float] = None
    last_histogram: Optional[float] = None


class FibonacciLevel(BaseModel):
    level: float  # 0.236, 0.382, 0.5, 0.618, etc.
    price: float


class FibonacciLevels(BaseModel):
    high_anchor_time: int
    low_anchor_time: int
    levels: List[FibonacciLevel]


class TechnicalOverview(BaseModel):
    rating: Literal["Bullish", "Neutral", "Bearish"]
    rating_score: float = Field(..., description="Normalized score -1..1, where >0 bullish")
    macd: Optional[MACDSeries] = None
    bollinger_bands: Optional[BollingerBandsSeries] = None
    fibonacci: Optional[FibonacciLevels] = None
    notes: Optional[List[str]] = None  # e.g., "Price above middle band", "MACD > Signal"


class SummaryTableItem(BaseModel):
    key: str  # stable key for UI test hooks
    label: str
    value_raw: Optional[float] = None
    value_formatted: str
    delta_pct: Optional[float] = None
    delta_formatted: Optional[str] = None
    tooltip: Optional[str] = None


class SummaryTable(BaseModel):
    rows: List[SummaryTableItem]


class OptionLeg(BaseModel):
    right: OptionRight
    action: OptionAction
    strike: float
    expiry: date  # YYYY-MM-DD
    quantity: int


class StrategyInsight(BaseModel):
    strategy_code: StrategyCode
    title: str
    rationale: str
    recommended_legs: List[OptionLeg]
    net_debit_credit: float  # positive for debit, negative for credit
    max_profit: Optional[float] = None
    max_profit_text: Optional[str] = None  # e.g., "Unlimited"
    max_loss: Optional[float] = None
    max_loss_text: Optional[str] = None
    breakevens: Optional[List[float]] = None
    probability_of_profit_pct: Optional[float] = None
    greeks_delta: Optional[float] = None
    greeks_gamma: Optional[float] = None
    greeks_theta: Optional[float] = None
    greeks_vega: Optional[float] = None
    greeks_rho: Optional[float] = None
    time_horizon_days: Optional[int] = None
    tags: Optional[List[str]] = None  # ["income", "directional-bullish"]


class StrategicInsights(BaseModel):
    iv_rank: Optional[float] = None
    iv_percentile: Optional[float] = None
    skew_25d: Optional[float] = None
    spot_price: float
    items: List[StrategyInsight]


class NewsItem(BaseModel):
    id: str
    title: str
    source: str
    published_at: datetime
    url: str
    image_url: str
    description: Optional[str] = None
    tickers: Optional[List[str]] = None


class RelatedNews(BaseModel):
    items: List[NewsItem]


class DashboardData(BaseModel):
    price_header: PriceHeader
    market_snapshot: MarketSnapshot
    chart: ChartData
    technical_overview: TechnicalOverview
    summary_table: SummaryTable
    strategic_insights: StrategicInsights
    related_news: RelatedNews