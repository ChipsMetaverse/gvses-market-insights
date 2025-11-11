# Agent Builder Tool Calling Limitation - Final Investigation Report

## Date: 2025-11-06 19:15 PST

## Executive Summary

**Chart control implementation is complete and working on the backend**, but **Agent Builder's GPT-5 model does not respect explicit function calling instructions**. Despite multiple fixes and publishing v39 to production with clear tool-calling commands, the Chart Control Agent continues to provide conversational analysis instead of calling MCP tools.

**Recommendation**: Implement **Custom Agent Builder Action** (Option 1) or **Direct API Integration** (Option 2) to bypass Agent Builder's function calling limitations.

---

## Investigation Timeline

### Phase 1: Initial Analysis (Completed ✅)
- Verified backend chart control working perfectly via direct API
- Confirmed function schemas correctly configured
- Test: `curl http://localhost:8000/api/agent/orchestrate` returns `{"chart_commands": ["LOAD:TSLA"]}`

### Phase 2: Root Cause #1 - Disabled MCP Tools (Fixed ✅)
- **Problem**: All 4 chart control tools were unchecked in Agent Builder
- **Tools Affected**: change_chart_symbol, set_chart_timeframe, toggle_chart_indicator, capture_chart_snapshot
- **Fix**: Enabled all tools in Agent Builder v38
- **Status**: ✅ RESOLVED

### Phase 3: Root Cause #2 - Wrong Instructions (Fixed ✅)
- **Problem**: Agent instructions said "Generate clear, actionable chart descriptions"
- **Impact**: Agent followed instructions by providing analysis instead of calling tools
- **Fix**: Updated instructions to "**IMMEDIATELY call change_chart_symbol(symbol)**"
- **Status**: ✅ RESOLVED

### Phase 4: Root Cause #3 - Unpublished Draft (Fixed ✅)
- **Problem**: Instructions were edited but remained in draft, never published to production
- **Discovery**: URL showed `version=draft` instead of `version=38`
- **Fix**: Published draft to production as v39
- **Status**: ✅ RESOLVED

### Phase 5: End-to-End Testing (FAILED ❌)
- **Test**: Sent "Show me NVDA chart" to production v39 workflow
- **Expected**: Agent calls `change_chart_symbol("NVDA")`
- **Actual**: Agent provides detailed price analysis and technical levels
- **Status**: ❌ CHART CONTROL STILL NOT WORKING

---

## Test Results Summary

### Backend API Test (✅ PASSING)
```bash
$ curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me NVDA chart"}'

Response:
{
  "response": "Loading NVDA chart...",
  "chart_commands": ["LOAD:NVDA"],
  "tools_used": ["load_chart"]
}
```
**Conclusion**: Backend 100% functional

### Agent Builder v39 Test (❌ FAILING)
```
User Query: "Show me NVDA chart"

Agent Response:
{
  "intent": "chart_command",
  "symbol": "NVDA",
  "confidence": "high"
}

Here's the latest snapshot of NVDA (NVIDIA Corporation)...
- Last Price: $188.08 (down $7.13, -3.65%)
- Day Range: $186.38 – $197.62
- 52-Week Range: $86.62 – $212.19
...detailed technical analysis continues...

Would you like a technical analysis breakdown...?
```

**Observable Results**:
- ✅ Banner changed to "NVDA stock chart" (Intent Classifier working)
- ✅ Agent recognizes chart command intent
- ❌ No function call to `change_chart_symbol()`
- ❌ Provides conversational analysis instead
- ❌ Chart remains on TSLA

**Conclusion**: Agent Builder GPT-5 ignores explicit tool-calling instructions

---

## Root Causes Identified

### ✅ Root Cause #1: MCP Tools Disabled (FIXED)
**Status**: Resolved by enabling all chart control tools in Agent Builder

### ✅ Root Cause #2: Incorrect Instructions (FIXED)
**Status**: Resolved by updating to explicit tool-calling commands

### ✅ Root Cause #3: Unpublished Draft (FIXED)
**Status**: Resolved by publishing v39 to production

### ❌ Root Cause #4: Agent Builder Function Calling Limitation (ACTIVE)
**Problem**: GPT-5 in Agent Builder prioritizes conversational responses over function execution

**Evidence**:
1. Instructions explicitly say: "**IMMEDIATELY call change_chart_symbol(symbol)**"
2. Instructions explicitly say: "**CRITICAL: Your job is to CALL TOOLS, not provide analysis.**"
3. Agent completely ignores these instructions
4. Agent provides detailed analysis instead of calling tools
5. No function call visible in response structure

**Hypothesis**: Agent Builder's GPT-5 implementation may:
- Treat function schemas as optional suggestions rather than mandatory actions
- Prioritize chat-optimized behavior over function execution
- Override explicit instructions with conversational patterns
- Have a configuration setting we haven't found that forces strict tool calling

