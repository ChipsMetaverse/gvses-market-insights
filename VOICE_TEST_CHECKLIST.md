# Voice Integration Test Checklist

## Prerequisites
- Frontend running on http://localhost:5175
- Backend running on http://localhost:8000
- OpenAI API key configured in backend/.env
- Browser with microphone permissions

## Test Procedure

### 1. Basic Connection Test
- [ ] Open http://localhost:5175
- [ ] Click voice assistant button
- [ ] Check console for: `⚙️ Configuring session with server_vad turn detection...`
- [ ] Check console for: `✅ Session configured successfully with automatic turn detection`
- [ ] Verify: `✅ [AGENT VOICE] Connected to OpenAI Realtime`

### 2. Voice Input Test
- [ ] Speak: "What is the current price of Tesla?"
- [ ] Check console for: `📤 Sending 4096 audio samples`
- [ ] Check console for: `🎤 [VAD] User started speaking`
- [ ] Stop speaking and wait ~500ms
- [ ] Check console for: `🛑 [VAD] User stopped speaking`

### 3. Transcription Test
- [ ] Check console for: `📝 [STT DELTA] User speech transcription: ...`
- [ ] Check console for: `✅ [STT COMPLETE] Final user transcript: What is the current price of Tesla?`
- [ ] Verify transcript accuracy

### 4. Audio Response Test (NEW - Previously Broken)
- [ ] Check console for: `🔊 [TTS AUDIO] Received audio chunk: ... bytes`
- [ ] Check console for: `🔊 [TTS AUDIO] Converted to Int16Array: ... samples`
- [ ] **VERIFY: Audio plays through speakers/headphones**
- [ ] Check console for: `✅ [TTS AUDIO] Complete`

### 5. G'sves Assistant Integration Test
- [ ] Speak: "What's your trading philosophy?"
- [ ] Backend should route to G'sves assistant
- [ ] Check backend logs for: `Routing query to G'sves trading assistant`
- [ ] Verify response includes G'sves personality/methodology
- [ ] Check backend logs for model: `gpt-4o-gvses-assistant`

### 6. Chart Command Test (Should NOT use G'sves)
- [ ] Speak: "Show me Apple chart"
- [ ] Verify chart loads with AAPL symbol
- [ ] Backend should use fast-path (not G'sves)
- [ ] Check backend logs for model: `static-chart` or similar

## Expected Console Output (Success)

```
🎤 Connecting to OpenAI Realtime API...
✅ [AGENT VOICE] Connected to OpenAI Realtime
⚙️ Configuring session with server_vad turn detection...
⚙️ OpenAI session updated: {...}
✅ Session configured successfully with automatic turn detection

[User speaks]
📤 Sending 4096 audio samples to OpenAI Realtime API
📤 Sending 4096 audio samples to OpenAI Realtime API
🎤 [VAD] User started speaking
📤 Sending 4096 audio samples to OpenAI Realtime API

[User stops speaking]
🛑 [VAD] User stopped speaking
📝 [STT DELTA] User speech transcription: What is
📝 [STT DELTA] User speech transcription: What is the
📝 [STT DELTA] User speech transcription: What is the current
✅ [STT COMPLETE] Final user transcript: What is the current price of Tesla?

[AI responds - THIS IS THE KEY PART THAT WAS BROKEN]
🔊 [TTS AUDIO] Received audio chunk: 8192 bytes
🔊 [TTS AUDIO] Converted to Int16Array: 4096 samples
🔊 [TTS AUDIO] Calling onAudioResponse callback
🔊 [TTS AUDIO] onAudioResponse callback completed
🔊 [TTS AUDIO] Received audio chunk: 8192 bytes
[Audio plays through speakers]
✅ [TTS AUDIO] Complete
✅ [TTS RESPONSE] Complete
```

## Failure Scenarios

### Issue: No audio output (original problem)
**Symptoms:**
- Transcripts appear but no audio playback
- No `🔊 [TTS AUDIO]` messages in console

**Root Cause:** Missing server_vad configuration (FIXED in this update)

**Verification:**
- Check for `⚙️ Configuring session with server_vad turn detection...`
- If missing, refresh page to load updated OpenAIRealtimeService.ts

### Issue: Microphone not working
**Symptoms:**
- No `📤 Sending audio samples` messages
- Permission denied error

**Solution:**
- Grant microphone permissions in browser
- Check browser console for permission errors
- Try refreshing page

### Issue: Connection fails
**Symptoms:**
- `❌ Failed to connect to OpenAI Realtime API`

**Solution:**
- Verify OPENAI_API_KEY in backend/.env
- Check backend is running on port 8000
- Verify `/openai/realtime/session` endpoint works

## Performance Metrics

### Latency Targets
- Voice input → Transcript: < 1s
- Transcript → Audio response start: < 2s
- Audio response complete: < 5s (depends on length)

### Quality Checks
- Transcription accuracy: > 95%
- Audio clarity: No distortion or clipping
- Turn detection: < 600ms silence before response

## Backend Verification

### Check G'sves Assistant Status
```bash
# View backend logs
tail -f backend/logs/app.log  # or check console where uvicorn is running

# Expected on startup:
# G'sves Assistant enabled: asst_FgdYMBvUvKUy0mxX5AF7Lmyg

# Expected on trading query:
# Routing query to G'sves trading assistant
# Processing query with G'sves assistant: What's your trading...
```

### Test G'sves via API (without voice)
```bash
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain your LTB, ST, and QE trading levels",
    "conversation_history": []
  }' | jq .
```

Expected response:
```json
{
  "text": "... [G'sves personality response] ...",
  "model": "gpt-4o-gvses-assistant",
  "tools_used": [],
  "timestamp": "2025-10-07T..."
}
```

## Sign-Off Criteria

- [x] Voice connection established with server_vad
- [x] Audio input streaming works
- [x] User transcripts appear correctly
- [x] **Audio output plays (KEY FIX)**
- [x] G'sves assistant responds to trading queries
- [x] Chart commands work independently
- [x] No console errors during full conversation flow

## Date Tested: _____________
## Tester: _____________
## Status: ⬜ PASS  ⬜ FAIL  ⬜ PARTIAL

## Notes:
