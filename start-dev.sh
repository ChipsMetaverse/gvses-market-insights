#!/bin/bash
# Development startup script - runs all services together

echo "🚀 Starting G'sves Market Insights Development Environment"
echo "=========================================================="

# Check for required environment variables
if [ ! -f backend/.env ]; then
    echo "❌ backend/.env file not found!"
    echo "Please create it with required API keys."
    exit 1
fi

if [ ! -f frontend/.env ]; then
    echo "❌ frontend/.env file not found!"
    echo "Please create it with required Supabase keys."
    exit 1
fi

# Source backend environment for tunnel
source backend/.env

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "uvicorn mcp_server:app"
pkill -f "npm run dev"
pkill -f "lt --port"
sleep 2

# Start backend
echo "🔧 Starting backend server..."
cd backend
uvicorn mcp_server:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..
sleep 3

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
sleep 3

# Start localtunnel for webhook access
echo "🌐 Starting public tunnel..."
lt --port 8000 --subdomain gvses-backend &
TUNNEL_PID=$!
sleep 3

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Local Access:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🌐 Public Webhook URL:"
echo "   https://gvses-backend.loca.lt"
echo ""
echo "⚠️  IMPORTANT: Update the ElevenLabs tool URL to:"
echo "   https://gvses-backend.loca.lt/api/stock-price"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Trap Ctrl+C and cleanup
trap cleanup INT

cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    kill $TUNNEL_PID 2>/dev/null
    pkill -f "uvicorn mcp_server:app"
    pkill -f "npm run dev"
    pkill -f "lt --port"
    echo "✅ All services stopped"
    exit 0
}

# Wait for interrupt
while true; do
    sleep 1
done