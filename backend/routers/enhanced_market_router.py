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
from mcp_client import get_mcp_manager

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
        manager = get_mcp_manager()
        await manager.initialize()
        
        result = await manager.get_stock_data(symbol, source)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
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
        manager = get_mcp_manager()
        await manager.initialize()
        
        result = await manager.get_historical_data(symbol, days, source)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpaca-account")
async def get_alpaca_account():
    """Get Alpaca account information."""
    try:
        manager = get_mcp_manager()
        await manager.initialize()
        
        if 'alpaca' not in manager.servers:
            raise HTTPException(
                status_code=503,
                detail="Alpaca MCP server not available"
            )
        
        result = await manager.call_tool('alpaca', 'get_account', {})
        
        if result:
            return json.loads(result) if isinstance(result, str) else result
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch account information"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Alpaca account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpaca-positions")
async def get_alpaca_positions():
    """Get all open positions from Alpaca."""
    try:
        manager = get_mcp_manager()
        await manager.initialize()
        
        if 'alpaca' not in manager.servers:
            raise HTTPException(
                status_code=503,
                detail="Alpaca MCP server not available"
            )
        
        result = await manager.call_tool('alpaca', 'get_positions', {})
        
        if result:
            return json.loads(result) if isinstance(result, str) else result
        else:
            return []
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alpaca-orders")
async def get_alpaca_orders(
    status: str = Query("open", description="Order status: 'open', 'closed', or 'all'")
):
    """Get orders from Alpaca."""
    try:
        manager = get_mcp_manager()
        await manager.initialize()
        
        if 'alpaca' not in manager.servers:
            raise HTTPException(
                status_code=503,
                detail="Alpaca MCP server not available"
            )
        
        result = await manager.call_tool('alpaca', 'get_orders', {"status": status})
        
        if result:
            return json.loads(result) if isinstance(result, str) else result
        else:
            return []
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-status")
async def get_market_status():
    """Get current market status from Alpaca."""
    try:
        manager = get_mcp_manager()
        await manager.initialize()
        
        if 'alpaca' not in manager.servers:
            # Fallback to a simple status
            return {
                "is_open": False,
                "message": "Market status unavailable",
                "source": "fallback"
            }
        
        result = await manager.call_tool('alpaca', 'get_market_status', {})
        
        if result:
            status = json.loads(result) if isinstance(result, str) else result
            status['source'] = 'alpaca'
            return status
        else:
            return {
                "is_open": False,
                "message": "Unable to determine market status",
                "source": "error"
            }
            
    except Exception as e:
        logger.error(f"Error fetching market status: {e}")
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
    Compare data from both Yahoo Finance and Alpaca for a symbol.
    Useful for debugging and data quality assessment.
    """
    try:
        manager = get_mcp_manager()
        await manager.initialize()
        
        comparison = {
            "symbol": symbol.upper(),
            "sources": {}
        }
        
        # Get data from Yahoo Finance
        if 'market' in manager.servers:
            yahoo_result = await manager.call_tool('market', 'get_stock_quote', {'symbol': symbol})
            if yahoo_result:
                comparison['sources']['yahoo'] = yahoo_result
        
        # Get data from Alpaca
        if 'alpaca' in manager.servers:
            alpaca_result = await manager.call_tool('alpaca', 'get_stock_snapshot', {'symbol': symbol})
            if alpaca_result:
                comparison['sources']['alpaca'] = json.loads(alpaca_result) if isinstance(alpaca_result, str) else alpaca_result
        
        if not comparison['sources']:
            raise HTTPException(
                status_code=503,
                detail="No data sources available"
            )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))