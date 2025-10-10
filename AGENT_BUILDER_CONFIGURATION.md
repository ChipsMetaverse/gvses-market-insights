# G'sves Agent Builder Configuration Guide

## ✅ Pre-Configuration Checklist

- [✅] G'sves instructions prepared (`AGENT_BUILDER_INSTRUCTIONS.md`)
- [✅] Direct API MCP server created (`agent-builder-functions/`)
- [✅] Vector store setup script ready (`setup_vector_store.py`)
- [✅] Hybrid tool strategy documented (`HYBRID_TOOL_STRATEGY.md`)
- [ ] Run vector store setup: `python setup_vector_store.py`
- [ ] Install direct API MCP: `cd agent-builder-functions && npm install`
- [ ] Test direct API MCP: `npm start`

---

## Step-by-Step Agent Builder Configuration

### Step 1: Create Vector Store (5 minutes)

```bash
# From project root
python setup_vector_store.py
```

**Expected Output**:
```
✅ OpenAI client initialized
📚 Creating vector store for G'sves trading knowledge...
✅ Vector store created: vs_abc123xyz...
   📄 Found: AGENT_BUILDER_INSTRUCTIONS.md
   📄 Converted: technical_analysis_for_dummies_2nd_edition.json → .md
   ...
📊 VECTOR STORE SETUP COMPLETE
📌 Vector Store ID: vs_abc123xyz...
```

**Action**: Copy the Vector Store ID - you'll need it in Step 5

---

### Step 2: Configure Agent Node (10 minutes)

1. **Open Agent Builder**: https://platform.openai.com/agent-builder
2. **Open your existing workflow** ("New workflow" with "Gvses" agent)
3. **Click on the "Gvses" Agent node**
4. **Update Instructions**:
   - Open `AGENT_BUILDER_INSTRUCTIONS.md`
   - Copy entire content (Ctrl+A, Ctrl+C)
   - Paste into Agent node Instructions field
5. **Configure Model**:
   - Model: `gpt-5-mini` (fast, cost-effective)
   - Reasoning effort: `medium`
6. **Output format**: `Text` (natural conversation)

**Result**: Your agent now has the full G'sves personality and methodology

---

### Step 3: Add MCP Node for Direct API (15 minutes)

1. **Add new MCP node**:
   - Click `+` button in workflow
   - Select "MCP" from Tools section
   - Name it: "Direct API (Alpaca & Yahoo)"

2. **Configure MCP Connection** (Local Development):

   ```json
   {
     "type": "stdio",
     "command": "node",
     "args": ["/Volumes/WD My Passport 264F Media/claude-voice-mcp/agent-builder-functions/index.js"],
     "env": {
       "ALPACA_API_KEY": "PKM2U9W8XB8D0EUP1Q38",
       "ALPACA_SECRET_KEY": "HdSPzEKEvMEcgUqKcNModn1nXaTCyDOK4Mr5mW3t"
     }
   }
   ```

3. **Select Tools to Enable**:
   - ✅ `get_realtime_quote` - Real-time stock prices
   - ✅ `get_historical_bars` - OHLCV data for technical analysis
   - ✅ `get_multiple_quotes` - Batch quotes for watchlists
   - ✅ `get_market_news` - Latest news and catalysts
   - ✅ `get_yahoo_quote_fallback` - Backup + crypto support

**Why**: Sub-500ms latency for real-time trading decisions

---

### Step 4: Add MCP Node for Market Analysis (15 minutes)

1. **Add second MCP node**:
   - Click `+` button
   - Select "MCP"
   - Name it: "Market Analysis (Yahoo & CNBC)"

2. **Configure MCP Connection** (market-mcp-server):

   ```json
   {
     "type": "stdio",
     "command": "node",
     "args": ["/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server/index.js"]
   }
   ```

