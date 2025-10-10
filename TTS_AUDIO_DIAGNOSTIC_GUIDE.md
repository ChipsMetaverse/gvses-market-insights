# TTS Audio Diagnostic Guide

## What Logs Tell You Audio is Received and Played

This document explains exactly what logs to look for to determine if TTS audio is being received from OpenAI and played back to the user.

---

## Complete Audio Pipeline Flow

### 1. Agent Response Received
```
[AGENT ORCHESTRATOR SERVICE] 📦 Parsed JSON response: ...
```
**Means:** Agent (backend) has sent a text response

---

### 2. TTS Trigger Check
```
🚨 [TTS CHECK] source: voice hasRef: true isConnected: true
[AGENT VOICE] 🔊 Sending to TTS: [first 100 chars of response]
```
**Means:** The frontend is attempting to send the agent's text response to OpenAI for TTS conversion

**If you see instead:**
```
🚨 [TTS CHECK] TTS SKIPPED - Condition not met
```
**Problem:** One of these conditions failed:
- `source !== 'voice'` (wasn't a voice interaction)
- `!openAIServiceRef.current` (OpenAI service not initialized)
- `!isConnected` (not connected to OpenAI)

---

### 3. TTS Request Sent to OpenAI
```
🔊 [TTS] Creating assistant message for TTS
✅ [TTS] Waiting for response.audio.delta events
```
**Means:** Successfully sent two WebSocket messages to OpenAI:
1. `conversation.item.create` - Added assistant's text to conversation
2. `response.create` with `output_modalities: ['audio']` - Requested audio generation

---

### 4. Audio Data Received from OpenAI ✅ **CRITICAL**
```
🔊 [TTS AUDIO] Received audio chunk: 1234 bytes
🔊 [TTS AUDIO] Converted to Int16Array: 5678 samples
🔊 [TTS AUDIO] Calling onAudioResponse callback
🔊 [TTS AUDIO] onAudioResponse callback completed
```
**Means:** OpenAI is sending audio data back! Each chunk is:
- Base64-encoded PCM16 audio
- Converted to Int16Array (16-bit PCM samples)
- Passed to the `onAudioResponse` callback

**Location:** `frontend/src/services/OpenAIRealtimeService.ts:125-135`

**If missing:** OpenAI is NOT generating/sending audio. Possible reasons:
- Backend OpenAI relay not configured for audio output
- Session config missing `output_modalities: ['audio']`
- OpenAI API error (check for error logs)

---

### 5. Audio Queued for Playback
```javascript
// Code in useAgentVoiceConversation.ts:326-330
onAudioResponse: (audioData: Int16Array) => {
  audioQueueRef.current.push(audioData);
  playNextAudio();
}
```
**No explicit log here**, but this happens when `onAudioResponse` callback is fired.

**Means:** Audio chunk added to playback queue and `playNextAudio()` called

---

### 6. Audio Playback via Web Audio API
```javascript
// Code in useAgentVoiceConversation.ts:135-176
const playNextAudio = async () => {
  // Creates AudioContext
  // Converts Int16Array → Float32Array
  // Creates AudioBuffer at 24kHz
  // Plays via source.start()
}
```
**Currently NO explicit playback logs!**

**To detect playback, you need to:**
- Check if `🔊 [TTS AUDIO] Received audio chunk` logs appear
- Actually hear audio through your speakers/headphones
- Check browser's audio indicator (speaker icon in tab)

---

## Quick Diagnostic Checklist

Use this checklist to debug TTS audio issues:

### ✅ Step 1: Is TTS being triggered?
**Look for:**
```
🚨 [TTS CHECK] source: voice hasRef: true isConnected: true
[AGENT VOICE] 🔊 Sending to TTS: ...
```
**If missing:** Voice interaction not detected or connection lost

---

### ✅ Step 2: Is TTS request sent?
**Look for:**
```
🔊 [TTS] Creating assistant message for TTS
✅ [TTS] Waiting for response.audio.delta events
```
**If missing:** OpenAI service not properly initialized or connection failed

---

### ✅ Step 3: Is audio data arriving? (MOST IMPORTANT)
**Look for:**
```
🔊 [TTS AUDIO] Received audio chunk: XXX bytes
```
**If missing:** OpenAI is not sending audio back. Check:
- Backend relay configuration
- OpenAI API errors
- Session audio output settings

---

### ✅ Step 4: Can you hear audio?
**Check:**
- Computer volume not muted
- Browser tab not muted (check speaker icon in tab)
- Browser audio permissions granted
- Headphones/speakers connected

---

## Adding More Playback Logs

To add explicit playback logs, modify `useAgentVoiceConversation.ts:135-176`:

```typescript
const playNextAudio = useCallback(async () => {
  console.log('🎧 [PLAYBACK] playNextAudio called, queue length:', audioQueueRef.current.length);

  if (isPlayingRef.current || audioQueueRef.current.length === 0) {
    console.log('🎧 [PLAYBACK] Skipped - isPlaying:', isPlayingRef.current, 'queueEmpty:', audioQueueRef.current.length === 0);
    return;
  }

  isPlayingRef.current = true;
  const audioData = audioQueueRef.current.shift();

  if (audioData) {
    console.log('🎧 [PLAYBACK] Playing audio chunk:', audioData.length, 'samples');
    try {
      const audioContext = await initAudioContext();
      console.log('🎧 [PLAYBACK] AudioContext state:', audioContext.state);

      const floatArray = new Float32Array(audioData.length);
      for (let i = 0; i < audioData.length; i++) {
        floatArray[i] = audioData[i] / 32768.0;
      }

      const audioBuffer = audioContext.createBuffer(1, floatArray.length, 24000);
      audioBuffer.copyToChannel(floatArray, 0);

      const source = audioContext.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContext.destination);

      source.onended = () => {
        console.log('🎧 [PLAYBACK] Audio chunk finished playing');
        isPlayingRef.current = false;
        playNextAudio();
      };

      source.start();
      console.log('🎧 [PLAYBACK] Audio playback started, duration:', audioBuffer.duration, 'seconds');
    } catch (err) {
      console.error('🎧 [PLAYBACK] Error playing audio:', err);
      isPlayingRef.current = false;
      playNextAudio();
    }
  }
}, [initAudioContext]);
```

---

## Summary: The Key Log

**The MOST IMPORTANT log that tells you audio is being received:**

```
🔊 [TTS AUDIO] Received audio chunk: XXXX bytes
```

**If you see this log repeatedly:**
- ✅ OpenAI is generating and sending TTS audio
- ✅ Audio data is arriving at the frontend
- ✅ Audio should be queued for playback

**If you DON'T see this log:**
- ❌ OpenAI is NOT sending audio
- ❌ Check backend configuration
- ❌ Check OpenAI session settings
- ❌ Check for OpenAI API errors

**If you see the log but hear NO audio:**
- Audio is arriving but playback is failing
- Check browser audio permissions
- Check computer volume/mute
- Check AudioContext initialization
- Add playback logging (see section above)
