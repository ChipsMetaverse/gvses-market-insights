# Agent Builder Backend Integration Guide

**Created**: October 9, 2025
**Purpose**: Explain how Agent Builder integrates with your existing G'sves backend
**Audience**: Developers configuring Agent Builder workflows

---

## Current Architecture Reality

### What You Actually Have

Your G'sves system already has **all the infrastructure needed** for Agent Builder integration:

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Current System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (g-vses.fly.dev)                                  │
│         ↓                                                    │
│  Backend FastAPI (gvses-market-insights.fly.dev)           │
│         ├─ REST API Endpoints (HTTP)                       │
│         ├─ market-mcp-server (Node.js subprocess)          │
│         └─ alpaca-mcp-server (Python subprocess)           │
│                ↓                                            │
│         Yahoo Finance + CNBC + Alpaca Markets              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Facts

**MCP Servers Run as Subprocesses**:
- `market-mcp-server`: Node.js process spawned by backend
- Communication: STDIO (stdin/stdout), NOT HTTP
- Location: Inside `gvses-market-insights` Docker container
- Managed by: `backend/mcp_client.py` (MCPClient class)

**Backend Exposes REST API**:
- Already deployed: `https://gvses-market-insights.fly.dev`
- Endpoints wrap MCP functionality
- Returns JSON responses
- Production-ready and tested

**No Separate MCP Deployment Needed**:
- ❌ Do NOT deploy market-mcp-server to Fly.io
- ❌ Do NOT create standalone HTTP MCP server
- ✅ Use existing backend REST API endpoints

---

## Agent Builder Integration Options

### Option 1: Agent Node with Function Calling (Recommended)

Agent Builder's Agent node can call HTTP APIs directly using OpenAI function calling.

**Configuration:**

```yaml
Node Type: Agent
Model: gpt-4o
Instructions: |
  You are G'sves, a professional trading assistant.

  You have access to real-time market data tools:
  - get_stock_price: Get current stock price
  - get_stock_history: Get historical price data
  - get_stock_news: Get latest market news

  Use these tools to answer user questions about the market.
  Always cite your data source and provide context.

Tools:
  - Type: Function
    Name: get_stock_price
    Description: Get current stock price and quote data
    Parameters:
      symbol:
        type: string
        description: Stock ticker symbol (e.g., TSLA, AAPL)
        required: true
    HTTP Config:
      URL: https://gvses-market-insights.fly.dev/api/stock-price
      Method: GET
      Query Parameters:
        symbol: {{symbol}}

  - Type: Function
    Name: get_stock_history
    Description: Get historical price data for charting
    Parameters:
      symbol:
        type: string
        description: Stock ticker symbol
        required: true
      days:
        type: integer
        description: Number of days of history (default 100)
        required: false
        default: 100
    HTTP Config:
      URL: https://gvses-market-insights.fly.dev/api/stock-history
      Method: GET
      Query Parameters:
        symbol: {{symbol}}
        days: {{days}}

  - Type: Function
    Name: get_stock_news
    Description: Get latest market news for a symbol
    Parameters:
      symbol:
        type: string
        description: Stock ticker symbol
        required: true
    HTTP Config:
      URL: https://gvses-market-insights.fly.dev/api/stock-news
      Method: GET
      Query Parameters:
        symbol: {{symbol}}
```

### Option 2: Custom Tool Node (Alternative)

If Agent Builder supports Custom Tool nodes, you can wrap backend APIs:

```yaml
Node Type: Custom Tool
Name: Market Data Tool
Base URL: https://gvses-market-insights.fly.dev/api
Endpoints:
  - /stock-price?symbol={symbol}
  - /stock-history?symbol={symbol}&days={days}
  - /stock-news?symbol={symbol}
```

---

## Available Backend Endpoints

### Core Market Data

**GET /api/stock-price**
```bash
# Request
curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=TSLA"

# Response (300-400ms)
{
  "symbol": "TSLA",
  "price": 242.50,
  "change": 5.23,
  "percent_change": 2.20,
  "volume": 125000000,
  "data_source": "alpaca",
  "timestamp": "2025-10-09T14:30:00Z"
}
```

