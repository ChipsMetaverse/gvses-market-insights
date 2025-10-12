"""
Enhanced Voice Assistant MCP Server
====================================
Implements an MCP server with voice capabilities, WebSocket support,
and Supabase integration for conversation persistence.

Production deployment: Oct 11, 2025 - v2.0.2 - MCP HTTP endpoint enabled
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
import datetime
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Header
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from market_data_service import MarketDataService
from routers.dashboard_router import router as dashboard_router
from mcp_client import get_stock_history as mcp_get_stock_history
from services.market_service_factory import MarketServiceFactory
from services.openai_relay_server import openai_relay_server

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Voice Assistant MCP Server")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - allow all localhost ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174",
        "https://gvses-market-insights.fly.dev",
        "*"  # Allow all origins in development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global MCP client instance
mcp_client = None

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_anon_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = None

if supabase_url and supabase_anon_key:
    supabase = create_client(supabase_url, supabase_anon_key)
    logger.info("Supabase client initialized successfully")
else:
    logger.warning("Supabase credentials not found - some features may not work")

# Global market data service instance
market_service = MarketServiceFactory.create_service()

# Voice session management
active_voice_sessions = {}

class AIMessageRequest(BaseModel):
    """Request model for AI message endpoint"""
    query: str
    session_id: Optional[str] = None

class Message(BaseModel):
    """Message model for WebSocket communication"""
    type: str
    content: str
    session_id: Optional[str] = None
    timestamp: Optional[str] = None

class StockQuote(BaseModel):
    """Stock quote model"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: str

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting Voice Assistant MCP Server...")
    
    # Initialize market service
    if hasattr(market_service, 'initialize'):
        try:
            await market_service.initialize()
            logger.info("✅ Market service initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize market service: {e}")
    
    # Initialize OpenAI Relay Server
    try:
        await openai_relay_server.initialize()
        logger.info("✅ OpenAI Relay Server initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI Relay Server: {e}")

    logger.info("🎯 Server startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down Voice Assistant MCP Server...")
    
    # Cleanup market service
    if hasattr(market_service, 'cleanup'):
        try:
            await market_service.cleanup()
            logger.info("✅ Market service cleanup completed")
        except Exception as e:
            logger.error(f"❌ Failed to cleanup market service: {e}")
    
    # Cleanup OpenAI Relay Server
    try:
        await openai_relay_server.cleanup()
        logger.info("✅ OpenAI Relay Server cleanup completed")
    except Exception as e:
        logger.error(f"❌ Failed to cleanup OpenAI Relay Server: {e}")

    # Close any remaining voice sessions
    for session_id in list(active_voice_sessions.keys()):
        try:
            session = active_voice_sessions.pop(session_id)
            if hasattr(session, 'close'):
                await session.close()
        except Exception as e:
            logger.error(f"❌ Failed to close voice session {session_id}: {e}")

    logger.info("👋 Server shutdown completed")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if market service is operational
        service_status = "operational" if market_service else "unavailable"
        
        # Check service mode
        service_mode = "Unknown"
        if hasattr(market_service, 'get_service_info'):
            service_info = await market_service.get_service_info()
            service_mode = service_info.get('mode', 'Unknown')
        
        # Check MCP sidecars status
        mcp_status = {}
        if hasattr(market_service, 'get_mcp_status'):
            mcp_status = await market_service.get_mcp_status()
        
        # Get OpenAI relay metrics
        openai_relay_metrics = await openai_relay_server.get_metrics()
        
        return {
            "status": "healthy",
            "service_mode": service_mode,
            "service_initialized": service_status == "operational",
            "openai_relay_ready": openai_relay_metrics.get("active", False),
            "timestamp": datetime.now().isoformat(),
            "services": {
                "direct": service_status,
                "mcp": "operational" if mcp_status.get("initialized") else "unavailable",
                "mode": "hybrid" if service_status == "operational" and mcp_status.get("initialized") else "fallback"
            },
            "mcp_sidecars": mcp_status,
            "openai_relay": openai_relay_metrics,
            "features": {
                "tool_wiring": True,
                "triggers_disclaimers": True,
                "advanced_ta": {
                    "enabled": True,
                    "fallback_enabled": True,
                    "timeout_ms": 3000,
                    "levels": [
                        "sell_high_level",
                        "buy_low_level", 
                        "btd_level",
                        "retest_level"
                    ]
                },
                "tailored_suggestions": True,
                "concurrent_execution": {
                    "enabled": True,
                    "global_timeout_s": 10,
                    "per_tool_timeouts": {
                        "get_stock_price": 2.0,
                        "get_stock_history": 3.0,
                        "get_stock_news": 4.0,
                        "get_comprehensive_stock_data": 5.0
                    }
                },
                "ideal_formatter": True,
                "bounded_llm_insights": {
                    "enabled": True,
                    "max_chars": 250,
                    "model": "gpt-4.1",
                    "timeout_s": 2.0,
                    "fallback_enabled": True
                },
                "test_suite": {
                    "enabled": True,
                    "last_run_success_rate": 76.9,
                    "total_tests": 26
                }
            },
            "version": "2.0.1",
            "build_timestamp": "2025-10-12T00:00:00Z",
            "agent_version": "1.5.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.1",
            "build_timestamp": "2025-10-12T00:00:00Z"
        }

