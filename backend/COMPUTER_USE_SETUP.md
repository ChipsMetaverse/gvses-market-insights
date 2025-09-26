# Computer Use Verification Setup Guide

## Overview

This guide explains how to set up and use OpenAI's Computer Use feature (Responses API, `computer-use-preview`) together with Python Playwright to automatically verify and debug the trading app's UI behavior. Computer Use lets the AI visually interact with your app, run test scenarios, and identify issues.

## Prerequisites

1. **OpenAI API Key** with Computer Use access (Responses API)
2. **Local development environment** running:
   - Backend: `uvicorn mcp_server:app --host 0.0.0.0 --port 8000`
   - Frontend: `npm run dev` (port 5174)
3. **Tunnel software** to expose localhost (ngrok, cloudflared, or localtunnel)
4. Python Playwright runtime (browser install)

## Setup Instructions

### Step 1: Install Tunnel Software

Computer Use runs in OpenAI's cloud and needs a public URL to access your local app.

#### Option A: ngrok (Recommended)
```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Create tunnel
ngrok http 5174

# Note the public URL (e.g., https://abc123.ngrok.io)
```

#### Option B: Cloudflared
```bash
# Install cloudflared
brew install cloudflared  # macOS

# Create tunnel
cloudflared tunnel --url http://localhost:5174

# Note the public URL
```

#### Option C: Localtunnel
```bash
# Install via npm
npm install -g localtunnel

# Create tunnel
lt --port 5174

# Note the public URL
```

### Step 2: Configure Environment

Add these variables to your `backend/.env` file:

```bash
# Computer Use Configuration
USE_COMPUTER_USE=true
TUNNEL_URL=https://your-tunnel-url.ngrok.io  # Replace with your tunnel URL

# Existing OpenAI configuration
OPENAI_API_KEY=your-openai-api-key
```

### Step 3: Install Playwright browser

Install the Chromium browser for Playwright (first time only):

```bash
python -m playwright install chromium
```

### Step 4: Mount Computer Use Router

The router is automatically mounted when available. Verify it's working:

```bash
# In backend/mcp_server.py, add this import:
from routers.computer_use_router import router as computer_use_router
app.include_router(computer_use_router)
```

### Step 5: Create OpenAI Agent (Dashboard Method) (optional)

