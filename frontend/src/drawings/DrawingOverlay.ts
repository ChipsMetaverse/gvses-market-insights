import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { AnyDrawing, Horizontal, Ray, Trendline, Tp } from './types';
import { DrawingStore } from './DrawingStore';
import { TrendlineHandlePrimitive } from './TrendlineHandlePrimitive';

interface TrendlineVisual {
  primitive: TrendlineHandlePrimitive;
}

export function createDrawingOverlay(opts: {
  chart: IChartApi;
  series: ISeriesApi<'Candlestick'|'Line'|'Area'|'Baseline'|'Histogram'|'Bar'>;
  container: HTMLElement;
  store: DrawingStore;
  onUpdate?: (d: AnyDrawing) => void;
  onDelete?: (id: string) => void;
}) {
  console.log('🎨 DrawingOverlay INITIALIZING with native line series rendering');
  const { chart, series, container, store } = opts;

  // Store line series references (like standalone)
  const trendlines = new Map<string, TrendlineVisual>();

  let drag: { id: string; handle: 'a' | 'b' | 'line'; startX?: number; startY?: number; startA?: Tp; startB?: Tp } | null = null;

  // Helper: Distance from point to line segment (exact standalone implementation)
  function distanceToLineSegment(
    px: number, py: number,
    x1: number, y1: number,
    x2: number, y2: number
  ): number {
    const A = px - x1;
    const B = py - y1;
    const C = x2 - x1;
    const D = y2 - y1;

    const dot = A * C + B * D;
    const lenSq = C * C + D * D;
    let param = -1;

    if (lenSq !== 0) param = dot / lenSq;

    let xx, yy;

    if (param < 0) {
      xx = x1;
      yy = y1;
    } else if (param > 1) {
      xx = x2;
      yy = y2;
    } else {
      xx = x1 + param * C;
      yy = y1 + param * D;
    }

    const dx = px - xx;
    const dy = py - yy;
    return Math.sqrt(dx * dx + dy * dy);
  }

  // Helper: Check if trendline data has changed
  function trendlineDataChanged(existing: Trendline, updated: Trendline): boolean {
    return (
      existing.a.time !== updated.a.time ||
      existing.a.price !== updated.a.price ||
      existing.b.time !== updated.b.time ||
      existing.b.price !== updated.b.price ||
      existing.color !== updated.color ||
      existing.width !== updated.width ||
      existing.selected !== updated.selected
    );
  }

  // Render trendline using v5 custom primitive (optimized to avoid unnecessary recreations)
  function renderTrendline(id: string, drawing: Trendline) {
    const existing = trendlines.get(id);

    if (existing) {
      // Primitive already exists - check if data changed
      const currentData = existing.primitive.getTrendline();

      if (trendlineDataChanged(currentData, drawing)) {
        // Data changed - update existing primitive instead of recreating
        existing.primitive.updateTrendline(drawing);
      }
      // If data hasn't changed, do nothing (avoid unnecessary operations)
    } else {
      // New trendline - create and attach primitive
      const primitive = new TrendlineHandlePrimitive(drawing);
      series.attachPrimitive(primitive);
      trendlines.set(id, { primitive });
    }
  }

  // Delete trendline
  function deleteTrendline(id: string) {
    const visual = trendlines.get(id);
    if (visual) {
      series.detachPrimitive(visual.primitive);
      trendlines.delete(id);
    }
  }

  // Sync all drawings with line series
  function syncDrawings() {
    const all = store.all();
    const currentIds = new Set(all.map(d => d.id));

    // Remove deleted drawings
    for (const id of trendlines.keys()) {
      if (!currentIds.has(id)) {
        deleteTrendline(id);
      }
    }

    // Add/update drawings
    for (const drawing of all) {
      if (drawing.kind === 'trendline') {
        renderTrendline(drawing.id, drawing);
      }
      // TODO: Add ray and horizontal support
    }
  }

  // Subscribe to store changes
  store.subscribe(syncDrawings);

  // Initial render
  syncDrawings();

  // Exact standalone click handler for hit detection
  function disableChartInteractions() {
    chart.applyOptions({ handleScroll: false, handleScale: false });
  }

  function enableChartInteractions() {
    chart.applyOptions({ handleScroll: true, handleScale: true });
  }

  // Click handler with exact standalone hit detection logic
  chart.subscribeClick((param) => {
    console.log('🆕 NEW click handler triggered!', param);
    if (!param.point || !param.time) return;

    const price = series.coordinateToPrice(param.point.y);
    if (price === null) return;

    const clickedTime = param.time as number;
    const clickedPrice = price;
    const clickPointX = param.point.x;
    const clickPointY = param.point.y;

    console.log('🆕 Click coordinates:', { clickedTime, clickedPrice, clickPointX, clickPointY });

    // Dynamic price tolerance (exact standalone logic)
    const pixelTolerance = 30;
    const visiblePriceRange = Math.abs(
      (series.coordinateToPrice(0) || 0) - (series.coordinateToPrice(600) || 0)
    );
    const priceTolerance = (visiblePriceRange / 600) * pixelTolerance;

    // Check handles first (higher priority)
    for (const drawing of store.all()) {
      if (drawing.kind !== 'trendline' && drawing.kind !== 'ray') continue;
      if (drawing.id.startsWith('preview')) continue;

      // Check handle A
      const logicalClickTime = chart.timeScale().timeToCoordinate(clickedTime as Time);
      const logicalHandleA = chart.timeScale().timeToCoordinate(drawing.a.time as Time);

      if (logicalClickTime !== null && logicalHandleA !== null) {
        const logicalTimeDiff = Math.abs(logicalClickTime - logicalHandleA);
        const priceDiff = Math.abs(clickedPrice - drawing.a.price);

        if (logicalTimeDiff < pixelTolerance && priceDiff < priceTolerance) {
          console.log('🎯 Drawing selected:', drawing.id, 'Type:', drawing.kind, 'Handle: a');
          store.select(drawing.id);
          drag = { id: drawing.id, handle: 'a' };
          disableChartInteractions();
          syncDrawings(); // Re-render with selection
          return;
        }
      }

      // Check handle B
      const logicalHandleB = chart.timeScale().timeToCoordinate(drawing.b.time as Time);

      if (logicalClickTime !== null && logicalHandleB !== null) {
        const logicalTimeDiff = Math.abs(logicalClickTime - logicalHandleB);
        const priceDiff = Math.abs(clickedPrice - drawing.b.price);

        if (logicalTimeDiff < pixelTolerance && priceDiff < priceTolerance) {
          console.log('🎯 Drawing selected:', drawing.id, 'Type:', drawing.kind, 'Handle: b');
          store.select(drawing.id);
          drag = { id: drawing.id, handle: 'b' };
          disableChartInteractions();
          syncDrawings(); // Re-render with selection
          return;
        }
      }
    }

    // Check line segments (lower priority)
    const lineClickTolerance = 10; // pixels
    for (const drawing of store.all()) {
      if (drawing.kind !== 'trendline' && drawing.kind !== 'ray') continue;
      if (drawing.id.startsWith('preview')) continue;

      // Convert drawing endpoints to pixel coordinates
      const x1 = chart.timeScale().timeToCoordinate(drawing.a.time as Time);
      const y1 = series.priceToCoordinate(drawing.a.price);
      const x2 = chart.timeScale().timeToCoordinate(drawing.b.time as Time);
      const y2 = series.priceToCoordinate(drawing.b.price);

      if (x1 !== null && y1 !== null && x2 !== null && y2 !== null) {
        const distance = distanceToLineSegment(
          clickPointX,
          clickPointY,
          x1,
          y1,
          x2,
          y2
        );

        if (distance < lineClickTolerance) {
          console.log('🎯 Drawing selected:', drawing.id, 'Type:', drawing.kind, 'Handle: line');
          store.select(drawing.id);
          drag = {
            id: drawing.id,
            handle: 'line',
            startX: clickPointX,
            startY: clickPointY,
            startA: { ...drawing.a },
            startB: { ...drawing.b }
          };
          disableChartInteractions();
          syncDrawings(); // Re-render with selection
          return;
        }
      }
    }

    // No hit - deselect
    console.log('❌ No drawing hit - deselecting all');
    store.select(undefined);
    syncDrawings(); // Re-render without selection
  });

  // Mouse up - end drag
  container.addEventListener('mouseup', () => {
    if (drag) {
      drag = null;
      enableChartInteractions();
      if (opts.onUpdate) {
        const d = store.get(drag?.id || '');
        if (d) opts.onUpdate(d);
      }
    }
  }, true);

  // Cleanup
  function destroy() {
    // Detach all primitives
    for (const visual of trendlines.values()) {
      series.detachPrimitive(visual.primitive);
    }
    trendlines.clear();
  }

  return { destroy };
}
