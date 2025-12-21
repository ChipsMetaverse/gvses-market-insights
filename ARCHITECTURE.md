# GVSES System Architecture

## Overview

GVSES is a professional stock market analysis system integrating OpenAI Agent Builder, custom widgets, and real-time market data via MCP (Model Context Protocol) servers. The system provides intelligent routing between a specialized widget interface for single-ticker queries and a general conversational agent for broader market analysis.

## Current Version: v44 (Production)

**Release Date**: 2025-11-27  
**Major Change**: Fixed Common Expression Language (CEL) syntax error in workflow routing logic

## System Components

### 1. OpenAI Agent Builder Workflow

The core workflow orchestrates user interactions and routes them to appropriate handlers:

```
User Input → Transform → Intent Classifier → If/Else Decision → Agent Handler
```

#### Workflow Nodes

1. **Start**: Initial user input capture
2. **Transform**: Pre-processes user input
3. **Intent Classifier Agent**: Categorizes user intent (market_data, chart_command, general)
4. **If/Else Decision**: Routes based on query type
5. **GVSES Widget Agent**: Handles single-ticker stock queries
6. **General G'sves Agent**: Handles general market queries

### 2. Routing Logic (v44)

The if/else condition determines which agent handles the query:

**Condition (CEL Syntax):**
```javascript
(input.intent == "market_data" || input.intent == "chart_command") 
&& input.symbol 
&& input.symbol.length > 0 
&& !input.symbol.contains(',') 
&& !input.symbol.contains(' ')
```

**Logic Breakdown:**
- Must be market_data OR chart_command intent
- Must have a symbol field
- Symbol must not be empty
- Symbol must NOT contain commas (no "AAPL,TSLA")
- Symbol must NOT contain spaces (no "AAPL TSLA")

**Example Routes:**

| Query | Symbol | Route | Reason |
|-------|--------|-------|--------|
| "show me AAPL" | AAPL | Widget | Single ticker |
| "analyze Tesla" | TSLA | Widget | Single ticker |
| "scan the market" | null | General | No symbol |
| "AAPL, TSLA" | AAPL, TSLA | General | Multiple tickers (comma) |
| "AAPL TSLA" | AAPL TSLA | General | Multiple tickers (space) |

### 3. GVSES Widget Agent

**Purpose**: Generate comprehensive stock analysis with visual widgets

**MCP Tools Used:**
1. `get_stock_quote(symbol)` - Real-time price and stats
2. `get_stock_history(symbol, period, interval)` - Historical chart data
3. `get_market_news(symbol)` - Recent news articles
4. `get_earnings_calendar()` - Upcoming earnings events

**Response Format**: JSON with 15 required fields

#### Required JSON Schema

The widget REQUIRES all 15 fields to be present or it will fail silently:

```json
{
  "1. company": "Apple Inc",
  "2. symbol": "AAPL",
  "3. analysis": "Technical analysis text...",
  "4. timestamp": "Updated Nov 27, 2025 10:30 PM ET",
  "5. price": {
    "current": "$150.25",
    "changeLabel": "+2.50 (1.69%)",
    "changeColor": "success"
  },
  "6. timeframes": ["1D", "5D", "1M", "3M", "6M", "1Y", "YTD", "MAX"],
  "7. selectedTimeframe": "1D",
  "8. chartData": [
    {"date": "2025-11-20", "Close": 148.90},
    {"date": "2025-11-21", "Close": 149.50}
  ],
  "9. stats": {
    "open": "$149.80",
    "volume": "45.2M",
    "marketCap": "$2.35T",
    "dayLow": "$149.20",
    "yearLow": "$124.17",
    "eps": "$6.42",
    "dayHigh": "$150.50",
    "yearHigh": "$199.62",
    "peRatio": "23.4"
  },
  "10. technical": {
    "position": "Bullish",
    "color": "success",
    "levels": {
      "sh": "$155.00",
      "bl": "$152.00",
      "now": "$150.25",
      "btd": "$145.00"
    }
  },
  "11. patterns": [],
  "12. newsFilters": [
    {"value": "all", "label": "All"},
    {"value": "company", "label": "Company"}
  ],
  "13. selectedSource": "all",
  "14. news": [
    {
      "id": "n1",
      "headline": "Apple announces Q4 results",
      "source": "Reuters",
      "timeAgo": "2h",
      "color": "blue-400",
      "url": "https://reuters.com/article/12345"
    }
  ],
  "15. events": []
}
```

