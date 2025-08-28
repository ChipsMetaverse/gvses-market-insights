# MCP Deployment Fix for Fly.io

## Current Issue
The MCP servers are failing on production (Fly.io) with "No such file or directory" error because they are not included in the Docker image.

## Root Cause
The backend Dockerfile only copies the backend directory, not the MCP server directories:
```dockerfile
COPY backend/ .
```

This means `market-mcp-server/` and `alpaca-mcp-server/` are not available in production.

## Solution Options

### Option 1: Include MCP Servers in Docker Image (Recommended)

Update `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    python3-dev \
    curl \
    nodejs \  # Add Node.js for market-mcp-server
    npm \     # Add npm for dependencies
    && rm -rf /var/lib/apt/lists/*

# Copy and install market-mcp-server
COPY market-mcp-server/ ./market-mcp-server/
WORKDIR /app/market-mcp-server
RUN npm install

# Copy and install alpaca-mcp-server
WORKDIR /app
COPY alpaca-mcp-server/ ./alpaca-mcp-server/
RUN pip install -r alpaca-mcp-server/requirements.txt

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Expose ports
EXPOSE 8000 8080

# Run the application
CMD uvicorn mcp_server:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
```

### Option 2: Deploy MCP Servers as Separate Services

Create separate Fly.io apps for each MCP server and communicate via HTTP instead of stdio.

#### market-mcp-server deployment:
```toml
# fly.toml for market-mcp-server
app = "gvses-market-mcp"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8081"

[[services]]
  protocol = "tcp"
  internal_port = 8081
```

#### alpaca-mcp-server deployment:
```toml
# fly.toml for alpaca-mcp-server
app = "gvses-alpaca-mcp"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8082"
  ALPACA_API_KEY = "your_key"
  ALPACA_SECRET_KEY = "your_secret"

[[services]]
  protocol = "tcp"
  internal_port = 8082
```

### Option 3: Use Environment-Based Paths

Update `backend/mcp_client.py` to handle production vs development paths:
```python
def get_mcp_client() -> MCPClient:
    """Get or create the singleton MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        # Check if running in Docker/production
        if os.path.exists("/app/market-mcp-server/index.js"):
            # Production path
            server_path = "/app/market-mcp-server/index.js"
        else:
            # Development path
            server_path = "/Volumes/WD My Passport 264F Media/claude-voice-mcp/market-mcp-server/index.js"
        _mcp_client = MCPClient(server_path)
    return _mcp_client
```

## Implementation Steps

### For Option 1 (Recommended):

1. **Update Dockerfile** with the changes above

2. **Update mcp_client.py** to use relative paths:
```python
def get_mcp_client() -> MCPClient:
    global _mcp_client
    if _mcp_client is None:
        # Use relative path from backend
        project_root = Path(__file__).parent.parent
        server_path = project_root / "market-mcp-server" / "index.js"
        _mcp_client = MCPClient(str(server_path))
    return _mcp_client
```

3. **Update mcp_manager.py** similarly:
```python
async def initialize(self):
    # Get the project root
    if os.path.exists("/app"):
        # Production
        project_root = Path("/app")
    else:
        # Development
        project_root = Path(__file__).parent.parent
```

4. **Deploy to Fly.io**:
```bash
flyctl deploy --app gvses-market-insights --remote-only
```

## Testing

After deployment, test the endpoints:
```bash
# Test stock price (uses MCP)
curl "https://gvses-market-insights.fly.dev/api/stock-price?symbol=TSLA"

# Test stock history (uses MCP)
curl "https://gvses-market-insights.fly.dev/api/stock-history?symbol=TSLA&days=5"

# Test news (uses MCP)
curl "https://gvses-market-insights.fly.dev/api/stock-news?symbol=TSLA"
```

## Benefits of Option 1
- Single deployment unit
- No network latency between services
- Simpler architecture
- Easier to manage and debug

## Current Workaround
The application gracefully handles MCP server failures by returning error messages, but full functionality requires the MCP servers to be available.