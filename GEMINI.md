# GEMINI Project: Claude Voice Assistant MCP Server

## Project Overview

This project is a sophisticated voice-enabled Model Context Protocol (MCP) server that leverages Claude AI for intelligent conversations. It features a FastAPI backend and a React frontend, enabling real-time voice interaction, WebSocket communication, and persistent conversation history with Supabase.

**Key Technologies:**

*   **Backend:** Python, FastAPI
*   **Frontend:** React, TypeScript, Vite
*   **Database:** PostgreSQL (Supabase)
*   **AI:** Anthropic's Claude
*   **Deployment:** Docker

## Building and Running

### Prerequisites

*   Python 3.11+
*   Node.js 20+
*   Docker & Docker Compose (optional)
*   Anthropic API key
*   Supabase project (optional for persistence)

### 1. Environment Setup

Create `.env` files for both the backend and frontend with the necessary API keys and configuration.

**Backend (`backend/.env`):**
```bash
OPENAI_API_KEY=sk-openai-...
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
ALPACA_API_KEY=AK...
ALPACA_SECRET_KEY=SK...
```

**Frontend (`frontend/.env`):**
```bash
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
```

### 2. Running the Application

**Option A: Docker Compose (Recommended)**
```bash
docker-compose up --build
```

**Option B: Local Development**

*   **Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn mcp_server:app --reload
    ```
*   **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

### 3. Accessing the Application

*   **Frontend:** `http://localhost:5173`
*   **Backend API:** `http://localhost:8000`
*   **API Docs:** `http://localhost:8000/docs`

## Development Conventions

*   **Testing:**
    *   Backend tests are run with `pytest`.
    *   The frontend does not have a test runner configured.
*   **Contributing:**
    *   Contributions are welcome through pull requests on GitHub.
    *   The standard fork, branch, commit, and pull request workflow is used.
*   **Dependencies:**
    *   Backend Python dependencies are managed with `pip` and a `requirements.txt` file.
    *   Frontend Node.js dependencies are managed with `npm` and a `package.json` file.
