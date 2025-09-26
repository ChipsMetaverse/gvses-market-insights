# Cache Architecture Documentation

## Overview

The knowledge retrieval system implements a **per-process, in-memory cache** for optimizing repeated queries. This cache significantly improves response times for frequently asked questions but has important limitations in distributed deployments.

## Cache Implementation

### Current Architecture (In-Memory)

```python
# Location: backend/services/agent_orchestrator.py

class AgentOrchestrator:
    def __init__(self):
        # Knowledge cache with bounds and thread safety
        self._knowledge_cache = OrderedDict()  # LRU cache
        self._cache_ttl = 300  # 5 minutes TTL
        self._cache_max_size = 100  # Maximum cache entries
        self._cache_lock = asyncio.Lock()  # Thread safety
```

### Features

1. **LRU Eviction**: Least Recently Used eviction when cache exceeds 100 entries
2. **TTL Expiration**: Entries expire after 5 minutes
3. **Thread Safety**: asyncio.Lock prevents race conditions
4. **Bounded Size**: Prevents unbounded memory growth

### Performance Characteristics

- **Cache Hit**: <50ms response time
- **Cache Miss**: 200-500ms (embedding + retrieval)
- **Hit Rate**: ~30-50% on single machine
- **Memory Usage**: ~10-20MB at max capacity

## Distributed Deployment Limitations

⚠️ **IMPORTANT**: In multi-machine deployments (e.g., Fly.io with multiple regions), the cache is **per-machine only**.

### What This Means

```
User Request 1 → Machine A → Cache Miss → Store in Machine A's cache
User Request 2 → Machine B → Cache Miss → Store in Machine B's cache
User Request 3 → Machine A → Cache Hit! → Fast response
User Request 4 → Machine C → Cache Miss → Store in Machine C's cache
```

### Impact on Production

- **Limited Hit Rate**: With N machines, effective hit rate ≈ single_machine_hit_rate / N
- **Cold Starts**: New machines start with empty caches
- **Regional Variance**: Different regions build different cache patterns

## Redis Implementation (Recommended for Production)

For true distributed caching, implement Redis:

### 1. Install Dependencies

```bash
pip install redis aioredis
```

### 2. Environment Configuration

```env
REDIS_URL=redis://localhost:6379
REDIS_CACHE_TTL=300
REDIS_MAX_CONNECTIONS=10
```

### 3. Implementation Example

```python
import aioredis
import json

class DistributedCache:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        
    async def get(self, key: str) -> Optional[str]:
        value = await self.redis.get(key)
        return json.loads(value) if value else None
        
    async def set(self, key: str, value: Any, ttl: int = 300):
        await self.redis.setex(
            key, 
            ttl, 
            json.dumps(value)
        )
```

### 4. Fly.io Redis Setup

```toml
# fly.toml
[env]
  REDIS_URL = "redis://your-redis.fly.dev:6379"

[services]
  [[services.ports]]
    handlers = ["tls", "http"]
    port = 8080
```

## Monitoring & Metrics

### Cache Metrics to Track

```python
class CacheMetrics:
    - cache_hits: Counter
    - cache_misses: Counter
    - cache_evictions: Counter
    - avg_retrieval_time: Histogram
    - cache_size: Gauge
```

### Monitoring Endpoints

```
GET /metrics/cache
{
  "hit_rate": 0.45,
  "total_hits": 1234,
  "total_misses": 2756,
  "cache_size": 87,
  "avg_hit_time_ms": 12,
  "avg_miss_time_ms": 234
}
```

## Migration Path

### Phase 1: Current (In-Memory)
- ✅ Implemented
- Good for single-instance or low-traffic deployments
- Sufficient for development and staging

### Phase 2: Hybrid (In-Memory + Redis)
- Local cache for ultra-fast hits
- Redis for distributed cache
- Write-through pattern

### Phase 3: Redis-Only
- Simplified architecture
- Consistent performance across all machines
- Required for high-traffic production

## Configuration Recommendations

### Development
```python
CACHE_TYPE = "memory"
CACHE_MAX_SIZE = 100
CACHE_TTL = 300
```

### Staging
```python
CACHE_TYPE = "memory"
CACHE_MAX_SIZE = 500
CACHE_TTL = 600
```

### Production
```python
CACHE_TYPE = "redis"
REDIS_URL = "redis://production-redis:6379"
CACHE_TTL = 300
REDIS_POOL_SIZE = 20
```

## Troubleshooting

### Low Hit Rate in Production

1. **Check Machine Count**: More machines = lower per-machine hit rate
2. **Analyze Query Patterns**: Are queries well-distributed or concentrated?
3. **Consider Sticky Sessions**: Route users to same machine (trade-off with load balancing)

### Memory Issues

1. **Reduce cache_max_size**: Lower from 100 to 50
2. **Decrease TTL**: Lower from 300s to 180s
3. **Monitor cache_size metric**: Ensure eviction is working

### Performance Degradation

1. **Check lock contention**: Too many concurrent requests?
2. **Verify TTL expiration**: Are expired entries being removed?
3. **Monitor eviction rate**: Too aggressive eviction?

## Future Enhancements

1. **Compression**: Compress cached knowledge (zlib/lz4)
2. **Warming**: Pre-populate cache with common queries
3. **Tiered Caching**: L1 (memory) + L2 (Redis) + L3 (disk)
4. **Smart Eviction**: ML-based eviction policies
5. **Regional Affinity**: Route queries to machines with warm caches

## Key Takeaways

✅ **Current implementation is production-ready for single-instance deployments**

⚠️ **Multi-machine deployments will see reduced cache effectiveness**

🎯 **Redis implementation recommended for production scale**

📊 **Monitor cache metrics to optimize configuration**

---

For questions or issues, contact the engineering team or file an issue in the repository.