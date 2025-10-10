# Complete Architecture Wiring Diagram

**Created**: October 7, 2025
**Updated**: October 7, 2025
**Purpose**: Comprehensive visualization of current and target architecture
**Status**: Complete system integration map
**Audience**: Technical and non-technical readers

---

## 📚 Related Documentation

- **For Non-Technical Readers**: See `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md` for step-by-step UI-based instructions
- **For Developers**: See `MCP_NODE_MIGRATION_GUIDE.md` for code implementation details
- **For Agent Builder Details**: See `AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md` for workflow patterns
- **For Knowledge Base**: See `AGENT_BUILDER_MCP_CURRENT_KNOWLEDGE.md` for complete feature reference

---

## 🎯 Current Architecture (Production - As-Is)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │  React Frontend │
                              │  (Port 5174)    │
                              │                 │
                              │  Components:    │
                              │  - Dashboard    │
                              │  - TradingChart │
                              │  - Voice UI     │
                              └────────┬────────┘
                                       │
                                       │ HTTP/WebSocket
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND API LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────────┐
                         │   FastAPI Server     │
                         │   (Port 8000)        │
                         │                      │
                         │   mcp_server.py      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
        │ Market Service  │ │  ElevenLabs │ │ Agent           │
        │ Wrapper         │ │  Proxy      │ │ Orchestrator    │
        │                 │ │             │ │                 │
        │ - Alpaca First  │ │ - Signed    │ │ - Responses API │
        │ - MCP Fallback  │ │   URLs      │ │ - G'sves Asst   │
        └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
                 │                 │                  │
                 │                 │                  │
┌────────────────┼─────────────────┼──────────────────┼─────────────────────┐
│                │                 │                  │                      │
│  DATA SOURCES  │   VOICE AI      │    OPENAI API    │                      │
└────────────────┼─────────────────┼──────────────────┼─────────────────────┘
                 │                 │                  │
      ┌──────────┴──────────┐      │                  │
      │                     │      │                  │
      ▼                     ▼      ▼                  ▼
┌──────────┐     ┌──────────────────┐      ┌──────────────────┐
│  Alpaca  │     │  market-mcp      │      │  OpenAI          │
│  Markets │     │  (Node.js)       │      │  Responses API   │
│          │     │                  │      │                  │
│  - Quotes│     │  stdio transport │      │  - GPT-4o        │
│  - Bars  │     │  (localhost only)│      │  - Assistant ID  │
│  - News  │     │                  │      │  - Tools         │
└──────────┘     │  35+ Tools:      │      └──────────────────┘
                 │  - Yahoo Finance │
      ▼          │  - CNBC News     │
┌──────────┐     │  - Market Data   │
│  Yahoo   │◄────┤                  │
│  Finance │     └──────────────────┘
└──────────┘              │
                          │
                          ▼
                   ┌──────────────┐
                   │  CNBC API    │
                   └──────────────┘
```

### Current Data Flow:

**1. Stock Quote Request:**
```
User → Frontend → FastAPI (/api/stock-price?symbol=TSLA)
  → MarketServiceWrapper.get_stock_price()
    → TRY Alpaca API (300-400ms) ✅
      → Returns: { price, change, source: "alpaca" }
    → ON ERROR: MCP Fallback (3-15s)
      → market-mcp-server → Yahoo Finance
      → Returns: { price, change, source: "yahoo_mcp" }
```

**2. Voice Conversation:**
```
User → Frontend → WebSocket Connection
  → FastAPI (/elevenlabs/signed-url)
    → ElevenLabs Proxy generates signed WebSocket URL
      → Frontend connects directly to ElevenLabs
        → ElevenLabs Conversational AI
          → Agent responds with voice output
```

**3. Chart Analysis (Text):**
```
User → Frontend → FastAPI (/ask)
  → AgentOrchestrator.process_message()
    → OpenAI Responses API
      → Assistant: asst_FgdYMBvUvKUy0mxX5AF7Lmyg
        → Tools: get_stock_price, get_stock_history, etc.
          → Calls back to MarketServiceWrapper
            → Returns market data
