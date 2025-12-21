# 📋 Drawing Persistence Integration Checklist

Complete step-by-step guide for integrating standalone drawing persistence into main application.

---

## ✅ Phase 1: Database Setup (5 minutes)

### Step 1.1: Apply Schema to Supabase
- [ ] Go to Supabase Dashboard → SQL Editor
- [ ] Open `schema.sql`
- [ ] Copy entire contents
- [ ] Paste into SQL Editor
- [ ] Click **Run**
- [ ] Verify success message

### Step 1.2: Verify Tables Created
- [ ] Go to Table Editor
- [ ] Find `drawings` table
- [ ] Verify columns: id, user_id, symbol, kind, coordinates, etc.
- [ ] Check Row Level Security is **ENABLED**

### Step 1.3: Test Policies
- [ ] Go to Authentication → Policies
- [ ] Verify 4 policies on `drawings` table:
  - `drawings_select_policy`
  - `drawings_insert_policy`
  - `drawings_update_policy`
  - `drawings_delete_policy`

**Validation:**
```bash
# Should show drawings table with RLS enabled
psql -h db.xxx.supabase.co -U postgres -d postgres \
  -c "\dt drawings" \
  -c "\d+ drawings"
```

---

## ✅ Phase 2: Standalone Testing (15 minutes)

### Step 2.1: Setup Environment
- [ ] Copy `.env.example` to `.env`
- [ ] Fill in `SUPABASE_URL` from project settings
- [ ] Fill in `SUPABASE_ANON_KEY` from project settings
- [ ] Verify no trailing slashes or spaces

### Step 2.2: Install Dependencies
```bash
cd standalone-drawing-persistence
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- [ ] All packages installed successfully
- [ ] No error messages

### Step 2.3: Test Models Locally
```bash
python3 models.py
```
Expected output:
```
Testing trendline validation...
✅ Trendline valid: {...}

Testing horizontal validation...
✅ Horizontal valid: {...}

# Auto-generated TypeScript types
```
- [ ] Both validations pass
- [ ] TypeScript types print

### Step 2.4: Start Server
```bash
python3 server.py
```
Expected output:
```
🚀 Starting Drawing Persistence Server...
📚 API Docs: http://localhost:8001/docs
🔍 Health Check: http://localhost:8001/health

✨ Ready to test drawing persistence!

INFO:     Uvicorn running on http://0.0.0.0:8001
```
- [ ] No error messages
- [ ] Server starts successfully

### Step 2.5: Test Health Endpoints
```bash
# In new terminal
curl http://localhost:8001/health
curl http://localhost:8001/api/drawings/health
```
Expected:
```json
{"status": "healthy", "service": "drawing-persistence"}
{"status": "healthy", "database": "connected", "timestamp": "..."}
```
- [ ] Both return healthy status
- [ ] Database connected

### Step 2.6: Manual API Test
```bash
# Create a drawing
curl -X POST http://localhost:8001/api/drawings \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "TSLA",
    "kind": "trendline",
    "coordinates": {
      "a": {"time": 1609459200, "price": 700},
      "b": {"time": 1612137600, "price": 850}
    }
  }'

# Should return 201 with drawing ID
```
- [ ] Returns 201 Created
- [ ] Has `id` field
- [ ] Has `created_at` timestamp

```bash
# List drawings
curl "http://localhost:8001/api/drawings?symbol=TSLA"
```
- [ ] Returns drawing list
- [ ] Contains the drawing we just created

### Step 2.7: Run Test Suite
```bash
python3 test_api.py
```
Expected:
```
🧪 Running Drawing Persistence API Tests...
======================== test session starts ========================
test_api.py::test_root_endpoint PASSED                         [  5%]
test_api.py::test_health_check PASSED                          [ 10%]
...
test_api.py::test_get_stats PASSED                             [100%]

