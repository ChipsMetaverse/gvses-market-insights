# Voice Assistant Debugging Status

## Issue Summary
User reported voice assistant showing "I couldn't generate a response" for queries like:
- "What is the price of Bitcoin?"
- "What is the price of Ethereum?"
- "What is the price of Apple?"

## Investigation Findings

### ✅ What's Working
1. **OpenAI Realtime WebSocket**: Connected successfully, STT working
2. **Microphone Access**: User speech being captured and transcribed
3. **Speech-to-Text (STT)**: User queries correctly transcribed
   - Example: "What is the price of Bitcoin?" ✅
4. **Backend Agent Endpoint**: `/api/agent/orchestrate` works correctly when tested directly
   - Test confirmed: `curl http://localhost:8000/api/agent/orchestrate` returns proper responses
5. **TTS Audio Handler**: Added `response.audio.delta` event with base64 decoder

### ❌ The Problem
When called via the **voice pipeline**, the agent returns "I couldn't generate a response" instead of the actual answer.

### 🔍 Root Cause Analysis

**Evidence**:
1. User's console logs showed STT completion but NO backend logs for `/api/agent/orchestrate`
2. Direct `curl` test of `/api/agent/orchestrate` produces backend logs and works perfectly
3. Frontend code shows correct endpoint being called (`/api/agent/orchestrate`)
4. Error message "I couldn't generate a response" comes from `agent_orchestrator.py` when `response_text` is empty

**Hypothesis**:
The HTTP request from frontend to backend is either:
- Not being made at all (silently failing)
- Timing out before completion
- Returning an empty response for some reason
- Being blocked/intercepted

## Diagnostic Tools Added

### 1. Enhanced Frontend Logging
Added comprehensive console logging to:
- `useAgentVoiceConversation.ts` - Shows when `sendQuery()` is called and what response is received
- `agentOrchestratorService.ts` - Shows HTTP request/response details

### 2. Test HTML Page
Created `/test_voice_flow.html` for isolated testing:
- Tests agent orchestrator endpoint directly
- Tests OpenAI session creation
- Simulates complete voice flow

### 3. Playwright Test
Created `test-voice-flow.spec.ts` for automated testing

## Next Steps for User

### Test 1: Check Enhanced Logs
1. Open the app at http://localhost:5174
2. Click the microphone and say "What is the price of Bitcoin?"
3. Open browser DevTools Console (F12)
4. Look for these specific log messages:

```
✅ [STT COMPLETE] Final user transcript: What is the price of Bitcoin?
[AGENT VOICE] 🚀 Calling agentOrchestratorService.sendQuery() with: {...}
[AGENT ORCHESTRATOR SERVICE] 🌐 Making HTTP request to /api/agent/orchestrate
[AGENT ORCHESTRATOR SERVICE] 📡 HTTP response received: {...}
[AGENT ORCHESTRATOR SERVICE] 📦 Parsed JSON response: {...}
[AGENT VOICE] 📦 Received agent response: {...}
```

### Test 2: Run Test Page
1. Open http://localhost:8000/test_voice_flow.html
2. Click "Test Agent Orchestrator" button
3. Check if it shows "✅ Valid response received" or "⚠️ WARNING: Empty or error response"

### Test 3: Check Backend Logs
While running voice queries, watch the backend terminal for:
```
INFO:     127.0.0.1:XXXXX - "POST /api/agent/orchestrate HTTP/1.1" 200 OK
```

If this line appears, the request is reaching the backend.
If it doesn't appear, the request is failing in the frontend.

## Expected Diagnostic Outcomes

### Scenario A: Backend Receives Request
**Logs will show**:
- Frontend: All logs from "Making HTTP request" through "Parsed JSON response"
- Backend: `POST /api/agent/orchestrate` with 200 OK
- Response has empty `text` field

**Solution**: Issue in agent orchestrator logic - need to debug why it returns empty text for voice queries

### Scenario B: Backend Never Receives Request
**Logs will show**:
- Frontend: "Making HTTP request" but NO "HTTP response received"
- Backend: NO logs for `/api/agent/orchestrate`

**Solution**: Network/CORS issue, timeout, or frontend error before request completes

### Scenario C: Request Fails with Error
**Logs will show**:
- Frontend: "❌ Agent orchestrator error: ..."
- Error details in console

**Solution**: Fix the specific error shown

## Files Modified

### Frontend
1. `frontend/src/hooks/useAgentVoiceConversation.ts` - Added request/response logging
2. `frontend/src/services/agentOrchestratorService.ts` - Added HTTP request logging
3. `frontend/src/services/OpenAIRealtimeService.ts` - Added TTS audio event handler with base64 decoder

### Test Files Created
1. `test_voice_flow.html` - Manual test page
2. `test-voice-flow.spec.ts` - Automated Playwright test

## Summary of Voice Pipeline

```
User speaks → Microphone → OpenAI Realtime STT → Transcript
                                                      ↓
                                                 sendToAgent()
                                                      ↓
                                         agentOrchestratorService.sendQuery()
                                                      ↓
                                         POST /api/agent/orchestrate
                                                      ↓
                                         Agent Orchestrator processes
                                                      ↓
                                         Returns {text, tools_used, data}
                                                      ↓
                                         Frontend displays message
                                                      ↓
                                         Sends text to OpenAI TTS
                                                      ↓
                                         Audio played to user
```

**Current Status**: Pipeline breaks somewhere between STT and agent response. Enhanced logging will pinpoint exact failure point.

## Technical Details

### Agent Orchestrator Response Format
```json
{
  "text": "The actual response text",
  "tools_used": ["tool1", "tool2"],
  "data": {},
  "timestamp": "2025-10-05T...",
  "model": "gpt-5-mini",
  "cached": false,
  "chart_commands": []
}
```

### Error Response Format
When agent fails:
```json
{
  "text": "I couldn't generate a response.",
  ...
}
```

This happens in `agent_orchestrator.py` when `response_text` is `None` or empty.

## Commands for Quick Testing

### Test Backend Directly
```bash
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query":"What is the price of Bitcoin?"}'
```

Expected: Valid response with Bitcoin price information

### Watch Backend Logs
```bash
# Backend logs should show:
INFO:     127.0.0.1:XXXXX - "POST /api/agent/orchestrate HTTP/1.1" 200 OK
INFO:services.agent_orchestrator:Query: 'What is the price of Bitcoin?' → Intent: price-only
```

### Check Frontend Logs
Open browser DevTools → Console tab → Filter for "[AGENT"
