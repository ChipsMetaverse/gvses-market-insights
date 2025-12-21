# Quick Reference - Lazy Loading System

**Copy & Paste Commands for Fast Setup**

---

## ⚡ 30-Second Status Check

```bash
cd backend && python3 check_readiness.py
```

**Expect:**
- ✅ ENV: All credentials configured
- ✅ DB: All 3 tables exist
- ✅ SERVER: Backend running

---

## 🔧 Setup Commands

### 1. Database Migration (One-Time)

**Supabase Dashboard (Recommended):**
```
https://app.supabase.com/project/cwnzgvrylvxfhwhsqelc/sql/new
```
Copy: `backend/supabase_migrations/004_historical_data_tables.sql`
Paste → Run

**Or Terminal (if psql installed):**
```bash
cd backend && ./run_migration.sh
```

### 2. Test Backend

**Localhost:**
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000  # Terminal 1
python3 test_historical_data_implementation.py               # Terminal 2
```

**Production:**
```bash
cd backend
python3 test_historical_data_implementation.py --url https://YOUR-APP.fly.dev
```

### 3. Pre-warm Database

**Quick test (3 symbols):**
```bash
cd backend
python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA --intervals 1d
```

**Full pre-warm (20 symbols):**
```bash
cd backend
python3 -m backend.scripts.prewarm_data
```

---

## 💻 Frontend Integration

### Import & Use

```tsx
// 1. Import
import { TradingChartLazy } from '../components/TradingChartLazy'

// 2. Use
function MyDashboard() {
  return (
    <TradingChartLazy
      symbol="AAPL"
      interval="5m"
      initialDays={60}
      enableLazyLoading={true}
      showCacheInfo={false}  // true for debug
    />
  )
}
```

### Development

```bash
cd frontend
npm run dev
# Visit: http://localhost:5174
```

---

## 📊 Testing Checklist

```bash
# Backend
cd backend
python3 check_readiness.py                                   # ✅ All checks pass?
python3 test_historical_data_implementation.py               # ✅ 4/4 tests pass?
python3 -m backend.scripts.prewarm_data --symbols AAPL      # ✅ Data stored?

# Frontend
cd frontend
npm run build                                                # ✅ Builds without errors?
```

---

## 🐛 Troubleshooting

### Tables Don't Exist
```bash
# Run migration (see Setup Commands #1 above)
cd backend && ./run_migration.sh
```

### Backend Not Running
```bash
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```

### No Data Loading
```bash
# Check backend health
curl http://localhost:8000/health

# Check environment
cat backend/.env | grep -E "SUPABASE_URL|ALPACA_API_KEY"
```

### Slow Performance
```bash
# Pre-warm database
cd backend
python3 -m backend.scripts.prewarm_data --symbols AAPL TSLA NVDA
```

---

## 📁 Key Files

### Backend
```
backend/supabase_migrations/004_historical_data_tables.sql  # DB schema
backend/check_readiness.py                                  # Diagnostics
backend/test_historical_data_implementation.py              # Tests
backend/scripts/prewarm_data.py                             # Data init
```

### Frontend
```
frontend/src/hooks/useInfiniteChartData.ts                  # Hook
frontend/src/components/TradingChartLazy.tsx                # Component
frontend/src/components/ChartLoadingIndicator.tsx           # Loading UI
frontend/src/examples/LazyLoadingChartExample.tsx           # Example
```

### Docs
```
QUICK_START.md                                              # 5-min setup
IMPLEMENTATION_COMPLETE.md                                  # Full summary
backend/TESTING_GUIDE.md                                    # Detailed testing
frontend/LAZY_LOADING_INTEGRATION.md                        # Frontend guide
```

---

## 🎯 Success Indicators

✅ `check_readiness.py` shows all green
✅ Tests pass: 4/4
✅ Database has 100k+ bars
✅ Chart loads < 200ms (cached)
✅ Lazy loading badge appears on scroll left
✅ No API calls for repeated views

---

## 📈 Performance Targets

| Metric | Target | How to Verify |
|--------|--------|---------------|
| Initial load (cached) | < 200ms | Browser DevTools Network tab |
| Lazy load | < 200ms | Watch "Loading..." badge duration |
| API call reduction | 99% | Check `/api/intraday` calls in Network tab |
| Cache hit rate | > 90% | Enable `showCacheInfo={true}` |

---

## 🚀 Deploy Checklist

- [ ] Migration executed in Supabase
- [ ] Backend tests pass (4/4)
- [ ] Database pre-warmed (20 symbols)
- [ ] Frontend builds successfully
- [ ] Manual testing complete
- [ ] Production deployment ready

---

## 💡 Common Use Cases

### Debug Mode
```tsx
<TradingChartLazy
  symbol="AAPL"
  showCacheInfo={true}  // See cache tier + timing
/>
```

### Different Timeframes
```tsx
// Intraday (5-minute)
<TradingChartLazy symbol="AAPL" interval="5m" initialDays={7} />

// Daily
<TradingChartLazy symbol="AAPL" interval="1d" initialDays={90} />

// Weekly
<TradingChartLazy symbol="AAPL" interval="1wk" initialDays={730} />
```

### Multiple Symbols
```tsx
{['AAPL', 'TSLA', 'NVDA'].map(symbol => (
  <TradingChartLazy key={symbol} symbol={symbol} interval="1d" initialDays={60} />
))}
```

---

## 📞 Support

**Stuck?** Run diagnostics:
```bash
cd backend && python3 check_readiness.py
```

**Need help?** Check docs:
- Quick setup: `QUICK_START.md`
- Full details: `IMPLEMENTATION_COMPLETE.md`
- Testing: `backend/TESTING_GUIDE.md`
- Frontend: `frontend/LAZY_LOADING_INTEGRATION.md`

---

**Ready to ship!** 🚀