```

---

## 🚀 Target Architecture (Agent Builder Integration - To-Be)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE LAYER                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │  React Frontend │
                              │  (Port 5174)    │
                              │                 │
                              │  Components:    │
                              │  - Dashboard    │
                              │  - TradingChart │
                              │  - Voice UI     │
                              └────────┬────────┘
                                       │
                                       │ HTTP/WebSocket
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKEND API LAYER                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌──────────────────────┐
                         │   FastAPI Server     │
                         │   (Port 8000)        │
                         │                      │
                         │   mcp_server.py      │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
        │ Market Service  │ │  ElevenLabs │ │ Agent Builder    │
        │ (Direct APIs)   │ │  Proxy      │ │ Client           │
        │                 │ │             │ │                  │
        │ - Alpaca        │ │ - Signed    │ │ - Workflow ID    │
        │ - Yahoo (fast)  │ │   URLs      │ │ - Version        │
        └─────────────────┘ └──────┬──────┘ └────────┬─────────┘
                                   │                  │
                                   │                  │
┌──────────────────────────────────┼──────────────────┼─────────────────────┐
│                                  │                  │                      │
│       VOICE AI                   │    OPENAI AGENT BUILDER                 │
└──────────────────────────────────┼──────────────────┼─────────────────────┘
                                   │                  │
                                   ▼                  ▼
                         ┌──────────────────┐  ┌─────────────────────────┐
                         │  ElevenLabs      │  │  Agent Builder Cloud    │
                         │  Conversational  │  │                         │
                         │  AI              │  │  Published Workflow:    │
                         │                  │  │  "G'sves Market Agent"  │
                         │  - Voice Input   │  │                         │
                         │  - Voice Output  │  │  ┌────────────────────┐ │
                         │  - Real-time     │  │  │ Classification     │ │
                         └──────────────────┘  │  │ Agent              │ │
                                              │  └──────┬─────────────┘ │
                                              │         │               │
                                              │  ┌──────┴─────────┐     │
                                              │  │ Condition Node │     │
                                              │  └──────┬─────────┘     │
                                              │         │               │
                                              │  ┌──────┴──────────┐    │
                                              │  │                 │    │
                                              │  ▼                 ▼    │
                                              │ ┌────────┐  ┌─────────┐│
                                              │ │MCP Node│  │G'sves   ││
                                              │ │        │  │Agent    ││
                                              │ │Connected │Node     ││
                                              │ │to:      │  │        ││
                                              │ │        │  │        ││
                                              │ │Market  │  │        ││
                                              │ │Data MCP│  │        ││
                                              │ └────┬───┘  └────────┘│
                                              └──────┼────────────────┘
                                                     │
                                                     │ HTTPS/SSE
                                                     ▼
                                    ┌─────────────────────────────────┐
                                    │  market-mcp-server              │
                                    │  (Fly.io Deployment)            │
                                    │                                 │
                                    │  HTTPS: market-mcp.fly.dev      │
                                    │                                 │
                                    │  HTTP/SSE Transport             │
                                    │                                 │
                                    │  35+ Tools:                     │
                                    │  - get_stock_quote              │
                                    │  - get_stock_history            │
                                    │  - get_stock_news               │
                                    │  - search_stocks                │
                                    │  - get_market_movers            │
                                    │  - get_sector_performance       │
                                    │  - (+ 29 more tools)            │
                                    └────────┬────────────────────────┘
                                             │
                                    ┌────────┴────────┐
                                    │                 │
                                    ▼                 ▼
                              ┌──────────┐     ┌──────────┐
                              │  Yahoo   │     │  CNBC    │
                              │  Finance │     │  API     │
                              └──────────┘     └──────────┘
```

### Target Data Flow:

**1. Voice Market Query (Agent Builder):**
```
User: "What's Tesla's stock price?"
  → ElevenLabs Voice Input
    → Frontend WebSocket → ElevenLabs Conversational AI
      → ElevenLabs → Agent Builder Workflow (Published)
        → Classification Agent: "Market Data Query"
          → Condition: Route to MCP Node
            → MCP Node calls market-mcp-server
              → HTTPS: POST https://market-mcp.fly.dev/messages
                → Tool: get_stock_quote(symbol="TSLA")
                  → Yahoo Finance API
                    → Returns: { symbol, price, change, volume }
              → MCP Response to Agent Builder
            → G'sves Agent Node formats response
              → "Tesla is trading at $245.32, up 2.3%"
        → Agent Builder returns to ElevenLabs
      → ElevenLabs TTS → Voice Output
    → User hears response
```

