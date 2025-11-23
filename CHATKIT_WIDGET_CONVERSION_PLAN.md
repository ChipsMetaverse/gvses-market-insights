# ChatKit Widget Conversion Plan

**Date**: November 15, 2025
**Goal**: Convert GVSES Trading Dashboard panels to ChatKit widgets
**Architecture**: ChatKit-first design with widgets replacing React components

---

## Current Architecture Analysis

### Current Layout (3-Panel Desktop)
```
┌─────────────────────────────────────────────────────────────────┐
│  LEFT PANEL          │  CENTER PANEL   │  RIGHT PANEL           │
│  (analysis-panel)    │  (chart)        │  (chatkit-container)   │
├──────────────────────┼─────────────────┼────────────────────────┤
│ • Chart Analysis     │ TradingChart    │ RealtimeChatKit        │
│ • News Feed          │ TimeSelector    │ (Voice Assistant)      │
│ • Technical Levels   │ Drawing Tools   │                        │
│ • Pattern Detection  │                 │                        │
│ • Economic Calendar  │                 │                        │
└──────────────────────┴─────────────────┴────────────────────────┘
```

### Components to Convert

#### 1. **Economic Calendar** (EconomicCalendar.tsx)
**Current Features**:
- ForexFactory event scraping
- Time period filters (Today, Tomorrow, This Week, Next Week)
- Impact filters (High, Medium, Low, All)
- Impact summary counts
- Event details with actual/forecast/previous values
- Refresh button
- Last updated timestamp

**Data Source**: `forexDataService.getCalendar()`
**API Endpoint**: `/api/forex/calendar`

**Widget Requirements**:
- Time period selector buttons
- Impact level selector buttons
- Event list with timeline grouping
- Refresh action
- Auto-refresh capability
- Impact color coding (🔴 High, 🟡 Medium, 🟢 Low)

#### 2. **News Feed** (Currently in TradingDashboardSimple.tsx)
**Current Features**:
- Need to identify in code (appears to be in left panel based on className)

**Data Source**: TBD (likely `marketDataService.getNews()`)
**API Endpoint**: `/api/stock-news`

**Widget Requirements**:
- Symbol-specific news filtering
- CNBC + Yahoo Finance hybrid feed
- Article cards with title, description, source
- External link buttons
- Auto-refresh on symbol change

#### 3. **Technical Levels** (Lines 2122-2156)
**Current Features**:
- Sell High Level (Resistance - QE label)
- Buy Low Level (Support - ST label)
- BTD Level (Buy The Dip - LTB label)
- Tooltips with explanations
- Loading/error states
- Dynamic updates on symbol/timeframe change

**Data Source**: `technicalLevels` state (API call TBD)
**API Endpoint**: TBD (likely `/api/technical-levels`)

**Widget Requirements**:
- Three level displays with labels
- Color-coded values (green for buy, red for sell)
- Tooltips for each level
- Chart integration (highlight levels on click)
- Auto-update on symbol change

#### 4. **Pattern Detection** (Lines 2158+)
**Current Features**:
- "Show All Patterns" master toggle
- Pattern categories (Reversal, Continuation, Neutral)
- Individual pattern visibility toggles
- Pattern cards with:
  - Pattern name
  - Signal (bullish/bearish/neutral)
  - Confidence level
  - Category badge
- Hover effects highlighting patterns on chart
- Click to toggle pattern visibility
- "Show More" expansion

**Data Source**: `backendPatterns` and `detectedPatterns` state
**API Endpoint**: TBD (pattern detection service)

**Widget Requirements**:
- Category filters
- Pattern list with cards
- Signal indicators
- Visibility toggles
- Chart highlighting on hover
- Chart pattern drawing on click
- Confidence scoring display

---

## Widget Specifications

### Widget 1: Economic Calendar Widget

