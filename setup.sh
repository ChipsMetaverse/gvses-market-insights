#!/bin/bash

# Claude Voice MCP Server - Quick Setup Script

echo "🔧 Claude Voice MCP Server - Quick Setup"
echo "========================================="
echo ""

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check system requirements
echo "📋 Checking system requirements..."

REQUIREMENTS_MET=true

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    echo "✅ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found"
    REQUIREMENTS_MET=false
fi

# Check Node
if command_exists node; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js $NODE_VERSION found"
else
    echo "❌ Node.js not found"
    REQUIREMENTS_MET=false
fi

# Check npm
if command_exists npm; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm $NPM_VERSION found"
else
    echo "❌ npm not found"
    REQUIREMENTS_MET=false
fi

# Check Docker (optional)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    echo "✅ Docker $DOCKER_VERSION found (optional)"
else
    echo "ℹ️  Docker not found (optional - can run locally)"
fi

if [ "$REQUIREMENTS_MET" = false ]; then
    echo ""
    echo "⚠️  Please install missing requirements and run this script again."
    exit 1
fi

echo ""
echo "📦 Setting up environment files..."

# Setup backend .env
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env and add:"
    echo "   - ANTHROPIC_API_KEY (required)"
    echo "   - SUPABASE_URL (optional)"
    echo "   - SUPABASE_ANON_KEY (optional)"
else
    echo "✅ backend/.env already exists"
fi

# Setup frontend .env
if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✅ Created frontend/.env from template"
    echo ""
    echo "ℹ️  Note: Edit frontend/.env if using Supabase"
else
    echo "✅ frontend/.env already exists"
fi

echo ""
echo "🎯 Setup Options:"
echo "1) Install dependencies and run locally"
echo "2) Use Docker Compose"
echo "3) Exit (manual setup)"
echo ""
read -p "Choose an option (1-3): " OPTION

case $OPTION in
    1)
        echo ""
        echo "📦 Installing Python dependencies..."
        cd backend
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        echo "✅ Python dependencies installed"
        cd ..
        
        echo ""
        echo "📦 Installing Node dependencies..."
        cd frontend
        npm install --silent
        echo "✅ Node dependencies installed"
        cd ..
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "To start the application, run:"
        echo "  ./start.sh"
        echo ""
        echo "Or start services manually:"
        echo "  Backend:  cd backend && source venv/bin/activate && uvicorn mcp_server:app --reload"
        echo "  Frontend: cd frontend && npm run dev"
        ;;
        
    2)
        echo ""
        echo "🐳 Building Docker containers..."
        docker-compose build
        echo ""
        echo "✅ Docker setup complete!"
        echo ""
        echo "To start the application, run:"
        echo "  docker-compose up"
        ;;
        
    3)
        echo ""
        echo "ℹ️  Manual setup selected."
        echo ""
        echo "Next steps:"
        echo "1. Edit backend/.env with your API keys"
        echo "2. Install Python dependencies: cd backend && pip install -r requirements.txt"
        echo "3. Install Node dependencies: cd frontend && npm install"
        echo "4. Run the application using ./start.sh or manually"
        ;;
        
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📚 Documentation: See README.md for detailed instructions"
echo "🔗 Access points:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
