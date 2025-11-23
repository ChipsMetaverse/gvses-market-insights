# GVSES Comprehensive Widget - Complete Implementation Guide

## Widget Overview

**File**: `chatkit-widgets/gvses-comprehensive-widget.json`

**Purpose**: All-in-one market analysis widget combining price, technical levels, patterns, news, and events in single conversational snapshot.

**Key Features**:
- ✅ Stock quote with timestamp
- ✅ Quick stats (open, volume, range)
- ✅ Technical levels (QE, ST, LTB) with position indicator
- ✅ Pattern detection (top 3 patterns with confidence)
- ✅ Market news (top 5 articles with source filtering)
- ✅ Upcoming events (earnings, Fed meetings, etc.)
- ✅ Interactive actions (refresh, source filter, open article)

---

## Complete Data Schema

### Required Widget Data Structure

```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc",
  "timestamp": "Nov 16, 2025 2:30 PM",

  "price": 272.41,
  "price_change": -0.65,
  "price_change_percent": -0.24,
  "price_change_color": "red",

  "open": 271.06,
  "volume": "47.4M",
  "day_low": 269.60,
  "day_high": 275.93,

  "qe_level": 280.00,
  "st_level": 275.00,
  "ltb_level": 265.00,
  "technical_position_label": "Between ST & LTB",
  "technical_position_color": "yellow",

  "patterns": [
    {
      "pattern_name": "Ascending Triangle",
      "pattern_confidence": "High",
      "pattern_direction": "Bullish",
      "pattern_confidence_color": "green-500"
    },
    {
      "pattern_name": "Higher Lows",
      "pattern_confidence": "Medium",
      "pattern_direction": "Bullish",
      "pattern_confidence_color": "yellow-500"
    }
  ],

  "news": [
    {
      "news_title": "Apple announces new product line",
      "news_source": "CNBC",
      "news_time_ago": "2h ago",
      "news_url": "https://www.cnbc.com/...",
      "news_source_color": "blue-500"
    },
    {
      "news_title": "Stock surges on revenue growth",
      "news_source": "Yahoo Finance",
      "news_time_ago": "4h ago",
      "news_url": "https://finance.yahoo.com/...",
      "news_source_color": "orange-400"
    }
  ],

  "news_filter_all_color": "info",
  "news_filter_all_variant": "solid",
  "news_filter_cnbc_color": "secondary",
  "news_filter_cnbc_variant": "outline",
  "news_filter_yahoo_color": "secondary",
  "news_filter_yahoo_variant": "outline",

  "events": [
    {
      "event_name": "Earnings Report",
      "event_date": "Nov 28",
      "event_countdown": "12 days",
      "event_impact_color": "red-500"
    },
    {
      "event_name": "Fed Meeting",
      "event_date": "Dec 15",
      "event_countdown": "29 days",
      "event_impact_color": "orange-400"
    }
  ]
}
```

---

## Backend Implementation

### Step 1: Create Comprehensive Analysis Service

**File**: `backend/services/comprehensive_analysis.py`

