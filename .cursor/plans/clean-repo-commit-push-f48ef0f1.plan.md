---
name: Pattern Recognition with Knowledge Base Integration
overview: ""
todos:
  - id: 6500a74c-3559-4e9e-bf23-d99f8de036ff
    content: Add API key authentication middleware to market-mcp-server/index.js
    status: pending
  - id: 2be055fb-c890-473e-95ff-7544f9e66c2b
    content: Implement origin validation in MCP server
    status: pending
  - id: f5658c15-c6fb-41e9-804a-4cbf3be1ede6
    content: Add express-rate-limit to prevent abuse
    status: pending
  - id: 7fac87d7-3dc1-4a59-bfc6-b8de8e05082e
    content: Update protocol version to 2025-06-18 and add validation
    status: pending
  - id: 2b2a2402-bae0-4bd8-879c-e7adacd1c2c7
    content: Update Python client to send API key header
    status: pending
  - id: 6e496f78-d8af-4799-b986-ebe8ef580134
    content: Add streaming capability to server capabilities response
    status: pending
  - id: 7f6d657d-9db4-4e97-b554-23d8c4a0de39
    content: Refactor streamMarketNews to use true SSE with event-stream headers
    status: pending
  - id: a955e5a1-53ff-4def-8ace-a15130a1cb16
    content: Add call_tool_streaming method to HTTPMCPClient for SSE
    status: pending
  - id: ee29a343-77e7-4227-822c-12b736b3c0cf
    content: Add EventSource handling to TradingDashboardSimple.tsx
    status: pending
  - id: 91fb3bde-8734-4f23-b5ef-bc5b85a5ed82
    content: Create /api/mcp/stream-news endpoint in FastAPI backend
    status: pending
  - id: e6ab3fc8-ec45-4287-a06b-de3e97251a89
    content: Add ENABLE_STREAMING environment variable and feature flag
    status: pending
  - id: 28d20343-e5e9-45e9-910d-82338ff19ed6
    content: Test security features (auth, origin, rate limit) with existing clients
    status: pending
  - id: 3cb63638-19d1-450f-afc5-a5dda3229c2c
    content: Test streaming with manual test script and real clients
    status: pending
  - id: 69e84c82-e728-414c-b449-742024b350f0
    content: Create STREAMING_IMPLEMENTATION.md with usage guide and examples
    status: pending
---

# Pattern Recognition with Knowledge Base Integration

## Phase 1: Knowledge-Driven Pattern Validation

### 1.1 Load Structured Pattern Knowledge

**File**: `backend/pattern_detection.py`

Create a new `PatternLibrary` class that loads `backend/training/patterns.json` at module import:

```python
class PatternLibrary:
    """Loads and provides access to validated pattern definitions."""
    
    def __init__(self, patterns_file: Path = None):
        if patterns_file is None:
            patterns_file = Path(__file__).parent / "training" / "patterns.json"
        
        with open(patterns_file) as f:
            self.patterns = {p["pattern_id"]: p for p in json.load(f)}
    
    def get_recognition_rules(self, pattern_id: str) -> Dict:
        """Returns candle_structure, trend_context, volume_confirmation, invalidations"""
        return self.patterns.get(pattern_id, {}).get("recognition_rules", {})
    
    def get_trading_playbook(self, pattern_id: str) -> Dict:
        """Returns signal, entry, stop_loss, targets, risk_notes"""
        return self.patterns.get(pattern_id, {}).get("trading_playbook", {})
    
    def validate_against_rules(self, pattern_id: str, candles: List[Dict], metadata: Dict) -> Tuple[bool, float, str]:
        """
        Validate detected pattern against knowledge base rules.
        Returns: (is_valid, confidence_adjustment, reasoning)
        """
        rules = self.get_recognition_rules(pattern_id)
        # Check invalidations, trend context, volume confirmation
        # Return detailed reasoning for confidence score
```

### 1.2 Enhance Pattern Detectors with Knowledge Validation

**File**: `backend/pattern_detection.py`

Refactor each pattern detector method (e.g., `_detect_head_shoulders`, `_detect_triangles`, `_detect_cup_handle`) to:

1. Run existing geometric detection (keep current logic as "candidate detection")
2. Pass candidates to `PatternLibrary.validate_against_rules()` for knowledge-based validation
3. Apply confidence adjustments based on validation results
4. Enrich pattern metadata with knowledge base fields:

   - Add `entry`, `stop_loss`, `targets` from `trading_playbook`
   - Add `invalidations` from `recognition_rules`
   - Add `description` and `risk_notes` for UI display

