# 🎨 Drawing Persistence System - Standalone Test Environment

Complete, production-ready drawing persistence system for GVSES Trading Platform. Built with FastAPI + Supabase matching your exact stack.

## 📋 Features

✅ **Complete CRUD API**
- Create, read, update, delete drawings
- Batch operations
- Filtering by symbol and kind
- Pagination support

✅ **Three Drawing Types**
- **Trendlines**: Two-point lines with time/price anchoring
- **Rays**: Lines extending infinitely in specified direction
- **Horizontal**: Price levels with optional rotation

✅ **Production Features**
- Row-level security (RLS) with Supabase
- Automatic timestamps
- Input validation with Pydantic
- Coordinate validation matching TypeScript types
- User isolation

✅ **Developer Experience**
- Interactive API docs at `/docs`
- Comprehensive test suite (20+ tests)
- Type-safe models
- Clear error messages

---

## 🚀 Quick Start

### 1. Set Up Supabase

```bash
# Go to https://supabase.com/dashboard
# Create a new project or use existing one

# Go to SQL Editor and run schema.sql:
cat schema.sql
# Copy and paste into SQL Editor, click Run
```

**Verify tables created:**
- Go to Table Editor
- Should see `drawings` table with proper columns

### 2. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
```

**Get credentials from:**
- Settings → API → Project URL
- Settings → API → Project API keys → anon public

### 3. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Start Server

```bash
python3 server.py
```

**Server running at:**
- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

### 5. Run Tests

```bash
# With server running in another terminal
python3 -m pytest test_api.py -v

# Or run directly
python3 test_api.py
```

---

## 📚 API Documentation

### Core Endpoints

#### Create Drawing
```http
POST /api/drawings
Content-Type: application/json

{
  "symbol": "TSLA",
  "kind": "trendline",
  "name": "Support Line",
  "color": "#22c55e",
  "width": 2,
  "style": "solid",
  "coordinates": {
    "a": {"time": 1609459200, "price": 700},
    "b": {"time": 1612137600, "price": 850}
  }
}
```

**Response:** `201 Created`
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "...",
  "symbol": "TSLA",
  "kind": "trendline",
  "name": "Support Line",
  "visible": true,
  "selected": false,
  "color": "#22c55e",
  "width": 2,
  "style": "solid",
  "coordinates": {...},
  "created_at": "2025-01-27T10:00:00Z",
  "updated_at": "2025-01-27T10:00:00Z"
}
```

#### List Drawings
```http
GET /api/drawings?symbol=TSLA&kind=trendline&page=1&page_size=100
```

**Response:** `200 OK`
```json
{
  "drawings": [...],
  "total": 42,
  "page": 1,
  "page_size": 100
}
```

#### Get Single Drawing
```http
GET /api/drawings/{drawing_id}
```

#### Update Drawing
```http
PATCH /api/drawings/{drawing_id}
Content-Type: application/json

{
  "color": "#ef4444",
  "visible": false,
  "coordinates": {
    "a": {"time": 1609459200, "price": 750},
    "b": {"time": 1612137600, "price": 900}
  }
}
```

#### Delete Drawing
```http
DELETE /api/drawings/{drawing_id}
```

**Response:** `204 No Content`

#### Bulk Delete
```http
DELETE /api/drawings?symbol=TSLA&kind=trendline
```

#### Batch Create
```http
POST /api/drawings/batch
Content-Type: application/json

[
  {drawing1},
  {drawing2},
  {drawing3}
]
```

#### Statistics
```http
GET /api/drawings/stats/summary
```

**Response:**
```json
{
  "total_drawings": 150,
  "symbols_with_drawings": 12,
  "drawings_by_kind": {
    "trendline": 85,
    "horizontal": 45,
    "ray": 20
  },
  "last_drawing_created": "2025-01-27T15:30:00Z"
}
```

---

## 🧪 Testing

### Run All Tests
```bash
python3 -m pytest test_api.py -v
```

### Run Specific Test
```bash
python3 -m pytest test_api.py::test_create_trendline -v
```

### Test Coverage
The test suite covers:
- ✅ Health checks
- ✅ Create operations (all drawing types)
- ✅ Input validation
- ✅ List/filter operations
- ✅ Get single drawing
- ✅ Update operations
- ✅ Delete operations
- ✅ Bulk operations
- ✅ Statistics
- ✅ Error cases (404, 422)

---

## 📦 Drawing Types

### Trendline
```json
{
  "kind": "trendline",
  "coordinates": {
    "a": {"time": 1609459200, "price": 700},
    "b": {"time": 1612137600, "price": 850}
  }
}
```

### Ray
```json
{
  "kind": "ray",
  "coordinates": {
    "a": {"time": 1609459200, "price": 700},
    "b": {"time": 1612137600, "price": 850},
    "direction": "right"  // "left", "right", or "both"
  }
}
```

