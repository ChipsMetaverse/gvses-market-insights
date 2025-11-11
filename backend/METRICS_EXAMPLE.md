# Prometheus Metrics Output Example

This document shows what the `/metrics` endpoint returns.

## Example Output

When you visit `http://localhost:8000/metrics`, you'll see output like this:

```prometheus
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health",status="200"} 42.0
http_requests_total{method="POST",endpoint="/ask",status="200"} 15.0
http_requests_total{method="GET",endpoint="/api/stock-price",status="200"} 8.0

# HELP http_request_duration_seconds HTTP request latency in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="POST",endpoint="/ask",le="0.01"} 0.0
http_request_duration_seconds_bucket{method="POST",endpoint="/ask",le="0.05"} 2.0
http_request_duration_seconds_bucket{method="POST",endpoint="/ask",le="0.1"} 5.0
http_request_duration_seconds_bucket{method="POST",endpoint="/ask",le="0.5"} 12.0
http_request_duration_seconds_bucket{method="POST",endpoint="/ask",le="1.0"} 15.0
http_request_duration_seconds_sum{method="POST",endpoint="/ask"} 4.523
http_request_duration_seconds_count{method="POST",endpoint="/ask"} 15.0

# HELP model_selections_total Total model selections by ModelRouter
# TYPE model_selections_total counter
model_selections_total{intent="price_only",model="gpt-4o-mini",tier="cheap"} 8.0
model_selections_total{intent="technical_analysis",model="gpt-4o",tier="mid"} 5.0
model_selections_total{intent="general_query",model="gpt-4o",tier="mid"} 2.0

# HELP model_fallbacks_total Model routing fallbacks
# TYPE model_fallbacks_total counter
model_fallbacks_total{intent="price_only",reason="fallback_index_1"} 1.0

# HELP model_routing_duration_seconds Model routing decision latency
# TYPE model_routing_duration_seconds histogram
model_routing_duration_seconds_bucket{intent="price_only",le="0.0001"} 5.0
model_routing_duration_seconds_bucket{intent="price_only",le="0.0005"} 8.0
model_routing_duration_seconds_bucket{intent="price_only",le="0.001"} 8.0
model_routing_duration_seconds_sum{intent="price_only"} 0.000634
model_routing_duration_seconds_count{intent="price_only"} 8.0

# HELP prompt_cache_operations_total Prompt cache operations
# TYPE prompt_cache_operations_total counter
prompt_cache_operations_total{operation="get",result="hit"} 10.0
prompt_cache_operations_total{operation="get",result="miss"} 5.0
prompt_cache_operations_total{operation="put",result="success"} 5.0

# HELP prompt_cache_size Current prompt cache size
# TYPE prompt_cache_size gauge
prompt_cache_size 5.0

# HELP prompt_cache_hit_rate Prompt cache hit rate
# TYPE prompt_cache_hit_rate gauge
prompt_cache_hit_rate 0.6667

# HELP openai_api_calls_total Total OpenAI API calls
# TYPE openai_api_calls_total counter
openai_api_calls_total{model="gpt-4o-mini",endpoint="/ask",intent="price_only",stream="false"} 8.0
openai_api_calls_total{model="gpt-4o",endpoint="/ask",intent="technical_analysis",stream="false"} 5.0

# HELP openai_tokens_used Tokens used per request
# TYPE openai_tokens_used histogram
openai_tokens_used_bucket{model="gpt-4o-mini",token_type="prompt",le="10"} 0.0
openai_tokens_used_bucket{model="gpt-4o-mini",token_type="prompt",le="50"} 3.0
openai_tokens_used_bucket{model="gpt-4o-mini",token_type="prompt",le="100"} 8.0
openai_tokens_used_sum{model="gpt-4o-mini",token_type="prompt"} 542.0
openai_tokens_used_count{model="gpt-4o-mini",token_type="prompt"} 8.0

openai_tokens_used_sum{model="gpt-4o-mini",token_type="completion"} 156.0
openai_tokens_used_count{model="gpt-4o-mini",token_type="completion"} 8.0

openai_tokens_used_sum{model="gpt-4o-mini",token_type="cached"} 120.0
openai_tokens_used_count{model="gpt-4o-mini",token_type="cached"} 3.0

# HELP openai_cost_usd OpenAI API cost in USD
# TYPE openai_cost_usd histogram
openai_cost_usd_bucket{model="gpt-4o-mini",intent="price_only",le="0.00001"} 0.0
openai_cost_usd_bucket{model="gpt-4o-mini",intent="price_only",le="0.0001"} 5.0
openai_cost_usd_bucket{model="gpt-4o-mini",intent="price_only",le="0.001"} 8.0
openai_cost_usd_sum{model="gpt-4o-mini",intent="price_only"} 0.001234
openai_cost_usd_count{model="gpt-4o-mini",intent="price_only"} 8.0

# HELP openai_total_cost_usd Total OpenAI API costs in USD
# TYPE openai_total_cost_usd counter
openai_total_cost_usd{model="gpt-4o-mini"} 0.001234
openai_total_cost_usd{model="gpt-4o"} 0.008765

# HELP errors_total Total errors
# TYPE errors_total counter
errors_total{error_type="ValueError",endpoint="/ask"} 1.0

# HELP service_info Service version and configuration
# TYPE service_info gauge
service_info{version="1.0.0",service="claude-voice-mcp",component="backend"} 1.0
```

