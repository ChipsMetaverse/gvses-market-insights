# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GVSES AI Market Analysis Assistant - A professional trading dashboard with voice-enabled market insights powered by ElevenLabs Conversational AI and Claude. The application provides real-time market data visualization, technical analysis, and an AI voice assistant for market queries. Built with React TypeScript frontend featuring TradingView Lightweight Charts, FastAPI backend with hybrid MCP/Direct API architecture for optimal performance.

## Key Architecture

### Backend (`backend/`)
FastAPI server with hybrid MCP/Direct API architecture for optimal performance:
- **Hybrid Data Service**: Automatically selects best service based on environment
  - **Direct API Mode** (Production): Sub-second Yahoo Finance responses, no subprocess overhead
  - **MCP Mode** (Development): AI tooling benefits, JSON-RPC communication
- **Service Factory Pattern**: `MarketServiceFactory` intelligently routes based on `USE_MCP` environment variable
- **Dual MCP Support**: market-mcp-server (Node.js) and alpaca-mcp-server (Python) for extended capabilities
- **ElevenLabs Proxy**: Signed URL generation for WebSocket voice streaming
- **Claude Integration**: Text-only `/ask` endpoint fallback

### Frontend (`frontend/`)
React + TypeScript + Vite application with professional trading interface:
- **TradingDashboardSimple**: Three-panel layout (Market Insights, Interactive Charts, Chart Analysis)
- **TradingChart**: TradingView Lightweight Charts v5 with real-time candlestick visualization
  - **Technical Level Labels**: Left-side labels (QE, ST, LTB) that sync instantly with chart movements
  - **Label Synchronization**: Uses ref pattern to avoid React closure issues in event handlers
  - **Instant Updates**: Direct event handling without requestAnimationFrame for zero-delay tracking
  - **Chart Events**: Subscribes to pan, zoom, and crosshair events for continuous label positioning
- **Voice Assistant**: ElevenLabs Conversational AI with visual feedback
- **Market Insights Panel**: Stock tickers with technical indicators (ST, LTB, QE)
- **Chart Analysis Panel**: Scrollable expandable news feed (CNBC + Yahoo Finance hybrid)

### MCP Servers
- **market-mcp-server** (`market-mcp-server/`): Node.js, 35+ Yahoo Finance and CNBC tools
- **alpaca-mcp-server** (`alpaca-mcp-server/`): Python, Alpaca Markets API integration

## Development Commands

### Backend
```bash
cd backend && pip install -r requirements.txt
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000

# Testing
python test_server.py          # Basic functionality
python test_dual_mcp.py         # Dual MCP integration
python test_alpaca_mcp.py       # Alpaca MCP testing
```

### Frontend
```bash
cd frontend && npm install
npm run dev      # Development server (port 5174)
npm run build    # Production build with TypeScript checking
npm run lint     # ESLint checking
```

### Market MCP Server
```bash
cd market-mcp-server && npm install
npm start        # Production mode
npm run dev      # Development with watch
npm test         # Run tests
```

### Docker
```bash
docker-compose up --build    # Build and run all services
docker-compose up -d          # Run in background
docker-compose logs -f        # View logs
docker-compose down           # Stop services
```

## Environment Configuration

### Backend (`backend/.env`)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
ELEVENLABS_API_KEY=your_key
ELEVENLABS_AGENT_ID=your_agent_id

# Performance Control
USE_MCP=false    # Set to false in production for Direct API mode
                 # Set to true in development for MCP benefits

# Optional
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
MODEL=claude-3-sonnet-20240229
```

### Frontend (`frontend/.env` and `frontend/.env.development`)
```bash
VITE_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOi...
VITE_API_URL=http://localhost:8000    # Important: Use port 8000
```

## API Endpoints

### Core Market Data
All endpoints support both MCP and Direct modes transparently:

- `GET /api/stock-price?symbol=TSLA` - Real-time price (< 500ms in Direct mode)
- `GET /api/stock-history?symbol=TSLA&days=100` - Historical candles (< 300ms in Direct mode)
- `GET /api/stock-news?symbol=TSLA` - Hybrid CNBC + Yahoo news (< 700ms in Direct mode)
- `GET /api/comprehensive-stock-data?symbol=TSLA` - Complete stock information
- `GET /api/market-overview` - Market indices and movers

### Enhanced Endpoints
- `GET /api/enhanced/market-data` - Auto-selects best data source
- `GET /api/enhanced/historical-data` - Intelligent routing
- `GET /api/enhanced/compare-sources` - Debug tool for data comparison

### Voice & AI
- `GET /elevenlabs/signed-url` - WebSocket URL for voice streaming
- `POST /ask` - Text-only Claude fallback
- `WS /ws/quotes` - Real-time quote streaming

### Health & Status
- `GET /health` - Reports service mode (MCP or Direct) and health status

## Performance Characteristics

### Production (Direct Mode)
- **Response Times**: 40-700ms (375x faster than MCP)
- **Cold Start**: None (direct HTTP calls)
- **Reliability**: No subprocess management issues
- **Memory**: Minimal overhead

### Development (MCP Mode)
- **Response Times**: 3-15+ seconds (subprocess overhead)
- **Cold Start**: 3-5 seconds per subprocess
- **Benefits**: AI tooling integration, unified protocol
- **Use Case**: Development and AI agent interactions

## Key Implementation Details

### Hybrid Architecture (`backend/services/market_service_factory.py`)
```python
def create_market_service():
    use_mcp = os.getenv('USE_MCP', 'true').lower() == 'true'
    if use_mcp:
        return MarketDataService()  # MCP mode
    else:
        return DirectMarketDataService()  # Direct API mode
