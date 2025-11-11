# ForexFactory MCP Server

A Model Context Protocol (MCP) server for retrieving economic calendar events from ForexFactory using Playwright-based web scraping.

## Features

- **FastMCP Framework**: Built on the modern FastMCP framework for rapid MCP server development
- **Playwright Scraping**: Headless Chromium browser automation for reliable data extraction
- **Flexible Time Ranges**: Support for predefined periods (today, tomorrow, this_week, etc.) and custom date ranges
- **HTTP Transport**: Production-ready HTTP endpoint for Docker/remote integration
- **Structured Events**: Returns normalized event data with consistent field names
- **Configurable**: Environment-based configuration with sensible defaults

## Architecture

```
forex-mcp-server/
├── src/forex_mcp/
│   ├── models/           # Event and TimePeriod models
│   ├── services/         # ForexFactory scraper service
│   ├── tools/            # MCP tool definitions
│   ├── utils/            # Event normalization utilities
│   ├── settings.py       # Configuration management
│   └── server.py         # Main entrypoint
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker build configuration
└── README.md            # This file
```

## Installation

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium

# Copy environment configuration
cp .env.example .env

# Run the server
python src/forex_mcp/server.py --transport http --host 0.0.0.0 --port 3002
```

### Docker

```bash
# Build the image
docker build -t forex-mcp-server .

# Run the container
docker run -p 3002:3002 forex-mcp-server

# Or use docker-compose
docker-compose up -d forex-mcp-server
```

## Configuration

Environment variables can be set in `.env` file:

```bash
# MCP Server Configuration
MCP_TRANSPORT=http       # stdio | http | sse
MCP_HOST=0.0.0.0        # Bind address
MCP_PORT=3002           # HTTP port

# Scraper Configuration
SCRAPER_TIMEOUT_MS=5000  # Playwright timeout

# Namespace
NAMESPACE=ffcal         # Tool prefix
```

## MCP Tool: ffcal_get_calendar_events

Retrieve ForexFactory calendar events for a given time period or custom date range.

### Parameters

- `time_period` (optional): Named period such as:
  - `today`, `tomorrow`, `yesterday`
  - `this_week`, `next_week`, `last_week`
  - `this_month`, `next_month`, `last_month`
  - `custom` (requires start_date and end_date)

- `start_date` (optional): Start date in YYYY-MM-DD format (required for custom)
- `end_date` (optional): End date in YYYY-MM-DD format (required for custom)

### Returns

List of event objects with fields:

```json
{
  "id": "12345",
  "title": "Non-Farm Payrolls",
  "currency": "USD",
  "impact": 3,
  "datetime": "2025-11-10T13:30:00+00:00",
  "forecast": "200K",
  "previous": "180K",
  "actual": "210K",
  "datetime_utc": "2025-11-10T13:30:00+00:00",
  "datetime_local": "2025-11-10T08:30:00-05:00"
}
```

### Example Usage (via HTTP)

```bash
# Get today's events
curl -X POST http://localhost:3002/tools/ffcal_get_calendar_events \
  -H "Content-Type: application/json" \
  -d '{"time_period": "today"}'

# Get next week's events
curl -X POST http://localhost:3002/tools/ffcal_get_calendar_events \
  -H "Content-Type: application/json" \
  -d '{"time_period": "next_week"}'

# Get custom date range
curl -X POST http://localhost:3002/tools/ffcal_get_calendar_events \
  -H "Content-Type: application/json" \
  -d '{
    "time_period": "custom",
    "start_date": "2025-11-10",
    "end_date": "2025-11-15"
  }'
```

## Integration with Backend

The backend server can connect to this MCP server via HTTP on port 3002:

```python
# backend/services/forex_service.py
import httpx

async def get_forex_calendar(time_period: str = "today"):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:3002/tools/ffcal_get_calendar_events",
            json={"time_period": time_period},
            timeout=10.0
        )
        return response.json()
```

Backend endpoint:

```python
# backend/mcp_server.py
@app.get("/api/forex/calendar")
async def get_forex_calendar(
    time_period: str = "today",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Retrieve ForexFactory calendar events.

    Returns:
        List of economic calendar events
    """
    # Call forex-mcp-server via HTTP
    return await forex_service.get_calendar_events(
        time_period=time_period,
        start_date=start_date,
        end_date=end_date
    )
```

## Event Fields

### Standard Fields
- `id`: Unique event identifier
- `title`: Event name (e.g., "Non-Farm Payrolls")
- `currency`: Affected currency code (e.g., "USD")
- `impact`: Impact level (1=Low, 2=Medium, 3=High)
- `datetime`: Event datetime (ISO 8601 format)
- `forecast`: Forecasted value
- `previous`: Previous value
- `actual`: Actual value (after event occurs)

### Enriched Fields (automatically added)
- `datetime_utc`: Event time in UTC timezone
- `datetime_local`: Event time in local timezone (configurable)

## Performance

- **Scraper Timeout**: 5 seconds (configurable)
- **Response Time**: ~2-5 seconds depending on ForexFactory page load
- **Caching**: Not implemented (can be added at backend level)

## Error Handling

The server includes comprehensive error handling:

- Invalid time periods → Returns helpful error message with valid options
- Malformed dates → Returns date format validation error
- Scraping failures → Logs detailed error and returns empty array
- Browser crashes → Automatic cleanup and error logging

## Logging

Logs are written to stderr with the following format:

```
[11/10/25 10:30:15] INFO     Starting ForexFactory MCP server (transport=http) server.py:123
[11/10/25 10:30:15] INFO     Server configuration: host=0.0.0.0, port=3002 server.py:124
[11/10/25 10:30:20] INFO     Scraping ForexFactory: https://www.forexfactory.com/calendar?day=today ff_scraper_service.py:137
```

## Testing

```bash
# Test the server is running
curl http://localhost:3002/health

# Test calendar tool
python -c "
import asyncio
import httpx

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://localhost:3002/tools/ffcal_get_calendar_events',
            json={'time_period': 'today'},
            timeout=10.0
        )
        print(response.json())

asyncio.run(test())
"
```

## Troubleshooting

### Playwright Issues

```bash
# Reinstall browsers
playwright install chromium --force
playwright install-deps chromium
```

### Port Already in Use

```bash
# Change port in .env or command line
python src/forex_mcp/server.py --port 3003
```

### Timeout Errors

```bash
# Increase timeout in .env
SCRAPER_TIMEOUT_MS=10000
```

## Security Considerations

- **Headless Browser**: Runs in sandboxed environment with `--no-sandbox` flag
- **No Credentials**: No authentication required for ForexFactory (public data)
- **Rate Limiting**: Consider implementing rate limiting if deploying publicly
- **Network Access**: Requires outbound HTTPS access to www.forexfactory.com

## License

MIT License - See LICENSE file for details

## Credits

Based on the forexfactory-mcp repository patterns and adapted for the claude-voice-mcp project architecture.
