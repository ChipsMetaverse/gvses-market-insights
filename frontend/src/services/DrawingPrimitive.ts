import { 
  ISeriesPrimitive, 
  ISeriesPrimitivePaneView,
  ISeriesPrimitivePaneRenderer,
  CanvasRenderingTarget2D,
  SeriesAttachedParameter,
  IChartApi,
  ISeriesApi,
  Time,
  Coordinate
} from 'lightweight-charts';

export interface DrawingObject {
  id: string;
  type: 'trendline' | 'horizontal' | 'fibonacci' | 'vertical' | 'rectangle';
  data: any;
  color?: string;
  lineWidth?: number;
  lineDash?: number[];
}

interface TrendlineData {
  startPrice: number;
  startTime: Time;
  endPrice: number;
  endTime: Time;
}

interface HorizontalLineData {
  price: number;
  label?: string;
}

interface FibonacciData {
  highPrice: number;
  lowPrice: number;
  startTime: Time;
  endTime: Time;
  levels?: number[];
}

export class DrawingPrimitive implements ISeriesPrimitive<Time> {
  private _drawings: DrawingObject[] = [];
  private _series?: ISeriesApi<'Candlestick'>;
  private _chart?: IChartApi;
  private _requestUpdateCallback?: () => void;

  attached(param: SeriesAttachedParameter<Time>): void {
    console.log('[DrawingPrimitive] Attached to series', {
      hasChart: !!param.chart,
      hasSeries: !!param.series,
      hasRequestUpdate: !!param.requestUpdate
    });
    this._series = param.series as ISeriesApi<'Candlestick'>;
    this._chart = param.chart;
    this._requestUpdateCallback = param.requestUpdate;
  }

  detached(): void {
    this._series = undefined;
    this._chart = undefined;
    this._requestUpdateCallback = undefined;
  }

  paneViews(): ISeriesPrimitivePaneView[] {
    console.log('[DrawingPrimitive] paneViews called', {
      hasChart: !!this._chart,
      hasSeries: !!this._series,
      drawingCount: this._drawings.length
    });
    if (!this._series || !this._chart) {
      console.log('[DrawingPrimitive] paneViews returning empty - missing chart or series');
      return [];
    }
    return [new DrawingPaneView(this._drawings, this._series, this._chart)];
  }

  updateAllViews(): void {
    // Trigger updates for all views
  }

  priceAxisViews() {
    return [];
  }

  timeAxisViews() {
    return [];
  }

  addTrendline(startPrice: number, startTime: Time, endPrice: number, endTime: Time): string {
    const id = `trendline_${Date.now()}`;
    console.log('[DrawingPrimitive] Adding trendline', {
      id,
      startPrice,
      startTime,
      endPrice,
      endTime,
      hasRequestUpdate: !!this._requestUpdateCallback
    });
    this._drawings.push({
      id,
      type: 'trendline',
      data: { startPrice, startTime, endPrice, endTime } as TrendlineData,
      color: '#2196F3',
      lineWidth: 2
    });
    this.requestUpdate();
    return id;
  }

  addHorizontalLine(price: number, label?: string, color: string = '#4CAF50'): string {
    const id = `horizontal_${Date.now()}`;
    this._drawings.push({
      id,
      type: 'horizontal',
      data: { price, label } as HorizontalLineData,
      color,
      lineWidth: 1,
      lineDash: [5, 5]
    });
    this.requestUpdate();
    return id;
  }

  addFibonacci(highPrice: number, lowPrice: number, startTime: Time, endTime: Time): string {
    const id = `fibonacci_${Date.now()}`;
    const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
    this._drawings.push({
      id,
      type: 'fibonacci',
      data: { highPrice, lowPrice, startTime, endTime, levels } as FibonacciData,
      color: '#FF9800',
      lineWidth: 1
    });
    this.requestUpdate();
    return id;
  }

  removeDrawing(id: string): boolean {
    const index = this._drawings.findIndex(d => d.id === id);
    if (index !== -1) {
      this._drawings.splice(index, 1);
      this.requestUpdate();
      return true;
    }
    return false;
  }

  clearAllDrawings(): void {
    this._drawings = [];
    this.requestUpdate();
  }

