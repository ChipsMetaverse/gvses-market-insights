# Chart Control Tools MCP Integration Fix

**Date**: November 12, 2025
**Status**: 🔧 Deployed - Awaiting Testing

---

## Issue Discovered

After successfully fixing the async/await bug and deploying to production, chart control tools were still not appearing in the MCP server's tools list. Testing revealed only market data tools were returned:

```bash
curl -X POST https://gvses-market-insights.fly.dev/api/mcp \
  -H "Authorization: Bearer fo1_..." \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'

# Only returned: get_stock_quote, get_stock_history, get_market_news, get_technical_indicators
# Missing: change_chart_symbol, set_chart_timeframe, toggle_chart_indicator
```

## Root Cause

The HTTP MCP endpoint was taking a different code path than the WebSocket endpoint:

### WebSocket Path (Working)
```
/mcp → mcp_websocket_endpoint()
     → handle_websocket()
     → _handle_list_tools() ✅ Includes chart control tools
```

### HTTP Path (Broken)
```
/api/mcp → mcp_http_endpoint()
         → handle_request()
         → mcp_client.list_tools() directly ❌ Only market data tools
```

The HTTP `handle_request()` method was calling `self.mcp_client.list_tools()` directly, bypassing the `_handle_list_tools()` method that had the chart control tools logic.

## Solution

Updated two sections in `backend/services/mcp_websocket_transport.py`:

### 1. Fixed `handle_request()` - tools/list (Lines 480-557)

**Before**:
```python
elif method == "tools/list":
    if self.mcp_client:
        tools_response = await self.mcp_client.list_tools()
        return {
            "jsonrpc": "2.0",
            "result": tools_response.get("result", {"tools": []}),
            "id": msg_id
        }
```

**After**:
```python
elif method == "tools/list":
    if self.mcp_client:
        tools_response = await self.mcp_client.list_tools()

        # Start with market data tools
        tools_list = tools_response.get("result", {}).get("tools", [])

        # Add chart control tools
        chart_control_tools = [
            {
                "name": "change_chart_symbol",
                "description": "Change the displayed symbol on the trading chart",
                "inputSchema": {...}
            },
            {
                "name": "set_chart_timeframe",
                "description": "Set the timeframe for chart data display",
                "inputSchema": {...}
            },
            {
                "name": "toggle_chart_indicator",
                "description": "Toggle technical indicators on/off",
                "inputSchema": {...}
            }
        ]

        # Combine market data tools and chart control tools
        tools_list.extend(chart_control_tools)

        return {
            "jsonrpc": "2.0",
            "result": {"tools": tools_list},
            "id": msg_id
        }
```

### 2. Fixed `handle_request()` - tools/call (Lines 559-601)

**Before**:
```python
elif method == "tools/call":
    tool_name = params.get("name")
    tool_arguments = params.get("arguments", {})

    if self.mcp_client:
        tool_result = await self.mcp_client.call_tool(tool_name, tool_arguments)
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": str(tool_result)}]},
            "id": msg_id
        }
```

**After**:
```python
elif method == "tools/call":
    tool_name = params.get("name")
    tool_arguments = params.get("arguments", {})

    # Handle chart control tools locally
    if tool_name in ["change_chart_symbol", "set_chart_timeframe", "toggle_chart_indicator"]:
        tool_result = await self._handle_chart_control_tool(tool_name, tool_arguments)
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": tool_result}]},
            "id": msg_id
        }
    elif self.mcp_client:
        tool_result = await self.mcp_client.call_tool(tool_name, tool_arguments)
        return {
            "jsonrpc": "2.0",
            "result": {"content": [{"type": "text", "text": str(tool_result)}]},
            "id": msg_id
        }
```

## Files Modified

- **`backend/services/mcp_websocket_transport.py`**:
  - Lines 480-557: Updated `handle_request()` tools/list to include chart control tools
  - Lines 559-601: Updated `handle_request()` tools/call to route chart control tools locally

## Chart Control Tools Specifications

### 1. change_chart_symbol
- **Description**: Change the displayed symbol on the trading chart
- **Parameters**:
  - `symbol` (string, required): Stock ticker symbol (e.g., AAPL, TSLA, MSFT)
