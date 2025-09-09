"""
Enhanced Voice Assistant MCP Server
====================================
Implements an MCP server with voice capabilities, WebSocket support,
and Supabase integration for conversation persistence.
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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from market_data_service import MarketDataService
from routers.dashboard_router import router as dashboard_router
from mcp_client import get_stock_history as mcp_get_stock_history
from services.market_service_factory import MarketServiceFactory
from services.openai_realtime_service import OpenAIRealtimeService
from services.openai_relay_server import openai_relay_server

# Load environment variables from .env if present
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Voice Assistant MCP Server")

# Configure CORS - allow all localhost ports for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(dashboard_router)

# Try to mount Alpaca router if available
try:
    from routers.alpaca_router import router as alpaca_router
    app.include_router(alpaca_router)
    logger.info("Alpaca router mounted successfully")
except ImportError as e:
    logger.warning(f"Alpaca router not available: {e}")
except Exception as e:
    logger.error(f"Error mounting Alpaca router: {e}")

# Mount enhanced market router for dual MCP support
try:
    from routers.enhanced_market_router import router as enhanced_router
    app.include_router(enhanced_router)
    logger.info("Enhanced market router mounted successfully")
except ImportError as e:
    logger.warning(f"Enhanced market router not available: {e}")
except Exception as e:
    logger.error(f"Error mounting enhanced market router: {e}")

# Initialize Supabase client
def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        raise ValueError("Supabase credentials not configured")
    return create_client(url, key)


class QueryRequest(BaseModel):
    """Request model for voice queries."""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    include_history: bool = True
    voice_enabled: bool = False


class QueryResponse(BaseModel):
    """Response model for voice queries."""
    response: str
    session_id: str
    timestamp: str
    audio_url: Optional[str] = None


class ConversationManager:
    """Manages conversation history and persistence."""
    
    def __init__(self, supabase: Client):
        self.supabase = supabase
        self.active_sessions: Dict[str, List[Dict[str, str]]] = {}
    
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve conversation history from Supabase."""
        try:
            response = self.supabase.table("conversations").select("*").eq(
                "session_id", session_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            if response.data:
                return [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in reversed(response.data)
                ]
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
        return []
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        user_id: Optional[str] = None
    ):
        """Save message to Supabase."""
        try:
            data = {
                "session_id": session_id,
                "role": role,
                "content": content,
                "created_at": datetime.utcnow().isoformat(),
            }
            if user_id:
                data["user_id"] = user_id
            
            self.supabase.table("conversations").insert(data).execute()
        except Exception as e:
            logger.error(f"Error saving message: {e}")


class ClaudeService:
    """Service for interacting with Claude API."""
    
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        self.model = os.environ.get("MODEL", "claude-3-sonnet-20240229")
        self.mcp_servers = self._load_mcp_servers()
        self.system_prompt = self._build_system_prompt()
    
    def _load_mcp_servers(self) -> List[Dict[str, Any]]:
        """Load MCP server configurations."""
        config = os.environ.get("MCP_SERVERS", "[]")
        try:
            servers = json.loads(config)
            return [s for s in servers if isinstance(s, dict) and "url" in s]
        except json.JSONDecodeError:
            return []
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the assistant."""
        custom = os.environ.get("SYSTEM_PROMPT")
        if custom:
            return custom
        
        return """You are a helpful voice assistant with access to real-time data.
        Provide concise, conversational responses suitable for voice output.
        When presenting data, use natural language and avoid excessive technical jargon.
        If asked about market data or financial information, always include relevant 
        timestamps and emphasize risk considerations.
        Keep responses brief unless the user requests more detail."""
    
    async def ask(
        self, 
        query: str, 
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Send query to Claude and return response."""
        messages = []
        
        # Add history if provided
        if history:
            messages.extend(history)
        
        # Add current query
        messages.append({"role": "user", "content": query})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "system": self.system_prompt,
            "max_tokens": 700,  # Limited for conversational responses
        }
        
        # Add MCP servers if configured
        if self.mcp_servers:
            payload["mcp_servers"] = self.mcp_servers
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "computer-use-2024-10-22",
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract content from response
                content = data.get("content", [])
                if isinstance(content, list) and content:
                    return content[0].get("text", "")
                return "I couldn't process that request."
                
            except Exception as e:
                logger.error(f"Claude API error: {e}")
                raise


