"""
Enhanced Rate Limiter Middleware
=================================
Production-ready rate limiting with Redis backend and in-memory fallback.

Features:
- Redis-backed distributed rate limiting
- In-memory fallback for development
- Tiered limits (anonymous, authenticated, premium)
- Standard X-RateLimit headers
- Rate limit metrics and monitoring
"""

import time
import logging
from typing import Dict, Optional, Tuple
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config.rate_limits import (
    UserTier,
    RateLimit,
    RateLimitConfig,
    get_rate_limit,
)

logger = logging.getLogger(__name__)


# ============================================================================
# REDIS BACKEND
# ============================================================================

class RedisRateLimiter:
    """Redis-backed rate limiter for distributed systems"""

    def __init__(self):
        self.redis = None
        self.available = False
        self._initialize_redis()

    def _initialize_redis(self):
        """Initialize Redis connection"""
        if not RateLimitConfig.USE_REDIS:
            logger.info("Redis rate limiting disabled by configuration")
            return

        try:
            import redis
            from redis.connection import ConnectionPool

            # Use connection pool for better performance
            if RateLimitConfig.REDIS_URL:
                self.redis = redis.from_url(
                    RateLimitConfig.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
            else:
                pool = ConnectionPool(
                    host=RateLimitConfig.REDIS_HOST,
                    port=RateLimitConfig.REDIS_PORT,
                    db=RateLimitConfig.REDIS_DB,
                    password=RateLimitConfig.REDIS_PASSWORD,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                self.redis = redis.Redis(connection_pool=pool)

            # Test connection
            self.redis.ping()
            self.available = True
            logger.info(f"Redis rate limiter initialized: {RateLimitConfig.REDIS_HOST}:{RateLimitConfig.REDIS_PORT}")

        except Exception as e:
            logger.warning(f"Redis not available: {e}. Falling back to in-memory rate limiting")
            self.redis = None
            self.available = False

    def is_allowed(
        self,
        key: str,
        limit: RateLimit
    ) -> Tuple[bool, int, int]:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier for rate limit bucket (e.g., "ip:127.0.0.1:endpoint:/api/stock-price")
            limit: Rate limit configuration

        Returns:
            (allowed, remaining, reset_time)
        """
        if not self.available:
            raise Exception("Redis not available")

        try:
            current_time = int(time.time())
            window_start = current_time - (current_time % limit.window_seconds)
            redis_key = f"ratelimit:{key}:{window_start}"

            # Use Redis pipeline for atomicity
            pipe = self.redis.pipeline()
            pipe.incr(redis_key)
            pipe.expire(redis_key, limit.window_seconds + 10)  # Add buffer
            results = pipe.execute()

            current_count = results[0]
            remaining = max(0, limit.requests - current_count)
            reset_time = window_start + limit.window_seconds

            allowed = current_count <= limit.requests

            if RateLimitConfig.LOG_RATE_LIMIT_HITS:
                logger.debug(f"Rate limit check: key={key}, count={current_count}/{limit.requests}, allowed={allowed}")

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            raise


# ============================================================================
# IN-MEMORY BACKEND
# ============================================================================

class InMemoryRateLimiter:
    """In-memory rate limiter for development/fallback"""

    def __init__(self):
        self.buckets: Dict[str, Dict[str, any]] = {}
        logger.info("In-memory rate limiter initialized")

    def _cleanup_old_buckets(self):
        """Remove expired buckets to prevent memory leak"""
        current_time = int(time.time())
        expired_keys = [
            key for key, bucket in self.buckets.items()
            if bucket.get('reset_time', 0) < current_time
        ]
        for key in expired_keys:
            del self.buckets[key]

    def is_allowed(
        self,
        key: str,
        limit: RateLimit
    ) -> Tuple[bool, int, int]:
        """
        Check if request is allowed under rate limit.

        Args:
            key: Unique identifier for rate limit bucket
            limit: Rate limit configuration

        Returns:
            (allowed, remaining, reset_time)
        """
        current_time = int(time.time())
        window_start = current_time - (current_time % limit.window_seconds)
        bucket_key = f"{key}:{window_start}"

        # Cleanup old buckets periodically (every 100 requests)
        if len(self.buckets) % 100 == 0:
            self._cleanup_old_buckets()

        # Get or create bucket
        if bucket_key not in self.buckets:
            self.buckets[bucket_key] = {
                'count': 0,
                'reset_time': window_start + limit.window_seconds
            }

        bucket = self.buckets[bucket_key]

        # Reset if window has passed
        if current_time >= bucket['reset_time']:
            bucket['count'] = 0
            bucket['reset_time'] = window_start + limit.window_seconds

        # Increment and check
        bucket['count'] += 1
        current_count = bucket['count']
        remaining = max(0, limit.requests - current_count)
        reset_time = bucket['reset_time']

        allowed = current_count <= limit.requests

        if RateLimitConfig.LOG_RATE_LIMIT_HITS:
            logger.debug(f"Rate limit check: key={key}, count={current_count}/{limit.requests}, allowed={allowed}")

        return allowed, remaining, reset_time


# ============================================================================
# UNIFIED RATE LIMITER
# ============================================================================

class RateLimiterBackend:
    """Unified rate limiter with automatic Redis fallback"""

    def __init__(self):
        self.redis_limiter = None
        self.memory_limiter = InMemoryRateLimiter()
        self.using_redis = False

        # Try to initialize Redis
        if RateLimitConfig.USE_REDIS:
            try:
                self.redis_limiter = RedisRateLimiter()
                if self.redis_limiter.available:
                    self.using_redis = True
                    logger.info("Rate limiter using Redis backend")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis rate limiter: {e}")

        if not self.using_redis:
            logger.info("Rate limiter using in-memory backend")

    def is_allowed(
        self,
        key: str,
        limit: RateLimit
    ) -> Tuple[bool, int, int]:
        """Check if request is allowed"""
        try:
            if self.using_redis:
                return self.redis_limiter.is_allowed(key, limit)
        except Exception as e:
            logger.warning(f"Redis rate limit check failed, falling back to memory: {e}")
            if not RateLimitConfig.FALLBACK_TO_MEMORY:
                raise

        return self.memory_limiter.is_allowed(key, limit)


# Global rate limiter instance
_rate_limiter_backend: Optional[RateLimiterBackend] = None


def get_rate_limiter() -> RateLimiterBackend:
    """Get or create global rate limiter instance"""
    global _rate_limiter_backend
    if _rate_limiter_backend is None:
        _rate_limiter_backend = RateLimiterBackend()
    return _rate_limiter_backend


# ============================================================================
# MIDDLEWARE
# ============================================================================

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting with tiered limits.

    Adds X-RateLimit headers to all responses:
    - X-RateLimit-Limit: Maximum requests allowed
    - X-RateLimit-Remaining: Requests remaining in current window
    - X-RateLimit-Reset: Unix timestamp when limit resets
    """

    def __init__(self, app):
        super().__init__(app)
        self.limiter = get_rate_limiter()

    def _get_user_tier(self, request: Request) -> UserTier:
        """
        Determine user tier from request.

        Priority:
        1. X-User-Tier header (for testing/admin override)
        2. X-Admin-Key header (admin API key)
        3. Authorization header (authenticated users)
        4. Premium status from database/JWT
        5. Default to anonymous
        """
        # Check header for tier (testing/admin)
        tier_header = request.headers.get("X-User-Tier", "").lower()
        if tier_header in ["admin", "authenticated", "premium"]:
            return UserTier[tier_header.upper()]

        # Check for admin API key
        admin_key = request.headers.get("X-Admin-Key")
        if admin_key:
            # TODO: Validate admin key against environment variable
            # For now, any admin key grants admin access
            import os
            expected_admin_key = os.getenv("ADMIN_API_KEY")
            if expected_admin_key and admin_key == expected_admin_key:
                logger.info(f"Admin access granted for {self._get_client_identifier(request)}")
                return UserTier.ADMIN

        # Check authorization
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # TODO: Decode JWT and check premium/admin status
            return UserTier.AUTHENTICATED

        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            # TODO: Validate API key and determine tier
            return UserTier.AUTHENTICATED

        return UserTier.ANONYMOUS

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique identifier for the client"""
        # Priority: X-Forwarded-For (proxy) > X-Real-IP > client host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        # Skip rate limiting for certain paths
        skip_paths = ["/metrics", "/docs", "/openapi.json", "/redoc"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)

        # Get user tier - ADMINS BYPASS ALL RATE LIMITS
        tier = self._get_user_tier(request)
        if tier == UserTier.ADMIN:
            logger.debug(f"Admin request bypassing rate limits: {request.url.path}")
            return await call_next(request)

        # Get rate limit for non-admin users
        limit = get_rate_limit(request.url.path, tier)

        # Create rate limit key
        client_id = self._get_client_identifier(request)
        rate_limit_key = f"ip:{client_id}:endpoint:{request.url.path}"

        # Check rate limit
        try:
            allowed, remaining, reset_time = self.limiter.is_allowed(rate_limit_key, limit)
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if rate limiting is broken
            return await call_next(request)

        # Add rate limit headers if configured
        response = None
        if allowed:
            response = await call_next(request)
        else:
            # Rate limit exceeded
            retry_after = reset_time - int(time.time())
            response = JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit": limit.requests,
                    "window": f"{limit.window_seconds}s"
                }
            )

        # Add standard rate limit headers
        if RateLimitConfig.INCLUDE_HEADERS:
            response.headers[f"{RateLimitConfig.HEADER_PREFIX}-Limit"] = str(limit.requests)
            response.headers[f"{RateLimitConfig.HEADER_PREFIX}-Remaining"] = str(remaining)
            response.headers[f"{RateLimitConfig.HEADER_PREFIX}-Reset"] = str(reset_time)
            response.headers[f"{RateLimitConfig.HEADER_PREFIX}-Window"] = f"{limit.window_seconds}s"

        return response
