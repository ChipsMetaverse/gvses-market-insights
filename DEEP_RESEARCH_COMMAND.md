# Deep Research Command - Ready to Execute

## After Restarting Cursor, Run This:

```
Research comprehensive pattern recognition implementation for trading platform:

CONTEXT: React+TypeScript frontend (TradingView Lightweight Charts), Python FastAPI backend, currently returns empty pattern arrays.

CURRENT IMPLEMENTATION:
- File: backend/pattern_detection.py (PatternDetector class)
- Problem: 50 candles lookback, 85%+ confidence thresholds, perfect pattern matching
- Result: Always returns {"detected": [], "total": 0}
- Tech: yfinance + Alpaca API data, async Python, 12 patterns in patterns.json

SPECIFIC RESEARCH NEEDS:

1. ALGORITHMS: Exact mathematical formulas for candlestick patterns (engulfing, doji, hammer, morning/evening star, three white soldiers) and chart patterns (head-shoulders, triangles, double tops/bottoms, flags). Include body-to-range ratios, wick-to-body ratios, price level tolerances (±1%, ±2%?), minimum candle counts.

2. CONFIDENCE SCORING: Dynamic confidence formula. Example: confidence = (pattern_quality * 0.30 + volume_confirmation * 0.25 + trend_alignment * 0.20 + timeframe_confluence * 0.15 + historical_accuracy * 0.10). What weights do TradingView/MetaTrader/ThinkorSwim use? Minimum confidence thresholds (60%, 70%?)?

3. HISTORICAL DATA: Optimal lookback periods per pattern (100, 200, 500 candles?). How much data for reliable detection? Performance vs accuracy tradeoffs.

4. MULTI-TIMEFRAME: Confluence scoring across 1D, 1W, 1M timeframes. How to weight each? Handle conflicts? Parallel detection patterns. Confluence score 0-10 algorithm.

5. TRADINGVIEW CHARTS INTEGRATION: How to draw patterns on TradingView Lightweight Charts (TypeScript). API for trendlines, candle highlights, markers. chart_metadata structure specification. Performance for real-time overlay.

6. UX FOR 4 PERSONAS:
   - Beginner: Educational tooltips, plain English, confidence as "Strong/Moderate/Weak"
   - Intermediate: Trading plans (entry/target/stop), historical win rates, R:R ratios
   - Advanced: Multi-timeframe matrix, backtesting, API export, custom patterns
   - Seasonal: Session persistence, "welcome back" summaries, terminology refresh

7. CODE EXAMPLES: Python pattern detection with tolerance (body2 >= body1 * 0.85 instead of 1.0), confidence calculation algorithm, multi-timeframe async detection, TypeScript chart drawing primitives.

8. PERFORMANCE TRACKING: Database schema for pattern outcomes, win rate calculation, Sharpe ratio per pattern, storage strategies.

9. BENCHMARKS: TradingView/ThinkorSwim/MetaTrader comparison. Detection latency (<500ms?), watchlist scanner scale (how many symbols?), real-time vs batch detection.

10. IMPLEMENTATION PRIORITY: Quick fixes for empty arrays (increase candles to 200, lower confidence to 65%, allow 85% pattern match tolerance) vs long-term improvements (ML-based confidence, automated backtesting, real-time scanner).

DELIVERABLES NEEDED:
- Exact Python code for pattern detection functions (10+ patterns)
- Confidence scoring formula with specific weights
- TradingView chart integration TypeScript examples
- Multi-timeframe detection implementation
- UX mockups for 4 trader types
- Performance optimization strategies
- Benchmark data from professional platforms

FORMAT: Comprehensive technical report with code examples, mathematical formulas, data-backed thresholds, implementation guides, and step-by-step integration path from research to production deployment on Fly.io.
```

## Command to Execute in Cursor:

After restart, use the Deep Research MCP tool with the above query.

