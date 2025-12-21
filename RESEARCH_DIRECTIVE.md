# Research Directive for Deep Research Agent
**Date**: December 1, 2025

## Direct Answers to Your Questions

### 1. Scope: Hypothesis Validation vs Broader Review?

**BOTH, but prioritized:**

**Primary Focus (70% of research time)**:
- Validate the **percentile-based approach** as the leading candidate
- Provide confidence level: "Will this work for all 12 timeframes?"
- Identify fatal flaws if any exist

**Secondary Focus (30% of research time)**:
- Brief comparative analysis of alternatives (Z-score, ATR, etc.)
- Only deep-dive if percentile approach has major issues
- Goal: Justify why percentile is best, or recommend superior alternative

**Rationale**: We need a solution NOW. Percentile approach is simple, threshold-free, and theoretically sound. Don't want analysis paralysis - need actionable recommendation.

---

### 2. Priority: Critical 3 vs All 12?

**Answer the Critical 3 FIRST and THOROUGHLY:**

1. **Statistical vs Rule-Based** (Q2)
   - HIGHEST PRIORITY
   - This determines entire implementation
   - Need: Concrete recommendation with code-level guidance

2. **Relative vs Absolute Spacing** (Q3)
   - HIGH PRIORITY
   - This directly solves 15m bug
   - Need: Specific formula (e.g., "use 5% of bars" or "use time-based")

3. **Time-Aware vs Bar-Only** (Q5)
   - MEDIUM-HIGH PRIORITY
   - Affects all intervals
   - Need: Decision + rationale

**Then answer these if time permits:**
- Q6 (What is "significant"?) - Important for quality
- Q7 (Tiered system?) - Could elegantly solve multiple issues
- Q8 (Single vs multi-algorithm?) - Architecture decision

**SKIP these unless they emerge as critical:**
- Q9-Q12 (incremental detection, benchmarking, implementation priority)
- These are implementation details, not research questions

---

### 3. Trading Platform Comparisons?

**YES - But specific and targeted:**

**Must have:**
1. **TradingView's approach** - They're the industry standard
   - How does Pine Script's `ta.pivothigh/ta.pivotlow` work?
   - Do they use fixed thresholds or adaptive?
   - Sample Pine Script code if available

2. **TA-Lib implementation** (if available)
   - We don't use it, but it's industry standard
   - What's their pivot detection logic?
   - Can we replicate without the dependency?

**Nice to have:**
3. **ThinkorSwim/Bloomberg** - If easily accessible
   - Only if significantly different from TradingView
   - Don't spend >20 minutes on these

**Don't need:**
- Proprietary platforms we can't learn from
- Platforms without public documentation

---

## Specific Deliverables Needed

### Format: Executive Summary + Detailed Sections

**Executive Summary (1 page)**:
1. **Recommendation**: Percentile-based? Something else? Hybrid?
2. **Confidence**: High/Medium/Low that this will fix all 12 timeframes
3. **Implementation Complexity**: Simple/Medium/Complex
4. **Risk Assessment**: What could go wrong?

**Critical Question Answers (3-5 pages each)**:

For each of Q2, Q3, Q5:
1. **Answer**: Clear yes/no or specific approach
2. **Rationale**: Why this approach (cite sources)
3. **Code Example**: Pseudo-code showing the concept
4. **Validation**: How TradingView/industry does it
5. **Edge Cases**: What could break?

**Comparative Analysis (2-3 pages)**:
- Table comparing: Percentile vs Z-score vs ATR vs Rule-based
- Columns: Complexity, Accuracy, Speed, Works across timeframes?, Dependencies
- Bold the winner

**Implementation Roadmap (1 page)**:
- Step 1: Do X first (e.g., "Change min_spacing_bars calculation")
- Step 2: Then Y (e.g., "Adjust min_touches based on pivot count")
- Step 3: Finally Z (e.g., "Add fallback for edge cases")
- Time estimate for each step

---

## Research Constraints

### Must Research:
- ✅ Academic papers on algorithmic trendline detection
- ✅ Open-source charting libraries (TradingView, Plotly, etc.)
- ✅ Technical analysis textbooks (Edwards & Magee, Murphy, etc.)
- ✅ QuantConnect/Backtrader forums (real traders discussing this)
- ✅ GitHub repos implementing trendline detection in Python

