"""
combined_agent.py
~~~~~~~~~~~~~~~~~~

This script demonstrates how to orchestrate the OpenAI and ElevenLabs modules
together to build a fully conversational market assistant.  The intent is to
show a modular design: the reasoning logic lives in the OpenAI agent
(`openai_agent.py`), while the speech I/O could be handled by ElevenLabs
(`elevenlabs_agent.py`) or another TTS/ASR provider.  In this offline
example we simply read text from the user, generate a response via the
OpenAI agent, and print it to the console.  When integrated with a speech
engine you would send the text to TTS and play the resulting audio.

Run this module to enter a simple interactive loop.  Type your question and
press Enter.  To quit, type "exit" or press Ctrl+D.

```bash
python -m modular_agent.combined_agent
```
"""

from __future__ import annotations

import asyncio
import sys

from .openai_agent import call_openai_agent


async def handle_user_input() -> None:
    """Interactive loop: prompt the user, call the agent, print the response."""
    print("Welcome to the Market Assistant!  Type your question or 'exit' to quit.")
    while True:
        try:
            query = input("You: ").strip()
        except EOFError:
            # User pressed Ctrl+D
            print()
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break
        # Call the OpenAI agent to get an answer.  In a real implementation
        # you might choose different models based on complexity or user tier.
        try:
            answer = await call_openai_agent(query)
        except Exception as exc:
            print(f"Error calling agent: {exc}")
            continue
        # Print the answer.  In a voice application you would convert this
        # string to speech and play it through the speakers.
        print(f"Assistant: {answer}\n")
    print("Goodbye!")


async def main() -> None:
    await handle_user_input()


if __name__ == "__main__":
    asyncio.run(main())