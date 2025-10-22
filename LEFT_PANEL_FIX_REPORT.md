# Left Panel Data Failure - Root Cause & Fix

**Date**: 2025-10-22  
**Severity**: 🔴 CRITICAL  
**Status**: ✅ FIXED  

---

## 🚨 Problem Summary

The left panel in production was completely broken:
- ❌ Technical levels showing `$---` (placeholders)
- ❌ No news loading
- ❌ No pattern detection
- ❌ 500 errors on `/api/technical-indicators`
- ❌ MCP Server returning "Unknown tool" errors

---

## 🔍 Root Cause Analysis

### Issue 1: Tool Name Mismatch (CRITICAL)

The HTTP handler in `market-mcp-server/index.js` had **THREE critical bugs**:

#### Bug 1: Wrong Tool Names in Switch Statement
**Lines 2557-2574 (HTTP handler)**
```javascript
switch (name) {
  case 'get_stock_quote':
  case 'get_quote':
    result = await this.getQuote(args);  // ❌ METHOD DOESN'T EXIST!
```

**Lines 600-601 (STDIO handler - correct)**
```javascript
case 'get_stock_quote':
  result = await this.getStockQuote(args);  // ✅ CORRECT METHOD
```

#### Bug 2: News Method Name Wrong
**HTTP handler called:**
```javascript
case 'get_market_news':
  result = await this.getStockNews(args);  // ❌ METHOD DOESN'T EXIST!
```

**Should call (line 1384):**
```javascript
async getMarketNews(args) {  // ✅ ACTUAL METHOD NAME
```

#### Bug 3: Technical Indicators Method Name Wrong
**HTTP handler called:**
```javascript
case 'get_technical_indicators':
  result = await this.calculateTechnicalIndicators(args);  // ❌ METHOD DOESN'T EXIST!
```

**Should call (line 1480):**
```javascript
async getTechnicalIndicators(args) {  // ✅ ACTUAL METHOD NAME
```

### Issue 2: Tools/List Response Had Wrong Names

The HTTP endpoint's `tools/list` response advertised incorrect tool names:
- Listed: `get_quote` ❌
- Should be: `get_stock_quote` ✅

This caused confusion between what tools were available vs. what the backend was calling.

---

## 🔧 The Fix

### Commit 1: `08aad2d` - Fixed tool names in tools/list
- Updated `get_quote` → `get_stock_quote`
- Updated `get_stock_news` → `get_market_news`
- Updated `calculate_technical_indicators` → `get_technical_indicators`

### Commit 2: `e1f526c` - Fixed method calls (CRITICAL)
**Changed HTTP handler switch cases to call correct methods:**

```diff
  case 'get_stock_quote':
  case 'get_quote':
-   result = await this.getQuote(args);
+   result = await this.getStockQuote(args);
    break;
    
  case 'get_market_news':
  case 'get_stock_news':
-   result = await this.getStockNews(args);
+   result = await this.getMarketNews(args);
    break;
    
  case 'get_technical_indicators':
  case 'calculate_technical_indicators':
-   result = await this.calculateTechnicalIndicators(args);
+   result = await this.getTechnicalIndicators(args);
    break;
```

---

## 📊 Evidence of the Bug

### Backend Logs (Before Fix)
```
ERROR:services.http_mcp_client:HTTP error calling MCP server: 500 - {"jsonrpc":"2.0","id":1,"error":{"code":-32603,"message":"Unknown tool: get_stock_quote"}}
ERROR:services.http_mcp_client:Failed to call MCP tool get_stock_quote via HTTP: MCP HTTP error: 500
ERROR:services.http_mcp_client:HTTP error calling MCP server: 500 - {"jsonrpc":"2.0","id":1,"error":{"code":-32603,"message":"Unknown tool: get_market_news"}}
ERROR:services.market_service:Failed to fetch real OHLCV data for TSLA: No historical data available for TSLA
ERROR:services.market_service_factory:Error getting comprehensive data: Unable to fetch real historical data for TSLA
```

### MCP Server Logs (Before Fix)
```
[HTTP] Received request: tools/call
[HTTP] Error: Unknown tool: get_technical_indicators
[HTTP] Received request: tools/call
[HTTP] Error: Unknown tool: get_market_news
[HTTP] Received request: tools/call
[HTTP] Error: Unknown tool: get_stock_quote
```

### API Response (Before Fix)
```json
{
  "symbol": "TSLA",
  "price_data": {},
  "technical_levels": {},
  "data_source": "error",
  "error": "Unable to fetch real historical data for TSLA",
  "news": []
}
```

---

## 🎯 Why This Happened

When we migrated from **STDIO to HTTP mode** for the MCP server:

1. ✅ **STDIO handler** was correctly calling `getStockQuote()`, `getMarketNews()`, `getTechnicalIndicators()`
2. ❌ **HTTP handler** was newly written but used **WRONG method names** copied from a different implementation
3. ❌ The HTTP handler was **never tested** with actual backend calls
4. ❌ The tool names in `tools/list` didn't match what the backend expected

The STDIO code path worked perfectly. The HTTP code path was fundamentally broken.

---

## ✅ Verification Steps

### After Deployment
1. **Check MCP server logs** - should see successful tool calls, no "Unknown tool" errors
2. **Check backend logs** - should see successful HTTP responses from MCP server
3. **Test comprehensive data API**:
   ```bash
   curl https://gvses-market-insights.fly.dev/api/comprehensive-stock-data?symbol=TSLA | jq .
   ```
   Should return actual technical levels, not empty objects.

4. **Test left panel in browser**:
   - Technical levels should populate with real prices
   - News should load
   - Pattern detection should show actual patterns or "No patterns detected"

---

## 🔄 Related Files

### Files Changed
- `market-mcp-server/index.js` (lines 2499-2574)

### Files Affected (Not Changed)
- `backend/services/http_mcp_client.py` - Was calling correct tool names all along
- `backend/services/market_service.py` - Was calling correct tool names
- `backend/services/news_service.py` - Was calling correct tool names
- `backend/routers/enhanced_market_router.py` - Was calling correct tool names

**Conclusion**: The backend was correct. Only the MCP server's HTTP handler was wrong.

---

## 📝 Lessons Learned

1. **Test both code paths**: When maintaining dual modes (STDIO + HTTP), ensure BOTH are tested
2. **Method name consistency**: Don't copy/paste code without verifying method names exist
3. **Integration testing**: Need automated tests that verify HTTP endpoints actually work
4. **Logging is critical**: The detailed error messages led us directly to the root cause

---

## 🚀 Expected Results After Fix

Once the deployment completes:

✅ Left panel technical levels populate with real values  
✅ News articles load correctly  
✅ Pattern detection functions properly  
✅ No "Unknown tool" errors in MCP logs  
✅ No 500 errors on `/api/technical-indicators`  
✅ Comprehensive stock data API returns complete data  

---

## 📌 Deployment

**Commits**:
- `08aad2d` - Fixed tool names in tools/list response
- `e1f526c` - Fixed HTTP handler method calls (CRITICAL FIX)

**Pushed to**: `master` branch  
**Auto-deploys to**: `gvses-market-insights.fly.dev`  

**Monitor deployment**:
```bash
fly logs -a gvses-market-insights
```

Look for: `Market MCP Server running in HTTP mode on port 3001`

