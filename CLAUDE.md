# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

GVSES AI Market Analysis Assistant - A professional trading dashboard with voice-enabled market insights powered by ElevenLabs Conversational AI and Claude. The application provides real-time market data visualization, technical analysis, and an AI voice assistant for market queries. Built with React TypeScript frontend featuring TradingView Lightweight Charts, FastAPI backend with hybrid MCP/Direct API architecture for optimal performance.

## Key Architecture

### Current Production Architecture (Commit e009f62 - Sep 2, 2025)

FastAPI server with Alpaca-first architecture and intelligent fallback:
- **MarketServiceWrapper**: Primary routing through Alpaca, fallback to MCP
  - **Stock Quotes/History**: Alpaca Markets (300-400ms) → Yahoo via MCP (3-15s) on failure
  - **News**: Always uses MCP for CNBC + Yahoo hybrid (now working with Node.js 22)
  - **Source Attribution**: All responses include `data_source` field
- **Node.js 22 Requirement**: Docker updated to Node.js 22 to fix undici compatibility
- **Service Factory Pattern**: `MarketServiceFactory` manages service lifecycle
- **Dual MCP Support**: market-mcp-server (Node.js) and alpaca-mcp-server (Python)
- **ElevenLabs Proxy**: Signed URL generation for WebSocket voice streaming
- **Claude Integration**: Text-only `/ask` endpoint fallback

### Previous Architecture Attempts

#### Phase 1: Alpaca-First with MCP Fallback (Localhost - Commit 6753c2e)
- Initial implementation of Alpaca-first architecture
- Worked locally but MCP news returned 0 articles in production due to Node.js 18 issue

#### Phase 2: Triple Hybrid Architecture (Production Attempt - Commit b152f15)
- Over-engineered solution with Direct API + Alpaca + MCP running concurrently
- Removed in favor of simpler Alpaca-first approach

### Frontend (`frontend/`)
React + TypeScript + Vite application with professional trading interface:
- **TradingDashboardSimple**: Three-panel layout (Market Insights, Interactive Charts, Chart Analysis)
- **TradingChart**: TradingView Lightweight Charts v5 with real-time candlestick visualization
  - **Technical Level Labels**: Left-side labels (QE, ST, LTB) that sync instantly with chart movements
  - **Label Synchronization**: Uses ref pattern to avoid React closure issues in event handlers
  - **Instant Updates**: Direct event handling without requestAnimationFrame for zero-delay tracking
  - **Chart Events**: Subscribes to pan, zoom, and crosshair events for continuous label positioning
- **Voice Assistant**: ElevenLabs Conversational AI with visual feedback
- **Market Insights Panel**: Dynamic watchlist with customizable stock tickers
  - **Add Any Symbol**: Search input to add any valid stock ticker (PLTR, MSFT, GOOGL, etc.)
  - **Remove Symbols**: X button on each card (minimum 1 symbol required)
  - **LocalStorage Persistence**: User's watchlist saved across sessions
  - **Default Symbols**: TSLA, AAPL, NVDA, SPY, PLTR (fully customizable)
  - **API Validation**: Symbols verified before adding to watchlist
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

**Important**: Docker uses Node.js 22 for both builder and runtime stages to ensure MCP server compatibility

## Environment Configuration

### Backend (`backend/.env`)
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
ELEVENLABS_API_KEY=your_key
ELEVENLABS_AGENT_ID=your_agent_id

# Alpaca-first architecture is now default in production
# No USE_MCP variable needed - simplified architecture

# Market Data Sources
ALPACA_API_KEY=your_alpaca_key      # Primary data source
ALPACA_SECRET_KEY=your_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Optional
MODEL=claude-3-sonnet-20240229
PORT=8080        # Production port (nginx proxy)
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
- `GET /api/symbol-search?query=microsoft&limit=10` - **NEW**: Semantic symbol search via Alpaca API

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

### Phase 1: Current Localhost (Alpaca-First + MCP)
- **Alpaca Quotes**: 300-400ms (professional data)
- **Alpaca History**: 400-500ms (licensed bars)
- **MCP Fallback**: 3-15s (when Alpaca unavailable)
- **News (MCP)**: 3-5s (CNBC + Yahoo hybrid)
- **Architecture**: Primary Alpaca, fallback to MCP

### Phase 2: Production (Triple Hybrid)
- **Direct API**: 40-700ms (Yahoo direct HTTP)
- **Alpaca API**: Sub-second (professional grade)
- **MCP Service**: 3-15s (comprehensive tooling)
- **Intelligent Routing**: Automatic best source selection
- **Performance**: 375x improvement over MCP-only

## Key Implementation Details

### Current Architecture (`backend/services/market_service_factory.py`)
```python
class MarketServiceWrapper:
    async def get_stock_price(self, symbol: str):
        # Try Alpaca first (professional data)
        try:
            if ALPACA_AVAILABLE:
                quote = await get_quote_from_alpaca(symbol)
                quote["data_source"] = "alpaca"
                return quote
        except Exception:
            # Fallback to Yahoo via MCP
            quote = await self._get_quote(symbol)
            quote["data_source"] = "yahoo_mcp"
            return quote
```

