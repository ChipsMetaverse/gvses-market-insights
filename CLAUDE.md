# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚀 VIBE CODING WORKFLOW - ACTIVE

### Automatic MCP Server Usage Pattern
When working on this project, proactively use the following MCP servers:

1. **LINEAR** - Create issues for all bugs/features automatically
2. **PERPLEXITY** - Research best practices before implementing
3. **CONTEXT7** - Get latest docs before using any library
4. **SEMGREP** - Scan every code change for security
5. **PLAYWRIGHT** - Generate tests for all new code
6. **GITHUB** - Create PRs with semantic commits
7. **MEMORY** - Store and recall all solutions
8. **SENTRY** - Monitor errors, analyze issues, and use Seer for automated fixes

### Workflow Triggers
- **Bug mentioned** → Create Linear issue → Research → Fix → Test → PR
- **Feature requested** → Linear issue → Docs → Implement → Scan → Test → PR
- **Question asked** → Check Memory → Research → Store answer
- **Code written** → Semgrep scan → Generate tests → Update Linear
- **Production error** → Check Sentry → Use Seer to analyze → Implement fix

### Always Active Rules
- ✅ Run Semgrep after ANY code change
- ✅ Check Context7 before using new libraries
- ✅ Store solutions in Memory
- ✅ Update Linear issue status as work progresses
- ✅ Generate Playwright tests for UI components
- ✅ Use Sentry MCP to investigate production errors

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

### Mobile UX (Dec 17, 2025)
Mobile-optimized trading experience with two-tab navigation system:

**Mobile Breakpoint**: `1024px` - switches to mobile layout below this width

**Two-Tab Navigation System**:
- **Analysis Tab**: Economic Calendar, Pattern Detection (168 patterns), News Feed - TSLA
- **Chart + Voice Tab**: Interactive TradingView chart with timeframe controls, technical levels, AI assistant

**Panel Visibility Logic**:
- Uses `data-active` attributes to show/hide panels based on `activePanel` state
- Parent `main-content` visible for both 'chart' and 'analysis' tabs
- Chart section hidden when Analysis tab active via `data-active={!isMobile || activePanel === 'chart'}`
- Analysis panel shows full-height when active: `flex: 1; max-height: none;`

**Touch Gesture Support**:
- Swipe detection for tab navigation (40px threshold)
- Touch start/end event handlers
- Tab bar ref for gesture area detection

**Mobile State Management**:
- `isMobile`: boolean (window.innerWidth <= 1024)
- `activePanel`: 'analysis' | 'chart' | 'voice'
- `mobileChartRatio`: localStorage-persisted (20-70% range, default 35%)

**CSS Mobile Controls** (`TradingDashboardSimple.css:1386-1407`):
```css
@media (max-width: 1024px) {
  .chart-section[data-active="false"],
  .analysis-panel-below[data-active="false"] {
    display: none;
  }

  .analysis-panel-below[data-active="true"] {
    flex: 1;
    max-height: none;
  }
}
```

**Optional Enhancement Opportunities** (for future polish):
1. **Technical Levels Display**: Currently horizontal bar with small text
   - Consider: Vertical stack or 2-column grid for better mobile readability
   - Touch targets: Increase to minimum 44x44px for iOS guidelines

2. **Timeframe Buttons**: Currently 3 rows taking vertical space
   - Consider: Horizontal scrollable row or compact dropdown selector

3. **Economic Calendar**: Always expanded by default
   - Consider: Collapsed by default on mobile to reduce scroll depth

4. **News Feed**: Shows all articles at once
   - Consider: "Load More" pagination for better performance

5. **Pattern Detection**: 168 patterns detected
   - Consider: Mobile-optimized pattern cards with larger touch targets
   - Show fewer patterns initially with "Show More" expansion

**Mobile Performance**:
- Same data fetching as desktop (no mobile-specific API calls)
- React lazy loading for chart components
- LocalStorage for user preferences persistence
- Touch-optimized input fields (16px font to prevent iOS zoom)