## How to Read These Metrics

### Counters (always increase)
```prometheus
http_requests_total{method="GET",endpoint="/health",status="200"} 42.0
```
- **Meaning:** 42 successful GET requests to /health
- **Labels:** method, endpoint, status (for filtering)
- **Usage:** Track request volume, error counts, costs

### Histograms (distributions)
```prometheus
http_request_duration_seconds_sum{method="POST",endpoint="/ask"} 4.523
http_request_duration_seconds_count{method="POST",endpoint="/ask"} 15.0
```
- **Meaning:** 15 requests took 4.523 seconds total (avg: 0.30s)
- **Buckets:** le="0.1" shows how many were under 100ms
- **Usage:** Calculate percentiles (p50, p95, p99), averages

### Gauges (current values)
```prometheus
prompt_cache_hit_rate 0.6667
```
- **Meaning:** Current cache hit rate is 66.67%
- **Changes:** Goes up and down (not monotonic like counters)
- **Usage:** Track current state, rates, percentages

## Useful Prometheus Queries

### Average Request Latency
```promql
rate(http_request_duration_seconds_sum[5m]) /
rate(http_request_duration_seconds_count[5m])
```

### Requests Per Second
```promql
rate(http_requests_total[1m])
```

### Error Rate Percentage
```promql
100 * (
  sum(rate(http_requests_total{status=~"5.."}[5m])) /
  sum(rate(http_requests_total[5m]))
)
```

### Model Selection Distribution
```promql
sum by (model, tier) (model_selections_total)
```

### Cost Per Hour
```promql
rate(openai_total_cost_usd[1h]) * 3600
```

### Cache Hit Rate
```promql
prompt_cache_hit_rate * 100
```

### P99 Latency
```promql
histogram_quantile(0.99,
  rate(http_request_duration_seconds_bucket[5m])
)
```

## Grafana Dashboard Examples

### Panel 1: Requests Per Second
- **Type:** Graph
- **Query:** `rate(http_requests_total[1m])`
- **Legend:** `{{method}} {{endpoint}}`

### Panel 2: Model Selection Pie Chart
- **Type:** Pie Chart
- **Query:** `sum by (model) (model_selections_total)`
- **Legend:** `{{model}}`

### Panel 3: Cache Hit Rate Gauge
- **Type:** Gauge
- **Query:** `prompt_cache_hit_rate * 100`
- **Thresholds:** Green >70%, Yellow 50-70%, Red <50%

### Panel 4: Hourly Costs
- **Type:** Stat
- **Query:** `rate(openai_total_cost_usd[1h]) * 3600`
- **Unit:** USD
- **Format:** $0.0000

## Alerting Examples

### High Error Rate Alert
```yaml
- alert: HighErrorRate
  expr: |
    100 * (
      sum(rate(http_requests_total{status=~"5.."}[5m])) /
      sum(rate(http_requests_total[5m]))
    ) > 5
  for: 5m
  annotations:
    summary: "High error rate detected ({{ $value }}%)"
```

### High Cost Alert
```yaml
- alert: HighAPICost
  expr: rate(openai_total_cost_usd[1h]) * 3600 > 10
  for: 10m
  annotations:
    summary: "API costs exceeding $10/hour ({{ $value }})"
```

### Low Cache Hit Rate
```yaml
- alert: LowCacheHitRate
  expr: prompt_cache_hit_rate < 0.5
  for: 15m
  annotations:
    summary: "Cache hit rate below 50% ({{ $value }})"
```

## Testing Metrics

### 1. Generate Some Traffic
```bash
# Price queries (should use gpt-4o-mini)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the price of TSLA?"}'

# Technical analysis (should use gpt-4o)
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze NVDA with RSI and MACD"}'
```

### 2. View Metrics
```bash
curl http://localhost:8000/metrics
```

### 3. Filter Specific Metrics
```bash
# Just model selections
curl http://localhost:8000/metrics | grep model_selections

# Just costs
curl http://localhost:8000/metrics | grep cost

# Just cache metrics
curl http://localhost:8000/metrics | grep cache
```

### 4. Run Test Suite
```bash
python3 test_prometheus_metrics.py
```

This will:
- ✅ Verify metrics endpoint works
- ✅ Make sample API calls
- ✅ Confirm metrics are being recorded
- ✅ Validate Prometheus format

---

**For full documentation, see:** `SPRINT_1_DAY_2_COMPLETE.md`
