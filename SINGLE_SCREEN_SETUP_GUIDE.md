# Agent Builder Setup - Single Screen Guide

**EVERYTHING YOU NEED IN ONE DOCUMENT**

**Time**: 4-5 hours | **Current Step**: START HERE ⬇️

---

## ✅ What You Already Have

**Already Deployed & Working:**
- ✅ Backend FastAPI server on Fly.io (`gvses-market-insights`)
  - Includes REST API endpoints for market data
  - MCP servers run as subprocesses inside backend
  - Alpaca + Yahoo Finance data sources
- ✅ Frontend React app on Fly.io (`g-vses`)
- ✅ Voice system with ElevenLabs working
- ✅ Alpaca Markets integration

**What We're Adding:**
- Agent Builder visual workflow (replaces Python agent_orchestrator)
- 5-node workflow with classification and routing
- Backend API integration in Agent Builder
- **No additional infrastructure needed!**

---

## 🎯 STEP 1: Create Workflow in Agent Builder (2-3 hours)

### 1A. Open Agent Builder
1. Go to: https://platform.openai.com/playground/agents
2. Click "Create Agent"
3. Name: "G'sves Market Assistant"

### 1B. Add 5 Nodes

**Drag these from left sidebar:**
1. Start (already there)
2. Agent node → Name: "Classification Agent"
3. If/Else node → Name: "Router"
4. Agent node → Name: "G'sves Market Agent"
5. Agent node → Name: "Chat Handler"
6. End (already there)

**Visual Layout:**
```
Start
  ↓
[Classification Agent]
  ↓
[If/Else Router]
  ├─ True → [G'sves Market Agent] ──┐
  └─ False → [Chat Handler] ─────────┤
                                     ↓
                                    End
```

---

## 🎯 STEP 2: Configure Each Node (COPY-PASTE THESE)

### NODE 1: Classification Agent

**Click node → Configure:**

**Model**: gpt-4o-mini (faster, cheaper for classification)

**Instructions** (COPY THIS):
```
You are a classification agent for G'sves trading assistant.

Analyze the user's message and classify it into ONE category:

1. "market_data" - User wants real-time market information
   Examples: "What's Tesla's price?", "Show me AAPL chart", "Get NVDA news"

2. "general_chat" - Everything else
   Examples: "Hello", "How are you?", "Thanks", "Explain moving averages"

Output ONLY the category name: "market_data" or "general_chat"
```

**Output Variable**: `classification_result`

---

### NODE 2: If/Else Router

**Click node → Configure:**

**Condition**:
```
classification_result == "market_data"
```

**True path**: Goes to G'sves Market Agent
**False path**: Goes to Chat Handler

---

### NODE 3: G'sves Market Agent

**Click node → Configure:**

**Model**: gpt-4o

**Instructions** (COPY THIS):
```
You are G'sves, a professional trading assistant with 30 years of experience.

You have access to real-time market data through backend API functions.
Use these tools to answer user questions about markets.

Available functions:
- get_stock_price(symbol) - Get current stock price and quote data
- get_stock_history(symbol, days) - Get historical price data for charts
- get_stock_news(symbol) - Get latest market news

Always:
1. Use the appropriate function for the user's question
2. Provide context and analysis with the data
3. Keep responses concise for voice delivery (under 100 words)
4. Format numbers clearly for voice: "242 dollars" not "$242"

You are warm, knowledgeable, and focus on risk management.
```

**Tools** (Click "Add Tool" → "Function"):

**Function 1: get_stock_price**
```yaml
Name: get_stock_price
Description: Get current stock price, change, volume, and quote data

Parameters:
  symbol:
    type: string
    description: Stock ticker symbol (e.g., TSLA, AAPL, NVDA)
    required: true

HTTP Configuration:
  Method: GET
  URL: https://gvses-market-insights.fly.dev/api/stock-price
  Query Parameters:
    symbol: {{symbol}}
```

**Function 2: get_stock_history**
```yaml
Name: get_stock_history
Description: Get historical price data for charting and analysis

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

HTTP Configuration:
  Method: GET
  URL: https://gvses-market-insights.fly.dev/api/stock-history
  Query Parameters:
    symbol: {{symbol}}
    days: {{days}}
```