- **Implementation**: Queues command with type "change_symbol" for frontend polling

### 2. set_chart_timeframe
- **Description**: Set the timeframe for chart data display
- **Parameters**:
  - `timeframe` (string, required): One of ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
- **Implementation**: Queues command with type "set_timeframe" for frontend polling

### 3. toggle_chart_indicator
- **Description**: Toggle technical indicators on/off on the chart
- **Parameters**:
  - `indicator` (string, required): One of ["sma", "ema", "bollinger", "rsi", "macd", "volume"]
  - `enabled` (boolean, required): Whether to show or hide the indicator
  - `period` (number, optional): Period for the indicator
- **Implementation**: Queues command with type "toggle_indicator" for frontend polling

## Architecture Overview

```
Agent Builder Chart Control Agent
  ↓
HTTPS POST /api/mcp (JSON-RPC 2.0)
  ↓
mcp_http_endpoint() [mcp_server.py:2681]
  ↓
handle_request() [mcp_websocket_transport.py:450]
  ↓
  ├─ tools/list → Returns market data tools + chart control tools
  └─ tools/call → Routes chart control tools to _handle_chart_control_tool()
                → Routes market data tools to mcp_client
```

## Testing Plan

### 1. Test MCP Endpoint
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fo1_LfBVrKP5isehK-D7BlsBh6H8NrTOa8PYR5nSxHeV2N8" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

**Expected**: 7 tools (4 market data + 3 chart control)

### 2. Test Tool Call
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fo1_..." \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "params":{"name":"change_chart_symbol","arguments":{"symbol":"AAPL"}},
    "id":2
  }'
```

**Expected**: `{"jsonrpc":"2.0","result":{"content":[{"type":"text","text":"Chart will switch to AAPL"}]},"id":2}`

### 3. Test in Agent Builder Preview Mode
1. Navigate to Chart Agent workflow v52
2. Enter "show me Apple"
3. Verify Chart Control Agent loads tools successfully
4. Verify change_chart_symbol is called with symbol="AAPL"
5. Verify command is queued in backend

### 4. Test End-to-End in Production
1. Open ChatKit with Chart Agent workflow
2. Say "show me Tesla"
3. Verify chart switches to TSLA
4. Verify natural language response is shown

## Deployment

**Deployment Started**: November 12, 2025, ~8:05 PM
**Deployment Command**: `fly deploy`
**Expected Duration**: ~2-3 minutes

## Success Criteria

- [x] Code changes complete (both HTTP and WebSocket paths)
- [ ] Deployment successful
- [ ] MCP endpoint returns 7 tools (4 market data + 3 chart control)
- [ ] Agent Builder can load chart control tools
- [ ] Chart Control Agent can call change_chart_symbol
- [ ] Commands are queued correctly
- [ ] Frontend polls and executes commands
- [ ] Chart switches symbols in production

## Related Documentation

- `ROUTING_FIX_COMPLETE_MCP_URL_ISSUE.md` - MCP server URL fix
- `IF_ELSE_FIX_COMPLETE_V51.md` - If/Else routing fix
- `ROOT_CAUSE_FOUND.md` - Original routing investigation
- `CHART_CONTROL_FIX_SESSION_NOV12.md` - Complete session log

---

## Timeline

- **8:05 PM**: Discovered chart control tools not appearing via HTTP endpoint
- **8:10 PM**: Identified root cause - HTTP path bypassing _handle_list_tools
- **8:15 PM**: Fixed handle_request() for both tools/list and tools/call
- **8:20 PM**: Started deployment to production

---

## Key Learnings

1. **HTTP vs WebSocket**: Different MCP transport methods can have different code paths
2. **Testing Both Paths**: Must test both HTTP (/api/mcp) and WebSocket (/mcp) endpoints
3. **Code Duplication**: Chart control tools logic needed in multiple places for different transports
4. **Systematic Testing**: Test each endpoint directly with curl before testing full workflow

---

## Next Steps

1. Wait for deployment to complete
2. Test MCP endpoint with curl
3. Test in Agent Builder Preview mode
4. Test end-to-end in ChatKit production
5. Mark feature as 100% complete
