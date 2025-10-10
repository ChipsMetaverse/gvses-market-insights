# Voice Pipeline Audit Report
**Date**: October 5, 2025
**Status**: COMPREHENSIVE AUDIT IN PROGRESS

---

## 1. Backend Configuration Audit

### OpenAI Realtime Relay Server
**File**: `backend/services/openai_relay_server.py`

#### A. Connection Details
```python
Line 39: self.openai_url = "wss://api.openai.com/v1/realtime"
Line 40: self.model = "gpt-realtime-2025-08-28"  # Instance variable (not used in session)
```

**Status**: ⚠️ MISMATCH
- Instance variable: `gpt-realtime-2025-08-28`
- Session config uses: `gpt-4o-realtime-preview-2024-12-17` (hardcoded)
- **Impact**: Session config overrides instance variable, so actual model is preview version
- **Action**: Verify which model name is correct with OpenAI API

#### B. Session Configuration (Lines 190-211)
```python
session_config = {
    "type": "session.update",
    "session": {
        "type": "realtime",  # ✅ Explicit session type
        "model": "gpt-4o-realtime-preview-2024-12-17",  # ⚠️ May be incorrect
        "instructions": instructions,  # ✅ Passive mode instructions

        "audio": {
            "input": {"format": "pcm16"},  # ✅ Correct format
            "output": {"voice": "alloy", "format": "pcm16"}  # ✅ Correct
        },

        "turn_detection": {"type": "none"},  # ✅ CRITICAL: Passive mode
        "tools": []  # ✅ No tools (agent handles)
    }
}
```

**Status**: ✅ MOSTLY CORRECT
- `turn_detection: {type: "none"}` ✅ Prevents autonomous responses
- Audio format: `pcm16` ✅ Standard format
- No tools ✅ Agent orchestrator handles all intelligence
- **Issue**: Model name may need verification

#### C. Instructions (Lines 177-188)
```python
instructions = """You are ONLY a transcription service.

Your SOLE function: Convert speech to text (STT).

You MUST NEVER:
- Generate any responses
- Answer questions
- Provide information
- Speak autonomously
- React to user input

If you receive text to speak (TTS), speak it naturally. Otherwise, remain completely silent."""
```

**Status**: ✅ EXCELLENT
- Clear passive-only mandate
- Prevents autonomous responses
- Allows TTS when explicitly requested

---

## 2. Frontend Event Handlers Audit

### OpenAI Realtime Service
**File**: `frontend/src/services/OpenAIRealtimeService.ts`

#### A. GA Event Handlers (Lines 96-120)

**NEW: GA Transcript Delta Handler**
```typescript
Line 97-103: this.client.on('response.output_audio_transcript.delta', (event: any) => {
  console.log('📝 [GA TRANSCRIPT DELTA]', event.delta);
  if (event.delta) {
    this.config.onTranscript?.(event.delta, false, event.item_id);
  }
});
```
**Status**: ✅ ADDED
- Handles incremental transcript updates
- Calls `onTranscript` callback
- **Question**: Is this the correct event for user speech STT?

**NEW: Conversation Item Added**
```typescript
Line 106-108: this.client.on('conversation.item.added', (event: any) => {
  console.log('📋 [GA ITEM ADDED]', event.item);
});
```
**Status**: ✅ ADDED (logging only)

**NEW: Conversation Item Done**
```typescript
Line 110-120: this.client.on('conversation.item.done', (event: any) => {
  console.log('✅ [GA ITEM DONE]', event.item);
  if (event.item.type === 'message' && event.item.role === 'user') {
    const transcript = event.item.content?.[0]?.transcript || '';
    if (transcript) {
      console.log('🎯 [USER SPEECH COMPLETE] Final transcript:', transcript);
      this.config.onTranscript?.(transcript, true, event.item.id);
    }
  }
});
```
**Status**: ✅ ADDED
- Handles complete user messages
- Calls `onTranscript` with final=true
- **Critical**: This sends transcript to agent

