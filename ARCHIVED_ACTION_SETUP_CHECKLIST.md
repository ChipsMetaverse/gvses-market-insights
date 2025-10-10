# ✅ Agent Builder Actions - 5-Minute Setup Checklist

## What You Have Right Now

- ✅ OpenAPI spec generated: `backend/openapi_agent_builder.json`
- ✅ Backend running: https://gvses-market-insights.fly.dev (and localhost:8000)
- ✅ G'sves Agent in Agent Builder: `wf_68e474d14d28819085`
- ✅ Knowledge base uploaded (4 files)
- ❌ **Missing**: API actions for live data

---

> **📌 Integration Approach Note**
>
> Agent Builder offers two ways to connect to your backend:
>
> 1. **Actions (OpenAPI)** - This guide ← **Recommended for localhost development**
>    - Works with your current setup immediately
>    - FastAPI wraps MCP servers and exposes REST endpoints
>    - Curated tool surface (5 key endpoints)
>    - Easier debugging and security
>
> 2. **MCP Node** - Alternative approach (see `MCP_NODE_MIGRATION_GUIDE.md`)
>    - Requires hosting MCP servers publicly (not localhost)
>    - Requires network transport (HTTP/SSE/WebSocket)
>    - Automatic tool discovery (all 35+ tools)
>    - Consider after Actions approach is working
>
> Since your MCP servers run on localhost, **Actions is the correct choice now**.

---

## 🎯 Quick Setup (Do This Now)

### Step 1: Import API Actions (2 minutes)

1. **Open Agent Builder**: https://platform.openai.com/agent-builder
2. **Open your workflow**: `wf_68e474d14d28819085`
3. **Click "Actions"** in left sidebar
4. **Create Action** → **Import from OpenAPI**
5. **Select file**: `backend/openapi_agent_builder.json` from your computer
6. **Review operations**: Should show 5 endpoints:
   - ✅ getStockPrice
   - ✅ getStockHistory
   - ✅ searchSymbol
   - ✅ getStockNews
   - ✅ getMarketOverview
7. **Set Base URL**: `https://gvses-market-insights.fly.dev`
   - (Or use `http://localhost:8000` for testing)
8. **Authentication**: None (public endpoints)
9. **Click "Create Action"**

### Step 2: Enable Actions on Agent (1 minute)

1. **Click G'sves Agent node** on canvas
2. **Scroll to Actions section**
3. **Toggle ON**: The action you just created
4. **Save changes**

### Step 3: Update Instructions (2 minutes)

1. **Click G'sves Agent node**
2. **Click "Instructions" tab**
3. **Copy from**: `AGENT_BUILDER_SYSTEM_INSTRUCTIONS.md`
4. **Paste** (replaces existing instructions)
5. **Save changes**

### Step 4: Test (1 minute)

1. **Click "Preview"** button (top right)
2. **Type**: "What is the current price of AAPL?"
3. **Expected**: Agent calls getStockPrice, returns real price
4. **If it works**: You're done! 🎉
5. **If it fails**: See troubleshooting below

---

## 🧪 Test Cases

Run these 3 tests in preview mode:

### Test 1: Simple Price Query
```
Input: "What is the current price of AAPL?"
Expected: Real-time price with change %
Tool Called: getStockPrice(symbol="AAPL")
```

### Test 2: Company Name Resolution
```
Input: "Show me Microsoft's price"
Expected: Agent searches for MSFT, then gets price
Tools Called:
1. searchSymbol(query="Microsoft")
2. getStockPrice(symbol="MSFT")
```

### Test 3: Trading Analysis
```
Input: "Give me a trade setup for TSLA"
Expected: LTB/ST/QE analysis with entry/stop/target
Tools Called:
1. getStockPrice(symbol="TSLA")
2. getStockHistory(symbol="TSLA", days=90)
3. getStockNews(symbol="TSLA", limit=10)
```

---

## 🐛 Troubleshooting

### "Action failed to execute"
**Check**:
- Is backend URL correct? Try: `curl https://gvses-market-insights.fly.dev/health`
- Are you using production URL (not localhost)?
- Network tab in browser for actual error

