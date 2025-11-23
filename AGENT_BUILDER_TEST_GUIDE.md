# Agent Builder Testing Guide - Chart Control Workflow

## Objective
Test whether the Intent Classifier JSON output issue is a **workflow configuration problem** or a **ChatKit integration problem**.

---

## Prerequisites
- Logged into OpenAI Platform
- Access to Agent Builder workflow v50 (production)
- URL: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736&version=50

---

## Testing Steps

### Step 1: Switch to Preview Mode
1. Navigate to the Agent Builder workflow v50
2. At the top of the page, you'll see two radio buttons:
   - **Edit mode** (currently selected)
   - **Preview mode** ← Click this
3. This switches to the test panel where you can interact with the workflow

### Step 2: Test with "show me Apple"
1. In the Preview mode panel, you'll see a chat interface
2. Type the test message: **"show me Apple"**
3. Click Send
4. Observe the response

---

## Expected vs Actual Results

### ❌ Current Behavior (Incorrect)
If you see this output, the workflow has a routing problem:
```json
{"intent":"chart_command","symbol":"AAPL","confidence":"high"}
```

**What this means**: The workflow stops at the Intent Classifier and returns its JSON output instead of continuing to the Chart Control Agent.

### ✅ Expected Behavior (Correct)
If you see this output, the workflow is routing correctly:
```
I've identified this as a chart display request for Apple Inc. (AAPL).

I'll now use the chart control tools to switch the display to AAPL.

[MCP tool call: change_chart_symbol with symbol=AAPL]

**Chart Update**: Successfully queued command to display AAPL chart.

**Current Analysis**:
- Price: $275.25 (+2.2%)
- Technical Picture: [Analysis based on current data]
- Key Levels: Support at $270, Resistance at $280

**Trader's Takeaway**: [Actionable insight]
```

---

## Diagnostic Analysis

### If Preview Mode Shows JSON ❌
**Problem**: Workflow configuration issue
- The routing through Transform → If/Else → Chart Control Agent is broken
- Need to investigate workflow output settings
- May need to check Agent Builder platform behavior

**Next Steps**:
1. Check if there's a "Return First Output" setting somewhere
2. Verify the If/Else node is actually routing to Chart Control Agent
3. Check Chart Control Agent's output format configuration
4. Consider simplifying workflow (remove Transform node, use direct routing)

### If Preview Mode Shows Natural Language ✅
**Problem**: ChatKit integration issue
- Workflow is correct
- ChatKit is caching an old workflow version
- ChatKit might have different output handling than Preview mode

**Next Steps**:
1. Force refresh ChatKit session
2. Check ChatKit configuration for workflow version
3. Verify ChatKit is using v50 (not v48 or v49)
4. Clear browser cache and restart ChatKit session

---

## Additional Test Cases

Once you've tested "show me Apple", try these:

1. **"show me Tesla"** → Should classify as `chart_command` with symbol `TSLA`
2. **"what is Apple's latest earnings?"** → Should classify as `market_data`
3. **"tell me about Tesla's business model"** → Should classify as `company-info` (NOT chart_command)
4. **"hello"** → Should classify as `general_chat`

Each test helps verify:
- Intent Classifier is working correctly
- Transform node is extracting the intent
- If/Else is routing to the correct agent
- Final agents are returning natural language (not JSON)

---

## Workflow Structure Reference

The correct flow should be:

```
User Input: "show me Apple"
    ↓
Start Node
    ↓
Intent Classifier Agent
    ↓ outputs: {"intent":"chart_command","symbol":"AAPL","confidence":"high"}
    ↓
Transform Node
    ↓ extracts: {intent: "chart_command"}
    ↓
If/Else Node (condition: intent in ["market_data", "chart_command"])
    ↓ (IF branch - matches)
    ↓
Chart Control Agent
    ↓ - Receives original user message: "show me Apple"
    ↓ - Calls MCP tool: change_chart_symbol(symbol="AAPL")
    ↓ - Returns natural language analysis
    ↓
End Node
    ↓
User Sees: Natural language response + chart switches to AAPL ✅
```