**Schema** (`economic-calendar-widget.json`):
```json
{
  "title": "Economic Calendar",
  "subtitle": "Stay ahead of high-impact macro events",
  "selectedPeriod": "today",
  "selectedImpact": "high",
  "periods": [
    { "value": "today", "label": "Today" },
    { "value": "tomorrow", "label": "Tomorrow" },
    { "value": "week", "label": "This Week" },
    { "value": "next-week", "label": "Next Week" }
  ],
  "impacts": [
    { "value": "all", "label": "All", "emoji": "🌐" },
    { "value": "high", "label": "High", "emoji": "🔴" },
    { "value": "medium", "label": "Medium", "emoji": "🟡" },
    { "value": "low", "label": "Low", "emoji": "🟢" }
  ],
  "events": [],
  "lastUpdated": null
}
```

**Component Layout**:
```tsx
<Card size="md">
  <Col gap={3}>
    <Row justify="between" align="center">
      <Col gap={1}>
        <Title value={title} size="md" />
        <Caption value={subtitle} />
      </Col>
      <Button
        label="⟳ Refresh"
        variant="outline"
        onClickAction={{ type: "widget.refresh", payload: { widget: "economic-calendar" } }}
      />
    </Row>
  </Col>

  <Divider />

  <Col gap={2}>
    <Caption value="Period" />
    <Row wrap="wrap" gap={2}>
      {periods.map((period) => (
        <Button
          label={period.label}
          variant={selectedPeriod === period.value ? "solid" : "outline"}
          onClickAction={{
            type: "widget.updateFilter",
            payload: { widget: "economic-calendar", filter: "period", value: period.value }
          }}
        />
      ))}
    </Row>
  </Col>

  <Divider />

  <Col gap={2}>
    <Caption value="Impact" />
    <Row wrap="wrap" gap={2}>
      {impacts.map((impact) => (
        <Button
          label={`${impact.emoji} ${impact.label}`}
          variant={selectedImpact === impact.value ? "solid" : "outline"}
          onClickAction={{
            type: "widget.updateFilter",
            payload: { widget: "economic-calendar", filter: "impact", value: impact.value }
          }}
        />
      ))}
    </Row>
  </Col>

  <Divider />

  <Col gap={2} maxHeight="400px" overflow="scroll">
    {events.map((event) => (
      <EventCard event={event} />
    ))}
  </Col>

  {lastUpdated && (
    <Caption value={`Updated ${lastUpdated}`} align="right" />
  )}
</Card>
```

**Actions**:
- `widget.refresh` - Fetches latest calendar data
- `widget.updateFilter` - Updates period/impact filter and refetches

---

### Widget 2: News Feed Widget

**Schema** (`news-feed-widget.json`):
```json
{
  "title": "Market News",
  "symbol": "AAPL",
  "sources": ["CNBC", "Yahoo Finance"],
  "articles": [],
  "lastUpdated": null,
  "autoRefresh": true
}
```

**Component Layout**:
```tsx
<Card size="md">
  <Col gap={3}>
    <Row justify="between" align="center">
      <Title value={`${symbol} News`} size="md" />
      <Button
        label="⟳"
        variant="ghost"
        onClickAction={{ type: "widget.refresh", payload: { widget: "news-feed" } }}
      />
    </Row>
  </Col>

  <Divider />

  <Col gap={2} maxHeight="500px" overflow="scroll">
    {articles.map((article) => (
      <Card size="sm" variant="outline">
        <Col gap={2}>
          <Title value={article.title} size="sm" />
          <Caption value={article.description} />
          <Row justify="between" align="center">
            <Caption value={article.source} />
            <Button
              label="Read More ↗"
              variant="link"
              onClickAction={{
                type: "browser.openUrl",
                payload: { url: article.url }
              }}
            />
          </Row>
        </Col>
      </Card>
    ))}
  </Col>

  {lastUpdated && (
    <Caption value={`Updated ${lastUpdated}`} align="right" />
  )}
</Card>
```

**Actions**:
- `widget.refresh` - Fetches latest news for current symbol
- `browser.openUrl` - Opens article in new tab

---

### Widget 3: Technical Levels Widget

