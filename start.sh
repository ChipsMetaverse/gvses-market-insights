#!/bin/bash

# Claude Voice MCP Server - Startup Script

echo "🚀 Starting Claude Voice MCP Server..."

# Check for required environment variables
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Backend .env file not found!"
    echo "Creating from template..."
    cp backend/.env.example backend/.env
    echo "Please edit backend/.env with your API keys"
    exit 1
fi

if [ ! -f "frontend/.env" ]; then
    echo "⚠️  Frontend .env file not found!"
    echo "Creating from template..."
    cp frontend/.env.example frontend/.env
    echo "Please edit frontend/.env if using Supabase"
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Docker
if command_exists docker && command_exists docker-compose; then
    echo "🐳 Docker detected. Starting with Docker Compose..."
    docker-compose up --build
else
    echo "📦 Starting services locally..."
    
    # Check for Python
    if ! command_exists python3; then
        echo "❌ Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
    
    # Check for Node
    if ! command_exists node; then
        echo "❌ Node.js not found. Please install Node.js 20+"
        exit 1
    fi
    
    # Install backend dependencies if needed
    if [ ! -d "backend/venv" ]; then
        echo "📦 Creating Python virtual environment..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
    
    # Install frontend dependencies if needed
    if [ ! -d "frontend/node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    # Start backend
    echo "🔧 Starting backend server..."
    cd backend
    source venv/bin/activate
    uvicorn mcp_server:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    echo "🎨 Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "   Frontend: http://localhost:5173"
    echo "   Backend:  http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services..."
    
    # Wait for interrupt
    trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
    wait
fi
