# FIX AGENT BUILDER - 15 Minute Solution

## 🎯 Problem
Agent Builder has `chart_control` tool defined, but it's **not configured to call our backend**.

## ✅ Solution
Add HTTP endpoint configuration to the `chart_control` tool.

---

## 📋 Step-by-Step Instructions (15 minutes)

### Step 1: Open Agent Builder (2 min)
Go to: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736

### Step 2: Select Chart Control Agent (1 min)
- Click on the "Chart Control Agent" node in the workflow canvas
- Configuration panel opens on the right

### Step 3: Find chart_control Tool (1 min)
- Scroll to "Tools" section
- Look for `chart_control` (Custom tool)

### Step 4: Add HTTP Endpoint (5 min)

**If there's an "Edit" or "Configure" button:**
1. Click "Edit" on `chart_control` tool
2. Look for "Endpoint" or "API Configuration" section
3. Add these settings:

```
Endpoint URL: https://gvses-market-insights.fly.dev/api/chatkit/chart-action
Method: POST
Headers: 
{
  "Content-Type": "application/json"
}
Body Template:
{
  "query": "{{input.query}}",
  "session_id": "{{session_id}}",
  "user_id": "{{user_id}}",
  "metadata": {}
}
```

4. Save the tool configuration

**If there's no Edit button, the tool might be configured via MCP:**
1. Look for "MCP Server" configuration
2. Check if `Chart_Control_MCP_Server` exists
3. Verify its endpoint points to: `https://gvses-market-insights.fly.dev`
4. If not, update it

### Step 5: Update Agent Instructions (3 min)

In the "Instructions" field for Chart Control Agent, ensure it says:

```
When users ask about charts, support/resistance, patterns, or technical analysis:

ALWAYS call the chart_control tool with their exact query.

Examples of queries that need chart_control:
- "draw support and resistance"
- "analyze this chart"
- "show me patterns"
- "what patterns do you see"
- "draw trendlines"

Pass the user's query directly to chart_control and display the response.
```

### Step 6: Publish (2 min)
1. Click "Publish" button (top right)
2. Confirm "Deploy to production" is checked
3. Click "Publish" to deploy

### Step 7: Verify (1 min immediately + monitoring)

**Immediate Test in Agent Builder:**
1. Click "Test" or "Preview" button
2. Type: "draw support and resistance for TSLA"
3. Check if response includes chart commands

**Production Test:**
```bash
# Terminal 1: Watch backend logs
flyctl logs -a gvses-market-insights -f | grep CHATKIT

# Terminal 2 or Browser:
# - Open https://gvses-market-insights.fly.dev/
# - Load TSLA chart
# - Open ChatKit
# - Type: "draw support and resistance"

# Expected in Terminal 1:
[CHATKIT ACTION] Query: draw support and resistance
[CHATKIT ACTION] Session: <session_id>
[CHATKIT ACTION] Generated 9 chart commands
```

---

## 🧪 Quick Verification Commands

### Test 1: Backend Endpoint (Already Verified ✅)
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "draw support and resistance for TSLA",
    "session_id": "test",
    "metadata": {"chart_context": {"symbol": "TSLA", "timeframe": "1D"}}
  }' | jq .success

# Expected: true
```

### Test 2: Agent Builder Calling Backend (After Fix)
```bash
# Watch logs while testing in ChatKit:
flyctl logs -a gvses-market-insights -f | grep "CHATKIT ACTION"

# If you see logs = SUCCESS ✅
# If no logs = Agent Builder still not configured ❌
```

---

## 🚨 Alternative: If Agent Builder UI Doesn't Allow HTTP Config

Some versions of Agent Builder may not have a UI for configuring HTTP endpoints on Custom tools.

**In that case, we have 2 options:**

### Option A: Use OpenAI API Directly from Backend
Instead of relying on Agent Builder routing, we intercept ChatKit requests in our backend and handle function calling ourselves.

**Pros:**
- Full control
- Guaranteed to work
- No Agent Builder config needed

**Cons:**
- More backend code
- Bypasses Agent Builder workflow

### Option B: Create an MCP Server
Create a simple MCP server that acts as a bridge between Agent Builder and our HTTP endpoint.

**Would need:**
- New repo: `gvses-mcp-chart-control`
- Expose MCP protocol
- Forward to our HTTP endpoint
- Deploy to Fly.io

---

## 📊 Expected Results After Fix

### Before Fix ❌
```
User: "draw support and resistance"
↓
ChatKit sends to Agent Builder
↓
Agent Builder processes query
↓
chart_control tool has no endpoint
↓
Function call goes nowhere
↓
Agent returns generic text
↓
❌ No chart commands, no drawings
```

### After Fix ✅
```
User: "draw support and resistance"
↓
ChatKit sends to Agent Builder
↓
Agent Builder detects chart intent
↓
Calls chart_control with query
↓
HTTP POST to our backend /api/chatkit/chart-action
↓
Backend processes with agent orchestrator
↓
Returns chart commands: SUPPORT:, RESISTANCE:, etc.
↓
Agent Builder sends response to ChatKit
↓
Frontend parses commands
↓
✅ Lines appear on chart!
```

---

## 💡 Key Insights

1. **Backend is 100% ready** - No code changes needed
2. **Only missing piece** - Agent Builder HTTP routing config
3. **Quick fix** - 15 minutes of configuration
4. **High impact** - Unlocks entire chart control feature

---

## 🎯 Success Criteria

After implementing this fix, you should see:

✅ Backend logs showing `[CHATKIT ACTION]` entries  
✅ Agent responses include `SUPPORT:` and `RESISTANCE:` commands  
✅ Frontend console shows "Parsed chart commands"  
✅ Chart displays support/resistance lines  
✅ Symbol auto-switches when analyzing different stocks  

---

## 📞 If You Need Help

**Can't find the HTTP endpoint config in Agent Builder?**
- Take a screenshot of the chart_control tool configuration
- Check if it's an MCP tool or Function Calling tool
- We may need to implement Option A or B above

**Agent Builder publishes but still not working?**
- Check backend logs: `flyctl logs -a gvses-market-insights -f`
- If no `[CHATKIT ACTION]` logs appear, the routing is still not configured
- May need to create a custom MCP server bridge

---

**Time to Fix**: 15 minutes  
**Difficulty**: Low (configuration only)  
**Impact**: HIGH (restores chart control)  
**Next Step**: Open Agent Builder and configure HTTP endpoint NOW

---

**Last Updated**: November 3, 2025 02:57 UTC  
**Status**: Ready to implement  
**Blocking**: None - backend ready, just needs Agent Builder config