**GET /api/stock-history**
```bash
# Request
curl "https://gvses-market-insights.fly.dev/api/stock-history?symbol=TSLA&days=100"

# Response (400-500ms)
{
  "symbol": "TSLA",
  "bars": [
    {
      "timestamp": "2025-10-09T09:30:00Z",
      "open": 240.00,
      "high": 245.00,
      "low": 239.50,
      "close": 242.50,
      "volume": 5000000
    }
    // ... 100 days of data
  ],
  "data_source": "alpaca"
}
```

**GET /api/stock-news**
```bash
# Request
curl "https://gvses-market-insights.fly.dev/api/stock-news?symbol=TSLA"

# Response (3-5s)
{
  "symbol": "TSLA",
  "articles": [
    {
      "title": "Tesla Q3 Earnings Beat Expectations",
      "source": "CNBC",
      "url": "https://...",
      "published_at": "2025-10-09T10:00:00Z",
      "summary": "Tesla reported..."
    }
    // ... more articles
  ],
  "data_source": "mcp" // Uses market-mcp-server subprocess
}
```

**GET /api/symbol-search**
```bash
# Request
curl "https://gvses-market-insights.fly.dev/api/symbol-search?query=microsoft&limit=10"

# Response (<500ms)
{
  "results": [
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "exchange": "NASDAQ",
      "asset_class": "us_equity"
    }
    // ... more results
  ],
  "data_source": "alpaca"
}
```

### Performance Characteristics

| Endpoint | Response Time | Data Source | Notes |
|----------|---------------|-------------|-------|
| /api/stock-price | 300-400ms | Alpaca (primary) | Falls back to Yahoo via MCP |
| /api/stock-history | 400-500ms | Alpaca (primary) | Professional-grade bars |
| /api/stock-news | 3-5s | MCP (CNBC + Yahoo) | Subprocess call |
| /api/symbol-search | <500ms | Alpaca Asset DB | Semantic search |

---

## Agent Builder Workflow Example

Here's a complete 5-node workflow using the backend API:

```
Start
  ↓
[Classification Agent]
  ├─ Model: gpt-4o-mini
  ├─ Instructions: "Classify user intent: market_data or general_chat"
  └─ Output: classification_result
  ↓
[If/Else Router]
  ├─ Condition: classification_result == "market_data"
  ├─ True Path → [G'sves Agent with Backend API Tools]
  └─ False Path → [Chat Handler]
  ↓
[Response Formatter]
  └─ Format for voice delivery
  ↓
End
```

**G'sves Agent Node Configuration:**
- Model: gpt-4o
- Instructions: Trading assistant personality
- Tools: 3 functions (stock-price, stock-history, stock-news)
- Each function calls backend REST API
- No MCP Node needed!

---

## Testing Backend Integration

### 1. Test Endpoints Directly

```bash
# Test from terminal
curl "https://gvses-market-insights.fly.dev/health"
# Expected: {"status": "healthy", "timestamp": "..."}

curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=AAPL"
# Expected: Quote data with price, change, volume
```

### 2. Test in Agent Builder Preview

1. Configure Agent node with backend API functions
2. Click "Preview" button
3. Ask: "What's Tesla's price?"
4. Verify:
   - Agent calls get_stock_price function
   - Function makes HTTP request to backend
   - Response contains TSLA price data
   - Agent formats response naturally

### 3. Monitor Backend Logs

```bash
# Watch backend logs in real-time
fly logs --app gvses-market-insights -f

# Look for:
# - "Fetching Alpaca quote for TSLA" (success path)
# - "Falling back to MCP for TSLA" (fallback path)
# - Response times in logs
```

---

## Why This Architecture Works

### No Separate MCP Deployment Needed

**Agent Builder Requirement**: HTTP endpoints
**What You Have**: REST API wrapping MCP functionality
**Result**: Perfect match, no additional infrastructure

### MCP Servers Already Managed