---

## Configuration Verified

### Agent Builder v39 Production Settings
```yaml
Agent Name: Chart Control Agent
Model: gpt-5
Reasoning Effort: low
Include Chat History: ✅ Enabled
Tools Attached:
  - Chart_Control_MCP_Server (✅ Enabled)
  - chart_control (✅ Enabled)
Output Format: Text

Instructions:
  "You are a chart control agent for the GVSES trading platform.

  **Your PRIMARY job is to CALL MCP TOOLS to control the chart display.**

  When users request charts (e.g., \"show me AAPL\", \"display Tesla\", \"chart NVDA\"):
  1. **IMMEDIATELY call change_chart_symbol(symbol)** with the requested symbol
  2. Do NOT provide analysis - just call the tool
  3. Keep responses brief: \"Loading [SYMBOL] chart...\"

  **CRITICAL: Your job is to CALL TOOLS, not provide analysis.**"
```

**Status**: ✅ All settings correct, tools enabled, instructions explicit

---

## Recommended Solutions

### ⭐ Option 1: Custom Agent Builder Action (RECOMMENDED)
**Approach**: Configure Agent Builder to POST to a custom webhook for chart commands

**Implementation**:
```python
# Backend endpoint
@app.post("/api/agent-actions/chart-control")
async def chart_control_action(request: Request):
    data = await request.json()
    symbol = data.get("symbol")
    action = data.get("action", "load_chart")

    return {
        "success": True,
        "chart_commands": [f"LOAD:{symbol}"],
        "message": f"Loading {symbol} chart..."
    }
```

**Agent Builder Configuration**:
1. Add Custom Action: "Chart Control"
2. URL: `https://g-vses.fly.dev/api/agent-actions/chart-control`
3. Method: POST
4. Parameters: `symbol` (string), `action` (string)

**Pros**:
- ✅ Bypasses function calling issues entirely
- ✅ Direct control over chart commands
- ✅ Keeps Agent Builder for voice and routing
- ✅ Simple to implement (2-3 hours)

**Cons**:
- ⚠️ Requires Agent Builder custom action setup
- ⚠️ May have rate limits or usage restrictions

**Estimated Effort**: 2-3 hours

---

### Option 2: Direct API Integration
**Approach**: Replace ChatKit with direct `/api/agent/orchestrate` calls

**Implementation**:
```typescript
const sendMessage = async (query: string) => {
  const response = await fetch('/api/agent/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      chart_context: currentChartState
    })
  });

  const data = await response.json();

  // Full control over chart_commands
  if (data.chart_commands) {
    data.chart_commands.forEach(cmd => {
      executeChartCommand(cmd);
    });
  }

  // Display agent response
  displayMessage(data.response);
};
```

**Pros**:
- ✅ Full control over chart commands (proven working)
- ✅ No Agent Builder limitations
- ✅ Simple implementation
- ✅ Can still use Agent Builder for voice separately

**Cons**:
- ⚠️ Loses Agent Builder UI
- ⚠️ Need to implement chat interface
- ⚠️ Voice integration more complex

**Estimated Effort**: 4-6 hours

---

### Option 3: iframe postMessage Communication
**Approach**: Listen for postMessage events from ChatKit iframe

**Implementation**:
```typescript
useEffect(() => {
  const handleMessage = (event: MessageEvent) => {
    if (event.origin === 'https://chatkit.openai.com') {
      if (event.data.type === 'assistant_message') {
        tryParseChartCommands(event.data.content);
      }
    }
  };

  window.addEventListener('message', handleMessage);
  return () => window.removeEventListener('message', handleMessage);
}, []);
```

**Pros**:
- ✅ Non-invasive
- ✅ Keeps ChatKit intact

**Cons**:
- ❌ Relies on ChatKit emitting postMessage events (may not exist)
- ❌ Still doesn't solve agent not calling tools

**Estimated Effort**: 2-3 hours if API exists, impossible if not