```python
import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ComprehensiveAnalysisService:
    """Aggregates data from multiple MCP tools into comprehensive widget"""

    def __init__(self, market_service):
        self.market_service = market_service

    async def get_comprehensive_analysis(self, symbol: str) -> Dict:
        """
        Fetch all data in parallel and combine into widget-compatible structure

        Returns complete widget data schema
        """
        try:
            # Parallel API calls for performance (5s instead of 15s)
            results = await asyncio.gather(
                self._get_quote_data(symbol),
                self._get_technical_data(symbol),
                self._get_pattern_data(symbol),
                self._get_news_data(symbol),
                self._get_events_data(symbol),
                return_exceptions=True
            )

            quote, technical, patterns, news, events = results

            # Handle partial failures gracefully
            if isinstance(quote, Exception):
                logger.error(f"Quote fetch failed: {quote}")
                quote = self._get_empty_quote()

            if isinstance(technical, Exception):
                logger.error(f"Technical fetch failed: {technical}")
                technical = self._get_empty_technical()

            if isinstance(patterns, Exception):
                logger.error(f"Patterns fetch failed: {patterns}")
                patterns = []

            if isinstance(news, Exception):
                logger.error(f"News fetch failed: {news}")
                news = []

            if isinstance(events, Exception):
                logger.error(f"Events fetch failed: {events}")
                events = []

            # Build complete widget data
            return self._build_widget_data(
                symbol=symbol,
                quote=quote,
                technical=technical,
                patterns=patterns,
                news=news,
                events=events
            )

        except Exception as e:
            logger.error(f"Comprehensive analysis error for {symbol}: {str(e)}")
            raise

    async def _get_quote_data(self, symbol: str) -> Dict:
        """Fetch real-time quote"""
        response = await self.market_service.get_stock_price(symbol)
        return response

    async def _get_technical_data(self, symbol: str) -> Dict:
        """Calculate technical levels (QE, ST, LTB)"""
        # TODO: Implement technical levels calculation
        # For now, use placeholder values
        history = await self.market_service.get_stock_history(symbol, days=100)

        # Calculate pivot points from historical data
        prices = [candle["close"] for candle in history]

        qe = max(prices) * 1.05  # 5% above recent high
        st = max(prices)  # Recent high
        ltb = min(prices)  # Recent low

        return {
            "qe": round(qe, 2),
            "st": round(st, 2),
            "ltb": round(ltb, 2)
        }

    async def _get_pattern_data(self, symbol: str) -> List[Dict]:
        """Detect chart patterns"""
        # TODO: Implement pattern detection algorithm
        # For now, return placeholder patterns
        return [
            {
                "name": "Ascending Triangle",
                "confidence": "high",
                "direction": "bullish"
            },
            {
                "name": "Higher Lows",
                "confidence": "medium",
                "direction": "bullish"
            }
        ]

    async def _get_news_data(self, symbol: str) -> List[Dict]:
        """Fetch market news"""
        response = await self.market_service.get_news(symbol)
        return response.get("news", [])[:5]  # Top 5 articles

    async def _get_events_data(self, symbol: str) -> List[Dict]:
        """Fetch upcoming economic events"""
        # TODO: Integrate with forex_mcp_client for economic calendar
        # For now, return placeholder events
        return [
            {
                "name": "Earnings Report",
                "date": "2025-11-28",
                "impact": "high"
            }
        ]

    def _build_widget_data(
        self,
        symbol: str,
        quote: Dict,
        technical: Dict,
        patterns: List[Dict],
        news: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """Transform raw data into widget-compatible structure"""

        current_price = quote.get("price", 0)
        price_change = quote.get("change", 0)
        price_change_percent = quote.get("changePercent", 0)

        # Determine price change color
        price_change_color = "green" if price_change >= 0 else "red"

        # Calculate technical position
        qe = technical.get("qe", 0)
        st = technical.get("st", 0)
        ltb = technical.get("ltb", 0)

        technical_position = self._calculate_position(current_price, qe, st, ltb)

        # Format patterns
        formatted_patterns = [
            {
                "pattern_name": p["name"],
                "pattern_confidence": p["confidence"].capitalize(),
                "pattern_direction": p["direction"].capitalize(),
                "pattern_confidence_color": self._get_confidence_color(p["confidence"])
            }
            for p in patterns[:3]  # Top 3
        ]

        # Format news
        formatted_news = [
            {
                "news_title": article.get("headline", ""),
                "news_source": article.get("source", ""),
                "news_time_ago": self._format_time_ago(article.get("publishedAt", "")),
                "news_url": article.get("url", ""),
                "news_source_color": self._get_source_color(article.get("source", ""))
            }
            for article in news[:5]  # Top 5
        ]

        # Format events
        formatted_events = [
            {
                "event_name": event.get("name", ""),
                "event_date": self._format_date(event.get("date", "")),
                "event_countdown": self._format_countdown(event.get("date", "")),
                "event_impact_color": self._get_impact_color(event.get("impact", ""))
            }
            for event in events[:2]  # Top 2
        ]

        # Build complete widget data
        return {
            "symbol": symbol,
            "company_name": quote.get("companyName", symbol),
            "timestamp": datetime.now().strftime("%b %d, %Y %I:%M %p"),

            # Price data
            "price": current_price,
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "price_change_color": price_change_color,

            # Quick stats
            "open": quote.get("open", 0),
            "volume": self._format_volume(quote.get("volume", 0)),
            "day_low": quote.get("low", 0),
            "day_high": quote.get("high", 0),

            # Technical levels
            "qe_level": qe,
            "st_level": st,
            "ltb_level": ltb,
            "technical_position_label": technical_position["label"],
            "technical_position_color": technical_position["color"],

            # Patterns
            "patterns": formatted_patterns,

            # News
            "news": formatted_news,
            "news_filter_all_color": "info",
            "news_filter_all_variant": "solid",
            "news_filter_cnbc_color": "secondary",
            "news_filter_cnbc_variant": "outline",
            "news_filter_yahoo_color": "secondary",
            "news_filter_yahoo_variant": "outline",

            # Events
            "events": formatted_events
        }

    def _calculate_position(self, price: float, qe: float, st: float, ltb: float) -> Dict:
        """Determine current price position relative to technical levels"""
        if price > qe:
            return {"label": "Above QE", "color": "green"}
        elif price > st:
            return {"label": "Between QE & ST", "color": "green"}
        elif price > ltb:
            return {"label": "Between ST & LTB", "color": "yellow"}
        else:
            return {"label": "Below LTB", "color": "red"}

    def _get_confidence_color(self, confidence: str) -> str:
        """Map pattern confidence to color"""
        colors = {
            "high": "green-500",
            "medium": "yellow-500",
            "low": "gray-400"
        }
        return colors.get(confidence.lower(), "gray-400")

    def _get_source_color(self, source: str) -> str:
        """Map news source to color"""
        if "cnbc" in source.lower():
            return "blue-500"
        elif "yahoo" in source.lower():
            return "orange-400"
        else:
            return "gray-500"

    def _get_impact_color(self, impact: str) -> str:
        """Map event impact to color"""
        colors = {
            "high": "red-500",
            "medium": "orange-400",
            "low": "gray-400"
        }
        return colors.get(impact.lower(), "gray-400")

    def _format_volume(self, volume: int) -> str:
        """Format volume (e.g., 47400000 -> 47.4M)"""
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return str(volume)

    def _format_time_ago(self, published_at: str) -> str:
        """Format timestamp as relative time (e.g., '2h ago')"""
        # TODO: Implement proper relative time calculation
        return "2h ago"  # Placeholder

    def _format_date(self, date_str: str) -> str:
        """Format date (e.g., '2025-11-28' -> 'Nov 28')"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date_obj.strftime("%b %d")
        except:
            return date_str

    def _format_countdown(self, date_str: str) -> str:
        """Format countdown (e.g., '12 days')"""
        try:
            date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            delta = (date_obj - datetime.now()).days
            return f"{delta} days" if delta > 0 else "today"
        except:
            return ""

    def _get_empty_quote(self) -> Dict:
        """Return empty quote structure"""
        return {
            "price": 0,
            "change": 0,
            "changePercent": 0,
            "open": 0,
            "volume": 0,
            "low": 0,
            "high": 0,
            "companyName": ""
        }

    def _get_empty_technical(self) -> Dict:
        """Return empty technical levels"""
        return {
            "qe": 0,
            "st": 0,
            "ltb": 0
        }
```

