# Quick Voice Test Checklist

## 🚀 Start Testing (5 Minutes)

### Environment
- ✅ Backend: http://localhost:8000 (RUNNING)
- ✅ Frontend: http://localhost:5175 (RUNNING)
- ⚠️ **IMPORTANT**: Hard refresh browser (Ctrl+Shift+R) to clear cached JS

---

## ✅ Test Sequence

### 1️⃣ Microphone Permission (30 seconds)
```
1. Open http://localhost:5175
2. Click microphone button
3. ✓ See permission prompt
4. Click "Allow"
5. ✓ See "recording" indicator
```

### 2️⃣ Silence Test - CRITICAL (15 seconds)
```
1. Wait 5 seconds after connecting
2. ✓ AI does NOT speak
3. ✓ NO auto-greeting
4. ✓ Console: NO "response.audio_transcript.delta"
```
**If AI speaks = FAIL - turn_detection not set correctly**

### 3️⃣ User Speech Test (30 seconds)
```
1. Say: "What is the price of Tesla?"
2. ✓ Console shows: "📝 [USER STT] Transcript: what is the price of Tesla"
3. ✓ Console shows: "✅ [FINAL] User speech completed"
4. ✓ Console shows: "✅ [AGENT VOICE] Sending to agent"
```

### 4️⃣ Agent Response (15 seconds)
```
1. Wait for processing
2. ✓ Console shows: "📊 [AGENT] Calling tool: get_stock_price"
3. ✓ Console shows: "🤖 [AGENT] Generated response" with price
4. ✓ Response includes current Tesla price
```

### 5️⃣ Voice Output (15 seconds)
```
1. Listen for audio
2. ✓ Hear AI voice speaking
3. ✓ Console shows: "🔊 Audio delta received"
4. ✓ Speech is clear and natural
```

### 6️⃣ Complex Query (60 seconds)
```
1. Type: "Build a trading plan for this week"
2. ✓ Full response (not truncated)
3. ✓ Includes: analysis, entry points, stop loss, targets
4. ✓ Response > 500 characters
```

---

## 🔍 What to Look For

### ✅ GOOD Signs
- Microphone permission prompt appears
- AI is silent until you speak
- Your speech transcribed accurately
- Agent calls market data tools
- Voice response plays clearly
- No console errors

### ❌ BAD Signs
- No permission prompt
- AI speaks immediately ("Hello! How can I help...")
- Console shows `response.audio_transcript.delta`
- No audio playback
- Responses truncated mid-sentence
- Console errors about cancellation

---

## 🐛 Quick Debugging

### No Microphone Prompt?
```bash
# Check if useAgentVoiceConversation has audio processor
grep -n "useOpenAIAudioProcessor" frontend/src/hooks/useAgentVoiceConversation.ts
```

### AI Speaking Autonomously?
```bash
# Check turn_detection setting
grep -A5 "turn_detection" backend/services/openai_relay_server.py
# Should show: "type": "none"
```

### No Voice Output?
```javascript
// In browser console
console.log("AudioContext:", window.audioContext?.state);
// Should be: "running"
```

### Response Truncated?
```bash
# Check max_tokens
grep "max_tokens" backend/services/agent_orchestrator.py
# Should be: 1500 (not 800)
```

---

## 📊 Expected Console Flow

```
[Connection]
✅ GA-compliant session configured: PASSIVE voice I/O

[User Speaks]
📝 [USER STT] New user speech started
📝 [USER STT] Transcript: "what is the price of Tesla"
✅ [FINAL] User speech completed

[Agent Processing]
✅ [AGENT VOICE] Sending to agent: what is the price of Tesla
📊 [AGENT] Calling tool: get_stock_price
✅ [AGENT] Tool result: {"price": 234.56, ...}
🤖 [AGENT] Generated response: Tesla is trading at $234.56

[Voice Output]
📤 Sending text for TTS: Tesla is trading at $234.56
🔊 Audio delta received: 4800 samples
🔊 playNextAudio: Starting playback
```

---

## 🎯 Pass Criteria

**Minimum for "Working":**
- [ ] Microphone permission works
- [ ] AI silent after connection (passive mode)
- [ ] User speech recognized
- [ ] Agent responds with data
- [ ] Voice output plays

**100% Success:**
- All above ✓
- [ ] Complex queries work
- [ ] No console errors
- [ ] Turn-taking smooth
- [ ] Voice quality excellent

---

## 📝 Report Template

```
Voice Test Results - [Date]

Environment:
- Backend: ✓/✗ Running
- Frontend: ✓/✗ Running
- Browser: Chrome/Firefox/Safari

Test Results:
1. Microphone: ✓/✗
2. Passive Mode: ✓/✗
3. User STT: ✓/✗
4. Agent Response: ✓/✗
5. Voice TTS: ✓/✗
6. Complex Query: ✓/✗

Issues Found:
- [List any problems]

Console Errors:
- [Copy error messages]

Notes:
- [Any observations]
```

---

**Ready to Test?** → Open http://localhost:5175 and start with Test 1
