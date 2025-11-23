# GVSES Market Insights - Application Summary

**Generated**: November 13, 2025, 5:25 AM
**Purpose**: Comprehensive discovery document for external research and agent orchestration

---

## Executive Summary

**Application**: GVSES AI Market Analysis Assistant
**Status**: Production (deployed to Fly.io)
**Primary Value**: Professional trading dashboard with voice-enabled AI market insights, combining real-time data visualization, technical analysis, and conversational market intelligence.

---

## Fast-Track Discovery (20 Core Questions)

### 1. Problem & Users
**One-sentence problem**: Day traders and market analysts need instant access to real-time market data, technical analysis, and AI-powered insights without switching between multiple tools.

**Target Users**:
- Day traders needing real-time price action and technical indicators
- Market analysts conducting research across multiple symbols
- Retail investors learning technical analysis

### 2. Launch Timeline & Priorities
**Current State**: Live in production (https://gvses-market-insights.fly.dev/)
**Must-Have Now**:
- ✅ Real-time market data (Alpaca Markets primary, Yahoo Finance fallback)
- ✅ TradingView Lightweight Charts with technical indicators
- ✅ ElevenLabs voice assistant integration
- ✅ Dynamic watchlist with symbol search
- ✅ CNBC + Yahoo Finance news feed
- ✅ Chart control function calling (just deployed)

**Can Wait**:
- Automated testing (E2E)
- User authentication/accounts
- Portfolio tracking
- Price alerts
- Mobile app

### 3. Top 3 Personas

**Persona 1: Active Day Trader**
- Primary tasks: Monitor real-time prices, identify entry/exit points, check news catalysts
- Frequency: 50+ trades/day, 6-8 hours screen time
- Pain points: Needs multiple monitors, slow news discovery, manual chart setup

**Persona 2: Technical Analyst**
- Primary tasks: Multi-timeframe analysis, pattern recognition, indicator signals
- Frequency: Deep analysis on 10-20 symbols/day
- Pain points: Repetitive chart configuration, indicator switching, data context switching

**Persona 3: Retail Investor/Learner**
- Primary tasks: Research companies, understand market movements, learn technical analysis
- Frequency: 1-2 hours/day, educational focus
- Pain points: Information overload, unclear data interpretation, expensive tools

### 4. Must-Have Modules (Next Release)
- [x] Real-time price quotes and historical candlestick data
- [x] Interactive TradingView charts with pan/zoom
- [x] Technical indicators (SMA, EMA, Bollinger Bands, RSI, MACD)
- [x] Dynamic watchlist with add/remove symbols
- [x] Symbol search with company name resolution
- [x] Market news feed (CNBC + Yahoo Finance)
- [x] Voice assistant for market queries
- [x] Chart control function calling and widget support
- [ ] Chart command polling integration (frontend implementation)
- [ ] Economic calendar (ForexFactory data available via MCP)
- [ ] Price alert notifications (optional)

### 5. Authentication & Authorization
**Current**: No authentication system
**User Sessions**: LocalStorage for watchlist preferences only
**Roles**: Single-user application (no RBAC)
**Future Needs**:
- Supabase Auth (already configured in env)
- User profiles and watchlist persistence
- API rate limiting per user
- Premium features gating

### 6. Multi-Tenant / Enterprise
**Current**: Single-tenant, public application
**Data Isolation**: None (stateless except localStorage)
**Future Considerations**:
- User accounts with personal watchlists
- Team collaboration features
- Enterprise SSO (not planned)

### 7. Core Entities & Relationships

```
User (future)
  └─> Watchlist (1:N)
       └─> Symbol (N:N)

StockQuote
  - symbol: string (PK)
  - price: float
  - change: float
  - volume: int
  - timestamp: datetime
  - data_source: alpaca|yahoo_mcp

HistoricalData
  - symbol: string
  - timestamp: datetime (PK)
  - open/high/low/close: float
  - volume: int
  - timeframe: 1m|5m|15m|1h|1d

NewsArticle
  - id: string
  - title: string
  - summary: text
  - source: cnbc|yahoo
  - url: string
  - published_at: datetime
  - related_symbols: [string]

ChartCommand (transient)
  - type: change_symbol|set_timeframe|toggle_indicator
  - payload: json
  - timestamp: datetime
  - executed: boolean

VoiceSession (ElevenLabs)
  - session_id: string
  - conversation_id: string
  - signed_url: string (temp)
  - expires_at: datetime
```

### 8. Sensitive Data & Retention
**PII**: None currently (no user accounts)
**Financial Data**: Public market data only (no personal trading data)
**API Keys**:
- Alpaca Markets API key (secret)
- Anthropic API key (secret)
- ElevenLabs API key + Agent ID (secret)
- Supabase keys (configured but unused)

**Encryption**:
- In transit: HTTPS/TLS (Fly.io + nginx)
- At rest: N/A (no persistent user data)
- Field-level: Not implemented

**Retention**:
- Market data: Not stored (real-time only)
- Logs: 7 days (Fly.io default)
- User sessions: Browser localStorage (no expiry)

### 9. Current Stack (Fully Defined)

**Frontend**:
- React 18 + TypeScript
- Vite (build/dev server)
- TradingView Lightweight Charts v5
- CSS Modules
- LocalStorage for state persistence
- Hosting: Fly.io (nginx serves static files)

**Backend**:
- FastAPI (Python 3.11)
- Uvicorn ASGI server
- Supervisor (process manager)
- Nginx (reverse proxy)
- Node.js 22 (for MCP servers)

**Data Sources**:
- Alpaca Markets API (primary market data)
- Yahoo Finance via MCP (fallback)
- CNBC via MCP (news)
- ForexFactory via MCP (economic calendar)

**AI/Voice**:
- Anthropic Claude (Sonnet 3.5)
- ElevenLabs Conversational AI
- OpenAI Agent Builder (in progress)

**Infrastructure**:
- Hosting: Fly.io (Docker)
- CDN: Fly.io edge
- Secrets: Fly.io secrets
- No database (stateless)

**Decided Stack Items**: Everything ✅

### 10. External Integrations

**Production Integrations**:

1. **Alpaca Markets** (Primary Data)
   - Stock quotes: 300-400ms latency
   - Historical bars: 400-500ms latency
   - Symbol search: Asset database
   - Rate limits: Unknown (no issues yet)
   - Fallback: Yahoo Finance via MCP

2. **Yahoo Finance** (MCP Fallback)
   - Stock quotes: 3-15s latency
   - Historical data: Full history available
   - Rate limits: Handled by MCP server
   - Reliability: Good (but slow)

3. **CNBC** (News Source)
   - Top stories: 3-5s latency
   - Market movers: Pre-market data
   - Rate limits: None observed
   - Requires: Node.js 22 (undici compatibility)

4. **ElevenLabs** (Voice AI)
   - Conversational AI agent
   - WebSocket signed URL generation
   - Timeout: 10 minutes per session
   - Rate limits: Per API key

5. **Anthropic Claude** (Text Fallback)
   - Model: claude-3-sonnet-20240229
   - Text-only `/ask` endpoint
   - Fallback when voice unavailable

6. **ForexFactory** (Economic Calendar)
   - Playwright scraping via MCP
   - NFP, CPI, Fed meetings, GDP data
   - Rate limits: Respectful scraping

**Integration Patterns**:
- Idempotency: Not implemented (stateless operations)
- Retries: Basic (Alpaca → Yahoo fallback)
- Circuit breakers: None
- Webhook verification: N/A (no webhooks)

### 11. Performance Expectations

**Current Targets** (implicit):
- Stock quotes: < 500ms (Alpaca primary)
- Historical data: < 500ms (Alpaca primary)
- News feed: < 5s (acceptable for non-critical)
- Chart rendering: < 100ms (client-side)
- Symbol search: < 500ms (300ms debounced)

**Measured Performance**:
- Alpaca quotes: 300-400ms ✅
- Alpaca history: 400-500ms ✅
- Yahoo MCP fallback: 3-15s (acceptable)
- News (CNBC + Yahoo): 3-5s ✅
- Frontend bundle: ~2MB (needs optimization)

**Availability**:
- Target: 99.5% (single Fly.io instance)
- No SLA (free/hobby project)
- No health monitoring/alerting

**Performance Monitoring**: None (should add)

### 12. Accessibility & Browser Support

**Accessibility Target**: None formally defined
**Current Support**:
- Keyboard navigation: Partial (form inputs only)
- Screen readers: Not tested
- Color contrast: Unknown
- Focus indicators: Default browser

**Browser Support**:
- Chrome/Edge: Primary (tested)
- Firefox: Likely works
- Safari: Unknown
- Mobile browsers: Not optimized

**Should Target**: WCAG 2.1 AA for financial app accessibility

### 13. Real-Time & Offline Features

**Real-Time Capabilities**:
- Voice conversations: WebSocket (ElevenLabs)
- Chart updates: Polling (not implemented yet)
- Stock quotes: On-demand (manual refresh)
- No live price streaming currently

**Offline/PWA**:
- PWA: Not configured
- Service worker: None
- Offline mode: Not supported
- Cache strategy: Browser default

**Future Considerations**:
- WebSocket for live quotes
- Server-Sent Events for news updates
- PWA for mobile offline access

### 14. Search Needs

**Current Search Implementation**:
- **Symbol Search**:
  - Alpaca Markets asset database
  - Company name → ticker resolution
  - 300ms debounced input
  - Real-time dropdown suggestions
  - Format validation (1-5 letters for stocks, XXX-USD for crypto)

**Search Filters**: None (simple string matching)
**Permissions**: N/A (public data)
**Ranking**: Alpaca's default (likely by market cap)

**Future Enhancements**:
- Search news by keyword
- Filter by sector/industry
- Historical symbol lookup

### 15. Notifications

**Current**: None implemented

**Future Needs**:
- Email: Price alerts, daily summary
- Push: Price target reached, breaking news
- SMS: Critical alerts only (premium feature)
- In-app: News notifications, technical signals

**User Preferences**: Not implemented
**Quiet Hours**: Not implemented
**Compliance**: CAN-SPAM (for email)

### 16. Pricing Model

**Current**: Free, no monetization
**No Billing System**

**Future Considerations**:
- Freemium model
- Basic: Free (limited symbols, ads)
- Pro: $9.99/month (unlimited symbols, alerts, priority data)
- Enterprise: Custom pricing (teams, API access)

**Trial**: Not applicable
**Billing**: Would use Stripe if implemented

### 17. Analytics & North-Star Metrics

**Current Analytics**: None implemented

**Must-Answer Questions Post-Launch**:
1. Daily active users (DAU)
2. Average session duration
3. Symbols per user per session
4. Voice assistant usage rate
5. News article click-through rate
6. Chart interaction patterns (zoom, indicators)
7. Symbol search → add to watchlist conversion
8. Time spent per symbol
9. Peak usage hours
10. Feature adoption (voice vs manual)

**Tool Recommendations**:
- Product analytics: PostHog or Mixpanel
- Performance: Sentry or DataDog
- Business metrics: Custom dashboard

### 18. Environments & Release Flow

**Current Environments**:
- **Local**: `localhost:5174` (frontend) + `localhost:8000` (backend)
- **Production**: `https://gvses-market-insights.fly.dev/`
- **No Staging**: Deploy directly to production

**CI/CD**:
- None automated
- Manual `fly deploy` from local machine
- Docker build via Depot

**Release Flow**:
1. Develop locally
2. Test manually
3. `git commit` with semantic message
4. `fly deploy` (3-5 minutes)
5. Verify in production
6. No rollback strategy (redeploy previous commit)

**Feature Flags**: Not implemented
**Canary Deploys**: Not supported
**Blue-Green**: Not configured

**Should Implement**:
- GitHub Actions for CI
- Staging environment on Fly.io
- Automated tests before deploy
- Feature flags for gradual rollout

### 19. QA Gates & Sign-Off

**Current QA Process**: Manual testing only

**Before "Done" (informal)**:
- ✅ Feature works in local dev
- ✅ No console errors
- ✅ Deployment succeeds
- ⚠️ No automated tests
- ⚠️ No performance benchmarks
- ⚠️ No accessibility checks
- ⚠️ No security scans

**Sign-Off Owner**: Developer (no formal QA team)

**Should Implement**:
- Unit tests (Vitest for frontend, pytest for backend)
- E2E tests (Playwright)
- Performance budgets (Lighthouse CI)
- Security scans (Snyk, Dependabot)
- Accessibility audit (axe DevTools)

### 20. Risks & Blockers

**Current Risks**:

1. **Single Point of Failure**
   - One Fly.io instance (no redundancy)
   - No load balancer
   - No auto-scaling
   - Mitigation: Add second instance, health checks

2. **API Rate Limits**
   - Alpaca Markets: Unknown limits
   - Yahoo Finance: Could be rate-limited
   - ElevenLabs: Per-key limits
   - Mitigation: Implement caching, request throttling

3. **Node.js Version Dependency**
   - MCP servers require Node.js 22
   - Undici compatibility issues
   - Already fixed in production (Docker uses Node 22)

4. **No Authentication**
   - Anyone can access the app
   - No user data protection (currently not needed)
   - No API abuse prevention
   - Future blocker for premium features

5. **Data Source Reliability**
   - Alpaca-first with Yahoo fallback works
   - But Yahoo is 10x slower
   - News requires CNBC scraping (fragile)

6. **Frontend Bundle Size**
   - ~2MB (TradingView Lightweight Charts is heavy)
   - Slow initial load on mobile
   - Should implement code splitting

7. **Legal/Compliance**
   - No terms of service
   - No privacy policy
   - Market data disclaimers needed
   - Not suitable for production without legal review

---

## Deep Dive Sections

### Architecture Deep Dive

**System Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                         Browser                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  React App   │  │  TradingView │  │ ElevenLabs   │     │
│  │  (Vite)      │  │   Charts     │  │   Voice      │     │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘     │
│         │                                     │              │
└─────────┼─────────────────────────────────────┼─────────────┘
          │                                     │
          │ HTTPS                               │ WebSocket
          │                                     │
┌─────────▼─────────────────────────────────────▼─────────────┐
│                    Fly.io (nginx)                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Backend (uvicorn)                           │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │  Endpoints                                     │  │  │
│  │  │  - /api/stock-price                           │  │  │
│  │  │  - /api/stock-history                         │  │  │
│  │  │  - /api/stock-news                            │  │  │
│  │  │  - /api/symbol-search                         │  │  │
│  │  │  - /api/functions (NEW)                       │  │  │
│  │  │  - /api/function-call (NEW)                   │  │  │
│  │  │  - /api/widget-action (NEW)                   │  │  │
│  │  │  - /elevenlabs/signed-url                     │  │  │
│  │  │  - /ask (Claude text fallback)                │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  │  ┌───────────────────────────────────────────────┐  │  │
│  │  │  Service Layer                                 │  │  │
│  │  │  - MarketServiceWrapper (Alpaca + MCP)        │  │  │
│  │  │  - ChartFunctionRegistry (NEW)                │  │  │
│  │  │  - VoiceRelayService                          │  │  │
│  │  └───────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Servers (Node.js 22)                           │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │  │
│  │  │   Market    │  │   Alpaca    │  │    Forex    │ │  │
│  │  │   (Yahoo)   │  │  (Primary)  │  │ (Economic)  │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                          │
                          │ External APIs
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                  │
    ┌───▼────┐       ┌───▼────┐       ┌────▼────┐
    │ Alpaca │       │ Claude │       │ElevenLbs│
    │Markets │       │  API   │       │  Voice  │
    └────────┘       └────────┘       └─────────┘
```

**Data Flow Examples**:

1. **Real-Time Quote Request**:
   ```
   User clicks symbol → Frontend /api/stock-price
   → MarketServiceWrapper tries Alpaca (300ms)
   → If fails, fallback to Yahoo MCP (3-15s)
   → Return with data_source field
   → Frontend updates UI
   ```

2. **Voice Command**:
   ```
   User speaks → ElevenLabs WebSocket
   → Agent processes intent
   → Agent calls /api/function-call
   → ChartFunctionRegistry executes function
   → Returns chart command
   → Frontend polls (not implemented yet)
   → Chart updates
   ```

3. **Widget Button Click**:
   ```
   User clicks TSLA button → /api/widget-action
   → Maps action to function (chart.setSymbol → change_chart_symbol)
   → ChartFunctionRegistry executes
   → Returns success + chart command
   → Frontend applies command immediately
   ```

**Deployment Architecture**:
```
Developer Machine
  └─> git commit
      └─> fly deploy (manual)
          └─> Depot (Docker build)
              └─> Fly.io Registry
                  └─> Fly.io Machine (single instance)
                      ├─> Nginx (port 80/443)
                      ├─> Supervisor
                      │   ├─> FastAPI (port 8000)
                      │   ├─> Market MCP (port 3001)
                      │   ├─> Alpaca MCP (subprocess)
                      │   └─> Forex MCP (port 3002)
                      └─> Playwright (headless Chromium)
```

### Data Model Detailed

**No Persistent Database**: Application is stateless

**Transient Data Structures**:

```python
# backend/models/chart_command.py
class ChartCommand(BaseModel):
    type: str  # change_symbol|set_timeframe|toggle_indicator|highlight_pattern
    payload: Dict[str, Any]
    description: Optional[str]
    legacy: Optional[str]  # For backward compatibility
```

```python
# backend/services/function_registry.py
class FunctionDefinition:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema
    handler: Callable  # Async function
```

**Frontend State** (React):
```typescript
// frontend/src/contexts/MarketDataContext.tsx
interface MarketDataContextType {
  watchlist: string[];  // Symbol array
  addSymbol: (symbol: string) => Promise<void>;
  removeSymbol: (symbol: string) => void;
  currentSymbol: string;
  setCurrentSymbol: (symbol: string) => void;
}

// Persisted to localStorage
const WATCHLIST_KEY = 'marketWatchlist';
```

**API Response Formats**:
```typescript
// Stock Quote
interface StockQuote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  timestamp: string;
  data_source: 'alpaca' | 'yahoo_mcp';
}

