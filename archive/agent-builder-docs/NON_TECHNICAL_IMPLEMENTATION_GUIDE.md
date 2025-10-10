# Non-Technical Implementation Guide
## G'sves AI Agent Builder Integration

**Created**: October 7, 2025
**For**: Non-technical assistants
**Goal**: Connect G'sves AI to OpenAI Agent Builder with market data tools
**Time Required**: 4-6 hours total

---

## 📖 Table of Contents

1. [What We're Building](#what-were-building)
2. [Before You Start](#before-you-start)
3. [Phase 1: Deploy the Market Data Server](#phase-1-deploy-the-market-data-server)
4. [Phase 2: Create the Agent Builder Workflow](#phase-2-create-the-agent-builder-workflow)
5. [Phase 3: Connect Everything Together](#phase-3-connect-everything-together)
6. [Phase 4: Test the System](#phase-4-test-the-system)
7. [Troubleshooting](#troubleshooting)
8. [Success Checklist](#success-checklist)

---

## 🎯 What We're Building

### The Big Picture

Imagine you're building a smart trading assistant that can:
- Answer questions about stocks using your voice
- Show charts when you ask
- Get real-time market data
- Remember conversations

**Current Setup (What you have now):**
```
You speak → ElevenLabs (voice AI) → Backend Server → Market Data → Voice response
```

**New Setup (What we're building):**
```
You speak → ElevenLabs (voice AI)
           ↓
    OpenAI Agent Builder (smart workflow)
           ↓
    Market Data Server (35+ tools)
           ↓
    Real market data from Yahoo Finance & CNBC
           ↓
    Voice response back to you
```

### Why This Is Better

| What | Before | After |
|------|--------|-------|
| **Making Changes** | Need a programmer to edit code | Change workflow visually, no code |
| **Seeing What Happens** | Check logs in terminal | See live visual diagram of what AI is doing |
| **Fixing Errors** | Hard to find where things broke | Click on failed step to see error |
| **Adding Features** | Write code, test, deploy | Drag and drop new nodes |
| **Understanding Flow** | Read code files | Look at flowchart |

---

## 🛠 Before You Start

### What You'll Need

**Accounts & Access:**
1. ✅ OpenAI account with Agent Builder access
2. ✅ Fly.io account (for hosting the market data server)
3. ✅ GitHub account (to access the code)
4. ✅ Access to the G'sves AI backend (already set up)

**Information You'll Need:**
- [ ] OpenAI API Key (from OpenAI dashboard)
- [ ] Current G'sves Assistant ID (ask developer: starts with `asst_`)
- [ ] ElevenLabs Agent ID (from ElevenLabs dashboard)
- [ ] Fly.io authentication token

**Browser/Tools:**
- Modern web browser (Chrome, Firefox, Safari)
- Notepad or text editor (to save IDs/URLs)
- This guide open in a tab

**Ask Your Developer For:**
1. **market-mcp-server folder** - The code for the market data tools
2. **Help with Fly.io deployment** - This part needs terminal access (30 minutes)
3. **OpenAI API key** - If you don't have one

### Key Concepts (Simple Explanations)

**MCP (Model Context Protocol):**
- Think of it like a phone book of tools
- Each "tool" is a function the AI can use (like "get stock price" or "get news")
- Agent Builder can "call" these tools when it needs information

**Agent Builder:**
- Visual flowchart editor for AI
- Drag boxes (called "nodes") onto a canvas
- Connect them with arrows to show flow
- Each node does one job

**Workflow:**
- The complete flowchart you build
- Has a start point (user question) and end point (AI response)
- Gets "published" when ready, which gives it an ID number

**Node Types (The Building Blocks):**
- **Agent Node**: AI that thinks and makes decisions
- **MCP Node**: Connects to your market data tools
- **Classification Node**: Figures out what the user wants
- **Condition Node**: If/then logic ("if user asks for price, do this")
- **Transform Node**: Changes data format
- **Set State Node**: Remembers information

---

## 🚀 Phase 1: Deploy the Market Data Server
**Time Required**: 1-2 hours (with developer help)
**Difficulty**: ⭐⭐⭐ (Need developer for this part)

### What This Does
Creates a server at `https://market-mcp.fly.dev` that Agent Builder can talk to. This server has 35+ market data tools.

### Step 1.1: Get the Code Ready

**Ask your developer to:**

1. Open the `market-mcp-server` folder
2. Update the `index.js` file to use "HTTP/SSE transport" instead of "stdio"
   - This means: change from local-only to internet-accessible
   - Reference: See `MCP_NODE_MIGRATION_GUIDE.md` for exact code changes

3. Test it locally first:
   ```
   cd market-mcp-server
   npm install
   npm run dev
   ```

**What Success Looks Like:**
- Terminal shows: `MCP Server running on port 8080`
- Browser can open: `http://localhost:8080/health`
- Health page shows: `{"status":"healthy","tools":35}`

### Step 1.2: Deploy to Fly.io

**Ask your developer to:**

1. Install Fly.io CLI tool (one-time setup)
2. Login to Fly.io: `fly auth login`
3. Create the app: `fly launch --name market-mcp`
4. Deploy: `fly deploy`

**Important Settings:**
- App name: `market-mcp` (or any name you choose)
- Region: Choose closest to your users
- Plan: Start with free tier

**What Success Looks Like:**
- Deployment shows: ✅ Deployed successfully
- You get a URL: `https://market-mcp.fly.dev`
- Opening URL in browser shows health check

### Step 1.3: Test the Deployed Server

**You Can Do This Part:**

1. Open browser
2. Go to: `https://market-mcp.fly.dev/health`
3. You should see:
   ```json
   {
     "status": "healthy",
     "server": "market-mcp-server",
     "version": "1.0.0",
     "tools": 35
   }
   ```

**Save This Information:**
```
✅ Server URL: https://market-mcp.fly.dev
✅ Status: Healthy
✅ Tools Available: 35
✅ Date Deployed: __________
```

### 🎯 Phase 1 Checklist
- [ ] Code updated with HTTP/SSE transport
- [ ] Server tested locally
- [ ] Deployed to Fly.io
- [ ] Health check accessible
- [ ] URL saved for next phase

---

## 🎨 Phase 2: Create the Agent Builder Workflow
**Time Required**: 1-2 hours
**Difficulty**: ⭐⭐ (You can do this!)

### What This Does
Creates a visual flowchart that decides what to do when users ask questions.

### Step 2.1: Access Agent Builder

1. Go to: https://platform.openai.com
2. Log in with your OpenAI account
3. Look for **"Agent Builder"** in the left sidebar
4. Click **"Create"** to start a new workflow

**What You'll See:**
- Empty canvas in the center
- Sidebar on the left with node types
- Properties panel on the right (empty until you select something)

### Step 2.2: Name Your Workflow

1. At the top, click the default name (probably "Untitled Workflow")
2. Type: **"G'sves Market Assistant"**
3. Press Enter to save

**Good Workflow Names:**
- G'sves Market Assistant
- Trading Voice Agent
- Market Data Workflow
- Stock Price Agent

### Step 2.3: Build the Workflow (Drag & Drop)

**Visual Map of What You're Building:**

```
                    [Start: User Question]
                             │
                             ▼
                   ┌──────────────────┐
                   │  Classification  │  ← Figures out what user wants
                   │     Agent        │
                   └────────┬─────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │   Condition      │  ← Decides which path to take
                   │   Node           │
                   └────┬─────────┬───┘
                        │         │
          ┌─────────────┘         └─────────────┐
          │                                      │
          ▼                                      ▼
   ┌─────────────┐                      ┌──────────────┐
   │  MCP Node   │                      │   G'sves     │
   │             │                      │   Agent      │
   │ Calls:      │                      │   Node       │
   │ - Stock     │                      │              │
   │   Price     │                      │  Formats     │
   │ - News      │                      │  Response    │
   │ - History   │                      └──────┬───────┘
   └─────┬───────┘                             │
         │                                     │
         └─────────────┬───────────────────────┘
                       ▼
              ┌────────────────┐
              │  Final Output  │  ← Returns to user
              └────────────────┘
```

**Detailed Steps:**

#### Node 1: Classification Agent

**Purpose**: Understands what the user is asking for

1. **Add the Node:**
   - In left sidebar, find **"Classification Agent"**
   - Drag it onto canvas
   - Drop it near the top

2. **Configure It:**
   - Click on the node
   - Properties panel opens on right
   - **Name**: Type "Intent Classifier"
   - **Instructions**: Type:
     ```
     Classify user questions into these categories:
     - "market_data" - Questions about stock prices, news, charts, market info
     - "chart_command" - Requests to show or change charts
     - "general_chat" - Greetings, thank you, general conversation

     Examples:
     "What's Tesla's price?" → market_data
     "Show me Apple chart" → chart_command
     "Hello" → general_chat
     ```
   - **Model**: Select `gpt-4o` (recommended)

3. **Set Input:**
   - Find "Input" field
   - Type: `{{user_message}}`
   - This means "use whatever the user typed"

**What This Does:**
Every question goes through here first. It decides: "Is this about market data? Chart command? Or just chat?"

---

#### Node 2: Condition Node

**Purpose**: Routes to the correct path based on classification

1. **Add the Node:**
   - Find **"Condition"** in left sidebar
   - Drag below Classification Agent
   - Connect them:
     - Click output dot on Classification Agent
     - Drag line to input dot on Condition Node

2. **Configure It:**
   - Click Condition Node
   - **Name**: Type "Route Query"
   - **Condition Logic**: Set up 3 branches:

   **Branch 1: Market Data Path**
   - If: `{{intent}} == "market_data"`
   - Then: Connect to MCP Node (we'll add this next)

   **Branch 2: Chart Command Path**
   - If: `{{intent}} == "chart_command"`
   - Then: Connect to G'sves Agent Node

   **Branch 3: General Chat Path**
   - If: `{{intent}} == "general_chat"`
   - Then: Connect directly to G'sves Agent Node

**What This Does:**
Like a traffic cop. Sends market questions to MCP tools, chart commands to G'sves agent directly.

---

#### Node 3: MCP Node (Market Data Tools)

**Purpose**: Connects to your market-mcp-server to get real data

1. **Add the Node:**
   - Find **"MCP"** in left sidebar
   - Drag to the right of Condition Node

2. **Connect to Your Server:**
   - Click the MCP node
   - Look for **"+ Add"** button (top right of properties panel)
   - Click it

3. **"Connect to MCP Server" Dialog Opens:**

   Fill in these fields:

   ```
   URL: https://market-mcp.fly.dev
   ↑ Use the URL from Phase 1

   Label: Market Data MCP
   ↑ Give it a friendly name

   Description: Real-time market data and analysis tools
   ↑ Optional, but helps you remember what it does

   Authentication: Access token / API key
   ↑ Select from dropdown

   🔑 Add your access token: [Leave blank if public]
   ↑ Only fill if your server requires authentication
   ```

4. **Click "Connect"**

   **What Happens:**
   - Agent Builder contacts `https://market-mcp.fly.dev`
   - Asks: "What tools do you have?"
   - Server responds with list of 35+ tools
   - Tools appear in dropdown below

5. **Select Tools to Enable:**

   Check these important ones:
   - ✅ `get_stock_quote` - Get current price
   - ✅ `get_stock_history` - Get price history for charts
   - ✅ `get_stock_news` - Get news articles
   - ✅ `search_stocks` - Find stocks by company name
   - ✅ `get_market_movers` - Biggest gainers/losers
   - ✅ `get_sector_performance` - Sector analysis

   (You can enable all 35 if you want - more tools = more AI capabilities)

6. **Configure Instructions:**
   - **Instructions for Tool Use**:
     ```
     When user asks about stocks or market data:
     1. Use get_stock_quote for current prices
     2. Use get_stock_history for chart data
     3. Use get_stock_news for recent news
     4. Use search_stocks if user provides company name instead of ticker

     Always include the data source in your response.
     Format numbers with commas and 2 decimal places.
     ```

7. **Connect to Workflow:**
   - Connect output from **Condition Node** (market_data branch)
   - Connect output from **MCP Node** to **G'sves Agent Node** (we'll add next)

**What This Does:**
When users ask about stocks, this node calls the appropriate tool from your server, gets real data, and passes it to the next step.

---

#### Node 4: G'sves Agent Node

**Purpose**: The personality of G'sves - formats responses in the right voice/style

1. **Add the Node:**
   - Find **"Agent"** in left sidebar
   - Drag below the MCP Node

2. **Configure It:**
   - Click on the node
   - **Name**: Type "G'sves Response Agent"
   - **Model**: Select `gpt-4o`
   - **Instructions**: Copy the G'sves personality from `backend/prompts/idealagent.md`

   **Shortened Version (You Can Customize):**
   ```
   You are G'sves, a professional trading mentor and market analyst.

   Your Role:
   - Provide clear, actionable market insights
   - Teach trading concepts with patience
   - Balance optimism with realistic risk awareness
   - Use conversational but professional tone

   Response Style:
   - Start with direct answer to the question
   - Add brief context or educational note
   - End with forward-looking insight or question
   - Keep responses under 3 sentences for voice

   Data Handling:
   - Always cite your source (e.g., "According to Yahoo Finance...")
   - Format prices clearly: "$245.32, up 2.3%"
   - Acknowledge data delays if applicable

   Personality:
   - Confident but humble
   - Educational without being condescending
   - Optimistic but realistic about risks
   - Uses occasional trading terminology but explains it
   ```

3. **Set Input:**
   - **Input Field**: `{{mcp_results}}` (if coming from MCP Node)
   - Or: `{{user_message}}` (if coming directly from Condition)

4. **Connect Inputs:**
   - From **MCP Node** output → This node input (for market data path)
   - From **Condition Node** (chart/chat paths) → This node input

**What This Does:**
Takes raw data from MCP tools, formats it in G'sves' voice, makes it natural for voice response.

---

### Step 2.4: Connect All the Nodes

**Visual Check - Your Canvas Should Look Like:**

```
[Classification Agent]
        │
        ▼
  [Condition Node]
    │  │    │
    │  │    └──────────────┐
    │  │                   │
    │  └─────────┐         │
    ▼            ▼         ▼
[MCP Node]  [G'sves]  [G'sves]
    │          ▲         ▲
    └──────────┘         │
                         │
            [Output to User]
```

**Connection Checklist:**
- [ ] Classification Agent → Condition Node
- [ ] Condition (market_data) → MCP Node
- [ ] Condition (chart_command) → G'sves Agent
- [ ] Condition (general_chat) → G'sves Agent
- [ ] MCP Node → G'sves Agent
- [ ] All paths lead to output

---

### Step 2.5: Test in Preview Mode

**Before Publishing, Test It:**

1. **Click "Preview" Button** (top right of screen)

2. **Test Modal Opens** - Type test questions:

   **Test 1: Market Data**
   - Type: "What's Tesla's stock price?"
   - Watch the flow:
     - Classification Agent lights up → identifies "market_data"
     - Condition Node routes to MCP branch
     - MCP Node calls `get_stock_quote`
     - G'sves Agent formats response
   - Expected response: "Tesla is currently trading at $245.32, up 2.3%..."

   **Test 2: Chart Command**
   - Type: "Show me Apple chart"
   - Should route directly to G'sves Agent
   - Expected: Chart command response

   **Test 3: General Chat**
   - Type: "Hello G'sves"
   - Should route to G'sves Agent
   - Expected: Friendly greeting

3. **Check Tool Call Logs:**
   - In preview, click **"View tool call logs"**
   - Verify MCP tools were called correctly
   - Check response times (should be under 2 seconds)

4. **Debug If Needed:**
   - If something fails, click **"Debug"** button
   - Agent Builder shows you where it broke
   - Fix that node and test again

**Common Preview Issues:**

| Issue | What It Means | How to Fix |
|-------|---------------|------------|
| "MCP connection failed" | Can't reach your server | Check Fly.io deployment, verify URL |
| "Tool not found" | Tool name mismatch | Check tool names in MCP node config |
| "No response" | Agent got stuck | Check that all nodes have instructions |
| "Timeout" | Taking too long | Optimize tool calls, check server speed |

---

### Step 2.6: Publish the Workflow

**Once Preview Works:**

1. **Click "Publish" Button** (top right)

2. **Publish Dialog Opens:**
   - **Workflow Name**: Confirm "G'sves Market Assistant"
   - **Description**: "Voice-enabled trading assistant with real-time market data"
   - **Version Notes**: "Initial release - MCP integration"

3. **Click "Publish"**

4. **You'll Receive:**
   ```
   Workflow ID: wf_abc123xyz
   Version: v1
   Published: [timestamp]
   Status: Active
   ```

**IMPORTANT - Save These:**
```
✅ Workflow ID: ___________________
✅ Version: v1
✅ Published Date: ___________________
✅ Test in Preview: Passed
```

You'll need the Workflow ID for Phase 3!

---

### 🎯 Phase 2 Checklist
- [ ] Agent Builder workflow created
- [ ] Classification Agent configured
- [ ] Condition Node routing set up
- [ ] MCP Node connected to market-mcp.fly.dev
- [ ] 35 tools discovered and enabled
- [ ] G'sves Agent Node configured
- [ ] All nodes connected properly
- [ ] Preview mode tested successfully
- [ ] Workflow published
- [ ] Workflow ID saved

---

## 🔗 Phase 3: Connect Everything Together
**Time Required**: 1 hour
**Difficulty**: ⭐⭐ (Some technical help recommended)

### What This Does
Connects your existing G'sves frontend to the new Agent Builder workflow.

### Step 3.1: Update Backend Configuration

**Ask Your Developer to Add:**

**File: `backend/.env`**
```bash
# Add these new lines:
OPENAI_API_KEY=sk-...                      # Your OpenAI API key
AGENT_BUILDER_WORKFLOW_ID=wf_abc123xyz     # From Phase 2
AGENT_BUILDER_VERSION=v1
```

### Step 3.2: Create Agent Builder Client

**Ask Your Developer to Create:**

**New File: `backend/services/agent_builder_client.py`**

This file will:
- Connect to OpenAI Agent Builder
- Call your published workflow
- Handle responses

**What It Does (Simple Explanation):**
Instead of the backend handling all the logic, it now asks your Agent Builder workflow "What should I do with this question?" and Agent Builder orchestrates everything.

### Step 3.3: Update API Endpoints

**Two Options:**

**Option A: Parallel System (Recommended)**

Keep both old and new systems running:
- Old endpoint: `/ask` → Uses current Responses API
- New endpoint: `/ask-builder` → Uses Agent Builder workflow

**Benefits:**
- Zero downtime
- Can test new system while old still works
- Easy to switch back if issues

**Option B: Full Replacement**

Replace `/ask` endpoint entirely with Agent Builder.

**Benefits:**
- Simpler architecture
- Single source of truth

**Recommendation**: Start with Option A, migrate to Option B after testing.

---

### Step 3.4: Connect ElevenLabs to Agent Builder

**This Part Connects Voice:**

1. **Go to ElevenLabs Dashboard**
   - https://elevenlabs.io
   - Log in to your account
   - Find your G'sves agent

2. **Update Agent Configuration:**

   **Add Custom Action:**
   - Click on your agent
   - Go to "Actions" tab
   - Click "Add Action"

   **Fill in:**
   ```
   Name: Query Agent Builder

   Type: Webhook

   URL: https://api.openai.com/v1/workflows/{workflow_id}/run
   ↑ Replace {workflow_id} with your actual ID from Phase 2

   Method: POST

   Headers:
     Authorization: Bearer {your_openai_api_key}
     Content-Type: application/json

   Body Template:
   {
     "input": {
       "user_message": "{{user_input}}"
     }
   }
   ```

3. **Test ElevenLabs Connection:**
   - In ElevenLabs dashboard, use "Test" feature
   - Speak: "What's Tesla's stock price?"
   - Should hear G'sves respond with real data

**What This Does:**
When you speak to G'sves through ElevenLabs, your voice is:
1. Converted to text by ElevenLabs
2. Sent to Agent Builder workflow
3. Workflow processes via MCP tools
4. Response sent back to ElevenLabs
5. Converted to speech
6. You hear G'sves' voice response

---

### Step 3.5: Update Frontend (Optional)

**If You Want a "Switch" Between Old/New:**

**Ask Your Developer to Add:**

In the frontend settings panel, add a toggle:
```
☐ Use Agent Builder (Beta)
```

When checked:
- Voice queries → Agent Builder workflow
- Text queries → Still use old system (or Agent Builder)

When unchecked:
- Everything uses old system

**What This Does:**
Lets you easily test the new system without breaking the old one.

---

### 🎯 Phase 3 Checklist
- [ ] Backend environment variables updated
- [ ] Agent Builder client created
- [ ] API endpoints configured (parallel or replacement)
- [ ] ElevenLabs connected to Agent Builder
- [ ] ElevenLabs test successful
- [ ] Frontend toggle added (optional)
- [ ] Developer confirmed all changes deployed

---

## ✅ Phase 4: Test the System
**Time Required**: 30-60 minutes
**Difficulty**: ⭐ (You can do this!)

### End-to-End Testing

**Test 1: Voice Query (Full Pipeline)**

1. **Open your G'sves AI app**
2. **Click the microphone button**
3. **Speak clearly:** "What is Tesla's stock price?"

**Expected Flow:**
```
Your voice
  → ElevenLabs (voice to text)
    → Agent Builder workflow receives text
      → Classification Agent: Identifies "market_data"
        → Condition Node: Routes to MCP Node
          → MCP Node: Calls get_stock_quote("TSLA")
            → market-mcp-server: Fetches from Yahoo Finance
              → Returns: { symbol: "TSLA", price: 245.32, change: +2.3% }
            → MCP Node: Sends data to G'sves Agent
          → G'sves Agent: Formats as "Tesla is trading at $245.32, up 2.3%"
        → Response to Agent Builder
      → Back to ElevenLabs
    → ElevenLabs (text to speech)
  → You hear G'sves' voice
```

**What Success Looks Like:**
- ✅ Response in under 5 seconds
- ✅ Accurate stock price
- ✅ Natural G'sves voice
- ✅ No errors or disconnections

---

**Test 2: Chart Command**

1. **Speak:** "Show me Apple stock chart"

**Expected:**
- Chart appears on screen
- Shows AAPL price history
- Candlestick chart visible
- Voice confirms: "Here's the Apple chart"

---

**Test 3: News Query**

1. **Speak:** "What's the latest news about Microsoft?"

**Expected:**
- MCP Node calls `get_stock_news("MSFT")`
- Returns 3-5 recent headlines
- G'sves summarizes key points
- Cites sources (CNBC, Yahoo Finance)

---

**Test 4: Multi-Tool Query**

1. **Speak:** "Compare Tesla and Apple stock performance"

**Expected:**
- MCP calls `get_stock_quote` twice (TSLA and AAPL)
- G'sves compares both
- Mentions which is performing better
- Provides percentage changes

---

**Test 5: Edge Cases**

**Test Invalid Symbol:**
- Speak: "Show me XYZ123 stock price"
- Expected: "I couldn't find that stock symbol. Can you verify?"

**Test Ambiguous Query:**
- Speak: "Tell me about Apple"
- Expected: Classification Agent asks if you mean AAPL stock or the company info

**Test Network Failure:**
- Disconnect internet briefly
- Try voice query
- Expected: Graceful error message

---

### Performance Benchmarks

**Measure These:**

| Metric | Target | How to Check |
|--------|--------|--------------|
| Voice Response Time | < 5 seconds | Speak → Hear response |
| MCP Tool Call | < 1 second | Check Agent Builder logs |
| Tool Accuracy | 100% | Verify stock prices on Yahoo Finance |
| Error Recovery | Graceful | Test with bad inputs |

**Record Your Results:**
```
Test 1: Voice Query Time: _____ seconds
Test 2: Chart Command Time: _____ seconds
Test 3: News Query Time: _____ seconds
Test 4: Multi-Tool Time: _____ seconds
Test 5: Error Handling: _____ (Pass/Fail)
```

---

### Debugging Tools

**If Something Doesn't Work:**

**1. Check Agent Builder Logs:**
- Go to Agent Builder
- Click "Logs" in left sidebar
- Find your recent workflow execution
- Click on it to see step-by-step
- Look for red X marks (errors)

**2. Check MCP Server Logs:**
- Go to Fly.io dashboard
- Click on "market-mcp" app
- Click "Logs" tab
- Look for error messages
- Common issues:
  - "Tool not found" → Check tool names match
  - "Timeout" → Server too slow, check API keys
  - "401 Unauthorized" → Check authentication

**3. Check ElevenLabs Logs:**
- Go to ElevenLabs dashboard
- Click your agent
- Go to "Activity" tab
- See recent conversations
- Check for webhook errors

**4. Check Frontend Console:**
- Open browser (Chrome recommended)
- Press F12 (opens developer tools)
- Click "Console" tab
- Look for red error messages
- Common issues:
  - "Network error" → Backend not reachable
  - "WebSocket failed" → ElevenLabs connection issue

---

### 🎯 Phase 4 Checklist
- [ ] Voice query works end-to-end
- [ ] Chart commands work
- [ ] News queries return results
- [ ] Multi-tool queries work
- [ ] Error handling is graceful
- [ ] Response times under 5 seconds
- [ ] All test cases passed
- [ ] Debugging tools accessible

---

## 🚨 Troubleshooting

### Common Issues and Solutions

#### Issue 1: "MCP Server Not Responding"

**Symptoms:**
- Agent Builder shows "Connection timeout"
- Workflow stuck at MCP Node
- No market data returned

**Diagnosis:**
1. Check server health: `https://market-mcp.fly.dev/health`
2. If 404 or no response → Server is down

**Solutions:**

**Step 1: Verify Deployment**
- Go to Fly.io dashboard
- Check "market-mcp" app status
- Should show: ✅ Running
- If not, ask developer to redeploy

**Step 2: Check URL in Agent Builder**
- Open workflow
- Click MCP Node
- Verify URL exactly: `https://market-mcp.fly.dev`
- No typos, no trailing slash

**Step 3: Test Authentication**
- In MCP Node properties
- Click "Test authentication"
- Should show: ✅ Connected

**Step 4: Restart Server**
- In Fly.io dashboard
- Click "Restart"
- Wait 30 seconds
- Test again

---

#### Issue 2: "Tools Not Discovered"

**Symptoms:**
- MCP Node shows 0 tools
- Or shows "Loading..." forever

**Diagnosis:**
Server is reachable but not responding with tool list

**Solutions:**

**Step 1: Check MCP Protocol Response**
Ask developer to test:
```bash
curl https://market-mcp.fly.dev/sse
```
Should return SSE stream

**Step 2: Verify Tool Definition**
Developer should check `index.js`:
- Tools array is populated
- Each tool has: name, description, parameters

**Step 3: Re-add Server**
- In Agent Builder, remove MCP server
- Add it again with "+ Add"
- Wait for full discovery (can take 30 seconds)

---

#### Issue 3: "Voice Response Too Slow"

**Symptoms:**
- Takes 10+ seconds to respond
- User hears long silence

**Diagnosis:**
Bottleneck somewhere in pipeline

**Solutions:**

**Step 1: Measure Each Part**
- ElevenLabs processing: Should be < 1 second
- Agent Builder workflow: Should be < 2 seconds
- MCP tool call: Should be < 1 second
- Response synthesis: Should be < 1 second

**Step 2: Check MCP Tool Performance**
In Agent Builder logs:
- Look for MCP tool call duration
- If > 3 seconds → Yahoo Finance might be slow
- Solution: Add caching to MCP server (ask developer)

**Step 3: Optimize Workflow**
- Reduce number of tools in parallel
- Use Transform node to filter data before sending to G'sves
- Simplify G'sves instructions (shorter responses)

**Step 4: Use Faster Tools First**
Order of preference:
1. Alpaca API (fastest, but needs API key)
2. Yahoo Finance (medium speed)
3. CNBC (slower for large datasets)

---

#### Issue 4: "Inaccurate or Old Data"

**Symptoms:**
- Stock prices don't match current market
- News articles are days old

**Diagnosis:**
Data source issue or caching problem

**Solutions:**

**Step 1: Verify Data Source**
- Check Yahoo Finance directly
- Compare timestamp in MCP response
- If delayed, it's the source's limitation

**Step 2: Check Caching**
Ask developer:
- Is MCP server caching responses?
- Cache should be < 1 minute for quotes
- Cache should be < 5 minutes for news

**Step 3: Add Data Freshness Check**
Update G'sves Agent instructions:
```
Always mention data freshness:
- "As of [timestamp], Tesla is..."
- "According to the latest update..."
```

---

#### Issue 5: "ElevenLabs Not Connecting to Agent Builder"

**Symptoms:**
- Voice query works but gives generic response
- Doesn't use real market data
- Falls back to old system

**Diagnosis:**
ElevenLabs webhook not configured properly

**Solutions:**

**Step 1: Check Webhook Configuration**
In ElevenLabs dashboard:
- Verify URL: `https://api.openai.com/v1/workflows/{id}/run`
- Workflow ID is correct
- Authorization header has valid API key

**Step 2: Test Webhook Directly**
Ask developer to use Postman or curl:
```bash
curl -X POST https://api.openai.com/v1/workflows/wf_abc123/run \
  -H "Authorization: Bearer sk-..." \
  -H "Content-Type: application/json" \
  -d '{"input":{"user_message":"test"}}'
```
Should return workflow response

**Step 3: Check ElevenLabs Logs**
- Go to Activity tab
- Click on recent conversation
- Look for webhook errors
- Common: 401 Unauthorized (bad API key)

---

#### Issue 6: "Agent Builder Shows Wrong Tool Response"

**Symptoms:**
- Asked for Tesla, got Apple data
- Tool returns error but workflow continues

**Diagnosis:**
Parameter mapping issue

**Solutions:**

**Step 1: Check Tool Call Logs**
In Agent Builder logs:
- Click on MCP Node step
- Verify parameters sent
- Example: Should see `{ symbol: "TSLA" }`
- If wrong symbol → Classification Agent extracted wrong ticker

**Step 2: Improve Classification Agent**
Add more examples to Classification Agent instructions:
```
User: "What's the price of Tesla?"
Extract: symbol = "TSLA"

User: "Tell me about AAPL"
Extract: symbol = "AAPL"

User: "Microsoft stock"
Extract: symbol = "MSFT"
```

**Step 3: Add Transform Node**
Between Classification and MCP:
- Validates symbol format
- Converts company names to tickers
- Handles edge cases

---

### Emergency Rollback Plan

**If Everything Breaks:**

**Step 1: Switch Back to Old System**
- In backend `.env`, comment out:
  ```bash
  # AGENT_BUILDER_WORKFLOW_ID=...
  ```
- Restart backend
- Old Responses API takes over

**Step 2: Disable ElevenLabs Webhook**
- Go to ElevenLabs dashboard
- Remove Agent Builder webhook
- System reverts to old voice handling

**Step 3: Keep MCP Server Running**
- Don't shut down Fly.io deployment
- You can reconnect when issues are fixed
- Historical data still accessible

**Step 4: Debug Offline**
- Use Agent Builder Preview mode
- Test workflow without affecting live users
- Fix issues incrementally
- Re-enable when ready

---

## 📋 Success Checklist

### Complete System Verification

**Infrastructure:**
- [ ] market-mcp-server deployed to Fly.io
- [ ] Health check accessible at URL
- [ ] 35 tools visible in server response
- [ ] Server uptime > 99% (check Fly.io metrics)

**Agent Builder:**
- [ ] Workflow published with ID
- [ ] All nodes configured correctly
- [ ] MCP server connected and verified
- [ ] Tools discovered automatically (35+)
- [ ] Preview mode passes all test cases
- [ ] Live workflow executing successfully

**Integration:**
- [ ] Backend connected to Agent Builder
- [ ] ElevenLabs webhook configured
- [ ] Voice queries reach Agent Builder
- [ ] MCP tools called correctly
- [ ] Responses formatted in G'sves voice

**Performance:**
- [ ] End-to-end response time < 5 seconds
- [ ] MCP tool calls < 1 second
- [ ] Voice quality maintained
- [ ] Error rate < 1%

**User Experience:**
- [ ] Voice commands work naturally
- [ ] Chart commands display correctly
- [ ] News queries return relevant results
- [ ] Error messages are user-friendly
- [ ] System feels responsive

**Monitoring:**
- [ ] Agent Builder logs accessible
- [ ] MCP server logs visible in Fly.io
- [ ] ElevenLabs activity tracking enabled
- [ ] Alert system configured for errors

---

## 📚 Reference Information

### Key URLs to Bookmark

```
Agent Builder:
https://platform.openai.com/agent-builder

Your Workflow:
https://platform.openai.com/agent-builder/workflows/{your_id}

MCP Server:
https://market-mcp.fly.dev

MCP Health Check:
https://market-mcp.fly.dev/health

ElevenLabs Dashboard:
https://elevenlabs.io/dashboard

Fly.io Dashboard:
https://fly.io/dashboard
```

### IDs and Credentials to Save

**IMPORTANT - Keep This Secure:**

```
OpenAI API Key: sk-...
Workflow ID: wf_...
Workflow Version: v1
ElevenLabs Agent ID: ...
Fly.io App Name: market-mcp
MCP Server URL: https://market-mcp.fly.dev
```

### Support Contacts

**When You Need Help:**

**Technical Issues:**
- Your developer (for code/deployment issues)
- OpenAI support (for Agent Builder)
- Fly.io support (for server issues)

**Questions About This Guide:**
- Refer to `MCP_NODE_MIGRATION_GUIDE.md` for code details
- See `AGENT_BUILDER_MCP_INTEGRATION_GUIDE.md` for technical context
- Check `COMPLETE_ARCHITECTURE_WIRING.md` for system architecture

---

## 🎓 Understanding the System (For Learning)

### What Happens When User Asks a Question?

**Example: "What's Tesla's stock price?"**

**Timeline:**

```
0.0s - User speaks into microphone
  ↓
0.1s - ElevenLabs receives audio
  ↓
0.3s - ElevenLabs converts speech to text: "What's Tesla's stock price?"
  ↓
0.4s - Text sent to Agent Builder workflow
  ↓
0.5s - Classification Agent analyzes text
       Identifies: intent = "market_data", symbol = "TSLA"
  ↓
0.7s - Condition Node routes to MCP branch
  ↓
0.8s - MCP Node prepares tool call
       Tool: get_stock_quote
       Parameter: { symbol: "TSLA" }
  ↓
1.0s - HTTPS POST to https://market-mcp.fly.dev/messages
  ↓
1.1s - market-mcp-server receives request
  ↓
1.2s - Server calls Yahoo Finance API
  ↓
1.5s - Yahoo Finance responds with data
  ↓
1.6s - Server formats MCP response
       Returns: { symbol: "TSLA", price: 245.32, change: +2.3%, ... }
  ↓
1.7s - MCP Node receives data
  ↓
1.8s - Data passed to G'sves Agent Node
  ↓
2.0s - G'sves Agent formats response:
       "Tesla is currently trading at $245.32, up 2.3% today"
  ↓
2.2s - Response sent back to Agent Builder
  ↓
2.3s - Agent Builder returns to ElevenLabs
  ↓
2.4s - ElevenLabs converts text to speech
  ↓
3.0s - User hears G'sves voice response
```

**Total Time: 3 seconds** ⚡

---

### Visual Data Flow

```
┌─────────────┐
│    USER     │
│  "Question" │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│   ELEVENLABS     │
│  Voice → Text    │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────┐
│     AGENT BUILDER WORKFLOW           │
│                                      │
│  ┌────────────────────┐             │
│  │ Classification     │             │
│  │ Agent              │             │
│  └────────┬───────────┘             │
│           │                          │
│           ▼                          │
│  ┌────────────────────┐             │
│  │ Condition Node     │             │
│  └────┬───────────────┘             │
│       │                              │
│       ▼                              │
│  ┌────────────────────┐             │
│  │ MCP Node           │◄────────┐  │
│  │ (Calls tools)      │          │  │
│  └────────┬───────────┘          │  │
│           │                       │  │
│           ▼                       │  │
│  ┌────────────────────┐          │  │
│  │ G'sves Agent       │          │  │
│  │ (Formats response) │          │  │
│  └────────┬───────────┘          │  │
└───────────┼──────────────────────┼──┘
            │                      │
            ▼                      │
    ┌───────────────┐             │
    │  Response     │             │
    └───────┬───────┘             │
            │                      │
            ▼                      │
    ┌───────────────┐             │
    │  ELEVENLABS   │             │
    │  Text → Voice │             │
    └───────┬───────┘             │
            │                      │
            ▼                      │
    ┌──────────────┐              │
    │    USER      │              │
    │  Hears Voice │              │
    └──────────────┘              │
                                  │
                                  │
        ┌─────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│   MARKET-MCP-SERVER              │
│   (Fly.io)                       │
│                                  │
│   Tools:                         │
│   - get_stock_quote              │
│   - get_stock_history            │
│   - get_stock_news               │
│   - (+ 32 more)                  │
│                                  │
│   Data Sources:                  │
│   - Yahoo Finance                │
│   - CNBC                         │
└──────────┬───────────────────────┘
           │
           ▼
   ┌──────────────────┐
   │  Real Market     │
   │  Data APIs       │
   └──────────────────┘
```

---

## 🎉 Congratulations!

If you've completed all phases, you now have:

✅ **A cloud-deployed market data server** with 35+ tools
✅ **A visual Agent Builder workflow** that orchestrates AI decisions
✅ **Voice-enabled trading assistant** that gets real market data
✅ **Professional, scalable architecture** that's easy to modify
✅ **Monitoring and debugging tools** for quick issue resolution

### What You Can Do Now

**Easy Changes (No Code):**
- Add new tools to MCP node (just check more boxes)
- Modify G'sves personality (edit Agent Node instructions)
- Change routing logic (adjust Condition Node)
- Add approval steps (insert User Approval Node)

**Advanced Changes (Ask Developer):**
- Add more data sources
- Implement caching for faster responses
- Add user authentication
- Create custom tools for specific analysis

### Next Steps

**Week 1:**
- Monitor performance daily
- Collect user feedback
- Fine-tune G'sves responses

**Month 1:**
- Analyze most-used tools
- Optimize slow queries
- Add requested features

**Ongoing:**
- Update Agent Builder workflow as needed
- Add new market data tools
- Improve classification accuracy

---

## 📖 Glossary

**Agent Builder**: OpenAI's visual tool for creating AI workflows
**MCP**: Model Context Protocol - standard for AI tool communication
**Node**: A building block in Agent Builder (does one job)
**Workflow**: The complete flowchart of nodes
**Tool**: A function the AI can call (like "get stock price")
**Classification**: Figuring out what the user wants
**Condition**: If/then logic to route queries
**SSE**: Server-Sent Events - way for servers to push data
**Fly.io**: Cloud hosting platform
**ElevenLabs**: Voice AI service
**G'sves**: Your AI trading assistant personality

---

**Document Version**: 1.0
**Last Updated**: October 7, 2025
**Maintained By**: [Your Team]
**Questions**: [Your Contact]
