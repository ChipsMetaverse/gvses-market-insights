# Agent Builder Actions Setup Guide

## 📋 Overview

This guide walks you through connecting your G'sves Agent Builder workflow to the backend APIs so it can fetch real-time market data.

**Problem**: Agent has knowledge base but can't fetch live prices → **Solution**: Add Actions (API integrations)

---

## 🎯 Quick Start (15 minutes)

### Step 1: Open Your Workflow
1. Go to: https://platform.openai.com/agent-builder
2. Open workflow: `wf_68e474d14d28819085`
3. You should see your G'sves Agent node

### Step 2: Import OpenAPI Spec

**Option A: Import from File** (Recommended)
1. Click **Actions** in left sidebar
2. Click **Create Action** → **Import from OpenAPI**
3. Select file: `backend/openapi_agent_builder.json`
4. Review imported operations (should see 5 endpoints)
5. Click **Create Action**

**Option B: Import from URL**
If you have the backend running locally:
1. Click **Create Action** → **Import from URL**
2. URL: `http://localhost:8000/openapi.json`
3. (Note: This won't work for production - use Option A)

**Option C: Manual Entry** (If import fails)
See "Manual Action Creation" section below.

### Step 3: Configure Action Settings

1. **Action Name**: `Market Data API`
2. **Base URL**:
   - Development: `http://localhost:8000`
   - **Production**: `https://gvses-market-insights.fly.dev`
3. **Authentication**:
   - For testing: None (endpoints are public)
   - For production: Add API key if needed
4. **Timeout**: 30 seconds (news endpoint can be slow)

### Step 4: Attach Action to G'sves Agent

1. Click on **G'sves Agent** node in canvas
2. Scroll to **Actions** section
3. Toggle ON: **Market Data API**
4. Save changes

### Step 5: Update System Instructions

Click G'sves Agent → **Instructions** → Add this to the top:

```
TOOL USAGE INSTRUCTIONS:
- When users ask for current prices, ALWAYS call getStockPrice(symbol)
- When users ask for charts or history, ALWAYS call getStockHistory(symbol, days, interval)
- When users ask about news, ALWAYS call getStockNews(symbol)
- When users ask for market status, ALWAYS call getMarketOverview()
- When users mention a company name (e.g., "Microsoft"), first call searchSymbol(query) to get the ticker
- Do NOT answer from knowledge base alone for live data
- Always cite the data source in your response

EXISTING INSTRUCTIONS:
[Keep your existing G'sves personality and methodology instructions below]
```

---

## 🧪 Testing

### Test 1: Price Query
**Input**: "What is the current price of AAPL?"

**Expected Behavior**:
1. Agent calls `getStockPrice(symbol="AAPL")`
2. Receives response: `{"symbol": "AAPL", "price": 178.32, ...}`
3. Responds: "Apple is currently trading at $178.32, up 2.1%..."

**If it fails**:
- Check Action is enabled on the node
- Verify base URL is correct
- Check network tab for errors

### Test 2: Company Name Resolution
**Input**: "Show me Microsoft's price"

**Expected Behavior**:
1. Agent calls `searchSymbol(query="Microsoft")`
2. Gets `{"results": [{"symbol": "MSFT", "name": "Microsoft Corporation"}]}`
3. Then calls `getStockPrice(symbol="MSFT")`
4. Responds with price

### Test 3: News Query
**Input**: "What's the latest news on Tesla?"

**Expected Behavior**:
1. Agent calls `getStockNews(symbol="TSLA")`
2. Receives array of articles
3. Summarizes top 3-5 articles

### Test 4: Market Overview
**Input**: "How's the market doing today?"

**Expected Behavior**:
1. Agent calls `getMarketOverview()`
2. Gets S&P 500, NASDAQ, Dow Jones data
3. Summarizes market status

---

## 📝 Manual Action Creation

If OpenAPI import doesn't work, create functions manually:

### Function 1: getStockPrice
```json
{
  "name": "getStockPrice",
  "description": "Get real-time stock price and market data",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
      }
    },
    "required": ["symbol"]
  },
  "url": "https://gvses-market-insights.fly.dev/api/stock-price",
  "method": "GET"
}
```

### Function 2: getStockHistory
```json
{
  "name": "getStockHistory",
  "description": "Get historical OHLCV data for charting",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "days": {
        "type": "integer",
        "description": "Number of days (default: 30)",
        "default": 30
      },
      "interval": {
        "type": "string",
        "enum": ["1m", "5m", "15m", "1h", "1d"],
        "description": "Candle interval (default: 1d)",
        "default": "1d"
      }
    },
    "required": ["symbol"]
  },
  "url": "https://gvses-market-insights.fly.dev/api/stock-history",
  "method": "GET"
}
```

### Function 3: searchSymbol
```json
{
  "name": "searchSymbol",
  "description": "Search for stock symbols by company name",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Company name or ticker to search"
      },
      "limit": {
        "type": "integer",
        "description": "Max results (default: 10)",
        "default": 10
      }
    },
    "required": ["query"]
  },
  "url": "https://gvses-market-insights.fly.dev/api/symbol-search",
  "method": "GET"
}
```

### Function 4: getStockNews
```json
{
  "name": "getStockNews",
  "description": "Get recent news articles for a symbol",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock ticker symbol"
      },
      "limit": {
        "type": "integer",
        "description": "Max articles (default: 10)",
        "default": 10
      }
    },
    "required": ["symbol"]
  },
  "url": "https://gvses-market-insights.fly.dev/api/stock-news",
  "method": "GET"
}
```

### Function 5: getMarketOverview
```json
{
  "name": "getMarketOverview",
  "description": "Get current market indices status",
  "parameters": {
    "type": "object",
    "properties": {}
  },
  "url": "https://gvses-market-insights.fly.dev/api/market-overview",
  "method": "GET"
}
```

---

## 🔧 Troubleshooting

### "Action failed to execute"
- **Check**: Is backend reachable? Try: `curl https://gvses-market-insights.fly.dev/health`
- **Check**: Are you using the production URL, not localhost?
- **Check**: Network tab in Agent Builder for actual error

### "Agent doesn't call the function"
- **Fix**: Update system instructions to explicitly tell agent to use tools
- **Fix**: Add examples in instructions showing tool usage
- **Fix**: Test with direct command: "Call getStockPrice for AAPL"

### "Invalid symbol" errors
- **Expected**: Some symbols are invalid (e.g., "ITS", "XYZABC")
- **Solution**: Use searchSymbol first for company names
- **Backend validation**: Returns 404 for invalid symbols

### Production URL returns "Wagyu Club"
- **Issue**: Fly.io deployment may have routing issue
- **Workaround**: Use localhost for testing, fix deployment later
- **Check**: `fly status` to see if app is running

---

## 📊 Production Deployment Notes

### Current Status:
- ✅ Backend deployed: `gvses-market-insights.fly.dev`
- ⚠️ May have routing issues (returns "Wagyu Club" instead of API)
- ✅ Localhost version works perfectly

### To Fix Production:
1. Check Fly.io logs: `fly logs`
2. Verify environment variables are set
3. Test health endpoint: `curl https://gvses-market-insights.fly.dev/health`
4. If needed, redeploy: `fly deploy`

### Alternative: Use ngrok for Testing
If Fly.io has issues:
```bash
# Terminal 1: Run backend
cd backend && uvicorn mcp_server:app --reload --port 8000

# Terminal 2: Expose via ngrok
ngrok http 8000

# Use the ngrok URL in Agent Builder
# Example: https://abcd-1234.ngrok.io
```

---

## ✅ Success Criteria

After completing this guide, you should have:

- [x] Action created in Agent Builder with 5 operations
- [x] Action attached to G'sves Agent node
- [x] System instructions updated to use tools
- [x] Test query "What is AAPL price?" returns live data
- [x] Agent calls correct functions automatically
- [x] Company name resolution works (searchSymbol)

---

## 🚀 Next Steps

Once tools are working:

1. **Implement 5-node architecture** (see `AGENT_BUILDER_ASSISTANT_INSTRUCTIONS.md`)
   - Intent Classifier → faster routing
   - Branch → separate chart commands from analysis
   - Specialized paths for different query types

2. **Add more tools** (optional):
   - `/api/technical-indicators` - RSI, MACD, etc.
   - `/api/options-chain` - Options data
   - `/api/analyst-ratings` - Professional ratings

3. **Monitor usage**:
   - Check Action call logs in Agent Builder
   - Monitor backend logs for errors
   - Track latency and success rates

---

**Created**: October 7, 2025
**Status**: Ready for implementation
**Next Action**: Import `openapi_agent_builder.json` into Agent Builder → Test with "What is AAPL price?" ⚡