// Historical Data
interface CandlestickData {
  time: number;  // Unix timestamp
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
}

// News Article
interface NewsArticle {
  title: string;
  summary: string;
  url: string;
  source: 'cnbc' | 'yahoo';
  published_at: string;
  thumbnail?: string;
}
```

### Security Posture

**Current Security Measures**:
- ✅ HTTPS/TLS (Fly.io default)
- ✅ API keys in environment variables (Fly.io secrets)
- ✅ No SQL injection risk (no database)
- ✅ CORS configured (frontend origin only)
- ⚠️ No rate limiting (exposed to abuse)
- ⚠️ No input sanitization (could be XSS vector)
- ⚠️ No CSRF protection (no state to modify)
- ⚠️ No authentication (public app)

**Threat Model** (not formally documented):
- **Threat**: API abuse (repeated calls to expensive endpoints)
  - Impact: High cloud costs, service degradation
  - Mitigation: Implement rate limiting (10 req/min per IP)

- **Threat**: XSS via user input (symbol search)
  - Impact: Low (no sensitive data to steal)
  - Mitigation: React's built-in XSS protection (uses textContent)

- **Threat**: API key exposure in frontend
  - Impact: None (all keys server-side)
  - Mitigation: N/A (already secure)

- **Threat**: DDoS attack
  - Impact: Service unavailable
  - Mitigation: Fly.io DDoS protection, add rate limiting

**Security Roadmap**:
1. Implement rate limiting (Redis-based)
2. Add request validation (Pydantic strict mode)
3. Security headers (CSP, X-Frame-Options, etc.)
4. Dependency scanning (Dependabot, Snyk)
5. Regular penetration testing (not planned)

### Observability & Operations

**Current Monitoring**: Minimal

**Logs**:
- Location: Fly.io logs (stdout/stderr)
- Retention: 7 days
- Format: Plain text (should be JSON)
- Access: `fly logs --app gvses-market-insights`
- No log aggregation

**Metrics**: None
- Should track: Request count, latency, error rate
- Tools to consider: Prometheus + Grafana, DataDog

**Traces**: None
- Should implement: OpenTelemetry for distributed tracing

**Error Tracking**: None
- Should use: Sentry or Rollbar

**Health Checks**:
- Endpoint: `/health` (returns service mode and status)
- Fly.io health check: HTTP GET / every 30s
- Grace period: 2 minutes (should be 1 minute)

**Alerting**: None
- Should alert on:
  - HTTP 5xx rate > 1%
  - Response time p95 > 2s
  - Memory usage > 80%
  - Deployment failures

**Incident Response**: No formal process
- Should define: On-call rotation, escalation, postmortems

### Testing Strategy

**Current Testing**: Minimal

**Unit Tests**:
- Frontend: None (should use Vitest)
- Backend: None (should use pytest)

**Integration Tests**:
- Manual testing with curl commands
- Example: `test_server.py`, `test_dual_mcp.py`, `test_alpaca_mcp.py`
- Not automated in CI

**E2E Tests**: None
- Should use: Playwright (already installed for forex scraping)
- Critical flows to test:
  - Symbol search → add to watchlist
  - Chart symbol change
  - News feed loading
  - Voice assistant connection

**Performance Tests**: None
- Should measure: Time to first quote, chart render time
- Tools: Lighthouse CI, k6

**Accessibility Tests**: None
- Should use: axe DevTools, WAVE

**Security Tests**: None
- Should implement: OWASP ZAP, dependency scanning

**Test Data**:
- Uses live market data (not ideal for testing)
- Should create: Mock data fixtures for reliable tests

### Compliance & Legal

**Current State**: No formal compliance

**Required Before Production**:
1. **Terms of Service**
   - User obligations
   - Disclaimer of financial advice
   - Limitation of liability
   - Acceptable use policy

2. **Privacy Policy**
   - Data collection (currently none)
   - Cookie policy
   - Third-party integrations (Alpaca, ElevenLabs, Claude)
   - User rights (GDPR/CCPA)

3. **Market Data Disclaimers**
   - "Data provided by Alpaca Markets"
   - "Not real-time" (if using delayed data)
   - "For informational purposes only"
   - "Not financial advice"

4. **Accessibility Statement**
   - WCAG compliance level
   - Known issues
   - Contact for assistance

**Regulatory Considerations**:
- Not a broker-dealer (no trading execution)
- Not providing investment advice (general market data)
- SEC compliance: Likely not required (check with lawyer)
- FINRA: Not applicable (not a financial services firm)

**Data Residency**:
- Fly.io region: US (default)
- No GDPR data export controls needed (public data only)

### Capacity & Cost

**Current Capacity**:
- Single Fly.io machine
- CPU: Shared (unknown specs)
- RAM: 256MB (likely, check with `fly scale show`)
- No auto-scaling
- No load balancer

**Traffic Model** (estimated):
- Current: < 10 users/day
- Target: 100 users/day
- Peak: Market open (9:30 AM ET)
- Request pattern: Bursty (user clicks, not streaming)

**Cost Breakdown** (monthly):
- Fly.io: $5-10/month (hobby plan)
- Alpaca Markets: Free (paper trading account)
- Yahoo Finance: Free (via MCP)
- ElevenLabs: $X/month (usage-based)
- Anthropic Claude: $X/month (usage-based)
- Total: ~$50-100/month (estimated)

**Scaling Considerations**:
- Add Redis cache for quotes (reduce API calls)
- Implement CDN for static assets (already on Fly.io edge)
- Add second Fly.io instance (geo-redundancy)
- Consider WebSocket connection pooling for voice

### Technical Debt & Improvements

**High Priority**:
1. **Chart Command Polling** (frontend not implemented)
   - Backend returns commands, frontend doesn't poll yet
   - Blocks: Voice commands → chart updates
   - Effort: 2 hours

2. **Rate Limiting** (API abuse prevention)
   - No limits on expensive endpoints
   - Risk: High cloud costs
   - Effort: 4 hours (Redis + middleware)

3. **Error Handling** (inconsistent across app)
   - Some endpoints return 500, others 404
   - Poor user feedback on errors
   - Effort: 8 hours (standardize error responses)

4. **Automated Tests** (zero coverage)
   - No confidence in changes
   - Manual testing is time-consuming
   - Effort: 16 hours (critical path coverage)

**Medium Priority**:
5. **Performance Optimization**
   - Frontend bundle size (2MB)
   - Code splitting for TradingView
   - Effort: 4 hours

6. **Accessibility** (WCAG 2.1 AA)
   - Keyboard navigation incomplete
   - Screen reader support missing
   - Effort: 16 hours

7. **Authentication** (Supabase integration)
   - Env vars configured but not used
   - Needed for user accounts
   - Effort: 8 hours

8. **Staging Environment**
   - Test before production deploy
   - Effort: 2 hours (Fly.io clone)

**Low Priority**:
9. **Mobile Optimization**
   - Responsive design incomplete
   - Touch gestures for charts
   - Effort: 16 hours

10. **Analytics Integration**
    - Track user behavior
    - PostHog or Mixpanel
    - Effort: 4 hours

---

## Technical Specifications

### API Endpoints Reference

**Market Data Endpoints**:
```
GET  /api/stock-price?symbol=TSLA
  Response: StockQuote (300-500ms with Alpaca)

