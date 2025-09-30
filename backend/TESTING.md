# Testing Documentation

## Overview
This document describes the testing procedures for the GVSES backend system, including regression testing, smoke testing, and production deployment validation.

## Test Suites

### 1. Production Smoke Tests
**Purpose**: Validate critical functionality for production readiness

**Run Locally**:
```bash
cd backend
python3 production_smoke_tests.py
```

**Expected Results**:
- ✅ 7/7 tests passing
- Cached responses: <500ms
- Uncached responses: <5s (OpenAI limited to ~8s)
- No Supabase foreign key errors

### 2. Supabase Session Validation
**Purpose**: Verify Supabase schema and session handling

```bash
cd backend
python3 test_supabase_session.py
```

**Tests**:
- Schema inspection
- UUID format validation
- Upsert pattern testing
- Foreign key constraints
- Required fields verification

### 3. Regression Testing

#### Docker-based (Production-like)
```bash
# Build test image
docker build -t gvses-test .

# Run regression suite
docker run --rm gvses-test python3 test_backward_compatibility.py

# Run smoke tests
docker run --rm gvses-test python3 production_smoke_tests.py
```

#### Local Testing (Platform Warning)
```bash
cd backend

# Run with platform warning
python3 test_backward_compatibility.py
# ⚠️ Warning: Results may differ from production environment

# Basic API tests
python3 test_server.py
python3 test_dual_mcp.py
python3 test_alpaca_mcp.py
```

#### Phase 5 ML Flow Smoke Tests
- **Purpose**: Validate ML model registry fallbacks and champion artifact loading prior to enabling Phase 5 in production.

```bash
# Run from repo root
pytest backend/tests/test_phase5_ml_flow.py

# Optional: retrain models used by tests (skips optional boosters if unavailable)
PYTHONPATH=. python backend/ml/pattern_confidence.py --models random_forest logistic
```

## Environment Variables

### Required for Testing
```bash
# backend/.env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-key
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
AGENT_MODEL=gpt-5-mini  # Fastest model
```

### Optional Test Configuration
```bash
# Cache configuration
CACHE_WARM_ON_STARTUP=true    # Enable/disable cache warming
CACHE_WARM_TIMEOUT=30          # Max seconds for cache warming

# Metrics protection
METRICS_TOKEN=your-secret-token

# Model selection
AGENT_MODEL=gpt-5-mini        # Options: gpt-5, gpt-5-mini
```

## Performance Benchmarks

### Current Performance (as of implementation)
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Cached Response | <500ms | 289ms | ✅ |
| Uncached Response | <5s | 7.9s | ⚠️ (OpenAI limit) |
| Cache Hit Rate | >40% | 50%+ with warming | ✅ |
| Startup Time | <60s | ~35s with cache warming | ✅ |
| Memory Usage | <500MB | ~350MB | ✅ |

### Test Commands for Performance
```bash
# Test cached response time
time curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RSI?", "session_id": "test-perf"}'

# Test metrics endpoint
curl http://localhost:8000/metrics \
  -H "Authorization: Bearer ${METRICS_TOKEN}"
```

## Streaming Endpoint Testing

### Test Streaming Response
```bash
# Test streaming endpoint (if implemented)
curl -N -X POST http://localhost:8000/api/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain MACD indicator"}'
```

### WebSocket Testing
```javascript
// Test WebSocket connection
const ws = new WebSocket('ws://localhost:8000/ws/quotes');
ws.onmessage = (event) => console.log(event.data);
```

## CI/CD Pipeline

### GitHub Actions Workflow (Recommended)
Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        cd backend
        python3 test_server.py
        python3 production_smoke_tests.py
  
  docker-build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t gvses-backend:test .
    
    - name: Run regression tests in Docker
      run: |
        docker run --rm \
          -e SUPABASE_URL=${{ secrets.SUPABASE_URL }} \
          -e SUPABASE_ANON_KEY=${{ secrets.SUPABASE_ANON_KEY }} \
          gvses-backend:test python3 production_smoke_tests.py
  
  deploy:
    runs-on: ubuntu-latest
    needs: docker-build
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Fly.io
      env:
        FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
      run: |
        curl -L https://fly.io/install.sh | sh
        export PATH="$HOME/.fly/bin:$PATH"
        fly deploy --remote-only
```

### Local CI Simulation
```bash
# Run full test suite locally
cd backend
./run_tests.sh

# Content of run_tests.sh:
#!/bin/bash
set -e

echo "Running Supabase validation..."
python3 test_supabase_session.py

echo "Running production smoke tests..."
python3 production_smoke_tests.py

echo "Testing API endpoints..."
python3 test_server.py

echo "All tests passed!"
```

## Deployment Validation

### Pre-Deployment Checklist
- [ ] All tests passing locally
- [ ] UUID session IDs working
- [ ] Cache warming < 30s
- [ ] Metrics endpoint secured
- [ ] Environment variables set

### Post-Deployment Validation
```bash
# 1. Health check
curl https://your-app.fly.dev/health

# 2. Run smoke tests against production
python3 production_smoke_tests.py --url https://your-app.fly.dev

# 3. Verify Supabase persistence
curl -X POST https://your-app.fly.dev/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Test message", "session_id": "$(uuidgen)"}'

# 4. Check metrics (with auth)
curl https://your-app.fly.dev/metrics \
  -H "Authorization: Bearer ${METRICS_TOKEN}"

# 5. Monitor logs
fly logs --app your-app-name
```

## Troubleshooting

### Common Issues

#### UUID Format Errors
**Problem**: `invalid input syntax for type uuid`
**Solution**: Ensure session IDs use proper UUID format (not `test-session-XXX`)

#### Cache Warming Timeout
**Problem**: Startup takes too long
**Solution**: Set `CACHE_WARM_ON_STARTUP=false` or increase `CACHE_WARM_TIMEOUT`

#### Slow Uncached Responses
**Problem**: Responses take >8s
**Solution**: This is OpenAI API latency. Consider:
- Using streaming responses
- Switching to `gpt-5` or `gpt-5-mini`
- Implementing client-side loading indicators

## Rollback Procedure

If deployment fails:
```bash
# Get previous deployment ID
fly releases --app your-app-name

# Rollback to previous version
fly deploy --image registry.fly.io/your-app:v123

# Restore environment if needed
fly secrets set AGENT_MODEL=gpt-5-mini

# Verify rollback
curl https://your-app.fly.dev/health
```
