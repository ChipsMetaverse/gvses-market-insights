#!/usr/bin/env python3
"""
Alpaca MCP Server
Provides market data and trading tools via Alpaca Markets API
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from alpaca.trading.client import TradingClient
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import (
    StockBarsRequest,
    StockQuotesRequest,
    StockTradesRequest,
    StockSnapshotRequest,
    StockLatestBarRequest
)
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.requests import (
    GetOrdersRequest,
    GetPositionsRequest,
    MarketOrderRequest,
    LimitOrderRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.common.exceptions import APIError

# Configure logging to stderr to avoid stdout pollution
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


class AlpacaMCPServer:
    """MCP Server for Alpaca Markets integration."""
    
    def __init__(self):
        """Initialize the MCP server and Alpaca clients."""
        self.server = Server("alpaca-mcp-server")
        
        # Load API credentials from environment
        self.api_key = os.getenv('ALPACA_API_KEY')
        self.secret_key = os.getenv('ALPACA_SECRET_KEY')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found in environment")
        
        # Determine if we're in paper mode
        self.paper_trading = 'paper' in self.base_url.lower()
        
        # Initialize Alpaca clients
        self.trading_client = TradingClient(
            api_key=self.api_key,
            secret_key=self.secret_key,
            paper=self.paper_trading
        )
        
        self.data_client = StockHistoricalDataClient(
            api_key=self.api_key,
            secret_key=self.secret_key
        )
        
        logger.info(f"Alpaca MCP Server initialized ({'Paper' if self.paper_trading else 'Live'} mode)")
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools with the MCP server."""
        
        # Account & Trading Tools
        @self.server.tool()
        async def get_account() -> str:
            """Get Alpaca account information including buying power and portfolio value."""
            try:
                account = self.trading_client.get_account()
                return json.dumps({
                    "status": account.status,
                    "buying_power": float(account.buying_power),
                    "cash": float(account.cash),
                    "portfolio_value": float(account.portfolio_value),
                    "equity": float(account.equity),
                    "pattern_day_trader": account.pattern_day_trader,
                    "trading_blocked": account.trading_blocked,
                    "account_blocked": account.account_blocked,
                    "currency": account.currency
                }, indent=2)
            except Exception as e:
                logger.error(f"Error fetching account: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_positions() -> str:
            """Get all open positions in the account."""
            try:
                positions = self.trading_client.get_all_positions()
                result = []
                for pos in positions:
                    result.append({
                        "symbol": pos.symbol,
                        "qty": float(pos.qty),
                        "side": pos.side,
                        "market_value": float(pos.market_value),
                        "cost_basis": float(pos.cost_basis),
                        "unrealized_pl": float(pos.unrealized_pl),
                        "unrealized_plpc": float(pos.unrealized_plpc),
                        "current_price": float(pos.current_price) if pos.current_price else None,
                        "avg_entry_price": float(pos.avg_entry_price)
                    })
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Error fetching positions: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_orders(status: str = "open") -> str:
            """Get orders with specified status (open, closed, all)."""
            try:
                if status == "open":
                    order_status = QueryOrderStatus.OPEN
                elif status == "closed":
                    order_status = QueryOrderStatus.CLOSED
                else:
                    order_status = QueryOrderStatus.ALL
                
                request = GetOrdersRequest(status=order_status, limit=100)
                orders = self.trading_client.get_orders(request)
                
                result = []
                for order in orders:
                    result.append({
                        "id": order.id,
                        "symbol": order.symbol,
                        "qty": float(order.qty) if order.qty else None,
                        "filled_qty": float(order.filled_qty) if order.filled_qty else None,
                        "side": order.side,
                        "type": order.order_type,
                        "time_in_force": order.time_in_force,
                        "limit_price": float(order.limit_price) if order.limit_price else None,
                        "stop_price": float(order.stop_price) if order.stop_price else None,
                        "status": order.status,
                        "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None,
                        "filled_at": order.filled_at.isoformat() if order.filled_at else None
                    })
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Error fetching orders: {e}")
                return json.dumps({"error": str(e)})
        
        # Market Data Tools
        @self.server.tool()
        async def get_stock_quote(symbol: str) -> str:
            """Get the latest quote for a stock symbol."""
            try:
                request = StockQuotesRequest(symbol_or_symbols=symbol.upper())
                quotes = self.data_client.get_stock_latest_quote(request)
                
                if symbol.upper() in quotes:
                    quote = quotes[symbol.upper()]
                    return json.dumps({
                        "symbol": symbol.upper(),
                        "ask_price": float(quote.ask_price) if quote.ask_price else None,
                        "bid_price": float(quote.bid_price) if quote.bid_price else None,
                        "ask_size": quote.ask_size,
                        "bid_size": quote.bid_size,
                        "timestamp": quote.timestamp.isoformat() if quote.timestamp else None
                    }, indent=2)
                return json.dumps({"error": f"No quote data for {symbol}"})
            except Exception as e:
                logger.error(f"Error fetching quote for {symbol}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_stock_bars(
            symbol: str,
            timeframe: str = "1Day",
            days_back: int = 30
        ) -> str:
            """
            Get historical bar data for a stock.
            
            Args:
                symbol: Stock ticker symbol
                timeframe: Bar timeframe (1Min, 5Min, 15Min, 30Min, 1Hour, 1Day)
                days_back: Number of days of history to fetch
            """
            try:
                # Map timeframe string to TimeFrame enum
                timeframe_map = {
                    "1Min": TimeFrame.Minute,
                    "5Min": TimeFrame(5, "Min"),
                    "15Min": TimeFrame(15, "Min"),
                    "30Min": TimeFrame(30, "Min"),
                    "1Hour": TimeFrame.Hour,
                    "1Day": TimeFrame.Day,
                    "1Week": TimeFrame.Week,
                    "1Month": TimeFrame.Month
                }
                
                tf = timeframe_map.get(timeframe, TimeFrame.Day)
                
                # Calculate date range
                end_time = datetime.now()
                start_time = end_time - timedelta(days=days_back)
                
                request = StockBarsRequest(
                    symbol_or_symbols=symbol.upper(),
                    timeframe=tf,
                    start=start_time,
                    end=end_time
                )
                
                bars = self.data_client.get_stock_bars(request)
                
                result = []
                if symbol.upper() in bars.data:
                    for bar in bars.data[symbol.upper()]:
                        result.append({
                            "timestamp": bar.timestamp.isoformat(),
                            "open": float(bar.open),
                            "high": float(bar.high),
                            "low": float(bar.low),
                            "close": float(bar.close),
                            "volume": bar.volume,
                            "vwap": float(bar.vwap) if bar.vwap else None,
                            "trade_count": bar.trade_count
                        })
                
                return json.dumps({
                    "symbol": symbol.upper(),
                    "timeframe": timeframe,
                    "bars": result
                }, indent=2)
            except Exception as e:
                logger.error(f"Error fetching bars for {symbol}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_stock_snapshot(symbol: str) -> str:
            """Get a comprehensive snapshot of a stock including quote, bar, and trades."""
            try:
                request = StockSnapshotRequest(symbol_or_symbols=symbol.upper())
                snapshots = self.data_client.get_stock_snapshot(request)
                
                if symbol.upper() in snapshots:
                    snapshot = snapshots[symbol.upper()]
                    result = {
                        "symbol": symbol.upper()
                    }
                    
                    # Add latest trade
                    if snapshot.latest_trade:
                        result["latest_trade"] = {
                            "price": float(snapshot.latest_trade.price),
                            "size": snapshot.latest_trade.size,
                            "timestamp": snapshot.latest_trade.timestamp.isoformat()
                        }
                    
                    # Add latest quote
                    if snapshot.latest_quote:
                        result["latest_quote"] = {
                            "ask_price": float(snapshot.latest_quote.ask_price) if snapshot.latest_quote.ask_price else None,
                            "bid_price": float(snapshot.latest_quote.bid_price) if snapshot.latest_quote.bid_price else None,
                            "ask_size": snapshot.latest_quote.ask_size,
                            "bid_size": snapshot.latest_quote.bid_size,
                            "timestamp": snapshot.latest_quote.timestamp.isoformat()
                        }
                    
                    # Add minute bar
                    if snapshot.minute_bar:
                        result["minute_bar"] = {
                            "open": float(snapshot.minute_bar.open),
                            "high": float(snapshot.minute_bar.high),
                            "low": float(snapshot.minute_bar.low),
                            "close": float(snapshot.minute_bar.close),
                            "volume": snapshot.minute_bar.volume,
                            "timestamp": snapshot.minute_bar.timestamp.isoformat()
                        }
                    
                    # Add daily bar
                    if snapshot.daily_bar:
                        result["daily_bar"] = {
                            "open": float(snapshot.daily_bar.open),
                            "high": float(snapshot.daily_bar.high),
                            "low": float(snapshot.daily_bar.low),
                            "close": float(snapshot.daily_bar.close),
                            "volume": snapshot.daily_bar.volume,
                            "timestamp": snapshot.daily_bar.timestamp.isoformat()
                        }
                    
                    # Add previous daily bar
                    if snapshot.previous_daily_bar:
                        result["previous_daily_bar"] = {
                            "open": float(snapshot.previous_daily_bar.open),
                            "high": float(snapshot.previous_daily_bar.high),
                            "low": float(snapshot.previous_daily_bar.low),
                            "close": float(snapshot.previous_daily_bar.close),
                            "volume": snapshot.previous_daily_bar.volume,
                            "timestamp": snapshot.previous_daily_bar.timestamp.isoformat()
                        }
                    
                    return json.dumps(result, indent=2)
                
                return json.dumps({"error": f"No snapshot data for {symbol}"})
            except Exception as e:
                logger.error(f"Error fetching snapshot for {symbol}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_latest_bar(symbol: str) -> str:
            """Get the latest bar for a stock symbol."""
            try:
                request = StockLatestBarRequest(symbol_or_symbols=symbol.upper())
                bars = self.data_client.get_stock_latest_bar(request)
                
                if symbol.upper() in bars:
                    bar = bars[symbol.upper()]
                    return json.dumps({
                        "symbol": symbol.upper(),
                        "timestamp": bar.timestamp.isoformat(),
                        "open": float(bar.open),
                        "high": float(bar.high),
                        "low": float(bar.low),
                        "close": float(bar.close),
                        "volume": bar.volume,
                        "vwap": float(bar.vwap) if bar.vwap else None,
                        "trade_count": bar.trade_count
                    }, indent=2)
                return json.dumps({"error": f"No bar data for {symbol}"})
            except Exception as e:
                logger.error(f"Error fetching latest bar for {symbol}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def place_market_order(
            symbol: str,
            qty: float,
            side: str = "buy"
        ) -> str:
            """
            Place a market order (PAPER TRADING ONLY).
            
            Args:
                symbol: Stock ticker symbol
                qty: Quantity to buy/sell
                side: Order side ('buy' or 'sell')
            """
            if not self.paper_trading:
                return json.dumps({"error": "Orders can only be placed in paper trading mode"})
            
            try:
                order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
                
                request = MarketOrderRequest(
                    symbol=symbol.upper(),
                    qty=qty,
                    side=order_side,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.trading_client.submit_order(request)
                
                return json.dumps({
                    "order_id": order.id,
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "side": order.side,
                    "type": order.order_type,
                    "status": order.status,
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None
                }, indent=2)
            except APIError as e:
                logger.error(f"API error placing order: {e}")
                return json.dumps({"error": str(e)})
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def place_limit_order(
            symbol: str,
            qty: float,
            limit_price: float,
            side: str = "buy"
        ) -> str:
            """
            Place a limit order (PAPER TRADING ONLY).
            
            Args:
                symbol: Stock ticker symbol
                qty: Quantity to buy/sell
                limit_price: Limit price for the order
                side: Order side ('buy' or 'sell')
            """
            if not self.paper_trading:
                return json.dumps({"error": "Orders can only be placed in paper trading mode"})
            
            try:
                order_side = OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL
                
                request = LimitOrderRequest(
                    symbol=symbol.upper(),
                    qty=qty,
                    side=order_side,
                    limit_price=limit_price,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.trading_client.submit_order(request)
                
                return json.dumps({
                    "order_id": order.id,
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "side": order.side,
                    "type": order.order_type,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "status": order.status,
                    "submitted_at": order.submitted_at.isoformat() if order.submitted_at else None
                }, indent=2)
            except APIError as e:
                logger.error(f"API error placing order: {e}")
                return json.dumps({"error": str(e)})
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def cancel_order(order_id: str) -> str:
            """Cancel an open order by ID."""
            try:
                self.trading_client.cancel_order_by_id(order_id)
                return json.dumps({"success": True, "message": f"Order {order_id} cancelled"})
            except APIError as e:
                logger.error(f"API error cancelling order: {e}")
                return json.dumps({"error": str(e)})
            except Exception as e:
                logger.error(f"Error cancelling order: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_market_status() -> str:
            """Get current market status (open/closed)."""
            try:
                clock = self.trading_client.get_clock()
                return json.dumps({
                    "is_open": clock.is_open,
                    "timestamp": clock.timestamp.isoformat(),
                    "next_open": clock.next_open.isoformat() if clock.next_open else None,
                    "next_close": clock.next_close.isoformat() if clock.next_close else None
                }, indent=2)
            except Exception as e:
                logger.error(f"Error fetching market status: {e}")
                return json.dumps({"error": str(e)})
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point."""
    try:
        server = AlpacaMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())