GET  /api/stock-history?symbol=TSLA&days=100
  Response: CandlestickData[] (300-500ms)

GET  /api/stock-news?symbol=TSLA
  Response: NewsArticle[] (3-5s, hybrid CNBC + Yahoo)

GET  /api/comprehensive-stock-data?symbol=TSLA
  Response: { quote, history, news } (5-10s)

GET  /api/symbol-search?query=microsoft&limit=10
  Response: { results: Symbol[] } (< 500ms via Alpaca)

GET  /api/market-overview
  Response: { indices, movers } (via MCP)
```

**Function Calling Endpoints** (NEW):
```
GET  /api/functions
  Response: { functions: ToolDefinition[], schemas: {} }

POST /api/function-call
  Body: { name: string, arguments: {} }
  Response: { success: boolean, results: [] }

POST /api/widget-action
  Body: { action: { type, payload }, itemId? }
  Response: { success: boolean, message, data }

POST /api/chat-widget
  Body: { query: string }
  Response: { widget: JSON } | { message }
```

**Voice & AI Endpoints**:
```
GET  /elevenlabs/signed-url
  Response: { signed_url: string }

POST /ask
  Body: { query: string }
  Response: { answer: string }

WS   /ws/quotes?symbol=TSLA
  Streams: Real-time quote updates (not implemented)
