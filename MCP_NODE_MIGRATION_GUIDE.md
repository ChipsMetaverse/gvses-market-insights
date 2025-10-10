# MCP Node Migration Guide
## From Actions (OpenAPI) to Direct MCP Integration

---

## 📋 Overview

This guide explains how to migrate from the **Actions approach** (OpenAPI → FastAPI → MCP servers) to using Agent Builder's **MCP node** for direct MCP server integration.

### Current Architecture (Actions)
```
Agent Builder (cloud)
    ↓ HTTPS
FastAPI (localhost:8000 or Fly.io)
    ↓ stdio/function calls
MCP Servers (market-mcp-server, alpaca-mcp-server)
    ↓
Data Sources (Yahoo, CNBC, Alpaca Markets)
```

### Target Architecture (MCP Node)
```
Agent Builder (cloud)
    ↓ HTTPS + MCP Protocol
MCP Servers (hosted publicly with network transport)
    ↓
Data Sources (Yahoo, CNBC, Alpaca Markets)
```

**Key Difference**: Agent Builder connects directly to MCP servers using the MCP protocol over network transport.

---

## ⚖️ Actions vs MCP Node: Decision Matrix

| Factor | Actions (Current) | MCP Node (Migration Target) |
|--------|-------------------|----------------------------|
| **Localhost Support** | ✅ Works immediately | ❌ Requires public hosting |
| **Setup Complexity** | ⭐ Low (5-10 min) | ⭐⭐⭐ High (2-4 hours) |
| **Tool Discovery** | Manual (OpenAPI spec) | Automatic (MCP protocol) |
| **Tool Count** | Curated (5 endpoints) | All available (35+ tools) |
| **Latency** | +1 hop (FastAPI) | Direct connection |
| **Security** | ✅ Keys server-side | ⚠️ Must secure MCP endpoints |
| **Debugging** | ✅ Easy (HTTP logs) | ⭐⭐ Harder (MCP protocol) |
| **Maintenance** | OpenAPI spec updates | MCP server transport |
| **API Evolution** | Controlled, versioned | Automatic, less control |
| **Caching/Rate Limiting** | ✅ In FastAPI | Must implement in MCP |

---

## 🎯 When to Migrate to MCP Node

### ✅ Good Reasons to Migrate:
1. **Tool Sprawl**: You have 35+ tools and want automatic discovery
2. **Latency Critical**: Every millisecond counts (though FastAPI hop is ~10-50ms)
3. **No API Facade Needed**: Don't need caching, auth, or rate limiting layer
4. **MCP-First Architecture**: Want to align with MCP ecosystem standards
5. **Reduce Maintenance**: Don't want to maintain OpenAPI spec

### ❌ Reasons to Stay with Actions:
1. **Localhost Development**: MCP node can't reach localhost
2. **Curated Tool Surface**: Want to expose only 5-10 key tools
3. **Centralized Control**: FastAPI provides caching, logging, auth
4. **Simpler Debugging**: HTTP logs easier than MCP protocol traces
5. **It's Working**: Actions approach meets your needs

### 🤔 Consider Hybrid Approach:
- Keep Actions for development (localhost)
- Use MCP node for production (hosted servers)
- A/B test to compare performance and reliability

---

## 🚧 Prerequisites for MCP Node Migration

### 1. Network Transport Layer

Your MCP servers currently use **stdio transport** (process stdin/stdout). For Agent Builder's MCP node to connect, you need **network transport** (HTTP, SSE, or WebSocket).

**Options:**

#### Option A: Add HTTP/SSE Transport to MCP Servers

For **market-mcp-server** (Node.js):
```javascript
// Add to your MCP server
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import express from "express";

const app = express();
const mcpServer = new Server({
  name: "market-mcp-server",
  version: "1.0.0"
});

// Existing tool definitions...
mcpServer.setRequestHandler(/* ... */);

// Add SSE endpoint
app.get("/mcp/sse", async (req, res) => {
  const transport = new SSEServerTransport("/mcp/message", res);
  await mcpServer.connect(transport);
});

app.post("/mcp/message", express.json(), async (req, res) => {
  // Handle MCP messages
});

app.listen(3000, () => {
  console.log("MCP server with SSE transport on port 3000");
});
```