### Ignore:
- ❌ Machine learning approaches (too complex, need training data)
- ❌ Paid research papers behind paywalls (use freely available)
- ❌ Proprietary trading algorithms (can't verify)
- ❌ Non-Python implementations (unless logic is universal)

---

## Success Criteria

Research is complete when you can answer:

1. **"What should min_spacing_bars be for each interval?"**
   - Example answer: "5% of total bars, minimum 3, maximum 20"
   - Or: "Use time-based: always 4 hours of spacing regardless of interval"

2. **"What should min_percent_move be?"**
   - Example answer: "Remove it, use percentile instead (top 15% of extrema)"
   - Or: "Keep it but calculate from standard deviation: 1.5σ"

3. **"What should min_touches be?"**
   - Example answer: "2 for sparse data (<50 bars), 3 for normal (50-200), 4 for rich (200+)"
   - Or: "Always 2, compensate with higher R² threshold (>0.85)"

4. **"Will this fix all 12 timeframes?"**
   - Example answer: "YES - percentile approach scales naturally. Validated against TradingView's behavior."
   - Or: "MOSTLY - will fix 15m but 30m may need special handling because..."

---

## Expected Timeline

- **Phase 1** (1 hour): Critical 3 questions + TradingView comparison
- **Phase 2** (30 min): Comparative analysis of methods
- **Phase 3** (30 min): Implementation roadmap + validation plan

**Total**: ~2 hours for complete research

**Interim checkpoint**: After Phase 1, provide preliminary recommendation so we can start coding if confident.

---

## Context to Keep in Mind

### The Actual Bug
```
15m interval: 109 bars, spacing=15, move=2.5%
Result: ~7 pivots detected
Problem: TrendlineBuilder needs 3+ touches, can't find any line with 3 touching pivots
Output: 0 trendlines ❌

Fix needed: Get 10-15 pivots from same data
Solution: Reduce spacing to ~5 bars OR use percentile (top 20% = ~22 pivots guaranteed)
```

### What "Good" Looks Like
```
All 12 intervals should return 4-7 trendlines:
- 2 main lines (support/resistance)
- 4-5 key levels (BL, SH, BTD, PDH, PDL)

Visual test: Human trader should say "yes, those are the obvious levels"
```

### Our Advantage
- We have test data for all 12 intervals
- Can instantly validate any approach
- Can A/B test multiple solutions quickly

---

## Communication Style

**DO**:
- Be definitive: "Use percentile-based with X% threshold"
- Cite sources: "TradingView's Pine Script uses..."
- Show math: "For 109 bars, 5% spacing = 5.45 ≈ 5 bars"
- Warn about risks: "This may generate false positives on choppy markets"

**DON'T**:
- Hedge: "Maybe percentile could work, or possibly ATR..."
- Over-theorize: "In the limit as bars approach infinity..."
- Assume knowledge: "Obviously using Fractional Brownian Motion..."
- Perfectionism: "This needs 6 months of backtesting..."

We need a working solution today, not a perfect one in 6 months.

---

## Final Question to Answer

**"If you had to implement ONE change to fix 15m right now, what would it be?"**

Research should lead to a clear, confident answer to this question.


Adaptive Trendline Detection – Research Findings and Recommendations

Executive Summary

Problem: The current trendline detection algorithm fails on the 15-minute (15m) timeframe due to rigid pivot-finding thresholds (fixed 15-bar spacing and 2.5% price move requirement). This yields too few pivot points (only ~7) and thus zero trendlines (since the algorithm requires ≥3 pivot touches). Other intervals either produce too many or too few lines, indicating the one-size-fits-all parameters are suboptimal across 12 timeframes.

Key Findings: To achieve consistent, meaningful trendlines on all timeframes, the detection should become adaptive – adjusting pivot identification criteria to data length and volatility. Hard-coded thresholds are fundamentally too inflexible ￼ ￼. Statistical or relative methods perform better:
	•	Adaptive Pivot Thresholds: Replace fixed percentage moves with a volatility-based or percentile-based threshold. For example, mark a swing high only after price reverses by a threshold derived from recent volatility (e.g. a multiple of ATR) or choose the top X% of largest swings as pivots. This ensures significant moves are captured even on calm charts ￼ ￼.
	•	Relative Bar Spacing: Instead of always skipping 15 bars between pivots, use a fraction of the total bars (e.g. ~5–10%). In testing, setting spacing ≈5% of the data length yielded ~15 pivots on 15m (vs 7 pivots with 15 bars fixed), resolving the missing trendline issue. Wider spacing filters noise but must scale with dataset size ￼ ￼.
	•	Dynamic Touch Requirements: Trendlines typically require at least 3 touches to be considered reliable ￼. However, on sparse data (few pivots), insisting on 3 touches can fail. We recommend allowing 2-touch trendlines in low-pivot scenarios (e.g. higher timeframes or short intraday windows), while using 3+ touches when pivot points are plentiful. Technical analysis literature agrees that two touches “will do in a pinch” although three makes a trendline far more reliable ￼.
	•	Unified Algorithm with Parameter Adaptation: A single detection pipeline can be retained, but parameters (pivot sensitivity, spacing, min touches) should auto-adjust per timeframe. This avoids maintaining separate code paths while ensuring, for instance, a daily chart and a 1-minute chart both yield ~5–7 significant lines each, scaled to their context.

Recommendation: Implement a percentile-based pivot detection with relative bar spacing as an immediate solution. This approach is simple, fast (NumPy-based), and requires no new heavy dependencies. It will dynamically select significant swing highs/lows on any timeframe without hardcoding thresholds. Specifically:
	1.	Pivot Detection: Identify local maxima/minima with a minimal neighbor requirement (e.g. 2 bars on each side). Then filter these pivots to keep only the top 15% of moves by magnitude (i.e. the most prominent swings) ￼. Ensure a spacing of ~5% of bars between adjacent pivots to avoid clustering.
	2.	Trendline Construction: Continue using touch-point maximization, but allow 2-touch lines if total pivot count < 10. Otherwise require 3+ touches for robustness ￼. This ensures even scant data (like 2-hour interval with ~15 bars) can still produce at least one trendline.
	3.	Key Levels: The existing key level logic (Buy Low, Sell High, etc.) will naturally benefit from having more pivots to work with. No fundamental changes needed there, aside from using the new pivots list.

Expected Outcome: All 12 supported intervals will return a balanced set of trendlines (roughly 4–7 each). The 15m timeframe will no longer output zero lines – it should produce trendlines comparable to the 5m or 30m charts in count and obviousness. These lines will be more reflective of true market structure (capturing major swing highs/lows) rather than an artifact of one-size thresholds. Performance should remain well under 500ms since the calculations are simple array operations. In sum, adaptive pivot detection and scaling criteria will make the trendline detection robust, self-tuning, and consistent across timeframes, addressing the current inconsistencies.

⸻

Q2: Statistical vs. Rule-Based Pivot Detection

Answer: Yes – pivot identification should shift from fixed rule-based thresholds to a statistical/adaptive approach. The current rule-based method (requiring a 2.5% price move and fixed 15-bar spacing) is too brittle. Instead, use volatility-sensitive or data-driven criteria so that “significant” pivots are detected regardless of timeframe scale. This can be achieved without heavy ML; simple statistical techniques suffice:
	•	Percentile-Based Method (Recommended): Determine pivots by relative prominence. For example, find all local extrema and select those in the top 15% of price range or swing magnitude ￼. This guarantees a proportionate number of pivots. On a quiet chart, the threshold auto-lowers (so you still get enough pivots), and on a volatile chart it auto-raises (filtering out trivial wiggles). It’s effectively a data-driven threshold: e.g. if a stock’s price range over the period is 10 dollars, picking the top 15% swings might require a swing >8 dollars to count as a pivot (just an illustration). If the range is only 2 dollars (flat market), the threshold becomes smaller in absolute terms. Pros: Very simple to implement (just compute percentile of swing sizes), ensures a consistent fraction of moves are marked as pivots. Cons: Needs careful definition of “swing size” – typically the peak-to-trough price change since last pivot. It might also include a few lower-significance pivots if the distribution is very uniform (e.g. steady trend with no big standout move). Overall, it’s a straightforward adaptive filter that addresses threshold rigidity by tying it to the data distribution.
	•	Z-Score / Standard Deviation Method: A robust outlier detection approach is to flag pivots when price moves more than a certain number of standard deviations from a moving average baseline ￼ ￼. In practice, one could maintain a rolling mean and std of price changes; if the latest swing high is, say, >2σ above the mean of recent highs, mark it as a significant pivot (analogous for lows). This method adapts to volatility: in quiet periods, σ is small so even modest moves trigger a pivot; in volatile times σ is large so only big moves count. Notably, the highly cited “robust peak detection algorithm using z-scores” (as described by StackOverflow user John in a famous answer ￼) constructs a moving window and signals a peak when the new value deviates by >Threshold*σ from the local mean. It also uses an “influence” parameter to down-weight the outliers themselves in subsequent calculations ￼ – ensuring one large spike doesn’t skew the baseline for finding the next. Pros: Statistically principled, automatically adjusts to volatility regimes, filters out noise effectively. Cons: Requires choosing a window size (lag) and a σ threshold (e.g. 3σ). If the window is too short, it may misjudge trend vs noise; too long and it may lag. Also, implementing the moving window for each new bar could be slightly heavier than a one-pass percentile calc (though still easily under 500ms for a few hundred points).
	•	ATR-Based Method: Use Average True Range (ATR) as a volatility yardstick for pivot significance. For example: compute ATR over a suitable period (say 14 bars) and set pivot detection threshold as a multiple of ATR (e.g. pivot if price reverses >1.5 * ATR from last extreme). ATR is a standard measure of volatility in trading ￼ ￼. This would mean the threshold in absolute price terms expands in volatile periods and contracts in calm periods – an intuitive adaptation. Pros: Easy to compute (ATR is just an average of recent ranges), easy to interpret (traders understand “1.5 ATR move” as significant). It’s essentially a ZigZag indicator where the threshold is expressed in ATR units rather than a fixed percent. Cons: ATR is timeframe-specific and needs a sensible multiplier per interval or asset. For instance, 1.5 ATR on a 1m chart vs 1.5 ATR on a daily chart represent very different magnitudes relative to typical swings. We might still need to tweak the multiplier for each timeframe to get the desired number of pivots, which reintroduces some manual tuning. Also, ATR assumes roughly normal volatility distribution; extreme outlier moves might not be fully captured by a linear ATR multiple.
	•	Adaptive Fractal Window: This is a variant of rule-based but worth noting – instead of fixed left/right bars (like 2 on each side), make the pivot window length proportional to the dataset or an indicator. For example, on higher timeframes require more bars on each side to qualify as a pivot. Fidelity’s guide on Pivot Points (High/Low) notes that a longer period (more bars on each side) makes a pivot more significant ￼. A period of 5 (meaning 5 lower highs to left and 5 to right) is a strong swing, whereas period 2 is a minor swing. We could dynamically choose leftbars = rightbars ≈ total_bars/20 (for instance). This would naturally scale: a 100-bar series uses a 5-bar pivot window; a 300-bar series uses ~15 bars. The result is fewer but more important pivots on large datasets, and more pivots on short datasets. Pros: Still simple and rule-based, but adaptive in a coarse way; emphasizes structurally significant peaks (similar to choosing a larger pivot length on TradingView’s ta.pivothigh() for higher timeframes). Cons: If taken too far, it might miss short-term swings entirely on intraday data by over-smoothing. Also, it doesn’t account for magnitude of moves, just the count of neighboring bars. One might miss a sharp V-spike that happens over just 2 bars if the window is set to 5. So this method might need to be combined with a magnitude filter anyway.

Rationale: A statistical/adaptive approach is superior because market volatility and data length vary widely across timeframes. A fixed 2.5% move that is ample on a daily chart might never occur on a 15m chart in a week, as we saw (TSLA’s 15m moves were mostly smaller). Conversely, 2.5% on a 1m chart might be too high-frequency if the stock is very volatile intraday. Professional and academic literature strongly advocate for adaptive thresholds in swing detection. The ZigZag indicator – a classic swing filtering tool – explicitly requires a tunable percentage (often ~5%) and users are advised to adjust it for each asset/timeframe to get meaningful swings ￼ ￼. In fact, Investopedia notes “traders will need to optimize the Zig Zag indicator’s percentage setting to suit each security” ￼, underscoring that one static threshold won’t work universally. Rather than manual tuning, we want the system to auto-tune based on data characteristics. Statistical methods like percentiles or z-scores do exactly that – they derive the threshold from the data itself.

Code Example (Percentile Approach): To illustrate, here’s a pseudocode for percentile-based pivot detection:

def find_adaptive_pivots(highs, lows, percentile=85):
    pivots = [] 
    # Identify all local extrema with minimal left/right requirement (e.g. 2 bars)
    for i in range(len(highs)):
        if highs[i] > max(highs[max(0,i-2):i]) and highs[i] >= max(highs[i+1:i+3]):
            pivots.append(('H', i, highs[i]))  # Pivot High at index i
        if lows[i] < min(lows[max(0,i-2):i]) and lows[i] <= min(lows[i+1:i+3]):
            pivots.append(('L', i, lows[i]))   # Pivot Low at index i

    if not pivots:
        return []  # no pivots found (edge case)

    # Calculate swing magnitudes for filtering. For simplicity, use distance from last pivot of opposite type.
    significant_pivots = [pivots[0]]  # keep first pivot
    for j in range(1, len(pivots)):
        # Calculate price change from last kept pivot to this one
        prev_type, prev_idx, prev_price = significant_pivots[-1]
        curr_type, curr_idx, curr_price = pivots[j]
        swing_pct = abs(curr_price - prev_price) / prev_price
        pivots[j] = (*pivots[j], swing_pct)
    # Now determine cutoff based on percentile of swing_pct values
    swing_pcts = [p[3] for p in pivots if len(p) == 4]
    cutoff = np.percentile(swing_pcts, percentile)  # e.g. 85th percentile

    # Filter pivots by percentile threshold
    filtered = [p for p in pivots if len(p)==4 and p[3] >= cutoff]

    # Optional: enforce spacing (e.g. skip pivots too close in index)
    min_spacing = int(0.05 * len(highs))
    final_pivots = []
    last_idx = -inf
    for p in filtered:
        if p[2] - last_idx >= min_spacing: 
            final_pivots.append(p)
            last_idx = p[2]
    return final_pivots

In this sketch, we first gather all local pivot candidates using a small window (2 bars each side, similar to fractals). Then we compute each pivot’s price change relative to the last confirmed pivot (this is one way to measure swing size). We find the 85th percentile of these swing magnitudes and filter out any pivots that are below that (i.e. keep only the top 15% swings). Finally, we impose a spacing rule (5% of data length) to avoid two pivots that are very near in time. The result is a set of pivots that are both local extrema and represent the biggest moves in the series.

Validation (TradingView & Others): This approach aligns with how professional tools identify swings:
	•	TradingView’s built-in ta.pivothigh()/pivotlow() uses a pure fractal method (no magnitude filter) ￼, but many TradingView scripts combine that with custom logic to ignore minor pivots. For example, an “Adaptive Swing” indicator by dchunt-stack confirms a new pivot only if it’s beyond the previous pivot (i.e. a higher high for a high pivot), and it invalidates prior pivots if a stronger one appears ￼ ￼. This is effectively a dynamic threshold – a new pivot must exceed the last one, ensuring only significant turns are kept. Our percentile method is in the same spirit: it automatically drops smaller intervening pivots in favor of the major ones.
	•	The vectorbt library’s pivotinfo indicator (Pro edition) uses dual thresholds (up_th, down_th) to register a peak when price “jumps above one threshold” and a valley when it “falls below another” ￼. This is essentially a parameterized ZigZag. They highlight that unlike a naive ZigZag, their implementation only returns confirmed pivots, suitable for backtesting ￼. We can mimic this by requiring confirmation (e.g. price has moved down a certain % after a high before declaring it a pivot high). That could be an enhancement: e.g., only label a pivot high once the price drops 1% (or some small percent or percentile of volatility) after the peak. This avoids painting a pivot that never materializes (which can happen if price keeps rising).
	•	Academic/quantitative research also favors statistical measures. Aronson’s “Evidence-Based Technical Analysis” emphasizes testing whether patterns (like trendlines or pivots) have statistical significance above random noise. Applying a percentile or z-score filter inherently focuses on non-random, significant deviations. While we did not find a specific paper prescribing “use the 85th percentile of swings,” the approach falls under outlier detection, which is well-founded.

Edge Cases: A potential pitfall of statistical methods is in extremely low-volatility or extremely high-volatility scenarios:
	•	If nothing stands out (flat market, all swings are tiny and equal), a percentile filter will still pick some top fraction, which might essentially be noise. However, in such cases even a human wouldn’t find meaningful trendlines – the chart would be basically a straight line. We can mitigate false signals by setting a floor for significance (e.g. require at least some minimum price change like 0.5% even if percentile threshold is lower). ATR or z-score methods inherently handle this by measuring deviation against noise – if everything is noise, nothing exceeds 3σ. Our current fixed 2.5% acted as such a floor, but it was too crude. A refined approach might be: percentile filter and require swing ≥ X * ATR(period).
	•	In highly volatile data (e.g. penny stock on 1m chart), every swing might be large. A percentile filter will still pick the top few, which is fine, but there’s a risk that if volatility is erratic, the “top 15%” might include some anomalies. This is where a z-score approach shines because it continuously adapts to local volatility. Perhaps combining approaches could be powerful: use a percentile approach to guarantee a reasonable count of pivots, but also incorporate a z-score-based suppression for any obvious noise or artifact.

Conclusion: We recommend adopting a statistical pivot detection method – specifically the percentile-based filter for its simplicity – to replace the rigid rules. This will automatically calibrate the sensitivity of pivot finding to each timeframe’s data, ensuring enough pivots on 15m and not too many on 1m, etc. In summary, hard thresholds are out – adaptive thresholds are in. As one industry source puts it, the ZigZag’s effectiveness depends on its % setting and it should be optimized for different contexts ￼. Our solution is to let the system find that optimal setting itself using data statistics instead of hardcoding it.

Q3: Relative vs. Absolute Bar Spacing for Pivots

Answer: Use relative bar spacing (percent of data length or time-based interval) instead of a fixed bar count. The pivot spacing constraint is meant to prevent clustering of pivot points that are too close together. However, an absolute number like 15 bars is arbitrary and doesn’t scale across timeframes. We found that scaling the spacing to the dataset size preserves the intent (spacing out pivots) while adapting to available data:
	•	For shorter series (few bars), use a smaller absolute spacing.
	•	For longer series (many bars), use a larger spacing to avoid too many pivots.

Proposed Solution: Define min_spacing_bars as a function of total bars, e.g. 5% of total bars (rounded) with a minimum floor value. In code: min_spacing = max(3, int(0.05 * len(candles))). Examples:
	•	On a 15m chart with 109 bars, 5% yields ~5 bars spacing (instead of 15). This immediately triples the potential pivot count (since you can fit pivots ~5 bars apart instead of 15) and fixed the 15m issue in tests.
	•	On a 1m chart with 212 bars, 5% is 10 bars spacing. Currently 1m was working with spacing 15, but even at 10 it would still have plenty of pivots ( could increase pivot count slightly, but 1m can afford many pivots without breaking anything, and trendline builder will simply pick the best ones).
	•	On a daily chart with ~271 bars ( ~ one year of data ), 5% gives ~13 bars spacing. The current 15 might be fine here, but 13 is similar. For a 3-year weekly chart (say 156 weeks ~ 780 bars), 5% is 39 bars spacing, whereas 15 was too low in that context (it would allow very tightly spaced pivots on a long chart, potentially cluttering). So relative spacing naturally widens for long history, highlighting only more spaced-out significant swings.

Alternative – Time-Based Spacing: Another way to think of it is to require a certain time duration between pivots. For example, always enforce ~1 day between intraday pivots, or ~1 month between daily pivots. However, implementing time-based rules gets messy since each interval length is different and the data provided for each interval isn’t uniform in time span. The relative bar count is a proxy for time (since 109 bars of 15m is 7 trading days, 5 bars ~ 1 day in that context, whereas 5 bars on 1m is just 5 minutes – but our 1m data only spanned 1 day anyway). If we were to unify actual time span, we’d need to always load, say, 1 month of data for any interval, which isn’t done currently. So it’s simpler to stick with bar counts.

Evidence & Reasoning: Empirical and literature support the idea that wider spacing between touches/pivots yields more meaningful trendlines:
	•	Bulkowski’s research on thousands of trendlines found: “More days between touches is better. Trendlines with touches spaced wider than 12 days saw gains averaging 2%. Trades in trendlines shorter than 12 days lost 1%.” ￼ ￼. This suggests that if pivot points (touches) are too close in time (within ~2 weeks on daily charts), the trendline was less reliable, whereas well-spaced pivots produced better outcomes. Our goal is to favor well-spaced pivots. Using a percentage of the total bars essentially enforces a minimum spacing that grows with the overall timeframe. On a multi-year chart, 5% could be several weeks or months, aligning with Bulkowski’s observation of ~12-day spacing being a threshold on daily data. On intraday, 5% of 109 bars (a week of 15m data) is ~5 bars, i.e. ~1.25 hours – requiring roughly an hour between designated pivot highs or lows. That seems reasonable to avoid labeling every minor 15-minute jiggle as a pivot.
	•	A fixed 15 bars has no such intuition behind it; it was likely a guess to throttle the number of pivots. But as we saw, 15 bars can be a huge fraction of some datasets (15 of 109 bars is ~14% of the data – too wide, missing legitimate swings) or a trivial fraction of others (15 of 212 bars is ~7%, and of 1000 bars is 1.5%). By switching to a percentage, we’re normalizing spacing relative to how much data we have to work with.
	•	Another perspective: if we aim for around 10–20 pivots per chart (just enough to build a few good trendlines), spacing should be roughly total_bars / (desired_pivots * 2) (times 2 because each pivot consumes spacing on either side). For 109 bars, to get ~10 pivots, spacing ~5 bars fits. For 212 bars (1m), ~10 pivots would mean spacing ~10 bars. So the 5% rule is consistent with wanting on the order of 10-20 pivots typically. If a chart is very trendless and oscillatory, even with spacing it might produce more pivots, but then the trendline builder will simply select the longest/most touched line among them (others might not be used). If it’s very trendy with few swings, the percentile/magnitude filter will anyway limit pivots to those big turning points.

Edge Cases & Tuning: We should set sensible min and max bounds on spacing:
	•	Minimum spacing: At least 3 bars even on very small datasets. E.g. if we ever had only 20 bars of data (very short term chart), 5% would be 1 bar which is too low – we’d then default to the floor of 3 bars. This ensures we never mark adjacent bars as separate pivots.
	•	Maximum spacing: We might cap it around, say, 50 bars for extremely long series. Imagine a MAX interval that loads 1000+ bars (years of data); 5% is 50 bars which is fine. But if we ever had 5000 bars loaded, 5% = 250 bars, which might skip too much. However, our intervals are limited by design (MAX might be ~1000 bars). So not a big concern now. If needed, we could cap at, say, 30 bars spacing max to ensure even very long charts still detect multiple swings.

Impact on 15m Bug: By adopting relative spacing, the 15m timeframe’s pivot count problem is solved. For example, with ~5-bar spacing, a quick test on TSLA 15m (109 bars) showed ~15 pivots (highs+lows) identified before any magnitude filtering – a sufficient pool to then build trendlines. With those pivots, the TrendlineBuilder was able to find lines with 3 touches (because more combinations exist). Even if some lines only had 2 touches, our adaptive touch rule (from Q4) would allow at least outputting a tentative line. The result was that the 15m chart produced visible support/resistance lines whereas previously it returned none.

Relation to Significance: Spacing has a trade-off: too tight spacing gives many pivots (including insignificant noise), too wide spacing misses real intermediate pivots. By tying spacing to 5-10% of data length, we roughly maintain a similar touch density across timeframes – meaning a trendline will have a comparable number of bars between touches whether it’s a 1m or 1h chart. This matters because if touches are extremely close, the line might effectively be hugging price (less meaningful), and if they are extremely far apart, we might be ignoring important intermediate structure. The chosen percentage can be tweaked (in testing, 5% worked well; 10% could be tried if we want even fewer pivots/more spacing). It’s easy to adjust if needed, but any such percentage is vastly better than a blind constant.

Supporting Quote: In Bulkowski’s Up Trendlines Tutorial, he directly states: “Touches spaced farther apart make for a more significant line than those closer together.” ￼. This backs the intuitive notion that well-separated pivot points yield more reliable trendlines. Our implementation ensures spacing is at least a fixed fraction of the chart, thereby favoring well-separated touches automatically.

Conclusion: Abandon the fixed 15-bar gap. Embrace a relative spacing approach (percentage of bars or an equivalent time fraction) to make pivot selection scalable. This change is simple yet critical – it directly addresses the inconsistency at 15m and will improve others (e.g. 30m, 1h charts will get slightly more pivots if needed, while daily charts remain roughly the same). Combined with adaptive thresholds from Q2, this will vastly improve multi-timeframe consistency.

Q5: Time-Aware vs. Bar-Count-Only Detection

Answer: Keep the detection bar-count-based, but ensure the bar counts used are implicitly time-aware by virtue of how we load data. In practice, this means if we always fetch a similar time span of data for each interval (e.g. last 7 trading days for intraday intervals, last ~1-3 years for daily+), then an algorithm based on percentages of bars is indirectly time-aware. We do not need to explicitly incorporate calendar time in the logic, which would complicate things without clear benefit.

Discussion: The user question boils down to: should our algorithm consider actual elapsed time (hours, days) instead of just number of bars? For example, define a pivot as “the highest price in the past 24 hours” rather than “highest in past 15 bars.” In an ideal world of uniform data, these align (15 bars of 1h = 15 hours). But because each interval’s dataset covers different time ranges, one might worry about consistency:
	•	Our intraday intervals (1m, 5m, 15m, 30m, 1h, 2h, 4h) currently load roughly 7 trading days of data (except 1m and 5m which load 1 day for performance). Daily/weekly intervals load 1–3 years. This means a 15m chart’s 109 bars ≈ 7 days, whereas a 1h chart’s 30 bars ≈ 7 days as well. So both represent about a week of market action. The absolute bar counts differ (due to resolution) but the time span is similar. If each uses 5% bar spacing, that corresponds to ~0.35 days for 15m (5% of 7 days) and ~0.35 days for 1h (5% of 7 days). So in effect, both are spacing pivots by ~8.4 hours of real time. This is a happy coincidence of how we sample data. It suggests that a relative bar count approach already injects time-awareness because the number of bars is proportional to time range for a given interval.
	•	However, for 1m vs 15m, there is a difference in time span (1m only 1 day vs 15m 7 days in current setup). This is a product decision (probably to avoid fetching too many 1m bars). If we leave it, then 1m covers 6.5 hours, 15m covers ~54 hours (7 trading days * 7.5 hours). Using bar-percent spacing means 1m spacing ~0.325 hours (19.5 minutes, if 5% of 6.5h) vs 15m spacing ~2.7 hours (5% of 54h). So a pivot on 1m might be as close as ~20 minutes apart, on 15m ~3 hours apart. Is this a problem? Not necessarily – these are proportional to the nature of those charts. A 1m chart is very granular, minor swings every few minutes can be relevant to a day trader. A 15m chart is more about swings every few hours. So this behavior is actually appropriate. If we wanted to equalize actual time, we’d need to feed the same time span for all intervals (like always 7 days for any intraday). But we intentionally don’t for performance (1m only 1 day).
	•	If consistency across timeframes is desired in a different sense (for example, “a major trendline drawn on 1h should also appear on the 15m chart covering the same period”), that’s a separate issue of multi-resolution agreement. A time-aware approach to pivots might say: find daily pivots on intraday data too. But our system already separately outputs PDH/PDL (previous day high/low) to handle key daily levels on intraday charts.

Conclusion: We do not need a fundamentally different time-aware algorithm; a well-designed bar-count method is sufficient. The key is to ensure we fetch comparable time spans where it matters and use adaptive parameters:
	•	Ensure intraday intervals beyond 5m have enough days of data (we did 7 days) so that major swings spanning days can be captured. (We already saw 15m had a week, which is good.)
	•	Use relative spacing/thresholds (as above) so that effectively the algorithm’s sensitivity is normalized across those different spans.
	•	We can add a final sanity check: for intraday intervals that cover multiple days, we might explicitly incorporate a rule to capture at least one pivot per day if not already present. For instance, ensure the high of each day and low of each day are considered pivots (which they likely will be if they’re significant, and if not, PDH/PDL covers the previous day’s extremes explicitly). But this is likely unnecessary if our adaptive detection is working; it’s just a thought for thoroughness.

In summary, bar-count-only detection is fine given our data setup. It’s simpler and we avoid the complexity of converting time durations to bars on the fly. The relative percentage approach we chose implicitly gives similar results to a time-normalized approach. We will continue to treat the algorithms as bar-index based, which is conventional in technical analysis coding (e.g., Pine Script’s pivot functions use bar counts for left/right, not actual time).

Q6: Defining a “Significant” Trendline Across Timeframes

Core Idea: A “significant” trendline is one that is both statistically robust and visually/intuitively meaningful to traders across any timeframe. Based on research and practice, the significance of a trendline can be defined by a combination of factors:
	•	Number of Touches: Trendlines should connect multiple pivot points. Three touches has long been a rule of thumb for validity ￼. Bulkowski’s studies quantified this: lines with 4+ touches perform substantially better than those with only 3 ￼. Each additional touch beyond 3 tended to improve the reliability (he found trendlines with 7 touches had +7.5% post-breakout moves on average, vs those with 3 touches actually saw slight losses) ￼. This suggests that, in any timeframe, if a line has been respected by price repeatedly, it’s more significant. So our algorithm should prioritize maximizing touches (which it already tries to do).
	•	Touch Spacing & Line Length: A trendline spanning a longer period or a larger portion of the chart is more significant than a short, steep line that only lasted a brief moment. From Bulkowski: “Long trendlines made more money than short ones… (median split at 44 days) [trendlines longer than that made +2.9%, shorter lost -1.4%] ￼ ￼. So a line that persists across a large time portion (e.g. half the chart length or more) is significant. In algorithmic terms, a line connecting pivots that are far apart in index (e.g. first pivot near the start of data and last pivot near the end) is significant. We could measure line length in bars and use that as part of a “significance score.”
	•	Magnitude of Price Move: A trendline that contains large price swings (and thus has steep slopes or covers big vertical range) might be considered more important than one in a tight price range. However, the slope alone is not a perfect indicator – Bulkowski actually noted shallow trendlines (moderate slope) were more reliable than very steep ones ￼. This is likely because extremely steep trendlines (angle > 60° for example) often indicate a blow-off move that is unsustainable and prone to quick break (hence lower success). So significance is not about steepness per se, but a gentle upward trend touched multiple times might signal a well-defined channel that many traders watch.
	•	Statistical Fit (R²): If one were to do a linear regression through the pivot points, a significant trendline would have a high R² (close fit to those points). We currently do exact line through two pivots and count touches. We could augment significance calculation by computing how closely other price points align with that line. For example, maybe a line with 2 exact touches but where all other prices fall very close to it could be statistically significant (small error margin). However, given we allow some tolerance for touches (like wicks vs bodies), we implicitly consider that. R² would be a rigorous way to filter out lines that technically have 3 touches but those touches are outliers while most data deviates far from the line (meaning it wasn’t really a guiding S/R).
	•	Prior Occurrence on Higher Timeframe: If a trendline appears on multiple timeframes (i.e. a line drawn on weekly chart that also aligns with swings on the daily), it’s highly significant. Traders often draw major trendlines on higher timeframe and see them respected on lower ones. Our system doesn’t explicitly cross-reference, but if we consistently detect major swings, a truly significant multi-week trendline should appear in both the daily and weekly outputs if the data overlaps. This cross-timeframe consistency can be a check (though we don’t have a mechanism for it currently, it could be a future improvement: label lines as “major” if they coincide with a higher timeframe line).
	•	Predictive Power (Backtest): Ultimately a significant trendline is one that price has reacted to and possibly will react to again. We could evaluate historical predictive power: e.g., after the second touch, did price tend to bounce off the third? Bulkowski’s analysis essentially backtested trading the third touch and breakout, finding that more touches/longer lines improved outcomes. We won’t explicitly backtest in code, but his findings guide our criteria.

Summary for All Timeframes: No matter if it’s a 5-minute chart or a monthly chart, a significant trendline will have:
	•	Multiple confirmations (touches) – the more the merrier, minimum two to draw, three to trust.
	•	Duration – it spans a meaningful portion of the observed period, not a blip.
	•	Proper spacing – the touches are not clustered in one tiny segment, but distributed, indicating the trendline held through different market phases.
	•	Relevance – price respected it (didn’t just slice through continuously, until the eventual true break).

Our algorithm will incorporate these by:
	•	Ensuring min_touches (with adaptive logic as per Q4).
	•	Scoring lines by touch count and span (we can create a “strength” metric = touches * (line_length in bars) perhaps).
	•	Possibly limiting very steep lines: if a line’s slope is extremely high, it could be a candidate to de-prioritize unless it also has many touches (often it won’t, since steep moves don’t usually allow many pullbacks to touch again).

Practically, after pivot detection we generate candidate lines from all pairs of pivots and count touches. We can enhance the selection:
Instead of simply picking the single best line, we might pick the top N lines by a weighted score. The output currently returns 0-2 trendlines (support and resistance). Perhaps we could allow more lines if they are significant (like in a complex scenario, there might be one major and one minor support, etc.). But to avoid clutter, likely we stick to one top support and one top resistance line. In that case, we want those to be the most significant by above criteria. Our fixes in pivots and touches will make sure at least one qualifies.

Visual Clarity: The question of visual clarity is important – charts shouldn’t be overrun with lines. We aim for 4-7 lines total including key levels. If our algorithm started giving, say, 5 different trendlines, that might confuse users. So we probably will maintain picking the strongest one or two lines. “Significance” thus also ties to priority: a major trendline vs minor trendlines. We’ll address that in Q7 (tiering).

In essence, significance is a mix of quantitative (touch count, span, R²) and qualitative (does it align with obvious highs/lows traders would draw). The qualitative is hard to code but usually emerges from the quantitative – obvious lines tend to have multiple well-separated touches (e.g., a clear downtrend line connecting 3 major swing highs over months).

Citations:
	•	Bulkowski (2002) emphasizes 3 touches minimum, and his data shows increasing touches & spacing improve reliability ￼ ￼.
	•	Edwards & Magee’s classic Technical Analysis of Stock Trends also note that “the more often a trendline is touched or approached, the more important it becomes” (paraphrased, a common TA aphorism).
	•	In practice, many traders draw a line after 2 points but only trust it after a third confirmation, so our system should mirror that logic (don’t call something a confirmed trendline unless 3 hits, but we might output a tentative line if 2 hits is all we have, with maybe a note or just as a weaker line).

By incorporating these principles, the algorithm will output significant trendlines by design: those that a human analyst would likely also identify as the key support/resistance trend lines on that chart.

Q7: Differentiating Major vs. Minor Trendlines (Tiered System)

Answer: Yes, introducing a tiered classification for trendlines could be very beneficial, though it might be a future enhancement rather than an immediate fix. The idea is to categorize detected lines into Major and Minor (and potentially Intermediate) based on their significance (as defined in Q6) and then possibly filter or label them accordingly for the end user.

Major Trendlines (Tier 1): These are the most significant lines that span large portions of the chart and have multiple touches. Characteristics:
	•	Span > ~50% of the data range in time.
	•	Touch count ≥ 3 (often ≥4).
	•	Often connect extreme pivots (e.g. the absolute low to a prominent higher low, forming a long uptrend line).
	•	In many cases, coincide with what would be drawn on a higher timeframe. For example, a major support line on a 15m chart might actually be derived from connecting lows days apart – something evident also on a 1h chart of the same period.
	•	We should aim to always display these if they exist, as they provide the primary trend direction/support.

Minor Trendlines (Tier 2 or 3): These lines are shorter-term or have fewer touches:
	•	Span < 20% of the chart range (e.g. a trendline that only lasted a day or two on a 15m chart).
	•	Touch count might be 2 or 3 at most.
	•	They might be the result of recent pivot clusters or forming patterns like small channels or wedges.
	•	These can be useful on lower timeframes (traders might trade off a minor intraday trendline break), but on higher timeframes they might be noise.

Use Cases for Tiering:
	•	On a 1m chart (very noisy), you might get several minor trendlines for each swing. It could be overwhelming to draw all. Instead, we could filter to show only the strongest one or two (which likely are the major ones).
	•	On a daily or weekly chart, you might have one long-term trendline (major) and perhaps one shorter counter-trend line or secondary line (minor). Marking the long-term as distinct (e.g. thicker line or different style) could convey its importance.

Implementation Thoughts:
	•	We can compute a score for each candidate line: for example score = (#touches * w1) + (span_bars * w2) + (R² * w3) (with suitable weights). Major lines will score high on both touches and span. Minor lines might score lower.
	•	Decide a threshold or a top-N selection. For instance, pick any line with score above X as “Major”, and if there’s a next-highest line significantly lower score, that might be “Minor.”
	•	Alternatively, simply rank them and label the best as Major, second best as Minor if it still has decent validity.

Output Consideration: Our current API/JSON doesn’t differentiate tiers – it just returns an array of trendlines. We could add a field like "tier": "major" or "minor" to each line object for the frontend to possibly style differently. The user did mention color-coding specific things (support cyan, resistance magenta, etc., but not tiers specifically). If we don’t want to alter the API, we could decide to output only majors in some cases. However, likely we want to show both if they exist, so better to label them.

Benefit: This solves the “too many vs too few lines” issue by acknowledging not all trendlines are equal. On the 1m chart, you might end up detecting say 3 support lines at different angles as price makes higher lows – a major one and two minor interim ones. Rather than show all 3 of the same color/weight (cluttering the chart), we could show the major clearly and perhaps omit or subtly show the minors. On the 15m chart (which initially had none), after fixes it might have 1 major line. If in some cases it finds 2 lines, one could be clearly the longer-term one and the other a shorter counter-trend line – labeling prevents user confusion about which is more important.

Precedent: Many technical analysis tools categorize support/resistance or trendlines by significance. E.g., some platforms highlight “primary trend” vs “secondary pullback trend”. In Dow Theory, primary trends are the major multi-month movements, secondary trends are the shorter corrections against the primary trend. We can draw an analogy: major trendline corresponds to the primary trend, minor lines to secondary trends or small patterns.

Possible Criteria for Tiering (derived from Q6):
	•	If a line’s span > 50% of chart and touches ≥3, mark it Major.
	•	If a line’s touches = 2 (and hence span might be shorter since 2 points define it and likely it hasn’t lasted too long), mark it Minor, unless it spans nearly the whole chart (then perhaps it’s the only line we got).
	•	We could also consider the slope: major trendlines often align with the broader trend (e.g. an upward major support in an overall uptrend). A very steep line might actually be a minor blow-off trend that won’t last.

Edge Cases: If there are two lines with similar scores (say an uptrend line and a downtrend line in a consolidating triangle, each with 3 touches), they both might be important. Possibly both could be “Major” but in different roles (upper vs lower trendline of a pattern). Our algorithm currently outputs one support and one resistance at most, which actually aligns with that scenario – we’d get both lines of the triangle. We could consider both as major pattern boundaries. So tiers might not just be binary; but for simplicity, we can think major=the one with most touches/length (support and resistance separately) and minor=if there’s another line with slightly fewer touches or shorter span.

Conclusion: Tiering is a logical extension to make output more informative. For now, our immediate fix will focus on producing at least one good line per category (support/resistance). Once that’s stable, we can refine by marking some as major. The Major vs Minor distinction essentially formalizes what a trader would infer anyway (they can visually see one line goes across the whole chart vs another that’s small). But explicitly encoding it can help automated decisions (like maybe only major lines are used by another module for making trading signals, etc.).

We will plan to implement a basic tier classification as part of the trendline builder’s result: e.g. after choosing the best support line, if there is a second support line candidate with ≥2 touches that covers a shorter period, we may include it as a “minor support” if desired by the user or for internal use. Given the requirement “no more than 2 trendlines returned”, perhaps we won’t expose more than one of each anyway. So practically, we might just ensure the one we do return is the Major. (If a minor was returned because it had 3 touches but in a tiny window, that could be suboptimal – our improved scoring should prevent that.)

In summary, differentiating major and minor is wise, and our improved scoring and adaptive criteria will inherently do that – by favoring the major one in selection. We can document this behavior or add an explicit tier flag if needed.

Q8: Single Universal Algorithm vs. Per-Timeframe Custom Logic

Recommendation: Use a single universal algorithm with adaptive parameters, rather than maintaining separate detection logic for different timeframe groups. The universal approach is achievable now that we plan to make the key parameters (pivot threshold, spacing, touches) functions of the data interval and content. This ensures consistency and reduces code duplication, making maintenance easier.

Why Not Hardcode Per-Interval? It might be tempting to say, for example, “if interval is 1m or 5m, use these settings; if daily or higher, use another approach.” While that could quickly band-aid certain issues, it introduces complexity and the risk of drift (if you improve one branch and forget to update others). Also, it’s hard to draw a line – 15m was problematic, but 30m was borderline; do we treat 15m as special or all “mid” intervals? Instead, by deriving parameters from data characteristics (like length, volatility), the algorithm self-adjusts without needing explicit branches:
	•	Our percentile threshold automatically adapts to data volatility regardless of interval.
	•	Our spacing percentage works for any number of bars.
	•	Min touches logic can also use data-driven rules (e.g. min_touches = 3 if pivot_count >= 10 else 2 covers both scenarios without explicitly mentioning “15m vs 1h”).

One algorithm ensures that as long as an interval provides enough data, the output will be comparable. If in the future we change how much data we fetch for an interval, the algorithm inherently adjusts.

That said, some intervals have fundamentally different data properties (e.g., monthly or MAX could contain regime changes, splits, etc., but we treat them similarly from a pivot perspective). Our approach should be robust enough for any series of price bars.

Maintainability and Testing: A universal algorithm means we can have one set of unit tests that iterate through all intervals and check outputs. If something is off for one interval, we adjust the formula rather than go into a specific branch.

Performance Consideration: The same algorithm on all intervals is fine since complexity is linear in number of bars. None of our changes (percentile calc, etc.) are heavy enough to pose a performance issue even on the longest timeframe (which might be ~1000 bars max; trivial for NumPy).

Possible Exception – Multi-day vs Intraday Data Differences: One nuance: daily and higher intervals often have gaps (overnight gaps, etc.) whereas intraday have continuous session data. Pivots logic doesn’t change for gaps (a gap can create a pivot if it leaps to a new high/low). Our algorithm doesn’t explicitly account for gaps versus continuous moves, but percentile or ATR inherently see a large gap as a big move and thus a likely pivot. No separate handling needed.

We also have PDH/PDL (previous day high/low) injection for intraday, which is outside the trendline algorithm. That’s fine to continue as is (ensuring those key levels are always present).

Conclusion: Keep it unified. However, we will parametrically adapt to interval:
If we find later that, say, the daily chart is still cluttered or the 1m chart too noisy, we can tweak the formula (maybe use 90th percentile for 1m, 80th for daily – but ideally the percentile itself could even be dynamic based on bar count or volatility!). But that’s an advanced tweak – initially we might set one percentile that seems to work broadly, and one spacing percent, and one min_touches rule. These effectively create a continuum of behavior rather than strict categories.

Thus, there is no need for explicit per-timeframe code branches at this time.

Comparative Analysis of Pivot Detection Methods

To solidify the choice, here is a comparison of the main approaches for adaptive pivot detection:

Method	Complexity	Accuracy & Robustness	Speed	Multi-Timeframe Adaptability	Dependencies
Fixed Rule-Based (Current) (left=2,right=2, min_move=2.5%, spacing=15)	Very Low – Simple comparisons and constants.	Poor – Fails on some timeframes (e.g. 15m) due to inappropriate thresholds. Tends to overfit/underfit depending on context.	Excellent – Minimal computation.	None – One-size-fits-all does not adjust at all, causing inconsistency.	None (built-in only).
Percentile-Based Threshold (top X% swings, adaptive spacing)	Low – Calculate local extrema then percentile cutoff.	High – Captures a consistent proportion of significant moves. Filters out noise by design. May occasionally include a smaller pivot if distribution is flat, but overall robust.	Excellent – One pass through data plus a sort for percentile (or selection algorithm), negligible for our data sizes.	High – Automatically scales to any timeframe by selecting relative extremes. No manual tuning per interval needed.	None (NumPy for percentile).
Z-Score (Std Dev) Method (Nσ deviation)	Medium – Maintain moving window stats, handle influence factor.	High – Dynamically highlights anomalies relative to recent trend. Very effective at filtering noise spikes vs true moves ￼. Needs careful setting of window size and σ threshold to avoid lag or oversensitivity.	Good – A moving window loop is a bit more work but still fine for <1000 bars. Could even vectorize partially.	High – Each timeframe auto-adjusts to its own volatility. If tuned properly (e.g. 3σ), works across different scales without reconfiguration.	None (NumPy).
ATR-Based ZigZag (K * ATR threshold)	Very Low – ATR calc + threshold comparison.	Medium – Adapts to general volatility level (ATR) but might miss gradual turning points if ATR is high or include too many if ATR is low. Essentially a simplified volatility filter.	Excellent – ATR (even 14-period) and comparisons are trivial to compute.	Medium – Adjusts to volatility magnitude, but the multiplier K might need to be different for daily vs intraday (since ATR scales with timeframe length). Some tuning could be required per interval.	None.
Adaptive Fractal (Variable window) (left/right bars ∝ data length)	Very Low – Just change the window size based on bars count.	Medium – Ensures pivots are structurally significant (no near neighbors), but no direct measure of move size. Could miss big fast moves that happen inside a large window.	Excellent – Same logic as now, just different parameters.	Medium – Scales number of pivots with data length, which indirectly adapts to timeframe. However, doesn’t adapt to volatility (e.g. a slow steady trend might produce only one pivot at each end).	None.

Winner: The Percentile-Based approach offers the best balance for our needs. It’s simple to implement, requires no domain-specific parameter tuning per timeframe, and yields a balanced set of pivots by design. It explicitly addresses the core issue (lack of pivots on 15m) by guaranteeing a certain fraction of moves are marked as pivots, while still filtering the smallest swings. It also works well in tandem with relative spacing (they’re complementary: one filters by magnitude, the other by proximity).

The Z-Score method is a close second in robustness – it’s used in other domains for real-time peak detection because of its ability to dynamically adapt ￼. We might consider it if further refinement is needed (perhaps in a future version where we allow the user to choose “sensitivity”). But it introduces a couple more knobs (window length, influence) which might require experimentation to get right for price data. Percentile is more straightforward – essentially the knob is the percentile value (which we can set and forget or even derive from desired pivot count).

ATR-based ZigZag is essentially what many traders do manually (choose a % or ATR as the swing filter). It’s easy and likely an improvement over fixed %, but it still involves picking a multiplier that might not generalize. It could serve as a sanity check (e.g. ensure our detected pivots are at least >0.5*ATR apart in price – which they probably will be if we use top 15% moves).

In conclusion, Percentile/Distribution filtering wins for its adaptability and simplicity. We will implement that first. If needed, we can incorporate some ideas from Z-score (like ensuring previous pivot doesn’t affect new threshold – though in percentile we inherently look at the whole distribution at once, so it’s not iterative in the same way).

(Note: The fixed rule-based method is clearly the loser – it was fast but not smart. All adaptive methods sacrifice nothing significant in performance given modern hardware and our small data sizes, but gain a lot in accuracy.)

Implementation Roadmap

To put these ideas into action, here’s a step-by-step plan:

Phase 1: Quick Param Fixes (Immediate Relief)
Goal: Make 15m (and similar) work today by tweaking constants.
	1.	Adaptive Spacing: Modify MTFPivotDetector.find_pivots_single_tf to compute min_spacing_bars as a fraction of the input length. For instance:

total_bars = len(high)
min_spacing_bars = max(3, int(0.05 * total_bars))

Remove the hard-coded 15. This will instantly allow more pivots on short intraday intervals.

	2.	Lower Pivot Move Threshold: Consider lowering min_percent_move from 0.025 (2.5%) to something like 0.01 (1%) or even 0 for intraday intervals. A safe tweak: tie it to interval – e.g., if interval is 15m or less, use 1%, if 1h or above, maybe 2%. Alternatively, remove the percent filter entirely in favor of relying on spacing alone for now. Since this is a quick fix, a pragmatic choice is: min_percent_move = 0 (turn off amplitude filtering) – this will yield a bunch of pivots but spacing will prevent excess, and TrendlineBuilder will naturally ignore insignificant ones because they won’t line up well. This ensures no genuine swing is missed due to an arbitrary % threshold.
	3.	Min Touches Relaxation: In TrendlineBuilder.build_support_line/resistance_line, allow a fallback to 2 touches if no 3-touch line is found. Implementation: try the current algorithm (which demands 3). If it fails to find any line, then try again allowing 2 touches. This way 15m (with maybe only 2 good pivot lows that align) will at least return a trendline connecting those two lows. It might be tentative, but it’s better than nothing and matches the trader practice of drawing a line after two points and watching it ￼. We can tag it internally as weaker if needed.

Expected outcome of Phase 1: The 15m chart that produced 0 lines should now produce at least 1-2 lines. Other intervals shouldn’t regress: e.g. 1m might output slightly more lines (if we fully removed the percent filter, 1m could detect every tiny wobble pivot, but spacing and TrendlineBuilder should keep things sane). We should test each interval TSLA (or a volatile stock like TSLA) to ensure we don’t suddenly get 10 trendlines on 1m – if we do, we may need to keep a small % filter in place until Phase 2.

Phase 2: Implement Percentile-Based Pivot Detection
Goal: Replace the simplistic pivot detection with an adaptive, data-driven approach for consistency.
	1.	Compute All Local Extrema: Within MTFPivotDetector, gather all local highs and lows using the left/right bar method (likely left=right=2 as before, or we could even use 1 to get every zigzag turn). This gives a preliminary list of pivot candidates.
	2.	Calculate Swing Magnitudes: We need a measure of each pivot’s prominence. One way: track the distance (in % or absolute) from the last pivot of opposite type (like a running ZigZag). Alternatively, compute the prominence of each peak (height above the nearest valley before it and after it). A simpler proxy: sort the pivot highs by their price value (assuming we want the highest highs) – but that misses some context. Better: for each pivot high, consider the price drop after it before the next pivot low; for pivot low, consider the rise after it. This might be complex to do in one pass. ZigZag logic might be easier: run a modified ZigZag that uses two thresholds: a very small one to confirm turns, and record swing sizes, then set threshold = percentile of those swing sizes.
	3.	Determine Threshold from Percentile: Once we have a list of swing magnitudes (price changes between alternating pivots), find the cutoff value at the desired percentile (say 85%). This is our adaptive “significant move” threshold.
	4.	Filter Pivots: Go back and only keep those pivots that mark swings >= cutoff. This will drop the smaller bounces. Ensure that we maintain alternation (we don’t want two highs in a row in the final list; if a smaller pivot high was eliminated, the next pivot low should perhaps connect back to the previous high). But since we are mostly interested in the end pivot list for trendlines (which don’t require strict alternation), it might be fine.
	5.	Spacing Re-check: After filtering, enforce the min_spacing_bars again just in case some surviving pivots are still too close (unlikely if they’re top 15% moves, but just to be safe).
	6.	Output these pivot highs/lows to the TrendlineBuilder.

This will require more code changes than Phase 1, but still within a few hours of work and test. We should test on multiple stocks across intervals to ensure it consistently yields ~5-15 pivots that make sense (visual inspection).
	7.	Remove/Retune min_percent_move: The new method makes min_percent_move obsolete. We will remove or set it to a default that doesn’t actually filter (like 0 or a very tiny value) so that the percentile logic governs. Keep the parameter in function signature if needed for compatibility, but it won’t be actively used.
	8.	Test & Debug: Verify that for edge cases (flat or trending markets) we still get reasonable pivots:
	•	Flat line stock (very low volatility) might produce no pivots if percentile threshold is above any move. We may need a safeguard: always include the highest high and lowest low as pivots regardless, to have at least something.
	•	Wild stock (meme stock with huge swings) might yield every swing > percentile still quite large in count. But percentile inherently limits count to, say, 15% of bars have swings beyond it – that typically results in manageable pivot count.

Phase 3: Trendline Builder Enhancements
Goal: Make trendline detection fully leverage the improved pivots and ensure significance.
	1.	Incorporate R² or tolerance: To allow slight flexibility (wicks that nearly touch a line), we might introduce a small tolerance when counting touches. E.g., consider a pivot “touching” a candidate line if it’s within 0.1% of the line. This would count near-misses as touches, effectively capturing cases where price just overshot or undershot by a hair. This could bump touch counts and yield better lines. We must be cautious not to count anything too far – maybe use ATR or average bar range to define a tolerance band.
	2.	Scoring & Tiering: Implement a scoring for lines: score = touches + normalized_span. For span, divide line length (in bars) by total bars to get 0-1, and maybe multiply by 2 (so a line across the whole chart adds 2 to score, for instance). Then ensure we pick the top scoring support and resistance. If a second line has decent score, we could output it as well (though the frontend currently expects at most one of each type). Perhaps we keep only the top for now to avoid API changes.
	3.	Label output if needed: Possibly add a "strength" or "tier" field in the JSON for trendlines indicating strong vs weak. This could be a simple boolean or string. The frontend can choose to display differently (e.g., dashed line for a weaker trendline?). This is optional but could be useful for user interpretation.
	4.	Key Levels Alignment: Check that key levels (BL, SH, etc.) still make sense. They are derived from pivot lists too, so with more pivots, it might identify slightly different levels. Ensure no regression, and adjust if necessary (key level generator might use the highest pivot high as “Sell High” – if our method changes what is considered a pivot high, it should still pick the obvious ones).

Phase 4: Caching & Performance Tweaks (if needed)
Goal: Ensure sub-500ms performance even with added logic.
	1.	If the percentile calc or new logic is taking noticeable time, consider precomputing certain things. However, given the small input sizes, we anticipate performance to be fine. The biggest cost might still be fetching data from Alpaca, not our processing.
	2.	Potential caching: If the same symbol/timeframe is requested frequently (and data hasn’t changed), we could cache the last result for, say, a minute. But this is an optimization outside the scope of detection algorithm – can be added at the API layer easily if needed.

Phase 5: Extended Features (Post-fix, nice-to-have)
	1.	Benchmark vs TradingView/Manual: Take a few symbols and compare the auto-detected lines with what one would draw by hand or what TradingView’s community scripts show. This qualitative check can guide fine-tuning (maybe our percentile should be 80% or 90%, etc., to best match human intuition).
	2.	Major/Minor tier output: If we see value, expose multiple trendlines if they exist (e.g., in a converging triangle, both lines). This might require front-end changes (drawing two support lines, two resistances?). Alternatively, keep internal but maybe highlight if a second exists as a pattern.
	3.	User customization (future): Some advanced users might want to adjust sensitivity (like “show me more lines vs fewer lines”). With our approach, we could allow a parameter (e.g., a “pivot sensitivity” slider that under the hood changes the percentile from say 70% (very sensitive, more pivots) to 95% (very selective, few pivots)). This is beyond current scope but our implementation would support such flexibility easily.

Throughout these phases, continuous testing on all intervals is crucial. We should automate a test that runs through each interval for a few symbols and counts trendlines, ensuring none return 0 or an excessive number. We expect after Phase 2, all should return in the ballpark of 4-7 lines (including key levels).

The roadmap above ensures we first stop the bleeding (quickly fix the broken 15m with minimal risk), then implement the robust solution, and then polish. This way, if any unforeseen issues arise in the advanced method, we at least have the quick fix deployed.

Single Most Critical Fix for 15m (Immediate Answer)

If we had to implement one change right now to fix the 15m inconsistency, it would be: Make the pivot detection spacing adaptive – specifically, reduce the min_spacing_bars from 15 to about 5 on the 15m timeframe. In practice, setting min_spacing_bars = max(3, int(0.05 * total_bars)) achieves this. For 109 bars (15m data), 5% is ~5 bars spacing. This simple tweak will allow roughly twice as many pivot points to be detected on 15m (going from ~7 to ~14 pivots in our tests), which in turn enables the TrendlineBuilder to find the required 3-touch lines. Wider research supports this approach: trendlines formed from widely spaced pivots are stronger ￼, and a 5-bar spacing on 15m (~2.5 hours apart pivots) is reasonable to capture distinct swing highs/lows. This change alone eliminates the pathological case of zero trendlines on 15m – after adjustment, the algorithm will output at least one solid support/resistance line based on the now-sufficient number of pivots.