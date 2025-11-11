"""
Prometheus Metrics Middleware
==============================
Comprehensive metrics collection for OpenAI Platform Hardening.

Sprint 1, Day 2: Prometheus Metrics & Observability

Metrics Categories:
- Request latency and throughput
- Model routing decisions
- Prompt cache performance
- Cost tracking
- Tool execution
- Error rates
"""

import time
import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Info,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
)

logger = logging.getLogger(__name__)

# Create custom registry (allows multiple registries in tests)
registry = CollectorRegistry()


def get_registry() -> CollectorRegistry:
    """Return the Prometheus registry used for metrics export."""
    return registry

# ====================
# REQUEST METRICS
# ====================

# Total requests counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

# Request duration histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
    registry=registry
)

# Request size
http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000),
    registry=registry
)

# Response size
http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    buckets=(100, 1000, 10000, 100000, 1000000),
    registry=registry
)

# ====================
# MODEL ROUTING METRICS
# ====================

# Model selection counter
model_selections_total = Counter(
    'model_selections_total',
    'Total model selections by ModelRouter',
    ['intent', 'model', 'tier'],
    registry=registry
)

# Model fallback counter
model_fallbacks_total = Counter(
    'model_fallbacks_total',
    'Model routing fallbacks',
    ['intent', 'reason'],
    registry=registry
)

# Model routing latency
model_routing_duration_seconds = Histogram(
    'model_routing_duration_seconds',
    'Model routing decision latency',
    ['intent'],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05),
    registry=registry
)

# ====================
# PROMPT CACHE METRICS
# ====================

# Cache operations counter
prompt_cache_operations_total = Counter(
    'prompt_cache_operations_total',
    'Prompt cache operations',
    ['operation', 'result'],  # operation: get/put, result: hit/miss/success
    registry=registry
)

# Cache size gauge
prompt_cache_size = Gauge(
    'prompt_cache_size',
    'Current prompt cache size',
    registry=registry
)

# Cache hit rate gauge
prompt_cache_hit_rate = Gauge(
    'prompt_cache_hit_rate',
    'Prompt cache hit rate',
    registry=registry
)

# Cache evictions counter
prompt_cache_evictions_total = Counter(
    'prompt_cache_evictions_total',
    'Total cache evictions',
    registry=registry
)

# ====================
# OPENAI API METRICS
# ====================

# OpenAI API calls counter
openai_api_calls_total = Counter(
    'openai_api_calls_total',
    'Total OpenAI API calls',
    ['model', 'endpoint', 'intent', 'stream'],
    registry=registry
)

# OpenAI API latency
openai_api_duration_seconds = Histogram(
    'openai_api_duration_seconds',
    'OpenAI API call latency',
    ['model', 'endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0),
    registry=registry
)

# Token usage histogram
openai_tokens_used = Histogram(
    'openai_tokens_used',
    'Tokens used per request',
    ['model', 'token_type'],  # token_type: prompt/completion/total/cached
    buckets=(10, 50, 100, 500, 1000, 5000, 10000, 50000),
    registry=registry
)

# ====================
# COST TRACKING METRICS
# ====================

# Cost per request histogram
openai_cost_usd = Histogram(
    'openai_cost_usd',
    'OpenAI API cost in USD',
    ['model', 'intent'],
    buckets=(0.00001, 0.0001, 0.001, 0.01, 0.1, 1.0, 10.0),
    registry=registry
)

# Total cost counter
openai_total_cost_usd = Counter(
    'openai_total_cost_usd',
    'Total OpenAI API costs in USD',
    ['model'],
    registry=registry
)

# Cost savings from routing
cost_savings_usd = Counter(
    'cost_savings_usd',
    'Estimated cost savings from model routing',
    ['intent'],
    registry=registry
)

# ====================
# TOOL EXECUTION METRICS
# ====================

# Tool calls counter
tool_calls_total = Counter(
    'tool_calls_total',
    'Total tool executions',
    ['tool_name', 'status'],
    registry=registry
)

# Tool execution latency
tool_execution_duration_seconds = Histogram(
    'tool_execution_duration_seconds',
    'Tool execution latency',
    ['tool_name'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=registry
)

# ====================
# ERROR METRICS
# ====================

# Error counter
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint'],
    registry=registry
)

# OpenAI error counter
openai_errors_total = Counter(
    'openai_errors_total',
    'OpenAI API errors',
    ['model', 'error_type'],
    registry=registry
)

# ====================
# STREAMING METRICS
# ====================

# SSE connections
sse_connections_active = Gauge(
    'sse_connections_active',
    'Active SSE connections',
    registry=registry
)

# Chunk timing
sse_chunk_duration_seconds = Histogram(
    'sse_chunk_duration_seconds',
    'SSE chunk interval timing',
    ['endpoint'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0),
    registry=registry
)

# Time to first byte (TTFB)
sse_ttfb_seconds = Histogram(
    'sse_ttfb_seconds',
    'Time to first SSE chunk',
    ['endpoint'],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0),
    registry=registry
)

# ====================
# SYSTEM INFO
# ====================

# Service info
service_info = Info(
    'service_info',
    'Service version and configuration',
    registry=registry
)

# Set service info (should be called once at startup)
service_info.info({
    'version': '1.0.0',
    'service': 'claude-voice-mcp',
    'component': 'backend'
})


# ====================
# MIDDLEWARE
# ====================

class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for Prometheus metrics collection.

    Automatically tracks:
    - Request/response metrics
    - Latency
    - Status codes
    - Error rates
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        # Start timing
        start_time = time.perf_counter()

        # Extract path and method
        path = request.url.path
        method = request.method

        # Normalize endpoint (remove IDs, etc.)
        endpoint = self._normalize_endpoint(path)

        # Track request size
        content_length = request.headers.get('content-length', 0)
        if content_length:
            try:
                http_request_size_bytes.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(int(content_length))
            except (ValueError, TypeError):
                pass

        # Process request
        status_code = 500  # Default to error
        response = None

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Track response size
            if hasattr(response, 'headers'):
                response_length = response.headers.get('content-length', 0)
                if response_length:
                    try:
                        http_response_size_bytes.labels(
                            method=method,
                            endpoint=endpoint
                        ).observe(int(response_length))
                    except (ValueError, TypeError):
                        pass

            return response

        except Exception as e:
            # Track errors
            errors_total.labels(
                error_type=type(e).__name__,
                endpoint=endpoint
            ).inc()
            raise

        finally:
            # Track request metrics
            duration = time.perf_counter() - start_time

            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()

            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

    def _normalize_endpoint(self, path: str) -> str:
        """
        Normalize endpoint path for consistent metrics.

        Examples:
        - /api/stock-price?symbol=TSLA -> /api/stock-price
        - /api/user/123/profile -> /api/user/{id}/profile
        """
        # Remove query parameters
        if '?' in path:
            path = path.split('?')[0]

        # Common normalization patterns
        path = path.rstrip('/')

        # Replace UUIDs and IDs with placeholders
        import re
        # UUID pattern
        path = re.sub(
            r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '/{uuid}',
            path,
            flags=re.IGNORECASE
        )
        # Numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)

        return path


# ====================
# METRICS EXPORT
# ====================

def get_metrics() -> bytes:
    """
    Generate Prometheus metrics in text format.

    Returns:
        bytes: Prometheus metrics in text format
    """
    return generate_latest(registry)


def get_metrics_content_type() -> str:
    """Get the content type for Prometheus metrics."""
    return CONTENT_TYPE_LATEST
