# Rate Limiting System

Production-ready rate limiting with Redis backend and in-memory fallback for the GVSES Market Insights API.

## Overview

The rate limiting system provides:
- **Tiered limits** - Different limits for anonymous, authenticated, premium, and admin users
- **Redis-backed** - Distributed rate limiting for production scaling
- **In-memory fallback** - Works without Redis for development
- **Standard headers** - X-RateLimit-* headers in all responses
- **Admin bypass** - Admins can make unlimited requests
- **Monitoring endpoints** - Real-time rate limit status and configuration

## Features

### ✅ Implemented

- [x] Configuration-based rate limits (easy to update)
- [x] Redis backend with connection pooling
- [x] In-memory fallback for development
- [x] Tiered limits (anonymous, authenticated, premium, admin)
- [x] Admin bypass functionality
- [x] Standard X-RateLimit headers
- [x] Rate limit monitoring endpoints
- [x] Per-endpoint rate limits
- [x] Automatic cleanup of expired buckets

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                  RateLimitMiddleware                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ 1. Check user tier (anonymous/authenticated/premium)  │  │
│  │ 2. ADMIN? → Bypass all limits                         │  │
│  │ 3. Get rate limit for endpoint + tier                 │  │
│  │ 4. Check rate limit (Redis or Memory)                 │  │
│  │ 5. Add X-RateLimit headers                            │  │
│  │ 6. Return 429 if exceeded                             │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│           RateLimiterBackend (Unified Interface)             │
│  ┌──────────────────┐      ┌─────────────────────────────┐  │
│  │  Redis Limiter   │  OR  │  In-Memory Limiter          │  │
│  │  (Production)    │      │  (Development/Fallback)     │  │
│  └──────────────────┘      └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Rate Limit Tiers

### Anonymous Users
Default for all unauthenticated requests:
- Health/Status: **120 requests/minute**
- Market Data: **60 requests/minute**
- Search: **30 requests/minute**
- AI/LLM: **5 requests/minute**
- Voice: **3 requests/minute**
- WebSocket: **2 connections/minute**

### Authenticated Users
For users with valid Bearer token or API key:
- Health/Status: **200 requests/minute**
- Market Data: **120 requests/minute**
- Search: **100 requests/minute**
- AI/LLM: **20 requests/minute**
- Voice: **10 requests/minute**
- WebSocket: **5 connections/minute**

### Premium Users
For users with premium subscription:
- Health/Status: **300 requests/minute**
- Market Data: **300 requests/minute**
- Search: **200 requests/minute**
- AI/LLM: **60 requests/minute**
- Voice: **30 requests/minute**
- WebSocket: **10 connections/minute**

### Admin Users
**UNLIMITED** - Admins bypass all rate limits entirely.

## Configuration

### Environment Variables

Add to `backend/.env`:

```bash
# Redis Configuration (optional - falls back to in-memory)
REDIS_URL=redis://localhost:6379/0
# OR
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password

# Rate Limiting Behavior
USE_REDIS=true                    # Enable Redis backend (default: true)
FALLBACK_TO_MEMORY=true           # Fall back to memory if Redis fails (default: true)
RATE_LIMIT_HEADERS=true           # Include X-RateLimit headers (default: true)
LOG_RATE_LIMIT_HITS=false         # Log every rate limit check (default: false)

# Admin Access
ADMIN_API_KEY=your_secret_admin_key  # For X-Admin-Key header authentication
```

### Production Setup (Fly.io)

Add Redis addon:
```bash
fly redis create
```

Update `fly.toml`:
```toml
[env]
  USE_REDIS = "true"
  RATE_LIMIT_HEADERS = "true"
```

Redis URL will be automatically set via secrets.

## Usage

### Client Side

#### Anonymous Requests
```bash
curl http://localhost:8000/api/stock-price?symbol=TSLA
```

Response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1762862820
X-RateLimit-Window: 60s
```

#### Authenticated Requests
```bash
curl -H "Authorization: Bearer your_token" \\
     http://localhost:8000/api/stock-price?symbol=TSLA
```

Higher limits applied automatically.

#### Admin Requests (Bypass All Limits)
```bash
curl -H "X-Admin-Key: your_secret_admin_key" \\
     http://localhost:8000/api/stock-price?symbol=TSLA
```

OR for testing:
```bash
curl -H "X-User-Tier: admin" \\
     http://localhost:8000/api/stock-price?symbol=TSLA
```

### Rate Limit Exceeded

When limit is exceeded, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again in 45 seconds.",
  "retry_after": 45,
  "limit": 60,
  "window": "60s"
}
```

Headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1762862880
```

## Monitoring Endpoints

### Get Configuration
```bash
GET /api/rate-limits/config
```

Response:
```json
{
  "use_redis": true,
  "redis_available": true,
  "fallback_to_memory": true,
  "include_headers": true,
  "endpoints_configured": 25
}
```

### Get Your Rate Limit Status
```bash
GET /api/rate-limits/status
```

Response:
```json
{
  "client_identifier": "127.0.0.1",
  "tier": "anonymous",
  "backend": "redis",
  "limits": [
    {
      "endpoint": "/health",
      "tier": "anonymous",
      "limit": 120,
      "window_seconds": 60,
      "remaining": 115,
      "reset_time": 1762862880,
      "retry_after": 45
    }
    // ... more endpoints
  ]
}
```

### Check Specific Endpoint Limit
```bash
GET /api/rate-limits/check/api/stock-price
```

Response:
```json
{
  "endpoint": "/api/stock-price",
  "tier": "anonymous",
  "allowed": true,
  "limit": 60,
  "remaining": 58,
  "window_seconds": 60,
  "reset_time": 1762862880,
  "retry_after": 45
}
```

### List All Limits
```bash
GET /api/rate-limits/limits
```

Returns comprehensive list of all rate limits for all tiers.

## Testing

Run the test suite:

```bash
cd backend
python3 test_rate_limiting.py
```

Test output:
```
=== Test 1: Basic Rate Limiting (Anonymous User) ===
Request 1: Status 200, Remaining: 119, Limit: 120
✅ Basic rate limiting works

=== Test 4: Admin Bypass ===
✅ Admin made 150 requests without being rate limited

======================================================================
✅ TEST SUITE COMPLETED
======================================================================
```

## Customizing Rate Limits

Edit `backend/config/rate_limits.py`:

```python
# Increase market data limits for all tiers
MARKET_DATA_LIMITS = {
    UserTier.ANONYMOUS: RateLimit(requests=100, window_seconds=60),  # Was 60
    UserTier.AUTHENTICATED: RateLimit(requests=200, window_seconds=60),  # Was 120
    UserTier.PREMIUM: RateLimit(requests=500, window_seconds=60),  # Was 300
}
```

Changes take effect immediately (no restart needed with auto-reload).

## Performance

### In-Memory Backend
- **Response time**: <1ms additional latency
- **Memory usage**: ~100 bytes per active bucket
- **Cleanup**: Automatic every 100 requests
- **Suitable for**: Single-server deployments, development

### Redis Backend
- **Response time**: ~2-5ms additional latency
- **Memory usage**: ~200 bytes per bucket in Redis
- **Persistence**: Survives server restarts
- **Suitable for**: Multi-server deployments, production

## Troubleshooting

### Rate Limiting Not Working

1. **Check middleware is enabled:**
   ```bash
   curl http://localhost:8000/health -v | grep X-RateLimit
   ```
   Should see `X-RateLimit-*` headers.

2. **Check Redis connection (if using Redis):**
   ```bash
   curl http://localhost:8000/api/rate-limits/config
   ```
   Check `redis_available` field.

3. **Check logs:**
   ```bash
   tail -f logs/app.log | grep rate
   ```

### Redis Connection Failed

System automatically falls back to in-memory backend:
```
WARNING: Redis not available: Connection refused. Falling back to in-memory rate limiting
INFO: Rate limiter using in-memory backend
```

### Admin Bypass Not Working

1. **Set ADMIN_API_KEY environment variable:**
   ```bash
   export ADMIN_API_KEY=your_secret_key
   ```

2. **Use correct header:**
   ```bash
   curl -H "X-Admin-Key: your_secret_key" http://localhost:8000/health
   ```

3. **For testing, use tier header:**
   ```bash
   curl -H "X-User-Tier: admin" http://localhost:8000/health
   ```

## Security Considerations

1. **Admin Key Security:**
   - Never commit `ADMIN_API_KEY` to git
   - Use strong, random keys (min 32 characters)
   - Rotate keys periodically
   - Use secrets management (Fly.io Secrets, AWS Secrets Manager, etc.)

2. **IP Spoofing Protection:**
   - Rate limiting uses `X-Forwarded-For` header
   - Only trust proxy headers in production behind trusted proxy
   - Consider implementing IP whitelist for admin access

3. **DDoS Protection:**
   - Rate limiting helps but is not a complete DDoS solution
   - Use CloudFlare or similar CDN for full DDoS protection
   - Consider implementing progressive delays (exponential backoff)

## Future Enhancements

### Planned Features
- [ ] JWT-based tier detection
- [ ] Database-backed user tier management
- [ ] Custom rate limits per API key
- [ ] Rate limit analytics dashboard
- [ ] Webhook notifications on rate limit exceeded
- [ ] Distributed rate limiting with Redis Cluster
- [ ] Geographic rate limiting (different limits per region)

### Possible Improvements
- [ ] Token bucket algorithm for burst handling
- [ ] Sliding window counters for smoother limits
- [ ] Rate limit warnings (at 80% capacity)
- [ ] GraphQL rate limiting by query complexity
- [ ] WebSocket connection duration limits

## References

- Configuration: `backend/config/rate_limits.py`
- Middleware: `backend/middleware/rate_limiter.py`
- Router: `backend/routers/rate_limit_router.py`
- Tests: `backend/test_rate_limiting.py`
- Main integration: `backend/mcp_server.py`

## Support

For issues or questions:
1. Check logs: `tail -f logs/app.log`
2. Run tests: `python3 test_rate_limiting.py`
3. Check monitoring endpoints: `/api/rate-limits/status`
4. Review this documentation
5. Open GitHub issue with logs and configuration
