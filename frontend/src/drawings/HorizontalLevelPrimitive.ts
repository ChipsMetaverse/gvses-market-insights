import type {
  ISeriesPrimitive,
  SeriesAttachedParameter,
  Time,
  IChartApi,
  AutoscaleInfo,
  PrimitiveHoveredItem,
  Logical,
} from 'lightweight-charts';

export interface HorizontalLevelOptions {
  price: number;
  color: string;
  lineWidth?: number;
  lineStyle?: 'solid' | 'dotted' | 'dashed';
  interactive?: boolean;
  label?: string;
  zOrder?: 'bottom' | 'normal' | 'top';
}

/**
 * Custom primitive for rendering horizontal price levels (PDH, PDL, support, resistance, etc.)
 *
 * This primitive replaces createPriceLine() to provide full control over:
 * - Extension handles (can be disabled via interactive: false)
 * - Line styling (solid, dotted, dashed)
 * - Z-order/layering
 * - Selection and interaction
 */
export class HorizontalLevelPrimitive implements ISeriesPrimitive<Time> {
  private _chart: IChartApi | null = null;
  private _series: any = null; // Allow any series type (including CustomSeries)
  private _requestUpdate: (() => void) | null = null;

  private _options: Required<HorizontalLevelOptions>;
  private _paneViews: HorizontalLevelPaneView[];
  private _isSelected = false;

  constructor(options: HorizontalLevelOptions) {
    this._options = {
      price: options.price,
      color: options.color,
      lineWidth: options.lineWidth ?? 1,
      lineStyle: options.lineStyle ?? 'solid',
      interactive: options.interactive ?? false,
      label: options.label ?? '',
      zOrder: options.zOrder ?? 'bottom',
    };
    this._paneViews = [new HorizontalLevelPaneView(this)];
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
  updatePrice(newPrice: number): void {
    this._options.price = newPrice;
    this.requestUpdate();
  }

  applyOptions(options: Partial<HorizontalLevelOptions>): void {
    Object.assign(this._options, options);
    this.requestUpdate();
  }

  getOptions(): Readonly<Required<HorizontalLevelOptions>> {
    return { ...this._options };
  }

  setSelected(selected: boolean): void {
    this._isSelected = selected;
    this.requestUpdate();
  }

  isSelected(): boolean {
    return this._isSelected;
  }

  // Hit testing for click detection
  hitTest(_x: number, y: number): PrimitiveHoveredItem | null {
    if (!this._options.interactive || !this._series) {
      return null;
    }

    const priceScale = this._series.priceScale();
    const yCoord = priceScale.priceToCoordinate(this._options.price);

    if (yCoord === null) return null;

    // Check if click is within 5 pixels of the line
    const hitTolerance = 5;
    if (Math.abs(y - yCoord) <= hitTolerance) {
      return {
        cursorStyle: 'ns-resize',
        externalId: `level_${this._options.price}_${this._options.label}`,
        zOrder: this._options.zOrder,
      };
    }

    return null;
  }

  // Autoscale integration
  autoscaleInfo(_startTimePoint: Logical, _endTimePoint: Logical): AutoscaleInfo | null {
    // Include this level's price in autoscale calculations
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

  get price(): number {
    return this._options.price;
  }

  get color(): string {
    return this._options.color;
  }

  get lineWidth(): number {
    return this._options.lineWidth;
  }

  get lineStyle(): 'solid' | 'dotted' | 'dashed' {
    return this._options.lineStyle;
  }

  get label(): string {
    return this._options.label;
  }

  get zOrder(): 'bottom' | 'normal' | 'top' {
    return this._options.zOrder;
  }
}

/**
 * Pane view for rendering the horizontal level line
 */
class HorizontalLevelPaneView {
  private _primitive: HorizontalLevelPrimitive;

  constructor(primitive: HorizontalLevelPrimitive) {
    this._primitive = primitive;
  }

  zOrder(): 'bottom' | 'normal' | 'top' {
    return this._primitive.zOrder;
  }

  renderer() {
    return {
      draw: (target: any) => {
        const series = this._primitive.series;
        if (!series) {
          console.warn('[HorizontalLevel] No series available for rendering', this._primitive.label);
          return;
        }

        const yCoord = series.priceToCoordinate(this._primitive.price);
        if (yCoord === null) {
          return;
        }

        target.useBitmapCoordinateSpace((scope: any) => {
          const ctx = scope.context;
          const pixelRatio = scope.horizontalPixelRatio;

          // Set line style
          ctx.strokeStyle = this._primitive.color;
          ctx.lineWidth = this._primitive.lineWidth * pixelRatio;

          // Apply line dash pattern
          const lineStyle = this._primitive.lineStyle;
          if (lineStyle === 'dotted') {
            ctx.setLineDash([3 * pixelRatio, 3 * pixelRatio]);
          } else if (lineStyle === 'dashed') {
            ctx.setLineDash([6 * pixelRatio, 3 * pixelRatio]);
          } else {
            ctx.setLineDash([]);
          }

          // Draw the horizontal line across the full width
          const y = yCoord * pixelRatio;
          ctx.beginPath();
          ctx.moveTo(0, y);
          ctx.lineTo(scope.bitmapSize.width, y);
          ctx.stroke();

          // Reset line dash
          ctx.setLineDash([]);

          // Optional: Draw label
          if (this._primitive.label) {
            ctx.font = `${11 * pixelRatio}px -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif`;
            ctx.fillStyle = this._primitive.color;
            ctx.textBaseline = 'bottom';
            ctx.fillText(
              this._primitive.label,
              10 * pixelRatio,
              y - (2 * pixelRatio)
            );
          }

          // If selected and interactive, draw selection indicator
          if (this._primitive.isSelected()) {
            ctx.strokeStyle = '#0088FF';
            ctx.lineWidth = 2 * pixelRatio;
            ctx.setLineDash([4 * pixelRatio, 4 * pixelRatio]);
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(scope.bitmapSize.width, y);
            ctx.stroke();
            ctx.setLineDash([]);
          }
        });
      },
    };
  }
}