#### B. Legacy Event Handlers (Lines 123-131)

**Legacy VAD Events**
```typescript
Line 123-125: this.client.on('input_audio_buffer.speech_started', () => {
  console.log('🎤 [VAD] User started speaking');
});

Line 127-131: this.client.on('input_audio_buffer.speech_stopped', () => {
  console.log('🛑 [VAD] User stopped speaking');
  // Note: May not fire in passive mode with turn_detection: none
});
```
**Status**: ⚠️ LEGACY
- May not fire with `turn_detection: none`
- No `commitInputAudio()` call
- **Question**: Are these needed or should be removed?

#### C. Conversation Updated Handler (Lines 133-164)

**Existing handler** - Still present but may be superseded by GA events
```typescript
Line 113-146: this.client.on('conversation.updated', ({ item, delta }) => {
  switch (item.type) {
    case 'message':
      if (delta?.transcript) {
        if (item.role !== 'user') {
          console.warn('🚫 [VOICE I/O] Ignoring assistant auto-response');
          return; // Filter assistant messages
        }
        // Process user transcripts
        this.config.onTranscript?.(message.content, false, item.id);
      }
      break;
  }
});
```
**Status**: ⚠️ POTENTIAL DUPLICATION
- May fire alongside GA events
- Could cause double-processing of transcripts
- **Action**: Test to see which events actually fire

---

## 3. Agent Integration Flow

### useAgentVoiceConversation Hook
**File**: `frontend/src/hooks/useAgentVoiceConversation.ts`

#### A. Transcript Handler (Lines 134-175)
```typescript
const handleTranscript = useCallback((text: string, isFinal: boolean, messageId?: string) => {
  console.log(`📝 Transcript (final=${isFinal}):`, text);

  if (!isFinal) {
    // Partial transcript - update UI only
    return;
  }

  // Final transcript - send to agent
  sendToAgent(text);
}, [sendToAgent]);
```

**Status**: ✅ CORRECT
- Only sends final transcripts to agent
- Partial updates for UI only
- Calls `sendToAgent()` for processing

#### B. Agent Call Flow (Lines 231-286)
```typescript
const sendToAgent = useCallback(async (userMessage: string) => {
  // 1. Add user message to conversation
  // 2. Call /ask endpoint with conversation_history
  // 3. Process agent response
  // 4. Extract chart commands
  // 5. Send TTS request if audio enabled
}, [/* deps */]);
```

**Status**: ✅ CORRECT
- Full agent orchestration flow
- Handles tool calls
- Returns audio URL for playback

---

## 4. Complete Voice Pipeline Flow

### Expected Flow (Passive Mode)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER SPEAKS                                                  │
│    "What is the price of Tesla?"                                │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. MICROPHONE CAPTURE                                           │
│    useOpenAIAudioProcessor.ts                                   │
│    - Captures PCM16 audio @ 24kHz                               │
│    - Sends to OpenAI via WebSocket                              │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. WEBSOCKET RELAY                                              │
│    backend/services/openai_relay_server.py                      │
│    - Relays audio to wss://api.openai.com/v1/realtime          │
│    - Session configured with turn_detection: none               │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. OPENAI STT (Passive Mode)                                    │
│    - Transcribes audio to text                                  │
│    - NO autonomous response (turn_detection: none)              │
│    - Emits GA events:                                           │
│      * response.output_audio_transcript.delta (incremental)     │
│      * conversation.item.done (complete)                        │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. FRONTEND EVENT HANDLING                                      │
│    OpenAIRealtimeService.ts                                     │
│    - Receives conversation.item.done event                      │
│    - Extracts final transcript                                  │
│    - Calls onTranscript(text, true, id)                         │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. AGENT ORCHESTRATOR                                           │
│    useAgentVoiceConversation.ts → /ask endpoint                 │
│    - Receives: "What is the price of Tesla?"                    │
│    - Calls get_stock_price("TSLA")                              │
│    - Returns: "Tesla is trading at $429.86"                     │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┘
│ 7. TTS REQUEST                                                  │
│    POST /openai/realtime/tts                                    │
│    - Sends agent response text                                  │
│    - Requests audio synthesis                                   │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. OPENAI TTS                                                   │
│    - Synthesizes speech from text                               │
│    - Returns audio via response.audio_transcript.delta          │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. AUDIO PLAYBACK                                               │
│    useOpenAIAudioProcessor.ts                                   │
│    - Receives audio chunks                                      │
│    - Plays through speakers                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Critical Issues & Questions

### 🔴 CRITICAL ISSUES

1. **Model Name Uncertainty**
   - Session config uses: `gpt-4o-realtime-preview-2024-12-17`
   - Context7research.md shows: `gpt-realtime`
   - **Action**: Verify correct model name with OpenAI docs

2. **Event Handler Duplication**
   - Both GA events AND `conversation.updated` handler present
   - May cause double-processing
   - **Action**: Test which events fire, remove redundant handlers

3. **No Manual Transcription Trigger**
   - With `turn_detection: none`, VAD events don't fire
   - No `commitInputAudio()` call
   - **Question**: How does transcription get triggered?
   - **Hypothesis**: Passive mode auto-transcribes, no manual trigger needed

### ⚠️ QUESTIONS TO VERIFY

1. **Correct STT Event**: Is `response.output_audio_transcript.delta` for STT or TTS?
   - Name suggests it's for OUTPUT (TTS), not INPUT (STT)
   - May need different event for user speech transcription
   - **Action**: Check OpenAI docs for correct STT event name

2. **Turn Detection Behavior**: With `turn_detection: none`:
   - Does OpenAI still transcribe audio?
   - Do we need manual `createResponse()` call?
   - **Action**: Test behavior empirically

3. **Audio Format**: PCM16 vs audio/pcm
   - Session uses: `{"format": "pcm16"}`
   - Is this correct for WebSocket connection?
   - **Action**: Verify against OpenAI schema

---

## 6. Testing Checklist

### Backend Tests
- [ ] Verify session config is sent correctly
- [ ] Check backend logs for "✅ Passive mode configured" message
- [ ] Monitor WebSocket connection establishment
- [ ] Verify no autonomous responses generated

### Frontend Tests
- [ ] Check which events actually fire (GA vs legacy)
- [ ] Verify transcripts reach `onTranscript` callback
- [ ] Confirm `sendToAgent()` is called with final transcript
- [ ] Verify audio playback works

### Integration Tests
- [ ] End-to-end flow: mic → STT → agent → TTS → speaker
- [ ] Verify no double-processing of transcripts
- [ ] Check console logs for complete pipeline
- [ ] Test with: "What is the price of Tesla?"

---

## 7. Next Steps

1. **Verify Model Name**
   - Check OpenAI Realtime API docs
   - Test with both `gpt-realtime` and `gpt-4o-realtime-preview-2024-12-17`

2. **Test Event Handlers**
   - Add extensive console logging
   - Identify which events fire in passive mode
   - Remove redundant handlers

3. **Manual Testing**
   - Click 🎙️ button
   - Speak test phrase
   - Monitor all console logs
   - Verify complete flow

4. **Fix Issues**
   - Update model name if incorrect
   - Remove duplicate event handlers
   - Add missing manual triggers if needed

---

## 8. Confidence Assessment

**Overall Pipeline Readiness**: 🟡 75%

**Component Scores**:
- Backend Config: 🟢 85% (model name question)
- Frontend Events: 🟡 70% (duplication concerns)
- Agent Integration: 🟢 95% (looks solid)
- Audio Pipeline: 🟡 70% (untested)

**Recommendation**: PROCEED WITH TESTING
- Infrastructure is in place
- Key issues can be debugged via console logs
- Manual testing will reveal actual behavior