For **alpaca-mcp-server** (Python):
```python
# Add to your MCP server
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route
import uvicorn

mcp_server = Server("alpaca-mcp-server")

# Existing tool definitions...

async def handle_sse(request):
    async with SseServerTransport("/mcp/message") as transport:
        await mcp_server.run(
            transport.read_stream,
            transport.write_stream,
            mcp_server.create_initialization_options()
        )

async def handle_messages(request):
    # Handle MCP protocol messages
    pass

app = Starlette(routes=[
    Route("/mcp/sse", handle_sse),
    Route("/mcp/message", handle_messages, methods=["POST"])
])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)
```

#### Option B: Use MCP Gateway/Proxy

Deploy a separate service that bridges stdio MCP servers to network transport:

```bash
# Example using mcp-proxy (hypothetical tool)
mcp-proxy \
  --stdio-command "node market-mcp-server/build/index.js" \
  --http-port 3000 \
  --auth-token $MCP_AUTH_TOKEN
```

### 2. Public Hosting

Agent Builder runs in OpenAI's cloud and needs HTTPS access to your MCP servers.

**Hosting Options:**

| Platform | Complexity | Cost | Notes |
|----------|-----------|------|-------|
| **Fly.io** | ⭐⭐ Medium | Free tier available | Good for global edge deployment |
| **Railway** | ⭐ Easy | $5/month | Simple deploys, good DX |
| **Render** | ⭐ Easy | Free tier available | Auto-deploys from Git |
| **AWS ECS/Fargate** | ⭐⭐⭐ Complex | Pay-as-you-go | Enterprise-grade |
| **Cloudflare Workers** | ⭐⭐⭐ Complex | Free tier generous | Edge compute, need adapter |

**For Quick Testing: Use ngrok or Cloudflare Tunnel**
```bash
# Terminal 1: Run MCP server with network transport
node market-mcp-server/build/index.js --transport http --port 3000

# Terminal 2: Expose via ngrok
ngrok http 3000 --authtoken $NGROK_AUTH_TOKEN

# Use ngrok URL in Agent Builder: https://abcd-1234.ngrok-free.app
```

### 3. Authentication & Security

MCP servers designed for localhost often lack auth. For production:

**Minimum Security Requirements:**
- ✅ HTTPS/TLS (required by Agent Builder)
- ✅ Authentication (Bearer token, API key)
- ✅ Rate limiting (prevent abuse)
- ✅ Input validation (sanitize tool parameters)
- ✅ CORS configuration (if using HTTP transport)

**Example: Add Bearer Token Auth**

For Express (Node.js):
```javascript
app.use((req, res, next) => {
  const authHeader = req.headers.authorization;
  const expectedToken = process.env.MCP_AUTH_TOKEN;

  if (!authHeader || authHeader !== `Bearer ${expectedToken}`) {
    return res.status(401).json({ error: "Unauthorized" });
  }
  next();
});
```

For Starlette (Python):
```python
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware

async def verify_token(request):
    auth = request.headers.get("Authorization")
    expected = f"Bearer {os.getenv('MCP_AUTH_TOKEN')}"
    if auth != expected:
        raise HTTPException(401, "Unauthorized")

app = Starlette(
    middleware=[Middleware(AuthenticationMiddleware, backend=verify_token)]
)
```

### 4. Secrets Management

Store API keys (Alpaca, Alpha Vantage, etc.) securely:

**Options:**
- **Environment variables** (basic, for development)
- **Fly.io Secrets**: `fly secrets set ALPACA_API_KEY=xxx`
- **Railway Variables**: Set in dashboard
- **AWS Secrets Manager** (enterprise)
- **HashiCorp Vault** (advanced)

---

## 🔧 Migration Steps

### Step 1: Add Network Transport to MCP Servers (2-3 hours)

1. **Choose transport**: HTTP+SSE (recommended) or WebSocket
2. **Install dependencies**:
   ```bash
   # Node.js
   npm install @modelcontextprotocol/sdk express

   # Python
   pip install mcp starlette uvicorn
   ```
3. **Implement transport** (see code examples above)
4. **Test locally**:
   ```bash
   # Start server with network transport
   node market-mcp-server/build/index.js --transport sse --port 3000

   # Test with curl (should return MCP protocol response)
   curl http://localhost:3000/mcp/sse
   ```

### Step 2: Deploy to Production (1-2 hours)

**Example: Deploy to Fly.io**

