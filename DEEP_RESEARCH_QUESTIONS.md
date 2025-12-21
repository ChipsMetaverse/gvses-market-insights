# Deep Research Questions: Adaptive Trendline Detection
**Date**: December 1, 2025
**Context**: Solving inconsistent trendline detection across 12 timeframes

---

# TECHNICAL CONTEXT FOR RESEARCH AGENT

## Current System Architecture

### Backend Stack
- **Language**: Python 3.11
- **Framework**: FastAPI (async/await)
- **Libraries**: NumPy 1.26.0, no pandas, no scikit-learn, no TA-Lib
- **Constraints**: Keep dependencies minimal, production must be fast (<500ms)

### Existing Codebase Structure

**File**: `backend/pattern_detection.py` (Main orchestrator)
- Imports: `MTFPivotDetector`, `TrendlineBuilder`, `KeyLevelsGenerator`
- 3-Phase Pipeline:
  1. Phase 1: Pivot detection via `MTFPivotDetector`
  2. Phase 2: Trendline building via `TrendlineBuilder` (touch-point maximization)
  3. Phase 3: Key levels via `KeyLevelsGenerator` (BL, SH, BTD, PDH, PDL)

**File**: `backend/pivot_detector_mtf.py`
- Class: `MTFPivotDetector`
- Method: `find_pivots_single_tf(high, low, timestamps)`
- Returns: `Tuple[List[PivotPoint], List[PivotPoint]]` (highs, lows)
- Current params:
  ```python
  left_bars = 2
  right_bars = 2
  min_spacing_bars = 15  # ❌ Fixed, causes 15m failure
  min_percent_move = 0.025  # ❌ Fixed 2.5%
  ```

**File**: `backend/trendline_builder.py`
- Class: `TrendlineBuilder`
- Methods:
  - `build_support_line(pivot_lows, all_lows, min_touches=3)`
  - `build_resistance_line(pivot_highs, all_highs, min_touches=3)`
- Strategy: Try all pairs of pivots, count touches, keep best
- Constraint: **Must have >= 3 touches** ❌ Fails on 15m with few pivots
- No linear regression, uses touch-point maximization

**File**: `backend/key_levels.py`
- Class: `KeyLevelsGenerator`
- Generates: BL (Buy Low), SH (Sell High), BTD (Buy The Dip), PDH/PDL (Previous Day High/Low)
- Method: `generate_all_levels(pivot_highs, pivot_lows, candles, daily_data)`
- Returns: Dictionary of level objects

### Data Flow
```
API Request (/api/pattern-detection?symbol=TSLA&interval=15m)
  ↓
mcp_server.py: Fetch historical candles from Alpaca
  ↓
PatternDetector.detect_mtf_patterns(candles, interval, daily_pdh_pdl)
  ↓
Phase 1: MTFPivotDetector.find_pivots_single_tf()
  → Returns pivot_highs[], pivot_lows[]
  ↓
Phase 2: TrendlineBuilder.build_support_line() / build_resistance_line()
  → Returns 0-2 trendline objects (if >= 3 touches)
  ↓
Phase 3: KeyLevelsGenerator.generate_all_levels()
  → Returns 4-6 key level objects
  ↓
Combine all → Return JSON: {"trendlines": [...], "patterns": [...]}
```

### Current Bug Behavior (15m interval)
```
Input: 109 bars (7 days of 15m data)
  ↓
Phase 1: Detects ~5-7 pivot highs, ~5-7 pivot lows
  (Too few due to min_spacing_bars=15, min_percent_move=2.5%)
  ↓
Phase 2: TrendlineBuilder tries all pairs
  → FAILS: Cannot find 3 pivots touching any line
  → Returns: None for support, None for resistance
  ↓
Phase 3: KeyLevelsGenerator
  → FAILS: Not enough pivots to generate BL/SH/BTD
  → Returns: Empty dict
  ↓
Final output: {"trendlines": [], "summary": {"trendlines_count": 0}}
```

