# MCP Server Connection Issue Investigation

**Date**: 2025-11-01  
**Status**: 🟡 ROOT CAUSE IDENTIFIED  
**Impact**: Backend cannot connect to market data MCP server

---

## Issue Summary

The backend FastAPI application is running successfully at `http://localhost:8000`, but it cannot connect to the market MCP server because the Node.js MCP server is **not running**.

The error indicates:
```
⚠️ MCP Server: STDIO mode (connection failing because backend expects HTTP)
```

---

## Root Cause Analysis

### Architecture Overview

The application has **3 separate services** that need to run simultaneously:

1. **Backend** (Python/FastAPI) - Port 8000 ✅ RUNNING
2. **Frontend** (React/Vite) - Port 5174 ✅ RUNNING
3. **Market MCP Server** (Node.js) - Port 3001 ❌ **NOT RUNNING**

### Data Flow

```
Frontend (5174)
    ↓
Backend FastAPI (8000)
    ↓
Market MCP Server (3001) ← MISSING!
    ↓
Yahoo Finance API / Alpaca API
```

### Backend Configuration

The backend expects the MCP server at `http://127.0.0.1:3001/mcp`:

**File**: `backend/services/http_mcp_client.py` (Line 27)
```python
def __init__(self, base_url: str = "http://127.0.0.1:3001/mcp"):
    self.base_url = base_url
```

**File**: `backend/services/market_service_factory.py` (Line 1107)
```python
"endpoint": "http://127.0.0.1:3001/mcp",
```

### MCP Server Modes

The Node.js MCP server supports **two modes**:

1. **STDIO Mode** (default): For command-line usage
   ```bash
   npm start  # Runs in STDIO mode
   ```

2. **HTTP Mode** (required for backend): Accepts HTTP requests on port 3001
   ```bash
   npm start 3001  # Runs in HTTP mode on port 3001
   ```

**The backend requires HTTP mode on port 3001.**

---

## Evidence from Code

### MCP Server index.js (Lines 2575-2580)
```javascript
async run() {
  // Check if port is provided as command line argument
  const port = process.argv[2];
  
  if (port) {
    // StreamableHTTP mode - Official MCP transport for production
```

### Backend Connection Attempts

**File**: `backend/services/http_mcp_client.py` (Lines 346-347)
```python
logger.error(f"Failed to connect to MCP server at {self.base_url}")
raise RuntimeError(f"Cannot connect to MCP server at {self.base_url}. Is it running?")
```

This error is being triggered because the MCP server is not listening on port 3001.

---

## Current Status

### What's Working ✅
- Backend API server (FastAPI) is running on port 8000
- Frontend Vite dev server is running on port 5174
- Alpaca API integration works for basic quotes
- Backend can serve data when MCP is not required

### What's Broken ❌
- MCP server not running on port 3001
- Backend cannot fetch:
  - Comprehensive stock data with technical indicators
  - Historical price data
  - Market overview
  - CNBC movers
  - Advanced chart patterns
  - Options data
  - Sentiment analysis

### Impact on Features

| Feature | Status | Reason |
|---------|--------|--------|
| Stock Quotes (basic) | ✅ Working | Uses Alpaca directly |
| Chart Data | ⚠️ Degraded | Falls back to cached/limited data |
| Technical Indicators | ❌ Broken | Requires MCP server |
| Pattern Detection | ⚠️ Limited | Backend patterns work, but no enhanced data |
| Market Overview | ❌ Broken | Requires MCP server |
| News | ⚠️ Degraded | Limited without MCP |
| Sentiment | ❌ Broken | Requires MCP server |

---

## Solution

### Quick Fix: Start the MCP Server

#### Option 1: Start MCP Server in a 3rd Terminal (Recommended)

```bash
# Terminal 3: MCP Server
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server"

# Install dependencies (first time only)
npm install

# Start in HTTP mode on port 3001
npm start 3001
```

**Expected Output**:
```
🚀 Market MCP Server (HTTP mode)
📡 Listening on port 3001
✅ Server ready at http://127.0.0.1:3001/mcp
```

#### Option 2: Start All Services with a Script

Create a startup script to launch all three services:

**File**: `start_app.sh`
```bash
#!/bin/bash

echo "🚀 Starting claude-voice-mcp application..."

# Start MCP Server
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server"
npm start 3001 > ../logs/mcp-server.log 2>&1 &
MCP_PID=$!
echo "📡 MCP Server started (PID: $MCP_PID)"

# Wait for MCP server to be ready
sleep 3

# Start Backend
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend"
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "🐍 Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
sleep 3

# Start Frontend
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend"
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "⚛️  Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "✅ All services started!"
echo ""
echo "📝 Service URLs:"
echo "   - Frontend: http://localhost:5174"
echo "   - Backend:  http://localhost:8000"
echo "   - MCP:      http://localhost:3001"
echo ""
echo "📋 Process IDs:"
echo "   - MCP:      $MCP_PID"
echo "   - Backend:  $BACKEND_PID"
echo "   - Frontend: $FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   - MCP:      logs/mcp-server.log"
echo "   - Backend:  logs/backend.log"
echo "   - Frontend: logs/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $MCP_PID $BACKEND_PID $FRONTEND_PID"
```

Make it executable:
```bash
chmod +x start_app.sh
mkdir -p logs
./start_app.sh
```

---

## Verification Steps

### Step 1: Verify MCP Server is Running

```bash
# Check if port 3001 is listening
lsof -i :3001

# Test MCP server health
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
```

**Expected Response**: JSON-RPC response with server capabilities

### Step 2: Verify Backend Can Connect

```bash
# Test backend MCP status endpoint
curl http://localhost:8000/api/mcp/status
```

**Expected Response**:
```json
{
  "status": "connected",
  "endpoint": "http://127.0.0.1:3001/mcp",
  "tools_count": 35+
}
```

### Step 3: Test Full Integration

```bash
# Get comprehensive stock data (requires MCP)
curl "http://localhost:8000/api/comprehensive-stock-data?symbol=AAPL&days=30" | jq
```

**Expected**: Full response with technical indicators, patterns, and news

---

## Alternative: Use STDIO Mode (Not Recommended)

If you cannot run the MCP server on HTTP mode, you could modify the backend to use STDIO mode, but this would be **significantly slower** and not recommended for development.

**Why HTTP Mode is Better**:
- ⚡ 10-50x faster (no process creation overhead)
- 🔄 Connection pooling and reuse
- 📊 Better error handling with HTTP status codes
- 💾 Lower memory usage (single Node.js instance)

---

## Updated Run Instructions

### Complete 3-Service Startup

#### **Terminal 1: Market MCP Server**
```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server"
npm install  # First time only
npm start 3001
```

#### **Terminal 2: Backend**
```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend"
uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload
```

#### **Terminal 3: Frontend**
```bash
cd "/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend"
npm run dev
```

#### **Access Application**
Open browser to: **http://localhost:5174**

---

## Troubleshooting

### Issue: Port 3001 Already in Use

```bash
# Find process using port 3001
lsof -i :3001

# Kill it
kill -9 <PID>
```

### Issue: MCP Server Won't Start

```bash
# Check Node.js version (needs >= 18)
node --version

# Reinstall dependencies
cd market-mcp-server
rm -rf node_modules package-lock.json
npm install
```

### Issue: Backend Still Can't Connect

Check backend logs for exact error:
```bash
tail -f backend/logs/*.log

# Or if running in terminal, look for:
# "Failed to connect to MCP server at http://127.0.0.1:3001/mcp"
```

---

## Success Criteria

- ✅ All 3 services running (ports 8000, 5174, 3001)
- ✅ Backend can connect to MCP server
- ✅ MCP status endpoint returns "connected"
- ✅ Stock data includes technical indicators and patterns
- ✅ Chart loads with full historical data
- ✅ No "MCP server unavailable" warnings in logs

---

## Summary

**Problem**: Backend expects MCP server on HTTP mode (port 3001), but MCP server is not running.

**Solution**: Start the market MCP server with port argument:
```bash
cd market-mcp-server && npm start 3001
```

**Result**: All 3 services working together, full application functionality restored.

---

**Next Step**: Start the MCP server and verify all services are connected properly.

