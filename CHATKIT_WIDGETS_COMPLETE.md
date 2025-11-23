# ChatKit Widgets Design - COMPLETE ✅

**Date**: November 15, 2025
**Status**: All 5 widgets designed and exported
**Next Phase**: React implementation

## Widget Design Summary

### ✅ Widget 1: Economic Calendar
**Status**: Designed (needs simplification during implementation)
**Screenshot**: `.playwright-mcp/economic-calendar-widget-json.png`
**Key Features**:
- Period filters: Today, Tomorrow, This Week, Next Week
- Event list with time, currency, title, actual/forecast/previous values
- Refresh button with calendar.refresh action
- Last updated timestamp

**REQUIRED SIMPLIFICATION**:
- ❌ **Remove**: Impact filter buttons (All, High, Medium, Low)
- ❌ **Remove**: `selectedImpact` from schema
- ❌ **Remove**: `impactOptions` array from schema
- ✅ **Update**: Subtitle from "Filter by time & impact" to "High-impact events only"
- ✅ **Update**: Refresh action to always pass `impact: 'high'`
- ✅ **Keep**: Period filters (Today, Tomorrow, This Week, Next Week)

**Actions**:
- `calendar.refresh` - Refresh events with `{ period, impact: 'high' }`
- `calendar.setPeriod` - Change time period filter

---

### ✅ Widget 2: Market News Feed
**Status**: Complete
**Screenshot**: `.playwright-mcp/news-feed-widget-json.png`
**Key Features**:
- Symbol badge showing current ticker
- Source filters: All Sources, CNBC, Yahoo Finance
- News article cards with title, source, timestamp, snippet
- Refresh button
- Browser.openUrl action for article links

**Actions**:
- `news.refresh` - Refresh news feed
- `news.setSource` - Filter by news source (all/cnbc/yahoo)
- `browser.openUrl` - Open article in browser

---

### ✅ Widget 3: Technical Levels
**Status**: Complete
**Screenshot**: `.playwright-mcp/technical-levels-widget-json.png`
**Key Features**:
- 3 levels with color-coded indicators:
  - **Sell High** (🔴 Red) - Resistance level
  - **Buy Low** (🟢 Green) - Support level
  - **BTD** (🔵 Blue) - Buy The Dip level
- Price values displayed prominently
- Click to highlight level on chart

**Actions**:
- `levels.refresh` - Recalculate technical levels
- `chart.highlightLevel` - Highlight selected level on chart

---

### ✅ Widget 4: Pattern Detection
**Status**: Complete
**Screenshot**: `.playwright-mcp/pattern-detection-widget-json.png`
**Key Features**:
- "Show All Patterns" checkbox
- Category filter pills: Reversal, Continuation, Neutral
- Pattern cards showing:
  - Pattern name
  - Signal badge (BEARISH/BULLISH)
  - Category label
  - Confidence percentage
  - Progress bar for confidence
- Accent bar color coding per category

**Actions**:
- `patterns.refresh` - Recalculate pattern detection
- `patterns.toggleVisibility` - Show/hide pattern on chart
- `patterns.filterCategory` - Filter by pattern category

---

### ✅ Widget 5: Trading Chart Display
**Status**: Complete
**Screenshot**: `.playwright-mcp/trading-chart-display-widget-json.png`
**Key Features**:
- **Header**: Symbol badge, current price (color-coded), price change, fullscreen, close
- **Timeframe Controls**: 1D, 5D, 1M, 3M, 6M, 1Y, 5Y, All
- **Drawing Tools**: Trendline, Ray, Horizontal line, Clear All
- **Chart Types**: Candlestick, Line, Area
- **Chart Display Area**: 400px min height placeholder for TradingView Lightweight Charts
- **Technical Indicators**: Volume, SMA, EMA, RSI, MACD

**Actions**:
- `chart.setTimeframe` - Change timeframe (`{ value: '1D' }`)
- `chart.setType` - Change chart type (`{ value: 'candlestick' }`)
- `chart.activateDrawingTool` - Activate drawing tool (`{ value: 'trendline' }`)
- `chart.clearDrawings` - Clear all drawings
- `chart.toggleIndicator` - Toggle indicator (`{ name: 'volume' }`)
- `chart.fullscreen` - Expand to fullscreen
- `chart.close` - Close widget

---

## Widget Schema Examples

### Economic Calendar Schema (Simplified)
```json
{
  "title": "Economic Calendar",
  "subtitle": "ForexFactory events • High-impact only",
  "selectedPeriod": "today",
  "periodOptions": [
    { "label": "Today", "value": "today", "selected": true },
    { "label": "Tomorrow", "value": "tomorrow", "selected": false },
    { "label": "This Week", "value": "week", "selected": false },
    { "label": "Next Week", "value": "next-week", "selected": false }
  ],
  "events": [
    {
      "id": "evt-1",
      "time": "8:30 AM",
      "currency": "USD",
      "title": "Non-Farm Employment Change",
      "impact": "high",
      "actual": "180K",
      "forecast": "175K",
      "previous": "150K"
    }
  ],
  "lastUpdated": "Nov 15, 2025 09:10 ET",
  "impactLabel": "Impact: 🔴 High events only"
}
```

### Trading Chart Display Schema
```json
{
  "symbol": "TSLA",
  "currentPrice": 242.84,
  "priceChange": 12.5,
  "percentChange": 4.23,
  "isPositive": true,
  "timeframe": "1D",
  "chartType": "candlestick",
  "activeDrawingTool": null,
  "indicators": {
    "volume": true,
    "sma": false,
    "ema": false,
    "rsi": false,
    "macd": false
  }
}
```

---

## Implementation Checklist

