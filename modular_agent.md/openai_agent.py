"""
openai_agent.py
~~~~~~~~~~~~~~~~

An implementation of a simple conversation loop using OpenAI’s ChatCompletion
API with function calling.  The agent is instructed via a system prompt to
behave as an experienced market analyst.  It decides which tool functions to
invoke (defined in the `tools` module) in order to answer user questions
accurately.  After all necessary function calls are executed, the agent
produces a final answer that incorporates the data it retrieved.

This module is designed for educational purposes.  It assumes that the
developer has installed the `openai` Python package and has set
`OPENAI_API_KEY` in their environment.  In this offline environment the
network call to OpenAI’s API will not succeed, but the code structure
illustrates how to implement such an agent.

Usage example:

```bash
python -m modular_agent.openai_agent "Give me a snapshot of TSLA"
```
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional

import openai

from . import tools

# Read API key from environment (expected for real use).  In this offline
# environment the key may be None, but the code still defines it so that
# developers can see where to configure it.  If running against the actual
# OpenAI service, set OPENAI_API_KEY in your shell.
openai.api_key = os.getenv("OPENAI_API_KEY")


SYSTEM_PROMPT = """
You are an expert market analyst with decades of experience.  You have access
to real‑time market tools that can fetch current stock prices, news, and
market overviews.  Always use these tools to gather up‑to‑date data instead
of guessing.  Present your answers in a clear and structured way, starting
with key numbers and using bullet points for lists.  When referring to data
include the time at which it was retrieved.  If you are unable to get
information from the tools, politely inform the user rather than making
anything up.
"""


async def call_openai_agent(user_query: str, model: str = "gpt-4") -> str:
    """Run a single turn of the OpenAI chat agent with function calling.

    :param user_query: The natural language question from the user.
    :param model: The OpenAI model name (e.g. "gpt-4", "gpt-3.5-turbo").
    :return: The final answer produced by the model after executing tools.
    """
    # Start with the system prompt and the user message.
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT.strip()},
        {"role": "user", "content": user_query},
    ]

    # Keep calling the model until it stops requesting functions.
    while True:
        # Make the API call specifying our available functions.
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=messages,
            functions=tools.FUNCTION_SCHEMAS,
            function_call="auto",
        )
        # Extract the assistant's message.
        assistant_message = response["choices"][0]["message"]
        # If the assistant wants to call a function, call it and append the
        # result to the conversation history.
        if assistant_message.get("function_call"):
            func_name = assistant_message["function_call"]["name"]
            arguments_str = assistant_message["function_call"]["arguments"]
            # Parse arguments JSON safely.
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                result = {"error": f"Failed to parse arguments: {arguments_str}"}
            else:
                # Dispatch to the appropriate function.
                func = getattr(tools, func_name, None)
                if func is None:
                    result = {"error": f"Function {func_name} not found"}
                else:
                    # Await the asynchronous tool function.
                    result = await func(**arguments)
            # Append the assistant message and function response to the context.
            messages.append(assistant_message)
            messages.append(
                {
                    "role": "function",
                    "name": func_name,
                    "content": json.dumps(result),
                }
            )
            # Continue the loop – the model will use the function result in
            # forming its next message.
            continue
        # If no function call, return the assistant's content as the final answer.
        return assistant_message.get("content", "")


async def main() -> None:
    """Entry point when the module is run directly."""
    if len(sys.argv) < 2:
        print("Usage: python -m modular_agent.openai_agent '<user question>'")
        sys.exit(1)
    query = sys.argv[1]
    answer = await call_openai_agent(query)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())