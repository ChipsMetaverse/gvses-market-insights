# Production Bug Investigation - November 11, 2025

## Executive Summary

Comprehensive production investigation revealed **5 bugs**, including **1 CRITICAL user-impacting bug** that was silently failing for 100% of chart analysis requests today.

---

## 🔴 **BUG #1: GPT-5-mini Chart Analysis Failure** (CRITICAL - FIXED ✅)

### Impact
- **Severity**: CRITICAL
- **User Impact**: 100% failure rate on most-used feature
- **Users Affected**: All users attempting chart analysis (1 active user today made 10 attempts)
- **Silent Failure**: Returns 200 OK but produces no analysis results

### Root Cause
```python
# backend/services/chart_image_analyzer.py:136
response = await self.client.responses.create(
    model=config.model_id,
    temperature=config.temperature,  # ❌ NOT SUPPORTED BY RESPONSES API
    input=[...]
)
```

**Error Message in Logs:**
```
Error code: 400 - {'error': {'message': "Unsupported parameter: 'temperature' is not supported with this model."}}
Chart analysis failed after 2 attempts
```

### User Activity Evidence
```
22:28:29 POST /api/agent/chart-snapshot - 200 OK (failed internally)
22:28:38 POST /api/agent/chart-snapshot - 200 OK (failed internally)
22:28:46 POST /api/agent/chart-snapshot - 200 OK (failed internally)
... [7 more attempts]
```

User clicked "Analyze Chart" 10 times in 90 seconds, receiving false success responses but no actual analysis.

### Fix Applied ✅
**File**: `backend/services/chart_image_analyzer.py:136`
**Change**: Removed `temperature=config.temperature` parameter
**Status**: Fixed - ready for deployment

### Testing
```bash
# Test locally
cd backend
python -c "from services.chart_image_analyzer import ChartImageAnalyzer; print('OK')"

# Deploy to production
cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp
fly deploy
```

---

## 🔴 **BUG #2: Duplicate Resistance Labels** (CRITICAL - VISUAL)

### Impact
- **Severity**: CRITICAL (visual corruption)
- **User Impact**: Chart becomes cluttered and unreadable
- **Evidence**: Screenshot showing 7x "Resistance 203.97" stacked vertically

### Root Cause (Suspected)
When "Show All Patterns" is enabled, each pattern independently draws resistance/support labels without deduplication. Multiple patterns at the same price level result in stacked duplicate labels.

**Expected Behavior**: One label per unique price level
**Actual Behavior**: N labels where N = number of patterns touching that level

### Screenshot Evidence
```
Resistance 203.97 ← Pattern 1
Resistance 203.97 ← Pattern 2
Resistance 203.97 ← Pattern 3
Resistance 203.97 ← Pattern 4
Resistance 203.97 ← Pattern 5
Resistance 203.97 ← Pattern 6
Resistance 203.97 ← Pattern 7
```

### Investigation Status
- **Location**: `frontend/src/components/TradingChart.tsx` and `frontend/src/services/DrawingPrimitive.ts`
- **Suspected Code**: Pattern boundary box rendering logic
- **Fix Required**: Add Set-based deduplication before drawing level labels

### Proposed Fix
```typescript
// Create Set to track drawn levels
const drawnLevels = new Set<string>();

// Before drawing each level:
const levelKey = `${type}_${price.toFixed(2)}`;
if (drawnLevels.has(levelKey)) continue;
drawnLevels.add(levelKey);
// ... draw level
```

---

## 🟡 **BUG #3: Forex Calendar 404 Error** (MEDIUM)

### Impact
- **Severity**: MEDIUM (feature non-functional)
- **User Impact**: Economic calendar unavailable
- **Usage**: 0 users attempted to use this feature today

### Evidence
```
ERROR: Failed to load resource: the server responded with a status of 404
Endpoint: /api/forex/calendar?time_period=today
```

### Service Status
```
✅ forex-mcp-server: RUNNING (PID 660) - 11+ hours uptime
✅ Backend: Healthy
❌ API Endpoint: Returning 404
```

### Root Cause (Suspected)
- Service is running but endpoint not properly routed
- Possible nginx routing configuration issue
- OR endpoint path mismatch between frontend and backend

### Investigation Required
1. Check `backend/mcp_server.py` for `/api/forex/calendar` endpoint registration
2. Verify nginx proxy configuration in production
3. Test endpoint directly: `curl https://gvses-market-insights-api.fly.dev/api/forex/calendar?time_period=today`

---

## 🟡 **BUG #4: Symbol Search Empty Results** (MEDIUM)

### Impact
- **Severity**: MEDIUM (feature non-functional)
- **User Impact**: Cannot add custom symbols to watchlist
- **Usage**: 0 users attempted to use this feature today

### Evidence
```javascript
// Tested with query: "MSFT"
const response = await fetch('/api/symbol-search?query=MSFT&limit=10');
const data = await response.json();
// Result: {"results": []} - empty array
```

### Service Status
```
✅ Alpaca API integration configured
❌ Symbol search returning empty results
```

### Root Cause (Suspected)
- Alpaca API credentials issue in production
- OR Assets API endpoint incorrectly called
- OR Response parsing error

### Investigation Required
1. Check Alpaca API key validity in production
2. Test Alpaca assets endpoint directly
3. Review `backend/services/alpaca_service.py` symbol search implementation

---

## 🟢 **BUG #5: Missing Rate Limit Headers** (LOW)

### Impact
- **Severity**: LOW (infrastructure monitoring)
- **User Impact**: None (headers are for client-side rate limit awareness)
- **Expected**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Evidence
```javascript
// All production API responses missing rate limit headers
const headers = response.headers;
// Expected: X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
// Actual: {} (no rate limit headers)
```

