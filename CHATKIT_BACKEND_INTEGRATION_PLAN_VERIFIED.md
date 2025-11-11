# ChatKit Backend Integration Plan (VERIFIED)

## 🔍 **Current State Analysis**

### ✅ What We Already Have:
1. **ChatKit UI** - Currently working in iframe
2. **Agent Orchestrator** - Full backend logic at `backend/services/agent_orchestrator.py`
3. **Chart Command Extractor** - Parses drawing commands from agent responses
4. **Chart Context Support** - Agent orchestrator accepts `chart_context` parameter
5. **Workflow ID** - `wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736`

### ❌ What's Broken:
- ChatKit calls OpenAI API directly (bypassing our backend)
- No chart context passed to ChatKit
- Agent orchestrator never invoked
- Drawing commands never extracted/executed

---

## 🎯 **Solution: ChatKit Custom Backend Integration**

According to OpenAI ChatKit documentation, we can route ALL ChatKit API calls through our backend using a custom `fetch` function.

### **Architecture:**

```
User types in ChatKit iframe
         ↓
ChatKit widget calls api.fetch()
         ↓
Custom fetch() → POST /api/chatkit/proxy
         ↓
Our Backend:
  1. Extract query + inject chart context
  2. Call agent_orchestrator.process_query()
  3. Extract drawing commands
  4. Format response for ChatKit
         ↓
ChatKit displays response
         ↓
onMessage() callback fires
         ↓
AgentResponseParser extracts commands
         ↓
Chart commands executed on parent window
```

---

## 📋 **Implementation Steps**

### **Phase 1: Backend ChatKit Proxy Endpoint (1 hour)**

**File:** `backend/mcp_server.py`

Add a new endpoint that acts as a proxy between ChatKit and our agent orchestrator:

```python
class ChatKitProxyRequest(BaseModel):
    """Request from ChatKit custom backend"""
    messages: List[Dict[str, str]]
    user: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/api/chatkit/proxy")
async def chatkit_proxy(request: ChatKitProxyRequest):
    """
    Proxy endpoint for ChatKit API calls
    Intercepts ChatKit messages, adds chart context, calls agent orchestrator
    """
    try:
        # Extract the latest user message
        user_messages = [m for m in request.messages if m.get("role") == "user"]
        if not user_messages:
            return {"error": "No user message found"}
        
        latest_message = user_messages[-1].get("content", "")
        
        logger.info(f"[CHATKIT PROXY] Received: {latest_message[:100]}...")
        
        # TODO: Get chart context from session/metadata
        # For now, we'll extract from metadata if passed
        chart_context = request.metadata.get("chart_context") if request.metadata else None
        
        if chart_context:
            logger.info(f"[CHATKIT PROXY] Chart context: {chart_context}")
        
        # Call agent orchestrator
        from services.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        # Convert messages to conversation history
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in request.messages[:-1]  # All except latest
        ]
        
        result = await orchestrator.process_query(
            query=latest_message,
            conversation_history=conversation_history,
            chart_context=chart_context
        )
        
        # Format response for ChatKit
        response_text = result.get("text", "")
        chart_commands = result.get("chart_commands", [])
        
        # Embed chart commands in the response text for parsing
        if chart_commands:
            # ChatKit will display this, and our onMessage parser will extract commands
            command_text = "\n\n" + "\n".join(chart_commands)
            response_text += command_text
            logger.info(f"[CHATKIT PROXY] Embedded {len(chart_commands)} chart commands")
        
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": response_text
                }
            ],
            "metadata": {
                "chart_commands": chart_commands,
                "tools_used": result.get("tools_used", []),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"[CHATKIT PROXY] Error: {e}", exc_info=True)
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": f"I encountered an error: {str(e)}"
                }
            ],
            "metadata": {"error": str(e)}
        }
```

---

### **Phase 2: Frontend Custom Backend Configuration (1 hour)**

**File:** `frontend/src/components/RealtimeChatKit.tsx`

Update the ChatKit config to use our custom backend:

```typescript
const chatKitConfig = useMemo(() => {
  const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  return {
    api: {
      // Custom backend URL - routes ALL ChatKit API calls through our backend
      url: `${backendUrl}/api/chatkit/proxy`,
      
      // Custom fetch function to inject chart context
      async fetch(url: string, options: RequestInit) {
        // Add chart context to the request
        const body = options.body ? JSON.parse(options.body as string) : {};
        
        const enhancedBody = {
          ...body,
          metadata: {
            ...(body.metadata || {}),
            chart_context: {
              symbol: symbol,
              timeframe: timeframe,
              snapshot_id: snapshotId,
              timestamp: new Date().toISOString()
            }
          }
        };
        
        console.log('[ChatKit] Custom fetch with chart context:', enhancedBody.metadata.chart_context);
        
        return fetch(url, {
          ...options,
          body: JSON.stringify(enhancedBody)
        });
      },
      
      // Session management (keep existing)
      async getClientSecret(existing: any) {
        const res = await fetch(`${backendUrl}/api/chatkit/session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            device_id: localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`,
            existing_session: existing || null
          }),
        });

        if (!res.ok) {
          throw new Error(`Session failed: ${res.status}`);
        }

        const { client_secret } = await res.json();
        console.log('✅ ChatKit session with custom backend');
        return client_secret;
      }
    },
    
    // Enhanced message handler (keep existing logic)
    onMessage: (message: any) => {
      const msg: Message = {
        id: `chatkit-${Date.now()}`,
        role: message.role,
        content: message.content,
        timestamp: new Date().toISOString(),
        provider: 'chatkit-agent-builder'
      };
      onMessage?.(msg);
      queueMessage(msg);

      // Parse and execute drawing commands
      if (message.role === 'assistant' && message.content) {
        console.log('[ChatKit] Processing agent response');
        
        if (AgentResponseParser.containsDrawingCommands(message.content)) {
          const chartCommands = AgentResponseParser.parseResponse(message.content);
          
          if (chartCommands.length > 0) {
            console.log('[ChatKit] Executing chart commands:', chartCommands);
            chartCommands.forEach(command => {
              onChartCommand?.(command);
            });
          }
        }
      }
    }
  };
}, [symbol, timeframe, snapshotId, onMessage, onChartCommand, queueMessage]);
```

---

### **Phase 3: Agent Orchestrator Verification (Already Done ✅)**

The agent orchestrator already supports:
- ✅ Chart context parameter: `process_query(..., chart_context=...)`
- ✅ Drawing command extraction: `ChartCommandExtractor`
- ✅ System prompt includes chart awareness (lines 3215-3255)
- ✅ Returns `chart_commands` in response

**No changes needed here!**

---

### **Phase 4: Test ChatKit Custom Backend (30 min)**

#### **Test 1: Verify Backend Receives Requests**

```bash
# Watch backend logs
tail -f logs/chatkit_proxy.log

# Expected in logs when user types in ChatKit:
# [CHATKIT PROXY] Received: draw support and resistance for TSLA
# [CHATKIT PROXY] Chart context: {'symbol': 'TSLA', 'timeframe': '1D'}
# [CHATKIT PROXY] Embedded 4 chart commands
```

#### **Test 2: Verify Chart Context Injection**

```typescript
// In browser console:
// 1. Load TSLA chart
// 2. Open ChatKit
// 3. Type: "what chart is loaded?"
// Expected response: "You're viewing TSLA on 1D timeframe"
```

#### **Test 3: Verify Drawing Commands**

```typescript
// 1. Load TSLA chart
// 2. Type in ChatKit: "draw support and resistance"
// Expected:
// - Backend logs show chart_context
// - Response contains SUPPORT: and RESISTANCE: commands
// - Lines appear on chart
```

---

## 🚨 **Potential Issues & Solutions**

### **Issue 1: ChatKit Rejects Custom Backend**

**Symptom:** ChatKit doesn't call our proxy endpoint

**Solution:** Fall back to widget actions:

```typescript
widgets: {
  async onAction(action, item) {
    if (action.type === 'chart_command') {
      const result = await fetch(`${backendUrl}/api/chatkit/chart-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: action.payload.query,
          chart_context: { symbol, timeframe, snapshot_id: snapshotId }
        })
      });
      
      const data = await result.json();
      if (data.chart_commands) {
        data.chart_commands.forEach(cmd => onChartCommand?.(cmd));
      }
    }
  }
}
```

---

### **Issue 2: Chart Context Not Passing**

**Symptom:** Agent still asks "which symbol?"

**Debug Steps:**
1. Check backend logs for `[CHATKIT PROXY] Chart context:`
2. Verify `symbol`, `timeframe`, `snapshotId` props are defined
3. Add console.log in custom fetch function

**Solution:** Ensure props are passed from TradingDashboardSimple:

```typescript
// In TradingDashboardSimple.tsx (already done ✅)
<RealtimeChatKit
  symbol={selectedSymbol}
  timeframe={selectedTimeframe}
  snapshotId={currentSnapshot?.metadata?.snapshot_id}
/>
```

---

### **Issue 3: Drawing Commands Not Executing**

**Symptom:** Response contains commands but nothing draws on chart

**Debug Steps:**
1. Check `AgentResponseParser.containsDrawingCommands()` returns true
2. Verify `onChartCommand` callback is defined
3. Check parent component receives commands

**Solution:** Ensure `onChartCommand` prop wired correctly in TradingDashboardSimple.

---

## ✅ **Success Criteria**

After implementation, verify these work:

1. ✅ **Backend Receives ChatKit Messages**
   - Log shows: `[CHATKIT PROXY] Received: <message>`

2. ✅ **Chart Context Passes**
   - Log shows: `[CHATKIT PROXY] Chart context: {'symbol': 'TSLA', ...}`
   - Agent responds: "I'll draw these levels on your TSLA chart"

3. ✅ **Drawing Commands Execute**
   - Agent returns commands like `SUPPORT:450.00 "key level"`
   - Lines appear on chart at correct prices

4. ✅ **Network Requests**
   - DevTools shows: `POST /api/chatkit/proxy` (not `api.openai.com` directly)

5. ✅ **End-to-End Flow**
   - User types: "draw support and resistance"
   - Chart shows support/resistance lines
   - Response explains levels

---

## 📊 **Comparison: Before vs After**

### **Before (BROKEN):**
```
ChatKit → OpenAI API → Generic GPT-4 → Text response
❌ No chart context
❌ No drawing commands
❌ Backend bypassed
```

### **After (WORKING):**
```
ChatKit → Custom fetch() → /api/chatkit/proxy → Agent Orchestrator
✅ Chart context injected
✅ Drawing commands extracted
✅ Full backend logic
✅ Commands execute on chart
```

---

## 🚀 **Implementation Timeline**

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Backend proxy endpoint | 1 hour | 🔴 Not started |
| 2 | Frontend custom backend | 1 hour | 🔴 Not started |
| 3 | Verify agent orchestrator | 5 min | ✅ Already done |
| 4 | Test & debug | 30 min | 🔴 Not started |
| 5 | Deploy to production | 15 min | 🔴 Not started |

**Total: ~3 hours**

---

## 🎯 **Next Actions**

1. **Implement Phase 1** - Add `/api/chatkit/proxy` endpoint to `mcp_server.py`
2. **Implement Phase 2** - Update `RealtimeChatKit.tsx` with custom fetch
3. **Test locally** - Verify chart context and drawing commands
4. **Deploy** - Push to production via Fly.io
5. **Verify** - Test on production with Playwright

---

## 📚 **References**

- [ChatKit Custom Backends Documentation](https://openai.github.io/chatkit-js/guides/custom-backends)
- [ChatKit Widget Actions Documentation](https://openai.github.io/chatkit-js/guides/widget-actions)
- Our codebase:
  - `backend/services/agent_orchestrator.py` (lines 4594-4628: chart_context support)
  - `backend/services/chart_command_extractor.py` (drawing command parser)
  - `frontend/src/services/agentResponseParser.ts` (command extraction)

---

**Status:** ✅ Plan verified against actual codebase and ChatKit documentation

**Ready to implement:** YES

**Estimated time:** 3 hours

**Risk level:** LOW (well-documented ChatKit feature)

