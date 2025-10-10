# Voice Pipeline Testing Guide

## Quick Start - 5 Minute Test

**URL**: http://localhost:5175
**Browser**: Chrome/Edge (best support for Web Audio API)
**Action**: Click the 🎙️ floating button (bottom-right corner)

---

## Complete Pipeline Test (Step-by-Step)

### Prerequisites
- ✅ Backend running on port 8000
- ✅ Frontend running on port 5175
- ✅ Browser DevTools open (F12 → Console tab)
- ✅ Headphones/speakers connected (for audio output)
- ✅ Microphone available

---

## Test Stages

### Stage 1: UI Initialization ✅
**Action**: Open http://localhost:5175

**Expected UI**:
- Main dashboard loads
- Right panel shows "VOICE ASSISTANT"
- Message: "🎤 Click mic to start"
- Floating button: 🎙️ (bottom-right, inactive state)

**Expected Console**:
```
🌐 OpenAIRealtimeService initialized
🔍 Config.relayServerUrl: undefined
```

**✅ Pass Criteria**: Dashboard loads, voice panel visible, no errors

---

### Stage 2: Connection Initiation ✅
**Action**: Click the 🎙️ floating button

**Expected UI**:
- Button changes to ⌛ (connecting state)
- Voice panel shows "Listening..." placeholder

**Expected Console**:
```javascript
🎯 handleConnectToggle called, voiceProvider: agent, isConnected: false
🚀 Connecting to OpenAI Realtime...
📞 About to call startConversation()...
🎙️ [AGENT VOICE] Step 1: Requesting microphone access...
🎤 [AUDIO PROCESSOR] ========== startRecording() CALLED ==========
🎤 [AUDIO PROCESSOR] Checking navigator.mediaDevices availability: true
🎤 [AUDIO PROCESSOR] Checking getUserMedia availability: true
🎤 [AUDIO PROCESSOR] About to call getUserMedia()...
```

**✅ Pass Criteria**: Console shows microphone request starting

---

### Stage 3: Microphone Permission ⚠️ CRITICAL
**Action**: Browser shows permission dialog → Click "Allow"

**Expected Browser Prompt**:
```
[Website] wants to use your microphone
[ Block ] [ Allow ]
```

**Expected Console (after Allow)**:
```javascript
✅ [AUDIO PROCESSOR] getUserMedia() completed successfully!
✅ [AUDIO PROCESSOR] Stream obtained: [MediaStream object]
✅ [AUDIO PROCESSOR] Microphone access granted
🔊 AudioContext created, state: running
✅ [AUDIO PROCESSOR] Audio processing started
✅ [AGENT VOICE] Microphone access granted and recording started
```

**❌ Failure Modes**:
- **No prompt appears**: Check browser permissions settings
- **"Permission denied"**: User blocked mic, need to reset in browser settings
- **"getUserMedia not supported"**: Browser too old or not HTTPS

**✅ Pass Criteria**: Microphone permission granted, AudioContext running

---

### Stage 4: WebSocket Connection ⚠️ CRITICAL
**Action**: Automatic (happens after mic granted)

**Expected Console**:
```javascript
🌐 [AGENT VOICE] Step 2: Connecting to OpenAI Realtime...
🌐 OpenAIRealtimeService initialized
🌐 Fetching OpenAI relay URL from: http://localhost:8000/elevenlabs/signed-url
📡 Relay URL obtained: wss://api.openai.com/v1/realtime?model=...
📡 Creating RealtimeClient with URL: wss://...
🔌 Connecting to OpenAI Realtime API...
✅ RealtimeClient.connect() completed - waiting for session.created
📡 RealtimeEvent: server session.created {...}
🚀 OpenAI session created - connection established!
⚙️ OpenAI session updated: {model: 'gpt-realtime-2025-08-28', ...}
✅ [AGENT VOICE] Connected to OpenAI Realtime
✅ startConversation() completed
```

**Backend Logs** (`/tmp/backend_official_schema.log`):
```
INFO:services.openai_relay_server:WebSocket connection established for session session_xxx
INFO:services.openai_relay_server:✅ Official schema configured: server_vad with manual response control
```

**Expected UI**:
- Button changes to 🎤 (active/connected state)
- Voice panel: "Connected" or "Listening..."
- VoiceCommandHelper appears (optional floating panel)

**❌ Failure Modes**:
- **"Failed to fetch relay URL"**: Backend not running or CORS issue
- **WebSocket error**: Network issue or invalid API key
- **Session creation timeout**: OpenAI API issue

**✅ Pass Criteria**: Session created, UI shows connected state

---

### Stage 5: Audio Streaming 📤
**Action**: Start speaking (e.g., "What is the price of Tesla?")

