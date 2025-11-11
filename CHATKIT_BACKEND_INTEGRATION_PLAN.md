# ChatKit Backend Integration Plan

## 🎯 Goal
Make ChatKit call our backend agent orchestrator while maintaining the ChatKit UI, enabling chart awareness and drawing commands.

---

## 🔍 Current Architecture (BROKEN)

```
User → ChatKit iframe → OpenAI API directly
                         ↓
                    Generic GPT-4 (no chart context)
                         ↓
                    Text response only
```

**Problems:**
- ❌ No chart context
- ❌ No drawing commands
- ❌ No backend orchestrator
- ❌ All our fixes are bypassed

---

## ✅ Target Architecture (WORKING)

```
User → ChatKit iframe → OpenAI Agent Builder
                         ↓
                    (detects chart intent)
                         ↓
                    Custom Action: "chart_control"
                         ↓
        ┌───────────────────────────────────┐
        │  POST /api/chatkit/chart-action   │
        │  - Receives chart context         │
        │  - Calls agent orchestrator       │
        │  - Returns drawing commands       │
        └───────────────────────────────────┘
                         ↓
                    ChatKit displays response
                         ↓
        window.postMessage({ chart_commands: [...] })
                         ↓
        Parent window executes drawings
```

---

## 📋 Implementation Steps

### Phase 1: Create ChatKit Custom Action Endpoint (1 hour)

**File:** `backend/mcp_server.py`

Add new endpoint:

```python
class ChatKitActionRequest(BaseModel):
    """Request from ChatKit custom action"""
    query: str
    conversation_id: Optional[str] = None
    chart_context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/api/chatkit/chart-action")
async def chatkit_chart_action(request: ChatKitActionRequest):
    """
    Custom action for ChatKit Agent Builder
    Receives chart queries and returns drawing commands + analysis
    """
    try:
        logger.info(f"[CHATKIT ACTION] Query: {request.query[:100]}...")
        logger.info(f"[CHATKIT ACTION] Chart context: {request.chart_context}")
        
        # Call our agent orchestrator with chart context
        from services.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=[],
            chart_context=request.chart_context
        )
        
        # Format response for ChatKit
        response = {
            "success": True,
            "text": result.get("text", ""),
            "chart_commands": result.get("chart_commands", []),
            "tools_used": result.get("tools_used", []),
            "metadata": {
                "symbol": request.chart_context.get("symbol") if request.chart_context else None,
                "timeframe": request.chart_context.get("timeframe") if request.chart_context else None,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        logger.info(f"[CHATKIT ACTION] Returning {len(response['chart_commands'])} chart commands")
        
        return response
        
    except Exception as e:
        logger.error(f"[CHATKIT ACTION] Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "text": f"I encountered an error: {str(e)}"
        }
```

---

### Phase 2: Configure Agent Builder Custom Action (30 min)

