"""
Standalone Drawing Persistence Server
FastAPI application for testing drawing CRUD operations
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv

from api import router

# Load environment variables
load_dotenv()

# ============================================================================
# FastAPI Application Setup
# ============================================================================

app = FastAPI(
    title="Drawing Persistence API",
    description="Standalone server for testing trading chart drawing persistence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://localhost:3000", "*"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include drawing router
app.include_router(router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ============================================================================
# Root Endpoint
# ============================================================================

@app.get("/")
async def root():
    """API information endpoint"""
    return {
        "name": "Drawing Persistence API",
        "version": "1.0.0",
        "status": "running",
        "frontend": "/static/index.html",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/drawings/health",
            "drawings": "/api/drawings"
        },
        "usage": {
            "create": "POST /api/drawings",
            "list": "GET /api/drawings?symbol=TSLA",
            "get": "GET /api/drawings/{id}",
            "update": "PATCH /api/drawings/{id}",
            "delete": "DELETE /api/drawings/{id}",
            "batch": "POST /api/drawings/batch",
            "stats": "GET /api/drawings/stats/summary"
        }
    }


@app.get("/health")
async def health():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "drawing-persistence"
    }


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Create a .env file with:")
        print("   SUPABASE_URL=https://your-project.supabase.co")
        print("   SUPABASE_ANON_KEY=your-anon-key")
        exit(1)

    print("🚀 Starting Drawing Persistence Server...")
    print("📚 API Docs: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("\n✨ Ready to test drawing persistence!\n")

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
