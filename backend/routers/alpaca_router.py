"""
Alpaca Markets API Router
Provides endpoints for real-time market data from Alpaca
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import logging
from alpaca_service import get_alpaca_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/alpaca", tags=["alpaca"])


@router.get("/account")
async def get_account():
    """Get Alpaca account information."""
    try:
        service = get_alpaca_service()
        return await service.get_account_info()
    except Exception as e:
        logger.error(f"Account endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quote/{symbol}")
async def get_quote(symbol: str):
    """Get latest quote for a symbol."""
    try:
        service = get_alpaca_service()
        return await service.get_stock_quote(symbol.upper())
    except Exception as e:
        logger.error(f"Quote endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshot/{symbol}")
async def get_snapshot(symbol: str):
    """Get comprehensive snapshot data for a symbol."""
    try:
        service = get_alpaca_service()
        return await service.get_snapshot(symbol.upper())
    except Exception as e:
        logger.error(f"Snapshot endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bars/{symbol}")
async def get_bars(
    symbol: str,
    timeframe: str = Query("1Day", description="Timeframe: 1Min, 5Min, 15Min, 1Hour, 1Day, etc"),
    days: int = Query(30, description="Number of days back"),
    limit: Optional[int] = Query(None, description="Limit number of bars")
):
    """Get historical bars for a symbol."""
    try:
        service = get_alpaca_service()
        return await service.get_stock_bars(
            symbol.upper(), 
            timeframe=timeframe,
            days_back=days,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Bars endpoint error for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions():
    """Get all open positions."""
    try:
        service = get_alpaca_service()
        return await service.get_positions()
    except Exception as e:
        logger.error(f"Positions endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(
    status: str = Query("all", description="Order status: all, open, closed"),
    limit: int = Query(50, description="Maximum number of orders")
):
    """Get orders with specified status."""
    try:
        service = get_alpaca_service()
        return await service.get_orders(status=status, limit=limit)
    except Exception as e:
        logger.error(f"Orders endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-status")
async def get_market_status():
    """Check if market is open."""
    try:
        service = get_alpaca_service()
        return await service.get_market_status()
    except Exception as e:
        logger.error(f"Market status endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stock-price")
async def get_stock_price(symbol: str):
    """Get current stock price (compatible with existing frontend)."""
    try:
        service = get_alpaca_service()
        snapshot = await service.get_snapshot(symbol.upper())
        
        if "error" in snapshot:
            raise HTTPException(status_code=404, detail=snapshot["error"])
        
        # Extract price from snapshot
        price = None
        change = None
        change_percent = None
        
        if "latest_trade" in snapshot:
            price = snapshot["latest_trade"]["price"]
        
        if "daily_bar" in snapshot and "previous_daily_bar" in snapshot:
            current_close = snapshot["daily_bar"]["close"]
            prev_close = snapshot["previous_daily_bar"]["close"]
            change = current_close - prev_close
            change_percent = (change / prev_close) * 100 if prev_close else 0
        
        return {
            "symbol": symbol.upper(),
            "price": price,
            "change": change,
            "changePercent": change_percent,
            "source": "alpaca"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock price endpoint error for {symbol}: {e}")
        # Fallback to quote if snapshot fails
        try:
            service = get_alpaca_service()
            quote = await service.get_stock_quote(symbol.upper())
            if "error" not in quote:
                return {
                    "symbol": symbol.upper(),
                    "price": quote.get("ask_price") or quote.get("bid_price"),
                    "source": "alpaca"
                }
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))