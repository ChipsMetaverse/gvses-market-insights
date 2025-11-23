# MCP Streamable HTTP Transport Fix

**Date**: November 12, 2025
**Issue**: HTTP 405 error when OpenAI Agent Builder tries to connect to MCP endpoint
**Root Cause**: Missing GET handler and improper Streamable HTTP transport implementation

## MCP Specification Requirements

According to the MCP Streamable HTTP transport specification:

### Server MUST:
1. Provide single HTTP endpoint supporting both POST and GET methods
2. Handle POST requests with `Accept: application/json, text/event-stream` header
3. Return either `Content-Type: application/json` OR `Content-Type: text/event-stream`
4. Support GET requests (can return 405 if not supporting SSE listening)

### Our Current Implementation:
```python
@app.post("/api/mcp")  # ❌ Only POST
@app.post("/mcp/http") # ❌ Only POST
```

### Required Implementation:
```python
@app.post("/api/mcp")    # ✅ Handle client requests
@app.get("/api/mcp")     # ✅ Return 405 (we don't support SSE listening)
@app.options("/api/mcp") # ✅ Handle CORS preflight
```

## Fix Strategy

1. **Add GET handler** - Return 405 Method Not Allowed (we don't support server-initiated SSE)
2. **Add OPTIONS handler** - Handle CORS preflight requests
3. **Add explicit Content-Type** - Return `Content-Type: application/json` in POST responses
4. **Add proper Accept header validation** - Check client's Accept header

## Implementation

See `backend/mcp_server.py` for implementation.

## Testing

### Test 1: POST request ✅ PASSED
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/mcp \
  -H "Authorization: Bearer fo1_..." \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```
**Result**: HTTP 200, returns 7 tools (4 market data + 3 chart control)

### Test 2: GET request ✅ PASSED
```bash
curl -X GET https://gvses-market-insights.fly.dev/api/mcp \
  -H "Authorization: Bearer fo1_..." \
  -H "Accept: text/event-stream"
```
**Result**: HTTP 405, proper error message: "GET method not supported. Use POST for MCP requests."

### Test 3: OPTIONS request ✅ PASSED
```bash
curl -X OPTIONS "https://gvses-market-insights.fly.dev/api/mcp" \
  -H "Origin: https://platform.openai.com" \
  -H "Access-Control-Request-Method: POST"
```
**Result**: HTTP 200 with CORS headers:
- `access-control-allow-origin: https://platform.openai.com`
- `access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT`
- `access-control-max-age: 600`

## References
- MCP Streamable HTTP Transport: https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http
- OpenAI MCP Integration: https://platform.openai.com/docs/guides/tools-connectors-mcp
