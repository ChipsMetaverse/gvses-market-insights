FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Node.js for MCP servers
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    python3-dev \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy and setup market-mcp-server (Node.js)
COPY market-mcp-server/ ./market-mcp-server/
WORKDIR /app/market-mcp-server
RUN npm install

# Copy and setup alpaca-mcp-server (Python)
WORKDIR /app
COPY alpaca-mcp-server/ ./alpaca-mcp-server/
RUN pip install -r alpaca-mcp-server/requirements.txt

# Copy and setup forex-mcp-server (Python + Playwright)
WORKDIR /app
COPY forex-mcp-server/ ./forex-mcp-server/
RUN pip install --no-cache-dir -r forex-mcp-server/requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Make startup script executable
RUN chmod +x start.sh

# Expose port (8080 for Fly.io, 8000 for local)
EXPOSE 8000
EXPOSE 8080

# Run both MCP server and FastAPI server
CMD ["/bin/bash", "./start.sh"]