Create `fly.toml` for each MCP server:
```toml
app = "market-mcp-server"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "3000"
  MCP_TRANSPORT = "sse"

[[services]]
  internal_port = 3000
  protocol = "tcp"

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

Create `Dockerfile`:
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "build/index.js", "--transport", "sse"]
```

Deploy:
```bash
fly deploy
fly secrets set \
  ALPHA_VANTAGE_API_KEY=$ALPHA_VANTAGE_API_KEY \
  MCP_AUTH_TOKEN=$(openssl rand -hex 32)

# Note the URL: https://market-mcp-server.fly.dev
```

Repeat for alpaca-mcp-server.

### Step 3: Configure Agent Builder MCP Node (10 minutes)

1. **Open Agent Builder**: https://platform.openai.com/agent-builder
2. **Open your workflow**: `wf_68e474d14d28819085`
3. **Add MCP Node**:
   - Drag **MCP** node from left sidebar
   - Place between Start and G'sves Agent (or parallel to Actions)
4. **Configure MCP Node**:
   - Click **"Add your own server"**
   - Server URL: `https://market-mcp-server.fly.dev/mcp/sse`
   - Transport: HTTP+SSE
   - Authentication: Add secret for Bearer token
     - Key: `Authorization`
     - Value: `Bearer your-mcp-auth-token-here`
5. **Verify Tool Discovery**:
   - MCP node should list all 35+ tools from market-mcp-server
   - Check: `yahoo_get_quote`, `yahoo_get_historical`, `cnbc_get_news`, etc.
6. **Optional: Filter Tools**:
   - Click "Configure Tools"
   - Select only tools you want agent to use (e.g., top 10)
   - This prevents tool sprawl and improves agent tool selection

### Step 4: Connect MCP Node to Agent (5 minutes)

**Option A: Replace Actions**
1. Remove connection between Start → G'sves Agent
2. Connect: Start → MCP Node → G'sves Agent
3. Disable/remove old Actions

**Option B: Parallel (A/B Test)**
1. Keep existing Actions path
2. Add new MCP path: Start → MCP Node → New G'sves Agent Clone
3. Use Branch node to split traffic 50/50
4. Compare performance and reliability

### Step 5: Update Agent Instructions (2 minutes)

MCP node provides tool names automatically, but verify they match:

```markdown
TOOL USAGE (MCP NODE):
- Current prices: `yahoo_get_quote(symbol)`
- Historical data: `yahoo_get_historical(symbol, days, interval)`
- Company search: `yahoo_search_symbol(query)`
- News: `cnbc_get_news(symbol)` or `yahoo_get_news(symbol)`
- Market overview: `yahoo_get_market_indices()`

All tools are discovered automatically via MCP protocol.
Call the appropriate tool based on user query.
```

### Step 6: Test MCP Integration (10 minutes)

Run the same test cases from Actions setup:

**Test 1: Price Query**
```
Input: "What is the current price of AAPL?"
Expected Tool Call: yahoo_get_quote(symbol="AAPL")
Verify: Response includes real-time price
```

**Test 2: Company Search**
```
Input: "Show me Microsoft's price"
Expected Tool Calls:
1. yahoo_search_symbol(query="Microsoft")
2. yahoo_get_quote(symbol="MSFT")
```

**Test 3: Historical Analysis**
```
Input: "Give me a trade setup for TSLA"
Expected Tool Calls:
1. yahoo_get_quote(symbol="TSLA")
2. yahoo_get_historical(symbol="TSLA", days=90)
3. cnbc_get_news(symbol="TSLA")
```

**Monitor MCP Server Logs**:
```bash
# Fly.io
fly logs -a market-mcp-server

# Local testing
# Check your MCP server's console output for incoming requests
```

### Step 7: Monitor and Optimize (Ongoing)

**Key Metrics to Track:**
- **Latency**: Compare MCP vs Actions response times
- **Success Rate**: Tool call success vs failure ratio
- **Tool Usage**: Which tools are called most frequently
- **Error Patterns**: Common failure modes

**Logging Setup**:
```javascript
// Add to MCP server
mcpServer.on("tool-call", (toolName, params) => {
  console.log(`[MCP] Tool called: ${toolName}`, params);
});

mcpServer.on("tool-result", (toolName, result, duration) => {
  console.log(`[MCP] Tool result: ${toolName} (${duration}ms)`);
});

mcpServer.on("tool-error", (toolName, error) => {
  console.error(`[MCP] Tool error: ${toolName}`, error);
});
```

