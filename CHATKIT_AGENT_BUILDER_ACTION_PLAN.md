# ChatKit Agent Builder Custom Action Plan (FINAL)

## 🎯 Goal
Add a custom action to the Agent Builder "Gvses" agent node that calls our backend for chart control, enabling chart awareness and drawing commands while keeping the ChatKit UI.

---

## 📊 Current Workflow Analysis

**Agent Builder Workflow:**
```
Start → Intent Classifier → if/else → Gvses Agent → End
```

**Agent Builder URL:**
https://platform.openai.com/agent-builder/edit?version=draft&workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736

**Current Problem:**
- "Gvses" agent calls OpenAI directly
- No chart context
- No drawing commands
- Our backend bypassed

---

## ✅ Solution: Add Custom Action to Gvses Agent

### **Architecture:**

```
User Query → ChatKit → Agent Builder Workflow
                              ↓
                    Intent Classifier (routes query)
                              ↓
                    Gvses Agent (detects chart intent)
                              ↓
        Calls Custom Action: "chart_control"
                              ↓
        POST https://gvses-market-insights.fly.dev/api/chatkit/chart-action
                              ↓
        Our Backend:
          - Receives query + metadata
          - Gets chart context from session
          - Calls agent_orchestrator.process_query()
          - Returns drawing commands + analysis
                              ↓
        Agent Builder receives response
                              ↓
        ChatKit displays response
                              ↓
        Frontend parses drawing commands
                              ↓
        Chart commands executed
```

---

## 📋 Implementation Steps

### **Phase 1: Create Backend Chart Action Endpoint (30 min)**

**File:** `backend/mcp_server.py`

Add the custom action endpoint:

```python
class ChatKitChartActionRequest(BaseModel):
    """Request from Agent Builder custom action"""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatKitChartActionResponse(BaseModel):
    """Response to Agent Builder custom action"""
    success: bool
    text: str
    chart_commands: List[str] = []
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/api/chatkit/chart-action", response_model=ChatKitChartActionResponse)
async def chatkit_chart_action(request: ChatKitChartActionRequest):
    """
    Custom action endpoint for Agent Builder
    Handles chart control, pattern detection, drawing commands
    
    Called by Agent Builder's "Gvses" agent when chart-related queries detected
    """
    try:
        logger.info(f"[CHATKIT ACTION] Query: {request.query[:100]}...")
        logger.info(f"[CHATKIT ACTION] Session: {request.session_id}, User: {request.user_id}")
        
        # TODO: Retrieve chart context from session storage
        # For now, check if passed in metadata
        chart_context = None
        if request.metadata and 'chart_context' in request.metadata:
            chart_context = request.metadata['chart_context']
            logger.info(f"[CHATKIT ACTION] Chart context from metadata: {chart_context}")
        else:
            # Try to get from session storage (implement session store)
            # For now, we'll extract symbol from query if present
            import re
            symbol_match = re.search(r'\b([A-Z]{1,5})\b', request.query)
            if symbol_match:
                chart_context = {
                    'symbol': symbol_match.group(1),
                    'timeframe': '1D',  # default
                    'source': 'extracted_from_query'
                }
                logger.info(f"[CHATKIT ACTION] Extracted chart context: {chart_context}")
        
        # Call agent orchestrator
        from services.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=[],
            chart_context=chart_context
        )
        
        # Format response for Agent Builder
        response_text = result.get("text", "")
        chart_commands = result.get("chart_commands", [])
        
        logger.info(f"[CHATKIT ACTION] Generated {len(chart_commands)} chart commands")
        
        # Embed commands in response text so frontend can parse them
        if chart_commands:
            command_text = "\n\n" + "\n".join(chart_commands)
            response_text += command_text
        
        return ChatKitChartActionResponse(
            success=True,
            text=response_text,
            chart_commands=chart_commands,
            data={
                'tools_used': result.get('tools_used', []),
                'chart_context': chart_context,
                'timestamp': datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"[CHATKIT ACTION] Error: {e}", exc_info=True)
        return ChatKitChartActionResponse(
            success=False,
            text=f"I encountered an error processing your chart request: {str(e)}",
            chart_commands=[],
            error=str(e)
        )
```

**Test the endpoint:**
```bash
curl -X POST http://localhost:8000/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "draw support and resistance for TSLA",
    "session_id": "test_session",
    "metadata": {
      "chart_context": {
        "symbol": "TSLA",
        "timeframe": "1D"
      }
    }
  }' | jq
```

**Expected response:**
```json
{
  "success": true,
  "text": "I'll draw support and resistance levels for TSLA...\n\nSUPPORT:440.00 \"key level\"\nRESISTANCE:460.00 \"resistance zone\"",
  "chart_commands": [
    "SUPPORT:440.00 \"key level\"",
    "RESISTANCE:460.00 \"resistance zone\""
  ],
  "data": {
    "tools_used": ["detect_chart_patterns"],
    "chart_context": {"symbol": "TSLA", "timeframe": "1D"}
  }
}
```

