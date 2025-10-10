# Agent Builder MCP Integration - Step-by-Step Guide

**Created**: October 7, 2025
**Purpose**: Complete guide for integrating market-mcp-server with OpenAI Agent Builder
**Status**: Ready except for custom MCP server registration (see section 4)

---

## 🎯 Overview

This guide shows you how to build visual AI workflows in Agent Builder and integrate your custom `market-mcp-server` for market data tools.

**What You'll Learn:**
1. Building workflows with Agent Builder nodes
2. Testing and debugging workflows
3. Publishing workflows for production
4. **Integrating custom MCP servers** (pending registration documentation)

**Prerequisites:**
- OpenAI account with Agent Builder access
- `market-mcp-server` ready to deploy
- Basic understanding of API endpoints

---

## Part 1: Building Your First Workflow

### Step 1: Access Agent Builder

1. Visit [OpenAI Platform](https://platform.openai.com)
2. Log in to your account
3. Navigate to Agent Builder (should appear in sidebar)

### Step 2: Create New Workflow

1. Click **"Create"** in left sidebar
2. Select **"New Workflow"**
3. Name your workflow (e.g., "G'sves Market Assistant")

### Step 3: Understand the Interface

**Left Sidebar** (Available Nodes):
- Agent
- Jailbreak Guardrail
- Classification Agent
- Condition (If/Else)
- User Approval
- Set State
- Transform
- **MCP** ⭐
- Web Search
- Code Interpreter
- File Search

**Center Canvas**:
- Drag & drop nodes here
- Connect nodes by dragging between outputs/inputs
- Visual workflow representation

**Right Properties Panel**:
- Configure selected node
- Set instructions, variables, authentication
- Test connections

---

## Part 2: Building a Market Data Workflow

### Example: G'sves Trading Assistant Workflow

```
User Query
  ↓
Classification Agent (market data vs chart command)
  ↓
Condition Node
  ├─ Market Data → MCP Node (market-mcp-server) → Agent (analysis)
  └─ Chart Command → Agent (chart instructions) → Response
```

### Step-by-Step Construction:

#### 1. Add Classification Agent

**Purpose**: Determine if user wants market data or chart interaction

1. Drag **"Classification Agent"** onto canvas
2. Click to open properties panel
3. Configure:
   ```
   Name: Intent Classifier
   Instructions: Classify user intent as either "market_data" or "chart_command"
   Output Format: JSON with "intent" field
   ```
4. Example output: `{"intent": "market_data"}`

#### 2. Add Condition Node

**Purpose**: Route based on classification

1. Drag **"Condition"** onto canvas
2. Connect Classification Agent output → Condition input
3. Configure:
   ```
   Condition: intent === "market_data"
   True Branch: Market Data Path
   False Branch: Chart Command Path
   ```

#### 3. Add MCP Node (Market Data Path)

**Purpose**: Call market-mcp-server tools

1. Drag **"MCP"** onto canvas
2. Connect Condition (true branch) → MCP Node
3. Configure (see Part 3 for authentication)
4. Select tools to enable (once server registered)

#### 4. Add Agent for Analysis

**Purpose**: Interpret market data and provide insights

1. Drag **"Agent"** onto canvas
2. Connect MCP Node output → Agent input
3. Configure:
   ```
   Name: G'sves Analyst
   Instructions: You are G'sves, a seasoned trading mentor...
   (Copy from AGENT_BUILDER_SYSTEM_INSTRUCTIONS.md)

   Use variables: {{stock_data}}, {{news}}, {{price}}
   ```

#### 5. Variable Passing

**Between nodes**, use curly braces:
```
User message: "What's AAPL doing?"
Classification: {"intent": "market_data", "symbol": "AAPL"}
MCP call: get_stock_price({{symbol}})
Agent prompt: "Analyze {{stock_data}} for {{symbol}}"
```

---

## Part 3: MCP Node Configuration (Pre-built Servers)

### How to Configure MCP Node

1. **Select MCP Server**:
   - Click MCP node
   - Properties panel shows "Available Servers"
   - Select from dropdown (e.g., Microsoft Outlook)

2. **Configure Authentication**:
   - Choose auth method: API Key, Headers, or OAuth
   - Example for API Key:
     ```
     Auth Type: Bearer Token
     Header Name: Authorization
     Value: Bearer YOUR_API_KEY
     ```

3. **Test Connection**:
   - Click **"Test"** button
   - Verify success before continuing

4. **Select Tools** (if available):
   - View discovered tools
   - Enable/disable specific functions
   - Configure parameters

### Example: Connecting to Pre-built Server

```
Server: Microsoft Outlook
Auth Type: OAuth
Permissions: Read Mail, Send Mail
Tools:
  ✓ read_email
  ✓ send_email
  ✗ delete_email (disabled)
```

---

## Part 4: Custom MCP Server Integration ✅ SOLVED!

### ✅ Custom Server Registration - Complete Process

**Discovery**: Screenshot from Agent Builder UI (October 7, 2025) reveals the complete process!

#### How to Add Custom MCP Servers:

**Step 1: Prepare Your MCP Server**

1. Add HTTP/SSE transport to `market-mcp-server`:
   ```bash
   cd market-mcp-server
   npm install @modelcontextprotocol/server-http
   # Update index.js with HTTP transport
   # See MCP_NODE_MIGRATION_GUIDE.md for details
   ```

2. Deploy to public HTTPS endpoint:
   ```bash
   fly deploy
   # Or use Railway, Render, etc.
   # Get URL: https://market-mcp.fly.dev
   ```

**Step 2: Add Server in Agent Builder**

1. **Open Workflow**: Navigate to your workflow in Agent Builder

2. **Click MCP Node**: Select MCP node on canvas

3. **Click "+ Add"**: In MCP panel (top right), click the "+ Add" button

4. **Fill Connection Dialog**:
   ```
   ┌─────────────────────────────────────────┐
   │     Connect to MCP Server              │
   ├─────────────────────────────────────────┤
   │ URL                                     │
   │ Only use MCP servers you trust and verify│
   │ ┌───────────────────────────────────┐  │
   │ │ https://market-mcp.fly.dev        │  │
   │ └───────────────────────────────────┘  │
   │                                         │
   │ Label                                   │
   │ ┌───────────────────────────────────┐  │
   │ │ Market Data MCP                    │  │
   │ └───────────────────────────────────┘  │
   │                                         │
   │ Description (optional)                  │
   │ ┌───────────────────────────────────┐  │
   │ │ Real-time market data and analysis │  │
   │ └───────────────────────────────────┘  │
   │                                         │
   │ Authentication ⓘ                       │
   │ ┌───────────────────────────────────┐  │
   │ │ Access token / API key         ▼  │  │
   │ └───────────────────────────────────┘  │
   │ 🔑 Add your access token (if needed)   │
   │                                         │
   │  [Back]              [⚡ Connect]      │
   └─────────────────────────────────────────┘
   ```

5. **Click "Connect"**: Agent Builder will:
   - Attempt connection to your server
   - Verify MCP protocol handshake
   - Auto-discover available tools (35+ tools from market-mcp-server)
   - Add server to your MCP server list

**Step 3: Verify Connection**

1. **Check Server List**: Your server should now appear in MCP dropdown
2. **View Tools**: Tools automatically discovered and available
3. **Test in Workflow**: Use preview mode to test tool calls

### Authentication Options

**Dropdown shows**:
- Access token / API key (default)
- OAuth (if supported)
- Custom headers (possibly)

**For market-mcp-server**:
- If public: Leave authentication blank or add optional API key
- If secured: Add Bearer token in authentication field

### Tool Auto-Discovery

**After connection:**
- Agent Builder sends `tools/list` MCP request
- Server responds with all 35+ market data tools
- Tools appear in MCP node configuration
- Select which tools to enable in workflow

### Example: market-mcp-server Configuration

```
URL: https://market-mcp.fly.dev
Label: Market Data MCP
Description: Real-time market data, news, and analysis tools
Authentication: Access token / API key (optional)
Token: [Your API key if server requires auth]

Tools Auto-Discovered:
✓ get_stock_price
✓ get_stock_history
✓ get_stock_news
✓ get_market_overview
✓ search_symbol
✓ [30+ additional tools...]
```

### Important Notes

**Security Warning**:
- "Only use MCP servers you trust and verify"
- User takes responsibility for custom servers
- No OpenAI approval process required
- Self-service registration

**Server Requirements**:
- ✅ HTTPS endpoint (required)
- ✅ MCP protocol implementation
- ✅ HTTP/SSE transport
- ✅ Publicly accessible
- ❌ HTTP not allowed
- ❌ Localhost not accessible from Agent Builder

---

## Part 5: Testing & Debugging

### Preview Mode

1. Click **"Preview"** button (top of screen)
2. Enter test query: "What is the current price of AAPL?"
3. Watch workflow execute step-by-step
4. Verify each node processes correctly

### View Tool Call Logs

1. In preview mode, click **"View tool call logs"**
2. See all MCP tool calls and responses:
   ```
   [12:34:56] MCP Call: get_stock_price(symbol="AAPL")
   [12:34:57] Response: {"price": 178.32, "change": 3.45, ...}
   [12:34:58] Agent: "Apple is currently trading at $178.32..."
   ```

### Debugging Failures

**If workflow fails:**

1. Click **"Debug"** button
2. Review error message
3. Common issues:
   - **Authentication failed**: Check MCP node auth settings, click "Test"
   - **Tool not found**: Verify MCP server is online, tools registered
   - **Variable error**: Check curly brace syntax `{{variable}}`
   - **Node disconnected**: Ensure all nodes connected properly

### Testing Authentication

**Before publishing:**

1. Click MCP node
2. Click **"Test authentication"** button
3. Verify success message
4. If fails: Check API key, headers, server availability

---

## Part 6: Publishing & Integration

### Publishing Workflow

1. **Final Testing**:
   - Run multiple test queries
   - Test error cases (invalid symbols, etc.)
   - Verify all branches execute correctly

2. **Click Publish**:
   - Navigate to publish interface
   - Assign version number (auto-increments)
   - Add release notes (optional)

3. **Receive Credentials**:
   - Workflow ID: `wf_abc123...`
   - Version: `v1.0`
   - API endpoint URL

### Integrating with Your Frontend

**Option 1: Direct API Calls**

```python
import requests

workflow_id = "wf_abc123..."
version = "v1.0"

response = requests.post(
    f"https://api.openai.com/v1/workflows/{workflow_id}/execute",
    headers={
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": {"message": "What is AAPL doing?"},
        "version": version
    }
)

result = response.json()
```

**Option 2: ChatKit SDK**

Embed in your React frontend:
```javascript
import { ChatKit } from '@openai/chatkit';

const chat = new ChatKit({
  workflowId: 'wf_abc123...',
  version: 'v1.0',
  apiKey: process.env.OPENAI_API_KEY
});

// Customize appearance
chat.setTheme({
  primaryColor: '#007bff',
  fontFamily: 'Inter'
});

// Render
chat.render('#chat-container');
```

### Version Management

**Creating New Versions:**
1. Make changes to workflow
2. Test thoroughly
3. Click "Publish" → New version created
4. Old versions remain accessible

**Rolling Back:**
1. Go to "Manage" sidebar
2. Select workflow
3. View version history
4. Click "Revert to v1.0" (or any version)

---

## Part 7: Advanced Patterns

### Pattern 1: Multi-Tool Market Analysis

```
User Query → Classification
  ↓
Parallel MCP Calls:
  ├─ get_stock_price
  ├─ get_stock_history
  └─ get_stock_news
  ↓
Transform (combine data)
  ↓
Agent (G'sves analysis)
```

**Implementation:**
- Use multiple MCP nodes in parallel
- Connect all to Transform node
- Transform combines JSON outputs
- Agent receives complete market picture

### Pattern 2: Approval Gate for Trades

```
User: "Buy 100 shares of AAPL"
  ↓
Agent (validates trade setup)
  ↓
User Approval Node
  ├─ Approve → Execute trade
  └─ Reject → Explain why rejected
```

**Safety Feature:**
- Prevents accidental trades
- Human confirmation required
- Audit trail in logs

### Pattern 3: Jailbreak Protection

```
User Input → Jailbreak Guardrail
  ├─ Safe → Continue to Agent
  └─ Suspicious → Block with warning
```

**Security:**
- Detects prompt injection attempts
- Validates input before processing
- Protects against malicious queries

---

## Part 8: Your Market-MCP-Server Integration

### Workflow Design for G'sves

**Recommended Architecture:**

```
User Voice/Text Input
  ↓
Classification Agent
  ├─ Market Data Query
  │   ↓
  │   MCP Node (market-mcp-server)
  │   ├─ get_stock_price
  │   ├─ get_stock_history
  │   ├─ get_stock_news
  │   └─ get_market_overview
  │   ↓
  │   G'sves Agent (LTB/ST/QE analysis)
  │
  ├─ Chart Command
  │   ↓
  │   Agent (chart instructions)
  │
  └─ Educational Query
      ↓
      File Search (knowledge base)
      ↓
      Agent (teaching response)
```

### Tools from market-mcp-server

Once registered, you'll have access to:

1. `get_stock_price(symbol)` - Real-time quotes
2. `get_stock_history(symbol, days, interval)` - Historical data
3. `get_stock_news(symbol, limit)` - News articles
4. `get_market_overview()` - Market indices
5. `search_symbol(query)` - Company name → ticker
6. ... (30+ more tools from your MCP server)

### Agent Instructions

Copy from `AGENT_BUILDER_SYSTEM_INSTRUCTIONS.md`:
- G'sves personality and methodology
- LTB/ST/QE framework
- Risk management (2% rule)
- Options strategy
- Voice response guidelines

---

## Part 9: Monitoring & Optimization

### Performance Monitoring

**Via Logs Sidebar:**
- View all workflow executions
- See success/failure rates
- Track response times
- Monitor tool usage

**Metrics to Track:**
- Average workflow duration
- MCP tool call latency
- Error rate by node
- User satisfaction (if collecting feedback)

### Optimization Strategies

1. **Reduce Sequential Dependencies**:
   - Run MCP calls in parallel when possible
   - Use Transform to combine results

2. **Cache Frequent Data**:
   - Use Set State for market hours, common symbols
   - Reduce redundant API calls

3. **Optimize Agent Prompts**:
   - Shorter prompts = faster responses
   - Clear instructions = fewer retries

4. **Error Handling**:
   - Add fallback paths for MCP failures
   - Provide graceful error messages

---

## Part 10: Troubleshooting Guide

### Common Issues

#### 1. "MCP Server Not Found"
**Cause**: Server not in available list
**Fix**: See Part 4 - Custom server registration needed

#### 2. "Authentication Failed"
**Cause**: Invalid API key or headers
**Fix**:
- Click "Test authentication" button
- Verify API key is correct
- Check header format (e.g., `Bearer YOUR_KEY`)
- Ensure server is publicly accessible

#### 3. "Tool Not Available"
**Cause**: MCP server not exposing tool
**Fix**:
- Verify tool exists in market-mcp-server
- Check MCP server logs for errors
- Ensure HTTP/SSE transport configured
- Test server endpoint directly

#### 4. "Workflow Timeout"
**Cause**: MCP call taking too long
**Fix**:
- Optimize server response time
- Add timeout handling in workflow
- Use faster data sources if available

#### 5. "Variable Not Found"
**Cause**: Incorrect variable syntax
**Fix**:
- Use `{{variable_name}}` (double curly braces)
- Check variable is output from previous node
- Verify spelling matches exactly

---

## 📚 Additional Resources

### Related Documentation:
- `AGENT_BUILDER_MCP_CURRENT_KNOWLEDGE.md` - Complete knowledge base
- `MCP_NODE_MIGRATION_GUIDE.md` - HTTP/SSE transport setup
- `AGENT_BUILDER_SYSTEM_INSTRUCTIONS.md` - G'sves agent prompts
- `CURRENT_ARCHITECTURE_CLARIFICATION.md` - Backend vs Agent Builder

### OpenAI Documentation:
- [Agent Builder Docs](https://platform.openai.com/docs/agent-builder)
- [MCP Protocol](https://platform.openai.com/docs/mcp)
- [Workflow API](https://platform.openai.com/docs/api-reference/workflows)

### Next Steps:
1. ✅ Study this guide
2. ⏳ Wait for custom MCP server registration documentation
3. ⏳ Deploy market-mcp-server with HTTP/SSE transport
4. ⏳ Register with Agent Builder
5. ⏳ Build G'sves workflow
6. ⏳ Test and publish
7. ⏳ Integrate with frontend

---

## 🎯 Quick Start Checklist

**Before you start:**
- [ ] OpenAI account with Agent Builder access
- [ ] Reviewed this guide completely
- [ ] market-mcp-server code ready
- [ ] Deployment platform chosen (Fly.io)

**Building workflow:**
- [ ] Created new workflow in Agent Builder
- [ ] Added Classification Agent for intent routing
- [ ] Added Condition node for branching
- [ ] **Added MCP node** (pending registration process)
- [ ] Added G'sves Agent with instructions
- [ ] Connected all nodes properly
- [ ] Tested with Preview mode
- [ ] Reviewed tool call logs
- [ ] Fixed any errors

**Publishing:**
- [ ] Tested all workflow branches
- [ ] Tested error cases
- [ ] Published workflow
- [ ] Saved Workflow ID and version
- [ ] Integrated with frontend
- [ ] Monitoring performance

**Post-launch:**
- [ ] Monitor logs for errors
- [ ] Collect user feedback
- [ ] Optimize based on metrics
- [ ] Create new versions as needed

---

**Status**: Guide complete except for Part 4 (custom MCP server registration)
**Blocking Issue**: Custom server registration process unknown
**Ready to Use**: All other workflow building, testing, and publishing procedures documented
