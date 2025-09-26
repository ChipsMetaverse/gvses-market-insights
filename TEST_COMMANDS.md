# Test Commands for Technical Analysis Drawing Feature

## ✅ Services are Running

- **Backend**: http://localhost:8000 (PID 51172)
- **Frontend**: http://localhost:5174 (PID 52834)

## 📊 Test the Feature

### 1. Open the Application
Open your browser and go to: http://localhost:5174

### 2. Test via UI (Recommended)
In the right panel input field, try these queries:

1. **Basic Chart Switch**
   - Type: "Show me NVDA chart"
   - Expected: Chart switches to NVDA

2. **Support/Resistance Levels**
   - Type: "Show me support and resistance levels for Tesla"
   - Expected: Chart switches to TSLA and draws horizontal lines

3. **Fibonacci Retracement**
   - Type: "Display Fibonacci retracement for NVDA"
   - Expected: Fibonacci levels appear on chart

4. **Full Technical Analysis**
   - Type: "Show technical analysis with trend lines for SPY"
   - Expected: Multiple drawing elements appear

### 3. Test via API (Direct)

```bash
# Quick test - just symbol switch
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Show NVDA"}' \
  -s | python3 -m json.tool | grep chart_commands

# Technical analysis test
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"Show support and resistance for NVDA"}' \
  -s | python3 -m json.tool | grep -A 10 chart_commands
```

### 4. Check Drawing Commands
The API should return commands like:
```json
"chart_commands": [
  "CHART:NVDA",
  "SUPPORT:175.50",
  "SUPPORT:172.00",
  "RESISTANCE:185.00",
  "RESISTANCE:190.00",
  "FIBONACCI:190.00:170.00"
]
```

## 🔧 Troubleshooting

### If API is slow:
The first request takes 20-40 seconds due to:
- OpenAI API calls for response generation
- Market data fetching
- Technical analysis calculations

Subsequent requests should be faster due to caching.

### If no drawing commands appear:
1. Check backend logs: `tail -f /tmp/backend.log | grep -E "drawing|technical"`
2. Verify market data is available for the symbol
3. Try a simple query first like "NVDA" before technical queries

### If frontend doesn't show drawings:
1. Open browser console (F12)
2. Look for "Chart Command:" or "Drew" messages
3. Check if enhancedChartControl is initialized

## 📝 What's Working

✅ **Backend generates drawing commands** for:
- Support levels (SUPPORT:price)
- Resistance levels (RESISTANCE:price)  
- Fibonacci retracements (FIBONACCI:high:low)
- Trend lines (TRENDLINE:startPrice:startTime:endPrice:endTime)
- Entry/Target/Stop loss levels

✅ **Frontend executes drawings** via:
- chartControlService parses commands
- enhancedChartControl draws on chart
- Visual feedback in UI

## 🚀 Quick Verification

The fastest way to verify everything works:

1. Open http://localhost:5174
2. In the text input (right panel), type: "Show NVDA"
3. Wait for response (may take 20-30 seconds first time)
4. Chart should switch to NVDA
5. Try: "Show support levels for NVDA"
6. Horizontal lines should appear on the chart

## 📊 Expected Results

When you ask for technical analysis, you should see:
- Chart switches to requested symbol
- Horizontal lines for support/resistance
- Fibonacci levels (if swing points detected)
- Trend lines (if patterns detected)
- Professional technical analysis visualization

## 🎯 The Feature is Complete!

The agent now provides professional-grade technical analysis with automatic chart drawings based on real market data and trading knowledge.