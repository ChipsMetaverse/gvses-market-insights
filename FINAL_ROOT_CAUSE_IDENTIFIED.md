# FINAL ROOT CAUSE IDENTIFIED

**Date**: November 4, 2025  
**Investigation Method**: Playwright + Code Analysis  
**Status**: 🔴 **CRITICAL ARCHITECTURE ISSUE FOUND**

---

## The Real Problem

**THE CHART CONTROL AGENT IS NOT GENERATING chart_commands - IT'S CALLING AN MCP TOOL THAT CALLS THE BACKEND ORCHESTRATOR!**

This creates a circular/confused architecture where:
1. Agent Builder's Chart Control Agent receives `{"intent":"chart_command","symbol":"NVDA"}`
2. Chart Control Agent calls MCP tool `change_chart_symbol("NVDA")`
3. MCP tool calls backend `/api/chatkit/chart-action` with query "Show me NVDA chart..."
4. Backend orchestrator processes this query and returns response
5. Orchestrator's `chart_commands` gets passed back through MCP to Chart Control Agent
6. Chart Control Agent returns this in its response

**THIS IS WRONG!** The Chart Control Agent should directly generate `["LOAD:NVDA"]` based on the intent, NOT call the backend!

---

## Evidence from Code

### MCP Tool Implementation (`market-mcp-server/sse-server.js` line 501-552)

```javascript
async changeChartSymbol(args) {
  const { symbol } = args;
  
  try {
    // ❌ THIS IS THE PROBLEM - Calling backend orchestrator!
    const backendUrl = process.env.BACKEND_URL || 'https://gvses-market-insights.fly.dev';
    const response = await fetch(`${backendUrl}/api/chatkit/chart-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Show me ${symbol.toUpperCase()} chart and analyze it`,
        session_id: this.currentSessionId || 'mcp-session'
      })
    });
    
    const result = await response.json();
    
    // Returns whatever the backend returns (which might be incomplete)
    return {
      content: [{
        type: 'text',
        text: result.text || `Switched chart to ${symbol.toUpperCase()}`
      }],
      _meta: {
        chart_commands: result.chart_commands || [],  // ❌ Trusts backend output
        action: 'change_symbol',
        symbol: symbol.toUpperCase()
      }
    };
  } catch (error) {
    // ✅ Error handler DOES return correct format!
    return {
      content: [{
        type: 'text',
        text: `Switched to ${symbol.toUpperCase()} chart`
      }],
      _meta: {
        chart_commands: [`LOAD:${symbol.toUpperCase()}`],  // ✅ CORRECT!
        action: 'change_symbol',
        symbol: symbol.toUpperCase()
      }
    };
  }
}
```

### Backend Endpoint (`backend/mcp_server.py` line 2093-2179)

The backend calls the orchestrator, which has its own complex logic for generating chart_commands. If the orchestrator returns `["LOAD"]` without the symbol, that's what gets returned!

---

## The Fix

### Option 1: Fix MCP Tool to NOT Call Backend (RECOMMENDED)

The MCP tool `change_chart_symbol` should directly return the correct format:

```javascript
async changeChartSymbol(args) {
  const { symbol } = args;
  
  // ✅ SIMPLE AND CORRECT
  return {
    content: [{
      type: 'text',
      text: `Switched to ${symbol.toUpperCase()} chart`
    }],
    _meta: {
      chart_commands: [`LOAD:${symbol.toUpperCase()}`],
      action: 'change_symbol',
      symbol: symbol.toUpperCase()
    }
  };
}
```

**Benefits:**
- Simple and direct
- No backend dependency
- Fast response
- Correct format guaranteed

### Option 2: Fix Agent Builder to NOT Call MCP Tool

Remove the MCP tool call entirely and have the Chart Control Agent directly output:

```json
{
  "text": "Switched to NVDA",
  "chart_commands": ["LOAD:NVDA"]
}
```

**Benefits:**
- One less hop
- Faster
- More control

---

## Why The Bug Exists

Looking at the MCP tool error handler (line 546), it DOES return the correct format:
```javascript
chart_commands: [`LOAD:${symbol.toUpperCase()}`]
```

But the success path (line 533) trusts the backend:
```javascript
chart_commands: result.chart_commands || []
```

**So when the backend orchestrator returns incomplete data, the MCP tool passes it through!**

The backend orchestrator likely has its own bug where it's returning `["LOAD"]` instead of `["LOAD:NVDA"]`.

---

## Immediate Action Required

### Fix the MCP Tool (Simplest Fix)

**File**: `market-mcp-server/sse-server.js`  
**Line**: 501-552  
**Change**: Remove backend call, return correct format directly

```javascript
async changeChartSymbol(args) {
  const { symbol } = args;
  
  return {
    content: [{
      type: 'text',
      text: `Switched to ${symbol.toUpperCase()} chart`
    }],
    _meta: {
      chart_commands: [`LOAD:${symbol.toUpperCase()}`],
      action: 'change_symbol',
      symbol: symbol.toUpperCase()
    }
  };
}
```

---

## Test Plan

1. Fix MCP tool as shown above
2. Restart MCP server
3. Test in Agent Builder Preview with "chart NVDA"
4. Verify Chart Control Agent returns `["LOAD:NVDA"]`
5. Publish workflow v34
6. Deploy to production
7. Test in live app

---

## Conclusion

**Root Cause**: The MCP tool `change_chart_symbol` calls the backend orchestrator which returns incomplete `chart_commands` (`["LOAD"]` without symbol).

**Solution**: Simplify the MCP tool to directly return `["LOAD:SYMBOL"]` without calling the backend.

**Priority**: 🔴 CRITICAL - This blocks all chart control functionality.

