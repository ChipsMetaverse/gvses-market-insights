# 🎭 Persona-Based Drawing Capabilities Test Plan

**Testing Method**: Playwright MCP Server  
**URL**: http://localhost:5174  
**Date**: 2025-11-01  
**Status**: Ready for Execution

---

## Test Structure

### 4 Personas × 3 Queries Each = 12 Total Tests

---

## 👶 PERSONA 1: BEGINNER TRADER

**Profile**: Just learned about trendlines and S/R, wants simple visual aids  
**Experience**: 0-6 months  
**Needs**: Clear visuals, simple explanations, not overwhelming

### Test 1.1: Basic Trendline
**Query**: "Show me a simple trendline for AAPL"  
**Expected Backend Commands**:
- `LOAD:AAPL`
- `TRENDLINE:xxx:xxx:xxx:xxx`

**Expected Frontend**:
- Line drawn on chart
- Clear color (blue/red)
- Visible label

**Success Criteria**:
- ✅ Trendline appears on chart
- ✅ Response is simple (< 200 words)
- ✅ No technical jargon

### Test 1.2: Support & Resistance
**Query**: "What is support and resistance for TSLA?"  
**Expected Backend Commands**:
- `LOAD:TSLA`
- `SUPPORT:xxx` (1-3 levels)
- `RESISTANCE:xxx` (1-3 levels)

**Expected Frontend**:
- Green lines (support)
- Red lines (resistance)
- Labels visible

**Success Criteria**:
- ✅ At least 2 support levels shown
- ✅ At least 2 resistance levels shown
- ✅ Lines are color-coded
- ✅ Explanation mentions "bounce" or "ceiling/floor"

### Test 1.3: Price Bounce Help
**Query**: "Help me understand where the price might bounce for NVDA"  
**Expected Backend Commands**:
- `LOAD:NVDA`
- `SUPPORT:xxx`

**Expected Frontend**:
- Support levels highlighted
- Clear visual indication

**Success Criteria**:
- ✅ Support levels identified
- ✅ Beginner-friendly explanation
- ✅ Visual makes sense without context

---

## 📈 PERSONA 2: INTERMEDIATE TRADER

**Profile**: 1-2 years experience, learning patterns and fibonacci  
**Experience**: 6 months - 2 years  
**Needs**: Pattern recognition, strategy context, actionable setups

### Test 2.1: Fibonacci Retracement
**Query**: "Draw fibonacci retracement levels for MSFT from recent high to low"  
**Expected Backend Commands**:
- `LOAD:MSFT`
- `FIBONACCI:high:low`

**Expected Frontend**:
- Multiple fibonacci levels (23.6%, 38.2%, 50%, 61.8%)
- Horizontal lines at each level
- Labels with percentages

**Success Criteria**:
- ✅ Fibonacci command generated
- ✅ Levels calculated from recent swing
- ✅ Response explains which levels to watch

### Test 2.2: Triangle Pattern
**Query**: "Show me triangle patterns on SPY with trendlines"  
**Expected Backend Commands**:
- `LOAD:SPY`
- `PATTERN:TRIANGLE` or similar
- `TRENDLINE:xxx` (for triangle boundaries)

**Expected Frontend**:
- Pattern boundary box
- Trendlines showing triangle shape
- Pattern label with confidence

**Success Criteria**:
- ✅ Pattern detected (or explains why not present)
- ✅ If present, trendlines drawn
- ✅ Trading implications explained

### Test 2.3: Multiple S/R with Context
**Query**: "Where are the key support and resistance levels for AMD? I want to plan my trades"  
**Expected Backend Commands**:
- `LOAD:AMD`
- Multiple `SUPPORT:xxx`
- Multiple `RESISTANCE:xxx`

**Expected Frontend**:
- 3-5 support levels
- 3-5 resistance levels
- All clearly labeled

**Success Criteria**:
- ✅ Multiple levels identified
- ✅ Response includes trading strategy
- ✅ Mentions entry/exit concepts

---

## 🎯 PERSONA 3: ADVANCED TRADER

**Profile**: 3-5 years experience, uses complex strategies  
**Experience**: 2-5 years  
**Needs**: Precision, risk/reward, complex patterns, multiple timeframes

### Test 3.1: Multiple Timeframe Trendlines
**Query**: "Draw multiple timeframe trendlines for GOOGL - I need to see weekly and daily trends"  
**Expected Backend Commands**:
- `LOAD:GOOGL`
- Multiple `TRENDLINE:xxx` commands
- Different timeframe analysis

**Expected Frontend**:
- 2+ trendlines
- Different colors if possible
- Clear distinction between timeframes

**Success Criteria**:
- ✅ Multiple trendlines generated
- ✅ Response mentions timeframe alignment
- ✅ Visual shows trend direction

### Test 3.2: Swing Trade Setup
**Query**: "Show me precise entry and exit levels for a swing trade on NFLX with risk/reward"  
**Expected Backend Commands**:
- `LOAD:NFLX`
- `ENTRY:xxx`
- `TARGET:xxx`
- `STOPLOSS:xxx`

**Expected Frontend**:
- Blue line (entry)
- Green line (target)
- Red line (stop loss)
- All labeled

**Success Criteria**:
- ✅ Entry, target, stop loss calculated
- ✅ Risk/reward ratio mentioned
- ✅ Precise price levels (to 2 decimals)

### Test 3.3: Head & Shoulders Pattern
**Query**: "Identify head and shoulders pattern on COIN and mark the neckline"  
**Expected Backend Commands**:
- `LOAD:COIN`
- `PATTERN:HEAD_SHOULDERS`
- `TRENDLINE:xxx` (neckline)

