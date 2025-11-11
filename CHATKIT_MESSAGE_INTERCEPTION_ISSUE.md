# ChatKit Message Interception Issue - Root Cause Found

## Date: 2025-11-06 18:30 PST

## Summary
Chart control function calling implementation is complete and working on the backend, but **ChatKit messages are not being intercepted** by the frontend React component.

## Root Cause Confirmed

### The Problem
The `onMessage` callback in `chatKitConfig` (RealtimeChatKit.tsx:155) is **NEVER triggered** when ChatKit receives messages from the Agent Builder.

### Evidence
1. ✅ ChatKit iframe displays agent responses correctly
2. ✅ JSON responses contain `{"chart_commands":["LOAD:AAPL"]}`
3. ✅ Banner shows "AAPL Chart Request" (Agent Builder tracking working)
4. ❌ Console logs show **NO** `🔥🔥🔥 [ChatKit CONFIG] onMessage CALLED!!!` debug message
5. ❌ Chart does not switch symbols (commands never executed)

### Code Location
```typescript
// RealtimeChatKit.tsx line 155
const chatKitConfig = useMemo(() => ({
  api: { ... },
  onMessage: (message: any) => {
    console.log('🔥🔥🔥 [ChatKit CONFIG] onMessage CALLED!!!', message); // NEVER LOGS
    // ... chart command parsing code that never runs
  }
}), [onMessage, onChartCommand]);
```

## Why This Is Happening

The `@openai/chatkit-react` library likely **does not support** an `onMessage` callback in the config object passed to `useChatKit()`.

ChatKit messages are handled internally within the iframe, and there's no documented way to intercept them in the parent React component.

## Backend Chart Control Status

✅ **FULLY WORKING**
- Direct API test: `curl http://localhost:8000/api/agent/orchestrate`
- Returns: `{"chart_commands": ["LOAD:NVDA"], "tools_used": ["load_chart"]}`
- Backend logs: `[CHART_CONTROL] Loading chart for symbol: NVDA`

## What We've Tried

1. ✅ Implemented JSON parsing logic (lines 174-187)
2. ✅ Added drawing command parsing (lines 190-203)
3. ✅ Added legacy text command fallback (lines 206-211)
4. ✅ Added extensive debug logging
5. ❌ **None of this code ever executes** because onMessage is never called

## Potential Solutions

### Option 1: iframe postMessage Communication
Set up postMessage listener to communicate between ChatKit iframe and parent:

```typescript
useEffect(() => {
  const handleMessage = (event: MessageEvent) => {
    if (event.origin === 'https://chatkit.openai.com') { // Verify origin
      if (event.data.type === 'assistant_message') {
        // Parse chart commands from event.data.content
        tryParseChartCommands(event.data.content);
      }
    }
  };

  window.addEventListener('message', handleMessage);
  return () => window.removeEventListener('message', handleMessage);
}, []);
```

### Option 2: Polling ChatKit DOM
Use MutationObserver to watch for new messages in the iframe DOM:

```typescript
useEffect(() => {
  const iframe = document.querySelector('iframe[name="chatkit"]');
  if (!iframe?.contentWindow) return;

  const observer = new MutationObserver((mutations) => {
    // Detect new assistant messages
    // Extract chart_commands from message content
  });

  observer.observe(iframe.contentDocument.body, {
    childList: true,
    subtree: true
  });
}, [chatKitControl]);
```

### Option 3: Custom Agent Builder Action
Configure Agent Builder to call a custom action endpoint that executes chart commands:

```typescript
// Backend endpoint
POST /api/agent-actions/chart-control
Body: {"action": "load_chart", "symbol": "AAPL"}

// Agent Builder configuration
Custom Actions:
- Name: "Chart Control"
- URL: https://g-vses.fly.dev/api/agent-actions/chart-control
- Method: POST
```

### Option 4: Switch to Direct API Integration
Replace ChatKit with direct Agent Builder API calls, giving us full control:

```typescript
const sendMessage = async (query: string) => {
  const response = await fetch('/api/agent/orchestrate', {
    method: 'POST',
    body: JSON.stringify({ query, chart_context })
  });

  const data = await response.json();

  // We have full control over chart_commands
  if (data.chart_commands) {
    executeChartCommands(data.chart_commands);
  }
};
```

## Recommended Next Step

**Option 4 (Direct API Integration)** is the cleanest solution because:
- ✅ We already have the backend API working perfectly
- ✅ Full control over message handling
- ✅ No iframe communication complexity
- ✅ Can still use Agent Builder for voice
- ✅ Consistent with how the rest of the app works

## Files Affected

- `frontend/src/components/RealtimeChatKit.tsx` - Main ChatKit integration
- `frontend/src/components/TradingDashboardSimple.tsx` - Parent component
- `frontend/src/services/enhancedChartControl.ts` - Chart command execution
- `backend/services/agent_orchestrator.py` - Working chart control backend

## Test Results

### Backend API (✅ PASSING)
```bash
$ python3 test_chart_control_tools.py
✅ Found 5 chart control tools
✅ load_chart requires "symbol" parameter
✅ ALL TESTS PASSING
```

### Direct API Call (✅ PASSING)
```bash
$ curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me TSLA chart"}'

Response:
{
  "response": "Loading TSLA chart...",
  "chart_commands": ["LOAD:TSLA"],
  "tools_used": ["load_chart"]
}
```

### ChatKit Integration (❌ FAILING)
```
User types: "Show me AAPL chart"
Agent responds: {"chart_commands": ["LOAD:AAPL"]}
Frontend: NO interception, NO execution, chart stays on TSLA
```

## Conclusion

The chart control implementation is **100% complete and working** on the backend. The issue is purely a frontend message interception problem with the ChatKit library.

We need to either:
1. Find the correct way to intercept ChatKit messages (if it exists)
2. Implement an alternative message interception strategy
3. Switch to direct API integration (recommended)

---

**Status**: Backend ✅ Complete | Frontend ❌ Message Interception Broken
**Next Action**: Implement direct API integration or find ChatKit message interception solution
**Priority**: HIGH - Core functionality blocked