**2. Chart Command (Direct to Frontend):**
```
User: "Show me Apple chart"
  → Voice → ElevenLabs → Agent Builder
    → Classification Agent: "Chart Command"
      → Condition: Route to G'sves Agent
        → G'sves Agent: Returns chart command
          → Frontend receives: { action: "show_chart", symbol: "AAPL" }
            → TradingChart.tsx updates
              → Fetches data: FastAPI /api/stock-history?symbol=AAPL
                → MarketService → Alpaca API → Returns candlestick data
                  → Chart renders
```

**3. Complex Analysis (Multi-Node Workflow):**
```
User: "Compare Tesla and Apple performance"
  → Voice Input → Agent Builder Workflow
    → Classification Agent: "Comparative Analysis"
      → Parallel MCP Calls:
        ├─ MCP Node → get_stock_quote("TSLA")
        └─ MCP Node → get_stock_quote("AAPL")
      → Transform Node: Combine results
        → G'sves Agent: Generate comparison narrative
          → "Tesla is up 2.3% at $245, while Apple is down 0.5% at $178"
            → Voice response to user
```

---

## 🔌 Integration Wiring Details

### 1. Frontend → Backend Connection

**Current (Unchanged):**
```typescript
// frontend/src/services/marketDataService.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Stock data fetch
export async function getStockPrice(symbol: string) {
  const response = await fetch(`${API_URL}/api/stock-price?symbol=${symbol}`);
  return response.json();
}

// WebSocket for voice
export function connectToElevenLabs() {
  const wsUrl = await fetch(`${API_URL}/elevenlabs/signed-url`).then(r => r.json());
  return new WebSocket(wsUrl.signed_url);
}
```

**Environment:**
```bash
# frontend/.env.development
VITE_API_URL=http://localhost:8000

# frontend/.env.production
VITE_API_URL=https://your-domain.fly.dev
```

---

### 2. Backend → OpenAI Integration

**Option A: Current (Responses API)**
```python
# backend/services/agent_orchestrator.py (lines 4295-4301)

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("ANTHROPIC_API_KEY"))

async def process_message(self, message: str):
    response = await client.responses.create(
        model="gpt-4o",
        assistant_id="asst_FgdYMBvUvKUy0mxX5AF7Lmyg",  # G'sves Assistant
        messages=[{"role": "user", "content": message}],
        tools=self.tools,  # Defined in backend
        store=True
    )
    return response
```

**Tools Defined in Backend:**
```python
# Lines 878-908+
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get real-time stock quote",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"}
                }
            }
        }
    },
    # ... 5+ more tools
]
```

**Option B: Target (Agent Builder)**
```python
# backend/services/agent_builder_client.py (NEW FILE)

from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def call_workflow(self, message: str, conversation_id: str = None):
    """
    Call published Agent Builder workflow
    """
    response = await client.workflows.run(
        workflow_id="wf_abc123xyz",  # Published workflow ID
        version="v1",
        input={
            "user_message": message,
            "conversation_id": conversation_id
        }
    )
    return response.output
```

---

### 3. MCP Server Wiring

**Current (stdio - localhost only):**
```javascript
// market-mcp-server/index.js (line 2)

import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'market-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);

// Accessible only via: subprocess stdio communication
```

**Target (HTTP/SSE - public network):**
```javascript
// market-mcp-server/index.js (UPDATED)

import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';

const app = express();
const server = new Server({
  name: 'market-mcp-server',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {}
  }
});

// SSE endpoint for MCP protocol
app.get('/sse', async (req, res) => {
  const transport = new SSEServerTransport('/messages', res);
  await server.connect(transport);
});

// Message endpoint for client requests
app.post('/messages', async (req, res) => {
  // Handle MCP protocol messages
  await server.handleRequest(req.body, res);
});

app.listen(8080, () => {
  console.log('MCP Server running on port 8080');
});

// Accessible via: https://market-mcp.fly.dev
```

**Fly.io Deployment:**
```toml
# market-mcp-server/fly.toml

app = "market-mcp"

[env]
  PORT = "8080"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

[http_service]
  internal_port = 8080
  force_https = true
```