---

### **Phase 2: Configure Agent Builder Custom Action (30 min)**

**Steps:**

1. **Open Agent Builder:**
   - Go to: https://platform.openai.com/agent-builder/edit?version=draft&workflow=wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736

2. **Click on "Gvses" Agent Node**

3. **Add Custom Action:**
   - Click "Add Action" or "Add Tool"
   - Name: `chart_control`
   - Description: `Analyze charts, draw support/resistance, detect patterns, control chart display`

4. **Configure Action Details:**

```json
{
  "name": "chart_control",
  "description": "Call this when user asks about charts, support/resistance, patterns, or technical analysis. Use it for queries like 'draw support and resistance', 'what patterns do you see?', 'analyze this chart', 'show trendlines'.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The user's chart-related query"
      },
      "session_id": {
        "type": "string",
        "description": "Current ChatKit session ID"
      },
      "metadata": {
        "type": "object",
        "description": "Additional context including chart_context with symbol and timeframe"
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

5. **Update Gvses Agent Instructions:**

Add this to the agent's system prompt:

```
When users ask about charts, patterns, support/resistance, or technical analysis:
1. Call the chart_control action with their query
2. Include session_id if available
3. Pass any chart_context (symbol, timeframe) in metadata if known
4. Display the response text naturally
5. The response may contain chart commands (SUPPORT:, RESISTANCE:, etc.) - include them

Always use chart_control for:
- "draw support and resistance"
- "what patterns do you see?"
- "analyze this chart"
- "show me trendlines"
- "detect patterns"
- Any chart-related technical analysis

If you don't know which chart is loaded, ask the user for the ticker symbol first, then call chart_control.
```

6. **Save and Publish:**
   - Click "Save"
   - Click "Publish" to make it live

---

### **Phase 3: Frontend Chart Context Passing (1 hour)**

We need to pass chart context to ChatKit so it can be forwarded to our custom action.

**Option A: Session Storage (Recommended)**

Store chart context in a session store that the backend can access.

**File:** `backend/services/session_store.py` (NEW)

```python
"""
Session Store for ChatKit Chart Context
Stores chart context keyed by session_id so custom actions can access it
"""
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

# In-memory store (TODO: move to Redis for production)
_session_store: Dict[str, Dict[str, Any]] = {}

