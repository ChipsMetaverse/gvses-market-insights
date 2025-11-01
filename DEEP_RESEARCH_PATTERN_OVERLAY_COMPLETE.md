# Root Cause Analysis

- **Timestamp/Coordinate Mismatch (≈30%)** – If overlay times use the wrong unit or format, they lie off-screen. For example, TradingView’s Lightweight Charts expects a UNIX timestamp in **seconds** for intraday data, not milliseconds ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/UTCTimestamp#:~:text=Note%20that%20JavaScript%20Date%20APIs,expects%20a%20number%20of%20seconds)). Passing `Date.now()` (ms) without `/1000` means the overlay is plotted far outside the intended range. Timezone confusion or using a date string instead of a timestamp can likewise misplace the overlay. Always verify that the pattern’s `time` matches the chart’s expected format (e.g. cast to `UTCTimestamp` in TS ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/UTCTimestamp#:~:text=Note%20that%20JavaScript%20Date%20APIs,expects%20a%20number%20of%20seconds))).  
- **Viewport/Visible Range (≈25%)** – Overlays drawn outside the current time range will not appear. For example, Lightweight Charts had known bugs where newly added markers or series outside the visible window were not rendered ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes#:~:text=,1294)). If your chart is `autoSize` or fixed to latest data, drawing an older/higher-time overlay won’t show unless you pan/refresh. Similarly, the 60-day filter logic itself might inadvertently omit valid overlay times (e.g. off-by-one day or incorrect timezone cut-off). Double-check that the pattern time lies within `chart.timeScale().getVisibleRange()`.  
- **Chart Initialization/Timing (≈20%)** – In React, ensure the chart is created on the actual DOM node and fully initialized before drawing. A common pitfall is using a ref object directly instead of its `.current` element. For instance, the correct pattern is `createChart(chartRef.current, {...})`, not `createChart(chartRef, ...)` ([stackoverflow.com](https://stackoverflow.com/questions/62419072/using-useeffect-and-useref-to-render-light-weight-chart-but-gets-error#:~:text=You%20just%20need%20to%20use,current)). If overlays are drawn in a `useEffect` before the chart is ready or before data is set, they will not render. Ensure your drawing logic runs **after** the chart is mounted and has data (e.g. check `if (!chart) return;` in the effect).  
- **Missing Update/Refresh Calls (≈10%)** – Some chart APIs require an explicit redraw or rescale after adding objects. For example, after calling `drawHorizontalLine` or `drawTrendline`, you may need to auto-fit or scroll the time scale to include the new elements. In Lightweight Charts you can call `chart.timeScale().fitContent()` or `chart.timeScale().scrollToRealTime()` after adding overlays to bring them into view ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes#:~:text=,1294)). Without this, a freshly drawn line may remain offscreen even if its time is within range.  
- **Styling/Z-Ordering (≈10%)** – Overlays may be present but invisible due to style or layering. For instance, if a line’s color or width is set incorrectly (e.g. fully transparent or zero width), it will not appear. Also, verify that you’re drawing on the correct panel/price scale – an overlay drawn in the volume subchart or a hidden pane won’t show on the main price chart. In many libs, horizontal and trend lines are drawn in the main (price) pane; for Lightweight Charts, note that v4.0.0 fixed “price lines” to render on top of all series ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes#:~:text=,470)). If using an older version or a different library, ensure your overlay layer isn’t being clipped or hidden behind other canvas layers.  
- **Logic/Filter Bugs (≈5%)** – The 60-day filter itself might mistakenly exclude patterns. For example, if you compare timestamps in seconds vs milliseconds or neglect UTC conversion, patterns near the boundary can be dropped. Test the filter logic with known dates to ensure nothing valid is being skipped.

# Debugging Checklist

1. **Verify Coordinates & Time Units:** Console-log the pattern times and compare to chart data. Convert the timestamp to a coordinate with the API – e.g.  
   ```ts
   const coord = chart.timeScale().timeToCoordinate(pattern.time as UTCTimestamp);
   console.log("Overlay time", pattern.time, "=> x =", coord);
   ```  
   If `timeToCoordinate` returns `null` or a negative value ([victorbrambati.github.io](https://victorbrambati.github.io/lightweight-charts/docs/next/api/interfaces/ITimeScaleApi#:~:text=Converts%20a%20time%20to%20local,x%20coordinate)), the time isn’t recognized by the chart. This immediately indicates a mismatch (wrong unit or out-of-range).  
2. **Inspect Visible Range:** Call `chart.timeScale().getVisibleRange()` (or equivalent) and ensure it includes the pattern time. In React, you can inspect this in a debug console or log. If the pattern time lies outside, either pan/zoom the chart or adjust your filter.  
3. **Enable Canvas Debugging (for Canvas-based charts):** Use Chrome DevTools’ Canvas Profiler (under DevTools Settings → Experiments → **Canvas Inspection** ([web.dev](https://web.dev/articles/canvas-inspection#:~:text=You%E2%80%99ll%20need%20to%20decide%20whether,see%20in%20the%20DevTools%20Timeline))). Capture a frame and step through the draw calls. This lets you see if/when your overlay drawing code executes and where on the canvas it lands.  
4. **Check Chart Instance & Lifecycle:** In React DevTools or console, confirm that your chart object is non-null before drawing overlays. Ensure `chartRef.current` (or your equivalent) is correctly passed to `createChart` ([stackoverflow.com](https://stackoverflow.com/questions/62419072/using-useeffect-and-useref-to-render-light-weight-chart-but-gets-error#:~:text=You%20just%20need%20to%20use,current)). If using hooks, double-check `useEffect` dependencies so that drawing only happens after the chart is initialized (e.g. `[chart, backendPatterns]`).  
5. **Toggle Filter & Data:** Temporarily disable the 60-day filter to test if patterns show. Or inject a test pattern with a timestamp that is definitely on-screen (e.g. now). If this appears, the issue likely lies in the filter logic or time conversion.  
6. **Review Styling:** Change overlay color/width in code to something highly visible (bright red, thick) to rule out “invisible color” issues. Also confirm there’s no CSS overlay (like an element covering the canvas). If using SVG layers, inspect with the DOM inspector to see if unseen elements exist.  
7. **Layer Ordering:** If using a library that supports layers or panes, verify you drew on the correct pane. In Lightweight Charts, `chart.addPlotLine` or `series.createPriceLine` draw on the price pane. If using TradingView Charting Library, ensure you call the correct API (e.g. `createShape` on the active chart) so the line is on the main series, not an indicator panel.  
8. **API Gotchas:** Check the chart API docs for any “gotchas.” For example, confirm you’re using the right method (`drawTrendline`, `addPriceLine`, etc.) and passing expected parameters. Logging success/failure of draw calls can catch silent errors.  
9. **Update Calls:** After drawing, explicitly trigger any refresh. For Lightweight Charts, call `chart.timeScale().fitContent()` or `chart.timeScale().scrollToRealTime()` and see if the overlays appear. For libraries with explicit refresh calls, invoke them.  
10. **Compare Reference Data:** Use a known-good example (for instance, a TradingView snippet or the library’s example code) and see how their coordinates/formats differ from yours.

# Code Fixes for Top Causes

Below are example fixes for three high-priority issues. Adjust to your specific chart library and code:

- **(1) Correct Timestamp Units:** Convert pattern times to the format the chart expects. In TypeScript with Lightweight Charts, cast to `UTCTimestamp` (seconds):  
  ```ts
  backendPatterns.forEach(pt => {
    // If backend provides seconds:
    const timestampSec: UTCTimestamp = pt.timestamp as UTCTimestamp;
    // If backend might send milliseconds instead, convert:
    // const timestampSec: UTCTimestamp = Math.floor(pt.timestamp / 1000) as UTCTimestamp;
    enhancedChartControl.drawHorizontalLine({
      time: timestampSec,
      price: pt.price,
      color: pt.direction === 'bull' ? 'green' : 'red',
    });
  });
  ```  
  Here we ensure `time` is in seconds ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/UTCTimestamp#:~:text=Note%20that%20JavaScript%20Date%20APIs,expects%20a%20number%20of%20seconds)). If your API expects milliseconds, multiply accordingly. The key is matching the chart’s time unit.  

- **(2) Ensure Overlay Enters Viewport:** After drawing lines, adjust the time scale so the overlays are visible. For example:  
  ```ts
  // After creating lines:
  enhancedChartControl.timeScale().fitContent(); 
  // or animate-scroll to real time if near the right edge:
  enhancedChartControl.timeScale().scrollToRealTime();
  ```  
  This forces the chart to re-compute its visible range. If using the TradingView Charting Library, you might call something like `widget.activeChart().scrollToRealTime()`. For lightweight-charts, `fitContent()` is often sufficient ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes#:~:text=,1294)).  

- **(3) React Initialization and Drawing Timing:** Ensure you initialize the chart with the actual DOM element and draw overlays in a safe effect. Example:  
  ```tsx
  const chartContainer = useRef<HTMLDivElement>(null);
  const [chart, setChart] = useState<IChartApi | null>(null);

  // Create chart on mount
  useEffect(() => {
    if (!chartContainer.current) return;
    const newChart = createChart(chartContainer.current, { width: 800, height: 600 });
    newChart.addCandlestickSeries(); // e.g. set up main series
    setChart(newChart);
  }, []);

  // Draw overlays when patterns update AND chart is ready
  useEffect(() => {
    if (!chart || !backendPatterns) return;
    // (Convert and draw, then fit time scale as above)
    backendPatterns.forEach(pt => {
      const ts: UTCTimestamp = Math.floor(pt.timestamp) as UTCTimestamp;
      chart.addLineSeries({...}).addPriceLine({
        price: pt.price,
        color: pt.color,
        axisLabelVisible: false,
        title: pt.name,
      });
    });
    chart.timeScale().fitContent();
  }, [chart, backendPatterns]);
  ```  
  Note the use of `chartContainer.current` when creating the chart (the React ref’s `.current`) ([stackoverflow.com](https://stackoverflow.com/questions/62419072/using-useeffect-and-useref-to-render-light-weight-chart-but-gets-error#:~:text=You%20just%20need%20to%20use,current)). Drawing is deferred until after the chart is set in state. Adjust the API calls (`addLineSeries`, `addPriceLine`) to match your library’s syntax.  

# Verification Test Procedures

- **Unit Tests for Timestamp Conversion:** Write tests that feed known timestamps to the drawing function and check the chart’s data. For example, simulate a pattern at time “1622505600” (Unix seconds) and assert that `chart.timeScale().getVisibleRange()` includes it after `fitContent()`.  
- **Console Inspection:** After invoking the fix, log `chart.timeScale().getVisibleRange()` and pattern times. Confirm that each overlay’s time lies within (or exactly at) this range. Also log `chart.timeScale().timeToCoordinate(pattern.time)`; it should be a finite number (not `null`).  
- **Visual Tests:** Add a dummy pattern exactly at the current time or at chart edges and manually verify it appears. You can use a distinctive style (color/label) for this test.  
- **Debug Tools:** Use the Chrome Canvas Profiler (as in Debugging step 3) to capture a frame after drawing. The canvas inspection should show the overlay drawing call with the correct coordinates. If it does, rendering is working.  
- **Filter Logic Test:** With filtering enabled, assert that patterns older than 60 days are omitted. Then temporarily disable filtering in code and ensure those patterns reappear. This checks your date-comparison logic.  
- **Responsive/Resize Test:** If the chart resizes or new data arrives, check that overlays persist. For example, add a new candle or change chart size after drawing lines and verify overlays are still visible or properly repositioned (no untimely re-draw bug).  
- **Regression Check:** Make sure unrelated chart features still work (no console errors, no blank screen). Sometimes a fix (like forcing fitContent) can cause performance issues or conflicts, so test common interactions (zoom, pan, crosshair).  

# Performance Optimization

- **Batch Overlay Operations:** If you draw many lines, do it in a single batch or loop without intermediate renders. Some libraries allow grouping updates to avoid repeated layout. For example, add all lines then call `fitContent()` once, rather than fitting after each line.  
- **Limit Overlays:** Only draw patterns that are within or near the visible range (your 60-day limit is a good start). Remove or disable overlays for old patterns. Excessive shapes slow down canvas/SVG. If patterns accumulate, periodically clear or reuse old overlays.  
- **Throttle Pattern Updates:** If patterns are detected in real time, debounce or throttle redrawing. Don’t update overlays on every data tick; maybe update once per N seconds or when the user stops panning.  
- **Use Lightweight Markers or Annotations:** If your library has a lightweight annotation API (like markers or symbols), prefer those over custom objects – they are often batched and optimized.  
- **Offscreen Computation:** Perform any heavy coordinate/time calculations outside of the render/UI thread (e.g. Web Worker) so the drawing thread isn’t blocked.  
- **Optimize Chart Options:** Disable animations or unnecessary features when updating overlays. For example, static lines don’t need transition effects. In Lightweight Charts you can disable crosshair or tooltip updates during overlay drawing if they interfere.  
- **Profiling:** Use browser performance tools to measure draw times. If overlay drawing is a bottleneck, consider simplifying the graphics (thinner lines, fewer labels) or clustering nearby patterns into a single annotation.

These steps will help ensure that pattern lines and trendlines reliably appear on the chart and that any missing overlays are systematically diagnosed and fixed. Ultimately, consistent time-unit handling ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/api/type-aliases/UTCTimestamp#:~:text=Note%20that%20JavaScript%20Date%20APIs,expects%20a%20number%20of%20seconds)) and ensuring overlays fall into the chart’s visible window ([tradingview.github.io](https://tradingview.github.io/lightweight-charts/docs/4.2/release-notes#:~:text=,1294)) ([victorbrambati.github.io](https://victorbrambati.github.io/lightweight-charts/docs/next/api/interfaces/ITimeScaleApi#:~:text=Converts%20a%20time%20to%20local,x%20coordinate)) are the most common keys to solving invisibility issues.
