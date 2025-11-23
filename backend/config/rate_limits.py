"""
Rate Limiting Configuration
===========================
Centralized rate limit definitions for all API endpoints.

Supports:
- Tiered limits (anonymous, authenticated, premium)
- Redis-backed distributed rate limiting
- In-memory fallback for development
- Standard X-RateLimit headers
"""

from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum


class UserTier(Enum):
    """User tier for rate limiting"""
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"
    ADMIN = "admin"  # Admins bypass all rate limits


@dataclass
class RateLimit:
    """Rate limit configuration for an endpoint"""
    requests: int
    window_seconds: int
    tier: UserTier = UserTier.ANONYMOUS

    def to_string(self) -> str:
        """Convert to slowapi format: '100/minute', '10/second', etc."""
        if self.window_seconds == 1:
            return f"{self.requests}/second"
        elif self.window_seconds == 60:
            return f"{self.requests}/minute"
        elif self.window_seconds == 3600:
            return f"{self.requests}/hour"
        elif self.window_seconds == 86400:
            return f"{self.requests}/day"
        else:
            # For custom windows, use minute as base unit
            return f"{self.requests}/{self.window_seconds}second"


# ============================================================================
# RATE LIMIT DEFINITIONS
# ============================================================================

# Health & Status Endpoints (high limits - lightweight)
HEALTH_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=120, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=200, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=300, window_seconds=60),
}

# Market Data Endpoints (moderate limits - external API calls)
MARKET_DATA_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=60, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=120, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=300, window_seconds=60),
}

# Symbol Search Endpoints (moderate limits - database queries)
SEARCH_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=30, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=100, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=200, window_seconds=60),
}

# AI/LLM Endpoints (low limits - expensive operations)
AI_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=5, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=20, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=60, window_seconds=60),
}

# Voice/Agent Endpoints (very low limits - expensive streaming operations)
VOICE_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=3, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=10, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=30, window_seconds=60),
}

# WebSocket Connections (very low limits - long-lived connections)
WEBSOCKET_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=2, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=5, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=10, window_seconds=60),
}

# Authentication Endpoints (low limits - prevent brute force)
AUTH_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=5, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=10, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=20, window_seconds=60),
}

# Database Write Operations (low limits - prevent abuse)
WRITE_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=10, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=30, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=100, window_seconds=60),
}

# MCP/Tool Execution (moderate limits - external tool calls)
MCP_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=20, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=60, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=150, window_seconds=60),
}

# Static Asset Serving (high limits - cheap operations)
STATIC_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=300, window_seconds=60),
    UserTier.AUTHENTICATED: RateLimit(requests=500, window_seconds=60),
    UserTier.PREMIUM: RateLimit(requests=1000, window_seconds=60),
}


# ============================================================================
# ENDPOINT MAPPING
# ============================================================================

