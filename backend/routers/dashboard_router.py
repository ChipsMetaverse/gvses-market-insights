from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
from typing import Optional
import json
import asyncio

from models.schemas import (
    TimeRange, ResponseMeta, DashboardData, ChartData, TechnicalOverview,
    RelatedNews, StrategicInsights
)
from services.market_service import get_quote, get_ohlcv, humanize_market_cap, build_summary_table
from services.technical_service import build_technical_overview
from services.chart_service import build_chart_data
from services.options_insights_service import get_insights
from services.news_service import get_related_news
from response_formatter import format_response


router = APIRouter(prefix="/api/v1")


@router.get("/dashboard")
async def get_dashboard(
    symbol: str = Query(..., description="Stock symbol"),
    range: TimeRange = Query(TimeRange.D1, description="Time range")
):
    """Get complete dashboard data - REAL DATA ONLY"""
    
    try:
        # Fetch quote/snapshot
        quote = await get_quote(symbol)
        candles = await get_ohlcv(symbol, range.value)
    except ValueError as e:
        # Return error response if real data not available
        return format_response(
            data=None,
            error=str(e),
            meta={
                "symbol": symbol.upper(),
                "requested_range": range.value,
                "server_time": datetime.now(timezone.utc).isoformat(),
                "timezone": "UTC",
                "version": "1.0.0"
            }
        )
    
    # Build price header
    price_header = {
        "symbol": symbol.upper(),
        "company_name": quote["company_name"],
        "exchange": quote["exchange"],
        "currency": quote.get("currency", "USD"),
        "last_price": quote["last"],
        "change_abs": quote["change_abs"],
        "change_pct": quote["change_pct"],
        "is_market_open": quote["is_open"],
        "as_of": datetime.now(timezone.utc).isoformat(),
        "last_price_formatted": f"${quote['last']:,.2f}",
        "change_abs_formatted": f"{quote['change_abs']:+,.2f}",
        "change_pct_formatted": f"{quote['change_pct']:+.2f}%"
    }
    
    # Build market snapshot
    market_snapshot = {
        "open_price": quote["open"],
        "day_high": quote["high"],
        "day_low": quote["low"],
        "prev_close": quote["prev_close"],
        "volume": quote["volume"],
        "avg_volume_3m": quote.get("avg_volume_3m"),
        "market_cap": quote.get("market_cap"),
        "pe_ttm": quote.get("pe_ttm"),
        "dividend_yield_pct": quote.get("dividend_yield_pct"),
        "beta": quote.get("beta"),
        "week52_high": quote.get("week52_high"),
        "week52_low": quote.get("week52_low"),
        "volume_formatted": f"{quote['volume']:,}",
        "avg_volume_3m_formatted": f"{quote.get('avg_volume_3m', 0):,}" if quote.get("avg_volume_3m") else "—",
        "market_cap_formatted": humanize_market_cap(quote.get("market_cap")),
        "pe_ttm_formatted": f"{quote['pe_ttm']:.2f}" if quote.get("pe_ttm") is not None else "—",
        "dividend_yield_pct_formatted": f"{quote['dividend_yield_pct']:.2f}%" if quote.get("dividend_yield_pct") else "—",
        "week52_range_formatted": f"${quote['week52_low']:.2f} - ${quote['week52_high']:.2f}" if quote.get("week52_low") and quote.get("week52_high") else "—"
    }
    
    # Build chart data
    chart = build_chart_data(symbol, range.value, candles)
    
    # Build technical overview
    technical = build_technical_overview(symbol, candles)
    
    # Build summary table
    summary = build_summary_table(quote)
    
    # Get strategic insights
    insights = get_insights(symbol=symbol, spot=quote["last"], horizon_days=30)
    
    # Get related news
    news = await get_related_news(symbol=symbol, limit=6)
    
    # Combine all data
    data = {
        "price_header": price_header,
        "market_snapshot": market_snapshot,
        "chart": chart,
        "technical_overview": technical,
        "summary_table": summary,
        "strategic_insights": insights,
        "related_news": news
    }
    
    # Build metadata
    meta = {
        "symbol": symbol.upper(),
        "requested_range": range.value,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "version": "1.0.0"
    }
    
    return format_response(data=data, meta=meta)


@router.get("/chart")
async def get_chart(
    symbol: str = Query(..., description="Stock symbol"),
    range: TimeRange = Query(..., description="Time range")
):
    """Get chart data only"""
    
    candles = await get_ohlcv(symbol, range.value)
    chart = build_chart_data(symbol, range.value, candles)
    
    meta = {
        "symbol": symbol.upper(),
        "requested_range": range.value,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "version": "1.0.0"
    }
    
    return format_response(data=chart, meta=meta)


@router.get("/technical")
async def get_technical(
    symbol: str = Query(..., description="Stock symbol"),
    range: TimeRange = Query(..., description="Time range")
):
    """Get technical analysis overview"""
    
    candles = await get_ohlcv(symbol, range.value)
    technical = build_technical_overview(symbol, candles)
    
    meta = {
        "symbol": symbol.upper(),
        "requested_range": range.value,
        "server_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "version": "1.0.0"
    }
    
    return format_response(data=technical, meta=meta)


@router.get("/news")
async def get_news(
    symbol: str = Query(..., description="Stock symbol"),
    limit: int = Query(6, description="Number of news items", ge=1, le=20)
):
    """Get related news"""
    
    news = await get_related_news(symbol=symbol, limit=limit)
    
    meta = {
        "symbol": symbol.upper(),
        "requested_range": "1D",  # News doesn't have range
        "server_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "version": "1.0.0"
    }
    
    return format_response(data=news, meta=meta)


@router.get("/options/strategic-insights")
async def get_strategic_insights(
    symbol: str = Query(..., description="Stock symbol"),
    horizon_days: int = Query(30, description="Time horizon in days", ge=1, le=365)
):
    """Get options strategy recommendations"""
    
    quote = await get_quote(symbol)
    insights = get_insights(symbol=symbol, spot=quote["last"], horizon_days=horizon_days)
    
    meta = {
        "symbol": symbol.upper(),
        "requested_range": "1D",
        "server_time": datetime.now(timezone.utc).isoformat(),
        "timezone": "UTC",
        "version": "1.0.0"
    }
    
    return format_response(data=insights, meta=meta)


# WebSocket for live quotes
@router.websocket("/ws/quotes")
async def websocket_quotes(websocket: WebSocket, symbol: Optional[str] = None):
    """WebSocket endpoint for live price updates"""
    await websocket.accept()
    
    # Get symbol from query or first message
    if not symbol:
        try:
            data = await websocket.receive_json()
            if data.get("type") == "subscribe":
                symbol = data.get("symbol")
        except:
            await websocket.close(code=1003, reason="Invalid message")
            return
    
    if not symbol:
        await websocket.close(code=1003, reason="No symbol provided")
        return
    
    try:
        while True:
            # Get current quote
            quote = await get_quote(symbol)
            
            # Send quote update
            message = {
                "type": "quote",
                "symbol": symbol.upper(),
                "last_price": quote["last"],
                "change_abs": quote["change_abs"],
                "change_pct": quote["change_pct"],
                "as_of": int(datetime.now().timestamp())
            }
            
            await websocket.send_json(message)
            
            # Wait before next update (simulate real-time)
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason="Internal error")