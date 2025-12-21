# Lazy Loading Integration Guide - Frontend

**Status:** Frontend implementation complete
**Backend Requirement:** Database migration must be run first

---

## 📦 What's Been Built

### Core Components

1. **useInfiniteChartData Hook** (`src/hooks/useInfiniteChartData.ts`)
   - Automatic lazy loading when user scrolls left
   - 3-tier caching integration (in-memory → database → API)
   - Smart edge detection (loads more when within 15% of left edge)
   - Loading state management
   - Error handling and retry logic

2. **ChartLoadingIndicator** (`src/components/ChartLoadingIndicator.tsx`)
   - Center overlay for initial loading
   - Top-left badge for "loading more" state
   - Optional cache performance info (debug mode)
   - Smooth animations and transitions

3. **TradingChartLazy** (`src/components/TradingChartLazy.tsx`)
   - Drop-in replacement for TradingChart
   - Fully integrated with lazy loading hook
   - Maintains all existing features (drawings, technical levels, etc.)
   - Backward compatible props

---

## 🚀 Quick Start

### Step 1: Import the New Component

**Before:**
```tsx
import { TradingChart } from '../components/TradingChart'

function MyDashboard() {
  return (
    <TradingChart
      symbol="AAPL"
      days={100}
      interval="1d"
    />
  )
}
```

**After:**
```tsx
import { TradingChartLazy } from '../components/TradingChartLazy'

function MyDashboard() {
  return (
    <TradingChartLazy
      symbol="AAPL"
      initialDays={60}  // Loads 60 days initially
      interval="5m"     // 5-minute candles
      enableLazyLoading={true}  // Enable infinite scrolling
      showCacheInfo={false}     // Show cache debug info (dev only)
    />
  )
}
```

### Step 2: Test Locally

1. **Ensure backend is running:**
   ```bash
   cd backend
   uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start frontend dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser and test:**
   - Navigate to chart view
   - Pan left (drag chart to the right)
   - Watch for "Loading older data..." badge in top-left
   - See smooth integration of older data

---

## 🎨 Component API

### TradingChartLazy Props

```typescript
interface TradingChartLazyProps {
  symbol: string                  // Stock symbol (e.g., "AAPL", "TSLA")
  interval?: string               // Timeframe: '1m', '5m', '15m', '30m', '1h', '1d', '1wk', '1mo'
  initialDays?: number            // Days to load on mount (default: 60)
  displayDays?: number            // Days to display on chart (zoom level)
  technicalLevels?: any           // Technical analysis levels
  onChartReady?: (chart) => void  // Callback when chart initializes
  enableLazyLoading?: boolean     // Enable/disable lazy loading (default: true)
  showCacheInfo?: boolean         // Show cache performance badge (default: false)
}
```

### Hook API

```typescript
const {
  data,           // ChartCandle[] - All loaded candles
  isLoading,      // boolean - Initial load in progress
  isLoadingMore,  // boolean - Loading more data (scrolling)
  error,          // string | null - Error message
  hasMore,        // boolean - More data available?
  oldestDate,     // Date | null - Oldest loaded date
  newestDate,     // Date | null - Newest loaded date
  cacheInfo,      // { tier, duration_ms } - Cache performance

  // Actions
  loadMore,       // () => Promise<void> - Manually trigger load
  refresh,        // () => Promise<void> - Reload initial data
  reset,          // () => void - Reset all state
  attachToChart,  // (chart: IChartApi) => void - Attach to chart
  detachFromChart // () => void - Detach from chart
} = useInfiniteChartData({
  symbol: 'AAPL',
  interval: '5m',
  initialDays: 60,
  loadMoreDays: 30,
  edgeThreshold: 0.15,  // 15% from edge triggers load
  enabled: true
})
```

---

## 📊 Performance Expectations

### Initial Load
- **Cold (no cache):** 500-1000ms
  - API fetch from Alpaca
  - Store in database
  - Return to frontend

- **Warm (database cache):** 50-200ms
  - Fetch from Supabase
  - Skip API call

- **Hot (memory cache):** ~20ms
  - In-memory cache hit
  - No database or API call

### Lazy Loading (Scrolling Left)
- **Database hit:** 50-200ms
  - Data already pre-warmed
  - Direct from Supabase

- **API call (gap):** 500-800ms
  - Missing data range
  - Fetch from Alpaca
  - Store for future use

### API Call Reduction
- **Before:** 1000 chart views = 1000 API calls
- **After:** 1000 chart views = ~10 API calls (99% reduction!)

---

## 🎯 User Experience

### What Users See

1. **Initial Load (First Time)**
   - Center loading spinner: "Loading chart data..."
   - Chart appears after ~500ms
   - Smooth fade-in animation

2. **Initial Load (Cached)**
   - Instant appearance (~50ms)
   - No loading spinner (sub-200ms threshold)
   - Seamless experience

3. **Scrolling Left**
   - Blue badge appears: "Loading older data..."
   - Loads 30 more days of history
   - New candles smoothly prepended
   - Badge fades out when complete

4. **Edge Cases**
   - No more data: Badge doesn't appear
   - Error: Chart shows error message
   - Offline: Uses last cached data

---

## 🧪 Testing Checklist

### Manual Testing

- [ ] **Initial Load - Cold Cache**
  - Clear browser cache
  - Load chart
  - Expect: ~500ms load time, center spinner
  - Verify: Data appears correctly

- [ ] **Initial Load - Warm Cache**
  - Reload page (browser cache)
  - Expect: Instant load (~50ms)
  - Verify: No loading spinner

- [ ] **Lazy Loading - Database Hit**
  - Pan chart left (drag right)
  - Approach left edge
  - Expect: Blue "Loading older data..." badge
  - Verify: Older candles appear smoothly

- [ ] **Lazy Loading - End of Data**
  - Keep panning left
  - Reach 7-year limit (or data limit)
  - Expect: Badge stops appearing
  - Verify: No errors

- [ ] **Symbol Change**
  - Change symbol (e.g., AAPL → TSLA)
  - Expect: Fresh data load
  - Verify: Correct data for new symbol

- [ ] **Interval Change**
  - Change interval (e.g., 1d → 5m)
  - Expect: Fresh data load
  - Verify: Correct timeframe

- [ ] **Mobile Responsive**
  - Test on mobile viewport
  - Verify: Touch gestures work
  - Verify: Badge positions correctly

### Automated Testing (Future)

```bash
# Unit tests for hook
npm test src/hooks/useInfiniteChartData.test.ts

