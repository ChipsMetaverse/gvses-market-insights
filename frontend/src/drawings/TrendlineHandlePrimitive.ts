import type {
  ISeriesPrimitive,
  SeriesAttachedParameter,
  Time,
  IChartApi,
  ISeriesApi,
  AutoscaleInfo,
  Logical,
} from 'lightweight-charts';
import type { Trendline, Tp } from './types';

/**
 * Custom primitive for rendering draggable trendline handles in lightweight-charts v5
 * Implements ISeriesPrimitive to avoid stack overflow from single-point line series
 */
export class TrendlineHandlePrimitive implements ISeriesPrimitive<Time> {
  private _chart: IChartApi | null = null;
  private _series: ISeriesApi<'Candlestick' | 'Line' | 'Area' | 'Baseline' | 'Histogram' | 'Bar'> | null = null;
  private _requestUpdate: (() => void) | null = null;

  private _trendline: Trendline;
  private _paneViews: TrendlinePaneView[];

  // Handle interaction state
  private _hoveredHandle: 'a' | 'b' | 'line' | null = null;

  constructor(trendline: Trendline) {
    this._trendline = trendline;
    this._paneViews = [new TrendlinePaneView(this)];
  }

  // Lifecycle methods
  attached(param: SeriesAttachedParameter<Time>): void {
    this._chart = param.chart;
    this._series = param.series;
    this._requestUpdate = param.requestUpdate;
  }

  detached(): void {
    this._chart = null;
    this._series = null;
    this._requestUpdate = null;
  }

  // View providers
  paneViews() {
    return this._paneViews;
  }

  // Update methods
  updateAllViews(): void {
    this._paneViews.forEach(view => view.update());
  }

  requestUpdate(): void {
    if (this._requestUpdate) {
      this._requestUpdate();
    }
  }

  // Autoscale integration - provides price range to chart for proper scaling
  autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo | null {
    // Performance optimization: Quick validation
    if (!this._chart || !this._series) {
      return null;
    }

    // Get logical coordinates for trendline endpoints
    const logicalA = this._chart.timeScale().timeToCoordinate(this._trendline.a.time as Time);
    const logicalB = this._chart.timeScale().timeToCoordinate(this._trendline.b.time as Time);

    // If both points are outside visible range, don't affect autoscale
    if (logicalA === null && logicalB === null) {
      return null;
    }

    // Check if trendline intersects with visible range
    // Only include in autoscale if at least part of it is visible
    const minLogical = Math.min(
      logicalA !== null ? logicalA : Infinity,
      logicalB !== null ? logicalB : Infinity
    );
    const maxLogical = Math.max(
      logicalA !== null ? logicalA : -Infinity,
      logicalB !== null ? logicalB : -Infinity
    );

    // Trendline is completely outside visible range
    if (maxLogical < startTimePoint || minLogical > endTimePoint) {
      return null;
    }

    // Calculate price range covered by this trendline
    const minPrice = Math.min(this._trendline.a.price, this._trendline.b.price);
    const maxPrice = Math.max(this._trendline.a.price, this._trendline.b.price);

    // Add small margin to ensure handles are fully visible
    const priceMargin = (maxPrice - minPrice) * 0.02; // 2% margin

    return {
      priceRange: {
        minValue: minPrice - priceMargin,
        maxValue: maxPrice + priceMargin,
      },
    };
  }

  // Hit testing for interaction
  hitTest(x: number, y: number): { cursorStyle: string; zOrder: string; externalId: string } | null {
    if (!this._series || !this._chart) return null;

    const handleRadius = 8;
    const lineClickTolerance = 10;
    let newHoverState: 'a' | 'b' | 'line' | null = null;

    // Check handle A
    const coordA = this._getPixelCoordinate(this._trendline.a);
    if (coordA) {
      const distA = Math.sqrt(
        Math.pow(coordA.x - x, 2) + Math.pow(coordA.y - y, 2)
      );

      if (distA <= handleRadius + 2) {
        newHoverState = 'a';
        // Only update if hover state changed
        if (this._hoveredHandle !== 'a') {
          this._hoveredHandle = 'a';
          this.requestUpdate();
        }
        return {
          cursorStyle: 'grab',
          zOrder: 'top',
          externalId: `${this._trendline.id}-handle-a`
        };
      }
    }

    // Check handle B
    const coordB = this._getPixelCoordinate(this._trendline.b);
    if (coordB) {
      const distB = Math.sqrt(
        Math.pow(coordB.x - x, 2) + Math.pow(coordB.y - y, 2)
      );

      if (distB <= handleRadius + 2) {
        newHoverState = 'b';
        // Only update if hover state changed
        if (this._hoveredHandle !== 'b') {
          this._hoveredHandle = 'b';
          this.requestUpdate();
        }
        return {
          cursorStyle: 'grab',
          zOrder: 'top',
          externalId: `${this._trendline.id}-handle-b`
        };
      }
    }

    // Check line segment
    if (coordA && coordB) {
      const dist = this._distanceToLineSegment(x, y, coordA.x, coordA.y, coordB.x, coordB.y);

      if (dist < lineClickTolerance) {
        newHoverState = 'line';
        // Only update if hover state changed
        if (this._hoveredHandle !== 'line') {
          this._hoveredHandle = 'line';
          this.requestUpdate();
        }
        return {
          cursorStyle: 'move',
          zOrder: 'normal',
          externalId: `${this._trendline.id}-line`
        };
      }
    }

    // Clear hover state if nothing hit (only if state changed)
    if (this._hoveredHandle !== null) {
      this._hoveredHandle = null;
      this.requestUpdate();
    }

    return null;
  }

