# Debug Logging Deployed - HTTP 405 Investigation

**Date**: November 13, 2025, 1:45 AM
**Status**: 🚀 Debug logging deployed, awaiting Agent Builder test

---

## What Was Done

Added comprehensive debug logging to `/backend/mcp_server.py` (POST endpoint) that captures:

### Logged Information
```python
# For every POST request to /api/mcp, we now log:
1. Request method
2. Full URL
3. Client IP address
4. ALL request headers (with auth token masked)
5. Request body length
6. Request body content (first 500 chars)
7. Parsed JSON-RPC method
8. Parsed JSON-RPC ID
```

### Example Log Output
```
================================================================================
MCP HTTP POST REQUEST RECEIVED
Method: POST
URL: https://gvses-market-insights.fly.dev/api/mcp
Client: 54.187.123.45
Headers:
  host: gvses-market-insights.fly.dev
  user-agent: OpenAI-Agent-Builder/1.0
  authorization: Bearer fo1_LfBVrKP5...
  content-type: application/json
  accept: application/json, text/event-stream
Body length: 89 bytes
Body content: {"jsonrpc":"2.0","method":"tools/list","id":1}
JSON-RPC Method: tools/list
JSON-RPC ID: 1
================================================================================
```

---

## Next Steps

### 1. Test from Agent Builder (YOU DO THIS)
1. Open Agent Builder: https://platform.openai.com/agent-builder
2. Navigate to Chart Control Agent workflow
3. Try to add/configure the MCP server: `https://gvses-market-insights.fly.dev/api/mcp`
4. Or test in Preview mode with: "show me Apple"

### 2. Check Fly.io Logs (I'LL DO THIS)
```bash
fly logs --app gvses-market-insights
```

Look for the debug logs starting with:
```
================================================================================
MCP HTTP POST REQUEST RECEIVED
```

### 3. Analyze What Agent Builder Sends

The logs will show EXACTLY what Agent Builder is sending:
- Is it sending POST or GET first?
- What headers is it including?
- What authentication format?
- What JSON-RPC method? (`initialize` vs `tools/list`)
- What Accept headers?

### 4. Root Cause Identification

Based on the logs, we'll identify:
- **If no logs appear**: Agent Builder isn't reaching our backend (Fly.io proxy issue?)
- **If 401 error**: Auth token format mismatch
- **If 400 error**: Request format issue
- **If we see GET attempt**: Agent Builder is trying old HTTP+SSE transport first

---

## Hypothesis Testing

### Hypothesis 1: POST Fails, Falls Back to GET
**Expected logs**:
```
MCP HTTP POST REQUEST RECEIVED
Method: POST
... then 401 or 400 error ...
[No subsequent logs from our GET handler]
```
**Meaning**: Agent Builder tries POST, it fails, then tries GET and reports that 405

### Hypothesis 2: Agent Builder Uses GET First
**Expected logs**:
```
[No POST logs]
[GET endpoint returns 405]
```
**Meaning**: Agent Builder is configured to use old HTTP+SSE transport

### Hypothesis 3: Authentication Issue
**Expected logs**:
```
MCP HTTP POST REQUEST RECEIVED
...
authorization: [something unexpected]
...
[Then 401 error logged]
```
**Meaning**: Auth token format doesn't match our validation

### Hypothesis 4: Fly.io Proxy Blocking
**Expected logs**:
```
[No logs at all]
```
**Meaning**: Requests never reach our application

---

## How to View Logs

### Real-time Logs
```bash
fly logs --app gvses-market-insights
```

### Filter for MCP Requests
```bash
fly logs --app gvses-market-insights | grep "MCP HTTP"
```

### Last 100 Lines
```bash
fly logs --app gvses-market-insights | tail -100
```

---

## Deployment Status

**Deployment Command**: `fly deploy`
**Expected Duration**: 2-3 minutes
**Version**: Will be v95 (after current v94)

Check deployment status:
```bash
fly status --app gvses-market-insights
```

---

## Files Modified

1. **`backend/mcp_server.py`** (lines 2747-2785)
   - Added comprehensive debug logging
   - Fixed duplicate body read issue
   - Enhanced error messages

2. **`HTTP_405_INVESTIGATION_ULTRATHINK.md`**
   - Complete investigation analysis

3. **`DEBUG_LOGGING_DEPLOYED.md`**
   - This file - deployment summary

---

## Success Criteria

After deployment and Agent Builder test:
- ✅ Logs show Agent Builder's actual request
- ✅ We identify root cause of 405 error
- ✅ We know exactly what to fix

---

## Important Notes

1. **Logs are temporary**: Debug logs will be removed after we fix the issue
2. **Auth token masked**: Only first 20 chars logged for security
3. **500 char limit**: Body content truncated to first 500 characters
4. **All requests logged**: Every POST to /api/mcp will generate logs

---

## When to Remove Debug Logging

After we:
1. Identify the root cause
2. Implement the fix
3. Verify Agent Builder connection works
4. Document the solution

Then remove lines 2747-2785 to clean up production code.
