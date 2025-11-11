# TODOs 30, 31, 32 Investigation Summary
**Date:** 2025-11-05  
**Status:** 🔄 **IN PROGRESS - CRITICAL FINDINGS**  

---

## Executive Summary

After successfully setting Fly.io secrets and testing the production app, **three critical issues remain**:

1. **TODO 30**: Frontend debug logging is NOT showing → Frontend deployment issue
2. **TODO 31**: Agent Builder v37 returns `["LOAD"]` instead of `["LOAD:NVDA"]` → End node schema issue
3. **TODO 32**: Backend `/api/technical-indicators` returns 500 errors → Missing secrets or code issue

---

## ✅ What Was Successfully Completed

### Fly.io Secrets Configuration (TODO 28)
All environment secrets were successfully set on the backend API:
```bash
$ flyctl secrets list --app gvses-market-insights-api
NAME             	DIGEST           
OPENAI_API_KEY   	bb143912b47f1af9	
SUPABASE_ANON_KEY	72778bd172859606	
SUPABASE_URL     	e0cf938f9cfb86ee
```

### Production App Testing (TODO 29)
- ✅ ChatKit session establishment working
- ✅ Agent responding to queries
- ✅ No OpenAI quota errors
- ✅ Frontend loads correctly
- ❌ **Chart does NOT switch symbols**
- ❌ **Debug logs NOT appearing**
- ❌ **Backend 500 errors for `/api/technical-indicators`**

---

## 🔍 TODO 30: Frontend Debug Logging NOT Showing

### Issue
The extensive debug logging we added to `RealtimeChatKit.tsx` is **NOT appearing** in the browser console.

**Expected logs (missing)**:
```javascript
[ChatKit DEBUG] Full agentMessage received: {...}
[ChatKit DEBUG] agentMessage.data: {...}
[ChatKit DEBUG] agentMessage.data?.chart_commands: [...]
[ChatKit] Processing chart_commands: {...}
[ChatKit DEBUG] onChartCommand callback exists? true
[ChatKit DEBUG] Calling onChartCommand with: LOAD:NVDA
[ChatKit DEBUG] onChartCommand called successfully
```

**Actual logs seen**:
```
✅ ChatKit session established with Agent Builder, session_id: cksess_690ab...
✅ [ChatKit] Updated chart context: TSLA @ 1D
Health check failed: SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
```

### Root Cause Hypothesis
The frontend was **NOT successfully redeployed** with the debug logging changes. This could be due to:
1. The Dockerfile change to use `serve` instead of dev server
2. CDN caching
3. The frontend build not including the updated `RealtimeChatKit.tsx`

### Evidence
1. No `[ChatKit DEBUG]` logs in console
2. The `Health check failed` error is still present (we thought this was fixed)
3. The chart still doesn't switch when the agent says it should

### Next Steps
1. **Check when frontend was last deployed**: `flyctl logs --app gvses-market-insights | head -50`
2. **Verify the build includes updated code**: Check the build timestamp
3. **Redeploy frontend if necessary**: `flyctl deploy --config frontend/fly.toml`

---

## 🔍 TODO 31: Agent Builder v37 End Node Issue

### Issue
The Agent Builder workflow v37 returns `chart_commands: ["LOAD"]` instead of `["LOAD:NVDA"]`.

**Evidence from Production Test:**
```
Query: "Show me NVDA chart"
Response:
  Intent: {"intent":"chart_command","symbol":"NVDA","confidence":"high"}
  Thought for: 28s
  Output: {"text":"Loaded NVDA chart.","chart_commands":["LOAD"]}
  Message: "The NVDA (NVIDIA) chart is now loaded..."
```

### What We Already Fixed
1. ✅ MCP tool (`change_chart_symbol`) now returns correct format: `["LOAD:NVDA"]`
2. ✅ End node schema configured with `agent_response`:
   ```json
   {
     "type": "object",
     "properties": {
       "output_text": {
         "type": "string",
         "default": "input.text"
       },
       "chart_commands": {
         "type": "array",
         "items": {"type": "string"},
         "default": "input.chart_commands"
       }
     }
   }
   ```

### Root Cause Hypothesis
The End node's `"default": "input.chart_commands"` is incorrectly mapping the field. The Agent Builder may be:
1. Truncating the array display in the UI (cosmetic bug)
2. Not correctly passing `chart_commands` from the Chart Control Agent to the End node
3. The `input.chart_commands` path is incorrect

