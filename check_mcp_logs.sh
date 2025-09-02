#!/bin/bash

echo "=== Checking MCP Server Logs in Production ==="
echo ""

echo "1. Checking backend logs for MCP startup:"
fly logs --app gvses-market-insights | grep -E "MCP|mcp" | tail -20

echo ""
echo "2. Testing news endpoint:"
curl -s "https://gvses-market-insights.fly.dev/api/stock-news?symbol=AAPL&limit=3" | python3 -m json.tool

echo ""
echo "3. SSH into container to check processes:"
echo "Run: fly ssh console --app gvses-market-insights"
echo "Then: ls -la /app/market-mcp-server/"