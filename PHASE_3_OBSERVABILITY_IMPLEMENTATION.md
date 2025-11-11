# Phase 3: Observability Infrastructure - Implementation Guide

**Status**: 🟡 In Progress (25% Complete)
**Started**: January 2025
**Goal**: Production-grade monitoring with distributed tracing

---

## Overview

Implementing comprehensive observability infrastructure to gain full visibility into the OpenAI integration performance, costs, and errors. This phase builds the foundation for optimization and debugging.

---

## ✅ Completed: Request ID Propagation

### Implementation Summary

**Goal**: Enable end-to-end request tracing across frontend → backend → OpenAI

**Files Created**:
- `backend/utils/request_context.py` - Request ID utilities and context management

**Files Modified**:
- `backend/routers/agent_router.py` - Request ID extraction and propagation
- `backend/services/agent_orchestrator.py` - Request ID parameter support

### Features Implemented

#### 1. Request ID Generation
```python
from utils.request_context import generate_request_id

# Generates: "req_xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
request_id = generate_request_id()
```

#### 2. Header Extraction
```python
# In agent_router.py
request_id = request.headers.get("X-Request-ID") or generate_request_id()
```

#### 3. Context Propagation
```python
# Thread-safe context variable
set_request_id(request_id)  # Set for current async context
get_request_id()  # Get from anywhere in request scope
```

#### 4. Logging Integration
```python
# Automatic request ID in all logs
from utils.request_context import RequestIDFilter

handler.addFilter(RequestIDFilter())
# All logs now include: request_id='req_xxxxx'
```

#### 5. Response Headers
```python
# AgentResponse model includes request_id field
{
  "text": "...",
  "request_id": "req_xxxxxxxx...",
  ...
}
```

### Usage

**Frontend (JavaScript/TypeScript)**:
```typescript
// Generate and send request ID
const requestId = `req_${crypto.randomUUID()}`;

fetch('/api/agent/orchestrate', {
  method: 'POST',
  headers: {
    'X-Request-ID': requestId,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ query: '...' })
});
```

**Backend Logging**:
```python
# All logs automatically include request_id
logger.info("Processing query", extra={"request_id": request_id})
# Output: INFO Processing query request_id=req_xxxxx
```

**Request Flow**:
1. Frontend generates UUID → `X-Request-ID` header
2. Router extracts header → `set_request_id()`
3. Orchestrator receives `request_id` parameter
4. All logs include `request_id` via filter
5. Response includes `request_id` for correlation

### Benefits

✅ **End-to-End Tracing**: Track request from frontend through all backend layers
✅ **Log Correlation**: Grep logs by request ID to see complete flow
✅ **Error Debugging**: Quickly find all logs related to failed request
✅ **Performance Analysis**: Track latency across services for specific request

### Testing

```bash
# Test request ID propagation
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "X-Request-ID: req_test-12345" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is AAPL price?", "stream": false}'

# Verify response includes request_id
# Check logs show: request_id=req_test-12345
```

---

## ✅ Completed: Cost Tracking

### Implementation Summary

**Goal**: Track token usage and costs per request with attribution tags.

**Files Created**:
- `backend/models/cost_record.py` - Pydantic models for cost tracking
- `backend/services/cost_tracker.py` - Cost calculation and storage service

**Files Modified**:
- `backend/services/agent_orchestrator.py` - Cost tracking integration

### Features Implemented

#### 1. Cost Tracking Models
```python
from models.cost_record import TokenUsage, CostTags, CostRecord, CostSummary, TimeWindow

# Token usage with caching support
TokenUsage(
    prompt_tokens=150,
    completion_tokens=50,
    total_tokens=200,
    cached_tokens=100  # Prompt caching savings
)

# Attribution tags
CostTags(
    endpoint="/api/agent/orchestrate",
    session_id="session_123",
    user_id="user_456",
    intent="price-only",
    tools_used=["get_stock_quote"],
    stream=False
)
```

#### 2. Cost Calculation Service
- **Model Pricing**: Comprehensive pricing for all OpenAI models (gpt-4o-mini, gpt-4o, gpt-5, o1, etc.)
- **Prompt Caching**: Tracks cached tokens and calculates 50% savings
- **Attribution**: Tags costs by endpoint, intent, tools, session, user
- **In-Memory Storage**: 10,000 record limit with FIFO eviction

#### 3. Automatic Cost Recording
All OpenAI API calls now automatically record costs:
- `_process_query_single_pass()` - Single-pass chat completions (2 API calls)
- `_process_query_chat()` - Legacy chat completions (1 API call)
- `_process_query_responses()` - Responses API (3 API calls)

#### 4. Cost Tracking Helper
```python
self._record_api_cost(
    response=api_response,
    model="gpt-4o-mini",
    request_id=request_id,
    endpoint="/api/agent/orchestrate",
    intent="price-only",
    tools_used=["get_stock_quote"],
    stream=False
)
# Automatically:
# - Extracts token usage
# - Calculates costs
# - Records with attribution
# - Logs cost summary
```

#### 5. Cost Summaries
```python
cost_tracker = get_cost_tracker()

# Get daily summary
summary = cost_tracker.get_summary(TimeWindow.DAY)
# Returns: CostSummary with total_cost_usd, cost_by_model, cost_by_endpoint,
#          cost_by_intent, cache_hit_rate, total_cached_savings_usd

# Get total cost
total = cost_tracker.get_total_cost()

# Get recent records
records = cost_tracker.get_recent_records(limit=100)

# Get statistics
stats = cost_tracker.get_stats()
```

### Usage Example

**Automatic cost tracking happens on every OpenAI API call**:

```python
# User makes request with X-Request-ID header
# → Frontend: fetch('/api/agent/orchestrate', {
#       headers: { 'X-Request-ID': 'req_abc123' }
#     })
# → Router extracts request_id and passes to orchestrator
# → Orchestrator calls OpenAI API
# → _record_api_cost() automatically called with response
# → Cost tracked with full attribution

# Later, query costs:
cost_tracker = get_cost_tracker()
summary = cost_tracker.get_summary(TimeWindow.HOUR)
print(f"Hourly cost: ${summary.total_cost_usd:.6f}")
print(f"Cached savings: ${summary.total_cached_savings_usd:.6f}")
print(f"Cache hit rate: {summary.cache_hit_rate:.2%}")
```

### Benefits

✅ **Cost Visibility**: See exactly how much each request costs
✅ **Attribution**: Track costs by endpoint, intent, user, session
✅ **Prompt Caching**: Measure 50% savings from cached tokens
✅ **Aggregation**: View costs by hour/day/week/month
✅ **Model Insights**: Compare costs across models
✅ **Budget Planning**: Historical data for forecasting

### Testing

Cost tracking is automatically tested on every API call. To verify:

```bash
# Make a test query
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "X-Request-ID: req_test-cost" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is AAPL price?",
    "stream": false
  }'

# Check logs for cost recording:
# INFO Cost recorded: $0.000123 (200 tokens, 100 cached) request_id=req_test-cost
```

---

## ✅ Completed: /api/agent/costs Endpoints

### Implementation Summary

**Goal**: Create FastAPI endpoints to expose cost data to frontend.

**Files Modified**:
- `backend/routers/agent_router.py` - Added three cost tracking endpoints

### Endpoints Implemented

#### 1. GET /api/agent/costs/summary
Get cost summary for a time window.

**Query Parameters**:
- `window` (optional): Time window - "hour", "day", "week", "month", "custom" (default: "day")
- `start_time` (optional): ISO datetime for custom window start
- `end_time` (optional): ISO datetime for custom window end

**Response Example**:
```json
{
  "period_start": "2025-01-10T00:00:00",
  "period_end": "2025-01-11T00:00:00",
  "total_requests": 245,
  "total_tokens": 48500,
  "total_cost_usd": 0.073200,
  "avg_cost_per_request_usd": 0.000299,
  "cost_by_model": {
    "gpt-4o-mini": 0.065400,
    "gpt-4o": 0.007800
  },
  "cost_by_endpoint": {
    "/api/agent/orchestrate": 0.072000,
    "/api/agent/stream": 0.001200
  },
  "cost_by_intent": {
    "price-only": 0.045000,
    "technical": 0.028200
  },
  "total_cached_savings_usd": 0.012300,
  "cache_hit_rate": 0.4200
}
```

#### 2. GET /api/agent/costs/stats
Get overall cost tracking statistics.

**Response Example**:
```json
{
  "total_records": 2458,
  "total_cost_usd": 1.234500,
  "total_tokens": 456000,
  "total_cached_savings_usd": 0.123450,
  "models_used": ["gpt-4o-mini", "gpt-4o", "gpt-5-mini"],
  "oldest_record": "2025-01-01T00:00:00",
  "newest_record": "2025-01-10T23:59:59"
}
```

#### 3. GET /api/agent/costs/recent
Get recent cost records with detailed attribution.

**Query Parameters**:
- `limit` (optional): Number of records (default: 100, max: 1000)

