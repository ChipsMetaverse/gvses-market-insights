"""
Enhanced Market Data Router
============================
Provides market data from both Yahoo Finance (via market-mcp-server) 
and Alpaca Markets (via alpaca-mcp-server) for professional-grade data.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
import logging
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.direct_mcp_client import get_direct_mcp_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enhanced", tags=["enhanced"])


@router.get("/market-data")
async def get_enhanced_market_data(
    symbol: str = Query(..., description="Stock ticker symbol"),
    source: str = Query("auto", description="Data source: 'yahoo', 'alpaca', or 'auto'")
) -> Dict[str, Any]:
    """
    Get enhanced market data from available sources.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, TSLA)
        source: Preferred data source ('yahoo', 'alpaca', or 'auto')
        
    Returns:
        Market data with source attribution
    """
    try:
        client = get_direct_mcp_client()
        
        # Direct client approach - call specific tool directly
        result = await client.call_tool("get_stock_quote", {"symbol": symbol})
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        return {"data": result, "source": "yahoo_mcp", "symbol": symbol}
        
    except Exception as e:
        logger.error(f"Error fetching enhanced market data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-data")
async def get_enhanced_historical_data(
    symbol: str = Query(..., description="Stock ticker symbol"),
    days: int = Query(30, description="Number of days of history"),
    source: str = Query("auto", description="Data source: 'yahoo', 'alpaca', or 'auto'")
) -> Dict[str, Any]:
    """
    Get historical data from available sources.
    
    Args:
        symbol: Stock ticker symbol
        days: Number of days of historical data
        source: Preferred data source
        
    Returns:
        Historical data with source attribution
    """
    try:
        client = get_direct_mcp_client()
        
        # Convert days to period 
        period = "1mo" if days <= 30 else "3mo" if days <= 90 else "1y"
        result = await client.call_tool("get_stock_history", {"symbol": symbol, "period": period})
        
        if not result:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")
        
        return {"data": result, "source": "yahoo_mcp", "symbol": symbol, "days": days}
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpaca-account")
async def get_alpaca_account():
    """Get Alpaca account information - not available in current MCP server."""
    raise HTTPException(
        status_code=503,
        detail="Alpaca MCP server not available - using Yahoo Finance MCP only"
    )


@router.get("/alpaca-positions")
async def get_alpaca_positions():
    """Get all open positions from Alpaca - not available in current MCP server."""
    raise HTTPException(
        status_code=503,
        detail="Alpaca MCP server not available - using Yahoo Finance MCP only"
    )


@router.get("/alpaca-orders")
async def get_alpaca_orders(
    status: str = Query("open", description="Order status: 'open', 'closed', or 'all'")
):
    """Get orders from Alpaca - not available in current MCP server."""
    raise HTTPException(
        status_code=503,
        detail="Alpaca MCP server not available - using Yahoo Finance MCP only"
    )


@router.get("/market-status")
async def get_market_status():
    """Get current market status - simplified version."""
    try:
        # Simple fallback since we don't have Alpaca MCP server
        from datetime import datetime, timezone
        import pytz
        
        # Check if markets are typically open (9:30 AM - 4:00 PM ET, Monday-Friday)
        et_tz = pytz.timezone('America/New_York')
        now_et = datetime.now(et_tz)
        
        is_weekend = now_et.weekday() >= 5  # Saturday = 5, Sunday = 6
        hour = now_et.hour
        minute = now_et.minute
        time_decimal = hour + minute / 60.0
        
        # Market hours: 9:30 AM (9.5) to 4:00 PM (16.0) ET
        is_market_hours = 9.5 <= time_decimal <= 16.0
        
        is_open = not is_weekend and is_market_hours
        
        return {
            "is_open": is_open,
            "message": f"Market {'open' if is_open else 'closed'} - estimated based on time",
            "source": "time_estimation",
            "current_time_et": now_et.strftime("%Y-%m-%d %H:%M:%S ET")
        }
        
    except Exception as e:
        logger.error(f"Error determining market status: {e}")
        return {
            "is_open": False,
            "message": str(e),
            "source": "error"
        }


@router.get("/compare-sources")
async def compare_data_sources(
    symbol: str = Query(..., description="Stock ticker symbol")
) -> Dict[str, Any]:
    """
    Get data from Yahoo Finance MCP server for comparison.
    """
    try:
        client = get_direct_mcp_client()
        
        comparison = {
            "symbol": symbol.upper(),
            "sources": {}
        }
        
        # Get data from Yahoo Finance
        yahoo_result = await client.call_tool("get_stock_quote", {"symbol": symbol})
        if yahoo_result:
            comparison['sources']['yahoo_mcp'] = yahoo_result
        
        if not comparison['sources']:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol {symbol}"
            )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))