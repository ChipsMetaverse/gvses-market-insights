#!/bin/bash

echo "=== Verifying Production Deployment ==="
echo ""

# Health check
echo "1. Health Check:"
curl -s https://gvses-market-insights.fly.dev/health | python3 -m json.tool

echo ""
echo "2. Stock Price (Testing Alpaca):"
curl -s "https://gvses-market-insights.fly.dev/api/stock-price?symbol=AAPL" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'   Price: ${data.get(\"price\", \"N/A\")}, Source: {data.get(\"data_source\", \"unknown\")}')"

echo ""
echo "3. Stock News (Testing MCP):"
curl -s "https://gvses-market-insights.fly.dev/api/stock-news?symbol=AAPL&limit=3" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f'   News count: {data.get(\"total\", 0)}, Source: {data.get(\"source\", \"unknown\")}')"

echo ""
echo "4. Response Times:"
echo -n "   Stock Price: "
time -p curl -s "https://gvses-market-insights.fly.dev/api/stock-price?symbol=TSLA" > /dev/null 2>&1

echo ""
echo "=== Deployment Verification Complete ==="