FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (8080 for Fly.io, 8000 for local)
EXPOSE 8000
EXPOSE 8080

# Run the application (PORT env var for production)
CMD uvicorn mcp_server:app --host 0.0.0.0 --port ${PORT:-8000}