### MCP Servers
- **market-mcp-server** (`market-mcp-server/`): Node.js, 35+ Yahoo Finance and CNBC tools
- **alpaca-mcp-server** (`alpaca-mcp-server/`): Python, Alpaca Markets API integration
- **forex-mcp-server** (`forex-mcp-server/`): Python + FastMCP + Playwright, ForexFactory economic calendar scraping
- **sentry-mcp-server**: Remote hosted, OAuth-enabled error monitoring with Seer AI agent for automated debugging

### Error Monitoring (Nov 11, 2025)
- **Sentry Integration**: Comprehensive error tracking and performance monitoring
  - **Frontend**: `@sentry/react` with browser tracing and session replay
  - **Backend**: `sentry-sdk` with FastAPI integration and logging
  - **Configuration**: `frontend/src/config/sentry.ts` and `backend/config/sentry.py`
  - **Seer AI Agent**: Automated root cause analysis and fix recommendations via Sentry MCP
  - **Documentation**: See `SENTRY_INTEGRATION.md` for complete setup guide
- **Usage**: Set `VITE_SENTRY_DSN` and `SENTRY_DSN` environment variables to enable
- **MCP Commands**:
  - "Check Sentry for errors in TradingChart.tsx"
  - "Use Sentry's Seer to analyze issue FRONTEND-123"
  - "Tell me about recent errors in gvses-backend"

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
# Run validation/unit tests (Vitest)
npx vitest frontend/src/utils/__tests__/chartCommandUtils.test.ts
```

### Market MCP Server
```bash
cd market-mcp-server && npm install

# HTTP Mode (Required for historical data service)
node index.js 3001     # HTTP mode on port 3001

# STDIO Mode (Legacy)
npm start              # Production mode (STDIO)
npm run dev            # Development with watch (STDIO)

# Testing
npm test               # Run tests
```

**Important**: For the 3-tier historical data caching to work, the market MCP server **must** run in HTTP mode on port 3001. The `HistoricalDataService` connects via HTTP to fetch decades of Yahoo Finance data.

### Forex MCP Server
```bash
cd forex-mcp-server && pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002

# Testing
python test_server.py    # Standalone server test
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

### Forex Economic Calendar (Nov 10, 2025)
- `GET /api/forex/calendar?time_period=today&impact=high` - Economic calendar events
- `GET /api/forex/events-today` - Today's forex events (convenience endpoint)
- `GET /api/forex/events-week` - This week's forex events (convenience endpoint)
- **Parameters**: time_period (today|tomorrow|this_week|next_week|custom), start, end, impact (high|medium|low)
- **Data Source**: ForexFactory via forex-mcp-server (Playwright scraping)
- **Events**: NFP, CPI, Fed meetings, GDP, unemployment, retail sales, etc.

### MCP Integration (Oct 11, 2025)
- `POST /api/mcp` - **NEW**: HTTP MCP endpoint for OpenAI Agent Builder integration
- `POST /mcp/http` - Alternative HTTP MCP endpoint
- `WS /mcp` - WebSocket MCP endpoint for real-time streaming
- `GET /mcp/status` - MCP transport status and active sessions

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
- `test_forex_mcp.py` - Forex MCP integration testing
- `forex-mcp-server/test_server.py` - Forex MCP standalone server test
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

### Working with Forex Economic Calendar
1. **Start Forex MCP Server**: `cd forex-mcp-server && python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002`
2. **Test Standalone**: `cd forex-mcp-server && python test_server.py`
3. **Test Integration**: `cd backend && python test_forex_mcp.py`
4. **Frontend Display**: Economic calendar appears in TradingDashboard with filters
5. **API Testing**: `curl "http://localhost:8000/api/forex/calendar?time_period=today&impact=high"`
6. **View Logs**: Check `/var/log/app/forex-mcp-server.err.log` in Docker
7. **Scraping Configuration**: Edit `forex-mcp-server/src/forex_mcp/settings.py` for timeout/URL adjustments

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