======================== 20 passed in 2.34s =========================
```
- [ ] All tests pass (20/20)
- [ ] No failures or errors

**If any tests fail:**
1. Check server logs
2. Verify Supabase connection
3. Check RLS policies
4. Review error messages

---

## ✅ Phase 3: Backend Integration (20 minutes)

### Step 3.1: Copy Files to Backend
```bash
# From standalone-drawing-persistence directory
cp models.py ../backend/models/drawing_models.py
cp api.py ../backend/routers/drawings.py
```
- [ ] Files copied successfully
- [ ] No overwrite conflicts

### Step 3.2: Update Backend Structure
```bash
# Verify directory structure
ls -la ../backend/models/
ls -la ../backend/routers/
```
Should see:
```
backend/
├── models/
│   ├── __init__.py
│   └── drawing_models.py  ← NEW
└── routers/
    ├── __init__.py
    └── drawings.py          ← NEW
```
- [ ] Files in correct locations

### Step 3.3: Update Backend Imports
Edit `backend/mcp_server.py`:
```python
# Add at top with other router imports
from routers.drawings import router as drawings_router

# Add after other router includes
app.include_router(drawings_router)
```
- [ ] Imports added
- [ ] Router registered
- [ ] No syntax errors

### Step 3.4: Test Backend Integration
```bash
# Restart main backend
cd ../backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000
```
- [ ] Server starts without errors
- [ ] No import errors

```bash
# Test drawings endpoint
curl http://localhost:8000/api/drawings/health
```
- [ ] Returns healthy status
- [ ] Database connected

### Step 3.5: Test Full Backend Flow
```bash
# Create drawing via main backend
curl -X POST http://localhost:8000/api/drawings \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "AAPL",
    "kind": "horizontal",
    "coordinates": {"price": 150}
  }'

# List drawings
curl "http://localhost:8000/api/drawings?symbol=AAPL"
```
- [ ] Create works (201)
- [ ] List works (200)
- [ ] Drawing persisted

---

## ✅ Phase 4: Frontend Integration (30 minutes)

### Step 4.1: Create Persistence Service
Create `frontend/src/services/drawingPersistenceService.ts`:
```typescript
import { AnyDrawing } from '../drawings/types'

const API_URL = import.meta.env.VITE_API_URL || window.location.origin