**⚠️ Critical**: Field #15 (`events`) is the most commonly forgotten field and must be included even if empty.

### 4. Widget Template & Chart Component

**File**: `GVSES-stock-card---with-analysis-v27-FIXED.widget`

**Chart Component Properties (Valid Only):**
```json
{
  "type": "Chart",
  "height": "160",
  "width": "100%",
  "data": "{{ (chartData) | tojson }}",
  "series": [{
    "type": "line",
    "dataKey": "Close",
    "label": "Close Price",
    "color": "blue"
  }],
  "xAxis": {"dataKey": "date"},
  "showYAxis": true
}
```

**Invalid Properties (Removed in v27):**
- `size`, `flex`, `minHeight`, `maxHeight`, `minWidth`, `maxWidth`, `minSize`, `maxSize`, `aspectRatio`

These caused component errors and were removed.

### 5. MCP Server Architecture

**market-mcp-server** (Node.js 22)
- Location: `market-mcp-server/`
- Port: 3001
- Tools: 35+ Yahoo Finance and CNBC tools
- APIs: Yahoo Finance, CNBC
- **Critical**: Requires Node.js 22+ for undici compatibility

**alpaca-mcp-server** (Python)
- Location: `alpaca-mcp-server/`
- Tools: Alpaca Markets API integration
- Data: Professional-grade market data

**forex-mcp-server** (Python + Playwright)
- Location: `forex-mcp-server/`
- Port: 3002
- Tools: ForexFactory economic calendar scraping
- Data: NFP, CPI, Fed meetings, GDP, unemployment

### 6. Data Flow

```
User Query
    ↓
OpenAI Agent Builder
    ↓
Intent Classifier
    ↓
If/Else Router (v44 CEL Logic)
    ↓
GVSES Widget Agent  OR  General G'sves Agent
    ↓                       ↓
MCP Tool Calls          MCP Tool Calls
    ↓                       ↓
market-mcp-server      market-mcp-server
alpaca-mcp-server      alpaca-mcp-server
    ↓                       ↓
Format 15-Field JSON   Text Response
    ↓
Widget Validation
    ↓
Render Chart + UI
```

## Version History

### v44 (Current - 2025-11-27)
**Changes:**
- Fixed CEL syntax error in if/else condition
- Replaced JavaScript regex `/[,\s]+/` with CEL string methods
- Used `!input.symbol.contains(',')` and `!input.symbol.contains(' ')`
- Successfully deployed to production

**Impact:**
- Workflow now properly validates single vs. multiple ticker symbols
- No more parsing errors in Agent Builder
- Improved routing accuracy

### v43 (Deprecated - 2025-11-26)
**Changes:**
- Attempted to use JavaScript regex in CEL condition
- Error: "Expecting token of type --> CloseParenthesis <-- but found --> '/' <--"

**Issue:**
- OpenAI Agent Builder uses CEL, not JavaScript
- Regex literals not supported in CEL

### v27 (Widget Fix)
**Changes:**
- Removed invalid Chart component properties
- Fixed silent widget rendering failures
- Cleaned up Chart configuration

### Earlier Versions
- v1-v26: Various iterations of agent instructions and widget improvements
- Progressive refinement of JSON schema requirements
- Addition of events field requirement

## Technical Constraints

### Common Expression Language (CEL)
- OpenAI Agent Builder uses CEL, NOT JavaScript
- No regex literals (no `/pattern/`)
- Use string methods: `contains()`, `startsWith()`, `endsWith()`
- Logical operators: `&&`, `||`, `!`
- Comparison: `==`, `!=`, `>`, `<`, `>=`, `<=`