# Integration tests
npm test src/components/TradingChartLazy.test.tsx

# E2E tests
npm run test:e2e
```

---

## 🐛 Troubleshooting

### Issue: "No data loads"
**Possible Causes:**
- Backend not running
- Database migration not executed
- Invalid API URL in `.env`

**Fix:**
```bash
# Check backend
curl http://localhost:8000/health

# Check environment
cat frontend/.env
# Verify: VITE_API_URL=http://localhost:8000

# Run migration (if needed)
cd backend && python3 check_readiness.py
```

### Issue: "Lazy loading doesn't trigger"
**Possible Causes:**
- `enableLazyLoading={false}`
- Chart not wide enough to scroll
- Already at data limit

**Fix:**
```tsx
<TradingChartLazy
  symbol="AAPL"
  enableLazyLoading={true}  // Ensure this is true
  initialDays={10}          // Start with less data to test scrolling
/>
```

### Issue: "Slow performance"
**Possible Causes:**
- Database not pre-warmed
- Cache not hitting
- Network latency

**Fix:**
```bash
# Pre-warm database
cd backend
python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA

# Enable cache debug
<TradingChartLazy showCacheInfo={true} />
# Check if "database" tier is showing (should be fast)
```

### Issue: "Console errors"
**Common Errors:**
- `Failed to fetch`: Backend not running
- `HTTP 404`: Symbol not found or invalid
- `HTTP 500`: Backend error (check backend logs)

**Debug:**
```bash
# Backend logs
cd backend
uvicorn mcp_server:app --reload --log-level debug

# Frontend console
# Open DevTools → Console
# Look for network errors
```

---

## 🔄 Migration from Old TradingChart

### Option 1: Side-by-Side (Recommended)

Keep both components during testing:

```tsx
import { TradingChart } from '../components/TradingChart'
import { TradingChartLazy } from '../components/TradingChartLazy'

function MyDashboard() {
  const [useLazy, setUseLazy] = useState(true)

  return (
    <>
      <button onClick={() => setUseLazy(!useLazy)}>
        Toggle: {useLazy ? 'Lazy' : 'Old'}
      </button>

      {useLazy ? (
        <TradingChartLazy symbol="AAPL" initialDays={60} />
      ) : (
        <TradingChart symbol="AAPL" days={100} />
      )}
    </>
  )
}
```

### Option 2: Direct Replacement

Replace all instances:

```bash
# Find all usages
grep -r "TradingChart" frontend/src --include="*.tsx" --include="*.ts"

