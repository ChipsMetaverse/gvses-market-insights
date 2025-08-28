========================
CODE SNIPPETS
========================
TITLE: Series API Documentation
DESCRIPTION: Provides access to various methods for interacting with a chart series, including retrieving options, price scale information, setting and updating data, and accessing historical data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesApi

LANGUAGE: APIDOC
CODE:
```
options(): Readonly<TOptions>
  - Returns currently applied options.
  - Returns: Readonly<TOptions> - Full set of currently applied options, including defaults.

priceScale(): IPriceScaleApi
  - Returns interface of the price scale the series is currently attached.
  - Returns: IPriceScaleApi - IPriceScaleApi object to control the price scale.

setData(data: TData[]): void
  - Sets or replaces series data.
  - Parameters:
    - data: TData[] - Ordered (earlier time point goes first) array of data items. Old data is fully replaced with the new one.
  - Returns: void
  - Examples:
    lineSeries.setData([
      {time:'2018-12-12',value:24.11},
      {time:'2018-12-13',value:31.74},
    ]);

    barSeries.setData([
      {time:'2018-12-19',open:141.77,high:170.39,low:120.25,close:145.72},
      {time:'2018-12-20',open:145.72,high:147.99,low:100.11,close:108.19},
    ]);

update(bar: TData): void
  - Adds new data item to the existing set (or updates the latest item if times of the passed/latest items are equal).
  - Parameters:
    - bar: TData - A single data item to be added. Time of the new item must be greater or equal to the latest existing time point. If the new item's time is equal to the last existing item's time, then the existing item is replaced with the new one.
  - Returns: void
  - Examples:
    lineSeries.update({
      time:'2018-12-12',
      value:24.11,
    });

    barSeries.update({
      time:'2018-12-19',
      open:141.77,
      high:170.39,
      low:120.25,
      close:145.72,
    });

dataByIndex(logicalIndex: number, mismatchDirection?: MismatchDirection): TData
  - Returns a bar data by provided logical index.
  - Parameters:
    - logicalIndex: number - Logical index
    - mismatchDirection?: MismatchDirection - Search direction if no data found at provided logical index.
  - Returns: TData - Original data item provided via setData or update methods.
  - Example:
    const originalData = series.dataByIndex(10,LightweightCharts.MismatchDirection.NearestLeft);

data(): readonly TData[]
  - Returns all the bar data for the series.
  - Returns: readonly TData[] - Original data items provided via setData or update methods.
  - Example:
    const originalData = series.data();
```

----------------------------------------

TITLE: Series Type and Examples
DESCRIPTION: Demonstrates how to get the type of a series (e.g., Line, Candlestick) and provides examples of creating different series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/ISeriesApi

LANGUAGE: javascript
CODE:
```
const lineSeries = chart.addLineSeries();  
console.log(lineSeries.seriesType());// "Line"  

const candlestickSeries = chart.addCandlestickSeries();  
console.log(candlestickSeries.seriesType());// "Candlestick"  
```

----------------------------------------

TITLE: Update Series Data
DESCRIPTION: Adds a new data point to the series or updates the latest data point if its time matches the existing latest point. Can optionally update historical data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi

LANGUAGE: APIDOC
CODE:
```
update(bar: TData, historicalUpdate?: boolean): void
  Description: Adds new data item to the existing set (or updates the latest item if times of the passed/latest items are equal).
  Parameters:
    bar: TData - A single data item to be added. Time of the new item must be greater or equal to the latest existing time point. If the new item's time is equal to the last existing item's time, then the existing item is replaced with the new one.
    historicalUpdate?: boolean - If true, allows updating an existing data point that is not the latest bar. Default is false. Updating older data using `historicalUpdate` will be slower than updating the most recent data point.
  Returns: void
  Examples:
    lineSeries.update({
      time:'2018-12-12',
      value:24.11,
    });

    barSeries.update({
      time:'2018-12-19',
      open:141.77,
      high:170.39,
      low:120.25,
      close:145.72,
    });
```

----------------------------------------

TITLE: Time Type Examples
DESCRIPTION: Demonstrates different ways to represent time, including literal timestamps, business day objects, and business day strings.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/Time

LANGUAGE: javascript
CODE:
```
const timestamp =1529899200;// Literal timestamp representing 2018-06-25T04:00:00.000Z  
const businessDay ={year:2019,month:6,day:1};// June 1, 2019  
const businessDayString ='2021-02-03';// Business day string literal  
```

----------------------------------------

TITLE: Bars in Logical Range
DESCRIPTION: Retrieves information about bars within a specified logical range of the chart. This is particularly useful for implementing data loading strategies, such as fetching more historical data when a user scrolls near the edge of the currently loaded data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/ISeriesApi

LANGUAGE: APIDOC
CODE:
```
barsInLogicalRange(range: Range<number>): BarsInfo | null
  Returns bars information for the series in the provided logical range or null, if no series data has been found in the requested range.
  Parameters:
    range: Range<number> - The logical range to retrieve info for.
  Returns:
    BarsInfo | null - The bars info for the given logical range.
  Examples:
    const barsInfo = series.barsInLogicalRange(chart.timeScale().getVisibleLogicalRange());
    console.log(barsInfo);

    function onVisibleLogicalRangeChanged(newVisibleLogicalRange) {
      const barsInfo = series.barsInLogicalRange(newVisibleLogicalRange);
      if (barsInfo !== null && barsInfo.barsBefore < 50) {
        // try to load additional historical data and prepend it to the series data
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(onVisibleLogicalRangeChanged);
```

----------------------------------------

TITLE: Get Series Type Example
DESCRIPTION: Shows how to retrieve the type of a series (e.g., Line, Candlestick) using the `seriesType` method in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesApi

LANGUAGE: javascript
CODE:
```
const lineSeries = chart.addSeries(LineSeries);
console.log(lineSeries.seriesType());// "Line"

const candlestickSeries = chart.addCandlestickSeries();
console.log(candlestickSeries.seriesType());// "Candlestick"
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Details the properties available for OhlcData, a base interface for candlestick data. Includes time, open, high, low, and close prices.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  Properties:
    time: Time
      The timestamp of the data point.
    open: number
      The opening price.
    high: number
      The highest price.
    low: number
      The lowest price.
    close: number
      The closing price.
```

----------------------------------------

TITLE: Data Item and Related Types
DESCRIPTION: Defines the structure for data points used in charts and related types for data handling and formatting.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DataItem:
  time: Time
  value: number

Time:
  number | string | Date

BaseValueType:
  'volume' | 'price'

BarPrice:
  number | {
    open: number
    high: number
    low: number
    close: number
  }

Coordinate:
  number

HorzAlign:
  'left' | 'center' | 'right'

DataChangedScope:
  'data' | 'options' | 'visibleRange' | 'width' | 'height'

DataChangedHandler:
  (scope: DataChangedScope) => void

AutoscaleInfoProvider:
  {
    autoscaleInfo: (startIndex: Time, endIndex: Time) => {
      minPossibleValue: number
      maxPossibleValue: number
    }
  }

CreatePriceLineOptions:
  {
    price: number
    color?: string
    lineStyle?: 'solid' | 'dotted' | 'dashed'
    lineWidth?: number
    axis?: 'left' | 'right'
    title?: string
    titleDisplayMode?: 0 | 1
    priceLineSource?: 'last_visible_data' | 'first_visible_data' | 'none'
    priceLineColor?: string
    priceLineStyle?: 'solid' | 'dotted' | 'dashed'
    priceLineVisible?: boolean
  }

CustomSeriesPricePlotValues:
  {
    [key: string]: number
  }

CustomSeriesOptions:
  {
    color?: string
    priceLineSource?: 'last_visible_data' | 'first_visible_data' | 'none'
    priceLineColor?: string
    priceLineStyle?: 'solid' | 'dotted' | 'dashed'
    priceLineVisible?: boolean
    base?: number
    priceFormat?: {
      type: 'volume' | 'price'
      precision?: number
      minMove?: number
      fractionPrice?: boolean
      fractionNumerator?: number
      fractionDenominator?: number
    }
    autoscaleInfoProvider?: AutoscaleInfoProvider
    crosshairMarkerVisible?: boolean
    lastValueAnimationSpeed?: number
    title?: string
    visible?: boolean
  }

CustomSeriesPartialOptions:
  {
    color?: string
    priceLineSource?: 'last_visible_data' | 'first_visible_data' | 'none'
    priceLineColor?: string
    priceLineStyle?: 'solid' | 'dotted' | 'dashed'
    priceLineVisible?: boolean
    base?: number
    priceFormat?: {
      type: 'volume' | 'price'
      precision?: number
      minMove?: number
      fractionPrice?: boolean
      fractionNumerator?: number
      fractionDenominator?: number
    }
    autoscaleInfoProvider?: AutoscaleInfoProvider
    crosshairMarkerVisible?: boolean
    lastValueAnimationSpeed?: number
    title?: string
    visible?: boolean
  }
```

----------------------------------------

TITLE: Scale and Time Related Types
DESCRIPTION: Provides types for horizontal scale items, price scales, time points, and time ranges, crucial for managing chart axes and data points.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/AreaSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  // Defines horizontal alignment options

HorzScaleItemConverterToInternalObj:
  // Converter function for horizontal scale items to internal object format

HorzScalePriceItem:
  // Represents an item on the horizontal price scale

InternalHorzScaleItem:
  // Internal representation of a horizontal scale item

InternalHorzScaleItemKey:
  // Key for internal horizontal scale items

Logical:
  // Represents a logical index or position

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Event handler for logical range changes

OverlayPriceScaleOptions:
  // Options for overlay price scales

Time:
  // Represents a point in time

TimePointIndex:
  // Index representing a point in time

TimeRangeChangeEventHandler:
  // Event handler for time range changes
```

----------------------------------------

TITLE: ISeriesPrimitiveBase API Documentation
DESCRIPTION: Provides methods to retrieve different types of views for series primitives within the Lightweight Charts library. These methods are crucial for rendering chart elements on the time axis, price axis, and main pane. The library's performance optimization relies on returning cached arrays when no changes occur.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitiveBase:
  timeAxisViews(): readonly ISeriesPrimitiveAxisView[]
    - Returns an array of labels to be drawn on the time axis.
    - Each object in the array must implement the ISeriesPrimitiveAxisView interface.
    - For performance, return a new array if the set of views has changed, otherwise return the same array.

  paneViews(): readonly IPrimitivePaneView[]
    - Returns an array of objects representing primitives in the main area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array if the set of views has changed, otherwise return the same array.

  priceAxisPaneViews(): readonly IPrimitivePaneView[]
    - Returns an array of objects representing primitives in the price axis area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array if the set of views has changed, otherwise return the same array.

  timeAxisPaneViews(): readonly IPrimitivePaneView[]
    - Returns an array of objects representing primitives in the time axis area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array if the set of views has changed, otherwise return the same array.
```

----------------------------------------

TITLE: String Prototype Replacement
DESCRIPTION: Deprecated `String.prototype.substr` has been replaced with modern alternatives to ensure compatibility and adherence to current JavaScript standards.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
// Example of using slice instead of substr
const str = 'hello world';
const newStr = str.slice(0, 5); // 'hello'
```

----------------------------------------

TITLE: Time Type Consistency
DESCRIPTION: All time-related types in the public API have been standardized to use the `Time` type for better consistency and predictability.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: typescript
CODE:
```
import { Chart, Time, LineStyle } from 'lightweight-charts';

const chart = new Chart(document.body, {
  // ... options ...
});

const series = chart.addLineSeries();
series.setData([
  { time: '2023-01-01', value: 10 },
  { time: '2023-01-02', value: 12 },
]);
```

----------------------------------------

TITLE: Lightweight Charts API Documentation
DESCRIPTION: This section details the API documentation for Lightweight Charts version 4.2. It includes type aliases and references to various parts of the API. Links to the latest version (5.0) and community resources are also provided.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: VertAlign
Description: Represents vertical alignment options for chart elements.
Link: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/VertAlign

Type alias: VisiblePriceScaleOptions
Description: Defines options for a visible price scale.
Link: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/VisiblePriceScaleOptions

Type alias: CandlestickSeriesPartialOptions
Description: Represents candlestick series options where all properties are optional. It extends SeriesPartialOptions and includes CandlestickStyleOptions.
Link: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesPartialOptions

Related Documentation:
- Getting Started: https://tradingview.github.io/lightweight-charts/docs
- Tutorials: https://tradingview.github.io/lightweight-charts/tutorials
- API Reference: https://tradingview.github.io/lightweight-charts/docs/api
- Latest Version (5.0) API: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesPartialOptions

Community Resources:
- Stack Overflow: https://stackoverflow.com/questions/tagged/lightweight-charts
- Twitter: https://twitter.com/tradingview

Other Resources:
- Advanced Charts: https://www.tradingview.com/charting-library-docs/
- TradingView Widgets: https://www.tradingview.com/widget/

Copyright © 2025 TradingView, Inc. Built with Docusaurus.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: Maps series types to their partial options, allowing for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Maps series types to partial options.
```

----------------------------------------

TITLE: Get Series Type
DESCRIPTION: Retrieves the current type of the series (e.g., Line, Candlestick). Includes examples for both line and candlestick series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesApi

LANGUAGE: APIDOC
CODE:
```
seriesType(): TSeriesType
  Returns the current type of the series.
  Returns:
    TSeriesType: The type of the series.
  Example:
    const lineSeries = chart.addLineSeries();
    console.log(lineSeries.seriesType()); // "Line"

    const candlestickSeries = chart.addCandlestickSeries();
    console.log(candlestickSeries.seriesType()); // "Candlestick"
```

----------------------------------------

TITLE: IPanePrimitiveBase Methods
DESCRIPTION: Documentation for methods available on the IPanePrimitiveBase interface, including updating views, accessing pane views, and handling attachment/detachment events.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IPanePrimitiveBase

LANGUAGE: APIDOC
CODE:
```
IPanePrimitiveBase:
  updateAllViews()?
    - Updates all views associated with the primitive.

  paneViews()?
    - Returns an array of pane views.

  attached()?
    - Called when the primitive is attached to a pane.

  detached()?
    - Called when the primitive is detached from a pane.

  hitTest()?
    - Performs a hit test on the primitive.
```

----------------------------------------

TITLE: OhlcData Interface Documentation
DESCRIPTION: Documentation for the OhlcData interface, which represents a bar with time and OHLC prices. It extends WhitespaceData and can be extended by BarData and CandlestickData. The interface includes properties for time, open, high, low, close, and optional custom values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData<HorzScaleItem>

Represents a bar with a Time and open, high, low, and close prices.

Extends:
  * WhitespaceData<HorzScaleItem>

Extended by:
  * BarData
  * CandlestickData

Type parameters:
• HorzScaleItem = Time

Properties:

time:
> **time** : `HorzScaleItem`
> The bar time.
> Overrides:
> WhitespaceData.time

open:
> **open** : `number`
> The open price.

high:
> **high** : `number`
> The high price.

low:
> **low** : `number`
> The low price.

close:
> **close** : `number`
> The close price.

customValues?:
> `optional` **customValues** : `Record`<`string`, `unknown`>
> Additional custom values which will be ignored by the library, but could be used by plugins.
```

----------------------------------------

TITLE: Lightweight Charts Next Type Aliases
DESCRIPTION: This section lists various type aliases available in the Next version of Lightweight Charts, including event handlers, formatters, and time-related types. These are fundamental building blocks for customizing chart behavior and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type Aliases:
- SizeChangeEventHandler
- TickMarkFormatter
- TickMarkWeightValue
- TickmarksPercentageFormatterFn
- TickmarksPriceFormatterFn
- Time
- TimeFormatterFn
- TimePointIndex
- TimeRangeChangeEventHandler
- UTCTimestamp
- UpDownMarkersSupportedSeriesTypes
- VertAlign
- VisiblePriceScaleOptions
- YieldCurveSeriesType
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: A partial version of CandlestickSeriesOptions, allowing for optional properties to be updated.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  // Partial options for candlestick series
  // Allows updating only specific properties
```

----------------------------------------

TITLE: Interface: TimeScaleOptions
DESCRIPTION: Options for the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
  Options for the time scale.
```

----------------------------------------

TITLE: Supported Series Types
DESCRIPTION: Lists the series types that support up/down markers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
Type alias: UpDownMarkersSupportedSeriesTypes
> **UpDownMarkersSupportedSeriesTypes** : "Area" | "Line" | "Range" | "Candlestick" | "Bar"
Supported series types for up/down markers.
```

----------------------------------------

TITLE: Interface: SeriesPartialOptionsMap
DESCRIPTION: Maps series types to their partial options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
  Maps series types to their partial options.
```

----------------------------------------

TITLE: Other Type Aliases
DESCRIPTION: A collection of other important type aliases available in the Lightweight Charts API, including event handlers, timestamp formats, marker support types, alignment options, price scale configurations, and yield curve series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Defines the data types for different series in Lightweight Charts. It maps series types (like 'Bar') to their corresponding data structures, which can include BarData or WhitespaceData. The HorzScaleItem type parameter defaults to Time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>

Represents the type of data that a series contains.
For example a bar series contains [BarData](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarData) or [WhitespaceData](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/WhitespaceData).

Type parameters:
• HorzScaleItem = [Time](https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Time)

Properties:
### Bar
> **Bar** : [WhitespaceData](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/WhitespaceData)<`HorzScaleItem`> | [BarData](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarData)<`HorzScaleItem`>
The types of bar series data.
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Options for handling double-click events on axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable: boolean
    Enable or disable axis double-click behavior.
```

----------------------------------------

TITLE: TimeScaleOptions API
DESCRIPTION: Documentation for properties within TimeScaleOptions, detailing their purpose, default values, and inheritance from HorzScaleOptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  ticksVisible?: boolean
    Description: Controls the visibility of tick marks on the time scale.
    Inherited from: HorzScaleOptions.ticksVisible

  tickMarkMaxCharacterLength?: number
    Description: Maximum length for tick mark labels. Overrides the default 8 characters.
    Default Value: undefined
    Inherited from: HorzScaleOptions.tickMarkMaxCharacterLength

  uniformDistribution: boolean
    Description: Affects horizontal scale mark generation. If true, marks of the same weight are either all drawn or none are drawn.
    Inherited from: HorzScaleOptions.uniformDistribution

  minimumHeight: number
    Description: Sets a minimum height for the time scale. This value can be exceeded if the time scale requires more space. Useful for aligning multiple charts or for plugins.
    Default Value: 0
    Inherited from: HorzScaleOptions.minimumHeight

  allowBoldLabels: boolean
    Description: Enables rendering of major time scale labels with a bolder font weight.
    Default Value: true
    Inherited from: HorzScaleOptions.allowBoldLabels

  tickMarkFormatter?: TickMarkFormatter
    Description: A formatter function to customize the appearance of tick mark labels on the time axis.
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Options for handling double-click events on axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
  resetPriceScale?: boolean
  resetTimeScale?: boolean
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Options for handling double-click events on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
  action?: ActionType
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: OhlcData Interface
DESCRIPTION: Defines the structure for a bar with time and price data (open, high, low, close). It extends WhitespaceData and is extended by BarData and CandlestickData. The HorzScaleItem type parameter defaults to Time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData<HorzScaleItem = Time>
  Represents a bar with a Time and open, high, low, and close prices.
  Extends: WhitespaceData<HorzScaleItem>
  Extended by: BarData, CandlestickData

  Properties:
    time: HorzScaleItem
      The bar time.
      Overrides: WhitespaceData.time
```

----------------------------------------

TITLE: Series Properties
DESCRIPTION: Lists the common properties available for various series types in Lightweight Charts, including Bar, Candlestick, Area, Baseline, Line, and Histogram.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Properties:
  - Bar
  - Candlestick
  - Area
  - Baseline
  - Line
  - Histogram
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Options for configuring double-click behavior on an axis.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  type: 'autoScale' | 'none'
    The type of action to perform on double-click.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase API Documentation
DESCRIPTION: Provides methods to retrieve different types of views (axis views, pane views) for series primitives in the Lightweight Charts library. These methods are crucial for rendering chart elements and managing visual data. The library's performance relies on efficient cache management, so returning new arrays only when data changes is recommended.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitiveBase:
  timeAxisViews(): readonly ISeriesPrimitiveAxisView[]
    - Returns an array of labels to be drawn on the time axis.
    - Each object in the array must implement the ISeriesPrimitiveAxisView interface.
    - For performance, return a new array only if the set of views has changed; otherwise, return the same array.

  paneViews(): readonly ISeriesPrimitivePaneView[]
    - Returns an array of objects representing primitives in the main area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array only if the set of views has changed; otherwise, return the same array.

  priceAxisPaneViews(): readonly ISeriesPrimitivePaneView[]
    - Returns an array of objects representing primitives in the price axis area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array only if the set of views has changed; otherwise, return the same array.

  timeAxisPaneViews(): readonly ISeriesPrimitivePaneView[]
    - Returns an array of objects representing primitives in the time axis area of the chart.
    - Each object in the array must implement the ISeriesPrimitivePaneView interface.
    - For performance, return a new array only if the set of views has changed; otherwise, return the same array.
```

----------------------------------------

TITLE: CandlestickData Interface Properties
DESCRIPTION: Defines the properties for candlestick data, inheriting from OhlcData. Includes standard OHLC values, time, and optional color properties, along with custom values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  Inherits from: OhlcData

  Properties:
    color?: string
      - The color of the candlestick body.
    borderColor?: string
      - The color of the candlestick border.
    wickColor?: string
      - The color of the candlestick wick.
    time: Time
      - The time of the data point.
    open: number
      - The opening price.
    high: number
      - The highest price.
    low: number
      - The lowest price.
    close: number
      - The closing price.
    customValues?: Record<string, any>
      - An optional object for custom data values.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: Map of partial series options types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
  Map of partial series options types.
```

----------------------------------------

TITLE: Type Aliases and Utility Types
DESCRIPTION: Provides definitions for various type aliases and utility types used within the Lightweight Charts API, such as DeepPartial, Coordinate, and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  T extends object ? {
    [P in keyof T]?: DeepPartial<T[P]>;
  } : T

Coordinate:
  number

BarPrice:
  number

BaseValueType:
  'open' | 'high' | 'low' | 'close'

HorzAlign:
  'left' | 'right' | 'center'

LineWidth:
  number

Logical:
  number

LogicalRange:
  {
    from: Logical,
    to: Logical
  }

MouseEventHandler:
  (param: MouseEventParams) => void

MouseEventParams:
  {
    clientX: number,
    clientY: number,
    pageX: number,
    pageY: number,
    clientX: number,
    clientY: number,
    time: Time | null,
    price: Price | null
  }

LogicalRangeChangeEventHandler:
  (newRange: LogicalRange) => void

AutoscaleInfoProvider:
  {
    autoscaleInfo(data: SeriesDataItem[]): AutoscaleInfo | null
  }

AutoscaleInfo:
  {
    minPossibleValue: number,
    maxPossibleValue: number
  }

Background:
  Color | Gradient

Color:
  string

Gradient:
  {
    angle: number,
    colors: {
      offset: number,
      color: Color
    }[]
  }

LineStyle:
  0 | 1 | 2 | 3 | 4 | 5

Nominal:
  number
```

----------------------------------------

TITLE: OhlcData Interface
DESCRIPTION: Represents Open, High, Low, and Close data points for financial charts. This interface is a base for more specific data types like CandlestickData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData
Structure describing a single item of data for OHLC series
Properties:
open:
> **open** : `number`
Open price
* * *
high:
> **high** : `number`
High price
* * *
low:
> **low** : `number`
Low price
* * *
close:
> **close** : `number`
Close price
* * *
time:
> **time** : `Time`
Time of the data point
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: A map for partial updates of series options, allowing specific properties to be modified.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
Map of partial series options by type
Properties:
  [key: string]: Partial<SeriesOptionsCommon>
    A map of partial series options.
```

----------------------------------------

TITLE: Series Options Documentation
DESCRIPTION: Documentation for various series types available in Lightweight Charts, including their partial options and common series properties. This covers Candlestick, Area, Baseline, Line, Histogram, and Custom series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Candlestick:
  Type: DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
  Description: The type of candlestick series partial options.

Area:
  Type: DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
  Description: The type of area series partial options.

Baseline:
  Type: DeepPartial<BaselineStyleOptions & SeriesOptionsCommon>
  Description: The type of baseline series partial options.

Line:
  Type: DeepPartial<LineStyleOptions & SeriesOptionsCommon>
  Description: The type of line series partial options.

Histogram:
  Type: DeepPartial<HistogramStyleOptions & SeriesOptionsCommon>
  Description: The type of histogram series partial options.

Custom:
  Type: DeepPartial<CustomStyleOptions & SeriesOptionsCommon>
  Description: The type of a custom series partial options.

Properties:
  - Bar
  - Candlestick
  - Area
  - Baseline
  - Line
  - Histogram
  - Custom
```

----------------------------------------

TITLE: Lightweight Charts v3.3.0 Release Notes
DESCRIPTION: Details the changes in version 3.3.0 of Lightweight Charts. This release adds type predicates for series types, creates a Grid instance for every pane, and allows customization of the crosshair marker color. It also includes an option to prevent shifting the time scale when data is added.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/release-notes

LANGUAGE: javascript
CODE:
```
/**
 * Lightweight Charts v3.3.0 Release Notes
 *
 * - Enhancements:
 *   - Add type predicates for series type (#670)
 *   - Create Grid instance for every pane (#382)
 *   - Add possibility to chose crosshairMarker color, independent from line-series color (#310)
 *   - Implement option not to shift the time scale at all when data is added with `setData` (#584)
 *
 * - Fixed:
 *   - Incorrect bar height when its value is more than chart's height (#673)
 *   - Disabling autoScale for non-visible series (#687)
 */
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface Documentation
DESCRIPTION: Documentation for SeriesPartialOptionsMap, a utility type that maps series types to their partial options interfaces, allowing for partial updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Maps series types to their partial options interfaces.

Properties:

- Area:
  > **Area** : Partial<AreaSeriesOptions>

- Line:
  > **Line** : Partial<LineSeriesOptions>

- Candlestick:
  > **Candlestick** : Partial<CandlestickSeriesOptions>

- Bar:
  > **Bar** : Partial<BarSeriesOptions>

- Histogram:
  > **Histogram** : Partial<HistogramSeriesOptions>
```

----------------------------------------

TITLE: TimeScaleOptions Interface Documentation
DESCRIPTION: Documentation for the TimeScaleOptions interface, defining options for the time scale in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Options for the time scale.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Interface: OhlcData<HorzScaleItem>
DESCRIPTION: Represents a bar with a Time and open, high, low, and close prices. This interface is crucial for defining candlestick or bar chart data points.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData<HorzScaleItem>

Represents a bar with a [Time](https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Time) and open, high, low, and close prices.
```

----------------------------------------

TITLE: Lightweight Charts Release Notes
DESCRIPTION: Lists the release history of Lightweight Charts, detailing new features, improvements, and bug fixes for each version.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/release-notes

LANGUAGE: APIDOC
CODE:
```
Lightweight Charts Release Notes:
  - Version 1.0.0: First release. Docs available at https://github.com/tradingview/lightweight-charts/tree/v1.0.0/docs
  - Subsequent versions (4.0.1, 4.0.0, ..., 1.0.0) are documented with specific release notes linked from the main documentation.
```

----------------------------------------

TITLE: Lightweight Charts Versioning Information
DESCRIPTION: Information regarding the versioning of Lightweight Charts, indicating that version 4.1 is outdated and providing a link to the latest documentation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/TimeScalePoint

LANGUAGE: text
CODE:
```
This is documentation for Lightweight Charts 4.1, which is no longer actively maintained. For up-to-date documentation, see the latest version (5.0).
```

----------------------------------------

TITLE: Lightweight Charts API Documentation
DESCRIPTION: References to key API elements affected by the time value type change in Lightweight Charts v4.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/migrations/from-v3-to-v4

LANGUAGE: APIDOC
CODE:
```
IChartApi.subscribeClick:
  Subscribes to the click event on the chart.
  Parameters:
    - callback: A function that will be called when the chart is clicked. It receives `MouseEventParams`.
  
MouseEventParams.time:
  The time of the event.
  Type: `Time` (string, `BusinessDay`, or `number` representing UTC timestamp)

IChartApi.subscribeCrosshairMove:
  Subscribes to the crosshair move event on the chart.
  Parameters:
    - callback: A function that will be called when the crosshair moves. It receives `MouseEventParams`.

LocalizationOptions.timeFormatter:
  A function to format the time.
  Type: `TimeFormatterFn`

TimeFormatterFn:
  A function that takes a `Time` value and returns a formatted string.
  Signature: `(time: Time) => string`

TimeScaleOptions.tickMarkFormatter:
  A function to format tick marks on the time scale.
  Type: `TickMarkFormatter`

TickMarkFormatter:
  A function that takes a `Time` value and returns a formatted string.
  Signature: `(time: Time) => string`

ISeriesApi.setData:
  Sets data for a series.
  Parameters:
    - data: An array of data points, where each point has a `time` property.
    - updateMode: Optional. Specifies how to update the data.
```

----------------------------------------

TITLE: Interface: SeriesPartialOptionsMap
DESCRIPTION: A map for partial options of different series types, allowing for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BaseValuePrice

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
  
  A map for partial options of different series types.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: IPanePrimitiveBase Interface Methods
DESCRIPTION: Documentation for methods within the IPanePrimitiveBase interface, which serves as a base for series primitives in Lightweight Charts. It includes methods for updating views and retrieving pane views.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IPanePrimitiveBase

LANGUAGE: APIDOC
CODE:
```
IPanePrimitiveBase<TPaneAttachedParameters>
  updateAllViews(): void
    - Optional method called when the viewport changes, requiring the primitive to recalculate or invalidate its data.
    - Returns: void

  paneViews(): readonly IPanePrimitivePaneView[]
    - Optional method that returns an array of objects representing the primitive in the main chart area.
    - Returns: readonly IPanePrimitivePaneView[]
```

----------------------------------------

TITLE: ISeriesPrimitivePaneRenderer Methods
DESCRIPTION: Documentation for the methods available on the ISeriesPrimitivePaneRenderer interface, including draw and drawBackground.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneRenderer

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitivePaneRenderer:
  draw(): void
    Renders the series primitive on the pane.

  drawBackground?(): void
    Optionally renders the background for the series primitive on the pane.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap API Documentation
DESCRIPTION: This API documentation entry describes the SeriesPartialOptionsMap interface, which defines the structure for partial options applicable to various series types in Lightweight Charts. It includes details on the properties for Bar, Candlestick, Area, and Baseline series, referencing their specific style and common options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Represents the type of partial options for each series type.

Properties:

Bar:
  Type: DeepPartial<BarStyleOptions & SeriesOptionsCommon>
  Description: The type of bar series partial options.

Candlestick:
  Type: DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
  Description: The type of candlestick series partial options.

Area:
  Type: DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
  Description: The type of area series partial options.

Baseline:
  Type: DeepPartial<BaselineStyleOptions & SeriesOptionsCommon>
  Description: The type of baseline series partial options.

Note: This documentation is for version 4.1, which is not actively maintained. Refer to the latest version for current documentation.
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the basic properties for OhlcData, including time, open, high, low, and close prices.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  Properties:
    time: Time
      The timestamp of the data point.
    open: number
      The opening price.
    high: number
      The highest price.
    low: number
      The lowest price.
    close: number
      The closing price.
```

----------------------------------------

TITLE: HistogramStyleOptions Properties
DESCRIPTION: Details on the properties available for HistogramStyleOptions, including color and base.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color: Color
    The color of the histogram.
  base: number
    The base value for the histogram.
```

----------------------------------------

TITLE: WhitespaceData Example
DESCRIPTION: Demonstrates how to represent data points with potential whitespace in Lightweight Charts. The `time` property is mandatory, while `value` can be omitted to indicate a gap or whitespace in the data series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/WhitespaceData

LANGUAGE: javascript
CODE:
```
const data = [
  { time: '2018-12-03', value: 27.02 },
  { time: '2018-12-04' }, // whitespace
  { time: '2018-12-05' }, // whitespace
  { time: '2018-12-06' }, // whitespace
  { time: '2018-12-07' }, // whitespace
  { time: '2018-12-08', value: 23.92 },
  { time: '2018-12-13', value: 30.74 },
];
```

----------------------------------------

TITLE: API Reference - AxisDoubleClickOptions
DESCRIPTION: Defines options for handling double-click events on the chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/BarStyleOptions

LANGUAGE: APIDOC
CODE:
```
interface AxisDoubleClickOptions {
  // Whether to enable double-click to reset the price scale
  priceScale?: boolean;
  // Whether to enable double-click to reset the time scale
  timeScale?: boolean;
}
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesType

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: TickMark Properties API Documentation
DESCRIPTION: Documentation for the properties of the TickMark interface in Lightweight Charts. This includes 'time', 'species', 'weight', and 'originalTime'.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TickMark

LANGUAGE: APIDOC
CODE:
```
TickMark:
  time: object
    Description: Time / Coordinate
  species: "InternalHorzScaleItem"
    Description: The 'name' or species of the nominal.
  weight: TickMarkWeightValue
    Description: Weight of the tick mark
  originalTime: unknown
    Description: Original value for the `time` property

  Properties:
    index
    time
    weight
    originalTime
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesPartialOptionsMap interface, for partial updates to series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
Defines partial options for series.
```

----------------------------------------

TITLE: General Type Aliases
DESCRIPTION: Includes various general type aliases used within the Lightweight Charts library, such as BarPrice, Coordinate, and DeepPartial.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: typescript
CODE:
```
type BarPrice = number | string;

type Coordinate = number;

type DeepPartial<T> = {
  [P in keyof T]?: DeepPartial<T[P]>;
};

```

----------------------------------------

TITLE: Autoscale and Base Value Types
DESCRIPTION: Defines types for autoscale information providers and base value types used in charting.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: AutoscaleInfoProvider()
Type alias: BaseValueType
```

----------------------------------------

TITLE: Lightweight Charts v3.3.0 Release Notes
DESCRIPTION: Details changes in version 3.3.0, including enhancements for type predicates, grid instances, crosshair marker color, and time scale shifting, along with fixes for bar height and autoscale for non-visible series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: text
CODE:
```
## 3.3.0
**Enhancement**
  * Add type predicates for series type (see [#670](https://github.com/tradingview/lightweight-charts/issues/670))
  * Create Grid instance for every pane (see [#382](https://github.com/tradingview/lightweight-charts/issues/382))
  * Add possibility to chose crosshairMarker color, so it will be independent from line-series color (see [#310](https://github.com/tradingview/lightweight-charts/issues/310))
  * Implement option not to shift the time scale at all when data is added with `setData` (see [#584](https://github.com/tradingview/lightweight-charts/issues/584))

**Fixed**
  * Incorrect bar height when its value is more than chart's height (see [#673](https://github.com/tradingview/lightweight-charts/issues/673))
  * Disabling autoScale for non-visible series (see [#687](https://github.com/tradingview/lightweight-charts/issues/687))
```

----------------------------------------

TITLE: TimeScaleOptions API Documentation
DESCRIPTION: Documentation for TimeScaleOptions interface, detailing properties for controlling the time scale's behavior and appearance. Includes default values and inheritance information.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  rightBarStaysOnScroll: boolean
    Prevent the hovered bar from moving when scrolling.
    Default Value: false
    Inherited from: HorzScaleOptions.rightBarStaysOnScroll

  borderVisible: boolean
    Show the time scale border.
    Default Value: true
    Inherited from: HorzScaleOptions.borderVisible

  borderColor: string
    The time scale border color.
    Default Value: '#2B2B43'
    Inherited from: HorzScaleOptions.borderColor

  visible: boolean
    Show the time scale.
    Default Value: true
    Inherited from: HorzScaleOptions.visible

  timeVisible: boolean
    Show the time, not just the date, in the time scale and vertical crosshair label.
    Default Value: false
    Inherited from: HorzScaleOptions.timeVisible

  secondsVisible: boolean
    Show seconds in the time scale and vertical crosshair label in hh:mm:ss format for intraday data.
    Default Value: true
    Inherited from: HorzScaleOptions.secondsVisible
```

----------------------------------------

TITLE: SeriesOptionsMap Interface
DESCRIPTION: A map where keys are series types and values are their respective options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
Map of series options by type
Properties:
  [key: string]: SeriesOptionsCommon
    A map of series options.
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts 3.8 Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 3.8, covering options for price scales, series formatting, markers, and time-related events.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
OverlayPriceScaleOptions
PriceFormat
PriceFormatterFn
SeriesMarkerPosition
SeriesMarkerShape
SeriesOptions
SeriesPartialOptions
SeriesType
SizeChangeEventHandler
TickMarkFormatter
Time
TimeFormatterFn
TimeRange
TimeRangeChangeEventHandler
UTCTimestamp
VertAlign
VisiblePriceScaleOptions
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface Documentation
DESCRIPTION: Documentation for the SeriesDataItemTypeMap interface, mapping series types to their data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap
Maps series types to their data item types.
```

----------------------------------------

TITLE: v5 Advanced Text Watermark Example
DESCRIPTION: A comprehensive example of implementing a text watermark in v5 with multiple lines, custom styling, and alignment options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/migrations/from-v4-to-v5

LANGUAGE: javascript
CODE:
```
const chart =createChart(container, options);
const mainSeries = chart.addSeries(LineSeries);
mainSeries.setData(generateData());

const firstPane = chart.panes()[0];
createTextWatermark(firstPane,{
  horzAlign:'center',
  vertAlign:'center',
  lines:[
    {
      text:'Hello',
      color:'rgba(255,0,0,0.5)',
      fontSize:100,
      fontStyle:'bold',
    },
    {
      text:'This is a text watermark',
      color:'rgba(0,0,255,0.5)',
      fontSize:50,
      fontStyle:'italic',
      fontFamily:'monospace',
    },
  ],
});
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: Interface: SeriesDataItemTypeMap
DESCRIPTION: A map defining data item types for series, associated with horizontal scale items.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BaseValuePrice

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>
  
  A map defining data item types for series.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ITextWatermarkPluginApi

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: OhlcData Interface Documentation
DESCRIPTION: Documentation for the OhlcData interface, used for representing Open-High-Low-Close data points.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData
Represents Open-High-Low-Close data.
```

----------------------------------------

TITLE: Supported Series Types and Alignment
DESCRIPTION: Documentation for supported series types for up/down markers and vertical alignment options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Logical

LANGUAGE: APIDOC
CODE:
```
Type Aliases:

* UpDownMarkersSupportedSeriesTypes
* VertAlign
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: API documentation for Lightweight Charts, covering methods for creating chart instances, adding series types (Area, Bar), and interacting with the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/series-types

LANGUAGE: APIDOC
CODE:
```
IChartApi:
  createChart(container: HTMLElement, options?: ChartOptions): Chart
    Creates a new chart instance.
    container: The DOM element where the chart will be rendered.
    options: Optional chart configuration options.

  addAreaSeries(options?: AreaStyleOptions): IAreaSeries
    Adds an Area series to the chart.
    options: Optional styling options for the area series.
    Returns: An instance of IAreaSeries.

  addBarSeries(options?: BarStyleOptions): IBarSeries
    Adds a Bar series to the chart.
    options: Optional styling options for the bar series.
    Returns: An instance of IBarSeries.

IChartApi.timeScale(): TimeScale
    Returns the TimeScale API for the chart.

TimeScale:
  fitContent(): void
    Adjusts the visible range of the chart to fit all data points.

SingleValueData:
  value: number
    The data point value.
  time: Time
    The time of the data point.

WhitespaceData:
  time: Time
    The time of the whitespace data point.

BarData:
  open: number
    The opening price of the bar.
  high: number
    The highest price of the bar.
  low: number
    The lowest price of the bar.
  close: number
    The closing price of the bar.
  time: Time
    The time of the bar.

SeriesOptionsCommon:
  (Common options for all series types)

AreaStyleOptions:
  (Specific options for Area series, e.g., lineColor, topColor, bottomColor)

BarStyleOptions:
  (Specific options for Bar series, e.g., upColor, downColor)
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Interface mapping series data item types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>
  Maps series data item types.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ISeriesPrimitive

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the basic Open, High, Low, and Close (OHLC) data structure for chart data points. This interface is extended by CandlestickData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  time: number | Date | string
    The time of the bar.
  open: number
    The open price.
  high: number
    The high price.
  low: number
    The low price.
  close: number
    The close price.
```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing rendering issues with multiple datasets having unequal timescales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: javascript
CODE:
```
/**
 * Lightweight Charts v1.2.2 Release Notes
 *
 * Fixed:
 * - Bug while rendering few datasets with not equal timescale.
 */
```

----------------------------------------

TITLE: Scale Item Converters and Types
DESCRIPTION: Provides type definitions for horizontal scale items and their conversion to internal objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj:
  (item: HorzScalePriceItem) => InternalHorzScaleItem

HorzScalePriceItem:
  price: number
  label: string

InternalHorzScaleItem:
  key: InternalHorzScaleItemKey
  price: number
  label: string
```

----------------------------------------

TITLE: BaseValueType Type
DESCRIPTION: Represents a base value, which can be a number or null.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
BaseValueType:
  number | null
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Configuration options for double-click behavior on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: "boolean"
  action?: "ActionType"
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Interface Documentation
DESCRIPTION: Documentation for the ISeriesPrimitiveBase interface, which serves as the base for series primitives in Lightweight Charts. It outlines methods for updating views and accessing price axis views.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveBase<TSeriesAttachedParameters>
Base interface for series primitives. It must be implemented to add some external graphics to series

Type parameters:
• TSeriesAttachedParameters = unknown

Methods:
updateAllViews()?
> optional updateAllViews(): void
This method is called when viewport has been changed, so primitive have to recalculate / invalidate its data
Returns:
void

priceAxisViews()?
> optional priceAxisViews(): readonly ISeriesPrimitiveAxisView[]
Returns array of labels to be drawn on the price axis used by the series
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: CandlestickData Interface Properties
DESCRIPTION: Defines the properties for candlestick data, inheriting from OhlcData. Includes time, open, high, low, and close prices, along with optional color, border color, and wick color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  time: number | Date | string
    The time of the bar.
  open: number
    The open price.
  high: number
    The high price.
  low: number
    The low price.
  close: number
    The close price.
  color?: string
    The color of the candlestick body.
  borderColor?: string
    The color of the candlestick border.
  wickColor?: string
    The color of the candlestick wick.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesPartialOptionsMap interface, a partial mapping for series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

A partial mapping for series options.
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Scale Item Converters and Types
DESCRIPTION: Provides type definitions for horizontal scale items and their conversion to internal objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Nominal

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj:
  (item: HorzScalePriceItem) => InternalHorzScaleItem

HorzScalePriceItem:
  price: number
  label: string

InternalHorzScaleItem:
  key: InternalHorzScaleItemKey
  price: number
  label: string
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Defines the structure for data points in different series types, such as Bar and Candlestick. It specifies the possible data formats, including whitespace data and specific data types like BarData and CandlestickData, parameterized by the horizontal scale item type.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>

Represents the type of data that a series contains.
For example a bar series contains [BarData](https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BarData) or [WhitespaceData](https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/WhitespaceData).

Type parameters:
• HorzScaleItem = Time

Properties:
### Bar
> **Bar** : WhitespaceData<HorzScaleItem> | BarData<HorzScaleItem>
The types of bar series data.

### Candlestick
> **Candlestick** : WhitespaceData<HorzScaleItem> | CandlestickData<HorzScaleItem>
The types of candlestick series data.
```

----------------------------------------

TITLE: Lightweight Charts Community Links
DESCRIPTION: Community resources for Lightweight Charts, including Stack Overflow and Twitter.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
Community:
  Stack Overflow: https://stackoverflow.com/questions/tagged/lightweight-charts
  Twitter: https://twitter.com/tradingview
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface Documentation
DESCRIPTION: Documentation for the SeriesDataItemTypeMap interface, which maps series data item types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

Maps series data item types.
```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing an issue with rendering multiple datasets with unequal timescales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
## 1.2.2
**Fixed**
  * Bug while rendering few datasets with not equal timescale
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Related TradingView Resources
DESCRIPTION: Links to other TradingView resources, including advanced charting and widget documentation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IPanePrimitiveBase

LANGUAGE: APIDOC
CODE:
```
More:
  Advanced Charts: https://www.tradingview.com/charting-library-docs/
  TradingView Widgets: https://www.tradingview.com/widget/
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface Documentation
DESCRIPTION: Documentation for SeriesDataItemTypeMap, a utility type that maps series types to their corresponding data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

Maps series types to their data item types.

Properties:

- Area:
  > **Area** : AreaData

- Line:
  > **Line** : LineData

- Candlestick:
  > **Candlestick** : CandlestickData

- Bar:
  > **Bar** : BarData

- Histogram:
  > **Histogram** : HistogramData
```

----------------------------------------

TITLE: Logical Type
DESCRIPTION: Represents a logical index or position, often used internally by the charting library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index
  // Typically a number.
  // Example:
  // 100
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the basic Open, High, Low, and Close (OHLC) data structure for chart data points. Includes time and OHLC values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  Properties:
    time: Time
      - The time of the data point.
    open: number
      - The opening price.
    high: number
      - The highest price.
    low: number
      - The lowest price.
    close: number
      - The closing price.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PrimitiveHasApplyOptions

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: A map for providing partial updates to series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/PriceLineOptions

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

A map for providing partial updates to series options.

Properties:
  - Line?: Partial<LineSeriesOptions>
    Partial options for Line series.
  - Area?: Partial<AreaSeriesOptions>
    Partial options for Area series.
  - Bar?: Partial<BarSeriesOptions>
    Partial options for Bar series.
  - Candlestick?: Partial<CandlestickSeriesOptions>
    Partial options for Candlestick series.
```

----------------------------------------

TITLE: Scale Item Converters and Types
DESCRIPTION: Provides type definitions for horizontal scale items and their conversion to internal objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickMarkWeightValue

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj:
  (item: HorzScalePriceItem) => InternalHorzScaleItem

HorzScalePriceItem:
  price: number
  label: string

InternalHorzScaleItem:
  key: InternalHorzScaleItemKey
  price: number
  label: string
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Represents data for a single candlestick, including OHLC (Open, High, Low, Close) values and time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/GridOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  time: Time
    The time of the candlestick.
  open: number
    The opening price.
  high: number
    The highest price.
  low: number
    The lowest price.
  close: number
    The closing price.
  color?: string
    Optional custom color for the candlestick.
```

----------------------------------------

TITLE: CandlestickSeries API Documentation
DESCRIPTION: Documentation for the CandlestickSeries variable, which defines candlestick chart types in Lightweight Charts. It specifies the type as 'Candlestick' and inherits from SeriesDefinition.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/variables/CandlestickSeries

LANGUAGE: APIDOC
CODE:
```
Variable: CandlestickSeries

Type: SeriesDefinition<"Candlestick">

Description: Defines the configuration and behavior for candlestick series in Lightweight Charts. This variable is used to create and manage candlestick charts, providing a specific type identifier for this chart kind.
```

----------------------------------------

TITLE: Candlestick Chart Example
DESCRIPTION: Demonstrates how to create and populate a candlestick chart using Lightweight Charts. It includes setting chart options, adding a candlestick series, and providing sample data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/series-types

LANGUAGE: javascript
CODE:
```
const chartOptions = {
  layout: {
    textColor: 'black',
    background: {
      type: 'solid',
      color: 'white'
    }
  }
};
const chart = createChart(document.getElementById('container'), chartOptions);
const candlestickSeries = chart.addSeries(CandlestickSeries, {
  upColor: '#26a69a',
  downColor: '#ef5350',
  borderVisible: false,
  wickUpColor: '#26a69a',
  wickDownColor: '#ef5350'
});

const data = [{
  open: 10,
  high: 10.63,
  low: 9.49,
  close: 9.55,
  time: 1642427876
}, {
  open: 9.55,
  high: 10.30,
  low: 9.42,
  close: 9.94,
  time: 1642514276
}, {
  open: 9.94,
  high: 10.17,
  low: 9.92,
  close: 9.78,
  time: 1642600676
}, {
  open: 9.78,
  high: 10.59,
  low: 9.18,
  close: 9.51,
  time: 1642687076
}, {
  open: 9.51,
  high: 10.46,
  low: 9.10,
  close: 10.17,
  time: 1642773476
}, {
  open: 10.17,
  high: 10.96,
  low: 10.16,
  close: 10.47,
  time: 1642859876
}, {
  open: 10.47,
  high: 11.39,
  low: 10.40,
  close: 10.81,
  time: 1642946276
}, {
  open: 10.81,
  high: 11.60,
  low: 10.30,
  close: 10.75,
  time: 1643032676
}, {
  open: 10.75,
  high: 11.60,
  low: 10.49,
  close: 10.93,
  time: 1643119076
}, {
  open: 10.93,
  high: 11.53,
  low: 10.76,
  close: 10.96,
  time: 1643205476
}];

candlestickSeries.setData(data);

chart.timeScale().fitContent();
```

----------------------------------------

TITLE: Histogram Series Options
DESCRIPTION: Defines the options for configuring a Histogram series, including visual properties and data handling. This is a partial options type, meaning not all properties are required.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  priceFormat?: {
    type: 'volume' | 'price'
    precision?: number
    minMove?: number
    fractionPrice?: boolean
    fractionNumerator?: number
    fractionDenominator?: number
  }
  base?: number
  color?: string
  priceLineSource?: 'last_visible_data' | 'first_visible_data' | 'none'
  priceLineColor?: string
  priceLineStyle?: 'solid' | 'dotted' | 'dashed'
  priceLineVisible?: boolean
  autoscaleInfoProvider?: AutoscaleInfoProvider
  crosshairMarkerVisible?: boolean
  lastValueAnimationSpeed?: number
  title?: string
  visible?: boolean

HistogramSeriesPartialOptions:
  priceFormat?: {
    type: 'volume' | 'price'
    precision?: number
    minMove?: number
    fractionPrice?: boolean
    fractionNumerator?: number
    fractionDenominator?: number
  }
  base?: number
  color?: string
  priceLineSource?: 'last_visible_data' | 'first_visible_data' | 'none'
  priceLineColor?: string
  priceLineStyle?: 'solid' | 'dotted' | 'dashed'
  priceLineVisible?: boolean
  autoscaleInfoProvider?: AutoscaleInfoProvider
  crosshairMarkerVisible?: boolean
  lastValueAnimationSpeed?: number
  title?: string
  visible?: boolean
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for configuring a candlestick series in Lightweight Charts. This allows for incremental updates to existing series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: 
    string
    The color of candlesticks when the close price is higher than the open price. Defaults to '#26a69a'.
  downColor?: 
    string
    The color of candlesticks when the close price is lower than the open price. Defaults to '#ef5350'.
  borderVisible?: 
    boolean
    Whether the candlestick borders are visible. Defaults to true.
  borderColor?: 
    string
    The color of the candlestick borders. Defaults to '#888888'.
  wickVisible?: 
    boolean
    Whether the candlestick wicks are visible. Defaults to true.
  wickColor?: 
    string
    The color of the candlestick wicks. Defaults to '#888888'.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the properties for OHLC (Open, High, Low, Close) data points used in Lightweight Charts. It includes time, open, high, low, close prices, and optional custom values. This interface extends WhitespaceData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  time: Time
    The time of the data point.
  open: number
    The opening price.
  high: number
    The highest price.
  low: number
    The lowest price.
  close: number
    The closing price.
  customValues?: any
    Optional custom values associated with the data point.
```

----------------------------------------

TITLE: OhlcData Interface
DESCRIPTION: Defines the structure for Open, High, Low, and Close data points, typically used for OHLC and candlestick charts. It includes the time and the respective price values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData
Structure describing a single item of data for OHLC series
Properties:
  time:
    time : Time
    The bar time.
  open:
    open : number
    The open price.
  high:
    high : number
    The high price.
  low:
    low : number
    The low price.
  close:
    close : number
    The close price.
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These aliases define specific data types, options, and event handlers for chart customization and interaction.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  Represents the options for a histogram series.

HistogramSeriesPartialOptions:
  Represents partial options for a histogram series, allowing for incremental updates.

HorzAlign:
  Defines horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj<HorzScaleItem>:
  A type alias for a converter function that transforms horizontal scale items to an internal object format.

ISeriesPrimitive<HorzScaleItem>:
  An interface for series primitives that interact with the horizontal scale.

InternalHorzScaleItem:
  Represents an internal structure for horizontal scale items.

InternalHorzScaleItemKey:
  A key type for internal horizontal scale items.

LineSeriesOptions:
  Represents the options for a line series.

LineSeriesPartialOptions:
  Represents partial options for a line series.

LineWidth:
  Defines the possible values for line width.

Logical:
  A type alias for logical time points.

LogicalRange:
  Represents a range of logical time points.

LogicalRangeChangeEventHandler<HorzScaleItem>:
  An event handler type for changes in the logical range, potentially involving horizontal scale items.

MouseEventHandler<HorzScaleItem>:
  A generic type for mouse event handlers, adaptable to horizontal scale items.

Mutable<T>:
  A utility type to indicate a mutable type T.

Nominal<T, Name>:
  A nominal typing utility to create distinct types from a base type T.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn():
  A function type for formatting percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn():
  A function type for formatting prices.

PriceToCoordinateConverter():
  A function type for converting price values to chart coordinates.

SeriesMarkerPosition:
  Defines the possible positions for series markers.

SeriesMarkerShape:
  Defines the possible shapes for series markers.

SeriesOptions<T>:
  A generic type for series options, where T is the specific series type.

SeriesPartialOptions<T>:
  A generic type for partial series options.

SeriesPrimitivePaneViewZOrder:
  Defines the Z-order for series primitive pane views.

SeriesType:
  An enumeration of available series types (e.g., 'Line', 'Area', 'Histogram').

SizeChangeEventHandler():
  An event handler type for size change events.

TickMarkFormatter():
  A function type for formatting tick marks on an axis.

TickMarkWeightValue:
  Represents the weight or significance of a tick mark.

Time:
  A type alias for time values used in the chart.

TimeFormatterFn<HorzScaleItem>():
  A function type for formatting time values, potentially related to horizontal scale items.

TimePointIndex:
  An index representing a specific time point.

TimeRangeChangeEventHandler<HorzScaleItem>():
  An event handler type for changes in the time range, potentially involving horizontal scale items.

UTCTimestamp:
  A type alias for UTC timestamps.

VertAlign:
  Defines vertical alignment options for chart elements.
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: A type map that associates series types with their corresponding data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap
Map of series data item types
Properties:
  [key: string]: LineData | OhlcData | SingleValueData | WhitespaceData
    A map of series data item types.
```

----------------------------------------

TITLE: Background and Utility Types
DESCRIPTION: Includes types for background configuration and general utility types like DeepPartial for creating partial option objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: Background
Type alias: DeepPartial<T>
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/YieldCurveSeriesType

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesMarkerBarPosition

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Data Item Type
DESCRIPTION: Represents a single data point in a series, typically containing a time and a price value. The generic parameter `HorzScaleItem` specifies the type of the horizontal scale item (usually `Time`).

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CustomSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: DataItem<HorzScaleItem>
  time: HorzScaleItem
  value: number
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for a Candlestick Series, allowing for incremental updates to existing series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesPartialOptions

  Represents partial options for a Candlestick Series, allowing for incremental updates.
  All properties are optional.

  Properties:
    - upColor?: string
      The color of candlestick bodies when the price increases.
    - downColor?: string
      The color of candlestick bodies when the price decreases.
    - borderUpColor?: string
      The color of the border for candlesticks when the price increases.
    - borderDownColor?: string
      The color of the border for candlesticks when the price decreases.
    - wickUpColor?: string
      The color of the wick for candlesticks when the price increases.
    - wickDownColor?: string
      The color of the wick for candlesticks when the price decreases.
    - wickVisible?: boolean
      Whether the wicks are visible.
    - borderVisible?: boolean
      Whether the borders are visible.
    - candlestickSpacing?: number
      The spacing between candlesticks.
    - priceFormat?: import("../models/priceScale").PriceFormat
      The format of the price displayed on the price scale.
    - invertScale?: boolean
      Inverts the scale of the series.
    - visible?: boolean
      Whether the series is visible.
    - title?: string
      The title of the series, displayed in the legend.
    - lastValueProvider?: import("../models/series").SeriesLastValueProvider
      A function to provide the last value for the series.
    - priceScaleId?: string
      The ID of the price scale to which the series is attached.
    - priceLineVisible?: boolean
      Whether the price line is visible.
    - priceLineColor?: string
      The color of the price line.
    - priceLineWidth?: number
      The width of the price line.
    - priceLineStyle?: import("../models/lineStyle").LineStyle
      The style of the price line.
    - priceLineSource?: import("../models/series").SeriesPriceLineSource
      The source of the price line.
    - highlightBenzyloxy?: boolean
      Whether to highlight the area above the baseline.
    - highlightBelowBenzyloxy?: boolean
      Whether to highlight the area below the baseline.
    - accentColors?: string[]
      An array of accent colors for the series.
    - fade?: boolean
      Whether to fade the series.
    - transparency?: number
      The transparency of the series fill.
    - color?: string
      The color of the series.
    - lineType?: import("../models/series").LineType
      The type of line for the series.

  Example:
    const partialCandlestickSeriesOptions = {
      wickUpColor: 'rgba(0, 0, 255, 1)',
      wickDownColor: 'rgba(255, 255, 0, 1)',
    };

```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing an issue with rendering multiple datasets with unequal timescales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/release-notes

LANGUAGE: javascript
CODE:
```
// Version 1.2.2
// Fixed:
// - Bug while rendering few datasets with not equal timescale.
```

----------------------------------------

TITLE: TimeScaleOptions Properties
DESCRIPTION: Configuration options for the time scale of Lightweight Charts. These properties control aspects like bar spacing, margins, and edge behavior.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  rightOffset: number
    The margin space in bars from the right side of the chart.
    Default Value: 0
    Inherited from: HorzScaleOptions.rightOffset

  barSpacing: number
    The space between bars in pixels.
    Default Value: 6
    Inherited from: HorzScaleOptions.barSpacing

  minBarSpacing: number
    The minimum space between bars in pixels.
    Default Value: 0.5
    Inherited from: HorzScaleOptions.minBarSpacing

  maxBarSpacing: number
    The maximum space between bars in pixels. Has no effect if value is set to 0.
    Default Value: 0
    Inherited from: HorzScaleOptions.maxBarSpacing

  fixLeftEdge: boolean
    Prevent scrolling to the left of the first bar.
    Default Value: false
    Inherited from: HorzScaleOptions.fixLeftEdge

  fixRightEdge: boolean
    Prevent scrolling to the right of the most recent bar.
    Default Value: false
    Inherited from: HorzScaleOptions.fixRightEdge
```

----------------------------------------

TITLE: Interface: SeriesDataItemTypeMap
DESCRIPTION: Maps series types to their data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>
  Maps series types to their data item types.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DeepPartial

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: CandlestickData Interface Properties
DESCRIPTION: Details the properties available for CandlestickData, which inherits from OhlcData. Includes time, open, high, low, close prices, and optional color, borderColor, wickColor, and customValues.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  Inherits from: OhlcData

  Properties:
    color?: string
      Optional color for the candlestick.
    borderColor?: string
      Optional border color for the candlestick.
    wickColor?: string
      Optional wick color for the candlestick.
    time: Time
      The timestamp of the data point.
    open: number
      The opening price.
    high: number
      The highest price.
    low: number
      The lowest price.
    close: number
      The closing price.
    customValues?: Record<string, any>
      Optional custom values associated with the data point.
```

----------------------------------------

TITLE: HistogramSeries API Reference
DESCRIPTION: Defines the HistogramSeries variable used for rendering histogram data. It specifies the type as 'Histogram' and inherits properties from SeriesDefinition.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/variables/HistogramSeries

LANGUAGE: APIDOC
CODE:
```
Variable: HistogramSeries

Type: const HistogramSeries : SeriesDefinition<"Histogram">

Description: Represents the configuration and behavior for rendering histogram series in Lightweight Charts.

Related Documentation:
- Getting Started: https://tradingview.github.io/lightweight-charts/docs
- Tutorials: https://tradingview.github.io/lightweight-charts/tutorials
- API Reference: https://tradingview.github.io/lightweight-charts/docs/api
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases and Variables
DESCRIPTION: References to Type Aliases and Variables documentation for the Next version of Lightweight Charts, indicating available data structures and constants.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesStyleOptionsMap

LANGUAGE: APIDOC
CODE:
```
Type Aliases:
  (Referenced via https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesStyleOptionsMap)

Variables:
  (Referenced via https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesStyleOptionsMap)
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: References type aliases, variables, and functions available in the Next version of Lightweight Charts, with a specific mention of IRange.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IRange

LANGUAGE: APIDOC
CODE:
```
Type Aliases: IRange
Variables: IRange
Functions: IRange
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: Map for partial series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SingleValueData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap
Documentation for SeriesPartialOptionsMap.
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Types
DESCRIPTION: Defines types related to time representation, logical ranges, and event handlers for time and logical range changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Time:
  Represents a point in time.

TimeFormatterFn:
  A function type for formatting time values.

TimePointIndex:
  An index representing a point in time.

LogicalRange:
  Represents a range of logical values.

LogicalRangeChangeEventHandler:
  An event handler for logical range changes.

TimeRangeChangeEventHandler:
  An event handler for time range changes.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases
DESCRIPTION: This section lists various type aliases available in the Next version of Lightweight Charts, including formatters, time-related types, and alignment options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
TickMarkFormatter
TickMarkWeightValue
TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn
Time
TimeFormatterFn
TimePointIndex
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API. These types define the structure and expected values for chart options, data points, and event handlers, enabling developers to configure and interact with chart components effectively. Includes options for Area, Bar, Candlestick, and Histogram series, as well as general types like colors, coordinates, and alignment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series
  // Properties include color, lineColor, topColor, bottomColor, etc.

AreaSeriesPartialOptions:
  // Partial options for Area Series, allowing for optional property overrides

AutoscaleInfoProvider:
  // Interface for providing autoscale information

Background:
  // Type for background color or image settings

BarPrice:
  // Type representing the price of a bar (open, high, low, close)

BarSeriesOptions:
  // Options for Bar Series
  // Properties include color, open, high, low, close, etc.

BarSeriesPartialOptions:
  // Partial options for Bar Series

BaseValueType:
  // Base type for values used in the chart

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

Coordinate:
  // Type for X or Y coordinates on the chart

CreatePriceLineOptions:
  // Options for creating a price line

DeepPartial:
  // Utility type for creating deeply nested partial objects

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

HorzAlign:
  // Enum or type for horizontal alignment (e.g., 'left', 'center', 'right')

LineSeriesOptions:
  // Options for Line Series

LineSeriesPartialOptions:
  // Partial options for Line Series

LineWidth:
  // Type for specifying line width

Logical:
  // Type representing a logical index or position

LogicalRange:
  // Type representing a range of logical indices

LogicalRangeChangeEventHandler:
  // Type for event handler when logical range changes

MouseEventHandler:
  // Type for event handlers triggered by mouse interactions
```

----------------------------------------

TITLE: Other Type Aliases
DESCRIPTION: Provides links to various type aliases used within the Lightweight Charts API, including UTCTimestamp for time representation, UpDownMarkersSupportedSeriesTypes for marker support, VertAlign for vertical alignment, VisiblePriceScaleOptions for price scale visibility, and YieldCurveSeriesType for yield curve data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Options for styling a histogram series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color?: string
    The color of the histogram bars.
  base?: number
    The base value for the histogram bars.
```

----------------------------------------

TITLE: Lightweight Charts Next Type Aliases
DESCRIPTION: Lists various type aliases available in the Next version of Lightweight Charts, including formatters, time-related types, and alignment options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CustomSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
TickMarkFormatter
TickMarkWeightValue
TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn
Time
TimeFormatterFn
TimePointIndex
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
```

----------------------------------------

TITLE: Series Properties
DESCRIPTION: Lists the available properties for different series types within the SeriesOptionsMap, such as Bar, Candlestick, Area, Baseline, Line, and Histogram.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/SeriesOptionsMap

LANGUAGE: APIDOC
CODE:
```
SeriesOptionsMap:
  bar: BarSeriesOptions
  candlestick: CandlestickSeriesOptions
  area: AreaSeriesOptions
  baseline: BaselineSeriesOptions
  line: LineSeriesOptions
  histogram: HistogramSeriesOptions
```

----------------------------------------

TITLE: Other Type Aliases
DESCRIPTION: Includes type aliases for background settings, bar prices, base value types, and autoscale information providers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/DeepPartial

LANGUAGE: APIDOC
CODE:
```
Type alias: AutoscaleInfoProvider()
  Provides information for autoscale calculations.

Type alias: Background
  Represents the background configuration for the chart.

Type alias: BarPrice
  Represents the price of a bar, typically a number.

Type alias: BaseValueType
  Represents the base type for values used in the chart.
```

----------------------------------------

TITLE: HistogramStyleOptions Properties
DESCRIPTION: Defines the properties for styling histogram series in Lightweight Charts. Includes options for column color and the base level.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color: string
    Column color.
    Default Value: '#26a69a'
  base: number
    Initial level of histogram columns.
    Default Value: 0
```

----------------------------------------

TITLE: Lightweight Charts Next Type Aliases
DESCRIPTION: This section lists various type aliases available in the Next version of Lightweight Charts. These aliases define specific data types and event handler signatures used within the charting library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SizeChangeEventHandler: Function signature for handling size change events.
TickMarkFormatter: Type for formatting tick marks on the chart.
TickMarkWeightValue: Represents the weight value for tick marks.
TickmarksPercentageFormatterFn: Function type for formatting percentage tick marks.
TickmarksPriceFormatterFn: Function type for formatting price tick marks.
Time: Represents a point in time on the chart.
TimeFormatterFn: Function type for formatting time.
TimePointIndex: Index representing a point in time.
TimeRangeChangeEventHandler: Function signature for handling time range change events.
UTCTimestamp: Represents a timestamp in UTC.
UpDownMarkersSupportedSeriesTypes: Supported series types for up/down markers.
VertAlign: Vertical alignment options.
VisiblePriceScaleOptions: Options for configuring visible price scales.
YieldCurveSeriesType: Type for yield curve series.
```

----------------------------------------

TITLE: Lightweight Charts v3.3.0 Release Notes
DESCRIPTION: Details changes in version 3.3.0, including enhancements like type predicates for series type, creating Grid instances for every pane, choosing crosshairMarker color, and implementing an option not to shift the time scale. It also lists fixes for incorrect bar height and disabling autoScale for non-visible series. Contributions from [@dubroff](https://github.com/dubroff), [@SuperPenguin](https://github.com/SuperPenguin), and [@mecm1993](https://github.com/mecm1993) are acknowledged.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: javascript
CODE:
```
/**
 * Lightweight Charts v3.3.0 Release Notes
 *
 * Enhancements:
 * - Added type predicates for series type.
 * - Created Grid instance for every pane.
 * - Added possibility to chose crosshairMarker color.
 * - Implemented option not to shift the time scale when data is added.
 *
 * Fixes:
 * - Incorrect bar height when its value is more than chart's height.
 * - Disabling autoScale for non-visible series.
 *
 * Contributors: [@dubroff](https://github.com/dubroff), [@SuperPenguin](https://github.com/SuperPenguin), [@mecm1993](https://github.com/mecm1993)
 */
console.log('Lightweight Charts v3.3.0 released');
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface
DESCRIPTION: Maps series types to their partial options structures, allowing for partial updates in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Maps series types to their partial options structures.
```

----------------------------------------

TITLE: Lightweight Charts v3.5.0 Release Notes
DESCRIPTION: Details changes in version 3.5.0, including a note on rendering order of series, screenshot output fixes, overlapped line chart color order, and price line label display.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: text
CODE:
```
## 3.5.0
**A note about rendering order of series, which might be interpret as a bug or breaking change since this release**
This is not really a breaking change, but might be interpret like that. In [#794](https://github.com/tradingview/lightweight-charts/issues/794) we've fixed the wrong order of series, thus now all series will be displayed in opposite order (they will be displayed in order of creating now; previously they were displayed in reversed order).
To fix that, just change the order of creating the series (thus instead of create series A, then series B create series B first and then series A) - see [#812](https://github.com/tradingview/lightweight-charts/issues/812).
**Fixed**
  * Screenshot output missing piece on bottom right (see [#798](https://github.com/tradingview/lightweight-charts/issues/798))
  * Overlapped line chart show wrong color order when hover (see [#794](https://github.com/tradingview/lightweight-charts/issues/794))
  * Price line label show on both axis (see [#795](https://github.com/tradingview/lightweight-charts/issues/795))
```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing an issue with rendering multiple datasets with unequal time scales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes

LANGUAGE: APIDOC
CODE:
```
Version: 1.2.2

Fixed:
- Bug in rendering multiple datasets with unequal time scales.
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Defines options for handling double-click events on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
  action?: AutoscaleInfoType
```

----------------------------------------

TITLE: Update Candlestick Series Options
DESCRIPTION: Shows how to dynamically update the up and down colors of a Candlestick series using the applyOptions method.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/series-types

LANGUAGE: javascript
CODE:
```
candlestickSeries.applyOptions({
  upColor:'red',
  downColor:'blue',
});
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Options for double-clicking on an axis.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BarData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  mode?: AxisDoubleClickMode
    The mode for double-clicking on the axis (e.g., 'none', 'autoScale').
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsMap interface, which defines the structure for options associated with different types of series in Lightweight Charts. This includes Bar, Candlestick, Area, Baseline, Line, and Histogram series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesOptionsMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap

Represents the type of options for each series type.
For example a bar series has options represented by [BarSeriesOptions](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BarSeriesOptions).

Properties:

Bar:
  > **Bar** : [`BarSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BarSeriesOptions)
  The type of bar series options.

Candlestick:
  > **Candlestick** : [`CandlestickSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CandlestickSeriesOptions)
  The type of candlestick series options.

Area:
  > **Area** : [`AreaSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/AreaSeriesOptions)
  The type of area series options.

Baseline:
  > **Baseline** : [`BaselineSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaselineSeriesOptions)
  The type of baseline series options.

Line:
  > **Line** : [`LineSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/LineSeriesOptions)
  The type of line series options.

Histogram:
  > **Histogram** : [`HistogramSeriesOptions`](https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesOptions)
  The type of histogram series options.
```

----------------------------------------

TITLE: ISeriesPrimitive Type Alias Documentation
DESCRIPTION: This entry documents the ISeriesPrimitive type alias, which is an interface for series primitives. It must be implemented to add external graphics to series. It extends ISeriesPrimitiveBase and is parameterized by HorzScaleItem, which defaults to Time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/ISeriesPrimitive

LANGUAGE: APIDOC
CODE:
```
Type alias: ISeriesPrimitive<HorzScaleItem>

> **ISeriesPrimitive** <`HorzScaleItem`>: [`ISeriesPrimitiveBase`](https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitiveBase) <[`SeriesAttachedParameter`](https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SeriesAttachedParameter)<`HorzScaleItem`, [`SeriesType`](https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/SeriesType)>>

Interface for series primitives. It must be implemented to add some external graphics to series.

## Type parameters

• **HorzScaleItem** = [`Time`](https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/Time)
  * [Type parameters](https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/ISeriesPrimitive#type-parameters)
```

----------------------------------------

TITLE: Lightweight Charts API Reference - Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API for version 3.8. These include options for different series types (Area, Bar, Candlestick, Histogram, Line, Baseline) and other fundamental types like coordinates, prices, and alignment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

AutoscaleInfoProvider:
  // Provider for autoscale information

Background:
  // Background properties

BarPrice:
  // Price for a bar

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

BaseValueType:
  // Base value type

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

Coordinate:
  // A coordinate value

DeepPartial:
  // A deep partial type utility

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

HorzAlign:
  // Horizontal alignment options

LineSeriesOptions:
  // Options for Line Series

LineSeriesPartialOptions:
  // Partial options for Line Series

LineWidth:
  // Line width value

Logical:
  // Logical value type

LogicalRange:
  // Represents a logical range

LogicalRangeChangeEventHandler:
  // Event handler for logical range changes

MouseEventHandler:
  // Event handler for mouse events

Nominal:
  // Nominal value type

OverlayPriceScaleOptions:
  // Options for an overlay price scale
```

----------------------------------------

TITLE: Lightweight Charts 4.2 vs 5.0 Documentation
DESCRIPTION: Information regarding the maintenance status of Lightweight Charts version 4.2 and a link to the latest version's documentation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CustomData

LANGUAGE: markdown
CODE:
```
This is documentation for Lightweight Charts **4.2** , which is no longer actively maintained. For up-to-date documentation, see the **[latest version](https://tradingview.github.io/lightweight-charts/docs/api/interfaces/CustomData)** (5.0).
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: Defines the options and types for different series types like Area, Bar, Candlestick, Baseline, and Histogram. Includes partial options for deep customization.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/DeepPartial

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

CustomSeriesOptions:
  // Options for Custom Series

CustomSeriesPartialOptions:
  // Partial options for Custom Series
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for a Candlestick Series, allowing for incremental updates to existing series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: Color
  downColor?: Color
  borderVisible?: boolean
  borderColor?: Color
  wickVisible?: boolean
  wickColor?: Color
```

----------------------------------------

TITLE: TimeScaleOptions Interface Documentation
DESCRIPTION: Documentation for the TimeScaleOptions interface, containing options for configuring the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Contains options for configuring the time scale.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Logical

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: SeriesStyleOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesStyleOptionsMap interface, a mapping for series style options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesStyleOptionsMap

A mapping for series style options.
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Maps series types to their corresponding data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>

Maps series types to their data item types.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesOptions

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: SeriesOptionsCommon Interface
DESCRIPTION: Common options applicable to all series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon

Common options for all series types.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesMarkerPricePosition

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/IImageWatermarkPluginApi

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for a Candlestick Series, allowing for optional updates to existing configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesPartialOptions

Represents partial options for a Candlestick Series, allowing for optional updates.

Properties:
  - upColor?: string
    The color of the candlestick body when the price increased.
  - downColor?: string
    The color of the candlestick body when the price decreased.
  - borderUpColor?: string
    The color of the candlestick border when the price increased.
  - borderDownColor?: string
    The color of the candlestick border when the price decreased.
  - wickUpColor?: string
    The color of the candlestick wick when the price increased.
  - wickDownColor?: string
    The color of the candlestick wick when the price decreased.
  - priceLineVisible?: boolean
    Whether the price line is visible for this series.
  - lastValueProvider?: (value: number) => number
    A function to provide the last value for the series.
  - priceFormat?: PriceFormat
    The format for displaying prices.
  - timeScale?: TimeScaleOptions
    Options for the time scale.
  - visible?: boolean
    Whether the series is visible.
```

----------------------------------------

TITLE: SingleValueData Interface Documentation
DESCRIPTION: Documentation for SingleValueData, representing a data point with a time and a single value, suitable for series like histograms or baseline indicators.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: SingleValueData

Represents a data point with a time and a single value.

Properties:

- time:
  > **time** : Time
  The time of the data point.

- value:
  > **value** : number
  The value of the data point.
```

----------------------------------------

TITLE: SingleValueData Interface Properties
DESCRIPTION: Defines the base properties for single value data, including time, value, and optional custom values. This is inherited by other data types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
SingleValueData:
  time: Time
    Time of the data point.
  value: number
    Price value of the data.
  customValues?: Record<string, unknown>
    Additional custom values which will be ignored by the library, but could be used by plugins.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: SeriesOptions Type
DESCRIPTION: Base type for all series options, defining common properties applicable to various chart series types like Line, Area, Bar, and Candlestick.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/TickMarkWeightValue

LANGUAGE: APIDOC
CODE:
```
Type alias: SeriesOptions
> **SeriesOptions** : <TData, TStyleOptions>
Base type for all series options.
```

----------------------------------------

TITLE: Series Options Properties
DESCRIPTION: Lists available properties for series options, including specific types like Bar, Candlestick, Area, Baseline, Line, Histogram, and Custom.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Properties:
  Bar: Link to Bar series options
  Candlestick: Link to Candlestick series options
  Area: Link to Area series options
  Baseline: Link to Baseline series options
  Line: Link to Line series options
  Histogram: Link to Histogram series options
  Custom: Link to Custom series options
```

----------------------------------------

TITLE: Price Formatting Examples
DESCRIPTION: Demonstrates how `minMove` and `precision` properties affect price formatting in Lightweight Charts. Shows examples with different combinations of these properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/PriceFormatBuiltIn

LANGUAGE: javascript
CODE:
```
minMove=0.01, precision is not specified - prices will change like 1.13,1.14,1.15 etc.
```

LANGUAGE: javascript
CODE:
```
minMove=0.01, precision=3 - prices will change like 1.130,1.140,1.150 etc.
```

LANGUAGE: javascript
CODE:
```
minMove=0.05, precision is not specified - prices will change like 1.10,1.15,1.20 etc.
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the structure for Open, High, Low, Close data points in financial charts. Includes optional custom values for plugins. Inherits properties from WhitespaceData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  open: number
    The open price.
  high: number
    The high price.
  low: number
    The low price.
  close: number
    The close price.
  customValues?: Record<string, unknown>
    Additional custom values which will be ignored by the library, but could be used by plugins.
    Inherited from WhitespaceData.
```

----------------------------------------

TITLE: SeriesStyleOptionsMap Interface
DESCRIPTION: A map defining the style options for each series type.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/PriceLineOptions

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesStyleOptionsMap

A map defining the style options for each series type.

Properties:
  - Line: LineStyleOptions
    Style options for Line series.
  - Area: AreaStyleOptions
    Style options for Area series.
  - Bar: BarStyleOptions
    Style options for Bar series.
  - Candlestick: CandlestickStyleOptions
    Style options for Candlestick series.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface Documentation
DESCRIPTION: Documentation for the SeriesDataItemTypeMap interface, a mapping for different series data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

A mapping for different series data item types.
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesPartialOptionsMap interface, used for partial updates of series options in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Partial updates for series options.
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for a single data point in a candlestick series. It extends OhlcData and allows for optional overrides of color, borderColor, and wickColor for individual data items. The 'time' property is mandatory.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData
Structure describing a single item of data for candlestick series
Extends:
  * OhlcData
Properties:
  color?:
    optional color : string
    Optional color value for certain data item. If missed, color from options is used
  borderColor?:
    optional borderColor : string
    Optional border color value for certain data item. If missed, color from options is used
  wickColor?:
    optional wickColor : string
    Optional wick color value for certain data item. If missed, color from options is used
  time:
    time : Time
    The bar time.
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Configuration for handling double-click events on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/LineData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
    Enables or disables double-click interaction on the axis.
```

----------------------------------------

TITLE: Histogram Series Options
DESCRIPTION: Defines the partial options for configuring a Histogram series. This includes properties for styling and behavior specific to histogram charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  priceFormat?: {
    type: 'volume' | 'integer' | 'fixed' | 'decimal',
    precision?: number,
    minMove?: number,
    fractDigits?: number
  }
  baseLineVisible?: boolean
  baseLineColor?: Color
  baseLineStyle?: LineStyle
  baseLineWidth?: LineWidth
  color?: Color
  base?: number
  invertScale?: boolean

HistogramSeriesPartialOptions:
  priceFormat?: {
    type: 'volume' | 'integer' | 'fixed' | 'decimal',
    precision?: number,
    minMove?: number,
    fractDigits?: number
  }
  baseLineVisible?: boolean
  baseLineColor?: Color
  baseLineStyle?: LineStyle
  baseLineWidth?: LineWidth
  color?: Color
  base?: number
  invertScale?: boolean
```

----------------------------------------

TITLE: Axis Double Click Options
DESCRIPTION: Defines the options for handling double-click events on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
    Enables or disables the double-click action on the axis.
  resetTimeScale?: boolean
    Resets the time scale when double-clicked if true.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: A partial type for Candlestick Series options, allowing for optional properties when updating or creating a Candlestick Series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineWidth

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions: DeepPartial<CandlestickSeriesOptions>;
```

----------------------------------------

TITLE: IRange Interface Properties
DESCRIPTION: Defines the 'from' and 'to' properties for the IRange interface in Lightweight Charts. 'from' represents the start of the range, and 'to' represents the end of the range. Both properties are generic types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IRange

LANGUAGE: APIDOC
CODE:
```
IRange:
  from: T
    The from value. The start of the range.
  to: T
    The to value. The end of the range.
```

----------------------------------------

TITLE: Lightweight Charts v1.0.1 - Bug Fixes
DESCRIPTION: Version 1.0.1 addresses a bug in the Lightweight Charts library where setting data to a series failed after setting data to a histogram series with a custom color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
// Bug Fix: Setting the data to series fails after setting the data to histogram series with custom color
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: Related TradingView Resources
DESCRIPTION: Links to other TradingView resources such as Advanced Charts and TradingView Widgets.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
More Resources:
  Advanced Charts: https://www.tradingview.com/charting-library-docs/
  TradingView Widgets: https://www.tradingview.com/widget/
```

----------------------------------------

TITLE: Type Checking Time Values in Lightweight Charts
DESCRIPTION: Provides an example of how to check the type of time values received from chart events in Lightweight Charts v4 using utility functions. It demonstrates checking if a time value is a UTCTimestamp, a BusinessDay object, or a business day string in ISO format.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/migrations/from-v3-to-v4

LANGUAGE: javascript
CODE:
```
import{
  createChart,
  isUTCTimestamp,
  isBusinessDay,
}from'lightweight-charts';

const chart =createChart(document.body);

chart.subscribeClick(param=>{
if(param.time===undefined){
// the time is undefined, i.e. there is no any data point where a time could be received from
return;
}

if(isUTCTimestamp(param.time)){
// param.time is UTCTimestamp
}elseif(isBusinessDay(param.time)){
// param.time is a BusinessDay object
}else{
// param.time is a business day string in ISO format, e.g. `'2010-01-01'`
}
});
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HorzScalePriceItem

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Add coordinateToLogical and logicalToCoordinate API
DESCRIPTION: Introduces new API methods to convert between chart coordinates and logical coordinates. This is useful for precise data point mapping and interaction.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: javascript
CODE:
```
chart.coordinateToLogical(x, y);
chart.logicalToCoordinate(logicalX, logicalY);
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DataChangedHandler

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts 4.0 Type Aliases
DESCRIPTION: This section lists various type aliases used in the Lightweight Charts API version 4.0. These include definitions for price formatting, series markers, options, and time-related types. This is a reference for developers using this specific version of the library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/Time

LANGUAGE: APIDOC
CODE:
```
PriceFormatterFn: Function signature for price formatting.
SeriesMarkerPosition: Enum for the position of series markers.
SeriesMarkerShape: Enum for the shape of series markers.
SeriesOptions: Interface for configuring series options.
SeriesPartialOptions: Interface for partial series options updates.
SeriesType: Enum for the type of series (e.g., Candlestick, Line).
SizeChangeEventHandler: Function signature for handling size change events.
TickMarkFormatter: Function signature for tick mark formatting.
Time: Union type for representing time (UTCTimestamp, BusinessDay, string).
TimeFormatterFn: Function signature for time formatting.
TimeRange: Interface for representing a time range.
TimeRangeChangeEventHandler: Function signature for handling time range change events.
UTCTimestamp: Type for UTC timestamps.
VertAlign: Enum for vertical alignment.
VisiblePriceScaleOptions: Interface for visible price scale options.
```

----------------------------------------

TITLE: ISeriesPrimitiveAxisView Interface Documentation
DESCRIPTION: Documentation for the ISeriesPrimitiveAxisView interface, which represents a label on the price or time axis. This entry includes details about its methods.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ISeriesPrimitiveAxisView

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveAxisView

This interface represents a label on the price or time axis.

Methods:

(No specific methods are detailed in the provided text, but the structure indicates they would be listed here.)
```

----------------------------------------

TITLE: Histogram Series Partial Options
DESCRIPTION: Allows for partial updates to Histogram Series options, enabling dynamic adjustments to histogram styling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/LineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions:
  color?: string
  lineWidth?: number
  lineStyle?: LineStyle
  lineType?: LineType
  crosshairMarkerVisible?: boolean
  crosshairMarkerRadius?: number
  visible?: boolean
  title?: string
  lastValueProvider?: LastValueProvider
  priceLineSource?: PriceLineSource
  priceLineStyle?: LineStyle
  priceLineColor?: string
  priceLineWidth?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceFormat?: PriceFormat
  formatter?: TickMarkFormatter
  coordinate?: Coordinate
  scaleMargins?: VerticalScaleMargins
  thinCharts?: boolean
  showPriceLine?: boolean
  priceLine?: PriceLineOptions
  highlighted?: boolean
  interactive?: boolean
  disableScale?: boolean
  disableHighlighting?: boolean
  wrap?: boolean
  wrapWidth?: number
  wrapColor?: string
  wrapStyle?: LineStyle
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Options for the time scale of the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SingleValueData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
Documentation for TimeScaleOptions.
```

----------------------------------------

TITLE: SeriesUpDownMarker Interface Documentation
DESCRIPTION: Documentation for the SeriesUpDownMarker interface, representing markers for up and down movements in a series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesUpDownMarker

Represents markers for up and down movements in a series.
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: TickMark Interface Properties
DESCRIPTION: Details the properties available within the TickMark interface. This includes originalTime, which stores the original value of the time property.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TickMark

LANGUAGE: APIDOC
CODE:
```
TickMark Interface:
  Properties:
    index: The index of the tick mark.
    time: The time value of the tick mark.
    weight: The weight of the tick mark.
    originalTime: Original value for the time property.
```

----------------------------------------

TITLE: CandlestickData Properties
DESCRIPTION: Details the properties of the CandlestickData interface, including time, open, high, low, close prices, and optional custom values. These properties are often inherited from the OhlcData interface.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  time: HorzScaleItem
    The bar time.
    Inherited from OhlcData.time

  open: number
    The open price.
    Inherited from OhlcData.open

  high: number
    The high price.
    Inherited from OhlcData.high

  low: number
    The low price.
    Inherited from OhlcData.low

  close: number
    The close price.
    Inherited from OhlcData.close

  customValues?: Record<string, unknown>
    Optional. Additional custom values which will be ignored by the library, but could be used by plugins.
```

----------------------------------------

TITLE: HistogramData Interface Properties
DESCRIPTION: Details the properties of the HistogramData interface, which extends SingleValueData. Includes 'color', 'time', and 'value'.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
HistogramData:
  Inherits from: SingleValueData
  Properties:
    color? (string): Optional color for the histogram bar.
    time (Time): The time of the data point.
    value (number): The value of the data point.
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: Implementing a Text Watermark (v5)
DESCRIPTION: Demonstrates a comprehensive example of implementing a multi-line text watermark using the `createTextWatermark` function in v5, showing different text styles and alignment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5

LANGUAGE: javascript
CODE:
```
const chart =createChart(container, options);
const mainSeries = chart.addSeries(LineSeries);
mainSeries.setData(generateData());

const firstPane = chart.panes()[0];
createTextWatermark(firstPane,{
  horzAlign:'center',
  vertAlign:'center',
  lines:[
  {
  text:'Hello',
  color:'rgba(255,0,0,0.5)',
  fontSize:100,
  fontStyle:'bold',
  },
  {
  text:'This is a text watermark',
  color:'rgba(0,0,255,0.5)',
  fontSize:50,
  fontStyle:'italic',
  fontFamily:'monospace',
  },
  ],
});
```

----------------------------------------

TITLE: ISeriesPrimitiveBase API Documentation
DESCRIPTION: Provides documentation for methods within the ISeriesPrimitiveBase interface, including autoscaleInfo, attached, detached, and hitTest. These methods are crucial for custom series primitives to interact with the chart's rendering and event handling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo
  - Returns autoscaleInfo which will be merged with the series base autoscaleInfo.
  - Can be used to expand the autoscale range to include visual elements drawn outside of the series' current visible price range.
  - Important: This method is called often during scrolling and zooming, so it should be optimized (e.g., with caching).
  - Parameters:
    - startTimePoint: The start time point for the current visible range.
    - endTimePoint: The end time point for the current visible range.
  - Returns: AutoscaleInfo

attached(param: TSeriesAttachedParameters): void
  - Attached Lifecycle hook.
  - Parameters:
    - param: An object containing useful references for the attached primitive to use.
  - Returns: void

detached(): void
  - Detached Lifecycle hook.
  - Returns: void

hitTest(x: number, y: number): PrimitiveHoveredItem
  - Hit test method called when the cursor is moved.
  - Used to register object IDs being hovered for use within crosshairMoved and click events.
  - Can specify a preferred cursor type.
  - Should return the top-most hit for the primitive.
  - Parameters:
    - x: x Coordinate of mouse event.
    - y: y Coordinate of mouse event.
  - Returns: PrimitiveHoveredItem
```

----------------------------------------

TITLE: Utility Functions
DESCRIPTION: Utility functions for checking data types and retrieving library version information.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/functions/defaultHorzScaleBehavior

LANGUAGE: javascript
CODE:
```
isBusinessDay(value: any): value is BusinessDay
isUTCTimestamp(value: any): value is UTCTimestamp
version(): string
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Provides partial configuration options for a Candlestick Series, allowing for selective updates to its properties. This is useful for modifying specific visual aspects of the candlesticks.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  // Partial options for a Candlestick Series
  // Inherits from BaseSeriesPartialOptions
  upColor?: string;
  downColor?: string;
  borderVisible?: boolean;
  borderColor?: string;
  wickVisible?: boolean;
  wickColor?: string;
  // ... other candlestick-specific partial options
```

----------------------------------------

TITLE: Candlestick Series Options
DESCRIPTION: Defines the options for a Candlestick Series, used for displaying OHLC (Open, High, Low, Close) data with distinct colors for up and down periods.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesOptions
  Properties:
    upColor?: string
    downColor?: string
    borderVisible?: boolean
    borderColor?: string
    wickVisible?: boolean
    wickColor?: string
    barSpacing?: number
    priceLineSource?: 'open' | 'high' | 'low' | 'close'
    priceLineStyle?: number
    priceLineVisible?: boolean
    crosshairMarkerVisible?: boolean
    crosshairMarkerBorderColor?: string
    crosshairMarkerBackgroundColor?: string

Type alias: CandlestickSeriesPartialOptions
  Extends: DeepPartial<CandlestickSeriesOptions>
  Description: Represents a partial set of options for a Candlestick Series, allowing for selective updates.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Methods
DESCRIPTION: Documentation for methods available on ISeriesPrimitiveBase, including autoscaleInfo, attached, detached, and hitTest. These methods are part of the lifecycle and interaction model for custom series primitives.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo
  - Returns autoscaleInfo which will be merged with the series base autoscaleInfo.
  - Can be used to expand the autoscale range to include visual elements drawn outside of the series' current visible price range.
  - Important: This method is called often during scrolling and zooming, so it should be simple or use caching for responsiveness.
  - Parameters:
    - startTimePoint: Logical - start time point for the current visible range
    - endTimePoint: Logical - end time point for the current visible range
  - Returns: AutoscaleInfo

attached(param: TSeriesAttachedParameters): void
  - Attached Lifecycle hook.
  - Parameters:
    - param: TSeriesAttachedParameters - An object containing useful references for the attached primitive to use.
  - Returns: void

detached(): void
  - Detached Lifecycle hook.
  - Returns: void

hitTest(x: number, y: number): PrimitiveHoveredItem
  - Hit test method called when the cursor is moved.
  - Use to register object IDs being hovered for use within crosshairMoved and click events.
  - Can specify a preferred cursor type.
  - Should return the top-most hit for this primitive.
  - Parameters:
    - x: number - x Coordinate of mouse event
    - y: number - y Coordinate of mouse event
  - Returns: PrimitiveHoveredItem
```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing an issue with rendering multiple datasets with unequal timescales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/release-notes

LANGUAGE: javascript
CODE:
```
## 1.2.2
**Fixed**
  * Bug while rendering few datasets with not equal timescale
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Lightweight Charts Documentation Links
DESCRIPTION: Links to various sections of the Lightweight Charts documentation, including getting started, tutorials, and API reference.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
Documentation:
  Getting Started: https://tradingview.github.io/lightweight-charts/docs
  Tutorials: https://tradingview.github.io/lightweight-charts/tutorials
  API Reference: https://tradingview.github.io/lightweight-charts/docs/api
```

----------------------------------------

TITLE: TimeScaleOptions Interface Documentation
DESCRIPTION: Documentation for the TimeScaleOptions interface, used for configuring the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
Defines options for the time scale.
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These types define the structure and constraints for options, data, and internal representations, facilitating precise chart configuration and data manipulation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial:
  A utility type that makes all properties of a type optional and recursively applies to nested objects.

GreenComponent:
  Represents a component that is visually green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series, allowing for incremental updates.

HorzAlign:
  Defines the horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj:
  A type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item displayed on the horizontal price scale.

IImageWatermarkPluginApi:
  Interface for the Image Watermark Plugin API.

IPanePrimitive:
  Interface for a primitive drawn within a chart pane.

ISeriesPrimitive:
  Interface for a primitive associated with a chart series.

ITextWatermarkPluginApi:
  Interface for the Text Watermark Plugin API.

InternalHorzScaleItem:
  Internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  Key used to identify internal horizontal scale items.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series, allowing for incremental updates.

LineWidth:
  Defines the possible values for a line width.

Logical:
  Represents a logical index or position within the chart's data.

LogicalRange:
  Defines a range based on logical indices.

LogicalRangeChangeEventHandler:
  A function type for handling changes in the logical range.

MouseEventHandler:
  A function type for handling mouse events.

Mutable:
  A utility type that makes all properties of a type mutable.

Nominal:
  Represents a nominal value, often used for discrete categories.

OverlayPriceScaleOptions:
  Options for configuring an overlay price scale.

PercentageFormatterFn:
  A function type for formatting percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn:
  A function type for formatting prices.

PriceToCoordinateConverter:
  A function type for converting price values to chart coordinates.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has an 'applyOptions' method.

PrimitivePaneViewZOrder:
  Defines the z-order for primitives within a pane view.

RedComponent:
  Represents a component that is visually red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker displayed on a chart series.

SeriesMarkerBarPosition:
  Defines the position of a series marker relative to a bar.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerPricePosition:
  Defines the vertical position of a series marker relative to a price level.

SeriesMarkerShape:
  Defines the shape of a series marker.

SeriesMarkerZOrder:
  Defines the z-order for series markers.

SeriesOptions:
  General options for configuring any chart series.

SeriesPartialOptions:
  Partial options for configuring any chart series, allowing for incremental updates.

SeriesType:
  Defines the possible types of chart series (e.g., 'Line', 'Area', 'Histogram').
```

----------------------------------------

TITLE: Series Data Types
DESCRIPTION: Defines the data types for various series in Lightweight Charts, including Candlestick, Area, Baseline, Line, Histogram, and Custom. Each type specifies the data structures and potential whitespace data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Candlestick:
  Description: The types of candlestick series data.
  Inherits: WhitespaceData | CandlestickData<HorzScaleItem>

Area:
  Description: The types of area series data.
  Inherits: AreaData<HorzScaleItem> | WhitespaceData<HorzScaleItem>

Baseline:
  Description: The types of baseline series data.
  Inherits: WhitespaceData<HorzScaleItem> | BaselineData<HorzScaleItem>

Line:
  Description: The types of line series data.
  Inherits: WhitespaceData<HorzScaleItem> | LineData<HorzScaleItem>

Histogram:
  Description: The types of histogram series data.
  Inherits: WhitespaceData<HorzScaleItem> | HistogramData<HorzScaleItem>

Custom:
  Description: The base types of an custom series data.
  Inherits: CustomData<HorzScaleItem> | CustomSeriesWhitespaceData<HorzScaleItem>

Properties:
  - Bar
  - Candlestick
  - Area
  - Baseline
  - Line
  - Histogram
  - Custom
```

----------------------------------------

TITLE: Utility Types
DESCRIPTION: Provides utility types such as DeepPartial for creating deeply nested partial objects and Background for defining chart background properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/SeriesType

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  // A utility type that makes all properties of T and its nested properties optional.

Background:
  // Defines the background properties of the chart.
  // Properties: type: 'solid' | 'gradient', color: string (for solid), or gradientColors: string[] (for gradient)

LineWidth:
  // Represents the width of a line in pixels.

BaseValueType:
  // Represents the base value type for calculations, typically 'number'.

```

----------------------------------------

TITLE: Series Options Properties
DESCRIPTION: Lists the available properties for various series types within Lightweight Charts, including Bar, Candlestick, Area, Baseline, Line, Histogram, and Custom.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SeriesOptionsMap

LANGUAGE: APIDOC
CODE:
```
Properties:
  Bar: BarSeriesOptions
  Candlestick: CandlestickSeriesOptions
  Area: AreaSeriesOptions
  Baseline: BaselineSeriesOptions
  Line: LineSeriesOptions
  Histogram: HistogramSeriesOptions
  Custom: CustomSeriesOptions
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: This section provides a comprehensive API reference for Lightweight Charts, covering various aspects of chart customization and functionality. It includes details on series types, price and time scales, panes, time zones, plugins, and migration guides.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/plugins/pixel-perfect-rendering/widths/candlestick

LANGUAGE: APIDOC
CODE:
```
Lightweight Charts API Reference:

Overview:
  Provides detailed documentation for all available APIs in the Lightweight Charts library.

Key Areas:
  - Getting Started: Basic setup and initialization.
  - Series: Adding and configuring different series types (candlesticks, bars, areas, lines, etc.).
  - Chart Types: Understanding different chart visualizations.
  - Price Scale: Customizing the price axis.
  - Time Scale: Customizing the time axis.
  - Panes: Managing multiple chart panes.
  - Time Zones: Handling time zone conversions.
  - Plugins: Extending chart functionality with custom plugins.
    - Introduction to Plugins
    - Series Primitives
    - Pane Primitives
    - Custom Series Types
    - Canvas Rendering Target
    - Pixel Perfect Rendering:
      - Default Widths:
        - Candlesticks
        - Columns
        - Crosshair
        - Full Bar Width
  - Migrations: Guides for migrating between versions.
  - Platform Specifics: iOS and Android integration.
  - Release Notes: History of changes and new features.

Example Usage (Conceptual):
  // Initialize chart
  const chart = LightweightCharts.createChart('chart-container', {
    width: 800,
    height: 600,
  });

  // Add candlestick series
  const candleSeries = chart.addCandlestickSeries();
  candleSeries.setData([
    { time: '2023-01-01', open: 100, high: 110, low: 95, close: 105 },
    { time: '2023-01-02', open: 105, high: 115, low: 100, close: 112 },
  ]);

  // Configure pixel-perfect rendering for candlesticks (example)
  // This would typically be done via plugin configuration or specific API calls
  // related to rendering options.

  // Example of accessing a specific API for pixel-perfect rendering (hypothetical):
  // chart.applyPlugin('PixelPerfectRendering', { candlestickWidth: 10 });

  // Note: Actual API for pixel-perfect rendering might differ and depend on plugin implementation.

Dependencies:
  - None (as a library, but requires a DOM element for rendering).

Limitations:
  - Performance may vary based on the complexity of the chart and the number of data points.
  - Browser compatibility should be checked for specific features.
```

----------------------------------------

TITLE: SeriesOptionsMap Interface
DESCRIPTION: Maps series types to their specific options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap

Maps series types to their options.
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for Candlestick chart data points. It includes time, open, high, low, and close values, similar to OhlcData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  time: Time
  open: number
  high: number
  low: number
  close: number
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesMarkerZOrder

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts 4.1 API Type Aliases
DESCRIPTION: This section lists various type aliases used within the Lightweight Charts API for version 4.1. These include definitions for series primitives, scale items, line series options, time formatting functions, and more. This documentation is for an older, unmaintained version.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitive
  - Represents a primitive series in Lightweight Charts.

InternalHorzScaleItem
  - Represents an internal item for the horizontal scale.

InternalHorzScaleItemKey
  - Key for internal horizontal scale items.

LineSeriesOptions
  - Options for configuring a Line Series.

LineSeriesPartialOptions
  - Partial options for configuring a Line Series.

LineWidth
  - Type for specifying line width.

Logical
  - Represents a logical value.

LogicalRange
  - Represents a range of logical values.

LogicalRangeChangeEventHandler
  - Event handler for logical range changes.

MouseEventHandler
  - Event handler for mouse events.

Mutable
  - Indicates a mutable type.

Nominal
  - Represents a nominal value.

OverlayPriceScaleOptions
  - Options for an overlay price scale.

PercentageFormatterFn
  - Function type for formatting percentages.

PriceFormat
  - Defines the format for prices.

PriceFormatterFn
  - Function type for formatting prices.

PriceToCoordinateConverter
  - Function to convert price to coordinate.

SeriesMarkerPosition
  - Defines the position of a series marker.

SeriesMarkerShape
  - Defines the shape of a series marker.

SeriesOptions
  - General options for all series types.

SeriesPartialOptions
  - Partial options for all series types.

SeriesPrimitivePaneViewZOrder
  - Z-order for series primitive pane views.

SeriesType
  - Enum for different series types (e.g., Line, Bar, Area).

SizeChangeEventHandler
  - Event handler for size changes.

TickMarkFormatter
  - Function type for formatting tick marks.

TickMarkWeightValue
  - Value type for tick mark weights.

Time
  - Represents time in the chart.

TimeFormatterFn
  - Function type for formatting time.

TimePointIndex
  - Index for time points.

TimeRangeChangeEventHandler
  - Event handler for time range changes.

UTCTimestamp
  - Represents a timestamp in UTC.

VertAlign
  - Defines vertical alignment.

VisiblePriceScaleOptions
  - Options for a visible price scale.
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Defines extended time scale options for a time-based horizontal scale. It inherits properties from HorzScaleOptions and includes specific options for managing the right offset.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Extended time scale options for time-based horizontal scale.

Extends:
  * HorzScaleOptions

Properties:
  rightOffset:
    > rightOffset : number
    The margin space in bars from the right side of the chart.
    Default Value:
    `0`
    Inherited from:
    HorzScaleOptions . rightOffset
```

----------------------------------------

TITLE: Interface: SeriesOptionsMap
DESCRIPTION: Maps series types to their options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
  Maps series types to their options.
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsMap interface, mapping series types to their specific options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
Maps series types to their specific options.
```

----------------------------------------

TITLE: SeriesUpDownMarker Interface Properties
DESCRIPTION: Defines the properties for the SeriesUpDownMarker interface, including time, value, and sign. The 'time' property represents the point on the horizontal scale, 'value' is the price for the data point, and 'sign' indicates the direction of the price change using the MarkerSign enumeration.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesUpDownMarker

LANGUAGE: APIDOC
CODE:
```
SeriesUpDownMarker:
  time: T
    The point on the horizontal scale.
  value: number
    The price value for the data point.
  sign: MarkerSign
    The direction of the price change.
```

----------------------------------------

TITLE: BarsInfo Interface Properties
DESCRIPTION: Details the properties inherited by the BarsInfo interface, including barsBefore, barsAfter, from, and to. These properties provide information about the bars available before and after a specific point in the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/BarsInfo

LANGUAGE: APIDOC
CODE:
```
BarsInfo:
  barsBefore: number
    - Number of bars available before the current point.
  barsAfter: number
    - Number of bars available after the current point.
  from?: Time
    - Optional start time of the visible range.
  to?: Time
    - Optional end time of the visible range.
```

----------------------------------------

TITLE: Lightweight Charts General Type Aliases
DESCRIPTION: Provides type aliases for general chart configurations and data types used within the Lightweight Charts library. This includes types for price lines, backgrounds, coordinates, and utility types like DeepPartial.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/TickMarkFormatter

LANGUAGE: APIDOC
CODE:
```
CreatePriceLineOptions:
  // Options for creating a price line

Background:
  // Type for background color or image

Coordinate:
  // Type for coordinate values (e.g., pixel position)

DeepPartial<T>:
  // Utility type to make all properties of T deeply optional

BaseValueType:
  // Base type for values displayed on the chart

Nominal:
  // Type for nominal values, often used for prices or quantities
```

----------------------------------------

TITLE: subscribeClick on Mobile Devices Fix
DESCRIPTION: Addresses an issue where `subscribeClick` on mobile devices was consistently returning the last index of all items, ensuring accurate click event data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/release-notes

LANGUAGE: javascript
CODE:
```
chart.subscribeClick(param => {
    // param.point will contain the coordinates of the click
    // param.series and param.data will contain information about the clicked series and data point
    console.log('Clicked on:', param);
});
```

----------------------------------------

TITLE: Unified Time Value Handling in Lightweight Charts
DESCRIPTION: Demonstrates how to handle unified time value types in Lightweight Charts v4. Previously, inbound and outbound time types differed. Now, they are consistent, meaning if you provide a string time, you receive the same string back. This example shows how to use `timeFormatter` and `tickMarkFormatter` and access time in `subscribeCrosshairMove` and `subscribeClick` events.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/migrations/from-v3-to-v4

LANGUAGE: javascript
CODE:
```
series.setData([
  {time:'2001-01-01',value:1},
]);

chart.applyOptions({
localization:{
timeFormatter:time=> time, // will be '2001-01-01' for the bar above
},
timeScale:{
tickMarkFormatter:time=> time, // will be '2001-01-01' for the bar above
},
});

chart.subscribeCrosshairMove(param=>{
console.log(param.time); // will be '2001-01-01' if you hover the bar above
});

chart.subscribeClick(param=>{
console.log(param.time); // will be '2001-01-01' if you click on the bar above
});
```

----------------------------------------

TITLE: Lightweight Charts Next Type Aliases
DESCRIPTION: Lists various type aliases available in the unreleased 'Next' version of Lightweight Charts. These include definitions for tick mark weights, formatters, time-related types, and more.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HorzScalePriceItem

LANGUAGE: APIDOC
CODE:
```
TickMarkWeightValue: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickMarkWeightValue
TickmarksPercentageFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPriceFormatterFn
Time: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Time
TimeFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimeFormatterFn
TimePointIndex: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimePointIndex
TimeRangeChangeEventHandler: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimeRangeChangeEventHandler
UTCTimestamp: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp
UpDownMarkersSupportedSeriesTypes: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UpDownMarkersSupportedSeriesTypes
VertAlign: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/VertAlign
VisiblePriceScaleOptions: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/VisiblePriceScaleOptions
YieldCurveSeriesType: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/YieldCurveSeriesType
HorzScalePriceItem: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HorzScalePriceItem
```

----------------------------------------

TITLE: Data Item
DESCRIPTION: Represents a single data point in a series, typically including a time and a value.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DataItem:
  time: Time
  value: number
```

----------------------------------------

TITLE: Series Type and Primitive Management
DESCRIPTION: This section covers methods for retrieving the current series type and managing drawing primitives attached to a series. It includes examples of how to use `seriesType`, `attachPrimitive`, and `detachPrimitive`.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/ISeriesApi

LANGUAGE: APIDOC
CODE:
```
seriesType(): TSeriesType
  - Returns the current type of the series.
  - Example:
    ```javascript
    const lineSeries = chart.addLineSeries();
    console.log(lineSeries.seriesType()); // "Line"

    const candlestickSeries = chart.addCandlestickSeries();
    console.log(candlestickSeries.seriesType()); // "Candlestick"
    ```

attachPrimitive(primitive: ISeriesPrimitive<HorzScaleItem>): void
  - Attaches an additional drawing primitive to the series.
  - Parameters:
    - primitive: An implementation of the ISeriesPrimitive interface.

detachPrimitive(primitive: ISeriesPrimitive<HorzScaleItem>): void
  - Detaches an additional drawing primitive from the series.
  - Parameters:
    - primitive: The implementation of ISeriesPrimitive to detach. Does nothing if the primitive was not attached.
```

LANGUAGE: javascript
CODE:
```
const lineSeries = chart.addLineSeries();
console.log(lineSeries.seriesType()); // "Line"

const candlestickSeries = chart.addCandlestickSeries();
console.log(candlestickSeries.seriesType()); // "Candlestick"
```

----------------------------------------

TITLE: TimeScaleOptions: allowBoldLabels
DESCRIPTION: Controls whether major time scale labels are rendered with a bolder font weight. This property is inherited from HorzScaleOptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
allowBoldLabels: boolean
  Allow major time scale labels to be rendered in a bolder font weight.
  Default Value: true
```

----------------------------------------

TITLE: SeriesMarkerBar Properties
DESCRIPTION: Defines the properties for a SeriesMarkerBar, including optional text, size, and price. These properties are inherited from SeriesMarkerBase.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesMarkerBar

LANGUAGE: APIDOC
CODE:
```
SeriesMarkerBar:
  text?: string
    The optional text for the marker.
    Inherited from SeriesMarkerBase.

  size?: number
    The optional size of the marker.
    Default Value: 1
    Inherited from SeriesMarkerBase.

  price?: number
    The price value for exact Y-axis positioning.
    Required when using SeriesMarkerPricePosition position type.
    Inherited from SeriesMarkerBase.
```

----------------------------------------

TITLE: Utility and Base Types
DESCRIPTION: Includes utility types like DeepPartial for creating partial versions of complex types, and base types for values and data providers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/TimeRange

LANGUAGE: typescript
CODE:
```
DeepPartial
BaseValueType
AutoscaleInfoProvider
Background
Nominal
```

----------------------------------------

TITLE: IPanePrimitiveBase Interface
DESCRIPTION: The base interface for series primitives in Lightweight Charts Next. It must be implemented to add external graphics to series. It includes a type parameter TPaneAttachedParameters for unknown types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IPanePrimitiveBase

LANGUAGE: APIDOC
CODE:
```
Interface: IPanePrimitiveBase<TPaneAttachedParameters>

Base interface for series primitives. It must be implemented to add some external graphics to series.

Type parameters:
• TPaneAttachedParameters = unknown
```

----------------------------------------

TITLE: CandlestickSeriesPartialOptions Type Alias
DESCRIPTION: Defines the `CandlestickSeriesPartialOptions` type alias for Lightweight Charts version 3.8. This type represents optional properties for candlestick series, inheriting from `SeriesPartialOptions` and extending `CandlestickStyleOptions`.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions : SeriesPartialOptions<CandlestickStyleOptions>

Description: Represents candlestick series options where all properties are optional.
```

----------------------------------------

TITLE: Candlestick Series Options
DESCRIPTION: Defines the complete options for configuring a candlestick series in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesOptions:
  upColor?: 
    string
    The color of candlesticks when the close price is higher than the open price. Defaults to '#26a69a'.
  downColor?: 
    string
    The color of candlesticks when the close price is lower than the open price. Defaults to '#ef5350'.
  borderVisible?: 
    boolean
    Whether the candlestick borders are visible. Defaults to true.
  borderColor?: 
    string
    The color of the candlestick borders. Defaults to '#888888'.
  wickVisible?: 
    boolean
    Whether the candlestick wicks are visible. Defaults to true.
  wickColor?: 
    string
    The color of the candlestick wicks. Defaults to '#888888'.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: Provides links to documentation for type aliases, variables, and functions in the Next version of Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Type Aliases: Point
Variables: Point
Functions: Point
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: This section details the various options and type definitions for different series types supported by Lightweight Charts, including Area, Bar, Candlestick, and Histogram series. It covers both full and partial options for customization.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/LineWidth

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CustomSeriesOptions:
  // Options for Custom Series

CustomSeriesPartialOptions:
  // Partial options for Custom Series

CustomSeriesPricePlotValues:
  // Defines values for custom series price plots

ChartOptions:
  // General chart options

CreatePriceLineOptions:
  // Options for creating price lines

ISeriesPrimitive:
  // Interface for series primitives

DataItem:
  // Represents a single data item in a series

BarPrice:
  // Represents a price for a bar

BaseValueType:
  // Base type for values

Coordinate:
  // Represents a coordinate on the chart

Background:
  // Defines background properties

AutoscaleInfoProvider:
  // Provider for autoscale information

DataChangedHandler:
  // Handler for data changed events

DataChangedScope:
  // Scope for data changed events

HorzAlign:
  // Horizontal alignment options

HorzScaleItemConverterToInternalObj:
  // Converter for horizontal scale items

DeepPartial:
  // Utility type for deep partial objects

```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BarPrice

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Data Validation Improvements
DESCRIPTION: Enhancements to data validation for `OhlcData` and `SingleValueData`. The library now includes `isFulfilledBarData` and `isFulfilledLineData` for more accurate data type validation, addressing issues with data integrity.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
import { isFulfilledBarData } from 'lightweight-charts';

// Example usage with OhlcData
const ohlcData = {
  open: 100,
  high: 110,
  low: 95,
  close: 105,
  time: '2023-01-01'
};

if (isFulfilledBarData(ohlcData)) {
  console.log('Valid OhlcData');
} else {
  console.log('Invalid OhlcData');
}
```

----------------------------------------

TITLE: Plugin Typings Migration (v4 to v5)
DESCRIPTION: This section details the renaming of plugin types and interfaces from version 4 to version 5 of Lightweight Charts, necessitated by the introduction of Pane Primitives. It lists the specific changes in interface names.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/migrations/from-v4-to-v5

LANGUAGE: typescript
CODE:
```
ISeriesPrimitivePaneView → IPrimitivePaneView
ISeriesPrimitivePaneRenderer → IPrimitivePaneRenderer
SeriesPrimitivePaneViewZOrder → PrimitivePaneViewZOrder
```

----------------------------------------

TITLE: AutoScaleMargins Interface
DESCRIPTION: Defines margins for autoscale calculations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  top: number
    Top margin in price units.
  bottom: number
    Bottom margin in price units.
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Maps series data item types to their corresponding structures, considering the horizontal scale item.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>

Maps series data item types to their corresponding structures.
```

----------------------------------------

TITLE: Scale Item Converters and Types
DESCRIPTION: Provides type definitions for horizontal scale items and their conversion to internal objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DataChangedScope

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj:
  (item: HorzScalePriceItem) => InternalHorzScaleItem

HorzScalePriceItem:
  price: number
  label: string

InternalHorzScaleItem:
  key: InternalHorzScaleItemKey
  price: number
  label: string
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Represents a single data point for a candlestick series. Includes time, open, high, low, and close values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/AreaStyleOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  time: Time
  open: number
  high: number
  low: number
  close: number

// Related Interfaces:
// AreaData, BaselineData, BarData, HistogramData, CustomBarItemData
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: This section details the API for Lightweight Charts, including type aliases for various chart options and configurations. It covers options for Area Series, Bar Series, Candlestick Series, Histogram Series, and general Chart Options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  topColor?: string
  bottomColor?: string

AreaSeriesPartialOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  topColor?: string
  bottomColor?: string

AutoscaleInfoProvider:
  // Interface for providing autoscale information

Background:
  type?: 'solid' | 'gradient'
  color?: string
  topColor?: string
  bottomColor?: string

BarPrice:
  open: number
  high: number
  low: number
  close: number

BarSeriesOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  thinCheck?: boolean
  visible?: boolean
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean
  wickVisible?: boolean
  borderVisible?: boolean
  tickMarkVisible?: boolean

BarSeriesPartialOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  thinCheck?: boolean
  visible?: boolean
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean
  wickVisible?: boolean
  borderVisible?: boolean
  tickMarkVisible?: boolean

BaseValueType:
  'number' | 'integer' | 'time'

BaselineSeriesOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  topColor?: string
  bottomColor?: string
  baseLevelPercentage?: number

BaselineSeriesPartialOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  topColor?: string
  bottomColor?: string
  baseLevelPercentage?: number

CandlestickSeriesOptions:
  title?: string
  color?: string
  wickVisible?: boolean
  borderVisible?: boolean
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean

CandlestickSeriesPartialOptions:
  title?: string
  color?: string
  wickVisible?: boolean
  borderVisible?: boolean
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean

ChartOptions:
  width?: number
  height?: number
  layout?: ChartLayoutOptions
  grid?: GridOptions
  crosshair?: CrosshairOptions
  timeScale?: TimeScaleOptions
  rightPriceScale?: PriceScaleOptions
  leftPriceScale?: PriceScaleOptions
  handleScale?: HandleScaleOptions
  handleScroll?: HandleScrollOptions
  watermark?: WatermarkOptions
  localization?: LocalizationOptions
  timeLocator?: TimeLocatorOptions
  autoSize?: boolean
  kineticScrolling?: boolean
  layout?: ChartLayoutOptions
  grid?: GridOptions
  crosshair?: CrosshairOptions
  timeScale?: TimeScaleOptions
  rightPriceScale?: PriceScaleOptions
  leftPriceScale?: PriceScaleOptions
  handleScale?: HandleScaleOptions
  handleScroll?: HandleScrollOptions
  watermark?: WatermarkOptions
  localization?: LocalizationOptions
  timeLocator?: TimeLocatorOptions
  autoSize?: boolean
  kineticScrolling?: boolean

Coordinate:
  number

CreatePriceLineOptions:
  price: number
  color?: string
  lineWidth?: number
  lineStyle?: number
  axis?: 'left' | 'right'
  title?: string
  draggable?: boolean
  disableDragEvents?: boolean

CustomSeriesOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean
  wickVisible?: boolean
  borderVisible?: boolean
  tickMarkVisible?: boolean
  priceLineStyles?: PriceLineStyle[]

CustomSeriesPartialOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  priceFormat?: PriceFormat
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean
  wickVisible?: boolean
  borderVisible?: boolean
  tickMarkVisible?: boolean
  priceLineStyles?: PriceLineStyle[]

CustomSeriesPricePlotValues:
  [key: string]: number

DataChangedHandler:
  (scope: DataChangedScope) => void

DataChangedScope:
  'data' | 'options' | 'layout'

DataItem:
  time: Time
  value: number
  color?: string

DeepPartial<T>:
  T extends Record<string, any> ? {
    [P in keyof T]?: DeepPartial<T[P]>;
  } : T

HistogramSeriesOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean

HistogramSeriesPartialOptions:
  title?: string
  color?: string
  lineWidth?: number
  lineStyle?: number
  lineType?: number
  base?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceLineSource?: PriceLineSource
  priceLineVisible?: boolean
  lastValueAnimation?: boolean

HorzAlign:
  'left' | 'center' | 'right'
```

----------------------------------------

TITLE: ISeriesPrimitiveWrapper Interface Documentation
DESCRIPTION: Provides details on the ISeriesPrimitiveWrapper interface, which is extended by various plugin APIs. It includes type parameters and a detach method.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesPrimitiveWrapper

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveWrapper<T, Options>

Description: Interface for a series primitive.

Extended by:
  * ISeriesMarkersPluginApi
  * ISeriesUpDownMarkerPluginApi

Type parameters:
• T
• Options = unknown

Properties:
  detach(): void
    Description: Detaches the plugin from the series.
    Returns: void
```

----------------------------------------

TITLE: Lightweight Charts 4.0 Type Aliases
DESCRIPTION: This section lists and describes various type aliases available in Lightweight Charts version 4.0. These aliases define specific data types used within the charting library, such as price formats, series options, and time-related types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
PriceFormat
PriceFormatterFn
SeriesMarkerPosition
SeriesMarkerShape
SeriesOptions
SeriesPartialOptions
SeriesType
SizeChangeEventHandler
TickMarkFormatter
Time
TimeFormatterFn
TimeRange
TimeRangeChangeEventHandler
UTCTimestamp
VertAlign
VisiblePriceScaleOptions
```

----------------------------------------

TITLE: OhlcData Properties
DESCRIPTION: Defines the properties for Open, High, Low, and Close data points in Lightweight Charts. Includes optional customValues for plugins.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  open: number
    The open price.
  high: number
    The high price.
  low: number
    The low price.
  close: number
    The close price.
  customValues?: Record<string, unknown>
    Optional additional custom values which will be ignored by the library, but could be used by plugins.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Methods
DESCRIPTION: Documentation for methods within the ISeriesPrimitiveBase interface, including paneViews, priceAxisPaneViews, timeAxisPaneViews, autoscaleInfo, and attached.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
paneViews(): readonly ISeriesPrimitivePaneView[]
  - Returns an array of objects representing primitives in the main area of the chart.
  - Must return a new array if the set of views has changed, and the same array if nothing has changed.

priceAxisPaneViews(): readonly ISeriesPrimitivePaneView[]
  - Returns an array of objects representing primitives in the price axis area of the chart.
  - Must return a new array if the set of views has changed, and the same array if nothing has changed.

timeAxisPaneViews(): readonly ISeriesPrimitivePaneView[]
  - Returns an array of objects representing primitives in the time axis area of the chart.
  - Must return a new array if the set of views has changed, and the same array if nothing has changed.

autoscaleInfo(startTimePoint: Logical, endTimePoint: Logical): AutoscaleInfo
  - Returns autoscaleInfo which will be merged with the series base autoscaleInfo.
  - Can be used to expand the autoscale range to include visual elements drawn outside of the series' current visible price range.
  - Important: This method will be evoked very often during scrolling and zooming, so it should be simple or use caching.
  - Parameters:
    - startTimePoint: The start time point for the current visible range.
    - endTimePoint: The end time point for the current visible range.
  - Returns: AutoscaleInfo

attached(param): void
  - Attached Lifecycle hook.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: TimeScalePoint Interface Properties
DESCRIPTION: Documentation for the properties of the TimeScalePoint interface in Lightweight Charts. This includes timeWeight, time, and originalTime, detailing their types and descriptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScalePoint

LANGUAGE: APIDOC
CODE:
```
TimeScalePoint:
  timeWeight: TickMarkWeightValue
    - Weight of the point
  time: object
    - Time of the point
  [species]: "InternalHorzScaleItem"
    - The 'name' or species of the nominal.
  originalTime: unknown
    - Original time for the point
  Properties:
    - timeWeight
    - time
    - originalTime
```

----------------------------------------

TITLE: ISeriesPrimitiveWrapper API
DESCRIPTION: Documentation for the ISeriesPrimitiveWrapper interface, detailing its parameters, return types, and associated methods like detach() and getSeries().

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ISeriesPrimitiveWrapper

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitiveWrapper:
  applyOptions(options: DeepPartial<Options>): void
    Parameters:
      options: DeepPartial<Options> - Options to apply. The options are deeply merged with the current options.
    Returns: void

    Methods:
      detach(): void
      getSeries(): Series
    Extended by:
      Type parameters:
      Properties:
        detach(): void
        getSeries(): Series
        applyOptions()? : void
```

----------------------------------------

TITLE: HistogramSeriesPartialOptions Type Alias
DESCRIPTION: Defines the optional properties for histogram series in Lightweight Charts version 4.0. It extends `SeriesPartialOptions` and incorporates `HistogramStyleOptions`, allowing for flexible customization of histogram series appearance and behavior.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: HistogramSeriesPartialOptions

Inherits from: SeriesPartialOptions < HistogramStyleOptions

Description: Represents histogram series options where all properties are optional.
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These types define the structure and constraints for options, data, and internal representations, facilitating precise chart configuration and data manipulation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial:
  A utility type that makes all properties of a type optional and recursively applies to nested objects.

GreenComponent:
  Represents a component that is visually green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series, allowing for incremental updates.

HorzAlign:
  Defines the horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj:
  A type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item displayed on the horizontal price scale.

IImageWatermarkPluginApi:
  Interface for the Image Watermark Plugin API.

IPanePrimitive:
  Interface for a primitive drawn within a chart pane.

ISeriesPrimitive:
  Interface for a primitive associated with a chart series.

ITextWatermarkPluginApi:
  Interface for the Text Watermark Plugin API.

InternalHorzScaleItem:
  Internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  Key used to identify internal horizontal scale items.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series, allowing for incremental updates.

LineWidth:
  Defines the possible values for a line width.

Logical:
  Represents a logical index or position within the chart's data.

LogicalRange:
  Defines a range based on logical indices.

LogicalRangeChangeEventHandler:
  A function type for handling changes in the logical range.

MouseEventHandler:
  A function type for handling mouse events.

Mutable:
  A utility type that makes all properties of a type mutable.

Nominal:
  Represents a nominal value, often used for discrete categories.

OverlayPriceScaleOptions:
  Options for configuring an overlay price scale.

PercentageFormatterFn:
  A function type for formatting percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn:
  A function type for formatting prices.

PriceToCoordinateConverter:
  A function type for converting price values to chart coordinates.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has an 'applyOptions' method.

PrimitivePaneViewZOrder:
  Defines the z-order for primitives within a pane view.

RedComponent:
  Represents a component that is visually red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker displayed on a chart series.

SeriesMarkerBarPosition:
  Defines the position of a series marker relative to a bar.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerPricePosition:
  Defines the vertical position of a series marker relative to a price level.

SeriesMarkerShape:
  Defines the shape of a series marker.

SeriesMarkerZOrder:
  Defines the z-order for series markers.

SeriesOptions:
  General options for configuring any chart series.

SeriesPartialOptions:
  Partial options for configuring any chart series, allowing for incremental updates.

SeriesType:
  Defines the possible types of chart series (e.g., 'Line', 'Area', 'Histogram').
```

----------------------------------------

TITLE: OhlcData Interface
DESCRIPTION: Defines the structure for a data point representing a financial bar, including time and price information (open, high, low, close). It extends WhitespaceData and can be extended by other data types like BarData and CandlestickData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData<HorzScaleItem>

Represents a bar with a Time and open, high, low, and close prices.

Extends:
  * WhitespaceData<HorzScaleItem>

Extended by:
  * BarData
  * CandlestickData

Type parameters:
• HorzScaleItem = Time

Properties:
### time
> **time** : HorzScaleItem
The bar time.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for configuring a candlestick series, allowing for incremental updates to existing configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: 'string'
    Color of the bars when the close price is higher than the open price.
  downColor?: 'string'
    Color of the bars when the close price is lower than the open price.
  borderVisible?: boolean
    Whether to display borders for the bars.
  borderColor?: 'string'
    Color of the bar borders.
  wickVisible?: boolean
    Whether to display wicks for the bars.
  wickColor?: 'string'
    Color of the bar wicks.
```

----------------------------------------

TITLE: IPanePrimitive Type Alias
DESCRIPTION: Defines the interface for pane primitives, which are external graphics added to a chart pane. It extends IPanePrimitiveBase and PaneAttachedParameter, with a generic type parameter for horizontal scale items, defaulting to Time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/IPanePrimitive

LANGUAGE: APIDOC
CODE:
```
Type alias: IPanePrimitive<HorzScaleItem>

IPanePrimitive <HorzScaleItem>: IPanePrimitiveBase <IPanePrimitiveBase>
  PaneAttachedParameter <PaneAttachedParameter><HorzScaleItem>

Interface for pane primitives. It must be implemented to add some external graphics to a pane.

Type parameters:
• HorzScaleItem = Time
  * Type parameters
```

----------------------------------------

TITLE: Lightweight Charts Next API Documentation
DESCRIPTION: This section details the type aliases available in the unreleased 'Next' version of Lightweight Charts. It includes links to specific type definitions such as TickMarkWeightValue, Time, and VisiblePriceScaleOptions, along with general API reference links.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/InternalHorzScaleItem

LANGUAGE: APIDOC
CODE:
```
Type Aliases:
  - TickMarkWeightValue
  - TickmarksPercentageFormatterFn
  - TickmarksPriceFormatterFn
  - Time
  - TimeFormatterFn
  - TimePointIndex
  - TimeRangeChangeEventHandler
  - UTCTimestamp
  - UpDownMarkersSupportedSeriesTypes
  - VertAlign
  - VisiblePriceScaleOptions
  - YieldCurveSeriesType

Type alias: InternalHorzScaleItem
> **InternalHorzScaleItem** : Nominal<unknown, "InternalHorzScaleItem">
Internal Horizontal Scale Item

Documentation Links:
  - Getting Started: https://tradingview.github.io/lightweight-charts/docs
  - Tutorials: https://tradingview.github.io/lightweight-charts/tutorials
  - API Reference (Latest): https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/InternalHorzScaleItem

Community Links:
  - Stack Overflow: https://stackoverflow.com/questions/tagged/lightweight-charts
  - Twitter: https://twitter.com/tradingview

Related Projects:
  - Advanced Charts: https://www.tradingview.com/charting-library-docs/
  - TradingView Widgets: https://www.tradingview.com/widget/

Copyright © 2025 TradingView, Inc. Built with Docusaurus.
```

----------------------------------------

TITLE: SeriesOptionsMap Interface
DESCRIPTION: Map of series options types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
  Map of series options types.
```

----------------------------------------

TITLE: Time Type Alias
DESCRIPTION: Represents a point in time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/VertAlign

LANGUAGE: APIDOC
CODE:
```
Type alias: Time
(Details for Time would be here if available in the provided text)
```

----------------------------------------

TITLE: OhlcData Interface Documentation
DESCRIPTION: Documentation for the OhlcData interface, which represents a bar with time and open, high, low, and close prices. It details the 'time' and 'open' properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData
Represents a bar with a Time and open, high, low, and close prices.

Extended by:
  * BarData
  * CandlestickData

Properties:

time:
> **time** : Time
The bar time.
* * *

open:
> **open** : number
The open price.
* * *
```

----------------------------------------

TITLE: OhlcData Interface Documentation
DESCRIPTION: Documentation for the OhlcData interface, defining the structure for Open-High-Low-Close data points used in OHLC series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData

Defines the structure for OHLC data points.

```

----------------------------------------

TITLE: SeriesStyleOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesStyleOptionsMap interface, mapping series styles to their options in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesStyleOptionsMap

Maps series styles to their options.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Interface Documentation (Lightweight Charts 4.1)
DESCRIPTION: Documentation for the ISeriesPrimitiveBase interface, which serves as the base for custom series primitives in Lightweight Charts. It includes methods for updating views and retrieving axis labels.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveBase<TSeriesAttachedParameters>
  Base interface for series primitives. It must be implemented to add some external graphics to series

  Type parameters:
  • TSeriesAttachedParameters = unknown

  Methods:
  updateAllViews()
    optional
    > updateAllViews(): void
    This method is called when viewport has been changed, so primitive have to recalculate / invalidate its data
    Returns: void

  priceAxisViews()
    optional
    > priceAxisViews(): readonly ISeriesPrimitiveAxisView[]
    Returns array of labels to be drawn on the price axis used by the series
    Returns: readonly ISeriesPrimitiveAxisView[]
    array of objects; each of then must implement ISeriesPrimitiveAxisView interface
    For performance reasons, the lightweight library uses internal caches based on references to arrays So, this method must return new array if set of views has changed and should try to return the same array if nothing changed

  timeAxisViews()
    optional
    > timeAxisViews(): readonly ISeriesPrimitiveAxisView[]
    Returns array of labels to be drawn on the time axis
    Returns: readonly ISeriesPrimitiveAxisView[]
    array of objects; each of then must implement ISeriesPrimitiveAxisView interface
    For performance reasons, the lightweight library uses internal caches based on references to arrays So, this method must return new array if set of views has changed and should try to return the same array if nothing changed
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Populate Histogram Series with Data
DESCRIPTION: Illustrates how to create and add data points to a histogram series. It includes examples of `HistogramData` and `WhitespaceData` for different time intervals.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/android

LANGUAGE: kotlin
CODE:
```
val data = listOf(
HistogramData(Time.BusinessDay(2019,6,11),40.01f),
HistogramData(Time.BusinessDay(2019,6,12),52.38f),
HistogramData(Time.BusinessDay(2019,6,13),36.30f),
HistogramData(Time.BusinessDay(2019,6,14),34.48f),
WhitespaceData(Time.BusinessDay(2019,6,15)),
WhitespaceData(Time.BusinessDay(2019,6,16)),
HistogramData(Time.BusinessDay(2019,6,17),41.50f),
HistogramData(Time.BusinessDay(2019,6,18),34.82f)
)
histogramSeries.setData(data)
```

----------------------------------------

TITLE: Lightweight Charts General Types
DESCRIPTION: Provides definitions for general types used within Lightweight Charts, including price scales, alignment, coordinate systems, and event handling mechanisms.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
AutoscaleInfoProvider:
  // Provider for autoscale information

Background:
  // Background color or image settings

BarPrice:
  // Represents a price for a bar (e.g., open, high, low, close)

BaseValueType:
  // Base type for values

Coordinate:
  // Represents a coordinate on the chart

DeepPartial<T>:
  // Utility type for deeply nested partial objects

HorzAlign:
  // Horizontal alignment options (e.g., 'left', 'center', 'right')

LineWidth:
  // Type for line width values

Logical:
  // Represents a logical index or position

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Nominal:
  // Represents a nominal value

OverlayPriceScaleOptions:
  // Options for overlay price scales
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: API Reference - CandlestickData
DESCRIPTION: Represents a single data point for a candlestick series. It includes the time, open, high, low, and close values, similar to BarData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/BarStyleOptions

LANGUAGE: APIDOC
CODE:
```
interface CandlestickData {
  time: 'Time'; // Time value for the candlestick
  open: number; // Opening price
  high: number; // Highest price
  low: number;  // Lowest price
  close: number; // Closing price
}
```

----------------------------------------

TITLE: OhlcData Interface
DESCRIPTION: Defines the structure for Open, High, Low, and Close data points used in candlestick and OHLC charts. Requires a timestamp, open, high, low, and close values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  time: Time
  open: number
  high: number
  low: number
  close: number
```

----------------------------------------

TITLE: Lightweight Charts Next Type Aliases
DESCRIPTION: Lists various type aliases available in the 'Next' version of Lightweight Charts, including formatting functions, time-related types, and series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CustomSeriesOptions

LANGUAGE: APIDOC
CODE:
```
TickMarkWeightValue
TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn
Time
TimeFormatterFn
TimePointIndex
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
CustomSeriesOptions
```

----------------------------------------

TITLE: Interface: SeriesDataItemTypeMap<HorzScaleItem> API Documentation
DESCRIPTION: Maps series types to their corresponding data item types, using HorzScaleItem for horizontal scale context. This interface is fundamental for data handling in different series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/Range

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>

Maps series types to their data item types.

Type parameters:
• HorzScaleItem: Type representing an item on the horizontal scale.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling (Double Click)
DESCRIPTION: This section covers the subscription and unsubscription of double-click events on the Lightweight Charts. It details the handler function signature and provides examples for both subscribing and unsubscribing.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IChartApi

LANGUAGE: javascript
CODE:
```
function myDblClickHandler(param) {
  if (!param.point) {
    return;
  }
  console.log(`Double Click at ${param.point.x}, ${param.point.y}. The time is ${param.time}.`);
}

chart.subscribeDblClick(myDblClickHandler);
```

LANGUAGE: javascript
CODE:
```
chart.unsubscribeDblClick(myDblClickHandler);
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Defines extended options for the time-based horizontal scale in Lightweight Charts. It inherits properties from HorzScaleOptions, providing further customization for time-related scaling behavior.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Extended time scale options for time-based horizontal scale.

Extends:
  * HorzScaleOptions

Properties:
  (Details for properties would typically follow here, but are not provided in the input text.)

Example Usage:
(Example usage would typically be provided here, but is not present in the input text.)
```

----------------------------------------

TITLE: SeriesPartialOptions Type
DESCRIPTION: Base type for partial series options, enabling partial updates to series configurations. This allows developers to modify specific aspects of a series without needing to provide all configuration details.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/TickMarkWeightValue

LANGUAGE: APIDOC
CODE:
```
Type alias: SeriesPartialOptions
> **SeriesPartialOptions** : <TData, TStyleOptions>
Base type for partial series options.
```

----------------------------------------

TITLE: Lightweight Charts v1.2.2 Release Notes
DESCRIPTION: Details bug fixes for version 1.2.2 of Lightweight Charts, specifically addressing an issue with rendering multiple datasets with unequal time scales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/release-notes

LANGUAGE: javascript
CODE:
```
/**
 * Lightweight Charts v1.2.2 Release Notes
 *
 * Fixed:
 * - Bug while rendering few datasets with not equal timescale.
 */
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: Provides an overview of the Lightweight Charts API, focusing on methods for adding different series types and their associated data and style options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/series-types

LANGUAGE: APIDOC
CODE:
```
IChartApi:
  addBaselineSeries(options?: BaselineSeriesOptions): BaselineSeries
    Adds a baseline series to the chart.
    options: Configuration for the baseline series, including baseValue and style options.
    Returns: The created BaselineSeries object.

  addCandlestickSeries(options?: CandlestickSeriesOptions): CandlestickSeries
    Adds a candlestick series to the chart.
    options: Configuration for the candlestick series, including colors and border visibility.
    Returns: The created CandlestickSeries object.

SingleValueData:
  value: number
  time: Time

WhitespaceData:
  time: Time

CandlestickData:
  open: number
  high: number
  low: number
  close: number
  time: Time

SeriesOptionsCommon:
  // Common options for all series types

BaselineStyleOptions:
  baseValue: { type: 'price', price: number } | { type: 'time', time: Time }
  topLineColor?: SeriesColor
  topFillColor1?: SeriesColor
  topFillColor2?: SeriesColor
  bottomLineColor?: SeriesColor
  bottomFillColor1?: SeriesColor
  bottomFillColor2?: SeriesColor

CandlestickStyleOptions:
  upColor?: SeriesColor
  downColor?: SeriesColor
  borderVisible?: boolean
  wickUpColor?: SeriesColor
  wickDownColor?: SeriesColor
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Defines options for handling double-clicks on chart axes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
AxisDoubleClickOptions:
  enable?: boolean
    Whether to enable double-click to reset the view. Defaults to true.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: References to type aliases, variables, and functions within the next version of Lightweight Charts, with MouseEventParams serving as an example.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/MouseEventParams

LANGUAGE: APIDOC
CODE:
```
Type Aliases: MouseEventParams
Variables: MouseEventParams
Functions: MouseEventParams
```

----------------------------------------

TITLE: OhlcData Interface Definition
DESCRIPTION: Defines the structure for Open, High, Low, Close data points in Lightweight Charts. It includes the time of the bar and its price values. This interface extends WhitespaceData and is extended by BarData and CandlestickData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData
  Extends: WhitespaceData<HorzScaleItem>
  Extended by: BarData, CandlestickData
  Type parameters:
    HorzScaleItem = Time
  Properties:
    time: HorzScaleItem
      The bar time.
      Overrides: WhitespaceData.time
    open: number
      The open price.
    high: number
      The high price.
    low: number
      The low price.
    close: number
      The close price.
    customValues?: Record<string, unknown>
      Optional. Additional custom values ignored by the library but usable by plugins.
      Inherited from: WhitespaceData.customValues
```

----------------------------------------

TITLE: SingleValueData Interface Properties
DESCRIPTION: Defines the base properties for data points that have a single value, including time and the value itself. This interface is extended by other data types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
SingleValueData:
  time: Time
    - The time of the data.
  value: number
    - Price value of the data.
```

----------------------------------------

TITLE: Type Alias: SeriesPartialOptions
DESCRIPTION: Base type for partial series options, allowing for updates to common properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
SeriesPartialOptions:
  title?: string
  priceScaleId?: string
  base: BaseSeriesOptions

Partial base options for any series type.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PrimitivePaneViewZOrder

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts Formatting and Price Types
DESCRIPTION: Defines types for price formatting, including percentage and general price formatters, and price-to-coordinate conversion.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
PercentageFormatterFn:
  A function type for formatting percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn:
  A function type for formatting prices.

PriceToCoordinateConverter:
  A function type for converting a price value to a coordinate.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Provides options for partially updating a Candlestick Series. This allows for dynamic adjustments to specific properties like colors or visibility without reinitializing the entire series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/LineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: string
  downColor?: string
  borderVisible?: boolean
  borderColor?: string
  wickVisible?: boolean
  wickColor?: string
  barSpacing?: number
  thinCharts?: boolean
  visible?: boolean
  title?: string
  lastValueProvider?: LastValueProvider
  priceLineSource?: PriceLineSource
  priceLineStyle?: LineStyle
  priceLineColor?: string
  priceLineWidth?: number
  autoscaleInfoProvider?: AutoscaleInfoProvider
  priceFormat?: PriceFormat
  formatter?: TickMarkFormatter
  coordinate?: Coordinate
  scaleMargins?: VerticalScaleMargins
  showPriceLine?: boolean
  priceLine?: PriceLineOptions
  highlighted?: boolean
  interactive?: boolean
  disableScale?: boolean
  disableHighlighting?: boolean
  wrap?: boolean
  wrapWidth?: number
  wrapColor?: string
  wrapStyle?: LineStyle
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These include definitions for series options (like HistogramSeriesOptions, LineSeriesOptions), formatting functions (PercentageFormatterFn, PriceFormatterFn), event handlers (MouseEventHandler, SizeChangeEventHandler), and internal data structures for scale items and primitives.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
GreenComponent:
  Represents a component that is green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series.

HorzAlign:
  Defines horizontal alignment options.

HorzScaleItemConverterToInternalObj:
  Converter function for horizontal scale items to internal objects.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

IImageWatermarkPluginApi:
  API for image watermark plugins.

IPanePrimitive:
  Interface for primitives within a chart pane.

ISeriesPrimitive:
  Interface for series primitives.

ITextWatermarkPluginApi:
  API for text watermark plugins.

InternalHorzScaleItem:
  Internal representation of a horizontal scale item.

InternalHorzScaleItemKey:
  Key for internal horizontal scale items.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series.

LineWidth:
  Defines the width of a line.

Logical:
  Represents a logical index.

LogicalRange:
  Defines a range of logical indices.

LogicalRangeChangeEventHandler:
  Handler for logical range change events.

MouseEventHandler:
  Handler for mouse events.

Mutable:
  Indicates a mutable type.

Nominal:
  Represents a nominal value.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn:
  Function type for formatting percentages.

PriceFormat:
  Defines the format for prices.

PriceFormatterFn:
  Function type for formatting prices.

PriceToCoordinateConverter:
  Converter function from price to coordinate.

PrimitiveHasApplyOptions:
  Indicates if a primitive has apply options.

PrimitivePaneViewZOrder:
  Z-order for primitive rendering in a pane view.

RedComponent:
  Represents a component that is red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker on a series.

SeriesMarkerBarPosition:
  Position of a marker relative to a bar.

SeriesMarkerPosition:
  General position of a marker.

SeriesMarkerPricePosition:
  Position of a marker relative to a price.

SeriesMarkerShape:
  Shape of a series marker.

SeriesMarkerZOrder:
  Z-order for series markers.

SeriesOptions:
  General options for any series type.

SeriesPartialOptions:
  Partial options for any series type.

SeriesType:
  Defines the type of a series (e.g., 'Line', 'Histogram').

SizeChangeEventHandler:
  Handler for size change events.
```

----------------------------------------

TITLE: Data Item with Horizontal Scale Item
DESCRIPTION: Represents a data item that includes horizontal scale information.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: DataItem<HorzScaleItem>

Represents a data item with horizontal scale information.

Properties:
  - time: Time
    The time of the data point.
  - value: number
    The value of the data point.
  - color?: string
    The color of the data point.
```

----------------------------------------

TITLE: SeriesType Enum
DESCRIPTION: Enumerates the different types of series that can be rendered on the Lightweight Charts, including Line, Area, Bar, and Candlestick charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/TickMarkWeightValue

LANGUAGE: APIDOC
CODE:
```
Type alias: SeriesType
> **SeriesType** : "Line" | "Area" | "Bar" | "Candlestick" | "Histogram"
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsMap interface, mapping series types to their specific options in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap

Maps series types to their options.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases
DESCRIPTION: This section lists various type aliases available in the unreleased 'Next' version of Lightweight Charts. These include definitions for tick mark weights, formatters, time-related types, and more. It serves as a reference for developers using the upcoming features.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Logical

LANGUAGE: APIDOC
CODE:
```
Type Aliases:

TickMarkWeightValue: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickMarkWeightValue
TickmarksPercentageFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPriceFormatterFn
Time: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Time
TimeFormatterFn: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimeFormatterFn
TimePointIndex: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimePointIndex
TimeRangeChangeEventHandler: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TimeRangeChangeEventHandler
UTCTimestamp: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp
UpDownMarkersSupportedSeriesTypes: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UpDownMarkersSupportedSeriesTypes
VertAlign: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/VertAlign
VisiblePriceScaleOptions: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/VisiblePriceScaleOptions
YieldCurveSeriesType: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/YieldCurveSeriesType

Logical: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Logical
  Represents the `to` or `from` number in a logical range.
  Type: `Nominal<number, "Logical">`
```

----------------------------------------

TITLE: Horizontal Alignment Type
DESCRIPTION: Defines the type for horizontal alignment, used for positioning elements relative to a point.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  // Defines horizontal alignment options
  // Possible values: 'left', 'center', 'right'
  // Example:
  // 'center'
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Map for series data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SingleValueData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap<HorzScaleItem>
Documentation for SeriesDataItemTypeMap.
```

----------------------------------------

TITLE: Series Marker and Type Definitions
DESCRIPTION: Specifies types for series markers, including their position and shape, and the general SeriesType enum.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/AreaSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  // Represents a marker on a series
  // Properties: time, position, color, shape, text, id

SeriesMarkerPosition:
  // Defines the position of a series marker

SeriesMarkerShape:
  // Defines the shape of a series marker

SeriesType:
  // Enum for different types of chart series (e.g., Line, Area, Histogram, Baseline)
  // Possible values: 'Line', 'Area', 'Histogram', 'Baseline'
```

----------------------------------------

TITLE: Formatting and Event Handling Types
DESCRIPTION: Includes types for price and time formatters, as well as event handlers for mouse interactions and size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/AreaSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Converter function from price to chart coordinate

MouseEventHandler:
  // Event handler for mouse interactions

SizeChangeEventHandler:
  // Event handler for chart size changes
```

----------------------------------------

TITLE: SingleValueData Interface
DESCRIPTION: Represents data with a single value, typically used for non-OHLC series like area or histogram.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: SingleValueData
Data with a single value
Properties:
  time:
    time : Time
    The bar time.
  value:
    value : number
    The value.
```

----------------------------------------

TITLE: Series Options and Type Aliases
DESCRIPTION: Defines various options and type aliases for different series types like Area, Bar, Candlestick, Histogram, and Line. These include partial options for incremental updates and specific configurations for visual properties like line width and alignment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

LineSeriesOptions:
  // Options for Line Series

LineSeriesPartialOptions:
  // Partial options for Line Series

LineWidth:
  // Type for line width

HorzAlign:
  // Type for horizontal alignment

BaseValueType:
  // Type for base value

Background:
  // Type for background configuration

BarPrice:
  // Type for bar price representation

Coordinate:
  // Type for coordinate values

CreatePriceLineOptions:
  // Options for creating price lines

DeepPartial:
  // Utility type for deep partial application

Logical:
  // Type for logical values

LogicalRange:
  // Type for logical range

LogicalRangeChangeEventHandler:
  // Event handler for logical range changes

MouseEventHandler:
  // Event handler for mouse events

Nominal:
  // Type for nominal values

AutoscaleInfoProvider:
  // Provider for autoscale information
```

----------------------------------------

TITLE: Candlestick Data Interface Example
DESCRIPTION: Example of how to structure CandlestickData for a Lightweight Chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: javascript
CODE:
```
const candlestickData = [
  { time: '2023-01-01', open: 100, high: 110, low: 95, close: 105 },
  { time: '2023-01-02', open: 105, high: 115, low: 100, close: 112 },
  { time: '2023-01-03', open: 112, high: 118, low: 108, close: 115 }
];
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: This section provides API documentation for Lightweight Charts, covering various functionalities like price scale, time scale, and plugins. It includes details on methods, parameters, and usage examples.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/plugins/pixel-perfect-rendering/widths/candlestick

LANGUAGE: APIDOC
CODE:
```
LightweightCharts API Reference (v4.2)

Overview:
This documentation covers the API for Lightweight Charts version 4.2, including core functionalities, series types, price and time scales, and plugins.

Key Areas:
- Getting Started: https://tradingview.github.io/lightweight-charts/docs/4.2
- Series Types: https://tradingview.github.io/lightweight-charts/docs/4.2/series-types
- Price Scale: https://tradingview.github.io/lightweight-charts/docs/4.2/price-scale
- Time Scale: https://tradingview.github.io/lightweight-charts/docs/4.2/time-scale
- Working with Time Zones: https://tradingview.github.io/lightweight-charts/docs/4.2/time-zones
- Plugins: https://tradingview.github.io/lightweight-charts/docs/4.2/plugins/intro
  - Pixel Perfect Rendering: https://tradingview.github.io/lightweight-charts/docs/4.2/plugins/pixel-perfect-rendering
    - Default Widths (Candlesticks, Columns, Crosshair, Full Bar Width): https://tradingview.github.io/lightweight-charts/docs/4.2/plugins/pixel-perfect-rendering/widths/candlestick
- Migrations: https://tradingview.github.io/lightweight-charts/docs/4.2/migrations
- iOS Integration: https://tradingview.github.io/lightweight-charts/docs/4.2/ios
- Android Integration: https://tradingview.github.io/lightweight-charts/docs/4.2/android
- Release Notes: https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes

Note: Version 4.2 is no longer actively maintained. For the latest documentation, refer to version 5.0.
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesMarkerPosition

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: Data Changed Handler
DESCRIPTION: A callback function type that is invoked when data in a series is changed. Used for reacting to data updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
DataChangedHandler:
  // Callback for data changes
  (scope: DataChangedScope) => void;
```

----------------------------------------

TITLE: YieldCurveChartOptions Properties
DESCRIPTION: Details the properties available in the YieldCurveChartOptions interface, including their types, descriptions, default values, and inheritance.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/YieldCurveChartOptions

LANGUAGE: APIDOC
CODE:
```
YieldCurveChartOptions:
  width: number
    Width of the chart in pixels
    Default Value: 0 (calculated based on container size if not provided)
    Inherited from: ChartOptionsImpl.width

  height: number
    Height of the chart in pixels
    Default Value: 0 (calculated based on container size if not provided)
    Inherited from: ChartOptionsImpl.height

  autoSize: boolean
    Enables automatic resizing of the chart to fit its container.
    Requires ResizeObserver to be available. If ResizeObserver is not available, a warning will appear and the flag will be ignored.
    autoSize option and explicit sizes options width and height do not conflict. If autoSize is specified, width and height options will be ignored unless ResizeObserver has failed. If it fails, the values will be used as fallback.
    The flag autoSize can be set and unset with applyOptions function.
    Example:
    const chart = LightweightCharts.createChart(document.body, {
      autoSize: true,
    });
    Inherited from: ChartOptionsImpl.autoSize

  layout: LayoutOptions
    Layout options
    Inherited from: ChartOptionsImpl.layout

  leftPriceScale: PriceScaleOptions
    Left price scale options
    Inherited from: ChartOptionsImpl.leftPriceScale
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section lists various type aliases used within the Lightweight Charts API for version 4.0. These types define the structure and options for different chart series, including Area, Bar, Candlestick, and Line series, as well as related configurations like price lines, colors, and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions
  - Defines the options for an Area series.

AreaSeriesPartialOptions
  - Defines partial options for an Area series, allowing for incremental updates.

AutoscaleInfoProvider
  - An interface for providing information for autoscaling.

Background
  - Defines the background properties of the chart.

BarPrice
  - Represents the price of a bar (open, high, low, close).

BarSeriesOptions
  - Defines the options for a Bar series.

BarSeriesPartialOptions
  - Defines partial options for a Bar series.

BaseValueType
  - Represents the base value type for calculations.

BaselineSeriesOptions
  - Defines the options for a Baseline series.

BaselineSeriesPartialOptions
  - Defines partial options for a Baseline series.

CandlestickSeriesOptions
  - Defines the options for a Candlestick series.

CandlestickSeriesPartialOptions
  - Defines partial options for a Candlestick series.

Coordinate
  - Represents a coordinate on the chart.

CreatePriceLineOptions
  - Defines the options for creating a price line.

DeepPartial<T>
  - A utility type to make all properties of a type deeply optional.

HistogramSeriesOptions
  - Defines the options for a Histogram series.

HistogramSeriesPartialOptions
  - Defines partial options for a Histogram series.

HorzAlign
  - Defines horizontal alignment options.

LineSeriesOptions
  - Defines the options for a Line series.

LineSeriesPartialOptions
  - Defines partial options for a Line series.

LineWidth
  - Defines the width of a line.

Logical
  - Represents a logical index.

LogicalRange
  - Represents a range of logical indices.

LogicalRangeChangeEventHandler
  - A type for handling logical range change events.

MouseEventHandler
  - A type for handling mouse events.
```

----------------------------------------

TITLE: Lightweight Charts Next API Interfaces
DESCRIPTION: This section lists various interfaces available in the Next version of Lightweight Charts, covering price formatting, series options, time scales, and more.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
PriceFormatBuiltIn
PriceFormatCustom
PriceLineOptions
PriceRange
PriceScaleMargins
PriceScaleOptions
PrimitiveHoveredItem
SeriesAttachedParameter
SeriesDataItemTypeMap
SeriesDefinition
SeriesMarkerBar
SeriesMarkerBase
SeriesMarkerPrice
SeriesMarkersOptions
SeriesOptionsCommon
SeriesOptionsMap
SeriesPartialOptionsMap
SeriesStyleOptionsMap
SeriesUpDownMarker
SingleValueData
SolidColor
TextWatermarkLineOptions
TextWatermarkOptions
TickMark
TimeChartOptions
TimeMark
TimeScaleOptions
TimeScalePoint
TouchMouseEventData
TrackingModeOptions
UpDownMarkersPluginOptions
VerticalGradientColor
WhitespaceData
YieldCurveChartOptions
YieldCurveOptions
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases, Variables, and Functions (Next Version)
DESCRIPTION: References to type aliases, variables, and functions documented for the Next version of Lightweight Charts, specifically related to IYieldCurveChartApi.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IYieldCurveChartApi

LANGUAGE: APIDOC
CODE:
```
Type Aliases
Variables
Functions

These are documented under the IYieldCurveChartApi interface for the Next version of Lightweight Charts.
```

----------------------------------------

TITLE: Mobile Click Subscription Index Issue
DESCRIPTION: This bug fix resolves an issue where the subscribeClick event on mobile devices consistently returned the last index of all items, regardless of the actual click location.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
chart.subscribeClick((param) => {
  // On mobile, param.logical or param.index might be incorrect.
});
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: This section provides links to documentation for type aliases, variables, and functions available in the 'Next' version of Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SolidColor

LANGUAGE: APIDOC
CODE:
```
Type Aliases
Variables
Functions
```

----------------------------------------

TITLE: Lightweight Charts v3.1.2 Bug Fixes
DESCRIPTION: Version 3.1.2 resolves a bug in the Lightweight Charts library where the crosshair was not functioning on touch devices.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
// This fix ensures the crosshair functionality works correctly on touch-enabled devices.
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Types
DESCRIPTION: Defines types related to time representation, logical ranges, and event handlers for time and logical range changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Time:
  Represents a point in time.

TimeFormatterFn:
  A function type for formatting time values.

TimePointIndex:
  An index representing a point in time.

LogicalRange:
  Represents a range of logical values.

LogicalRangeChangeEventHandler:
  An event handler for logical range changes.

TimeRangeChangeEventHandler:
  An event handler for time range changes.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: HistogramData Interface
DESCRIPTION: Represents a single data point for a histogram series, including a value and optionally time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
HistogramData:
  time: "Time"
  value: "number"
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface Documentation
DESCRIPTION: Documentation for the SeriesDataItemTypeMap interface, which maps series types to their corresponding data item types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

Maps series types to their data item types.

```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/LineWidth

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: CandlestickData Interface Documentation (Lightweight Charts 4.1)
DESCRIPTION: Documentation for the CandlestickData interface in Lightweight Charts v4.1. This interface describes the structure for a single data item in a candlestick series, extending OhlcData. It includes properties for time, open, high, low, close prices, and optional color, border color, and wick color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>

Structure describing a single item of data for candlestick series.

Extends:
  OhlcData<HorzScaleItem>

Type parameters:
• HorzScaleItem = Time

Properties:
  color? : string
    Optional color value for certain data item. If missed, color from options is used.
  borderColor? : string
    Optional border color value for certain data item. If missed, color from options is used.
  wickColor? : string
    Optional wick color value for certain data item. If missed, color from options is used.
  time : HorzScaleItem
    The bar time.
    Inherited from: OhlcData.time
  open : number
    The open price.
    Inherited from: OhlcData.open
  high : number
    The high price.
    Inherited from: OhlcData.high
```

----------------------------------------

TITLE: IPanePrimitiveBase Methods
DESCRIPTION: Documentation for methods within the IPanePrimitiveBase interface, used for managing chart primitives.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IPanePrimitiveBase

LANGUAGE: APIDOC
CODE:
```
IPanePrimitiveBase:
  updateAllViews(): void
    - Description: Called when the viewport changes, requiring the primitive to recalculate or invalidate its data.
    - Returns: void

  paneViews(): readonly IPanePrimitivePaneView[]
    - Description: Returns an array of objects representing the primitive in the main chart area. Must return a new array if views change, otherwise the same array to optimize caching.
    - Returns: readonly IPanePrimitivePaneView[]

  attached(param: TPaneAttachedParameters): void
    - Description: Lifecycle hook called when the primitive is attached. Receives parameters for use by the primitive.
    - Parameters:
      - param: TPaneAttachedParameters - An object containing useful references for the attached primitive.
    - Returns: void

  detached(): void
    - Description: Lifecycle hook called when the primitive is detached.
    - Returns: void

  hitTest(x: number, y: number): PrimitiveHoveredItem
    - Description: Performs a hit test at the given coordinates. Used to register hovered objects for crosshair and click events, and can specify a preferred cursor type. Should return the topmost hit.
    - Parameters:
      - x: number - The x-coordinate of the mouse event.
      - y: number - The y-coordinate of the mouse event.
    - Returns: PrimitiveHoveredItem
```

----------------------------------------

TITLE: SeriesUpDownMarker Interface Documentation
DESCRIPTION: Documentation for the SeriesUpDownMarker interface, defining options for up/down markers on series in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesUpDownMarker

Options for up/down markers on series.
```

----------------------------------------

TITLE: SeriesOptionsCommon Interface
DESCRIPTION: Common options for all series types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon
  Common options for all series types.
```

----------------------------------------

TITLE: CandlestickSeriesPartialOptions Type Alias
DESCRIPTION: Defines optional properties for candlestick series in Lightweight Charts 4.0. It extends `SeriesPartialOptions` and incorporates `CandlestickStyleOptions`, allowing for flexible customization of candlestick chart appearances.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions: SeriesPartialOptions<CandlestickStyleOptions>

Represents candlestick series options where all properties are optional.
```

----------------------------------------

TITLE: Time Scale Size Change Subscriptions
DESCRIPTION: Allows subscribing to and unsubscribing from events when the time scale's size changes. Requires a handler function to be passed for both operations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ITimeScaleApi

LANGUAGE: APIDOC
CODE:
```
subscribeSizeChange(handler: SizeChangeEventHandler): void
  Adds a subscription to time scale size changes.
  Parameters:
    handler: Handler (function) to be called when the time scale size changes

unsubscribeSizeChange(handler: SizeChangeEventHandler): void
  Removes a subscription to time scale size changes.
  Parameters:
    handler: Previously subscribed handler
```

LANGUAGE: javascript
CODE:
```
chart.timeScale().subscribeSizeChange(mySizeChangeHandler);
chart.timeScale().unsubscribeSizeChange(mySizeChangeHandler);
```

----------------------------------------

TITLE: Type Checking Time Values with Lightweight Charts Helpers
DESCRIPTION: Illustrates how to check the type of time values received from chart events in Lightweight Charts v4 using utility functions like `isUTCTimestamp` and `isBusinessDay`. This is crucial for correctly processing time data after the v4 migration.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/migrations/from-v3-to-v4

LANGUAGE: javascript
CODE:
```
import{
  createChart,
  isUTCTimestamp,
  isBusinessDay,
}from'lightweight-charts';

const chart =createChart(document.body);

chart.subscribeClick(param=>{
if(param.time===undefined){
// the time is undefined, i.e. there is no any data point where a time could be received from
return;
}

if(isUTCTimestamp(param.time)){
// param.time is UTCTimestamp
}elseif(isBusinessDay(param.time)){
// param.time is a BusinessDay object
}else{
// param.time is a business day string in ISO format, e.g. '2010-01-01'
}
});
```

----------------------------------------

TITLE: HistogramSeriesPartialOptions Type Alias
DESCRIPTION: Defines optional properties for histogram series in Lightweight Charts version 3.8. It extends `SeriesPartialOptions` and incorporates `HistogramStyleOptions`, allowing for flexible customization of histogram chart appearances.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions : SeriesPartialOptions<HistogramStyleOptions>
Represents histogram series options where all properties are optional.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesMarkerPosition

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: TimeScaleOptions Properties
DESCRIPTION: Details the various properties available for configuring the time scale in Lightweight Charts. This includes settings for offsets, spacing, visibility, and formatting of time-related elements.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  rightOffset: number
    Offset in pixels from the right edge of the chart.
  barSpacing: number
    The spacing between bars in pixels.
  minBarSpacing: number
    The minimum spacing between bars in pixels.
  fixLeftEdge: boolean
    Fixes the left edge of the chart to the first visible bar.
  fixRightEdge: boolean
    Fixes the right edge of the chart to the last visible bar.
  lockVisibleTimeRangeOnResize: boolean
    Locks the visible time range when the chart is resized.
  rightBarStaysOnScroll: boolean
    Ensures the rightmost bar stays on the right edge when scrolling.
  borderVisible: boolean
    Shows or hides the border of the time scale.
  borderColor: string
    Sets the color of the time scale border.
  visible: boolean
    Shows or hides the entire time scale.
  timeVisible: boolean
    Shows or hides the time labels on the time scale.
  secondsVisible: boolean
    Shows or hides seconds in the time labels.
  shiftVisibleRangeOnNewBar: boolean
    Shifts the visible range when a new bar is added.
  allowShiftVisibleRangeOnWhitespaceReplacement: boolean
    Allows shifting the visible range when whitespace is replaced.
  ticksVisible: boolean
    Shows or hides the ticks on the time scale.
  tickMarkMaxCharacterLength?: number
    Maximum character length for tick marks.
  uniformDistribution: boolean
    Distributes tick marks uniformly.
  minimumHeight: number
    Minimum height of the time scale.
  allowBoldLabels: boolean
    Allows bold labels for tick marks.
  tickMarkFormatter?: (time: Time, tickMarkType: TickMarkType) => string
    Custom formatter for tick marks.
```

----------------------------------------

TITLE: Candlestick Series Options
DESCRIPTION: Defines the options for a Candlestick Series, including styling and data properties. This is a partial type, meaning not all properties are required.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CustomSeriesPricePlotValues

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesOptions:
  // Options for a candlestick series

CandlestickSeriesPartialOptions:
  // Partial options for a candlestick series
```

----------------------------------------

TITLE: Logical Type
DESCRIPTION: Represents a logical index or position on the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
Logical:
  number
```

----------------------------------------

TITLE: TimeScalePoint Interface Documentation
DESCRIPTION: Documentation for the TimeScalePoint interface, representing a point on the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint

Represents a point on the time scale.
```

----------------------------------------

TITLE: Utility and Event Type Aliases
DESCRIPTION: Provides type aliases for utility types and event handlers used within the Lightweight Charts library. This includes types for coordinates, deep partials, logical ranges, and mouse event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/SeriesType

LANGUAGE: APIDOC
CODE:
```
Coordinate:
  // Represents a coordinate on the chart
  number

DeepPartial<T>:
  // Utility type to make all properties of T deeply optional

Logical:
  // Represents a logical index
  number

LogicalRange:
  // Represents a range of logical indices
  from: Logical
  to: Logical

LogicalRangeChangeEventHandler:
  // Handler for logical range change events
  (newRange: LogicalRange | null) => void

MouseEventHandler:
  // Handler for mouse events on the chart
  (event: MouseEvent) => void

AutoscaleInfoProvider:
  // Provider for autoscale information
  getAutoscaleInfo: (data: any) => any

BaseValueType:
  // Base type for values
  number

BarPrice:
  // Represents a price for a bar
  open: number
  high: number
  low: number
  close: number

Background:
  // Defines background properties
  color: string

LineWidth:
  // Defines line width
  number
```

----------------------------------------

TITLE: Lightweight Charts v3.1.3 Bug Fixes
DESCRIPTION: Version 3.1.3 fixes an issue where the `handleScroll` and `handleScale` options were not being applied correctly in the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
chart.applyOptions({
  handleScroll: {
    // ... scroll options
  },
  handleScale: {
    // ... scale options
  }
});
// The fix ensures these options are now correctly processed.
```

----------------------------------------

TITLE: Baseline Series Partial Options
DESCRIPTION: A partial version of BaselineSeriesOptions, allowing for optional properties to be updated.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
BaselineSeriesPartialOptions:
  // Partial options for baseline series
  // Allows updating only specific properties
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DataItem

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Lightweight Charts 4.1 API Type Aliases
DESCRIPTION: This section lists various type aliases used within the Lightweight Charts API version 4.1. These aliases define specific data structures and types for chart elements, options, and event handlers, aiding in precise data manipulation and configuration.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj: Converts horizontal scale items to an internal object format.
ISeriesPrimitive: Interface for series primitives.
InternalHorzScaleItem: Represents an internal horizontal scale item.
InternalHorzScaleItemKey: Key for internal horizontal scale items.
LineSeriesOptions: Defines options for Line Series.
LineSeriesPartialOptions: Defines partial options for Line Series.
LineWidth: Type for specifying line width.
Logical: Represents a logical value.
LogicalRange: Defines a range of logical values.
LogicalRangeChangeEventHandler: Event handler for logical range changes.
MouseEventHandler: Event handler for mouse events.
Mutable: Represents a mutable type.
Nominal: Represents a nominal value.
OverlayPriceScaleOptions: Options for an overlay price scale.
PercentageFormatterFn: Function type for formatting percentages.
PriceFormat: Defines the format for prices.
PriceFormatterFn: Function type for formatting prices.
PriceToCoordinateConverter: Converts price to coordinate.
SeriesMarkerPosition: Position of a series marker.
SeriesMarkerShape: Shape of a series marker.
SeriesOptions: General options for series.
SeriesPartialOptions: Partial options for series.
SeriesPrimitivePaneViewZOrder: Z-order for series primitive pane views.
SeriesType: Type of the series.
SizeChangeEventHandler: Event handler for size changes.
TickMarkFormatter: Formatter for tick marks.
TickMarkWeightValue: Value for tick mark weight.
Time: Represents time.
TimeFormatterFn: Function type for formatting time.
TimePointIndex: Index of a time point.
TimeRangeChangeEventHandler: Event handler for time range changes.
UTCTimestamp: Represents a UTC timestamp.
VertAlign: Vertical alignment.
VisiblePriceScaleOptions: Options for a visible price scale.
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: Defines various type aliases for configuring different series types like Area, Bar, Baseline, Candlestick, and Histogram. Includes options for partial configurations and custom series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/SeriesPrimitivePaneViewZOrder

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

CustomSeriesOptions:
  // Options for Custom Series

CustomSeriesPartialOptions:
  // Partial options for Custom Series
```

----------------------------------------

TITLE: Histogram Series Partial Options
DESCRIPTION: Defines partial options for configuring a histogram series in Lightweight Charts. This allows for incremental updates to series settings.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions:
  // Options for histogram series
  // These are partial options, meaning you can update specific properties without providing the full set.
  // Example:
  // {
  //   color: '#FF0000',
  //   priceLineVisible: false
  // }
```

----------------------------------------

TITLE: BarData Interface Documentation
DESCRIPTION: Documentation for the BarData interface, which describes a single data item for bar series. It extends OhlcData and includes properties like color and time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarData

LANGUAGE: APIDOC
CODE:
```
Interface: BarData<HorzScaleItem>
Structure describing a single item of data for bar series

Type parameters:
• HorzScaleItem = Time

Properties:
• color? : string
Optional color value for certain data item. If missed, color from options is used

• time : HorzScaleItem
The bar time.
Inherited from: OhlcData.time
```

----------------------------------------

TITLE: Background and Series Marker Position Type Aliases
DESCRIPTION: Defines type aliases for background properties and the position of series markers within Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/SeriesMarkerPosition

LANGUAGE: APIDOC
CODE:
```
Background:
  - Defines properties related to the chart's background.
SeriesMarkerPosition:
  - Specifies the position of a marker on a series.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for configuring a Candlestick Series, allowing for incremental updates to existing Candlestick Series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: string
  downColor?: string
  borderVisible?: boolean
  borderColor?: string
  wickVisible?: boolean
  wickColor?: string
  base?: BaseValueType
  priceLineSource?: SeriesPriceLineSource
  crosshairMarkerVisible?: boolean
  crosshairMarkerBorderColor?: string
  crosshairMarkerBackgroundColor?: string
  visible?: boolean
  title?: string
  lastValueProvider?: LastValueProvider
  priceFormat?: PriceFormat
  base?: BaseValueType
  autoscaleInfoProvider?: AutoscaleInfoProvider
  scaleMargins?: ScaleMargins
  thinCharts?: boolean
  syncTooltips?: boolean
  interactive?: boolean
  tooltipDecorator?: TooltipDecorator
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: AutoScaleMargins Interface
DESCRIPTION: Options for controlling automatic scaling of margins.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  top: boolean
    Enable or disable automatic scaling of the top margin.
  bottom: boolean
    Enable or disable automatic scaling of the bottom margin.
```

----------------------------------------

TITLE: Histogram Series Partial Options
DESCRIPTION: Defines partial options for configuring a Histogram Series, allowing for incremental updates to existing Histogram Series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions:
  color?: string
  base?: BaseValueType
  priceLineSource?: SeriesPriceLineSource
  crosshairMarkerVisible?: boolean
  crosshairMarkerBorderColor?: string
  crosshairMarkerBackgroundColor?: string
  visible?: boolean
  title?: string
  lastValueProvider?: LastValueProvider
  priceFormat?: PriceFormat
  base?: BaseValueType
  autoscaleInfoProvider?: AutoscaleInfoProvider
  scaleMargins?: ScaleMargins
  thinCharts?: boolean
  syncTooltips?: boolean
  interactive?: boolean
  tooltipDecorator?: TooltipDecorator
```

----------------------------------------

TITLE: Candlestick Data Interface
DESCRIPTION: Defines the structure for data points used in Candlestick series. It includes properties for time, open, high, low, and close prices, similar to BarData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SeriesOptionsMap

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>
  - Represents a data point for a Candlestick series.
  - Properties:
    - time: The time value of the data point.
    - open: The opening price.
    - high: The highest price.
    - low: The lowest price.
    - close: The closing price.
    - color?: string
    - // Other optional properties related to HorzScaleItem
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HorzAlign

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Deep Partial Utility Type
DESCRIPTION: A utility type that makes all properties of a type, and all of their nested properties, optional.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  // Makes all properties of T and its nested properties optional.
  // Useful for creating partial configurations.
  // Example:
  // type MyOptions = {
  //   a: number;
  //   b: {
  //     c: string;
  //   };
  // };
  // type PartialMyOptions = DeepPartial<MyOptions>;
  // // PartialMyOptions will be:
  // // {
  // //   a?: number;
  // //   b?: {
  // //     c?: string;
  // //   };
  // // }
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Coordinate

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: SeriesMarkerBase Interface Documentation
DESCRIPTION: Documentation for the SeriesMarkerBase interface, the base interface for all series markers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesMarkerBase

The base interface for all series markers.
```

----------------------------------------

TITLE: Base Value Type
DESCRIPTION: Defines the base value type, typically a number.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: BaseValueType

Represents the base value type.

Type:
  number
```

----------------------------------------

TITLE: Chart Event Subscriptions and Unsubscriptions
DESCRIPTION: This section details how to subscribe to and unsubscribe from various chart events, including double-click and crosshair movement. It outlines the handler parameters, return types, and provides code examples for each.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IChartApi

LANGUAGE: APIDOC
CODE:
```
subscribeDblClick(handler: MouseEventHandler<Time>): void
  - Handler to be called on mouse double-click.
  - Parameters:
    - handler: MouseEventHandler<Time> - Handler to be called on mouse double-click.
  - Returns: void
  - Inherited from: IChartApiBase.subscribeDblClick
  - Example:
    function myDblClickHandler(param) {
      if (!param.point) {
        return;
      }
      console.log(`Double Click at ${param.point.x}, ${param.point.y}. The time is ${param.time}.`);
    }
    chart.subscribeDblClick(myDblClickHandler);

unsubscribeDblClick(handler: MouseEventHandler<Time>): void
  - Unsubscribe a handler that was previously subscribed using subscribeDblClick.
  - Parameters:
    - handler: MouseEventHandler<Time> - Previously subscribed handler
  - Returns: void
  - Inherited from: IChartApiBase.unsubscribeDblClick
  - Example:
    chart.unsubscribeDblClick(myDblClickHandler);

subscribeCrosshairMove(handler: MouseEventHandler<Time>): void
  - Subscribe to the crosshair move event.
  - Parameters:
    - handler: MouseEventHandler<Time> - Handler to be called on crosshair move.
  - Returns: void
  - Inherited from: IChartApiBase.subscribeCrosshairMove
  - Example:
    function myCrosshairMoveHandler(param) {
      if (!param.point) {
        return;
      }
      console.log(`Crosshair moved to ${param.point.x}, ${param.point.y}. The time is ${param.time}.`);
    }
    chart.subscribeCrosshairMove(myCrosshairMoveHandler);

unsubscribeCrosshairMove(handler: MouseEventHandler<Time>): void
  - Unsubscribe a handler that was previously subscribed using subscribeCrosshairMove.
  - Parameters:
    - handler: MouseEventHandler<Time> - Previously subscribed handler
  - Returns: void
  - Inherited from: IChartApiBase.unsubscribeCrosshairMove
```

----------------------------------------

TITLE: Series Options Common - baseLineStyle
DESCRIPTION: Defines the base line style for series, suitable for percentage and indexedTo100 scales. The default value is LineStyle.Solid.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SeriesOptionsCommon

LANGUAGE: APIDOC
CODE:
```
baseLineStyle: LineStyle
  Base line style. Suitable for percentage and indexedTo100 scales.
  Default Value: {@link LineStyle.Solid}
```

----------------------------------------

TITLE: Chart Options: Related Properties
DESCRIPTION: Lists properties that extend or are related to the main chart options, including dimensions, layout, price scales, time scale, and interaction controls.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ChartOptionsBase

LANGUAGE: APIDOC
CODE:
```
width: number
height: number
autoSize: boolean
layout: LayoutOptions
leftPriceScale: PriceScaleOptions
rightPriceScale: PriceScaleOptions
overlayPriceScales: OverlayPriceScalesOptions
timeScale: TimeScaleOptions
crosshair: CrosshairOptions
grid: GridOptions
handleScroll: boolean
handleScale: boolean
kineticScroll: boolean
trackingMode: TrackingModeOptions
localization: LocalizationOptionsBase
addDefaultPane: boolean
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: Improve OhlcData and SingleValueData Validation
DESCRIPTION: Enhances data validation for `OhlcData` and `SingleValueData` by introducing `isFulfilledBarData` and `isFulfilledLineData` respectively. This ensures more accurate data type validation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes

LANGUAGE: javascript
CODE:
```
// Example usage of validation functions (conceptual)
// import { isFulfilledBarData } from 'lightweight-charts';

// const ohlcData = { time: '2023-01-01', open: 100, high: 110, low: 95, close: 105 };
// if (isFulfilledBarData(ohlcData)) {
//   console.log('Valid OhlcData');
// }
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for a single data item in a candlestick series. It extends OhlcData and includes optional color and borderColor properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData
Structure describing a single item of data for candlestick series
Extends:
  * OhlcData
Properties:
color?:
> `optional` **color** : `string`
Optional color value for certain data item. If missed, color from options is used
* * *
borderColor?:
> `optional` **borderColor** : `string`
Optional border color value for certain data item. If missed, color from options is used
* * *
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: References for type aliases, variables, and functions available in the next version of Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScalePoint

LANGUAGE: APIDOC
CODE:
```
Type Aliases
Variables
Functions
```

----------------------------------------

TITLE: CandlestickStyleOptions Interface
DESCRIPTION: Options for styling candlestick series, including colors for rising and falling candles, borders, and wicks.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
CandlestickStyleOptions:
  upColor?: Colord
  downColor?: Colord
  borderUpColor?: Colord
  borderDownColor?: Colord
  wickUpColor?: Colord
  wickDownColor?: Colord
  priceLineStyle?: LineStyle
  priceLineColor?: Colord
  priceLineWidth?: LineWidth
```

----------------------------------------

TITLE: Series Data Types
DESCRIPTION: Defines the different types of data that can be used for series in Lightweight Charts. This includes specific data structures for Candlestick, Area, Baseline, Line, and Histogram series, as well as a common WhitespaceData type.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Candlestick:
  Type: CandlestickData | WhitespaceData
  Description: The types of candlestick series data.

Area:
  Type: AreaData | WhitespaceData
  Description: The types of area series data.

Baseline:
  Type: BaselineData | WhitespaceData
  Description: The types of baseline series data.

Line:
  Type: LineData | WhitespaceData
  Description: The types of line series data.

Histogram:
  Type: HistogramData | WhitespaceData
  Description: The types of histogram series data.

Properties:
  Bar: Refers to properties related to bar charts.
  Candlestick: Refers to properties related to candlestick charts.
  Area: Refers to properties related to area charts.
  Baseline: Refers to properties related to baseline charts.
  Line: Refers to properties related to line charts.
  Histogram: Refers to properties related to histogram charts.
```

----------------------------------------

TITLE: Running the Android Example
DESCRIPTION: Instructions on how to run the example application for Lightweight Charts on Android. This requires cloning the repository, opening it in Android Studio, and having NodeJS/NPM installed.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/android

LANGUAGE: bash
CODE:
```
git clone https://github.com/tradingview/lightweight-charts-android.git
cd lightweight-charts-android
# Open in Android Studio and run
```

----------------------------------------

TITLE: Data Item with Horizontal Scale Item
DESCRIPTION: Defines a data item structure that includes information relevant to the horizontal scale, typically used for time-series data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: DataItem<HorzScaleItem>
  
  Represents a data item with horizontal scale information.
  
  Properties:
    - time: HorzScaleItem
      The time value for the data point.
    - value: number
      The price or value for the data point.
    - ... (other potential data properties)

  Example:
  const dataPoint = {
    time: 1678886400, // Unix timestamp
    value: 100.50,
  };

```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for configuring a Candlestick Series, allowing for incremental updates to existing Candlestick Series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UpDownMarkersSupportedSeriesTypes

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series
  // Allows updating specific properties of an existing Candlestick Series.
```

----------------------------------------

TITLE: CandlestickStyleOptions Interface
DESCRIPTION: Defines the style options for candlestick series in Lightweight Charts. It includes properties for the color of rising and falling candles, and whether candle wicks are visible.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickStyleOptions:
  upColor: string
    Color of rising candles.
    Default Value: '#26a69a'
  downColor: string
    Color of falling candles.
    Default Value: '#ef5350'
  wickVisible: boolean
    Enable high and low prices candle wicks.
    Default Value: true
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CustomSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Chart Options
DESCRIPTION: Defines the overall options for the chart, including layout, time scale, and series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: ChartOptions

Represents the options for the chart.

Properties:
  - width?: number
    The width of the chart.
  - height?: number
    The height of the chart.
  - layout?: LayoutOptions
    Options for the chart layout.
  - timeScale?: TimeScaleOptions
    Options for the time scale.
  - crosshairOptions?: CrosshairOptions
    Options for the crosshair.
  - gridOptions?: GridOptions
    Options for the grid.
  - priceScaleOptions?: PriceScaleOptions
    Options for the price scale.
  - handleScale?: HandleScaleOptions
    Options for handling scale events.
  - handleScroll?: HandleScrollOptions
    Options for handling scroll events.
  - localization?: LocalizationOptions
    Options for localization.
  - overlay?: boolean
    Whether the chart is an overlay.
  - autoSize?: boolean
    Whether the chart should automatically resize.
```

----------------------------------------

TITLE: WhitespaceData Time Property
DESCRIPTION: Documentation for the 'time' property within the WhitespaceData interface. It specifies the type and provides links to examples and related properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/WhitespaceData

LANGUAGE: APIDOC
CODE:
```
WhitespaceData.time:
  Type: Time
  Description: The time of the data.
  Links:
    - Example: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/WhitespaceData#example
    - Properties: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/WhitespaceData#properties
    - Self: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/WhitespaceData#time
```

----------------------------------------

TITLE: SeriesPartialOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesPartialOptionsMap interface, used for applying partial updates to series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesPartialOptionsMap

Applies partial updates to series options.

```

----------------------------------------

TITLE: SeriesOptionsCommon Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsCommon interface, containing common options for all series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BusinessDay

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon
Contains common options for all series types.
```

----------------------------------------

TITLE: Interface: HistogramStyleOptions
DESCRIPTION: Represents style options for a histogram series in Lightweight Charts. It defines properties like 'color' for column color and 'base' for the initial level of histogram columns. The documentation notes that version 4.2 is outdated and directs users to version 5.0.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: HistogramStyleOptions

Represents style options for a histogram series.

Properties:
  color: string
    Column color.
    Default Value: '#26a69a'
  base: number
    Initial level of histogram columns.
```

LANGUAGE: typescript
CODE:
```
interface HistogramStyleOptions {
  color?: string;
  base?: number;
}
```

----------------------------------------

TITLE: Candlestick Series Options
DESCRIPTION: Defines the options for a Candlestick Series in Lightweight Charts. This includes properties for the color of rising and falling candles, and their borders.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesOptions:
  // Options for a candlestick series
  // Inherits from BaseSeriesOptions
  upColor?: string;
  downColor?: string;
  borderUpColor?: string;
  borderDownColor?: string;
  wickUpColor?: string;
  wickDownColor?: string;
  
CandlestickSeriesPartialOptions:
  // Partial options for a candlestick series, allowing for incremental updates
  // Inherits from BaseSeriesPartialOptions
```

----------------------------------------

TITLE: Get Series Type
DESCRIPTION: Retrieves the current type of the chart series (e.g., Line, Candlestick). Includes examples for different series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ISeriesApi

LANGUAGE: javascript
CODE:
```
const lineSeries = chart.addSeries(LineSeries);
console.log(lineSeries.seriesType());// "Line"

const candlestickSeries = chart.addCandlestickSeries();
console.log(candlestickSeries.seriesType());// "Candlestick"
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for a single data item in a candlestick series. It extends OhlcData and includes optional color and borderColor properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>
Structure describing a single item of data for candlestick series

Type parameters:
• HorzScaleItem = Time

Properties:
color?:
> optional color : string
Optional color value for certain data item. If missed, color from options is used

borderColor?:
> optional borderColor : string
Optional border color value for certain data item. If missed, color from options is used
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Options for styling histogram series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color: string
    Color of the histogram.
```

----------------------------------------

TITLE: Add Series in Lightweight Charts v5
DESCRIPTION: Demonstrates how to add different series types (Line, Area, Bar, Baseline, Candlestick, Histogram) to a chart in Lightweight Charts v5 using the `addSeries` method with the respective Series constructor.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/migrations/from-v4-to-v5

LANGUAGE: javascript
CODE:
```
import { createChart, LineSeries, AreaSeries, BarSeries, BaselineSeries, CandlestickSeries, HistogramSeries } from 'lightweight-charts';

const chart = createChart(container, {});

const lineSeries = chart.addSeries(LineSeries, { color: 'red' });
const areaSeries = chart.addSeries(AreaSeries, { color: 'green' });
const barSeries = chart.addSeries(BarSeries, { color: 'blue' });
const baselineSeries = chart.addSeries(BaselineSeries, { color: 'orange' });
const candlestickSeries = chart.addSeries(CandlestickSeries, { color: 'purple' });
const histogramSeries = chart.addSeries(HistogramSeries, { color: 'brown' });
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CustomColorParser

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: CustomStyleOptions Interface
DESCRIPTION: Base interface for custom series style options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CustomStyleOptions:
  lineStyle?: LineStyle
    The style of the line.
  lineColor?: string
    The color of the line.
  lineWidth?: number
    The width of the line.
```

----------------------------------------

TITLE: Histogram Series Partial Options
DESCRIPTION: Defines partial options for configuring a histogram series in Lightweight Charts. This allows for incremental updates to existing series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions:
  base?: 
    "open" | "close" | "high" | "low"
    The base value for histogram bars. Defaults to "close".
  color?: 
    string
    The color of the histogram bars. Defaults to '#26a69a'.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: CustomSeriesWhitespaceData Interface
DESCRIPTION: Data structure for custom series whitespace.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CustomSeriesWhitespaceData:
  time: Time | BusinessDay
    The time of the whitespace.
  price: number
    The price level of the whitespace.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/InternalHorzScaleItem

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: Defines the options and types for different series types in Lightweight Charts, including Area, Bar, Candlestick, Histogram, and Baseline series. These options control the visual appearance and behavior of each series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series
  // Properties include color, lineColor, topColor, bottomColor, etc.

AreaSeriesPartialOptions:
  // Partial options for Area Series, allowing for overriding specific properties.

BarSeriesOptions:
  // Options for Bar Series
  // Properties include color, open, high, low, close, etc.

BarSeriesPartialOptions:
  // Partial options for Bar Series.

BaselineSeriesOptions:
  // Options for Baseline Series
  // Properties include topFillColor, bottomFillColor, etc.

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series.

CandlestickSeriesOptions:
  // Options for Candlestick Series
  // Properties include color, upColor, downColor, etc.

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series.

HistogramSeriesOptions:
  // Options for Histogram Series
  // Properties include color, etc.

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series.

CustomSeriesOptions:
  // Options for Custom Series

CustomSeriesPartialOptions:
  // Partial options for Custom Series.

BaseValueType:
  // Base type for values used in the chart.

Coordinate:
  // Represents a coordinate on the chart.

BarPrice:
  // Represents the price of a bar (open, high, low, close).

Background:
  // Defines the background properties of the chart.

CreatePriceLineOptions:
  // Options for creating a price line.

AutoscaleInfoProvider:
  // Interface for providing autoscale information.

DataChangedHandler:
  // Handler for data changed events.

DataChangedScope:
  // Scope of data change.

DataItem:
  // Represents a single data item in a series.

DeepPartial<T>:
  // Utility type to make all properties of a type deeply optional.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScaleItemConverterToInternalObj

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Data Structures for Series
DESCRIPTION: Interfaces defining the data structures used for different types of chart series, including Area, Bar, Candlestick, and Histogram.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/AreaStyleOptions

LANGUAGE: APIDOC
CODE:
```
AreaData:
  time: Time
  value: number

BarData:
  time: Time
  open: number
  high: number
  low: number
  close: number

CandlestickData:
  time: Time
  open: number
  high: number
  low: number
  close: number

HistogramData:
  time: Time
  value: number
```

----------------------------------------

TITLE: Primitive and Utility Types
DESCRIPTION: Defines types for chart primitives, background configurations, and data change handlers. Includes interfaces for series primitives and providers for autoscale information.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/Time

LANGUAGE: typescript
CODE:
```
interface ISeriesPrimitive { ... };
type Background = { type: 'solid', color: string } | { type: 'gradient', colors: string[] };
type AutoscaleInfoProvider = { ... };
type DataChangedHandler = (scope: DataChangedScope) => void;
type DataChangedScope = { ... };
type BarPrice = number;
type BaseValueType = number;
type HorzAlign = 'left' | 'center' | 'right';
```

----------------------------------------

TITLE: Interface: SeriesOptionsCommon
DESCRIPTION: Common options for all series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon
  Common options for all series types.
```

----------------------------------------

TITLE: BaselineSeriesPartialOptions Type Alias
DESCRIPTION: Defines the partial options for configuring a Baseline Series in Lightweight Charts. This allows for incremental updates to existing series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
BaselineSeriesPartialOptions:
  // Options for the baseline series
  // These options are partial, meaning you can update only the properties you need.
  priceFormat?: PriceFormat;
  base?: BaseValueType;
  autoscaleInfoProvider?: AutoscaleInfoProvider;
  visible?: boolean;
  title?: string;
  overlay?: boolean;
  priceLineSource?: SeriesPriceLineSource;
  priceLineVisible?: boolean;
  baseLineVisible?: boolean;
  // ... other potential properties for baseline series customization
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Chart API Methods
DESCRIPTION: Provides documentation for various methods available on the chart API, including clearing crosshair positions and retrieving pane dimensions and horizontal scale behavior.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IChartApiBase

LANGUAGE: APIDOC
CODE:
```
clearCrosshairPosition(): void
  Clears the crosshair position within the chart.
  Returns: void


```

LANGUAGE: APIDOC
CODE:
```
paneSize(paneIndex?: number): PaneSize
  Returns the dimensions of the chart pane (the plot surface which excludes time and price scales).
  Parameters:
    paneIndex?: number - The index of the pane (defaults to 0)
  Returns:
    PaneSize - Dimensions of the chart pane


```

LANGUAGE: APIDOC
CODE:
```
horzBehaviour(): IHorzScaleBehavior<HorzScaleItem>
  Returns the horizontal scale behaviour.
  Returns:
    IHorzScaleBehavior<HorzScaleItem> - The horizontal scale behaviour object.
```

----------------------------------------

TITLE: Lightweight Charts 3.8 Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 3.8, including options for price scales, series markers, and time formatting. These aliases define the structure and types for chart configurations and data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
OverlayPriceScaleOptions
PriceFormat
PriceFormatterFn
SeriesMarkerPosition
SeriesMarkerShape
SeriesOptions
SeriesPartialOptions
SeriesType
SizeChangeEventHandler
TickMarkFormatter
Time
TimeFormatterFn
TimeRange
TimeRangeChangeEventHandler
UTCTimestamp
VertAlign
VisiblePriceScaleOptions
```

----------------------------------------

TITLE: Lightweight Charts Next API Base Interface: ISeriesPrimitiveBase
DESCRIPTION: The ISeriesPrimitiveBase interface serves as the foundation for all series primitives in Lightweight Charts. Implementing this interface allows for the addition of custom external graphics to chart series, providing a base structure for such elements.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveBase<TSeriesAttachedParameters>
Base interface for series primitives. It must be implemented to add some external graphics to series.
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API for defining chart series options and related configurations. It covers options for Area, Baseline, Candlestick, Histogram, and Line series, as well as general types like Coordinates, Colors, and Event Handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/BaselineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series
  topColor?: string;
  bottomColor?: string;
  lineColor?: string;
  lineWidth?: number;
  base?: number;

AreaSeriesPartialOptions:
  // Partial options for Area Series
  topColor?: string;
  bottomColor?: string;
  lineColor?: string;
  lineWidth?: number;
  base?: number;

AutoscaleInfoProvider:
  // Provider for autoscale information
  autoscaleInfo(data: SeriesItem[]): AutoscaleInfo;

Background:
  // Background color or image
  backgroundColor?: string;

BarPrice:
  // Price for a bar
  open: number;
  high: number;
  low: number;
  close: number;

BarSeriesOptions:
  // Options for Bar Series
  upColor?: string;
  downColor?: string;
  wickUpColor?: string;
  wickDownColor?: string;
  borderUpColor?: string;
  borderDownColor?: string;
  barWidth?: number;

BarSeriesPartialOptions:
  // Partial options for Bar Series
  upColor?: string;
  downColor?: string;
  wickUpColor?: string;
  wickDownColor?: string;
  borderUpColor?: string;
  borderDownColor?: string;
  barWidth?: number;

BaseValueType:
  // Base value type for series
  value: number;

BaselineSeriesOptions:
  // Options for Baseline Series
  topLineColor?: string;
  bottomLineColor?: string;
  topFillColor?: string;
  bottomFillColor?: string;
  base?: number;

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series
  topLineColor?: string;
  bottomLineColor?: string;
  topFillColor?: string;
  bottomFillColor?: string;
  base?: number;

CandlestickSeriesOptions:
  // Options for Candlestick Series
  upColor?: string;
  downColor?: string;
  wickUpColor?: string;
  wickDownColor?: string;
  borderUpColor?: string;
  borderDownColor?: string;
  wickWidth?: number;
  borderWidth?: number;

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series
  upColor?: string;
  downColor?: string;
  wickUpColor?: string;
  wickDownColor?: string;
  borderUpColor?: string;
  borderDownColor?: string;
  wickWidth?: number;
  borderWidth?: number;

Coordinate:
  // Coordinate on the chart
  x: number;
  y: number;

CreatePriceLineOptions:
  // Options for creating a price line
  price: number;
  color?: string;
  lineWidth?: number;
  lineStyle?: number;
  axis?: 'left' | 'right';
  title?: string;
  draggable?: boolean;
  dragAxis?: 'left' | 'right';
  onMove?: (price: number) => void;

DeepPartial<T>:
  // Utility type for deep partial objects
  // Example: DeepPartial<MyObject>

HistogramSeriesOptions:
  // Options for Histogram Series
  color?: string;
  base?: number;

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series
  color?: string;
  base?: number;

HorzAlign:
  // Horizontal alignment
  left | center | right;

LineSeriesOptions:
  // Options for Line Series
  color?: string;
  lineWidth?: number;
  lineStyle?: number;
  crosshairMarkerVisible?: boolean;
  crosshairMarkerRadius?: number;
  crosshairMarkerBorderColor?: string;
  crosshairMarkerBackgroundColor?: string;

LineSeriesPartialOptions:
  // Partial options for Line Series
  color?: string;
  lineWidth?: number;
  lineStyle?: number;
  crosshairMarkerVisible?: boolean;
  crosshairMarkerRadius?: number;
  crosshairMarkerBorderColor?: string;
  crosshairMarkerBackgroundColor?: string;

LineWidth:
  // Line width in pixels
  number;

Logical:
  // Logical index for data points
  number;

LogicalRange:
  // Range of logical indices
  from: Logical;
  to: Logical;

LogicalRangeChangeEventHandler:
  // Handler for logical range changes
  (newRange: LogicalRange | null) => void;

MouseEventHandler:
  // Handler for mouse events
  (event: MouseEvent) => void;

Nominal:
  // Nominal value type
  value: number;

```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: A map that defines the data item types for different series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/PriceLineOptions

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

A map that defines the data item types for different series types.

Properties:
  - Line: TimeData
    Data item type for Line series.
  - Bar: BarData
    Data item type for Bar series.
  - Candlestick: CandlestickData
    Data item type for Candlestick series.
```

----------------------------------------

TITLE: CustomSeriesOptions Type Alias
DESCRIPTION: Defines the base options for any custom series type in Lightweight Charts. This serves as a foundation for creating unique series visualizations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CustomSeriesOptions:
  // Base options applicable to all series types
  priceFormat?: PriceFormat;
  base?: BaseValueType;
  autoscaleInfoProvider?: AutoscaleInfoProvider;
  visible?: boolean;
  title?: string;
  overlay?: boolean;
  priceLineSource?: SeriesPriceLineSource;
  priceLineVisible?: boolean;
  baseLineVisible?: boolean;
  // Specific options for the custom series would extend this type
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section lists and describes various type aliases used within the Lightweight Charts library. These types define the structure and constraints for chart options, data points, event handlers, and internal representations, facilitating precise control over chart elements and behavior.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
GreenComponent:
  Represents a component that is colored green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series, allowing for incremental updates.

HorzAlign:
  Defines the horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj:
  A converter function to transform horizontal scale items into an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

IImageWatermarkPluginApi:
  Interface for a plugin that adds image watermarks to the chart.

IPanePrimitive:
  Interface for a primitive object that can be rendered within a chart pane.

ISeriesPrimitive:
  Interface for a primitive object associated with a chart series.

ITextWatermarkPluginApi:
  Interface for a plugin that adds text watermarks to the chart.

InternalHorzScaleItem:
  The internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  The key used to identify an internal horizontal scale item.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series, allowing for incremental updates.

LineWidth:
  Defines the possible values for a line width.

Logical:
  Represents a logical index or position within the chart's data.

LogicalRange:
  Defines a range based on logical indices.

LogicalRangeChangeEventHandler:
  An event handler function that is called when the logical range of the chart changes.

MouseEventHandler:
  A handler function for mouse events on the chart.

Mutable:
  A type indicating that a value can be modified.

Nominal:
  A type representing a nominal value, often used for identifiers or categories.

OverlayPriceScaleOptions:
  Options for configuring an overlay price scale.

PercentageFormatterFn:
  A function that formats a number as a percentage string.

PriceFormat:
  Defines the format for displaying price values.

PriceFormatterFn:
  A function that formats a price value into a string.

PriceToCoordinateConverter:
  A function that converts a price value to a pixel coordinate.

PrimitiveHasApplyOptions:
  A type indicating that a primitive object has an `applyOptions` method.

PrimitivePaneViewZOrder:
  Defines the z-order for primitive objects within a pane view.

RedComponent:
  Represents a component that is colored red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker to be displayed on a chart series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.

SeriesOptions:
  Base options for all series types.

SeriesPartialOptions:
  Partial options for series, allowing for incremental updates.

SeriesType:
  Defines the type of a chart series (e.g., 'Line', 'Area', 'Histogram').

SizeChangeEventHandler:
  An event handler function that is called when the chart size changes.

TickMarkFormatter:
  A function that formats tick marks on the price scale.

TickMarkWeightValue:
  Defines the weight or importance of a tick mark.

Time:
  Represents a point in time, typically used for chart data.

TimeFormatterFn:
  A function that formats a time value into a string.

TimePointIndex:
  An index representing a specific point in time within the chart's data.
```

----------------------------------------

TITLE: AutoScaleMargins Interface - 'above' Property
DESCRIPTION: The 'above' property defines the top margin in pixels for the AutoScaleMargins interface. This is part of the API reference for Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  above: number
    The number of pixels for top margin.
```

----------------------------------------

TITLE: Lightweight Charts 3.8 API Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 3.8, including formatters, marker positions, series types, and time-related types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/LineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
PriceFormatterFn: Function to format price values.
SeriesMarkerPosition: Enum for the position of series markers.
SeriesMarkerShape: Enum for the shape of series markers.
SeriesOptions: Base options for all series types.
SeriesPartialOptions: Partial options for series updates.
SeriesType: Enum for different series types (e.g., 'Line', 'Bar', 'Area').
SizeChangeEventHandler: Handler for size change events.
TickMarkFormatter: Function to format tick mark labels.
Time: Represents a point in time, can be a Date object or a number.
TimeFormatterFn: Function to format time values.
TimeRange: Represents a range of time.
TimeRangeChangeEventHandler: Handler for time range change events.
UTCTimestamp: Timestamp in UTC.
VertAlign: Enum for vertical alignment.
VisiblePriceScaleOptions: Options for visible price scales.
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used in the Lightweight Charts library. These aliases define the structure and types for chart options, data points, event handlers, and formatting functions, enabling precise control over chart behavior and appearance.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>
  - A utility type that makes all properties of a type T optional and recursively applies to nested objects.

HistogramSeriesOptions
  - Defines the options for a histogram series.

HistogramSeriesPartialOptions
  - A partial version of HistogramSeriesOptions, allowing for partial updates.

HorzAlign
  - Represents the horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj<HorzScaleItem>
  - A type for a converter function that transforms HorzScaleItem to an internal object.

ISeriesPrimitive<HorzScaleItem>
  - Interface for primitive series elements that can be rendered on the chart.

InternalHorzScaleItem
  - Represents an internal data structure for horizontal scale items.

InternalHorzScaleItemKey
  - The key type for internal horizontal scale items.

LineSeriesOptions
  - Defines the options for a line series.

LineSeriesPartialOptions
  - A partial version of LineSeriesOptions, allowing for partial updates.

LineWidth
  - Represents the possible values for the width of a line series.

Logical
  - Represents a logical index, often used for time points.

LogicalRange
  - Defines a range based on logical indices.

LogicalRangeChangeEventHandler()
  - Type for an event handler that is called when the logical range changes.

MouseEventHandler<HorzScaleItem>
  - Type for a generic mouse event handler.

Mutable<T>
  - A utility type that makes all properties of a type T mutable.

Nominal<T, Name>
  - A utility type for creating nominal types, ensuring type safety.

OverlayPriceScaleOptions
  - Defines options for an overlay price scale.

PercentageFormatterFn()
  - Type for a function that formats a percentage value.

PriceFormat
  - Defines the formatting options for price values.

PriceFormatterFn()
  - Type for a function that formats a price value.

PriceToCoordinateConverter()
  - Type for a function that converts a price value to a chart coordinate.

SeriesMarkerPosition
  - Defines the possible positions for series markers.

SeriesMarkerShape
  - Defines the possible shapes for series markers.

SeriesOptions<T>
  - Generic type for series options, where T is the type of data points.

SeriesPartialOptions<T>
  - Generic partial type for series options.

SeriesPrimitivePaneViewZOrder
  - Defines the z-order for series primitive pane views.

SeriesType
  - Represents the type of a series (e.g., line, bar, histogram).

SizeChangeEventHandler()
  - Type for an event handler that is called when the chart size changes.

TickMarkFormatter()
  - Type for a function that formats tick marks on the price scale.

TickMarkWeightValue
  - Represents the weight or significance of a tick mark.

Time
  - Represents a time value, typically used for data points.

TimeFormatterFn<HorzScaleItem>
  - Type for a function that formats time values.

TimePointIndex
  - Represents the index of a time point.

TimeRangeChangeEventHandler<HorzScaleItem>
  - Type for an event handler that is called when the time range changes.

UTCTimestamp
  - Represents a timestamp in UTC format.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesType

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: SeriesMarkerPrice Properties
DESCRIPTION: Defines the properties for a price-based marker in Lightweight Charts. This includes essential properties like time, shape, and color, as well as optional properties such as id, text, and size. The 'position' property overrides the base class to specify price-based positioning.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesMarkerPrice

LANGUAGE: APIDOC
CODE:
```
SeriesMarkerPrice:
  Properties:
    time: TimeType - The time of the marker.
    shape: SeriesMarkerShape - The shape of the marker.
    color: string - The color of the marker.
    id?: string - The optional ID of the marker.
    text?: string - The optional text of the marker.
    size?: number - The optional size of the marker. Defaults to 1.
    position: SeriesMarkerPricePosition - The position of the marker (overrides SeriesMarkerBase.position).
```

----------------------------------------

TITLE: Lightweight Charts v3.4.0 Release Notes
DESCRIPTION: Details the changes in version 3.4.0 of Lightweight Charts. This release introduces an option to fix the right edge, removes restrictions on min bar spacing, and rounds corners of line-style plots. It also includes several bug fixes related to candlestick colors, data clearing, and visible range handling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/release-notes

LANGUAGE: javascript
CODE:
```
/**
 * Lightweight Charts v3.4.0 Release Notes
 *
 * - Enhancements:
 *   - Add option to fix right edge (#218)
 *   - Drop restriction for min bar spacing value (#558)
 *   - Round corners of the line-style plots (#731)
 *
 * - Fixed:
 *   - AutoscaleProvider documentation error (#773)
 *   - Candlestick upColor and downColor is not changed on applyOptions (#750)
 *   - Cleared and reset data appears at visually different location (#757)
 *   - Remove unused internal method from SeriesApi (#768)
 *   - Removing data for the last series doesn't actually remove the data (#752)
 *   - `to` date of getVisibleRange contains partially visible data item and it's impossible to hover it (#624)
 *   - series.priceFormatter().format(price) does not work (#790)
 */
```

----------------------------------------

TITLE: BaseValueType Documentation
DESCRIPTION: Documentation for the BaseValueType alias in Lightweight Charts Next. It represents a type of base value for baseline series types and links to the BaseValuePrice interface.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
Type alias: BaseValueType
> **BaseValueType** : [`BaseValuePrice`](https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/BaseValuePrice)
Represents a type of a base value of baseline series type.
```

----------------------------------------

TITLE: Interface: SeriesOptionsMap
DESCRIPTION: A map that defines options for different series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BaseValuePrice

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
  
  A map defining options for different series types.
```

----------------------------------------

TITLE: OhlcData Interface Properties
DESCRIPTION: Defines the properties of the OhlcData interface, including open, high, low, and close prices, as well as optional custom values.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/BarData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  Properties:
    open?: number
      The opening price of the bar.
    high?: number
      The highest price of the bar.
    low?: number
      The lowest price of the bar.
    close?: number
      The closing price of the bar.
    customValues?: Record<string, unknown>
      Optional custom values that can be used by plugins and are ignored by the library.
```

----------------------------------------

TITLE: Data Changed Scope
DESCRIPTION: Provides context about a data change event, including the type of change and the affected data range.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UpDownMarkersSupportedSeriesTypes

LANGUAGE: APIDOC
CODE:
```
DataChangedScope:
  type DataChangedScope = {
    // Properties describing the data change
    // e.g., type: 'add' | 'remove' | 'update'
    //       from: Time | null
    //       to: Time | null
  }
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ITextWatermarkPluginApi

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: Base Value Type
DESCRIPTION: Defines the base type for values used in the chart, typically representing numerical data points.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
BaseValueType:
  // Represents a numerical value on the chart
  // Can be a number or a string that can be parsed into a number.
  // Example:
  // 100
  // "150.5"
```

----------------------------------------

TITLE: CandlestickData Interface Properties
DESCRIPTION: Defines the properties for CandlestickData, which extends OhlcData. Includes time, open, high, low, close prices, and optional color, borderColor, wickColor, and customValues.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  Inherits from: OhlcData
  Properties:
    color?: string
      Optional color for the candlestick.
    borderColor?: string
      Optional border color for the candlestick.
    wickColor?: string
      Optional color for the candlestick wick.
    time: Time
      The timestamp of the data point.
    open: number
      The opening price.
    high: number
      The highest price.
    low: number
      The lowest price.
    close: number
      The closing price.
    customValues?: any
      Optional custom values associated with the data point.
```

----------------------------------------

TITLE: HandleScaleOptions Interface
DESCRIPTION: Options for handling chart scaling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
HandleScaleOptions:
  axisPressedMouseMove: AxisPressedMouseMoveOptions
    Options for axis scaling when the mouse is pressed and moved.
  pinchScale: boolean
    Enable or disable pinch-to-scale functionality.
```

----------------------------------------

TITLE: SeriesOptionsCommon Interface Documentation
DESCRIPTION: Documentation for SeriesOptionsCommon, containing common options applicable to all series types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon

Common options for all series types.

Properties:

- title:
  > **title** : string
  The title of the series.

- visible:
  > **visible** : boolean
  Whether the series is visible.

- priceScaleId:
  > **priceScaleId** : string | undefined
  The ID of the price scale to use.
```

----------------------------------------

TITLE: HistogramData Interface
DESCRIPTION: Defines the structure for histogram data, including value and time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
HistogramData:
  time: Time | BusinessDay
    The time of the data point.
  value: number
    The value of the data point.
```

----------------------------------------

TITLE: Series Type Options
DESCRIPTION: Defines the options for different series types like Area, Bar, Candlestick, and Baseline. Includes both full and partial option types for customization.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: AreaSeriesOptions
Type alias: AreaSeriesPartialOptions
Type alias: BarSeriesOptions
Type alias: BarSeriesPartialOptions
Type alias: BaselineSeriesOptions
Type alias: BaselineSeriesPartialOptions
Type alias: CandlestickSeriesOptions
Type alias: CandlestickSeriesPartialOptions
Type alias: CustomSeriesOptions
Type alias: CustomSeriesPartialOptions
```

----------------------------------------

TITLE: Interface: TimeScaleOptions
DESCRIPTION: Configuration options for the chart's time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BaseValuePrice

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
  
  Configuration options for the time scale.
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: Background and Color Types
DESCRIPTION: Defines types related to background colors and general color properties used in chart elements.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Background:
  color?: string

Color:
  string
```

----------------------------------------

TITLE: Data Changed Handler
DESCRIPTION: A callback function that is invoked when data in a series has changed, allowing for custom updates or reactions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
DataChangedHandler:
  (scope: DataChangedScope) => void
```

----------------------------------------

TITLE: CandlestickSeriesPartialOptions Type Alias
DESCRIPTION: A partial version of CandlestickSeriesOptions, allowing for optional configuration of Candlestick Series properties. Useful for updating specific chart options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DeepPartial

LANGUAGE: typescript
CODE:
```
type CandlestickSeriesPartialOptions = DeepPartial<CandlestickSeriesOptions>;
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for a single data item in a candlestick series. It extends OhlcData and includes optional properties for color, border color, and wick color, allowing for per-item styling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>
  Structure describing a single item of data for candlestick series
  Extends:
    OhlcData<HorzScaleItem>
  Type parameters:
    HorzScaleItem = Time
  Properties:
    color? : string
      Optional color value for certain data item. If missed, color from options is used
    borderColor? : string
      Optional border color value for certain data item. If missed, color from options is used
    wickColor? : string
      Optional wick color value for certain data item. If missed, color from options is used
```

----------------------------------------

TITLE: SeriesOptionsCommon Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsCommon interface, providing common options for all series types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon

Common options for all series types.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Common Type Aliases
DESCRIPTION: Provides definitions for common types used across various series options in Lightweight Charts, including partial options, coordinate types, and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaselineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  Partial<T>

Coordinate:
  number

LogicalRangeChangeEventHandler:
  (newRange: LogicalRange | null) => void

MouseEventHandler:
  (event: MouseEvent) => void

AutoscaleInfoProvider:
  {
    lastValueProvider: () => number | undefined
  }

Background:
  {
    type: 'solid' | 'gradient'
    color: Color
  }

BarPrice:
  number

BaseValueType:
  number

HorzAlign:
  'left' | 'right' | 'center'

LineStyle:
  0 | 1 | 2 | 3

LineType:
  0 | 1

LineWidth:
  number

Logical:
  number

Nominal:
  number

OverlayPriceScaleOptions:
  {
    autoScale?: boolean
    mode?: number
    invertScale?: boolean
    position?: 'left' | 'right'
    scaleMargins?: VerticalMargin
    priceLineVisible?: boolean
    borderVisible?: boolean
    borderColor?: Color
  }
```

----------------------------------------

TITLE: Lightweight Charts Formatting and Alignment
DESCRIPTION: Provides type definitions for horizontal alignment, price formatting functions, and percentage formatting functions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  // Enum or type for horizontal alignment (e.g., 'left', 'center', 'right')

PriceFormat:
  // Structure defining how prices are formatted (e.g., decimals, currency symbol)

PriceFormatterFn:
  // Type for a function that formats a price value into a string
  // (priceValue: number) => string

PercentageFormatterFn:
  // Type for a function that formats a percentage value into a string
  // (percentageValue: number) => string
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases
DESCRIPTION: This section lists various type aliases available in the 'Next' version of Lightweight Charts, including formatting functions, time-related types, and series types. These are crucial for defining data structures and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PriceFormat

LANGUAGE: APIDOC
CODE:
```
TickMarkWeightValue
TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn
Time
TimeFormatterFn
TimePointIndex
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
PriceFormat: PriceFormatBuiltIn | PriceFormatCustom
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Options for styling histogram series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color?: string
  base?: number
  invert?: boolean
```

----------------------------------------

TITLE: TimeMark Interface Documentation
DESCRIPTION: Documentation for the TimeMark interface, which represents a tick mark on the horizontal (time) scale. It includes details about its properties, such as needAlignCoordinate.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeMark

LANGUAGE: APIDOC
CODE:
```
Interface: TimeMark

Represents a tick mark on the horizontal (time) scale.

Properties:

needAlignCoordinate:
> **needAlignCoordinate** : `boolean`
Does time mark need to be aligned
```

----------------------------------------

TITLE: Data Handling Types
DESCRIPTION: Defines types related to data handling and changes within the chart, including data item structures and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: DataChangedHandler
  Signature: (scope: DataChangedScope) => void
  Description: Handler function called when data in the chart has changed.

Type alias: DataChangedScope
  Properties:
    newPrices?: boolean
    newTimestamps?: boolean
    newSeries?: boolean
    newCrosshair?: boolean
    newPriceScale?: boolean
    newLayout?: boolean
    newMargins?: boolean
    newScaleMargins?: boolean
    newVisibleRange?: boolean
    newLeftPriceScale?: boolean
    newRightPriceScale?: boolean

Type alias: DataItem<HorzScaleItem>
  Properties:
    time: HorzScaleItem
    value: number
    color?: string
```

----------------------------------------

TITLE: Interface: IRange<T>
DESCRIPTION: Represents a generic range with 'from' and 'to' values. This interface is parameterized by type T.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IRange

LANGUAGE: APIDOC
CODE:
```
Interface: IRange<T>
  Type parameters:
    • T
  Properties:
    from: T
    to: T
```

----------------------------------------

TITLE: BaselineStyleOptions Interface
DESCRIPTION: Options for styling a baseline series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
BaselineStyleOptions:
  topLineColor?: string
    The color of the top line of the baseline.
  bottomLineColor?: string
    The color of the bottom line of the baseline.
  topFillColor?: string
    The color of the top fill of the baseline.
  bottomFillColor?: string
    The color of the bottom fill of the baseline.
  base?: number
    The base value for the baseline.
```

----------------------------------------

TITLE: SeriesOptionsCommon Interface
DESCRIPTION: Common options applicable to all series types, including visibility, title, and price scale assignment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon
Common options for all series types
Properties:
  title?: 
    optional title : string
    The title of the series.
  visible?: 
    optional visible : boolean
    Whether the series is visible.
  priceScaleId?: 
    optional priceScaleId : string
    The ID of the price scale to which the series belongs.
```

----------------------------------------

TITLE: Time Scale Conversion and Dimension APIs
DESCRIPTION: Provides methods to convert between time and coordinate systems, and to retrieve the dimensions of the time scale. These are essential for custom chart interactions and data visualization.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ITimeScaleApi

LANGUAGE: APIDOC
CODE:
```
timeToCoordinate(time: HorzScaleItem): Coordinate | null
  Converts a time to local x coordinate.
  Parameters:
    time: Time needs to be converted
  Returns:
    X coordinate of that time or null if no time found on time scale.

coordinateToTime(x: number): HorzScaleItem | null
  Converts a coordinate to time.
  Parameters:
    x: Coordinate needs to be converted.
  Returns:
    Time of a bar that is located on that coordinate or null if there are no bars found on that coordinate.

width(): number
  Returns a width of the time scale.
  Returns:
    The width of the time scale.

height(): number
  Returns a height of the time scale.
  Returns:
    The height of the time scale.
```

----------------------------------------

TITLE: Lightweight Charts API Reference
DESCRIPTION: This section details the methods available on the IYieldCurveChartApi interface for managing charts and series. It includes methods for adding, removing, and updating series, handling pane management, and subscribing to user interactions like clicks and crosshair movements.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IYieldCurveChartApi

LANGUAGE: APIDOC
CODE:
```
IYieldCurveChartApi:
  remove(): void
    Removes the chart from the DOM.

  resize(): void
    Resizes the chart to fit its container.

  addCustomSeries<T extends SeriesType>(
    customSeriesType: T,
    options?: SeriesPartialOptionsMap[T]
  ): ISeriesApi<T, number, WhitespaceData<number> | LineData<number>, SeriesOptionsMap[T], SeriesPartialOptionsMap[T]>
    Adds a custom series to the chart.
    Parameters:
      customSeriesType: The type of the custom series.
      options: Optional initial options for the custom series.
    Returns: An interface for the added custom series.

  removeSeries(seriesId: SeriesId): boolean
    Removes a series from the chart.
    Parameters:
      seriesId: The ID of the series to remove.
    Returns: True if the series was removed successfully, false otherwise.

  subscribeClick(handler: MouseEventHandler<'click'>): void
    Subscribes to click events on the chart.
    Parameters:
      handler: The function to call when a click event occurs.

  unsubscribeClick(handler: MouseEventHandler<'click'>): void
    Unsubscribes from click events on the chart.
    Parameters:
      handler: The handler function to unsubscribe.

  subscribeDblClick(handler: MouseEventHandler<'dblclick'>): void
    Subscribes to double-click events on the chart.
    Parameters:
      handler: The function to call when a double-click event occurs.

  unsubscribeDblClick(handler: MouseEventHandler<'dblclick'>): void
    Unsubscribes from double-click events on the chart.
    Parameters:
      handler: The handler function to unsubscribe.

  subscribeCrosshairMove(handler: CrosshairMoveHandler): void
    Subscribes to crosshair move events on the chart.
    Parameters:
      handler: The function to call when the crosshair moves.

  unsubscribeCrosshairMove(handler: CrosshairMoveHandler): void
    Unsubscribes from crosshair move events on the chart.
    Parameters:
      handler: The handler function to unsubscribe.

  priceScale(priceScaleId: string): IPriceScaleApi
    Gets the API for a specific price scale.
    Parameters:
      priceScaleId: The ID of the price scale.
    Returns: The price scale API.

  timeScale(): ITimeScaleApi
    Gets the API for the time scale.
    Returns: The time scale API.

  applyOptions(options: DeepPartial<ChartOptions>): void
    Applies new options to the chart.
    Parameters:
      options: The options to apply.

  options(): ChartOptions
    Gets the current options of the chart.
    Returns: The current chart options.

  takeScreenshot(options?: ScreenshotOptions): Promise<string>
    Takes a screenshot of the chart.
    Parameters:
      options: Optional screenshot options.
    Returns: A promise that resolves with the screenshot data URL.

  addPane(options?: PaneOptions): IPaneApi
    Adds a new pane to the chart.
    Parameters:
      options: Optional options for the new pane.
    Returns: The API for the new pane.

  panes(): readonly IPaneApi[]
    Gets all panes of the chart.
    Returns: An array of pane APIs.

  removePane(paneId: string): boolean
    Removes a pane from the chart.
    Parameters:
      paneId: The ID of the pane to remove.
    Returns: True if the pane was removed successfully, false otherwise.

  swapPanes(paneIndex1: number, paneIndex2: number): void
    Swaps two panes on the chart.
    Parameters:
      paneIndex1: The index of the first pane.
      paneIndex2: The index of the second pane.

  autoSizeActive(): boolean
    Checks if auto-sizing is active for the chart.
    Returns: True if auto-sizing is active, false otherwise.

  chartElement(): HTMLCanvasElement | null
    Gets the chart's canvas element.
    Returns: The canvas element or null if not available.

  setCrosshairPosition(x: number, y: number): void
    Sets the position of the crosshair.
    Parameters:
      x: The x-coordinate.
      y: The y-coordinate.

  clearCrosshairPosition(): void
    Clears the crosshair position.

  paneSize(paneId: string): Size | null
    Gets the size of a specific pane.
    Parameters:
      paneId: The ID of the pane.
    Returns: The size of the pane or null if not found.

  horzBehaviour(): HorizontalBehavior
    Gets the horizontal behavior of the chart.
    Returns: The horizontal behavior.

  addSeries<T extends SeriesType>(
    seriesType: T,
    options?: SeriesPartialOptionsMap[T]
  ): ISeriesApi<T, number, WhitespaceData<number> | LineData<number>, SeriesOptionsMap[T], SeriesPartialOptionsMap[T]>
    Adds a series to the chart.
    Parameters:
      seriesType: The type of the series to add.
      options: Optional initial options for the series.
    Returns: An interface for the added series.
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API for defining options and configurations for different chart series types and general chart settings. It covers options for Area, Bar, Baseline, and Candlestick series, as well as chart-wide options and data-related types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for an Area Series
  // Includes properties like topColor, bottomColor, lineColor, etc.

AreaSeriesPartialOptions:
  // Partial options for an Area Series, allowing for incremental updates

AutoscaleInfoProvider():
  // Provider for autoscale information

Background:
  // Type for background color or image settings

BarPrice:
  // Type representing the price of a bar (e.g., open, high, low, close)

BarSeriesOptions:
  // Options for a Bar Series
  // Includes properties like barColor, wickColor, etc.

BarSeriesPartialOptions:
  // Partial options for a Bar Series

BaseValueType:
  // Base type for values used in the chart

BaselineSeriesOptions:
  // Options for a Baseline Series
  // Includes properties for baseline color and visibility

BaselineSeriesPartialOptions:
  // Partial options for a Baseline Series

CandlestickSeriesOptions:
  // Options for a Candlestick Series
  // Includes properties like upColor, downColor, borderVisible, etc.

CandlestickSeriesPartialOptions:
  // Partial options for a Candlestick Series

ChartOptions:
  // General options for the chart itself
  // Includes properties like width, height, layout, timeScale, etc.

Coordinate:
  // Type representing a coordinate on the chart

CreatePriceLineOptions:
  // Options for creating a price line
  // Includes properties like price, color, width, etc.

CustomSeriesOptions:
  // Base options for custom series

CustomSeriesPartialOptions:
  // Partial options for custom series

CustomSeriesPricePlotValues:
  // Values for price plots in custom series

DataChangedHandler():
  // Handler for data changed events

DataChangedScope:
  // Scope of data changes

DataItem<HorzScaleItem>:
  // Represents a data item with horizontal scale information
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for a single data item in a candlestick series. It extends the OhlcData interface, inheriting properties for open, high, low, and close prices, along with time information.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>

Structure describing a single item of data for candlestick series.

Extends:
  * OhlcData<HorzScaleItem>
```

----------------------------------------

TITLE: OhlcData Interface Documentation
DESCRIPTION: Documentation for the OhlcData interface, which represents a financial data bar with time, open, high, low, and close prices. It details the properties and their types, and lists interfaces that extend OhlcData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: OhlcData

Represents a bar with a Time and open, high, low, and close prices.

Extended by:
  * BarData
  * CandlestickData

Properties:

- time:
  > **time** : Time
  The bar time.

- open:
  > **open** : number
  The open price.

- high:
  > **high** : number
  The high price.

- low:
  > **low** : number
  The low price.

- close:
  > **close** : number
  The close price.
```

----------------------------------------

TITLE: BaselineStyleOptions Interface
DESCRIPTION: Options for styling baseline series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
BaselineStyleOptions:
  color?: string
  lineStyle?: LineStyle
  topFillColor1?: string
  topFillColor2?: string
  bottomFillColor1?: string
  bottomFillColor2?: string
```

----------------------------------------

TITLE: SeriesAttachedParameter Interface Documentation
DESCRIPTION: Documentation for the SeriesAttachedParameter interface, which contains references to chart and series instances and a method to request chart updates. This interface is generic and depends on HorzScaleItem and TSeriesType.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesAttachedParameter

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesAttachedParameter<HorzScaleItem, TSeriesType>

Object containing references to the chart and series instances, and a requestUpdate method for triggering a refresh of the chart.

Properties:
  chart: Reference to the chart instance.
  series: Reference to the series instance.
  requestUpdate: Function to request an update of the chart.
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These include definitions for series options (like HistogramSeriesOptions, LineSeriesOptions), formatting functions (PercentageFormatterFn, PriceFormatterFn), event handlers (MouseEventHandler, SizeChangeEventHandler), and internal data structures for scale items and primitives.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
GreenComponent:
  Represents a component that is green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series.

HorzAlign:
  Defines horizontal alignment options.

HorzScaleItemConverterToInternalObj:
  Converter function for horizontal scale items to internal objects.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

IImageWatermarkPluginApi:
  API for image watermark plugins.

IPanePrimitive:
  Interface for primitives within a chart pane.

ISeriesPrimitive:
  Interface for series primitives.

ITextWatermarkPluginApi:
  API for text watermark plugins.

InternalHorzScaleItem:
  Internal representation of a horizontal scale item.

InternalHorzScaleItemKey:
  Key for internal horizontal scale items.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series.

LineWidth:
  Defines the width of a line.

Logical:
  Represents a logical index.

LogicalRange:
  Defines a range of logical indices.

LogicalRangeChangeEventHandler:
  Handler for logical range change events.

MouseEventHandler:
  Handler for mouse events.

Mutable:
  Indicates a mutable type.

Nominal:
  Represents a nominal value.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn:
  Function type for formatting percentages.

PriceFormat:
  Defines the format for prices.

PriceFormatterFn:
  Function type for formatting prices.

PriceToCoordinateConverter:
  Converter function from price to coordinate.

PrimitiveHasApplyOptions:
  Indicates if a primitive has apply options.

PrimitivePaneViewZOrder:
  Z-order for primitive rendering in a pane view.

RedComponent:
  Represents a component that is red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker on a series.

SeriesMarkerBarPosition:
  Position of a marker relative to a bar.

SeriesMarkerPosition:
  General position of a marker.

SeriesMarkerPricePosition:
  Position of a marker relative to a price.

SeriesMarkerShape:
  Shape of a series marker.

SeriesMarkerZOrder:
  Z-order for series markers.

SeriesOptions:
  General options for any series type.

SeriesPartialOptions:
  Partial options for any series type.

SeriesType:
  Defines the type of a series (e.g., 'Line', 'Histogram').

SizeChangeEventHandler:
  Handler for size change events.
```

----------------------------------------

TITLE: Data Validation Improvements
DESCRIPTION: Enhances data validation for OhlcData and SingleValueData with new helper functions. isFulfilledBarData and isFulfilledLineData ensure more accurate data type validation, addressing issues with data fulfillment.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: javascript
CODE:
```
import { isFulfilledBarData } from 'lightweight-charts';
import { isFulfilledLineData } from 'lightweight-charts';

// Example usage:
const ohlcData = { open: 10, high: 20, low: 5, close: 15, time: '2023-01-01' };
if (isFulfilledBarData(ohlcData)) {
  // Process valid OHLC data
}
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These include options for different series types (Area, Bar, Candlestick, Histogram, Line, Baseline), event handlers, and utility types for deep partial application and coordinate systems.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/MouseEventHandler

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  Type alias for Area series options.

AreaSeriesPartialOptions:
  Type alias for partial Area series options.

AutoscaleInfoProvider:
  Interface for providing autoscale information.

Background:
  Type alias for background color or image settings.

BarPrice:
  Type alias for bar price values (open, high, low, close).

BarSeriesOptions:
  Type alias for Bar series options.

BarSeriesPartialOptions:
  Type alias for partial Bar series options.

BaseValueType:
  Type alias for the base value type used in calculations.

BaselineSeriesOptions:
  Type alias for Baseline series options.

BaselineSeriesPartialOptions:
  Type alias for partial Baseline series options.

CandlestickSeriesOptions:
  Type alias for Candlestick series options.

CandlestickSeriesPartialOptions:
  Type alias for partial Candlestick series options.

Coordinate:
  Type alias for a coordinate value (number).

CreatePriceLineOptions:
  Type alias for options when creating a price line.

DeepPartial<T>:
  Utility type to make all properties of a type recursively optional.

HistogramSeriesOptions:
  Type alias for Histogram series options.

HistogramSeriesPartialOptions:
  Type alias for partial Histogram series options.

HorzAlign:
  Type alias for horizontal alignment options (e.g., 'left', 'center', 'right').

LineSeriesOptions:
  Type alias for Line series options.

LineSeriesPartialOptions:
  Type alias for partial Line series options.

LineWidth:
  Type alias for line width values.

Logical:
  Type alias for logical index values.

LogicalRange:
  Type alias for a range defined by logical indices.

LogicalRangeChangeEventHandler:
  Type alias for a function that handles logical range changes.

MouseEventHandler:
  Type alias for a function that handles mouse events.

Nominal:
  Type alias for nominal values.
```

----------------------------------------

TITLE: Histogram Series Partial Options
DESCRIPTION: Defines partial options for a Histogram Series, allowing for incremental updates to existing series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesPartialOptions:
  color?: Color
  base?: number
```

----------------------------------------

TITLE: Nominal Type Alias Examples
DESCRIPTION: Examples demonstrating the usage of the Nominal type alias to create distinct types in TypeScript, ensuring type safety.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/Nominal

LANGUAGE: typescript
CODE:
```
type Index = Nominal<number, 'Index'>;
// let i: Index = 42; // this fails to compile
let i: Index = 42 as Index; // OK
```

LANGUAGE: typescript
CODE:
```
type TagName = Nominal<string, 'TagName'>;
```

----------------------------------------

TITLE: Candlestick Series Options
DESCRIPTION: Defines the options for a Candlestick Series, including visual properties for wick, border, and body colors.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesOptions

Represents the options for a Candlestick Series.

Properties:
  - upColor?: string
    The color of the candlestick body when the price increased.
  - downColor?: string
    The color of the candlestick body when the price decreased.
  - borderUpColor?: string
    The color of the candlestick border when the price increased.
  - borderDownColor?: string
    The color of the candlestick border when the price decreased.
  - wickUpColor?: string
    The color of the candlestick wick when the price increased.
  - wickDownColor?: string
    The color of the candlestick wick when the price decreased.
  - priceLineVisible?: boolean
    Whether the price line is visible for this series.
  - lastValueProvider?: (value: number) => number
    A function to provide the last value for the series.
  - priceFormat?: PriceFormat
    The format for displaying prices.
  - timeScale?: TimeScaleOptions
    Options for the time scale.
  - visible?: boolean
    Whether the series is visible.
```

----------------------------------------

TITLE: Histogram Series Options
DESCRIPTION: Defines the complete options for configuring a histogram series in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  base?: 
    "open" | "close" | "high" | "low"
    The base value for histogram bars. Defaults to "close".
  color?: 
    string
    The color of the histogram bars. Defaults to '#26a69a'.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: Line Series Options
DESCRIPTION: Defines the partial options for configuring a Line series. This includes properties for styling and behavior specific to line charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
LineSeriesOptions:
  priceFormat?: {
    type: 'volume' | 'integer' | 'fixed' | 'decimal',
    precision?: number,
    minMove?: number,
    fractDigits?: number
  }
  baseLineVisible?: boolean
  baseLineColor?: Color
  baseLineStyle?: LineStyle
  baseLineWidth?: LineWidth
  lineStyle?: LineStyle
  lineColor?: Color
  lineWidth?: LineWidth
  crosshairMarkerVisible?: boolean
  crosshairMarkerColor?: Color
  crosshairMarkerRadius?: number

LineSeriesPartialOptions:
  priceFormat?: {
    type: 'volume' | 'integer' | 'fixed' | 'decimal',
    precision?: number,
    minMove?: number,
    fractDigits?: number
  }
  baseLineVisible?: boolean
  baseLineColor?: Color
  baseLineStyle?: LineStyle
  baseLineWidth?: LineWidth
  lineStyle?: LineStyle
  lineColor?: Color
  lineWidth?: LineWidth
  crosshairMarkerVisible?: boolean
  crosshairMarkerColor?: Color
  crosshairMarkerRadius?: number
```

----------------------------------------

TITLE: Watermark Feature Changes in v5
DESCRIPTION: Details the changes to the watermark feature in Lightweight Charts v5, including its extraction from the core library and re-implementation as a Pane Primitive.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5

LANGUAGE: APIDOC
CODE:
```
Watermark Feature Changes:
- Extraction from Core: Watermark functionality moved out of the core library.
- Re-implementation: Now a Pane Primitive (plugin) within the library.
- Improved Tree-shaking: Reduces bundle sizes for users not needing watermarks.
- New Image Watermark Primitive: Added `createImageWatermark` for image-based watermarks.
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ChartOptions

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: CandlestickStyleOptions Interface
DESCRIPTION: Options for styling a candlestick series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickStyleOptions:
  color?: string
    The color of the bullish candlesticks.
  downColor?: string
    The color of the bearish candlesticks.
  borderVisible?: boolean
    Whether to show the candlestick borders.
  borderColor?: string
    The color of the candlestick borders.
  wickVisible?: boolean
    Whether to show the candlestick wicks.
  wickColor?: string
    The color of the candlestick wicks.
  bar уеныVisible?: boolean
    Whether to show the bar part of the candlestick.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Interface
DESCRIPTION: Base interface for series primitives in Lightweight Charts. It must be implemented to add external graphics to series. This interface includes methods for updating views and retrieving price axis labels.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveBase<TSeriesAttachedParameters>
  Type parameters:
    • TSeriesAttachedParameters = unknown
  Methods:
    updateAllViews()?
      optional updateAllViews(): void
      This method is called when viewport has been changed, so primitive have to recalculate / invalidate its data
      Returns: void
    priceAxisViews()?
      optional priceAxisViews(): readonly ISeriesPrimitiveAxisView[]
      Returns array of labels to be drawn on the price axis used by the series
```

LANGUAGE: typescript
CODE:
```
interface ISeriesPrimitiveBase<TSeriesAttachedParameters = unknown> {
  updateAllViews?(): void;
  priceAxisViews?(): readonly ISeriesPrimitiveAxisView[];
}
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Defines the options for the time scale of Lightweight Charts. This includes properties like rightOffset and barSpacing, which control the margins and spacing of the chart's horizontal axis.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  rightOffset: number
    The margin space in bars from the right side of the chart.
    Default Value: 0
  barSpacing: number
    The space between bars in pixels.
    Default Value: 6
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Options for configuring the time scale of the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Options for the time scale.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Options for configuring the time scale in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
  Options for the time scale.
```

----------------------------------------

TITLE: OhlcData Properties
DESCRIPTION: Defines the properties for OHLC (Open, High, Low, Close) data points used in Lightweight Charts. Includes the high, low, and close prices, which are numerical values representing the respective price points for a given time interval.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
OhlcData:
  high: number
    The high price.
  low: number
    The low price.
  close: number
    The close price.
```

----------------------------------------

TITLE: TimeScaleOptions Interface Documentation
DESCRIPTION: Documentation for TimeScaleOptions, used to configure the behavior and appearance of the time scale on the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Defines options for the time scale.

Properties:

- timeVisible:
  > **timeVisible** : boolean
  Whether the time axis labels are visible.

- secondsVisible:
  > **secondsVisible** : boolean
  Whether seconds are visible in the time axis labels.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Plugin API Types
DESCRIPTION: Defines types for primitives, plugin APIs, and related components within the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  API for the image watermark plugin.

IPanePrimitive:
  Represents a primitive within a chart pane.

ISeriesPrimitive:
  Represents a primitive associated with a series.

ITextWatermarkPluginApi:
  API for the text watermark plugin.

PrimitiveHasApplyOptions:
  A type indicating that a primitive has applyOptions functionality.

PrimitivePaneViewZOrder:
  Defines the Z-order for primitives within a pane view.

RedComponent:
  Represents a red component, likely for color definitions.
```

----------------------------------------

TITLE: Series Markers Migration: v4 vs v5
DESCRIPTION: Compares the methods for managing series markers in Lightweight Charts v4 and v5. V5 introduces a separate primitive for markers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/migrations/from-v4-to-v5

LANGUAGE: APIDOC
CODE:
```
v4:
// Markers were directly managed through the series instance
series.setMarkers([
  {
    time: '2019-04-09',
    position: 'aboveBar',
    color: 'black',
    shape: 'arrowDown',
  },
]);

// Getting markers
const markers = series.markers();

v5:
// Import the markers primitive
import { createSeriesMarkers } from 'lightweight-charts';

// Create a markers primitive instance
const seriesMarkers = createSeriesMarkers(series, [
  {
    time: '2019-04-09',
    position: 'aboveBar',
    color: 'black',
    shape: 'arrowDown',
  },
]);

// Getting markers
const markers = seriesMarkers.markers();

// Updating markers
seriesMarkers.setMarkers([/* new markers */]);

// Remove all markers
seriesMarkers.setMarkers([]);

```

----------------------------------------

TITLE: Horizontal Scale Item Converter
DESCRIPTION: Defines the structure for converting horizontal scale items to internal objects.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
HorzScaleItemConverterToInternalObj:
  // Interface for converting horizontal scale items.
  // Typically used for custom time scale formatting.
```

----------------------------------------

TITLE: Series Options - Line
DESCRIPTION: Defines partial options for the Line series type. It extends common series options and line style options, allowing for deep partial updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Line:
  DeepPartial<LineStyleOptions & SeriesOptionsCommon>
  The type of line series partial options.
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Defines the options for handling double-click events on chart axes in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CrosshairLineOptions

LANGUAGE: APIDOC
CODE:
```
Interface: AxisDoubleClickOptions
  enable?: boolean
    Enables or disables the double-click action on the axis. Defaults to true.
```

----------------------------------------

TITLE: AutoScaleMargins Interface
DESCRIPTION: Defines the options for auto-scaling margins on the price scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  top?: number
    The top margin for auto-scaling. Defaults to 0.
  bottom?: number
    The bottom margin for auto-scaling. Defaults to 0.
```

----------------------------------------

TITLE: Chart API Types
DESCRIPTION: Provides type definitions for various chart-related functionalities, including price lines, data types, and event handlers.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CreatePriceLineOptions:
  price: number
  color?: string
  lineWidth?: LineWidth
  lineStyle?: LineStyle
  axisLabelVisible?: boolean
  title?: string
  draggable?: boolean
  onMoveEnd?: (newPrice: number) => void

LineWidth:
  // Represents the width of a line
  // Example: 1 | 2 | 3

LineStyle:
  // Represents the style of a line
  // Example: 0 (Solid), 1 (Dotted), 2 (Dashed)

BarPrice:
  // Represents the price of a bar
  // Example: open: number, high: number, low: number, close: number

Coordinate:
  // Represents a coordinate on the chart
  // Example: number

MouseEventHandler:
  // Handler for mouse events
  // Example: (event: MouseEvent) => void

LogicalRangeChangeEventHandler:
  // Handler for logical range changes
  // Example: (newRange: LogicalRange) => void

LogicalRange:
  from: number
  to: number

AutoscaleInfoProvider:
  // Provides information for autoscaling
  // Example: getAutoscaleInfo: () => AutoscaleInfo

AutoscaleInfo:
  // Information for autoscaling
  // Example: priceRange: { min: number, max: number }

Background:
  // Background color or image settings
  // Example: color?: string;

BaseValueType:
  // Base value type for series
  // Example: 'number' | 'datetime'

HorzAlign:
  // Horizontal alignment options
  // Example: 'left' | 'center' | 'right'

Nominal:
  // Represents a nominal value
  // Example: number

Logical:
  // Represents a logical value
  // Example: number

DeepPartial<T>:
  // Utility type for creating deep partial objects
  // Example: DeepPartial<AreaSeriesOptions>
```

----------------------------------------

TITLE: Lightweight Charts Next API Interfaces
DESCRIPTION: Lists available interfaces for the next version of Lightweight Charts, providing links to detailed documentation for each.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScalePoint

LANGUAGE: APIDOC
CODE:
```
PriceLineOptions
PriceRange
PriceScaleMargins
PriceScaleOptions
PrimitiveHoveredItem
SeriesAttachedParameter
SeriesDataItemTypeMap
SeriesDefinition
SeriesMarkerBar
SeriesMarkerBase
SeriesMarkerPrice
SeriesMarkersOptions
SeriesOptionsCommon
SeriesOptionsMap
SeriesPartialOptionsMap
SeriesStyleOptionsMap
SeriesUpDownMarker
SingleValueData
SolidColor
TextWatermarkLineOptions
TextWatermarkOptions
TickMark
TimeChartOptions
TimeMark
TimeScaleOptions
TimeScalePoint
TouchMouseEventData
TrackingModeOptions
UpDownMarkersPluginOptions
VerticalGradientColor
WhitespaceData
YieldCurveChartOptions
YieldCurveOptions
```

----------------------------------------

TITLE: Supported Series Types and Alignment
DESCRIPTION: Documentation for type aliases related to supported series types and vertical alignment within Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/PriceFormat

LANGUAGE: APIDOC
CODE:
```
Type alias: UpDownMarkersSupportedSeriesTypes

Represents the series types that support up and down markers.
```

LANGUAGE: APIDOC
CODE:
```
Type alias: VertAlign

Represents the vertical alignment options for chart elements.
```

LANGUAGE: APIDOC
CODE:
```
Type alias: VisiblePriceScaleOptions

Defines options for the visible price scale.
```

LANGUAGE: APIDOC
CODE:
```
Type alias: YieldCurveSeriesType

Represents the series type for yield curve data.
```

----------------------------------------

TITLE: TimeScalePoint Interface Documentation
DESCRIPTION: Documentation for the TimeScalePoint interface, representing points on the time scale in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint

Represents points on the time scale.
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for SeriesOptionsMap, a utility type that maps series types to their specific options interfaces.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap

Maps series types to their options interfaces.

Properties:

- Area:
  > **Area** : AreaSeriesOptions

- Line:
  > **Line** : LineSeriesOptions

- Candlestick:
  > **Candlestick** : CandlestickSeriesOptions

- Bar:
  > **Bar** : BarSeriesOptions

- Histogram:
  > **Histogram** : HistogramSeriesOptions
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Types
DESCRIPTION: Defines types related to time representation, logical ranges, and event handlers for time and logical range changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Time:
  Represents a point in time.

TimeFormatterFn:
  A function type for formatting time values.

TimePointIndex:
  An index representing a point in time.

LogicalRange:
  Represents a range of logical values.

LogicalRangeChangeEventHandler:
  An event handler for logical range changes.

TimeRangeChangeEventHandler:
  An event handler for time range changes.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ISeriesPrimitive

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the structure for partial options of various chart series types, including Candlestick, Area, Baseline, Line, and Histogram. These types extend common series options and are based on DeepPartial for flexible configuration.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Candlestick:
  Type: DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
  Description: The type of candlestick series partial options.

Area:
  Type: DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
  Description: The type of area series partial options.

Baseline:
  Type: DeepPartial<BaselineStyleOptions & SeriesOptionsCommon>
  Description: The type of baseline series partial options.

Line:
  Type: DeepPartial<LineStyleOptions & SeriesOptionsCommon>
  Description: The type of line series partial options.

Histogram:
  Type: DeepPartial<HistogramStyleOptions & SeriesOptionsCommon>
  Description: The type of histogram series partial options.

Properties:
  - Bar
  - Candlestick
  - Area
  - Baseline
  - Line
  - Histogram
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Defines the style options for a histogram series in Lightweight Charts. It includes properties for column color and the base level of histogram columns.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: HistogramStyleOptions

Represents style options for a histogram series.

Properties:
  color: string
    Column color.
    Default Value: '#26a69a'
  base: number
    Initial level of histogram columns.
    Default Value: 0
```

----------------------------------------

TITLE: Supported Series Types and Alignment
DESCRIPTION: Lists supported series types for up/down markers and vertical alignment options for chart elements.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BarPrice

LANGUAGE: APIDOC
CODE:
```
Type Aliases:

UpDownMarkersSupportedSeriesTypes
VertAlign
```

----------------------------------------

TITLE: TimeChartOptions Interface Documentation
DESCRIPTION: Documentation for the TimeChartOptions interface, defining options for time-based charts in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/Point

LANGUAGE: APIDOC
CODE:
```
Interface: TimeChartOptions

Options for time-based charts.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial configuration options for Candlestick Series, allowing for incremental updates to existing settings.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/YieldCurveSeriesType

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: string
  downColor?: string
  borderVisible?: boolean
  borderColor?: string
  wickVisible?: boolean
  wickColor?: string
  barSpacing?: number
  crosshairMarkerVisible?: boolean
  priceLineVisible?: boolean
  priceLineSource?: 'open' | 'close' | 'high' | 'low'
  priceLineLabelVisible?: boolean
  autoscaleInfoProvider?: AutoscaleInfoProvider
  visible?: boolean
  title?: string
  lastValueProvider?: (data: SeriesItem, visibleRange: Range | null) => number | null
  priceFormat?: PriceFormat
  
  // Other common series options...
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DataChangedHandler

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: IPanePrimitiveWrapper Interface Documentation
DESCRIPTION: Documentation for the IPanePrimitiveWrapper interface, which serves as a base for pane primitives in Lightweight Charts. It includes type parameters and properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/IPanePrimitiveWrapper

LANGUAGE: APIDOC
CODE:
```
Interface: IPanePrimitiveWrapper<T, Options>

Interface for a pane primitive.

Type parameters:
• T
• Options

Properties:
(No specific properties listed in the provided text, but this section would typically detail the properties of the interface.)
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Defines the style options for a histogram series in Lightweight Charts. It includes properties for column color and the base level of histogram columns.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color: string
    Column color.
    Default Value: '#26a69a'
  base: number
    Initial level of histogram columns.
```

----------------------------------------

TITLE: Series Options - Histogram
DESCRIPTION: Defines partial options for the Histogram series type. It extends common series options and histogram style options, enabling granular configuration.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Histogram:
  DeepPartial<HistogramStyleOptions & SeriesOptionsCommon>
  The type of histogram series partial options.
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: Defines various options and types for different series types like Area, Bar, Candlestick, Histogram, and Line. Includes partial options for updating specific properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/LogicalRangeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

LineSeriesOptions:
  // Options for Line Series

LineSeriesPartialOptions:
  // Partial options for Line Series
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: WhitespaceData Interface Properties
DESCRIPTION: Details the properties of the WhitespaceData interface in Lightweight Charts API version 4.2. Specifically, it describes the 'time' property.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/WhitespaceData

LANGUAGE: APIDOC
CODE:
```
Interface: WhitespaceData<HorzScaleItem>
  Properties:
    time:
      type: HorzScaleItem (defaults to Time)
      description: The time of the data.
```

----------------------------------------

TITLE: Lightweight Charts v1.1.0 - Bug Fixes
DESCRIPTION: Version 1.1.0 addresses a number of bugs in the Lightweight Charts library. Fixes include issues with chart starting position, OHLC chart rendering, price axis display, line chart movement, event listener warnings, histogram series color application, price axis scaling, line series display, crosshair updates, and pinch gesture handling.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
// Bug Fix: Chart cannot start from the left
// Bug Fix: OHLC charts render incorrect when value is provided
// Bug Fix: Price axis is not shown if series is created inside promise chain
// Bug Fix: Line chart cannot move to the left
// Bug Fix: Non-passive event listener warnings
// Bug Fix: applyOptions of histogram series with color doesn't affect the data
// Bug Fix: Price Axis Scaling Bug
// Bug Fix: LineSeries is not displayed if starting x value is out of viewport
// Bug Fix: Crosshair isn't updated when timescale is changed
// Bug Fix: Pinch isn't prevented by long tap
```

----------------------------------------

TITLE: ISeriesPrimitive Interface Getters
DESCRIPTION: These getter functions are invoked by the library to obtain references to the views defined within a series primitive. They allow primitives to specify different views for various chart sections.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/plugins/series-primitives

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitiveBase:
  paneViews(): IPrimitivePaneView[] | undefined
    - Returns views for drawing on the main chart pane.
  priceAxisPaneViews(): IPrimitivePaneView[] | undefined
    - Returns views for drawing on the price scale pane.
  timeAxisPaneViews(): IPrimitivePaneView[] | undefined
    - Returns views for drawing on the horizontal time scale pane.
  priceAxisViews(): ISeriesPrimitiveAxisView[] | undefined
    - Returns views for defining labels on the price scale.
  timeAxisViews(): ISeriesPrimitiveAxisView[] | undefined
    - Returns views for defining labels on the time scale.
```

----------------------------------------

TITLE: Data Changed Handler
DESCRIPTION: A callback function type that is invoked when data in a series has changed.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/YieldCurveSeriesType

LANGUAGE: APIDOC
CODE:
```
DataChangedHandler: (scope: DataChangedScope) => void
```

----------------------------------------

TITLE: Lightweight Charts Release Notes
DESCRIPTION: Lists all release versions of the Lightweight Charts library, with links to specific release notes and documentation for each version.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: APIDOC
CODE:
```
Release Notes:
  https://tradingview.github.io/lightweight-charts/docs/release-notes

This section provides a history of all Lightweight Charts releases, starting from version 1.0.0. Each entry typically includes:
- Version number
- Release date (implied by order)
- Key changes, new features, bug fixes, and improvements for that version.

Example entries:
- 1.0.0: The first release. Docs available at https://github.com/tradingview/lightweight-charts/tree/v1.0.0/docs.
- 5.0.8: Latest documented version (as per provided text).
- ... and many other versions listed chronologically.
```

----------------------------------------

TITLE: Line Series Partial Options
DESCRIPTION: Defines partial options for configuring a line series in Lightweight Charts. This allows for incremental updates to existing series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
LineSeriesPartialOptions:
  color?: 
    string
    The color of the line. Defaults to '#21384d'.
  lineStyle?: 
    0 | 1 | 2 | 3
    The style of the line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  lineWidth?: 
    number
    The width of the line. Defaults to 2.
  lineType?: 
    0 | 1
    The type of the line (0: simple, 1: with area). Defaults to 0.
  crosshairMarkerVisible?: 
    boolean
    Whether the crosshair marker is visible on the line. Defaults to true.
  crosshairMarkerColor?: 
    string
    The color of the crosshair marker. Defaults to '#21384d'.
  crosshairMarkerRadius?: 
    number
    The radius of the crosshair marker. Defaults to 4.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/ITextWatermarkPluginApi

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Histogram Series Options
DESCRIPTION: Defines the options for a Histogram Series, including styling and data properties. This is a partial type, meaning not all properties are required.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/CustomSeriesPricePlotValues

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series
```

----------------------------------------

TITLE: Deep Partial Utility
DESCRIPTION: A utility type that makes all properties of a type, and all nested properties, optional.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  T extends object ? {
    [P in keyof T]?: DeepPartial<T[P]>;
  } : T
```

----------------------------------------

TITLE: TimeScalePoint Interface
DESCRIPTION: Interface representing a point on the time scale in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/ISeriesPrimitivePaneView

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint
  Represents a point on the time scale.
```

----------------------------------------

TITLE: APIDOC: Other Type Aliases
DESCRIPTION: References to other supported type aliases in the Lightweight Charts API, including UpDownMarkersSupportedSeriesTypes, VertAlign, VisiblePriceScaleOptions, and YieldCurveSeriesType.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineWidth

LANGUAGE: APIDOC
CODE:
```
Type Aliases:
* UpDownMarkersSupportedSeriesTypes
* VertAlign
* VisiblePriceScaleOptions
* YieldCurveSeriesType
```

----------------------------------------

TITLE: TimeScaleOptions API Documentation
DESCRIPTION: Provides details on various properties available within the TimeScaleOptions interface for Lightweight Charts. This includes options for controlling scrolling behavior, edge locking, and visual aspects of the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  fixLeftEdge: boolean
    Prevent scrolling to the left of the first bar.
    Default Value: false
    Inherited from: HorzScaleOptions.fixLeftEdge

  fixRightEdge: boolean
    Prevent scrolling to the right of the most recent bar.
    Default Value: false
    Inherited from: HorzScaleOptions.fixRightEdge

  lockVisibleTimeRangeOnResize: boolean
    Prevent changing the visible time range during chart resizing.
    Default Value: false
    Inherited from: HorzScaleOptions.lockVisibleTimeRangeOnResize

  rightBarStaysOnScroll: boolean
    Prevent the hovered bar from moving when scrolling.
    Default Value: false
    Inherited from: HorzScaleOptions.rightBarStaysOnScroll

  borderVisible: boolean
    Show the time scale border.
    Default Value: true
    Inherited from: HorzScaleOptions.borderVisible

  borderColor: string
    The time scale border color.
    Default Value: '#2B2B43'
    Inherited from: HorzScaleOptions.borderColor

  visible: boolean
    Show the time scale.
    Default Value: true
```

----------------------------------------

TITLE: AreaData Interface
DESCRIPTION: Represents a single data point for an area series, including a value and optionally time.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
AreaData:
  time: "Time"
  value: "number"
```

----------------------------------------

TITLE: Type Alias: ISeriesPrimitive
DESCRIPTION: Interface for primitive series elements that can be rendered on the chart.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitive:
  draw(ctx: CanvasRenderingContext2D, timeScale: TimeScale, priceScale: PriceScale, // ... other parameters
  )

Interface for primitive series elements.
```

----------------------------------------

TITLE: SeriesMarkerBar Properties
DESCRIPTION: Details the properties of the SeriesMarkerBar interface, which represents a marker on a chart bar. It includes properties like position, time, shape, color, and optional id, text, and size. Some properties are inherited from SeriesMarkerBase.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesMarkerBar

LANGUAGE: APIDOC
CODE:
```
SeriesMarkerBar:
  Properties:
    position: SeriesMarkerBarPosition - The position of the marker. Overrides SeriesMarkerBase.position.
    time: TimeType - The time of the marker. Inherited from SeriesMarkerBase.time.
    shape: SeriesMarkerShape - The shape of the marker. Inherited from SeriesMarkerBase.shape.
    color: string - The color of the marker. Inherited from SeriesMarkerBase.color.
    id?: string - The optional ID of the marker. Inherited from SeriesMarkerBase.id.
    text?: string - The optional text of the marker. Inherited from SeriesMarkerBase.text.
    size?: number - The optional size of the marker. Defaults to 1. Inherited from SeriesMarkerBase.size.
```

----------------------------------------

TITLE: ISeriesPrimitiveBase Methods
DESCRIPTION: This section covers the methods of the ISeriesPrimitiveBase interface. These methods are crucial for managing how custom series primitives interact with the chart, including updating views, retrieving labels for price and time axes, and defining how primitives are rendered in different chart panes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/ISeriesPrimitiveBase

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitiveBase:
  updateAllViews(): void
    - Called when the viewport changes, requiring the primitive to recalculate or invalidate its data.
    - Returns: void

  priceAxisViews(): readonly ISeriesPrimitiveAxisView[]
    - Returns an array of labels to be drawn on the price axis used by the series.
    - Returns: readonly ISeriesPrimitiveAxisView[]
    - Note: For performance, return the same array reference if no changes occur.

  timeAxisViews(): readonly ISeriesPrimitiveAxisView[]
    - Returns an array of labels to be drawn on the time axis.
    - Returns: readonly ISeriesPrimitiveAxisView[]
    - Note: For performance, return the same array reference if no changes occur.

  paneViews(): readonly IPrimitivePaneView[]
    - Returns an array of objects representing primitives in the main chart area.
    - Returns: readonly IPrimitivePaneView[]
    - Note: For performance, return the same array reference if no changes occur.

  priceAxisPaneViews(): readonly IPrimitivePaneView[]
    - Returns an array of objects representing primitives in the price axis area of the chart.
    - Returns: readonly IPrimitivePaneView[]
    - Note: For performance, return the same array reference if no changes occur.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options specific to histogram series

HistogramSeriesPartialOptions:
  // Partial options for histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options specific to line series

LineSeriesPartialOptions:
  // Partial options for line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series, allowing updates to specific properties
```

----------------------------------------

TITLE: Base and Utility Type Aliases
DESCRIPTION: Includes fundamental type aliases such as BaseValueType, BarPrice, Background, and AutoscaleInfoProvider. These types are essential for various chart configurations and data representations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/BaseValueType

LANGUAGE: typescript
CODE:
```
type BaseValueType = number | string;
type BarPrice = { open: number; high: number; low: number; close: number };
type Background = { type: 'solid'; color: string };
type AutoscaleInfoProvider = () => { firstValue: number; lastValue: number };
```

----------------------------------------

TITLE: Lightweight Charts General Utility Types
DESCRIPTION: Includes general utility types such as Rgba color representation, series type enumeration, and event handlers for size changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScaleItemConverterToInternalObj

LANGUAGE: APIDOC
CODE:
```
Rgba:
  Represents a color in RGBA format.

SeriesType:
  Enumerates the different types of series available.

SizeChangeEventHandler:
  An event handler for size change events.

TickMarkFormatter:
  A function type for formatting tick marks.

TickMarkWeightValue:
  Represents a value with a weight for tick marks.

LineWidth:
  Represents the width of a line.

Logical:
  A generic type for logical values.

Mutable:
  A type indicating that a value is mutable.

Nominal:
  A type indicating a nominal value.
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsMap interface, which maps series types to their specific options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/AutoscaleInfo

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap

Maps series types to their specific options.

```

----------------------------------------

TITLE: Lightweight Charts v1.0.1 Bug Fixes
DESCRIPTION: Version 1.0.1 resolves an issue where setting data to a series failed after setting data to a histogram series with a custom color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: javascript
CODE:
```
// Fix for data setting failure after histogram with custom color (conceptual)
// histogramSeries.applyOptions({ color: 'green' });
// histogramSeries.setData(histogramData);
// lineSeries.setData(lineData);
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These aliases define specific data types, options, and event handlers for chart customization and interaction.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  Represents the options for a histogram series.

HistogramSeriesPartialOptions:
  Represents partial options for a histogram series, allowing for incremental updates.

HorzAlign:
  Defines horizontal alignment options for chart elements.

HorzScaleItemConverterToInternalObj<HorzScaleItem>:
  A type alias for a converter function that transforms horizontal scale items to an internal object format.

ISeriesPrimitive<HorzScaleItem>:
  An interface for series primitives that interact with the horizontal scale.

InternalHorzScaleItem:
  Represents an internal structure for horizontal scale items.

InternalHorzScaleItemKey:
  A key type for internal horizontal scale items.

LineSeriesOptions:
  Represents the options for a line series.

LineSeriesPartialOptions:
  Represents partial options for a line series.

LineWidth:
  Defines the possible values for line width.

Logical:
  A type alias for logical time points.

LogicalRange:
  Represents a range of logical time points.

LogicalRangeChangeEventHandler<HorzScaleItem>:
  An event handler type for changes in the logical range, potentially involving horizontal scale items.

MouseEventHandler<HorzScaleItem>:
  A generic type for mouse event handlers, adaptable to horizontal scale items.

Mutable<T>:
  A utility type to indicate a mutable type T.

Nominal<T, Name>:
  A nominal typing utility to create distinct types from a base type T.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn():
  A function type for formatting percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn():
  A function type for formatting prices.

PriceToCoordinateConverter():
  A function type for converting price values to chart coordinates.

SeriesMarkerPosition:
  Defines the possible positions for series markers.

SeriesMarkerShape:
  Defines the possible shapes for series markers.

SeriesOptions<T>:
  A generic type for series options, where T is the specific series type.

SeriesPartialOptions<T>:
  A generic type for partial series options.

SeriesPrimitivePaneViewZOrder:
  Defines the Z-order for series primitive pane views.

SeriesType:
  An enumeration of available series types (e.g., 'Line', 'Area', 'Histogram').

SizeChangeEventHandler():
  An event handler type for size change events.

TickMarkFormatter():
  A function type for formatting tick marks on an axis.

TickMarkWeightValue:
  Represents the weight or significance of a tick mark.

Time:
  A type alias for time values used in the chart.

TimeFormatterFn<HorzScaleItem>():
  A function type for formatting time values, potentially related to horizontal scale items.

TimePointIndex:
  An index representing a specific time point.

TimeRangeChangeEventHandler<HorzScaleItem>():
  An event handler type for changes in the time range, potentially involving horizontal scale items.

UTCTimestamp:
  A type alias for UTC timestamps.

VertAlign:
  Defines vertical alignment options for chart elements.
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API. These include options for different series types (Area, Bar, Candlestick, Histogram, Line, Baseline), price formatting, scaling information, and event handling types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/Coordinate

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  // Options for Area Series

AreaSeriesPartialOptions:
  // Partial options for Area Series

AutoscaleInfoProvider:
  // Provider for autoscale information

Background:
  // Background properties

BarPrice:
  // Price for a bar

BarSeriesOptions:
  // Options for Bar Series

BarSeriesPartialOptions:
  // Partial options for Bar Series

BaseValueType:
  // Base value type

BaselineSeriesOptions:
  // Options for Baseline Series

BaselineSeriesPartialOptions:
  // Partial options for Baseline Series

CandlestickSeriesOptions:
  // Options for Candlestick Series

CandlestickSeriesPartialOptions:
  // Partial options for Candlestick Series

Coordinate:
  // Represents a coordinate on the chart

DeepPartial:
  // Utility type for deep partial objects

HistogramSeriesOptions:
  // Options for Histogram Series

HistogramSeriesPartialOptions:
  // Partial options for Histogram Series

HorzAlign:
  // Horizontal alignment options

LineSeriesOptions:
  // Options for Line Series

LineSeriesPartialOptions:
  // Partial options for Line Series

LineWidth:
  // Line width definition

Logical:
  // Represents a logical index

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Nominal:
  // Represents a nominal value

OverlayPriceScaleOptions:
  // Options for overlay price scales

PriceFormat:
  // Defines price formatting options
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines the partial options for a Candlestick Series, allowing for incremental updates to candlestick chart configurations. This is useful for changing specific visual elements like candle colors or wick styles.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  upColor?: CustomColorParser
  downColor?: CustomColorParser
  borderUpColor?: CustomColorParser
  borderDownColor?: CustomColorParser
  wickUpColor?: CustomColorParser
  wickDownColor?: CustomColorParser
```

----------------------------------------

TITLE: BaselineStyleOptions Interface
DESCRIPTION: Options for styling baseline series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
BaselineStyleOptions:
  topLineColor: string
    Color of the top line of the baseline.
  bottomLineColor: string
    Color of the bottom line of the baseline.
  topFillColor1: string
    Color of the top fill gradient (first color).
  topFillColor2: string
    Color of the top fill gradient (second color).
  bottomFillColor1: string
    Color of the bottom fill gradient (first color).
  bottomFillColor2: string
    Color of the bottom fill gradient (second color).
```

----------------------------------------

TITLE: Core Value and Coordinate Types
DESCRIPTION: Defines fundamental type aliases for values and coordinates used within the charting library. `BarPrice` represents the price of a bar, `BaseValueType` is a generic type for values, and `Coordinate` defines point coordinates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/ISeriesPrimitive

LANGUAGE: typescript
CODE:
```
type BarPrice = number;
type BaseValueType = number | string;
type Coordinate = number;
```

----------------------------------------

TITLE: Series Options and Types
DESCRIPTION: Defines options and types for different series types like Histogram and Line, including partial options for incremental updates and general series configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/AreaSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options specific to histogram series

HistogramSeriesPartialOptions:
  // Partial options for histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options specific to line series

LineSeriesPartialOptions:
  // Partial options for line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series configurations
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Defines the structure for candlestick data, including open, high, low, and close prices, along with time and volume. It supports generic type for horizontal scale items.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickData<HorzScaleItem>
  Properties:
    time: Time | BusinessDay - The time of the bar.
    open: number - The opening price of the bar.
    high: number - The highest price of the bar.
    low: number - The lowest price of the bar.
    close: number - The closing price of the bar.
    value?: number - Optional value for the bar.
    color?: string - Optional color for the bar.
    data?: HorzScaleItem - Optional custom data for the horizontal scale item.
```

----------------------------------------

TITLE: Lightweight Charts v1.0.1 - Bug Fixes
DESCRIPTION: Version 1.0.1 of the lightweight-charts library resolves an issue where setting data to a series failed after setting data to a histogram series with a custom color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/release-notes

LANGUAGE: javascript
CODE:
```
// Fix: Setting the data to series fails after setting the data to histogram series with custom color
// Related Issue: #110
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/TickmarksPercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: HorzScaleOptions Interface
DESCRIPTION: Defines options for the horizontal (time) scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/BarData

LANGUAGE: APIDOC
CODE:
```
HorzScaleOptions:
  visible?: boolean
  ticksVisible?: boolean
  labelsVisible?: boolean
  uniformDistribution?: boolean
  timeVisible?: boolean
  timeFormat?: DateTimeFormat
  dateFormat?: DateTimeFormat
  rightOffset?: number
  leftOffset?: number
  mode?: 'normal' | 'week' | 'day'
  invert?: boolean
  snap?: boolean
  fixLeftEdge?: boolean
  fixRightEdge?: boolean
  minValidTime?: Time
  maxValidTime?: Time
  visibleRange?: { from: Time, to: Time }
  lockVisibleTimeRange?: boolean
  scaleMargins?: AutoScaleMargins
  syncTooltips?: boolean
  labelStyle?: TextStyle
  tickMarkColor?: string
  labelColor?: string
  borderVisible?: boolean
  borderColor?: string
  padding?: { top?: number, bottom?: number }
  autoScale?: boolean
  minScaleRatio?: number
  maxScaleRatio?: number
  visibleTimeRange?: { from: Time, to: Time }
  lockVisibleRange?: boolean
  timeAxis?: boolean
  timeAxisVisible?: boolean
  timeAxisLabelsVisible?: boolean
  timeAxisFormat?: DateTimeFormat
  timeAxisTickMarksVisible?: boolean
  timeAxisLabelStyle?: TextStyle
  timeAxisTickMarkColor?: string
  timeAxisLabelColor?: string
  timeAxisBorderVisible?: boolean
  timeAxisBorderColor?: string
  timeAxisPadding?: { top?: number, bottom?: number }
  timeAxisAutoScale?: boolean
  timeAxisMinScaleRatio?: number
  timeAxisMaxScaleRatio?: number
```

----------------------------------------

TITLE: AutoscaleInfoPartial Interface
DESCRIPTION: Partial information related to autoscale behavior for a single price scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AutoscaleInfoPartial:
  minPossibleAmount: number
  maxPossibleAmount: number
```

----------------------------------------

TITLE: AutoScaleMargins Interface Properties
DESCRIPTION: Defines the properties for automatic scaling margins in Lightweight Charts. 'below' specifies the number of pixels for the bottom margin, and 'above' specifies the number of pixels for the top margin.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  below: number
    The number of pixels for bottom margin
  above: number
    The number of pixels for top margin
```

----------------------------------------

TITLE: Style Options Interfaces
DESCRIPTION: Interfaces for configuring the visual appearance of different series types, including Area, Bar, Candlestick, Histogram, and Baseline series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesStyleOptionsMap

LANGUAGE: APIDOC
CODE:
```
AreaStyleOptions:
  color?: string
    // The color of the area.
  lineColor?: string
    // The color of the area's border line.
  lineWidth?: number
    // The width of the area's border line.
  topColor?: string
    // The color of the top gradient fill.
  bottomColor?: string
    // The color of the bottom gradient fill.

BarStyleOptions:
  color?: string
    // The color of the bars.
  openVisible?: boolean
    // Whether the open price line is visible.
  thinBars?: boolean
    // Whether to use thin bars.

CandlestickStyleOptions:
  color?: string
    // The color of the candlestick body when the price increases.
  increase?: { color: string }
    // The color of the candlestick body when the price increases.
  decrease?: { color: string }
    // The color of the candlestick body when the price decreases.
  wickVisible?: boolean
    // Whether the wick is visible.
  borderVisible?: boolean
    // Whether the border is visible.
  borderColor?: string
    // The color of the candlestick border.
  wickColor?: string
    // The color of the candlestick wick.

HistogramStyleOptions:
  color?: string
    // The color of the histogram bars.
  base?: number
    // The base value for the histogram.

BaselineStyleOptions:
  topLine?: { color: string, width: number }
    // Configuration for the top line of the baseline.
  bottomLine?: { color: string, width: number }
    // Configuration for the bottom line of the baseline.
  topFill?: { color: string }
    // Color for the top fill area.
  bottomFill?: { color: string }
    // Color for the bottom fill area.
  base?: number
    // The base value for the baseline.

CustomStyleOptions:
  // Options specific to custom series types.
```

----------------------------------------

TITLE: WhitespaceData Interface Definition
DESCRIPTION: Defines the WhitespaceData interface, which includes a 'time' property. This interface is extended by other data types like OhlcData and SingleValueData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/WhitespaceData

LANGUAGE: APIDOC
CODE:
```
Interface: WhitespaceData<HorzScaleItem>

Represents a whitespace data item, which is a data point without a value.

Type parameters:
• HorzScaleItem = Time

Properties:
### time
> **time** : `HorzScaleItem`
The time of the data.
```

----------------------------------------

TITLE: ISeriesPrimitiveWrapper - getSeries
DESCRIPTION: Retrieves the series associated with the primitive wrapper. This method is inherited from ISeriesPrimitiveWrapper.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesMarkersPluginApi

LANGUAGE: APIDOC
CODE:
```
getSeries(): SeriesApi
  Retrieves the series associated with the primitive wrapper.
  Inherited from:
    ISeriesPrimitiveWrapper.getSeries
```

----------------------------------------

TITLE: Lightweight Charts v3.0.1 Fixes
DESCRIPTION: This release corrects the handling of `overlay: true` in series options during series creation to maintain backward compatibility.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/release-notes

LANGUAGE: javascript
CODE:
```
// Fix: Correctly handle 'overlay: true' in series options while create series to backward compat
// See: https://github.com/tradingview/lightweight-charts/issues/475
```

----------------------------------------

TITLE: Generic Type Aliases
DESCRIPTION: Provides generic type aliases for common programming patterns like mutable values and nominal types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
Mutable<T>:
  T

Nominal<T, Name>:
  T
```

----------------------------------------

TITLE: Interface: TimeScalePoint
DESCRIPTION: Represents a point on the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/AutoScaleMargins

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint
  Represents a point on the time scale.
```

----------------------------------------

TITLE: CandlestickSeriesPartialOptions Type Alias
DESCRIPTION: Defines optional properties for candlestick series, extending SeriesPartialOptions and CandlestickStyleOptions. This type alias is part of the unreleased 'Next' version of Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesPartialOptions
> **CandlestickSeriesPartialOptions** : [`SeriesPartialOptions`](https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/SeriesPartialOptions) <[`CandlestickStyleOptions`](https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CandlestickStyleOptions)>
Represents candlestick series options where all properties are optional.
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases
DESCRIPTION: This section lists various type aliases available in the Next version of Lightweight Charts. These aliases define specific data types and function signatures used within the charting library, such as formatters for tick marks and time, and types for time points and timestamps.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BarSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
TickMarkFormatter
TickMarkWeightValue
TickmarksPercentageFormatterFn
TickmarksPriceFormatterFn
Time
TimeFormatterFn
TimePointIndex
TimeRangeChangeEventHandler
UTCTimestamp
UpDownMarkersSupportedSeriesTypes
VertAlign
VisiblePriceScaleOptions
YieldCurveSeriesType
```

----------------------------------------

TITLE: AutoScaleMargins Interface
DESCRIPTION: Defines margins for auto-scaling the price axis, ensuring data points are not cut off.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  top?: "number"
  bottom?: "number"
```

----------------------------------------

TITLE: TextWatermarkLineOptions Properties
DESCRIPTION: Documentation for properties within the TextWatermarkLineOptions interface, including their types and default values. This covers font-related settings for text watermarks.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TextWatermarkLineOptions

LANGUAGE: APIDOC
CODE:
```
TextWatermarkLineOptions:
  fontFamily: string
    Font family.
    Default Value: "-apple-system, BlinkMacSystemFont, 'Trebuchet MS', Roboto, Ubuntu, sans-serif"
  fontStyle: string
    Font style.
    Default Value: ""
  fontSize: number
    Font size.
    Default Value: "1.2 * fontSize"
  color: string
    Color of the text watermark.
  text: string
    The text of the watermark.
  lineHeight?: number
    The height of the line.
```

----------------------------------------

TITLE: CandlestickStyleOptions Interface
DESCRIPTION: Options for styling candlestick series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
CandlestickStyleOptions:
  upColor: string
    Color of an up candlestick.
  downColor: string
    Color of a down candlestick.
  borderVisible: boolean
    Whether or not to show borders of candlesticks.
  borderColor: string
    Color of borders of candlesticks.
  wickVisible: boolean
    Whether or not to show wicks of candlesticks.
  wickColor: string
    Color of wicks of candlesticks.
```

----------------------------------------

TITLE: Data Item Structure
DESCRIPTION: Represents a single data point within a series. It typically includes a timestamp and a value.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
DataItem:
  // A single data point
  time: Time;
  value: number;
  // For candlestick/bar series, additional properties like open, high, low, close might be present
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Handling
DESCRIPTION: Defines types related to time points, time ranges, and event handlers for changes in logical and time ranges.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
Time:
  // Represents a point in time, could be a Date object, timestamp, or custom format

TimePointIndex:
  // An index representing a specific time point

LogicalRange:
  // Represents a range defined by logical indices

LogicalRangeChangeEventHandler:
  // Handler for events when the logical range changes
  // (newRange: LogicalRange | null) => void

TimeRangeChangeEventHandler:
  // Handler for events when the time range changes
  // (newRange: TimeRange | null) => void
```

----------------------------------------

TITLE: SingleValueData Interface
DESCRIPTION: Represents a data point with a time and a value, serving as a base for other data types like HistogramData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: SingleValueData
Structure describing a single item of data
Properties:
### time
> **time** : `Time`
The time of the data.
* * *
### value
> **value** : `number`
Price value of the data.
```

----------------------------------------

TITLE: ISeriesPrimitiveAxisView Interface Documentation
DESCRIPTION: Documentation for the ISeriesPrimitiveAxisView interface, which represents a label on the price or time axis. It includes details about its methods, specifically the 'coordinate' method.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/ISeriesPrimitiveAxisView

LANGUAGE: APIDOC
CODE:
```
Interface: ISeriesPrimitiveAxisView

This interface represents a label on the price or time axis.

Methods:
  coordinate()
    Returns: number
    Description: The desired coordinate for the label. Note that the label will be automatically moved to prevent overlapping with other labels. If you would like the label to be drawn at the exact coordinate under all circumstances then rather use `fixedCoordinate`. For a price axis the value returned will represent the vertical distance (pixels) from the top. For a time axis the value will represent the horizontal distance from the left.
    Return Value: coordinate. distance from top for price axis, or distance from left for time axis.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DeepPartial

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: PriceScaleOptions API Documentation
DESCRIPTION: Documentation for various properties of PriceScaleOptions in Lightweight Charts, including alignment, margins, borders, text, visibility, and width.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/PriceScaleOptions

LANGUAGE: APIDOC
CODE:
```
alignLabels:
  type: boolean
  description: Align price scale labels to prevent them from overlapping.
  defaultValue: true

scaleMargins:
  type: PriceScaleMargins
  description: Price scale margins.
  defaultValue: { bottom: 0.1, top: 0.2 }
  example: |
    chart.priceScale('right').applyOptions({
      scaleMargins: {
        top: 0.8,
        bottom: 0,
      },
    });

borderVisible:
  type: boolean
  description: Set true to draw a border between the price scale and the chart area.
  defaultValue: true

borderColor:
  type: string
  description: Price scale border color.
  defaultValue: '#2B2B43'

textColor:
  type: string (optional)
  description: Price scale text color. If not provided LayoutOptions.textColor is used.
  defaultValue: undefined

entireTextOnly:
  type: boolean
  description: Show top and bottom corner labels only if entire text is visible.
  defaultValue: false

visible:
  type: boolean
  description: Indicates if this price scale visible. Ignored by overlay price scales.
  defaultValue: true for the right price scale and false for the left

ticksVisible:
  type: boolean
  description: Draw small horizontal line on price axis labels.
  defaultValue: false

minimumWidth:
  type: number
  description: Define a minimum width for the price scale. This value will be exceeded if the price scale needs more space to display its contents. Useful for ensuring identical price scale widths across multiple charts or for plugins requiring more space within the price scale pane.
  defaultValue: undefined
```

----------------------------------------

TITLE: Background Type
DESCRIPTION: Defines the type for background properties, allowing customization of the chart's background.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Background:
  // Properties for chart background
  // Properties:
  //   - type: 'solid' | 'gradient'
  //   - color: string (for solid background)
  //   - topColor: string (for gradient background)
  //   - bottomColor: string (for gradient background)
  // Example:
  // {
  //   type: 'solid',
  //   color: '#f0f0f0'
  // }
```

----------------------------------------

TITLE: Lightweight Charts Documentation Links
DESCRIPTION: Provides links to key documentation sections for Lightweight Charts, including Getting Started, Tutorials, and the full API Reference.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/SeriesAttachedParameter

LANGUAGE: APIDOC
CODE:
```
Documentation:
  Getting Started: https://tradingview.github.io/lightweight-charts/docs
  Tutorials: https://tradingview.github.io/lightweight-charts/tutorials
  API Reference: https://tradingview.github.io/lightweight-charts/docs/api
```

----------------------------------------

TITLE: Lightweight Charts Plugins Introduction
DESCRIPTION: Overview of Lightweight Charts plugins, enabling extension of library functionality with Custom Series and Drawing Primitives. Links to documentation and examples are provided.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: APIDOC
CODE:
```
Plugins:
  - Custom Series: Allows defining new types of data series.
  - Drawing Primitives: Enables creation of custom drawing tools and annotations.

Getting Started:
  - Documentation: https://tradingview.github.io/lightweight-charts/docs/next/plugins/intro
  - Examples: https://github.com/tradingview/lightweight-charts/tree/master/plugin-examples
  - Plugin Creation Tool: npm install -g create-lwc-plugin

Use Cases:
  - Highly customizable charting applications.
  - Unique data visualizations.
  - Custom interactive drawing tools.
```

----------------------------------------

TITLE: CandlestickData Interface
DESCRIPTION: Represents a single data point for a candlestick series. It includes the time, open, high, low, and close values, similar to BarData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/CrosshairOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickData:
  // Data point for a candlestick series
  //   - time: Time
  //   - open: number
  //   - high: number
  //   - low: number
  //   - close: number
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
```

----------------------------------------

TITLE: SingleValueData Interface
DESCRIPTION: Represents a base interface for data points in single-value series. It extends WhitespaceData and defines the 'time' property.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/SingleValueData

LANGUAGE: APIDOC
CODE:
```
Interface: SingleValueData<HorzScaleItem>
A base interface for a data point of single-value series.

Extends:
  * `WhitespaceData`<`HorzScaleItem`>

Extended by:
  * `AreaData`
  * `BaselineData`
  * `HistogramData`
  * `LineData`

Type parameters:
• **HorzScaleItem** = `Time`

Properties:
### time
> **time** : `HorzScaleItem`
The time of the data.
```

----------------------------------------

TITLE: Lightweight Charts 4.1 Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 4.1. These types define the structure and behavior of different chart elements, options, and event handlers. This documentation is for an older, unmaintained version.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
ISeriesPrimitive:
  Represents a primitive series on the chart.

InternalHorzScaleItem:
  Represents an item within the internal horizontal scale.

InternalHorzScaleItemKey:
  The key for an item in the internal horizontal scale.

LineSeriesOptions:
  Options specific to a Line Series.

LineSeriesPartialOptions:
  Partial options for a Line Series, allowing for updates.

LineWidth:
  Defines the width of a line.

Logical:
  Represents a logical index or position.

LogicalRange:
  Defines a range using logical indices.

LogicalRangeChangeEventHandler:
  An event handler for changes in the logical range.

MouseEventHandler:
  A handler for mouse events.

Mutable:
  Indicates a type that can be mutated.

Nominal:
  Represents a nominal value.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn:
  A function to format percentages.

PriceFormat:
  Defines the format for displaying prices.

PriceFormatterFn:
  A function to format prices.

PriceToCoordinateConverter:
  A function to convert price to a coordinate.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.

SeriesOptions:
  General options for any series type.

SeriesPartialOptions:
  Partial options for any series type.

SeriesPrimitivePaneViewZOrder:
  Defines the Z-order for series primitive pane views.

SeriesType:
  An enum representing the type of a series (e.g., Line, Bar, Area).

SizeChangeEventHandler:
  An event handler for size changes.

TickMarkFormatter:
  A formatter for tick marks on the price scale.

TickMarkWeightValue:
  A value representing the weight of a tick mark.

Time:
  Represents a point in time, can be a Date object, UTCTimestamp, or string.

TimeFormatterFn:
  A function to format time values.

TimePointIndex:
  An index representing a time point.

TimeRangeChangeEventHandler:
  An event handler for changes in the time range.

UTCTimestamp:
  A timestamp in UTC milliseconds.

VertAlign:
  Defines vertical alignment options.

VisiblePriceScaleOptions:
  Options for a visible price scale.
```

----------------------------------------

TITLE: TimeScalePoint Interface Documentation
DESCRIPTION: Documentation for the TimeScalePoint interface, which represents a point on the time scale. It includes properties like timeWeight and time, detailing their types and descriptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/TimeScalePoint

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint
Represents a point on the time scale

Properties:
  timeWeight:
    readonly timeWeight : TickMarkWeightValue
    Weight of the point

  time:
    readonly time : object
    Time of the point
      species:
        species : "InternalHorzScaleItem"
        The 'name' or species of the nominal.
```

----------------------------------------

TITLE: Series Data Interfaces
DESCRIPTION: Interfaces for defining data points for different series types, including Area, Bar, Candlestick, Histogram, and Baseline series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/SeriesStyleOptionsMap

LANGUAGE: APIDOC
CODE:
```
AreaData:
  time: Time | BusinessDay
    // The time of the data point.
  value: number
    // The value of the data point.

BarData:
  time: Time | BusinessDay
    // The time of the data point.
  open: number
    // The opening price.
  high: number
    // The highest price.
  low: number
    // The lowest price.
  close: number
    // The closing price.

CandlestickData:
  time: Time | BusinessDay
    // The time of the data point.
  open: number
    // The opening price.
  high: number
    // The highest price.
  low: number
    // The lowest price.
  close: number
    // The closing price.

HistogramData:
  time: Time | BusinessDay
    // The time of the data point.
  value: number
    // The value of the data point.

BaselineData:
  time: Time | BusinessDay
    // The time of the data point.
  value: number
    // The value of the data point.
  topFill?: number
    // The value for the top fill boundary.
  bottomFill?: number
    // The value for the bottom fill boundary.
```

----------------------------------------

TITLE: Lightweight Charts Scale and Alignment Types
DESCRIPTION: Defines types related to horizontal alignment, price scale items, and converters for scale data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesMarkerPosition

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  Represents the horizontal alignment of an element.

HorzScaleItemConverterToInternalObj:
  A function type for converting horizontal scale items to an internal object format.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

InternalHorzScaleItem:
  An internal representation of an item on the horizontal scale.

InternalHorzScaleItemKey:
  A key used to identify internal horizontal scale items.

OverlayPriceScaleOptions:
  Options for an overlay price scale.
```

----------------------------------------

TITLE: Supported Series Types and Alignment Options
DESCRIPTION: Lists supported series types for up/down markers and vertical alignment options for chart elements in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/InternalHorzScaleItemKey

LANGUAGE: APIDOC
CODE:
```
UpDownMarkersSupportedSeriesTypes: Supported series types for up/down markers.
VertAlign: Vertical alignment options for chart elements.
```

----------------------------------------

TITLE: SeriesDataItemTypeMap Interface
DESCRIPTION: Defines the types of data that a series can contain. For example, a bar series can hold BarData or WhitespaceData.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/SeriesDataItemTypeMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesDataItemTypeMap

Represents the type of data that a series contains.
For example a bar series contains [BarData](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/BarData) or [WhitespaceData](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/WhitespaceData).

Properties:
  Bar: [`BarData`](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/BarData) | [`WhitespaceData`](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/WhitespaceData)
    The types of bar series data.
  Candlestick: [`CandlestickData`](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/CandlestickData) | [`WhitespaceData`](https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/WhitespaceData)
    The types of candlestick series data.
```

----------------------------------------

TITLE: version Function
DESCRIPTION: Returns the current version of the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/functions/isBusinessDay

LANGUAGE: APIDOC
CODE:
```
version(): string
  Returns:
    The version string of the library.
```

----------------------------------------

TITLE: YieldCurveSeriesType API Documentation
DESCRIPTION: Defines the possible series types for yield curve charts. This type alias specifies the allowed string values for representing area or line charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/YieldCurveSeriesType

LANGUAGE: APIDOC
CODE:
```
Type alias: YieldCurveSeriesType

Description:
  Specifies the type of series used for yield curve charts.

Allowed Values:
  - "Area"
  - "Line"

Usage:
  This type is used when configuring chart series to represent yield curve data.

Example:
  chart.addAreaSeries({ type: 'Area' });
  chart.addLineSeries({ type: 'Line' });
```

----------------------------------------

TITLE: Series Options
DESCRIPTION: Defines the structure for partial options of different series types in Lightweight Charts. Each series type (Candlestick, Area, Baseline, Line, Histogram) extends common series options and allows for deep partial updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/SeriesPartialOptionsMap

LANGUAGE: APIDOC
CODE:
```
Candlestick:
  Type: DeepPartial<CandlestickStyleOptions & SeriesOptionsCommon>
  Description: The type of candlestick series partial options.

Area:
  Type: DeepPartial<AreaStyleOptions & SeriesOptionsCommon>
  Description: The type of area series partial options.

Baseline:
  Type: DeepPartial<BaselineStyleOptions & SeriesOptionsCommon>
  Description: The type of baseline series partial options.

Line:
  Type: DeepPartial<LineStyleOptions & SeriesOptionsCommon>
  Description: The type of line series partial options.

Histogram:
  Type: DeepPartial<HistogramStyleOptions & SeriesOptionsCommon>
  Description: The type of histogram series partial options.

Properties:
  - Bar
  - Candlestick
  - Area
  - Baseline
  - Line
  - Histogram
```

----------------------------------------

TITLE: CandlestickSeriesPartialOptions Type Alias
DESCRIPTION: Defines the partial options for configuring a Candlestick Series in Lightweight Charts. This allows for incremental updates to existing series options.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/CandlestickSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
CandlestickSeriesPartialOptions:
  // Options for the candlestick series
  // These options are partial, meaning you can update only the properties you need.
  priceFormat?: PriceFormat;
  base?: BaseValueType;
  autoscaleInfoProvider?: AutoscaleInfoProvider;
  visible?: boolean;
  title?: string;
  overlay?: boolean;
  priceLineSource?: SeriesPriceLineSource;
  priceLineVisible?: boolean;
  baseLineVisible?: boolean;
  // ... other potential properties for candlestick series customization
```

----------------------------------------

TITLE: Data Changed Scope
DESCRIPTION: Provides context about the data changes that occurred, including the series that was affected and the range of data that was updated.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/AreaSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
DataChangedScope:
  // Information about the data change scope
  // timeScale: The time scale of the chart
  // // Example:
  // {
  //   timeScale: chart.timeScale()
  // }
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates. These types specify visual and behavioral properties of chart series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PrimitiveHasApplyOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  // Options for a histogram series

HistogramSeriesPartialOptions:
  // Partial options for a histogram series, allowing updates to specific properties

LineSeriesOptions:
  // Options for a line series

LineSeriesPartialOptions:
  // Partial options for a line series, allowing updates to specific properties

SeriesOptions:
  // General options applicable to all series types

SeriesPartialOptions:
  // Partial options for general series properties
```

----------------------------------------

TITLE: TimeScaleOptions Properties
DESCRIPTION: Details the various properties available for configuring the time scale in Lightweight Charts. These include settings for offsets, spacing, visibility, and formatting.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
TimeScaleOptions:
  rightOffset: number
    Description: The offset from the right edge of the chart in pixels.
    Default: undefined

  barSpacing: number
    Description: The spacing between bars in pixels.
    Default: undefined

  minBarSpacing: number
    Description: The minimum spacing between bars in pixels.
    Default: undefined

  fixLeftEdge: boolean
    Description: Whether to fix the left edge of the chart.
    Default: undefined

  fixRightEdge: boolean
    Description: Whether to fix the right edge of the chart.
    Default: undefined

  lockVisibleTimeRangeOnResize: boolean
    Description: Whether to lock the visible time range when the chart is resized.
    Default: undefined

  rightBarStaysOnScroll: boolean
    Description: Whether the rightmost bar stays on scroll.
    Default: undefined

  borderVisible: boolean
    Description: Whether the border of the time scale is visible.
    Default: undefined

  borderColor: string
    Description: The color of the time scale border.
    Default: undefined

  visible: boolean
    Description: Whether the time scale is visible.
    Default: undefined

  timeVisible: boolean
    Description: Whether the time labels are visible.
    Default: undefined

  secondsVisible: boolean
    Description: Whether the seconds are visible in the time labels.
    Default: undefined

  shiftVisibleRangeOnNewBar: boolean
    Description: Whether to shift the visible range when a new bar is added.
    Default: undefined

  tickMarkFormatter?: (time: Time, tickMarkType: TickMarkType) => string
    Description: A formatter function for tick marks.
    Default: undefined
```

----------------------------------------

TITLE: Scale and Utility Functions
DESCRIPTION: Functions related to horizontal scale behavior, and type checking for business days and timestamps.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/functions/createSeriesMarkers

LANGUAGE: APIDOC
CODE:
```
defaultHorzScaleBehavior(): HorizontalScaleBehavior
  Returns the default horizontal scale behavior.

isBusinessDay(value: any): value is BusinessDay
  Checks if a value is a BusinessDay.

isUTCTimestamp(value: any): value is UTCTimestamp
  Checks if a value is a UTCTimestamp.

version(): string
  Returns the current version of the Lightweight Charts library.
```

----------------------------------------

TITLE: Data Item
DESCRIPTION: Represents a single data point within a series in Lightweight Charts. This typically includes a timestamp and a value.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/PercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
DataItem:
  // Represents a single data item
  time: Time;
  value: BaseValueType;
  // ... other data item properties
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These aliases define specific data structures and types for chart elements and configurations, ensuring type safety and clarity in development. Examples include UpDownMarkersSupportedSeriesTypes for marker types, VertAlign for vertical alignment, VisiblePriceScaleOptions for price scale visibility, and YieldCurveSeriesType for yield curve data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
Type Aliases:

- UpDownMarkersSupportedSeriesTypes: Supported series types for up/down markers.
- VertAlign: Defines vertical alignment options for chart elements.
- VisiblePriceScaleOptions: Options for controlling the visibility of price scales.
- YieldCurveSeriesType: Specifies the type for yield curve series data.
- BaseValueType: Represents a type of a base value of baseline series type. It extends BaseValuePrice.
```

----------------------------------------

TITLE: UTCTimestamp Type Alias
DESCRIPTION: Defines a UTCTimestamp as a nominal type representing a number of seconds, typically used for intraday intervals. It highlights the difference in units (seconds vs. milliseconds) compared to JavaScript's Date.now() and suggests type casting in TypeScript.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/UTCTimestamp

LANGUAGE: APIDOC
CODE:
```
UTCTimestamp : Nominal<number, "UTCTimestamp">
Represents a time at a UNIX timestamp.
If your chart displays an intraday interval you should use a UNIX Timestamp.
Note that JavaScript Date APIs like `Date.now` return a number of milliseconds but UTCTimestamp expects a number of seconds.
Note that to prevent errors, you should cast the numeric type of the time to `UTCTimestamp` type from the package (`value as UTCTimestamp`) in TypeScript code.
```

LANGUAGE: typescript
CODE:
```
const timestamp =1529899200as UTCTimestamp;// Literal timestamp representing 2018-06-25T04:00:00.000Z  
const timestamp2 =(Date.now()/1000)as UTCTimestamp;
```

----------------------------------------

TITLE: Histogram Series Options
DESCRIPTION: Defines the options for a Histogram Series, including color and base value.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/3.8/api/type-aliases/BaseValueType

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  color?: Color
  base?: number
```

----------------------------------------

TITLE: SeriesOptionsMap Interface Documentation
DESCRIPTION: Documentation for the SeriesOptionsMap interface in the Lightweight Charts Next API. This interface defines the type of options for each series type, with examples like BarSeriesOptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/SeriesOptionsMap

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsMap
Description: Represents the type of options for each series type.
Example: For example a bar series has options represented by [BarSeriesOptions](https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/BarSeriesOptions).
Related: Links to Type Aliases, Variables, and Functions are available in the API documentation.
```

----------------------------------------

TITLE: Interface: SeriesOptionsCommon
DESCRIPTION: Common options applicable to all series types in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/BaseValuePrice

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesOptionsCommon
  
  Common options for all series types.
```

----------------------------------------

TITLE: Lightweight Charts Primitive and Marker Types
DESCRIPTION: Details types related to chart primitives, including their application options, pane views, and z-order. Also covers series marker configurations and their properties.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/DataChangedHandler

LANGUAGE: APIDOC
CODE:
```
IImageWatermarkPluginApi:
  // API for image watermark plugin

IPanePrimitive:
  // Interface for a primitive within a chart pane

ISeriesPrimitive:
  // Interface for a primitive related to a chart series

ITextWatermarkPluginApi:
  // API for text watermark plugin

PrimitiveHasApplyOptions:
  // Type indicating a primitive that can have options applied

PrimitivePaneViewZOrder:
  // Z-order for primitives in a pane view

SeriesMarker:
  // Represents a marker on a series

SeriesMarkerBarPosition:
  // Position of a marker relative to a bar

SeriesMarkerPosition:
  // General position of a series marker

SeriesMarkerPricePosition:
  // Position of a marker relative to a price level

SeriesMarkerShape:
  // Shape of a series marker

SeriesMarkerZOrder:
  // Z-order for series markers

SeriesType:
  // Enum for different series types (e.g., 'Line', 'Area', 'Histogram')
```

----------------------------------------

TITLE: Lightweight Charts API Reference Links
DESCRIPTION: Provides links to various API reference sections for Lightweight Charts, including type aliases and core functionalities.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScalePriceItem

LANGUAGE: APIDOC
CODE:
```
API Reference Sections:
- VertAlign: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/VertAlign
- VisiblePriceScaleOptions: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/VisiblePriceScaleOptions
- YieldCurveSeriesType: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/YieldCurveSeriesType
- HorzScalePriceItem (Variables): https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScalePriceItem
- HorzScalePriceItem (Functions): https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScalePriceItem
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: AutoScaleMargins Interface
DESCRIPTION: Options for controlling automatic margin calculation for price scales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/CandlestickData

LANGUAGE: APIDOC
CODE:
```
AutoScaleMargins:
  top?: number
  bottom?: number
```

----------------------------------------

TITLE: API Reference - AutoscaleMargins
DESCRIPTION: Defines the margins used for autoscale calculations on the price axis.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/BarStyleOptions

LANGUAGE: APIDOC
CODE:
```
interface AutoscaleMargins {
  // Top margin for autoscale
  top?: number;
  // Bottom margin for autoscale
  bottom?: number;
}
```

----------------------------------------

TITLE: Line Series Options
DESCRIPTION: Defines the complete options for configuring a line series in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
LineSeriesOptions:
  color?: 
    string
    The color of the line. Defaults to '#21384d'.
  lineStyle?: 
    0 | 1 | 2 | 3
    The style of the line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  lineWidth?: 
    number
    The width of the line. Defaults to 2.
  lineType?: 
    0 | 1
    The type of the line (0: simple, 1: with area). Defaults to 0.
  crosshairMarkerVisible?: 
    boolean
    Whether the crosshair marker is visible on the line. Defaults to true.
  crosshairMarkerColor?: 
    string
    The color of the crosshair marker. Defaults to '#21384d'.
  crosshairMarkerRadius?: 
    number
    The radius of the crosshair marker. Defaults to 4.
  priceLineSource?: 
    "open" | "close" | "high" | "low"
    The source for the price line. Defaults to 'close'.
  priceLineColor?: 
    string
    The color of the price line. Defaults to '#888888'.
  priceLineStyle?: 
    0 | 1 | 2 | 3
    The style of the price line (0: solid, 1: dotted, 2: dashed, 3: sparse dashed). Defaults to 0.
  priceLineVisible?: 
    boolean
    Whether the price line is visible. Defaults to true.
  priceLineWidth?: 
    number
    The width of the price line. Defaults to 1.
  visible?: 
    boolean
    Whether the series is visible. Defaults to true.
  title?: 
    string
    The title of the series. Defaults to ''.
  lastValueProvider?: 
    (data: readonly 
      (HistogramData | CandlestickData | BarData | LineData | AreaData)
    ) => 
      number | undefined
    A function to provide the last value of the series. Defaults to undefined.
  priceFormat?: 
    PriceFormat
    Formatting options for the price. Defaults to { type: 'number', precision: 2, minMove: 0.01 }.
  autoscaleInfoProvider?: 
    AutoscaleInfoProvider
    Provider for autoscale information. Defaults to undefined.
```

----------------------------------------

TITLE: TimeScalePoint Interface Documentation
DESCRIPTION: Documentation for the TimeScalePoint interface, which represents a point on the time scale in Lightweight Charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/TimeScalePoint

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint
Represents a point on the time scale

Properties:
  (No specific properties listed in the provided text, but the interface defines the structure for points on the time scale.)
```

----------------------------------------

TITLE: Alignment and Series Type
DESCRIPTION: Defines horizontal alignment options and the types of series available.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PercentageFormatterFn

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  'left' | 'center' | 'right'

SeriesType:
  'Area' | 'Line' | 'Bar' | 'Candlestick' | 'Histogram'
```

----------------------------------------

TITLE: HistogramSeriesPartialOptions Type Alias
DESCRIPTION: Defines the HistogramSeriesPartialOptions type alias, which extends SeriesPartialOptions and incorporates HistogramStyleOptions. All properties within this type are optional, allowing for flexible configuration of histogram series.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: HistogramSeriesPartialOptions

Represents histogram series options where all properties are optional.
Inherits from: SeriesPartialOptions < HistogramStyleOptions
```

----------------------------------------

TITLE: Deep Partial Utility
DESCRIPTION: A utility type that recursively makes all properties of a type optional.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/TickMarkWeightValue

LANGUAGE: APIDOC
CODE:
```
DeepPartial<T>:
  T extends object ? {
    [P in keyof T]?: DeepPartial<T[P]>;
  } : T
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Defines the style options for a histogram series in Lightweight Charts. It includes properties for column color and the base level of the histogram columns.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  color: string
    Column color.
    Default Value: '#26a69a'
  base: number
    Initial level of histogram columns.
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Defines extended time scale options for time-based horizontal scales in Lightweight Charts. It inherits properties from HorzScaleOptions and includes specific settings for time scales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/TimeScaleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions

Extended time scale options for time-based horizontal scale

Extends:
  * `HorzScaleOptions`

Properties:

rightOffset:
> **rightOffset** : `number`
> The margin space in bars from the right side of the chart.
> Default Value: `0`
> Inherited from: `HorzScaleOptions.rightOffset`

barSpacing:
> **barSpacing** : `number`
> The space between bars in pixels.
> Default Value: `6`
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/LogicalRange

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: TimeChartOptions Interface Documentation
DESCRIPTION: Documentation for the TimeChartOptions interface, containing options specific to time-based charts.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AreaData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeChartOptions

Contains options specific to time-based charts.
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Types
DESCRIPTION: Defines types related to time representation, logical ranges, and event handlers for time and logical range changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Time:
  Represents a point in time.

TimeFormatterFn:
  A function type for formatting time values.

TimePointIndex:
  An index representing a point in time.

LogicalRange:
  Represents a range of logical values.

LogicalRangeChangeEventHandler:
  An event handler for logical range changes.

TimeRangeChangeEventHandler:
  An event handler for time range changes.
```

----------------------------------------

TITLE: Series Options Type Aliases
DESCRIPTION: Documentation for various type aliases related to series options, including AreaSeriesOptions, BarSeriesOptions, CandlestickSeriesOptions, HistogramSeriesOptions, and their partial counterparts. These define the configurable properties for different chart series types.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Time

LANGUAGE: APIDOC
CODE:
```
AreaSeriesOptions:
  Options for configuring an Area Series.
  Includes properties like `topColor`, `bottomColor`, `lineColor`, `lineWidth`, etc.

AreaSeriesPartialOptions:
  Partial options for configuring an Area Series. Allows for overriding specific properties.

BarSeriesOptions:
  Options for configuring a Bar Series.
  Includes properties like `upColor`, `downColor`, `borderVisible`, `wickVisible`, etc.

BarSeriesPartialOptions:
  Partial options for configuring a Bar Series.

CandlestickSeriesOptions:
  Options for configuring a Candlestick Series.
  Includes properties like `upColor`, `downColor`, `borderVisible`, `wickVisible`, etc.

CandlestickSeriesPartialOptions:
  Partial options for configuring a Candlestick Series.

HistogramSeriesOptions:
  Options for configuring a Histogram Series.
  Includes properties like `color`, `base`, etc.

HistogramSeriesPartialOptions:
  Partial options for configuring a Histogram Series.
```

----------------------------------------

TITLE: Custom Series Partial Options
DESCRIPTION: A partial version of CustomSeriesOptions, allowing for optional properties to be updated.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Background

LANGUAGE: APIDOC
CODE:
```
CustomSeriesPartialOptions:
  // Partial options for custom series
  // Allows updating only specific properties
```

----------------------------------------

TITLE: Lightweight Charts Time and Range Types
DESCRIPTION: Defines types related to time representation, logical ranges, and event handlers for time and logical range changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Time:
  Represents a point in time.

TimeFormatterFn:
  A function type for formatting time values.

TimePointIndex:
  An index representing a point in time.

LogicalRange:
  Represents a range of logical values.

LogicalRangeChangeEventHandler:
  An event handler for logical range changes.

TimeRangeChangeEventHandler:
  An event handler for time range changes.
```

----------------------------------------

TITLE: SeriesMarkerBase Interface
DESCRIPTION: Base interface for all series markers, providing common properties like position and color.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/PriceLineOptions

LANGUAGE: APIDOC
CODE:
```
Interface: SeriesMarkerBase

Base interface for all series markers.

Properties:
  - time: Time
    The time of the marker.
  - position: 'top' | 'bottom'
    The position of the marker relative to the price level.
```

----------------------------------------

TITLE: CandlestickStyleOptions Interface
DESCRIPTION: Defines the style properties for candlestick series in Lightweight Charts. It includes options for colors of rising and falling candles, and visibility of wicks and borders.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/CandlestickStyleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: CandlestickStyleOptions

Represents style options for a candlestick series.

Properties:
  upColor: string
    Color of rising candles.
    Default Value: '#26a69a'

  downColor: string
    Color of falling candles.
    Default Value: '#ef5350'

  wickVisible: boolean
    Enable high and low prices candle wicks.
    Default Value: true

  borderVisible: boolean
    Enable candle borders.
    Default Value: true
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SeriesMarkerPosition

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: Data Changed Handler
DESCRIPTION: Defines the signature for a handler function that is called when data in a series changes.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/HistogramSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
Type alias: DataChangedHandler()

Handler for data changed events.

Signature:
  (scope: DataChangedScope) => void

Parameters:
  - scope: DataChangedScope
    Information about the data change.
```

----------------------------------------

TITLE: Lightweight Charts Series Markers and Types
DESCRIPTION: Defines types for series markers, their positions, shapes, and the general series type.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/SizeChangeEventHandler

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  // Represents a marker on a series

SeriesMarkerPosition:
  // Enum or type for the position of a series marker

SeriesMarkerShape:
  // Enum or type for the shape of a series marker

SeriesType:
  // Enum or type for the type of series (e.g., 'Line', 'Area', 'Histogram', 'Candlestick')
```

----------------------------------------

TITLE: AxisDoubleClickOptions Interface
DESCRIPTION: Defines options for how the time and price axes of Lightweight Charts react to a double-click event. This interface allows customization of the chart's interactive behavior on double clicks.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/AxisDoubleClickOptions

LANGUAGE: APIDOC
CODE:
```
Interface: AxisDoubleClickOptions

Represents options for how the time and price axes react to mouse double click.

Properties:
  (No specific properties are detailed in the provided text, but the interface generally controls double-click behavior for axes.)
```

----------------------------------------

TITLE: Lightweight Charts Series Options
DESCRIPTION: Defines the options for different series types like Histogram and Line, including partial options for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/BaselineSeriesOptions

LANGUAGE: APIDOC
CODE:
```
HistogramSeriesOptions:
  A set of options for a histogram series.

HistogramSeriesPartialOptions:
  A set of partial options for a histogram series, allowing for incremental updates.

LineSeriesOptions:
  A set of options for a line series.

LineSeriesPartialOptions:
  A set of partial options for a line series, allowing for incremental updates.

SeriesOptions:
  A base type for all series options.

SeriesPartialOptions:
  A base type for partial series options, allowing for incremental updates.
```

----------------------------------------

TITLE: TimeScalePoint Interface
DESCRIPTION: Represents a point on the time scale.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScalePoint

Represents a point on the time scale.
```

----------------------------------------

TITLE: ISeriesPrimitiveAxisView Interface
DESCRIPTION: The ISeriesPrimitiveAxisView interface is used to define views for drawing labels on the price and time axes. These views are responsible for providing the content to be displayed on the respective scales.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/plugins/series-primitives

LANGUAGE: javascript
CODE:
```
interface ISeriesPrimitiveAxisView {
  // Methods for drawing labels on axes would be defined here
}
```

----------------------------------------

TITLE: Lightweight Charts 4.0 Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 4.0, covering options for price scales, formatting, series markers, and time handling. These aliases define the structure and types for chart configurations and data.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/CandlestickSeriesOptions

LANGUAGE: APIDOC
CODE:
```
OverlayPriceScaleOptions
PriceFormat
PriceFormatterFn
SeriesMarkerPosition
SeriesMarkerShape
SeriesOptions
SeriesPartialOptions
SeriesType
SizeChangeEventHandler
TickMarkFormatter
Time
TimeFormatterFn
TimeRange
TimeRangeChangeEventHandler
UTCTimestamp
VertAlign
VisiblePriceScaleOptions
```

----------------------------------------

TITLE: Lightweight Charts Next API Type Aliases, Variables, and Functions
DESCRIPTION: This section references type aliases, variables, and functions within the Lightweight Charts Next API, with a focus on HistogramStyleOptions.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/HistogramStyleOptions

LANGUAGE: APIDOC
CODE:
```
Type Aliases
Variables
Functions
```

----------------------------------------

TITLE: Lightweight Charts 4.0 API Type Aliases
DESCRIPTION: This section lists various type aliases available in Lightweight Charts version 4.0. These include options for price scales, formatting, series markers, and time-related configurations.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/type-aliases/HistogramSeriesOptions

LANGUAGE: APIDOC
CODE:
```
OverlayPriceScaleOptions
PriceFormat
PriceFormatterFn
SeriesMarkerPosition
SeriesMarkerShape
SeriesOptions
SeriesPartialOptions
SeriesType
SizeChangeEventHandler
TickMarkFormatter
Time
TimeFormatterFn
TimeRange
TimeRangeChangeEventHandler
UTCTimestamp
VertAlign
VisiblePriceScaleOptions
```

----------------------------------------

TITLE: API: Get Chart Data and Markers
DESCRIPTION: Provides methods to retrieve chart data and markers. Includes `ISeriesApi.markers` and `ISeriesApi.dataByIndex`. Time types in the public API have been updated to `Time`.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/release-notes

LANGUAGE: typescript
CODE:
```
interface ISeriesApi {
  markers(): 
  dataByIndex(index: number): 
}

type Time = 

// Example usage:
// const markers = seriesApi.markers();
// const data = seriesApi.dataByIndex(5);
```

----------------------------------------

TITLE: HistogramStyleOptions Interface
DESCRIPTION: Options for styling histogram series, including base color and histogram colors.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/interfaces/OhlcData

LANGUAGE: APIDOC
CODE:
```
HistogramStyleOptions:
  base?: number
  color?: Colord
  priceLineStyle?: LineStyle
  priceLineColor?: Colord
  priceLineWidth?: LineWidth
```

----------------------------------------

TITLE: Lightweight Charts API Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts API. These include options for different series types (Area, Bar, Candlestick, Baseline, Histogram), data item structures, coordinate systems, and utility types like DeepPartial.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/TimePointIndex

LANGUAGE: typescript
CODE:
```
/**
 * Options for an Area Series.
 */
interface AreaSeriesOptions {
  // ... properties for area series options
}

/**
 * Partial options for an Area Series, allowing for optional overrides.
 */
interface AreaSeriesPartialOptions {
  // ... properties for partial area series options
}

/**
 * Represents a point in time, typically a Unix timestamp in milliseconds.
 */
type TimePointIndex = number;

/**
 * Options for a Bar Series.
 */
interface BarSeriesOptions {
  // ... properties for bar series options
}

/**
 * Partial options for a Bar Series.
 */
interface BarSeriesPartialOptions {
  // ... properties for partial bar series options
}

/**
 * Options for a Candlestick Series.
 */
interface CandlestickSeriesOptions {
  // ... properties for candlestick series options
}

/**
 * Partial options for a Candlestick Series.
 */
interface CandlestickSeriesPartialOptions {
  // ... properties for partial candlestick series options
}

/**
 * Options for a Baseline Series.
 */
interface BaselineSeriesOptions {
  // ... properties for baseline series options
}

/**
 * Partial options for a Baseline Series.
 */
interface BaselineSeriesPartialOptions {
  // ... properties for partial baseline series options
}

/**
 * Options for a Histogram Series.
 */
interface HistogramSeriesOptions {
  // ... properties for histogram series options
}

/**
 * Partial options for a Histogram Series.
 */
interface HistogramSeriesPartialOptions {
  // ... properties for partial histogram series options
}

/**
 * Represents a single data item in a series.
 */
interface DataItem {
  time: TimePointIndex;
  value: number;
  // ... other potential properties
}

/**
 * A utility type to make all properties of a type optional, recursively.
 */
type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * Represents a coordinate on the chart.
 */
type Coordinate = number;

/**
 * Options for creating a price line.
 */
interface CreatePriceLineOptions {
  price: number;
  color?: string;
  lineWidth?: number;
  // ... other properties
}

/**
 * Options for the main chart.
 */
interface ChartOptions {
  width: number;
  height: number;
  // ... other chart options
}

/**
 * Represents a price value for a bar.
 */
type BarPrice = number;

/**
 * Defines the structure for custom series options.
 */
interface CustomSeriesOptions {
  // ... properties for custom series options
}

/**
 * Defines partial options for custom series.
 */
interface CustomSeriesPartialOptions {
  // ... properties for partial custom series options
}

/**
 * Defines the values for price plots in a custom series.
 */
interface CustomSeriesPricePlotValues {
  [key: string]: number;
}

/**
 * Handler for data changes.
 */
type DataChangedHandler = (scope: DataChangedScope) => void;

/**
 * Scope of data changes.
 */
interface DataChangedScope {
  // ... properties defining the scope of data changes
}

/**
 * Provider for autoscale information.
 */
interface AutoscaleInfoProvider {
  -readonly [key: string]: unknown;
  updateAllViews(): void;
}

/**
 * Represents a background color or gradient.
 */
interface Background {
  color: string;
}

/**
 * Defines horizontal alignment.
 */
export type HorzAlign = 'left' | 'right' | 'center';

/**
 * Converts horizontal scale items to internal objects.
 */
interface HorzScaleItemConverterToInternalObj {
  // ... properties for conversion
}

/**
 * Interface for a primitive drawn on a series.
 */
interface ISeriesPrimitive {
  // ... methods and properties for series primitives
}

```

----------------------------------------

TITLE: Alignment and Series Type
DESCRIPTION: Defines horizontal alignment options and the types of series available.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/Nominal

LANGUAGE: APIDOC
CODE:
```
HorzAlign:
  'left' | 'center' | 'right'

SeriesType:
  'Area' | 'Line' | 'Bar' | 'Candlestick' | 'Histogram'
```

----------------------------------------

TITLE: IYieldCurveChartApi Interface Documentation
DESCRIPTION: Provides detailed documentation for the IYieldCurveChartApi interface, including its methods, inheritance, and parameters. This interface is crucial for interacting with yield curve charts in the Lightweight Charts library.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IYieldCurveChartApi

LANGUAGE: APIDOC
CODE:
```
Interface: IYieldCurveChartApi

The main interface of a single yield curve chart.

Extends:
  * Omit <IChartApiBase<number>, "addSeries">

Methods:

remove(): void
  Removes the chart object including all DOM elements. This is an irreversible operation, you cannot do anything with the chart after removing it.
  Returns: void
  Inherited from: Omit.remove

resize(width, height, forceRepaint?): void
  Sets fixed size of the chart. By default chart takes up 100% of its container.
  If chart has the autoSize option enabled, and the ResizeObserver is available then the width and height values will be ignored.
  Parameters:
    width: The new width of the chart.
    height: The new height of the chart.
    forceRepaint: Optional. Forces the chart to repaint after resizing.
```

----------------------------------------

TITLE: SingleValueData Interface
DESCRIPTION: Base interface for data points that have a single value, used by various chart types. Includes time and value.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/interfaces/HistogramData

LANGUAGE: APIDOC
CODE:
```
SingleValueData
  properties:
    time: Time
      The time of the data point.
    value: number
      The value of the data point.
```

----------------------------------------

TITLE: Lightweight Charts Series Marker Types
DESCRIPTION: Defines types for series markers, including their position and shape.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScaleItemConverterToInternalObj

LANGUAGE: APIDOC
CODE:
```
SeriesMarker:
  Represents a marker on a series.

SeriesMarkerPosition:
  Defines the position of a series marker.

SeriesMarkerShape:
  Defines the shape of a series marker.
```

----------------------------------------

TITLE: TimeScaleOptions Interface
DESCRIPTION: Extends HorzScaleOptions to provide comprehensive options for the time scale. This interface allows detailed control over how the time axis is displayed and behaves.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/interfaces/HorzScaleOptions

LANGUAGE: APIDOC
CODE:
```
Interface: TimeScaleOptions
Options for the time scale; the horizontal scale at the bottom of the chart that displays the time of data.

Extended by:
  * None

Properties:

rightOffset :
  > number
The margin space in bars from the right side of the chart.
Default Value: `0`

barSpacing :
  > number
The space between bars in pixels.
Default Value: `6`

minBarSpacing :
  > number
The minimum space between bars in pixels.
Default Value: `0.5`
```

----------------------------------------

TITLE: Lightweight Charts Event Handling and Utilities
DESCRIPTION: Documents types for handling various chart events, such as size changes and logical range updates, along with utility types for formatting and data representation.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/PriceFormat

LANGUAGE: APIDOC
CODE:
```
Logical:
  // Represents a logical index in the chart

LogicalRange:
  // Represents a range of logical indices

LogicalRangeChangeEventHandler:
  // Handler for logical range change events

MouseEventHandler:
  // Handler for mouse events

Mutable:
  // Utility type indicating a mutable property

Nominal:
  // Utility type for nominal values

PercentageFormatterFn:
  // Function type for formatting percentages

PriceFormat:
  // Defines the format for prices

PriceFormatterFn:
  // Function type for formatting prices

PriceToCoordinateConverter:
  // Function type for converting price to coordinate

SizeChangeEventHandler:
  // Handler for size change events

TickMarkFormatter:
  // Function type for formatting tick marks
```

----------------------------------------

TITLE: Data Changed Handler
DESCRIPTION: A function signature for handling data changes within a series. This callback is invoked when data is added, removed, or updated.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UpDownMarkersSupportedSeriesTypes

LANGUAGE: APIDOC
CODE:
```
DataChangedHandler:
  (scope: DataChangedScope) => void
  // scope: Information about the data change.
```

----------------------------------------

TITLE: Candlestick Series Partial Options
DESCRIPTION: Defines partial options for a Candlestick Series, allowing for incremental updates.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.2/api/type-aliases/DataItem

LANGUAGE: APIDOC
CODE:
```
Type alias: CandlestickSeriesPartialOptions

Represents partial options for a Candlestick Series.

Properties:
- color?: string - The color of the wick and border for bullish candles.
- upColor?: string - The color of the wick and border for bullish candles.
- downColor?: string - The color of the wick and border for bearish candles.
- borderVisible?: boolean - Whether to show the candle border.
- wickVisible?: boolean - Whether to show the candle wick.
- barWidth?: number - The width of the candles.

Example:
{
  upColor: '#00ff00',
  downColor: '#ff0000'
}
```

----------------------------------------

TITLE: Lightweight Charts Type Aliases
DESCRIPTION: This section details various type aliases used within the Lightweight Charts library. These include definitions for series options (like HistogramSeriesOptions, LineSeriesOptions), formatting functions (PercentageFormatterFn, PriceFormatterFn), event handlers (MouseEventHandler, SizeChangeEventHandler), and internal data structures for scale items and primitives.

SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/LineSeriesPartialOptions

LANGUAGE: APIDOC
CODE:
```
GreenComponent:
  Represents a component that is green.

HistogramSeriesOptions:
  Options for configuring a histogram series.

HistogramSeriesPartialOptions:
  Partial options for configuring a histogram series.

HorzAlign:
  Defines horizontal alignment options.

HorzScaleItemConverterToInternalObj:
  Converter function for horizontal scale items to internal objects.

HorzScalePriceItem:
  Represents an item on the horizontal price scale.

IImageWatermarkPluginApi:
  API for image watermark plugins.

IPanePrimitive:
  Interface for primitives within a chart pane.

ISeriesPrimitive:
  Interface for series primitives.

ITextWatermarkPluginApi:
  API for text watermark plugins.

InternalHorzScaleItem:
  Internal representation of a horizontal scale item.

InternalHorzScaleItemKey:
  Key for internal horizontal scale items.

LineSeriesOptions:
  Options for configuring a line series.

LineSeriesPartialOptions:
  Partial options for configuring a line series.

LineWidth:
  Defines the width of a line.

Logical:
  Represents a logical index.

LogicalRange:
  Defines a range of logical indices.

LogicalRangeChangeEventHandler:
  Handler for logical range change events.

MouseEventHandler:
  Handler for mouse events.

Mutable:
  Indicates a mutable type.

Nominal:
  Represents a nominal value.

OverlayPriceScaleOptions:
  Options for an overlay price scale.

PercentageFormatterFn:
  Function type for formatting percentages.

PriceFormat:
  Defines the format for prices.

PriceFormatterFn:
  Function type for formatting prices.

PriceToCoordinateConverter:
  Converter function from price to coordinate.

PrimitiveHasApplyOptions:
  Indicates if a primitive has apply options.

PrimitivePaneViewZOrder:
  Z-order for primitive rendering in a pane view.

RedComponent:
  Represents a component that is red.

Rgba:
  Represents a color in RGBA format.

SeriesMarker:
  Represents a marker on a series.

SeriesMarkerBarPosition:
  Position of a marker relative to a bar.

SeriesMarkerPosition:
  General position of a marker.

SeriesMarkerPricePosition:
  Position of a marker relative to a price.

SeriesMarkerShape:
  Shape of a series marker.

SeriesMarkerZOrder:
  Z-order for series markers.

SeriesOptions:
  General options for any series type.

SeriesPartialOptions:
  Partial options for any series type.

SeriesType:
  Defines the type of a series (e.g., 'Line', 'Histogram').

SizeChangeEventHandler:
  Handler for size change events.
```

========================
QUESTIONS AND ANSWERS
========================
TOPIC: Lightweight Charts API Reference
Q: What are some examples of series options available in the Lightweight Charts API?
A: The Lightweight Charts API provides options for various series types, including `AreaSeriesOptions`, `BarSeriesOptions`, `BaselineSeriesOptions`, and `CandlestickSeriesOptions`. There are also partial options available for these series types.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/UTCTimestamp

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What does the ITimeScaleApi interface in Lightweight Charts manage?
A: The ITimeScaleApi interface in Lightweight Charts is used to manage the time scale of the chart. This includes controlling how time is displayed, zoomed, and scrolled, enabling users to navigate through historical data.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/IChartApi

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What does the HandleScrollOptions interface control in Lightweight Charts?
A: The HandleScrollOptions interface in Lightweight Charts governs the user's ability to scroll through the chart's data. It allows for enabling or disabling the scroll behavior, which is essential for navigating through historical data.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/interfaces/IRange

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What are some examples of series options available in the Lightweight Charts API?
A: The API Reference details options for AreaSeriesOptions, BarSeriesOptions, BaselineSeriesOptions, and CandlestickSeriesOptions. It also includes partial options for these series types, allowing for more flexible configuration.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/next/api/type-aliases/InternalHorzScaleItem

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: Which versions of Lightweight Charts are accessible through the provided links?
A: The documentation provides access to multiple versions of Lightweight Charts, including 5.0, 4.2, 4.1, 4.0, 3.8, and 3.7.0, allowing users to refer to specific historical or current API details.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/TickMarkWeightValue

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What are some examples of series options available in the Lightweight Charts API?
A: The Lightweight Charts API provides options for various series types, including AreaSeriesOptions, BarSeriesOptions, CandlestickSeriesOptions, and HistogramSeriesOptions. There are also partial options available for each series type, allowing for more flexible configuration.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/IPanePrimitive

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What are some examples of series options documented in the Lightweight Charts API?
A: The Lightweight Charts API documents options for various series types, including AreaSeriesOptions, BarSeriesOptions, CandlestickSeriesOptions, and HistogramSeriesOptions. It also provides partial options for these series, allowing for incremental updates.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/HorzScalePriceItem

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: Which version of the Lightweight Charts API is currently being referenced?
A: The documentation currently references version 4.0 of the Lightweight Charts API. Links to other versions, including 'next', '5.0', '4.2', '4.1', '4.0', '3.8', and '3.7.0', are also provided for compatibility and historical reference.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.0/api/interfaces/BaseValuePrice

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What are some examples of series options available in the Lightweight Charts API?
A: The Lightweight Charts API provides options for AreaSeries, BarSeries, BaselineSeries, CandlestickSeries, and HistogramSeries. These options allow for customization of how each series type is displayed and behaves on the chart.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/Time

----------------------------------------

TOPIC: Lightweight Charts API Reference
Q: What kind of data can be represented by the DataItem type in Lightweight Charts?
A: The DataItem type in Lightweight Charts is used to represent a single data point for a series. It typically includes properties like time, and price values (open, high, low, close) depending on the series type, enabling the display of historical or real-time data on the chart.


SOURCE: https://tradingview.github.io/lightweight-charts/docs/4.1/api/type-aliases/Nominal