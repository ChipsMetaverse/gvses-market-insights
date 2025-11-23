# HTTP 405 Error Investigation - Ultrathink Analysis

**Date**: November 13, 2025
**Status**: 🔍 DEEP INVESTIGATION IN PROGRESS

---

## Problem Statement

Despite successfully implementing MCP Streamable HTTP transport with all tests passing:
- ✅ GET returns 405 (correct per spec)
- ✅ OPTIONS returns 200 with CORS headers
- ✅ POST returns 200 with 7 tools

**Agent Builder still reports**: `Http status code: 405 (Method Not Allowed)`

---

## Key Findings from MCP Specification

### Streamable HTTP Transport Requirements

From https://modelcontextprotocol.io/specification/2025-03-26/basic/transports:

1. **Server MUST provide single endpoint supporting POST and GET**
   - Our implementation: ✅ Both methods present

2. **POST Requests (Client → Server)**
   - Client MUST include Accept header: `application/json, text/event-stream`
   - Server MUST return either `Content-Type: application/json` OR `Content-Type: text/event-stream`
   - Our implementation: ✅ Returns `application/json`

3. **GET Requests (SSE Listening)**
   - Client MAY issue GET to open SSE stream
   - Server MUST return `Content-Type: text/event-stream` OR HTTP 405
   - Our implementation: ✅ Returns 405 (we don't support server-initiated SSE)

4. **OPTIONS Requests (CORS)**
   - Not explicitly required by MCP spec, but needed for browser CORS
   - Our implementation: ✅ Returns 200 with proper headers

### OpenAI Agent Builder Requirements

From https://platform.openai.com/docs/guides/tools-connectors-mcp:

1. **Supported Transports**
   - "The Responses API works with remote MCP servers that support either the **Streamable HTTP** or the **HTTP/SSE transport protocols**"

2. **Transport Detection (Backwards Compatibility)**
   - Clients should POST InitializeRequest first
   - If POST succeeds → assume Streamable HTTP
   - If POST fails with 4xx (405/404) → try GET for old HTTP+SSE transport
   - If GET succeeds with SSE 'endpoint' event → use old transport

---

## Hypothesis: Why Agent Builder Reports 405

### Theory 1: POST Request Failing Silently
Agent Builder might be:
1. Sending POST InitializeRequest
2. Getting an error (not 200 OK) - possibly auth/validation issue
3. Falling back to GET (thinking it's old transport)
4. Getting our 405 from GET
5. **Reporting the GET's 405 as the final error**

### Theory 2: Authorization Header Issue
Our tests use:
```bash
-H "Authorization: Bearer fo1_LfBVrKP5isehK-D7BlsBh6H8NrTOa8PYR5nSxHeV2N8"
```

Agent Builder might be:
- Using different auth format
- Not sending auth header at all
- Sending expired token
- Being rejected by our middleware **before** reaching our handlers

### Theory 3: Fly.io Proxy/Nginx Interception
Fly.io might have:
- Reverse proxy that intercepts certain requests
- Different handling for browser requests vs. curl
- CORS preflight issues not visible in our tests
- Rate limiting or security middleware

### Theory 4: MCP Session Management
From spec:
- Server MAY assign `Mcp-Session-Id` at initialization
- Clients MUST include it in subsequent requests
- Server SHOULD respond with 400 Bad Request if session ID missing

Our implementation might not be properly handling:
- InitializeRequest flow
- Session ID assignment
- Session validation on subsequent requests

---

## Evidence Contradicting Current Hypothesis

### Our Tests Pass
```bash
# GET - Works correctly
curl -X GET .../api/mcp
→ HTTP 405, proper error message ✅

# OPTIONS - Works correctly
curl -X OPTIONS .../api/mcp
→ HTTP 200, CORS headers ✅

# POST - Works correctly
curl -X POST .../api/mcp -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
→ HTTP 200, 7 tools returned ✅
```

### Direct API Access Works
The MCP endpoint responds correctly to direct HTTP requests with proper authentication.

---

## Critical Questions

1. **What is Agent Builder actually sending?**
   - Can we capture Agent Builder's request headers?
   - What authentication format does it use?
   - What Accept headers does it send?

2. **Is there middleware blocking the request?**
   - Does Fly.io have a proxy that filters requests?
   - Are there rate limits being hit?
   - Is CORS middleware blocking browser requests?

3. **Is our InitializeRequest handling correct?**
   - Do we properly respond to initialization?
   - Do we correctly assign session IDs?
   - Are we following the MCP lifecycle?

4. **Is Agent Builder using old or new transport?**
   - Is it trying old HTTP+SSE first?
   - Does it properly fall back to Streamable HTTP?

---

## Next Steps for Investigation

### 1. Check Fly.io Logs (CRITICAL)
```bash
fly logs --app gvses-market-insights
```
Look for:
- Requests from Agent Builder IP
- 405 responses
- Auth failures
- Proxy/middleware rejections

### 2. Check Backend Request Logging
Add detailed logging to see EXACTLY what Agent Builder sends:
```python
@app.post("/api/mcp")
async def mcp_http_endpoint(request: Request):
    logger.info(f"=== MCP REQUEST ===")
    logger.info(f"Method: {request.method}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"URL: {request.url}")
    # ... rest of handler
```

### 3. Test from Browser Console
Open Agent Builder and run:
```javascript
fetch('https://gvses-market-insights.fly.dev/api/mcp', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer fo1_...',
    'Accept': 'application/json, text/event-stream'
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'tools/list',
    id: 1
  })
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

### 4. Check MCP Server Configuration in Agent Builder
Verify:
- Server URL: `https://gvses-market-insights.fly.dev/api/mcp` (no trailing slash?)
- Authorization: Fly.io token format
- Any custom headers required

### 5. Review Backend MCP Transport Implementation
Check `backend/services/mcp_websocket_transport.py`:
- Does `handle_request()` properly parse InitializeRequest?
- Are we returning correct response format?
- Do we handle missing fields gracefully?

---

## Potential Root Causes (Ranked by Likelihood)

### 1. Authentication/Authorization Issue (70% likely)
Agent Builder sends request → Backend auth middleware rejects → Never reaches our handlers

**Fix**: Check auth middleware, add more permissive CORS, verify token format

### 2. MCP Initialize Flow Not Implemented (20% likely)
Agent Builder sends InitializeRequest → We don't handle it correctly → It falls back to GET → 405

**Fix**: Properly implement InitializeRequest/InitializeResponse flow

### 3. Fly.io Proxy Issue (5% likely)
Fly.io intercepts requests from OpenAI IPs → Returns 405 before reaching our app

**Fix**: Check Fly.io settings, whitelist OpenAI IPs

### 4. Content-Type Negotiation (5% likely)
Agent Builder sends specific Accept header → We don't match it → Returns 405

**Fix**: Update Accept header handling to be more flexible

---

## Related Files

- `backend/mcp_server.py` - HTTP endpoint handlers
- `backend/services/mcp_websocket_transport.py` - MCP message handling
- `backend/middleware/auth.py` - Authentication middleware (if exists)
- `fly.toml` - Fly.io configuration

---

## Recommended Immediate Action

**Add comprehensive logging and check Fly.io logs to see exactly what Agent Builder is sending.**

This will definitively answer:
- Is the request reaching our backend?
- What headers are being sent?
- Which handler is being hit?
- Why is 405 being returned?

Without seeing the actual request from Agent Builder, we're debugging blind.