3. **Select Tools to Enable**:
   - ✅ `get_support_resistance` - Calculate LTB/ST/QE levels!
   - ✅ `get_technical_indicators` - RSI, MACD, Bollinger Bands
   - ✅ `get_chart_patterns` - Head & shoulders, triangles, flags
   - ✅ `get_market_movers` - Biggest gainers/losers
   - ✅ `get_cnbc_sentiment` - CNBC market sentiment
   - ✅ `get_analyst_ratings` - Price targets
   - ✅ `get_options_chain` - Options with Greeks

**Why**: Complex analysis and pattern detection requiring computation

---

### Step 5: Add File Search Node (RAG) (10 minutes)

1. **Add File Search node**:
   - Click `+` button
   - Select "File search" from Tools section
   - Name it: "Trading Knowledge Base"

2. **Configure File Search**:
   - **Vector Store ID**: `vs_abc123xyz...` (from Step 1)
   - **Query**: `{{user_message}}` (dynamic - takes user's question)
   - **Max Results**: `5`
   - **Relevance Threshold**: `0.7`

3. **When to Use**:
   - User asks educational questions ("What is delta?")
   - Explaining G'sves methodology
   - Trading psychology guidance
   - Risk management principles

**Why**: Instant access to trading knowledge without API calls

---

### Step 6: Add If/Else Routing Logic (20 minutes) - OPTIONAL but RECOMMENDED

**Purpose**: Route queries to the optimal tool tier for best performance

1. **Add If/else node** after Start node:
   - Click `+` after Start
   - Select "If / else" from Logic section

2. **Configure Routing Logic** using CEL (Common Expression Language):

   **Branch 1: Real-time Price Query**
   ```cel
   input.message.matches("(?i)(price|quote|trading at|current|what's .* at)")
   ```
   → Route to: Direct API MCP → `get_realtime_quote`

   **Branch 2: Technical Analysis**
   ```cel
   input.message.matches("(?i)(RSI|MACD|support|resistance|LTB|ST|QE|technical|pattern|chart)")
   ```
   → Route to: Market Analysis MCP → `get_technical_indicators` + `get_support_resistance`

   **Branch 3: Educational Query**
   ```cel
   input.message.matches("(?i)(what is|explain|how do|teach me|definition|meaning)")
   ```
   → Route to: File Search (RAG)

   **Branch 4: Market Brief**
   ```cel
   input.message.matches("(?i)(good morning|market brief|overview|what's happening)")
   ```
   → Route to: Direct API + Market Analysis (parallel)

   **Else**: Default to Gvses Agent (general handling)

**Result**: Queries routed to optimal tool tier automatically

---

### Step 7: Add Human Approval Node (10 minutes) - COMPLIANCE

**Purpose**: Safeguard for trade recommendations

1. **Add Human approval node** after Gvses Agent:
   - Click `+`
   - Select "Human approval" from Logic section

2. **Configure Approval**:
   - **Condition**: Only trigger if response contains trade recommendation
   - **CEL Expression**:
     ```cel
     output.message.matches("(?i)(buy|sell|enter|exit|option|trade setup)")
     ```
   - **Approval Message**:
     ```
     ⚠️ Trade Recommendation Detected

     G'sves has suggested a trading setup. Please review:

     {{output.message}}

     This is educational analysis, not financial advice.
     Do you want to share this recommendation?
     ```
   - **On Approve**: Continue to End node
   - **On Reject**: End without sending

**Why**: Compliance safeguard, ensures users review trade suggestions

---

## Final Workflow Structure

### Simplified Flow (Fastest to Implement)
```
Start
  ↓
Gvses Agent
  ↓ (can call any tool)
[Direct API MCP] [Market Analysis MCP] [File Search]
  ↓
End
```

**Time to implement**: 45 minutes
**Complexity**: Low
**Performance**: Good

---

### Enhanced Flow (Recommended for Production)
```
Start (user input)
  ↓
If/else (Route by query type)
  ├─ "Price Query" → Direct API MCP → Gvses Agent → End
  ├─ "Technical Analysis" → Market Analysis MCP → Gvses Agent → End
  ├─ "Educational" → File Search RAG → Gvses Agent → End
  └─ "Market Brief" → Direct API + Market Analysis → Gvses Agent → End
      ↓
If/else (Contains trade recommendation?)
  ├─ Yes → Human Approval
  │          ↓ (approved)
  │        End
  └─ No → End
```

**Time to implement**: 90 minutes
**Complexity**: Medium
**Performance**: Excellent (routes to optimal tools)

---

## Testing Your Workflow

### Test Queries

1. **Real-time Price** (Direct API):
   - "What's AAPL trading at?"
   - Expected: < 500ms response with current price

2. **Technical Analysis** (Market MCP):
   - "Show me TSLA's RSI and support levels"
   - Expected: RSI calculation + LTB/ST/QE levels

3. **Educational** (File Search RAG):
   - "What is delta in options trading?"
   - Expected: Explanation from options guide

4. **Market Brief** (Both MCPs):
   - "Good morning, what's the market looking like?"
   - Expected: Indices + movers + news + sentiment

5. **Options Trade Setup** (All three tiers):
   - "NVDA call options for this week"
   - Expected: Current price + options chain + Greeks analysis + setup recommendation
   - Should trigger Human Approval node

### Performance Benchmarks

| Query Type | Target Latency | Tools Used |
|------------|----------------|------------|
| Real-time price | < 500ms | Direct API MCP |
| Technical analysis | < 3s | Direct API + Market MCP |
| Educational | < 2s | File Search RAG |
| Market brief | < 5s | All three (parallel) |
| Options setup | < 8s | All three (sequential) |

---

## Publishing Your Workflow

1. **Click "Publish"** in top navigation
2. **Version**: Major version (e.g., v1.0.0)
3. **Description**: "G'sves market analysis assistant with hybrid tool architecture"
4. **Get Workflow ID**: Copy the workflow ID (starts with `wf_...`)

**Save this ID** - you'll need it for voice integration!

---

## Environment Variables

Add to `backend/.env`:

```bash
# Agent Builder Configuration
GVSES_WORKFLOW_ID=wf_68e474d14d2881908553eddb75c0ff6400f3440573cf0d...
GVSES_VECTOR_STORE_ID=vs_abc123xyz...
```

---

## Next Steps: Voice Integration

Once your workflow is published and tested:

1. **Install Agents SDK**: `pip install openai-agents-sdk`
2. **Create workflow client**: `backend/services/agent_builder_client.py`
3. **Update voice pipeline**: Route transcripts to workflow instead of agent_orchestrator
4. **Test end-to-end**: Voice → STT → Workflow → TTS

See `HYBRID_TOOL_STRATEGY.md` Phase 4 for voice integration details.

---

## Troubleshooting

### MCP Connection Failed
- **Check**: Node.js 22+ installed (`node --version`)
- **Check**: Paths absolute in MCP config
- **Check**: Environment variables set correctly
- **Test**: Run MCP server manually: `node agent-builder-functions/index.js`

### File Search Returns No Results
- **Check**: Vector Store ID correct
- **Check**: Files uploaded successfully (check OpenAI platform)
- **Check**: Query relevance threshold not too high (try 0.5)

### Tools Not Executing
- **Check**: Tools enabled in Gvses Agent node configuration
- **Check**: Agent instructions mention tool availability
- **Check**: MCP servers running (test with stdio)

### Workflow Timeout
- **Check**: Parallel calls where possible (not sequential)
- **Check**: Direct API used for time-sensitive queries
- **Check**: Cached results in MCP servers

---

## Summary

Your G'sves Agent Builder workflow now has:

✅ **Complete G'sves personality and methodology** (Agent node)
✅ **Fast real-time data** (< 500ms via Direct API MCP)
✅ **Complex analysis** (Market Analysis MCP)
✅ **Educational knowledge** (File Search RAG)
✅ **Intelligent routing** (If/else logic - optional)
✅ **Compliance safeguards** (Human approval - optional)

**Ready for**: Testing, publishing, and voice integration!