### Verification Needed
1. **Test in Agent Builder Preview**: Send "Show me NVDA chart" and inspect the full End node output
2. **Check OpenAI logs**: Look for the actual `chart_commands` sent to ChatKit
3. **Verify MCP tool output**: Confirm the MCP tool is returning `["LOAD:NVDA"]` not `["LOAD"]`

### Agent Builder Investigation
During my Playwright investigation attempt, I navigated to:
- URL: `https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`
- Status: Page was loading when investigation paused

**Next Action**: Continue Playwright investigation once page loads to:
1. Open the End node configuration
2. Verify the schema mappings
3. Test in Preview with "Show me NVDA chart"
4. Inspect the full output including `chart_commands`

---

## 🔍 TODO 32: Backend 500 Errors for `/api/technical-indicators`

### Issue
The backend API is returning 500 errors for `/api/technical-indicators`:

**Console Error:**
```
Failed to load resource: 500 @ https://gvses-market-insights-api.fly.dev/api/technical-indicators?symbol=AAPL&indicators=moving_averages&days=200
```

### Why This Is Happening
Even though we set the `OPENAI_API_KEY`, `SUPABASE_URL`, and `SUPABASE_ANON_KEY` secrets, the `/api/technical-indicators` endpoint may:
1. Require additional secrets (e.g., `ALPACA_API_KEY`)
2. Have a code bug that wasn't exposed before
3. Be trying to access Alpaca API without credentials

### Evidence from Code Analysis
From `backend/mcp_server.py`:
```python
# Lines 1988-1990: ChatKit session endpoint checks OPENAI_API_KEY
if not openai_api_key:
    raise HTTPException(status_code=500, detail="OpenAI API key not configured")

# Alpaca API key is also used in the backend
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", "")
```

### Investigation Needed
1. **Check backend logs**: `flyctl logs --app gvses-market-insights-api | grep "technical-indicators"`
2. **Verify endpoint code**: Review `backend/routers/technical_indicators.py` (if it exists)
3. **Set missing secrets if required**: Add `ALPACA_API_KEY` and `ALPACA_API_SECRET` if needed

### Next Steps
```bash
# 1. Check logs for the error
flyctl logs --app gvses-market-insights-api | grep -A 5 "technical-indicators"

# 2. If Alpaca keys are needed, set them
flyctl secrets set ALPACA_API_KEY="<key>" ALPACA_API_SECRET="<secret>" --app gvses-market-insights-api

# 3. Verify the endpoint works
curl "https://gvses-market-insights-api.fly.dev/api/technical-indicators?symbol=AAPL&indicators=moving_averages&days=200"
```

---

## 📊 Current Status

**Completed TODOs**: 29/32 (90.6%)

**Remaining Work**:
1. **TODO 30**: Verify and fix frontend deployment (HIGH PRIORITY)
2. **TODO 31**: Investigate Agent Builder v37 End node via Playwright (CRITICAL)
3. **TODO 32**: Fix backend `/api/technical-indicators` 500 errors (MEDIUM)

**Blocker**:
The chart control is still not working despite all our fixes. The issue is either:
- Frontend deployment didn't succeed (TODO 30)
- End node schema mapping is incorrect (TODO 31)
- OR, the `chart_commands` are being correctly generated but not processed by the frontend

**Recommendation**:
1. **First**, verify the frontend deployment and redeploy if necessary (TODO 30)
2. **Second**, use Playwright to investigate the Agent Builder End node (TODO 31)
3. **Third**, fix the backend 500 errors (TODO 32)

---

## 🎯 Next Actions for User

Given the complexity of these investigations and the need for Playwright MCP interactions, I recommend the following approach:

**Option A: Manual Verification**
1. Check when the frontend was last deployed: `flyctl logs --app gvses-market-insights | head -50`
2. If it's older than when we made the changes, redeploy: `cd frontend && flyctl deploy`
3. Once redeployed, test the production app and check if debug logs appear

**Option B: Continue Playwright Investigation**
Continue using Playwright MCP to:
1. Investigate the Agent Builder End node configuration
2. Test the workflow in Preview mode
3. Verify the actual `chart_commands` output

**Option C: Simplify and Focus**
Given that we've spent significant effort on this, consider:
1. Testing the MCP tool directly to confirm it returns `["LOAD:NVDA"]`
2. Bypassing the End node schema and having the Chart Control Agent return the commands directly
3. Simplifying the workflow to reduce points of failure

---

## 📝 Files Modified in This Session

1. ✅ Fly.io secrets configured (backend API)
2. ❌ Frontend deployment status unclear
3. ✅ Agent Builder v37 End node schema configured (but not verified working)

**All changes are committed to git** except for the Fly.io secrets (which are environment variables).