### Working Behavior (1m interval)
```
Input: 212 bars (1 day of 1m data)
  ↓
Phase 1: Detects ~14 pivot highs, ~14 pivot lows
  (Enough pivots due to 212/15 = 14 possible with spacing)
  ↓
Phase 2: TrendlineBuilder finds lines with 3+ touches
  → Returns: support line (6 touches), resistance line (5 touches)
  ↓
Phase 3: KeyLevelsGenerator has enough pivots
  → Returns: BL, SH, BTD (61 MA), PDH, PDL
  ↓
Final output: {"trendlines": [6 objects], "summary": {"trendlines_count": 6}}
```

### Performance Requirements
- **Latency**: Must complete in <500ms (currently ~200-300ms)
- **No heavy ML**: No training, no GPU, pure algorithmic
- **Production**: Runs on Fly.io, limited CPU/memory
- **Caching**: Currently none, each request recalculates (could add caching if needed)

### Interval Specifications
The system supports 12 intervals:
```python
INTRADAY_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '2h', '4h']
DAILY_PLUS_INTERVALS = ['1d', '1Y', '2Y', '3Y', 'YTD', 'MAX']
```

Each interval has different bar counts:
- 1m: ~212 bars (1 trading day)
- 5m: ~44 bars (1 trading day)
- 15m: ~109 bars (7 trading days) ❌ BROKEN
- 30m: ~57 bars (7 trading days)
- 1h: ~30 bars (7 trading days)
- 2h-4h: ~15-7 bars (7 trading days)
- Daily+: ~271-1000+ bars (1-3 years)

### Frontend Display
- **Chart Library**: TradingView Lightweight Charts v5
- **Display Format**: Horizontal dotted lines drawn as price series
- **Color Coding**:
  - Support/Lower Trend: Cyan #00bcd4
  - Resistance/Upper Trend: Magenta #e91e63
  - BL (Buy Low): Green #4caf50
  - SH (Sell High): Red #f44336
  - BTD: Blue #2196f3
  - PDH/PDL: Orange #ff9800

### Constraints for Solution

**MUST preserve**:
1. Touch-point maximization (not linear regression)
2. 3-phase architecture (pivots → trendlines → key levels)
3. PDH/PDL only on intraday intervals
4. NumPy-only (no pandas/sklearn/TA-Lib)
5. <500ms response time
6. No breaking changes to API response format

**CAN modify**:
1. Pivot detection thresholds (min_spacing_bars, min_percent_move)
2. Touch requirements (min_touches)
3. Add new parameters/methods to existing classes
4. Add caching/memoization
5. Add new detection strategies alongside existing

**CANNOT do**:
1. Introduce heavy dependencies (scikit-learn, tensorflow, etc.)
2. Break backwards compatibility with frontend
3. Remove PDH/PDL deduplication fix (recently implemented)
4. Change API response schema
5. Require training data or ML models

---

## Core Philosophy Questions

### 1. Should We Use Thresholds At All?

**Question**: Are hard-coded thresholds fundamentally the wrong approach for multi-timeframe trendline detection?

**Sub-questions**:
- What do professional charting platforms (TradingView, ThinkorSwim, Bloomberg) do?
- Do they use fixed thresholds or statistical methods?
- Is there a threshold-free approach that works universally?

**Research needed**:
- Review TradingView Lightweight Charts documentation on trendline detection
- Study Pine Script's ta.pivothigh/ta.pivotlow implementation details
- Investigate if percentile-based methods (e.g., "top 20% of local maxima") would work better

---

## Statistical vs Rule-Based Approaches

### 2. Should Pivot Detection Be Statistical Instead of Rule-Based?

**Current approach** (Rule-based):
```python
min_spacing_bars = 15  # Fixed spacing
min_percent_move = 0.025  # Fixed 2.5% move
```

**Alternative approaches**:

**A) Standard Deviation Method**:
- Detect pivots that are N standard deviations from local mean
- Adaptive to volatility automatically
- Question: What N value? (1.5σ, 2σ, 2.5σ?)

**B) Percentile Method**:
- Find top/bottom X% of local extrema
- Always get proportional pivots regardless of bar count
- Question: What percentile? (80th/20th, 90th/10th?)

**C) ATR-Based (Average True Range)**:
- Use ATR for volatility-adjusted pivot detection
- Industry standard for volatility measurement
- Question: ATR multiplier? (1.5x, 2x, 3x ATR?)

**D) Z-Score Method**:
- Calculate Z-scores for each potential pivot
- Select peaks above threshold Z-score
- Question: Threshold Z-score value?

**Research needed**:
- What does quantitative finance literature recommend?
- Which method scales across micro (1m) to macro (1Y) timeframes?
- Performance benchmarks: accuracy vs computation cost?

---

### 3. Should Bar Spacing Be Absolute or Relative?

**Current**: `min_spacing_bars = 15` (absolute)

**Problem**:
- 15 bars in 1m = 15 minutes (good spacing)
- 15 bars in 1Y = 15 days (too wide!)
- 15 bars in 15m with 109 total = only 7 possible pivots (too strict!)

**Alternative A - Percentage of Total Bars**:
```python
min_spacing_bars = int(total_bars * 0.05)  # 5% of total data
```
- 1m (212 bars): 10 bar spacing
- 15m (109 bars): 5 bar spacing ✅ Fixes the issue
- 1Y (271 bars): 13 bar spacing

**Alternative B - Time-Based**:
```python
# Always maintain X hours/days of spacing regardless of interval
if interval == '1m': spacing = 60  # 1 hour
if interval == '15m': spacing = 4  # 1 hour
if interval == '1d': spacing = 5  # 1 week
```

**Alternative C - Adaptive to Volatility**:
```python
# More spacing in choppy markets, less in trending markets
spacing = base_spacing * (1 + choppiness_index)
```

**Research needed**:
- What maintains visual clarity across all timeframes?
- What preserves significant pivots while filtering noise?
- Is there academic research on optimal pivot spacing?

---

### 4. Should Minimum Touches Be Fixed or Adaptive?

**Current**: `min_touches = 3` (always require 3 pivot points)

**Problem**:
- 15m has too few pivots to find 3 touching a line
- Daily charts have hundreds of pivots, 3 touches is easy

**Alternative A - Reduce for Sparse Data**:
```python
if pivot_count < 10:
    min_touches = 2
else:
    min_touches = 3
```

**Alternative B - Proportional to Data**:
```python
min_touches = max(2, int(pivot_count * 0.1))  # 10% of pivots
```

**Alternative C - Remove Touch Requirement**:
- Use best-fit regression line through ALL pivots
- No "touch" requirement, just best statistical fit
- Question: Would this create too many false trendlines?

**Research needed**:
- What is the mathematical significance of 3 touches vs 2?
- Do technical analysts require 3 touches, or is that arbitrary?
- Would 2 touches + high R² (goodness of fit) be better than 3 touches?

---

## Time-Aware vs Time-Agnostic

### 5. Should Detection Be Time-Aware or Bar-Count-Only?

**Current approach**: Bar-count-only (ignores actual time)

**Problem**:
- 1m bar = 1 minute of time
- 1d bar = 1 day of time
- Same spacing (15 bars) = vastly different time periods

**Alternative - Time-Normalized**:
```python
# Define lookback in actual time, not bars
lookback_hours = 24 * 7  # 1 week
bars_to_use = calculate_bars_for_timespan(interval, lookback_hours)
```

**Question**:
- Should a "significant pivot" be defined by time (e.g., "highest point in 1 day") rather than bars?
- Does time-awareness prevent overfitting to recent micro-movements?

**Research needed**:
- How do professional traders think about pivots (time-based or bar-based)?
- Would time-normalization make 1m and 1d charts more comparable?