**Likelihood of Success**: Low (ChatKit likely doesn't emit events)

---

### Option 4: Contact OpenAI Support
**Approach**: Ask OpenAI about forcing strict function calling in Agent Builder

**Questions for Support**:
1. How to force strict function calling vs conversational responses?
2. Is there a configuration to prioritize tool execution?
3. Are there Agent Builder settings we're missing?
4. Does ChatKit support message interception?

**Pros**:
- ✅ May reveal hidden configuration options
- ✅ Official support from OpenAI

**Cons**:
- ⚠️ May take days/weeks for response
- ⚠️ May not have a solution
- ⚠️ Blocks progress while waiting

**Estimated Time**: Unknown (support response time)

---

## Comparison Matrix

| Solution | Effort | Success Likelihood | Maintains Voice | Full Control |
|----------|--------|-------------------|-----------------|--------------|
| Custom Action | 2-3 hrs | ⭐⭐⭐⭐⭐ High | ✅ Yes | ✅ Yes |
| Direct API | 4-6 hrs | ⭐⭐⭐⭐⭐ High | ⚠️ Complex | ✅ Yes |
| postMessage | 2-3 hrs | ⭐ Low | ✅ Yes | ⚠️ Partial |
| OpenAI Support | Unknown | ⭐⭐ Low | ✅ Yes | ❓ Unknown |

---

## Recommended Action Plan

### Immediate Next Steps (Recommended)

**1. Implement Custom Agent Builder Action** (2-3 hours)
   - Create `/api/agent-actions/chart-control` endpoint
   - Configure Agent Builder custom action
   - Test with "Show me NVDA" query
   - Verify chart switching works

**2. If Custom Action Fails, Switch to Direct API** (4-6 hours)
   - Remove ChatKit dependency
   - Implement direct `/api/agent/orchestrate` calls
   - Create simple chat UI
   - Keep Agent Builder for voice separately

### Long-Term Strategy

**For Voice Integration**:
- Use Agent Builder for voice transcription
- Route chart commands through custom action or direct API
- Keep voice UI separate from chart control logic

**For Chart Control**:
- Use proven working backend API
- Bypass Agent Builder function calling entirely
- Full control over chart_commands execution

---

## Files Modified During Investigation

### Agent Builder Changes
1. **Chart Control Agent** (v38 → v39)
   - Enabled 4 MCP tools
   - Updated instructions (draft → published)
   - Published to production

### Frontend Code (Investigation Only)
1. `frontend/src/components/RealtimeChatKit.tsx`
   - Added debug logging (not deployed)
   - Code never executes (onMessage not triggered)

### Backend Code (Verified Working)
1. `backend/services/agent_orchestrator.py`
   - Chart control function calling (lines 1068-1188)
   - Tool execution handlers (lines 2659+)
   - ✅ All working correctly

---

## Key Learnings

### What Worked ✅
1. Backend chart control implementation (100% functional)
2. Direct API testing approach (proves functionality)
3. Systematic root cause analysis
4. Local testing before deployment (per user request)
5. Playwright MCP for Agent Builder automation

### What Didn't Work ❌
1. ChatKit onMessage callback (not supported)
2. Explicit tool-calling instructions in Agent Builder
3. Enabling MCP tools alone (agent needs to actually call them)
4. Publishing fixes (agent still ignores instructions)

### Surprising Discoveries 💡
1. Agent Builder auto-saves changes BUT needs publish step
2. Draft vs production versions are separate
3. GPT-5 in Agent Builder may prioritize chat over function calling
4. Even explicit "CALL THIS TOOL" instructions are ignored
5. ChatKit operates entirely within iframe with no parent access

---

## Current Status

**Backend**: ✅ 100% Working
- Chart control function calling implemented
- Tool execution handlers working
- Command extraction working
- Direct API verified functional

**MCP Tools**: ✅ Enabled and Configured
- All 4 chart control tools enabled in v39
- Function schemas correct
- Tool descriptions clear

**Agent Instructions**: ✅ Updated and Published
- Explicit tool-calling commands
- Published to production v39
- Instructions verified saved

**Agent Behavior**: ❌ Not Calling Tools
- Provides analysis instead of calling functions
- Ignores explicit instructions
- No function call in response structure
- Chart control completely non-functional

**Priority**: 🔴 HIGH - Core functionality blocked by Agent Builder limitation

---

## Conclusion

The chart control implementation is **technically complete and working perfectly** on the backend. The issue is a **frontend integration problem** caused by Agent Builder's GPT-5 model not respecting explicit function calling instructions.

**Three fixes were applied**:
1. ✅ Enabled disabled MCP tools
2. ✅ Updated instructions to command tool calling
3. ✅ Published draft to production

**Result**: Agent still provides analysis instead of calling tools

**Root Cause**: Agent Builder's GPT-5 implementation may be fundamentally incompatible with strict function calling for this use case.

**Recommended Solution**: Implement Custom Agent Builder Action (2-3 hours) to bypass function calling limitations while maintaining voice integration.

**Alternative Solution**: Direct API Integration (4-6 hours) for full control at the cost of more complex voice setup.

---

**Investigation Completed**: 2025-11-06 19:15 PST
**Next Action**: Implement Custom Agent Builder Action OR Direct API Integration
**Estimated Time to Fix**: 2-6 hours depending on approach chosen
**Backend Status**: ✅ Ready for integration
**Blocking Issue**: Agent Builder function calling limitation