export const drawingPersistenceService = {
  async saveDrawing(drawing: AnyDrawing): Promise<AnyDrawing> {
    const response = await fetch(`${API_URL}/api/drawings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(drawing)
    })

    if (!response.ok) {
      throw new Error(`Failed to save drawing: ${response.statusText}`)
    }

    return response.json()
  },

  async loadDrawings(symbol: string): Promise<AnyDrawing[]> {
    const response = await fetch(
      `${API_URL}/api/drawings?symbol=${symbol}&page_size=500`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to load drawings: ${response.statusText}`)
    }

    const data = await response.json()
    return data.drawings
  },

  async updateDrawing(id: string, updates: Partial<AnyDrawing>): Promise<AnyDrawing> {
    const response = await fetch(`${API_URL}/api/drawings/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(updates)
    })

    if (!response.ok) {
      throw new Error(`Failed to update drawing: ${response.statusText}`)
    }

    return response.json()
  },

  async deleteDrawing(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/drawings/${id}`, {
      method: 'DELETE',
      credentials: 'include'
    })

    if (!response.ok && response.status !== 404) {
      throw new Error(`Failed to delete drawing: ${response.statusText}`)
    }
  },

  async deleteAllDrawings(symbol: string): Promise<void> {
    await fetch(`${API_URL}/api/drawings?symbol=${symbol}`, {
      method: 'DELETE',
      credentials: 'include'
    })
  }
}
```
- [ ] File created
- [ ] No TypeScript errors

### Step 4.2: Update TradingChart Component
Edit `frontend/src/components/TradingChart.tsx`:

Find the DrawingOverlay initialization (around line 578):
```typescript
overlayRef.current = createDrawingOverlay({
  chart,
  series: candlestickSeries,
  container: chartContainerRef.current,
  store,
  onUpdate: async (d) => {
    console.log('Drawing updated:', d)
    // OLD: TODO: PATCH /api/drawings/:id
    // NEW:
    try {
      await drawingPersistenceService.updateDrawing(d.id, d)
      console.log('✅ Drawing saved to database')
    } catch (error) {
      console.error('❌ Failed to save drawing:', error)
    }
  },
  onDelete: async (id) => {
    console.log('Drawing deleted:', id)
    // OLD: TODO: DELETE /api/drawings/:id
    // NEW:
    try {
      await drawingPersistenceService.deleteDrawing(id)
      console.log('✅ Drawing deleted from database')
    } catch (error) {
      console.error('❌ Failed to delete drawing:', error)
    }
  },
})
```

Find the ToolboxManager initialization (around line 594):
```typescript
toolboxRef.current = createToolbox({
  chart,
  series: candlestickSeries,
  container: chartContainerRef.current,
  store,
  onCreate: async (d) => {
    console.log('Drawing created:', d)
    // OLD: TODO: POST /api/drawings
    // NEW:
    try {
      const saved = await drawingPersistenceService.saveDrawing(d)
      d.id = saved.id  // Update with server-assigned ID
      store.upsert(d)
      console.log('✅ Drawing created in database:', saved.id)
    } catch (error) {
      console.error('❌ Failed to create drawing:', error)
    }
  },
  onUpdate: async (d) => {
    console.log('Drawing updated (toolbox):', d)
    // OLD: TODO: PATCH /api/drawings/:id
    // NEW:
    try {
      await drawingPersistenceService.updateDrawing(d.id, d)
    } catch (error) {
      console.error('❌ Failed to update drawing:', error)
    }
  },
  onDelete: async (id) => {
    console.log('Drawing deleted (toolbox):', id)
    // OLD: TODO: DELETE /api/drawings/:id
    // NEW:
    try {
      await drawingPersistenceService.deleteDrawing(id)
    } catch (error) {
      console.error('❌ Failed to delete drawing:', error)
    }
  },
})
```

- [ ] Callbacks updated
- [ ] Import added: `import { drawingPersistenceService } from '../services/drawingPersistenceService'`

### Step 4.3: Add Drawing Loading on Symbol Change
Add this effect in `TradingChart.tsx` after the chart initialization:
```typescript
// Load saved drawings when symbol changes
useEffect(() => {
  if (!chartRef.current || !symbol) return

  const loadDrawings = async () => {
    try {
      console.log(`📥 Loading saved drawings for ${symbol}...`)
      const drawings = await drawingPersistenceService.loadDrawings(symbol)
      console.log(`✅ Loaded ${drawings.length} drawings`)
      store.import(drawings)
    } catch (error) {
      console.error('❌ Failed to load drawings:', error)
    }
  }

  loadDrawings()
}, [symbol, store])
```
- [ ] Effect added
- [ ] Dependencies correct

### Step 4.4: Test Frontend Integration
```bash
cd frontend
npm run dev
```
- [ ] Frontend starts (port 5174)
- [ ] No console errors

**Manual Test:**
1. Open http://localhost:5174
2. Select chart drawing tool (trendline)
3. Draw a line on chart
4. Check browser console: `✅ Drawing created in database: xxx`
5. Refresh page
6. Verify line persists
7. Try moving the line
8. Check console: `✅ Drawing saved to database`
9. Delete the line (right-click → Delete)
10. Check console: `✅ Drawing deleted from database`

- [ ] Drawing creation works
- [ ] Refresh persistence works
- [ ] Updates persist
- [ ] Deletion works

---

## ✅ Phase 5: End-to-End Testing (15 minutes)

### Test Case 1: Basic Persistence
1. [ ] Draw trendline on TSLA chart
2. [ ] Refresh browser
3. [ ] Verify trendline reappears

### Test Case 2: Symbol Switching
1. [ ] Draw trendline on TSLA
2. [ ] Switch to AAPL (drawings should disappear)
3. [ ] Draw horizontal line on AAPL
4. [ ] Switch back to TSLA
5. [ ] Verify TSLA trendline reappears
6. [ ] Switch to AAPL again
7. [ ] Verify AAPL horizontal line reappears

### Test Case 3: Multiple Drawings
1. [ ] Draw 3 different lines on same chart
2. [ ] Refresh browser
3. [ ] Verify all 3 lines persist

### Test Case 4: Editing
1. [ ] Draw trendline
2. [ ] Drag endpoint to new position
3. [ ] Refresh browser
4. [ ] Verify new position persists

### Test Case 5: Styling
1. [ ] Draw line
2. [ ] Right-click → Change color to red
3. [ ] Refresh browser
4. [ ] Verify red color persists

### Test Case 6: Deletion
1. [ ] Draw 3 lines
2. [ ] Delete middle line
3. [ ] Refresh browser
4. [ ] Verify only 2 lines remain

---

## ✅ Phase 6: Production Deployment (10 minutes)

### Step 6.1: Update Backend .env
```bash
# backend/.env
SUPABASE_URL=https://your-prod-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...  # Production key
```
- [ ] Production credentials set
- [ ] No local credentials leaked

### Step 6.2: Test Production Database
```bash
# From backend/
python3 -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
result = client.table('drawings').select('id').limit(1).execute()
print('✅ Production database connected')
"
```
- [ ] Connection successful

### Step 6.3: Deploy Backend
```bash
# Using Docker (if applicable)
docker-compose up --build -d

