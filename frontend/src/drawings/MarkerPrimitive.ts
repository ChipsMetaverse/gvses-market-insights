import type {
  ISeriesPrimitive,
  SeriesAttachedParameter,
  Time,
  IChartApi,
  AutoscaleInfo,
  PrimitiveHoveredItem,
  Logical,
} from 'lightweight-charts';

export interface MarkerOptions {
  time: number;
  price: number;
  type: 'circle' | 'arrow' | 'star';
  direction?: 'up' | 'down'; // For arrows
  color: string;
  size?: number; // Radius in pixels
  label?: string;
  zOrder?: 'bottom' | 'normal' | 'top';
}

/**
 * Custom primitive for rendering pattern markers (circles, arrows, stars)
 *
 * Replaces the deprecated setMarkers() method in TradingView Lightweight Charts v5.
 * Renders markers at specific price/time coordinates on the chart.
 */
export class MarkerPrimitive implements ISeriesPrimitive<Time> {
  private _chart: IChartApi | null = null;
  private _series: any = null;
  private _requestUpdate: (() => void) | null = null;

  private _options: Required<MarkerOptions>;
  private _paneViews: MarkerPaneView[];

  constructor(options: MarkerOptions) {
    this._options = {
      time: options.time,
      price: options.price,
      type: options.type,
      direction: options.direction ?? 'up',
      color: options.color,
      size: options.size ?? 6,
      label: options.label ?? '',
      zOrder: options.zOrder ?? 'top',
    };
    this._paneViews = [new MarkerPaneView(this)];
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
  updatePosition(time: number, price: number): void {
    this._options.time = time;
    this._options.price = price;
    this.requestUpdate();
  }

  applyOptions(options: Partial<MarkerOptions>): void {
    Object.assign(this._options, options);
    this.requestUpdate();
  }

  getOptions(): Readonly<Required<MarkerOptions>> {
    return { ...this._options };
  }

  // Hit testing for click detection
  hitTest(x: number, y: number): PrimitiveHoveredItem | null {
    if (!this._series || !this._chart) {
      return null;
    }

    const timeScale = this._chart.timeScale();
    const xCoord = timeScale.timeToCoordinate(this._options.time as Time);
    const yCoord = this._series.priceToCoordinate(this._options.price);

    if (xCoord === null || yCoord === null) return null;

    // Check if click is within marker radius
    const hitTolerance = this._options.size + 3;
    const distance = Math.sqrt(
      Math.pow(x - xCoord, 2) + Math.pow(y - yCoord, 2)
    );

    if (distance <= hitTolerance) {
      return {
        cursorStyle: 'pointer',
        externalId: `marker_${this._options.time}_${this._options.type}`,
        zOrder: this._options.zOrder,
      };
    }

    return null;
  }

  // Autoscale integration
  autoscaleInfo(_startTimePoint: Logical, _endTimePoint: Logical): AutoscaleInfo | null {
    // Include this marker's price in autoscale calculations
    return {
      priceRange: {
        minValue: this._options.price,
        maxValue: this._options.price,
      },
    };
  }

  private requestUpdate(): void {
    if (this._requestUpdate) {
      this._requestUpdate();
    }
  }

  // Getters for pane view
  get chart(): IChartApi | null {
    return this._chart;
  }

  get series(): any {
    return this._series;
  }

  get time(): number {
    return this._options.time;
  }

  get price(): number {
    return this._options.price;
  }

  get type(): 'circle' | 'arrow' | 'star' {
    return this._options.type;
  }

  get direction(): 'up' | 'down' {
    return this._options.direction;
  }

  get color(): string {
    return this._options.color;
  }

  get size(): number {
    return this._options.size;
  }

  get label(): string {
    return this._options.label;
  }

  get zOrder(): 'bottom' | 'normal' | 'top' {
    return this._options.zOrder;
  }
}

/**
 * Pane view for rendering the marker
 */
class MarkerPaneView {
  private _primitive: MarkerPrimitive;

  constructor(primitive: MarkerPrimitive) {
    this._primitive = primitive;
  }

  zOrder(): 'bottom' | 'normal' | 'top' {
    return this._primitive.zOrder;
  }

  renderer() {
    return {
      draw: (target: any) => {
        const series = this._primitive.series;
        const chart = this._primitive.chart;
        if (!series || !chart) {
          return;
        }

        // Get coordinates
        const timeScale = chart.timeScale();
        const xCoord = timeScale.timeToCoordinate(this._primitive.time as Time);
        const yCoord = series.priceToCoordinate(this._primitive.price);

        if (xCoord === null || yCoord === null) {
          return;
        }

        target.useBitmapCoordinateSpace((scope: any) => {
          const ctx = scope.context;
          const pixelRatio = scope.horizontalPixelRatio;

          const x = xCoord * pixelRatio;
          const y = yCoord * pixelRatio;
          const size = this._primitive.size * pixelRatio;

          ctx.fillStyle = this._primitive.color;
          ctx.strokeStyle = this._primitive.color;
          ctx.lineWidth = 2 * pixelRatio;

          // Draw marker based on type
          const type = this._primitive.type;

          if (type === 'circle') {
            // Draw filled circle
            ctx.beginPath();
            ctx.arc(x, y, size, 0, 2 * Math.PI);
            ctx.fill();

            // Add white border for better visibility
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5 * pixelRatio;
            ctx.stroke();
          } else if (type === 'arrow') {
            // Draw arrow (triangle)
            const direction = this._primitive.direction;
            const arrowSize = size * 1.5;

            ctx.beginPath();
            if (direction === 'up') {
              // Arrow pointing up (above bar - bullish)
              ctx.moveTo(x, y - arrowSize);
              ctx.lineTo(x - arrowSize, y + arrowSize);
              ctx.lineTo(x + arrowSize, y + arrowSize);
            } else {
              // Arrow pointing down (below bar - bearish)
              ctx.moveTo(x, y + arrowSize);
              ctx.lineTo(x - arrowSize, y - arrowSize);
              ctx.lineTo(x + arrowSize, y - arrowSize);
            }
            ctx.closePath();
            ctx.fill();

            // Add white border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5 * pixelRatio;
            ctx.stroke();
          } else if (type === 'star') {
            // Draw star (5-pointed)
            const starSize = size * 1.3;
            const spikes = 5;
            const outerRadius = starSize;
            const innerRadius = starSize * 0.5;

            ctx.beginPath();
            for (let i = 0; i < spikes * 2; i++) {
              const radius = i % 2 === 0 ? outerRadius : innerRadius;
              const angle = (Math.PI / spikes) * i - Math.PI / 2;
              const px = x + Math.cos(angle) * radius;
              const py = y + Math.sin(angle) * radius;

              if (i === 0) {
                ctx.moveTo(px, py);
              } else {
                ctx.lineTo(px, py);
              }
            }
            ctx.closePath();
            ctx.fill();

            // Add white border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5 * pixelRatio;
            ctx.stroke();
          }

          // Draw label if provided
          if (this._primitive.label) {
            ctx.font = `${10 * pixelRatio}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`;
            ctx.fillStyle = this._primitive.color;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.fillText(
              this._primitive.label,
              x,
              y + (this._primitive.size + 4) * pixelRatio
            );
          }
        });
      },
    };
  }
}