  getDrawings(): DrawingObject[] {
    return [...this._drawings];
  }
  
  forceUpdate(): void {
    console.log('[DrawingPrimitive] Force update triggered');
    this.requestUpdate();
    // Also try to force chart update if available
    if (this._chart) {
      this._chart.applyOptions({});
      console.log('[DrawingPrimitive] Applied empty options to force chart update');
    }
  }

  private requestUpdate(): void {
    console.log('[DrawingPrimitive] requestUpdate called', {
      hasCallback: !!this._requestUpdateCallback,
      drawingCount: this._drawings.length
    });
    if (this._requestUpdateCallback) {
      this._requestUpdateCallback();
      console.log('[DrawingPrimitive] requestUpdate callback executed');
    } else {
      console.warn('[DrawingPrimitive] No requestUpdate callback available!');
    }
  }
}

class DrawingPaneView implements ISeriesPrimitivePaneView {
  private _drawings: DrawingObject[];
  private _series: ISeriesApi<'Candlestick'>;
  private _chart: IChartApi;

  constructor(drawings: DrawingObject[], series: ISeriesApi<'Candlestick'>, chart: IChartApi) {
    this._drawings = drawings;
    this._series = series;
    this._chart = chart;
  }

  renderer(): ISeriesPrimitivePaneRenderer | null {
    console.log('[DrawingPaneView] renderer called, creating DrawingRenderer with', this._drawings.length, 'drawings');
    return new DrawingRenderer(this._drawings, this._series, this._chart);
  }

  zOrder(): 'top' | 'normal' | 'bottom' {
    return 'top';
  }
}

class DrawingRenderer implements ISeriesPrimitivePaneRenderer {
  private _drawings: DrawingObject[];
  private _series: ISeriesApi<'Candlestick'>;
  private _chart: IChartApi;

  constructor(drawings: DrawingObject[], series: ISeriesApi<'Candlestick'>, chart: IChartApi) {
    this._drawings = drawings;
    this._series = series;
    this._chart = chart;
  }

  draw(target: CanvasRenderingTarget2D): void {
    console.log('[DrawingRenderer] draw called with', this._drawings.length, 'drawings');
    target.useMediaCoordinateSpace((scope: any) => {
      const ctx = scope.context;
      const timeScale = this._chart.timeScale();
      const priceScale = this._series.priceScale();

      console.log('[DrawingRenderer] Processing drawings in canvas context');
      for (const drawing of this._drawings) {
        console.log('[DrawingRenderer] Drawing object:', drawing);
        ctx.save();
        
        // Set common drawing properties
        ctx.strokeStyle = drawing.color || '#2196F3';
        ctx.lineWidth = drawing.lineWidth || 2;
        if (drawing.lineDash) {
          ctx.setLineDash(drawing.lineDash);
        }

        switch (drawing.type) {
          case 'trendline':
            this.drawTrendline(ctx, drawing.data as TrendlineData, timeScale, priceScale);
            break;
          case 'horizontal':
            this.drawHorizontalLine(ctx, drawing.data as HorizontalLineData, priceScale, scope.mediaSize);
            break;
          case 'fibonacci':
            this.drawFibonacci(ctx, drawing.data as FibonacciData, timeScale, priceScale, scope.mediaSize);
            break;
        }

        ctx.restore();
      }
    });
  }

  private drawTrendline(
    ctx: CanvasRenderingContext2D, 
    data: TrendlineData,
    timeScale: any,
    priceScale: any
  ): void {
    // Use interpolation for timestamps that may not match exact data points
    const x1 = this.interpolateTimeCoordinate(data.startTime, timeScale);
    const x2 = this.interpolateTimeCoordinate(data.endTime, timeScale);
    // Use series.priceToCoordinate instead of priceScale.priceToCoordinate
    const y1 = this._series.priceToCoordinate(data.startPrice);
    const y2 = this._series.priceToCoordinate(data.endPrice);

    console.log('[DrawingRenderer] Trendline coordinates:', {
      x1, y1, x2, y2,
      startTime: data.startTime,
      startPrice: data.startPrice,
      endTime: data.endTime,
      endPrice: data.endPrice
    });

    if (x1 === null || y1 === null || x2 === null || y2 === null) {
      console.warn('[DrawingRenderer] Invalid coordinates, skipping trendline');
      return;
    }

    ctx.beginPath();
    ctx.moveTo(x1 as number, y1 as number);
    ctx.lineTo(x2 as number, y2 as number);
    ctx.stroke();
    console.log('[DrawingRenderer] Trendline drawn successfully');
  }

