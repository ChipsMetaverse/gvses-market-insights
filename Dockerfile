# Multi-stage build for optimized image size
FROM node:22-slim AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ .
RUN npm run build

# Final production image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (minimal set)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    python3-dev \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Node.js 22 (minimal install)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy built frontend from builder stage
RUN rm -rf /usr/share/nginx/html/*
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html/

# Setup market-mcp-server (production dependencies only)
COPY market-mcp-server/package*.json ./market-mcp-server/
WORKDIR /app/market-mcp-server
RUN npm ci --only=production && npm cache clean --force

# Copy MCP server source
COPY market-mcp-server/ .

# Install Python dependencies for alpaca-mcp-server
WORKDIR /app
COPY alpaca-mcp-server/ ./alpaca-mcp-server/
RUN pip install --no-cache-dir mcp>=1.0.0 alpaca-py>=0.33.0 python-dotenv>=1.0.0

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy configuration files
COPY nginx.conf /etc/nginx/sites-available/default
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Clean up build dependencies to reduce image size
RUN apt-get remove -y gcc g++ python3-dev curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip cache purge

# Expose ports
EXPOSE 8080

# Start supervisor
ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]