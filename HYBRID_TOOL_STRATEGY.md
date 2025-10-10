# G'sves Agent Builder: Hybrid Tool Strategy

## Overview

Your G'sves Agent Builder workflow will use a **3-tier hybrid architecture** combining:

1. **Direct API Calls** (Function calling) - For real-time market data (Alpaca, Yahoo Finance)
2. **MCP Tools** (market-mcp-server) - For comprehensive market analysis and streaming
3. **File Search / RAG** - For trading knowledge base and educational content

This approach optimizes for **performance, reliability, and capabilities**.

---

## Tier 1: Direct API Calls (Function Calling)

### Best For
- Real-time quote data (< 500ms latency required)
- High-frequency calls where MCP overhead is undesirable
- Critical trading operations requiring guaranteed uptime

### Recommended Tools via Function Calling

#### 1. Alpaca Markets API (Primary Data Source)
```python
# Function: get_alpaca_quote
async def get_alpaca_quote(symbol: str):
    """Get real-time quote from Alpaca Markets (< 400ms)"""
    headers = {
        "APCA-API-KEY-ID": os.getenv("ALPACA_API_KEY"),
        "APCA-API-SECRET-KEY": os.getenv("ALPACA_SECRET_KEY")
    }
    url = f"https://data.alpaca.markets/v2/stocks/{symbol}/quotes/latest"
    response = await httpx.get(url, headers=headers)
    return response.json()
```

**Endpoints**:
- Latest quote: `GET /v2/stocks/{symbol}/quotes/latest`
- Historical bars: `GET /v2/stocks/{symbol}/bars`
- News: `GET /v1beta1/news`

**Advantages**:
- Professional-grade data (used by hedge funds)
- Sub-second latency (300-400ms)
- No MCP subprocess overhead
- Real-time accuracy

#### 2. Yahoo Finance Direct (Fallback)
```python
# Function: get_yahoo_quote_fallback
async def get_yahoo_quote_fallback(symbol: str):
    """Fallback to Yahoo Finance if Alpaca fails"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = await httpx.get(url)
    return response.json()
```

