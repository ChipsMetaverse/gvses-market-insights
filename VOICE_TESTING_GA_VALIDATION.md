# Voice Testing - GA Compliance Validation

## Test Environment
- **Frontend**: http://localhost:5175
- **Backend**: http://localhost:8000
- **Date**: October 5, 2025
- **Configuration**: GA-compliant OpenAI Realtime API with passive voice I/O

## Critical Fixes Implemented

### 1. Backend Session Configuration (GA-Compliant)
**File**: `backend/services/openai_relay_server.py:173-234`

**Changes**:
- ✅ Changed `turn_detection: {type: "none"}` (was `server_vad`) - **CRITICAL FIX**
- ✅ Updated to GA audio schema: `audio.input.format`, `audio.output.voice`
- ✅ Removed deprecated fields: `modalities`, `voice`, `input_audio_format`
- ✅ Removed `response.cancel` message (not needed with turn_detection: none)
- ✅ Passive instructions (no autonomous responses)

### 2. Frontend Microphone Integration
**File**: `frontend/src/hooks/useAgentVoiceConversation.ts`

**Changes**:
- ✅ Added `useOpenAIAudioProcessor` integration
- ✅ Microphone requested BEFORE WebSocket connection
- ✅ Proper cleanup on disconnect
- ✅ Added `isRecording` state to return value

### 3. Response Type Guard
**File**: `frontend/src/services/OpenAIRealtimeService.ts:342-365`

**Changes**:
- ✅ Added type check: `item.type === 'response'`
- ✅ Try-catch for cancel errors
- ✅ Better error logging

### 4. Token Limit Fix
**File**: `backend/services/agent_orchestrator.py:3377-3378`

**Changes**:
- ✅ Increased max_tokens from 800 to 1500 for complex queries

## Pre-Flight Checklist

### Backend Status
- [x] Backend running on port 8000
- [x] OpenAI relay active (`openai_relay_ready: true`)
- [x] GA-compliant session config deployed
- [x] Turn detection set to "none"

### Frontend Status
- [x] Frontend running on port 5175
- [ ] Browser cache cleared (hard refresh required)
- [ ] Microphone permissions ready

## Test Procedures

### Test 1: Microphone Permission Request
**Expected Behavior**: Browser should show microphone permission prompt

**Steps**:
1. Open http://localhost:5175 in Chrome/Edge
2. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
3. Click microphone button in UI
4. **VERIFY**: Browser shows "Allow microphone access?" prompt
5. Click "Allow"

**Success Criteria**:
- [ ] Permission prompt appears
- [ ] Microphone icon shows "recording" state
- [ ] Console shows: `✅ [AGENT VOICE] Microphone access granted`

**Failure Indicators**:
- ❌ No permission prompt
- ❌ Connection shows "connected" but no microphone request
- ❌ Console error: "Microphone access denied"

---

### Test 2: Passive Mode Verification (CRITICAL)
**Expected Behavior**: OpenAI should remain SILENT after connection

**Steps**:
1. Connect voice (microphone active)
2. Wait 5 seconds in complete silence
3. Check browser console

**Success Criteria**:
- [ ] **NO** `response.audio_transcript.delta` events in console
- [ ] **NO** auto-greeting from AI
- [ ] **NO** autonomous responses to silence
- [ ] Console shows: `✅ GA-compliant session configured: PASSIVE voice I/O`

**Failure Indicators**:
- ❌ `response.audio_transcript.delta` events appear
- ❌ AI speaks without user input
- ❌ Console shows OpenAI generating text autonomously

---

### Test 3: User Speech Recognition (STT)
**Expected Behavior**: User speech should be transcribed accurately

**Steps**:
1. With microphone active, speak clearly: **"What is the price of Tesla?"**
2. Monitor browser console

