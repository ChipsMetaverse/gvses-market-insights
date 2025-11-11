# Playwright MCP Investigation Results - Complete Analysis

## Date: November 4, 2025, 01:50 UTC
## Method: Live Testing with Playwright MCP
## Status: ❌ **CHART CONTROL NOT WORKING**

---

## 🧪 Test Performed

**Query**: `"show me apple"`

**Expected Behavior**:
1. Agent calls `change_chart_symbol("AAPL")` MCP tool
2. Agent returns JSON: `{"text": "...", "chart_commands": ["LOAD:AAPL"]}`
3. Chart switches from TSLA to AAPL

**Actual Behavior**:
1. ❌ Agent did NOT call any MCP tools
2. ❌ Agent returned malformed output (double JSON intent)
3. ❌ Chart remained on TSLA (did not switch to AAPL)

---

## 📊 Evidence

### 1. Agent Response (from ChatKit iframe)

```
User: "show me apple"

Agent Response:
{"intent":"market_data","symbol":"AAPL","confidence":"high"}
{"intent":"market_data","symbol":"AAPL","confidence":"high"}

Apple Inc. (AAPL) — Real-Time Snapshot
Timestamp: 2025-11-04 01:48 UTC
...
[Analysis text continues]
```

**Problems:**
- Duplicate JSON intent output (appears twice)
- NO `chart_commands` array in response
- Response is NOT valid JSON format (mixing JSON + markdown)
- Agent is NOT using the configured `response_schema`

### 2. MCP Server Logs

```
[01:27:06] SSE connection established
[01:27:06] MESSAGE REQUEST (3 times)
[01:27:06] SSE connection closed
```

**CRITICAL:** **ZERO** chart control tool calls!  
No `change_chart_symbol` calls  
No `CHART CONTROL TOOL CALLED` logs  
No tool execution whatsoever

### 3. Chart Status

**Current Symbol**: TSLA  
**Sidebar News**: All TSLA news  
**Technical Levels**: TSLA levels ($482.42, $449.64, $430.90)

**Chart did NOT switch to AAPL!** ❌

---

## 🔍 Root Cause Analysis

### Problem 1: Agent Ignoring JSON Schema

Despite configuring:
- Output Format: JSON ✅
- Schema: `response_schema` with `text` + `chart_commands` ✅
- Required fields: both ✅

**The agent is NOT following the schema!**

Instead, it's outputting:
1. Raw JSON intent string (twice)
2. Markdown-formatted text analysis
3. NO `chart_commands` array

### Problem 2: Agent NOT Calling MCP Tools

Despite:
- Reasoning Effort: HIGH ✅
- Instructions: "ALWAYS call change_chart_symbol FIRST" ✅
- MCP Server: Connected and available ✅

**The agent is NOT calling any tools!**

The LLM is choosing to:
1. Parse the user intent
2. Generate text analysis
3. Skip tool execution entirely

### Problem 3: Workflow Routing Issue

The workflow is:
```
Intent Classifier → Chart Control Agent → G'sves Agent
```

But the Chart Control Agent is:
- Outputting TEXT (not JSON)
- Not calling tools
- Not generating chart_commands

**The G'sves agent then has nothing to work with!**

---

## 🎯 Why JSON Schema Isn't Working

**Agent Builder Limitation**: Even with structured JSON output configured, the agent can still:
1. Ignore the schema if instructions don't explicitly require it
2. Mix JSON and text in responses
3. Choose not to populate required fields

**The schema is a GUIDE, not a CONSTRAINT.**

---

## 💡 Solution: Force Tool Usage

The agent needs to be FORCED to call MCP tools. There are 3 ways to do this:

### Option A: Update Instructions (Try This First)

Add to the TOP of instructions:

```
🚨 MANDATORY TOOL REQUIREMENT 🚨

BEFORE generating ANY response, you MUST:
1. Call change_chart_symbol([SYMBOL]) tool if symbol detected
2. Wait for tool response
3. ONLY THEN generate your JSON response

NO EXCEPTIONS. Tool call is REQUIRED, not optional.

If user says "show me apple" or "show me AAPL":
→ IMMEDIATELY call: change_chart_symbol("AAPL")
→ THEN return: {"text": "analysis", "chart_commands": ["LOAD:AAPL"]}
```

### Option B: Add Tool Call Verification Step

Create a "Tool Coordinator" agent BEFORE Chart Control Agent:
```
Intent → Tool Coordinator → Chart Control Agent → G'sves
```

Tool Coordinator's job:
- Detect symbol in query
- Call change_chart_symbol
- Pass result to Chart Control Agent

### Option C: Backend Control (Most Reliable)

Skip Agent Builder tool calling entirely:
1. Chart Control Agent generates intent JSON
2. Backend parses intent JSON
3. Backend generates chart_commands directly
4. Frontend receives chart_commands from backend

**This is the most reliable solution** because we control the entire flow.

---

## 📋 Immediate Next Steps

### 1. Update Instructions (Playwright)

Use Playwright to update Chart Control Agent instructions with MANDATORY section at the very top.

### 2. Test Again

Run same test: `"show me apple"`  
Check logs for tool calls  
Verify chart switches to AAPL

### 3. If Still Doesn't Work → Option C

Implement backend control:
- Keep Agent Builder for text generation
- Add backend logic to parse intent and generate commands
- Frontend uses backend-generated commands

---

## 🔧 Code Changes Needed (Option C)

### Backend: `/backend/routers/agent_router.py`

```python
@app.post("/api/chatkit/proxy-agent")
async def proxy_agent_response(request: Request):
    # Get agent response from ChatKit/Agent Builder
    agent_response = await get_agent_response(request)
    
    # Parse intent from response
    intent = extract_intent_json(agent_response)
    
    # Generate chart commands
    chart_commands = []
    if intent.get("symbol"):
        chart_commands.append(f"LOAD:{intent['symbol']}")
    
    # Inject chart_commands into response
    return {
        "text": agent_response,
        "chart_commands": chart_commands,
        "intent": intent
    }
```

### Frontend: Update ChatKit to proxy through backend

Instead of ChatKit → Agent Builder directly  
Do: ChatKit → Backend → Agent Builder → Backend → ChatKit

Backend injects `chart_commands` before sending to frontend.

---

## ✅ Success Criteria

- [ ] Agent calls `change_chart_symbol` tool (visible in MCP logs)
- [ ] Agent returns valid JSON with `chart_commands` array
- [ ] Chart switches to requested symbol
- [ ] No duplicate JSON in response
- [ ] Schema is properly followed

---

## 📊 Current Config Status

| Setting | Status | Working? |
|---------|--------|----------|
| Output Format: JSON | ✅ Configured | ❌ Not followed |
| JSON Schema | ✅ Created | ❌ Ignored |
| Reasoning Effort: HIGH | ✅ Set | ❌ Still no tools |
| Instructions Updated | ✅ Done | ❌ Needs stronger |
| MCP Server Connected | ✅ Yes | ✅ Working |
| Tool Calls | ❌ Not happening | ❌ **CRITICAL** |

---

## 🎬 Next Action

**RECOMMENDED: Option A** - Update instructions with MANDATORY section and test again.

If that fails after 2-3 attempts → **Switch to Option C** (backend control) as it's the most reliable solution.

**Option C is production-ready** because:
- We control the flow 100%
- No dependency on LLM deciding to call tools
- Backend can parse any agent output and generate commands
- Works with ANY agent configuration

---

**Last Updated**: November 4, 2025, 01:50 UTC  
**Next Step**: Implement Option A with stronger instructions

