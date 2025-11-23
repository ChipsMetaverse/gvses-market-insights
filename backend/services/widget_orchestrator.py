"""
Widget Orchestration Service

Intelligently classifies user queries and determines which market analysis
widgets to display based on intent.
"""

import re
from typing import List, Dict, Set, Optional
from enum import Enum
from dataclasses import dataclass


class WidgetType(Enum):
    """Available widget types for market analysis"""
    ECONOMIC_CALENDAR = "economic-calendar"
    MARKET_NEWS = "market-news-feed"
    PATTERN_DETECTION = "pattern-detection"
    TECHNICAL_LEVELS = "technical-levels"
    TRADING_CHART = "trading-chart-display"


class QueryIntent(Enum):
    """User query intent categories"""
    NEWS = "news"
    ECONOMIC_EVENTS = "economic_events"
    PATTERNS = "patterns"
    TECHNICAL_LEVELS = "technical_levels"
    CHART = "chart"
    COMPREHENSIVE = "comprehensive"
    UNKNOWN = "unknown"


@dataclass
class WidgetOrchestrationResult:
    """Result of widget orchestration"""
    symbol: str
    intent: QueryIntent
    widgets: List[WidgetType]
    confidence: float
    reasoning: str


class WidgetOrchestrator:
    """
    Orchestrates widget display based on user query analysis.

    Examples:
        >>> orchestrator = WidgetOrchestrator()
        >>> result = orchestrator.classify_query("What's the news on TSLA?")
        >>> print(result.widgets)
        [WidgetType.MARKET_NEWS]

        >>> result = orchestrator.classify_query("Show me AAPL chart with support levels")
        >>> print(result.widgets)
        [WidgetType.TRADING_CHART, WidgetType.TECHNICAL_LEVELS]
    """

    # Stock symbol patterns
    SYMBOL_PATTERN = r'\b([A-Z]{1,5})\b'

    # Common stock symbols (for validation)
    COMMON_SYMBOLS = {
        'TSLA', 'AAPL', 'NVDA', 'SPY', 'MSFT', 'GOOGL', 'AMZN', 'META',
        'NFLX', 'AMD', 'INTC', 'QQQ', 'DIA', 'IWM', 'PLTR', 'BTC', 'ETH'
    }

    # Intent keyword mappings
    INTENT_KEYWORDS = {
        QueryIntent.ECONOMIC_EVENTS: [
            'nfp', 'non-farm', 'cpi', 'inflation', 'fed', 'fomc',
            'economic calendar', 'forex calendar', 'economic event',
            'gdp', 'unemployment', 'interest rate', 'central bank',
            'powell', 'yellen', 'lagarde'
        ],
        QueryIntent.NEWS: [
            'news', 'headline', 'article', 'breaking', 'latest',
            'announcement', 'press release', 'earnings', 'report'
        ],
        QueryIntent.PATTERNS: [
            'pattern', 'head and shoulders', 'bull flag', 'bear flag',
            'triangle', 'double top', 'double bottom', 'reversal',
            'continuation', 'wedge', 'pennant'
        ],
        QueryIntent.TECHNICAL_LEVELS: [
            'support', 'resistance', 'buy low', 'sell high',
            'technical level', 'price level', 'btd', 'buy the dip',
            'fibonacci', 'pivot'
        ],
        QueryIntent.CHART: [
            'chart', 'price', 'candle', 'timeframe', '1d', '5d',
            'technical indicator', 'sma', 'ema', 'rsi', 'macd',
            'volume', 'bollinger'
        ],
        QueryIntent.COMPREHENSIVE: [
            'full analysis', 'complete analysis', 'everything',
            'all data', 'comprehensive', 'full picture', 'deep dive'
        ]
    }

    # Widget mapping for each intent
    INTENT_WIDGET_MAP = {
        QueryIntent.ECONOMIC_EVENTS: [WidgetType.ECONOMIC_CALENDAR],
        QueryIntent.NEWS: [WidgetType.MARKET_NEWS],
        QueryIntent.PATTERNS: [WidgetType.PATTERN_DETECTION, WidgetType.TRADING_CHART],
        QueryIntent.TECHNICAL_LEVELS: [WidgetType.TECHNICAL_LEVELS, WidgetType.TRADING_CHART],
        QueryIntent.CHART: [WidgetType.TRADING_CHART],
        QueryIntent.COMPREHENSIVE: [
            WidgetType.TRADING_CHART,
            WidgetType.TECHNICAL_LEVELS,
            WidgetType.PATTERN_DETECTION,
            WidgetType.MARKET_NEWS,
            WidgetType.ECONOMIC_CALENDAR
        ],
        QueryIntent.UNKNOWN: [WidgetType.TRADING_CHART]  # Default
    }

    def __init__(self, default_symbol: str = "TSLA"):
        self.default_symbol = default_symbol

    def extract_symbol(self, query: str) -> str:
        """
        Extract stock symbol from query.

        Args:
            query: User query text

        Returns:
            Extracted symbol or default

        Examples:
            >>> orchestrator = WidgetOrchestrator()
            >>> orchestrator.extract_symbol("Show me AAPL chart")
            'AAPL'
            >>> orchestrator.extract_symbol("What's the news?")
            'TSLA'
        """
        # Find all potential symbols (2-5 uppercase letters)
        matches = re.findall(self.SYMBOL_PATTERN, query)

        # Filter to likely stock symbols
        for match in matches:
            # Check if it's a common symbol
            if match in self.COMMON_SYMBOLS:
                return match

            # Check if it looks like a ticker (not a common word)
            if len(match) <= 5 and match not in {'I', 'A', 'AM', 'IS', 'IT', 'ME'}:
                return match

        return self.default_symbol

    def classify_intent(self, query: str) -> tuple[QueryIntent, float]:
        """
        Classify the intent of the user query.

        Args:
            query: User query text

        Returns:
            Tuple of (intent, confidence_score)

        Examples:
            >>> orchestrator = WidgetOrchestrator()
            >>> intent, conf = orchestrator.classify_intent("What's the news on TSLA?")
            >>> print(intent)
            QueryIntent.NEWS
            >>> print(conf > 0.8)
            True
        """
        query_lower = query.lower()
        scores: Dict[QueryIntent, float] = {intent: 0.0 for intent in QueryIntent}

        # Score each intent based on keyword matches
        for intent, keywords in self.INTENT_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > 0:
                # Higher score for more matches, normalized by keyword count
                scores[intent] = matches / len(keywords)

        # Find highest scoring intent
        if max(scores.values()) > 0:
            best_intent = max(scores.items(), key=lambda x: x[1])
            return best_intent[0], min(best_intent[1] * 2, 1.0)  # Scale confidence

        return QueryIntent.UNKNOWN, 0.5

    def get_widgets_for_intent(self, intent: QueryIntent) -> List[WidgetType]:
        """
        Get widgets to display for a given intent.

        Args:
            intent: Classified query intent

        Returns:
            List of widgets to display
        """
        return self.INTENT_WIDGET_MAP.get(intent, [WidgetType.TRADING_CHART])

    def classify_query(self, query: str) -> WidgetOrchestrationResult:
        """
        Main orchestration function: analyze query and determine widgets to show.

        Args:
            query: User query text

        Returns:
            WidgetOrchestrationResult with symbol, intent, widgets, and confidence

        Examples:
            >>> orchestrator = WidgetOrchestrator()
            >>> result = orchestrator.classify_query("Show me AAPL chart")
            >>> print(result.symbol)
            'AAPL'
            >>> print(result.intent)
            QueryIntent.CHART
            >>> print(len(result.widgets))
            1
        """
        # Extract symbol
        symbol = self.extract_symbol(query)

        # Classify intent
        intent, confidence = self.classify_intent(query)

        # Get widgets for intent
        widgets = self.get_widgets_for_intent(intent)

        # Generate reasoning
        reasoning = self._generate_reasoning(query, symbol, intent, widgets)

        return WidgetOrchestrationResult(
            symbol=symbol,
            intent=intent,
            widgets=widgets,
            confidence=confidence,
            reasoning=reasoning
        )

    def _generate_reasoning(
        self,
        query: str,
        symbol: str,
        intent: QueryIntent,
        widgets: List[WidgetType]
    ) -> str:
        """Generate human-readable reasoning for widget selection"""
        widget_names = [w.value for w in widgets]

        if intent == QueryIntent.NEWS:
            return f"User wants news about {symbol}. Showing Market News Feed."
        elif intent == QueryIntent.ECONOMIC_EVENTS:
            return "User wants economic calendar data. Showing Economic Calendar."
        elif intent == QueryIntent.PATTERNS:
            return f"User wants pattern analysis for {symbol}. Showing Pattern Detection with chart context."
        elif intent == QueryIntent.TECHNICAL_LEVELS:
            return f"User wants technical levels for {symbol}. Showing Technical Levels with chart."
        elif intent == QueryIntent.CHART:
            return f"User wants to see {symbol} chart. Showing Trading Chart."
        elif intent == QueryIntent.COMPREHENSIVE:
            return f"User wants comprehensive analysis of {symbol}. Showing all 5 widgets."
        else:
            return f"Showing default chart view for {symbol}."


# Test the orchestrator
if __name__ == "__main__":
    orchestrator = WidgetOrchestrator()

    test_queries = [
        "What's the news on TSLA?",
        "Show me AAPL chart",
        "Are there any head and shoulders patterns on NVDA?",
        "What are the support levels for SPY?",
        "When is the next NFP?",
        "Give me everything on MSFT"
    ]

    print("Widget Orchestration Test Results")
    print("=" * 80)

    for query in test_queries:
        result = orchestrator.classify_query(query)
        print(f"\nQuery: {query}")
        print(f"Symbol: {result.symbol}")
        print(f"Intent: {result.intent.value}")
        print(f"Confidence: {result.confidence:.2f}")
        print(f"Widgets: {[w.value for w in result.widgets]}")
        print(f"Reasoning: {result.reasoning}")
        print("-" * 80)
