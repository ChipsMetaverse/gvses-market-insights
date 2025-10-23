# News Display Investigation - Testing Guide
**Date:** October 23, 2025  
**Issue:** Frontend news display investigation  
**Critical Fix:** MCP server crash bug resolved (commit `b41da37`)

---

## 🔴 **CRITICAL FIX DEPLOYED**

### **MCP Server Crash Bug**
**Symptom:** Server crashes every 5 minutes during session cleanup  
**Root Cause:** Attempted to call `.close()` on plain metadata objects  
**Fix:** Removed `.close()` call from cleanup interval  
**Status:** ✅ **FIXED** and pushed to production

---

## 🧪 **TESTING STEPS TO EXECUTE**

### **STEP 1: Restart MCP Server with Fix**

```bash
# Kill any existing MCP server instances
pkill -f "node.*index.js 3001"

# Wait 2 seconds
sleep 2

# Start MCP server with fix
cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp/market-mcp-server
node index.js 3001 2>&1 | tee /tmp/mcp-fixed.log &

# Verify it started
sleep 3
curl -sS http://localhost:3001/mcp -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05"},"id":1}' \
  | jq '.result.serverInfo'
```

**Expected Output:**
```json
{
  "name": "market-mcp-server",
  "version": "1.0.0"
}
```

---

### **STEP 2: Restart Backend (Clear Stale Sessions)**

```bash
# Kill existing backend
pkill -f "uvicorn mcp_server:app"

# Wait 2 seconds
sleep 2

# Start fresh backend
cd /Volumes/WD\ My\ Passport\ 264F\ Media/claude-voice-mcp/backend
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload 2>&1 | tee /tmp/backend-test.log &

# Verify health
sleep 5
curl -sS http://localhost:8000/health | jq '{status, features}'
```

**Expected Output:**
```json
{
  "status": "healthy",
  "features": {"advanced_ta": true}
}
```

---

### **STEP 3: Test News Endpoint**

```bash
# Test news fetch
curl -sS "http://localhost:8000/api/stock-news?symbol=TSLA&limit=3" | jq '{
  symbol,
  news_count: (.news | length),
  first_item: (if (.news | length) > 0 then {
    headline: .news[0].headline,
    source: .news[0].source,
    published: .news[0].published
  } else "No news" end)
}'
```

**Expected Output (if working):**
```json
{
  "symbol": "TSLA",
  "news_count": 3,
  "first_item": {
    "headline": "Tesla Stock Analysis...",
    "source": "CNBC",
    "published": "2025-10-23T..."
  }
}
```

**Expected Output (if MCP news fails):**
```json
{
  "symbol": null,
  "news_count": 0,
  "first_item": "No news"
}
```

---

### **STEP 4: Frontend Verification**

#### **4A. Open Browser to Dashboard**
```bash
# Frontend should already be running on http://localhost:5174
# Open in browser:
open http://localhost:5174
# Or manually navigate to http://localhost:5174
```

#### **4B. Check News Panel (Left Side)**

**Location:** Left panel → Below "TECHNICAL LEVELS" section

**What to Look For:**

**Scenario 1: News Loading ✅**
```
NEWS
▸ Tesla Stock Surges on Earnings Beat
  Source: CNBC • 2h ago
  
▸ Analysts Upgrade TSLA to Buy
  Source: Yahoo Finance • 5h ago
```

**Scenario 2: No News Available ⚠️**
```
NEWS
No recent news available.
```

**Scenario 3: Error Message ❌**
```
NEWS
Failed to load news. Please try again.
```

#### **4C. Check Browser Console**

Press `F12` or `Cmd+Option+I` to open DevTools → Console tab

**Look for:**
- ✅ `GET /api/stock-news?symbol=TSLA&limit=6 200 OK`
- ❌ `GET /api/stock-news?symbol=TSLA&limit=6 500 Internal Server Error`
- ⚠️ `Auto-fetch failed: AxiosError`

---

### **STEP 5: Monitor MCP Server Stability**

**Important:** Wait at least 6 minutes to verify the crash is fixed!

```bash
# Check if MCP server is still running after 6+ minutes
sleep 360  # Wait 6 minutes

# Verify server is still alive
lsof -i :3001 | grep LISTEN

# Check logs for any errors
tail -50 /tmp/mcp-fixed.log | grep -E "ERROR|Cleaning up stale|TypeError"
```

