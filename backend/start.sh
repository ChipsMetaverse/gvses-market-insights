#!/bin/bash

# Start MCP Server in the background with port 3001
cd /app/market-mcp-server
node index.js 3001 &
MCP_PID=$!

echo "Started MCP server (PID: $MCP_PID)"

# Wait for MCP server to be ready
sleep 2

# Start FastAPI server in the foreground
cd /app
uvicorn mcp_server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2

# If FastAPI exits, kill the MCP server
kill $MCP_PID