```

**Economic Calendar** (Forex MCP):
```
GET  /api/forex/calendar?time_period=today&impact=high
  Response: ForexEvent[]

GET  /api/forex/events-today
  Response: ForexEvent[]

GET  /api/forex/events-week
  Response: ForexEvent[]
```

**Health & Status**:
```
GET  /health
  Response: { service_mode: "alpaca_primary", status: "healthy" }

GET  /mcp/status
  Response: { transports: [], sessions: [] }
```

### Environment Variables

**Required (Production)**:
```bash
# AI/Voice
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
ELEVENLABS_AGENT_ID=...

# Database (configured but unused)
SUPABASE_URL=https://....supabase.co
SUPABASE_ANON_KEY=eyJhbGci...

# Market Data
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Server
PORT=8080  # Nginx listens here
```

**Optional**:
```bash
MODEL=claude-3-sonnet-20240229
MAX_CONCURRENT_SESSIONS=10
SESSION_TIMEOUT_SECONDS=300
ACTIVITY_TIMEOUT_SECONDS=60
```

**Frontend** (`.env`, `.env.development`):
```bash
VITE_SUPABASE_URL=https://....supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_API_URL=http://localhost:8000  # Dev only
```

### Docker Configuration

**Dockerfile Highlights**:
- Base: `python:3.11-slim`
- Node.js 22 installed (for MCP servers)
- Playwright Chromium (for ForexFactory scraping)
- Multi-stage build (frontend in Node.js 22, backend in Python)
- Supervisor for process management
- Nginx for reverse proxy

**Build Process**:
1. Frontend: Vite build → `/usr/share/nginx/html/`
2. Backend: Copy Python code → `/app/backend/`
3. MCP servers: npm install → `/app/market-mcp-server/`
4. Install dependencies: pip + playwright
5. Cleanup: Remove build tools (gcc, g++, curl)

**Runtime**:
- Supervisor starts:
  - Nginx (port 80)
  - FastAPI (uvicorn on port 8000)
  - Market MCP server (port 3001)
  - Forex MCP server (port 3002)
- Logs to `/var/log/app/*.log`

### Git Repository Structure

```
claude-voice-mcp/
├── backend/
│   ├── mcp_server.py              # Main FastAPI app
│   ├── config/
│   │   └── rate_limits.py         # Rate limiting config
│   ├── middleware/
│   │   └── rate_limiter.py        # Rate limiting middleware
│   ├── models/
│   │   └── chart_command.py       # ChartCommand model
│   ├── services/
│   │   ├── agent_orchestrator.py  # Multi-agent coordination
│   │   ├── chart_image_analyzer.py # Chart analysis
│   │   ├── function_registry.py   # Function calling (NEW)
│   │   ├── market_service_factory.py # Data source routing
│   │   └── mcp_websocket_transport.py # MCP WebSocket
│   ├── widgets/
│   │   └── chart_controls.json    # ChatKit widget (NEW)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TradingChart.tsx   # Main chart component
│   │   │   └── TradingDashboardSimple.tsx # Dashboard layout
│   │   ├── contexts/
│   │   │   └── MarketDataContext.tsx # Watchlist state
│   │   ├── services/
│   │   │   ├── marketDataService.ts # API client
│   │   │   ├── chartControlService.ts # Voice commands
│   │   │   └── enhancedChartControl.ts # Chart manipulation
│   │   └── utils/
│   │       └── __tests__/
│   │           └── chartCommandUtils.test.ts # Unit tests
│   ├── package.json
│   └── vite.config.ts
├── market-mcp-server/           # Yahoo Finance MCP (Node.js 22)
│   ├── src/
│   │   └── index.ts
│   └── package.json
├── alpaca-mcp-server/           # Alpaca Markets MCP (Python)
│   └── server.py
├── forex-mcp-server/            # ForexFactory MCP (Python + Playwright)
│   ├── src/
│   │   └── forex_mcp/
│   │       └── server.py
│   └── requirements.txt
├── elevenlabs/                  # Voice agent config
│   └── convai.json
├── Dockerfile
├── docker-compose.yml
├── fly.toml                     # Fly.io deployment config
├── nginx.conf
├── supervisord.conf
├── CLAUDE.md                    # Project instructions
└── README.md
```

---

## Roadmap & Next Steps

### Immediate (This Week)
1. ✅ Function calling implementation (DONE)
2. [ ] Chart command polling (frontend)
3. [ ] Rate limiting middleware
4. [ ] Error handling standardization

### Short Term (2 Weeks)
5. [ ] Automated testing (Vitest + Playwright)
6. [ ] Staging environment
7. [ ] Performance monitoring (Sentry)
8. [ ] Legal pages (Terms, Privacy)

### Medium Term (1 Month)
9. [ ] User authentication (Supabase)
10. [ ] Persistent watchlists
11. [ ] Price alert notifications
12. [ ] Mobile responsive design

### Long Term (3 Months)
13. [ ] Premium features & billing
14. [ ] Portfolio tracking
15. [ ] Advanced technical analysis
16. [ ] Mobile app (React Native)

---

## Contact & Access

**Repository**: Private (location not specified)
**Production**: https://gvses-market-insights.fly.dev/
**Deployment**: Fly.io (manual via `fly deploy`)

**Key Personnel**:
- Developer: User (GitHub username unknown)
- Product Owner: N/A
- Design: N/A (developer-designed)

**Access Needed for External Research**:
- [x] Codebase (you have access)
- [ ] Fly.io dashboard (read-only)
- [ ] API key usage metrics (Alpaca, ElevenLabs, Claude)
- [ ] Analytics (not implemented)
- [ ] Error logs (Fly.io logs)

---

## Conclusion

GVSES Market Insights is a **production-ready MVP** with solid technical foundations but **minimal operational maturity**. The application successfully delivers real-time market data with AI-powered voice interactions, but lacks critical production infrastructure (monitoring, testing, auth, legal).

**Strengths**:
- ✅ Clean architecture (hybrid Alpaca + MCP)
- ✅ Modern stack (React/TypeScript, FastAPI, Docker)
- ✅ Performance (sub-second quotes via Alpaca)
- ✅ Innovative features (voice AI, function calling)
- ✅ Recently deployed function calling system

**Critical Gaps**:
- ⚠️ No automated tests
- ⚠️ No user authentication
- ⚠️ No monitoring/alerting
- ⚠️ No legal pages
- ⚠️ Single point of failure (one Fly.io instance)

**Recommended Priority**:
Focus on operational excellence (testing, monitoring, legal) before adding features. The core product is solid; make it reliable and compliant.

---

**Document Version**: 1.0
**Last Updated**: November 13, 2025, 5:25 AM
**Next Review**: After chart command polling implementation