**Use Cases**:
- When Alpaca API is down
- For crypto prices (Alpaca doesn't have)
- International markets

### Implementation in Agent Builder

**Option A: Deploy Functions as Custom MCP Server** (Recommended)
```javascript
// Create lightweight HTTP MCP server wrapping your Python functions
// Deploy to Fly.io alongside backend
// Agent Builder connects via MCP HTTP endpoint
```

**Option B: Inline Function Tools** (If supported)
- Define functions directly in Agent Builder workflow
- May require TypeScript/JavaScript implementation

---

## Tier 2: MCP Tools (market-mcp-server)

### Best For
- Comprehensive analysis requiring multiple data sources
- Streaming data (real-time price feeds)
- Complex calculations (technical indicators, pattern detection)
- CNBC news integration

### Recommended MCP Tools from market-mcp-server

#### High-Priority MCP Tools
1. **`get_technical_indicators`** - RSI, MACD, Bollinger Bands (requires historical data + calculation)
2. **`get_chart_patterns`** - Head & shoulders, triangles, flags (pattern recognition logic)
3. **`get_support_resistance`** - Calculate LTB/ST/QE levels! (Perfect for G'sves)
4. **`get_cnbc_sentiment`** - CNBC market sentiment (unique data source)
5. **`get_market_movers`** - Biggest gainers/losers (screener logic)
6. **`get_analyst_ratings`** - Price targets and recommendations (aggregated data)
7. **`stream_stock_prices`** - Real-time streaming (for active monitoring)

#### Medium-Priority MCP Tools
8. **`get_options_chain`** - Options data with Greeks
9. **`get_earnings_calendar`** - Upcoming earnings
10. **`calculate_correlation`** - Portfolio correlation analysis

### Why Use MCP for These?
- **Complex Logic**: Pattern detection and technical indicators require computation beyond simple API calls
- **Multiple Data Sources**: CNBC + Yahoo + technical analysis in one call
- **Streaming**: WebSocket streaming built into MCP server
- **Already Built**: Your market-mcp-server has 30+ tools ready to use

---

## Tier 3: File Search / RAG (Vector Store)

### Best For
- Educational responses (e.g., "What is implied volatility?")
- Trading strategy explanations
- Historical context and market wisdom
- Guardrails and compliance knowledge

### Recommended Vector Store Content

#### 1. Trading Education Knowledge Base
Upload these documents to OpenAI vector store:

**Technical Analysis**
- `technical_analysis_for_dummies_2nd_edition.json` (already exists in your backend!)
- Moving averages explained
- Fibonacci retracement strategies
- RSI and momentum indicators
- Chart pattern recognition guide

**Options Trading**
- Options Greeks explained (delta, gamma, theta, vega)
- Common option strategies (covered calls, spreads, straddles)
- IV rank vs IV percentile
- Risk management for options

**Market Psychology**
- Trading psychology and discipline
- Risk management principles
- Position sizing formulas
- Stop loss strategies

**G'sves Methodology**
- LTB/ST/QE level system documentation
- Entry and exit criteria
- Risk/reward calculation methods
- Swing trading best practices

#### 2. Compliance & Guardrails Documents
- Disclaimers and legal language
- What constitutes "financial advice" (to avoid it)
- Risk disclosure templates
- Educational vs advisory tone guidelines

#### 3. Market Context
- Recent major market events
- Sector analysis reports
- Economic indicator meanings (GDP, CPI, NFP, etc.)

### Vector Store Setup
```python
# 1. Create vector store in OpenAI platform
from openai import OpenAI
client = OpenAI()

vector_store = client.vector_stores.create(
    name="gvses-trading-knowledge",
    description="Trading education and G'sves methodology"
)

# 2. Upload files
file_streams = [
    open("technical_analysis_for_dummies.pdf", "rb"),
    open("gvses_methodology.md", "rb"),
    open("options_greeks_guide.pdf", "rb"),
    # ... more files
]

client.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id,
    files=file_streams
)

# 3. Get vector store ID for Agent Builder
print(f"Vector Store ID: {vector_store.id}")
```

### File Search Node Configuration in Agent Builder
```json
{
  "vector_store_id": "vs_abc123...",
  "query": "{{user_message}}",  // Dynamic from workflow
  "max_results": 5,
  "relevance_threshold": 0.7
}
```

---

## Optimal Tool Selection Strategy

### Decision Tree for G'sves Agent

```
User Query Arrives
    ↓
If/else Node: Classify Query Type
    ↓
    ├─ "Real-time Price Query" (e.g., "What's AAPL at?")
    │    ↓
    │  [TIER 1] Direct API Call: get_alpaca_quote()
    │    ↓
    │  Return price immediately (< 500ms total)
    │
    ├─ "Technical Analysis" (e.g., "Show me TSLA's RSI")
    │    ↓
    │  [TIER 1] Direct API: get_alpaca_bars() for historical data
    │    ↓
    │  [TIER 2] MCP Tool: get_technical_indicators()
    │    ↓
    │  [TIER 2] MCP Tool: get_support_resistance() for LTB/ST/QE
    │    ↓
    │  Gvses Agent analyzes and formats response
    │
    ├─ "Educational Query" (e.g., "What is a covered call?")
    │    ↓
    │  [TIER 3] File Search RAG: Query vector store
    │    ↓
    │  Gvses Agent provides educational explanation
    │    ↓
    │  NO market data calls (avoid unnecessary API usage)
    │
    ├─ "Market Brief" (e.g., "Good morning")
    │    ↓
    │  [TIER 1] Direct API: get_alpaca_quote() for indices
    │    ↓
    │  [TIER 2] MCP Tool: get_market_movers()
    │    ↓
    │  [TIER 2] MCP Tool: get_cnbc_sentiment()
    │    ↓
    │  [TIER 1] Direct API: Alpaca news endpoint
    │    ↓
    │  Gvses Agent compiles comprehensive brief
    │
    ├─ "Options Trade Setup" (e.g., "NVDA call options this week")
    │    ↓
    │  [TIER 1] Direct API: get_alpaca_quote() for current price
    │    ↓
    │  [TIER 2] MCP Tool: get_options_chain()
    │    ↓
    │  [TIER 2] MCP Tool: get_technical_indicators()
    │    ↓
    │  Gvses Agent analyzes Greeks and suggests strategy
    │    ↓
    │  Human Approval Node (compliance check)
    │
    └─ "Watchlist Request" (e.g., "What should I watch today?")
         ↓
       [TIER 2] MCP Tool: get_market_movers()
         ↓
       [TIER 1] Direct API: Alpaca news for catalysts
         ↓
       [TIER 2] MCP Tool: get_earnings_calendar()
         ↓
       Gvses Agent combines and ranks by opportunity
```

---

## Performance Comparison

| Data Source | Latency | Use Case | Cost |
|-------------|---------|----------|------|
| **Alpaca Direct API** | 300-400ms | Real-time quotes, history | Free (paper trading) |
| **Yahoo Direct API** | 400-700ms | Fallback, crypto, international | Free |
| **market-mcp-server** | 3-15s | Complex analysis, patterns | Free (self-hosted) |
| **File Search RAG** | 1-2s | Educational queries | $0.10/GB/day storage |

### Hybrid Performance Benefits
- **Real-time quotes**: 300ms (vs 3-15s MCP-only)
- **Technical analysis**: 2-4s (Alpaca data + MCP calculations)
- **Educational**: 1-2s (RAG retrieval)
- **Market brief**: 5-8s (parallel API + MCP calls)

---

## Implementation Plan

### Phase 2A: Create Direct API Functions

**Create `/Volumes/WD My Passport 264F Media/claude-voice-mcp/agent-builder-functions/`**

```bash
mkdir -p agent-builder-functions
cd agent-builder-functions
npm init -y
npm install @modelcontextprotocol/sdk axios dotenv
```

**File: `alpaca-functions.js`**
```javascript
import axios from 'axios';

export async function getAlpacaQuote(symbol) {
  const response = await axios.get(
    `https://data.alpaca.markets/v2/stocks/${symbol}/quotes/latest`,
    {
      headers: {
        'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY
      }
    }
  );
  return response.data;
}

