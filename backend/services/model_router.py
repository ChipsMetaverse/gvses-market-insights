"""
Model Router Service
====================
Intelligent model selection based on query intent with fallback chain.

Phase 2: Model Routing & Prompt Optimization - Routing Policy
Sprint 1, Day 2: Prometheus metrics integration
"""

import logging
import re
from typing import Optional, List, Dict
from enum import Enum
from dataclasses import dataclass

# Sprint 1, Day 2: Prometheus metrics collectors
from middleware import metrics

logger = logging.getLogger(__name__)


class QueryIntent(str, Enum):
    """Query intent classifications for model routing."""
    PRICE_ONLY = "price_only"
    TECHNICAL_ANALYSIS = "technical_analysis"
    NEWS_SUMMARY = "news_summary"
    MARKET_OVERVIEW = "market_overview"
    GENERAL_QUERY = "general_query"
    CHART_COMMAND = "chart_command"
    UNKNOWN = "unknown"


class ModelTier(str, Enum):
    """Model performance tiers."""
    CHEAP = "cheap"          # gpt-4o-mini - Fast, low-cost
    MID = "mid"               # gpt-4o - Balanced
    PREMIUM = "premium"       # gpt-5, o1 - High capability


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    tier: ModelTier
    max_tokens: int = 4096
    temperature: float = 0.7
    supports_function_calling: bool = True


# Available models (ordered by capability/cost)
AVAILABLE_MODELS = {
    "gpt-4o-mini": ModelConfig(
        name="gpt-4o-mini",
        tier=ModelTier.CHEAP,
        max_tokens=4096
    ),
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        tier=ModelTier.MID,
        max_tokens=4096
    ),
    "gpt-5-mini": ModelConfig(
        name="gpt-5-mini",
        tier=ModelTier.MID,
        max_tokens=8192
    ),
    "gpt-5": ModelConfig(
        name="gpt-5",
        tier=ModelTier.PREMIUM,
        max_tokens=8192
    ),
    "o1-mini": ModelConfig(
        name="o1-mini",
        tier=ModelTier.PREMIUM,
        max_tokens=8192,
        temperature=1.0  # o1 models use fixed temperature
    ),
    "o1": ModelConfig(
        name="o1",
        tier=ModelTier.PREMIUM,
        max_tokens=8192,
        temperature=1.0
    )
}