```

### Direct Service Benefits (`backend/services/direct_market_service.py`)
- Native Python Yahoo Finance client (no subprocess)
- Async HTTP operations with httpx
- Proper error handling with retries
- Sub-second response times

### MCP Integration (`backend/mcp_client.py`)
- JSON-RPC over stdio communication
- Subprocess management for Node.js server
- Tool abstraction for market data access
- Best for AI agent interactions

## Testing Scripts

- `test_server.py` - API endpoint functionality
- `test_dual_mcp.py` - Dual MCP server integration
- `test_alpaca_mcp.py` - Alpaca Markets testing
- `test_elevenlabs_conversation.py` - Voice conversation
- `test_supabase.py` - Database connection

## Common Development Tasks

### Switching Between MCP and Direct Mode
1. Set `USE_MCP=false` in `backend/.env` for Direct mode
2. Set `USE_MCP=true` for MCP mode
3. Restart backend server
4. Check `/health` endpoint to verify mode

### Adding New Market Data Endpoint
1. Add method to both `MarketDataService` and `DirectMarketDataService`
2. Ensure consistent interface between services
3. Add FastAPI endpoint in `mcp_server.py`
4. Update frontend service in `marketDataService.ts`

### Modifying Voice Agent
1. Update prompt in `idealagent.md`
2. Sync: `cd elevenlabs && convai sync --env dev`
3. Test: `python test_elevenlabs_conversation.py`

### Updating Chart Analysis Panel
1. Modify `TradingDashboardSimple.tsx` (news/analysis sections)
2. Update styles in `TradingDashboardSimple.css`
3. Maintain 350px max-height for scrollable container

## Architecture Philosophy

- **Performance First**: Direct API for production, MCP for development
- **Real Data Only**: All market data from real APIs (Yahoo Finance, CNBC, Alpaca)
- **Hybrid Intelligence**: Multiple data sources for comprehensive insights
- **Non-Obstructive UI**: Expandable elements instead of modals
- **Smart Service Selection**: Automatic environment-based optimization
- **Voice-First Design**: Natural voice interactions with visual feedback

## Production Deployment

### Fly.io Configuration
```toml
[env]
  USE_MCP = "false"  # Critical: Use Direct mode in production
  PORT = "8000"
```

### Performance Metrics (Production)
| Endpoint | MCP Mode | Direct Mode | Improvement |
|----------|----------|-------------|-------------|
| Health | 15s+ timeout | 40ms | 375x faster |
| Stock Price | 15s+ timeout | 493ms | 30x faster |
| Stock History | 503 Timeout | 217ms | Fixed |
| Stock News | 503 Timeout | 653ms | Fixed |

## Troubleshooting

### Timeout Issues in Production
- **Solution**: Ensure `USE_MCP=false` in production environment
- **Verification**: Check `/health` endpoint for "service_mode": "Direct"

### MCP Server Not Starting
- **Check**: Node.js installed and in PATH
- **Verify**: `cd market-mcp-server && npm install`
- **Alternative**: Switch to Direct mode with `USE_MCP=false`

### Voice Not Working
1. Check ElevenLabs signed URL: `curl http://localhost:8000/elevenlabs/signed-url`
2. Verify WebSocket connection in browser Network tab
3. Ensure microphone permissions granted
4. Check ElevenLabs agent configuration

## Recent Updates

### Chart Label Synchronization Fix (Latest)
- Fixed technical level labels (QE, ST, LTB) disappearing from chart
- Implemented instant label tracking with chart pan/zoom movements
- Resolved React closure issues using ref pattern for event handlers
- Removed requestAnimationFrame wrapper for zero-delay updates
- Labels now positioned on left side only for cleaner interface

### Production Performance Fix
- Implemented hybrid MCP/Direct architecture
- 375x performance improvement in production
- Eliminated subprocess timeout issues
- Maintained backward compatibility

### Enhanced News System
- Hybrid CNBC + Yahoo Finance integration
- Expandable inline news (no modals)
- Smart symbol relevance filtering
- Scrollable container with smooth animations