**Critical**: The Transform node should only pass the `intent` field forward for routing, but the Chart Control Agent should receive the **original user message**, not the JSON.

---

## What We've Already Verified

✅ **Backend Rate Limiting**: Fixed and deployed
✅ **Intent Classifier Examples**: Updated in v50 with explicit examples
✅ **Transform Node Config**: Correctly set to "Expressions" mode, extracts `intent` field
✅ **If/Else Routing**: Correctly configured with `intent in ["market_data", "chart_command"]`
✅ **Workflow Edges**: All 7 connections verified:
   1. Start → Intent Classifier
   2. Intent Classifier → Transform
   3. Transform → If/Else
   4. If/Else → Chart Control Agent (IF branch)
   5. If/Else → G'sves (ELSE branch)
   6. Chart Control Agent → End
   7. G'sves → End

---

## Known Issues from Previous Testing

From `AGENT_BUILDER_TESTING_COMPLETE.md`:

**Bug #2: If/Else Routing Issue**
> "The If/Else node isn't properly hiding the Intent Classifier's JSON output. Users see the raw classification instead of the final agent response."

**Supposed Fix in v48**:
> "Workflow was restructured to ensure Transform → If/Else properly routes to final agents."

**Current Status (v50)**: This issue has **recurred** despite the fix in v48.

---

## Session Logs Reference

From our testing session on Nov 12, 2025:

**ChatKit Test**:
- Input: "show me Apple"
- Output: `{"intent":"chart_command","symbol":"AAPL","confidence":"high"}`
- Result: ❌ JSON shown, chart didn't switch

**Console Logs** (showing polling is working):
```
[LOG] [ChartPoller] Starting command polling
[LOG] ✅ ChatKit session established with Agent Builder
```

This confirms:
- Frontend polling is working
- ChatKit is connected to Agent Builder
- Rate limiting is fixed
- But workflow output is wrong

---

## Debug Checklist

If Preview mode also shows JSON:

- [ ] Check Intent Classifier "Include chat history" setting
- [ ] Verify Chart Control Agent has "Include chat history" enabled
- [ ] Check if Transform node is configured as "Object" instead of "Expressions"
- [ ] Verify If/Else condition syntax is correct
- [ ] Check Chart Control Agent's input configuration
- [ ] Look for any "Return immediately" or "Streaming" settings
- [ ] Check End node configuration (might have output settings)

If Preview mode shows correct output:

- [ ] Clear ChatKit cache in browser
- [ ] Force refresh ChatKit widget (Ctrl+Shift+R)
- [ ] Check ChatKit is using workflow v50 (not older version)
- [ ] Verify ChatKit session_id is recent
- [ ] Check backend logs for ChatKit → Agent Builder communication
- [ ] Try deploying a new version (v51) to force ChatKit refresh

---

## Success Criteria

The test is **successful** when:

1. ✅ Preview mode returns natural language (not JSON)
2. ✅ Preview mode shows Chart Control Agent was invoked
3. ✅ Preview mode shows MCP tool call attempt
4. ✅ No raw JSON visible in the response
5. ✅ Response includes actionable trading insights

---

## Timeline

- **Nov 12, 2025**: Fixed rate limiting, updated Intent Classifier examples
- **Current**: Investigating workflow output routing issue
- **Next**: Test in Preview mode to isolate problem source

---

## Related Files

- `CHART_CONTROL_FIX_SESSION_NOV12.md` - Full session report
- `AGENT_BUILDER_TESTING_COMPLETE.md` - Original bug report
- `CHART_CONTROL_IMPLEMENTATION_COMPLETE.md` - Architecture docs
- `CHART_CONTROL_SOLUTION.md` - Alternative HTTP Actions approach
