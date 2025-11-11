# Market MCP Server - Current Capabilities

**Location**: `/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server/`  
**Deployed**: `gvses-mcp-sse-server.fly.dev`  
**Status**: ✅ Running in production  
**Protocols**: SSE ✅ | HTTP ✅ | Stdio ✅

---

## 🎯 **What This Server Does**

The Market MCP Server is a **comprehensive financial data aggregation and analysis platform** that provides 35+ tools for accessing real-time and historical market data. It acts as a **unified interface** to multiple financial data sources.

### **Primary Purpose:**
Provide AI agents (like ChatKit/Agent Builder) with tools to:
- Fetch stock quotes, prices, and fundamentals
- Stream real-time market data
- Calculate technical indicators
- Get market news and sentiment
- Track portfolios and watchlists
- Access crypto, forex, commodities, and economic data

---

## 📊 **Complete Tool Inventory (35 Tools)**

### **Stock Market Data (6 tools)**
1. ✅ `get_stock_quote` - Real-time stock quote with detailed metrics
2. ✅ `get_stock_history` - Historical price data (1d to max, various intervals)
3. ✅ `stream_stock_prices` - WebSocket streaming for real-time updates
4. ✅ `get_options_chain` - Options data with strikes and expirations
5. ✅ `get_stock_fundamentals` - Financials, valuation, key statistics
6. ✅ `get_earnings_calendar` - Upcoming earnings reports

### **Cryptocurrency (5 tools)**
7. ✅ `get_crypto_price` - Live crypto prices from CoinGecko
8. ✅ `get_crypto_market_data` - Top cryptos by market cap
9. ✅ `stream_crypto_prices` - Stream crypto price updates
10. ✅ `get_defi_data` - DeFi protocol TVL and metrics
11. ✅ `get_nft_collection` - NFT collection data

### **Market Overview (4 tools)**
12. ✅ `get_market_overview` - Indices, commodities, bonds
13. ✅ `get_market_movers` - Top gainers, losers, most active
14. ✅ `get_sector_performance` - Sector rotation analysis
15. ✅ `get_fear_greed_index` - Market sentiment indicator

### **News & Analysis (7 tools)**
16. ✅ `get_market_news` - Latest market news (CNBC + others)
17. ✅ `get_cnbc_movers` - Pre-market movers from CNBC
18. ✅ `get_cnbc_sentiment` - Market sentiment from CNBC
19. ✅ `stream_market_news` - Real-time news stream with filtering
20. ✅ `get_analyst_ratings` - Wall Street ratings and price targets
21. ✅ `get_insider_trading` - Insider transaction tracking

### **Technical Analysis (3 tools)**
22. ✅ `get_technical_indicators` - RSI, MACD, Bollinger Bands, SMA, EMA, Stochastic
23. ✅ `get_support_resistance` - Calculate key price levels
24. ✅ `get_chart_patterns` - Detect patterns (head & shoulders, triangles, etc.)

### **Portfolio Management (3 tools)**
25. ✅ `create_watchlist` - Create/manage stock/crypto watchlists
26. ✅ `track_portfolio` - Track holdings, P&L, performance
27. ✅ `calculate_correlation` - Asset correlation analysis

### **Economic Data (4 tools)**
28. ✅ `get_economic_calendar` - Upcoming economic events
29. ✅ `get_treasury_yields` - US Treasury bond yields, yield curve
30. ✅ `get_commodities` - Gold, Silver, Oil, Gas prices
31. ✅ `get_forex_rates` - Foreign exchange rates

### **Price Alerts (2 tools)**
32. ✅ `set_price_alert` - Set price target alerts
33. ✅ `stream_price_alerts` - Monitor active alerts in real-time

### **Chart Control (6 tools)** ⚠️ **CRITICAL**
34. ✅ `change_chart_symbol` - Change symbol on trading chart
35. ✅ `set_chart_timeframe` - Set chart timeframe
36. ✅ `toggle_chart_indicator` - Toggle indicators on/off
37. ✅ `highlight_chart_pattern` - Highlight patterns/levels
38. ✅ `capture_chart_snapshot` - Take chart screenshots
39. ✅ `set_chart_style` - Change chart visual style