**Schema** (`technical-levels-widget.json`):
```json
{
  "title": "Technical Levels",
  "symbol": "AAPL",
  "levels": {
    "sell_high": { "price": 185.50, "label": "Sell High", "type": "resistance", "color": "#ef4444" },
    "buy_low": { "price": 175.30, "label": "Buy Low", "type": "support", "color": "#22c55e" },
    "btd": { "price": 170.00, "label": "BTD", "type": "strong_support", "color": "#3b82f6" }
  },
  "tooltips": {
    "sell_high": "Resistance level - Consider taking profits near this price",
    "buy_low": "Support level - Potential buying opportunity near this price",
    "btd": "Buy The Dip - Strong support level for accumulation"
  },
  "autoUpdate": true
}
```

**Component Layout**:
```tsx
<Card size="md">
  <Col gap={3}>
    <Title value={title} size="md" />
  </Col>

  <Divider />

  <Col gap={2}>
    {Object.entries(levels).map(([key, level]) => (
      <Row
        justify="between"
        align="center"
        style={{ padding: "8px", borderRadius: "4px", background: "rgba(0,0,0,0.02)" }}
        onClickAction={{
          type: "chart.highlightLevel",
          payload: { price: level.price, type: level.type, label: level.label }
        }}
      >
        <Tooltip content={tooltips[key]}>
          <Caption value={level.label} />
        </Tooltip>
        <Title
          value={`$${level.price.toFixed(2)}`}
          size="sm"
          style={{ color: level.color }}
        />
      </Row>
    ))}
  </Col>

  <Divider />

  <Caption value={`Levels for ${symbol}`} align="center" />
</Card>
```

**Actions**:
- `chart.highlightLevel` - Draws horizontal line at price level on chart
- Auto-updates when symbol changes

---

### Widget 4: Pattern Detection Widget

**Schema** (`pattern-detection-widget.json`):
```json
{
  "title": "Pattern Detection",
  "symbol": "AAPL",
  "timeframe": "1D",
  "showAll": false,
  "categories": ["Reversal", "Continuation", "Neutral"],
  "selectedCategory": "all",
  "patterns": [
    {
      "id": "pattern-1",
      "name": "Head and Shoulders",
      "category": "Reversal",
      "signal": "bearish",
      "confidence": 0.85,
      "visible": false,
      "coordinates": { "start": "2025-01-10", "end": "2025-01-15" }
    }
  ]
}
```

**Component Layout**:
```tsx
<Card size="md">
  <Col gap={3}>
    <Row justify="between" align="center">
      <Title value={title} size="md" />
      <Toggle
        label="Show All"
        checked={showAll}
        onChangeAction={{
          type: "widget.toggleShowAll",
          payload: { widget: "pattern-detection" }
        }}
      />
    </Row>
  </Col>

  <Divider />

  <Col gap={2}>
    <Caption value="Category" />
    <Row wrap="wrap" gap={2}>
      <Button
        label="All"
        variant={selectedCategory === "all" ? "solid" : "outline"}
        onClickAction={{
          type: "widget.filterCategory",
          payload: { widget: "pattern-detection", category: "all" }
        }}
      />
      {categories.map((category) => (
        <Button
          label={category}
          variant={selectedCategory === category ? "solid" : "outline"}
          onClickAction={{
            type: "widget.filterCategory",
            payload: { widget: "pattern-detection", category }
          }}
        />
      ))}
    </Row>
  </Col>

  <Divider />

  <Col gap={2} maxHeight="400px" overflow="scroll">
    {patterns
      .filter(p => selectedCategory === "all" || p.category === selectedCategory)
      .map((pattern) => (
        <Card
          size="sm"
          variant="outline"
          style={{
            borderColor: pattern.signal === "bullish" ? "#22c55e" : pattern.signal === "bearish" ? "#ef4444" : "#gray"
          }}
          onClickAction={{
            type: "chart.togglePattern",
            payload: { patternId: pattern.id, coordinates: pattern.coordinates }
          }}
        >
          <Row justify="between" align="center">
            <Col gap={1}>
              <Row gap={2} align="center">
                <Title value={pattern.name} size="sm" />
                <Badge
                  label={pattern.category}
                  variant="outline"
                />
              </Row>
              <Caption value={`Confidence: ${(pattern.confidence * 100).toFixed(0)}%`} />
            </Col>
            <Toggle
              checked={pattern.visible}
              onChangeAction={{
                type: "widget.togglePattern",
                payload: { widget: "pattern-detection", patternId: pattern.id }
              }}
            />
          </Row>
        </Card>
      ))}
  </Col>

  <Caption value={`${patterns.length} patterns detected`} align="center" />
</Card>
```