---

## Pattern Detection Fundamentals

### 6. What Is a "Significant" Trendline Across All Timeframes?

**Core question**: What makes a trendline meaningful regardless of interval?

**Possible definitions**:

**A) Statistical Significance**:
- Trendline with R² > 0.85 (strong correlation)
- P-value < 0.05 (statistically significant slope)

**B) Touch Density**:
- Multiple touches relative to line length
- E.g., "3 touches per 100 bars" maintains same touch density

**C) Visual Clarity**:
- Lines that human traders would draw
- Avoid clutter: max 5-7 lines on any chart
- Prioritize: strongest, longest, most-touched lines

**D) Predictive Power**:
- Lines that historically predicted bounces/breaks
- Backtest trendlines: did price respect them?

**Research needed**:
- What makes a trendline "actionable" for traders?
- Survey of technical analysis textbooks: how do they define valid trendlines?
- Can we validate against human-drawn trendlines (ground truth)?

---

### 7. Should We Differentiate Major vs Minor Trendlines?

**Current approach**: All trendlines treated equally

**Alternative - Tiered System**:

**Tier 1 - Major Trendlines**:
- Long duration (across 50%+ of visible chart)
- Many touches (5+)
- Always displayed

**Tier 2 - Intermediate**:
- Medium duration (20-50% of chart)
- 3-4 touches
- Displayed on hour+ timeframes

**Tier 3 - Minor**:
- Short duration (<20% of chart)
- 2-3 touches
- Only displayed on intraday charts (1m-15m)

**Question**:
- Would tiered system solve the "too many lines on 1m, too few on 15m" problem?
- Should tier thresholds be timeframe-dependent?

---

## Implementation Architecture

### 8. Single Algorithm vs Per-Timeframe Logic?

**Approach A - Universal Algorithm**:
```python
def detect_trendlines(data, interval):
    # Same algorithm for all intervals
    # Parameters auto-adjust based on interval
    return universal_detection(data, adapt_params(interval))
```

**Approach B - Interval-Specific Logic**:
```python
def detect_trendlines(data, interval):
    if interval in ['1m', '5m']:
        return intraday_detection(data)
    elif interval in ['15m', '30m', '1h']:
        return mid_range_detection(data)
    else:
        return daily_detection(data)
```

**Question**:
- Is one universal algorithm possible, or do timeframes require fundamentally different approaches?
- Would conditional logic create maintenance nightmare?

---

### 9. Should Detection Be Incremental or Full Recalculation?

**Current**: Full recalculation on every timeframe change

**Alternative - Cached Multi-Resolution**:
- Calculate pivots once on smallest interval (1m)
- Aggregate up to larger intervals (5m, 15m, 1h, etc.)
- Cache results for performance

**Question**:
- Would this ensure consistency (same pivots across timeframes)?
- Performance improvement worth the complexity?

---

## Testing & Validation

### 10. How Do We Define "Success" for the Fix?

**Metrics to measure**:

**A) Trendline Count Consistency**:
- All intervals should return 4-7 trendlines (not 0, not 20)
- Target: Every interval shows at least BL, SH, PDH, PDL (4 minimum)

**B) Visual Quality**:
- Lines should look "natural" to human traders
- No excessive clutter, no missing obvious levels

**C) Cross-Timeframe Agreement**:
- Major trendlines should appear across multiple timeframes
- E.g., resistance at $432 on 1m should also appear on 1h

**D) Performance**:
- Detection should complete in <500ms
- No timeout issues

**Question**:
- What is the minimum acceptable success criteria?
- How do we validate against "ground truth" (manual trader analysis)?

---

### 11. Should We Benchmark Against TradingView?

**Proposal**: Load same TSLA data in TradingView, manually count trendlines at each interval

**Questions**:
- Is TradingView the "gold standard" we should match?
- Or should we define our own approach that's superior?
- Can we extract TradingView's trendline detection logic (open source)?