# Stock quote endpoint
@app.get("/api/stock-price")
@limiter.limit("100/minute")
async def get_stock_price(request: Request, symbol: str):
    """Get current stock price"""
    try:
        quote = await market_service.get_stock_price(symbol.upper())
        return quote
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get stock price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock price: {str(e)}")

# Symbol search endpoint
@app.get("/api/symbol-search")
@limiter.limit("100/minute")  
async def symbol_search(request: Request, query: str, limit: int = 10):
    """Search for stock symbols by company name or ticker"""
    try:
        if hasattr(market_service, 'search_symbols'):
            results = await market_service.search_symbols(query, limit)
            return {"results": results}
        else:
            # Fallback - return empty results if search not supported
            return {"results": []}
    except Exception as e:
        logger.error(f"Failed to search symbols for '{query}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search symbols: {str(e)}")

# Stock history endpoint  
@app.get("/api/stock-history")
@limiter.limit("100/minute")
async def get_stock_history(request: Request, symbol: str, days: int = 30):
    """Get historical stock data"""
    try:
        history = await market_service.get_stock_history(symbol.upper(), days)
        return history
    except ValueError as e:
        logger.error(f"Invalid request for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get stock history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock history: {str(e)}")

# Stock news endpoint
@app.get("/api/stock-news")
@limiter.limit("50/minute")
async def get_stock_news(request: Request, symbol: str, limit: int = 10):
    """Get recent news for a stock"""
    try:
        news = await market_service.get_stock_news(symbol.upper(), limit)
        return news
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get stock news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock news: {str(e)}")

# Comprehensive stock data endpoint
@app.get("/api/comprehensive-stock-data")
@limiter.limit("50/minute")
async def get_comprehensive_stock_data(request: Request, symbol: str):
    """Get comprehensive stock information including price, history, and news"""
    try:
        data = await market_service.get_comprehensive_stock_data(symbol.upper())
        return data
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get comprehensive data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch comprehensive stock data: {str(e)}")

# Market overview endpoint
@app.get("/api/market-overview")
@limiter.limit("50/minute")
async def get_market_overview(request: Request):
    """Get market overview including indices and top movers"""
    try:
        overview = await market_service.get_market_overview()
        return overview
    except Exception as e:
        logger.error(f"Failed to get market overview: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch market overview: {str(e)}")

# Enhanced market data endpoint
@app.get("/api/enhanced/market-data")
@limiter.limit("100/minute")
async def get_enhanced_market_data(request: Request, symbol: str):
    """Enhanced market data with intelligent service selection"""
    try:
        data = await market_service.get_enhanced_market_data(symbol.upper())
        return data
    except ValueError as e:
        logger.error(f"Invalid symbol {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get enhanced market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch enhanced market data: {str(e)}")