**Success Criteria**:
- [ ] Console shows: `📝 [USER STT] New user speech started - ID: <id>`
- [ ] Console shows: `📝 [USER STT] Transcript: "what is the price of Tesla"`
- [ ] Console shows: `✅ [FINAL] User speech completed, emitting final transcript`
- [ ] Console shows: `✅ [AGENT VOICE] Sending to agent: what is the price of Tesla`

**Failure Indicators**:
- ❌ No transcript appears
- ❌ Transcript is for "assistant" role instead of "user"
- ❌ Transcript incomplete or cut off

---

### Test 4: Agent Response Generation
**Expected Behavior**: Agent should process query and return market data

**Steps**:
1. After speaking "What is the price of Tesla?"
2. Wait for agent processing
3. Check console for agent response

**Success Criteria**:
- [ ] Console shows: `📊 [AGENT] Calling tool: get_stock_price`
- [ ] Console shows: `✅ [AGENT] Tool result:` with Tesla price data
- [ ] Console shows: `🤖 [AGENT] Generated response:` with formatted answer
- [ ] Response includes current Tesla price (e.g., "$234.56")

**Failure Indicators**:
- ❌ Empty response: `I couldn't generate a response`
- ❌ Response cut off (token limit issue)
- ❌ Tool call fails or times out

---

### Test 5: Text-to-Speech (TTS) Output
**Expected Behavior**: Agent response should be spoken aloud

**Steps**:
1. After agent generates response
2. Listen for audio playback

**Success Criteria**:
- [ ] Console shows: `📤 Sending text for TTS:` with agent response
- [ ] Console shows: `🔊 Audio delta received:` with sample counts
- [ ] Audio plays through speakers with OpenAI voice ("alloy")
- [ ] Speech is clear and natural

**Failure Indicators**:
- ❌ No audio playback
- ❌ Console shows: `🔊 playNextAudio: Skipping - queueLength: 0`
- ❌ AudioContext suspended or failed to initialize

---

### Test 6: Complex Query (Token Limit Validation)
**Expected Behavior**: Complex queries should return full responses

**Steps**:
1. Type in text input (or speak): **"Build a trading plan for this week"**
2. Wait for agent response

**Success Criteria**:
- [ ] Response includes multiple sections:
  - Market analysis
  - Entry points
  - Stop loss levels
  - Profit targets
  - Risk management
- [ ] Response NOT truncated
- [ ] Response length > 500 characters

**Failure Indicators**:
- ❌ Response ends abruptly mid-sentence
- ❌ Missing sections (e.g., no risk management)
- ❌ Response: `I couldn't generate a response`

---

### Test 7: Turn-Taking and Interruption
**Expected Behavior**: User can interrupt AI speech, AI waits for user to finish

**Steps**:
1. Ask a question that generates long response
2. While AI is speaking, start speaking again
3. Check console

**Success Criteria**:
- [ ] Console shows: `🛑 Cancelled active response:` (if AI was speaking)
- [ ] New user transcript starts immediately
- [ ] No overlapping speech

**Failure Indicators**:
- ❌ AI continues speaking over user
- ❌ Console error: `response_cancel_not_active`
- ❌ User speech not recognized during AI playback

---

## Console Event Flow Reference

### Correct Flow (Passive Mode with User Query)
```
✅ GA-compliant session configured: PASSIVE voice I/O (turn_detection: none)
🎤 Sending <N> audio samples to OpenAI Realtime API
📝 [USER STT] New user speech started - ID: msg_abc123
📝 [USER STT] Transcript: "what is the price of Tesla"
✅ [FINAL] User speech completed, emitting final transcript: what is the price of Tesla
✅ [AGENT VOICE] Sending to agent: what is the price of Tesla
📊 [AGENT] Calling tool: get_stock_price
✅ [AGENT] Tool result: {"symbol": "TSLA", "price": 234.56, ...}
🤖 [AGENT] Generated response: Tesla is currently trading at $234.56...
📤 Sending text for TTS: Tesla is currently trading at $234.56...
🔊 Audio delta received: 4800 samples
🔊 playNextAudio: Starting playback
```

