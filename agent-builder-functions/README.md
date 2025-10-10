# G'sves Direct API MCP Server

Lightweight, high-performance MCP server for Agent Builder providing direct access to Alpaca Markets and Yahoo Finance APIs.

## Performance

- **Real-time quotes**: < 400ms
- **Historical data**: < 1s
- **News**: < 700ms
- **Multiple quotes**: < 1s

**vs. market-mcp-server**: 10-15x faster for simple queries

## Tools Provided

### 1. get_realtime_quote
Get current stock quote from Alpaca Markets.

```json
{
  "symbol": "AAPL"
}
```

**Returns**:
```json
{
  "symbol": "AAPL",
  "price": 175.50,
  "bid": 175.48,
  "ask": 175.52,
  "timestamp": "2025-10-06T20:00:00Z",
  "source": "alpaca",
  "latency_ms": "385"
}
```

### 2. get_historical_bars
Get OHLCV bars for technical analysis.

```json
{
  "symbol": "TSLA",
  "days": 100,
  "timeframe": "1Day"
}
```

**Use for**: Calculating LTB/ST/QE levels, moving averages, Fibonacci retracements

### 3. get_multiple_quotes
Efficient batch quotes for watchlists.

```json
{
  "symbols": ["SPY", "QQQ", "DIA", "IWM"]
}
```

**Use for**: Market overview, index checks, watchlist monitoring

### 4. get_market_news
Latest news from Alpaca aggregated sources.

```json
{
  "symbol": "NVDA",
  "limit": 10
}
```

**Use for**: Catalyst identification, market sentiment

### 5. get_yahoo_quote_fallback
Fallback for Alpaca failures, crypto, international markets.

```json
{
  "symbol": "BTC-USD"
}
```

## Installation

```bash
cd agent-builder-functions
npm install
```

## Running Locally

```bash
npm start
```

## Testing

```bash
# Test real-time quote
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_realtime_quote","arguments":{"symbol":"AAPL"}}}' | node index.js

# Test historical bars
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_historical_bars","arguments":{"symbol":"TSLA","days":100}}}' | node index.js
```

## Agent Builder Configuration

### Local Development (stdio)
```json
{
  "mcpServers": {
    "gvses-direct-api": {
      "command": "node",
      "args": ["/Volumes/WD My Passport 264F Media/claude-voice-mcp/agent-builder-functions/index.js"],
      "env": {
        "ALPACA_API_KEY": "your_key",
        "ALPACA_SECRET_KEY": "your_secret"
      }
    }
  }
}
```

### Production (HTTP - if deployed to Fly.io)
```json
{
  "mcpServers": {
    "gvses-direct-api": {
      "url": "https://gvses-mcp.fly.dev",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      }
    }
  }
}
```

## When to Use This vs. market-mcp-server

### Use Direct API MCP (this server) for:
- ✅ Real-time price lookups (< 500ms required)
- ✅ Historical data for technical analysis
- ✅ Market news and catalysts
- ✅ Quick entry/exit price checks
- ✅ Watchlist monitoring

### Use market-mcp-server for:
- ✅ Technical indicator calculations (RSI, MACD, etc.)
- ✅ Chart pattern detection
- ✅ Support/resistance levels (for LTB/ST/QE)
- ✅ CNBC sentiment analysis
- ✅ Streaming data
- ✅ Options chain with Greeks

## Environment Variables

Create a `.env` file or use the backend `.env`:

```bash
ALPACA_API_KEY=PKM2U9W8XB8D0EUP1Q38
ALPACA_SECRET_KEY=HdSPzEKEvMEcgUqKcNModn1nXaTCyDOK4Mr5mW3t
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

## Architecture

```
Agent Builder Workflow
    ↓
If/else (Route by query type)
    ↓
┌────────────────────────────┐
│  TIER 1: Direct API MCP    │ ← THIS SERVER (fast quotes, news)
│  (gvses-direct-api)        │
└────────────────────────────┘
    ↓
┌────────────────────────────┐
│  TIER 2: Analysis MCP      │ ← market-mcp-server (indicators, patterns)
│  (market-mcp-server)       │
└────────────────────────────┘
    ↓
┌────────────────────────────┐
│  TIER 3: Knowledge RAG     │ ← Vector store (education, methodology)
│  (File Search)             │
└────────────────────────────┘
    ↓
Gvses Agent (synthesizes results)
    ↓
End (return to user)
```

## Next Steps

1. ✅ Install dependencies: `npm install`
2. ✅ Test locally: `npm start`
3. ⏳ Configure in Agent Builder MCP node
4. ⏳ Test workflow with real queries
5. ⏳ Deploy to Fly.io (optional, for production)

## Deployment to Fly.io (Optional)

```bash
# In agent-builder-functions/
flyctl launch --name gvses-direct-api-mcp
flyctl secrets set ALPACA_API_KEY=your_key ALPACA_SECRET_KEY=your_secret
flyctl deploy
```

Then update Agent Builder to use HTTP endpoint instead of stdio.

---

**Created for**: G'sves Agent Builder workflow
**Performance**: Optimized for < 500ms real-time trading decisions
**Data Sources**: Alpaca Markets (primary), Yahoo Finance (fallback)
