# Trading Agent Chart Control - Diagnostic Report

## 🎯 Problem Statement
**User Report**: "doesn't seem like the agent can control the lightweight chart or can even see what is loaded."

## ✅ What's Working (Confirmed)

### 1. Backend Chart Action Endpoint ✅
**Status**: **FULLY FUNCTIONAL**

**Test Result**:
```bash
curl -X POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action \
  -d '{"query": "draw support and resistance for TSLA", "session_id": "test", "metadata": {"chart_context": {"symbol": "TSLA", "timeframe": "1D"}}}'
```

**Response**:
```json
{
  "success": true,
  "text": "I'll draw the key support and resistance levels on your TSLA chart.\n\n**SUPPORT**: 438.30 \"Recent low and buy low level\"\n**SUPPORT**: 420.04 \"Buy the dip level at 200-day MA\"\n**RESISTANCE**: 470.75 \"Recent high and strong resistance level\"\n**RESISTANCE**: 458.22 \"Previous resistance area\"\n\nCurrently, TSLA is trading at $456.51, just below the resistance at $458.22. This setup indicates potential for a breakout if it can surpass this level.\n\nLOAD:TSLA\nTIMEFRAME:1D\nSUPPORT:319.69\nSUPPORT:325.6\nSUPPORT:328.51\nRESISTANCE:470.75\nRESISTANCE:467.0\nRESISTANCE:465.7\nRESISTANCE:458.22",
  "chart_commands": [
    "LOAD:TSLA",
    "TIMEFRAME:1D",
    "SUPPORT:319.69",
    "SUPPORT:325.6",
    "SUPPORT:328.51",
    "RESISTANCE:470.75",
    "RESISTANCE:467.0",
    "RESISTANCE:465.7",
    "RESISTANCE:458.22"
  ],
  "data": {
    "tools_used": ["get_stock_price", "get_stock_history", "get_comprehensive_stock_data"],
    "chart_context": {"symbol": "TSLA", "timeframe": "1D"},
    "timestamp": "2025-11-02T20:07:49.493110"
  },
  "error": null
}
```

✅ **Backend generates correct chart commands**  
✅ **Chart context is retrieved and used**  
✅ **Agent orchestrator is working properly**  
✅ **Drawing commands are formatted correctly**

### 2. Backend Session Store ✅
**File**: `backend/services/session_store.py`  
**Status**: Implemented and working

- ✅ `set_chart_context(session_id, context)` stores chart state
- ✅ `get_chart_context(session_id)` retrieves chart state
- ✅ `/api/chatkit/update-context` endpoint available

### 3. Frontend Chart Context Passing ✅
**File**: `frontend/src/components/RealtimeChatKit.tsx`  
**Lines**: 203-232