  // Helper: Convert logical coordinates to pixel coordinates
  private _getPixelCoordinate(point: Tp): { x: number; y: number } | null {
    if (!this._series || !this._chart) return null;

    const x = this._chart.timeScale().timeToCoordinate(point.time);
    const y = this._series.priceToCoordinate(point.price);

    if (x === null || y === null) return null;

    return { x, y };
  }

  // Helper: Distance from point to line segment (from standalone)
  private _distanceToLineSegment(
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

  // Public API for external updates
  getTrendline(): Trendline {
    return this._trendline;
  }

  updateTrendline(trendline: Partial<Trendline>): void {
    this._trendline = { ...this._trendline, ...trendline };
    this.requestUpdate();
  }

  getHoveredHandle(): 'a' | 'b' | 'line' | null {
    return this._hoveredHandle;
  }

  getChart(): IChartApi | null {
    return this._chart;
  }

  getSeries(): ISeriesApi<'Candlestick' | 'Line' | 'Area' | 'Baseline' | 'Histogram' | 'Bar'> | null {
    return this._series;
  }
}

/**
 * Pane view for rendering trendlines and handles
 */
class TrendlinePaneView {
  private _source: TrendlineHandlePrimitive;
  private _renderer: TrendlinePaneRenderer;

  constructor(source: TrendlineHandlePrimitive) {
    this._source = source;
    this._renderer = new TrendlinePaneRenderer(source);
  }

  update(): void {
    this._renderer.update();
  }

  renderer() {
    return this._renderer;
  }

  zOrder(): 'bottom' | 'normal' | 'top' {
    return 'top'; // Render on top of series data
  }
}

/**
 * Renderer for drawing trendlines and handles on canvas
 */
class TrendlinePaneRenderer {
  private _source: TrendlineHandlePrimitive;

  constructor(source: TrendlineHandlePrimitive) {
    this._source = source;
  }

  update(): void {
    // Called when view updates
  }

  draw(target: any): void {
    target.useBitmapCoordinateSpace((scope: any) => {
      const ctx = scope.context;
      const pixelRatio = scope.horizontalPixelRatio;

      const trendline = this._source.getTrendline();
      const chart = this._source.getChart();
      const series = this._source.getSeries();

      if (!chart || !series) return;

      // Get pixel coordinates
      const coordA = this._getPixelCoordinate(trendline.a, chart, series);
      const coordB = this._getPixelCoordinate(trendline.b, chart, series);

      if (!coordA || !coordB) return;

      // Scale coordinates for high-DPI displays
      const x1 = coordA.x * pixelRatio;
      const y1 = coordA.y * pixelRatio;
      const x2 = coordB.x * pixelRatio;
      const y2 = coordB.y * pixelRatio;

      // Draw main trendline
      const isSelected = trendline.selected;
      const color = trendline.color || '#22c55e';
      const lineWidth = (trendline.width || 2) * pixelRatio;

      ctx.save();
      ctx.strokeStyle = isSelected ? '#FFD700' : color;
      ctx.lineWidth = isSelected ? lineWidth * 2 : lineWidth;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      ctx.restore();

      // Draw handles
      this._drawHandle(ctx, x1, y1, color, pixelRatio, isSelected, this._source.getHoveredHandle() === 'a');
      this._drawHandle(ctx, x2, y2, color, pixelRatio, isSelected, this._source.getHoveredHandle() === 'b');

      // Draw label if available
      // Position label near the start point (left side) which is more likely to be visible
      if (trendline.label) {
        this._drawLabel(ctx, x1, y1, trendline.label, color, pixelRatio);
      }
    });
  }

  private _drawHandle(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    color: string,
    pixelRatio: number,
    isSelected: boolean,
    isHovered: boolean
  ): void {
    const radius = 8 * pixelRatio;

    ctx.save();

    // Fill
    ctx.fillStyle = isSelected || isHovered ? '#FFD700' : color;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, 2 * Math.PI);
    ctx.fill();

    // Stroke
    ctx.strokeStyle = isSelected || isHovered ? '#FFA500' : '#ffffff';
    ctx.lineWidth = 2 * pixelRatio;
    ctx.stroke();

    ctx.restore();
  }

  private _drawLabel(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    label: string,
    color: string,
    pixelRatio: number
  ): void {
    ctx.save();

    // Set font
    const fontSize = 12 * pixelRatio;
    ctx.font = `${fontSize}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';

    // Measure text
    const metrics = ctx.measureText(label);
    const textWidth = metrics.width;
    const textHeight = fontSize;
    const padding = 4 * pixelRatio;

    // Position label to the right of the end handle with some offset
    // Note: x, y are already in bitmap coordinates (scaled by pixelRatio)
    const labelX = x + 12;  // Fixed pixel offset in bitmap space
    const labelY = y;

    // Draw background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.75)';
    ctx.fillRect(
      labelX - padding,
      labelY - textHeight / 2 - padding,
      textWidth + padding * 2,
      textHeight + padding * 2
    );

    // Draw border
    ctx.strokeStyle = color;
    ctx.lineWidth = 1 * pixelRatio;
    ctx.strokeRect(
      labelX - padding,
      labelY - textHeight / 2 - padding,
      textWidth + padding * 2,
      textHeight + padding * 2
    );

    // Draw text
    ctx.fillStyle = color;
    ctx.fillText(label, labelX, labelY);

    ctx.restore();
  }

  private _getPixelCoordinate(point: Tp, chart: IChartApi, series: any): { x: number; y: number } | null {
    const x = chart.timeScale().timeToCoordinate(point.time);
    const y = series.priceToCoordinate(point.price);

    if (x === null || y === null) return null;

    return { x, y };
  }
}
