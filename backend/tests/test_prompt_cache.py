"""
Tests for Prompt Cache Service
================================
Tests for LRU prompt caching and OpenAI cache optimization.

Phase 2: Model Routing & Prompt Optimization - Cache Tests
"""

import pytest
import time
from datetime import datetime, timedelta
from services.prompt_cache import PromptCache, get_prompt_cache


class TestPromptCache:
    """Test prompt caching functionality."""

    def test_cache_initialization(self):
        """Test cache initializes with correct parameters."""
        cache = PromptCache(max_size=50, ttl_seconds=600)

        assert cache.max_size == 50
        assert cache.ttl_seconds == 600
        assert len(cache.cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0

    def test_cache_miss(self):
        """Test cache miss on first access."""
        cache = PromptCache()

        result = cache.get("system prompt", "user query", "gpt-4o")

        assert result is None
        assert cache.misses == 1
        assert cache.hits == 0

    def test_cache_put_and_get(self):
        """Test putting and getting from cache."""
        cache = PromptCache()

        # Put in cache
        key = cache.put("system prompt", "user query", "gpt-4o")
        assert key is not None

        # Get from cache
        result = cache.get("system prompt", "user query", "gpt-4o")

        assert result is not None
        assert result.system_prompt == "system prompt"
        assert result.user_prompt == "user query"
        assert result.model == "gpt-4o"
        assert cache.hits == 1

    def test_cache_hit_increments_access_count(self):
        """Test that cache hits increment access counter."""
        cache = PromptCache()

        cache.put("system", "user", "gpt-4o")

        # Access multiple times
        result1 = cache.get("system", "user", "gpt-4o")
        result2 = cache.get("system", "user", "gpt-4o")
        result3 = cache.get("system", "user", "gpt-4o")

        assert result3.access_count == 3
        assert cache.hits == 3

    def test_cache_stores_recent_responses(self):
        """Test that cache stores recent responses."""
        cache = PromptCache()

        cache.put("system", "user", "gpt-4o", response="Response 1")
        cache.put("system", "user", "gpt-4o", response="Response 2")
        cache.put("system", "user", "gpt-4o", response="Response 3")

        result = cache.get("system", "user", "gpt-4o")

        assert len(result.recent_responses) == 3
        assert "Response 1" in result.recent_responses

    def test_cache_limits_recent_responses(self):
        """Test that recent responses are limited."""
        cache = PromptCache()

        # Add 5 responses (limit is 3)
        for i in range(5):
            cache.put("system", "user", "gpt-4o", response=f"Response {i}")

        result = cache.get("system", "user", "gpt-4o")

        assert len(result.recent_responses) <= result.max_recent_responses


class TestCacheEviction:
    """Test cache eviction policies."""

    def test_lru_eviction(self):
        """Test least recently used eviction."""
        cache = PromptCache(max_size=3)

        # Fill cache
        cache.put("system", "query1", "gpt-4o")
        cache.put("system", "query2", "gpt-4o")
        cache.put("system", "query3", "gpt-4o")

        # Add one more (should evict query1)
        cache.put("system", "query4", "gpt-4o")

        # query1 should be evicted
        assert cache.get("system", "query1", "gpt-4o") is None
        assert cache.get("system", "query2", "gpt-4o") is not None
        assert cache.evictions == 1

    def test_lru_updates_on_access(self):
        """Test that accessing an entry moves it to end (most recent)."""
        cache = PromptCache(max_size=3)

        cache.put("system", "query1", "gpt-4o")
        cache.put("system", "query2", "gpt-4o")
        cache.put("system", "query3", "gpt-4o")

        # Access query1 (makes it most recent)
        cache.get("system", "query1", "gpt-4o")

        # Add query4 (should evict query2, not query1)
        cache.put("system", "query4", "gpt-4o")

        assert cache.get("system", "query1", "gpt-4o") is not None
        assert cache.get("system", "query2", "gpt-4o") is None


class TestCacheExpiration:
    """Test cache TTL and expiration."""

    def test_expired_entry_returns_none(self):
        """Test that expired entries return None."""
        cache = PromptCache(ttl_seconds=1)  # 1 second TTL

        cache.put("system", "user", "gpt-4o")

        # Sleep to expire
        time.sleep(1.1)

        result = cache.get("system", "user", "gpt-4o")

        assert result is None
        assert cache.misses == 1

    def test_remove_expired(self):
        """Test manual removal of expired entries."""
        cache = PromptCache(ttl_seconds=1)

        cache.put("system", "query1", "gpt-4o")
        cache.put("system", "query2", "gpt-4o")

        time.sleep(1.1)

        # Add fresh entry
        cache.put("system", "query3", "gpt-4o")

        # Remove expired
        cache.remove_expired()

        # Only query3 should remain
        assert len(cache.cache) == 1
        assert cache.get("system", "query3", "gpt-4o") is not None


class TestCachingRecommendations:
    """Test caching recommendation logic."""

    def test_should_use_caching_for_large_prompts(self):
        """Test that large prompts are recommended for caching."""
        cache = PromptCache()

        # Large prompt (>1024 tokens ≈ >4096 characters)
        large_system = "A" * 3000
        large_user = "B" * 2000

        assert cache.should_use_caching(large_system, large_user) is True

    def test_should_not_cache_small_prompts(self):
        """Test that small prompts are not recommended for caching."""
        cache = PromptCache()

        small_system = "Short system prompt"
        small_user = "Short user query"

        assert cache.should_use_caching(small_system, small_user) is False


class TestCacheWarming:
    """Test cache warming functionality."""

    def test_warm_cache_with_common_prompts(self):
        """Test pre-populating cache with common prompts."""
        cache = PromptCache()

        common_prompts = [
            {"system": "sys1", "user": "user1", "model": "gpt-4o"},
            {"system": "sys2", "user": "user2", "model": "gpt-4o"},
            {"system": "sys3", "user": "user3", "model": "gpt-4o"}
        ]

        cache.warm_cache(common_prompts)

        assert len(cache.cache) == 3
        assert cache.get("sys1", "user1", "gpt-4o") is not None


class TestCacheStatistics:
    """Test cache statistics and metrics."""

    def test_get_stats(self):
        """Test cache statistics."""
        cache = PromptCache(max_size=10, ttl_seconds=300)

        cache.put("system", "query1", "gpt-4o")
        cache.get("system", "query1", "gpt-4o")  # Hit
        cache.get("system", "query2", "gpt-4o")  # Miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["max_size"] == 10
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5
        assert stats["total_requests"] == 2

    def test_clear_cache(self):
        """Test clearing entire cache."""
        cache = PromptCache()

        cache.put("system", "query1", "gpt-4o")
        cache.put("system", "query2", "gpt-4o")

        cache.clear()

        assert len(cache.cache) == 0
        assert cache.get("system", "query1", "gpt-4o") is None


class TestSingletonCache:
    """Test singleton cache instance."""

    def test_get_prompt_cache_singleton(self):
        """get_prompt_cache should return same instance."""
        cache1 = get_prompt_cache()
        cache2 = get_prompt_cache()

        assert cache1 is cache2

    def test_singleton_maintains_state(self):
        """Singleton should maintain state across calls."""
        cache = get_prompt_cache()
        cache.put("system", "test", "gpt-4o")

        # Get cache again
        cache2 = get_prompt_cache()
        result = cache2.get("system", "test", "gpt-4o")

        assert result is not None