---

### Step 2: Add API Endpoint

**File**: `backend/mcp_server.py`

```python
from services.comprehensive_analysis import ComprehensiveAnalysisService

# Initialize service
comprehensive_service = ComprehensiveAnalysisService(market_service)

@app.get("/api/comprehensive-analysis")
async def get_comprehensive_analysis(symbol: str):
    """
    Get comprehensive market analysis including:
    - Real-time quote
    - Technical levels (QE, ST, LTB)
    - Chart patterns
    - Market news (top 5)
    - Upcoming events

    Returns widget-compatible JSON structure
    """
    try:
        logger.info(f"Fetching comprehensive analysis for {symbol}")

        analysis = await comprehensive_service.get_comprehensive_analysis(symbol)

        return JSONResponse(content=analysis)

    except Exception as e:
        logger.error(f"Comprehensive analysis error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

### Step 3: Test Backend Endpoint

**File**: `backend/test_comprehensive_analysis.py`

```python
import requests
import json

# Test comprehensive analysis endpoint
response = requests.get("http://localhost:8000/api/comprehensive-analysis?symbol=AAPL")

data = response.json()

print("=== Comprehensive Analysis Response ===\n")
print(f"Symbol: {data['symbol']}")
print(f"Company: {data['company_name']}")
print(f"Timestamp: {data['timestamp']}")
print(f"\nPrice: ${data['price']} ({data['price_change']:+.2f}, {data['price_change_percent']:+.2f}%)")
print(f"\nQuick Stats:")
print(f"  Open: ${data['open']}")
print(f"  Volume: {data['volume']}")
print(f"  Range: ${data['day_low']} - ${data['day_high']}")
print(f"\nTechnical Levels:")
print(f"  QE:  ${data['qe_level']}")
print(f"  ST:  ${data['st_level']}")
print(f"  LTB: ${data['ltb_level']}")
print(f"  Position: {data['technical_position_label']}")
print(f"\nPatterns ({len(data['patterns'])}):")
for pattern in data['patterns']:
    print(f"  - {pattern['pattern_name']} ({pattern['pattern_confidence']} confidence, {pattern['pattern_direction']})")
print(f"\nNews ({len(data['news'])}):")
for article in data['news']:
    print(f"  - {article['news_title'][:50]}... ({article['news_source']}, {article['news_time_ago']})")