### Database-Backed Historical Data & Yearly Aggregation (Dec 20, 2025)
- **3-Tier Caching Architecture**: Professional-grade historical data management inspired by TradingView/Webull
  - **L1: Redis** (2ms) - Hot cache for last 30 days, popular symbols
  - **L2: Supabase** (20ms) - Persistent storage with unlimited history (currently: 188 monthly TSLA bars from 2010-2025)
  - **L3: Yahoo Finance via MCP** (300-5000ms) - Fetch missing data only, supports decades of history
- **Yearly Aggregation**: Monthly bars → Yearly candles (12 months → 1 year)
  - Jan open, Dec close, year's high/low, sum volume
  - TSLA: ~15 yearly candles (2010-2025) instead of 3
  - AAPL: ~45 yearly candles (1980-2025) when requested
- **Extended Market MCP Server** (`market-mcp-server/index.js:853-875`)
  - Added absolute date range support (`start_date`, `end_date` parameters)
  - Bypasses Yahoo Finance 5-year API limit for historical data
  - Can request 50+ years of data in single call
- **Smart Gap Filling**: Automatically detects missing data ranges and fetches only gaps
  - Reduces API calls by 99% after initial load
  - Pre-2020 data: Routes to Yahoo Finance MCP (Alpaca IEX feed limits ~5 years)
  - Post-2020 data: Uses Alpaca for recent bars
- **Implementation Files**:
  - `backend/services/historical_data_service.py`: 3-tier cache orchestration
  - `backend/services/bar_aggregator.py`: Monthly → yearly aggregation logic
  - `backend/supabase_migrations/004_historical_data_tables.sql`: Database schema
  - `market-mcp-server/index.js`: Extended with absolute date ranges
  - `frontend/src/components/TradingDashboardSimple.tsx:150`: Fetch 50 years for 1Y interval
- **Performance Benefits**:
  - First request: 4-8s (fetches decades from Yahoo Finance, stores in Supabase)
  - Subsequent requests: <200ms (served from Supabase L2 cache)
  - Sub-second responses for cached symbols
- **Storage Efficiency**: ~50 bytes per bar, 188 bars × 50 bytes = ~9.4KB per symbol
- **All 10 Intervals Working**: 1m, 5m, 15m, 1H, 1D, 1W, 1M, 1Y, YTD, MAX (9/10 return data, 1W has Alpaca API limitation)

### BTD (200-Day SMA) Display on All Timeframes (Dec 14, 2025)
- **Timeframe-Agnostic BTD**: BTD (200-day SMA) now displays on ALL timeframes, including intraday (1m, 5m, 15m, 30m, 1H, 2H, 4H)
- **Daily Data Integration**: Backend fetches 365 days of daily candles for BTD calculation on all timeframes
- **Consistent Reference Level**: BTD displays at same value across all timeframes (e.g., $368.34 for TSLA)
- **Implementation**:
  - `backend/mcp_server.py` (lines 1649-1717): Extended daily data fetch to 365 days for all timeframes
  - `backend/pattern_detection.py`: Updated to accept `daily_candles_for_btd` parameter
  - Uses daily candles specifically for BTD calculation while using chart candles for BL/SH
- **Why This Matters**: The 200-day SMA is a critical support/resistance level that traders reference regardless of current timeframe
- **Verified Timeframes**: 1m, 5m, 15m, 1H, 1Y all display BTD correctly at consistent value
- **Files Modified**: `mcp_server.py`, `pattern_detection.py`, `key_levels.py` (calculation logic)

### Forex Factory MCP Integration (Nov 10, 2025)
- **Economic Calendar Data**: New forex-mcp-server provides NFP, CPI, Fed meetings, GDP, unemployment data
- **ForexFactory Scraping**: Playwright-based scraper for real-time economic event data
- **FastMCP Framework**: Modern Python MCP server with HTTP transport on port 3002
- **Backend Integration**: Complete forex_mcp_client with HTTPMCPClient pattern
- **API Endpoints**: `/api/forex/calendar`, `/api/forex/events-today`, `/api/forex/events-week`
- **Frontend Display**: Economic calendar panel in TradingDashboard with impact filtering
- **Test Coverage**: Standalone and integration tests (test_forex_mcp.py, forex-mcp-server/test_server.py)
- **Docker Integration**: Supervisord manages forex-mcp-server with auto-restart
- **Documentation**: Complete integration guide in FOREX_MCP_INTEGRATION_COMPLETE.md