---

### 4. Agent Builder → MCP Server Connection

**Registration in Agent Builder UI:**

```
Step 1: Open Agent Builder
  → Create new workflow or edit existing

Step 2: Add MCP Node
  → Drag "MCP" from sidebar onto canvas

Step 3: Click "+ Add" in MCP panel
  → Opens "Connect to MCP Server" dialog

Step 4: Fill in connection details:
  ┌─────────────────────────────────────┐
  │ URL: https://market-mcp.fly.dev    │
  │                                     │
  │ Label: Market Data MCP              │
  │                                     │
  │ Description: Real-time market data  │
  │              and analysis tools     │
  │                                     │
  │ Authentication: Access token/API key│
  │ 🔑 [Optional token field]           │
  │                                     │
  │  [Back]           [⚡ Connect]      │
  └─────────────────────────────────────┘

Step 5: Click "Connect"
  → Agent Builder sends: GET https://market-mcp.fly.dev/sse
  → Establishes SSE connection
  → Sends MCP protocol: { method: "tools/list" }
  → Server responds with 35+ tools
  → Tools appear in MCP node dropdown

Step 6: Select tools to use
  → Check: get_stock_quote
  → Check: get_stock_history
  → Check: get_stock_news
  → (Enable 5-10 most important tools)

Step 7: Connect to workflow
  → Connect Classification Agent → Condition → MCP Node
  → MCP Node → G'sves Agent → Output
```

**MCP Protocol Handshake:**
```
Agent Builder                    market-mcp-server
     │                                  │
     │  GET /sse                        │
     ├─────────────────────────────────>│
     │                                  │
     │  SSE: Connected                  │
     │<─────────────────────────────────┤
     │                                  │
     │  POST /messages                  │
     │  { method: "tools/list" }        │
     ├─────────────────────────────────>│
     │                                  │
     │  Response: [                     │
     │    {                             │
     │      name: "get_stock_quote",    │
     │      description: "...",         │
     │      parameters: { ... }         │
     │    },                            │
     │    { ... 34 more tools }         │
     │  ]                               │
     │<─────────────────────────────────┤
     │                                  │
```

**Tool Execution Flow:**
```
Agent Builder Workflow Running
  → User query: "Tesla price"
    → MCP Node executes: get_stock_quote("TSLA")
      → POST /messages
        {
          method: "tools/call",
          params: {
            name: "get_stock_quote",
            arguments: { symbol: "TSLA" }
          }
        }
      → market-mcp-server processes
        → Calls Yahoo Finance API
        → Returns: { symbol: "TSLA", price: 245.32, ... }
      → Response to Agent Builder
        → G'sves Agent formats: "Tesla is at $245.32"
```

---

### 5. ElevenLabs Voice Integration

**Current (Unchanged - Working):**
```python
# backend/routers/elevenlabs_router.py

@router.get("/elevenlabs/signed-url")
async def get_signed_url():
    """Generate signed WebSocket URL for ElevenLabs"""

    agent_id = os.getenv("ELEVENLABS_AGENT_ID")
    api_key = os.getenv("ELEVENLABS_API_KEY")

    # Generate signed URL
    url = f"wss://api.elevenlabs.io/v1/convai/conversation"
    params = {
        "agent_id": agent_id,
        "api_key": api_key
    }

    signed_url = f"{url}?{urlencode(params)}"

    return {"signed_url": signed_url}
```

**Frontend Connection:**
```typescript
// frontend/src/hooks/useAgentVoiceConversation.ts

async function connectVoice() {
  // Get signed URL from backend
  const { signed_url } = await fetch('/elevenlabs/signed-url').then(r => r.json());

  // Connect WebSocket
  const ws = new WebSocket(signed_url);

  ws.onopen = () => {
    console.log('ElevenLabs connected');
    // Send audio stream
  };

  ws.onmessage = (event) => {
    // Receive audio response
    const audioData = JSON.parse(event.data);
    playAudio(audioData);
  };
}
```

**ElevenLabs → Agent Builder Integration:**
```
ElevenLabs Agent Configuration (idealagent.md)
  → Custom Actions → Agent Builder Workflow
    → Webhook URL: https://api.openai.com/v1/workflows/{workflow_id}/run
    → Auth: OpenAI API Key
    → On each user message:
      → POST to Agent Builder
      → Wait for response
      → Convert to voice
```

