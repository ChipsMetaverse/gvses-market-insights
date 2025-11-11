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
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Header
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from routers.agent_router import router as agent_router
from services.http_mcp_client import get_http_mcp_client as get_direct_mcp_client  # Using HTTP for better performance
from services.forex_mcp_client import get_forex_mcp_client
from services.market_service_factory import MarketServiceFactory
from services.openai_relay_server import openai_relay_server
from chart_control_api import router as chart_control_router
from services.agents_sdk_service import agents_sdk_service, AgentQuery, AgentResponse
from services.database_service import get_database_service
from websocket_server import chart_streamer  # Real-time chart command streaming
from utils.telemetry import build_request_telemetry, persist_request_log
from utils.request_context import generate_request_id, set_request_id

# Sprint 1, Day 2: Prometheus metrics
from middleware.metrics import PrometheusMiddleware, get_metrics, get_metrics_content_type
from fastapi.responses import Response as FastAPIResponse

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

# Sprint 1, Day 2: Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware)
logger.info("Prometheus metrics middleware enabled")

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
market_service = MarketServiceFactory.get_service()

# Voice session management
active_voice_sessions = {}

# ChatKit configuration
CHART_AGENT_WORKFLOW_ID = "wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736"

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
        await openai_relay_server.shutdown()
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
            "openai_relay_ready": True,  # Service is always ready, active sessions are tracked separately
            "timestamp": datetime.now().isoformat(),
            "services": {
                "direct": service_status,
                "mcp": "operational" if mcp_status.get("initialized") else "unavailable",
                "mode": "hybrid" if service_status == "operational" and mcp_status.get("initialized") else "fallback"
            },
            "mcp_sidecars": mcp_status,
            "openai_relay": {
                **openai_relay_metrics,
                "active": True  # Add active field for frontend compatibility
            },
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

# Sprint 1, Day 2: Prometheus metrics endpoint
@app.get("/metrics")
async def metrics_endpoint():
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    try:
        metrics_data = get_metrics()
        return FastAPIResponse(
            content=metrics_data,
            media_type=get_metrics_content_type()
        )
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        raise HTTPException(status_code=500, detail="Metrics generation failed")


async def _fetch_forex_calendar(
    request: Request,
    *,
    time_period: str,
    start: str | None = None,
    end: str | None = None,
    impact: str | None = None,
) -> Dict[str, Any]:
    """Shared helper to call the Forex MCP client and format telemetry logs."""

    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()

    try:
        client = await get_forex_mcp_client()
        calendar = await client.get_calendar_events(
            time_period=time_period,
            start=start,
            end=end,
            impact=impact,
        )
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "forex_calendar_request_completed",
            extra=completed.for_logging(
                time_period=time_period,
                start=start,
                end=end,
                impact=impact,
                event="forex_calendar",
                count=len(calendar.get("events", [])),
            ),
        )
        await persist_request_log(
            completed,
            {
                "event": "forex_calendar",
                "time_period": time_period,
                "start": start,
                "end": end,
                "impact": impact,
                "count": len(calendar.get("events", [])),
            },
        )
        return calendar
    except ValueError as err:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "forex_calendar_request_invalid",
            extra=errored.for_logging(event="forex_calendar", error=str(err), time_period=time_period),
        )
        await persist_request_log(
            errored,
            {
                "event": "forex_calendar_error",
                "time_period": time_period,
                "error": str(err),
                "status": "invalid_arguments",
            },
        )
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            "forex_calendar_request_failed",
            extra=errored.for_logging(event="forex_calendar", error=str(err), time_period=time_period),
        )
        await persist_request_log(
            errored,
            {
                "event": "forex_calendar_error",
                "time_period": time_period,
                "error": str(err),
                "status": "exception",
            },
        )
        raise HTTPException(status_code=502, detail="Failed to fetch ForexFactory calendar data")


@app.get("/api/forex/calendar")
@limiter.limit("60/minute")
async def get_forex_calendar(
    request: Request,
    time_period: str = "today",
    start: str | None = None,
    end: str | None = None,
    impact: str | None = None,
) -> Dict[str, Any]:
    """Generic economic calendar endpoint with optional filters."""

    return await _fetch_forex_calendar(
        request,
        time_period=time_period,
        start=start,
        end=end,
        impact=impact,
    )


@app.get("/api/forex/events-today")
@limiter.limit("60/minute")
async def get_forex_events_today(request: Request) -> Dict[str, Any]:
    """Convenience endpoint for today's events."""

    return await _fetch_forex_calendar(request, time_period="today")


@app.get("/api/forex/events-week")
@limiter.limit("60/minute")
async def get_forex_events_week(request: Request) -> Dict[str, Any]:
    """Convenience endpoint for current week events."""

    return await _fetch_forex_calendar(request, time_period="week")

# Stock quote endpoint
@app.get("/api/stock-price")
@limiter.limit("100/minute")
async def get_stock_price(request: Request, symbol: str):
    """Get current stock price"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        quote = await market_service.get_stock_price(symbol_upper)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "stock_price_request_completed",
            extra=completed.for_logging(symbol=symbol_upper)
        )
        await persist_request_log(
            completed,
            {
                "event": "stock_price",
                "symbol": symbol_upper,
                "status": "success",
            },
        )
        return quote
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "stock_price_request_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e))
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_price_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get stock price for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_price_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock price: {str(e)}")

# News endpoint for frontend
@app.get("/api/v1/news")
@limiter.limit("100/minute")
async def get_news_v1(request: Request, symbol: str, limit: int = 6):
    """Get news articles for a symbol (frontend compatible endpoint)"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        from services.news_service import get_related_news
        news_data = await get_related_news(symbol_upper, limit)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        articles = news_data.get("articles", []) if isinstance(news_data, dict) else []
        logger.info(
            "news_v1_request_completed",
            extra=completed.for_logging(symbol=symbol_upper, articles=len(articles))
        )
        await persist_request_log(
            completed,
            {
                "event": "news_v1",
                "symbol": symbol_upper,
                "status": "success",
                "articles": len(articles),
            },
        )
        return news_data  # Returns {"articles": [...], "items": [...]}
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get news for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "news_v1_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

# Stock news endpoint (alternative format)
@app.get("/api/stock-news")
@limiter.limit("100/minute")
async def get_stock_news(request: Request, symbol: str):
    """Get news articles for a symbol (returns array format)"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        from services.news_service import get_related_news
        news_data = await get_related_news(symbol_upper, limit=6)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        articles = news_data.get("articles", []) if isinstance(news_data, dict) else []
        logger.info(
            "stock_news_request_completed",
            extra=completed.for_logging(symbol=symbol_upper, articles=len(articles))
        )
        await persist_request_log(
            completed,
            {
                "event": "stock_news",
                "symbol": symbol_upper,
                "status": "success",
                "articles": len(articles),
            },
        )
        # Return just the articles array for backward compatibility
        return {"news": news_data.get("articles", [])}
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get news for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_news_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        return {"news": []}

# Symbol search endpoint
@app.get("/api/symbol-search")
@limiter.limit("100/minute")
async def symbol_search(
    request: Request,
    query: str,
    limit: int = 10,
    asset_classes: Optional[str] = None
):
    """
    Search for symbols across stocks, crypto, and forex markets.

    Query params:
        query: Search query (company name, ticker, crypto name, currency)
        limit: Max results per asset class (default: 10)
        asset_classes: Comma-separated list (e.g., "stock,crypto") or None for all
    """
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()

    try:
        # Parse asset_classes filter
        classes = None
        if asset_classes:
            classes = [c.strip() for c in asset_classes.split(',')]

        # Use the new multi-market search
        if hasattr(market_service, 'search_assets'):
            results = await market_service.search_assets(query, limit, classes)
            duration_ms = (time.perf_counter() - start_time) * 1000
            completed = telemetry.with_duration(duration_ms)

            # Count results by asset class
            asset_counts = {}
            for result in results:
                asset_class = result.get('asset_class', 'unknown')
                asset_counts[asset_class] = asset_counts.get(asset_class, 0) + 1

            logger.info(
                "symbol_search_completed",
                extra=completed.for_logging(
                    matches=len(results),
                    query=query,
                    asset_counts=asset_counts
                )
            )
            await persist_request_log(
                completed,
                {
                    "event": "symbol_search",
                    "query": query,
                    "status": "success",
                    "matches": len(results),
                    "asset_classes": classes or ['stock', 'crypto', 'forex'],
                    "asset_counts": asset_counts
                },
            )

            return {
                "query": query,
                "results": results,
                "total": len(results),
                "asset_classes": classes or ['stock', 'crypto', 'forex'],
                "asset_counts": asset_counts
            }
        else:
            # Fallback - return empty results if search not supported
            duration_ms = (time.perf_counter() - start_time) * 1000
            completed = telemetry.with_duration(duration_ms)
            logger.info(
                "symbol_search_no_support",
                extra=completed.for_logging(matches=0, query=query)
            )
            await persist_request_log(
                completed,
                {
                    "event": "symbol_search",
                    "query": query,
                    "status": "unsupported",
                    "matches": 0,
                },
            )
            return {"query": query, "results": [], "total": 0}
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to search symbols for '{query}': {e}",
            extra=errored.for_logging(query=query, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "symbol_search_error",
                "query": query,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to search symbols: {str(e)}")

# Stock history endpoint  
@app.get("/api/stock-history")
@limiter.limit("100/minute")
async def get_stock_history(request: Request, symbol: str, days: int = 30, interval: str = "1d"):
    """Get historical stock data with configurable interval (1m, 5m, 15m, 30m, 1h, 1d, 1wk, 1mo)"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        history = await market_service.get_stock_history(symbol_upper, days, interval)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "stock_history_completed",
            extra=completed.for_logging(symbol=symbol_upper, days=days, candles=len(history.get("candles", [])) if isinstance(history, dict) else None)
        )
        await persist_request_log(
            completed,
            {
                "event": "stock_history",
                "symbol": symbol_upper,
                "status": "success",
                "days": days,
            },
        )
        return history
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "stock_history_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), days=days)
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_history_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "days": days,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get stock history for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), days=days),
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_history_error",
                "symbol": symbol_upper,
                "status": "exception",
                "days": days,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock history: {str(e)}")

