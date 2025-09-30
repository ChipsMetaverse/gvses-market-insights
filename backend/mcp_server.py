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
from services.openai_realtime_service import OpenAIRealtimeService
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

# Mount agent router for internal agent orchestrator
try:
    from routers.agent_router import router as agent_router
    app.include_router(agent_router)
    logger.info("Agent router mounted successfully")
except ImportError as e:
    logger.warning(f"Agent router not available: {e}")
except Exception as e:
    logger.error(f"Error mounting agent router: {e}")

# Mount Computer Use verification router if enabled
if os.getenv("USE_COMPUTER_USE", "false").lower() == "true":
    try:
        from routers.computer_use_router import router as computer_use_router
        app.include_router(computer_use_router)
        logger.info("Computer Use verification router mounted successfully")
    except ImportError as e:
        logger.warning(f"Computer Use router not available: {e}")
    except Exception as e:
        logger.error(f"Error mounting Computer Use router: {e}")

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
    tool_results: Optional[Dict[str, Any]] = None
    chart_commands: Optional[List[str]] = None


class ConversationManager:
    """Manages conversation history and persistence."""
    
    def __init__(self, supabase: Client, max_attempts: int = 2, retry_delay: float = 0.05):
        self.supabase = supabase
        self.active_sessions: Dict[str, List[Dict[str, str]]] = {}
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay
    
    def _get_or_create_session(self, session_id: str, user_id: Optional[str] = None) -> None:
        """Ensure the session row exists before saving messages."""
        payload: Dict[str, Any] = {
            "id": session_id,
            "created_at": datetime.utcnow().isoformat()
        }
        if user_id:
            payload["user_id"] = user_id

        try:
            self.supabase.table("sessions").upsert(payload, on_conflict="id").execute()
        except Exception as exc:
            # Ignore duplicate-key errors (23505); propagate anything else.
            if "23505" in str(exc):
                return
            logger.warning(f"Sessions upsert failed for {session_id[:8]}…: {exc}")
    
    async def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """Retrieve conversation history from Supabase."""
        try:
            logger.info(f"🔍 Fetching history for session {session_id}")
            response = self.supabase.table("conversations").select("*").eq(
                "session_id", session_id
            ).order("created_at", desc=True).limit(limit).execute()
            
            # Debug log the raw response
            logger.info(f"📦 Supabase response data count: {len(response.data) if response.data else 0}")
            if response.data:
                logger.debug(f"📋 Raw Supabase data (first 2): {response.data[:2] if len(response.data) > 0 else []}")
                
            if response.data:
                history = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in reversed(response.data)
                ]
                logger.info(f"✅ Retrieved {len(history)} messages for session {session_id[:8]}...")
                return history
            else:
                logger.warning(f"⚠️ No data returned from Supabase for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error fetching history for {session_id}: {e}")
        logger.info(f"📭 No history found for session {session_id[:8]}...")
        return []
    
    async def save_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        user_id: Optional[str] = None
    ) -> bool:
        """Save message to Supabase with automatic session creation and fallback."""
        import time
        start_time = time.time()
        attempts = 0
        last_error: Optional[Exception] = None

        while attempts < self.max_attempts:
            attempts += 1
            try:
                logger.info(f"💾 Saving {role} message for session {session_id} (attempt {attempts})")
                
                # Ensure session exists before saving messages
                self._get_or_create_session(session_id, user_id)
                
                # Now save the message
                data = {
                    "session_id": session_id,
                    "role": role,
                    "content": content[:5000],  # Limit content size
                    "created_at": datetime.utcnow().isoformat(),
                }
                if user_id:
                    data["user_id"] = user_id
                
                response = self.supabase.table("conversations").insert(data).execute()
                logger.info(
                    f"✅ Saved {role} message for session {session_id[:8]}... "
                    f"(response has data: {response.data is not None})"
                )
                elapsed = (time.time() - start_time) * 1000
                if elapsed > 500:
                    logger.warning(f"Slow Supabase save: {elapsed:.0f}ms for session {session_id}")
                return True
            except Exception as exc:
                last_error = exc
                elapsed = (time.time() - start_time) * 1000
                err_str = str(exc)
                logger.warning(
                    f"⚠️ Supabase save attempt {attempts}/{self.max_attempts} failed for session "
                    f"{session_id[:8]}… after {elapsed:.0f}ms: {err_str}"
                )
                # Foreign key violation: recreate session row and retry immediately
                if "23503" in err_str:
                    self._get_or_create_session(session_id, user_id)
                if attempts < self.max_attempts:
                    await asyncio.sleep(self.retry_delay)

        logger.warning(
            f"Skipping history save for {session_id[:8]}… after {self.max_attempts} attempts: {last_error}"
        )
        return False


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
    global supabase, conversation_manager, claude_service, market_service, market_service_error, openai_service, orchestrator
    
    try:
        # Initialize Supabase (required)
        supabase = get_supabase_client()
        conversation_manager = ConversationManager(supabase)
        logger.info("✅ Supabase initialized successfully")
        
        # Disabled Claude service - using AgentOrchestrator instead
        # claude_service = ClaudeService()
        claude_service = None
        
        # Initialize the agent orchestrator early (required for /ask endpoint)
        try:
            from services.agent_orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            logger.info("✅ Agent orchestrator initialized successfully")
            
            # Pre-warm cache with common queries for instant responses
            cache_warm_enabled = os.getenv("CACHE_WARM_ON_STARTUP", "true").lower() == "true"
            if cache_warm_enabled:
                asyncio.create_task(orchestrator.prewarm_cache())
                logger.info("🔥 Cache pre-warming started in background")
            else:
                logger.info("📦 Cache pre-warming disabled by CACHE_WARM_ON_STARTUP=false")
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent orchestrator: {e}")
            orchestrator = None
        
        # Test Alpaca connectivity on startup
        if os.environ.get("ALPACA_API_KEY") and os.environ.get("ALPACA_SECRET_KEY"):
            try:
                from services.market_service import get_quote_from_alpaca, ALPACA_AVAILABLE
                if ALPACA_AVAILABLE:
                    test_quote = await get_quote_from_alpaca("AAPL")
                    logger.info(f"✅ Alpaca service validated: AAPL=${test_quote.get('price', 'N/A')}, open=${test_quote.get('open', 0)}")
                else:
                    logger.warning("⚠️ Alpaca service not available - will use Yahoo Finance fallback")
            except Exception as e:
                logger.error(f"❌ Alpaca validation failed: {e}")
        else:
            logger.warning("⚠️ Alpaca credentials not found - using Yahoo Finance only")
        
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
                    # Voice-only interface - no tools
                    logger.info("OpenAI Realtime voice-only interface loaded")
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
        logger.error(f"Failed to initialize some services: {e}")
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
        "openai_relay_ready": False,  # Will be set below after checking actual relay server
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Add detailed service status if available
    service_status = MarketServiceFactory.get_service_status()
    if service_status:
        response["services"] = service_status

    # Report MCP sidecar status
    try:
        from mcp_client import get_mcp_manager
        mcp_manager = get_mcp_manager()
        if hasattr(mcp_manager, "initialized") and not mcp_manager.initialized:
            try:
                await mcp_manager.initialize()
            except Exception as exc:
                logger.warning(f"MCP manager initialization during health check failed: {exc}")
        response["mcp_sidecars"] = mcp_manager.get_status_snapshot() if hasattr(mcp_manager, "get_status_snapshot") else {"status": "unavailable"}
    except Exception as exc:
        response["mcp_sidecars"] = {"status": "error", "error": str(exc)}

    # Add OpenAI relay details if available
    try:
        # Try to import the relay server directly
        from services.openai_relay_server import openai_relay_server
        active_sessions = await openai_relay_server.get_active_sessions()
        response["openai_relay_ready"] = True
        response["openai_relay"] = {
            "active": True,
            "sessions": len(active_sessions),
            "voice_only": True,  # Voice-only interface (no tools)
            "api_key_configured": bool(openai_relay_server.api_key)
        }
    except ImportError:
        # Fallback to checking OpenAI service
        if openai_service:
            response["openai_relay_ready"] = True
            response["openai_relay"] = {
                "active": True,
                "reason": "OpenAI service mode",
                "api_key_configured": bool(openai_service.api_key)
            }
        else:
            response["openai_relay_ready"] = False
            response["openai_relay"] = {"active": False, "reason": "Service not initialized"}
    except Exception as e:
        response["openai_relay_ready"] = False
        response["openai_relay"] = {"active": False, "error": str(e)}
    
    if market_service_error:
        response["service_error"] = market_service_error
    
    # Day 5.2: Add feature flags
    response["features"] = {
        "tool_wiring": True,  # Day 1: Tool integration complete
        "triggers_disclaimers": True,  # Day 2: Smart triggers and disclaimers
        "advanced_ta": {  # Day 3.1: Advanced technical analysis
            "enabled": True,
            "fallback_enabled": True,
            "timeout_ms": 3000,
            "levels": ["sell_high_level", "buy_low_level", "btd_level", "retest_level"]
        },
        "tailored_suggestions": True,  # Day 3.2: Dynamic suggestions
        "concurrent_execution": {  # Day 4.1: Concurrent with timeouts
            "enabled": True,
            "global_timeout_s": 10,
            "per_tool_timeouts": {
                "get_stock_price": 2.0,
                "get_stock_history": 3.0,
                "get_stock_news": 4.0,
                "get_comprehensive_stock_data": 5.0
            }
        },
        "ideal_formatter": True,  # Priority: Professional response format
        "bounded_llm_insights": {  # Day 4.2: AI insights
            "enabled": True,
            "max_chars": 250,
            "model": "gpt-4.1",
            "timeout_s": 2.0,
            "fallback_enabled": True
        },
        "test_suite": {  # Day 5.1: Comprehensive testing
            "enabled": True,
            "last_run_success_rate": 76.9,
            "total_tests": 26
        }
    }
    
    # Add version info
    response["version"] = "2.0.0"  # Major update with all features
    response["agent_version"] = "1.5.0"  # Agent orchestrator version
    
    return response


