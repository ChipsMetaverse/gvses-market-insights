# Frontend-Backend Query Flow Mapping

## System Architecture
- **Frontend**: React app on http://localhost:5174
- **Backend**: FastAPI on http://localhost:8000
- **ML System**: Phase 5 enabled and model loaded

## Query Flow Patterns

### 1. Automatic Polling (Every 10-15 seconds)
The frontend automatically refreshes market data for the watchlist:

```
Frontend Component          →  Backend API                    →  Response
─────────────────────────────────────────────────────────────────────────
Market Insights Panel       →  GET /api/stock-price?symbol=TSLA  →  Price data
Market Insights Panel       →  GET /api/stock-price?symbol=AAPL  →  Price data  
Market Insights Panel       →  GET /api/stock-price?symbol=NVDA  →  Price data
Market Insights Panel       →  GET /api/stock-price?symbol=SPY   →  Price data
Market Insights Panel       →  GET /api/stock-price?symbol=PLTR  →  Price data
Chart Analysis Panel        →  GET /api/technical-indicators     →  MA data
System Health Monitor       →  GET /health                       →  Status
```

### 2. User-Triggered Actions

#### Voice Commands (ElevenLabs Integration)
```
User speaks → Voice Assistant → WebSocket /ws/elevenlabs → Backend processes → AI response
                                                         ↓
                                                    Pattern detection
                                                         ↓
                                                    ML enhancement (Phase 5)
```

#### Chart Interactions
```
User selects symbol → TradingChart component → GET /api/stock-history → OHLCV data
                                             → GET /api/technical-indicators → Analysis
```

#### Pattern Detection Flow
```
1. User query about patterns
   ↓
2. Backend calls PatternDetector
   ↓
3. PatternStructuredAdapter converts to structured format
   ↓
4. PatternLifecycleManager processes pattern
   ↓
5. PatternConfidenceService (ML) enhances confidence
   ↓
6. Response returned with ML-enhanced confidence scores
```

## Current System Status

### Active Components
- ✅ Market data polling (5 symbols)
- ✅ Technical indicators (AAPL)
- ✅ Health monitoring
- ✅ ML model loaded (v1.0.0_20250928_131457)
- ⏳ Pattern detection (awaiting user trigger)
- ⏳ ML inference (0 predictions so far)

### Data Flow Metrics
- **Polling frequency**: ~10 second intervals
- **Symbols tracked**: TSLA, AAPL, NVDA, SPY, PLTR
- **API response time**: < 500ms average
- **ML latency**: Not yet measured (no inferences)

## ML Integration Points

### When ML Gets Triggered
1. **Pattern Detection**: When comprehensive stock data includes pattern analysis
2. **Voice Commands**: When user asks about patterns or technical analysis
3. **Manual Trigger**: Direct API call to `/api/comprehensive-stock-data?indicators=patterns`

### Why ML Hasn't Triggered Yet
- No patterns detected in current market data
- No user voice commands requesting pattern analysis
- Automatic polling only fetches prices, not patterns

## Testing ML Activation

To trigger ML pattern confidence:
```bash
# 1. Request comprehensive data with patterns
curl "http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns"

# 2. Use voice command (in browser)
"Show me patterns for Tesla"
"Analyze TSLA for trading patterns"

# 3. Monitor ML activity
tail -f backend/server.log | grep -i "ml\|confidence\|pattern"
```

## Frontend Components Map

```
TradingDashboardSimple.tsx
├── Market Insights Panel (Left)
│   ├── StockCard components
│   └── Auto-refresh timer
├── Interactive Charts (Center)
│   ├── TradingChart.tsx
│   └── TradingView integration
└── Chart Analysis Panel (Right)
    ├── News feed
    └── Technical analysis

VoiceAssistantElevenlabs.tsx
├── WebSocket connection
├── Audio streaming
└── Command processing
```

## Monitoring Commands

```bash
# Watch all API calls
tail -f backend/server.log | grep "HTTP/1.1"

# Watch ML activity only
tail -f backend/server.log | grep -i "ml\|pattern\|confidence"

# Watch errors
tail -f backend/server.log | grep -i "error\|warning"

# Check ML health
curl http://localhost:8000/api/ml/health

# Check ML metrics  
curl http://localhost:8000/api/ml/metrics
```

---
*Generated: Sep 28, 2025*
*Status: System operational, awaiting pattern detection to trigger ML*