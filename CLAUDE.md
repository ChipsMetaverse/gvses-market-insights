# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GVSES AI Market Analysis Assistant - A professional trading dashboard with voice-enabled market insights powered by ElevenLabs Conversational AI and Claude. The application provides real-time market data visualization, technical analysis, and an AI voice assistant for market queries. Built with React TypeScript frontend featuring TradingView Lightweight Charts, FastAPI backend, and Supabase for conversation persistence.

## Key Architecture

- **Backend** (`backend/`): FastAPI server exposing REST endpoints, a proxy to ElevenLabs for signed WS URLs, and text-only `/ask` fallback to Claude
- **Frontend** (`frontend/`): React + TypeScript + Vite application featuring:
  - **TradingDashboardSimple**: Main dashboard component with three-panel layout
  - **TradingChart**: Candlestick chart component using TradingView Lightweight Charts v5
  - **Voice Assistant**: Real-time voice interface with visual feedback and conversation history
  - **Market Insights Panel**: Stock tickers with price movements and technical indicators (ST, LTB, QE)
  - **Chart Analysis Panel**: Real-time market analysis and pattern detection
- **Database** (`database/`): PostgreSQL schema for Supabase conversation persistence
- **Docker**: Full containerization support with docker-compose

## Development Commands

### Backend
```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Run development server
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000

# Run test script
python test_server.py
```

### Frontend
```bash
# Install dependencies
cd frontend && npm install

# Development server
npm run dev

# Build for production
npm run build

# Type checking
npm run build  # includes tsc

# Linting
npm run lint
```

### Docker Development
```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Environment Configuration

Supabase is required for persistence and multi-user support. ElevenLabs is required for real-time voice (ASR+TTS).

Set variables in:
- `backend/.env`
  - `ANTHROPIC_API_KEY`
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `ELEVENLABS_API_KEY`
  - `ELEVENLABS_AGENT_ID`
- `frontend/.env`
  - `VITE_SUPABASE_URL`
  - `VITE_SUPABASE_ANON_KEY`
  - `VITE_API_URL` (default `http://localhost:8000`)

## WebSocket Protocol

The application uses ElevenLabs Conversational AI WebSocket for real-time voice conversations. The browser connects directly to ElevenLabs using a signed URL fetched from the backend.

Key flow:
- Client fetches signed URL: `GET /elevenlabs/signed-url`
- Client opens WS to ElevenLabs: `wss://api.elevenlabs.io/v1/convai/conversation?...`
- Client streams mic audio (`user_audio_chunk`) and receives events:
  - `audio` (base64 PCM chunks) → queued and played
  - `user_transcript` → user’s recognized text
  - `agent_response` → agent’s text (usually sent with first `audio`)
  - `agent_response_correction`, `ping/pong`, etc.

## Key Dependencies

Backend:
- FastAPI with WebSocket support
- httpx for HTTP client operations
- Supabase client for database operations
- SpeechRecognition and gTTS for audio processing
- python-dotenv for environment configuration

Frontend:
- React 18 with TypeScript
- Vite for build tooling
- Supabase JS client
- `@elevenlabs/client` and `voice-stream` for Conversational AI
- `lightweight-charts` v5 for TradingView charting
- ESLint for code quality

## Testing

- Backend testing: Run `python test_server.py` from project root
- Frontend: No test runner configured

## Port Configuration

- Backend API: http://localhost:8000
- Frontend Dev: http://localhost:5174 (configured in vite.config.ts)
- API Documentation: http://localhost:8000/docs

## Database Schema

When using Supabase, the schema in `database/schema.sql` creates:
- `conversations` table for message storage
- `sessions` table for conversation sessions
- `audio_files` table for audio recordings

## MCP Server Configuration

External MCP servers can be configured via the `MCP_SERVERS` environment variable as a JSON array in the backend `.env` file.

---

## Implementation guide (end-to-end)

### 1) Create an ElevenLabs agent (CLI or dashboard)