**Expected Output:**
```
node    [PID]  localhost:redwood-broker (LISTEN)
[Session] Cleaning up stale session: [session-id]
```

**No crashes or TypeErrors!**

---

## 🔍 **DIAGNOSTIC COMMANDS**

### **Check All Services**
```bash
echo "=== Frontend ==="
lsof -i :5174 | grep LISTEN

echo "=== Backend ==="
lsof -i :8000 | grep LISTEN

echo "=== MCP Server ==="
lsof -i :3001 | grep LISTEN
```

### **Check Backend Logs for News Errors**
```bash
tail -100 /tmp/backend-test.log | grep -A5 "stock-news"
```

### **Check MCP Server Logs**
```bash
tail -100 /tmp/mcp-fixed.log | grep -E "getMarketNews|CNBC|TypeError"
```

### **Test MCP News Tool Directly**
```bash
# Initialize session
SESSION_ID=$(curl -sS -X POST http://127.0.0.1:3001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05"},"id":1}' \
  | jq -r '.result.serverInfo.name' && \
  curl -sS -I -X POST http://127.0.0.1:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05"},"id":1}' \
  | grep -i mcp-session-id | awk '{print $2}' | tr -d '\r')

echo "Session ID: $SESSION_ID"

# Call get_market_news
curl -sS -X POST http://127.0.0.1:3001/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Mcp-Session-Id: $SESSION_ID" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_market_news","arguments":{"limit":3}},"id":2}' \
  | jq '.result.content[0].text' | jq 'fromjson | {count: .count, first_headline: .articles[0].title}'
```

---

## 📊 **KNOWN ISSUES**

### **Issue 1: CNBC API Failures**
**Symptom:** `CNBC approach failed: All API endpoints failed`  
**Cause:** CNBC's API is rate-limited or temporarily unavailable  
**Impact:** News returns empty array  
**Workaround:** Yahoo Finance fallback should supplement  

### **Issue 2: News Count Inconsistency**
**Symptom:** Sometimes returns 6 items, sometimes 0  
**Cause:** MCP tool may be returning errors intermittently  
**Investigation:** Check `backend/services/news_service.py` line 30-31 logging

### **Issue 3: Frontend Not Displaying News**
**Possible Causes:**
1. News array is empty from backend
2. Frontend component not rendering news items
3. CSS hiding news elements
4. News data structure mismatch

---

## 🎯 **VERIFICATION CHECKLIST**

### **Backend Health**
- [ ] Backend responds to `/health`
- [ ] Backend returns `{"status": "healthy"}`
- [ ] MCP connection established

### **News Endpoint**
- [ ] `/api/stock-news?symbol=TSLA` returns 200 OK
- [ ] Response contains `{"news": [...]}`
- [ ] News array has items (or is intentionally empty)

### **MCP Server**
- [ ] Server running on port 3001
- [ ] Responds to initialize request
- [ ] `get_market_news` tool callable
- [ ] **NO CRASHES after 6+ minutes** ✅

### **Frontend UI**
- [ ] Dashboard loads successfully
- [ ] Technical levels display
- [ ] News panel visible
- [ ] News items render (if available)
- [ ] No console errors

---

## 📸 **SCREENSHOTS NEEDED**

If testing manually, capture:

1. **Browser DevTools → Network Tab**
   - Filter: `stock-news`
   - Show request/response

2. **Browser DevTools → Console Tab**
   - Any errors related to news

3. **Dashboard Left Panel**
   - Show news section (with or without items)

4. **Terminal: MCP Server Logs**
   - After 6+ minutes of uptime
   - Show "Cleaning up stale session" without crashes

---

## 🚀 **NEXT STEPS AFTER VERIFICATION**

### **If News Works:**
✅ Mark news display as functional  
✅ Document CNBC fallback behavior  
✅ Deploy to production

### **If News Shows Empty:**
1. Check if `get_market_news` returns data
2. Verify news_service.py parsing logic
3. Check frontend component rendering

### **If Frontend Doesn't Display:**
1. Verify news data structure matches frontend expectations
2. Check CSS display properties
3. Verify component is actually rendering news items

---

## 📝 **REPORTING RESULTS**

Please share:
1. Output from STEP 1 (MCP server start)
2. Output from STEP 3 (news endpoint test)
3. Browser screenshot of news panel
4. Any console errors
5. Confirmation that MCP server doesn't crash after 6+ minutes

---

**Ready to test!** The critical crash bug is fixed. Now we need to verify news display in the actual UI.