# Replace imports
# Old: import { TradingChart } from '../components/TradingChart'
# New: import { TradingChartLazy as TradingChart } from '../components/TradingChartLazy'
```

**Props Mapping:**
- `days={100}` → `initialDays={60}` (smaller initial load)
- Rest of props remain the same

---

## 📈 Best Practices

### 1. Choose Appropriate Initial Load Size

```tsx
// Daily charts: 60-90 days is good
<TradingChartLazy symbol="AAPL" interval="1d" initialDays={60} />

// Intraday (1h): 7-30 days
<TradingChartLazy symbol="TSLA" interval="1h" initialDays={14} />

// Short-term (5m): 2-7 days
<TradingChartLazy symbol="NVDA" interval="5m" initialDays={3} />
```

**Rationale:** Start small, let lazy loading fetch more as needed.

### 2. Pre-warm Popular Symbols

```bash
# Backend pre-warming for instant loads
cd backend
python3 -m backend.scripts.prewarm_data --symbols AAPL MSFT GOOGL TSLA NVDA
```

### 3. Use Cache Info During Development

```tsx
// Development
<TradingChartLazy showCacheInfo={true} />

// Production
<TradingChartLazy showCacheInfo={false} />
```

### 4. Handle Loading States Gracefully

The component already handles loading states, but you can add custom UI:

```tsx
function MyDashboard() {
  const chartHook = useInfiniteChartData({ symbol: 'AAPL', interval: '1d' })

  return (
    <div>
      {chartHook.isLoading && <p>Initializing chart...</p>}

      <TradingChartLazy symbol="AAPL" />

      {chartHook.cacheInfo.tier === 'api' && (
        <p style={{ color: 'orange' }}>⚠️ Fetching from API (slower)</p>
      )}
    </div>
  )
}
```

---

## 🎓 Advanced Usage

### Custom Hook Integration

```tsx
import { useInfiniteChartData } from '../hooks/useInfiniteChartData'

function AdvancedChart() {
  const hook = useInfiniteChartData({
    symbol: 'AAPL',
    interval: '5m',
    initialDays: 30,
    loadMoreDays: 15,
    edgeThreshold: 0.2,  // Trigger earlier (20% from edge)
  })

  return (
    <div>
      <div style={{ marginBottom: '10px' }}>
        <button onClick={hook.refresh}>Refresh</button>
        <button onClick={hook.loadMore}>Load More</button>
        <span>
          Loaded: {hook.data.length} candles
          ({hook.oldestDate?.toLocaleDateString()} - {hook.newestDate?.toLocaleDateString()})
        </span>
      </div>

      <TradingChartLazy
        symbol="AAPL"
        interval="5m"
        initialDays={30}
      />

      {hook.isLoadingMore && <p>📊 Loading historical data...</p>}
    </div>
  )
}
```

### Multiple Charts with Shared Cache

The hook automatically caches data, so multiple charts benefit:

```tsx
function MultiChartDashboard() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
      {/* Both charts share cached data for AAPL */}
      <TradingChartLazy symbol="AAPL" interval="1d" initialDays={60} />
      <TradingChartLazy symbol="AAPL" interval="1h" initialDays={7} />
    </div>
  )
}
```

---

## 📞 Support

### Questions?

- Check backend status: `python3 backend/check_readiness.py`
- Review API logs: Backend terminal output
- Browser console: Look for network errors

### Known Limitations

1. **7-Year Limit**: Alpaca free tier provides ~7 years of data
2. **Rate Limiting**: 200 API calls/minute (mitigated by caching)
3. **No Real-time**: Historical data only (use WebSocket for real-time)

---

## ✅ Success Criteria

You'll know it's working when:

- ✅ Initial chart load < 200ms (cached)
- ✅ Lazy loading triggers automatically when scrolling left
- ✅ "Loading older data..." badge appears briefly
- ✅ New candles appear smoothly without page reload
- ✅ Cache info shows "database" tier (fast)
- ✅ No API calls for repeated symbol views

---

**Ready to integrate?** Start with `TradingChartLazy` in a single view, test thoroughly, then roll out to all charts! 🚀
