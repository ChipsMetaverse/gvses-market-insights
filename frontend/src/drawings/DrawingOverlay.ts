import type { IChartApi, ISeriesApi, Time } from 'lightweight-charts';
import { AnyDrawing, Horizontal, Ray, Trendline, Tp, normalizeStyle } from './types';
import { DrawingStore } from './DrawingStore';

type Px = number;
type Pt = { x: Px; y: Px };

function lineDash(style: 'solid'|'dashed'|'dotted') {
  if (style === 'dashed') return [8,6];
  if (style === 'dotted') return [2,4];
  return [];
}

export function createDrawingOverlay(opts: {
  chart: IChartApi;
  series: ISeriesApi<'Candlestick'|'Line'|'Area'|'Baseline'|'Histogram'|'Bar'>;
  container: HTMLElement;
  store: DrawingStore;
  // optional callbacks
  onUpdate?: (d: AnyDrawing) => void;
  onDelete?: (id: string) => void;
}) {
  const { chart, series, container, store } = opts;

  // Canvas aligned to pane content area
  const overlay = document.createElement('canvas');
  overlay.style.position = 'absolute';
  overlay.style.left = '0';
  overlay.style.top = '0';
  overlay.style.pointerEvents = 'none'; // let chart receive events; we attach listeners to container
  overlay.style.zIndex = '3';
  container.appendChild(overlay);

  const menu = document.createElement('div');
  Object.assign(menu.style, {
    position: 'absolute',
    display: 'none',
    background: '#111',
    color: '#fff',
    fontSize: '12px',
    borderRadius: '6px',
    padding: '6px',
    zIndex: '4',
    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
  } as CSSStyleDeclaration);
  container.appendChild(menu);

  const ctx = overlay.getContext('2d')!;
  let dpr = Math.max(1, window.devicePixelRatio || 1);
  let left = 0, top = 0, width = 1, height = 1;

  function paneRect() {
    const outer = container.getBoundingClientRect();
    // first canvas inside container is pane's drawing area parent
    const paneCanvas = container.querySelector('canvas') as HTMLCanvasElement | null;
    const paneEl = (paneCanvas?.parentElement as HTMLElement) || container;
    const r = paneEl.getBoundingClientRect?.() ?? outer;
    left = Math.round(r.left - outer.left);
    top  = Math.round(r.top  - outer.top);
    width  = Math.max(1, Math.floor(r.width));
    height = Math.max(1, Math.floor(r.height));
  }

  function relayout() {
    dpr = Math.max(1, window.devicePixelRatio || 1);
    paneRect();
    overlay.style.left = `${left}px`;
    overlay.style.top  = `${top}px`;
    overlay.style.width  = `${width}px`;
    overlay.style.height = `${height}px`;
    overlay.width  = Math.floor(width * dpr);
    overlay.height = Math.floor(height * dpr);
    redraw();
  }

  const ro = new ResizeObserver(relayout);
  ro.observe(container);

  // Subscribe to chart events (cleanup handled by chart disposal)
  chart.timeScale().subscribeVisibleLogicalRangeChange(() => redraw());
  chart.subscribeCrosshairMove(() => redraw());

  // repaint loop for price-scale zoom drags
  let raf: number | null = null, lastKick = 0;
  const kick = () => {
    lastKick = performance.now();
    if (raf) return;
    const loop = () => {
      const now = performance.now();
      if (now - lastKick > 250) { raf = null; return; }
      redraw(); raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
  };
  ['wheel', 'mousedown', 'mousemove', 'mouseup', 'touchstart', 'touchmove', 'touchend']
    .forEach(ev => container.addEventListener(ev, kick, { passive: true }));

  function tpToPx(t: Time, price: number): Pt | null {
    const x = chart.timeScale().timeToCoordinate(t);
    const y = series.priceToCoordinate(price);
    if (x == null || y == null) return null;
    return { x: (x - left) * dpr, y: (y - top) * dpr };
  }

  function pxToTime(x: number): Time | null {
    const coord = (x / dpr) + left;
    // Convert pixel coordinate to time using chart's built-in method (free-range placement)
    return chart.timeScale().coordinateToTime(coord);
  }

  function pxToPrice(y: number): number | null {
    const coord = (y / dpr) + top;
    return series.coordinateToPrice(coord) as number | null;
  }

  function drawLine(p1: Pt, p2: Pt, color: string, widthPx: number, style: 'solid'|'dashed'|'dotted') {
    ctx.save();
    ctx.strokeStyle = color;
    ctx.lineWidth = Math.max(1, widthPx) * dpr;
    ctx.setLineDash(lineDash(style));
    ctx.beginPath(); ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
    ctx.restore();
  }
  function handleDot(p: Pt, selected: boolean) {
    ctx.save();
    ctx.fillStyle = selected ? '#1e90ff' : '#333';
    ctx.beginPath(); ctx.arc(p.x, p.y, 4 * dpr, 0, Math.PI*2); ctx.fill();
    ctx.restore();
  }

  function renderTrend(d: Trendline) {
    const s = normalizeStyle(d);
    const p1 = tpToPx(d.a.time, d.a.price), p2 = tpToPx(d.b.time, d.b.price);
    if (!p1 || !p2) return;
    drawLine(p1, p2, s.color, s.width, s.style);
    if (d.selected) { handleDot(p1, true); handleDot(p2, true); }
  }
  function renderRay(d: Ray) {
    const s = normalizeStyle(d);
    const a = tpToPx(d.a.time, d.a.price), b = tpToPx(d.b.time, d.b.price);
    if (!a || !b) return;
    const dx = b.x - a.x, dy = b.y - a.y;
    if (Math.abs(dx) < 1e-6) {
      drawLine({x: a.x, y: 0}, {x: a.x, y: overlay.height}, s.color, s.width, s.style);
    } else {
      const m = dy / dx, c = a.y - m * a.x;
      const segs: [Pt,Pt][] = [];
      const dir = d.direction ?? 'right';
      if (dir === 'right' || dir === 'both') segs.push([a, { x: overlay.width, y: m*overlay.width + c }]);
      if (dir === 'left'  || dir === 'both') segs.push([{ x: 0, y: c }, a]);
      for (const [p1,p2] of segs) drawLine(p1, p2, s.color, s.width, s.style);
    }
    if (d.selected) { handleDot(a, true); handleDot(b, true); }
  }
  function drawRotationHandle(centerX: number, centerY: number, rotation: number) {
    // Draw rotation pivot point
    ctx.save();
    ctx.fillStyle = '#1e90ff';
    ctx.beginPath();
    ctx.arc(centerX, centerY, 6 * dpr, 0, Math.PI * 2);
    ctx.fill();

    // Draw rotation handle at 50px radius
    const handleRadius = 50 * dpr;
    const angle = (rotation * Math.PI) / 180;
    const handleX = centerX + handleRadius * Math.cos(angle);
    const handleY = centerY + handleRadius * Math.sin(angle);

    // Line from center to handle
    ctx.strokeStyle = '#1e90ff';
    ctx.lineWidth = 1 * dpr;
    ctx.setLineDash([4 * dpr, 4 * dpr]);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(handleX, handleY);
    ctx.stroke();

    // Handle circle
    ctx.fillStyle = '#1e90ff';
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(handleX, handleY, 8 * dpr, 0, Math.PI * 2);
    ctx.fill();

    // Rotation angle display
    ctx.fillStyle = '#1e90ff';
    ctx.font = `${12 * dpr}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.fillText(`${Math.round(rotation)}°`, centerX, centerY - 15 * dpr);
    ctx.restore();
  }

  function renderHorizontal(d: Horizontal) {
    const s = normalizeStyle(d);
    const rotation = d.rotation ?? 0;
    const y = series.priceToCoordinate(d.price);
    if (y == null) return;
    const yy = (y - top) * dpr;

    const centerX = overlay.width / 2;
    const centerY = yy;

    // Use blue color and thicker line when selected
    const lineColor = d.selected ? '#1e90ff' : s.color;
    const lineWidth = d.selected ? s.width + 1 : s.width;

    if (rotation !== 0) {
      ctx.save();
      ctx.translate(centerX, centerY);
      ctx.rotate((rotation * Math.PI) / 180);
      ctx.translate(-centerX, -centerY);
      drawLine({x: 0, y: yy}, {x: overlay.width, y: yy}, lineColor, lineWidth, s.style);
      ctx.restore();
    } else {
      drawLine({x: 0, y: yy}, {x: overlay.width, y: yy}, lineColor, lineWidth, s.style);
    }

    // Draw selection handles at edges when selected
    if (d.selected) {
      const handleRadius = 6 * dpr;
      ctx.fillStyle = '#1e90ff';
      // Left handle
      ctx.beginPath();
      ctx.arc(50 * dpr, yy, handleRadius, 0, Math.PI * 2);
      ctx.fill();
      // Right handle
      ctx.beginPath();
      ctx.arc(overlay.width - 50 * dpr, yy, handleRadius, 0, Math.PI * 2);
      ctx.fill();
      // Center pivot
      ctx.beginPath();
      ctx.arc(centerX, yy, handleRadius, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw rotation handle when selected and rotated
    if (d.selected && rotation !== 0) {
      drawRotationHandle(centerX, centerY, rotation);
    }
  }

  function redraw() {
    ctx.clearRect(0, 0, overlay.width, overlay.height);
    for (const d of store.all()) {
      if (d.visible === false) continue;
      if (d.kind === 'trendline')   renderTrend(d);
      else if (d.kind === 'ray')    renderRay(d);
      else if (d.kind === 'horizontal') renderHorizontal(d as Horizontal);
    }
  }

  // --- hit test & drag
  function distPointToSegment(p: Pt, a: Pt, b: Pt) {
    const vx = b.x - a.x, vy = b.y - a.y;
    const wx = p.x - a.x, wy = p.y - a.y;
    const c1 = vx*wx + vy*wy;
    if (c1 <= 0) return Math.hypot(p.x - a.x, p.y - a.y);
    const c2 = vx*vx + vy*vy;
    if (c2 <= c1) return Math.hypot(p.x - b.x, p.y - b.y);
    const t = c1 / c2;
    const px = a.x + t*vx, py = a.y + t*vy;
    return Math.hypot(p.x - px, p.y - py);
  }

  function distPointToRotatedHorizontalLine(p: Pt, centerX: number, centerY: number, rotation: number, width: number): number {
    // Inverse rotate the point back to horizontal orientation
    const angleRad = -(rotation * Math.PI) / 180; // Negative for inverse rotation
    const dx = p.x - centerX;
    const dy = p.y - centerY;
    const rotatedX = dx * Math.cos(angleRad) - dy * Math.sin(angleRad);
    const rotatedY = dx * Math.sin(angleRad) + dy * Math.cos(angleRad);

    // Now the line is horizontal at y=0, calculate perpendicular distance
    const lineY = 0;
    const distY = Math.abs(rotatedY - lineY);

    // Check if point is within line bounds horizontally
    const halfWidth = width / 2;
    if (rotatedX < -halfWidth || rotatedX > halfWidth) {
      // Point is outside line bounds, return distance to nearest endpoint
      if (rotatedX < -halfWidth) {
        return Math.hypot(rotatedX + halfWidth, rotatedY - lineY);
      } else {
        return Math.hypot(rotatedX - halfWidth, rotatedY - lineY);
      }
    }

    return distY;
  }

  function findHit(x: number, y: number): { id: string; handle?: 'a'|'b'|'line'|'rotate' } | null {
    const p: Pt = { x: x * dpr, y: y * dpr };
    const r = 8 * dpr;

    // prefer handles
    for (const d of store.all()) {
      if (d.kind === 'trendline' || d.kind === 'ray') {
        const a = tpToPx(d.a.time, d.a.price), b = tpToPx(d.b.time, d.b.price);
        if (!a || !b) continue;
        if (Math.hypot(p.x - a.x, p.y - a.y) <= r) return { id: d.id, handle: 'a' };
        if (Math.hypot(p.x - b.x, p.y - b.y) <= r) return { id: d.id, handle: 'b' };
      }
      if (d.kind === 'horizontal') {
        const hd = d as Horizontal;
        const rotation = hd.rotation ?? 0;
        const yLine = series.priceToCoordinate(hd.price);
        if (yLine == null) continue;
        const yy = (yLine - top) * dpr;
        const centerX = overlay.width / 2;
        const centerY = yy;

        // Check rotation handle first (if rotated and selected)
        if (rotation !== 0 && d.selected) {
          const handleRadius = 50 * dpr;
          const angle = (rotation * Math.PI) / 180;
          const handleX = centerX + handleRadius * Math.cos(angle);
          const handleY = centerY + handleRadius * Math.sin(angle);
          if (Math.hypot(p.x - handleX, p.y - handleY) <= r) {
            return { id: d.id, handle: 'rotate' };
          }
          // Check center pivot
          if (Math.hypot(p.x - centerX, p.y - centerY) <= r) {
            return { id: d.id, handle: 'line' };
          }
        }

        // Check line itself (increased tolerance to 10px for easier selection)
        if (rotation !== 0) {
          const dist = distPointToRotatedHorizontalLine(p, centerX, centerY, rotation, overlay.width);
          if (dist <= 10 * dpr) return { id: d.id, handle: 'line' };
        } else {
          if (Math.abs(y - (yLine - top)) <= 10) return { id: d.id, handle: 'line' };
        }
      }
    }

    // then near segments
    let best: { id: string } | null = null, bestDist = Infinity;
    for (const d of store.all()) {
      if (d.kind === 'trendline' || d.kind === 'ray') {
        const a = tpToPx(d.a.time, d.a.price), b = tpToPx(d.b.time, d.b.price);
        if (!a || !b) continue;
        const dis = distPointToSegment(p, a, b);
        if (dis < bestDist && dis <= r) { bestDist = dis; best = { id: d.id }; }
      }
    }
    return best;
  }

  // drag state
  let drag: null | { id: string; handle?: 'a'|'b'|'line'|'rotate'; startX?: number; startY?: number; startA?: Tp; startB?: Tp } = null;
  let prevScroll = { handleScroll: true, handleScale: true };

  function disableChartInteractions() {
    prevScroll = { handleScroll: (chart as any).options().handleScroll ?? true, handleScale: (chart as any).options().handleScale ?? true };
    chart.applyOptions({ handleScroll: false, handleScale: false });
  }
  function restoreChartInteractions() {
    chart.applyOptions({ handleScroll: prevScroll.handleScroll, handleScale: prevScroll.handleScale });
  }

  // attach to container so chart remains interactive; we'll disable during drag
  container.addEventListener('mousedown', (e) => {
    if (e.button === 2) return; // context menu elsewhere
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left - left;
    const y = e.clientY - rect.top  - top;
    const hit = findHit(x, y);

    if (hit) {
      const drawing = store.get(hit.id);
      // Don't intercept clicks on preview drawings (they're for tool creation)
      if (drawing && drawing.id.startsWith('preview')) {
        return; // Let the click pass through to chart for tool completion
      }

      console.log('🎯 Drawing selected:', hit.id, 'Type:', drawing?.kind, 'Handle:', hit.handle);
      store.select(hit.id);

      // Store initial drag state for moving whole line
      if (drawing && (drawing.kind === 'trendline' || drawing.kind === 'ray') && !hit.handle) {
        drag = {
          id: hit.id,
          handle: 'line',
          startX: x,
          startY: y,
          startA: { ...drawing.a },
          startB: { ...drawing.b }
        };
      } else {
        drag = hit;
      }

      disableChartInteractions();
      e.preventDefault();
      e.stopPropagation(); // Prevent chart click handler from firing
      redraw();
    } else {
      console.log('❌ No drawing hit - deselecting all');
      store.select(undefined);
      redraw();
    }
  }, true); // Use capture phase to intercept before chart handlers

  container.addEventListener('mousemove', (e) => {
    if (!drag) return;
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left - left;
    const y = e.clientY - rect.top  - top;

    const d = store.get(drag.id)!;
    if (d.kind === 'trendline' || d.kind === 'ray') {
      if (drag.handle === 'line' && drag.startX !== undefined && drag.startY !== undefined && drag.startA && drag.startB) {
        // Move entire line - calculate offset from drag start
        const currentT = pxToTime(x * dpr);
        const currentP = pxToPrice(y * dpr);
        const startT = pxToTime(drag.startX * dpr);
        const startP = pxToPrice(drag.startY * dpr);

        if (currentT !== null && currentP !== null && startT !== null && startP !== null) {
          const deltaT = (currentT as number) - (startT as number);
          const deltaP = currentP - startP;

          // Move both endpoints by the same offset
          d.a = {
            time: ((drag.startA.time as number) + deltaT) as Time,
            price: drag.startA.price + deltaP
          };
          d.b = {
            time: ((drag.startB.time as number) + deltaT) as Time,
            price: drag.startB.price + deltaP
          };
          store.upsert(d);
          opts.onUpdate?.(d);
        }
      } else {
        // Move individual endpoint
        const target = drag.handle === 'b' ? 'b' : 'a';
        const t = pxToTime(x * dpr), p = pxToPrice(y * dpr);
        if (t != null && p != null) {
          (d as any)[target] = { time: t, price: p };
          store.upsert(d); opts.onUpdate?.(d);
        }
      }
    } else if (d.kind === 'horizontal') {
      const hd = d as Horizontal;
      if (drag.handle === 'line') {
        // Move horizontal line vertically
        const p = pxToPrice(y * dpr);
        if (p != null) { hd.price = p; store.upsert(hd); opts.onUpdate?.(hd); }
      } else if (drag.handle === 'rotate') {
        // Rotate horizontal line
        const yLine = series.priceToCoordinate(hd.price);
        if (yLine == null) return;
        const yy = (yLine - top) * dpr;
        const centerX = overlay.width / 2;
        const centerY = yy;

        // Calculate angle from center to mouse
        const dx = x * dpr - centerX;
        const dy = y * dpr - centerY;
        const angleRad = Math.atan2(dy, dx);
        let angleDeg = (angleRad * 180) / Math.PI;

        // Normalize to 0-360
        if (angleDeg < 0) angleDeg += 360;

        hd.rotation = angleDeg;
        store.upsert(hd);
        opts.onUpdate?.(hd);
      }
    }
    redraw();
  });

  function hideMenu() { menu.style.display = 'none'; menu.innerHTML = ''; }

  container.addEventListener('mouseup', () => {
    drag = null;
    restoreChartInteractions();
  });

  container.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const rect = container.getBoundingClientRect();
    const x = e.clientX - rect.left - left;
    const y = e.clientY - rect.top  - top;
    const hit = findHit(x, y);
    if (!hit) { hideMenu(); return; }

    const d = store.get(hit.id)!;
    store.select(hit.id); redraw();

    // Build context menu with rotation slider for horizontal lines
    const rotationControl = d.kind === 'horizontal' ? `
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">
        <span style="min-width:60px">Rotation:</span>
        <input type="range" min="0" max="360" value="${(d as Horizontal).rotation ?? 0}"
               data-rotation="1" style="flex:1;accent-color:#1e90ff">
        <span data-rotation-display style="min-width:35px;text-align:right">${Math.round((d as Horizontal).rotation ?? 0)}°</span>
      </div>
    ` : '';

    menu.innerHTML = `
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">Color:
        <button data-col="#22c55e" style="width:14px;height:14px;background:#22c55e;border:0;border-radius:2px"></button>
        <button data-col="#1e90ff" style="width:14px;height:14px;background:#1e90ff;border:0;border-radius:2px"></button>
        <button data-col="#ffa500" style="width:14px;height:14px;background:#ffa500;border:0;border-radius:2px"></button>
        <button data-col="#ef4444" style="width:14px;height:14px;background:#ef4444;border:0;border-radius:2px"></button>
      </div>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:6px">Style:
        <button data-style="solid">Solid</button>
        <button data-style="dashed">Dashed</button>
        <button data-style="dotted">Dotted</button>
      </div>
      ${rotationControl}
      <div><button data-del="1" style="color:#ff6b6b;background:#222;padding:4px 8px;border-radius:4px">Delete</button></div>
    `;

    const applyColor = (col: string) => { (d as any).color = col; store.upsert(d); opts.onUpdate?.(d); redraw(); };
    const applyStyle = (st: string) => { (d as any).style = st; store.upsert(d); opts.onUpdate?.(d); redraw(); };
    const del = () => { store.remove(d.id); opts.onDelete?.(d.id); hideMenu(); redraw(); };

    menu.querySelectorAll('button[data-col]').forEach(b => b.addEventListener('click', () => applyColor((b as HTMLButtonElement).dataset.col!)));
    menu.querySelectorAll('button[data-style]').forEach(b => b.addEventListener('click', () => applyStyle((b as HTMLButtonElement).dataset.style!)));
    (menu.querySelector('button[data-del]') as HTMLButtonElement).addEventListener('click', del);

    // Rotation slider handler
    const rotationSlider = menu.querySelector('input[data-rotation]') as HTMLInputElement | null;
    if (rotationSlider && d.kind === 'horizontal') {
      const display = menu.querySelector('[data-rotation-display]') as HTMLSpanElement;
      rotationSlider.addEventListener('input', () => {
        const rotation = parseFloat(rotationSlider.value);
        (d as Horizontal).rotation = rotation;
        display.textContent = `${Math.round(rotation)}°`;
        store.upsert(d);
        opts.onUpdate?.(d);
        redraw();
      });
    }

    menu.style.left = `${e.clientX - rect.left}px`;
    menu.style.top  = `${e.clientY - rect.top}px`;
    menu.style.display = 'block';
  });

  container.addEventListener('click', () => hideMenu());
  const unsubStore = store.subscribe(redraw);

  // initial layout
  relayout();

  return {
    destroy() {
      // Chart event cleanup is handled by chart disposal
      unsubStore();
      ro.disconnect();
      container.removeChild(overlay);
      container.removeChild(menu);
      ['wheel','mousedown','mousemove','mouseup','touchstart','touchmove','touchend','contextmenu','click']
        .forEach(ev => container.removeEventListener(ev, kick as any));
    }
  };
}
