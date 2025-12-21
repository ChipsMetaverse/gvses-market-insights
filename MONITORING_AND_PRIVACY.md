# Monitoring, Analytics & Privacy Documentation

**GVSES Market Analysis Assistant**
**Last Updated**: November 11, 2025
**Version**: 2.0.3 (Sentry Integration)

---

## Table of Contents

1. [Overview](#overview)
2. [API Monitoring Infrastructure](#api-monitoring-infrastructure)
3. [User Tracking & Data Collection](#user-tracking--data-collection)
4. [Privacy & Security](#privacy--security)
5. [Data Access & Control](#data-access--control)
6. [Compliance Considerations](#compliance-considerations)
7. [Monitoring Endpoints Reference](#monitoring-endpoints-reference)

---

## Overview

The GVSES platform implements comprehensive monitoring and analytics with both first-party and third-party error tracking. Core analytics use Supabase (PostgreSQL) and Prometheus metrics, while error monitoring leverages Sentry for AI-assisted debugging.

**Key Principles:**
- ✅ First-party data collection for core analytics (Supabase + Prometheus)
- ✅ Third-party error tracking via Sentry (optional, configurable)
- ✅ Row Level Security (RLS) protects user data
- ✅ Prometheus-based observability for operations
- ✅ Optional authentication (anonymous usage supported)
- ⚠️ IP addresses and user agents are collected for security/debugging
- ⚠️ Sentry captures error context including stack traces and session replays

---

## API Monitoring Infrastructure

### 1. Prometheus Metrics (`/metrics`)

**Location**: `backend/middleware/metrics.py`

Comprehensive metrics collection for operational monitoring:

#### Request Metrics
- `http_requests_total{method, endpoint, status}` - Total HTTP requests
- `http_request_duration_seconds{method, endpoint}` - Request latency histogram
  - Buckets: 10ms, 50ms, 100ms, 500ms, 1s, 2.5s, 5s, 10s, 30s
- `http_request_size_bytes{method, endpoint}` - Request payload size
- `http_response_size_bytes{method, endpoint}` - Response payload size

#### Model & AI Metrics
- `model_selections_total{intent, model, tier}` - AI model routing decisions
- `model_fallbacks_total{intent, reason}` - Model routing fallbacks
- `model_routing_duration_seconds{intent}` - Model selection latency
- `openai_api_calls_total{model, endpoint, intent, stream}` - OpenAI API usage
- `openai_api_duration_seconds{model, endpoint}` - OpenAI response times
- `openai_tokens_used{model, token_type}` - Token consumption tracking
  - Types: prompt, completion, total, cached

#### Cost Tracking
- `openai_cost_usd{model, intent}` - Cost per request (USD)
- `openai_total_cost_usd{model}` - Cumulative API costs
- `cost_savings_usd{intent}` - Savings from intelligent routing

#### Cache Performance
- `prompt_cache_operations_total{operation, result}` - Cache hits/misses
- `prompt_cache_size` - Current cache size (gauge)
- `prompt_cache_hit_rate` - Cache hit percentage (gauge)
- `prompt_cache_evictions_total` - Cache eviction count

#### Tool Execution
- `tool_calls_total{tool_name, status}` - MCP tool usage
- `tool_execution_duration_seconds{tool_name}` - Tool performance

#### Error Tracking
- `errors_total{error_type, endpoint}` - Application errors
- `openai_errors_total{model, error_type}` - OpenAI API errors

#### Streaming Metrics
- `sse_connections_active` - Active SSE connections (gauge)
- `sse_chunk_duration_seconds{endpoint}` - Chunk interval timing
- `sse_ttfb_seconds{endpoint}` - Time to first byte

### 2. Sentry Error Monitoring (`sentry.io`)

**Integration**: November 11, 2025
**Configuration**: `frontend/src/config/sentry.ts`, `backend/config/sentry.py`

Third-party error tracking and performance monitoring via Sentry.io:

#### Frontend Error Tracking
**SDK**: `@sentry/react`
**Location**: `frontend/src/config/sentry.ts`

**Captured Data**:
- ✅ JavaScript errors and unhandled exceptions
- ✅ Browser console errors
- ✅ API request failures
- ✅ Performance metrics (page load, API latency)
- ⚠️ Session replays (video recordings of user interactions)
- ✅ Breadcrumbs (user actions leading to errors)
- ✅ User context (user ID, if authenticated)
- ⚠️ Custom error context (symbol, timeframe, component name)

**Sample Rates** (Production):
- Error capture: **100%** (all errors sent to Sentry)
- Performance tracing: **10%** (1 in 10 requests)
- Session replay (normal): **10%** (1 in 10 sessions)
- Session replay (on error): **100%** (all error sessions recorded)

**Privacy Controls**:
```typescript
beforeSend(event, hint) {
  // Filter expected WebSocket/ElevenLabs disconnections
  const error = hint.originalException;
  if (error && 'message' in error) {
    const message = String(error.message).toLowerCase();
    if (message.includes('websocket') || message.includes('elevenlabs')) {
      event.level = 'info'; // Downgrade to info level
    }
  }
  return event;
}
```

**Data Sent to Sentry**:
- Error messages and stack traces
- Browser version, OS, screen resolution
- URL of page where error occurred
- User ID (if authenticated) - **PII**
- IP address (Sentry automatic) - **PII**
- Session replay video (if error occurred) - **May contain PII**

#### Backend Error Tracking
**SDK**: `sentry-sdk` (Python)
**Location**: `backend/config/sentry.py`

**Captured Data**:
- ✅ Python exceptions and tracebacks
- ✅ FastAPI request failures (500 errors)
- ✅ API endpoint performance metrics
- ✅ Database query errors
- ✅ External API failures (Alpaca, ElevenLabs)
- ✅ Logging integration (ERROR level logs)
- ✅ Request context (endpoint, method, headers)
- ⚠️ User context (user ID, if authenticated)

**Sample Rates** (Production):
- Error capture: **100%** (all errors sent)
- Performance tracing: **10%** (1 in 10 requests)
- Performance profiling: **10%** (CPU/memory sampling)

**Privacy Controls**:
```python
def _before_send(event, hint):
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Filter expected rate limit errors
        if exc_type.__name__ == "RateLimitExceeded":
            event["level"] = "info"

        # Filter expected WebSocket disconnections
        if "websocket" in str(exc_value).lower():
            event["level"] = "info"

    return event
```

**Data Sent to Sentry**:
- Error messages and Python tracebacks
- Python version, OS, server hostname
- API endpoint and HTTP method
- Request headers (sanitized)
- User ID (if authenticated) - **PII**
- IP address (Sentry automatic) - **PII**

#### Sentry MCP Integration
**Status**: Configured, requires OAuth authentication
**URL**: `https://mcp.sentry.dev/mcp`

**Available Capabilities**:
- AI-assisted root cause analysis (Seer)
- Issue search and filtering
- Automated fix recommendations
- Project and DSN management
- Integration with Claude Code for debugging

**Privacy Implications**:
- ⚠️ Sentry MCP allows AI analysis of error data
- ⚠️ Error context may be sent to Sentry's Seer AI
- ✅ No additional data collection (uses existing Sentry data)

#### Sentry Data Retention
**Default Policy** (configured in Sentry dashboard):
- Error events: **90 days** (Sentry default)
- Performance data: **90 days**
- Session replays: **30 days**
- Aggregated statistics: **Indefinite**

**Data Location**:
- Sentry.io cloud (US or EU, configured during setup)
- Third-party service (not self-hosted)
- Subject to [Sentry Privacy Policy](https://sentry.io/privacy/)

#### Opt-Out Mechanism
**Current Status**: ⚠️ Not Implemented

Users cannot currently opt out of Sentry error tracking. To implement:
1. Add user preference in frontend
2. Conditionally initialize Sentry based on preference
3. Store preference in localStorage or user profile
4. Respect "Do Not Track" browser setting

**Recommended Implementation**:
```typescript
// Frontend - check user preference
const userConsent = localStorage.getItem('sentry_consent');
if (userConsent !== 'false') {
  initSentry();
}
```

### 3. Health Check Endpoint (`/health`)

**Location**: `backend/mcp_server.py:229-317`

Returns real-time service status:

```json
{
  "status": "healthy",
  "service_mode": "hybrid",
  "service_initialized": true,
  "openai_relay_ready": true,
  "timestamp": "2025-12-04T05:38:06.308Z",
  "services": {
    "direct": "operational",
    "mcp": "operational",
    "mode": "hybrid"
  },
  "mcp_sidecars": {
    "market_mcp": "running",
    "alpaca_mcp": "running",
    "forex_mcp": "running"
  },
  "openai_relay": {
    "sessions_created": 42,
    "sessions_active": 3,
    "sessions_closed": 39,
    "sessions_rejected": 0,
    "sessions_timed_out": 0,
    "tts_requests": 156,
    "tts_failures": 2,
    "errors": 2,
    "uptime_seconds": 86400
  },
  "features": {
    "tool_wiring": true,
    "triggers_disclaimers": true,
    "advanced_ta": {
      "enabled": true,
      "levels": ["sell_high_level", "buy_low_level", "btd_level", "retest_level"]
    },
    "concurrent_execution": {
      "enabled": true,
      "global_timeout_s": 10
    }
  },
  "version": "2.0.2"
}
```

### 3. Request Telemetry System

**Location**: `backend/utils/telemetry.py`

Every API request captures metadata for debugging and analytics:

**RequestTelemetry Object:**
```python
{
  "request_id": "uuid-v4",           # Unique per request
  "path": "/api/stock-price",         # Endpoint accessed
  "method": "GET",                    # HTTP method
  "client_ip": "192.168.1.100",      # Direct client IP
  "forwarded_for": "1.2.3.4",        # X-Forwarded-For header
  "user_agent": "Mozilla/5.0...",    # Browser/client string
  "session_id": "session-uuid",       # Optional session ID
  "user_id": "user-uuid",            # Optional authenticated user
  "duration_ms": 234.567,            # Request processing time
  "cost_summary": {                   # API cost breakdown
    "total_usd": 0.0023,
    "tokens": 456
  }
}
```

### 4. Correlation ID Middleware

**Location**: `backend/middleware/correlation.py`

Every request receives a unique correlation ID for distributed tracing:
- Automatically generated UUIDs
- Propagated through all service calls
- Included in error responses for debugging
- Enables end-to-end request tracking

### 5. Rate Limiting Monitoring

**Location**: `backend/middleware/rate_limiter.py`

Tracks API abuse and rate limit violations:
- Requests per IP address
- Authenticated user rate limits
- Endpoint-specific throttling
- Rejection counts and patterns

---

## User Tracking & Data Collection

### Database Schema

All user data is stored in Supabase PostgreSQL with Row Level Security (RLS).

#### 1. Request Logs Table

**Migration**: `supabase/migrations/20251109000000_request_logs.sql`

```sql
CREATE TABLE request_logs (
    id UUID PRIMARY KEY,
    event TEXT NOT NULL,              -- Event type: 'agent_request', etc.
    request_id TEXT,                  -- Correlation ID
    path TEXT,                        -- API endpoint
    method TEXT,                      -- HTTP method
    client_ip TEXT,                   -- User's IP address
    forwarded_for TEXT,               -- Proxy IP chain
    user_agent TEXT,                  -- Browser/client identification
    session_id TEXT,                  -- Session identifier
    user_id TEXT,                     -- Authenticated user UUID
    duration_ms NUMERIC(12, 3),       -- Request latency
    cost_summary JSONB,               -- API cost breakdown
    payload JSONB,                    -- Additional metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
- `idx_request_logs_created_at` - Time-based queries
- `idx_request_logs_event` - Filter by event type
- `idx_request_logs_request_id` - Correlation ID lookup
- `idx_request_logs_user_id` - Per-user analytics

**Purpose**: Security auditing, debugging, performance analysis, cost tracking

#### 2. Query Analytics Table

**Migration**: `supabase/migrations/001_chat_and_market_history.sql:84-95`

```sql
CREATE TABLE query_analytics (
    id UUID PRIMARY KEY,
    user_id UUID,                     -- Authenticated user (nullable)
    query_type TEXT,                  -- 'price', 'news', 'chart', 'analysis', 'drawing'
    query_content TEXT,               -- User's search/query text
    symbol TEXT,                      -- Stock ticker queried
    response_time_ms INTEGER,         -- Performance tracking
    data_source TEXT,                 -- 'alpaca', 'yahoo', 'mcp'
    success BOOLEAN DEFAULT true,     -- Request success status
    error_message TEXT,               -- Error details if failed
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

**Index:**
- `idx_query_analytics_user` - Per-user query history

**Purpose**: Product analytics, feature usage, symbol popularity, performance optimization

#### 3. User-Specific Data Tables

**Conversations & Messages**
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID,                     -- Owner (nullable for anonymous)
    title TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role TEXT,                        -- 'user', 'assistant', 'system'
    content TEXT,                     -- Message text
    timestamp TIMESTAMPTZ
);
```

**RLS Policy**: Users can only view their own conversations
```sql
CREATE POLICY "Users can view their own conversations"
  ON conversations FOR ALL
  USING (auth.uid() = user_id OR user_id IS NULL);
```

**User Drawings**
```sql
CREATE TABLE user_drawings (
    id UUID PRIMARY KEY,
    user_id UUID,                     -- Owner (nullable)
    symbol TEXT,                      -- Stock ticker
    drawing_data JSONB,               -- Trendline coordinates
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

**RLS Policy**: Users can only manage their own drawings
```sql
CREATE POLICY "Users can manage their own drawings"
  ON user_drawings FOR ALL
  USING (auth.uid() = user_id OR user_id IS NULL);
```

**User Watchlists**
```sql
CREATE TABLE user_watchlists (
    id UUID PRIMARY KEY,
    user_id UUID,                     -- Owner
    symbols TEXT[],                   -- Array of tickers
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

**Purpose**: Personalization, saved preferences, multi-device sync

#### 4. Market Data Tables (Shared Cache)

**Market Candles & News** - Public read access (cached for all users)
```sql
CREATE TABLE market_candles (
    id UUID PRIMARY KEY,
    symbol TEXT,
    timeframe TEXT,                   -- '1m', '5m', '1h', '1d', etc.
    timestamp TIMESTAMPTZ,
    open NUMERIC,
    high NUMERIC,
    low NUMERIC,
    close NUMERIC,
    volume BIGINT
);

CREATE TABLE market_news (
    id UUID PRIMARY KEY,
    symbol TEXT,
    title TEXT,
    summary TEXT,
    url TEXT,
    source TEXT,                      -- 'CNBC', 'Yahoo', etc.
    published_at TIMESTAMPTZ
);
```

**RLS**: Public read access (no user-specific data)

### What Data is Collected?

| Data Type | Storage Location | PII? | Purpose |
|-----------|-----------------|------|---------|
| **IP Address** | `request_logs.client_ip` | ✅ Yes | Security, abuse detection, geolocation |
| **IP Proxy Chain** | `request_logs.forwarded_for` | ✅ Yes | CDN/proxy transparency |
| **User Agent** | `request_logs.user_agent` | ⚠️ Maybe | Browser fingerprinting, compatibility |
| **Session ID** | `request_logs.session_id` | ⚠️ Maybe | Session tracking (optional) |
| **User ID** | `request_logs.user_id` | ✅ Yes | User identification (if authenticated) |
| **Request Metadata** | `request_logs.payload` | ⚠️ Maybe | Debugging, analytics |
| **Query Text** | `query_analytics.query_content` | ⚠️ Maybe | Feature usage, search analytics |
| **Stock Symbols** | `query_analytics.symbol` | ❌ No | Interest patterns, popularity |
| **Chat Messages** | `messages.content` | ⚠️ Maybe | Conversation history, AI training |
| **Drawings** | `user_drawings.drawing_data` | ❌ No | Chart annotations |
| **Watchlists** | `user_watchlists.symbols` | ❌ No | Personalized experience |

**PII Definitions:**
- ✅ **Definitely PII**: IP addresses, user IDs
- ⚠️ **Potentially PII**: User agents (browser fingerprinting), session IDs, query text (may contain personal info), chat messages
- ❌ **Not PII**: Stock symbols, chart drawings (coordinates only)

### What is NOT Collected?

⚠️ **Limited Third-Party Services**
- ✅ Sentry.io for error tracking (optional, configurable)
- ❌ No Google Analytics
- ❌ No Facebook Pixel
- ❌ No Mixpanel, Amplitude, Segment, PostHog, Heap, etc.
- ❌ No advertising trackers
- ❌ No social media widgets with tracking

✅ **No Cross-Site Tracking**
- No cookies for advertising
- No device fingerprinting scripts
- No browser extension detection
- No canvas fingerprinting

✅ **No Sensitive Financial Data**
- No credit card information
- No bank account details
- No brokerage credentials
- No trading API keys (stored client-side only)

---

## Privacy & Security

### Row Level Security (RLS)

All user-specific tables enforce PostgreSQL Row Level Security:

```sql
-- Enable RLS on all user tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_drawings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_watchlists ENABLE ROW LEVEL SECURITY;
ALTER TABLE query_analytics ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own data
CREATE POLICY "Users can view their own data"
  ON {table_name} FOR ALL
  USING (auth.uid() = user_id OR user_id IS NULL);
```

**How RLS Works:**
1. Every query automatically filters by `auth.uid()`
2. Supabase JWT tokens provide user authentication
3. Users cannot access other users' data via API
4. Database administrators bypass RLS (SUPERUSER role)

### Authentication

**Supabase Auth** provides:
- Email/password authentication
- OAuth providers (Google, GitHub, etc.)
- Magic link (passwordless) login
- JWT-based session management
- Anonymous usage (user_id = NULL allowed)

**Anonymous Users:**
- Can use the application without creating an account
- Data stored with `user_id = NULL`
- Cannot sync across devices
- Cannot access data after session ends

### Data Encryption

**In Transit:**
- ✅ HTTPS/TLS 1.3 for all API traffic
- ✅ WSS (WebSocket Secure) for real-time connections
- ✅ Supabase enforces SSL connections

**At Rest:**
- ✅ Supabase PostgreSQL: AES-256 encryption
- ✅ Fly.io volumes: Encrypted storage
- ⚠️ Prometheus metrics: Stored in-memory (ephemeral)

### Data Retention

**Current Policy** (as of Dec 2025):
- Request logs: **Indefinite** (no automatic cleanup)
- Query analytics: **Indefinite**
- Chat messages: **Indefinite**
- Market data cache: **30 days** (rolling window)
- Prometheus metrics: **Ephemeral** (lost on restart)

**Recommended Policy** (to be implemented):
- Request logs: **90 days** retention
- Query analytics: **1 year** retention
- Aggregated metrics: **5 years** retention
- User data: **Retained until account deletion**

---

## Data Access & Control

### Who Can Access This Data?

| Role | Access Level | Data Visible |
|------|-------------|--------------|
| **End Users** | Own data only | Via RLS policies, API responses |
| **Database Admins** | Full access | All tables via Supabase dashboard |
| **Application Developers** | Full access | Logs, metrics, debugging |
| **Prometheus Scrapers** | Metrics only | `/metrics` endpoint (⚠️ currently public) |
| **System Administrators** | Infrastructure | Server logs, Fly.io metrics |

### User Rights (GDPR/CCPA)

**Currently Implemented:**
- ✅ Account deletion (Supabase Auth)
- ✅ Data isolation (RLS)
- ❌ Data export (not implemented)
- ❌ Opt-out of analytics (not implemented)
- ❌ Right to be forgotten (not implemented)

**To Be Implemented:**
1. **Data Export**: JSON download of all user data
2. **Analytics Opt-Out**: Disable query_analytics tracking
3. **Right to Erasure**: Delete all user data (GDPR Article 17)
4. **Data Portability**: Machine-readable export (GDPR Article 20)
5. **Privacy Dashboard**: View collected data, manage preferences

### API Access

**Request Logs Query** (admin only):
```sql
SELECT * FROM request_logs
WHERE user_id = 'user-uuid'
ORDER BY created_at DESC
LIMIT 100;
```

**Query Analytics** (admin only):
```sql
SELECT symbol, COUNT(*) as queries
FROM query_analytics
WHERE user_id = 'user-uuid'
GROUP BY symbol
ORDER BY queries DESC;
```

**User Data Export** (to be implemented):
```bash
GET /api/user/export
Authorization: Bearer {jwt_token}

Response:
{
  "user_id": "uuid",
  "request_logs": [...],
  "query_analytics": [...],
  "conversations": [...],
  "drawings": [...],
  "watchlists": [...]
}
```

---

## Compliance Considerations

### GDPR (European Union)

**Requirements:**
- ✅ Lawful basis for processing (legitimate interest: service provision)
- ⚠️ Consent for IP address tracking (may be required)
- ❌ Privacy policy link (not prominently displayed)
- ❌ Cookie consent banner (IP tracking = cookies equivalent)
- ❌ Data processing agreement with Supabase (verify)
- ❌ Right to erasure implementation

**Action Items:**
1. Add privacy policy page with clear data collection disclosure
2. Implement cookie/tracking consent banner
3. Add "Download My Data" feature
4. Add "Delete My Account" feature (with data erasure)
5. Verify Supabase DPA (Data Processing Agreement)
6. Verify Sentry.io DPA and data processing terms
7. Document lawful basis for each data type
8. Add Sentry opt-out mechanism (respect user consent)

### CCPA (California, USA)

**Requirements:**
- ✅ Business purpose disclosure (service provision)
- ⚠️ Privacy policy link (needs "Do Not Sell" disclosure)
- ❌ "Do Not Sell My Personal Information" link
- ❌ Opt-out mechanism for data sales
- ❌ Data deletion on request

**Action Items:**
1. Add CCPA-compliant privacy policy
2. Add "Do Not Sell" disclosure (even though we don't sell data)
3. Implement data deletion workflow
4. Maintain data sale disclosure (state we don't sell)

### HIPAA (Healthcare, USA)

**Status**: ✅ Not applicable (no protected health information collected)

### SOC 2 (Enterprise Customers)

**Type II Controls** (if targeting enterprise):
- ⚠️ Access controls (needs improvement)
- ⚠️ Encryption at rest (Supabase handles)
- ⚠️ Audit logging (partially implemented)
- ❌ Penetration testing (not performed)
- ❌ Vulnerability scanning (not automated)
- ❌ Incident response plan (not documented)

---

## Monitoring Endpoints Reference

### Public Endpoints

| Endpoint | Method | Auth Required | Purpose | Rate Limit |
|----------|--------|---------------|---------|------------|
| `GET /health` | GET | ❌ No | Service status check | None |
| `GET /metrics` | GET | ⚠️ Should require auth | Prometheus scraping | None |

**Security Issue**: `/metrics` endpoint is currently public and should be restricted to:
- Internal IP ranges (monitoring systems)
- Bearer token authentication
- API key authentication

### Internal Monitoring

**Supabase Dashboard:**
- Database query performance
- Table sizes and growth
- Real-time connections
- RLS policy violations

**Fly.io Metrics:**
- CPU/memory usage
- Request latency (at edge)
- Geographic distribution
- Error rates

**Prometheus Queries** (example):
```promql
# Average request latency by endpoint
rate(http_request_duration_seconds_sum[5m])
/ rate(http_request_duration_seconds_count[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m])) * 100

# OpenAI API cost per hour
rate(openai_total_cost_usd[1h])
```

---

## Recommendations & Action Items

### Security Improvements

1. **Restrict `/metrics` endpoint** - Add authentication
2. **IP anonymization** - Hash IPs after 24 hours for GDPR
3. **Rate limit bypass prevention** - Implement sliding window
4. **Request log cleanup** - Implement 90-day retention policy
5. **Session secret rotation** - Automated key rotation

### Privacy Enhancements

1. **Privacy policy page** - Legal disclosure of data collection (including Sentry)
2. **Data export feature** - GDPR Article 20 compliance
3. **Account deletion** - Right to erasure (GDPR Article 17)
4. **Analytics opt-out** - User preference for query_analytics
5. **Consent management** - Cookie/tracking consent banner (include Sentry consent)
6. **Sentry opt-out** - Respect user preference for error tracking
7. **Session replay review** - Verify no PII captured in Sentry replays

### Compliance Readiness

1. **GDPR audit** - Review all data flows
2. **CCPA disclosure** - Add required privacy links
3. **Data inventory** - Document all PII fields
4. **Processing agreements** - Verify Supabase/Fly.io DPAs
5. **Incident response plan** - Data breach procedures

### Monitoring Enhancements

1. **Alerting rules** - Prometheus alerts for errors, latency, costs
2. **Grafana dashboards** - Visual monitoring interface
3. **Log aggregation** - ELK/Loki for centralized logging
4. **APM integration** - Application performance monitoring
5. **Synthetic monitoring** - Uptime checks from multiple regions

---

## Contact & Questions

**Data Protection Officer**: (To be assigned)
**Security Team**: (To be created)
**Privacy Email**: (To be configured)

**Documentation Maintained By**: Engineering Team
**Last Review**: December 4, 2025
**Next Review**: March 4, 2026 (quarterly)

---

## Appendix: Related Documentation

- `CLAUDE.md` - Project overview and architecture
- `ARCHITECTURE.md` - System design and data flows
- `SENTRY_INTEGRATION.md` - Sentry error monitoring setup guide
- `SENTRY_AUDIT_REPORT.md` - Sentry integration audit and compliance review
- `backend/middleware/metrics.py` - Prometheus metrics definitions
- `backend/utils/telemetry.py` - Request telemetry implementation
- `backend/config/sentry.py` - Sentry backend configuration
- `frontend/src/config/sentry.ts` - Sentry frontend configuration
- `supabase/migrations/` - Database schema definitions
- `fly.toml` - Production deployment configuration