### Phase 1: Widget Components (React + ChatKit)
- [ ] Create `EconomicCalendarWidget.tsx` (simplified - no impact filters)
- [ ] Create `MarketNewsFeedWidget.tsx`
- [ ] Create `TechnicalLevelsWidget.tsx`
- [ ] Create `PatternDetectionWidget.tsx`
- [ ] Create `TradingChartDisplayWidget.tsx`

### Phase 2: Widget Actions Integration
- [ ] Implement `calendar.refresh(period, impact='high')` handler
- [ ] Implement `calendar.setPeriod(value)` handler
- [ ] Implement `news.refresh()` handler
- [ ] Implement `news.setSource(source)` handler
- [ ] Implement `browser.openUrl(url)` handler
- [ ] Implement `levels.refresh()` handler
- [ ] Implement `chart.highlightLevel(level)` handler
- [ ] Implement `patterns.refresh()` handler
- [ ] Implement `patterns.toggleVisibility(patternId)` handler
- [ ] Implement `patterns.filterCategory(category)` handler
- [ ] Implement `chart.setTimeframe(value)` handler
- [ ] Implement `chart.setType(value)` handler
- [ ] Implement `chart.activateDrawingTool(value)` handler
- [ ] Implement `chart.clearDrawings()` handler
- [ ] Implement `chart.toggleIndicator(name)` handler
- [ ] Implement `chart.fullscreen()` handler
- [ ] Implement `chart.close()` handler

### Phase 3: Dashboard Redesign
- [ ] Update `TradingDashboardSimple.tsx`:
  - Remove left panel (analysis-panel-left)
  - Remove center chart panel
  - Expand `RealtimeChatKit` to full width
  - Add widget launcher UI
  - Implement modal overlay system for all 5 widgets

### Phase 4: Backend API Endpoints
- [ ] `/api/widget/economic-calendar/refresh` (always high-impact)
- [ ] `/api/widget/news-feed/refresh`
- [ ] `/api/widget/technical-levels`
- [ ] `/api/widget/patterns`
- [ ] `/api/widget/chart/data`

### Phase 5: State Management
- [ ] Create `useWidgetState` hook for modal management
- [ ] Create `useChartSync` hook for symbol/timeframe synchronization
- [ ] Implement widget action dispatcher
- [ ] Add widget persistence (localStorage)

### Phase 6: Testing
- [ ] Test each widget modal open/close
- [ ] Test widget action handlers
- [ ] Test chart highlighting from Technical Levels
- [ ] Test pattern visibility toggling
- [ ] Test drawing tool activation from widget
- [ ] Test timeframe/symbol synchronization
- [ ] Test mobile responsiveness
- [ ] Test keyboard shortcuts (Esc to close)

---

## Widget Action Types Reference

```typescript
// Economic Calendar Actions
type CalendarAction =
  | { type: 'calendar.refresh'; payload: { period: string; impact: 'high' } }
  | { type: 'calendar.setPeriod'; payload: { value: string } };

// Market News Actions
type NewsAction =
  | { type: 'news.refresh' }
  | { type: 'news.setSource'; payload: { value: string } }
  | { type: 'browser.openUrl'; payload: { url: string } };

// Technical Levels Actions
type LevelsAction =
  | { type: 'levels.refresh' }
  | { type: 'chart.highlightLevel'; payload: { level: string } };

// Pattern Detection Actions
type PatternAction =
  | { type: 'patterns.refresh' }
  | { type: 'patterns.toggleVisibility'; payload: { patternId: string } }
  | { type: 'patterns.filterCategory'; payload: { category: string } };

// Trading Chart Actions
type ChartAction =
  | { type: 'chart.setTimeframe'; payload: { value: string } }
  | { type: 'chart.setType'; payload: { value: string } }
  | { type: 'chart.activateDrawingTool'; payload: { value: string } }
  | { type: 'chart.clearDrawings' }
  | { type: 'chart.toggleIndicator'; payload: { name: string } }
  | { type: 'chart.fullscreen' }
  | { type: 'chart.close' };
```

---

## ChatKit Component Patterns Learned

### Layout Components
- `Card` - Container with padding and border
- `Col` - Vertical stack with gap
- `Row` - Horizontal layout with gap/align/justify
- `Box` - Generic container with background/border/radius
- `Spacer` - Flexible spacing element

### Content Components
- `Title` - Heading text (sm/md/lg/xl)
- `Text` - Body text with weight/color
- `Caption` - Small secondary text
- `Badge` - Pill-shaped label
- `Icon` - Icon from ChatKit icon library
- `Divider` - Horizontal/vertical separator

### Interactive Components
- `Button` - Click action with label/icon/variant/color
- `Checkbox` - Toggle with label
- `ListView` - Scrollable list container
- `ListViewItem` - List item with click action

### Color System
- `discovery` - Blue accent
- `info` - Primary blue
- `success` - Green
- `danger` - Red
- `warning` - Yellow
- `secondary` - Gray
- `tertiary` - Light gray

### Variants
- `solid` - Filled background
- `outline` - Border only
- `ghost` - Transparent background

---

## Success Metrics

✅ **All 5 widgets designed** using ChatKit Studio AI builder
✅ **All JSON configurations exported** with screenshots
✅ **Widget actions defined** for all interactions
✅ **Schema structures documented** for data flow
✅ **Economic Calendar simplification** documented (implementation-ready)
✅ **ChatKit component patterns** learned and cataloged

---

## Next Steps

1. **Mark simplification task complete** (design phase done, implementation phase next)
2. **Begin React implementation** of all 5 widgets
3. **Create widget action dispatcher** system
4. **Redesign TradingDashboardSimple** to ChatKit-first layout
5. **Implement modal overlay system** for widget launching
6. **Test full widget integration** with chart synchronization

---

**Design Phase Status**: ✅ **COMPLETE - READY FOR IMPLEMENTATION**
