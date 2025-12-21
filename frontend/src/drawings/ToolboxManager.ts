import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { AnyDrawing, Horizontal, Ray, Trendline, Tp, uid } from './types';
import { DrawingStore } from './DrawingStore';

export type Tool = 'none' | 'trendline' | 'ray' | 'horizontal';

export function createToolbox(opts: {
  chart: IChartApi;
  series: ISeriesApi<'Candlestick'>;
  container: HTMLElement;
  store: DrawingStore;
  onCreate?: (d: AnyDrawing)=>void;
  onUpdate?: (d: AnyDrawing)=>void;   // forwarded from overlay
  onDelete?: (id: string)=>void;      // forwarded from overlay
}) {
  const { chart, series, container, store } = opts;
  let active: Tool = 'none';
  let first: Tp | null = null;
  let previewId: string | null = null;

  // Enable keyboard events on container
  container.tabIndex = 0;
  container.focus();

  function setTool(t: Tool) {
    active = t;
    first = null;
    // Clear any preview
    if (previewId) {
      store.remove(previewId);
      previewId = null;
    }
    container.style.cursor = (t === 'none') ? 'default' : 'crosshair';
  }

  function handleCrosshairMove(param: any) {
    // Only show preview when we have a first point
    if (!first || active === 'none') return;
    if (!param?.point?.x || !param?.point?.y) {
      // Mouse left chart area - keep last preview
      return;
    }

    // Use exact pixel coordinates without grid snapping
    const time = chart.timeScale().coordinateToTime(param.point.x) as Time;
    const price = series.coordinateToPrice(param.point.y) as number | null;
    if (time == null || price == null) return;

    // Crosshair position logging (per video tutorial)
    if (param.time !== undefined) {
      console.log('Crosshair Time:', param.time, 'Price:', price);
    } else if (param.logical !== undefined) {
      console.log('Crosshair Logical:', param.logical, 'Price:', price);
    }

    const tp: Tp = { time, price };

    // Update preview drawing
    if (active === 'trendline') {
      const preview: Trendline = {
        id: previewId || uid('preview'),
        kind: 'trendline',
        a: first,
        b: tp,
        width: 1,
        style: 'dotted',
        color: '#2196F3',  // Blue preview line (matches standalone implementation)
      };
      if (!previewId) previewId = preview.id;
      store.upsert(preview);
    } else if (active === 'ray') {
      const preview: Ray = {
        id: previewId || uid('preview'),
        kind: 'ray',
        a: first,
        b: tp,
        width: 1,
        style: 'dotted',
        color: '#888',
        direction: 'right',
      };
      if (!previewId) previewId = preview.id;
      store.upsert(preview);
    }
    // Note: Horizontal line preview is NOT updated during mouse movement
    // It stays at the first click position until second click finalizes it
  }

  function handleClick(param: any) {
    if (active === 'none') return;
    if (param.point?.x === undefined || param.point?.y === undefined) return;

    // Use exact pixel coordinates without grid snapping
    const time = chart.timeScale().coordinateToTime(param.point.x) as Time;
    const price = series.coordinateToPrice(param.point.y) as number | null;
    if (time == null || price == null) return;

    const tp: Tp = { time, price };

    // If this is the first click, set the first point and show preview
    if (!first) {
      first = tp;

      // For horizontal line, show preview at clicked price
      if (active === 'horizontal') {
        const preview: Horizontal = {
          id: uid('preview'),
          kind: 'horizontal',
          price: price,
          width: 1,
          style: 'dotted',
          color: '#888',
          draggable: false,
        };
        previewId = preview.id;
        store.upsert(preview);
      }
      return;
    }

    // Second click - remove preview and create final drawing
    if (previewId) {
      store.remove(previewId);
      previewId = null;
    }

    if (active === 'horizontal') {
      const d: Horizontal = { id: uid('h'), kind: 'horizontal', price: tp.price, width: 2, style: 'dashed', color: '#888', draggable: true };
      store.upsert(d); opts.onCreate?.(d);
    } else if (active === 'trendline') {
      const d: Trendline = { id: uid('tl'), kind:'trendline', a:first, b:tp, width:2, style:'solid', color:'#22c55e' };
      store.upsert(d); opts.onCreate?.(d);
    } else if (active === 'ray') {
      const d: Ray = { id: uid('ray'), kind:'ray', a:first, b:tp, width:2, style:'dashed', color:'#1e90ff', direction:'right' };
      store.upsert(d); opts.onCreate?.(d);
    }

    first = null;
    setTool('none');
  }

  chart.subscribeClick(handleClick);
  chart.subscribeCrosshairMove(handleCrosshairMove);

  function onKey(e: KeyboardEvent) {
    console.log('🎹 Keyboard event:', e.key, 'Alt:', e.altKey);
    if (e.altKey && (e.key === 't' || e.key === 'T')) {
      console.log('✅ Activating trendline tool');
      setTool('trendline'); e.preventDefault();
    }
    if (e.altKey && (e.key === 'h' || e.key === 'H')) {
      console.log('✅ Activating horizontal tool');
      setTool('horizontal'); e.preventDefault();
    }
    if (e.altKey && (e.key === 'r' || e.key === 'R')) {
      console.log('✅ Activating ray tool');
      setTool('ray'); e.preventDefault();
    }
    if (e.key === 'Escape') {
      console.log('✅ Deactivating drawing tool');
      setTool('none');
    }
    if (e.key === 'Delete' || e.key === 'Backspace') {
      const sel = store.all().find(d => d.selected);
      if (sel) {
        e.preventDefault();  // Prevent browser back navigation on Backspace
        console.log('✅ Deleting drawing:', sel.id);
        store.remove(sel.id); opts.onDelete?.(sel.id);
      }
    }
  }
  container.addEventListener('keydown', onKey);

  const unsubStore = store.subscribe(() => {/* selection changes handled by overlay */});

  return {
    setTool,
    destroy() {
      unsubStore();
      chart.unsubscribeClick(handleClick);
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      container.removeEventListener('keydown', onKey);
      setTool('none');
    }
  };
}
