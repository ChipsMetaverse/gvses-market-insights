# Alpaca MCP Server

Professional market data and trading execution via Alpaca Markets API, exposed as an MCP server.

## Features

- Real-time market quotes and snapshots
- Historical bar data with multiple timeframes
- Account information and portfolio management
- Order placement and management (paper trading)
- Position tracking and P&L monitoring

## Setup

1. Install dependencies:
```bash
pip3 install -r requirements.txt
```

2. Set environment variables:
```bash
export ALPACA_API_KEY="your_api_key"
export ALPACA_SECRET_KEY="your_secret_key"
export ALPACA_BASE_URL="https://paper-api.alpaca.markets"  # or live URL
```

3. Run the server:
```bash
python3 server.py
```

## Available Tools

### Account Management
- `get_account` - Account info, buying power, portfolio value
- `get_positions` - All open positions with P&L
- `get_orders` - Orders by status (open/closed/all)

### Market Data
- `get_stock_quote` - Latest bid/ask quotes
- `get_stock_bars` - Historical OHLCV bars
- `get_stock_snapshot` - Comprehensive market snapshot
- `get_latest_bar` - Most recent bar data
- `get_market_status` - Market hours and status

### Trading (Paper Only)
- `place_market_order` - Submit market orders
- `place_limit_order` - Submit limit orders
- `cancel_order` - Cancel pending orders

## Integration with Backend

The backend can use this server alongside the existing market-mcp-server:

```python
# In backend configuration
MCP_SERVERS = [
    {
        "name": "market-mcp-server",
        "command": ["node", "market-mcp-server/index.js"],
        "env": {}
    },
    {
        "name": "alpaca-mcp-server", 
        "command": ["python3", "alpaca-mcp-server/server.py"],
        "env": {
            "ALPACA_API_KEY": os.getenv("ALPACA_API_KEY"),
            "ALPACA_SECRET_KEY": os.getenv("ALPACA_SECRET_KEY"),
            "ALPACA_BASE_URL": os.getenv("ALPACA_BASE_URL")
        }
    }
]
```

## Data Format

All responses are JSON formatted with appropriate error handling:

```json
{
  "symbol": "AAPL",
  "ask_price": 195.50,
  "bid_price": 195.45,
  "ask_size": 100,
  "bid_size": 200,
  "timestamp": "2025-08-26T14:30:00Z"
}
```

## Security

- API keys are loaded from environment variables only
- Paper trading enforced for order placement
- All errors are caught and logged appropriately
- Stdout reserved for JSON-RPC protocol only