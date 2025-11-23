# Chart Control Fix Session - November 12, 2025

## Session Objective
Fix the chart control system that was implemented in previous sessions but wasn't working in production.

---

## Issues Identified

### Issue #1: Backend Rate Limiting ✅ FIXED
**Problem**: Frontend polling endpoint `/api/chart/commands` was being rate-limited to 10 requests/minute, but frontend polls every 1 second (60 requests/minute).

**Solution**: Modified `backend/config/rate_limits.py` to add explicit endpoint mapping:
```python
# Chart control - Read operations (polling endpoints need high limits)
"/api/chart/commands": HEALTH_LIMITS,  # Frontend polls every 1s (120 requests/minute)
```

**Status**: ✅ Deployed to production via `fly deploy`

---

### Issue #2: Intent Classifier Missing Examples ✅ FIXED
**Problem**: "show me [symbol]" commands were being classified as `company-info` instead of `chart_command`.

**Solution**: Updated Intent Classifier instructions in Agent Builder v50 with explicit examples:

**Category 2 (chart_command)** now includes:
```
2. "chart_command" - Chart display and control requests
   Examples:
   - "show me AAPL"
   - "display Tesla"
   - "chart NVDA"
   - "switch to MSFT"
   - "show me Apple"
   - "load PLTR"
```

**Category 6 (company-info)** now clarifies:
```
6. "company-info" - Company business information (NOT chart display requests)
   Examples:
   - "tell me about Apple's business"
   - "what does Tesla do?"
   - "explain Microsoft's products"
```

**Status**: ✅ Published as Agent Builder workflow v50 (production)

---

### Issue #3: Intent Classifier JSON Visible to Users ❌ STILL NOT FIXED
**Problem**: Users are seeing raw JSON output from Intent Classifier instead of natural language responses from Chart Control Agent.

**Test Results**:
- Input: "show me Apple"
- Expected: Natural language analysis + chart switches to AAPL
- Actual: `{"intent":"chart_command","symbol":"AAPL","confidence":"high"}`

**Root Cause**: Workflow routing issue - The Intent Classifier output is being returned directly to ChatKit instead of routing through:
```
Intent Classifier → Transform → If/Else → Chart Control Agent → Natural Response
```

**Workflow Configuration Verified**:
- ✅ Transform Node: Mode = "Expressions", extracts `intent` field correctly
- ✅ If/Else Node: Condition = `intent in ["market_data", "chart_command"]`
- ✅ Routing: Chart Control Agent for market_data/chart_command, G'sves for else

**Why It's Still Broken**: Despite the workflow configuration being correct in Agent Builder v50, ChatKit is displaying the Intent Classifier JSON. This suggests:
1. ChatKit might be using a different workflow version
2. There might be a direct connection from Intent Classifier to End that's bypassing the routing
3. The workflow output configuration might be set to show intermediate results

**Status**: ❌ NOT FIXED - Requires further investigation

---

## Files Modified

### Backend
- `backend/config/rate_limits.py` - Added explicit chart polling endpoint mappings

### Agent Builder (OpenAI Platform)
- Workflow v50 (published to production)
- Intent Classifier instructions updated with explicit examples

---

## Test Results

### Backend Rate Limiting Test ✅ PASS
- Frontend ChartPoller logs show: `[ChartPoller] Starting command polling`
- No HTTP 429 errors in console
- Polling every 1 second without rate limiting

### Intent Classification Test ⚠️ PARTIAL
- ✅ "show me Apple" correctly classified as `chart_command` with symbol `AAPL`
- ❌ JSON output shown to user instead of natural language response
- ❌ Chart did NOT switch to AAPL (MCP tool not called)

### End-to-End Flow Test ❌ FAIL
Expected Flow:
```
User: "show me Apple"
  ↓
Intent Classifier: {intent: "chart_command", symbol: "AAPL"}
  ↓
Transform: {intent: "chart_command"}
  ↓
If/Else: Routes to Chart Control Agent
  ↓
Chart Control Agent: Calls change_chart_symbol MCP tool
  ↓
Backend: Queues command
  ↓
Frontend Polling: Detects command
  ↓
Chart: Switches to AAPL ✅
  ↓
Agent: Returns natural analysis 📊
```

