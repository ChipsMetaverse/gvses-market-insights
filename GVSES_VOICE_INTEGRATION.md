# G'sves Voice Pipeline Integration

## Configuration

Add to `backend/.env`:
```bash
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg
```

## Integration Code

### Option A: Use Responses API Directly (Recommended)

```python
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def process_voice_transcript(transcript: str, session_id: str):
    """Process voice transcript with G'sves agent."""

    # Call Responses API with G'sves configuration
    response = client.responses.create(
        model="gpt-4o",
        instructions=assistant_instructions,
        input=transcript,
        tools=[
            {"type": "web_search"},  # Real-time market data
            {"type": "function", "name": "get_stock_quote", ...},  # Your MCP tools
        ],
        store=True  # Enable multi-turn
    )

    return response.output_text

# In your voice pipeline:
# transcript = await openai_relay_server.receive_transcript()
# response_text = process_voice_transcript(transcript, session_id)
# await openai_relay_server.send_tts(response_text, session_id)
```

### Option B: Use Assistant with Threads

```python
def process_with_assistant(transcript: str, thread_id: str = None):
    """Process using Assistant API with persistent threads."""

    # Create or use existing thread
    if not thread_id:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Add user message
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=transcript
    )

    # Run assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=os.getenv('GVSES_ASSISTANT_ID')
    )

    # Wait for completion and get response
    # (Add polling logic here)

    return response_text, thread_id
```

## Testing

```bash
python3 test_gvses_voice_integration.py
```