---

## 📊 Comparison: Before vs After

### Performance Impact

| Operation | Current (Responses API) | Target (Agent Builder) |
|-----------|------------------------|------------------------|
| Voice Query | 1-3s (API + tools) | 1-3s (similar) |
| Tool Discovery | Hardcoded in backend | Auto-discovered from MCP |
| Tool Updates | Code deploy required | MCP server restart only |
| Workflow Changes | Backend code changes | Visual editor (no code) |
| Debugging | Backend logs | Agent Builder visual logs |
| Version Control | Git commits | Workflow versions |

### Data Sources

| Source | Current Usage | Target Usage |
|--------|---------------|--------------|
| Alpaca Markets | Primary (quotes, bars) | Primary (quotes, bars) |
| Yahoo Finance (MCP) | Fallback (3-15s) | Agent Builder MCP (fast) |
| CNBC (MCP) | News only | Agent Builder MCP |
| Direct Yahoo | N/A | Potential future addition |

### Architecture Complexity

**Current:**
- ✅ Simple: FastAPI → Responses API → Tools in backend
- ✅ Fast: Direct Alpaca integration
- ❌ Rigid: Tool changes require deployment
- ❌ Opaque: Hard to visualize logic

**Target:**
- ✅ Flexible: Visual workflow editor
- ✅ Observable: Live debugging in UI
- ✅ Versioned: Rollback capability
- ⚠️ Complex: More moving parts (Agent Builder + MCP server)
- ⚠️ Network: Additional HTTP calls to MCP server

---

## 🔀 Migration Path

### Phase 1: MCP Server Preparation (Est: 2-4 hours)

```bash
# 1. Update market-mcp-server with HTTP/SSE transport
cd market-mcp-server
npm install express @modelcontextprotocol/sdk

# 2. Update index.js (see MCP_NODE_MIGRATION_GUIDE.md)
# 3. Test locally
npm run dev

# 4. Deploy to Fly.io
fly launch --name market-mcp
fly deploy

# 5. Verify deployment
curl https://market-mcp.fly.dev/health
```

### Phase 2: Agent Builder Setup (Est: 1-2 hours)

```
1. Create new workflow in Agent Builder
2. Add Classification Agent node (intent detection)
3. Add Condition node (routing logic)
4. Add MCP node → Connect to https://market-mcp.fly.dev
5. Add G'sves Agent node (response formatting)
6. Connect nodes in logical flow
7. Test with Preview mode
8. Publish workflow → Get workflow ID
```

### Phase 3: Backend Integration (Est: 1-2 hours)

```python
# Create new agent_builder_client.py
# Update frontend to call Agent Builder workflow
# Keep Responses API as fallback
# A/B test both approaches
```

### Phase 4: ElevenLabs Integration (Est: 30 min)

```
Update ElevenLabs agent configuration
→ Point to Agent Builder workflow URL
→ Test voice → Agent Builder → MCP → response
```

---

## 🎯 Recommended Approach

### Option 1: Parallel Architecture (Recommended)

Run BOTH systems simultaneously:

```
Frontend
  │
  ├─ Voice Queries → ElevenLabs → Agent Builder → MCP Server
  │
  └─ Text Queries → FastAPI → Responses API → Direct APIs
```

**Benefits:**
- ✅ Zero downtime migration
- ✅ A/B testing capability
- ✅ Fallback if Agent Builder has issues
- ✅ Keep fast Alpaca integration

**Implementation:**
```python
# backend/mcp_server.py

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Text queries → Responses API (current)"""
    return await agent_orchestrator.process_message(request.question)

@app.post("/ask-builder")
async def ask_via_builder(request: QuestionRequest):
    """New endpoint → Agent Builder workflow"""
    return await agent_builder_client.call_workflow(request.question)
```

### Option 2: Full Migration

Replace Responses API entirely with Agent Builder:

**Benefits:**
- ✅ Single source of truth
- ✅ Simplified architecture
- ✅ Full Agent Builder features

**Risks:**
- ❌ Vendor lock-in to OpenAI platform
- ❌ More network hops (latency)
- ❌ Dependency on Agent Builder availability

---