Example for Head and Shoulders:

```python
def _detect_head_shoulders(self, peaks, troughs):
    # Existing geometric detection...
    candidates = []  # List of geometrically valid patterns
    
    library = PatternLibrary()
    validated_patterns = []
    
    for candidate in candidates:
        # Validate against knowledge base
        is_valid, conf_adj, reasoning = library.validate_against_rules(
            "head_and_shoulders",
            self.candles,
            candidate.metadata
        )
        
        if is_valid:
            # Enrich with knowledge base data
            playbook = library.get_trading_playbook("head_and_shoulders")
            candidate.confidence += conf_adj
            candidate.action = "watch_closely"
            candidate.entry_guidance = playbook.get("entry")
            candidate.stop_loss_guidance = playbook.get("stop_loss")
            candidate.targets_guidance = playbook.get("targets")
            candidate.risk_notes = playbook.get("risk_notes")
            validated_patterns.append(candidate)
    
    return validated_patterns
```

### 1.3 Remove Arbitrary Threshold Adjustments

**File**: `backend/pattern_detection.py`

Replace the proposed threshold changes (0.4→0.6, etc.) with knowledge-driven validation. Instead of relaxing thresholds blindly, patterns must pass:

- Geometric structure test (existing logic, keep strict)
- Knowledge base validation (candle_structure, trend_context, volume_confirmation)
- Invalidation checks (ensure none of the invalidation conditions are met)

Confidence scores will now reflect alignment with knowledge base criteria, not arbitrary slope tolerances.

## Phase 2: Frontend Chart Visualization

### 2.1 Pattern Overlay Rendering System

**File**: `frontend/src/components/TradingDashboardSimple.tsx`

Add state for pattern visualization:

```typescript
// Pattern visualization state
const [visiblePatterns, setVisiblePatterns] = useState<Set<string>>(new Set());
const [hoveredPattern, setHoveredPattern] = useState<string | null>(null);
```

Add `useEffect` to automatically render patterns when detected:

```typescript
useEffect(() => {
  if (!detectedPatterns || detectedPatterns.length === 0) return;
  
  // Automatically show all patterns on initial load
  const allPatternIds = new Set(detectedPatterns.map(p => p.pattern_id));
  setVisiblePatterns(allPatternIds);
  
  // Draw patterns on chart
  detectedPatterns.forEach(pattern => {
    if (pattern.chart_metadata) {
      drawPatternOverlay(pattern);
    }
  });
}, [detectedPatterns]);
```

Create `drawPatternOverlay` function:

```typescript
const drawPatternOverlay = useCallback((pattern: Pattern) => {
  if (!chartControlRef.current || !pattern.chart_metadata) return;
  
  const { trendlines, levels } = pattern.chart_metadata;
  
  // Clear existing pattern overlays for this pattern_id
  chartControlRef.current.clearPattern(pattern.pattern_id);
  
  // Draw trendlines
  trendlines?.forEach((trendline: any) => {
    chartControlRef.current.drawTrendline(
      trendline.start.time,
      trendline.start.price,
      trendline.end.time,
      trendline.end.price,
      {
        color: trendline.type === 'upper_trendline' ? '#ef4444' : '#3b82f6',
        lineWidth: 2,
        lineStyle: 0, // solid
        patternId: pattern.pattern_id
      }
    );
  });
  
  // Draw horizontal levels
  levels?.forEach((level: any) => {
    const color = level.type === 'support' ? '#10b981' : '#ef4444';
    chartControlRef.current.drawHorizontalLine(
      level.price,
      {
        color,
        lineWidth: 1,
        lineStyle: 2, // dashed
        patternId: pattern.pattern_id
      }
    );
  });
}, []);
```

### 2.2 Pattern List Panel with Interactive Controls

**File**: `frontend/src/components/TradingDashboardSimple.tsx`

Replace the "No patterns detected" message with an interactive pattern list:

```typescript
{/* PATTERN DETECTION section - around line 1480 */}
<div className="panel-section">
  <div className="section-header">
    PATTERN DETECTION
  </div>
  <div className="pattern-list">
    {detectedPatterns.length === 0 ? (
      <div className="analysis-item">
        <p className="news-text">No patterns detected. Try different timeframes or symbols.</p>
      </div>
    ) : (
      detectedPatterns.map((pattern, index) => (
        <div
          key={pattern.pattern_id || index}
          className={`pattern-item ${hoveredPattern === pattern.pattern_id ? 'hovered' : ''}`}
          onMouseEnter={() => {
            setHoveredPattern(pattern.pattern_id);
            // Highlight on chart during hover
            if (pattern.chart_metadata) {
              highlightPattern(pattern);
            }
          }}
          onMouseLeave={() => {
            setHoveredPattern(null);
            clearHighlight();
          }}
          onClick={() => {
            // Toggle pattern visibility
            setVisiblePatterns(prev => {
              const next = new Set(prev);
              if (next.has(pattern.pattern_id)) {
                next.delete(pattern.pattern_id);
                chartControlRef.current?.clearPattern(pattern.pattern_id);
              } else {
                next.add(pattern.pattern_id);
                drawPatternOverlay(pattern);
              }
              return next;
            });
          }}
        >
          <div className="pattern-header">
            <span className="pattern-name">{pattern.pattern_type}</span>
            <span className={`pattern-signal ${pattern.signal}`}>
              {pattern.signal === 'bullish' ? '↑' : pattern.signal === 'bearish' ? '↓' : '•'} {pattern.signal}
            </span>
            <label className="pattern-toggle">
              <input
                type="checkbox"
                checked={visiblePatterns.has(pattern.pattern_id)}
                onChange={() => {}} // Handled by onClick above
              />
              <span className="checkmark"></span>
            </label>
          </div>
          <div className="pattern-details">
            <span className="confidence">Confidence: {pattern.confidence}%</span>
            {pattern.entry_guidance && (
              <Tooltip content={pattern.entry_guidance}>
                <span className="guidance-label">Entry</span>
              </Tooltip>
            )}
            {pattern.risk_notes && (
              <Tooltip content={pattern.risk_notes}>
                <span className="risk-icon">⚠️</span>
              </Tooltip>
            )}
          </div>
        </div>
      ))
    )}
  </div>
</div>
```

### 2.3 Pattern Styling

**File**: `frontend/src/components/TradingDashboardSimple.tsx` (inline styles section)

Add CSS for pattern list:

```css
.pattern-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pattern-item {
  padding: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.pattern-item:hover,
.pattern-item.hovered {
  background: #eff6ff;
  border-color: #3b82f6;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
}

.pattern-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.pattern-name {
  font-weight: 600;
  color: #111827;
  text-transform: capitalize;
}

.pattern-signal {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.pattern-signal.bullish {
  background: #d1fae5;
  color: #065f46;
}

.pattern-signal.bearish {
  background: #fee2e2;
  color: #991b1b;
}

.pattern-signal.neutral {
  background: #f3f4f6;
  color: #4b5563;
}

.pattern-toggle input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.pattern-details {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #6b7280;
}

.confidence {
  font-weight: 500;
}

.guidance-label {
  padding: 2px 6px;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 4px;
  font-weight: 500;
}

.risk-icon {
  cursor: help;
}
```

## Phase 3: Enhanced Chart Control Integration

### 3.1 Extend Chart Control with Pattern Management

**File**: `frontend/src/services/enhancedChartControl.ts`

Add pattern-specific drawing methods:

```typescript
// Pattern overlay management
private patternOverlays: Map<string, any[]> = new Map();

clearPattern(patternId: string): void {
  const overlays = this.patternOverlays.get(patternId);
  if (overlays) {
    overlays.forEach(overlay => overlay.remove());
    this.patternOverlays.delete(patternId);
  }
}

drawTrendline(
  startTime: number,
  startPrice: number,
  endTime: number,
  endPrice: number,
  options: { color: string; lineWidth: number; lineStyle: number; patternId: string }
): void {
  const trendline = this.chart.createTrendLine({
    start: { time: startTime, price: startPrice },
    end: { time: endTime, price: endPrice },
    options: {
      color: options.color,
      lineWidth: options.lineWidth,
      lineStyle: options.lineStyle
    }
  });
  
  // Store for cleanup
  if (!this.patternOverlays.has(options.patternId)) {
    this.patternOverlays.set(options.patternId, []);
  }
  this.patternOverlays.get(options.patternId)!.push(trendline);
}

drawHorizontalLine(price: number, options: any): void {
  const line = this.chart.createPriceLine({
    price,
    color: options.color,
    lineWidth: options.lineWidth,
    lineStyle: options.lineStyle
  });
  
  if (!this.patternOverlays.has(options.patternId)) {
    this.patternOverlays.set(options.patternId, []);
  }
  this.patternOverlays.get(options.patternId)!.push(line);
}

highlightPattern(patternId: string): void {
  const overlays = this.patternOverlays.get(patternId);
  if (overlays) {
    overlays.forEach(overlay => {
      // Temporarily increase opacity/width for highlight effect
      overlay.applyOptions({ lineWidth: 3 });
    });
  }
}

clearHighlight(): void {
  this.patternOverlays.forEach(overlays => {
    overlays.forEach(overlay => {
      overlay.applyOptions({ lineWidth: 2 });
    });
  });
}
```

