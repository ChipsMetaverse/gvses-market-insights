# Modular Market Analysis Voice Assistant

This repository provides a **proof‑of‑concept** implementation of a voice‑enabled market analysis assistant.  The goal is to illustrate how to structure an application that can be powered by either

1. **ElevenLabs Conversational AI** (for real‑time speech recognition and synthesis) or
2. **OpenAI’s function‑calling models** (for reasoning and data aggregation)

in a modular way.  The implementation here is deliberately simple and runs offline — there are no external API calls so you can explore the architecture without needing API keys.  To build a fully functional product you will need to substitute the stub functions with real API integrations (stock data providers, news feeds, etc.) and supply your own ElevenLabs/OpenAI keys.

## Overview

The assistant is split into three main components:

* **`tools.py`** – Defines a handful of data fetching functions (e.g. getting a stock’s price or a list of headlines) and exposes them via metadata.  In this offline version the functions return synthetic data.  When deploying for real, replace the stubs with calls to your backend (e.g. the endpoints on your Fly.io server).

* **`openai_agent.py`** – Implements an agent loop using OpenAI’s chat completion API with function calling.  It reads a system prompt, accepts a user question, decides which tool(s) to call, executes the functions and produces a final answer.  The agent will output text that you can feed to a text‑to‑speech engine or display in a UI.

* **`elevenlabs_agent.py`** – Shows how to connect to ElevenLabs’ Conversational AI service via WebSocket for real‑time audio streaming.  It contains a simple prompt and will echo back user input, using synthetic responses to stand in for the assistant’s answers.  In a real implementation you would pipe the text output from `openai_agent.py` into the ElevenLabs WebSocket to produce speech.

The **`combined_agent.py`** script ties everything together.  You can specify whether to run purely with OpenAI (text‑based), purely with ElevenLabs (voice‑only), or a hybrid mode (OpenAI decides on tools and ElevenLabs speaks the answer).  The code is designed to be modular so you can swap out the underlying provider without changing the surrounding logic.

## Prerequisites

This project requires Python 3.10+.  Install dependencies via pip:

```bash
pip install asyncio websockets openai tiktoken
```

> **Note:** The above libraries are imported in the code, but this offline version will not actually call any external APIs.  If you intend to run against ElevenLabs or OpenAI, install their official SDKs and set the required environment variables (`ELEVENLABS_API_KEY`, `OPENAI_API_KEY`).

## Running the Examples

Each module can be run directly from the command line.  All scripts live in the `modular_agent` package, so ensure you are in the repository root before running these examples.

### 1. Test the tools module

```bash
python -m modular_agent.tools
```

This prints the synthetic stock price and news headlines for the default symbol (`TSLA`).  You can pass a different symbol as the first argument (e.g. `python -m modular_agent.tools AAPL`).

### 2. Chat with the OpenAI agent

```bash
python -m modular_agent.openai_agent "Give me a snapshot of TSLA"
```

The agent reads a built‑in system prompt that defines the persona (a seasoned market analyst) and will then decide which of the synthetic tools to call.  It prints the final answer to stdout.  Replace the system prompt with your own content as needed.

### 3. Simulate ElevenLabs voice interaction

```bash
python -m modular_agent.elevenlabs_agent
```

This opens a WebSocket connection to a dummy server and sends a few fake audio messages.  Since we cannot connect to ElevenLabs in this offline environment, the script merely demonstrates the control flow.  For real use, set `ELEVENLABS_AGENT_ID` and `ELEVENLABS_API_KEY` in your environment, and implement `stream_conversation` accordingly.

### 4. Hybrid mode

```bash
python -m modular_agent.combined_agent
```

In hybrid mode the program accepts text from the user, passes it through the OpenAI agent for reasoning, and then feeds the result into a synthetic speech generator (just printing to console here).  To integrate with a live voice engine, replace the call to `speak_text` with code that sends the text to your TTS provider (e.g. ElevenLabs or a local synthesizer) and plays the audio.

## Next Steps

1. **Replace synthetic tools with real APIs.**  In `tools.py`, implement data fetching using your own backend endpoints (for example, the Fly.io services described in the project quick reference).  Wrap the HTTP calls in asynchronous functions so they can be awaited by the OpenAI agent.

2. **Configure system prompts.**  Edit the prompt strings in `openai_agent.py` and `elevenlabs_agent.py` to reflect your chosen persona, guidelines, and output structure.  Refer to the detailed prompt examples in the overall project documentation for guidance.

3. **Integrate audio streams.**  In `elevenlabs_agent.py` you will need to open an authenticated WebSocket connection to ElevenLabs and handle streaming audio in and out.  See the official ElevenLabs documentation for specifics on how to send microphone audio and receive synthesized speech.  In `combined_agent.py`, replace `print` with calls to your audio subsystem.

4. **Expand tool repertoire.**  To match the complete feature set of the market assistant, add additional tool functions such as `get_market_overview`, `get_stock_history`, `get_options_chain`, etc.  Provide JSON schemas describing each function’s parameters and return types so that the OpenAI model knows how to call them.

## Disclaimer

This code is intended for educational and prototyping purposes.  It is not production‑ready and does not include error handling, logging, or security features.  To deploy a real application you will need to address these aspects and comply with relevant data usage and financial advice regulations.