# Or direct deployment
# Follow your deployment process
```
- [ ] Backend deployed
- [ ] Health check passes
- [ ] `/api/drawings/health` returns 200

### Step 6.4: Deploy Frontend
```bash
cd frontend
npm run build
# Deploy dist/ folder to hosting
```
- [ ] Build succeeds
- [ ] No TypeScript errors
- [ ] Frontend deployed

### Step 6.5: Production Smoke Test
1. [ ] Open production URL
2. [ ] Draw a line
3. [ ] Refresh
4. [ ] Verify persistence works
5. [ ] Check browser network tab for API calls
6. [ ] Verify no 404s or 500s

---

## ✅ Phase 7: Monitoring & Optimization (Ongoing)

### Monitoring
- [ ] Set up Supabase dashboard monitoring
- [ ] Watch for slow queries
- [ ] Monitor table size growth
- [ ] Track API error rates

### Optimization Opportunities
- [ ] Add indexes if needed (already have main ones)
- [ ] Consider pagination for users with 500+ drawings
- [ ] Add caching for frequently accessed drawings
- [ ] Implement drawing templates/presets

### Future Enhancements
- [ ] Sharing: Allow drawings to be shared between users
- [ ] Templates: Save drawing sets as reusable templates
- [ ] Export: Download drawings as JSON
- [ ] Import: Upload drawings from file
- [ ] Collaboration: Real-time drawing sync (WebSocket)

---

## 🎉 Success Criteria

**Integration Complete When:**
- ✅ All 20 test cases pass
- ✅ Drawings persist after browser refresh
- ✅ Drawings load correctly per symbol
- ✅ Updates/deletes work correctly
- ✅ No console errors in browser
- ✅ No 500 errors in backend logs
- ✅ Production deployment successful

---

## 🆘 Troubleshooting

### "Failed to save drawing: 401"
→ Check Supabase RLS policies
→ Verify user authentication

### "Failed to load drawings: 500"
→ Check backend logs
→ Verify Supabase credentials
→ Test database connection

### Drawings don't persist after refresh
→ Check browser console for errors
→ Verify `onCreate` callback is firing
→ Test API directly with curl

### Wrong drawings appearing
→ Check symbol parameter in API calls
→ Verify user_id isolation in database
→ Test with Supabase Table Editor

---

## 📞 Support

If stuck:
1. Check this checklist from the beginning
2. Review standalone test results
3. Check backend logs: `docker-compose logs -f backend`
4. Check Supabase logs: Dashboard → Logs
5. Test API directly with curl/Postman
6. Review README.md for examples