### Horizontal
```json
{
  "kind": "horizontal",
  "coordinates": {
    "price": 800,
    "rotation": 45,  // Optional: 0-360 degrees
    "t0": 1609459200,  // Optional: start time bound
    "t1": 1612137600,  // Optional: end time bound
    "draggable": true
  }
}
```

---

## 🔧 Troubleshooting

### Server won't start
```bash
# Check environment variables
python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('URL:', os.getenv('SUPABASE_URL')); print('KEY:', os.getenv('SUPABASE_ANON_KEY')[:20] + '...')"

# Should print your Supabase URL and key prefix
```

### Tests failing
```bash
# Verify server is running
curl http://localhost:8001/health

# Check Supabase connection
curl http://localhost:8001/api/drawings/health

# Run single test with verbose output
python3 -m pytest test_api.py::test_health_check -v -s
```

### Database errors
1. Verify schema.sql was applied successfully in Supabase
2. Check RLS policies are enabled
3. Verify anon key has correct permissions
4. Check Table Editor shows `drawings` table

---

## 🔗 Integration Guide

### Phase 1: Backend Integration

1. **Copy files to main backend:**
```bash
# From standalone-drawing-persistence/
cp models.py ../backend/models/drawing_models.py
cp api.py ../backend/routers/drawings.py
```

2. **Update main FastAPI app:**
```python
# backend/mcp_server.py
from routers.drawings import router as drawings_router

app.include_router(drawings_router)
```

3. **Verify:**
```bash
curl http://localhost:8000/api/drawings/health
```

### Phase 2: Frontend Integration

1. **Create service:**
```typescript
// frontend/src/services/drawingPersistenceService.ts
export const drawingPersistenceService = {
  async saveDrawing(drawing: AnyDrawing) {
    const response = await fetch('/api/drawings', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(drawing)
    })
    return response.json()
  },

  async loadDrawings(symbol: string) {
    const response = await fetch(`/api/drawings?symbol=${symbol}`)
    const data = await response.json()
    return data.drawings
  },

  async updateDrawing(id: string, updates: Partial<AnyDrawing>) {
    const response = await fetch(`/api/drawings/${id}`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(updates)
    })
    return response.json()
  },

  async deleteDrawing(id: string) {
    await fetch(`/api/drawings/${id}`, {method: 'DELETE'})
  }
}
```

2. **Wire up TradingChart callbacks:**
```typescript
// frontend/src/components/TradingChart.tsx
overlayRef.current = createDrawingOverlay({
  chart,
  series: candlestickSeries,
  container: chartContainerRef.current,
  store,
  onCreate: async (d) => {
    const saved = await drawingPersistenceService.saveDrawing(d)
    d.id = saved.id  // Update with server ID
  },
  onUpdate: async (d) => {
    await drawingPersistenceService.updateDrawing(d.id, d)
  },
  onDelete: async (id) => {
    await drawingPersistenceService.deleteDrawing(id)
  },
})
```

3. **Load on symbol change:**
```typescript
useEffect(() => {
  const loadDrawings = async () => {
    const drawings = await drawingPersistenceService.loadDrawings(symbol)
    store.import(drawings)
  }
  loadDrawings()
}, [symbol])
```

### Phase 3: Testing Integration

```bash
# Test complete flow
cd frontend && npm run dev
# 1. Draw a trendline on chart
# 2. Refresh page
# 3. Verify trendline persists
# 4. Switch symbols
# 5. Switch back - trendline should reload
```

---

## 📊 Database Schema

```sql
drawings (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,  -- FK to auth.users
  symbol VARCHAR(20),
  kind VARCHAR(20),       -- 'trendline' | 'ray' | 'horizontal'
  name VARCHAR(255),
  visible BOOLEAN,
  selected BOOLEAN,
  color VARCHAR(7),       -- Hex code
  width INTEGER,          -- 1-10px
  style VARCHAR(20),      -- 'solid' | 'dashed' | 'dotted'
  coordinates JSONB,      -- Time/price data
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
)
```

**Indexes:**
- `(user_id, symbol)` - Fast symbol filtering
- `(user_id, created_at DESC)` - Recent drawings
- `(kind)` - Type filtering

**RLS Policies:**
- Users can only see/modify their own drawings
- Automatic user_id enforcement

---

## ✨ Next Steps

1. ✅ Run `python3 server.py` to start standalone server
2. ✅ Run `python3 test_api.py` to verify all tests pass
3. ✅ Test with curl or Postman
4. ✅ Integrate into main application using guide above
5. ✅ Deploy to production

---

## 📄 License

MIT - Part of GVSES Trading Platform

## 🤝 Support

Questions? Check:
- API Docs: http://localhost:8001/docs
- Main project: ../CLAUDE.md
- Supabase docs: https://supabase.com/docs