## 📋 Complete Wiring Checklist

### Backend Environment Variables

```bash
# backend/.env

# OpenAI
OPENAI_API_KEY=sk-...                    # For Agent Builder
ANTHROPIC_API_KEY=sk-ant-...             # Keep for Responses API fallback

# Agent Builder
AGENT_BUILDER_WORKFLOW_ID=wf_abc123xyz   # After publishing workflow
AGENT_BUILDER_VERSION=v1

# ElevenLabs
ELEVENLABS_API_KEY=...
ELEVENLABS_AGENT_ID=...

# Market Data
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Database
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
```

### Frontend Environment Variables

```bash
# frontend/.env.development

VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://...
VITE_SUPABASE_ANON_KEY=...
```

### MCP Server Environment Variables

```bash
# market-mcp-server/.env (Fly.io)

PORT=8080
NODE_ENV=production
YAHOO_FINANCE_API_KEY=...  # If needed
CNBC_API_KEY=...           # If needed
```

---

## 🔍 Testing & Validation

### 1. MCP Server Health Check

```bash
# Test local
curl http://localhost:8080/health

# Test production
curl https://market-mcp.fly.dev/health

# Expected response:
{
  "status": "healthy",
  "server": "market-mcp-server",
  "version": "1.0.0",
  "tools": 35
}
```

### 2. Agent Builder Connection Test

```
Agent Builder UI:
1. MCP Node → Properties → Test Authentication
2. Should show: ✅ Connected successfully
3. Should list: 35 tools available
```

### 3. End-to-End Voice Test

```
User: "What's Tesla's stock price?"
  → Check ElevenLabs console: Voice input received
  → Check Agent Builder logs: Workflow executed
  → Check MCP server logs: get_stock_quote("TSLA") called
  → Verify: Voice response with correct price
```

### 4. Performance Benchmarks

```bash
# Test MCP server response time
time curl -X POST https://market-mcp.fly.dev/messages \
  -H "Content-Type: application/json" \
  -d '{"method":"tools/call","params":{"name":"get_stock_quote","arguments":{"symbol":"TSLA"}}}'

# Target: < 1 second response time
```

---

## 🎉 Success Criteria

### ✅ Phase 1 Complete When:
- [ ] market-mcp-server deployed to Fly.io
- [ ] HTTPS endpoint accessible
- [ ] Health check returns 200 OK
- [ ] SSE connection works
- [ ] All 35 tools listed via MCP protocol

### ✅ Phase 2 Complete When:
- [ ] Agent Builder workflow created
- [ ] MCP server connected and registered
- [ ] Tools auto-discovered
- [ ] Preview mode shows correct tool calls
- [ ] Workflow published with ID

### ✅ Phase 3 Complete When:
- [ ] Backend can call Agent Builder workflow
- [ ] Response format matches expected schema
- [ ] Error handling works
- [ ] Performance within targets (< 3s)

### ✅ Phase 4 Complete When:
- [ ] Voice query → Agent Builder → MCP → Response
- [ ] End-to-end latency < 5 seconds
- [ ] Voice output quality maintained
- [ ] Error cases handled gracefully

---

## 🗺️ Implementation Roadmap

### For Non-Technical Users

**Follow this guide**: `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md`

**4-Phase Implementation:**
1. **Phase 1** (1-2 hours): Deploy MCP Server to Fly.io → Get URL
2. **Phase 2** (1-2 hours): Build Agent Builder Workflow → Visual flowchart
3. **Phase 3** (1 hour): Connect Backend & ElevenLabs → Integration
4. **Phase 4** (30-60 min): Test End-to-End → Validation

**No Coding Required** - All configuration done through web UIs

---

### For Developers

**Follow this sequence**:

**Step 1**: Read this document (COMPLETE_ARCHITECTURE_WIRING.md)
- Understand current vs target architecture
- Review data flow diagrams
- Note integration points

**Step 2**: Implement MCP Server Migration
- Reference: `MCP_NODE_MIGRATION_GUIDE.md`
- Code changes in `market-mcp-server/index.js`
- Deploy to Fly.io
- Test health endpoint

**Step 3**: Support Agent Builder Setup
- Guide non-technical user through `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md`
- Provide Workflow ID after publishing
- Configure backend environment variables