**Expected Frontend**:
- Pattern boundary box
- Neckline trendline
- Pattern label

**Success Criteria**:
- ✅ Pattern detection attempted
- ✅ If found, neckline marked
- ✅ Breakout target calculated

---

## 👔 PERSONA 4: SEASONED PROFESSIONAL

**Profile**: 10+ years, institutional trader  
**Experience**: 5+ years  
**Needs**: Speed, precision, comprehensive analysis, measurement tools

### Test 4.1: Comprehensive Technical Analysis
**Query**: "Comprehensive technical analysis for QQQ with all key levels and measurements"  
**Expected Backend Commands**:
- `LOAD:QQQ`
- Multiple `SUPPORT:xxx`
- Multiple `RESISTANCE:xxx`
- `FIBONACCI:xxx:xxx`
- `TRENDLINE:xxx`

**Expected Frontend**:
- 5+ drawing commands total
- Multiple types (S/R, fib, trendlines)
- Professional layout

**Success Criteria**:
- ✅ Comprehensive analysis (5+ levels)
- ✅ Response time < 3 seconds
- ✅ Precise prices (2 decimal places)
- ✅ All major levels identified

### Test 4.2: Precise Risk/Reward Trade
**Query**: "Calculate precise entry with 1:3 risk reward for TSLA swing trade"  
**Expected Backend Commands**:
- `LOAD:TSLA`
- `ENTRY:xxx`
- `TARGET:xxx` (should be 3x distance from entry to stop)
- `STOPLOSS:xxx`

**Expected Frontend**:
- 3 horizontal lines
- Exact price levels
- R:R validation

**Success Criteria**:
- ✅ 1:3 risk/reward calculated correctly
- ✅ Entry at optimal level
- ✅ Math verified in response
- ✅ Response time < 2 seconds

### Test 4.3: Complex Pattern Analysis
**Query**: "Show me Elliott Wave count on SPX with fibonacci extensions"  
**Expected Backend Commands**:
- `LOAD:SPX`
- `PATTERN:xxx` (wave analysis)
- `FIBONACCI:xxx:xxx` (extensions)
- Multiple `TRENDLINE:xxx`

**Expected Frontend**:
- Multiple fibonacci levels
- Wave count annotations
- Trendlines for waves

**Success Criteria**:
- ✅ Advanced pattern analysis attempted
- ✅ Fibonacci extensions calculated
- ✅ Professional-grade depth
- ✅ Acknowledges complexity if not fully supported

---

## 📊 Success Metrics

### By Persona

| Persona | Tests | Pass Threshold | Grade Target |
|---------|-------|----------------|--------------|
| Beginner | 3 | 3/3 | A (Essential) |
| Intermediate | 3 | 2/3 | B (Good) |
| Advanced | 3 | 2/3 | B (Acceptable) |
| Seasoned | 3 | 1/3 | C (Needs work) |

### Overall Success
- **Excellent**: 10-12 tests passed
- **Good**: 8-9 tests passed
- **Acceptable**: 6-7 tests passed
- **Needs Improvement**: < 6 tests passed

---

## Test Execution via Playwright MCP

### Commands to Run

```javascript
// Test 1: Navigate to app
await page.goto('http://localhost:5174');
await page.screenshot({ path: 'test_initial.png' });

// Test 2: Check drawing elements
const chartPresent = await page.locator('[class*="chart"]').isVisible();

// Test 3: Trigger pattern hover (tests drawing visibility)
await page.locator('[class*="pattern"]').first().hover();
await page.screenshot({ path: 'test_pattern_hover.png' });

// Test 4: Check for lines/annotations
const drawingElements = await page.evaluate(() => {
  return {
    lines: document.querySelectorAll('[class*="line"]').length,
    patterns: document.querySelectorAll('[class*="pattern"]').length
  };
});
```

### Backend API Tests

```bash
# For each query, test backend:
curl -X POST http://localhost:8000/api/agent/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"query": "<QUERY_TEXT>"}' | jq '.chart_commands'
```

---

## Expected Results Summary

### Backend Command Generation
- ✅ Beginner queries → Simple commands (1-3)
- ✅ Intermediate queries → Pattern + drawing commands (2-5)
- ✅ Advanced queries → Multiple precise commands (3-7)
- ✅ Professional queries → Comprehensive commands (5-10)

### Frontend Rendering
- ✅ Lines visible on chart
- ✅ Color-coded by type
- ✅ Labels present
- ✅ Interactive (hover works)

### Response Quality
- ✅ Beginner: Simple, clear (< 200 words)
- ✅ Intermediate: Strategic context (200-400 words)
- ✅ Advanced: Precise, detailed (300-500 words)
- ✅ Professional: Comprehensive, fast (any length, < 3s)

---

## Known Limitations to Document

1. **Measurement Tool** ❌
   - No visual ruler for distance measurement
   - Professionals will miss this

2. **Entry Query Routing** ⚠️
   - "Where should I enter?" may not trigger entry calculation
   - Workaround: "Calculate swing trade entry for X"

3. **Complex Patterns** ⚠️
   - Elliott Wave not fully supported
   - Will provide best effort analysis

---

## Test Deliverables

1. **Screenshots** (10-15 total)
   - Initial state
   - Each persona's key test
   - Pattern interactions
   - Final state

2. **Backend Response Log**
   - All 12 queries
   - Commands generated
   - Response times

3. **Assessment Report**
   - Pass/fail by persona
   - User experience ratings
   - Recommendations

4. **Video Recording** (Optional)
   - Full test execution
   - Visual proof of capabilities

---

**Status**: Ready for Execution  
**Estimated Time**: 15-20 minutes  
**Tools**: Playwright MCP + Backend API + Screenshots