---

## 🔍 Comparison: Before vs After

### Before (Actions)

**Request Flow:**
```
User: "What is AAPL price?"
  ↓
Agent Builder (gpt-4o)
  ↓ HTTPS POST /api/stock-price?symbol=AAPL
FastAPI (Fly.io)
  ↓ stdio MCP call
market-mcp-server (local)
  ↓ HTTP GET
Yahoo Finance API
  ↓
Response: {"symbol": "AAPL", "price": 178.32, ...}
```

**Total Latency**: ~500-800ms
- Agent reasoning: 200-300ms
- FastAPI call: 100-200ms
- MCP call: 50-100ms
- Yahoo API: 150-200ms

### After (MCP Node)

**Request Flow:**
```
User: "What is AAPL price?"
  ↓
Agent Builder (gpt-4o)
  ↓ MCP Protocol (SSE/HTTP)
market-mcp-server (Fly.io)
  ↓ HTTP GET
Yahoo Finance API
  ↓
Response: {"symbol": "AAPL", "price": 178.32, ...}
```

**Total Latency**: ~400-700ms (saved ~100ms)
- Agent reasoning: 200-300ms
- MCP call: 50-100ms (direct)
- Yahoo API: 150-200ms

**Latency Savings**: ~10-15% faster (FastAPI hop removed)

---

## 🐛 Troubleshooting MCP Node Integration

### "Could not connect to MCP server"

**Causes:**
- Server not reachable (firewall, DNS)
- Wrong URL or transport type
- SSL/TLS certificate issues

**Fixes:**
1. Test server directly: `curl https://your-mcp-server.fly.dev/mcp/sse`
2. Check DNS: `nslookup your-mcp-server.fly.dev`
3. Verify TLS: `openssl s_client -connect your-mcp-server.fly.dev:443`
4. Check server logs for connection attempts

### "Authentication failed"

**Causes:**
- Missing or incorrect Bearer token
- Token not in secrets store

**Fixes:**
1. In Agent Builder, go to MCP node settings
2. Click "Authentication" → Add secret
3. Ensure format: `Bearer your-token-here` (not just the token)
4. Regenerate token if needed: `openssl rand -hex 32`

### "Tools not discovered"

**Causes:**
- MCP server not implementing protocol correctly
- Transport handshake failing

**Fixes:**
1. Check MCP server logs for initialization errors
2. Verify server returns tool list on `tools/list` request
3. Test with MCP client locally:
   ```bash
   npx @modelcontextprotocol/inspector http://localhost:3000/mcp/sse
   ```

### "Tool calls timing out"

**Causes:**
- Yahoo/CNBC APIs slow
- MCP server overloaded
- Network latency (server in wrong region)

**Fixes:**
1. Add timeout handling in MCP server
2. Deploy closer to Agent Builder (US East coast recommended)
3. Implement caching in MCP server for frequently requested data
4. Scale up server resources (more CPU/memory)

### "High error rates"

**Causes:**
- Third-party API rate limits (Yahoo, CNBC)
- MCP server bugs
- Invalid parameters from agent

**Fixes:**
1. Add rate limiting and retries in MCP server
2. Validate tool parameters before calling APIs
3. Return helpful error messages to agent
4. Implement fallback strategies (Alpaca → Yahoo → Error)

---

## 💰 Cost Comparison

### Actions Approach (Current)
- **Fly.io FastAPI**: Free tier or ~$5/month
- **MCP Servers**: Run locally (free) or ~$0
- **Total**: $0-5/month

### MCP Node Approach
- **Fly.io market-mcp-server**: ~$5/month
- **Fly.io alpaca-mcp-server**: ~$5/month
- **Total**: ~$10/month

**Trade-off**: Pay $5-10/month for:
- ~100ms latency reduction
- Automatic tool discovery
- No OpenAPI spec maintenance

---

## 📊 Performance Benchmarks

Based on typical trading queries:

| Query Type | Actions Latency | MCP Node Latency | Improvement |
|------------|----------------|------------------|-------------|
| Simple price | 500-800ms | 400-700ms | ~15% faster |
| Historical data | 1-1.5s | 0.9-1.4s | ~10% faster |
| News + analysis | 3-5s | 2.8-4.8s | ~5% faster |
| Multi-tool calls | 5-8s | 4.5-7.5s | ~8% faster |