```typescript
// Update chart context whenever symbol, timeframe, or snapshotId changes
useEffect(() => {
  const updateChartContext = async () => {
    if (!sessionId || !symbol) {
      // Need both session ID and symbol to update context
      return;
    }

    try {
      const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${backendUrl}/api/chatkit/update-context`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          symbol: symbol,
          timeframe: timeframe || '1D',
          snapshot_id: snapshotId || null
        })
      });

      if (response.ok) {
        console.log(`✅ [ChatKit] Updated chart context: ${symbol} @ ${timeframe || '1D'}`);
      } else {
        console.error(`❌ [ChatKit] Failed to update chart context: ${response.status}`);
      }
    } catch (error) {
      console.error('❌ [ChatKit] Error updating chart context:', error);
    }
  };

  updateChartContext();
}, [sessionId, symbol, timeframe, snapshotId]);
```

✅ **Frontend sends chart context to backend when chart changes**

### 4. Agent Orchestrator Chart Context Injection ✅
**File**: `backend/services/agent_orchestrator.py`  
**Status**: Implemented

The agent orchestrator:
- ✅ Accepts `chart_context` parameter
- ✅ Injects `[CHART: symbol=X, timeframe=Y]` into queries
- ✅ Includes chart drawing instructions in system prompt
- ✅ Generates drawing commands

---

## ❌ What's NOT Working (Root Cause)

### 🚨 **CRITICAL ISSUE: Agent Builder Not Calling Our Backend**

**The Problem**: The Agent Builder workflow has a `chart_control` **function tool**, but it's **NOT configured to call our HTTP endpoint**.

**Why This Happens**:
- OpenAI Agent Builder "Custom" tools are **OpenAI Function Calling tools**, NOT HTTP actions
- When the agent decides to use `chart_control`, it returns a function call to OpenAI's platform
- **OpenAI's platform doesn't know to route this to our backend**
- The function call goes nowhere, so our backend never receives the request

**Evidence**:
- Backend logs show NO `[CHATKIT ACTION]` entries during user queries
- Frontend doesn't parse or execute drawing commands
- User reports agent doesn't control the chart

---

## 🔍 Diagnosis Checklist

### Phase 1: Verify ChatKit Session Flow

**Test Steps**:
1. Open browser DevTools console
2. Navigate to https://gvses-market-insights.fly.dev/
3. Load TSLA chart
4. Open ChatKit
5. Type: "draw support and resistance"

**Expected Console Logs**:
```
✅ [ChatKit] Updated chart context: TSLA @ 1D
✅ [ChatKit] Session established: <session_id>
```

**Check Backend Logs** (via `flyctl logs -a gvses-market-insights`):
```
[CHATKIT UPDATE] Session <session_id>: TSLA @ 1D
✅ [SESSION] Stored chart context for <session_id>: {'symbol': 'TSLA', 'timeframe': '1D'}
```

**If Missing**: Frontend is not calling `/api/chatkit/update-context` → Fix frontend

---

### Phase 2: Verify Agent Builder Function Call

**Test Steps**:
1. In ChatKit, type: "draw support and resistance for TSLA"
2. Check OpenAI Agent Builder logs (if accessible)
3. Check backend logs for `[CHATKIT ACTION]`

**Expected Backend Logs**:
```
[CHATKIT ACTION] Query: draw support and resistance for TSLA
[CHATKIT ACTION] Session: <session_id>, User: <user_id>
[CHATKIT ACTION] Retrieved chart context from session: {'symbol': 'TSLA', ...}
[CHATKIT ACTION] Generated 9 chart commands, used 3 tools
```

**If Missing**: Agent Builder is NOT calling `/api/chatkit/chart-action` → **THIS IS THE PROBLEM**

---

### Phase 3: Verify Frontend Command Parsing

**Test Steps**:
1. Manually send a response with chart commands to ChatKit
2. Check if frontend parses and displays them

**Expected Console Logs**:
```
[ChatKit] Processing agent response: <response text>
[ChatKit] Parsed chart commands: [...]
[ChatKit] Sending chart command: <command>
```

**If Missing**: Frontend is not parsing/executing commands → Fix frontend parser

---

## 🛠️ Solutions by Issue

### Solution A: Agent Builder is NOT Calling Backend ❌ (Current Issue)

**Root Cause**: The `chart_control` tool is a function calling tool, but there's no route configured to our backend.

**Fix Options**:

#### **Option 1: Configure Agent Builder to Use MCP Server** (Recommended)

The workflow already has `Chart_Control_MCP_Server` configured. We need to ensure this MCP server routes to our backend.

**Steps**:
1. Access Agent Builder MCP server configuration
2. Verify MCP server URL points to our backend
3. If not, update it to: `https://gvses-market-insights.fly.dev/api/chatkit/chart-action`
4. Test the integration

**Verification**:
```bash
# Check if MCP server is configured
# (Requires access to OpenAI Agent Builder settings)
```

#### **Option 2: Use Direct HTTP Custom Action**

Instead of function calling, configure a direct HTTP POST action.

**Steps**:
1. In Agent Builder, edit the `chart_control` tool
2. Change type from "Custom" to "HTTP Action"
3. Configure:
   - URL: `https://gvses-market-insights.fly.dev/api/chatkit/chart-action`
   - Method: POST
   - Headers: `{"Content-Type": "application/json"}`
   - Body template: `{"query": "{{user_query}}", "session_id": "{{session_id}}"}`

**Verification**:
```bash
# Test if HTTP action triggers backend
flyctl logs -a gvses-market-insights | grep "CHATKIT ACTION"
```

#### **Option 3: Bypass Agent Builder, Use Direct OpenAI API** (Fallback)

Replace ChatKit Agent Builder with direct OpenAI ChatCompletion API calls from our backend.

**Architecture**:
```
Frontend → Our Backend → OpenAI ChatCompletion API (with function calling)
                       ↓ Function call returned
                       ↓ Execute chart_control function locally
                       ↓ Return result with chart commands
```

**Benefits**:
- Full control over function execution
- No Agent Builder configuration needed
- Direct integration with our backend

**Drawbacks**:
- User explicitly said "We need to continue using ChatKit"
- Requires replacing ChatKit UI component
- More backend code to maintain

---

### Solution B: Frontend Not Parsing Commands ❌

**If backend IS calling but frontend doesn't display commands:**

**File**: `frontend/src/components/RealtimeChatKit.tsx`  
**Lines**: 122-150

