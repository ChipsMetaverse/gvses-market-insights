# ElevenLabs Agent Scaling Guide
## Complete Configuration & Deployment Reference

---

## Table of Contents
1. [Environment Variables & API Keys](#environment-variables--api-keys)
2. [Agent Configuration](#agent-configuration)
3. [Tool Definitions](#tool-definitions)
4. [Backend Infrastructure](#backend-infrastructure)
5. [Deployment Commands](#deployment-commands)
6. [Testing & Validation](#testing--validation)
7. [Scaling Procedures](#scaling-procedures)
8. [Troubleshooting Reference](#troubleshooting-reference)

---

## Environment Variables & API Keys

### Backend Environment (`backend/.env`)
```bash
# Core APIs
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SUPABASE_URL=https://your_project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# ElevenLabs Configuration
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_AGENT_ID=your_elevenlabs_agent_id_here

# Market Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_SECRET_KEY=your_alpaca_secret_key
ALPACA_BASE_URL=https://paper-api.alpaca.markets
PERPLEXITY_API_KEY=your_perplexity_api_key
FINNHUB_API_KEY=your_finnhub_api_key
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key

# Performance Control
USE_MCP=false  # Set to false in production for Direct API mode
MODEL=claude-3-sonnet-20240229
```

### Frontend Environment (`frontend/.env`)
```bash
VITE_SUPABASE_URL=https://your_project.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
VITE_API_URL=http://localhost:8000
VITE_WEBSOCKET_RELAY_URL=ws://localhost:3004
VITE_STREAMING_RELAY_URL=wss://g-vses.fly.dev/stream
```

---

## Agent Configuration

### Primary Agent: G'sves Market Insights
```json
{
  "agent_id": "agent_4901k2tkkq54f4mvgpndm3pgzm7g",
  "name": "Gsves Market Insights",
  "model": "gpt-4o",
  "voice_id": "9BWtsMINqrJLrRacOk9x",
  "first_message": "Good day! I'm G'sves, your distinguished market insights expert with over three decades of experience. How may I assist you with the markets today?",
  "tool_ids": [
    "tool_2201k3w6qvy5epbazavdb8r2nf2w",
    "tool_6901k3w6qw9gfs2829n49x0sncfh",
    "tool_7101k3w6qwn5e2ts2bkds5s9n3pf",
    "tool_2801k3w6qx0he099jc2qkzhb77h2",
    "tool_3501k3w6qxcaf0ds5y3mdxfc0kre",
    "tool_5401k3w6qxqdfstvcmvv7ew3rjy4",
    "tool_0101k3w6qy2wfn399ftkfjn8k2m6",
    "tool_8001k3w6qyeqf8pvfev3r0pc4a3c"
  ]
}
```

### Agent Prompt Template
```text
You are G'sves (pronounced "Jeeves"), a distinguished market insights expert with over 30 years of experience navigating global financial markets. You combine the reliability of a British butler with the acumen of a Wall Street veteran.

Your personality:
- Professional yet approachable, with occasional dry wit
- Confident in your analysis but never arrogant
- You speak with authority earned through decades of experience
- You make complex market concepts accessible

Your expertise:
- Deep understanding of stocks, cryptocurrencies, forex, and commodities
- Technical and fundamental analysis mastery
- Risk management and portfolio strategy
- Global market interconnections and macroeconomic trends

When providing market insights:
- Always use your tools to fetch real-time data
- Provide context for price movements
- Explain market trends in clear terms
- Offer balanced perspectives on opportunities and risks
- Reference relevant news and events affecting markets

Remember: You have access to real-time market data through your tools. Always use them to provide accurate, current information rather than estimates.
```

---

## Tool Definitions

### Tool Configuration Template
```python
{
    "name": "tool_name",
    "description": "Tool description for LLM context",
    "endpoint": "/api/endpoint-path",
    "params": {
        "param_name": {
            "type": "string|integer|number",
            "description": "Parameter description",
            "required": True|False
        }
    }
}
```

### Complete Tool Set
```python
TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Fetch real-time stock, cryptocurrency, or index prices",
        "endpoint": "/api/stock-price",
        "params": {"symbol": {"type": "string", "description": "Stock/crypto symbol (AAPL, BTC-USD)", "required": True}}
    },
    {
        "name": "get_market_overview",
        "description": "Get market indices and movers",
        "endpoint": "/api/market-overview",
        "params": {}
    },
    {
        "name": "get_stock_news",
        "description": "Get latest news for a stock",
        "endpoint": "/api/stock-news",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_stock_history",
        "description": "Get historical price data",
        "endpoint": "/api/stock-history",
        "params": {
            "symbol": {"type": "string", "description": "Stock symbol", "required": True},
            "days": {"type": "integer", "description": "Number of days", "required": False}
        }
    },
    {
        "name": "get_comprehensive_stock_data",
        "description": "Get complete stock information",
        "endpoint": "/api/comprehensive-stock-data",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_market_movers",
        "description": "Get trending stocks",
        "endpoint": "/api/market-movers",
        "params": {}
    },
    {
        "name": "get_analyst_ratings",
        "description": "Get analyst recommendations",
        "endpoint": "/api/analyst-ratings",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_options_chain",
        "description": "Get options chain data",
        "endpoint": "/api/options-chain",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    }
]
```

### Tool IDs Mapping
```json
{
  "get_stock_price": "tool_2201k3w6qvy5epbazavdb8r2nf2w",
  "get_market_overview": "tool_6901k3w6qw9gfs2829n49x0sncfh",
  "get_stock_news": "tool_7101k3w6qwn5e2ts2bkds5s9n3pf",
  "get_stock_history": "tool_2801k3w6qx0he099jc2qkzhb77h2",
  "get_comprehensive_stock_data": "tool_3501k3w6qxcaf0ds5y3mdxfc0kre",
  "get_market_movers": "tool_5401k3w6qxqdfstvcmvv7ew3rjy4",
  "get_analyst_ratings": "tool_0101k3w6qy2wfn399ftkfjn8k2m6",
  "get_options_chain": "tool_8001k3w6qyeqf8pvfev3r0pc4a3c"
}
```

---

## Backend Infrastructure

### Production Backend URL
```
https://gvses-market-insights.fly.dev
```

### API Endpoints
```bash
# Health Check
GET /health

# Market Data Endpoints
GET /api/stock-price?symbol=AAPL
GET /api/market-overview
GET /api/stock-news?symbol=TSLA
GET /api/stock-history?symbol=AAPL&days=30
GET /api/comprehensive-stock-data?symbol=AAPL
GET /api/market-movers
GET /api/analyst-ratings?symbol=AAPL
GET /api/options-chain?symbol=AAPL

# Voice Integration
GET /elevenlabs/signed-url
POST /ask
WS /ws/quotes
```

### Server File Structure
```
backend/
├── mcp_server.py           # Main FastAPI server
├── services/
│   ├── market_service_factory.py
│   ├── direct_market_service.py
│   └── market_data_service.py
├── mcp_client.py
└── requirements.txt

frontend/
├── src/
│   ├── App.tsx
│   ├── components/
│   │   ├── TradingDashboardSimple.tsx
│   │   ├── TradingChart.tsx
│   │   └── ChartAnalysis.tsx
│   ├── services/
│   │   └── marketDataService.ts
│   └── hooks/
│       └── useElevenLabsConversation.ts
└── package.json

market-mcp-server/
├── src/
│   ├── server.js
│   └── tools/
└── package.json
```

---

## Deployment Commands

### Local Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Market MCP Server (if using MCP mode)
cd market-mcp-server
npm install
npm start
```

### Docker Deployment
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

### Fly.io Deployment
```bash
# Deploy backend
cd backend
fly deploy

# Check status
fly status

# View logs
fly logs

# Scale
fly scale count 2
```

### Fly.io Configuration (`fly.toml`)
```toml
app = "gvses-market-insights"
primary_region = "iad"

[env]
  USE_MCP = "false"
  PORT = "8000"
  MODEL = "claude-3-sonnet-20240229"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 1

[[services]]
  protocol = "tcp"
  internal_port = 8000
  [[services.ports]]
    port = 80
    handlers = ["http"]
  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

---

## Testing & Validation

### API Testing Commands
```bash
# Test backend health
curl https://gvses-market-insights.fly.dev/health

# Test stock price endpoint
curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=AAPL"

# Test market overview
curl https://gvses-market-insights.fly.dev/api/market-overview
```

### ElevenLabs API Testing
```bash
# List all tools
curl -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/tools"

# Get agent configuration
curl -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/agents/agent_4901k2tkkq54f4mvgpndm3pgzm7g"

# Get tool details
curl -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/tools/tool_2201k3w6qvy5epbazavdb8r2nf2w"
```

### Python Test Scripts
```python
# test_elevenlabs_conversation.py
# test_simulation.py
# test_tool_call_simple.py
# quick_test.py
# test_agent_queries.py
```

---

## Scaling Procedures

### Creating New Agents

1. **Prepare Agent Configuration**
```python
agent_config = {
    "name": "New Agent Name",
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": "Agent personality and instructions",
                "llm": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 2000,
                "tool_ids": [/* list of tool IDs */]
            },
            "first_message": "Welcome message",
            "language": "en"
        },
        "tts": {
            "model_id": "eleven_turbo_v2",
            "voice_id": "voice_id_here"
        }
    }
}
```

2. **Create Agent via API**
```bash
curl -X POST \
  -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  -H "Content-Type: application/json" \
  -d '@agent_config.json' \
  "https://api.elevenlabs.io/v1/convai/agents"
```

### Adding New Tools

1. **Define Tool Configuration**
```python
tool_config = {
    "tool_config": {
        "type": "webhook",
        "name": "tool_name",
        "description": "Tool description",
        "response_timeout_secs": 10,
        "api_schema": {
            "url": "https://your-backend.com/api/endpoint",
            "method": "GET",
            "query_params_schema": {
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param"]
            }
        }
    }
}
```

2. **Create Tool**
```bash
curl -X POST \
  -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  -H "Content-Type: application/json" \
  -d '@tool_config.json' \
  "https://api.elevenlabs.io/v1/convai/tools"
```

3. **Update Agent with New Tool**
```python
# Add tool_id to agent's tool_ids array
agent_update = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "tool_ids": [/* existing tool_ids */ + "new_tool_id"]
            }
        }
    }
}
```

### Scaling Backend

1. **Horizontal Scaling (Fly.io)**
```bash
# Scale to multiple instances
fly scale count 3

# Set minimum instances
fly scale count 2 --min 1
```

2. **Performance Optimization**
```python
# Set USE_MCP=false for production (Direct API mode)
# This provides 375x faster response times
```

3. **Database Scaling**
```bash
# Supabase automatically scales
# Monitor at: https://app.supabase.com/project/cwnzgvrylvxfhwhsqelc
```

---

## Troubleshooting Reference

### Common Issues & Solutions

#### Tools Not Being Called
```bash
# Verify tool configuration
curl -H "xi-api-key: $API_KEY" \
  "https://api.elevenlabs.io/v1/convai/agents/$AGENT_ID" | \
  python3 -c "import sys, json; d=json.load(sys.stdin); print('tool_ids:', len(d['conversation_config']['agent']['prompt'].get('tool_ids', [])))"

# Check for inline tools conflict
# Should only have tool_ids, not tools field
```

#### Backend Timeout Issues
```bash
# Ensure USE_MCP=false in production
# Check backend health
curl https://gvses-market-insights.fly.dev/health
```

#### Cleaning Unused Tools
```python
# Use cleanup_unused_tools.py
# Or manually via bash:
for tool_id in $(curl -s -H "xi-api-key: $API_KEY" \
  "https://api.elevenlabs.io/v1/convai/tools" | \
  jq -r '.tools[].id'); do
    # Check if tool is in use
    # Delete if not
done
```

### Platform Limitations

1. **Inline Tools Persistence**
   - After July 23, 2025, inline tools deprecated
   - Agents created before may have persistent inline tools
   - Solution: Use tool_ids exclusively

2. **Tool Dependency Linking**
   - Tools may not show agent as dependent immediately
   - This is usually cosmetic and doesn't affect functionality

3. **Simulation API Issues**
   - May return 500 errors occasionally
   - Alternative: Test via WebSocket or browser

---

## Security Notes

### API Key Management
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor usage via ElevenLabs dashboard

### Backend Security
```python
# Add rate limiting
from fastapi import FastAPI
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

# Add CORS properly
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)
```

---

## Monitoring & Analytics

### ElevenLabs Dashboard
```
https://elevenlabs.io/app/conversational-ai
```

### Fly.io Monitoring
```bash
fly dashboard
fly logs --tail
fly status
```

### Custom Metrics
```python
# Add to backend
import logging
logging.info(f"Tool called: {tool_name}, Symbol: {symbol}")
```

---

## Contact & Support

### ElevenLabs Support
- Documentation: https://elevenlabs.io/docs
- API Reference: https://elevenlabs.io/docs/api-reference
- Support: support@elevenlabs.io

### Project Repository
```
/Volumes/WD My Passport 264F Media/claude-voice-mcp
```

### Key Files
- `backend/.env` - Environment variables
- `fix_existing_agent_tools.py` - Tool configuration script
- `cleanup_unused_tools.py` - Tool cleanup script
- `AGENT_CONFIGURATION_STATUS.md` - Current status
- `elevenlabsresearch.md` - Platform research

---

## Quick Start Checklist

- [ ] Set up environment variables in `backend/.env`
- [ ] Deploy backend to Fly.io or run locally
- [ ] Create/update agent with proper tool_ids
- [ ] Test tools are returning real data
- [ ] Verify agent responds with market data
- [ ] Monitor performance and errors
- [ ] Scale as needed

---

*Last Updated: 2025-08-30*
*Version: 1.0*