print(f"\nEvents ({len(data['events'])}):")
for event in data['events']:
    print(f"  - {event['event_name']} - {event['event_date']} ({event['event_countdown']})")

print("\n=== Complete JSON ===\n")
print(json.dumps(data, indent=2))
```

---

## Agent Builder Configuration

### Step 1: Upload Widget

1. Navigate to https://platform.openai.com/agents
2. Open G'sves workflow
3. Click "Widgets" tab
4. Upload `gvses-comprehensive-widget.json`
5. Name: "GVSES Market Analysis"

### Step 2: Configure MCP Tool

1. Add "Tool Call" node
2. Select MCP Server: GVSES_Market_Data_Server
3. Add new tool: `get_comprehensive_analysis`
4. Parameter: `symbol` (from user query extraction)

### Step 3: Change Output Format

1. Select Output Node
2. Format: TEXT → WIDGET
3. Widget: "GVSES Market Analysis"
4. Data mapping: Direct passthrough from MCP tool response

### Step 4: Update Agent Prompt

```markdown
You are GVSES, a professional market analysis assistant.

When users ask about a stock, provide comprehensive analysis including:
- Real-time price and change
- Technical position (QE, ST, LTB levels)
- Chart pattern detection
- Latest market news
- Upcoming events

SYMBOL EXTRACTION:
- "Apple" / "AAPL" → AAPL
- "Tesla" / "TSLA" → TSLA
- "Microsoft" / "MSFT" → MSFT

WORKFLOW:
1. Extract ticker symbol from query
2. Call get_comprehensive_analysis MCP tool
3. Return result as WIDGET (not TEXT)

The widget will display all data in a single comprehensive card.
```

---

## Testing Strategy

### Test 1: Complete Widget Rendering
```
Query: "Analyze AAPL"

Expected Widget Sections:
✅ Header: Apple Inc (AAPL), timestamp
✅ Price: $XXX.XX with green/red change
✅ Quick Stats: Open, Volume, Range
✅ Technical: QE, ST, LTB levels with position badge
✅ Patterns: 1-3 patterns with confidence indicators
✅ News: 5 articles with CNBC/Yahoo color dots
✅ Events: 1-2 upcoming events with impact colors
✅ Actions: Refresh button, source filters
```

### Test 2: Historical Reference
```
User at 2:00 PM: "Analyze TSLA"
Widget shows: Price $250.00

User at 4:00 PM: Scrolls back to 2:00 PM message
Widget still shows: Price $250.00 (snapshot preserved)

Dashboard shows: Price $255.50 (current)
```

### Test 3: Multiple Symbols
```
Query: "Analyze AAPL"
[Widget 1: AAPL data]

Query: "Analyze TSLA"
[Widget 2: TSLA data]

Query: "Analyze MSFT"
[Widget 3: MSFT data]

Chat history: 3 widgets, easy to scan
```

---

## Implementation Timeline

### Phase 1: Widget Structure (2 hours) ✅
- ✅ Widget JSON created
- ✅ Data schema defined

### Phase 2: Backend Service (6 hours)
- [ ] Create ComprehensiveAnalysisService
- [ ] Implement parallel API calls
- [ ] Add data transformation logic
- [ ] Add API endpoint
- [ ] Test with curl/Postman

### Phase 3: Technical Levels (3 hours)
- [ ] Implement pivot point calculation
- [ ] Add support/resistance detection
- [ ] Test with historical data

### Phase 4: Pattern Detection (4 hours)
- [ ] Implement basic pattern algorithms
- [ ] Add ascending triangle detection
- [ ] Add head & shoulders detection
- [ ] Add higher lows/highs detection

### Phase 5: Agent Builder Config (2 hours)
- [ ] Upload widget
- [ ] Configure MCP tool
- [ ] Change output format to WIDGET
- [ ] Update agent prompt

### Phase 6: Testing (3 hours)
- [ ] Test with 10+ symbols
- [ ] Verify widget rendering
- [ ] Check historical snapshots
- [ ] Test partial failures

**Total: 20 hours**

---

## Success Criteria

✅ Widget renders visually (not JSON text)
✅ All 6 sections display correctly
✅ Price changes show correct colors
✅ Technical position badge displays
✅ Patterns list with confidence colors
✅ News articles with source color dots
✅ Events with impact colors
✅ Interactive actions work (refresh, filters, open URL)
✅ Historical snapshots preserved
✅ Chat history easy to scan
✅ Response time < 5 seconds (parallel API calls)

---

**Document Version**: 1.0
**Created**: November 16, 2025
**Status**: 🟢 Ready for Backend Implementation
**Next Action**: Implement ComprehensiveAnalysisService in backend
