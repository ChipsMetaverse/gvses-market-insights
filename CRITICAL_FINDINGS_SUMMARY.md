# Critical Findings: Chart Control Issue - COMPLETE ANALYSIS

## Investigation Date: November 4, 2025
## Method: Playwright MCP Browser Automation
## Status: ✅ ROOT CAUSE IDENTIFIED

---

## 🎯 The Core Problem

**The Chart Control Agent is NOT calling MCP tools and is outputting TEXT instead of structured JSON with chart commands.**

---

## 📊 Workflow Flow (Verified via Playwright)

```
User Query: "show me nvidia"
    ↓
Intent Classifier (outputs JSON)
    ↓
Transform (extracts: input.output_parsed.intent)
    ↓
If/Else (checks: input.intent in ["market_data", "chart_command"])
    ↓ (TRUE for "market_data")
Chart Control Agent
    - Has: Chart_Control_MCP_Server tools available ✅
    - Has: Reasoning effort = HIGH ✅
    - Has: Instructions for chart analysis ✅
    - Output Format: TEXT ❌ (SHOULD BE JSON)
    - Tool Calls: NONE ❌ (Should call change_chart_symbol)
    ↓
G'sves Agent
    - Receives TEXT (no structured data)
    - Cannot extract chart_commands
    ↓
Frontend
    - Chart stays on TSLA (doesn't switch to NVDA)
```

---

## 🔍 Key Findings from Playwright Investigation

### Finding #1: Output Format is TEXT
**Screenshot Evidence**: `workflow_routing_issue.png`

The Chart Control Agent is configured with:
- **Output format**: TEXT
- **Should be**: JSON with schema including `text` and `chart_commands`

### Finding #2: Agent Not Calling MCP Tools
**Test Evidence**: "show me nvidia" test

Even with HIGH reasoning effort, the agent:
- Generates text analysis ✅
- Generates JSON intent string in text: `{"intent":"market_data","symbol":"NVDA"}` ❌
- Does NOT call `change_chart_symbol` MCP tool ❌
- Chart remains on TSLA ❌

### Finding #3: Workflow Routing IS Correct
**Visual Evidence**: Workflow diagram shows correct path

The If/Else node correctly routes:
- Educational queries → Educational branch
- Market Data & Charts → Chart Control Agent → G'sves Agent → End

The routing is NOT the problem.

### Finding #4: Instructions Don't Require Tool Calls
**Current instructions** tell the agent WHAT to analyze, but not HOW to use tools:
```
"When users request charts or technical analysis:
- Generate clear, actionable chart descriptions
- Focus on technical analysis and price action"
```

**Missing**: Explicit requirement to CALL MCP TOOLS FIRST

---

## ✅ The Solution (3 Steps)

### Step 1: Change Output Format to JSON ⚠️ CRITICAL
**Status**: ✅ IN PROGRESS (via Playwright)

Change Chart Control Agent:
- From: TEXT
- To: JSON with schema:

```json
{
  "text": "string",          // Analysis text
  "chart_commands": ["string"],  // e.g. ["LOAD:NVDA"]
  "symbol": "string"         // e.g. "NVDA"
}
```

### Step 2: Update Instructions to Require Tool Calls
**Status**: ⏳ PENDING

Prepend to Chart Control Agent instructions:

```markdown
**CRITICAL: YOU MUST CALL MCP TOOLS FIRST**

When users request to see a stock:
1. FIRST: Call change_chart_symbol({symbol: "NVDA"})
2. THEN: Call get_stock_price({symbol: "NVDA"})
3. FINALLY: Return JSON with:
   {
     "text": "Your analysis...",
     "chart_commands": ["LOAD:NVDA"],
     "symbol": "NVDA"
   }

DO NOT respond without calling tools first.
```

### Step 3: Publish and Test
**Status**: ⏳ PENDING

1. Publish as v30
2. Test: "show me apple"
3. Verify:
   - MCP server logs show `change_chart_symbol` call
   - Frontend receives `chart_commands: ["LOAD:AAPL"]`
   - Chart switches from TSLA → AAPL

---

## 📝 Manual Steps Required (Agent Builder UI)

Since the Playwright automation is complex for adding JSON schema properties, here are the **EXACT MANUAL STEPS**:

### In Agent Builder:

1. **✅ DONE**: Changed Output Format to JSON
2. **⏳ TODO**: Click "Add property" and add:
   - Property 1:
     - Name: `text`
     - Type: STR
     - Description: "Analysis text for the user"
   - Property 2:
     - Name: `chart_commands`
     - Type: ARRAY (items: STR)
     - Description: "Array of chart commands like LOAD:SYMBOL"
   - Property 3:
     - Name: `symbol`
     - Type: STR
     - Description: "The stock symbol being analyzed"

3. **⏳ TODO**: Click "Update"
4. **⏳ TODO**: Update Instructions (prepend the CRITICAL section above)
5. **⏳ TODO**: Click "Publish" → v30

---

## 🧪 Testing Checklist

After deploying v30:

### Test 1: Chart Switching
```bash
# In ChatKit, type: "show me apple"
# Expected:
# - Chart switches from current symbol → AAPL
# - Response includes Apple analysis
# - Happens within 3 seconds
```

### Test 2: MCP Server Logs
```bash
flyctl logs -a gvses-mcp-sse-server | grep "change_chart_symbol"
# Expected output:
# [INFO] Tool called: change_chart_symbol with args: {symbol: "AAPL"}
# [INFO] Returning chart command: LOAD:AAPL
```

### Test 3: Frontend Response
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "show me nvidia"}' | jq

# Expected output:
{
  "text": "NVIDIA analysis...",
  "chart_commands": ["LOAD:NVDA"],
  "symbol": "NVDA"
}
```

---

## 🎓 Root Cause Summary

**Why the chart doesn't switch:**

1. ❌ Chart Control Agent outputs TEXT (no structured `chart_commands`)
2. ❌ Agent doesn't call MCP tools (instructions don't require it)
3. ❌ Frontend never receives chart commands to execute
4. ❌ Chart remains on whatever symbol was previously loaded

**The fix:**
1. ✅ Change output to JSON with `chart_commands` field
2. ✅ Update instructions to explicitly require MCP tool calls
3. ✅ Frontend will receive and execute chart commands

---

## 📂 Files & References

- **Agent Builder Workflow**: `wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`
- **Current Version**: v29 (production)
- **Next Version**: v30 (with fixes - draft in progress)
- **MCP Server**: `gvses-mcp-sse-server.fly.dev`
- **Backend**: `gvses-market-insights.fly.dev`
- **Screenshot**: `.playwright-mcp/workflow_routing_issue.png`

---

## 🚀 Next Steps

**IMMEDIATE** (5-10 minutes):
1. Complete JSON schema in Agent Builder (add 3 properties)
2. Update Chart Control Agent instructions
3. Publish v30 to production
4. Test with "show me apple"

**FOLLOW-UP** (if still not working):
1. Check MCP server logs for tool calls
2. Add debug logging to Chart Control Agent
3. Consider adding hint in instructions about when to call tools

---

**Confidence Level**: 95%
**ETA to Resolution**: 10-15 minutes after completing manual UI steps
**Priority**: HIGH - User is blocked

---

**Investigation Complete** ✅