### Incorrect Flow (Autonomous Mode - Should NOT happen)
```
❌ response.audio_transcript.delta {"transcript": "Hello! How can I help..."}
❌ OpenAI generating autonomous responses
```

## Known Issues to Watch For

### Issue 1: Autonomous Responses
**Symptom**: AI speaks immediately after connection without user input
**Cause**: `turn_detection` not set to "none" or conversational instructions
**Fix Applied**: `turn_detection: {type: "none"}` + passive instructions
**Validation**: No `response.audio_transcript.delta` events in console

### Issue 2: Microphone Not Requested
**Symptom**: Connection shows "connected" but no permission prompt
**Cause**: Missing `useOpenAIAudioProcessor` integration
**Fix Applied**: Added microphone setup in `useAgentVoiceConversation.ts`
**Validation**: Browser permission prompt appears

### Issue 3: Token Limit Truncation
**Symptom**: Complex responses cut off mid-sentence
**Cause**: max_tokens too low (was 800)
**Fix Applied**: Increased to 1500 for complex queries
**Validation**: Full responses for "build a trading plan" queries

### Issue 4: Response Cancel Errors
**Symptom**: Console shows `response_cancel_not_active` errors
**Cause**: Trying to cancel non-response items or inactive responses
**Fix Applied**: Type guard checking `item.type === 'response'`
**Validation**: No cancel errors in console

## Browser Console Commands

### Check OpenAI Connection Status
```javascript
// In browser console
console.log("Connected:", window.realtimeService?.isConnected());
console.log("Recording:", window.audioProcessor?.isRecording);
```

### Force Hard Refresh
```
Chrome/Edge: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
Firefox: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
Safari: Cmd+Option+R (Mac)
```

### Check AudioContext State
```javascript
// In browser console
console.log("AudioContext state:", window.audioContext?.state);
```

## Environment Variables to Verify

### Backend (.env)
```bash
OPENAI_API_KEY=sk-...  # Required for Realtime API
ANTHROPIC_API_KEY=sk-ant-...  # Required for agent
ELEVENLABS_API_KEY=...  # Optional (agent uses OpenAI voice)
```

### Frontend (.env.development)
```bash
VITE_API_URL=http://localhost:8000  # Must match backend port
```

## Success Metrics

### Minimum Viable Test Pass
- [x] Backend GA-compliant config deployed
- [ ] Microphone permission prompt appears
- [ ] NO autonomous responses (passive mode confirmed)
- [ ] User speech transcribed correctly
- [ ] Agent generates response with market data
- [ ] Audio playback works

### Full Production Readiness
- [ ] All 7 tests pass
- [ ] No console errors or warnings
- [ ] Voice quality clear and natural
- [ ] Response times < 3 seconds
- [ ] Turn-taking works smoothly
- [ ] Complex queries return full responses

## Next Steps After Testing

### If Tests Pass
1. Document any edge cases discovered
2. Test with multiple browsers (Chrome, Firefox, Safari, Edge)
3. Test on mobile devices (iOS Safari, Android Chrome)
4. Deploy to production environment
5. Monitor production logs for autonomous response events

### If Tests Fail
1. Check browser console for specific error messages
2. Verify backend logs: `tail -f /tmp/backend_ga.log`
3. Confirm WebSocket connection in Network tab
4. Validate OpenAI API key has Realtime API access
5. Test with `gpt-4o-realtime-2024-10-01` (standard GA model)

## Additional Resources

- **OpenAI Realtime API Docs**: https://platform.openai.com/docs/guides/realtime
- **GA Release Notes**: https://platform.openai.com/docs/api-reference/realtime
- **Turn Detection Modes**: https://platform.openai.com/docs/guides/realtime#turn-detection
- **Audio Formats**: PCM16, 24kHz, mono (matching our config)

---

**Status**: Ready for manual browser testing
**Tester**: Please follow Test 1-7 in order and check boxes as completed
**Report**: Document any failures with console logs and error messages