---

## Implementation Priority

### 12. Which Fix Should We Implement First?

**Option A - Quick Fix** (Adaptive thresholds):
- Adjust `min_spacing_bars` and `min_percent_move` per interval
- Fastest implementation (30 minutes)
- May not be theoretically optimal

**Option B - Statistical Pivot Detection**:
- Replace rule-based with Z-score or percentile method
- More robust, no arbitrary thresholds
- Implementation time: 2-3 hours

**Option C - Complete Rewrite**:
- Time-normalized, multi-resolution, cached
- Theoretically best approach
- Implementation time: 1-2 days

**Question**:
- User needs it working NOW - which approach balances speed + correctness?
- Can we do quick fix now, better solution later?

---

## Research Sources Needed

### Academic/Industry
1. **"Technical Analysis of Stock Trends"** by Edwards & Magee - Chapter on trendlines
2. **"Evidence-Based Technical Analysis"** by David Aronson - Statistical validation
3. **Quantitative Finance journals** - Search for "automated trendline detection"
4. **TradingView Pine Script docs** - ta.pivothigh/ta.pivotlow implementation details

### Code References
5. **TA-Lib** (Technical Analysis Library) - How do they detect pivots?
6. **Backtrader** - Python algo trading framework, pivot detection
7. **TradingView Lightweight Charts** - Any built-in trendline detection?

### Empirical Testing
8. **Load TSLA in TradingView** - Manual count of auto-detected trendlines per interval
9. **Survey 10 professional traders** - How do YOU draw trendlines? What makes one valid?
10. **A/B test with users** - Show two approaches, which looks better?

---

## Decision Framework

To implement the correct solution, we need to answer in priority order:

### Critical (Must answer before coding):
1. **Statistical vs rule-based?** (Q2) - Determines entire architecture
2. **Relative vs absolute spacing?** (Q3) - Solves 15m immediately
3. **Time-aware vs bar-only?** (Q5) - Affects all intervals

### Important (Should answer before finalizing):
4. **What is "significant"?** (Q6) - Defines success criteria
5. **Tiered system?** (Q7) - May solve multiple problems at once
6. **Single vs multi-algorithm?** (Q8) - Architecture decision

### Nice to have (Can iterate later):
7. **Benchmark against TradingView?** (Q11) - Validation strategy
8. **Incremental detection?** (Q9) - Performance optimization

---

## Immediate Next Steps

Before writing ANY code, we should:

1. **Research TA-Lib's pivot detection** - 30 min
2. **Test TradingView on TSLA** - 15 min
3. **Review quantitative finance papers on trendline detection** - 1 hour
4. **Prototype 2-3 approaches** on same dataset - 2 hours
5. **Compare results visually** - Which looks right to a trader?

**Then** implement the winner.

---

## Hypothesis to Test

**Hypothesis**: A percentile-based approach with relative spacing will work across all timeframes:

```python
def adaptive_pivot_detection(data, interval):
    # Spacing: Always 5% of total bars
    spacing = max(3, int(len(data) * 0.05))

    # Pivots: Top/bottom 15% of local extrema
    pivots = find_percentile_extrema(data, percentile=85, spacing=spacing)

    # Trendlines: Best fit through any 2+ pivots with R² > 0.7
    trendlines = fit_regression_lines(pivots, min_r2=0.7, min_touches=2)

    # Return top 6 by strength (touch count * R² * line length)
    return sorted(trendlines, key=strength_score)[:6]
```

**This would**:
- ✅ Work on 15m (5% of 109 = 5 bar spacing, many pivots)
- ✅ Work on 1m (5% of 212 = 10 bar spacing, many pivots)
- ✅ Work on 1Y (5% of 271 = 13 bar spacing, many pivots)
- ✅ No arbitrary thresholds (2.5%, 15 bars, etc.)
- ✅ Always return same number of lines (~6)

**Question**: Is this the right approach, or should we research more first?