  /**
   * Interpolate coordinate for timestamps that may not match exact data points
   */
  private interpolateTimeCoordinate(timestamp: number, timeScale: any): number | null {
    try {
      // First try direct conversion
      const directCoord = timeScale.timeToCoordinate(timestamp);
      if (directCoord !== null) {
        console.log('[DrawingRenderer] Direct coordinate found for timestamp:', timestamp, '→', directCoord);
        return directCoord;
      }

      // Get visible range for interpolation
      const visibleRange = timeScale.getVisibleRange();
      if (!visibleRange) {
        console.warn('[DrawingRenderer] No visible range available');
        return null;
      }

      console.log('[DrawingRenderer] Interpolating for timestamp:', timestamp, 'in range:', visibleRange);

      // Clamp timestamp to visible range and interpolate
      const clampedTime = Math.max(visibleRange.from, Math.min(visibleRange.to, timestamp));
      
      // Get coordinates for range boundaries
      const startCoord = timeScale.timeToCoordinate(visibleRange.from);
      const endCoord = timeScale.timeToCoordinate(visibleRange.to);
      
      if (startCoord === null || endCoord === null) {
        console.warn('[DrawingRenderer] Cannot get boundary coordinates');
        return null;
      }

      // Linear interpolation
      const totalTime = visibleRange.to - visibleRange.from;
      const relativeTime = clampedTime - visibleRange.from;
      const ratio = totalTime > 0 ? relativeTime / totalTime : 0;
      
      const interpolatedCoord = startCoord + (endCoord - startCoord) * ratio;
      
      console.log('[DrawingRenderer] Interpolated coordinate:', {
        timestamp,
        clampedTime,
        ratio,
        startCoord,
        endCoord,
        interpolatedCoord
      });
      
      return interpolatedCoord;
    } catch (error) {
      console.error('[DrawingRenderer] Error interpolating coordinate:', error);
      return null;
    }
  }

  private drawHorizontalLine(
    ctx: CanvasRenderingContext2D,
    data: HorizontalLineData,
    priceScale: any,
    mediaSize: { width: number; height: number }
  ): void {
    // Use series.priceToCoordinate instead of priceScale.priceToCoordinate
    const y = this._series.priceToCoordinate(data.price);
    if (y === null) return;

    ctx.beginPath();
    ctx.moveTo(0, y as number);
    ctx.lineTo(mediaSize.width, y as number);
    ctx.stroke();

    // Draw label if provided
    if (data.label) {
      ctx.fillStyle = ctx.strokeStyle;
      ctx.font = '12px Arial';
      ctx.fillText(data.label, 10, (y as number) - 5);
    }
  }

  private drawFibonacci(
    ctx: CanvasRenderingContext2D,
    data: FibonacciData,
    timeScale: any,
    priceScale: any,
    _mediaSize: { width: number; height: number }
  ): void {
    const range = data.lowPrice - data.highPrice;
    const levels = data.levels || [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];

    const x1 = timeScale.timeToCoordinate(data.startTime);
    const x2 = timeScale.timeToCoordinate(data.endTime);
    if (x1 === null || x2 === null) return;

    levels.forEach(level => {
      const price = data.highPrice + range * level;
      // Use series.priceToCoordinate instead of priceScale.priceToCoordinate
      const y = this._series.priceToCoordinate(price);
      if (y === null) return;

      // Draw line
      ctx.beginPath();
      ctx.moveTo(x1 as number, y as number);
      ctx.lineTo(x2 as number, y as number);
      ctx.strokeStyle = `rgba(255, 152, 0, ${0.3 + level * 0.5})`;
      ctx.stroke();

      // Draw label
      ctx.fillStyle = '#FF9800';
      ctx.font = '11px Arial';
      ctx.fillText(
        `${(level * 100).toFixed(1)}% - $${price.toFixed(2)}`, 
        (x1 as number) + 5, 
        (y as number) - 3
      );
    });
  }
}