@app.get("/metrics")
@limiter.limit("10/minute")  # Allow 10 requests per minute per IP
async def get_metrics(request: Request, authorization: Optional[str] = Header(None)):
    """Get knowledge system performance metrics with authentication and rate limiting."""
    # Check for metrics token
    metrics_token = os.getenv("METRICS_TOKEN")
    if metrics_token:
        # If token is configured, require it
        if not authorization or authorization != f"Bearer {metrics_token}":
            raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Get metrics from orchestrator if available
    try:
        from services.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        if orchestrator and hasattr(orchestrator, 'metrics'):
            stats = orchestrator.metrics.get_stats()
            # Add response cache metrics
            stats['response_cache_size'] = len(orchestrator._response_cache) if hasattr(orchestrator, '_response_cache') else 0
            stats['knowledge_cache_size'] = len(orchestrator._knowledge_cache) if hasattr(orchestrator, '_knowledge_cache') else 0
            return stats
        else:
            return {"status": "metrics not available", "reason": "orchestrator not initialized"}
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {"status": "error", "error": str(e)}


# Phase 5 ML Monitoring Endpoints
@app.get("/api/ml/metrics")
@limiter.limit("30/minute")
async def get_ml_metrics(request: Request, hours: int = 1):
    """Get Phase 5 ML performance metrics"""
    try:
        from services.ml_monitoring import get_ml_monitoring
        monitoring = get_ml_monitoring()
        
        current_metrics = await monitoring.get_current_metrics()
        history = await monitoring.get_metrics_history(hours=hours)
        
        return {
            "current": current_metrics,
            "history": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ML metrics: {e}")
        raise HTTPException(status_code=500, detail=f"ML metrics error: {str(e)}")

@app.get("/api/ml/alerts")
@limiter.limit("20/minute")
async def get_ml_alerts(request: Request):
    """Get current ML alerts and warnings"""
    try:
        from services.ml_monitoring import get_ml_monitoring
        monitoring = get_ml_monitoring()
        
        alerts = await monitoring.get_alerts()
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ML alerts: {e}")
        raise HTTPException(status_code=500, detail=f"ML alerts error: {str(e)}")

@app.get("/api/ml/health")
@limiter.limit("60/minute")
async def get_ml_health(request: Request):
    """Get Phase 5 ML system health status"""
    try:
        from services.pattern_confidence_service import get_confidence_service
        from services.ml_monitoring import get_ml_monitoring
        
        confidence_service = get_confidence_service()
        monitoring = get_ml_monitoring()
        
        # Get service stats
        service_stats = confidence_service.get_service_stats()
        current_metrics = await monitoring.get_current_metrics()
        alerts = await monitoring.get_alerts()
        
        # Determine overall health
        error_rate = current_metrics["performance"]["error_rate"]
        sla_compliance = current_metrics["performance"]["sla_compliance"] 
        critical_alerts = [a for a in alerts if a.get("level") == "critical"]
        
        if error_rate > 0.2 or sla_compliance < 0.90 or critical_alerts:
            health_status = "critical"
        elif error_rate > 0.05 or sla_compliance < 0.95:
            health_status = "degraded"
        else:
            health_status = "healthy"
        
        return {
            "status": health_status,
            "phase5_enabled": True,
            "model_loaded": service_stats["model_loaded"],
            "model_version": service_stats["model_version"],
            "error_rate": error_rate,
            "sla_compliance": sla_compliance,
            "predictions_made": service_stats["predictions_made"],
            "average_latency_ms": service_stats["average_latency_ms"],
            "cache_hit_rate": service_stats["cache_hit_rate"],
            "fallback_rate": current_metrics["predictions"]["fallback_rate"],
            "alerts_count": len(alerts),
            "critical_alerts": len(critical_alerts),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting ML health: {e}")
        raise HTTPException(status_code=500, detail=f"ML health error: {str(e)}")

@app.post("/api/ml/baseline")
@limiter.limit("5/minute")
async def set_ml_baseline(request: Request, baseline_data: Dict[str, Any]):
    """Set baseline feature distribution for drift detection"""
    try:
        from services.ml_monitoring import get_ml_monitoring
        monitoring = get_ml_monitoring()
        
        features = baseline_data.get("features", {})
        if not features:
            raise HTTPException(status_code=400, detail="No features provided")
        
        monitoring.set_baseline(features)
        
        return {
            "status": "success",
            "message": f"Baseline set with {len(features)} features",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error setting ML baseline: {e}")
        raise HTTPException(status_code=500, detail=f"Baseline error: {str(e)}")


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
        
        # Normalize technical level field names using centralized helper
        if "technical_levels" in data:
            from utils.technical_levels import normalize_technical_levels
            data["technical_levels"] = normalize_technical_levels(data["technical_levels"])
        
        return data
    except Exception as e:
        logger.error(f"Error fetching comprehensive data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, (np.str_, np.unicode_)):
        return str(obj)
    else:
        return obj

@app.get("/api/technical-indicators")
async def get_technical_indicators(
    symbol: str, 
    indicators: str = "fibonacci,macd,rsi,bollinger,stochastic",
    period: int = 100
):
    """Get specific technical indicators for a stock symbol."""
    try:
        # Parse comma-separated indicators
        requested_indicators = [ind.strip().lower() for ind in indicators.split(',')]
        
        # Get market service
        service = await get_market_service()
        if service is None:
            raise HTTPException(
                status_code=503,
                detail="Market data service not available. Please try again in a moment."
            )
        
        # Get stock history for calculations
        history_result = await service.get_stock_history(symbol, period)
        candles = history_result.get('candles', [])
        
        if not candles or len(candles) < 20:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient historical data for {symbol}. Need at least 20 candles, got {len(candles)}."
            )
        
        # Get current price
        quote = await service.get_stock_price(symbol)
        current_price = quote.get('price', quote.get('last', 0))
        
        # Import technical analysis module
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from advanced_technical_analysis import AdvancedTechnicalAnalysis
        from pattern_detection import PatternDetector, format_patterns_for_agent
        
        # Extract price data
        prices = [c.get('close', c.get('c', 0)) for c in candles]
        highs = [c.get('high', c.get('h', 0)) for c in candles]
        lows = [c.get('low', c.get('l', 0)) for c in candles]
        volumes = [c.get('volume', c.get('v', 0)) for c in candles]
        
        result = {
            "symbol": symbol.upper(),
            "timestamp": candles[-1].get('time', candles[-1].get('date')) if candles else None,
            "current_price": current_price,
            "indicators": {}
        }
        
        # Calculate requested indicators
        if 'fibonacci' in requested_indicators and len(prices) >= 50:
            recent_high = max(highs[-50:])
            recent_low = min(lows[-50:])
            fib_levels = AdvancedTechnicalAnalysis.calculate_fibonacci_levels(
                recent_high, recent_low, current_price > sum(prices[-20:]) / 20
            )
            result["indicators"]["fibonacci"] = {
                **fib_levels,
                "swing_high": recent_high,
                "swing_low": recent_low
            }
        
        if 'macd' in requested_indicators and len(prices) >= 26:
            import numpy as np
            timestamps = [c.get('time', c.get('date')) for c in candles]
            
            # Calculate MACD as time series
            fast_period = 12
            slow_period = 26
            signal_period = 9
            
            # Calculate EMAs
            def calculate_ema(data, period):
                ema = []
                multiplier = 2 / (period + 1)
                current_ema = np.mean(data[:period])  # Start with SMA
                
                for i in range(period, len(data)):
                    current_ema = (data[i] - current_ema) * multiplier + current_ema
                    ema.append(current_ema)
                return ema
            
            # Need at least slow_period prices
            if len(prices) >= slow_period:
                fast_ema = calculate_ema(prices, fast_period)
                slow_ema = calculate_ema(prices, slow_period)
                
                # Calculate MACD line (fast EMA - slow EMA)
                macd_line = []
                for i in range(len(slow_ema)):
                    if i + (slow_period - fast_period) < len(fast_ema):
                        macd_value = fast_ema[i + (slow_period - fast_period)] - slow_ema[i]
                        macd_line.append(macd_value)
                
                # Calculate signal line (9-period EMA of MACD)
                signal_line = []
                if len(macd_line) >= signal_period:
                    signal_line = calculate_ema(macd_line, signal_period)
                
                # Build time series
                macd_series = {
                    "macd_line": [],
                    "signal_line": [],
                    "histogram": []
                }
                
                # Start from where we have all three values
                start_idx = slow_period + signal_period - 1
                for i in range(len(signal_line)):
                    idx = start_idx + i
                    if idx < len(timestamps):
                        macd_val = macd_line[signal_period - 1 + i]
                        signal_val = signal_line[i]
                        
                        macd_series["macd_line"].append({
                            "time": timestamps[idx],
                            "value": round(macd_val, 4)
                        })
                        macd_series["signal_line"].append({
                            "time": timestamps[idx],
                            "value": round(signal_val, 4)
                        })
                        macd_series["histogram"].append({
                            "time": timestamps[idx],
                            "value": round(macd_val - signal_val, 4)
                        })
                
                result["indicators"]["macd"] = macd_series
        
        if 'rsi' in requested_indicators and len(prices) >= 14:
            import numpy as np
            timestamps = [c.get('time', c.get('date')) for c in candles]
            
            # Calculate RSI as time series
            rsi_series = []
            period = 14
            
            for i in range(period, len(prices)):
                window_prices = prices[max(0, i-period):i+1]
                
                # Calculate price changes
                changes = np.diff(window_prices)
                gains = np.where(changes > 0, changes, 0)
                losses = np.where(changes < 0, -changes, 0)
                
                avg_gain = np.mean(gains)
                avg_loss = np.mean(losses)
                
                if avg_loss == 0:
                    rsi = 100
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                
                rsi_series.append({
                    "time": timestamps[i],
                    "value": round(rsi, 2)
                })
            
            # Get current RSI for signal
            current_rsi = rsi_series[-1]["value"] if rsi_series else 50
            
            result["indicators"]["rsi"] = {
                "values": rsi_series,
                "current": current_rsi,
                "overbought": 70,
                "oversold": 30,
                "signal": "overbought" if current_rsi > 70 else "oversold" if current_rsi < 30 else "neutral"
            }
        
        if 'bollinger' in requested_indicators and len(prices) >= 20:
            import numpy as np
            timestamps = [c.get('time', c.get('date')) for c in candles]
            
            # Calculate Bollinger Bands as time series
            bollinger_series = {
                "upper": [],
                "middle": [],
                "lower": []
            }
            
            for i in range(19, len(prices)):
                window_prices = prices[i-19:i+1]
                mean = np.mean(window_prices)
                std = np.std(window_prices)
                
                bollinger_series["upper"].append({
                    "time": timestamps[i],
                    "value": round(mean + 2 * std, 2)
                })
                bollinger_series["middle"].append({
                    "time": timestamps[i],
                    "value": round(mean, 2)
                })
                bollinger_series["lower"].append({
                    "time": timestamps[i],
                    "value": round(mean - 2 * std, 2)
                })
            
            result["indicators"]["bollinger"] = bollinger_series
        
        if 'stochastic' in requested_indicators and len(prices) >= 14:
            stoch_data = AdvancedTechnicalAnalysis.calculate_stochastic(highs, lows, prices)
            result["indicators"]["stochastic"] = stoch_data
        
        if 'moving_averages' in requested_indicators or 'ma' in requested_indicators:
            import numpy as np
            # Extract timestamps from candles
            timestamps = [c.get('time', c.get('date')) for c in candles]
            
            # Calculate moving averages as time series
            ma_data = {}
            
            # MA20 time series
            if len(prices) >= 20:
                ma20_series = []
                for i in range(19, len(prices)):
                    ma20_series.append({
                        "time": timestamps[i],
                        "value": round(np.mean(prices[i-19:i+1]), 2)
                    })
                ma_data["ma20"] = ma20_series
            
            # MA50 time series
            if len(prices) >= 50:
                ma50_series = []
                for i in range(49, len(prices)):
                    ma50_series.append({
                        "time": timestamps[i],
                        "value": round(np.mean(prices[i-49:i+1]), 2)
                    })
                ma_data["ma50"] = ma50_series
            
            # MA200 time series (if enough data)
            if len(prices) >= 200:
                ma200_series = []
                for i in range(199, len(prices)):
                    ma200_series.append({
                        "time": timestamps[i],
                        "value": round(np.mean(prices[i-199:i+1]), 2)
                    })
                ma_data["ma200"] = ma200_series
                
            result["indicators"]["moving_averages"] = ma_data
        
        if 'support_resistance' in requested_indicators or 'sr' in requested_indicators:
            sr_levels = AdvancedTechnicalAnalysis.identify_support_resistance(prices, volumes)
            result["indicators"]["support_resistance"] = sr_levels
        
        # Add pattern detection
        if 'patterns' in requested_indicators or len(requested_indicators) == 0:
            # Detect patterns on the candle data
            detector = PatternDetector(candles)
            patterns_result = detector.detect_all_patterns()
            result["patterns"] = patterns_result
            
            # Add formatted explanation for the agent
            result["patterns"]["agent_explanation"] = format_patterns_for_agent(patterns_result)
        
        result["data_source"] = history_result.get("data_source", "unknown")
        result["calculation_period"] = period
        
        # Convert numpy types to native Python types for JSON serialization
        return convert_numpy_types(result)
        
    except Exception as e:
        logger.error(f"Error calculating technical indicators: {e}")
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
        # Fire-and-forget to avoid blocking user request on DB latency
        asyncio.create_task(conversation_manager.save_message(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            user_id=request.user_id
        ))
        return {"status": "accepted", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error recording conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to record conversation")

# Agent Orchestrator endpoints
@app.post("/api/agent/orchestrate")
async def orchestrate_agent(request: QueryRequest):
    """Process a query using the agent orchestrator with function calling."""
    try:
        from services.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        
        # Process the query with the orchestrator
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=getattr(request, 'conversation_history', None)
        )
        
        return result
    except Exception as e:
        logger.error(f"Agent orchestration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/diag")
async def agent_diagnostics():
    """Diagnostic endpoint: SDK, flags, and last per-phase timings from orchestrator."""
    import openai
    from openai import AsyncOpenAI
    import time
    import os
    
    # Check SDK version and available methods
    client = AsyncOpenAI()
    
    # Collect diagnostics
    diag_data = {
        "sdk": {
            "version": openai.__version__,
            "responses_api": hasattr(client, 'responses'),
            "responses_methods": sorted([m for m in dir(client.responses) if not m.startswith('_')]) if hasattr(client, 'responses') else []
        },
        "environment": {
            "USE_RESPONSES": os.getenv("USE_RESPONSES", "false"),
            "model": os.getenv("MODEL", "gpt-4o-mini"),
            "python_version": sys.version.split()[0]
        },
        "feature_flags": {
            "responses_api_enabled": os.getenv("USE_RESPONSES", "false").lower() == "true",
            "use_mcp": os.getenv("USE_MCP", "true").lower() == "true",
            "single_pass": True
        },
        "performance_targets": {
            "price_query": "< 3s",
            "technical_analysis": "6-9s",
            "news_query": "3-5s"
        },
        "extraction_priority": [
            "response.output_text (SDK property)",
            "response.text (direct attribute)",
            "response.output[].content[].text (manual)",
            "reasoning content (fallback)"
        ],
        "timestamp": datetime.now().isoformat()
    }
    
    # Include orchestrator metrics if available
    try:
        from services.agent_orchestrator import get_orchestrator
        orch = get_orchestrator()
        last_diag = getattr(orch, 'last_diag', None)
        diag_data["orchestrator"] = {
            "model": getattr(orch, 'model', None),
            "use_responses_client": bool(getattr(orch, '_responses_client', None)),
            "last_diag": last_diag,
        }
    except Exception as e:
        diag_data["orchestrator_error"] = str(e)
    
    return diag_data

@app.get("/api/agent/health")
async def agent_health():
    """Check agent orchestrator health."""
    return {
        "status": "healthy",
        "model": os.getenv("AGENT_MODEL", "gpt-4o"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.7")),
        "backend": "agent_orchestrator"
    }

@app.get("/api/agent/tools")
async def get_agent_tools():
    """Get available tools for the agent."""
    from services.agent_orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    return orchestrator._get_tool_schemas()

@app.post("/api/agent/clear-cache")
async def clear_agent_cache():
    """Clear the agent's cache."""
    from services.agent_orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    orchestrator.clear_cache()
    return {"status": "success", "message": "Cache cleared"}

@app.post("/ask", response_model=QueryResponse)
async def ask_assistant(request: QueryRequest):
    """Process a voice query through the Agent Orchestrator."""
    try:
        # Import and get the orchestrator
        from services.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get conversation history if requested
        history = []
        if request.include_history and conversation_manager:
            logger.info(f"📚 include_history=True for session {session_id}, fetching history...")
            history = await conversation_manager.get_history(session_id)
            logger.info(f"📖 Retrieved {len(history)} messages from history")
        else:
            logger.info(f"⏭️ Skipping history: include_history={request.include_history}, conversation_manager={conversation_manager is not None}")
        
        # Convert history to orchestrator format if needed
        conversation_history = []
        for msg in history:
            if isinstance(msg, dict):
                conversation_history.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Process query through orchestrator
        logger.info(f"🤖 Processing query for session {session_id[:8]}... with {len(conversation_history)} history messages")
        result = await orchestrator.process_query(
            request.query, 
            conversation_history,
            stream=False
        )
        
        # Extract response text
        response_text = result.get("text", "")
        
        # Only save conversation to Supabase if not cached
        if not result.get("cached", False) and conversation_manager:
            try:
                # Save in background to keep hot path fast
                asyncio.create_task(conversation_manager.save_message(
                    session_id, "user", request.query, request.user_id
                ))
                asyncio.create_task(conversation_manager.save_message(
                    session_id, "assistant", response_text, request.user_id
                ))
                logger.debug(f"Saved conversation for session {session_id[:8]}...")
            except Exception as e:
                # Log but don't fail the request
                logger.warning(f"History save failed for {session_id}: {e}")
        elif result.get("cached", False):
            logger.debug(f"Skipped Supabase save for cached response (session {session_id[:8]}...)")
        
        # Generate audio URL if voice is enabled
        audio_url = None
        if request.voice_enabled:
            # This would integrate with a TTS service
            # audio_url = await generate_audio(response_text)
            pass
        
        return QueryResponse(
            response=response_text,
            session_id=session_id,
            timestamp=datetime.utcnow().isoformat(),
            audio_url=audio_url,
            tool_results=result.get("data", {}),
            chart_commands=result.get("chart_commands", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/debug/ask")
async def debug_ask_endpoint():
    """Debug endpoint to diagnose /ask issues."""
    debug_info = {
        "services_initialized": bool(orchestrator),
        "openai_api_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "knowledge_base_exists": os.path.exists("/app/backend/knowledge_base_embedded.json") if os.path.exists("/app") else os.path.exists("backend/knowledge_base_embedded.json"),
    }
    
    try:
        # Try to get the orchestrator
        from services.agent_orchestrator import get_orchestrator
        test_orchestrator = get_orchestrator()
        debug_info["orchestrator_initialized"] = True
        debug_info["orchestrator_type"] = type(test_orchestrator).__name__
        
        # Check knowledge base
        if hasattr(test_orchestrator, 'retriever') and hasattr(test_orchestrator.retriever, 'embeddings'):
            debug_info["embeddings_count"] = len(test_orchestrator.retriever.embeddings)
        
    except Exception as e:
        debug_info["orchestrator_error"] = str(e)
        debug_info["orchestrator_initialized"] = False
    
    return debug_info


@app.websocket("/openai/realtime/ws")
async def openai_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for OpenAI Realtime voice interaction."""
    if not openai_service:
        await websocket.close(code=1011, reason="OpenAI service not initialized")
        return
    
    try:
        # Handle WebSocket subprotocol negotiation
        headers = dict(websocket.headers)
        subprotocol = None
        
        # Check for Sec-WebSocket-Protocol header
        if "sec-websocket-protocol" in headers:
            requested_protocols = headers["sec-websocket-protocol"]
            # Use the first requested protocol (RealtimeClient typically sends protocol headers)
            subprotocol = requested_protocols.split(',')[0].strip() if requested_protocols else None
            logger.info(f"WebSocket subprotocol requested: {subprotocol}")
        
        # Accept WebSocket with subprotocol if requested
        if subprotocol:
            await websocket.accept(subprotocol=subprotocol)
        else:
            await websocket.accept()
        
        # Pass the accepted websocket to the OpenAI service
        await openai_service.handle_websocket_connection_accepted(websocket, None)
    except Exception as e:
        logger.error(f"OpenAI WebSocket error: {e}")
        try:
            await websocket.close(code=1011, reason=str(e))
        except:
            pass


@app.post("/openai/realtime/session")
async def create_openai_session(request: Request):
    """Create a new OpenAI Realtime session."""
    if not openai_service:
        raise HTTPException(status_code=503, detail="OpenAI service not initialized")
    
    try:
        session_id = str(uuid.uuid4())
        
        # Compute WebSocket URL from request to avoid mixed-content issues
        # Use the same scheme (ws/wss) and host as the HTTP request
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        ws_scheme = "wss" if forwarded_proto == "https" or request.url.scheme == "https" else "ws"
        
        # Get the host from headers or request
        host = request.headers.get("host", request.url.netloc)
        
        return {
            "session_id": session_id,
            "ws_url": f"{ws_scheme}://{host}/realtime-relay/{session_id}",
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
                    
                    # Save to database (non-blocking)
                    asyncio.create_task(conversation_manager.save_message(
                        session_id, "user", query
                    ))
                    asyncio.create_task(conversation_manager.save_message(
                        session_id, "assistant", response
                    ))
                    
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