## Phase 4: Testing & Validation

### 4.1 Backend Testing

Create `backend/test_knowledge_patterns.py`:

```python
# Test knowledge-driven pattern detection
def test_pattern_library_loading():
    library = PatternLibrary()
    assert "head_and_shoulders" in library.patterns
    assert "cup_and_handle" in library.patterns
    assert "bullish_engulfing" in library.patterns

def test_pattern_validation_with_knowledge():
    # Create synthetic candles matching head_and_shoulders rules
    candles = create_head_and_shoulders_candles()
    detector = PatternDetector(candles)
    patterns = detector.detect_all_patterns()
    
    # Should detect pattern with high confidence
    hs_patterns = [p for p in patterns if p.pattern_type == "head_and_shoulders"]
    assert len(hs_patterns) > 0
    assert hs_patterns[0].confidence >= 75
    assert "entry_guidance" in hs_patterns[0].__dict__

def test_invalidation_conditions():
    # Create candles that violate invalidation rules
    candles = create_invalid_head_and_shoulders()
    detector = PatternDetector(candles)
    patterns = detector.detect_all_patterns()
    
    # Should NOT detect pattern due to invalidation
    hs_patterns = [p for p in patterns if p.pattern_type == "head_and_shoulders"]
    assert len(hs_patterns) == 0
```

### 4.2 Integration Testing

```bash
# Restart backend with knowledge integration
cd backend && uvicorn mcp_server:app --host 0.0.0.0 --port 8000

# Test comprehensive API with volatile symbols
curl -s "http://localhost:8000/api/comprehensive-stock-data?symbol=GME" | jq '.patterns.detected[] | {type, confidence, entry_guidance, chart_metadata}'
curl -s "http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA" | jq '.patterns.detected[] | {type, confidence, entry_guidance, chart_metadata}'
curl -s "http://localhost:8000/api/comprehensive-stock-data?symbol=NVDA" | jq '.patterns.detected[] | {type, confidence, entry_guidance, chart_metadata}'
```

### 4.3 Frontend Visual Testing

1. Load dashboard at `http://localhost:5174`
2. Switch to volatile symbol (GME, TSLA, BTC)
3. Change timeframe to 1D, 1W, 1M to trigger different patterns
4. Verify:

   - Patterns automatically appear in left panel
   - Clicking pattern name toggles chart overlay
   - Hovering pattern highlights trendlines/levels
   - Tooltips show entry/stop-loss/targets from knowledge base
   - Visual overlays match pattern metadata exactly

## Success Criteria

1. Pattern detection uses `backend/training/patterns.json` for validation
2. Confidence scores reflect knowledge base alignment, not arbitrary thresholds
3. Detected patterns include `entry_guidance`, `stop_loss_guidance`, `targets_guidance`, `risk_notes` from playbook
4. Frontend displays interactive pattern list with checkboxes
5. Clicking pattern toggles chart overlay (trendlines, support, resistance)
6. Hovering pattern highlights it on chart
7. Pattern visualization metadata (trendlines, levels) renders correctly
8. Tooltips display entry/exit guidance from knowledge base
9. System detects 3-5 patterns for volatile symbols (GME, TSLA, BTC) across different timeframes
10. No false positives - all detected patterns pass knowledge base validation

## Files Modified

**Backend:**

- `backend/pattern_detection.py` (major refactor: add PatternLibrary class, enhance all detectors)
- `backend/services/market_service_factory.py` (minor: ensure entry_guidance fields passed through)
- `backend/test_knowledge_patterns.py` (new file: comprehensive testing)

**Frontend:**

- `frontend/src/components/TradingDashboardSimple.tsx` (add pattern list UI, overlay rendering, interactive controls)
- `frontend/src/services/enhancedChartControl.ts` (extend with pattern management methods)

**No threshold changes** - pattern detection remains strict, knowledge base provides validation and enrichment.