# Initialize services (will be done after app startup)
supabase = None
conversation_manager = None
claude_service = None
market_service = None  # Will be initialized in startup event
market_service_error = None  # Track initialization errors for debugging
openai_service = None  # OpenAI Realtime service


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global supabase, conversation_manager, claude_service, market_service, market_service_error, openai_service
    try:
        supabase = get_supabase_client()
        conversation_manager = ConversationManager(supabase)
        claude_service = ClaudeService()
        
        # Initialize OpenAI Realtime service
        try:
            # Check for required environment variable
            if not os.environ.get("OPENAI_API_KEY"):
                logger.warning("OPENAI_API_KEY not found in environment - OpenAI relay will be disabled")
                openai_service = None
            else:
                openai_service = OpenAIRealtimeService()
                logger.info("OpenAI Realtime service initialized successfully")
                # Log enhanced training status
                try:
                    from services.openai_relay_server import openai_relay_server
                    if openai_relay_server.tool_mapper:
                        logger.info("OpenAI agent enhanced training loaded successfully")
                except:
                    pass
        except Exception as e:
            logger.warning(f"OpenAI Realtime service initialization failed: {e}")
            openai_service = None
        
        # Initialize and warm up market service
        try:
            market_service = await MarketServiceFactory.initialize_service()
            service_mode = MarketServiceFactory.get_service_mode()
            logger.info(f"Market service initialized successfully in {service_mode} mode")
            market_service_error = None
        except Exception as e:
            logger.error(f"Failed to initialize market service: {e}")
            logger.warning("Market service will be unavailable - endpoints will return 503")
            market_service = None
            market_service_error = str(e)  # Store error for debugging
        
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Services will be None, endpoints will handle gracefully