1. Go to [OpenAI Dashboard](https://platform.openai.com/agents)
2. Create new Agent with:
   - **Name**: Trading App Verifier
   - **Model**: GPT-4o or GPT-4.1
   - **Tools**: Enable "Computer Use" and "Browser"
   - **Instructions**: (paste the following)

```
You are a QA engineer testing a trading web application.

Test Checklist:
1. Open [TUNNEL_URL] and verify UI loads
2. Test "What is PLTR?"
   - EXPECTED: Explanation of Palantir Technologies as a data analytics company
   - EXPECTED: Chart switches to PLTR
   - ACTUAL: Record what you see
   
3. Test "Show me Microsoft"  
   - EXPECTED: Chart switches to MSFT
   - ACTUAL: Record if chart changes
   
4. Test "What is artificial intelligence?"
   - EXPECTED: General explanation of AI
   - ACTUAL: Note if you get trading data instead
   
5. Test "Show 4hr chart for META"
   - EXPECTED: Chart shows META with 4H timeframe
   - ACTUAL: Check timeframe indicator

For each test:
- Take screenshot before and after
- Note expected vs actual behavior
- If something fails, suggest the fix with:
  - File path (e.g., backend/services/agent_orchestrator.py)
  - Line number range
  - Specific code change needed

Common issue locations:
- Intent classification: agent_orchestrator.py lines 3285-3312
- Chart commands: agent_orchestrator.py lines 865-1055
- Query routing: agent_orchestrator.py lines 3344-3438
```

## Running Verification

### Method 1: API Endpoints

```bash
# Start verification session
curl -X POST http://localhost:8000/api/verification/run \
  -H "Content-Type: application/json" \
  -d '{"tunnel_url": "https://your-tunnel.ngrok.io"}'

# Check status
curl http://localhost:8000/api/verification/status/{session_id}

# Get report
curl http://localhost:8000/api/verification/report/{session_id}

# Quick check (synchronous)
curl -X POST http://localhost:8000/api/verification/quick-check
```

### Method 2: CLI Script

```bash
# Run all scenarios
python backend/tools/run_computer_use_verification.py \
  --tunnel-url https://your-tunnel.ngrok.io

# Run specific scenarios
python backend/tools/run_computer_use_verification.py \
  --scenarios "Company Information - PLTR,Chart Symbol Synchronization"

# Quick check only
python backend/tools/run_computer_use_verification.py --quick

# View existing report
python backend/tools/run_computer_use_verification.py \
  --report-only {session_id}
```

### Method 3: Direct Agent Session

1. Start a session with your agent in OpenAI Dashboard
2. Send this message:
```
Please run the full verification checklist on https://your-tunnel.ngrok.io
Include screenshots and a pass/fail summary with suggested fixes.
```

## Test Scenarios

### Critical Tests

1. **Company Information**: "What is PLTR?" should explain the company
2. **Chart Sync**: "Show MSFT" should switch chart to MSFT  
3. **General Queries**: "What is AI?" should not return stock data

### Full Test Suite

See `backend/config/computer_use_scenarios.yaml` for complete scenarios including:
- Technical analysis with timeframes
- Sequential symbol changes
- Voice assistant integration
- Error recovery
- Performance benchmarks

## Understanding Results

### Report Structure

```json
{
  "session_id": "uuid",
  "summary": {
    "total_scenarios": 8,
    "passed": 6,
    "failed": 2,
    "success_rate": "75.0%"
  },
  "issues": [
    {
      "scenario": "Company Information - PLTR",
      "expected": "Company description",
      "actual": "Trading levels only",
      "priority": "Critical"
    }
  ],
  "suggested_fixes": [
    {
      "file": "backend/services/agent_orchestrator.py",
      "line": "3286",
      "description": "Add company-info intent before price-only check",
      "code": "if 'what is' in ql and self._extract_symbol(query): return 'company-info'"
    }
  ]
}
```

### Common Issues and Fixes

| Issue | Symptom | Fix Location |
|-------|---------|--------------|
| No company info | "What is X?" returns price | agent_orchestrator.py:3286 |
| Chart doesn't sync | Symbol discussed ≠ chart shown | agent_orchestrator.py:865 |
| General queries fail | Non-trading questions error | agent_orchestrator.py:3344 |
| Wrong timeframe | 4hr → H4 not mapped | agent_orchestrator.py:888 |

## Troubleshooting

### Tunnel Not Working
- Ensure frontend is running on port 5174
- Check CORS settings allow tunnel domain
- Try different tunnel service if one fails

### Agent Can't Access App
- Verify tunnel URL is correct in .env
- Check if app loads in regular browser via tunnel URL
- Ensure no authentication blocking access

### Tests Timing Out
- Increase timeout in scenarios.yaml
- Check if backend/frontend are responding
- Monitor server logs for errors

### Computer Use Not Available
- Ensure OPENAI_API_KEY has Agents beta access
- Check USE_COMPUTER_USE=true is set
- Verify agent has Computer Use tool enabled

## Best Practices

1. **Run tests after changes**: Verify fixes work
2. **Save screenshots**: Evidence for debugging
3. **Review suggested fixes**: Agent provides specific code locations
4. **Test incrementally**: Fix critical issues first
5. **Monitor performance**: Keep response times under SLA

## Integration with CI/CD

While Computer Use is great for interactive debugging, keep Playwright for CI:

```yaml
# .github/workflows/test.yml
- name: Playwright Tests (CI)
  run: npm run test:e2e

- name: Computer Use Verification (Manual)
  if: github.event_name == 'workflow_dispatch'
  run: python backend/tools/run_computer_use_verification.py --quick
```

## Next Steps

1. Set up tunnel and get public URL
2. Configure environment variables
3. Run quick verification: `--quick` flag
4. Review report and implement fixes
5. Re-run full suite to confirm

## Support

- Reports saved to: `backend/verification_reports/`
- Logs available in: `backend/logs/`
- Issues? Check `backend/AGENTS.md` for documented problems
