"""
Tests for Model Router Service
================================
Tests for intelligent model selection and fallback chains.

Phase 2: Model Routing & Prompt Optimization - Router Tests
"""

import pytest
from services.model_router import (
    ModelRouter,
    QueryIntent,
    ModelTier,
    get_model_router
)


class TestIntentClassification:
    """Test query intent classification."""

    def test_price_only_intent(self):
        """Test classification of simple price queries."""
        router = ModelRouter()

        # Basic price queries
        assert router.classify_intent("What's the price of TSLA?") == QueryIntent.PRICE_ONLY
        assert router.classify_intent("Get me AAPL stock price") == QueryIntent.PRICE_ONLY
        assert router.classify_intent("How much is NVDA?") == QueryIntent.PRICE_ONLY
        assert router.classify_intent("price for MSFT") == QueryIntent.PRICE_ONLY

    def test_technical_analysis_intent(self):
        """Test classification of technical analysis queries."""
        router = ModelRouter()

        queries = [
            "Analyze NVDA with RSI and MACD",
            "What are the support and resistance levels for TSLA?",
            "Show me Bollinger Bands",
            "Is AAPL oversold?",
            "Technical analysis of MSFT"
        ]

        for query in queries:
            assert router.classify_intent(query) == QueryIntent.TECHNICAL_ANALYSIS

    def test_news_summary_intent(self):
        """Test classification of news queries."""
        router = ModelRouter()

        queries = [
            "Latest news about Tesla",
            "AAPL headlines today",
            "What are the announcements for NVDA?",
            "Show me recent articles about Microsoft"
        ]

        for query in queries:
            assert router.classify_intent(query) == QueryIntent.NEWS_SUMMARY

    def test_market_overview_intent(self):
        """Test classification of market overview queries."""
        router = ModelRouter()

        queries = [
            "How are the markets doing?",
            "What's happening with the S&P 500?",
            "Market overview",
            "Nasdaq performance today"
        ]

        for query in queries:
            assert router.classify_intent(query) == QueryIntent.MARKET_OVERVIEW

    def test_chart_command_intent(self):
        """Test classification of chart commands."""
        router = ModelRouter()

        commands = [
            "LOAD:TSLA",
            "TIMEFRAME:1H",
            "INDICATOR:RSI",
            "DRAW:SUPPORT:420"
        ]

        for command in commands:
            assert router.classify_intent(command) == QueryIntent.CHART_COMMAND

    def test_general_query_intent(self):
        """Test classification of strategic queries."""
        router = ModelRouter()

        queries = [
            "Should I buy PLTR?",
            "What's a good entry point for NVDA?",
            "Investment strategy for tech stocks",
            "TSLA outlook for next quarter"
        ]

        for query in queries:
            assert router.classify_intent(query) == QueryIntent.GENERAL_QUERY

    def test_tool_based_classification(self):
        """Test intent classification using tool information."""
        router = ModelRouter()

        # Price only based on tools
        assert router.classify_intent(
            "Get stock info",
            tools_requested=["get_stock_quote"]
        ) == QueryIntent.PRICE_ONLY

        # Technical analysis based on tools
        assert router.classify_intent(
            "Analyze stock",
            tools_requested=["get_technical_indicators", "get_support_resistance"]
        ) == QueryIntent.TECHNICAL_ANALYSIS

        # News based on tools
        assert router.classify_intent(
            "Latest updates",
            tools_requested=["get_market_news"]
        ) == QueryIntent.NEWS_SUMMARY


class TestModelSelection:
    """Test model selection logic."""

    def test_price_only_uses_cheap_model(self):
        """Price queries should use cheapest model."""
        router = ModelRouter()

        model = router.select_model("What's TSLA price?", intent=QueryIntent.PRICE_ONLY)

        assert model.name == "gpt-4o-mini"
        assert model.tier == ModelTier.CHEAP

    def test_technical_analysis_uses_mid_model(self):
        """Technical analysis should use balanced model."""
        router = ModelRouter()

        model = router.select_model(
            "Analyze NVDA with RSI",
            intent=QueryIntent.TECHNICAL_ANALYSIS
        )

        assert model.name == "gpt-4o"
        assert model.tier == ModelTier.MID

    def test_general_query_uses_mid_model(self):
        """General queries should use capable model."""
        router = ModelRouter()

        model = router.select_model(
            "Should I buy PLTR?",
            intent=QueryIntent.GENERAL_QUERY
        )

        assert model.name == "gpt-4o"
        assert model.tier == ModelTier.MID

    def test_intent_auto_classification(self):
        """Model selection should auto-classify intent."""
        router = ModelRouter()

        # Should classify as PRICE_ONLY and select gpt-4o-mini
        model = router.select_model("What's the price of AAPL?")
        assert model.name == "gpt-4o-mini"

        # Should classify as TECHNICAL_ANALYSIS and select gpt-4o
        model = router.select_model("Analyze TSLA with RSI and MACD")
        assert model.name == "gpt-4o"


