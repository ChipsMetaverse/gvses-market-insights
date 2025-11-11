"""
Benchmark Record Models
========================
Pydantic models for tracking model performance benchmarks.

Phase 2: Model Routing & Prompt Optimization - Benchmark Suite
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class IntentType(str, Enum):
    """Intent types for query classification."""
    PRICE_ONLY = "price_only"
    TECHNICAL_ANALYSIS = "technical_analysis"
    NEWS_SUMMARY = "news_summary"
    MARKET_OVERVIEW = "market_overview"
    GENERAL_QUERY = "general_query"
    CHART_COMMAND = "chart_command"


class ModelType(str, Enum):
    """OpenAI model types."""
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5 = "gpt-5"
    O1_MINI = "o1-mini"
    O1 = "o1"


class BenchmarkQuery(BaseModel):
    """Sample query for benchmarking."""
    intent: IntentType
    query: str
    expected_tools: List[str] = Field(default_factory=list)
    description: str


class BenchmarkMetrics(BaseModel):
    """Performance metrics for a single benchmark run."""
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0
    cost_usd: float
    success: bool
    error: Optional[str] = None
    tools_called: List[str] = Field(default_factory=list)


class ModelBenchmarkResult(BaseModel):
    """Benchmark results for a single model on a query."""
    model: ModelType
    intent: IntentType
    query: str
    timestamp: datetime
    metrics: BenchmarkMetrics

    # Quality assessment
    correct_tools: bool = False  # Did it call the right tools?
    response_quality: Optional[int] = None  # 1-5 rating

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BenchmarkSuite(BaseModel):
    """Collection of benchmark queries."""
    name: str
    description: str
    queries: List[BenchmarkQuery]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BenchmarkReport(BaseModel):
    """Aggregated benchmark report."""
    suite_name: str
    run_timestamp: datetime
    total_queries: int
    total_models_tested: int
    results: List[ModelBenchmarkResult]

    # Aggregated statistics by model
    model_stats: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Aggregated statistics by intent
    intent_stats: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Recommendations
    recommended_routing: Dict[str, str] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Sample benchmark queries
STANDARD_BENCHMARK_QUERIES = [
    BenchmarkQuery(
        intent=IntentType.PRICE_ONLY,
        query="What's the current price of TSLA?",
        expected_tools=["get_stock_quote"],
        description="Simple price lookup - should use cheapest model"
    ),
    BenchmarkQuery(
        intent=IntentType.PRICE_ONLY,
        query="Get me AAPL stock price",
        expected_tools=["get_stock_quote"],
        description="Basic price query"
    ),
    BenchmarkQuery(
        intent=IntentType.TECHNICAL_ANALYSIS,
        query="Analyze NVDA with RSI, MACD, and support/resistance levels",
        expected_tools=["get_technical_indicators", "get_support_resistance", "get_stock_history"],
        description="Complex technical analysis - needs reasoning"
    ),
    BenchmarkQuery(
        intent=IntentType.TECHNICAL_ANALYSIS,
        query="What are the key technical levels for MSFT?",
        expected_tools=["get_technical_indicators", "get_support_resistance"],
        description="Technical analysis query"
    ),
    BenchmarkQuery(
        intent=IntentType.NEWS_SUMMARY,
        query="Summarize the latest news about Tesla",
        expected_tools=["get_market_news"],
        description="News synthesis - medium complexity"
    ),
    BenchmarkQuery(
        intent=IntentType.MARKET_OVERVIEW,
        query="How are the markets doing today?",
        expected_tools=["get_market_overview", "get_market_movers"],
        description="Market overview - medium complexity"
    ),
    BenchmarkQuery(
        intent=IntentType.CHART_COMMAND,
        query="Show me TSLA with Bollinger Bands on 1-hour timeframe",
        expected_tools=[],  # Chart commands don't use tools
        description="Chart control - simple structured output"
    ),
    BenchmarkQuery(
        intent=IntentType.GENERAL_QUERY,
        query="What's a good entry point for buying PLTR?",
        expected_tools=["get_stock_quote", "get_technical_indicators", "get_analyst_ratings"],
        description="Strategic analysis - needs premium model"
    ),
]