@app.get("/api/debug/test-direct")
async def test_direct_service():
    """Debug endpoint to test Direct service initialization."""
    try:
        from services.direct_market_service import DirectMarketDataService
        service = DirectMarketDataService()
        result = await service.get_stock_price("SPY")
        return {"success": True, "data": result}
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    global market_service, market_service_error, openai_service
    response = {
        "status": "healthy",
        "service_mode": MarketServiceFactory.get_service_mode(),
        "service_initialized": market_service is not None,
        "openai_relay_ready": openai_service is not None and hasattr(openai_service, 'relay_server'),
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add detailed service status if available
    service_status = MarketServiceFactory.get_service_status()
    if service_status:
        response["services"] = service_status
    
    # Add OpenAI relay details if available
    if openai_service:
        try:
            if hasattr(openai_service, 'relay_server'):
                from services.openai_relay_server import openai_relay_server
                active_sessions = await openai_relay_server.get_active_sessions()
                response["openai_relay"] = {
                    "active": True,
                    "sessions": len(active_sessions),
                    "tool_mapper_initialized": openai_relay_server.tool_mapper is not None
                }
            else:
                response["openai_relay"] = {"active": False, "reason": "Legacy service mode"}
        except Exception as e:
            response["openai_relay"] = {"active": False, "error": str(e)}
    else:
        response["openai_relay"] = {"active": False, "reason": "Service not initialized"}
    
    if market_service_error:
        response["service_error"] = market_service_error
    return response


async def get_market_service():
    """Get or initialize market service."""
    global market_service
    if market_service is None:
        # Try to initialize service on demand
        try:
            market_service = MarketServiceFactory.get_service()
            logger.info(f"Market service initialized on-demand in {MarketServiceFactory.get_service_mode()} mode")
        except Exception as e:
            logger.error(f"Failed to initialize market service on-demand: {e}")
            return None
    return market_service


@app.get("/api/stock-price")
async def get_stock_price(symbol: str):
    """Get comprehensive stock data using the appropriate service."""
    try:
        # Get or initialize service
        service = await get_market_service()
        if service is None:
            logger.error("Market service not initialized - startup may have failed")
            raise HTTPException(
                status_code=503, 
                detail="Market data service not available. Please try again in a moment."
            )
        
        result = await service.get_stock_price(symbol)
        
        # Validate that we got real market data
        # If price is 0 or missing, it's likely an invalid symbol
        if not result or result.get('price', 0) == 0:
            logger.warning(f"Invalid symbol or no market data for {symbol}")
            raise HTTPException(
                status_code=404,
                detail=f"Symbol '{symbol}' not found or has no market data"
            )
        
        # Additional validation: check if we have reasonable volume
        # (some valid symbols might have 0 volume during pre/post market)
        if result.get('volume', 0) == 0 and result.get('previous_close', 0) == 0:
            logger.warning(f"Symbol {symbol} appears invalid (no volume or previous close)")
            raise HTTPException(
                status_code=404,
                detail=f"Symbol '{symbol}' appears to be invalid or delisted"
            )
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except TimeoutError:
        logger.warning(f"Timeout fetching price for {symbol}")
        # Return a proper error response
        raise HTTPException(
            status_code=503,
            detail=f"Service temporarily unavailable. Request timed out for {symbol}"
        )
    except Exception as e:
        logger.error(f"Error fetching stock price for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching stock data: {str(e)}"
        )


@app.get("/api/symbol-search")
async def search_symbols(query: str, limit: int = 20):
    """Search for stock symbols using Alpaca Markets API."""
    try:
        # Get or initialize service
        service = await get_market_service()
        if service is None:
            logger.error("Market service not initialized - startup may have failed")
            raise HTTPException(
                status_code=503, 
                detail="Market data service not available. Please try again in a moment."
            )
        
        # Validate input
        if not query or len(query.strip()) < 1:
            return {
                "query": query,
                "results": [],
                "total": 0,
                "message": "Query must be at least 1 character"
            }
        
        if limit < 1 or limit > 100:
            limit = 20  # Default to 20 if invalid
        
        # Search for assets
        results = await service.search_assets(query.strip(), limit)
        
        return {
            "query": query,
            "results": results,
            "total": len(results),
            "data_source": "alpaca"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error searching symbols for query '{query}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error searching symbols: {str(e)}"
        )


@app.get("/api/comprehensive-stock-data")
async def get_comprehensive_stock_data(symbol: str):
    """Get all available data for a stock - matches ChatGPT capabilities."""
    try:
        # Get or initialize service
        service = await get_market_service()
        if service is None:
            logger.error("Market service not initialized - startup may have failed")
            raise HTTPException(
                status_code=503, 
                detail="Market data service not available. Please try again in a moment."
            )
        
        # Use the service
        data = await service.get_comprehensive_stock_data(symbol)
        
        # Map field names for frontend compatibility
        if "technical_levels" in data:
            tech_levels = data["technical_levels"]
            
            # Handle both old and new field name formats
            mapped_levels = {}
            
            # New format (human readable) -> Old format (abbreviated)
            if "quick_entry" in tech_levels:
                mapped_levels["qe_level"] = tech_levels["quick_entry"]
            elif "qe_level" in tech_levels:
                mapped_levels["qe_level"] = tech_levels["qe_level"]
                
            if "swing_trade" in tech_levels:
                mapped_levels["st_level"] = tech_levels["swing_trade"]
            elif "st_level" in tech_levels:
                mapped_levels["st_level"] = tech_levels["st_level"]
                
            if "load_the_boat" in tech_levels:
                mapped_levels["ltb_level"] = tech_levels["load_the_boat"]
            elif "ltb_level" in tech_levels:
                mapped_levels["ltb_level"] = tech_levels["ltb_level"]
            
            # Keep all other fields and add mapped ones
            data["technical_levels"] = {**tech_levels, **mapped_levels}
        
        return data
    except Exception as e:
        logger.error(f"Error fetching comprehensive data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock-history")
async def get_stock_history(symbol: str, days: int = 50):
    """Get historical stock data using the appropriate service."""
    try:
        logger.info(f"Fetching {days} days of historical data for {symbol}")
        
        # Get or initialize service
        service = await get_market_service()
        if service is None:
            logger.error("Market service not initialized - startup may have failed")
            raise HTTPException(
                status_code=503, 
                detail="Market data service not available. Please try again in a moment."
            )
        
        result = await service.get_stock_history(symbol, days)
        
        # Ensure we have the expected format for frontend
        if result and isinstance(result, dict):
            # Transform 'date' field to 'time' if needed (for TradingView compatibility)
            if 'candles' in result:
                for candle in result['candles']:
                    if 'date' in candle and 'time' not in candle:
                        candle['time'] = candle.pop('date')
            
            return result
        else:
            raise ValueError(f"Invalid response format for {symbol}")
            
    except TimeoutError:
        logger.warning(f"Timeout fetching history for {symbol}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service temporarily unavailable",
                "message": f"Request timed out for {symbol}",
                "symbol": symbol,
                "days": days
            }
        )
    except Exception as e:
        logger.error(f"Error fetching stock history for {symbol}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Historical data error",
                "message": str(e),
                "symbol": symbol,
                "days": days
            }
        )


