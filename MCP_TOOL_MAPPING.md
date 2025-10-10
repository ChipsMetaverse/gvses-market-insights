# G'sves Agent → market-mcp-server Tool Mapping

This document shows how the G'sves agent's 12 backend tools map to your existing `market-mcp-server` MCP tools.

## ✅ Complete Mapping Summary

All 12 G'sves agent tools can be mapped to existing market-mcp-server tools with no new server needed!

---

## Tool Mappings

### 1. get_stock_price → `get_stock_quote`
**Backend Tool**: `get_stock_price(symbol: str)`
**MCP Tool**: `get_stock_quote`
**Mapping**: ✅ Direct 1:1 mapping
**Parameters**:
```json
{
  "symbol": "AAPL",
  "includePrePost": true
}
```
**Notes**: MCP tool includes pre/post market data which aligns perfectly with G'sves requirements

---

### 2. get_company_info → `get_stock_fundamentals`
**Backend Tool**: `get_company_info(symbol: str)`
**MCP Tool**: `get_stock_fundamentals`
**Mapping**: ✅ Direct 1:1 mapping
**Parameters**:
```json
{
  "symbol": "AAPL"
}
```
**Notes**: Provides company profile, financials, and fundamental data

---

### 3. get_stock_news → `get_market_news`
**Backend Tool**: `get_stock_news(symbol: str)`
**MCP Tool**: `get_market_news`
**Mapping**: ✅ Direct 1:1 mapping
**Parameters**:
```json
{
  "query": "AAPL",
  "limit": 10
}
```
**Notes**: Returns news for specific symbols. Can also use `get_cnbc_movers` for enhanced CNBC data

---

### 4. get_market_overview → `get_market_overview`
**Backend Tool**: `get_market_overview()`
**MCP Tool**: `get_market_overview`
**Mapping**: ✅ Exact match
**Parameters**: None required
**Notes**: Returns major indices (S&P 500, Nasdaq, Dow Jones, Russell 2000)

---

### 5. get_stock_history → `get_stock_history`
**Backend Tool**: `get_stock_history(symbol: str, days: int)`
**MCP Tool**: `get_stock_history`
**Mapping**: ✅ Direct 1:1 mapping
**Parameters**:
```json
{
  "symbol": "AAPL",
  "period": "1mo",
  "interval": "1d"
}
```
**Notes**: MCP tool offers more granular control with period/interval parameters

---

### 6. analyze_chart_image → `get_technical_indicators` + `get_chart_patterns`
**Backend Tool**: `analyze_chart_image(image_url: str)`
**MCP Tools**:
- `get_technical_indicators` - Calculate RSI, MACD, Bollinger Bands, etc.
- `get_chart_patterns` - Detect head & shoulders, triangles, flags, etc.
**Mapping**: ✅ Composite mapping (2 tools replace 1)
**Parameters**:
```json
// Technical Indicators
{
  "symbol": "AAPL",
  "indicators": ["RSI", "MACD", "BollingerBands", "MovingAverage"],
  "period": "1mo",
  "interval": "1d"
}

// Chart Patterns
{
  "symbol": "AAPL",
  "period": "3mo",
  "timeframe": "daily"
}
```
**Notes**: G'sves agent should call both tools sequentially for comprehensive technical analysis

---

### 7. get_comprehensive_stock_data → Multiple MCP Tools (Composite)
**Backend Tool**: `get_comprehensive_stock_data(symbol: str)`
**MCP Tools**: Call these sequentially:
1. `get_stock_quote` - Real-time price
2. `get_stock_fundamentals` - Company data
3. `get_market_news` - Recent news
4. `get_technical_indicators` - Technical analysis
**Mapping**: ✅ Composite (4-tool sequence)
**Notes**: Agent Builder workflow can chain these with proper data flow

---

### 8. get_options_strategies → `get_options_chain`
**Backend Tool**: `get_options_strategies(symbol: str)`
**MCP Tool**: `get_options_chain`
**Mapping**: ✅ Direct 1:1 mapping
**Parameters**:
```json
{
  "symbol": "AAPL",
  "expiration": "2025-10-17"  // Optional: specific expiration date
}
```
**Notes**: Returns calls, puts, strike prices, Greeks, IV, open interest

---

### 9. analyze_options_greeks → `get_options_chain`
**Backend Tool**: `analyze_options_greeks(symbol: str, option_type: str, strike: float)`
**MCP Tool**: `get_options_chain`
**Mapping**: ✅ Same as #8 (filter client-side)
**Parameters**:
```json
{
  "symbol": "AAPL",
  "expiration": "2025-10-17"
}
```
**Notes**: The options chain includes Greeks (delta, gamma, theta, vega). G'sves agent can parse and filter by strike price in the workflow logic

---

### 10. generate_daily_watchlist → `get_market_movers` + `get_market_news`
**Backend Tool**: `generate_daily_watchlist()`
**MCP Tools**:
1. `get_market_movers` - Biggest gainers/losers
2. `get_market_news` - Stocks with news catalysts
3. `get_earnings_calendar` - Upcoming earnings (bonus)
**Mapping**: ✅ Composite (2-3 tools)
**Parameters**:
```json
// Market Movers
{
  "type": "gainers",  // or "losers", "actives"
  "count": 10
}

// Market News (for catalysts)
{
  "limit": 20
}

// Earnings Calendar (optional)
{
  "days": 7
}
```
**Notes**: Combine results to create comprehensive watchlist with technical setups + news catalysts

---

