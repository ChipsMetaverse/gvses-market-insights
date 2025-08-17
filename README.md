# Claude Voice Assistant MCP Server

A sophisticated voice-enabled Model Context Protocol (MCP) server that leverages Claude AI for intelligent conversations. Features real-time voice interaction, WebSocket communication, and persistent conversation history with Supabase.

## 🌟 Features

- **Voice Interaction**: Real-time speech-to-text and text-to-speech capabilities
- **Claude AI Integration**: Powered by Anthropic's Claude for intelligent responses
- **MCP Server Support**: Connect to external MCP servers for enhanced data access
- **WebSocket Communication**: Real-time bidirectional communication
- **Conversation Persistence**: Store and retrieve conversation history with Supabase
- **Modern UI**: React + TypeScript frontend with audio visualization
- **Session Management**: Track and manage conversation sessions
- **Multi-modal Input**: Support for both voice and text input

## 🏗️ Architecture

```
claude-voice-mcp/
├── backend/              # FastAPI MCP server
│   ├── mcp_server.py    # Main server implementation
│   ├── audio_processor.py # Audio processing utilities
│   └── requirements.txt  # Python dependencies
├── frontend/            # React + Vite application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom React hooks
│   │   └── lib/         # Utilities and configurations
│   └── package.json     # Node dependencies
├── database/            # Database schemas
│   └── schema.sql       # Supabase PostgreSQL schema
└── docker-compose.yml   # Container orchestration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- Anthropic API key
- Supabase project (optional for persistence)

### 1. Clone and Setup

```bash
cd /Users/MarcoPolo/workspace/claude-voice-mcp
```

### 2. Configure Environment Variables (Required)

Create and fill these files with your keys (examples shown inline):

#### Backend (`backend/.env`)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...

# Optional
MODEL=claude-3-sonnet-20240229
SYSTEM_PROMPT="You are a helpful voice assistant..."
MCP_SERVERS=[]
```

#### Frontend (`frontend/.env`)
```bash
# Required
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...

# Optional
VITE_WS_URL=ws://localhost:8000
VITE_API_URL=http://localhost:8000
```

### 3. Setup Database (Optional - for persistence)

If using Supabase:
1. Create a new Supabase project
2. Run the schema from `database/schema.sql` in the SQL editor
3. Copy your project URL and anon key to the environment files

### 4. Run the Application

#### Option A: Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

#### Option B: Run Locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📖 Usage

1. **Allow Microphone Access**: The browser will request microphone permissions
2. **Voice Input**: Hold the microphone button to speak
3. **Text Input**: Type messages in the text field
4. **View History**: Scroll through the conversation history
5. **Clear Session**: Click "Clear History" to start a new conversation

## 🔧 Configuration

### MCP Servers

Configure external MCP servers in the backend `.env`:

```bash
MCP_SERVERS='[
  {
    "name": "market-data",
    "url": "http://localhost:9000/sse"
  },
  {
    "name": "weather",
    "url": "http://localhost:9001/sse"
  }
]'
```

### System Prompt

Customize the assistant's behavior:

```bash
SYSTEM_PROMPT="You are a helpful voice assistant specializing in [your domain]..."
```

### Model Selection

Choose your Claude model:

```bash
MODEL=claude-3-sonnet-20240229  # or claude-3-opus-20240229
```

## 🛠️ Development

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn mcp_server:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
# (No test runner configured)
```

## 📚 API Endpoints

### REST Endpoints

- `GET /health` - Health check
- `POST /ask` - Submit a query and get response

### WebSocket

- `WS /ws/{session_id}` - Real-time communication channel

#### Message Types

**Client to Server:**
```json
{
  "type": "text",
  "query": "Your question here"
}
```

```json
{
  "type": "audio",
  "data": "base64_encoded_audio"
}
```

**Server to Client:**
```json
{
  "type": "response",
  "content": "Assistant's response",
  "timestamp": "2024-01-01T00:00:00Z",
  "audio_url": "optional_audio_url"
}
```

## 🗃️ Database Schema

The application uses PostgreSQL (via Supabase) with the following main tables:

- `conversations` - Stores all messages
- `sessions` - Tracks conversation sessions
- `audio_files` - Stores audio recordings (optional)

## 🔒 Security

- Row Level Security (RLS) enabled on all tables
- User authentication via Supabase Auth (optional)
- API key authentication for Claude
- CORS configuration for frontend access

## 🐛 Troubleshooting

### Common Issues

1. **Microphone not working**
   - Ensure HTTPS or localhost
   - Check browser permissions
   - Verify audio device is connected

2. **WebSocket connection failed**
   - Check backend is running
   - Verify CORS settings
   - Check firewall/proxy settings

3. **Claude API errors**
   - Verify API key is valid
   - Check rate limits
   - Ensure proper model name

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for Claude AI
- [Supabase](https://supabase.com) for database and auth
- [FastAPI](https://fastapi.tiangolo.com) for the backend framework
- [React](https://react.dev) for the frontend framework
- MCP community for protocol specifications

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the maintainers
- Check the documentation

---

Built with ❤️ using Claude AI and the MCP Protocol