Actual Flow:
```
User: "show me Apple"
  ↓
Intent Classifier: {intent: "chart_command", symbol: "AAPL"}
  ↓
??? Workflow stops here ???
  ↓
User sees: {"intent":"chart_command","symbol":"AAPL","confidence":"high"} ❌
```

---

## Next Steps (Priority Order)

### 🔴 CRITICAL: Fix Workflow Routing
**Problem**: Intent Classifier JSON is being returned as final output

**Investigation Needed**:
1. Check if there's a direct edge from Intent Classifier to End node
2. Verify ChatKit is using workflow v50 (not an older version)
3. Check workflow output configuration settings
4. Test the workflow in Agent Builder's built-in test panel (not just ChatKit)

**Possible Solutions**:
1. Remove any direct Intent Classifier → End connections
2. Ensure "Include chat history" is properly configured
3. Check if there's a setting to hide intermediate outputs
4. Verify the final agents (Chart Control Agent, G'sves) are returning outputs correctly

### 🟡 HIGH: Test Agent Builder Test Panel
**Action**: Use Agent Builder's built-in Test Panel to verify workflow routing works correctly before testing in ChatKit

**Why**: This will help isolate whether the issue is:
- Workflow configuration (test panel would also fail)
- ChatKit integration (test panel works, ChatKit doesn't)

### 🟢 MEDIUM: Verify MCP Tool Connectivity
**Action**: Once workflow routing is fixed, verify Chart Control Agent can call the MCP tools

**Check**:
1. MCP server `Chart_Control_Backend` is connected
2. Tools are visible to the agent: `change_chart_symbol`, `set_chart_timeframe`, etc.
3. Backend logs show MCP tool calls when agent runs

---

## Session Duration
Approximately 1 hour

## Session Outcome
✅ 2 out of 3 issues fixed and deployed to production
❌ 1 critical issue remains: Workflow routing not working correctly
📋 Created comprehensive testing guide: `AGENT_BUILDER_TEST_GUIDE.md`

## Testing Guide Created
Since the OpenAI session expired during testing, I created a comprehensive guide:
- **File**: `AGENT_BUILDER_TEST_GUIDE.md`
- **Purpose**: Test workflow in Agent Builder Preview mode to isolate the issue
- **Includes**: Step-by-step instructions, expected vs actual results, diagnostic analysis
- **Next Action**: Follow the guide to test in Preview mode and determine if it's a workflow or ChatKit issue

---

## Related Documentation
- `CHART_CONTROL_TESTING_REPORT.md` - Original test report identifying the issues
- `CHART_CONTROL_IMPLEMENTATION_COMPLETE.md` - Complete architecture documentation
- `AGENT_BUILDER_TESTING_COMPLETE.md` - Documents the exact routing issue we're still seeing
- `AGENT_BUILDER_TEST_GUIDE.md` - **NEW**: Step-by-step testing guide for Agent Builder Preview mode

---

## Console Logs Evidence

### ✅ Frontend Polling Working
```
[LOG] [TradingDashboardSimple] Initializing chart command polling
[LOG] [ChartPoller] Starting command polling
[LOG] ✅ ChatKit session established with Agent Builder, session_id: cksess_6914782c...
```

### ❌ Workflow Routing Not Working
ChatKit Response:
```json
{"intent":"chart_command","symbol":"AAPL","confidence":"high"}
```

Expected Natural Language Response:
```
I've switched the chart to Apple Inc. (AAPL).

**Current Price**: $275.25 (+2.2%)

**Technical Picture**:
[Analysis based on indicators]

**Key Levels**:
- Resistance: $280
- Support: $270

**Trader's Takeaway**: [Actionable insight]
```

---

## Workflow Version History
- **v48**: Previous version with routing issues
- **v49**: Draft version created during this session
- **v50**: Published version with Intent Classifier examples ✅ (Current Production)

---

## Deployment Status
- ✅ Backend rate limiting fix: Deployed to production
- ✅ Intent Classifier examples: Published as v50 (production)
- ❌ Workflow routing: Still broken despite configuration being correct

---

## Recommendations
1. Test workflow in Agent Builder Test Panel before deploying to ChatKit
2. Check for any Agent Builder platform issues or recent changes
3. Consider alternative approaches if workflow routing continues to fail:
   - Use a single agent with routing logic in instructions
   - Implement routing in backend instead of Agent Builder
   - Use HTTP Actions instead of MCP Tools (as documented in CHART_CONTROL_SOLUTION.md)
