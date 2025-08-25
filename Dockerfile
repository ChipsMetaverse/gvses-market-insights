FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    portaudio19-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Expose ports
EXPOSE 8000
EXPOSE 8080

# Run the application
CMD uvicorn mcp_server:app --host 0.0.0.0 --port ${PORT:-8000}