### Widget Validation
- **Silent Failures**: Missing fields cause no error messages
- **All-or-Nothing**: All 15 fields required for rendering
- **Type Matching**: Field types must match schema exactly
- **Empty Arrays**: Use `[]` not `null` for empty arrays

### Chart Component
- Only use officially documented properties
- Invalid properties cause component errors
- Height/width must be strings with units
- Data must be valid JSON via Jinja2 filter

## Development Guidelines

### Adding New Features

1. **Update mermaid.md**: Add new flow diagrams
2. **Update ARCHITECTURE.md**: Document changes
3. **Test CEL Syntax**: Verify in Agent Builder before deploying
4. **Validate JSON Schema**: Ensure all 15 fields present
5. **Test Both Routes**: Single ticker AND general queries

### Common Pitfalls

❌ **Don't:**
- Use JavaScript regex in CEL conditions
- Omit the `events` field from JSON response
- Use invalid Chart component properties
- Return `null` for empty arrays
- Test only in Draft mode (test production too)

✅ **Do:**
- Use CEL string methods (`contains`, `startsWith`)
- Always include all 15 required fields
- Use only documented Chart properties
- Use empty arrays `[]` for optional data
- Test thoroughly before publishing

### Debugging Checklist

**Widget Not Rendering:**
1. Check all 15 fields are present in JSON
2. Verify `events` field is included (even if empty)
3. Check Chart component properties are valid
4. Validate JSON syntax via online validator
5. Review browser console for errors

**Wrong Agent Triggered:**
1. Check if/else condition syntax
2. Verify symbol extraction from user input
3. Test with multiple query variations
4. Review Intent Classifier output
5. Check for commas/spaces in symbol field

**CEL Syntax Errors:**
1. Verify no JavaScript-specific syntax
2. Check for proper CEL operators
3. Validate string method usage
4. Test condition in Agent Builder UI
5. Review CEL documentation

## File Locations

```
claude-voice-mcp/
├── mermaid.md                              # System diagrams (this file's companion)
├── ARCHITECTURE.md                         # System architecture (this file)
├── .playwright-mcp/
│   ├── GVSES-agent-instructions-COMPLETE.md   # Full agent instructions
│   ├── GVSES-agent-system-prompt.md           # Concise agent prompt
│   ├── PASTE-THIS-INTO-AGENT-BUILDER.md       # Copy-paste ready instructions
│   ├── GVSES-stock-card---with-analysis-v27-FIXED.widget  # Widget template
│   ├── WIDGET_NOT_RENDERING_FIX.md            # Root cause analysis
│   └── AGENT_FIX_INSTRUCTIONS.md              # Fix guide
├── market-mcp-server/                      # Yahoo Finance MCP server
├── alpaca-mcp-server/                      # Alpaca Markets MCP server
└── forex-mcp-server/                       # Forex calendar MCP server
```

## API Endpoints (Not Currently Used)

Note: The current architecture uses OpenAI Agent Builder with MCP servers, not direct API endpoints. The FastAPI backend exists but is not integrated with the Agent Builder workflow.

**Available but Unused:**
- `GET /api/stock-price?symbol=TSLA`
- `GET /api/stock-history?symbol=TSLA&days=100`
- `GET /api/stock-news?symbol=TSLA`
- `GET /api/comprehensive-stock-data?symbol=TSLA`

## Security & Performance

### Security Considerations
- MCP servers run on localhost only
- No direct user access to MCP endpoints
- OpenAI Agent Builder handles authentication
- API keys managed via environment variables

### Performance Metrics
- **Alpaca Quote**: 300-400ms
- **Alpaca History**: 400-500ms
- **MCP News**: 3-5s (CNBC + Yahoo hybrid)
- **Widget Render**: < 1s after data received

## Future Enhancements

### Planned
- Integrate FastAPI backend with Agent Builder
- Add real-time quote streaming
- Implement caching layer for market data
- Enhanced error messages for widget failures

### Under Consideration
- Multi-symbol comparison widgets
- Portfolio tracking integration
- Technical indicator overlays on charts
- Historical pattern recognition

---

**Last Updated**: 2025-11-27  
**Current Version**: v44 (Production)  
**System Status**: Operational  
**Critical Issues**: None
