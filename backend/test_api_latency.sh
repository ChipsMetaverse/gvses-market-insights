#!/bin/bash
# Simple API latency test script

echo "========================================="
echo "API LATENCY TEST"
echo "========================================="
echo

# Test 1: Simple price
echo "1. Testing simple price query (AAPL)..."
START=$(date +%s)
curl -sS -X POST http://localhost:8000/api/agent/orchestrate \
  -H 'Content-Type: application/json' \
  -d '{"query":"AAPL price"}' \
  -o /tmp/test_price.json
END=$(date +%s)
ELAPSED=$((END - START))
TEXT_LEN=$(jq -r '.text' /tmp/test_price.json | wc -c)
echo "   Time: ${ELAPSED}s"
echo "   Response length: ${TEXT_LEN} chars"
echo

# Test 2: Analysis without news
echo "2. Testing analysis (should skip news)..."
START=$(date +%s)
curl -sS -X POST http://localhost:8000/api/agent/orchestrate \
  -H 'Content-Type: application/json' \
  -d '{"query":"Technical analysis for NVDA"}' \
  -o /tmp/test_analysis.json
END=$(date +%s)
ELAPSED=$((END - START))
TEXT_LEN=$(jq -r '.text' /tmp/test_analysis.json | wc -c)
COMMANDS=$(jq -r '.chart_commands | length' /tmp/test_analysis.json)
echo "   Time: ${ELAPSED}s"
echo "   Response length: ${TEXT_LEN} chars"
echo "   Chart commands: ${COMMANDS}"
echo

# Test 3: News query
echo "3. Testing news query (should include news)..."
START=$(date +%s)
curl -sS -X POST http://localhost:8000/api/agent/orchestrate \
  -H 'Content-Type: application/json' \
  -d '{"query":"Latest news on TSLA"}' \
  -o /tmp/test_news.json
END=$(date +%s)
ELAPSED=$((END - START))
TEXT_LEN=$(jq -r '.text' /tmp/test_news.json | wc -c)
echo "   Time: ${ELAPSED}s"
echo "   Response length: ${TEXT_LEN} chars"
echo

echo "========================================="
echo "Checking backend logs for timing info..."
echo "========================================="
tail -100 /tmp/backend_new.log | grep -E "LLM#1|Executed.*parallel|Skipping|latency" | tail -10 || echo "No timing logs found"

echo
echo "To see more logs, run:"
echo "  tail -100 /tmp/backend_new.log | grep orchestrate"