**Conclusion**: MCP node provides **modest latency improvements** (50-200ms) but requires additional hosting costs and complexity.

---

## ✅ Migration Checklist

### Pre-Migration
- [ ] Actions approach working and tested
- [ ] Decision made: Is migration worth it?
- [ ] Budget approved for hosting costs (~$10/month)

### Transport Layer
- [ ] Network transport added to market-mcp-server
- [ ] Network transport added to alpaca-mcp-server
- [ ] Local testing completed (localhost:3000, 3001)
- [ ] Authentication implemented (Bearer token)

### Hosting
- [ ] Fly.io account created (or alternative)
- [ ] market-mcp-server deployed to production
- [ ] alpaca-mcp-server deployed to production
- [ ] TLS/HTTPS verified (curl test)
- [ ] Secrets configured (API keys, auth tokens)

### Agent Builder
- [ ] MCP node added to workflow
- [ ] Server URL configured
- [ ] Authentication secret added
- [ ] Tools discovered (verified in UI)
- [ ] Tools filtered (if needed, to prevent sprawl)
- [ ] Connected to G'sves Agent node

### Testing
- [ ] Test 1: Simple price query (AAPL)
- [ ] Test 2: Company search (Microsoft → MSFT)
- [ ] Test 3: Historical analysis (TSLA trade setup)
- [ ] Test 4: News aggregation
- [ ] Test 5: Error handling (invalid symbol)
- [ ] Latency comparison (MCP vs Actions)

### Monitoring
- [ ] Logging configured in MCP servers
- [ ] Error tracking (Sentry or equivalent)
- [ ] Latency monitoring (Prometheus/Grafana or equivalent)
- [ ] Cost monitoring (Fly.io dashboard)

### Cleanup (Optional)
- [ ] Remove old Actions from Agent Builder
- [ ] Remove FastAPI if no longer needed
- [ ] Update documentation
- [ ] Archive openapi_agent_builder.json

---

## 🚀 Rollback Plan

If MCP node integration has issues:

### Immediate Rollback (5 minutes)
1. In Agent Builder, disconnect MCP node
2. Reconnect old Actions path
3. Verify Actions still working
4. Investigate MCP issues offline

### Gradual Rollback
1. Use Branch node to split traffic
2. Reduce MCP traffic from 50% → 25% → 10% → 0%
3. Monitor error rates during ramp-down
4. Fix issues and retry

### Keep Both (Hybrid)
- Actions for development (localhost)
- MCP node for production (hosted)
- Maintain both code paths

---

## 📚 Additional Resources

### MCP Protocol Documentation
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **MCP SDK (Node.js)**: https://github.com/modelcontextprotocol/typescript-sdk
- **MCP SDK (Python)**: https://github.com/modelcontextprotocol/python-sdk

### Agent Builder Documentation
- **MCP Node Reference**: https://platform.openai.com/docs/guides/node-reference#mcp
- **Actions vs MCP**: https://platform.openai.com/docs/guides/tools-connectors-mcp

### Hosting Platforms
- **Fly.io Docs**: https://fly.io/docs/
- **Railway Docs**: https://docs.railway.app/
- **Render Docs**: https://render.com/docs

---

## 🎯 Conclusion

**TL;DR:**
- Actions (current) ✅ works, simple, secure
- MCP node ⚡ slightly faster, more complex, requires hosting
- Recommendation: **Stick with Actions** unless you need automatic tool discovery for 35+ tools

**When to migrate:**
- ✅ After Actions approach is stable and tested
- ✅ If latency becomes critical (saving 50-200ms)
- ✅ If you want to expose all 35+ tools automatically
- ✅ If you're comfortable with MCP protocol debugging

**When NOT to migrate:**
- ❌ If Actions meets your needs (it probably does)
- ❌ If you prefer curated tool surface (5 key endpoints)
- ❌ If you value simpler debugging (HTTP logs)
- ❌ If localhost development is important

---

**Created**: October 7, 2025
**Status**: Reference guide for future migration
**Estimated Time**: 4-6 hours total (transport + hosting + testing)
**Recommended**: Only after Actions approach is working in production ✅
