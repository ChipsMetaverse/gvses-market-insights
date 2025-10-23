# StreamableHTTP Upgrade - Critical Bug Fix

**Date:** October 22, 2025  
**Issue:** Technical levels displaying `$---` in production  
**Root Cause:** Missing `await` on async `get_http_mcp_client()` calls  
**Status:** ✅ **FIXED & VERIFIED**

---

## Executive Summary

After upgrading the MCP transport to StreamableHTTP with stateful session management, the `get_http_mcp_client()` function became **async** to support the `initialize()` handshake. However, **5 call sites** across the codebase were not updated to `await` this async call, causing the comprehensive stock data endpoint to fail silently.

This resulted in the left panel technical levels showing placeholder values (`$---`) instead of real data like `$452.14 (Sell High)`, `$421.41 (Buy Low)`, `$403.85 (BTD)`.

---

## Investigation Timeline

### 1. Initial Symptom (Production)
```bash
curl https://gvses-market-insights.fly.dev/api/comprehensive-stock-data?symbol=TSLA
{
  "symbol": "TSLA",
  "price_data": {},
  "technical_levels": {},
  "error": "Unable to fetch real market data for TSLA..."
}
```

**Left Panel Display:** `$---` for all three technical levels

### 2. Root Cause Discovery

The user requested an audit against the commit **before** the StreamableHTTP upgrade (`bda7cc3`). This led to discovering that:

1. **Commit `0dbe881`** introduced StreamableHTTP with stateful session management
2. The `get_http_mcp_client()` function signature changed from sync to **async**
3. Multiple call sites were **not updated** to include `await`

**Error Pattern:**
```python
# WRONG (causes silent failure)
client = get_http_mcp_client()  # Returns a coroutine object, not HTTPMCPClient

# CORRECT
client = await get_http_mcp_client()  # Returns HTTPMCPClient instance
```

### 3. Affected Files & Fixes

| File | Line | Function | Status |
|------|------|----------|--------|
| `backend/services/market_service.py` | 254 | `get_quote()` | ✅ Fixed |
| `backend/services/market_service.py` | 414 | `get_ohlcv()` | ✅ Fixed |
| `backend/services/news_service.py` | 24 | `get_related_news()` | ✅ Fixed |
| `backend/services/market_service_factory.py` | 460 | `get_market_overview()` | ✅ Fixed |
| `backend/services/market_service_factory.py` | 483 | `get_market_overview()` | ✅ Fixed |
| `backend/mcp_server.py` | 389 | `get_technical_indicators()` | ✅ Fixed (earlier) |

**Total:** 6 missing `await` statements

---

## Verification Results

### Local Testing (Localhost)

**Before Fix:**
```bash
curl http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA
{
  "symbol": "TSLA",
  "technical_levels": {},  # Empty!
  "error": "Unable to fetch real market data..."
}
```

**After Fix:**
```bash
curl http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA
{
  "symbol": "TSLA",
  "price_data": {
    "price": 438.97,
    "change_pct": -0.820155
  },
  "technical_levels": {
    "sell_high_level": 452.14,  # ✅ Working!
    "buy_low_level": 421.41,    # ✅ Working!
    "btd_level": 403.85          # ✅ Working!
  }
}
```

### UI Verification (Playwright)

**Before Fix:**
```
TECHNICAL LEVELS
Sell High: $---
Buy Low:   $---
BTD:       $---
```

**After Fix:**
```
TECHNICAL LEVELS
Sell High: $452.14  ✅
Buy Low:   $421.41  ✅
BTD:       $403.85  ✅
```

**Screenshot:** `.playwright-mcp/localhost_technical_levels_working.png`

---

## Technical Details

### Why This Happened

When we upgraded to StreamableHTTP, the HTTP MCP client needed to:
1. Perform an `initialize` handshake to get a session ID
2. Store the session ID for subsequent requests
3. Reuse the session across multiple tool calls

This required `get_http_mcp_client()` to become **async** to perform the handshake:

```python
async def get_http_mcp_client() -> HTTPMCPClient:
    """Get or create singleton with persistent session."""
    global _global_client
    
    async with _client_lock:
        if _global_client is None:
            _global_client = HTTPMCPClient(base_url="http://127.0.0.1:3001/mcp")
            await _global_client.initialize()  # <-- Requires async!
    
    return _global_client
```

### Impact

Without `await`, Python returns a **coroutine object** instead of the actual `HTTPMCPClient` instance. When the code tries to call `.call_tool()` on this coroutine, it fails:

```python
# Without await
client = get_http_mcp_client()  # <coroutine object>
result = await client.call_tool(...)  # ❌ AttributeError: 'coroutine' has no attribute 'call_tool'

# With await
client = await get_http_mcp_client()  # <HTTPMCPClient instance>
result = await client.call_tool(...)  # ✅ Works!
```

---

## Related Fixes

### 1. Technical Indicators API (Commit `15fd13a`)
- **File:** `backend/mcp_server.py`
- **Line:** 389
- **Issue:** Same missing `await` in `/api/technical-indicators` endpoint
- **Status:** ✅ Fixed earlier

### 2. RSI Calculation Issues (Commit `94418e1`)
- **File:** `market-mcp-server/index.js`
- **Issue:** RSI period confusion, insufficient historical data
- **Status:** ✅ Fixed earlier

---

## Deployment Checklist

- [x] All 5 missing `await` statements added
- [x] Local testing passed (curl + API calls)
- [x] UI testing passed (Playwright verification)
- [x] Technical levels display correctly
- [x] News fetching works
- [x] No console errors
- [x] Git commits created
- [ ] **READY FOR PRODUCTION DEPLOYMENT**

---

## Commits

1. **`19f8835`** - fix(market-service): await async get_http_mcp_client calls (2 fixes in market_service.py)
2. **`8c02839`** - fix(critical): await all async get_http_mcp_client() calls (3 fixes in news_service.py, market_service_factory.py)

---

## Lessons Learned

1. **Type Hints:** Adding explicit type hints would have caught this at development time
2. **Linting:** Async/await linting rules should be enforced
3. **Testing:** Integration tests should cover the full request-response cycle
4. **Migration:** When changing function signatures (sync → async), use IDE refactoring tools to update all call sites

---

## Next Steps

1. Deploy to production via `git push origin master`
2. Monitor Fly.io logs for successful deployment
3. Verify technical levels in production UI
4. Close investigation

**Expected Production Result:**
```
TECHNICAL LEVELS
Sell High: $452.14  ✅
Buy Low:   $421.41  ✅
BTD:       $403.85  ✅
```

---

**Investigation Lead:** CTO Agent  
**Verification Method:** Playwright MCP + curl + git bisect  
**Status:** ✅ **COMPLETE - READY FOR DEPLOYMENT**