### Production Triple Hybrid (commit b152f15)
- **HybridMarketService**: Runs all services concurrently
- **DirectMarketDataService**: Direct Yahoo API (no subprocess)
- **AlpacaService**: Professional market data
- **MarketServiceWrapper**: MCP for comprehensive tools

### Service Selection Logic
- **Current**: Alpaca → MCP fallback per request
- **Production**: All services active, intelligent per-query routing

## Symbol Validation Strategy

### Market Data Validation (Implemented Sep 3, 2025)
The system uses **live market data validation** instead of blacklists to determine valid symbols:

#### Backend Validation (`mcp_server.py`)
- Returns HTTP 404 if symbol has price = 0 or no market data
- Returns HTTP 404 if symbol has no volume AND no previous close
- Validates against actual market data, not word lists

#### Frontend Validation (`TradingDashboardSimple.tsx`)
- Basic format check: 1-5 letters for stocks, XXX-USD for crypto
- Verifies symbol returns valid data (price > 0) before adding to watchlist
- Shows appropriate error messages based on API response

#### Voice Command Validation (`chartControlService.ts`)
- Removed extensive blacklist of common English words
- Simplified to format validation only
- Relies on backend API for final validation

### Why This Approach?
✅ **No false positives**: Valid tickers like "YOU" ($35.83), "IT" ($250.91), "ARE" work correctly  
✅ **No false negatives**: Invalid symbols like "ITS", "XYZABC" properly rejected  
✅ **Real-time validation**: Checks against live market state  
✅ **Simpler code**: No need to maintain blacklists  
✅ **Voice reliability**: Better handling of misinterpreted speech

## Testing Scripts

- `test_server.py` - API endpoint functionality
- `test_dual_mcp.py` - Dual MCP server integration
- `test_alpaca_mcp.py` - Alpaca Markets testing
- `test_elevenlabs_conversation.py` - Voice conversation
- `test_supabase.py` - Database connection

## Common Development Tasks

### Understanding Service Mode
- **Current Localhost**: Alpaca-first with MCP fallback (no USE_MCP variable)
- **Production**: Triple hybrid with Direct + Alpaca + MCP (USE_MCP controls Direct mode)
- Check `/health` endpoint to see active service mode

### Upgrading to Production Architecture
1. Checkout master branch: `git checkout master`
2. Set `USE_MCP=false` in `backend/.env` for Direct mode
3. Restart backend server
4. Verify with `/health` endpoint

### Adding New Market Data Endpoint
1. Add method to `MarketServiceWrapper` (current) or `HybridMarketService` (production)
2. Implement Alpaca integration if applicable (recommended for symbol-related endpoints)
3. Add FastAPI endpoint in `mcp_server.py`
4. Update frontend service in `marketDataService.ts`
5. **For search features**: Consider using Alpaca's asset database for professional accuracy

### Modifying Voice Agent
1. Update prompt in `idealagent.md`
2. Sync: `cd elevenlabs && convai sync --env dev`
3. Test: `python test_elevenlabs_conversation.py`

### Updating Chart Analysis Panel
1. Modify `TradingDashboardSimple.tsx` (news/analysis sections)
2. Update styles in `TradingDashboardSimple.css`
3. Maintain 350px max-height for scrollable container

### Managing Dynamic Watchlist
1. **Add Symbol via Search**: Type company name ("Microsoft") or ticker ("MSFT") - search dropdown shows suggestions
2. **Add via Voice**: Say "show me Microsoft" - automatically adds to watchlist and displays chart
3. **Remove Symbol**: Click the × button on any stock card (keeps minimum 1 symbol)
4. **Reset Defaults**: Clear localStorage: `localStorage.removeItem('marketWatchlist')`
5. **Set Custom Defaults**: `localStorage.setItem('marketWatchlist', JSON.stringify(['AAPL', 'GOOGL', 'AMZN']))`
6. **Professional Validation**: Alpaca API ensures only tradable symbols are added
7. **Search Features**: 300ms debounced search with real-time dropdown suggestions

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

### MCP News Returns 0 Articles in Production
- **Root Cause**: Node.js 18 has undici library compatibility issues
- **Solution**: Docker updated to use Node.js 22 in both builder and runtime
- **Error**: `ReferenceError: File is not defined` in undici/lib/web/webidl/index.js
- **Fixed**: Commit e009f62 - Sep 2, 2025

### MCP Server Not Starting
- **Check**: Node.js version (must be 22+ for undici compatibility)
- **Verify**: `cd market-mcp-server && npm install`
- **Local**: Run `node --version` (should be v22.x.x or higher)

### Voice Not Working
1. Check ElevenLabs signed URL: `curl http://localhost:8000/elevenlabs/signed-url`
2. Verify WebSocket connection in browser Network tab
3. Ensure microphone permissions granted
4. Check ElevenLabs agent configuration