### Service Status
```
✅ Rate limit middleware ACTIVE
✅ In-memory backend WORKING
❌ Headers NOT being added to responses
```

### Backend Logs
```
INFO: Enhanced rate limiting middleware enabled
WARNING: Redis not available: Error 111 (localhost:6379 refused)
INFO: Rate limiter using in-memory backend
```

### Root Cause (Suspected)
- Middleware registered but `RATE_LIMIT_HEADERS` environment variable not set
- OR nginx stripping headers in proxy configuration
- Middleware is functional (rate limiting works) but header injection is skipped

### Investigation Required
1. Check `backend/.env` for `RATE_LIMIT_HEADERS=true`
2. Verify middleware order in `backend/mcp_server.py`
3. Check nginx configuration for header passthrough

---

## Production Health Summary

### Services Status
| Service | Status | PID | Uptime |
|---------|--------|-----|--------|
| forex-mcp-server | ✅ RUNNING | 660 | 11+ hours |
| market-mcp-server | ✅ RUNNING | 661 | 11+ hours |
| backend | ✅ RUNNING | 714 | Auto-restart (normal) |
| nginx | ✅ RUNNING | 663 | 11+ hours |

### Auto-Restart Behavior (Backend)
```
WARNING: Maximum request limit of 1000 exceeded. Terminating process.
INFO: Spawned: 'backend' with pid 714
```
**Analysis**: Normal behavior - uvicorn configured with `--limit-max-requests 1000` for memory leak prevention. Backend auto-restarts every 1000 requests (not an error).

### User Activity Today
- **Active Users**: 1
- **Session Duration**: 20+ minutes (22:23-22:43 UTC / 5:23-5:43 PM EST)
- **Browser**: Chrome 141/142 on macOS 10.15.7
- **Features Used**:
  - Chart Snapshot Analysis (10 attempts - all failed)
  - Dashboard viewing
- **Features NOT Used**:
  - Symbol search
  - Forex calendar
  - Pattern detection toggle
  - Timeframe switching
  - News feed

---

## Priority Action Plan

### Immediate (Deploy Today) 🔴
1. **GPT-5-mini Chart Analysis Fix** ✅ COMPLETED
   - File: `backend/services/chart_image_analyzer.py`
   - Change: Removed temperature parameter
   - Status: Ready for deployment
   - Deploy: `cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp && fly deploy`

### High Priority (Deploy This Week) 🟡
2. **Duplicate Resistance Labels**
   - Investigate pattern boundary box rendering
   - Add deduplication logic
   - Test with multiple patterns
   - Estimated: 2-3 hours

3. **Forex Calendar 404**
   - Verify endpoint registration
   - Test routing configuration
   - Fix nginx proxy if needed
   - Estimated: 1-2 hours

4. **Symbol Search Empty Results**
   - Verify Alpaca credentials
   - Test assets API endpoint
   - Fix response parsing
   - Estimated: 1-2 hours

### Low Priority (Future Sprint) 🟢
5. **Rate Limit Headers**
   - Set environment variable
   - Verify middleware configuration
   - Test header passthrough
   - Estimated: 30 minutes

---

## Testing Checklist

### Pre-Deployment Testing
- [ ] GPT-5-mini chart analysis returns valid JSON
- [ ] No more temperature parameter errors in logs
- [ ] Chart analysis completes in <5 seconds
- [ ] Results displayed in frontend

### Post-Deployment Monitoring
- [ ] Check `/var/log/app/backend.err.log` for errors
- [ ] Monitor nginx access logs for 200 OK on `/api/agent/chart-snapshot`
- [ ] Verify user receives actual analysis results (not empty)
- [ ] Health check remains passing

### User Acceptance
- [ ] User clicks "Analyze Chart" button
- [ ] Receives pattern analysis within 5 seconds
- [ ] Analysis appears in UI with confidence scores
- [ ] No duplicate resistance labels visible

---

## Deployment Commands

```bash
# 1. Deploy backend fix
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp"
fly deploy

# 2. Monitor deployment
fly status

# 3. Check logs for errors
fly logs --app gvses-market-insights

# 4. SSH into production to verify
fly ssh console --app gvses-market-insights
tail -f /var/log/app/backend.err.log

# 5. Test endpoint
curl -X POST https://gvses-market-insights-api.fly.dev/api/agent/chart-snapshot \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "imageBase64": "..."}'
```

---

## Investigation Methods Used

1. **Production Log Analysis**
   - Backend error logs: `/var/log/app/backend.err.log`
   - Nginx access logs: `/var/log/nginx/access.log`
   - Nginx error logs: `/var/log/nginx/error.log`
   - Supervisord logs: `fly logs --app gvses-market-insights`

2. **Source Code Review**
   - `backend/services/chart_image_analyzer.py` (GPT-5 API integration)
   - `backend/middleware/rate_limiter.py` (Rate limiting middleware)
   - `frontend/src/components/TradingChart.tsx` (Pattern rendering)

3. **Live Production Testing**
   - Playwright MCP browser automation
   - Direct API endpoint testing
   - Header inspection
   - Console log analysis

4. **User Activity Tracking**
   - Nginx access log parsing
   - API request pattern analysis
   - Feature usage statistics

---

## References

- **Documentation**: `RATE_LIMITING.md`
- **Test Suite**: `backend/test_rate_limiting.py`
- **MCP Integration**: `backend/test_dual_mcp.py`
- **Requirements**: `backend/requirements.txt`

---

## Contact

For questions about this investigation:
- Logs: `fly logs --app gvses-market-insights`
- SSH: `fly ssh console --app gvses-market-insights`
- Status: `fly status --app gvses-market-insights`
