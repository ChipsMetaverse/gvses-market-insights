# Comprehensive Implementation Walkthrough
## G'sves Agent Builder Integration - Step-by-Step Guide

**Created**: October 8, 2025
**Audience**: Technical and non-technical team members
**Goal**: Complete Agent Builder implementation from zero to production
**Time Estimate**: 6-8 hours total (can be split across multiple sessions)

---

## 📋 Table of Contents

1. [Pre-Implementation Checklist](#pre-implementation-checklist)
2. [Phase 1: MCP Server Preparation (1-2 hours)](#phase-1-mcp-server-preparation)
3. [Phase 2: Agent Builder Workflow (2-3 hours)](#phase-2-agent-builder-workflow)
4. [Phase 3: Backend Integration (1 hour)](#phase-3-backend-integration)
5. [Phase 4: Testing & Validation (1-2 hours)](#phase-4-testing--validation)
6. [Phase 5: Production Deployment (30-60 min)](#phase-5-production-deployment)
7. [Phase 6: Enhancement - Vector Store (OPTIONAL)](#phase-6-enhancement---vector-store)
8. [Phase 7: Enhancement - Loop Node (OPTIONAL)](#phase-7-enhancement---loop-node)
9. [Troubleshooting Guide](#troubleshooting-guide)
10. [Quick Reference](#quick-reference)

---

## Pre-Implementation Checklist

### ✅ Required Accounts & Access

- [ ] **OpenAI Account** with Agent Builder access (platform.openai.com)
- [ ] **Fly.io Account** for MCP server deployment (fly.io)
- [ ] **Backend Access** to update environment variables
- [ ] **Git Access** to current codebase

### ✅ Required Information

Gather these before starting:

```bash
# Current Setup
G'sves Assistant ID: asst_FgdYMBvUvKUy0mxX5AF7Lmyg
Backend API URL: https://gvses-market-insights.fly.dev
Market MCP Server (local): /Volumes/.../market-mcp-server/

# Accounts
OpenAI Email: [your email]
Fly.io Email: [your email]
```

### ✅ Required Tools

- [ ] **Code Editor** (VS Code recommended)
- [ ] **Terminal** access
- [ ] **Web Browser** (Chrome/Firefox/Safari)
- [ ] **Fly CLI** installed: `curl -L https://fly.io/install.sh | sh`

### ✅ Knowledge Prerequisites

**Technical Person** should understand:
- Node.js basics
- Environment variables
- Command line usage
- Git basics

**Non-Technical Person** can:
- Follow UI instructions in Agent Builder
- Copy-paste configurations
- No coding required for Phase 2!

---

## Phase 1: MCP Server Preparation (1-2 hours)

### Overview
Transform your local market-mcp-server from stdio (localhost only) to HTTP/SSE (cloud accessible).

**Who Does This**: Backend developer (technical)
**Result**: MCP server accessible at https://market-mcp.fly.dev

### Step 1.1: Update MCP Server Transport

**Location**: `market-mcp-server/index.js`

**Current Code** (lines ~2-50):
```javascript
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

// ... server definition ...

const transport = new StdioServerTransport();
await server.connect(transport);
```

**Replace With**:
```javascript
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// SSE endpoint for MCP protocol
app.get('/sse', async (req, res) => {
  console.log('New SSE connection');
  const transport = new SSEServerTransport('/message', res);
  await server.connect(transport);
});

// Message endpoint for client requests
app.post('/message', async (req, res) => {
  // SSE transport handles this
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`MCP Server running on port ${PORT}`);
  console.log(`Health: http://localhost:${PORT}/health`);
  console.log(`SSE: http://localhost:${PORT}/sse`);
});
```

**Save File**: `market-mcp-server/index.js`

### Step 1.2: Update Package Dependencies

**Location**: `market-mcp-server/package.json`

**Add Dependencies**:
```json
{
  "name": "market-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "express": "^4.18.2",
    "cors": "^2.8.5",
    "yahoo-finance2": "^2.11.3",
    "dotenv": "^16.4.5"
  }
}
```

**Install**:
```bash
cd market-mcp-server
npm install
```

### Step 1.3: Test Locally

**Run Server**:
```bash
cd market-mcp-server
PORT=3000 node index.js
```

**Test Health Endpoint**:
```bash
# In another terminal
curl http://localhost:3000/health
```

**Expected Response**:
```json
{"status":"healthy","timestamp":"2025-10-08T19:00:00.000Z"}
```

**Test SSE Endpoint**:
```bash
curl http://localhost:3000/sse
```

**Expected**: Connection stays open (SSE stream)

**If Successful**: ✅ Move to deployment
**If Errors**: See [Troubleshooting - MCP Server](#troubleshooting-mcp-server)

### Step 1.4: Deploy to Fly.io

**Initialize Fly App** (first time only):
```bash
cd market-mcp-server
fly launch --name market-mcp
```

**Questions**:
- Would you like to copy configuration? → **Yes**
- Choose region → **Select closest to you**
- Would you like to set up PostgreSQL? → **No**
- Would you like to set up Redis? → **No**
- Would you like to deploy now? → **No** (we'll configure first)

**Create `fly.toml`** (if not auto-generated):
```toml
app = "market-mcp"
primary_region = "sea"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"
  NODE_ENV = "production"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[services]]
  protocol = "tcp"
  internal_port = 8080

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["http", "tls"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20
```

**Deploy**:
```bash
fly deploy
```

**Expected Output**:
```
==> Building image
==> Deploying market-mcp
--> v1 deployed successfully
```

**Get URL**:
```bash
fly status
```

**Expected URL**: `https://market-mcp.fly.dev`

### Step 1.5: Verify Deployment

**Test Health**:
```bash
curl https://market-mcp.fly.dev/health
```

**Expected**:
```json
{"status":"healthy","timestamp":"2025-10-08T19:05:00.000Z"}
```

**Test SSE**:
```bash
curl https://market-mcp.fly.dev/sse
```

**Expected**: Connection opens (SSE stream)

**If Successful**: ✅ Phase 1 Complete!
**Time Checkpoint**: Should take ~1-2 hours

---

## Phase 2: Agent Builder Workflow (2-3 hours)

### Overview
Build the 7-node workflow in OpenAI Agent Builder using the visual interface.

**Who Does This**: Anyone (non-technical friendly!)
**Result**: Published workflow with Workflow ID

### Step 2.1: Access Agent Builder

**Navigate**:
1. Open browser → `https://platform.openai.com`
2. Log in to OpenAI account
3. Click **"Agent Builder"** in left sidebar (or navigate to agents section)

**Expected**: Visual canvas with node library on left

### Step 2.2: Create New Workflow

**Click**: "Create" or "+ New Workflow" button

**Settings**:
```
Workflow Name: G'sves Market Assistant
Description: Voice-enabled trading assistant with real-time market data
```

**Expected**: Blank canvas with Start node

### Step 2.3: Add Node 1 - Classification Agent

**Drag**: "Agent" from left sidebar → Drop on canvas

**Configure** (click node, right panel opens):

**Name**:
```
Intent Classifier
```

**Model**:
```
gpt-4o
```

**Instructions** (copy-paste from EXACT_AGENT_BUILDER_CONFIGURATION.md:92-116):
```
You are a classification agent for a trading assistant.

Your job: Analyze the user's message and return ONLY ONE of these categories:

Categories:
1. "market_data" - User wants stock prices, market news, company info, sector data
   Examples: "What's Tesla's price?", "Show me Apple news", "How's the tech sector?"

2. "chart_command" - User wants to display/change charts
   Examples: "Show me Tesla chart", "Display Apple", "Switch to NVDA"

3. "general_chat" - Greetings, help, general conversation
   Examples: "Hello", "Thanks", "What can you do?"

Response Format:
Return ONLY the category name, nothing else.
No explanations, no extra text.

Examples:
User: "What's TSLA price?" → market_data
User: "Show me chart" → chart_command
User: "Hello" → general_chat
```

**Input Variable**:
```
user_message
```

**Output Variable**:
```
classification_result
```

**Save**: Click outside node or "Save" button

### Step 2.4: Add Node 2 - Route by Intent

**Drag**: "Condition" from left sidebar → Drop below Node 1

**Configure**:

**Name**:
```
Route by Intent
```

**Condition**:
```
{{classification_result}} == "market_data"
```

**Expected**: Node shows "If" and "Else" outputs

### Step 2.5: Add Node 3 - MCP Market Data

**Drag**: "MCP" from left sidebar → Drop to right of Node 2

**Configure**:

**Name**:
```
Market Data MCP
```

**Click**: "+ Add" button (top right of MCP panel)

**Dialog Opens** - "Connect to MCP Server":

**Fill In**:
```
URL: https://market-mcp.fly.dev
Label: Market Data
Description: Real-time stock quotes, news, and market data
Authentication: None (or select if you added auth)
```

**Click**: "Connect"

**Expected**:
- Connection test runs
- "35 tools discovered" message
- List of tools appears (get_stock_quote, get_stock_news, etc.)

**Select Tools** (check these):
- ✅ get_stock_quote
- ✅ get_stock_history
- ✅ get_stock_news
- ✅ get_market_overview
- ✅ search_symbol
- ✅ (select any others you want available)

**Instructions**:
```
You have access to real-time market data tools.

Use the appropriate tool based on what the user asked:
- Stock price/quote: get_stock_quote
- Price history: get_stock_history
- News: get_stock_news
- Market overview: get_market_overview

Extract the stock symbol from the user's message.
Call the appropriate tool.
Return the data in a clear, formatted way.
```

**Input Variable**:
```
user_message
```

**Output Variable**:
```
market_data
```

**Save**

### Step 2.6: Add Node 4 - Chart or Chat Router

**Drag**: "Condition" → Drop to right of Node 2 (Else branch)

**Configure**:

**Name**:
```
Chart or Chat
```

**Condition**:
```
{{classification_result}} == "chart_command"
```

### Step 2.7: Add Node 5 - Chart Handler

**Drag**: "Agent" → Drop connected to Node 4 "If" output

**Configure**:

**Name**:
```
Chart Handler
```

**Model**:
```
gpt-4o
```

**Instructions**:
```
You handle chart display commands.

Extract the stock symbol from the user's message.

Return EXACTLY this format:
{
  "action": "display_chart",
  "symbol": "SYMBOL_HERE"
}

Examples:
User: "Show me Tesla chart" → {"action": "display_chart", "symbol": "TSLA"}
User: "Display Apple" → {"action": "display_chart", "symbol": "AAPL"}
```

**Input Variable**:
```
user_message
```

**Output Variable**:
```
chart_command
```

**Save**

### Step 2.8: Add Node 6 - Chat Handler

**Drag**: "Agent" → Drop connected to Node 4 "Else" output

**Configure**:

**Name**:
```
General Chat Handler
```

**Model**:
```
gpt-4o
```

**Instructions**:
```
You are G'sves, a friendly trading assistant.

Handle general conversation:
- Greetings: Be warm and welcoming
- Help requests: Explain what you can do
- Thanks: Acknowledge graciously

Keep responses brief and friendly.

Capabilities you can mention:
- Real-time stock prices and quotes
- Market news and analysis
- Interactive price charts
- Voice interaction

Do NOT make up stock prices or market data.
```

**Input Variable**:
```
user_message
```

**Output Variable**:
```
chat_response
```

**Save**

### Step 2.9: Add Node 7 - G'sves Response Agent

**Drag**: "Agent" → Drop below all paths (will connect multiple inputs)

**Configure**:

**Name**:
```
G'sves Response Formatter
```

**Model**:
```
gpt-4o
```

**Instructions**:
```
You are the final response formatter for G'sves trading assistant.

You receive data from different sources:
- market_data: Real-time market information
- chart_command: Chart display instructions
- chat_response: General conversation

Your job: Format the response for voice and text output.

Guidelines:
- Keep voice responses concise (2-3 sentences max)
- Include key numbers clearly
- Be professional but friendly
- No jargon unless user used it first

Format:
{
  "text": "Response for display",
  "voice": "Spoken response (brief)",
  "data": {original data if applicable}
}
```

**Input Variables**:
```
market_data
chart_command
chat_response
```

**Output Variable**:
```
final_response
```

**Save**

### Step 2.10: Wire All Connections

**This is CRITICAL** - every node must be connected!

**Connections to Make**:

1. **Start → Node 1** (Classification Agent)
   - Drag from Start output → Node 1 input

2. **Node 1 → Node 2** (Classification → Router)
   - Drag from Node 1 output → Node 2 input

3. **Node 2 "If" → Node 3** (Market Data path)
   - Drag from Node 2 "If/True" output → Node 3 input

4. **Node 2 "Else" → Node 4** (Other queries path)
   - Drag from Node 2 "Else/False" output → Node 4 input

5. **Node 4 "If" → Node 5** (Chart command path)
   - Drag from Node 4 "If/True" output → Node 5 input

6. **Node 4 "Else" → Node 6** (General chat path)
   - Drag from Node 4 "Else/False" output → Node 6 input

7. **Node 3 → Node 7** (Market data to formatter)
   - Drag from Node 3 output → Node 7 input

8. **Node 5 → Node 7** (Chart command to formatter)
   - Drag from Node 5 output → Node 7 input

9. **Node 6 → Node 7** (Chat response to formatter)
   - Drag from Node 6 output → Node 7 input

10. **Node 7 → End**
    - Drag from Node 7 output → End node

**Visual Check**:
```
Start
  ↓
[1] Classification
  ↓
[2] Route by Intent
  ├─ If (market_data) → [3] MCP ────────┐
  │                                      │
  └─ Else → [4] Chart or Chat           │
             ├─ If → [5] Chart Handler ──┤
             │                           │
             └─ Else → [6] Chat Handler ─┤
                                         ↓
                              [7] G'sves Response
                                         ↓
                                       End
```

**Verify**:
- [ ] No floating/unconnected nodes
- [ ] Both If/Else branches connected
- [ ] All paths lead to Node 7
- [ ] Node 7 leads to End

**If Error "add missing elements/nodes"**: See FIX_YOUR_WORKFLOW_NOW.md

### Step 2.11: Test in Preview Mode

**Click**: "Preview" button (top right)

**Test Case 1: Market Data Query**
```
Type: "What's Tesla's price?"

Expected Flow:
  Start → Classification → "market_data"
       → MCP Node (calls get_stock_quote)
       → G'sves Response → Output

Expected Output:
  "Tesla (TSLA) is currently trading at $XXX.XX, up/down X%"
```

**Test Case 2: Chart Command**
```
Type: "Show me Apple chart"

Expected Flow:
  Start → Classification → "chart_command"
       → Chart Handler
       → G'sves Response → Output

Expected Output:
  {"action": "display_chart", "symbol": "AAPL"}
```

**Test Case 3: General Chat**
```
Type: "Hello"

Expected Flow:
  Start → Classification → "general_chat"
       → Chat Handler
       → G'sves Response → Output

Expected Output:
  "Hello! I'm G'sves, your trading assistant..."
```

**View Tool Call Logs**:
- Click "View tool call logs" in preview
- Verify MCP tools are being called correctly
- Check for any errors

**If Tests Pass**: ✅ Ready to publish
**If Tests Fail**: See [Troubleshooting - Workflow](#troubleshooting-workflow)

### Step 2.12: Publish Workflow

**Click**: "Publish" button (top right)

**Dialog Opens**:

**Name**:
```
G'sves Market Assistant v1
```

**Description**:
```
Voice-enabled trading assistant with real-time market data via MCP
```

**Click**: "Publish"

**Expected**: Success message with Workflow ID

**CRITICAL - SAVE THIS**:
```
Workflow ID: wf_xxxxxxxxxxxxxxxxxxxxx
Version: v1
Published: [timestamp]
```

**Write Down Workflow ID**: You need this for backend integration!

**If Successful**: ✅ Phase 2 Complete!
**Time Checkpoint**: Should take ~2-3 hours

---

## Phase 3: Backend Integration (1 hour)

### Overview
Connect your backend to use the new Agent Builder workflow instead of direct Responses API.

**Who Does This**: Backend developer
**Result**: Backend calls Agent Builder workflow for voice queries

### Step 3.1: Update Backend Environment Variables

**Location**: `backend/.env` or Fly.io secrets

**Add**:
```bash
# Agent Builder Configuration
AGENT_BUILDER_WORKFLOW_ID=wf_xxxxxxxxxxxxxxxxxxxxx  # From Step 2.12
USE_AGENT_BUILDER=true

# Keep existing
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...
# ... other vars
```

**If using Fly.io**:
```bash
fly secrets set AGENT_BUILDER_WORKFLOW_ID=wf_xxxxxxxxxxxxxxxxxxxxx
fly secrets set USE_AGENT_BUILDER=true
```

### Step 3.2: Update Agent Orchestrator

**Location**: `backend/services/agent_orchestrator.py`

**Find** (around line 4295):
```python
async def process_with_gvses_assistant(self, messages):
    response = await self.client.responses.create(
        model="gpt-4o",
        assistant_id=self.gvses_assistant_id,
        messages=messages,
        tools=tools,
        store=True
    )
    return response
```

**Replace With**:
```python
async def process_with_gvses_assistant(self, messages):
    # Check if Agent Builder workflow should be used
    use_agent_builder = os.getenv('USE_AGENT_BUILDER', 'false').lower() == 'true'
    workflow_id = os.getenv('AGENT_BUILDER_WORKFLOW_ID')

    if use_agent_builder and workflow_id:
        # Use Agent Builder workflow
        return await self._call_agent_builder_workflow(messages, workflow_id)
    else:
        # Fallback to Responses API (current method)
        response = await self.client.responses.create(
            model="gpt-4o",
            assistant_id=self.gvses_assistant_id,
            messages=messages,
            tools=tools,
            store=True
        )
        return response

async def _call_agent_builder_workflow(self, messages, workflow_id):
    """Call Agent Builder workflow via API"""
    import httpx

    # Extract latest user message
    user_message = messages[-1].get('content', '') if messages else ''

    # Call Agent Builder API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'https://api.openai.com/v1/workflows/{workflow_id}/execute',
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'input': {
                    'user_message': user_message
                }
            },
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        # Transform to match expected response format
        return {
            'output': result.get('output', {}),
            'workflow_id': workflow_id,
            'execution_id': result.get('id')
        }
```

**Import** (add at top if not present):
```python
import os
import httpx
```

### Step 3.3: Update Response Handling

**Location**: Same file, around line where responses are processed

**Find**:
```python
# Process response content
content = response.get('content', '')
```

**Update**:
```python
# Process response content (handle both Responses API and Agent Builder)
if 'output' in response:
    # Agent Builder workflow response
    content = response['output'].get('final_response', {})
    if isinstance(content, dict):
        # Extract text from formatted response
        content = content.get('text', str(content))
else:
    # Responses API response
    content = response.get('content', '')
```

### Step 3.4: Test Backend Locally

**Start Backend**:
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

**Test Health**:
```bash
curl http://localhost:8000/health
```

**Expected**:
```json
{
  "status": "healthy",
  "agent_builder_enabled": true,
  "workflow_id": "wf_xxxxx..."
}
```

**Test Voice Endpoint**:
```bash
curl http://localhost:8000/elevenlabs/signed-url
```

**Expected**: Returns signed URL for ElevenLabs WebSocket

### Step 3.5: Test with Voice Client

**Option A: Use Test Script**

**Create** `test_agent_builder_integration.py`:
```python
#!/usr/bin/env python3
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_integration():
    from backend.services.agent_orchestrator import AgentOrchestrator

    orchestrator = AgentOrchestrator()

    # Test queries
    test_messages = [
        [{"role": "user", "content": "What's Tesla's price?"}],
        [{"role": "user", "content": "Show me Apple chart"}],
        [{"role": "user", "content": "Hello"}]
    ]

    for messages in test_messages:
        print(f"\n{'='*60}")
        print(f"Query: {messages[0]['content']}")
        print(f"{'='*60}")

        response = await orchestrator.process_with_gvses_assistant(messages)
        print(f"Response: {response}")

if __name__ == "__main__":
    asyncio.run(test_integration())
```

**Run**:
```bash
cd backend
python test_agent_builder_integration.py
```

**Expected**:
- Query 1: Real Tesla price data
- Query 2: Chart command JSON
- Query 3: Greeting response

**Option B: Use Frontend**

**Start Frontend**:
```bash
cd frontend
npm run dev
```

**Open**: `http://localhost:5174`

**Click**: Voice assistant button (microphone icon)

**Say**: "What's Tesla's price?"

**Expected**:
- Voice recognition works
- Backend calls Agent Builder workflow
- MCP server returns real data
- Voice response speaks price

**If Successful**: ✅ Phase 3 Complete!
**Time Checkpoint**: Should take ~1 hour

---

## Phase 4: Testing & Validation (1-2 hours)

### Overview
Comprehensive testing to ensure everything works end-to-end.

**Who Does This**: QA team or developer
**Result**: Verified production-ready system

### Step 4.1: Functional Testing

**Test Matrix**:

| Test Case | Input | Expected Output | Status |
|-----------|-------|-----------------|--------|
| **Market Data - Single Stock** | "What's Tesla's price?" | Real TSLA quote | [ ] |
| **Market Data - News** | "Show me Apple news" | Latest AAPL news | [ ] |
| **Market Data - History** | "Get Tesla's 30-day history" | Historical data | [ ] |
| **Chart Command** | "Show me NVDA chart" | Chart display command | [ ] |
| **General Chat** | "Hello" | Greeting response | [ ] |
| **General Chat** | "What can you do?" | Capabilities list | [ ] |
| **Invalid Symbol** | "What's price of XYZABC?" | Error/not found | [ ] |
| **Multiple Stocks** | "Compare TSLA and AAPL" | Both stocks data | [ ] |

**How to Test Each**:

1. **Voice Testing**:
   - Open frontend
   - Click voice button
   - Speak test query
   - Verify audio response
   - Check visual feedback

2. **API Testing**:
   ```bash
   curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"message": "What'\''s Tesla'\''s price?"}'
   ```

3. **Workflow Testing**:
   - Open Agent Builder
   - Click "Preview"
   - Type test query
   - Check tool call logs

**Pass Criteria**: 8/8 tests passing

### Step 4.2: Performance Testing

**Metrics to Measure**:

```bash
# Test script
#!/bin/bash
echo "Testing response times..."

for i in {1..10}; do
  echo "Test $i:"
  time curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"message": "What is Tesla price?"}' \
    -s > /dev/null
done
```

**Target Metrics**:
- [ ] **Average Response Time**: < 3 seconds
- [ ] **MCP Call Time**: < 500ms
- [ ] **Agent Builder Execution**: < 2 seconds
- [ ] **Voice End-to-End**: < 5 seconds

**If Slower**:
- Check MCP server response time
- Verify Agent Builder workflow efficiency
- Check network latency

### Step 4.3: Error Handling Testing

**Scenarios to Test**:

**1. MCP Server Down**:
```bash
# Stop MCP server
fly apps stop market-mcp

# Test query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Tesla price?"}'

# Expected: Graceful error message
# "Unable to fetch market data at this time"
```

**2. Invalid Workflow ID**:
```bash
# Temporarily set wrong workflow ID
fly secrets set AGENT_BUILDER_WORKFLOW_ID=wf_invalid

# Test query

# Expected: Fallback to Responses API or clear error
```

**3. Rate Limiting**:
```bash
# Send 100 rapid requests
for i in {1..100}; do
  curl -X POST http://localhost:8000/ask \
    -H "Content-Type: application/json" \
    -d '{"message": "Test '$i'"}' &
done

# Expected: Graceful handling, no crashes
```

**Pass Criteria**: All error scenarios handled gracefully

### Step 4.4: Voice Quality Testing

**Manual Tests**:

**1. Clarity**:
- [ ] Numbers spoken clearly (prices)
- [ ] Company names pronounced correctly
- [ ] Percentages clear ("up 2.5 percent")

**2. Response Structure**:
- [ ] Concise (2-3 sentences for voice)
- [ ] Complete information
- [ ] Natural phrasing

**3. Edge Cases**:
- [ ] Very long company names
- [ ] Negative numbers/losses
- [ ] Zero/null values

**Record Results** in testing spreadsheet

### Step 4.5: Integration Testing

**Full User Journey**:

```
1. User opens app
2. Sees default watchlist (TSLA, AAPL, NVDA, SPY, PLTR)
3. Clicks voice button
4. Says: "What's Tesla's price?"
5. Hears: "Tesla is trading at $XXX, up/down X percent"
6. Visual shows: Price card updates
7. Says: "Show me the chart"
8. Sees: Chart switches to TSLA
9. Says: "What's the latest news?"
10. Sees: News panel expands with TSLA articles
```

**Pass Criteria**: Complete journey works smoothly

**If Successful**: ✅ Phase 4 Complete!
**Time Checkpoint**: Should take ~1-2 hours

---

## Phase 5: Production Deployment (30-60 min)

### Overview
Deploy everything to production.

**Who Does This**: DevOps/Backend developer
**Result**: Live production system

### Step 5.1: Pre-Deployment Checklist

- [ ] All tests passing (Phase 4)
- [ ] MCP server deployed to Fly.io
- [ ] Agent Builder workflow published
- [ ] Environment variables configured
- [ ] Database migrations (if any)
- [ ] Backup current production

### Step 5.2: Deploy Backend

**Update Production Environment**:
```bash
# Set production secrets
fly secrets set \
  AGENT_BUILDER_WORKFLOW_ID=wf_xxxxxxxxxxxxxxxxxxxxx \
  USE_AGENT_BUILDER=true \
  --app gvses-market-insights
```

**Deploy**:
```bash
cd backend
fly deploy --app gvses-market-insights
```

**Monitor Deployment**:
```bash
fly logs --app gvses-market-insights
```

**Expected**:
```
[info] Starting deployment
[info] Building image
[info] Deploying v123
[info] Deployment successful
```

### Step 5.3: Verify Production Health

**Test Backend**:
```bash
curl https://gvses-market-insights.fly.dev/health
```

**Expected**:
```json
{
  "status": "healthy",
  "agent_builder_enabled": true,
  "workflow_id": "wf_xxxxx...",
  "mcp_server": "https://market-mcp.fly.dev"
}
```

**Test MCP Server**:
```bash
curl https://market-mcp.fly.dev/health
```

**Expected**:
```json
{"status":"healthy","timestamp":"..."}
```

### Step 5.4: Deploy Frontend

**Build Production Bundle**:
```bash
cd frontend
npm run build
```

**Deploy** (method depends on your hosting):

**Option A: Fly.io**:
```bash
fly deploy --app gvses-frontend
```

**Option B: Vercel/Netlify**:
```bash
# Vercel
vercel --prod

# Netlify
netlify deploy --prod
```

### Step 5.5: Smoke Test Production

**Open Production URL**: `https://your-production-url.com`

**Quick Tests**:
1. [ ] Page loads
2. [ ] Voice button appears
3. [ ] Click voice button → "What's Tesla's price?" → Hear response
4. [ ] Chart displays correctly
5. [ ] News panel loads

**If All Pass**: ✅ Phase 5 Complete! 🎉

### Step 5.6: Monitor Initial Traffic

**Watch Logs**:
```bash
# Backend logs
fly logs --app gvses-market-insights

# MCP server logs
fly logs --app market-mcp
```

**Monitor for**:
- Error rates
- Response times
- MCP call failures
- User feedback

**Set Up Alerts** (if not already):
```bash
# Example: Sentry, LogRocket, or similar
```

**If Successful**: ✅ Production Deployed!
**Time Checkpoint**: Should take ~30-60 minutes

---

## Phase 6: Enhancement - Vector Store (OPTIONAL)

### Overview
Add knowledge base capabilities for context-aware responses.

**When to Do**: After Phase 5 is stable (1-2 weeks in production)
**Who Does This**: Product team + developer
**Result**: AI responses backed by research documents

### Step 6.1: Prepare Documents

**Gather Content**:
- [ ] Market research reports (PDF)
- [ ] Technical analysis guides (PDF/Word)
- [ ] Trading pattern descriptions (PDF/Word)
- [ ] Historical market commentary (PDF)
- [ ] Educational content (PDF/Word/Excel)

**Format Requirements**:
- PDF: ✅ Supported
- Word (.docx): ✅ Supported
- Excel (.xlsx): ✅ Supported
- Total size: Aim for < 100MB total

**Organize**:
```
market-knowledge/
├── research-reports/
│   ├── tech-sector-analysis-2025.pdf
│   ├── market-trends-q1.pdf
│   └── ...
├── trading-patterns/
│   ├── head-shoulders-pattern.pdf
│   ├── moving-averages-guide.pdf
│   └── ...
└── company-profiles/
    ├── tesla-analysis.pdf
    ├── apple-fundamentals.pdf
    └── ...
```

### Step 6.2: Add Vector Store Node to Workflow

**Open**: Agent Builder → Your workflow (edit mode)

**Add Node**:
1. **Drag**: "Vector Store" from left sidebar
2. **Drop**: Between Classification and MCP nodes
3. **Name**: `Market Knowledge Base`

**Configure**:
```
Node Type: Vector Store
Name: Market Knowledge Base
Description: Historical market analysis and research documents
```

**Upload Documents**:
1. Click Vector Store node
2. Properties panel → "Upload Documents"
3. Select files from `market-knowledge/` folder
4. Upload (may take 5-10 minutes for vectorization)
5. Verify: "35 documents uploaded, 1.2M tokens"

### Step 6.3: Connect to Agents

**Modify Node 5 (Chart Handler)**:

**Add to Instructions**:
```
Before responding, you can query the Market Knowledge Base for relevant information.

If user asks about patterns, strategies, or analysis:
1. Query Vector Store with user's question
2. Use retrieved context in your response
3. Cite sources when available
```

**Connect**:
- Drag from Vector Store output → Chart Handler input

**Repeat** for:
- Node 6 (Chat Handler)
- Node 7 (G'sves Response)

### Step 6.4: Test Vector Store

**Test Query**:
```
"What's a head and shoulders pattern?"
```

**Expected Flow**:
```
Classification → "general_chat"
  → Chat Handler queries Vector Store
  → Retrieves pattern documentation
  → Response includes detailed explanation
```

**Verify**: Response includes information from uploaded PDFs

**If Successful**: ✅ Vector Store Enhanced!

**See**: VECTOR_STORE_AND_LOOP_NODES_GUIDE.md for complete details

---

## Phase 7: Enhancement - Loop Node (OPTIONAL)

### Overview
Add batch processing for multi-stock analysis.

**When to Do**: After Vector Store is working
**Who Does This**: Developer
**Result**: Watchlist analysis and multi-stock queries

### Step 7.1: Add Loop Node to Workflow

**Open**: Agent Builder → Your workflow

**Add Node**:
1. **Drag**: "Loop" from left sidebar
2. **Drop**: After Classification, before MCP
3. **Name**: `Multi-Stock Processor`

**Configure**:
```
Node Type: Loop
Loop Type: ForEach
Input Variable: {{stock_symbols}}
Iterator: {{current_symbol}}
```

### Step 7.2: Modify Classification for Multi-Stock Detection

**Update Node 1 Instructions**:

**Add Category**:
```
4. "multi_stock" - User wants information about multiple stocks
   Examples: "Compare TSLA and AAPL", "Analyze my watchlist", "Show me tech stocks"
```

**Update Node 2 (Router)**:

**Add Condition Branch**:
```
If {{classification_result}} == "multi_stock"
  → Loop Node
```

### Step 7.3: Configure Loop Body

**Inside Loop**:
1. **MCP Call**: Get quote for {{current_symbol}}
2. **Vector Store**: Query historical context for {{current_symbol}}
3. **Agent**: Analyze current + historical
4. **Store**: Add to {{results_array}}

**Loop Output**:
```
{{all_stock_analysis}}
```

### Step 7.4: Add Aggregation Agent

**After Loop**:

**New Node**: "Results Aggregator"
```
Node Type: Agent
Name: Multi-Stock Aggregator

Instructions:
You receive analysis for multiple stocks.

Synthesize into:
1. Overall market sentiment
2. Best/worst performers
3. Comparison highlights
4. Recommendations

Format for voice: 2-3 sentence summary
Format for display: Detailed comparison table
```

### Step 7.5: Test Multi-Stock Query

**Test**:
```
"Compare Tesla, Apple, and Nvidia"
```

**Expected**:
```
Loop executes 3 times:
  1. TSLA analysis
  2. AAPL analysis
  3. NVDA analysis

Aggregator:
  "Here's a comparison of three tech leaders:
   Tesla is up 2.5%, Apple down 0.3%, Nvidia leading with 5.1% gain.
   Tech sector showing strength today."
```

**Verify**: All three stocks analyzed, comparison provided

**If Successful**: ✅ Loop Node Enhanced!

**See**: VECTOR_STORE_AND_LOOP_NODES_GUIDE.md for complete details

---

## Troubleshooting Guide

### Troubleshooting: MCP Server

**Issue**: Health endpoint returns 404

**Solution**:
```bash
# Check server logs
fly logs --app market-mcp

# Verify app is running
fly status --app market-mcp

# Restart if needed
fly apps restart market-mcp
```

---

**Issue**: SSE endpoint not working

**Solution**:
```javascript
// Verify SSE transport in index.js
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';

// Check endpoint is registered
app.get('/sse', async (req, res) => {
  // ... SSE handler
});
```

---

**Issue**: "35 tools not discovered" in Agent Builder

**Solution**:
1. Test MCP server locally: `curl http://localhost:3000/sse`
2. Verify tools list: `node index.js` → check console output
3. Check CORS headers: `app.use(cors());`
4. Verify HTTPS: Agent Builder requires HTTPS (http:// won't work)

---

### Troubleshooting: Workflow

**Issue**: "add missing elements/nodes" error

**Solution**: See FIX_YOUR_WORKFLOW_NOW.md

Quick fix:
1. Check left sidebar "Nodes" tab
2. Verify all nodes are connected
3. Both If/Else branches must connect
4. Every node needs input (except Start) and output (except End)

---

**Issue**: Preview mode shows no output

**Solution**:
```
1. Click "View tool call logs"
2. Check for errors in tool calls
3. Verify MCP server is responding
4. Test with simple query: "Hello"
5. Check each node's output variable is set
```

---

**Issue**: Classification not routing correctly

**Solution**:
```
1. Check Node 1 (Classification) output variable: classification_result
2. Check Node 2 (Router) condition: {{classification_result}} == "market_data"
3. Test classification alone:
   - Preview mode
   - Type: "What's Tesla price?"
   - Check Node 1 output shows "market_data"
```

---

### Troubleshooting: Backend Integration

**Issue**: Backend not calling Agent Builder workflow

**Solution**:
```bash
# Check environment variable
fly secrets list --app gvses-market-insights

# Should show:
# USE_AGENT_BUILDER=true
# AGENT_BUILDER_WORKFLOW_ID=wf_xxxxx...

# If missing:
fly secrets set USE_AGENT_BUILDER=true --app gvses-market-insights
```

---

**Issue**: "Workflow not found" error

**Solution**:
```python
# Verify workflow ID is correct
workflow_id = os.getenv('AGENT_BUILDER_WORKFLOW_ID')
print(f"Using workflow: {workflow_id}")

# Test workflow directly in Agent Builder:
# 1. Open workflow in Agent Builder
# 2. Check ID in URL: /workflows/wf_xxxxx...
# 3. Update backend if different
```

---

**Issue**: Response format incorrect

**Solution**:
```python
# Check response transformation
if 'output' in response:
    # Agent Builder response
    content = response['output'].get('final_response', {})
else:
    # Responses API response (fallback)
    content = response.get('content', '')

# Add logging
print(f"Response structure: {response.keys()}")
print(f"Content: {content}")
```

---

### Troubleshooting: Voice

**Issue**: Voice not activating

**Solution**:
```javascript
// Frontend: Check microphone permissions
navigator.permissions.query({ name: 'microphone' })
  .then(result => console.log('Mic permission:', result.state));

// Browser console should show:
// Mic permission: granted

// If denied:
// 1. Browser settings → Site permissions → Microphone
// 2. Allow for your domain
// 3. Refresh page
```

---

**Issue**: Voice hears but doesn't respond

**Solution**:
```bash
# Check ElevenLabs signed URL
curl http://localhost:8000/elevenlabs/signed-url

# Should return:
# {"signed_url": "wss://..."}

# Verify ElevenLabs agent ID
echo $ELEVENLABS_AGENT_ID

# Test in ElevenLabs console directly
```

---

## Quick Reference

### Workflow IDs and URLs

```bash
# Production
Agent Builder Workflow: wf_xxxxxxxxxxxxxxxxxxxxx
MCP Server: https://market-mcp.fly.dev
Backend API: https://gvses-market-insights.fly.dev
Frontend: https://your-frontend-url.com

# Development
MCP Server: http://localhost:3000
Backend API: http://localhost:8000
Frontend: http://localhost:5174
```

### Key Commands

```bash
# MCP Server
cd market-mcp-server
npm install
PORT=3000 node index.js                    # Local
fly deploy --app market-mcp                # Production
fly logs --app market-mcp                  # View logs

# Backend
cd backend
uvicorn mcp_server:app --reload            # Local
fly deploy --app gvses-market-insights     # Production
fly logs --app gvses-market-insights       # View logs

# Frontend
cd frontend
npm run dev                                # Local
npm run build                              # Build
fly deploy --app gvses-frontend            # Production
```

### Testing Shortcuts

```bash
# Quick health check
curl https://market-mcp.fly.dev/health
curl https://gvses-market-insights.fly.dev/health

# Test market data
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Tesla price?"}'

# Test voice
curl http://localhost:8000/elevenlabs/signed-url
```

### Environment Variables Quick Reference

```bash
# Backend
OPENAI_API_KEY=sk-...
AGENT_BUILDER_WORKFLOW_ID=wf_xxxxx...
USE_AGENT_BUILDER=true
ELEVENLABS_API_KEY=...
ELEVENLABS_AGENT_ID=...

# Frontend
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
```

---

## Success Criteria Summary

### Phase 1 ✅
- [ ] MCP server responds at `/health`
- [ ] MCP server deployed to Fly.io
- [ ] SSE endpoint working

### Phase 2 ✅
- [ ] All 7 nodes configured
- [ ] All connections wired
- [ ] Preview tests pass (3/3)
- [ ] Workflow published with ID

### Phase 3 ✅
- [ ] Backend environment variables set
- [ ] Agent orchestrator updated
- [ ] Local tests pass

### Phase 4 ✅
- [ ] Functional tests: 8/8 passing
- [ ] Performance: < 3s average response
- [ ] Error handling: Graceful failures
- [ ] Voice quality: Clear and accurate

### Phase 5 ✅
- [ ] Production deployed
- [ ] Health checks passing
- [ ] Smoke tests passing
- [ ] Monitoring active

---

**Document Version**: 1.0
**Created**: October 8, 2025
**Estimated Total Time**: 6-8 hours (can be split across multiple sessions)
**Difficulty**: Moderate (Phase 2 is non-technical friendly!)
**Support**: See individual guides for detailed troubleshooting

**Related Documentation**:
- EXACT_AGENT_BUILDER_CONFIGURATION.md - Detailed node configs
- NON_TECHNICAL_IMPLEMENTATION_GUIDE.md - UI-focused guide
- VECTOR_STORE_AND_LOOP_NODES_GUIDE.md - Phase 6 & 7 details
- FIX_YOUR_WORKFLOW_NOW.md - Connection troubleshooting
- COMPLETE_NODE_TYPES_LIST.md - All available nodes
