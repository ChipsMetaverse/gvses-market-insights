"""
Rate Limit Monitoring Router
============================
Endpoints for monitoring and managing rate limits.
"""

import time
from typing import Dict, List
from fastapi import APIRouter, Request, Header
from pydantic import BaseModel
from config.rate_limits import (
    UserTier,
    RateLimit,
    RateLimitConfig,
    get_rate_limit,
    ENDPOINT_LIMITS,
)
from middleware.rate_limiter import get_rate_limiter

router = APIRouter(prefix="/api/rate-limits", tags=["Rate Limiting"])


class RateLimitStatus(BaseModel):
    """Rate limit status for an endpoint"""
    endpoint: str
    tier: str
    limit: int
    window_seconds: int
    remaining: int
    reset_time: int
    retry_after: int


class RateLimitInfo(BaseModel):
    """Complete rate limit information"""
    client_identifier: str
    tier: str
    backend: str  # "redis" or "memory"
    limits: List[RateLimitStatus]


class RateLimitConfig(BaseModel):
    """Global rate limit configuration"""
    use_redis: bool
    redis_available: bool
    fallback_to_memory: bool
    include_headers: bool
    endpoints_configured: int


@router.get("/status", response_model=RateLimitInfo)
async def get_rate_limit_status(
    request: Request,
    x_user_tier: str = Header(None, alias="X-User-Tier")
):
    """
    Get current rate limit status for the client.

    Returns remaining requests for all configured endpoints.
    """
    # Determine user tier
    tier_str = x_user_tier.lower() if x_user_tier else "anonymous"
    try:
        tier = UserTier[tier_str.upper()]
    except KeyError:
        tier = UserTier.ANONYMOUS

    # Get client identifier
    client_id = _get_client_identifier(request)

    # Get rate limiter backend
    limiter = get_rate_limiter()
    backend = "redis" if limiter.using_redis else "memory"

    # Check limits for all configured endpoints
    limits = []
    current_time = int(time.time())

    for endpoint, tier_limits in ENDPOINT_LIMITS.items():
        limit = tier_limits[tier]
        rate_limit_key = f"ip:{client_id}:endpoint:{endpoint}"

        try:
            _, remaining, reset_time = limiter.is_allowed(rate_limit_key, limit)
            # Decrement to account for this check
            remaining = max(0, remaining - 1)

            limits.append(RateLimitStatus(
                endpoint=endpoint,
                tier=tier.value,
                limit=limit.requests,
                window_seconds=limit.window_seconds,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=max(0, reset_time - current_time)
            ))
        except Exception:
            # Skip if check fails
            continue

    return RateLimitInfo(
        client_identifier=client_id,
        tier=tier.value,
        backend=backend,
        limits=limits
    )


@router.get("/check/{endpoint:path}")
async def check_endpoint_limit(
    endpoint: str,
    request: Request,
    x_user_tier: str = Header(None, alias="X-User-Tier")
):
    """
    Check rate limit for a specific endpoint without consuming a request.

    Args:
        endpoint: API endpoint path (e.g., "api/stock-price")
    """
    # Normalize endpoint path
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    # Determine user tier
    tier_str = x_user_tier.lower() if x_user_tier else "anonymous"
    try:
        tier = UserTier[tier_str.upper()]
    except KeyError:
        tier = UserTier.ANONYMOUS

    # Get rate limit configuration
    limit = get_rate_limit(endpoint, tier)

    # Get client identifier
    client_id = _get_client_identifier(request)
    rate_limit_key = f"ip:{client_id}:endpoint:{endpoint}"

    # Check current status (this WILL consume a request)
    limiter = get_rate_limiter()
    try:
        allowed, remaining, reset_time = limiter.is_allowed(rate_limit_key, limit)
        # Decrement to account for this check
        remaining = max(0, remaining - 1)
    except Exception as e:
        return {
            "error": f"Rate limit check failed: {str(e)}",
            "endpoint": endpoint,
            "tier": tier.value
        }

    current_time = int(time.time())
    return {
        "endpoint": endpoint,
        "tier": tier.value,
        "allowed": allowed,
        "limit": limit.requests,
        "remaining": remaining,
        "window_seconds": limit.window_seconds,
        "reset_time": reset_time,
        "retry_after": max(0, reset_time - current_time)
    }


@router.get("/config", response_model=RateLimitConfig)
async def get_rate_limit_config():
    """Get global rate limiting configuration"""
    from config.rate_limits import RateLimitConfig as GlobalConfig

    limiter = get_rate_limiter()

    return RateLimitConfig(
        use_redis=GlobalConfig.USE_REDIS,
        redis_available=limiter.using_redis,
        fallback_to_memory=GlobalConfig.FALLBACK_TO_MEMORY,
        include_headers=GlobalConfig.INCLUDE_HEADERS,
        endpoints_configured=len(ENDPOINT_LIMITS)
    )


@router.get("/limits")
async def list_all_limits():
    """
    List all configured rate limits for all tiers.

    Useful for documentation and debugging.
    """
    limits_by_tier = {
        "anonymous": {},
        "authenticated": {},
        "premium": {}
    }

    for endpoint, tier_limits in ENDPOINT_LIMITS.items():
        for tier, limit in tier_limits.items():
            limits_by_tier[tier.value][endpoint] = {
                "requests": limit.requests,
                "window_seconds": limit.window_seconds,
                "window_display": _format_window(limit.window_seconds)
            }

    return {
        "tiers": limits_by_tier,
        "total_endpoints": len(ENDPOINT_LIMITS)
    }


def _get_client_identifier(request: Request) -> str:
    """Get unique identifier for the client"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "unknown"


def _format_window(seconds: int) -> str:
    """Format window duration for display"""
    if seconds == 1:
        return "1 second"
    elif seconds == 60:
        return "1 minute"
    elif seconds == 3600:
        return "1 hour"
    elif seconds == 86400:
        return "1 day"
    elif seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        return f"{seconds // 60} minutes"
    elif seconds < 86400:
        return f"{seconds // 3600} hours"
    else:
        return f"{seconds // 86400} days"