**Location:** OpenAI Agent Builder Dashboard (https://platform.openai.com/assistants)

**Steps:**

1. **Go to Agent Builder** for workflow ID: `chart_agent_workflow_123`
2. **Add Custom Action:**

```json
{
  "name": "chart_control",
  "description": "Analyze charts, draw support/resistance, detect patterns, and control chart display",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "User's chart-related query"
      },
      "chart_context": {
        "type": "object",
        "description": "Current chart state",
        "properties": {
          "symbol": {"type": "string"},
          "timeframe": {"type": "string"},
          "snapshot_id": {"type": "string"}
        }
      }
    },
    "required": ["query"]
  },
  "endpoint": {
    "url": "https://gvses-market-insights.fly.dev/api/chatkit/chart-action",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json"
    }
  }
}
```

3. **Update Agent Instructions:**

```
You are a trading assistant with chart control capabilities.

When users ask about charts, support/resistance, patterns, or technical analysis:
1. Call the chart_control action with their query
2. Include the current chart_context if available
3. Display the response text naturally
4. Emit any chart_commands for the parent window to execute

Example queries that need chart_control:
- "draw support and resistance"
- "what patterns do you see?"
- "show me trendlines"
- "analyze this chart"
- "load AAPL"

Always check for chart context before calling chart_control.
If no chart is loaded, ask the user which symbol they want to analyze.
```

---

### Phase 3: Frontend Chart Context Injection (1 hour)

**File:** `frontend/src/components/RealtimeChatKit.tsx`

Modify to pass chart context to ChatKit:

```typescript
// Add chart context to ChatKit config
const chatKitConfig = useMemo(() => ({
  api: {
    async getClientSecret(existing: any) {
      // ... existing code ...
    }
  },
  // NEW: Add custom context provider
  contextProvider: {
    getChartContext: () => ({
      symbol: symbol,
      timeframe: timeframe,
      snapshot_id: snapshotId,
      timestamp: new Date().toISOString()
    })
  },
  // NEW: Listen for chart commands from ChatKit
  onAction: (action: any) => {
    if (action.type === 'chart_control' && action.result?.chart_commands) {
      console.log('[ChatKit] Received chart commands:', action.result.chart_commands);
      onChartCommand?.(action.result.chart_commands);
    }
  }
}), [symbol, timeframe, snapshotId, onChartCommand]);
```

---

### Phase 4: PostMessage Bridge (30 min)

**If contextProvider doesn't work**, use postMessage:

**File:** `frontend/src/components/RealtimeChatKit.tsx`

```typescript
useEffect(() => {
  // Listen for chart command requests from ChatKit iframe
  const handleMessage = (event: MessageEvent) => {
    if (event.data?.type === 'chatkit_request_context') {
      // Send chart context back to iframe
      const iframe = document.querySelector('iframe[name="chatkit"]');
      if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({
          type: 'chart_context',
          data: {
            symbol,
            timeframe,
            snapshot_id: snapshotId
          }
        }, '*');
      }
    }
    
    if (event.data?.type === 'chatkit_chart_commands') {
      // Execute chart commands
      console.log('[ChatKit Bridge] Executing commands:', event.data.commands);
      onChartCommand?.(event.data.commands);
    }
  };
  
  window.addEventListener('message', handleMessage);
  return () => window.removeEventListener('message', handleMessage);
}, [symbol, timeframe, snapshotId, onChartCommand]);
```

---

### Phase 5: Backend Chart Command Parsing (Already Done! ✅)

Our backend already has this in `agent_orchestrator.py`:
- ✅ Drawing command extraction
- ✅ Chart context injection
- ✅ Pattern detection
- ✅ Tool execution

---

## 🧪 Testing Plan

### Test 1: Chart Context Injection
```
1. Load TSLA chart
2. Open ChatKit
3. Send message: "what chart is loaded?"
4. Expected: "You're viewing TSLA on 1D timeframe"
```

### Test 2: Drawing Commands
```
1. Load TSLA chart
2. Send message: "draw support and resistance"
3. Expected:
   - Backend receives chart_context: {symbol: "TSLA", timeframe: "1D"}
   - Agent returns SUPPORT: and RESISTANCE: commands
   - Commands execute on chart
   - Lines appear on TSLA chart
```

### Test 3: Pattern Detection
```
1. Load NVDA chart
2. Send message: "detect patterns"
3. Expected:
   - detect_chart_patterns tool called
   - Pattern overlays drawn on chart
   - Response explains detected patterns
```

---

## 📊 Success Metrics

- ✅ ChatKit calls `/api/chatkit/chart-action` (check logs)
- ✅ Chart context passes correctly (symbol, timeframe)
- ✅ Drawing commands execute (lines appear on chart)
- ✅ Agent aware of loaded chart (doesn't ask "which symbol?")
- ✅ Pattern detection works through ChatKit
- ✅ Network log shows POST to our backend (not just OpenAI)

---

## 🚨 Fallback Plan

If Agent Builder custom actions don't work:

### **Option B: Webhook Interceptor**

Create a middleware that intercepts ChatKit messages:

```python
@app.post("/api/chatkit/webhook")
async def chatkit_webhook(request: dict):
    """
    Webhook receiver for ChatKit messages
    OpenAI Agent Builder can be configured to send all messages here first
    """
    message = request.get("message", "")
    user_id = request.get("user_id", "")
    
    # Detect chart intent
    if any(keyword in message.lower() for keyword in ["draw", "chart", "pattern", "support", "resistance"]):
        # Get chart context from user session
        chart_context = await get_user_chart_context(user_id)
        
        # Process with agent orchestrator
        result = await orchestrator.process_query(message, chart_context=chart_context)
        
        # Return modified response
        return {
            "response": result["text"],
            "commands": result.get("chart_commands", [])
        }
    
    # Pass through to ChatKit for non-chart queries
    return {"response": None}
```

---

## 🎯 Recommended Approach

**Start with Phase 1-3** (Custom Action endpoint + Agent Builder config):
- **Time:** 2.5 hours
- **Risk:** Low (if Agent Builder supports custom actions)
- **Benefit:** Clean integration with ChatKit UI

**If that fails**, implement **postMessage bridge** (Phase 4):
- **Time:** +30 min
- **Risk:** Medium (iframe security)
- **Benefit:** Works without Agent Builder support

---

## 🚀 Next Steps

1. ✅ **Create `/api/chatkit/chart-action` endpoint** (30 min)
2. ✅ **Test endpoint with curl** (5 min)
3. ✅ **Configure Agent Builder** (30 min)
4. ✅ **Update frontend ChatKit config** (1 hour)
5. ✅ **Test end-to-end** (30 min)
6. ✅ **Deploy to production** (15 min)

**Total estimated time: 3 hours**

---

**Should I proceed with implementation?**