### 11. weekly_trade_review → `track_portfolio`
**Backend Tool**: `weekly_trade_review()`
**MCP Tool**: `track_portfolio`
**Mapping**: ✅ Direct mapping
**Parameters**:
```json
{
  "positions": [
    {"symbol": "AAPL", "quantity": 100, "entryPrice": 175.50},
    {"symbol": "TSLA", "quantity": 50, "entryPrice": 245.00}
  ],
  "metrics": ["total_return", "sharpe_ratio", "max_drawdown"]
}
```
**Notes**: Tracks positions and calculates performance metrics

---

### 12. detect_chart_patterns → `get_chart_patterns`
**Backend Tool**: `detect_chart_patterns(symbol: str)`
**MCP Tool**: `get_chart_patterns`
**Mapping**: ✅ Exact match
**Parameters**:
```json
{
  "symbol": "AAPL",
  "period": "3mo",
  "timeframe": "daily"
}
```
**Notes**: Detects classic patterns (head & shoulders, triangles, flags, double tops/bottoms)

---

## Additional Valuable MCP Tools for G'sves

Your market-mcp-server has additional tools that G'sves can leverage:

### Analyst Insights
- `get_analyst_ratings` - Get analyst price targets and recommendations
- `get_insider_trading` - Track insider buys/sells (bullish/bearish signal)

### Risk Management
- `get_support_resistance` - Calculate key support/resistance levels (perfect for LTB/ST/QE!)
- `calculate_correlation` - Portfolio correlation analysis

### Market Context
- `get_sector_performance` - Sector rotation analysis
- `get_fear_greed_index` - Market sentiment gauge
- `get_economic_calendar` - Macroeconomic events (Fed meetings, GDP, etc.)

### Advanced Features
- `set_price_alert` - Real-time price alerts for swing trade entries
- `stream_stock_prices` - Real-time streaming data
- `get_cnbc_sentiment` - CNBC market sentiment analysis

---

## Recommended Workflow in Agent Builder

### Simple Flow (Start + Agent + MCP)
```
Start
  ↓
Gvses Agent (Instructions loaded)
  ↓ (calls tools as needed)
MCP Node (market-mcp-server connection)
  ↓
End (return response to user)
```

### Enhanced Flow (With Routing Logic)
```
Start (user input)
  ↓
If/else (Classify query type)
  ├─ "General Info"
  │    ↓
  │  Gvses Agent → get_stock_fundamentals (MCP)
  │    ↓
  │  End
  │
  ├─ "Technical Analysis"
  │    ↓
  │  Gvses Agent → get_technical_indicators (MCP)
  │    ↓
  │  Gvses Agent → get_chart_patterns (MCP)
  │    ↓
  │  Gvses Agent → get_support_resistance (MCP)
  │    ↓
  │  End
  │
  ├─ "Options Trade Setup"
  │    ↓
  │  Gvses Agent → get_options_chain (MCP)
  │    ↓
  │  Gvses Agent (analyze Greeks, suggest strategy)
  │    ↓
  │  Human Approval Node (confirm trade recommendation)
  │    ↓
  │  End
  │
  └─ "Market Brief"
       ↓
     Gvses Agent → get_market_overview (MCP)
       ↓
     Gvses Agent → get_market_movers (MCP)
       ↓
     Gvses Agent → get_market_news (MCP)
       ↓
     End
```

---

## Implementation Checklist

### Phase 2: MCP Configuration (Current)
- [✅] Verify all 12 G'sves tools can map to existing MCP tools
- [ ] Configure MCP node in Agent Builder
- [ ] Connect to market-mcp-server (localhost or Fly.io URL)
- [ ] Test individual MCP tool calls from workflow

### Phase 3: Workflow Design
- [ ] Create If/else routing logic (optional but recommended)
- [ ] Configure Transform nodes if needed for data reshaping
- [ ] Set up Human Approval for trade recommendations (compliance)

### Phase 4: Voice Integration
- [ ] Install OpenAI Agents SDK in backend: `pip install openai-agents-sdk`
- [ ] Create `backend/services/agent_builder_client.py`
- [ ] Update voice pipeline to call Agent Builder workflow
- [ ] Test STT → Workflow → TTS flow

### Phase 5: Testing & Deployment
- [ ] Test workflow in Agent Builder Preview mode
- [ ] Publish workflow and get workflow ID
- [ ] Set `GVSES_WORKFLOW_ID` environment variable
- [ ] End-to-end voice test with real market queries
- [ ] Use "Evaluate" tab for trace analysis and optimization

---

## Next Steps

1. **Copy `AGENT_BUILDER_INSTRUCTIONS.md` content** into your Agent Builder "Gvses" Agent node Instructions field

2. **Add MCP Node** to workflow and connect to market-mcp-server:
   - Click "Add Node" → "MCP"
   - Configure server connection (local: stdio, or remote: HTTP)
   - Select tools to enable for the agent

3. **Test a simple query** like "What's AAPL trading at?" to verify MCP connection

4. **Iterate on workflow design** based on testing results

---

## MCP Server Connection Details

### Local Development
```json
{
  "type": "stdio",
  "command": "node",
  "args": ["/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server/index.js"]
}
```

### Production (if deployed to Fly.io)
```json
{
  "type": "http",
  "url": "https://your-mcp-server.fly.dev"
}
```

---

## Summary

✅ **All 12 G'sves tools mapped successfully**
✅ **No new MCP server needed**
✅ **Bonus tools available** (analyst ratings, support/resistance, sentiment)
✅ **Ready for Agent Builder integration**

Your existing market-mcp-server is perfectly suited for G'sves trading workflows!
