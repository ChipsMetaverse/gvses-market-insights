# Manual Drawing Remediation Plan — NOV14

**App:** GVSES Market Insights (React + TypeScript, TradingView Lightweight‑Charts v5)

**Scope:** Bring back **manual drawing** (trendline, ray, horizontal) and keep **programmatic drawing** stable; ensure drawings survive re‑renders, pan/zoom, and window resize; provide persistence + tests.

---

## Phase 1 — Render Stability (COMPLETED)

**Goal:** Stop continuous React re‑renders that were breaking/losing drawings.

**Key changes shipped**
- Isolated realtime voice state to an external **voiceBus** (`useSyncExternalStore`).
- Chart created **once** (empty‑dep effect); symbol change only refreshes data.
- Stable options/callbacks (`useMemo`, `useCallback`, `React.memo`).
- Throttled `ResizeObserver` via rAF.
- Removed crosshair → React state writes; use refs/bus instead.

**Acceptance**
- `TradingChart` renders ≤ 1/sec while idle.
- Pan/zoom/resize does not trigger React re‑render storms.

---

## Phase 2 — Drawing Manager (COMPLETED)

**Goal:** Manual + programmatic drawings outside React; perfect snapping to pane; HiDPI.

**Components**
- `DrawingStore` — in‑memory store with subscribe/notify.
- `DrawingOverlay` — pane‑anchored canvas; re‑projects coords on pan/zoom; hit‑test + drag; context menu.
- `ToolboxManager` — hotkeys: **Alt+T** (trendline), **Alt+H** (horizontal), **Alt+R** (ray), **Esc** (cancel), **Delete** (remove selected).
- `enhancedChartControl` — programmatic bridge for agent commands.

**Acceptance**
- Two clicks draw a trendline; one click draws a horizontal; two clicks draw a ray.
- Endpoints draggable (trendline/ray); horizontal line drag‑move; right‑click delete/edit color/style.
- Drawings stay aligned during pan/zoom/resize; crisp on HiDPI.

---

## Phase 3 — UI Integration (Toolbox & Legend)

**Status:** **TO SHIP** — minimal UI to complement hotkeys; no React churn.

### Objectives
1. Add a **ChartToolbar** with tool buttons (Trendline, Ray, Horizontal, Exit).
2. Add a small **Legend/Layer list** to show drawings; toggle visibility; rename; select.
3. Visual feedback: cursor change in drawing mode; live preview while placing second point.

### File adds/changes
- `frontend/src/components/ChartToolbar.tsx` — thin UI → `ToolboxManager.setTool()`
- `frontend/src/components/ChartLegend.tsx` — binds to `DrawingStore` via a read‑only subscription API.
- `frontend/src/components/TradingChart.tsx` — mount toolbar + legend; **no state flowing down from dashboard**.

### Implementation notes
- **No new props** on `TradingChart`; use the already‑mounted `ToolboxManager`/`DrawingStore` created in Phase‑2.
- Legend rows: `name`, color swatch, eye (show/hide), trash (delete). Renaming updates `drawing.name` in store → overlay rerenders.
- Preview line: subscribe to `chart.subscribeCrosshairMove` while a tool is active and draw a transient line from first anchor to crosshair on the overlay; clear on commit/cancel.

### Acceptance
- Toolbar buttons mirror hotkeys and survive re‑renders.
- Legend toggles visibility without removing drawings.
- Rename reflects instantly; selection state apparent.

---

## Phase 4 — Persistence & Backend Integration

**Status:** **TO SHIP** — local per‑symbol cache + optional backend CRUD.

### Local persistence (default)
- Key: `drawings:${symbol}` in `localStorage`.
- On symbol load: `store.import(JSON.parse(localStorage.getItem(key) ?? '[]'))`.
- On change: `beforeunload` (and/or debounced 1s) → `localStorage.setItem(key, JSON.stringify(store.export()))`.

### Backend API (optional; aligns with FastAPI stack)

**Endpoints**
- `POST /api/drawings` → create `{ id, userId?, symbol, kind, params, style, name }`
- `PATCH /api/drawings/{id}` → mutate coords/style/name/visibility
- `DELETE /api/drawings/{id}` → remove
- `GET /api/drawings?symbol=TSLA` → list for symbol (optionally scoped to `userId`)

**Payload shape**
```json
{
  "id": "drw_xxx",
  "symbol": "TSLA",
  "kind": "trendline|ray|horizontal",
  "params": { "a": {"time": 1731569400, "price": 231.25}, "b": {"time": 1731573000, "price": 234.8}, "price": 400 },
  "style": { "color": "#22c55e", "width": 2, "style": "solid|dashed|dotted", "direction": "right|left|both" },
  "name": "Resistance 1",
  "visible": true,
  "userId": "optional"
} I'm sorry