---

## 🔥 **CRITICAL DISCOVERY: Chart Control Tools Exist!**

The MCP server **ALREADY HAS** chart control tools! (Tools #34-39)

### **Existing Chart Tools:**
```javascript
// Tool 34: Change symbol
{
  name: 'change_chart_symbol',
  description: 'Change the symbol displayed on the trading chart',
  inputSchema: {
    type: 'object',
    properties: {
      symbol: { type: 'string', description: 'Stock ticker symbol (e.g., AAPL, TSLA)' }
    },
    required: ['symbol']
  }
}

// Tool 35: Set timeframe
{
  name: 'set_chart_timeframe',
  description: 'Set the timeframe for chart data display',
  inputSchema: {
    type: 'object',
    properties: {
      timeframe: {
        type: 'string',
        enum: ['1m', '5m', '15m', '30m', '1h', '4h', '1D', '1W', '1M'],
        description: 'Chart timeframe'
      }
    },
    required: ['timeframe']
  }
}

// Tool 36: Toggle indicators
{
  name: 'toggle_chart_indicator',
  description: 'Toggle technical indicators on/off on the chart',
  inputSchema: {
    type: 'object',
    properties: {
      indicator: {
        type: 'string',
        enum: ['sma', 'ema', 'rsi', 'macd', 'bollinger', 'volume'],
        description: 'Indicator type'
      },
      enabled: { type: 'boolean', description: 'Enable or disable' },
      params: { type: 'object', description: 'Indicator parameters (e.g., period: 20)' }
    },
    required: ['indicator', 'enabled']
  }
}

// Tool 37: Highlight patterns
{
  name: 'highlight_chart_pattern',
  description: 'Highlight chart patterns or levels on the trading chart',
  inputSchema: {
    type: 'object',
    properties: {
      patternType: {
        type: 'string',
        enum: ['support', 'resistance', 'trendline', 'pattern', 'fibonacci'],
        description: 'Type of pattern to highlight'
      },
      coordinates: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            price: { type: 'number' },
            time: { type: 'string' }
          }
        },
        description: 'Pattern coordinates'
      },
      label: { type: 'string', description: 'Label for the pattern' }
    },
    required: ['patternType', 'coordinates']
  }
}

// Tool 38: Capture snapshot
{
  name: 'capture_chart_snapshot',
  description: 'Capture a screenshot of the current chart state',
  inputSchema: {
    type: 'object',
    properties: {
      symbol: { type: 'string', description: 'Optional symbol to verify' },
      includeIndicators: { type: 'boolean', description: 'Include indicators in snapshot' }
    }
  }
}

// Tool 39: Set chart style
{
  name: 'set_chart_style',
  description: 'Change the visual style of the trading chart',
  inputSchema: {
    type: 'object',
    properties: {
      chartType: {
        type: 'string',
        enum: ['candlestick', 'line', 'area', 'bar'],
        description: 'Chart type'
      },
      theme: {
        type: 'string',
        enum: ['light', 'dark'],
        description: 'Color theme'
      }
    }
  }
}
```

---

## ⚠️ **THE PROBLEM**

These tools **exist in the MCP server's tool list**, but:

1. ❌ **Not implemented** - The tool handlers don't actually execute the chart commands
2. ❌ **Don't call backend** - They don't forward to our `/api/chatkit/chart-action` endpoint
3. ❌ **No drawing commands** - Can't generate `SUPPORT:`, `RESISTANCE:`, `TRENDLINE:` commands
4. ❌ **No agent orchestrator** - Don't leverage our backend's pattern detection and analysis

### **Current Tool Handler Status:**

Looking at the code, these tools likely return placeholder responses or simple messages, but **don't actually control the chart** because:
- They don't communicate with the frontend
- They don't generate chart commands
- They don't call the backend agent orchestrator

---

## 💡 **THE SOLUTION (Updated)**

### **Option A: Add `chart_control` Tool (Recommended)**
Add a **new comprehensive tool** that forwards to our backend:

```javascript
{
  name: 'chart_control',
  description: 'Comprehensive chart control: draw support/resistance, detect patterns, technical analysis',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Natural language chart request' },
      session_id: { type: 'string', description: 'ChatKit session ID' }
    },
    required: ['query']
  }
}
```

**Handler**:
```javascript
if (request.params.name === 'chart_control') {
  const response = await fetch('https://gvses-market-insights.fly.dev/api/chatkit/chart-action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request.params.arguments)
  });
  const data = await response.json();
  return {
    content: [{ type: 'text', text: data.text }],
    _meta: { chart_commands: data.chart_commands }
  };
}
```

### **Option B: Update Existing Tools**
Update the 6 existing chart tools (`change_chart_symbol`, `set_chart_timeframe`, etc.) to:
1. Call the backend agent orchestrator
2. Generate proper chart commands
3. Return structured responses with drawing instructions

---

## 🎯 **Data Sources**

The MCP server aggregates data from:

- **Yahoo Finance** (`yahoo-finance2` npm package)
  - Stock quotes, history, options, fundamentals
  - Real-time and historical data
  - Earnings, analyst ratings

- **CoinGecko API** (free tier)
  - Cryptocurrency prices
  - Market cap data
  - DeFi and NFT data

- **CNBC** (via `cnbc-integration.js`)
  - Pre-market movers
  - Market sentiment
  - Breaking news

- **Alternative.me**
  - Fear & Greed Index

- **Technical Indicators** (local calculation)
  - Uses `technicalindicators` npm package
  - RSI, MACD, Bollinger Bands, SMA, EMA
  - Calculated on historical data

---

## ⚡ **Streaming Capabilities**

The server supports **real-time streaming** via:

### **WebSocket Streaming:**
- Stock prices (2-second updates)
- Crypto prices (3-second updates)
- Market news (10-second polling)
- Price alerts (5-second monitoring)

### **SSE (Server-Sent Events):**
- Used by Agent Builder for MCP protocol
- Bidirectional communication
- Tool invocation and responses

### **HTTP:**
- REST-style endpoints
- `StreamableHTTPServerTransport` for MCP over HTTP
- Rate limiting and caching

---

## 🔒 **Performance & Reliability**

### **Caching:**
- NodeCache with 60-second TTL
- Prevents API rate limiting
- Improves response times

### **Rate Limiting:**
- Max 5 concurrent requests (`p-limit`)
- Prevents API abuse
- Graceful degradation

### **Error Handling:**
- Automatic retry logic
- Fallback responses
- Detailed error messages

### **Duration Limits:**
- Streaming max 5 minutes (300 seconds)
- Prevents runaway processes
- Automatic cleanup

---

## 📦 **Dependencies**

```json
{
  "@modelcontextprotocol/sdk": "^1.20.1",
  "axios": "^1.6.7",
  "cheerio": "^1.0.0-rc.12",
  "date-fns": "^3.3.1",
  "dotenv": "^16.4.5",
  "eventsource": "^2.0.2",
  "express": "^4.21.2",
  "express-rate-limit": "^7.1.5",
  "node-cache": "^5.1.2",
  "p-limit": "^5.0.0",
  "technicalindicators": "^3.1.0",
  "ws": "^8.16.0",
  "yahoo-finance2": "^2.11.0"
}
```

---

## 🚀 **Deployment**

**Fly.io App**: `gvses-mcp-sse-server`
**URL**: `https://gvses-mcp-sse-server.fly.dev/sse`
**Status**: ✅ Running and healthy
**Connected**: Agent Builder actively using it

---

## 📝 **Next Steps**

1. ✅ **Confirmed**: MCP server exists and is running
2. ✅ **Confirmed**: Has SSE and HTTP support
3. ✅ **Discovered**: Already has 6 chart control tools (but not implemented)
4. ⏳ **TODO**: Either:
   - **Option A**: Add new `chart_control` tool that forwards to backend (30 min)
   - **Option B**: Update 6 existing chart tools to call backend (2 hours)

**Recommended**: Option A - cleaner, faster, and provides comprehensive chart control through our already-working backend orchestrator.

---

**Last Updated**: November 3, 2025  
**Status**: Investigation Complete - Ready to Implement

