# Playwright Investigation V2 - Detailed Report

**Date:** November 10, 2025  
**Method:** Enhanced Playwright Browser Automation  
**Target:** https://gvses-market-insights-api.fly.dev  
**Timeout:** 10 seconds for agent endpoint

---

## ✅ **Working Endpoints**

### 1. Health Endpoint ✅
- **Status:** 200 OK
- **Response:** Healthy
- **Details:**
  - Service Mode: Hybrid
  - MCP Available: True
  - All services operational

### 2. Stock Price API ✅
- **Status:** 200 OK
- **Symbol Tested:** TSLA
- **Price:** $445.63
- **Data Source:** yahoo_mcp
- **Response Time:** Fast (< 1 second)

### 3. Analytics Queries ✅
- **Status:** 200 OK
- **Response:** `{}` (empty - expected, no queries logged yet)
- **Working correctly**

### 4. Docs Endpoint ✅ (Partial)
- **Status:** 200 OK
- **Page Title:** "Voice Assistant MCP Server - Swagger UI"
- **Swagger UI:** Loaded successfully
- **Issue:** Cannot load OpenAPI schema (see below)

---

## ❌ **Issues Found**

### 1. OpenAPI Endpoint ❌
- **Status:** 500 Internal Server Error
- **Error:** "Internal Server Error"
- **Impact:** Swagger UI cannot display API documentation
- **Response Headers Present:**
  - content-encoding
  - content-type
  - date
  - fly-request-id
  - server
  - via

**Analysis:**
- The endpoint is responding (not a network error)
- Server is processing the request but failing internally
- Likely an issue with FastAPI schema generation

**Root Cause Hypothesis:**
1. Invalid route definition causing schema generation to fail
2. Circular reference in Pydantic models
3. Serialization error in response models
4. Missing or invalid OpenAPI metadata

---

### 2. Agent Orchestrate Endpoint ⚠️
- **Status:** Timeout (10 seconds)
- **Behavior:** Request hangs, no response
- **Previous Finding:** Also timed out at 30 seconds

**Analysis:**
- Request is sent successfully
- Server receives the request
- No response is returned within timeout period
- Likely hanging on OpenAI API call

**Possible Causes:**
1. **OpenAI API hanging** - Waiting for response that never comes
2. **Quota exceeded** - Request stuck in retry loop
3. **Network issue** - Connection to OpenAI not completing
4. **Long processing** - Query taking > 10 seconds

**Previous Investigation Found:**
- OpenAI quota exceeded (429 error) when tested with browser extension
- This timeout suggests the error handling isn't working correctly

---

## 📊 **Network Traffic Analysis**

### Request Flow:
1. ✅ Health check: Fast response
2. ✅ Stock price: Fast response  
3. ❌ OpenAPI: Immediate 500 error
4. ⚠️ Agent: Hangs until timeout
5. ✅ Analytics: Fast response
6. ✅ Docs page: Loads successfully (but OpenAPI.json fails)

### Console Errors:
- `Failed to load resource: 404` - Favicon (not critical)
- `Failed to load resource: 500` - OpenAPI.json (critical)

---

## 🔍 **Key Observations**

### 1. OpenAPI Schema Issue
- **Symptom:** 500 error on `/openapi.json`
- **Impact:** Swagger docs unusable
- **Swagger UI:** Loads but cannot fetch schema
- **Error Detection:** Swagger UI may display error dynamically (not caught by text search)

### 2. Agent Endpoint Behavior
- **Consistent:** Times out consistently
- **No Error Response:** Not returning error immediately
- **Suggests:** Request is being processed but hanging
- **Likely:** OpenAI API call blocking without timeout

### 3. Other Endpoints
- **All working:** Health, stock prices, analytics
- **Fast responses:** < 1 second for most endpoints
- **MCP Integration:** Working correctly (yahoo_mcp data source)

---

## 🎯 **Recommendations**

### Priority 1: Fix OpenAPI Endpoint

**Investigation Steps:**
1. Check backend logs for OpenAPI generation errors
2. Review FastAPI route definitions for invalid schemas
3. Test OpenAPI generation locally
4. Check for circular references in Pydantic models

**Fix Approach:**
```python
# Add error handling to OpenAPI generation
try:
    return app.openapi()
except Exception as e:
    logger.error(f"OpenAPI generation error: {e}")
    # Return minimal schema or error details
```

### Priority 2: Fix Agent Endpoint Timeout

**Immediate Fix:**
```python
# Add timeout to OpenAI calls
import asyncio

try:
    response = await asyncio.wait_for(
        openai_client.chat.completions.create(...),
        timeout=10.0  # 10 second timeout
    )
except asyncio.TimeoutError:
    return {
        "text": "Request timed out. Please try again.",
        "error": "timeout"
    }
except RateLimitError as e:
    if "quota" in str(e).lower():
        return {
            "text": "OpenAI API quota exceeded...",
            "error": str(e)
        }
```

**Better Approach:**
- Add circuit breaker for OpenAI API
- Return error immediately if quota exceeded
- Don't wait for timeout

### Priority 3: Add Monitoring

1. **Error Tracking:**
   - Log all 500 errors with stack traces
   - Track timeout occurrences
   - Monitor OpenAI API response times

2. **Alerting:**
   - Alert on OpenAPI endpoint failures
   - Alert on agent endpoint timeouts
   - Alert on OpenAI quota issues

---

## 📸 **Screenshots**

- `production_investigation_v2.png` - Latest screenshot
- Shows Swagger UI page (but OpenAPI.json failing)

---

## ✅ **Summary**

**Overall Status:** **Partially Operational**

**Working (4/6 endpoints):**
- ✅ Health monitoring
- ✅ Stock price data API
- ✅ Analytics queries
- ✅ Docs page (UI loads)

**Issues (2 endpoints):**
- ❌ OpenAPI schema generation (500 error)
- ⚠️ Agent orchestrate (timeout)

**Next Steps:**
1. Check backend logs for OpenAPI error details
2. Add timeout handling to agent endpoint
3. Fix OpenAI quota error handling
4. Deploy fixes and verify

---

**Investigation Completed:** November 10, 2025  
**Tool:** Playwright Browser Automation (Enhanced)  
**Duration:** ~15 seconds