**Response Example**:
```json
[
  {
    "request_id": "req_abc123",
    "timestamp": "2025-01-10T12:34:56",
    "model": "gpt-4o-mini",
    "tokens": {
      "prompt_tokens": 150,
      "completion_tokens": 50,
      "total_tokens": 200,
      "cached_tokens": 100
    },
    "cost_usd": 0.000120,
    "input_cost_usd": 0.000030,
    "output_cost_usd": 0.000090,
    "cached_savings_usd": 0.000015,
    "tags": {
      "endpoint": "/api/agent/orchestrate",
      "session_id": "session_123",
      "user_id": "user_456",
      "intent": "price-only",
      "tools_used": ["get_stock_quote"],
      "stream": false
    }
  }
]
```

### Usage Examples

**Daily Cost Summary**:
```bash
curl http://localhost:8000/api/agent/costs/summary?window=day
```

**Custom Time Range**:
```bash
curl "http://localhost:8000/api/agent/costs/summary?window=custom&start_time=2025-01-01T00:00:00Z&end_time=2025-01-10T23:59:59Z"
```

**Overall Statistics**:
```bash
curl http://localhost:8000/api/agent/costs/stats
```

**Recent 50 Records**:
```bash
curl "http://localhost:8000/api/agent/costs/recent?limit=50"
```

### Benefits

✅ **Real-time Cost Visibility**: See costs as they accumulate
✅ **Historical Analysis**: Trend analysis over hours/days/weeks/months
✅ **Budget Tracking**: Monitor spending against budgets
✅ **Attribution**: Track costs by user, session, intent, endpoint
✅ **Cache Optimization**: Monitor cache hit rates and savings
✅ **Model Comparison**: Compare costs across different models

---

## ⏳ Pending: Error Taxonomy

### Goal
Categorize and aggregate errors for better monitoring and alerting.
```python
# In agent_orchestrator.py
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cached_tokens: int = 0

# Extract from OpenAI response
usage = response.usage
token_usage = TokenUsage(
    prompt_tokens=usage.prompt_tokens,
    completion_tokens=usage.completion_tokens,
    total_tokens=usage.total_tokens
)
```

#### 2. Cost Calculation
```python
# Model pricing (per 1M tokens)
MODEL_PRICING = {
    "gpt-4o-mini": {
        "input": 0.150,
        "output": 0.600,
        "cached_input": 0.075
    },
    "gpt-4o": {
        "input": 2.50,
        "output": 10.00,
        "cached_input": 1.25
    },
    "gpt-5": {
        "input": 3.00,
        "output": 12.00,
        "cached_input": 1.50
    }
}

def calculate_cost(model: str, usage: TokenUsage) -> float:
    pricing = MODEL_PRICING[model]
    input_cost = (usage.prompt_tokens / 1_000_000) * pricing["input"]
    output_cost = (usage.completion_tokens / 1_000_000) * pricing["output"]
    cached_cost = (usage.cached_tokens / 1_000_000) * pricing["cached_input"]
    return input_cost + output_cost - cached_cost
```

#### 3. Attribution Tags
```python
# Tag costs by dimensions
cost_record = {
    "request_id": request_id,
    "timestamp": datetime.utcnow(),
    "model": "gpt-4o-mini",
    "tokens": {
        "prompt": 150,
        "completion": 50,
        "cached": 100,
        "total": 200
    },
    "cost_usd": 0.00012,
    "tags": {
        "endpoint": "/api/agent/orchestrate",
        "session_id": "session_123",
        "user_id": "user_456",
        "intent": "price-only",
        "tools_used": ["get_stock_quote"]
    }
}
```

#### 4. Cost Storage
- Option A: In-memory cache with periodic flush
- Option B: SQLite database (simple, no dependencies)
- Option C: PostgreSQL (production-ready)

**Recommended**: Start with SQLite, migrate to PostgreSQL if needed

### Files to Create

```
backend/services/cost_tracker.py      # Cost calculation and storage
backend/models/cost_record.py          # Pydantic model for cost records
backend/routers/cost_router.py         # /api/agent/costs endpoint
backend/db/cost_db.py                  # SQLite database operations
```

---

## ⏳ Pending: Error Taxonomy

### Goal
Categorize and aggregate errors for better monitoring and alerting.

### Error Categories

```python
class ErrorCategory(Enum):
    RATE_LIMIT = "rate_limit"           # OpenAI rate limit
    TIMEOUT = "timeout"                 # Request timeout
    VALIDATION = "validation"           # Input validation
    TOOL_ERROR = "tool_error"          # Tool execution failed
    STREAM_ERROR = "stream_error"       # SSE stream error
    AUTHENTICATION = "authentication"   # API key invalid
    UNKNOWN = "unknown"                 # Uncategorized error
```

### Error Tracking