**Function 3: get_stock_news**
```yaml
Name: get_stock_news
Description: Get latest market news articles for a symbol

Parameters:
  symbol:
    type: string
    description: Stock ticker symbol
    required: true

HTTP Configuration:
  Method: GET
  URL: https://gvses-market-insights.fly.dev/api/stock-news
  Query Parameters:
    symbol: {{symbol}}
```

**Output Variable**: `market_response`

---

### NODE 4: Chat Handler

**Click node → Configure:**

**Model**: gpt-4o

**Instructions** (COPY THIS):
```
You are G'sves, a friendly trading assistant with 30 years of experience.

Personality:
- Warm and approachable
- Patient educator
- Focuses on risk management
- Never gives financial advice (for educational purposes only)

Handle these types of messages:
- Greetings: Be warm and welcoming
- Questions: Provide clear, educational answers about trading concepts
- Thanks: Acknowledge graciously
- Help requests: Explain what you can do

Keep responses conversational and under 3 sentences for general chat.

IMPORTANT: This is general conversation only. Do NOT provide real-time market data.
For market data requests, the classification agent will route to the market agent.
```

**Output Variable**: `chat_response`

---

### NODE 5: Start and End

**No configuration needed** - automatic

---

## 🎯 STEP 3: Connect the Nodes

**Draw lines between nodes (drag from output dot to input dot):**

1. Start → Classification Agent
2. Classification Agent → If/Else Router
3. If/Else Router (True) → G'sves Market Agent
4. If/Else Router (False) → Chat Handler
5. G'sves Market Agent → End
6. Chat Handler → End

**✅ CHECKPOINT**: Workflow looks like the diagram in Step 1B

---

## 🎯 STEP 4: Test in Preview Mode (30 min)

**Click "Preview" button (top right)**

### Test 1: Market Data
```
Input: "What's Tesla's stock price?"
Expected Path: Classification → Router (True) → Market Agent → End
Expected Output: "Tesla is currently trading at [price]..."
```

### Test 2: Chart Command
```
Input: "Show me Apple historical data"
Expected Path: Same as Test 1
Expected Output: Historical data summary with trend info
```

### Test 3: General Chat
```
Input: "Hello G'sves"
Expected Path: Classification → Router (False) → Chat → End
Expected Output: "Hello! I'm G'sves, your trading assistant..."
```

**ALL 3 WORKING?** ✅ Continue to Step 5