**Expected Console (continuous while speaking)**:
```javascript
🎤 [VAD] User started speaking
📤 Sending 4096 audio samples to OpenAI Realtime API
📤 Sending 4096 audio samples to OpenAI Realtime API
📤 Sending 4096 audio samples to OpenAI Realtime API
... (repeats every ~170ms)
```

**Expected UI**:
- Voice panel: "Listening..." message
- Audio level bars animate (if present)

**❌ Failure Modes**:
- **No audio samples sent**: Microphone not capturing
- **"AudioContext suspended"**: Click page to activate audio

**✅ Pass Criteria**: Continuous audio samples sent while speaking

---

### Stage 6: Voice Activity Detection (VAD) 🛑
**Action**: Stop speaking (pause for 500ms)

**Expected Console**:
```javascript
🛑 [VAD] User stopped speaking - manually committing buffer for transcription
```

**What Happens**:
1. OpenAI's server_vad detects silence (> 500ms)
2. Fires `input_audio_buffer.speech_stopped` event
3. Frontend calls `client.commitInputAudio()`
4. Triggers transcription (STT)

**❌ Failure Modes**:
- **VAD doesn't trigger**: Threshold too high or background noise
- **Triggers too early**: Threshold too low (0.6 is balanced)

**✅ Pass Criteria**: VAD event fires after speech ends

---

### Stage 7: Speech-to-Text (STT) 📝
**Action**: Automatic (after VAD commit)

**Expected Console**:
```javascript
📝 [USER STT] New user speech started - ID: msg_abc123
📝 [USER STT] Transcript: "what is the price of Tesla"
📝 [USER STT] Transcript: "what is the price of Tesla?" (delta updates)
✅ [COMPLETED] Item completed - Type: message, Role: user, Status: completed
📝 ✅ [FINAL] User speech completed, emitting final transcript: what is the price of Tesla
```

**Expected UI**:
- User message appears in voice panel
- Message bubble: "👤 what is the price of Tesla?"
- Timestamp shown

**❌ Failure Modes**:
- **No transcript**: Transcription model issue or audio quality too poor
- **Partial transcript**: Audio buffer too short
- **Wrong transcript**: Background noise or unclear speech

**✅ Pass Criteria**: Accurate transcript generated and displayed

---

### Stage 8: Agent Processing 🤖
**Action**: Automatic (after final transcript)

**Expected Console**:
```javascript
🎤 [AGENT VOICE] Transcript received - Final: true, Text: "what is the price of Tesla"
✅ [AGENT VOICE] User final transcript received, sending to agent: what is the price of Tesla
✅ [AGENT VOICE] Sending to agent: what is the price of Tesla

[Agent Orchestrator]
📊 [AGENT] Calling tool: get_stock_price
  → symbol: TSLA
✅ [AGENT] Tool result: {"symbol": "TSLA", "price": 429.86, "change": -13.68, ...}
🤖 [AGENT] Generated response: Tesla (TSLA) is currently trading at $429.86, down $13.68 (-3.08%) today...
```

**Backend Logs**:
```
INFO:services.market_service_factory:Using Alpaca for TSLA quote
INFO:services.market_service:Fetching Alpaca quote for TSLA
INFO:services.market_service:Alpaca quote for TSLA: $429.86, open: $443.545
```

**Expected UI**:
- Assistant thinking indicator (optional)
- Chart may update if chart commands present

**❌ Failure Modes**:
- **"I couldn't generate a response"**: Agent error or timeout
- **Tool call fails**: Backend API issue (Alpaca/Yahoo)
- **Empty response**: max_tokens too low

**✅ Pass Criteria**: Agent calls tools, generates response with market data

---

### Stage 9: Text-to-Speech (TTS) 📢
**Action**: Automatic (after agent response)

**Expected Console**:
```javascript
📤 Sending agent text for TTS: Tesla (TSLA) is currently trading at $429.86...
🛑 Cancelled active response: resp_xyz (if any autonomous response)
✅ TTS request sent (autonomous responses cancelled)
```

**OpenAI Response**:
```javascript
🔊 Audio delta received: 4800 samples
🔊 Audio delta received: 4800 samples
🔊 Audio delta received: 4800 samples
... (audio chunks arrive)
```

**❌ Failure Modes**:
- **No audio deltas**: TTS not triggered or OpenAI error
- **"response.create failed"**: Session configuration issue

**✅ Pass Criteria**: Audio deltas received from OpenAI

---

### Stage 10: Audio Playback 🔊
**Action**: Automatic (audio plays through speakers)

**Expected Console**:
```javascript
🔊 playNextAudio: Starting playback
🔊 playNextAudio: queueLength: N
[Audio plays...]
🔊 Audio playback completed
```

**Expected Experience**:
- Hear agent voice speaking the response
- Voice sounds natural (alloy voice)
- Audio quality clear

**Expected UI**:
- Assistant message appears in voice panel
- Message bubble: "🤖 Tesla (TSLA) is currently trading at..."
- Timestamp shown

