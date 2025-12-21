# A/B/C/D Test Implementation Guide
## Economic Calendar UX Optimization

**Created**: November 30, 2025
**Status**: Ready for Implementation
**Goal**: Determine optimal Economic Calendar layout for trader decision-making

---

## 📊 Test Overview

### Hypothesis
Different layout approaches will significantly impact trader efficiency and decision quality.

### Success Metrics
1. **Primary**: Time to Decision (ms from page load to first meaningful action)
2. **Secondary**:
   - Context Switches (lower is better)
   - Engagement Score (interactions - penalties)
   - Information Retrieval Speed
   - User Satisfaction (subjective)

### Test Duration
- **Minimum**: 50 sessions per variant (200 total)
- **Recommended**: 100+ sessions per variant for statistical significance
- **Timeline**: 1-2 weeks

---

## 🎨 Variant Designs

### **Variant A: CONTROL (Current Design)**

```
┌─────────────────────────────────────────────────────────┐
│  CHART ANALYSIS                                          │
├──────────────────────┬──────────────────────────────────┤
│  TAB 1               │  TAB 2 (Selected)                │
├──────────────────────┴──────────────────────────────────┤
│  ┌─────────────────────────┐  ┌─────────────────────┐   │
│  │ Economic Calendar       │  │  NEWS               │   │
│  │ ├───────────────────┐   │  │                     │   │
│  │ │ Period:           │   │  │  [Loading...]       │   │
│  │ │ [Today] Tomorrow  │   │  │                     │   │
│  │ │  This Week        │   │  │  [News Card]        │   │
│  │ └───────────────────┘   │  │                     │   │
│  │                         │  │  [News Card]        │   │
│  │ SUN, NOV 30            │  │                     │   │
│  │ 19:05  BOJ Speech      │  │  [News Card]        │   │
│  │ JPY                    │  │                     │   │
│  │                         │  │                     │   │
│  └─────────────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- Tab-based separation
- Period filter (4 buttons)
- Single event display
- 50/50 split with NEWS
- No countdown timers
- No forecast values

**Implementation**: ✅ Already complete (baseline)

---

### **Variant B: CONTEXTUAL EXPANSION**

```
┌─────────────────────────────────────────────────────────┐
│  CHART ANALYSIS                                          │
├──────────────────────┬──────────────────────────────────┤
│  TAB 1               │  TAB 2 (Selected)                │
├──────────────────────┴──────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │ Economic Calendar            Period: [Today ▼]   │   │
│  │ ┌─────────────────────────────────────────────┐  │   │
│  │ │ TODAY (1 event)                             │  │   │
│  │ │                                              │  │   │
│  │ │ 🔴 19:05 (in 9h 45m)              JPY       │  │   │
│  │ │    BOJ Gov Ueda Speaks                      │  │   │
│  │ │    Expected: Hawkish | Impact: High         │  │   │
│  │ └─────────────────────────────────────────────┘  │   │
│  │ ┌─────────────────────────────────────────────┐  │   │
│  │ │ TOMORROW (3 events) ━━━ Preview            │  │   │
│  │ │                                              │  │   │
│  │ │ 🟡 08:30  USD  Jobless Claims               │  │   │
│  │ │ 🔴 10:00  USD  ISM Manufacturing            │  │   │
│  │ │ 🟡 14:00  USD  Fed Williams Speaks          │  │   │
│  │ │                                              │  │   │
│  │ │ [View all tomorrow's events →]              │  │   │
│  │ └─────────────────────────────────────────────┘  │   │
│  │ ┌─────────────────────────────────────────────┐  │   │
│  │ │ THIS WEEK (12 high-impact)                  │  │   │
│  │ │ Mon: NFP, CPI | Wed: FOMC | Fri: GDP       │  │   │
│  │ └─────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**Features**:
- ✨ Auto-expands when sparse
- ✨ Countdown timers ("in 9h 45m")
- ✨ Forecast/previous/actual values
- ✨ Impact indicators (🔴🟡⚪)
- Compact period dropdown
- Progressive disclosure
- Full-width (no NEWS split)

**Implementation**: ~8 hours

**Key Changes**:
1. Detect sparse content: `todayEvents.length <= 2`
2. Show tomorrow/week preview automatically
3. Add countdown utility: `formatCountdown(eventTime)`
4. Enhance event cards with forecast data
5. Compact period filter to dropdown

---

### **Variant C: UNIFIED SPLIT VIEW**

```
┌─────────────────────────────────────────────────────────┐
│  CHART ANALYSIS                                          │
├─────────────────────┬───────────────────────────────────┤
│ Technical Levels    │  Market Events                    │
│ ┌─────────────────┐ │ ┌───────────────────────────────┐ │
│ │ ST:  $430.17    │ │ │ TODAY (1) Period: [Today ▼]  │ │
│ │ QE:  $425.00    │ │ ├───────────────────────────────┤ │
│ │ LTB: $400.00    │ │ │ 🔴 19:05 (9h 45m) JPY         │ │
│ └─────────────────┘ │ │    BOJ Gov Ueda Speaks        │ │
│                     │ ├───────────────────────────────┤ │
│ Pattern Detection   │ │ TOMORROW (3)                  │ │
│ ┌─────────────────┐ │ │ 🟡 08:30 Jobless Claims       │ │
│ │ • Breakout      │ │ │ 🔴 10:00 ISM Mfg              │ │
│ │   forming       │ │ │ 🟡 14:00 Fed Speaks           │ │
│ │ • Support at    │ │ ├───────────────────────────────┤ │
│ │   $425          │ │ │ 📰 Latest News                │ │
│ └─────────────────┘ │ │ • Tesla Q4 earnings           │ │
│                     │ │ • NVDA chip demand surge      │ │
└─────────────────────┴───────────────────────────────────┘
```

**Features**:
- ✨ No tabs - see everything
- ✨ 50/50 Technical | Market split
- ✨ Compact cards
- ✨ Integrated news
- Countdown timers
- Forecast values
- Always-visible context

**Implementation**: ~12 hours

**Key Changes**:
1. Remove tab system entirely
2. Create `UnifiedChartAnalysis.tsx` component
3. Implement 50/50 grid layout
4. Compact event cards (single-line)
5. Integrate news feed inline
6. Responsive: stack on mobile

---

### **Variant D: TIMELINE INTEGRATION**

```
┌─────────────────────────────────────────────────────────┐
│  TSLA Chart                                              │
│                                                          │
│  $450 ┤                      📍                          │
│       │                      │ BOJ 19:05                │
│  $430 ┤──────────────────────┤                          │
│       │                   ↗  │                          │
│  $400 ┤                      │                          │
│       └──────────────────────┴───────────────────────────│
│       Jan    Feb    Mar   Today  →                      │
│                                                          │
│  ┌─── Event Timeline ────────────────────────────────┐  │
│  │  Now: BOJ (9h) → Tomorrow: Jobless (18h) → ISM   │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────┐
│ Events      │
├─────────────┤
│ TODAY (1)   │
│ 🔴 19:05    │
│   BOJ       │
│             │
│ TMR (3)     │
│ 🟡 08:30    │
│ 🔴 10:00    │
│ 🟡 14:00    │
│             │
│ [View All]  │
└─────────────┘
(Right Sidebar)
```

**Features**:
- ✨ Events on chart timeline
- ✨ Compact sidebar (always visible)
- ✨ Click to zoom to event
- ✨ Hover for details
- Countdown on chart
- Timeline navigation
- Visual correlation

**Implementation**: ~16 hours (most complex)

**Key Changes**:
1. Add event markers to TradingChart.tsx
2. Create `ChartEventMarker` component
3. Implement hover tooltips on chart
4. Create compact sidebar `EventsSidebar.tsx`
5. Add zoom-to-event functionality
6. Sync chart time with events

---

## 🔧 Implementation Steps

### Step 1: Setup Test Infrastructure ✅
- [x] Create `abTestConfig.ts`
- [x] Create `ABTestSwitcher.tsx`
- [x] Add metrics tracking utilities

### Step 2: Integrate Switcher
```tsx
// In TradingDashboardSimple.tsx
import { ABTestSwitcher } from './ABTestSwitcher';
import { getTestConfig } from '../config/abTestConfig';

export const TradingDashboardSimple: React.FC = () => {
  const testConfig = getTestConfig();

  return (
    <>
      {/* Existing dashboard */}
      <ABTestSwitcher />
    </>
  );
};
```

### Step 3: Implement Variant B (Recommended First)
```tsx
// Create frontend/src/components/EconomicCalendarVariantB.tsx

import { useForexCalendar } from '../hooks/useForexCalendar';
import { formatCountdown, shouldAutoExpand } from '../utils/calendarUtils';

export const EconomicCalendarVariantB: React.FC = () => {
  const { todayEvents, tomorrowEvents, weekEvents } = useForexCalendar();
  const showPreview = shouldAutoExpand(todayEvents);

  return (
    <div className="economic-calendar-variant-b">
      {/* Today's events */}
      <section>
        <h4>TODAY ({todayEvents.length} events)</h4>
        {todayEvents.map(event => (
          <EventCardEnhanced
            key={event.id}
            event={event}
            showCountdown
            showForecast
          />
        ))}
      </section>

      {/* Auto-expand preview */}
      {showPreview && (
        <>
          <section className="preview">
            <h4>TOMORROW ({tomorrowEvents.length} events) ━━━ Preview</h4>
            {tomorrowEvents.slice(0, 3).map(event => (
              <EventCardCompact key={event.id} event={event} />
            ))}
            <button>View all tomorrow's events →</button>
          </section>

          <section className="preview">
            <h4>THIS WEEK ({weekEvents.length} high-impact)</h4>
            <WeekSummary events={weekEvents} />
          </section>
        </>
      )}
    </div>
  );
};
```

### Step 4: Add Metrics Tracking
```tsx
import { useState, useEffect } from 'react';
import { initMetrics, trackAction, saveMetrics } from '../config/abTestConfig';

export const useABTestMetrics = () => {
  const [metrics, setMetrics] = useState(initMetrics);

  // Track actions
  const track = (type, metadata) => {
    setMetrics(prev => trackAction(prev, type, metadata));
  };

  // Save on unmount
  useEffect(() => {
    return () => saveMetrics(metrics);
  }, [metrics]);

  return { track };
};

// Usage in component:
const { track } = useABTestMetrics();

<button onClick={() => {
  track('period_change', { from: 'today', to: 'tomorrow' });
  changePeriod('tomorrow');
}}>
  Tomorrow
</button>
```

### Step 5: Test Each Variant
1. Switch to variant via UI
2. Use for 5-10 minutes
3. Check metrics dashboard
4. Repeat for all variants

### Step 6: Analyze Results
```bash
# Export metrics from localStorage
# In browser console:
Object.keys(localStorage)
  .filter(k => k.startsWith('ab_test'))
  .forEach(k => {
    console.log(k, JSON.parse(localStorage.getItem(k)));
  });
```

---

## 📈 Success Criteria

### Quantitative
- **Winner**: Variant with highest engagement score
- **Minimum**: 50 sessions per variant
- **Confidence**: 95% statistical significance

### Qualitative
- User feedback survey
- Observation of actual trading sessions
- Time to spot important events

### Example Analysis
```
Variant A (Control):
- Sessions: 50
- Avg Time to Action: 4500ms
- Context Switches: 8.2
- Engagement: 42.1

Variant B (Contextual):
- Sessions: 50
- Avg Time to Action: 2800ms  ← 38% faster! ✅
- Context Switches: 3.1       ← 62% less! ✅
- Engagement: 71.5            ← 70% higher! ✅

WINNER: Variant B
```

---

## 🚀 Rollout Plan

### Phase 1: Development (3-5 days)
- Day 1: Implement Variant B
- Day 2: Implement Variant C
- Day 3-4: Implement Variant D
- Day 5: QA and bug fixes

### Phase 2: Internal Testing (3 days)
- Test all variants yourself
- Collect initial metrics
- Fix obvious issues

### Phase 3: User Testing (7-14 days)
- Share with 5-10 users
- Ask them to try all variants
- Collect feedback
- Analyze metrics

### Phase 4: Decision (1 day)
- Review all data
- Make final decision
- Implement winner as default

### Phase 5: Cleanup
- Remove A/B test code
- Keep best variant
- Document learnings

---

## 💡 Quick Start Commands

```bash
# Start all services
cd backend && python3 -m uvicorn mcp_server:app --host 0.0.0.0 --port 8000 &
cd forex-mcp-server && PYTHONPATH="$PWD/src" python3 src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002 &
cd frontend && npm run dev

# Switch variants (in browser console)
localStorage.setItem('ab_test_variant', 'B');
window.location.reload();

# View metrics
console.log(JSON.parse(localStorage.getItem('ab_test_aggregate_A')));
console.log(JSON.parse(localStorage.getItem('ab_test_aggregate_B')));
console.log(JSON.parse(localStorage.getItem('ab_test_aggregate_C')));
console.log(JSON.parse(localStorage.getItem('ab_test_aggregate_D')));
```

---

## 📝 Notes

### Why This Approach?
- **Data-Driven**: Removes guesswork with real metrics
- **Low Risk**: Can revert to control anytime
- **User-Centered**: Tests with actual usage patterns
- **Iterative**: Easy to add more variants

### What to Watch For
- Variant D may be buggy initially (most complex)
- Mobile responsiveness needs separate testing
- News integration affects all variants except A

### Next Steps After Test
1. Implement winning variant permanently
2. Remove A/B test infrastructure
3. Document UX patterns learned
4. Apply insights to other panels

---

**Ready to start?** Begin with `npm install` in frontend and implement Variant B first!