class SessionStore:
    @staticmethod
    def set_chart_context(session_id: str, chart_context: Dict[str, Any]):
        """Store chart context for a session"""
        _session_store[session_id] = {
            'chart_context': chart_context,
            'updated_at': datetime.now().isoformat()
        }
        logger.info(f"[SESSION] Stored chart context for {session_id}: {chart_context}")
    
    @staticmethod
    def get_chart_context(session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chart context for a session"""
        session_data = _session_store.get(session_id)
        if session_data:
            logger.info(f"[SESSION] Retrieved chart context for {session_id}")
            return session_data.get('chart_context')
        return None
    
    @staticmethod
    def clear_old_sessions():
        """Clear sessions older than 24 hours"""
        cutoff = datetime.now() - timedelta(hours=24)
        old_sessions = [
            sid for sid, data in _session_store.items()
            if datetime.fromisoformat(data['updated_at']) < cutoff
        ]
        for sid in old_sessions:
            del _session_store[sid]
        if old_sessions:
            logger.info(f"[SESSION] Cleared {len(old_sessions)} old sessions")
```

**Add endpoint to update chart context:**

**File:** `backend/mcp_server.py`

```python
from services.session_store import SessionStore

class UpdateChartContextRequest(BaseModel):
    """Request to update chart context for a session"""
    session_id: str
    symbol: str
    timeframe: str
    snapshot_id: Optional[str] = None

@app.post("/api/chatkit/update-context")
async def update_chart_context(request: UpdateChartContextRequest):
    """
    Update chart context for a ChatKit session
    Called by frontend when chart changes (symbol, timeframe, etc)
    """
    try:
        SessionStore.set_chart_context(
            request.session_id,
            {
                'symbol': request.symbol,
                'timeframe': request.timeframe,
                'snapshot_id': request.snapshot_id,
                'timestamp': datetime.now().isoformat()
            }
        )
        return {"success": True, "session_id": request.session_id}
    except Exception as e:
        logger.error(f"Error updating chart context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**Update chart action to use session store:**

```python
@app.post("/api/chatkit/chart-action", response_model=ChatKitChartActionResponse)
async def chatkit_chart_action(request: ChatKitChartActionRequest):
    try:
        # Get chart context from session store
        chart_context = None
        if request.session_id:
            chart_context = SessionStore.get_chart_context(request.session_id)
        
        # Fallback to metadata if not in session
        if not chart_context and request.metadata:
            chart_context = request.metadata.get('chart_context')
        
        logger.info(f"[CHATKIT ACTION] Chart context: {chart_context}")
        
        # ... rest of existing code ...
```

**Frontend: Send chart context updates**

**File:** `frontend/src/components/RealtimeChatKit.tsx`

```typescript
// Add effect to update chart context when it changes
useEffect(() => {
  const updateChartContext = async () => {
    if (!symbol || !timeframe) return;
    
    const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const sessionId = localStorage.getItem('chatkit_session_id');
    
    if (!sessionId) {
      console.warn('[ChatKit] No session ID for context update');
      return;
    }
    
    try {
      await fetch(`${backendUrl}/api/chatkit/update-context`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          symbol: symbol,
          timeframe: timeframe,
          snapshot_id: snapshotId
        })
      });
      console.log('[ChatKit] Updated chart context:', { symbol, timeframe });
    } catch (err) {
      console.error('[ChatKit] Failed to update context:', err);
    }
  };
  
  updateChartContext();
}, [symbol, timeframe, snapshotId]);

// Also store session ID when ChatKit session created
const chatKitConfig = useMemo(() => ({
  api: {
    async getClientSecret(existing: any) {
      const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const deviceId = localStorage.getItem('chatkit_device_id') || `device_${Date.now()}`;

      const res = await fetch(`${backendUrl}/api/chatkit/session`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: deviceId,
          existing_session: existing || null
        }),
      });

      if (!res.ok) {
        throw new Error(`Session failed: ${res.status}`);
      }

      const { client_secret, session_id } = await res.json();
      localStorage.setItem('chatkit_device_id', deviceId);
      localStorage.setItem('chatkit_session_id', session_id); // NEW: Store session ID
      console.log('✅ ChatKit session established:', session_id);
      return client_secret;
    }
  },
  // ... rest of config ...
}), [symbol, timeframe, snapshotId]);
```

---

### **Phase 4: Test End-to-End (30 min)**

#### **Test 1: Verify Custom Action Registration**

1. Open Agent Builder
2. Check "Gvses" agent has `chart_control` action
3. Test in Agent Builder playground

#### **Test 2: Verify Backend Endpoint**

```bash
# Terminal 1: Start backend
cd backend && uvicorn mcp_server:app --reload

# Terminal 2: Test endpoint
curl -X POST http://localhost:8000/api/chatkit/chart-action \
  -H "Content-Type: application/json" \
  -d '{
    "query": "draw support and resistance",
    "session_id": "test_123",
    "metadata": {
      "chart_context": {
        "symbol": "TSLA",
        "timeframe": "1D"
      }
    }
  }' | jq

# Expected: success=true, chart_commands array populated
```

#### **Test 3: Verify Chart Context Passing**

```typescript
// In browser console:
// 1. Load TSLA chart
// 2. Check localStorage
localStorage.getItem('chatkit_session_id') // Should have value

// 3. Check backend received context
// Look in backend logs for: [SESSION] Stored chart context for <session_id>: {'symbol': 'TSLA', ...}
```

#### **Test 4: Full End-to-End Flow**

1. Load TSLA chart
2. Open ChatKit
3. Type: "draw support and resistance"
4. Verify:
   - ✅ Backend logs show `[CHATKIT ACTION] Query: draw support and resistance`
   - ✅ Backend logs show `[CHATKIT ACTION] Chart context: {'symbol': 'TSLA', ...}`
   - ✅ Response contains SUPPORT: and RESISTANCE: commands
   - ✅ Lines appear on TSLA chart

---

## 📊 Success Criteria

| Criteria | Verification | Status |
|----------|-------------|--------|
| Custom action exists in Agent Builder | Check "Gvses" agent config | 🔴 |
| Backend endpoint responds | curl test returns 200 | 🔴 |
| Chart context stored | Backend logs show context | 🔴 |
| Chart context retrieved | Custom action receives context | 🔴 |
| Drawing commands generated | Response contains SUPPORT:, RESISTANCE: | 🔴 |
| Commands execute on chart | Lines appear on chart | 🔴 |
| Agent aware of chart | Agent says "your TSLA chart" | 🔴 |

---

## 🚀 Implementation Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Backend chart-action endpoint | 30 min | 🔴 |
| 2 | Agent Builder custom action | 30 min | 🔴 |
| 3 | Frontend context passing | 1 hour | 🔴 |
| 4 | Test & debug | 30 min | 🔴 |
| 5 | Deploy to production | 15 min | 🔴 |

**Total: ~3 hours**

---

## 🎯 Next Actions

**Ready to implement:**

1. ✅ Create `/api/chatkit/chart-action` endpoint
2. ✅ Create session store for chart context
3. ✅ Test backend endpoint locally
4. ✅ Configure Agent Builder custom action
5. ✅ Update frontend to pass chart context
6. ✅ Test end-to-end locally
7. ✅ Deploy to production
8. ✅ Verify with Playwright

---

**Status:** ✅ Plan verified, ready to implement

**Confidence:** HIGH (Agent Builder custom actions are well-documented)

**Risk:** LOW (isolated changes, easy to rollback)