### Structured Chart Payload Rollout (Nov 9, 2025)
- Phase 1 migration complete: backend now emits `chart_objects` (ChartCommandPayloadV2) alongside legacy strings.
- Frontend normalizers validate payloads with Zod before execution; fall back to legacy safely.
- Feature flags documented in `FEATURE_FLAGS.md`; staged rollout plan lives in `PHASE_1_ROLLOUT_PLAN.md`.
- New backend integration coverage: `backend/tests/test_dual_mode_integration.py` verifies hybrid vs. structured-first behavior.
- Run frontend validation tests with `npx vitest frontend/src/utils/__tests__/chartCommandUtils.test.ts`.

### HTTP MCP Integration for OpenAI Agent Builder (Oct 11, 2025)
- **HTTP MCP Endpoint**: New `POST /api/mcp` endpoint for OpenAI Agent Builder integration
- **Dual Transport Architecture**: Both WebSocket (`/mcp`) and HTTP (`/api/mcp`) access to MCP tools
- **JSON-RPC 2.0 Compliant**: Full standards compliance for maximum compatibility
- **35+ Market Data Tools**: Access to comprehensive market analysis via HTTP
- **Authentication Support**: Bearer token and query parameter authentication methods
- **Agent Builder Ready**: Direct integration with OpenAI Agent Builder interface
- **Test Suite**: Comprehensive testing with `test_mcp_http_endpoint.py` and `test_mcp_dual_transport.py`
- **Documentation**: Complete integration guide in `MCP_HTTP_INTEGRATION.md`

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

## Voice Relay Configuration

### Enterprise Voice Session Management (Jan 10, 2025)
The voice relay server now implements enterprise-grade session management with:

#### Session Limits & Control
- **Concurrent Session Limits**: Configurable max concurrent voice sessions (default: 10)
- **Session Rejection**: Graceful rejection with proper error messages when at capacity
- **Thread-Safe Locking**: Prevents race conditions in session creation/deletion

#### Timeout Management
- **Session Timeout**: Sessions auto-expire after configured time (default: 300s)
- **Activity Timeout**: Idle sessions cleaned up after inactivity (default: 60s)
- **Background Cleanup**: Automatic cleanup task runs periodically (default: every 60s)

#### Configuration Variables
Add these optional environment variables to `backend/.env`:
```bash
MAX_CONCURRENT_SESSIONS=10     # Max concurrent voice sessions
SESSION_TIMEOUT_SECONDS=300     # Session lifetime (5 minutes)
ACTIVITY_TIMEOUT_SECONDS=60     # Inactivity timeout (1 minute)  
CLEANUP_INTERVAL_SECONDS=60     # Cleanup frequency
```

#### Monitoring & Metrics
The `/health` endpoint now provides comprehensive voice metrics:
- Active session count and utilization
- Sessions created, closed, rejected, timed out
- TTS requests and failures
- Error counts and uptime
- Real-time session status

#### Architecture Changes
- **Removed Deprecated Service**: OpenAIRealtimeService is deprecated and no longer initialized
- **Relay-Only Architecture**: All voice flows through OpenAIRealtimeRelay for better control
- **Unified Session Management**: Single source of truth for all voice sessions
- **Graceful Shutdown**: Proper cleanup of all sessions on server shutdown

#### Testing
Voice relay session management tests available:
```bash
cd backend
python3 test_voice_relay_simple.py    # Quick functional test
python3 test_voice_relay_sessions.py  # Comprehensive test suite
```

These improvements ensure reliable voice sessions at scale with proper resource management and observability.