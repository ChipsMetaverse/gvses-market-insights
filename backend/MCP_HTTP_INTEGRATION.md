# HTTP MCP Integration for OpenAI Agent Builder

This document explains how to integrate the GVSES Market Analysis MCP server with OpenAI Agent Builder using the HTTP endpoint.

## Overview

The system provides both WebSocket and HTTP access to MCP tools:

- **WebSocket endpoint**: `/mcp` (for real-time streaming)
- **HTTP endpoint**: `/api/mcp` or `/mcp/http` (for OpenAI Agent Builder)

## OpenAI Agent Builder Configuration

### 1. MCP Server URL
```
https://your-domain.com/api/mcp
```

### 2. Authentication
Choose one of these methods:

**Option A: Authorization Header**
```
Authorization: Bearer fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
```

**Option B: Query Parameter**
```
https://your-domain.com/api/mcp?token=fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
```

### 3. Supported JSON-RPC Methods

#### Initialize
```json
{
  "jsonrpc": "2.0",
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-01",
    "capabilities": {"tools": {}},
    "clientInfo": {"name": "openai-agent", "version": "1.0.0"}
  },
  "id": "init-1"
}
```

#### List Tools
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": "list-1"
}
```

#### Call Tool
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_stock_quote",
    "arguments": {"symbol": "AAPL"}
  },
  "id": "call-1"
}
```

## Available Market Data Tools

The MCP server provides 35+ market data tools including:

### Stock Data
- `get_stock_quote` - Real-time stock quotes
- `get_stock_history` - Historical price data
- `get_stock_news` - Company news and analysis
- `get_earnings_calendar` - Upcoming earnings
- `get_financial_statements` - Company financials

### Market Analysis
- `get_market_overview` - Market indices and trends
- `get_sector_performance` - Sector analysis
- `get_trending_stocks` - Popular stocks
- `get_gainers_losers` - Top movers

### Technical Analysis
- `get_technical_indicators` - RSI, MACD, etc.
- `get_support_resistance` - Key levels
- `get_chart_patterns` - Pattern recognition

### Options & Derivatives
- `get_options_chain` - Options data
- `get_options_flow` - Unusual activity
- `get_crypto_prices` - Cryptocurrency data

## Testing the Integration

Run the test script to verify the HTTP endpoint works:

```bash
cd backend
python3 test_mcp_http_endpoint.py
```

This will test:
- Authentication (header and query param)
- Initialize handshake
- List available tools
- Call a sample tool
- Error handling

## Architecture

```
OpenAI Agent Builder
         ↓ HTTP JSON-RPC
    FastAPI HTTP Endpoint (/api/mcp)
         ↓ Bridge
    MCP WebSocket Transport
         ↓ stdio
    Market MCP Server (Node.js)
         ↓ APIs
    Yahoo Finance + CNBC
```

## Security Notes

1. **Authentication Required**: All requests must include valid Fly.io token
2. **CORS Enabled**: Frontend access allowed (development mode)
3. **Rate Limiting**: Uses slowapi for request throttling
4. **Error Handling**: Proper JSON-RPC error responses

## Status & Health Checks

Check MCP server status:
```bash
curl https://your-domain.com/mcp/status
```

Response includes:
- Transport initialization status
- Active WebSocket sessions
- MCP client connection health
- Available tools count

## Troubleshooting

### Common Issues

1. **401 Authentication Error**
   - Verify token format: `fo1_...`
   - Check Authorization header or query param

2. **MCP Client Not Initialized**
   - Ensure market-mcp-server is running
   - Check Node.js version (requires 22+)
   - Verify server path in backend config

3. **Tool Call Failures**
   - Check market-mcp-server logs
   - Verify tool name and parameters
   - Test with WebSocket endpoint first

### Debug Commands

```bash
# Check server health
curl https://your-domain.com/health

# Check MCP status
curl https://your-domain.com/mcp/status

# Test HTTP MCP endpoint
python3 test_mcp_http_endpoint.py

# Check market-mcp-server directly
cd market-mcp-server && npm start
```

## Production Deployment

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
ELEVENLABS_API_KEY=...

# Market Data
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...

# Database
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

### Docker Configuration
The system runs in Docker with Node.js 22 for MCP server compatibility:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - USE_MCP=true  # Enable MCP features
```

### Scaling Considerations

- **Concurrent Sessions**: Configurable limit (default: 10)
- **Session Timeout**: Auto-cleanup after 300s
- **Memory Usage**: Node.js optimized for Docker
- **API Rate Limits**: Yahoo Finance and CNBC respecting

## Integration Examples

### Simple Stock Quote
```python
import httpx

async def get_stock_price(symbol):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://your-domain.com/api/mcp",
            json={
                "jsonrpc": "2.0",
                "method": "tools/call", 
                "params": {
                    "name": "get_stock_quote",
                    "arguments": {"symbol": symbol}
                },
                "id": "quote-1"
            },
            headers={"Authorization": "Bearer fo1_..."}
        )
        return response.json()
```

### Market Overview
```python
async def get_market_summary():
    # Call get_market_overview tool
    response = await client.post(
        "https://your-domain.com/api/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_market_overview", 
                "arguments": {}
            },
            "id": "market-1"
        },
        headers={"Authorization": "Bearer fo1_..."}
    )
    return response.json()
```

This HTTP MCP integration enables OpenAI Agent Builder to access professional market data through a simple, standards-compliant interface.