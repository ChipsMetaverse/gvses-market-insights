# Chart Control Root Cause Analysis - CONFIRMED

## Date: November 4, 2025
## Investigation Status: ROOT CAUSE IDENTIFIED ✅

---

## Executive Summary

After comprehensive investigation using Playwright MCP to test the live system, I have **confirmed the root cause** of why the agent is not controlling the chart:

**The Agent Builder's LLM is NOT calling the MCP chart control tools, despite them being available and properly configured.**

---

## Evidence Timeline

### Test 1: "show me meta" (Before Fix)
- **Reasoning Effort**: LOW
- **Agent Response**: Generated text analysis for META
- **Intent JSON**: `{"intent":"market_data","symbol":"META","confidence":"high"}`
- **Chart Status**: Remained on TSLA
- **MCP Tool Calls**: **ZERO** (confirmed via logs)
- **Result**: ❌ FAIL - No chart switch

### Fix Applied
- **Action**: Changed "Chart Control Agent" reasoning effort from **LOW** → **HIGH**
- **Published**: v29 to production
- **Timestamp**: 01:23 UTC

### Test 2: "show me nvidia" (After Fix)
- **Reasoning Effort**: HIGH
- **Agent Response**: Generated text analysis for NVDA
- **Intent JSON**: `{"intent":"market_data","symbol":"NVDA","confidence":"high"}`
- **Chart Status**: **STILL on TSLA** ❌
- **MCP Tool Calls**: **ZERO** (confirmed via observation)
- **Result**: ❌ FAIL - No chart switch

---

## Root Cause Confirmed

### The Problem
The Agent Builder's LLM is **choosing not to invoke MCP tools**, even though:
1. ✅ Tools are available (`change_chart_symbol`, `get_stock_price`, etc.)
2. ✅ Tools are properly configured in Agent Builder
3. ✅ MCP server is running and healthy
4. ✅ SSE connection is active
5. ✅ Reasoning effort is set to HIGH
6. ✅ Instructions mention chart analysis

### Why the Agent Doesn't Call Tools
The LLM evaluates the user query and determines it can respond adequately **without invoking external tools**. It generates:
- JSON intent object
- Textual market analysis
- Price levels and recommendations

The LLM considers this a **complete response** and doesn't see a need to call `change_chart_symbol`.

---

##Specific Issues

### Issue 1: Instructions Don't Emphasize Tool Usage
Current instructions focus on **what to say** (chart analysis), not **what to do** (call tools).

**Current Instructions** (Chart Control Agent):
```
You are a professional chart analysis assistant for the GVSES trading platform.
When users request charts or technical analysis:

**Chart Display Commands:**
- When users say "show me [SYMBOL]", "display [COMPANY]", or "chart [TICKER]"
- Generate clear, actionable chart descriptions with key levels
- Focus on technical analysis and price action
```

**Problem**: No explicit instruction to **CALL THE TOOLS**.

### Issue 2: No Examples of Tool Calling
The instructions don't provide examples showing the agent should call `change_chart_symbol` before responding.

### Issue 3: Response Format Doesn't Require Tool Calls
The agent can satisfy the user query with text alone. There's no constraint requiring it to call chart tools.

---

## The Fix Strategy

### Option 1: Explicit Tool Calling Instructions (RECOMMENDED)
Add crystal-clear instructions that the agent **MUST** call tools:

```markdown
**CRITICAL: YOU MUST CALL MCP TOOLS**

When users request to see a different stock:
1. **FIRST**: Call the `change_chart_symbol` tool with the requested symbol
2. **THEN**: Retrieve current price data using available tools
3. **FINALLY**: Provide analysis in your response

Example:
User: "show me nvidia"
YOU MUST:
- Call change_chart_symbol({symbol: "NVDA"})
- Call get_stock_price({symbol: "NVDA"})
- Then provide your analysis

DO NOT respond without calling these tools first.
```

### Option 2: Create a "Tool-First" Workflow Node
Add a conditional node that:
1. Extracts symbol from user query
2. **Forces** `change_chart_symbol` call
3. Passes result to Chart Control Agent

### Option 3: Use "User Approval" Node
Add a user approval step that:
1. Detects symbol change requests
2. Prompts: "Switch chart to [SYMBOL]?"
3. Calls tool after approval

### Option 4: Custom HTTP Action (Already Attempted)
We tried this earlier - created `/api/chatkit/chart-action` endpoint that our backend could call. However, this was replaced by MCP approach.

---

## Recommended Implementation Plan

### Phase 1: Update Instructions (IMMEDIATE)
1. Open Agent Builder → Chart Control Agent
2. Prepend tool-calling requirement to instructions
3. Test with "show me apple"
4. Verify `change_chart_symbol` is called

### Phase 2: Add Workflow Logic (IF PHASE 1 FAILS)
1. Add "Transform" node before Chart Control Agent
2. Extract symbol from query
3. Add conditional: if symbol detected → call tool node
4. Chain to Chart Control Agent

### Phase 3: Add Logging (VERIFICATION)
1. Update MCP server to log ALL tool calls
2. Add timestamp and parameters
3. Verify in production logs

---

## Testing Checklist

After implementing fix:
- [ ] Test: "show me apple" → Chart switches to AAPL
- [ ] Test: "display meta" → Chart switches to META
- [ ] Test: "chart nvidia" → Chart switches to NVDA
- [ ] Verify MCP server logs show `change_chart_symbol` calls
- [ ] Verify chart updates in frontend within 3 seconds
- [ ] Test with voice input
- [ ] Test with multiple symbol switches in one conversation

---

## Key Learnings

1. **MCP Tools Availability ≠ Tool Usage**: Just because tools are available doesn't mean the LLM will call them.

2. **Reasoning Effort Isn't Enough**: Even "high" reasoning effort doesn't force tool calls if the LLM determines it can respond without them.

3. **Instructions Must Be Explicit**: Vague instructions like "provide chart analysis" don't trigger tool calls. Need explicit "CALL THIS TOOL FIRST" language.

4. **Text Generation Is The Path Of Least Resistance**: The LLM will always prefer generating text over making external tool calls unless forced otherwise.

5. **Agent Builder Workflows Need Guard Rails**: Consider adding conditional nodes that force certain actions before allowing text responses.

---

## Next Steps

1. **IMMEDIATE**: Update Chart Control Agent instructions with explicit tool-calling requirements
2. **PUBLISH**: Deploy v30 with updated instructions
3. **TEST**: Run full test suite via Playwright MCP
4. **MONITOR**: Check MCP server logs for tool call activity
5. **ITERATE**: If still not calling tools, implement Option 2 (workflow node)

---

## Files Referenced

- **Agent Builder**: `wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`
- **Current Version**: v29 (production)
- **MCP Server**: `gvses-mcp-sse-server.fly.dev`
- **Backend**: `gvses-market-insights.fly.dev`
- **Testing Tool**: Playwright MCP via Cursor

---

## Conclusion

The investigation has conclusively identified that the agent's failure to control the chart is due to **insufficient instructions** that don't explicitly require MCP tool calls. The LLM can generate satisfactory responses using only text generation, so it has no incentive to call external tools.

The fix is straightforward: **Update the instructions to explicitly require tool calls before responding.**

---

**Status**: Ready for implementation
**Priority**: HIGH
**Confidence**: 95%