ENDPOINT_LIMITS: Dict[str, Dict[UserTier, RateLimit]] = {
    # Health & monitoring
    "/health": HEALTH_LIMITS,
    "/metrics": HEALTH_LIMITS,
    "/api/health": HEALTH_LIMITS,

    # Market data
    "/api/stock-price": MARKET_DATA_LIMITS,
    "/api/stock-history": MARKET_DATA_LIMITS,
    "/api/stock-news": MARKET_DATA_LIMITS,
    "/api/comprehensive-stock-data": MARKET_DATA_LIMITS,
    "/api/market-overview": MARKET_DATA_LIMITS,
    "/api/forex/calendar": MARKET_DATA_LIMITS,
    "/api/forex/events-today": MARKET_DATA_LIMITS,
    "/api/forex/events-week": MARKET_DATA_LIMITS,

    # Search
    "/api/symbol-search": SEARCH_LIMITS,

    # AI/LLM
    "/ask": AI_LIMITS,
    "/api/agents/query": AI_LIMITS,

    # Voice/Agent
    "/elevenlabs/signed-url": VOICE_LIMITS,
    "/api/agents-sdk/query": VOICE_LIMITS,

    # WebSocket
    "/ws/quotes": WEBSOCKET_LIMITS,
    "/ws/chart-commands": WEBSOCKET_LIMITS,
    "/mcp": WEBSOCKET_LIMITS,

    # MCP
    "/api/mcp": MCP_LIMITS,
    "/mcp/http": MCP_LIMITS,
    "/mcp/status": HEALTH_LIMITS,

    # Database operations
    "/api/conversation": WRITE_LIMITS,
    "/api/conversations": MARKET_DATA_LIMITS,  # Read is less expensive

    # Chart control - Write operations (POST endpoints)
    "/api/chart/change-symbol": WRITE_LIMITS,
    "/api/chart/set-timeframe": WRITE_LIMITS,
    "/api/chart/toggle-indicator": WRITE_LIMITS,
    "/api/chart/capture-snapshot": WRITE_LIMITS,
    "/api/chart/set-style": WRITE_LIMITS,
    "/api/chart/reset": WRITE_LIMITS,

    # Chart control - Read operations (polling endpoints need high limits)
    "/api/chart/commands": HEALTH_LIMITS,  # Frontend polls every 1s
    "/api/chart/state": MARKET_DATA_LIMITS,
}


def get_rate_limit(endpoint: str, tier: UserTier = UserTier.ANONYMOUS) -> RateLimit:
    """
    Get rate limit for an endpoint and user tier.

    Args:
        endpoint: API endpoint path
        tier: User tier (anonymous, authenticated, premium)

    Returns:
        RateLimit configuration
    """
    # Try exact match first
    if endpoint in ENDPOINT_LIMITS:
        return ENDPOINT_LIMITS[endpoint][tier]

    # Try prefix match for nested routes
    for pattern, limits in ENDPOINT_LIMITS.items():
        if endpoint.startswith(pattern):
            return limits[tier]

    # Default to market data limits for unknown endpoints
    return MARKET_DATA_LIMITS[tier]


def get_rate_limit_string(endpoint: str, tier: UserTier = UserTier.ANONYMOUS) -> str:
    """
    Get rate limit string in slowapi format.

    Args:
        endpoint: API endpoint path
        tier: User tier

    Returns:
        Rate limit string (e.g., "100/minute")
    """
    limit = get_rate_limit(endpoint, tier)
    return limit.to_string()


# ============================================================================
# REDIS CONFIGURATION
# ============================================================================

class RateLimitConfig:
    """Global rate limiting configuration"""

    # Redis connection
    REDIS_URL: Optional[str] = None  # Set via environment variable
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Fallback to in-memory if Redis unavailable
    USE_REDIS: bool = True
    FALLBACK_TO_MEMORY: bool = True

    # Rate limit response headers
    INCLUDE_HEADERS: bool = True
    HEADER_PREFIX: str = "X-RateLimit"

    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_RATE_LIMIT_HITS: bool = False  # Set to True for debugging

    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        import os

        cls.REDIS_URL = os.getenv("REDIS_URL")
        cls.REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
        cls.REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
        cls.REDIS_DB = int(os.getenv("REDIS_DB", "0"))
        cls.REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

        cls.USE_REDIS = os.getenv("USE_REDIS", "true").lower() == "true"
        cls.FALLBACK_TO_MEMORY = os.getenv("FALLBACK_TO_MEMORY", "true").lower() == "true"

        cls.INCLUDE_HEADERS = os.getenv("RATE_LIMIT_HEADERS", "true").lower() == "true"
        cls.LOG_RATE_LIMIT_HITS = os.getenv("LOG_RATE_LIMIT_HITS", "false").lower() == "true"
        cls.ENABLE_METRICS = os.getenv("RATE_LIMIT_METRICS", "true").lower() == "true"


# Initialize from environment on import
RateLimitConfig.from_env()
