"""
Prompt Cache Service
===================
LRU cache for frequently asked queries to reduce API costs via prompt caching.

Phase 2: Model Routing & Prompt Optimization - Caching Layer
Sprint 1, Day 2: Prometheus metrics integration
"""

import logging
import hashlib
import time
from typing import Optional, Dict, Any, List
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# Sprint 1, Day 2: Prometheus metrics collectors
from middleware import metrics

logger = logging.getLogger(__name__)


@dataclass
class CachedPrompt:
    """Cached prompt entry."""
    prompt_hash: str
    system_prompt: str
    user_prompt: str
    model: str
    cached_at: datetime
    last_accessed: datetime
    access_count: int = 0
    # Store recent responses for query deduplication
    recent_responses: List[str] = field(default_factory=list)
    max_recent_responses: int = 3


class PromptCache:
    """
    LRU cache for prompts to leverage OpenAI's automatic prompt caching.

    Features:
    - Caches frequently used prompts (>1024 tokens)
    - LRU eviction policy
    - Cache hit tracking
    - Automatic cache warming for common queries
    """

    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        """
        Initialize prompt cache.

        Args:
            max_size: Maximum number of cached prompts
            ttl_seconds: Time-to-live for cached prompts (default: 5 minutes)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, CachedPrompt] = OrderedDict()

        # Metrics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

        logger.info(f"PromptCache initialized: max_size={max_size}, ttl={ttl_seconds}s")

    def _generate_hash(self, system_prompt: str, user_prompt: str, model: str) -> str:
        """Generate cache key hash."""
        content = f"{system_prompt}|{user_prompt}|{model}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _is_expired(self, cached_prompt: CachedPrompt) -> bool:
        """Check if cached prompt has expired."""
        age = datetime.utcnow() - cached_prompt.cached_at
        return age.total_seconds() > self.ttl_seconds

    def _evict_oldest(self):
        """Evict oldest (least recently used) entry."""
        if len(self.cache) >= self.max_size:
            oldest_key, _ = self.cache.popitem(last=False)
            self.evictions += 1
            logger.debug(f"Evicted oldest cache entry: {oldest_key}")
            # Sprint 1, Day 2: Update Prometheus metrics after eviction
            self._update_prometheus_metrics()

    def get(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str
    ) -> Optional[CachedPrompt]:
        """
        Get cached prompt if available.

        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text
            model: Model name

        Returns:
            CachedPrompt if found and valid, None otherwise
        """
        cache_key = self._generate_hash(system_prompt, user_prompt, model)

        if cache_key in self.cache:
            cached = self.cache[cache_key]

            # Check if expired
            if self._is_expired(cached):
                logger.debug(f"Cache entry expired: {cache_key}")
                del self.cache[cache_key]
                self.misses += 1
                metrics.prompt_cache_operations_total.labels(
                    operation="get",
                    result="miss"
                ).inc()
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)

            # Update access stats
            cached.last_accessed = datetime.utcnow()
            cached.access_count += 1

            self.hits += 1
            logger.info(f"Cache HIT: {cache_key} (accessed {cached.access_count} times)")
            metrics.prompt_cache_operations_total.labels(
                operation="get",
                result="hit"
            ).inc()
            return cached

        self.misses += 1
        logger.debug(f"Cache MISS: {cache_key}")
        metrics.prompt_cache_operations_total.labels(
            operation="get",
            result="miss"
        ).inc()
        return None

    def put(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str,
        response: Optional[str] = None
    ) -> str:
        """
        Add or update prompt in cache.

        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text
            model: Model name
            response: Optional response to store

        Returns:
            Cache key hash
        """
        cache_key = self._generate_hash(system_prompt, user_prompt, model)

        # Check if already cached
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            self.cache.move_to_end(cache_key)

            # Add response to recent list
            if response and response not in cached.recent_responses:
                cached.recent_responses.append(response)
                if len(cached.recent_responses) > cached.max_recent_responses:
                    cached.recent_responses.pop(0)

            logger.debug(f"Updated existing cache entry: {cache_key}")
            return cache_key

        # Evict if at capacity
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        # Create new cache entry
        cached = CachedPrompt(
            prompt_hash=cache_key,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model,
            cached_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            recent_responses=[response] if response else []
        )

        self.cache[cache_key] = cached
        logger.info(f"Cached new prompt: {cache_key}")
        metrics.prompt_cache_operations_total.labels(
            operation="put",
            result="success"
        ).inc()
        # Update Prometheus gauges
        self._update_prometheus_metrics()

        return cache_key

    def should_use_caching(self, system_prompt: str, user_prompt: str) -> bool:
        """
        Determine if prompt caching would be beneficial.

        OpenAI caches prompts >1024 tokens with 50% cost reduction.

        Args:
            system_prompt: System prompt text
            user_prompt: User prompt text

        Returns:
            True if caching is recommended
        """
        # Rough token estimation (1 token ≈ 4 characters)
        total_chars = len(system_prompt) + len(user_prompt)
        estimated_tokens = total_chars / 4

        return estimated_tokens > 1024

    def warm_cache(self, common_prompts: List[Dict[str, str]]):
        """
        Pre-populate cache with common prompts.

        Args:
            common_prompts: List of dicts with 'system', 'user', 'model' keys
        """
        for prompt_config in common_prompts:
            self.put(
                system_prompt=prompt_config["system"],
                user_prompt=prompt_config["user"],
                model=prompt_config.get("model", "gpt-4o")
            )

        logger.info(f"Warmed cache with {len(common_prompts)} common prompts")

    def _update_prometheus_metrics(self):
        """
        Update Prometheus metrics gauges.
        Sprint 1, Day 2: Helper method to sync internal metrics with Prometheus.
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        metrics.prompt_cache_size.set(len(self.cache))
        metrics.prompt_cache_hit_rate.set(hit_rate)
        current_evictions = metrics.prompt_cache_evictions_total._value._value
        if self.evictions > current_evictions:
            metrics.prompt_cache_evictions_total.inc(self.evictions - current_evictions)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dict with cache metrics
        """
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        # Sprint 1, Day 2: Update Prometheus metrics when stats are requested
        self._update_prometheus_metrics()

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": round(hit_rate, 4),
            "total_requests": total_requests,
            "ttl_seconds": self.ttl_seconds
        }

    def clear(self):
        """Clear all cached prompts."""
        self.cache.clear()
        logger.info("Cache cleared")

    def remove_expired(self):
        """Remove all expired entries."""
        expired_keys = [
            key for key, cached in self.cache.items()
            if self._is_expired(cached)
        ]

        for key in expired_keys:
            del self.cache[key]

        if expired_keys:
            logger.info(f"Removed {len(expired_keys)} expired cache entries")


# Common prompts for cache warming
COMMON_MARKET_PROMPTS = [
    {
        "system": "You are a professional trading assistant. Provide concise market insights.",
        "user": "What's the current price of {symbol}?",
        "model": "gpt-4o-mini"
    },
    {
        "system": "You are a technical analysis expert. Analyze stocks using indicators.",
        "user": "Analyze {symbol} with RSI and MACD",
        "model": "gpt-4o"
    },
    {
        "system": "You are a market news summarizer. Provide relevant market updates.",
        "user": "Latest news about {symbol}",
        "model": "gpt-4o"
    }
]


# Singleton instance
_cache: Optional[PromptCache] = None


def get_prompt_cache() -> PromptCache:
    """Get the global prompt cache instance."""
    global _cache
    if _cache is None:
        _cache = PromptCache()
        # Warm with common prompts
        # Note: Would need to format with actual symbols in production
        logger.info("Prompt cache initialized")
    return _cache