@app.get("/api/stock-news")
async def get_stock_news(symbol: str, limit: int = 10):
    """Get latest news for a stock using the appropriate service."""
    try:
        # Get or initialize service
        service = await get_market_service()
        if service is None:
            logger.error("Market service not initialized - startup may have failed")
            return {"symbol": symbol.upper(), "news": [], "error": "Service not available"}
        
        result = await service.get_stock_news(symbol, limit)
        
        # Ensure consistent format - keep original "news" field name for frontend compatibility
        if result and isinstance(result, dict):
            articles = result.get("articles", result.get("news", result.get("items", [])))
            return {
                "symbol": symbol.upper(),
                "news": articles,  # Keep original field name for frontend
                "total": len(articles),
                "source": result.get("data_source", "unknown")
            }
        else:
            return {"symbol": symbol.upper(), "news": [], "total": 0}
            
    except TimeoutError:
        logger.warning(f"Timeout fetching news for {symbol}")
        return {"symbol": symbol.upper(), "news": [], "error": "Timeout"}
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        return {"symbol": symbol.upper(), "news": [], "error": str(e)}


@app.get("/api/analyst-ratings")
async def get_analyst_ratings(symbol: str):
    """Get analyst ratings and price targets."""
    try:
        async with httpx.AsyncClient() as client:
            ratings = await market_service.get_analyst_ratings(client, symbol)
            return {"symbol": symbol.upper(), "ratings": ratings}
    except Exception as e:
        logger.error(f"Error fetching ratings: {e}")
        return {"symbol": symbol.upper(), "ratings": {}}


@app.get("/api/options-chain")
async def get_options_chain(symbol: str):
    """Get options chain data."""
    try:
        data = await market_service.get_options_chain(symbol)
        return {"symbol": symbol.upper(), "options": data}
    except Exception as e:
        logger.error(f"Error fetching options: {e}")
        return {"symbol": symbol.upper(), "options": {}}


@app.get("/api/market-movers")
async def get_market_movers():
    """Get trending stocks and market movers."""
    try:
        data = await market_service.get_market_movers()
        return data
    except Exception as e:
        logger.error(f"Error fetching market movers: {e}")
        return {"trending": [], "error": str(e)}


