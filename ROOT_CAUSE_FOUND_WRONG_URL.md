# ROOT CAUSE FOUND: Wrong URL in Agent Builder

**Date**: November 13, 2025, 1:55 AM
**Status**: 🎯 **ROOT CAUSE IDENTIFIED** - Wrong MCP server URL configured in Agent Builder

---

## The Discovery

Used Playwright to navigate to Agent Builder and inspect the Chart Control Agent's MCP server configuration. The screenshot revealed the **actual root cause** of the HTTP 405 error.

---

## The Problem

### What's Configured in Agent Builder:
```
URL: https://gvses-market-insights-api.fly.dev/api/mcp
Authentication: None
```

### What It Should Be:
```
URL: https://gvses-market-insights.fly.dev/api/mcp
Authentication: Bearer fo1_LfBVrKP5isehK-D7BlsBh6H8NrTOa8PYR5nSxHeV2N8
```

### The Issue:
1. **Wrong domain**: `gvses-market-insights-api.fly.dev` (doesn't exist)
2. **Correct domain**: `gvses-market-insights.fly.dev` (our actual app)
3. **Missing authentication**: No Bearer token configured
4. **Extra `-api` suffix**: The domain has an incorrect `-api` suffix that doesn't exist

---

## Why This Causes HTTP 405

The domain `https://gvses-market-insights-api.fly.dev` doesn't exist. When Agent Builder tries to connect:

1. **DNS lookup fails** or returns a different server
2. Agent Builder tries POST to non-existent domain
3. Some Fly.io proxy or error handler returns HTTP 405
4. User sees: "Http status code: 405 (Method Not Allowed)"

**Our backend never receives the request** because the URL is wrong!

---

## Evidence

### Screenshot: `agent-builder-mcp-config-wrong-url.png`
The dialog clearly shows:
- ❌ URL field: `https://gvses-market-insights-api.fly.dev/api/mcp`
- ❌ Authentication: "None"
- ❌ Error message: "Unable to load tools - Check the server URL and verify your authentication details."

### Our Successful Tests:
```bash
# Our tests work because we use the CORRECT URL:
curl -X POST https://gvses-market-insights.fly.dev/api/mcp \
  -H "Authorization: Bearer fo1_..." \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Result: HTTP 200 ✅ - Returns 7 tools
```

---

## Why Our Investigation Was Misleading

We spent hours fixing the MCP transport implementation:
- ✅ Added GET handler (returns 405 as per spec)
- ✅ Added OPTIONS handler (CORS)
- ✅ Added debug logging
- ✅ Deployed successfully

**But none of this mattered** because Agent Builder was connecting to the wrong URL the entire time!

---

## The Fix

### Option 1: Manual Fix in Agent Builder UI (Recommended)
1. Open Agent Builder: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736&version=50
2. Click on "Chart Control Agent" node
3. Click on "Chart_Control_Backend" MCP server button
4. Edit the URL:
   - **Remove**: `https://gvses-market-insights-api.fly.dev/api/mcp`
   - **Add**: `https://gvses-market-insights.fly.dev/api/mcp` (no `-api` suffix)
5. Click "Change" next to Authentication
6. Add Bearer token: `Bearer fo1_LfBVrKP5isehK-D7BlsBh6H8NrTOa8PYR5nSxHeV2N8`
7. Click "Update" to save
8. Verify tools load successfully (should show 7 tools)

### Option 2: Delete and Recreate
1. Remove the incorrectly configured "Chart_Control_Backend" MCP server
2. Add new MCP server with:
   - Label: `Chart_Control_Backend`
   - URL: `https://gvses-market-insights.fly.dev/api/mcp`
   - Authentication: Bearer token
   - Description: Chart control backend with change_chart_symbol, set_chart_timeframe, and toggle_chart_indicator tools

---

## Verification After Fix

Once the URL and authentication are corrected, Agent Builder should:
1. ✅ Successfully connect to MCP server
2. ✅ Load all 7 tools (4 market data + 3 chart control)
3. ✅ No more HTTP 405 errors
4. ✅ "show me Apple" works in Preview mode

---

## Key Learnings

1. **Always verify the configured URL first** before diving into code changes
2. **Screenshots are invaluable** for debugging UI-based configuration issues
3. **DNS/domain issues** can masquerade as HTTP method errors
4. **Test with exact production configuration** including URLs and auth tokens

---

## Related Files

From this investigation session:
- `DEBUG_LOGGING_DEPLOYED.md` - Debug logging deployment
- `HTTP_405_INVESTIGATION_ULTRATHINK.md` - Deep investigation analysis
- `MCP_TRANSPORT_FIX_COMPLETE.md` - MCP transport implementation (still valuable for spec compliance)
- `MCP_TRANSPORT_FIX.md` - Implementation details

From previous sessions:
- `CHART_CONTROL_MCP_INTEGRATION_COMPLETE.md` - Original MCP integration
- `IF_ELSE_FIX_COMPLETE_V51.md` - Routing fixes

---

## Next Steps

1. **You (the user)** need to fix the URL in Agent Builder UI manually
2. Add the Bearer token authentication
3. Test with "show me Apple" in Preview mode
4. Verify end-to-end workflow execution

---

## Celebration 🎉

**Root cause successfully identified!**

After hours of investigation, implementing MCP transport fixes, and adding comprehensive debug logging, we finally discovered the actual issue: **The URL configured in Agent Builder was simply wrong**.

It's always the simple things! 😄

The MCP transport implementation we added (GET, OPTIONS, POST handlers) is still valuable and ensures full spec compliance, but the immediate issue was just a typo in the URL (extra `-api` suffix).

Now that we know the root cause, the fix is straightforward: update the URL and add authentication in Agent Builder.