- Backend spawns market-mcp-server subprocess on startup
- Process lifecycle managed by MCPClient class
- Automatic restarts on failure
- Memory-optimized for Docker environment
- Production-proven and stable

### Performance Optimized

- Alpaca API: 300-400ms (primary data source)
- MCP fallback: 3-15s (only when needed)
- Intelligent routing based on data source availability
- 5-second cache for frequently accessed symbols

### Zero Additional Deployment

- No new Fly.io apps needed
- No additional infrastructure costs
- No MCP HTTP server to maintain
- Backend already handles everything

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Trying to Deploy market-mcp-server Separately
```bash
# DON'T DO THIS!
cd market-mcp-server
fly launch --name market-mcp
```

**Why Wrong**: market-mcp-server is a STDIO process, not an HTTP server

### ❌ Mistake 2: Expecting MCP Protocol in Agent Builder
```yaml
# DON'T DO THIS!
Node Type: MCP
URL: https://gvses-market-insights.fly.dev
```

**Why Wrong**: Backend exposes REST API, not MCP protocol

### ❌ Mistake 3: Creating HTTP MCP Wrapper
```python
# DON'T DO THIS!
@app.post("/mcp/tools/{tool_name}")
async def mcp_proxy(tool_name: str):
    # Unnecessary complexity!
```

**Why Wrong**: Backend REST API already exposes needed functionality

### ✅ Correct Approach: Use Existing REST API
```yaml
# DO THIS!
Node Type: Agent
Tools:
  - Function: get_stock_price
    HTTP: GET /api/stock-price?symbol={symbol}
```

---

## Migration from Python Agent Orchestrator

If you currently use `backend/services/agent_orchestrator.py`:

**Current Flow:**
```
Voice → Backend → AgentOrchestrator (Python) → MCP → Response
```

**Agent Builder Flow:**
```
Voice → Backend → Agent Builder (OpenAI) → Backend REST API → Response
```

**Migration Steps:**
1. Keep existing backend API endpoints unchanged
2. Configure Agent Builder with backend URLs
3. Test Agent Builder in preview mode
4. A/B test: 10% traffic to Agent Builder
5. Monitor latency and accuracy
6. Gradually increase to 100%
7. Deprecate Python orchestrator

---

## Debugging Tips

### Agent Builder Not Getting Data

**Check:**
1. Backend health: `curl https://gvses-market-insights.fly.dev/health`
2. API endpoint response: `curl https://gvses-market-insights.fly.dev/api/stock-price?symbol=TSLA`
3. Function call configuration in Agent Builder
4. Query parameter mapping: `{{symbol}}` syntax

### Slow Response Times

**Check:**
1. Data source in response: `"data_source": "alpaca"` (fast) vs `"yahoo_mcp"` (slower)
2. Backend logs for fallback messages
3. Alpaca API credentials configured correctly
4. MCP subprocess healthy: Look for startup messages in logs

### Function Calls Failing

**Check:**
1. URL correctness: `https://` (not `http://`)
2. Query parameters match API: `symbol` (not `ticker`)
3. Required parameters provided
4. Backend API returns 200 status code

---

## Summary

**Key Takeaways:**

1. ✅ **MCP servers already running** inside backend as subprocesses
2. ✅ **REST API already exposed** at gvses-market-insights.fly.dev
3. ✅ **No separate deployment needed** for market-mcp-server
4. ✅ **Agent Builder uses existing backend** via HTTP function calls
5. ✅ **Zero additional infrastructure** required

**Next Steps:**

1. Open Agent Builder: https://platform.openai.com/playground/agents
2. Create workflow with Agent node
3. Configure backend API functions (copy from this guide)
4. Test in preview mode
5. Publish workflow
6. Integrate with backend via workflow ID

**Time Estimate:** 4-5 hours (no infrastructure work needed!)

---

**Questions?** Check the main guides:
- SINGLE_SCREEN_SETUP_GUIDE.md - Step-by-step implementation
- AGENT_BUILDER_MASTER_GUIDE.md - Comprehensive reference