**❌ Failure Modes**:
- **No audio playback**: AudioContext suspended or speakers muted
- **"playNextAudio: Skipping - queueLength: 0"**: Audio queue empty
- **Choppy audio**: Buffer underrun or CPU overload

**✅ Pass Criteria**: Clear voice response plays, message displayed

---

## Success Checklist

After completing all 10 stages, verify:

- [ ] Microphone permission granted
- [ ] WebSocket connected ("session.created" received)
- [ ] Audio samples streaming while speaking
- [ ] VAD detects speech end
- [ ] Accurate transcript generated
- [ ] Agent processes query with tools
- [ ] Market data returned (price, change, etc.)
- [ ] TTS audio chunks received
- [ ] Voice response plays clearly
- [ ] UI shows complete conversation thread

**Full Pipeline Success**: All 10 stages pass ✅

---

## Quick Debug Commands

### Check Connection Status
```javascript
// In browser console
console.log("Backend health:", await fetch('http://localhost:8000/health').then(r => r.json()));
console.log("Relay URL:", await fetch('http://localhost:8000/elevenlabs/signed-url').then(r => r.json()));
```

### Check Audio Status
```javascript
// AudioContext state
console.log("AudioContext:", window.audioContext?.state); // Should be "running"

// Microphone devices
navigator.mediaDevices.enumerateDevices().then(devices => {
  console.log("Mics:", devices.filter(d => d.kind === 'audioinput'));
});
```

### Force Trigger Events
```javascript
// Manually click voice button
document.querySelector('[data-testid="voice-fab"]')?.click();

// Check current provider
console.log("Voice provider:", document.querySelector('.voice-panel-right')?.textContent);
```

---

## Common Failure Patterns

### Pattern 1: "Loading analysis..." Stuck
**Symptom**: UI frozen on loading state
**Root Cause**: Backend connection failure
**Fix**: Check backend health endpoint, restart backend

### Pattern 2: Mic Granted But No Audio Sent
**Symptom**: Permission granted, but no "📤 Sending audio samples"
**Root Cause**: AudioContext not created or suspended
**Fix**: Click page to activate audio context

### Pattern 3: Transcript Generated But No Agent Response
**Symptom**: User message appears, but no assistant reply
**Root Cause**: Agent orchestrator connection failure
**Fix**: Check `/ask` endpoint in Network tab

### Pattern 4: Agent Responds But No Voice
**Symptom**: Text response appears, but no audio playback
**Root Cause**: TTS not triggered or audio queue issue
**Fix**: Check console for "📤 Sending agent text for TTS"

---

## Performance Benchmarks

**Expected Timings** (from mic to voice response):

1. Microphone permission: < 1s (user action)
2. WebSocket connection: 500-1000ms
3. Audio streaming: Real-time (continuous)
4. VAD detection: 500ms (silence threshold)
5. STT transcription: 500-1500ms
6. Agent processing: 1-3s (includes tool calls)
7. TTS generation: 500-1500ms
8. Audio playback: Real-time (streaming)

**Total latency**: 3-7 seconds (speak → hear response)

---

## Advanced Diagnostics

### Enable Verbose Logging
Open `useAgentVoiceConversation.ts` and `OpenAIRealtimeService.ts`
All console.log statements already present - no changes needed

### Monitor Network Traffic
1. Open DevTools → Network tab
2. Filter: "WS" (WebSocket) + "Fetch/XHR"
3. Look for:
   - `/elevenlabs/signed-url` - Should return 200 OK with wss:// URL
   - WebSocket connection to `api.openai.com` - Should show "101 Switching Protocols"
   - `/ask` - Should POST user query, return 200 OK with agent response

### Backend Logs
```bash
# Watch backend logs in real-time
tail -f /tmp/backend_official_schema.log

# Look for:
# - "✅ Official schema configured"
# - "WebSocket connection established"
# - Session update events
# - Tool execution logs
```

### Test Individual Components

**Test Microphone Only**:
```javascript
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => console.log("✅ Mic works:", stream))
  .catch(err => console.error("❌ Mic failed:", err));
```

**Test Backend Health**:
```bash
curl -s http://localhost:8000/health | jq '.openai_relay_ready'
# Should output: true
```

**Test Relay URL**:
```bash
curl -s http://localhost:8000/elevenlabs/signed-url | jq '.url'
# Should output WebSocket URL starting with wss://
```

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Document any configuration steps needed
2. Create user guide for voice features
3. Consider adding error recovery UI
4. Deploy to production

### If Tests Fail ❌
1. Identify failure stage (1-10 above)
2. Capture console output + error messages
3. Check corresponding code file for that stage
4. Apply targeted fix
5. Re-test from failed stage

---

**Testing Status**: Ready for manual browser verification
**Expected Time**: 5-10 minutes per test cycle
**Tools Needed**: Browser DevTools, speakers, microphone
