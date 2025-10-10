# OpenAI Realtime API Schema Compatibility

## Critical Finding: Correct Schema Structure (2025)

### Issue Discovered (Oct 5, 2025)
**Error**: `Unknown parameter: 'session.audio'`
**Root Cause**: The OpenAI Realtime API uses **flat structure**, NOT nested `audio` object

### Correct Schema (Production 2025)

The official OpenAI Realtime API schema uses a **flat structure** with:
- `modalities`, `voice`, `input_audio_format`, `output_audio_format`
- This is the **current production API** structure (not Beta)
- Model `gpt-realtime-2025-08-28` and `gpt-realtime` both use this schema

**Source**: OpenAI Realtime API Documentation (2025-08-28)

## Current Configuration (Production Schema)

### Session Config Structure (CORRECT - Production 2025)
```json
{
  "type": "session.update",
  "session": {
    "model": "gpt-realtime-2025-08-28",
    "instructions": "...",

    // Production API fields (flat structure)
    "modalities": ["text", "audio"],
    "voice": "alloy",  // Options: alloy, echo, shimmer, cedar, marin
    "input_audio_format": "pcm16",  // Options: pcm16, g711_ulaw, g711_alaw
    "output_audio_format": "pcm16",

    // CRITICAL: turn_detection = "none" for passive mode
    "turn_detection": {
      "type": "none"  // Prevents autonomous responses
    },

    // Enable STT transcription
    "input_audio_transcription": {
      "model": "whisper-1"
    },

    // No tools - agent handles all function calls
    "tools": []
  }
}
```

### ❌ INCORRECT Schema (Does NOT exist in OpenAI API)

```json
{
  "type": "session.update",
  "session": {
    // This nested structure DOES NOT WORK
    "audio": {
      "input": {
        "format": "pcm16"  // ❌ Unknown parameter: 'session.audio'
      },
      "output": {
        "voice": "alloy",
        "format": "pcm16"
      }
    }
  }
}
```

## Key Learnings

1. **Flat Schema is Current**: OpenAI Realtime API uses flat structure, NOT nested `audio` object
2. **No "GA vs Beta"**: The schema structure is consistent across all Realtime API models
3. **Turn Detection Options**:
   - `none` - Passive mode (no autonomous responses) ✅ **OUR CONFIG**
   - `server_vad` - Automatic chunking based on silence
   - `semantic_vad` - Chunking based on semantic completion
4. **Passive Mode is Key**: `turn_detection: {type: "none"}` + passive instructions prevents autonomous responses
5. **Voice Options (2025)**: alloy, echo, shimmer, cedar, marin (NOT ash, ballad, coral, fable, onyx, nova)

## Turn Detection Modes Explained

### `none` (Current - Passive Voice I/O)
- **Behavior**: No automatic speech detection
- **Response Trigger**: Only when explicitly instructed to speak
- **Use Case**: Voice I/O interface for external agent (our architecture)
- **Pros**: Complete control, no autonomous responses
- **Cons**: Requires manual turn management

### `server_vad` (Voice Activity Detection)
- **Behavior**: Auto-detects silence to chunk audio
- **Response Trigger**: After silence threshold (default 200ms)
- **Use Case**: Autonomous conversational AI
- **Pros**: Natural conversation flow
- **Cons**: May respond autonomously, harder to control

### `semantic_vad` (Semantic Completion Detection)
- **Behavior**: Uses AI to detect utterance completion
- **Response Trigger**: When model thinks user finished speaking
- **Use Case**: Smart conversational interruption
- **Pros**: More natural than silence-based
- **Cons**: May interrupt user, less predictable

## References

- **Realtime API Guide**: https://platform.openai.com/docs/guides/realtime
- **API Reference**: https://platform.openai.com/docs/api-reference/realtime
- **Turn Detection**: https://platform.openai.com/docs/guides/realtime#turn-detection
- **Announcement**: https://openai.com/index/introducing-gpt-realtime/

---

**Current Status**: ✅ Production schema active, backend restarted, ready for testing
**Schema Type**: Production (Flat Structure)
**Model**: `gpt-realtime-2025-08-28`
**Turn Detection**: `none` (passive mode)
**Configuration File**: `backend/services/openai_relay_server.py:173-229`