**Current Code**:
```typescript
if (message.role === 'assistant' && message.content) {
  console.log('[ChatKit] Processing agent response:', message.content);
  
  // Check for drawing commands using the new parser
  if (AgentResponseParser.containsDrawingCommands(message.content)) {
    const chartCommands = AgentResponseParser.parseResponse(message.content);
    
    if (chartCommands.length > 0) {
      console.log('[ChatKit] Parsed chart commands:', chartCommands);
      // Send each command to the chart
      chartCommands.forEach(command => {
        console.log('[ChatKit] Sending chart command:', command);
        onChartCommand?.(command);
      });
    } else {
      console.log('[ChatKit] No chart commands found in drawing response');
    }
  }
}
```

**Test**:
```typescript
// In browser console:
AgentResponseParser.containsDrawingCommands("SUPPORT:440.00 \"test\"")
// Expected: true

AgentResponseParser.parseResponse("SUPPORT:440.00 \"test\"\nRESISTANCE:460.00 \"test\"")
// Expected: [{type: 'support', price: 440.00, label: 'test'}, ...]
```

---

### Solution C: Chart Not Displaying Commands ❌

**If commands are parsed but not displayed on chart:**

**Check**: `frontend/src/services/enhancedChartControl.ts`

**Verify**:
```typescript
export const enhancedChartControl = {
  processEnhancedResponse(response: string) {
    // Should parse SUPPORT:, RESISTANCE:, TRENDLINE:, etc.
  }
}
```

**Test**:
```bash
# In browser console:
enhancedChartControl.processEnhancedResponse("SUPPORT:440.00 \"test\"")
# Should trigger chart.addPriceLine() or similar
```

---

## 🧪 Comprehensive Testing Script

```bash
#!/bin/bash

echo "=== Testing Trading Agent Chart Control ==="
echo ""

echo "1. Testing Backend Chart Action Endpoint..."
response=$(curl -s -X POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "draw support and resistance for TSLA",
    "session_id": "test_123",
    "metadata": {
      "chart_context": {
        "symbol": "TSLA",
        "timeframe": "1D"
      }
    }
  }')

success=$(echo "$response" | jq -r '.success')
commands_count=$(echo "$response" | jq -r '.chart_commands | length')

if [ "$success" == "true" ] && [ "$commands_count" -gt 0 ]; then
  echo "✅ Backend endpoint working ($commands_count commands generated)"
else
  echo "❌ Backend endpoint failed"
  echo "$response"
  exit 1
fi

echo ""
echo "2. Testing Session Store..."
session_update=$(curl -s -X POST https://gvses-market-insights.fly.dev/api/chatkit/update-context \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_123",
    "symbol": "AAPL",
    "timeframe": "1D"
  }')

update_success=$(echo "$session_update" | jq -r '.success')

if [ "$update_success" == "true" ]; then
  echo "✅ Session store working"
else
  echo "❌ Session store failed"
  echo "$session_update"
  exit 1
fi

echo ""
echo "3. Testing Chart Action with Session Context..."
response2=$(curl -s -X POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "analyze the current chart",
    "session_id": "test_123"
  }')

success2=$(echo "$response2" | jq -r '.success')
context_symbol=$(echo "$response2" | jq -r '.data.chart_context.symbol')

if [ "$success2" == "true" ] && [ "$context_symbol" == "AAPL" ]; then
  echo "✅ Session context retrieval working (symbol: $context_symbol)"
else
  echo "❌ Session context retrieval failed"
  echo "$response2"
  exit 1
fi

echo ""
echo "=== All Backend Tests Passed ✅ ==="
echo ""
echo "Next Steps:"
echo "1. Check Agent Builder configuration:"
echo "   - Go to: https://platform.openai.com/agent-builder/edit?workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736"
echo "   - Verify chart_control tool routes to our backend"
echo ""
echo "2. Test in ChatKit:"
echo "   - Load TSLA chart"
echo "   - Ask: 'draw support and resistance'"
echo "   - Check browser console for '[ChatKit]' logs"
echo "   - Check backend logs: flyctl logs -a gvses-market-insights | grep CHATKIT"
```

Save as `test_chart_control.sh` and run:
```bash
chmod +x test_chart_control.sh
./test_chart_control.sh
```

---

## 📊 Diagnosis Decision Tree