**Step 4**: Backend Integration
- Create `backend/services/agent_builder_client.py`
- Update API endpoints
- Deploy changes
- Monitor logs

**Step 5**: End-to-End Testing
- Follow test cases in `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md` Phase 4
- Performance benchmarking
- Error handling validation

---

## 📊 Documentation Suite Map

```
Project Documentation
│
├─ COMPLETE_ARCHITECTURE_WIRING.md ← YOU ARE HERE
│  └─ Technical system architecture with data flows
│
├─ NON_TECHNICAL_IMPLEMENTATION_GUIDE.md ⭐ NEW
│  └─ Step-by-step UI-based instructions (no coding)
│
├─ MCP_NODE_MIGRATION_GUIDE.md
│  └─ Code-level HTTP/SSE transport implementation
│
├─ AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md
│  └─ Workflow patterns and node configuration
│
├─ AGENT_BUILDER_MCP_CURRENT_KNOWLEDGE.md
│  └─ Complete feature reference (100% coverage)
│
└─ CUSTOM_MCP_SERVER_QUESTIONS.md
   └─ FAQ with 30+ answered questions
```

---

## 🎯 Quick Start Paths

### Path 1: "I Want to Implement This" (Non-Technical)
1. Open `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md`
2. Follow Phase 1-4 sequentially
3. Get developer help for Phase 1 deployment
4. Complete Phases 2-4 yourself in Agent Builder UI

### Path 2: "I Need to Code This" (Developer)
1. Read this document (COMPLETE_ARCHITECTURE_WIRING.md)
2. Reference `MCP_NODE_MIGRATION_GUIDE.md` for code
3. Implement MCP server HTTP/SSE changes
4. Deploy to Fly.io with `fly deploy`
5. Support non-technical user with Agent Builder setup

### Path 3: "I Just Want to Understand" (Stakeholder)
1. Read "What We're Building" in `NON_TECHNICAL_IMPLEMENTATION_GUIDE.md`
2. Review visual diagrams in this document
3. Check "Success Criteria" sections
4. Review performance benchmarks

---

## ✅ Cross-Referenced Checklists

### Phase 1: MCP Server Deployment
**Developer Responsibility**
- [ ] HTTP/SSE transport code implemented (`MCP_NODE_MIGRATION_GUIDE.md`)
- [ ] Server deployed to Fly.io
- [ ] Health endpoint accessible: `https://market-mcp.fly.dev/health`
- [ ] 35 tools respond to MCP protocol queries
- [ ] URL provided to non-technical implementer

### Phase 2: Agent Builder Workflow
**Non-Technical User Responsibility**
- [ ] Workflow created in Agent Builder UI (`NON_TECHNICAL_IMPLEMENTATION_GUIDE.md` Phase 2)
- [ ] Classification Agent configured
- [ ] Condition Node routing logic set
- [ ] MCP Node connected to server URL
- [ ] G'sves Agent personality configured
- [ ] Preview mode tested successfully
- [ ] Workflow published → ID saved

### Phase 3: System Integration
**Team Effort - Developer + Non-Technical**
- [ ] Backend environment variables updated (Developer)
- [ ] ElevenLabs webhook configured (Non-Technical)
- [ ] Voice → Agent Builder → MCP flow working
- [ ] Test cases passed (`NON_TECHNICAL_IMPLEMENTATION_GUIDE.md` Phase 4)

### Phase 4: Validation & Launch
**Team Verification**
- [ ] End-to-end response time < 5 seconds
- [ ] All test scenarios pass
- [ ] Error handling verified
- [ ] Monitoring dashboards configured
- [ ] Rollback plan documented

---

**Status**: Complete wiring diagram ready for implementation
**Next Action**: Choose your path above and begin
**Quick Links:**
- 🚀 [Non-Technical Guide](NON_TECHNICAL_IMPLEMENTATION_GUIDE.md) - UI-based implementation
- 💻 [Developer Guide](MCP_NODE_MIGRATION_GUIDE.md) - Code changes
- 🎨 [Workflow Guide](AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md) - Agent Builder patterns
- 📚 [Knowledge Base](AGENT_BUILDER_MCP_CURRENT_KNOWLEDGE.md) - Feature reference

**Document Version**: 1.1
**Last Updated**: October 7, 2025