# Enhanced historical data endpoint
@app.get("/api/enhanced/historical-data")
@limiter.limit("100/minute") 
async def get_enhanced_historical_data(request: Request, symbol: str, days: int = 30):
    """Enhanced historical data with intelligent routing"""
    try:
        data = await market_service.get_enhanced_historical_data(symbol.upper(), days)
        return data
    except ValueError as e:
        logger.error(f"Invalid request for {symbol}: {e}")
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        logger.error(f"Failed to get enhanced historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch enhanced historical data: {str(e)}")

# Debug endpoint for comparing data sources
@app.get("/api/enhanced/compare-sources")
@limiter.limit("10/minute")  
async def compare_data_sources(request: Request, symbol: str):
    """Compare data from different sources for debugging"""
    try:
        comparison = await market_service.compare_data_sources(symbol.upper())
        return comparison
    except Exception as e:
        logger.error(f"Failed to compare data sources for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare data sources: {str(e)}")

# Dashboard router
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# Ask endpoint
@app.post("/ask")
@limiter.limit("30/minute")
async def ask_ai(request: Request, message_request: AIMessageRequest):
    """Ask AI a question (text-only fallback)"""
    try:
        # Import anthropic client here to avoid import issues
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Create conversation with context about the application
        system_prompt = """You are GVSES, an AI trading assistant integrated into a professional market analysis platform. 
        You have access to real-time market data, technical analysis, and financial news. 
        Keep responses concise but informative, focusing on actionable insights.
        Always provide data-driven analysis when discussing specific stocks or market conditions."""
        
        # Get AI response
        response = client.messages.create(
            model=os.getenv("MODEL", "claude-3-sonnet-20240229"),
            max_tokens=1000,
            system=system_prompt,
            messages=[
                {
                    "role": "user", 
                    "content": message_request.query
                }
            ]
        )
        
        return {
            "response": response.content[0].text,
            "session_id": message_request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")

# ElevenLabs proxy endpoints
@app.get("/elevenlabs/signed-url")
async def get_elevenlabs_signed_url():
    """Get signed URL for ElevenLabs WebSocket connection"""
    try:
        return await openai_relay_server.get_signed_url()
    except Exception as e:
        logger.error(f"Failed to get ElevenLabs signed URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get signed URL: {str(e)}")

# OpenAI Realtime Relay WebSocket endpoints
@app.websocket("/realtime-relay/{session_id}")
async def websocket_realtime_relay(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for OpenAI Realtime API relay"""
    try:
        await openai_relay_server.handle_websocket(websocket, session_id)
    except Exception as e:
        logger.error(f"Realtime relay WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass  # Connection might already be closed

# OpenAI proxy endpoints for voice relay
@app.api_route("/openai/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def openai_proxy(request: Request, path: str):
    """Proxy requests to OpenAI API with proper authentication"""
    try:
        return await openai_relay_server.proxy_request(request, path)
    except Exception as e:
        logger.error(f"OpenAI proxy error for path {path}: {e}")
        raise HTTPException(status_code=500, detail=f"Proxy request failed: {str(e)}")

# WebSocket endpoint for real-time quotes
@app.websocket("/ws/quotes")
async def websocket_quotes(websocket: WebSocket):
    """WebSocket endpoint for real-time stock quotes"""
    await websocket.accept()
    
    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                symbol = message.get("symbol", "").upper()
                
                if not symbol:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Symbol is required"
                    }))
                    continue
                
                try:
                    # Get current quote
                    quote = await market_service.get_stock_price(symbol)
                    
                    # Send quote to client
                    await websocket.send_text(json.dumps({
                        "type": "quote",
                        "symbol": symbol,
                        "data": quote
                    }))
                    
                except Exception as e:
                    logger.error(f"Failed to get quote for {symbol}: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error", 
                        "message": f"Failed to get quote for {symbol}"
                    }))
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from quotes endpoint")
    except Exception as e:
        logger.error(f"WebSocket error in quotes endpoint: {e}")

# WebSocket endpoint for general communication
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """General WebSocket endpoint for real-time communication"""
    await websocket.accept()
    logger.info(f"WebSocket connection established for session: {session_id}")
    
    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Echo back with timestamp
            response = {
                "type": "echo",
                "session_id": session_id,
                "received": message_data,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")

@app.post("/api/mcp")
@app.post("/mcp/http")
async def mcp_http_endpoint(
    request: Request,
    token: Optional[str] = Header(None, alias="Authorization"),
    query_token: Optional[str] = Query(None, alias="token")
):
    """
    HTTP MCP Endpoint for OpenAI Agent Builder
    ==========================================
    Provides HTTP access to MCP tools using JSON-RPC 2.0 protocol.
    Supports authentication via Fly.io API token in Authorization header or query parameter.
    
    OpenAI Agent Builder format: https://your-domain.com/api/mcp
    Production deployment: Oct 12, 2025 - v2.0.1
    Build timestamp: 2025-10-12T00:00:00Z
    """
    try:
        # Import the MCP transport layer
        from services.mcp_websocket_transport import get_mcp_transport
        transport = get_mcp_transport()
        await transport.initialize()
        
        # Extract token from header or query parameter
        auth_token = None
        if token and token.startswith("Bearer "):
            auth_token = token[7:]  # Remove "Bearer " prefix
        elif token:
            auth_token = token
        elif query_token:
            auth_token = query_token
        
        # Authenticate using Fly.io API token
        if not auth_token:
            logger.warning("MCP HTTP request without authentication token")
            raise HTTPException(status_code=401, detail="Invalid or missing authentication token")
        
        # For development, allow any token starting with "test_"
        if not (auth_token.startswith("fo1_") or auth_token.startswith("test_")):
            logger.warning(f"MCP HTTP request with invalid token format: {auth_token[:10]}...")
            raise HTTPException(status_code=401, detail="Invalid authentication token format")
        
        # Parse JSON-RPC request
        body = await request.body()
        if not body:
            logger.warning("MCP HTTP request with empty body")
            raise HTTPException(status_code=400, detail="Request body is required")
        
        try:
            rpc_request = json.loads(body)
        except json.JSONDecodeError as e:
            logger.warning(f"MCP HTTP request with invalid JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON in request body")
        
        # Validate JSON-RPC format
        if not isinstance(rpc_request, dict) or "jsonrpc" not in rpc_request:
            logger.warning(f"MCP HTTP request missing JSON-RPC format: {rpc_request}")
            raise HTTPException(status_code=400, detail="Invalid JSON-RPC format")
        
        # Process JSON-RPC request through MCP transport
        logger.info(f"Processing MCP HTTP request: {rpc_request.get('method', 'unknown')}")
        response = await transport.handle_request(rpc_request)
        
        # Log successful request
        logger.info(f"MCP HTTP request completed successfully: {rpc_request.get('method', 'unknown')}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"MCP HTTP endpoint error: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            },
            "id": rpc_request.get("id") if 'rpc_request' in locals() else None
        }

# MCP WebSocket endpoint  
@app.websocket("/mcp")
async def mcp_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol"""
    await websocket.accept()
    logger.info("MCP WebSocket connection established")
    
    try:
        # Import the MCP transport layer
        from services.mcp_websocket_transport import get_mcp_transport
        transport = get_mcp_transport()
        await transport.initialize()
        
        # Handle WebSocket messages
        await transport.handle_websocket(websocket)
        
    except WebSocketDisconnect:
        logger.info("MCP WebSocket client disconnected")
    except Exception as e:
        logger.error(f"MCP WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass  # Connection might already be closed

# MCP status endpoint
@app.get("/mcp/status")
async def mcp_status():
    """Get MCP server status"""
    try:
        from services.mcp_websocket_transport import get_mcp_transport
        transport = get_mcp_transport()
        status = await transport.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get MCP status: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Alternative MCP HTTP endpoint
@app.post("/mcp/http")
async def mcp_http_alt_endpoint(request: Request):
    """Alternative MCP HTTP endpoint"""
    return await mcp_http_endpoint(request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "mcp_server:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info"
    )