**Actions**:
- `widget.toggleShowAll` - Shows/hides all patterns on chart
- `widget.filterCategory` - Filters patterns by category
- `widget.togglePattern` - Toggles individual pattern visibility
- `chart.togglePattern` - Draws pattern on chart at coordinates

---

## New Dashboard Architecture

### New Layout (ChatKit-First)
```
┌──────────────────────────────────────────────────┐
│  MAIN VIEW - RealtimeChatKit (Full Width)       │
├──────────────────────────────────────────────────┤
│  ChatKit Interface with:                         │
│  • Voice controls                                │
│  • Message history                               │
│  • Chart commands                                │
│  • Widget launcher buttons                       │
└──────────────────────────────────────────────────┘

Widgets (Launched as Modals/Overlays):
• Economic Calendar Widget
• News Feed Widget
• Technical Levels Widget
• Pattern Detection Widget
```

### Implementation Strategy

1. **Phase 1: Widget Creation** (ChatKit Studio)
   - Create all 4 widget specifications in ChatKit Studio
   - Configure schemas and component layouts
   - Test widget actions and data binding

2. **Phase 2: Backend Integration**
   - Create widget API endpoints in backend
   - Implement widget action handlers
   - Connect widget data sources to existing services

3. **Phase 3: Dashboard Refactor**
   - Remove left panel from TradingDashboardSimple
   - Remove technical-section and pattern-section
   - Expand RealtimeChatKit to full width
   - Add widget launcher UI in ChatKit interface

4. **Phase 4: Chart Integration**
   - Implement widget → chart actions
   - Add chart event listeners for widget updates
   - Ensure symbol/timeframe sync between widgets

5. **Phase 5: Testing & Polish**
   - Test all widget functionalities
   - Verify chart integrations
   - Mobile responsive testing
   - Performance optimization

---

## Technical Implementation Details

### Widget Action Handlers (Backend)

```python
# backend/widget_handlers.py

@app.post("/api/widget/economic-calendar/refresh")
async def refresh_economic_calendar(
    period: str = "today",
    impact: Optional[str] = None
):
    """Refresh economic calendar widget data"""
    return await forexDataService.getCalendar(
        timePeriod=period,
        impact=impact
    )

@app.post("/api/widget/news-feed/refresh")
async def refresh_news_feed(symbol: str):
    """Refresh news feed widget data"""
    return await marketDataService.getNews(symbol)

@app.get("/api/widget/technical-levels")
async def get_technical_levels(symbol: str, timeframe: str = "1D"):
    """Get technical levels for symbol"""
    # Implementation TBD - calculate support/resistance
    pass

@app.get("/api/widget/patterns")
async def get_patterns(symbol: str, timeframe: str = "1D"):
    """Get detected patterns for symbol"""
    # Implementation TBD - pattern detection service
    pass
```

### Widget Launcher UI (RealtimeChatKit.tsx)

```tsx
// Add widget launcher buttons to ChatKit interface
<div className="widget-launcher">
  <Button
    label="📅 Economic Calendar"
    onClick={() => openWidget('economic-calendar')}
  />
  <Button
    label="📰 News Feed"
    onClick={() => openWidget('news-feed')}
  />
  <Button
    label="📊 Technical Levels"
    onClick={() => openWidget('technical-levels')}
  />
  <Button
    label="🔍 Pattern Detection"
    onClick={() => openWidget('pattern-detection')}
  />
</div>
```

### Chart Action Handlers (enhancedChartControl.ts)

```typescript
// Add widget action handlers
export const widgetActions = {
  'chart.highlightLevel': (payload: { price: number; type: string; label: string }) => {
    enhancedChartControl.addHorizontal(payload.price, {
      color: payload.type === 'resistance' ? '#ef4444' : '#22c55e',
      style: 'dashed',
      draggable: false
    });
  },

  'chart.togglePattern': (payload: { patternId: string; coordinates: any }) => {
    // Draw pattern on chart using coordinates
    // Implementation TBD
  },

  'chart.setSymbol': (payload: { symbol: string }) => {
    // Already implemented in existing chart controls
  },

  'chart.setTimeframe': (payload: { timeframe: string }) => {
    // Already implemented in existing chart controls
  }
};
```

---

## Migration Checklist

### Pre-Migration
- [ ] Backup current TradingDashboardSimple.tsx
- [ ] Document all current panel features
- [ ] Identify all API endpoints used
- [ ] Create widget specifications

### Phase 1: Widget Creation
- [ ] Create Economic Calendar widget in ChatKit Studio
- [ ] Create News Feed widget in ChatKit Studio
- [ ] Create Technical Levels widget in ChatKit Studio
- [ ] Create Pattern Detection widget in ChatKit Studio
- [ ] Test widgets in isolation

### Phase 2: Backend Integration
- [ ] Create `/api/widget/economic-calendar/refresh` endpoint
- [ ] Create `/api/widget/news-feed/refresh` endpoint
- [ ] Create `/api/widget/technical-levels` endpoint
- [ ] Create `/api/widget/patterns` endpoint
- [ ] Test all widget endpoints

### Phase 3: Dashboard Refactor
- [ ] Remove left panel (analysis-panel-left) from TradingDashboardSimple
- [ ] Remove technical-section
- [ ] Remove pattern-section
- [ ] Remove news feed section
- [ ] Expand RealtimeChatKit to full width
- [ ] Add widget launcher UI

### Phase 4: Chart Integration
- [ ] Implement `chart.highlightLevel` action
- [ ] Implement `chart.togglePattern` action
- [ ] Add widget → chart event system
- [ ] Add chart → widget update system
- [ ] Test symbol/timeframe synchronization

### Phase 5: Testing
- [ ] Test Economic Calendar widget functionality
- [ ] Test News Feed widget functionality
- [ ] Test Technical Levels widget functionality
- [ ] Test Pattern Detection widget functionality
- [ ] Test chart integrations
- [ ] Test mobile responsiveness
- [ ] Performance benchmarking
- [ ] User acceptance testing

---

## Success Criteria

1. ✅ All 4 widgets functional and accessible from ChatKit interface
2. ✅ Left panel completely removed from dashboard
3. ✅ RealtimeChatKit is the primary and only UI interface
4. ✅ All widget data updates in real-time
5. ✅ Chart integrations working (symbol sync, pattern highlighting, level drawing)
6. ✅ Mobile responsive on all screen sizes
7. ✅ Performance maintained or improved
8. ✅ No loss of existing functionality

---

## Risks and Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| ChatKit Studio limitations | High | Prototype widgets first, identify constraints early |
| API endpoint refactoring | Medium | Use adapter pattern to wrap existing services |
| Chart integration complexity | High | Build incrementally, test each action individually |
| Mobile responsiveness | Medium | Test on real devices early and often |
| Performance degradation | High | Implement lazy loading, optimize widget rendering |
| Data synchronization issues | High | Use event-driven architecture, implement state management |

---

## Timeline Estimate

- **Phase 1**: Widget Creation - 2-3 hours
- **Phase 2**: Backend Integration - 2-3 hours
- **Phase 3**: Dashboard Refactor - 1-2 hours
- **Phase 4**: Chart Integration - 3-4 hours
- **Phase 5**: Testing & Polish - 2-3 hours

**Total**: 10-15 hours

---

## Next Steps

1. ✅ **COMPLETED**: Create this comprehensive plan document
2. **TODO**: Get user approval on widget specifications
3. **TODO**: Begin Phase 1 - Create widgets in ChatKit Studio
4. **TODO**: Implement backend widget endpoints
5. **TODO**: Refactor TradingDashboardSimple layout
6. **TODO**: Integrate chart actions
7. **TODO**: Comprehensive testing
8. **TODO**: Production deployment

---

**Status**: ✅ **PLAN COMPLETE - READY FOR REVIEW**

*This plan provides a complete roadmap for converting the GVSES Trading Dashboard from a 3-panel React layout to a ChatKit-first widget-based architecture.*