**Fix**:
- Try localhost URL: `http://localhost:8000` if production is down
- Or use ngrok: `ngrok http 8000` and use that URL

### "Agent doesn't call functions"
**Symptom**: Agent answers from knowledge base instead of calling tools

**Fix**:
1. Verify Action is enabled on G'sves Agent node (toggle ON)
2. Check system instructions include "ALWAYS call tools for live data"
3. Test with explicit command: "Call getStockPrice for AAPL"

### "Invalid symbol" error
**Expected behavior**: Backend returns 404 for invalid symbols

**Fix**: Use searchSymbol for company names first

### Production URL returns "Wagyu Club"
**Issue**: Fly.io routing problem

**Workaround**:
1. Use localhost for now: `http://localhost:8000`
2. Fix production later with `fly deploy`

---

## 📸 Visual Checklist

After completing setup, you should see:

**In Agent Builder:**
- ✅ Actions section shows "Market Data API" (or similar name)
- ✅ 5 operations listed under the action
- ✅ G'sves Agent node has green "Actions: 1" indicator
- ✅ Preview mode shows tool calls in conversation log

**In Preview Test:**
```
User: What is the current price of AAPL?

[Tool Call] getStockPrice(symbol="AAPL")
[Tool Response] {"symbol": "AAPL", "price": 178.32, "change": 3.45...}

G'sves: Apple is currently trading at $178.32, up $3.45 or
2.1% today. Volume is healthy at 48M shares. The stock is
holding above its key $175 support level...
```

---

## 🚀 Next Steps (After Basic Tools Work)

1. **Add more endpoints** (optional):
   - `/api/technical-indicators` - RSI, MACD, Bollinger Bands
   - `/api/options-chain` - Options data
   - `/api/comprehensive-stock-data` - All-in-one endpoint

2. **Implement 5-node architecture**:
   - See `AGENT_BUILDER_ASSISTANT_INSTRUCTIONS.md`
   - Adds intent classification and routing
   - Separates chart commands (fast path) from analysis (deep path)

3. **Monitor performance**:
   - Check Action call logs in Agent Builder
   - Monitor backend logs: `fly logs` or `uvicorn` output
   - Track success rates and latency

4. **Publish workflow**:
   - Once testing passes, click "Publish"
   - Version: `v1.0 - Basic Actions Integration`
   - Copy workflow ID for backend integration

---

## 📊 Expected Performance

After setup:

| Query Type | Expected Latency | Tools Called |
|------------|------------------|--------------|
| Simple price | 500-800ms | getStockPrice (1 call) |
| Company search | 1-1.5s | searchSymbol + getStockPrice (2 calls) |
| Trading analysis | 3-5s | getStockPrice + getStockHistory + getStockNews (3 calls) |
| Market overview | 800-1200ms | getMarketOverview (1 call) |

---

## ✅ Success Criteria

You've completed setup when:

- [x] Action imported with 5 operations
- [x] Action enabled on G'sves Agent node
- [x] System instructions updated to use tools
- [x] Test query "What is AAPL price?" returns live data
- [x] Tool calls visible in preview logs
- [x] Agent responds naturally using tool data

---

## 💡 Pro Tips

1. **Start simple**: Test with just getStockPrice first
2. **Check logs**: Always look at tool call logs in preview
3. **Iterate instructions**: Refine system prompt based on agent behavior
4. **Use examples**: Add example tool calls to instructions if agent doesn't call them
5. **Monitor backend**: Keep an eye on backend logs for errors

---

## 📚 Reference Documents

- `backend/openapi_agent_builder.json` ← Import this file
- `AGENT_BUILDER_ACTIONS_GUIDE.md` ← Detailed setup guide
- `AGENT_BUILDER_SYSTEM_INSTRUCTIONS.md` ← Copy-paste for instructions
- `QUICK_START_GUIDE.md` ← Original workflow setup

---

**Status**: Ready for immediate use
**Time to complete**: 5-10 minutes
**Difficulty**: Easy (mostly copy-paste and toggle switches)

**Next action**: Open Agent Builder → Import OpenAPI → Enable Action → Test! 🚀