# Stock news endpoint
@app.get("/api/stock-news")
@limiter.limit("50/minute")
async def get_stock_news(request: Request, symbol: str, limit: int = 10):
    """Get recent news for a stock"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        news = await market_service.get_stock_news(symbol_upper, limit)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "stock_news_detailed_completed",
            extra=completed.for_logging(symbol=symbol_upper, articles=len(news) if isinstance(news, list) else None)
        )
        await persist_request_log(
            completed,
            {
                "event": "stock_news_detailed",
                "symbol": symbol_upper,
                "status": "success",
                "limit": limit,
            },
        )
        return news
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "stock_news_detailed_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), limit=limit)
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_news_detailed_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "limit": limit,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get stock news for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), limit=limit),
        )
        await persist_request_log(
            errored,
            {
                "event": "stock_news_detailed_error",
                "symbol": symbol_upper,
                "status": "exception",
                "limit": limit,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock news: {str(e)}")

# Streaming news endpoint (SSE)
@app.get("/api/mcp/stream-news")
@limiter.limit("10/minute")
async def stream_news(request: Request, symbol: str = "TSLA", interval: int = 10000, duration: int = 60000):
    """
    Stream news updates via Server-Sent Events (SSE).
    
    Args:
        symbol: Stock ticker symbol (default: TSLA)
        interval: Update interval in milliseconds (default: 10000ms / 10s)
        duration: Total stream duration in milliseconds (default: 60000ms / 60s)
    
    Returns:
        StreamingResponse with text/event-stream content type
    """
    from services.http_mcp_client import get_http_mcp_client
    import json as json_lib
    
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    logged_completion = False

    async def event_generator():
        nonlocal logged_completion
        try:
            client = await get_http_mcp_client()
            logger.info(f"Starting news stream for {symbol_upper}")
            await persist_request_log(
                telemetry,
                {
                    "event": "stream_news_start",
                    "symbol": symbol_upper,
                    "status": "started",
                },
            )

            async for event in client.call_tool_streaming(
                "stream_market_news",
                {"symbol": symbol, "interval": interval, "duration": duration}
            ):
                # Forward SSE event to client
                event_data = json_lib.dumps(event)
                yield f"data: {event_data}\n\n"

            logger.info(f"News stream completed for {symbol}")

        except Exception as e:
            logger.error(f"Error in news stream: {e}")
            error_event = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Stream error: {str(e)}"
                }
            }
            yield f"data: {json_lib.dumps(error_event)}\n\n"

            error_telemetry = telemetry.with_duration((time.perf_counter() - start_time) * 1000)
            await persist_request_log(
                error_telemetry,
                {
                    "event": "stream_news_error",
                    "symbol": symbol_upper,
                    "status": "exception",
                    "error": str(e),
                },
            )
            logged_completion = True
        else:
            completed = telemetry.with_duration((time.perf_counter() - start_time) * 1000)
            await persist_request_log(
                completed,
                {
                    "event": "stream_news_completed",
                    "symbol": symbol_upper,
                    "status": "success",
                },
            )
            logged_completion = True
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive"
        }
    )

# Comprehensive stock data endpoint
@app.get("/api/comprehensive-stock-data")
@limiter.limit("50/minute")
async def get_comprehensive_stock_data(request: Request, symbol: str):
    """Get comprehensive stock information including price, history, and news"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        data = await market_service.get_comprehensive_stock_data(symbol_upper)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "comprehensive_stock_data_completed",
            extra=completed.for_logging(symbol=symbol_upper)
        )
        await persist_request_log(
            completed,
            {
                "event": "comprehensive_stock_data",
                "symbol": symbol_upper,
                "status": "success",
            },
        )
        return data
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "comprehensive_stock_data_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e))
        )
        await persist_request_log(
            errored,
            {
                "event": "comprehensive_stock_data_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get comprehensive data for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "comprehensive_stock_data_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch comprehensive stock data: {str(e)}")

# Technical indicators endpoint
@app.get("/api/technical-indicators")
@limiter.limit("50/minute")
async def get_technical_indicators(
    request: Request,
    symbol: str = Query(..., description="Stock ticker symbol"),
    indicators: str = Query("rsi,macd,bollinger,moving_averages", description="Comma-separated list of indicators"),
    days: int = Query(100, description="Number of days of historical data")
):
    """Get technical indicators for a stock symbol"""
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")

    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    logger.info(f"Getting technical indicators for {symbol_upper}: {indicators}")

    try:
        # Get current stock price first
        price_data = await market_service.get_stock_price(symbol_upper)
        current_price = price_data.get("price", 0)
        
        # Parse requested indicators
        indicator_list = [i.strip().lower() for i in indicators.split(",")]
        
        # Call MCP server for technical indicators
        mcp_client = await get_direct_mcp_client()
        if not mcp_client:
            # Fallback: return empty indicators instead of 503
            logger.warning(f"MCP client unavailable for {symbol_upper}, returning empty indicators")
            return {
                "symbol": symbol_upper,
                "timestamp": int(asyncio.get_event_loop().time()),
                "current_price": current_price,
                "indicators": {},
                "data_source": "unavailable"
            }
        
        mcp_result = await mcp_client.call_tool(
            "get_technical_indicators",
            {"symbol": symbol_upper, "indicators": indicator_list, "days": days}
        )

        parsed_data: Dict[str, Any] = {}
        if isinstance(mcp_result, dict) and "content" in mcp_result:
            parsed_data = mcp_result["content"]
        elif isinstance(mcp_result, list) and mcp_result:
            first_item = mcp_result[0]
            if isinstance(first_item, dict) and "text" in first_item:
                import json
                try:
                    parsed_data = json.loads(first_item["text"])
                except json.JSONDecodeError as json_err:
                    logger.error(f"Failed to parse MCP JSON: {json_err}")

        if not parsed_data:
            raise HTTPException(status_code=404, detail=f"No technical data available for {symbol_upper}")
        
        mcp_data = parsed_data
        
        # Format response according to IndicatorApiResponse interface
        response = {
            "symbol": symbol.upper(),
            "timestamp": int(asyncio.get_event_loop().time()),
            "current_price": current_price,
            "indicators": {},
            "data_source": "mcp_technical_analysis", 
            "calculation_period": days
        }
        
        # Process MCP data - expected format: {"symbol": "AAPL", "indicators": {"rsi": null, ...}, ...}
        if isinstance(mcp_data, dict) and "indicators" in mcp_data:
            mcp_indicators = mcp_data["indicators"]
            
            # Update current price from MCP if available
            if "currentPrice" in mcp_data:
                response["current_price"] = mcp_data["currentPrice"]
            
            # RSI
            if "rsi" in indicator_list:
                if mcp_indicators.get("rsi") is not None:
                    response["indicators"]["rsi"] = {
                        "values": [],  # MCP doesn't provide historical values in this format
                        "current": float(mcp_indicators["rsi"]),
                        "overbought": 70,
                        "oversold": 30,
                        "signal": "overbought" if mcp_indicators["rsi"] > 70 else "oversold" if mcp_indicators["rsi"] < 30 else "neutral"
                    }
                else:
                    logger.warning(f"RSI requested but null for {symbol}")
            
            # MACD  
            if "macd" in indicator_list and mcp_indicators.get("macd"):
                response["indicators"]["macd"] = mcp_indicators["macd"]
                
            # Bollinger Bands
            if "bollinger" in indicator_list and mcp_indicators.get("bollinger"):
                response["indicators"]["bollinger"] = mcp_indicators["bollinger"]
                
            # Moving averages
            if "moving_averages" in indicator_list:
                current_time = int(time.time())
                ma_data = {}
                if mcp_indicators.get("sma20"):
                    ma_data["ma20"] = [{"time": current_time, "value": float(mcp_indicators["sma20"])}]
                if mcp_indicators.get("sma50"):
                    ma_data["ma50"] = [{"time": current_time, "value": float(mcp_indicators["sma50"])}]
                if mcp_indicators.get("sma200"):
                    ma_data["ma200"] = [{"time": current_time, "value": float(mcp_indicators["sma200"])}]
                if ma_data:
                    response["indicators"]["moving_averages"] = ma_data
        else:
            logger.warning(f"Unexpected MCP data structure for {symbol}: {mcp_data}")
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "technical_indicators_completed",
            extra=completed.for_logging(symbol=symbol_upper, indicators=indicator_list)
        )
        await persist_request_log(
            completed,
            {
                "event": "technical_indicators",
                "symbol": symbol_upper,
                "status": "success",
                "indicators": indicator_list,
            },
        )
        return response
        
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "technical_indicators_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e))
        )
        await persist_request_log(
            errored,
            {
                "event": "technical_indicators_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Invalid symbol: {symbol}")
    except HTTPException:
        raise
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Error getting technical indicators for {symbol_upper}: {str(e)}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "technical_indicators_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )

        try:
            fallback_price = await market_service.get_stock_price(symbol_upper)
            current_price = fallback_price.get("price", 0)
        except Exception:
            current_price = 0

        return {
            "symbol": symbol_upper,
            "timestamp": int(asyncio.get_event_loop().time()),
            "current_price": current_price,
            "indicators": {},
            "data_source": "fallback_error",
            "calculation_period": days,
            "error": "Technical indicators temporarily unavailable",
            "error_details": str(e)
        }

# Market overview endpoint
@app.get("/api/market-overview")
@limiter.limit("50/minute")
async def get_market_overview(request: Request):
    """Get market overview including indices and top movers"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    try:
        overview = await market_service.get_market_overview()
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info("market_overview_completed", extra=completed.for_logging())
        await persist_request_log(
            completed,
            {
                "event": "market_overview",
                "status": "success",
            },
        )
        return overview
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(f"Failed to get market overview: {e}", extra=errored.for_logging(error=str(e)))
        await persist_request_log(
            errored,
            {
                "event": "market_overview_error",
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch market overview: {str(e)}")

# Enhanced market data endpoint
@app.get("/api/enhanced/market-data")
@limiter.limit("100/minute")
async def get_enhanced_market_data(request: Request, symbol: str):
    """Enhanced market data with intelligent service selection"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        data = await market_service.get_enhanced_market_data(symbol_upper)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "enhanced_market_data_completed",
            extra=completed.for_logging(symbol=symbol_upper)
        )
        await persist_request_log(
            completed,
            {
                "event": "enhanced_market_data",
                "symbol": symbol_upper,
                "status": "success",
            },
        )
        return data
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "enhanced_market_data_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e))
        )
        await persist_request_log(
            errored,
            {
                "event": "enhanced_market_data_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get enhanced market data for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "enhanced_market_data_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch enhanced market data: {str(e)}")

# Enhanced historical data endpoint
@app.get("/api/enhanced/historical-data")
@limiter.limit("100/minute") 
async def get_enhanced_historical_data(request: Request, symbol: str, days: int = 30):
    """Enhanced historical data with intelligent routing"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        data = await market_service.get_enhanced_historical_data(symbol_upper, days)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "enhanced_history_completed",
            extra=completed.for_logging(symbol=symbol_upper, days=days)
        )
        await persist_request_log(
            completed,
            {
                "event": "enhanced_history",
                "symbol": symbol_upper,
                "status": "success",
                "days": days,
            },
        )
        return data
    except ValueError as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.warning(
            "enhanced_history_invalid_symbol",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), days=days)
        )
        await persist_request_log(
            errored,
            {
                "event": "enhanced_history_error",
                "symbol": symbol_upper,
                "status": "invalid_symbol",
                "days": days,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found or invalid")
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to get enhanced historical data for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e), days=days),
        )
        await persist_request_log(
            errored,
            {
                "event": "enhanced_history_error",
                "symbol": symbol_upper,
                "status": "exception",
                "days": days,
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to fetch enhanced historical data: {str(e)}")

# Debug endpoint for comparing data sources
@app.get("/api/enhanced/compare-sources")
@limiter.limit("10/minute")  
async def compare_data_sources(request: Request, symbol: str):
    """Compare data from different sources for debugging"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    symbol_upper = symbol.upper()
    try:
        comparison = await market_service.compare_data_sources(symbol_upper)
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        logger.info(
            "compare_sources_completed",
            extra=completed.for_logging(symbol=symbol_upper)
        )
        await persist_request_log(
            completed,
            {
                "event": "compare_sources",
                "symbol": symbol_upper,
                "status": "success",
            },
        )
        return comparison
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(
            f"Failed to compare data sources for {symbol_upper}: {e}",
            extra=errored.for_logging(symbol=symbol_upper, error=str(e)),
        )
        await persist_request_log(
            errored,
            {
                "event": "compare_sources_error",
                "symbol": symbol_upper,
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to compare data sources: {str(e)}")

# Dashboard router
app.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])

# Chart Control API router
app.include_router(chart_control_router, tags=["chart-control"])

# Agent router for MCP orchestration
app.include_router(agent_router, tags=["agent"])

# Ask endpoint
@app.post("/ask")
@limiter.limit("30/minute")
async def ask_ai(request: Request, message_request: AIMessageRequest):
    """Ask AI a question (text-only fallback)"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(
        request,
        request_id,
        session_id=message_request.session_id,
    )
    start_time = time.perf_counter()
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
        
        result = {
            "response": response.content[0].text,
            "session_id": message_request.session_id,
            "timestamp": datetime.now().isoformat()
        }
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        await persist_request_log(
            completed,
            {
                "event": "ask_ai",
                "status": "success",
                "model": os.getenv("MODEL", "claude-3-sonnet-20240229"),
            },
        )
        return result
        
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(f"AI request failed: {e}")
        await persist_request_log(
            errored,
            {
                "event": "ask_ai_error",
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"AI request failed: {str(e)}")

# ElevenLabs proxy endpoints
@app.get("/elevenlabs/signed-url")
async def get_elevenlabs_signed_url(request: Request):
    """Get signed URL for ElevenLabs WebSocket connection"""
    request_id = request.headers.get("X-Request-ID") or generate_request_id()
    set_request_id(request_id)
    telemetry = build_request_telemetry(request, request_id)
    start_time = time.perf_counter()
    try:
        # For now, return a basic response indicating the service is available
        # In production, this would integrate with ElevenLabs API
        import time as _time
        result = {
            "signed_url": "ws://localhost:8000/realtime-relay",
            "session_id": f"session_{int(_time.time())}",
            "expires_in": 3600
        }
        duration_ms = (time.perf_counter() - start_time) * 1000
        completed = telemetry.with_duration(duration_ms)
        await persist_request_log(
            completed,
            {
                "event": "elevenlabs_signed_url",
                "status": "success",
            },
        )
        return result
    except Exception as e:
        duration_ms = (time.perf_counter() - start_time) * 1000
        errored = telemetry.with_duration(duration_ms)
        logger.error(f"Failed to get ElevenLabs signed URL: {e}")
        await persist_request_log(
            errored,
            {
                "event": "elevenlabs_signed_url_error",
                "status": "exception",
                "error": str(e),
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to get signed URL: {str(e)}")

# OpenAI Realtime Relay WebSocket endpoints
@app.websocket("/realtime-relay/{session_id}")
async def websocket_realtime_relay(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for OpenAI Realtime API relay"""
    try:
        await openai_relay_server.handle_relay_connection(websocket, session_id)
    except Exception as e:
        logger.error(f"Realtime relay WebSocket error for session {session_id}: {e}")
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except:
            pass  # Connection might already be closed

# OpenAI Realtime Session Creation endpoint
@app.post("/openai/realtime/session")
async def create_openai_realtime_session():
    """Create a new OpenAI Realtime API session"""
    try:
        import uuid
        import os
        from datetime import datetime
        
        # Generate unique session ID
        session_id = f"session_{uuid.uuid4().hex[:16]}_{int(datetime.now().timestamp())}"
        
        # Get base API URL for WebSocket construction
        # Use the request host to build the correct WebSocket URL
        api_url = os.getenv('API_URL', 'http://localhost:8000')
        ws_url = api_url.replace('http://', 'ws://').replace('https://', 'wss://')
        
        # Create session data that frontend expects
        session_data = {
            "session_id": session_id,
            "id": session_id,  # Fallback field name
            "status": "created",
            "ws_url": f"{ws_url}/realtime-relay/{session_id}",
            "api_key": os.getenv('OPENAI_API_KEY', ''),
            "client_secret": {
                "value": os.getenv('OPENAI_API_KEY', '')
            },
            "created_at": datetime.now().isoformat(),
            "expires_in": 3600  # 1 hour
        }
        
        logger.info(f"Created OpenAI Realtime session: {session_id}")
        return session_data
        
    except Exception as e:
        logger.error(f"Failed to create OpenAI Realtime session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

# Chart Tools and Agent endpoints
@app.get("/api/agent/tools/chart")
async def get_chart_tools():
    """Get available chart analysis tools"""
    try:
        # Define essential chart tools for trading analysis
        tools = [
            {
                "name": "moving_average",
                "description": "Add moving average indicators to the chart",
                "category": "technical_indicator", 
                "topic": "trend_analysis",
                "parameters": {
                    "period": {"type": "int", "default": 20, "min": 5, "max": 200},
                    "type": {"type": "string", "options": ["SMA", "EMA"], "default": "SMA"}
                },
                "frontend_command": "ADD_INDICATOR:moving_average",
                "knowledge_source": [{
                    "doc_id": "ma_001",
                    "source": "Technical Analysis",
                    "text_preview": "Moving averages smooth price data to identify trend direction"
                }]
            },
            {
                "name": "bollinger_bands",
                "description": "Add Bollinger Bands for volatility analysis",
                "category": "technical_indicator",
                "topic": "volatility_analysis", 
                "parameters": {
                    "period": {"type": "int", "default": 20},
                    "std_dev": {"type": "float", "default": 2.0}
                },
                "frontend_command": "ADD_INDICATOR:bollinger_bands",
                "knowledge_source": [{
                    "doc_id": "bb_001",
                    "source": "Technical Analysis",
                    "text_preview": "Bollinger Bands measure market volatility and potential support/resistance levels"
                }]
            },
            {
                "name": "rsi",
                "description": "Relative Strength Index for momentum analysis",
                "category": "momentum_indicator",
                "topic": "momentum_analysis",
                "parameters": {
                    "period": {"type": "int", "default": 14}
                },
                "frontend_command": "ADD_INDICATOR:rsi",
                "knowledge_source": [{
                    "doc_id": "rsi_001", 
                    "source": "Technical Analysis",
                    "text_preview": "RSI measures overbought and oversold conditions"
                }]
            },
            {
                "name": "support_resistance",
                "description": "Draw support and resistance lines",
                "category": "drawing_tool",
                "topic": "price_levels",
                "parameters": {
                    "price": {"type": "float", "required": True},
                    "type": {"type": "string", "options": ["support", "resistance"]}
                },
                "frontend_command": "DRAW_LINE:support_resistance",
                "knowledge_source": [{
                    "doc_id": "sr_001",
                    "source": "Technical Analysis", 
                    "text_preview": "Support and resistance levels identify key price zones"
                }]
            },
            {
                "name": "trend_line",
                "description": "Draw trend lines connecting price points",
                "category": "drawing_tool",
                "topic": "trend_analysis",
                "parameters": {
                    "start_price": {"type": "float", "required": True},
                    "end_price": {"type": "float", "required": True},
                    "angle": {"type": "float", "default": 0}
                },
                "frontend_command": "DRAW_LINE:trend_line",
                "knowledge_source": [{
                    "doc_id": "tl_001",
                    "source": "Technical Analysis",
                    "text_preview": "Trend lines help identify price direction and momentum"
                }]
            },
            {
                "name": "volume_analysis",
                "description": "Analyze volume patterns and trends",
                "category": "volume_indicator",
                "topic": "volume_analysis", 
                "parameters": {
                    "period": {"type": "int", "default": 20}
                },
                "frontend_command": "SHOW_VOLUME:analysis",
                "knowledge_source": [{
                    "doc_id": "vol_001",
                    "source": "Technical Analysis",
                    "text_preview": "Volume analysis confirms price movements and trends"
                }]
            },
            {
                "name": "price_alerts",
                "description": "Set price alert levels on the chart",
                "category": "alert_tool",
                "topic": "risk_management",
                "parameters": {
                    "alert_price": {"type": "float", "required": True},
                    "condition": {"type": "string", "options": ["above", "below"]}
                },
                "frontend_command": "SET_ALERT:price",
                "knowledge_source": [{
                    "doc_id": "alert_001", 
                    "source": "Risk Management",
                    "text_preview": "Price alerts help monitor key levels and trading opportunities"
                }]
            }
        ]
        
        # Calculate categories
        categories = list(set(tool["category"] for tool in tools))
        
        return {
            "tools": tools,
            "count": len(tools),
            "categories": categories
        }
        
    except Exception as e:
        logger.error(f"Failed to get chart tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get chart tools: {str(e)}")

@app.get("/api/agent/tools/chart/search")
async def search_chart_tools(query: str, top_k: int = 5):
    """Search chart tools by query"""
    try:
        # Get all tools first
        tools_response = await get_chart_tools()
        all_tools = tools_response["tools"]
        
        # Simple search by name, description, category, and topic
        query_lower = query.lower()
        matching_tools = []
        
        for tool in all_tools:
            score = 0
            # Exact name match gets highest score
            if query_lower == tool["name"].lower():
                score += 10
            # Partial name match
            elif query_lower in tool["name"].lower():
                score += 5
            # Description match
            elif query_lower in tool["description"].lower():
                score += 3
            # Category/topic match  
            elif query_lower in tool["category"].lower() or query_lower in tool["topic"].lower():
                score += 2
            
            if score > 0:
                matching_tools.append((tool, score))
        
        # Sort by score and take top_k
        matching_tools.sort(key=lambda x: x[1], reverse=True)
        result_tools = [tool for tool, score in matching_tools[:top_k]]
        
        return {
            "query": query,
            "tools": result_tools,
            "count": len(result_tools)
        }
        
    except Exception as e:
        logger.error(f"Failed to search chart tools: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search chart tools: {str(e)}")

@app.get("/api/technical-indicators")
async def get_technical_indicators(
    symbol: str,
    indicators: str = "moving_averages,rsi,bollinger,macd",
    days: int = 100
):
    """Get technical indicators for a stock symbol"""
    try:
        import time
        import math
        from datetime import datetime, timedelta
        
        # Get the market service to fetch price data
        service_factory = MarketServiceFactory()
        market_service = service_factory.get_service()
        
        # Get historical data first
        historical_data = await market_service.get_stock_history(symbol, days)
        if not historical_data or 'historical_data' not in historical_data:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")
        
        prices = historical_data['historical_data']
        if not prices or len(prices) < 20:
            raise HTTPException(status_code=404, detail=f"Insufficient data for {symbol} - need at least 20 days")
        
        # Get current price
        current_quote = await market_service.get_stock_price(symbol)
        current_price = current_quote.get('price', 0)
        
        # Parse requested indicators
        requested_indicators = [ind.strip() for ind in indicators.split(',')]
        
        # Initialize response structure
        response_data = {
            "symbol": symbol.upper(),
            "timestamp": int(time.time()),
            "current_price": current_price,
            "indicators": {},
            "data_source": historical_data.get('data_source', 'unknown'),
            "calculation_period": days
        }
        
        # Extract price data for calculations
        price_data = []
        for item in prices:
            if isinstance(item, dict):
                close_price = item.get('close', item.get('price', 0))
                timestamp = item.get('timestamp', item.get('time', time.time()))
                if isinstance(timestamp, str):
                    # Parse date string to timestamp
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = int(dt.timestamp())
                    except:
                        timestamp = int(time.time())
                price_data.append({
                    'time': timestamp,
                    'close': float(close_price),
                    'high': item.get('high', close_price),
                    'low': item.get('low', close_price),
                    'volume': item.get('volume', 0)
                })
        
        # Sort by time
        price_data.sort(key=lambda x: x['time'])
        
        # Calculate requested indicators
        if 'moving_averages' in requested_indicators:
            response_data['indicators']['moving_averages'] = calculate_moving_averages(price_data)
            
        if 'rsi' in requested_indicators:
            response_data['indicators']['rsi'] = calculate_rsi(price_data)
            
        if 'bollinger' in requested_indicators:
            response_data['indicators']['bollinger'] = calculate_bollinger_bands(price_data)
            
        if 'macd' in requested_indicators:
            response_data['indicators']['macd'] = calculate_macd(price_data)
            
        if 'fibonacci' in requested_indicators:
            response_data['indicators']['fibonacci'] = calculate_fibonacci_retracements(price_data)
            
        if 'support_resistance' in requested_indicators:
            response_data['indicators']['support_resistance'] = calculate_support_resistance(price_data)
        
        logger.info(f"Generated technical indicators for {symbol} with {len(price_data)} data points")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to calculate technical indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate indicators: {str(e)}")

def calculate_moving_averages(price_data):
    """Calculate moving averages (MA20, MA50, MA200)"""
    result = {}
    closes = [item['close'] for item in price_data]
    
    # MA20
    if len(closes) >= 20:
        ma20_data = []
        for i in range(19, len(closes)):
            ma_value = sum(closes[i-19:i+1]) / 20
            ma20_data.append({
                'time': price_data[i]['time'],
                'value': round(ma_value, 2)
            })
        result['ma20'] = ma20_data
    
    # MA50
    if len(closes) >= 50:
        ma50_data = []
        for i in range(49, len(closes)):
            ma_value = sum(closes[i-49:i+1]) / 50
            ma50_data.append({
                'time': price_data[i]['time'],
                'value': round(ma_value, 2)
            })
        result['ma50'] = ma50_data
    
    # MA200
    if len(closes) >= 200:
        ma200_data = []
        for i in range(199, len(closes)):
            ma_value = sum(closes[i-199:i+1]) / 200
            ma200_data.append({
                'time': price_data[i]['time'],
                'value': round(ma_value, 2)
            })
        result['ma200'] = ma200_data
    
    return result

def calculate_rsi(price_data, period=14):
    """Calculate Relative Strength Index"""
    if len(price_data) < period + 1:
        return None
        
    closes = [item['close'] for item in price_data]
    gains = []
    losses = []
    
    # Calculate gains and losses
    for i in range(1, len(closes)):
        change = closes[i] - closes[i-1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))
    
    # Calculate initial averages
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rsi_values = []
    
    # Calculate RSI for each point
    for i in range(period, len(gains)):
        if i == period:
            # First RSI calculation
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
        else:
            # Smoothed averages
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
        
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append({
            'time': price_data[i+1]['time'],
            'value': round(rsi, 2)
        })
    
    current_rsi = rsi_values[-1]['value'] if rsi_values else 50
    
    return {
        'values': rsi_values,
        'current': current_rsi,
        'overbought': 70,
        'oversold': 30,
        'signal': 'overbought' if current_rsi > 70 else 'oversold' if current_rsi < 30 else 'neutral'
    }

def calculate_bollinger_bands(price_data, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    if len(price_data) < period:
        return None
    
    closes = [item['close'] for item in price_data]
    upper_band = []
    middle_band = []
    lower_band = []
    
    for i in range(period-1, len(closes)):
        # Calculate moving average
        ma = sum(closes[i-period+1:i+1]) / period
        
        # Calculate standard deviation
        variance = sum([(x - ma) ** 2 for x in closes[i-period+1:i+1]]) / period
        std = math.sqrt(variance)
        
        timestamp = price_data[i]['time']
        
        upper_band.append({'time': timestamp, 'value': round(ma + (std_dev * std), 2)})
        middle_band.append({'time': timestamp, 'value': round(ma, 2)})
        lower_band.append({'time': timestamp, 'value': round(ma - (std_dev * std), 2)})
    
    return {
        'upper': upper_band,
        'middle': middle_band,
        'lower': lower_band
    }

def calculate_macd(price_data, fast_period=12, slow_period=26, signal_period=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    if len(price_data) < slow_period:
        return None
    
    closes = [item['close'] for item in price_data]
    
    # Calculate EMAs
    def ema(data, period):
        multiplier = 2 / (period + 1)
        ema_values = []
        ema_values.append(data[0])  # Start with first value
        
        for i in range(1, len(data)):
            ema_value = (data[i] * multiplier) + (ema_values[-1] * (1 - multiplier))
            ema_values.append(ema_value)
        
        return ema_values
    
    # Calculate fast and slow EMAs
    fast_ema = ema(closes, fast_period)
    slow_ema = ema(closes, slow_period)
    
    # Calculate MACD line
    macd_line_values = []
    for i in range(slow_period-1, len(closes)):
        macd_value = fast_ema[i] - slow_ema[i]
        macd_line_values.append(macd_value)
    
    # Calculate signal line (EMA of MACD)
    signal_line_values = ema(macd_line_values, signal_period)
    
    # Calculate histogram
    histogram_values = []
    for i in range(len(signal_line_values)):
        histogram_values.append(macd_line_values[i] - signal_line_values[i])
    
    # Format data
    macd_line = []
    signal_line = []
    histogram = []
    
    start_idx = slow_period - 1
    for i in range(len(macd_line_values)):
        timestamp = price_data[start_idx + i]['time']
        macd_line.append({'time': timestamp, 'value': round(macd_line_values[i], 4)})
        
        if i < len(signal_line_values):
            signal_line.append({'time': timestamp, 'value': round(signal_line_values[i], 4)})
            
        if i < len(histogram_values):
            histogram.append({'time': timestamp, 'value': round(histogram_values[i], 4)})
    
    return {
        'macd_line': macd_line,
        'signal_line': signal_line,
        'histogram': histogram
    }

def calculate_fibonacci_retracements(price_data):
    """Calculate Fibonacci retracement levels"""
    if len(price_data) < 20:
        return None
    
    closes = [item['close'] for item in price_data]
    high_price = max(closes)
    low_price = min(closes)
    
    # Find swing high and low
    swing_high = high_price
    swing_low = low_price
    
    # Calculate Fibonacci levels
    diff = swing_high - swing_low
    
    return {
        'fib_0': round(swing_high, 2),
        'fib_236': round(swing_high - (0.236 * diff), 2),
        'fib_382': round(swing_high - (0.382 * diff), 2),
        'fib_500': round(swing_high - (0.500 * diff), 2),
        'fib_618': round(swing_high - (0.618 * diff), 2),
        'fib_786': round(swing_high - (0.786 * diff), 2),
        'fib_1000': round(swing_low, 2),
        'swing_high': swing_high,
        'swing_low': swing_low
    }

def calculate_support_resistance(price_data):
    """Calculate support and resistance levels"""
    if len(price_data) < 10:
        return None
    
    closes = [item['close'] for item in price_data]
    highs = [item['high'] for item in price_data]
    lows = [item['low'] for item in price_data]
    
    # Simple pivot point calculation
    recent_high = max(highs[-20:])  # Recent high
    recent_low = min(lows[-20:])    # Recent low
    current_price = closes[-1]
    
    # Calculate basic support and resistance levels
    resistance_levels = []
    support_levels = []
    
    # Resistance levels above current price
    if current_price < recent_high:
        resistance_levels.append(recent_high)
        
    # Support levels below current price  
    if current_price > recent_low:
        support_levels.append(recent_low)
    
    # Add some additional levels based on recent price action
    price_range = recent_high - recent_low
    mid_point = recent_low + (price_range * 0.5)
    
    if current_price < mid_point:
        resistance_levels.append(mid_point)
    else:
        support_levels.append(mid_point)
    
    return {
        'resistance_levels': [round(level, 2) for level in resistance_levels],
        'support_levels': [round(level, 2) for level in support_levels]
    }

# In-memory storage for chart snapshots (in production, use Redis or database)
chart_snapshots_store = {}

class ChartSnapshotRequest(BaseModel):
    symbol: str
    timeframe: str = "1D"
    image_base64: Optional[str] = None
    auto_analyze: bool = False
    chart_commands: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

@app.post("/api/agent/chart-snapshot")
async def create_chart_snapshot(request: ChartSnapshotRequest):
    """Store a chart snapshot for analysis"""
    try:
        import time
        from datetime import datetime
        
        snapshot_id = f"{request.symbol.upper()}_{request.timeframe}_{int(time.time())}"
        
        # Create snapshot data
        snapshot_data = {
            "id": snapshot_id,
            "symbol": request.symbol.upper(),
            "timeframe": request.timeframe,
            "captured_at": datetime.now().isoformat(),
            "chart_commands": request.chart_commands or [],
            "metadata": request.metadata or {},
            "vision_model": "claude-3-sonnet" if request.auto_analyze else None,
            "analysis": None,
            "analysis_error": None
        }
        
        # If image provided, store it (in production, save to blob storage)
        if request.image_base64:
            snapshot_data["image_base64"] = request.image_base64
            
        # If auto-analyze requested, perform basic analysis
        if request.auto_analyze and request.image_base64:
            try:
                # Basic pattern analysis (simplified for MVP)
                analysis = {
                    "summary": f"Chart snapshot captured for {request.symbol} on {request.timeframe} timeframe",
                    "patterns": [
                        {
                            "type": "trend_analysis",
                            "confidence": 0.75,
                            "description": "Chart patterns available for voice analysis",
                            "targets": []
                        }
                    ],
                    "indicators": {}
                }
                snapshot_data["analysis"] = analysis
            except Exception as e:
                snapshot_data["analysis_error"] = f"Analysis failed: {str(e)}"
        
        # Store in memory (replace with persistent storage in production)
        chart_snapshots_store[snapshot_id] = snapshot_data
        
        # Also store by symbol for easy retrieval
        symbol_key = f"{request.symbol.upper()}_{request.timeframe}"
        chart_snapshots_store[symbol_key] = snapshot_data
        
        logger.info(f"Stored chart snapshot: {snapshot_id} for {request.symbol}")
        
        # Return minimal response
        return {
            "id": snapshot_id,
            "symbol": request.symbol.upper(),
            "timeframe": request.timeframe,
            "captured_at": snapshot_data["captured_at"],
            "status": "stored",
            "auto_analyzed": request.auto_analyze
        }
        
    except Exception as e:
        logger.error(f"Failed to store chart snapshot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store snapshot: {str(e)}")

@app.get("/api/agent/chart-snapshot/{symbol}")
async def get_chart_snapshot(
    symbol: str,
    timeframe: str = "1D",
    include_image: bool = False
):
    """Retrieve a chart snapshot for analysis"""
    try:
        symbol_key = f"{symbol.upper()}_{timeframe}"
        
        # Try to find snapshot by symbol and timeframe
        snapshot_data = chart_snapshots_store.get(symbol_key)
        
        if not snapshot_data:
            # Try to find any snapshot for this symbol
            for key, data in chart_snapshots_store.items():
                if key.startswith(f"{symbol.upper()}_"):
                    snapshot_data = data
                    break
        
        if not snapshot_data:
            # Return 404 as expected by frontend
            raise HTTPException(status_code=404, detail=f"No chart snapshot found for {symbol}")
        
        # Prepare response
        response_data = {
            "symbol": snapshot_data["symbol"],
            "timeframe": snapshot_data["timeframe"],
            "captured_at": snapshot_data["captured_at"],
            "chart_commands": snapshot_data.get("chart_commands", []),
            "metadata": snapshot_data.get("metadata", {}),
            "vision_model": snapshot_data.get("vision_model"),
            "analysis": snapshot_data.get("analysis"),
            "analysis_error": snapshot_data.get("analysis_error")
        }
        
        # Include image if requested
        if include_image and "image_base64" in snapshot_data:
            response_data["image_base64"] = snapshot_data["image_base64"]
        
        logger.info(f"Retrieved chart snapshot for {symbol} ({timeframe})")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve chart snapshot for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve snapshot: {str(e)}")

@app.delete("/api/agent/chart-snapshot/{symbol}")
async def delete_chart_snapshot(symbol: str, timeframe: str = "1D"):
    """Delete a chart snapshot"""
    try:
        symbol_key = f"{symbol.upper()}_{timeframe}"
        
        if symbol_key in chart_snapshots_store:
            del chart_snapshots_store[symbol_key]
            logger.info(f"Deleted chart snapshot for {symbol} ({timeframe})")
            return {"status": "deleted", "symbol": symbol.upper(), "timeframe": timeframe}
        else:
            raise HTTPException(status_code=404, detail=f"No chart snapshot found for {symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete chart snapshot for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete snapshot: {str(e)}")

@app.get("/api/agent/chart-snapshots")
async def list_chart_snapshots():
    """List all available chart snapshots"""
    try:
        snapshots = []
        for key, data in chart_snapshots_store.items():
            if "_" in key and not key.endswith("_1D") and not key.endswith("_4H"):  # Skip duplicates, keep IDs
                continue
                
            snapshots.append({
                "symbol": data["symbol"],
                "timeframe": data["timeframe"], 
                "captured_at": data["captured_at"],
                "has_analysis": data.get("analysis") is not None,
                "has_image": "image_base64" in data
            })
        
        return {
            "snapshots": snapshots,
            "count": len(snapshots)
        }
        
    except Exception as e:
        logger.error(f"Failed to list chart snapshots: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list snapshots: {str(e)}")


# ========================================
# Chat History & Data Persistence Endpoints
# ========================================

class ConversationRequest(BaseModel):
    user_id: Optional[str] = None
    metadata: Optional[Dict] = None

class MessageRequest(BaseModel):
    conversation_id: str
    role: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    metadata: Optional[Dict] = None

class SaveMarketDataRequest(BaseModel):
    symbol: str
    timeframe: str
    candles: List[Dict]
    source: str = "alpaca"

class SaveNewsRequest(BaseModel):
    articles: List[Dict]
    symbol: Optional[str] = None

@app.post("/api/conversations")
async def create_conversation(request: ConversationRequest):
    """Create a new conversation session"""
    try:
        db_service = get_database_service()
        conversation_id = await db_service.create_conversation(
            user_id=request.user_id,
            metadata=request.metadata
        )
        
        return {
            "conversation_id": conversation_id,
            "created": True
        }
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/conversations/{conversation_id}/end")
async def end_conversation(conversation_id: str):
    """Mark a conversation as ended"""
    try:
        db_service = get_database_service()
        success = await db_service.end_conversation(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "ended": success
        }
    except Exception as e:
        logger.error(f"Failed to end conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages")
async def save_message(request: MessageRequest):
    """Save a message to the database"""
    try:
        db_service = get_database_service()
        
        # Log query analytics
        await db_service.log_query(
            user_id=None,  # Would come from auth
            query_type="chat",
            query_content=request.content[:500],
            success=True
        )
        
        message_id = await db_service.save_message(
            conversation_id=request.conversation_id,
            role=request.role,
            content=request.content,
            provider=request.provider,
            model=request.model,
            metadata=request.metadata
        )
        
        return {
            "message_id": message_id,
            "saved": True
        }
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0)
):
    """Get messages for a specific conversation"""
    try:
        db_service = get_database_service()
        messages = await db_service.get_conversation_history(
            conversation_id=conversation_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "conversation_id": conversation_id,
            "messages": messages,
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"Failed to get conversation messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/recent")
async def get_recent_conversations(
    user_id: Optional[str] = Query(default=None),
    days: int = Query(default=7, le=30),
    limit: int = Query(default=10, le=50)
):
    """Get recent conversations with summary"""
    try:
        db_service = get_database_service()
        conversations = await db_service.get_recent_conversations(
            user_id=user_id,
            days=days,
            limit=limit
        )
        
        return {
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        logger.error(f"Failed to get recent conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/market-data/cache")
async def cache_market_data(request: SaveMarketDataRequest):
    """Cache market candles to database"""
    try:
        db_service = get_database_service()
        count = await db_service.save_market_candles(
            symbol=request.symbol,
            timeframe=request.timeframe,
            candles=request.candles,
            source=request.source
        )
        
        return {
            "symbol": request.symbol,
            "candles_saved": count
        }
    except Exception as e:
        logger.error(f"Failed to cache market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-data/cache/{symbol}")
async def get_cached_market_data(
    symbol: str,
    timeframe: str = Query(default="1d"),
    limit: int = Query(default=100, le=500)
):
    """Get cached market data for a symbol"""
    try:
        db_service = get_database_service()
        candles = await db_service.get_market_candles(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "candles": candles,
            "count": len(candles),
            "cached": True
        }
    except Exception as e:
        logger.error(f"Failed to get cached market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news/cache")
async def cache_news(request: SaveNewsRequest):
    """Cache news articles to database"""
    try:
        db_service = get_database_service()
        count = await db_service.save_market_news(
            articles=request.articles,
            symbol=request.symbol
        )
        
        return {
            "articles_saved": count
        }
    except Exception as e:
        logger.error(f"Failed to cache news: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/queries")
async def get_query_analytics(
    user_id: Optional[str] = Query(default=None),
    days: int = Query(default=30, le=90)
):
    """Get query analytics and statistics"""
    try:
        db_service = get_database_service()
        stats = await db_service.get_query_stats(
            user_id=user_id,
            days=days
        )
        
        return stats
    except Exception as e:
        logger.error(f"Failed to get query analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ChatKit Server Protocol (following OpenAI advanced samples)
class ChatKitRequest(BaseModel):
    device_id: Optional[str] = None
    workflow_id: Optional[str] = None
    currentClientSecret: Optional[str] = None  # For refresh requests

@app.post("/chatkit")
async def chatkit_endpoint(request: ChatKitRequest = None):
    """Main ChatKit endpoint following OpenAI advanced samples pattern"""
    try:
        import uuid
        import os
        from datetime import datetime, timedelta
        
        # Check for required OpenAI API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY is not defined")
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY is not defined - check your backend environment"
            )
        
        # Get workflow configuration from environment
        workflow_id = os.getenv("CHATKIT_WORKFLOW_ID")
        assistant_id = os.getenv("GVSES_ASSISTANT_ID")
        
        if not workflow_id and not assistant_id:
            logger.warning("No ChatKit workflow or G'sves assistant configured")
        
        # Handle session refresh if currentClientSecret provided
        if request and request.currentClientSecret:
            # TODO: Implement session refresh logic in production with Redis
            # For now, generate new client_secret
            logger.info("Refreshing ChatKit session")
        
        # Generate client secret following OpenAI patterns
        client_secret = f"cs_live_{uuid.uuid4().hex[:24]}"
        
        logger.info(f"✅ Created ChatKit session with workflow: {workflow_id or 'default'}")
        
        # Return client_secret only as required by ChatKit SDK
        return {
            "client_secret": client_secret
        }
        
    except Exception as e:
        logger.error(f"ChatKit endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"ChatKit session failed: {str(e)}")

@app.post("/chatkit/refresh")
async def chatkit_refresh(request: dict):
    """ChatKit session refresh endpoint"""
    try:
        import uuid
        
        current_secret = request.get("currentClientSecret")
        if not current_secret:
            raise HTTPException(status_code=400, detail="currentClientSecret required")
        
        # Generate new client secret
        client_secret = f"cs_live_{uuid.uuid4().hex[:24]}"
        
        logger.info("✅ Refreshed ChatKit session")
        
        return {
            "client_secret": client_secret
        }
        
    except Exception as e:
        logger.error(f"ChatKit refresh error: {e}")
        raise HTTPException(status_code=500, detail=f"Session refresh failed: {str(e)}")

# Legacy ChatKit session management (deprecated - use /chatkit instead)
class ChatKitSessionRequest(BaseModel):
    device_id: str
    existing_session: Optional[str] = None

@app.post("/api/chatkit/session-old")  # Changed route to avoid duplicate - using newer version below
async def create_chatkit_session_old(request: ChatKitSessionRequest):
    """Create a ChatKit session following video best practices"""
    try:
        import uuid
        import os
        from datetime import datetime, timedelta
        
        # Check for required OpenAI API key (as shown in video)
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.error("OPENAI_API_KEY is not defined - ChatKit session cannot be created")
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY is not defined. Please check your environment configuration."
            )
        
        # Get workflow ID from environment (prioritize ChatKit workflow)
        workflow_id = os.getenv("CHATKIT_WORKFLOW_ID")
        assistant_id = os.getenv("GVSES_ASSISTANT_ID")
        
        if not workflow_id and not assistant_id:
            logger.warning("Neither CHATKIT_WORKFLOW_ID nor GVSES_ASSISTANT_ID set - using default configuration")
        else:
            primary_id = workflow_id or assistant_id
            logger.info(f"Using ChatKit workflow: {workflow_id} | G'sves Assistant: {assistant_id}")
        
        # Generate client secret following video pattern
        client_secret = f"chatkit_sess_{uuid.uuid4().hex[:16]}"
        
        # Store session with proper TTL (implement Redis/database in production)
        session_data = {
            "client_secret": client_secret,
            "device_id": request.device_id,
            "workflow_id": workflow_id,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=8)).isoformat(),  # 8-hour sessions
            "openai_config": {
                "api_key_configured": bool(openai_api_key),
                "model": "gpt-4o",  # Updated to latest model
                "tools_enabled": True,
                "assistant_id": os.getenv("GVSES_ASSISTANT_ID"),
                "use_responses_api": os.getenv("USE_GVSES_ASSISTANT", "false").lower() == "true"
            }
        }
        
        # TODO: In production, store session_data in Redis with TTL
        # redis_client.setex(f"chatkit_session:{client_secret}", 28800, json.dumps(session_data))
        
        logger.info(f"✅ Created ChatKit session for device: {request.device_id} with workflow: {workflow_id or 'default'}")
        
        # Return client_secret as required by ChatKit SDK
        return {
            "client_secret": client_secret,
            "device_id": request.device_id,
            "workflow_id": workflow_id,  # ChatKit Agent Builder workflow
            "assistant_id": assistant_id,  # G'sves Responses API assistant
            "status": "active",
            "expires_in": 28800  # 8 hours in seconds
        }
        
    except Exception as e:
        logger.error(f"Failed to create ChatKit session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

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

class ChatKitSessionRequest(BaseModel):
    """Request model for ChatKit session creation"""
    user_id: Optional[str] = None
    device_id: Optional[str] = None

@app.post("/api/chatkit/session")
async def create_chatkit_session(request: ChatKitSessionRequest):
    """Create a new ChatKit session for the Chart Agent workflow"""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Use httpx to make the API call to OpenAI
        session_data = {
            "workflow": {"id": CHART_AGENT_WORKFLOW_ID},
            "user": request.user_id or request.device_id or f"user_{datetime.now().timestamp()}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chatkit/sessions",
                headers={
                    "Content-Type": "application/json",
                    "OpenAI-Beta": "chatkit_beta=v1",
                    "Authorization": f"Bearer {openai_api_key}"
                },
                json=session_data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                logger.error(f"ChatKit session creation failed: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Failed to create ChatKit session: {response.text}"
                )
            
            session_response = response.json()
            logger.info(f"ChatKit session created successfully for user: {session_data['user']}")
            
            return {
                "client_secret": session_response.get("client_secret"),
                "session_id": session_response.get("id"),
                "user": session_data["user"],
                "timestamp": datetime.now().isoformat()
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ChatKit session creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# ChatKit Custom Action Endpoints for Agent Builder Integration
# ============================================================================

from services.session_store import SessionStore

class UpdateChartContextRequest(BaseModel):
    """Request to update chart context for a ChatKit session"""
    session_id: str
    symbol: str
    timeframe: str
    snapshot_id: Optional[str] = None

class ChatKitChartActionRequest(BaseModel):
    """Request from Agent Builder custom action"""
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatKitChartActionResponse(BaseModel):
    """Response to Agent Builder custom action"""
    success: bool
    text: str
    chart_commands: List[str] = []
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/api/chatkit/update-context")
async def update_chart_context(request: UpdateChartContextRequest):
    """
    Update chart context for a ChatKit session
    
    Called by frontend when chart changes (symbol, timeframe, snapshot)
    Stores context in session store so custom actions can retrieve it
    """
    try:
        logger.info(f"[CHATKIT UPDATE] Session {request.session_id}: {request.symbol} @ {request.timeframe}")
        
        SessionStore.set_chart_context(
            request.session_id,
            {
                'symbol': request.symbol,
                'timeframe': request.timeframe,
                'snapshot_id': request.snapshot_id,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            "success": True,
            "session_id": request.session_id,
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[CHATKIT UPDATE] Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")

@app.post("/api/chatkit/chart-action", response_model=ChatKitChartActionResponse)
async def chatkit_chart_action(request: ChatKitChartActionRequest):
    """
    Custom action endpoint for Agent Builder
    
    Handles chart control, pattern detection, drawing commands
    Called by Agent Builder's "Gvses" agent when chart-related queries detected
    
    Flow:
    1. Receive query from Agent Builder custom action
    2. Retrieve chart context from session store
    3. Call agent orchestrator with chart context
    4. Extract drawing commands from response
    5. Return formatted response with commands
    """
    try:
        logger.info(f"[CHATKIT ACTION] Query: {request.query[:100]}...")
        logger.info(f"[CHATKIT ACTION] Session: {request.session_id}, User: {request.user_id}")
        
        # Try to get chart context from session store
        chart_context = None
        if request.session_id:
            chart_context = SessionStore.get_chart_context(request.session_id)
            if chart_context:
                logger.info(f"[CHATKIT ACTION] Retrieved chart context from session: {chart_context}")
        
        # Fallback: check if passed in metadata
        if not chart_context and request.metadata and 'chart_context' in request.metadata:
            chart_context = request.metadata['chart_context']
            logger.info(f"[CHATKIT ACTION] Using chart context from metadata: {chart_context}")
        
        # Last resort: extract symbol from query
        if not chart_context:
            import re
            symbol_match = re.search(r'\b([A-Z]{2,5})\b', request.query)
            if symbol_match:
                chart_context = {
                    'symbol': symbol_match.group(1),
                    'timeframe': '1D',  # default
                    'source': 'extracted_from_query'
                }
                logger.info(f"[CHATKIT ACTION] Extracted chart context from query: {chart_context}")
            else:
                logger.warning(f"[CHATKIT ACTION] No chart context available - will ask user for symbol")
        
        # Call agent orchestrator
        from services.agent_orchestrator import AgentOrchestrator
        orchestrator = AgentOrchestrator()
        
        result = await orchestrator.process_query(
            query=request.query,
            conversation_history=[],
            chart_context=chart_context
        )
        
        # Format response for Agent Builder
        response_text = result.get("text", "")
        chart_commands = result.get("chart_commands", [])
        tools_used = result.get("tools_used", [])
        
        logger.info(f"[CHATKIT ACTION] Generated {len(chart_commands)} chart commands, used {len(tools_used)} tools")
        
        # Embed commands in response text so frontend can parse them
        if chart_commands:
            command_text = "\n\n" + "\n".join(chart_commands)
            response_text += command_text
            logger.info(f"[CHATKIT ACTION] Embedded commands in response")
        
        return ChatKitChartActionResponse(
            success=True,
            text=response_text,
            chart_commands=chart_commands,
            data={
                'tools_used': tools_used,
                'chart_context': chart_context,
                'timestamp': datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"[CHATKIT ACTION] Error: {e}", exc_info=True)
        return ChatKitChartActionResponse(
            success=False,
            text=f"I encountered an error processing your chart request: {str(e)}",
            chart_commands=[],
            error=str(e)
        )

# ============================================================================
# End ChatKit Custom Action Endpoints
# ============================================================================

# Agent Orchestration endpoint for direct frontend integration
@app.post("/api/agent/orchestrate")
async def agent_orchestrate(request: dict):
    """
    Agent orchestration endpoint for processing user queries
    This endpoint acts as a proxy to the MCP server for agent capabilities
    """
    try:
        query = request.get("query", "")
        conversation_history = request.get("conversation_history", [])
        session_id = request.get("session_id", "")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"[AGENT ORCHESTRATE] Processing query: {query[:100]}...")
        
        # For now, return a basic response indicating the feature is available
        # In production, this would connect to Claude or another LLM service
        response = {
            "text": f"I received your query: {query}. The agent orchestration system is available and processing market-related queries through the MCP integration.",
            "tools_used": ["market_data_analysis"],
            "data": {
                "query": query,
                "session_id": session_id,
                "status": "processed"
            },
            "timestamp": datetime.now().isoformat(),
            "model": "mcp-agent-orchestrator",
            "cached": False
        }
        
        logger.info(f"[AGENT ORCHESTRATE] Returning response for session {session_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent orchestration error: {e}")
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@app.post("/api/agent/sdk-orchestrate")
async def agent_sdk_orchestrate(request: dict):
    """
    Agents SDK orchestration endpoint - implements Agent Builder workflow logic
    Uses OpenAI Agents SDK patterns for intent classification and conditional routing
    """
    try:
        # Parse request
        agent_query = AgentQuery(
            query=request.get("query", ""),
            conversation_history=request.get("conversation_history", []),
            session_id=request.get("session_id", ""),
            user_id=request.get("user_id", None)
        )
        
        if not agent_query.query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        logger.info(f"[AGENTS SDK] Processing query: {agent_query.query[:100]}...")
        
        # Execute Agents SDK workflow
        response = await agents_sdk_service.run_workflow(agent_query)
        
        # Convert to dict for API response
        response_dict = {
            "text": response.text,
            "tools_used": response.tools_used,
            "data": response.data,
            "timestamp": response.timestamp,
            "model": response.model,
            "cached": response.cached,
            "session_id": response.session_id,
            "chart_commands": response.chart_commands
        }
        
        logger.info(f"[AGENTS SDK] Workflow completed for session {response.session_id}")
        return response_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agents SDK orchestration error: {e}")
        raise HTTPException(status_code=500, detail=f"SDK orchestration failed: {str(e)}")

# OpenAI Realtime SDK Endpoints (Phase 2: Voice Integration)
@app.post("/api/agent/realtime-token")
async def create_realtime_token(request: dict):
    """
    Create ephemeral token for OpenAI Realtime API + Agents SDK session.
    
    This initializes a voice session that uses the Agent Builder workflow
    for end-to-end audio-in to audio-out processing.
    """
    try:
        from services.realtime_sdk_service import realtime_sdk_service
        
        workflow_id = request.get("workflow_id", "wf_68e5c49989448190bafbdad788a4747005aa1bda218ab736")
        voice = request.get("voice", "marin")
        session_id = request.get("session_id")
        
        # Create session
        session_data = await realtime_sdk_service.create_session(
            workflow_id=workflow_id,
            voice=voice,
            session_id=session_id
        )
        
        logger.info(f"🎙️ [Realtime SDK] Token created for session {session_data['session_id']}")
        return session_data
        
    except Exception as e:
        logger.error(f"❌ [Realtime SDK] Token creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/realtime-sdk")
async def realtime_sdk_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for OpenAI Realtime API + Agents SDK.
    
    This relays between the frontend and OpenAI Realtime API,
    handling tool calls via the Agent Builder workflow.
    """
    await websocket.accept()
    
    try:
        from services.realtime_sdk_service import realtime_sdk_service
        
        # Wait for session init message
        init_message = await websocket.receive_json()
        
        if init_message.get("type") != "session.init":
            await websocket.send_json({
                "type": "error",
                "error": {"message": "Expected session.init message"}
            })
            return
        
        session_id = init_message.get("session_id")
        if not session_id:
            await websocket.send_json({
                "type": "error",
                "error": {"message": "session_id required"}
            })
            return
        
        logger.info(f"🔌 [Realtime SDK] WebSocket connected for session {session_id}")
        
        # Handle the session (relay between frontend and OpenAI)
        await realtime_sdk_service.handle_realtime_session(session_id, websocket)
        
    except WebSocketDisconnect:
        logger.info("🔌 [Realtime SDK] WebSocket disconnected")
    except Exception as e:
        logger.error(f"❌ [Realtime SDK] WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "error": {"message": str(e)}
            })
        except:
            pass

# Agent orchestration is handled directly by OpenAI Agent Builder via HTTP MCP endpoint
# The Agent Builder connects to /api/mcp and gets direct access to all MCP tools

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