@app.get("/api/market-overview")
async def get_market_overview():
    """Get market overview for ElevenLabs tool webhook."""
    try:
        # Use the market service factory to get real data
        market_service = MarketServiceFactory.get_service()
        overview = await market_service.get_market_overview()
        return overview
    except Exception as e:
        logger.error(f"Failed to get market overview: {e}")
        # Return a minimal response on error
        return {
            "indices": {},
            "movers": {},
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


@app.get("/elevenlabs/signed-url")
async def get_elevenlabs_signed_url(agent_id: Optional[str] = Query(default=None)):
    """Proxy to fetch ElevenLabs signed WebSocket URL for a given agent.

    Requires ELEVENLABS_API_KEY in environment. If agent_id not provided, uses ELEVENLABS_AGENT_ID.
    """
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="ELEVENLABS_API_KEY not configured")

    resolved_agent_id = agent_id or os.environ.get("ELEVENLABS_AGENT_ID")
    if not resolved_agent_id:
        raise HTTPException(status_code=400, detail="agent_id not provided and ELEVENLABS_AGENT_ID not configured")

    url = f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={resolved_agent_id}"
    headers = {"xi-api-key": api_key}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()
            signed_url = data.get("signed_url")
            if not signed_url:
                raise HTTPException(status_code=502, detail="Invalid response from ElevenLabs")
            return {"signed_url": signed_url}
        except httpx.HTTPStatusError as e:
            logger.error(f"ElevenLabs get-signed-url error: {e}")
            raise HTTPException(status_code=e.response.status_code, detail="Failed to get signed URL")
        except Exception as e:
            logger.error(f"ElevenLabs get-signed-url error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


class ConversationRecordRequest(BaseModel):
    """Request model for recording conversation messages."""
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    user_id: Optional[str] = None


@app.post("/conversations/record")
async def record_conversation(request: ConversationRecordRequest):
    """Record a conversation message to Supabase."""
    if not conversation_manager:
        raise HTTPException(status_code=503, detail="Database service not initialized")
    
    try:
        await conversation_manager.save_message(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            user_id=request.user_id
        )
        return {"status": "success", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error recording conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to record conversation")


@app.post("/ask", response_model=QueryResponse)
async def ask_assistant(request: QueryRequest):
    """Process a voice query through Claude."""
    if not claude_service or not conversation_manager:
        raise HTTPException(status_code=503, detail="Services not initialized")
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history if requested
        history = []
        if request.include_history:
            history = await conversation_manager.get_history(session_id)
        
        # Send query to Claude
        response = await claude_service.ask(request.query, history)
        
        # Save conversation to Supabase
        await conversation_manager.save_message(
            session_id, "user", request.query, request.user_id
        )
        await conversation_manager.save_message(
            session_id, "assistant", response, request.user_id
        )
        
        # Generate audio URL if voice is enabled
        audio_url = None
        if request.voice_enabled:
            # This would integrate with a TTS service
            # audio_url = await generate_audio(response)
            pass
        
        return QueryResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            audio_url=audio_url,
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.websocket("/openai/realtime/ws")
async def openai_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for OpenAI Realtime voice interaction."""
    if not openai_service:
        await websocket.close(code=1011, reason="OpenAI service not initialized")
        return
    
    try:
        await openai_service.handle_websocket_connection(websocket, None)
    except Exception as e:
        logger.error(f"OpenAI WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))


@app.post("/openai/realtime/session")
async def create_openai_session():
    """Create a new OpenAI Realtime session."""
    if not openai_service:
        raise HTTPException(status_code=503, detail="OpenAI service not initialized")
    
    try:
        session_id = str(uuid.uuid4())
        return {
            "session_id": session_id,
            "ws_url": f"ws://localhost:8000/openai/realtime/ws",
            "status": "ready"
        }
    except Exception as e:
        logger.error(f"Error creating OpenAI session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.websocket("/realtime-relay/{session_id}")
async def openai_relay_endpoint(websocket: WebSocket, session_id: str):
    """
    OpenAI Realtime API Relay Endpoint
    ==================================
    Secure WebSocket relay for RealtimeClient connections following OpenAI patterns.
    Provides secure access to OpenAI's Realtime API without exposing API keys.
    Handles WebSocket subprotocol negotiation for compatibility with RealtimeClient.
    """
    try:
        # Extract subprotocol from request headers if present
        subprotocol = None
        headers = websocket.headers
        
        # Check for Sec-WebSocket-Protocol header
        if "sec-websocket-protocol" in headers:
            requested_protocols = headers["sec-websocket-protocol"]
            # Use the first requested protocol (RealtimeClient typically sends 'openai-realtime')
            subprotocol = requested_protocols.split(',')[0].strip() if requested_protocols else None
            logger.info(f"WebSocket subprotocol requested: {subprotocol}")
        
        # Accept WebSocket with subprotocol if requested
        if subprotocol:
            await websocket.accept(subprotocol=subprotocol)
        else:
            await websocket.accept()
        
        # Pass the accepted websocket to the relay handler
        await openai_relay_server.handle_relay_connection_accepted(websocket, session_id)
    except Exception as e:
        logger.error(f"Relay WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass


@app.get("/realtime-relay/status")
async def relay_status():
    """Get relay server status and active sessions."""
    try:
        active_sessions = await openai_relay_server.get_active_sessions()
        return {
            "status": "operational",
            "active_sessions": len(active_sessions),
            "sessions": active_sessions,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting relay status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get relay status")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time voice interaction."""
    if not claude_service or not conversation_manager:
        await websocket.close(code=1011, reason="Services not initialized")
        return
    
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") == "audio":
                # Handle audio stream (would need audio processing)
                pass
            elif data.get("type") == "text":
                query = data.get("query")
                if query:
                    # Get history
                    history = await conversation_manager.get_history(session_id)
                    
                    # Get Claude's response
                    response = await claude_service.ask(query, history)
                    
                    # Save to database
                    await conversation_manager.save_message(
                        session_id, "user", query
                    )
                    await conversation_manager.save_message(
                        session_id, "assistant", response
                    )
                    
                    # Send response back
                    await websocket.send_json({
                        "type": "response",
                        "content": response,
                        "timestamp": datetime.utcnow().isoformat(),
                    })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
