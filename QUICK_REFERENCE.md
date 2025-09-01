# Quick Reference Card - ElevenLabs Agent System

## 🔑 Critical IDs & Keys
```bash
ELEVENLABS_API_KEY=sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb
AGENT_ID=agent_4901k2tkkq54f4mvgpndm3pgzm7g
BACKEND_URL=https://gvses-market-insights.fly.dev
```

## 🚀 Essential Commands

### Test Agent Configuration
```bash
curl -s -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/agents/agent_4901k2tkkq54f4mvgpndm3pgzm7g" | \
  python3 -m json.tool | grep tool_ids
```

### Test Backend
```bash
curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=AAPL"
```

### List All Tools
```bash
curl -s -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/tools" | \
  python3 -c "import sys,json; [print(f\"{t['id']}: {t['tool_config']['name']}\") for t in json.load(sys.stdin)['tools']]"
```

### Delete a Tool
```bash
curl -X DELETE -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  "https://api.elevenlabs.io/v1/convai/tools/TOOL_ID"
```

### Update Agent Tools
```bash
curl -X PATCH -H "xi-api-key: sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb" \
  -H "Content-Type: application/json" \
  "https://api.elevenlabs.io/v1/convai/agents/agent_4901k2tkkq54f4mvgpndm3pgzm7g" \
  -d '{"conversation_config":{"agent":{"prompt":{"tool_ids":["tool_id1","tool_id2"]}}}}'
```

## 📊 Tool IDs Reference
```
get_stock_price:            tool_2201k3w6qvy5epbazavdb8r2nf2w
get_market_overview:        tool_6901k3w6qw9gfs2829n49x0sncfh
get_stock_news:            tool_7101k3w6qwn5e2ts2bkds5s9n3pf
get_stock_history:         tool_2801k3w6qx0he099jc2qkzhb77h2
get_comprehensive_stock:   tool_3501k3w6qxcaf0ds5y3mdxfc0kre
get_market_movers:         tool_5401k3w6qxqdfstvcmvv7ew3rjy4
get_analyst_ratings:       tool_0101k3w6qy2wfn399ftkfjn8k2m6
get_options_chain:         tool_8001k3w6qyeqf8pvfev3r0pc4a3c
```

## 🔧 Python Scripts
```bash
# Fix agent tools
python3 fix_existing_agent_tools.py

# Clean unused tools
python3 cleanup_unused_tools.py

# Test configuration
python3 quick_test.py

# Test agent queries
python3 test_agent_queries.py
```

## 🌐 API Endpoints
```
/health                      - Health check
/api/stock-price            - Real-time prices
/api/market-overview        - Market indices
/api/stock-news            - News articles
/api/stock-history         - Historical data
/api/comprehensive-stock   - Full stock info
/api/market-movers        - Trending stocks
/api/analyst-ratings      - Analyst recommendations
/api/options-chain        - Options data
```

## 🐳 Docker Commands
```bash
docker-compose up --build   # Build and run
docker-compose logs -f      # View logs
docker-compose down         # Stop
```

## ✈️ Fly.io Commands
```bash
fly deploy                  # Deploy backend
fly status                  # Check status
fly logs --tail            # View logs
fly scale count 2          # Scale instances
```

## 🔍 Debugging Checklist
- [ ] Backend responding? `curl https://gvses-market-insights.fly.dev/health`
- [ ] Agent has tool_ids? Check configuration
- [ ] No inline tools? Should only have tool_ids
- [ ] Tools point to production? Check URLs
- [ ] USE_MCP=false in production? Check .env

## 📝 Important Notes
- **Platform Bug**: Inline tools may persist (shouldn't affect function)
- **Tool Dependencies**: May not show linked (cosmetic issue)
- **Simulation API**: May have issues, test via WebSocket instead
- **Production Mode**: Always set USE_MCP=false for performance

## 🆘 Quick Fixes

### If tools not working:
```bash
python3 fix_existing_agent_tools.py
```

### If too many tools:
```bash
python3 cleanup_unused_tools.py
```

### If backend slow:
```bash
# Ensure USE_MCP=false in backend/.env
# Redeploy: fly deploy
```

---
*Keep this handy for quick troubleshooting!*