```python
# backend/services/error_tracker.py
class ErrorTracker:
    def record_error(
        self,
        request_id: str,
        category: ErrorCategory,
        error: Exception,
        context: Dict[str, Any]
    ):
        error_record = {
            "request_id": request_id,
            "timestamp": datetime.utcnow(),
            "category": category.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        # Store in database or metrics system
        ...
```

### Error Metrics

Track:
- Error count by category
- Error rate (errors/total requests)
- Error rate by endpoint
- Error rate by model
- Time to recovery (for retryable errors)

---

## ⏳ Pending: Prometheus Metrics Exporter

### Goal
Expose metrics in Prometheus format for Grafana dashboards.

### Metrics to Track

```python
# Request metrics
agent_requests_total{endpoint, model, intent}
agent_request_duration_seconds{endpoint, model, intent}
agent_tokens_total{model, type}  # type: prompt, completion, cached

# Error metrics
agent_errors_total{endpoint, category}
agent_error_rate{endpoint}

# Cost metrics
agent_cost_usd_total{model, endpoint}
agent_cost_per_request{model}

# Cache metrics
agent_cache_hit_rate{cache_type}  # type: knowledge, response, tool
agent_cache_size{cache_type}
```

### Implementation

```python
# backend/routers/metrics_router.py
from prometheus_client import Counter, Histogram, generate_latest

requests_total = Counter(
    'agent_requests_total',
    'Total requests to agent',
    ['endpoint', 'model', 'intent']
)

request_duration = Histogram(
    'agent_request_duration_seconds',
    'Request duration in seconds',
    ['endpoint', 'model']
)

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

---

## ⏳ Pending: OpenTelemetry Integration

### Goal
Distributed tracing with full instrumentation of request flow.

### Spans to Create

```
agent_request
├── intent_classification
├── tool_execution
│   ├── get_stock_quote
│   └── get_stock_news
├── openai_completion
│   ├── prompt_construction
│   └── response_parsing
└── chart_command_extraction
```

### Implementation

```python
# backend/utils/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

tracer = trace.get_tracer(__name__)

# In orchestrator
with tracer.start_as_current_span("agent_request") as span:
    span.set_attribute("request_id", request_id)
    span.set_attribute("query", query)

    with tracer.start_as_current_span("intent_classification"):
        intent = self.intent_router.classify_intent(query)
        span.set_attribute("intent", intent)

    # ... rest of processing
```

---

## ⏳ Pending: Grafana Dashboard

### Goal
Visualization of all metrics in a single dashboard.

### Dashboard Panels

1. **Request Volume**
   - Requests/second by endpoint
   - P50/P95/P99 latency
   - Success rate

2. **Model Usage**
   - Requests by model
   - Token usage by model
   - Cost by model

3. **Error Monitoring**
   - Error rate by category
   - Top error messages
   - Error trend over time

4. **Cost Analytics**
   - Cost per hour/day/week
   - Cost by endpoint
   - Cost savings from caching

5. **Cache Performance**
   - Cache hit rate
   - Cache size
   - Cache evictions

### Dashboard JSON

Will create `grafana_dashboard.json` with panel definitions.

---

## Success Metrics (Phase 3)

- ✅ Request ID in 100% of logs
- 🔄 Cost tracked per request (In Progress)
- ⏳ Error categorization for 100% of errors
- ⏳ Metrics endpoint returning data
- ⏳ Grafana dashboard operational
- ⏳ OpenTelemetry traces for all requests

---

## Timeline

| Task | Status | Estimated Completion |
|------|--------|---------------------|
| Request ID Propagation | ✅ Complete | Week 1 - Done |
| Cost Tracking | 🔄 In Progress | Week 1 |
| Error Taxonomy | ⏳ Pending | Week 2 |
| Prometheus Metrics | ⏳ Pending | Week 2 |
| OpenTelemetry | ⏳ Pending | Week 3 |
| Grafana Dashboard | ⏳ Pending | Week 3 |

**Phase 3 Completion Target**: End of Week 3

---

## Next Steps

1. **Complete Cost Tracking** (Current Priority)
   - Implement token usage extraction
   - Add cost calculation
   - Create SQLite storage
   - Build `/api/agent/costs` endpoint

2. **Error Taxonomy**
   - Define error categories
   - Create error tracker service
   - Integrate with existing error handling

3. **Metrics Exporter**
   - Add prometheus_client dependency
   - Implement metrics collectors
   - Create /api/metrics endpoint

4. **OpenTelemetry**
   - Add OpenTelemetry dependencies
   - Instrument key code paths
   - Configure OTLP exporter

5. **Grafana Dashboard**
   - Create dashboard JSON
   - Document setup instructions
   - Test all panels with live data