- CLI (recommended):
  1. Install and auth: `npm i -g @elevenlabs/convai-cli` then `export ELEVENLABS_API_KEY=...`
  2. Initialize: `cd elevenlabs && convai init`
  3. Create dev agent: `convai add agent "Market Insights Voice" --template minimal --env dev --skip-upload`
  4. Open the generated JSON in `elevenlabs/agent_configs/dev/` and set:
     - `conversation_config.agent.prompt`: paste contents of `idealagent.md`
     - `conversation_config.agent.language`: `en`
     - `conversation_config.llm.temperature`: `0.3` (or as needed)
     - `conversation_config.tts`: `{ model: "eleven-multilingual-v1", voice_id: "<your_voice_id>", audio_format: { format: "pcm", sample_rate: 44100 } }`
     - `conversation_config.asr`: `{ model: "nova-2-general", language: "auto" }`
     - `conversation_config.conversation.text_only`: `false`
  5. Sync: `convai sync --env dev` and get the Agent ID: `convai status --agent "Market Insights Voice"`
  6. Set `ELEVENLABS_AGENT_ID` in `backend/.env`.

- Dashboard alternative:
  - Create an agent at `https://elevenlabs.io/app/conversational-ai`, configure ASR/voice, copy the Agent ID.

### 2) Configure environment variables

- `backend/.env` must include: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID`.
- `frontend/.env` must include: `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and optionally `VITE_API_URL`.

### 3) Backend endpoints

- `GET /health` → basic health
- `GET /elevenlabs/signed-url` → returns `{ signed_url }` by proxying ElevenLabs `get-signed-url`
- `POST /ask` → text-only fallback to Claude (optional for voice path)

### 4) Frontend behavior (what to expect)

- The UI shows:
  - Start Voice Chat / Stop Voice Chat buttons
  - A text input and Send button (“Or type your message…”) below the voice controls
  - An audio visualizer that moves while you speak
  - A scrolling chat history that updates with user and assistant messages

- When you click “Start Voice Chat”:
  - The app requests mic permission and immediately starts listening and streaming audio to ElevenLabs
  - You can speak right away; recognized text appears as `user_transcript`
  - The agent responds with streamed audio and an `agent_response` message

- When you type in the input box and click Send:
  - The text is sent to the same ElevenLabs session as a `user_message`
  - The agent responds as with voice input

### 5) Persistence

- Supabase is available to store conversation history. You can persist `user_transcript` and `agent_response` events directly from the frontend using the provided `SupabaseProvider` and client. Ensure RLS policies are set per `database/schema.sql`.

### 6) Troubleshooting voice input

- Verify backend returns a signed URL:
  - `curl -s http://localhost:8000/elevenlabs/signed-url`
- Check browser Network tab:
  - There should be a WS to `wss://api.elevenlabs.io/v1/convai/conversation?...`
- Ensure mic permission is granted and no OS-level block is present
- Ensure your ElevenLabs agent has ASR configured (`nova-2-general`) and is not configured to speak first if you prefer it to wait
- If using a private agent, ensure allowlist and signed URLs are configured for your domain or `localhost`

### 7) Production notes

- Consider reconnect/backoff handling for WS
- Add jitter buffer or more advanced audio queueing if needed
- Configure MCP tools in ElevenLabs with “Always Ask” first, then relax to fine-grained approvals as trust grows

### 8) Direct Claude usage (optional)

- The `/ask` endpoint remains available for text-only flows to Claude. For a consistent experience, prefer sending text via the ElevenLabs WS (`user_message`) so voice and text share one agent session.

## Trading Dashboard Components

### TradingDashboardSimple (`frontend/src/components/TradingDashboardSimple.tsx`)
Main dashboard component implementing the GVSES AI Market Analysis Assistant interface:
- Three-panel layout: Market Insights (left), Interactive Charts with Voice (center), Chart Analysis (right)
- Tab navigation between Interactive Charts and Voice + Manual Control modes
- Responsive design with clean white professional styling

### TradingChart (`frontend/src/components/TradingChart.tsx`)
Candlestick chart component using TradingView Lightweight Charts v5:
- Real-time price data visualization
- Technical level overlays (QE, ST, LTB levels)
- Responsive chart sizing
- Dark theme configuration

### Voice Assistant Interface
Interactive voice control with visual feedback:
- Animated microphone with pulse rings when listening
- Recording timer display
- Audio visualizer bars
- Voice conversation history with user/assistant messages
- "Control the chart" button for voice commands

### Market Data Display
- Stock cards with symbols, prices, and percentage changes
- Color-coded technical indicators (ST, LTB, QE)
- Real-time chart analysis updates
- Pattern detection with confidence levels