export async function getAlpacaBars(symbol, start, end, timeframe = '1Day') {
  const response = await axios.get(
    `https://data.alpaca.markets/v2/stocks/${symbol}/bars`,
    {
      params: { start, end, timeframe },
      headers: {
        'APCA-API-KEY-ID': process.env.ALPACA_API_KEY,
        'APCA-API-SECRET-KEY': process.env.ALPACA_SECRET_KEY
      }
    }
  );
  return response.data;
}

// Export as MCP tools
export const tools = [
  {
    name: 'get_alpaca_quote',
    description: 'Get real-time stock quote from Alpaca (< 400ms)',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: { type: 'string', description: 'Stock symbol (e.g., AAPL)' }
      },
      required: ['symbol']
    },
    handler: getAlpacaQuote
  },
  {
    name: 'get_alpaca_bars',
    description: 'Get historical price bars from Alpaca',
    inputSchema: {
      type: 'object',
      properties: {
        symbol: { type: 'string' },
        start: { type: 'string', description: 'ISO 8601 date (e.g., 2025-09-01)' },
        end: { type: 'string', description: 'ISO 8601 date' },
        timeframe: { type: 'string', enum: ['1Min', '5Min', '1Hour', '1Day'], default: '1Day' }
      },
      required: ['symbol', 'start', 'end']
    },
    handler: getAlpacaBars
  }
];
```

### Phase 2B: Setup Vector Store for RAG

```python
# Script: setup_vector_store.py
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create vector store
vector_store = client.vector_stores.create(
    name="gvses-trading-knowledge",
    description="G'sves trading education and methodology"
)

# Upload knowledge base files
files_to_upload = [
    "backend/training/json_docs/technical_analysis_for_dummies_2nd_edition.json",
    "AGENT_BUILDER_INSTRUCTIONS.md",  # G'sves methodology
    # Add more educational content
]

for file_path in files_to_upload:
    with open(file_path, "rb") as f:
        client.vector_stores.files.create(
            vector_store_id=vector_store.id,
            file=f
        )

print(f"✅ Vector Store Created: {vector_store.id}")
print("Copy this ID to Agent Builder File Search node")
```

### Phase 2C: MCP Tool Selection

**Tools to Enable in Agent Builder MCP Node**:
1. ✅ `get_support_resistance` - For LTB/ST/QE levels
2. ✅ `get_technical_indicators` - RSI, MACD, etc.
3. ✅ `get_chart_patterns` - Pattern detection
4. ✅ `get_market_movers` - Screener functionality
5. ✅ `get_cnbc_sentiment` - Unique sentiment data
6. ✅ `get_analyst_ratings` - Price targets
7. ✅ `get_options_chain` - Options data with Greeks

---

## Agent Builder Workflow Configuration

### Nodes to Add

1. **Start Node** (existing)
   - User input

2. **If/else Node** (NEW)
   - Classify query type using CEL expressions
   - Route to appropriate tool tier

3. **Gvses Agent Node** (existing, enhanced)
   - Instructions loaded from `AGENT_BUILDER_INSTRUCTIONS.md`
   - Model: `gpt-5-mini`
   - Tools: All three tiers available

4. **MCP Node** (NEW)
   - Server: market-mcp-server
   - Tools: 7 selected tools above

5. **File Search Node** (NEW)
   - Vector store ID: (from setup script)
   - Query: Dynamic from workflow variable

6. **Transform Node** (optional)
   - Reshape MCP outputs for consistency

7. **Human Approval Node** (for trade recommendations)
   - Compliance safeguard

8. **End Node** (existing)
   - Return final response

---

## Next Actions

1. ✅ **Phase 1 Complete**: G'sves instructions prepared (`AGENT_BUILDER_INSTRUCTIONS.md`)

2. **Phase 2 In Progress**: Hybrid tool strategy designed
   - [ ] Create `agent-builder-functions/` directory
   - [ ] Implement Alpaca direct API functions
   - [ ] Run vector store setup script
   - [ ] Document vector store ID

3. **Phase 3**: Configure Agent Builder workflow
   - [ ] Add If/else routing node
   - [ ] Connect MCP node to market-mcp-server
   - [ ] Add File Search node with vector store ID
   - [ ] Configure tool availability in Gvses Agent

4. **Phase 4**: Voice integration
   - [ ] Install OpenAI Agents SDK
   - [ ] Create workflow client in backend
   - [ ] Test STT → Workflow → TTS pipeline

---

## Summary

Your G'sves Agent Builder workflow will leverage:

- **⚡ Speed**: Direct Alpaca API calls for real-time data (< 500ms)
- **🧠 Intelligence**: MCP tools for complex analysis and unique data sources
- **📚 Knowledge**: RAG vector store for educational content and methodology

This 3-tier hybrid approach delivers the best of all worlds: **fast, smart, and knowledgeable** market analysis through a natural voice interface.
