#!/bin/bash
# Check tools count

# Initialize new session
curl -s -D /tmp/headers-check.txt -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {},
      "clientInfo": {"name": "test", "version": "1.0"}
    },
    "id": 1
  }' > /dev/null

# Get session ID
SID=$(grep -i "^Mcp-Session-Id:" /tmp/headers-check.txt | awk '{print $2}' | tr -d '\r\n')
echo "Session ID: $SID"

# List tools
echo "Tools count:"
curl -s -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }' | jq '.result.tools | length'

echo -e "\nTool names:"
curl -s -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -H "Mcp-Session-Id: $SID" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }' | jq -r '.result.tools[].name'
