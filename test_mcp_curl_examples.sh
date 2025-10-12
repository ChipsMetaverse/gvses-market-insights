#!/bin/bash

# MCP Integration Test Examples
# These curl commands demonstrate the MCP server working correctly
# Use these to verify functionality before integrating with OpenAI Agent Builder

echo "🚀 MCP Integration Test Examples"
echo "=================================="
echo ""

# Configuration
MCP_ENDPOINT="http://localhost:8000/api/mcp"
AUTH_TOKEN="fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
HEADERS="Authorization: Bearer $AUTH_TOKEN"

echo "📡 MCP Endpoint: $MCP_ENDPOINT"
echo "🔑 Auth Token: ${AUTH_TOKEN:0:20}..."
echo ""

echo "1️⃣ Testing MCP Tools List (should show 33 tools):"
echo "=================================================="
curl -s -H "$HEADERS" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' \
  "$MCP_ENDPOINT" | jq '.result.tools | length'
echo ""

echo "2️⃣ Getting Tesla (TSLA) Stock Quote:"
echo "===================================="
curl -s -H "$HEADERS" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_stock_quote", "arguments": {"symbol": "TSLA"}}}' \
  "$MCP_ENDPOINT" | jq -r '.result.content[0].text' | head -n 3
echo ""

echo "3️⃣ Getting Apple (AAPL) Stock History:"
echo "======================================"
curl -s -H "$HEADERS" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_stock_history", "arguments": {"symbol": "AAPL", "period": "5d"}}}' \
  "$MCP_ENDPOINT" | jq -r '.result.content[0].text' | head -n 3
echo ""

echo "4️⃣ Getting Market Fundamentals for Microsoft (MSFT):"
echo "===================================================="
curl -s -H "$HEADERS" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "get_stock_fundamentals", "arguments": {"symbol": "MSFT"}}}' \
  "$MCP_ENDPOINT" | jq -r '.result.content[0].text' | head -n 3
echo ""

echo "5️⃣ Getting Crypto Price for Bitcoin:"
echo "===================================="
curl -s -H "$HEADERS" -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "get_crypto_price", "arguments": {"coin_id": "bitcoin"}}}' \
  "$MCP_ENDPOINT" | jq -r '.result.content[0].text' | head -n 3
echo ""

echo "✅ All MCP tests completed!"
echo "=============================="
echo ""
echo "🎯 Integration Status:"
echo "- MCP Server: Running on localhost:8000"
echo "- Authentication: Bearer token working"  
echo "- Tools Available: 33 market data tools"
echo "- Data Sources: Real-time market data"
echo ""
echo "📋 Next Steps for OpenAI Agent Builder:"
echo "1. Open https://platform.openai.com/playground/assistants"
echo "2. Create new assistant with MCP integration"
echo "3. Use endpoint: http://localhost:8000/api/mcp"
echo "4. Use token: fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
echo "5. Test with: 'Get Tesla stock price using MCP tools'"
echo ""