class ModelRouter:
    """
    Routes queries to appropriate models based on intent classification.

    Features:
    - Intent-based model selection
    - Fallback chain (cheap → mid → premium)
    - Configurable routing policy
    - Token budget awareness
    """

    def __init__(self):
        """Initialize model router with default policy."""
        # Intent → Primary Model mapping (from benchmarks)
        self.routing_policy = {
            QueryIntent.PRICE_ONLY: "gpt-4o-mini",
            QueryIntent.CHART_COMMAND: "gpt-4o-mini",
            QueryIntent.NEWS_SUMMARY: "gpt-4o",
            QueryIntent.MARKET_OVERVIEW: "gpt-4o",
            QueryIntent.TECHNICAL_ANALYSIS: "gpt-4o",
            QueryIntent.GENERAL_QUERY: "gpt-4o",
            QueryIntent.UNKNOWN: "gpt-4o"
        }

        # Fallback chains per tier
        self.fallback_chains = {
            ModelTier.CHEAP: ["gpt-4o-mini", "gpt-4o", "gpt-5"],
            ModelTier.MID: ["gpt-4o", "gpt-5", "gpt-4o-mini"],
            ModelTier.PREMIUM: ["gpt-5", "gpt-4o", "o1"]
        }

        logger.info("ModelRouter initialized with routing policy")

    def classify_intent(self, query: str, tools_requested: Optional[List[str]] = None) -> QueryIntent:
        """
        Classify query intent for model routing.

        Args:
            query: User query text
            tools_requested: Optional list of tools being called

        Returns:
            QueryIntent classification
        """
        query_lower = query.lower()

        # Chart commands (LOAD:, TIMEFRAME:, etc.)
        if any(cmd in query_lower for cmd in ["load:", "timeframe:", "indicator:", "draw:"]):
            return QueryIntent.CHART_COMMAND

        # Simple price lookups
        price_patterns = [
            r"(?:what'?s|get|show|tell me)\s+(?:the\s+)?(?:current\s+)?(?:stock\s+)?price",
            r"(?:get|show)\s+(?:me\s+)?[a-z]+\s+(?:stock\s+)?price",  # Fixed: lowercase for query_lower
            r"how much is",
            r"^(?:price|quote)\s+(?:for|of)",
        ]
        if any(re.search(pattern, query_lower) for pattern in price_patterns):
            # Check if ONLY asking for price (no analysis)
            if not any(word in query_lower for word in ["analyze", "technical", "support", "resistance", "indicator"]):
                return QueryIntent.PRICE_ONLY

        # Technical analysis
        technical_keywords = [
            "rsi", "macd", "bollinger", "support", "resistance", "fibonacci",
            "technical", "indicator", "moving average", "trend", "pattern",
            "oversold", "overbought", "breakout", "level"
        ]
        if any(keyword in query_lower for keyword in technical_keywords):
            return QueryIntent.TECHNICAL_ANALYSIS

        # News requests
        if any(word in query_lower for word in ["news", "headlines", "announcement", "article"]):
            return QueryIntent.NEWS_SUMMARY

        # Market overview
        if any(phrase in query_lower for phrase in ["market", "markets", "indices", "dow", "s&p", "nasdaq"]):
            return QueryIntent.MARKET_OVERVIEW

        # Strategic/investment questions (premium model)
        strategic_keywords = [
            "should i buy", "good entry", "investment", "strategy",
            "recommendation", "analysis", "outlook", "forecast"
        ]
        if any(keyword in query_lower for keyword in strategic_keywords):
            return QueryIntent.GENERAL_QUERY

        # Tool-based classification
        if tools_requested:
            if "get_stock_quote" in tools_requested and len(tools_requested) == 1:
                return QueryIntent.PRICE_ONLY
            elif any(tool in tools_requested for tool in ["get_technical_indicators", "get_support_resistance"]):
                return QueryIntent.TECHNICAL_ANALYSIS
            elif "get_market_news" in tools_requested:
                return QueryIntent.NEWS_SUMMARY

        # Default to general query
        return QueryIntent.GENERAL_QUERY

    def select_model(
        self,
        query: str,
        intent: Optional[QueryIntent] = None,
        fallback_index: int = 0,
        tools_requested: Optional[List[str]] = None
    ) -> ModelConfig:
        """
        Select appropriate model for a query.

        Args:
            query: User query text
            intent: Optional pre-classified intent
            fallback_index: Index in fallback chain (0 = primary, 1+ = fallbacks)
            tools_requested: Optional list of tools being called

        Returns:
            ModelConfig for the selected model
        """
        # Sprint 1, Day 2: Track routing latency
        import time
        start_time = time.perf_counter()

        # Classify intent if not provided
        if intent is None:
            intent = self.classify_intent(query, tools_requested)

        logger.info(f"Intent classified as: {intent.value}")

        # Get primary model for this intent
        primary_model = self.routing_policy.get(intent, "gpt-4o")
        logger.info(f"Primary model for {intent.value}: {primary_model}")

        # Get model config
        model_config = AVAILABLE_MODELS.get(primary_model)
        if not model_config:
            logger.warning(f"Model {primary_model} not found, using gpt-4o")
            metrics.model_fallbacks_total.labels(
                intent=intent.value,
                reason="model_not_found"
            ).inc()
            fallback_config = AVAILABLE_MODELS["gpt-4o"]
            duration = time.perf_counter() - start_time
            metrics.model_routing_duration_seconds.labels(intent=intent.value).observe(duration)
            metrics.model_selections_total.labels(
                intent=intent.value,
                model=fallback_config.name,
                tier=fallback_config.tier.value
            ).inc()
            return fallback_config

        # Handle fallback if requested
        if fallback_index > 0:
            fallback_chain = self.fallback_chains[model_config.tier]
            if fallback_index < len(fallback_chain):
                fallback_model = fallback_chain[fallback_index]
                logger.info(f"Using fallback model #{fallback_index}: {fallback_model}")
                metrics.model_fallbacks_total.labels(
                    intent=intent.value,
                    reason=f"fallback_index_{fallback_index}"
                ).inc()
                fallback_config = AVAILABLE_MODELS[fallback_model]
                duration = time.perf_counter() - start_time
                metrics.model_routing_duration_seconds.labels(intent=intent.value).observe(duration)
                metrics.model_selections_total.labels(
                    intent=intent.value,
                    model=fallback_config.name,
                    tier=fallback_config.tier.value
                ).inc()
                return fallback_config
            else:
                logger.warning(f"Fallback index {fallback_index} out of range, using primary")
                metrics.model_fallbacks_total.labels(
                    intent=intent.value,
                    reason="fallback_out_of_range"
                ).inc()

        duration = time.perf_counter() - start_time
        metrics.model_routing_duration_seconds.labels(intent=intent.value).observe(duration)
        metrics.model_selections_total.labels(
            intent=intent.value,
            model=model_config.name,
            tier=model_config.tier.value
        ).inc()

        return model_config

    def get_fallback_chain(self, primary_model: str) -> List[str]:
        """
        Get fallback chain for a primary model.

        Args:
            primary_model: Primary model name

        Returns:
            List of model names in fallback order
        """
        model_config = AVAILABLE_MODELS.get(primary_model)
        if not model_config:
            return ["gpt-4o", "gpt-4o-mini"]

        return self.fallback_chains[model_config.tier]

    def update_routing_policy(self, intent: QueryIntent, model: str):
        """
        Update routing policy for an intent.

        Args:
            intent: Query intent
            model: Model name to use for this intent
        """
        if model not in AVAILABLE_MODELS:
            logger.error(f"Cannot update policy: model {model} not available")
            return

        self.routing_policy[intent] = model
        logger.info(f"Updated routing policy: {intent.value} → {model}")

    def get_routing_summary(self) -> Dict[str, str]:
        """
        Get current routing policy summary.

        Returns:
            Dictionary mapping intent names to model names
        """
        return {
            intent.value: model
            for intent, model in self.routing_policy.items()
        }


# Singleton instance
_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get the global model router instance."""
    global _router
    if _router is None:
        _router = ModelRouter()
    return _router