## Voice Command Processing

### Semantic Voice Parsing (Sep 3, 2025)
The voice command system now uses **semantic search** instead of regex patterns:

#### Enhanced chartControlService.ts Features:
- **Async Command Processing**: `parseAgentResponse()` now async to support API calls
- **Company Name Resolution**: `resolveSymbolWithSearch()` method uses Alpaca API
- **Fallback Strategy**: Tries semantic search first, falls back to legacy static mapping
- **Professional Data**: Alpaca Markets ensures accurate ticker symbol matching

#### Voice Command Examples:
```typescript
// Before (regex-based, unreliable):
"show me Microsoft" -> parsed "YOU" incorrectly

// After (semantic search):
"show me Microsoft" -> API search -> MSFT (Microsoft Corporation)
"display Apple" -> API search -> AAPL (Apple Inc)
"load Tesla chart" -> API search -> TSLA (Tesla, Inc.)
```

#### Implementation Details:
- **API Endpoint**: Uses `/api/symbol-search?query=microsoft` 
- **Response Time**: Sub-second symbol resolution
- **Data Source**: Alpaca Markets professional asset database
- **Error Handling**: Graceful fallback to original parsing if API fails
- **Toast Feedback**: Shows resolved company name and ticker in success messages

### useSymbolSearch Hook (Sep 3, 2025)
New React hook for frontend symbol search functionality:

```typescript
const { searchResults, isSearching, searchError, hasSearched } = useSymbolSearch(query, 300);
```

#### Features:
- **300ms Debouncing**: Prevents excessive API calls during typing
- **State Management**: Handles loading, results, and error states
- **Caching**: Results cached in marketDataService for performance
- **Error Handling**: User-friendly error messages for failed searches
- **Real-time Updates**: Instant dropdown results as user types

#### Integration Points:
- **Market Insights Panel**: Search input field with dropdown suggestions
- **Voice Commands**: Automatic company name to ticker resolution
- **Watchlist Management**: Add symbols via search or direct entry
- **Chart Navigation**: Voice-controlled symbol switching

## Recent Updates

### Alpaca Symbol Search Integration (Sep 3, 2025)
- **Semantic Voice Commands**: "show me Microsoft" now correctly resolves to MSFT via Alpaca API
- **Professional Symbol Search**: New `/api/symbol-search` endpoint using Alpaca's asset database
- **Real-time Search Dropdown**: 300ms debounced search in Market Insights panel
- **Company Name Resolution**: Natural language support for all voice commands
- **useSymbolSearch Hook**: Custom React hook for search state management
- **Async Command Processing**: Voice parsing converted to async for API integration
- **Enhanced UX**: Both manual search and voice commands support company names
- **Professional Validation**: Alpaca Markets ensures tradable, accurate symbol matching

### Market Data Validation (Sep 3, 2025)
- **Replaced Blacklist Approach**: Removed hardcoded list of invalid words
- **Live Market Validation**: Symbols validated against real market data
- **Backend 404 Responses**: Invalid symbols return proper HTTP 404 errors
- **Valid Tickers Work**: "YOU" ($35.83), "IT" ($250.91), "ARE" now work correctly
- **Invalid Symbols Rejected**: "ITS", "XYZABC", "ME-USD" properly blocked
- **Simplified Code**: Removed 50+ word blacklist from chartControlService
- **Better Voice Support**: More reliable handling of voice commands

### Dynamic Watchlist Feature (Sep 2, 2025)
- **Customizable Market Insights**: Users can now add/remove any stock ticker
- **Search & Add**: Input field with "Add" button for new symbols
- **Symbol Validation**: API verification before adding to watchlist
- **Remove Capability**: X button on each stock card (minimum 1 required)
- **Persistent Storage**: localStorage saves user preferences across sessions
- **Default Watchlist**: TSLA, AAPL, NVDA, SPY, PLTR (expandable to any ticker)

### Production MCP Fix (Sep 2, 2025 - Commit e009f62)
- **Fixed MCP News**: Updated Docker to Node.js 22 to resolve undici compatibility
- **Simplified Architecture**: Deployed Alpaca-first approach to production
- **Node.js 22 Requirement**: Both builder and runtime stages now use Node.js 22
- **MCP Working**: News endpoint now returns CNBC + Yahoo articles (was returning 0)

### Chart Label Synchronization Fix (Sep 1, 2025)
- Fixed technical level labels (QE, ST, LTB) disappearing from chart
- Implemented instant label tracking with chart pan/zoom movements
- Resolved React closure issues using ref pattern for event handlers
- Removed requestAnimationFrame wrapper for zero-delay updates
- Labels now positioned on left side only for cleaner interface

### Enhanced News System (Aug 26, 2025)
- Hybrid CNBC + Yahoo Finance integration
- Expandable inline news (no modals)
- Smart symbol relevance filtering
- Scrollable container with smooth animations