**FAILING?** Check:
- Node connections correct?
- Backend URL correct? (https://gvses-market-insights.fly.dev/api/...)
- Classification output variable = `classification_result`?
- If/Else condition exact: `classification_result == "market_data"`?
- Function definitions match backend API exactly?

**Test Backend API Directly:**
```bash
# In terminal - verify backend is responding
curl "https://gvses-market-insights.fly.dev/health"
# Expected: {"status": "healthy"}

curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=TSLA"
# Expected: {"symbol": "TSLA", "price": ...}
```

---

## 🎯 STEP 5: Publish Workflow (15 min)

1. Click "Publish" button (top right)
2. Version name: `v1.0 - Basic Market Assistant`
3. Description: `5-node workflow with backend API integration`
4. Click "Publish"
5. **COPY THE WORKFLOW ID** → Looks like `wf_xxxxxxxxxxxxx`
6. **SAVE THIS ID** - you need it for backend

---

## 🎯 STEP 6: Backend Integration (1 hour)

### 6A. Update Backend Environment

**File**: `backend/.env`

**Add these lines:**
```bash
# Agent Builder
AGENT_BUILDER_WORKFLOW_ID=wf_xxxxxxxxxxxxx  # From Step 5
USE_AGENT_BUILDER=true
OPENAI_API_KEY=sk-ant-...  # Your OpenAI API key
```

### 6B. Test Backend Connection

```bash
cd backend

# Test script
python -c "
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
workflow_id = os.getenv('AGENT_BUILDER_WORKFLOW_ID')

print(f'Testing workflow: {workflow_id}')

# Test query
response = client.chat.completions.create(
    model='gpt-4o',
    messages=[{'role': 'user', 'content': 'What is Tesla price?'}],
    extra_headers={'X-Workflow-ID': workflow_id}
)

print(f'Response: {response.choices[0].message.content}')
print('✓ Backend connected to Agent Builder!')
"
```

**Expected**: Response with Tesla price data

### 6C. Deploy Backend

```bash
# Set Fly.io secrets
fly secrets set AGENT_BUILDER_WORKFLOW_ID=wf_xxxxx --app gvses-market-insights
fly secrets set USE_AGENT_BUILDER=true --app gvses-market-insights
fly secrets set OPENAI_API_KEY=sk-ant-... --app gvses-market-insights

# Deploy
fly deploy --app gvses-market-insights

# Check status
fly status --app gvses-market-insights
```

**✅ CHECKPOINT**: Backend deployed successfully

---

## 🎯 STEP 7: End-to-End Test (30 min)

### Voice Test:

1. Open frontend: https://g-vses.fly.dev (or localhost:5174)
2. Click microphone icon
3. Say: **"What's Tesla's stock price?"**
4. **Expected**: Hear current Tesla price spoken back
5. Say: **"Hello G'sves"**
6. **Expected**: Hear friendly greeting
7. Say: **"Show me Apple chart"**
8. **Expected**: Chart updates to AAPL

### ALL 3 WORKING?

**🎉 PHASE 1 COMPLETE!**

You now have:
- ✅ Agent Builder workflow deployed
- ✅ Backend API providing real market data
- ✅ Backend routing voice queries to workflow
- ✅ End-to-end voice trading assistant working

---

## 📊 Progress Checklist

**Phase 1 - Basic (CURRENT)**:
- [ ] Agent Builder workflow created
- [ ] 5 nodes added and configured
- [ ] Backend API functions defined in Market Agent
- [ ] Nodes connected correctly
- [ ] Preview tests all passing
- [ ] Workflow published
- [ ] Workflow ID saved
- [ ] Backend .env updated
- [ ] Backend connection tested
- [ ] Backend deployed to Fly.io
- [ ] End-to-end voice test passed

**Time**: 4-5 hours total

---

## 🆘 Common Issues

### Backend API Not Responding
```bash
# Check backend health
curl https://gvses-market-insights.fly.dev/health

# If error, check logs
fly logs --app gvses-market-insights -f

# Check if backend is running
fly status --app gvses-market-insights
```

### Classification Always Goes to Chat
**Fix**: Check If/Else condition is EXACTLY:
```
classification_result == "market_data"
```
(No quotes around the variable name, no extra spaces)

### Function Calls Failing
**Fix**:
1. Verify backend URL: `https://gvses-market-insights.fly.dev/api/stock-price`
2. Check query parameter names match: `symbol` (not `ticker`)
3. Test API directly with curl (see Step 4 troubleshooting)
4. Check Agent Builder function definitions match backend API

### Variables Not Passing Between Nodes
**Fix**:
1. Node 1 output variable: `classification_result`
2. Node 2 condition uses: `classification_result`
3. Node 3 output: `market_response`
4. Node 4 output: `chat_response`

### Backend Can't Find Workflow
**Fix**: Check workflow ID in .env matches exactly (including `wf_` prefix)

---

## 🎯 You're Done When...

✅ Voice query → Agent Builder → Backend API → Real market data → Voice response

That's it! Phase 1 complete.

---

## 📚 Want More?

**Phase 2 - Enhanced (optional, +3-4 hours)**:
- Add Guardrails node (safety)
- Add Transform node (formatting)
- Add Structured Output (JSON)
- Add Set State (memory)

**Phase 3 - Advanced (optional, +2-3 hours)**:
- Add Loop node (batch processing)
- Add Code Interpreter (custom calcs)
- Add Web Search (more news)
- Add Approval (trade confirmations)

See AGENT_BUILDER_MASTER_GUIDE.md for Phase 2 & 3 details.

---

## 📘 Architecture Reference

**For detailed architecture explanation**, see:
- AGENT_BUILDER_BACKEND_INTEGRATION.md - Complete backend integration guide
- Shows how MCP servers run as subprocesses
- Explains why no separate deployment needed
- Provides API endpoint documentation

---

## ✨ Final Notes

**This is everything you need** in a single document.

Keep this open while working in Agent Builder.

Copy-paste the node configurations EXACTLY as shown.

Test each step before moving to next.

Take breaks - 4-5 hours is manageable!

**Good luck!** 🚀