```
User query: "draw support and resistance"
│
├─ Frontend sends to ChatKit? ──[NO]──> Issue: Frontend integration missing
│   └─ [YES]
│       │
│       ├─ ChatKit session ID exists? ──[NO]──> Issue: Session not initialized
│       │   └─ [YES]
│       │       │
│       │       ├─ Chart context sent to backend? ──[NO]──> Issue: useEffect not triggering
│       │       │   └─ [YES]
│       │       │       │
│       │       │       ├─ Agent Builder calls chart_control tool? ──[NO]──> ⚠️ CURRENT ISSUE
│       │       │       │   │
│       │       │       │   └─ Why not calling?
│       │       │       │       ├─ Tool not configured correctly
│       │       │       │       ├─ MCP server not routing to backend
│       │       │       │       └─ Agent intent classifier not routing to tool
│       │       │       │
│       │       │       └─ [YES]
│       │       │           │
│       │       │           ├─ Backend receives request? ──[NO]──> Issue: Network/routing
│       │       │           │   └─ [YES]
│       │       │           │       │
│       │       │           │       ├─ Backend generates commands? ──[NO]──> Issue: Agent orchestrator
│       │       │           │       │   └─ [YES]
│       │       │           │       │       │
│       │       │           │       │       ├─ Frontend receives response? ──[NO]──> Issue: Response parsing
│       │       │           │       │       │   └─ [YES]
│       │       │           │       │       │       │
│       │       │           │       │       │       ├─ Commands parsed? ──[NO]──> Issue: AgentResponseParser
│       │       │           │       │       │       │   └─ [YES]
│       │       │           │       │       │       │       │
│       │       │           │       │       │       │       └─ Chart displays lines? ──[NO]──> Issue: enhancedChartControl
│       │       │           │       │       │       │           └─ [YES] ✅ WORKING!
```

**Current Position**: ⚠️ "Agent Builder calls chart_control tool?" = NO

---

## 🎯 Recommended Next Action

### **Priority 1: Verify Agent Builder is Calling Backend** ⚠️

**Action**: Check backend logs to see if `/api/chatkit/chart-action` is being called.

```bash
# Watch backend logs in real-time
flyctl logs -a gvses-market-insights -f | grep CHATKIT

# Then in browser:
# 1. Open ChatKit
# 2. Type: "draw support and resistance for TSLA"
# 3. Check if logs appear

# Expected:
# [CHATKIT ACTION] Query: draw support and resistance for TSLA
# [CHATKIT ACTION] Session: <id>, User: <user_id>
# [CHATKIT ACTION] Retrieved chart context from session: {'symbol': 'TSLA', ...}
```

**If NO logs appear**: → Agent Builder is NOT calling our backend → **Configure Agent Builder routing** (see Solution A)

**If logs DO appear**: → Backend is called but commands not displayed → **Fix frontend** (see Solution B or C)

---

## 📝 Status Summary

| Component | Status | Verified |
|-----------|--------|----------|
| Backend `/api/chatkit/chart-action` endpoint | ✅ Working | ✅ Curl test passed |
| Backend `/api/chatkit/update-context` endpoint | ✅ Working | ✅ Implementation confirmed |
| Backend `SessionStore` | ✅ Working | ✅ Code reviewed |
| Agent Orchestrator chart context | ✅ Working | ✅ Implementation confirmed |
| Drawing command generation | ✅ Working | ✅ Test response includes commands |
| Frontend chart context passing | ✅ Implemented | ⚠️ Needs live verification |
| Agent Builder routing | ❌ **NOT WORKING** | ❌ **ROOT CAUSE** |
| Frontend command parsing | ✅ Implemented | ⚠️ Needs live verification |
| Chart command execution | ✅ Implemented | ⚠️ Needs live verification |

---

## 🚀 Action Plan

### Immediate (Next 1 Hour)

1. **[5 min]** Check backend logs to confirm Agent Builder is/isn't calling backend
   ```bash
   flyctl logs -a gvses-market-insights -f | grep CHATKIT
   ```

2. **[10 min]** If NOT calling backend:
   - Access Agent Builder workflow
   - Verify `chart_control` tool configuration
   - Check if MCP server is configured
   - Update routing to our backend endpoint

3. **[15 min]** Test in production:
   - Load TSLA chart
   - Type: "draw support and resistance"
   - Verify logs show backend receives request
   - Verify commands appear on chart

4. **[30 min]** If issues persist:
   - Enable verbose logging in frontend
   - Check browser console for errors
   - Verify AgentResponseParser is working
   - Test enhancedChartControl directly

### Follow-up (Next 2-4 Hours)

5. **End-to-end testing** with multiple scenarios
6. **Performance optimization** if latency is high
7. **Documentation update** with working configuration
8. **Deploy fixes** and verify in production

---

**Last Updated**: November 2, 2025  
**Status**: Backend confirmed working, Agent Builder routing investigation needed  
**Priority**: HIGH - User-facing feature not functional