class TestFallbackChains:
    """Test fallback chain logic."""

    def test_cheap_tier_fallback_chain(self):
        """Test fallback chain for cheap tier models."""
        router = ModelRouter()

        # Primary model
        model = router.select_model("Price of TSLA?", fallback_index=0)
        assert model.name == "gpt-4o-mini"

        # First fallback
        model = router.select_model("Price of TSLA?", fallback_index=1)
        assert model.name == "gpt-4o"

        # Second fallback
        model = router.select_model("Price of TSLA?", fallback_index=2)
        assert model.name == "gpt-5"

    def test_mid_tier_fallback_chain(self):
        """Test fallback chain for mid tier models."""
        router = ModelRouter()

        # Primary model
        model = router.select_model("Analyze NVDA", fallback_index=0)
        assert model.name == "gpt-4o"

        # First fallback
        model = router.select_model("Analyze NVDA", fallback_index=1)
        assert model.name == "gpt-5"

        # Second fallback
        model = router.select_model("Analyze NVDA", fallback_index=2)
        assert model.name == "gpt-4o-mini"

    def test_fallback_index_out_of_range(self):
        """Fallback index beyond chain length should use primary."""
        router = ModelRouter()

        model = router.select_model("Price of TSLA?", fallback_index=99)
        assert model.name == "gpt-4o-mini"  # Should use primary

    def test_get_fallback_chain(self):
        """Test getting fallback chain for a model."""
        router = ModelRouter()

        chain = router.get_fallback_chain("gpt-4o-mini")
        assert chain == ["gpt-4o-mini", "gpt-4o", "gpt-5"]

        chain = router.get_fallback_chain("gpt-4o")
        assert chain == ["gpt-4o", "gpt-5", "gpt-4o-mini"]


class TestPolicyManagement:
    """Test routing policy management."""

    def test_update_routing_policy(self):
        """Test updating routing policy for an intent."""
        router = ModelRouter()

        # Update policy
        router.update_routing_policy(QueryIntent.PRICE_ONLY, "gpt-4o")

        # Verify update
        model = router.select_model("Price of TSLA?", intent=QueryIntent.PRICE_ONLY)
        assert model.name == "gpt-4o"

    def test_update_policy_invalid_model(self):
        """Updating policy with invalid model should be ignored."""
        router = ModelRouter()

        original_model = router.routing_policy[QueryIntent.PRICE_ONLY]

        # Try to update with invalid model
        router.update_routing_policy(QueryIntent.PRICE_ONLY, "invalid-model")

        # Should remain unchanged
        assert router.routing_policy[QueryIntent.PRICE_ONLY] == original_model

    def test_get_routing_summary(self):
        """Test getting routing policy summary."""
        router = ModelRouter()

        summary = router.get_routing_summary()

        # Verify all intents are present
        assert QueryIntent.PRICE_ONLY.value in summary
        assert QueryIntent.TECHNICAL_ANALYSIS.value in summary
        assert QueryIntent.GENERAL_QUERY.value in summary

        # Verify values are model names
        assert summary[QueryIntent.PRICE_ONLY.value] == "gpt-4o-mini"


class TestSingletonRouter:
    """Test singleton router instance."""

    def test_get_model_router_singleton(self):
        """get_model_router should return same instance."""
        router1 = get_model_router()
        router2 = get_model_router()

        assert router1 is router2

    def test_singleton_maintains_state(self):
        """Singleton should maintain state across calls."""
        router = get_model_router()
        router.update_routing_policy(QueryIntent.PRICE_ONLY, "gpt-4o")

        # Get router again
        router2 = get_model_router()
        model = router2.select_model("Price?", intent=QueryIntent.PRICE_ONLY)

        # Should reflect earlier update
        assert model.name == "gpt-4o"


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query(self):
        """Empty query should classify as UNKNOWN or GENERAL_QUERY."""
        router = ModelRouter()

        intent = router.classify_intent("")
        assert intent in [QueryIntent.UNKNOWN, QueryIntent.GENERAL_QUERY]

    def test_mixed_signals_query(self):
        """Query with mixed signals should prioritize appropriately."""
        router = ModelRouter()

        # Has both "price" and "analyze" - should be technical analysis
        intent = router.classify_intent("What's the price and analyze TSLA with RSI?")
        assert intent == QueryIntent.TECHNICAL_ANALYSIS

    def test_model_config_completeness(self):
        """All models in routing policy should have configs."""
        router = ModelRouter()

        for intent, model_name in router.routing_policy.items():
            model = router.select_model("test", intent=intent)
            assert model is not None
            assert model.name is not None
            assert model.tier is not None
