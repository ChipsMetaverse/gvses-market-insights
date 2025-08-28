"""
MCP Manager for Multiple Servers
=================================
Manages connections to multiple MCP servers (market-mcp-server and alpaca-mcp-server)
"""

import asyncio
import logging
from typing import Any, Dict, Optional, List
from pathlib import Path
import os

from mcp_client import MCPClient

logger = logging.getLogger(__name__)


class MCPManager:
    """Manager for multiple MCP server connections."""
    
    def __init__(self):
        """Initialize the MCP manager."""
        self.servers = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize all configured MCP servers."""
        if self.initialized:
            return
            
        # Get the project root - check for production first
        if os.path.exists("/app"):
            # Production environment (Docker)
            project_root = Path("/app")
        else:
            # Development environment
            project_root = Path(__file__).parent.parent
        
        # Configure market-mcp-server (Node.js)
        market_server_path = project_root / "market-mcp-server" / "index.js"
        if market_server_path.exists():
            self.servers['market'] = NodeMCPClient(str(market_server_path))
            logger.info("Configured market-mcp-server")
        else:
            logger.warning(f"market-mcp-server not found at {market_server_path}")
        
        # Configure alpaca-mcp-server (Python)
        alpaca_server_path = project_root / "alpaca-mcp-server" / "server.py"
        if alpaca_server_path.exists():
            self.servers['alpaca'] = PythonMCPClient(str(alpaca_server_path))
            logger.info("Configured alpaca-mcp-server")
        else:
            logger.warning(f"alpaca-mcp-server not found at {alpaca_server_path}")
        
        # Start all servers
        for name, server in self.servers.items():
            try:
                await server.start()
                logger.info(f"Started {name} MCP server")
            except Exception as e:
                logger.error(f"Failed to start {name} MCP server: {e}")
        
        self.initialized = True
    
    async def stop(self):
        """Stop all MCP servers."""
        for name, server in self.servers.items():
            try:
                await server.stop()
                logger.info(f"Stopped {name} MCP server")
            except Exception as e:
                logger.error(f"Error stopping {name} MCP server: {e}")
        
        self.initialized = False
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on a specific MCP server.
        
        Args:
            server_name: Name of the server ('market' or 'alpaca')
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool result or None if error
        """
        if not self.initialized:
            await self.initialize()
        
        if server_name not in self.servers:
            logger.error(f"Unknown server: {server_name}")
            return None
        
        return await self.servers[server_name].call_tool(tool_name, arguments)
    
    async def get_stock_data(self, symbol: str, source: str = "auto") -> Dict[str, Any]:
        """
        Get stock data from the appropriate source.
        
        Args:
            symbol: Stock symbol
            source: Data source ('yahoo', 'alpaca', 'auto')
            
        Returns:
            Stock data from the selected source
        """
        if source == "auto":
            # Try Alpaca first if available (professional data)
            if 'alpaca' in self.servers:
                result = await self.call_tool('alpaca', 'get_stock_snapshot', {'symbol': symbol})
                if result and not result.get('error'):
                    return {'source': 'alpaca', 'data': result}
            
            # Fall back to Yahoo Finance
            if 'market' in self.servers:
                result = await self.call_tool('market', 'get_stock_quote', {'symbol': symbol})
                if result:
                    return {'source': 'yahoo', 'data': result}
        
        elif source == "alpaca" and 'alpaca' in self.servers:
            result = await self.call_tool('alpaca', 'get_stock_snapshot', {'symbol': symbol})
            return {'source': 'alpaca', 'data': result}
        
        elif source == "yahoo" and 'market' in self.servers:
            result = await self.call_tool('market', 'get_stock_quote', {'symbol': symbol})
            return {'source': 'yahoo', 'data': result}
        
        return {'error': f"No data available for {symbol} from {source}"}
    
    async def get_historical_data(self, symbol: str, days: int = 30, source: str = "auto") -> Dict[str, Any]:
        """
        Get historical data from the appropriate source.
        
        Args:
            symbol: Stock symbol
            days: Number of days of history
            source: Data source ('yahoo', 'alpaca', 'auto')
            
        Returns:
            Historical data from the selected source
        """
        if source == "auto":
            # Try Alpaca first for professional data
            if 'alpaca' in self.servers:
                result = await self.call_tool('alpaca', 'get_stock_bars', {
                    'symbol': symbol,
                    'timeframe': '1Day',
                    'days_back': days
                })
                if result and not result.get('error'):
                    return {'source': 'alpaca', 'data': result}
            
            # Fall back to Yahoo Finance
            if 'market' in self.servers:
                result = await self.call_tool('market', 'get_stock_history', {
                    'symbol': symbol,
                    'period': f'{days}d' if days <= 30 else '3mo'
                })
                if result:
                    return {'source': 'yahoo', 'data': result}
        
        elif source == "alpaca" and 'alpaca' in self.servers:
            result = await self.call_tool('alpaca', 'get_stock_bars', {
                'symbol': symbol,
                'timeframe': '1Day',
                'days_back': days
            })
            return {'source': 'alpaca', 'data': result}
        
        elif source == "yahoo" and 'market' in self.servers:
            period = f'{days}d' if days <= 30 else '3mo'
            result = await self.call_tool('market', 'get_stock_history', {
                'symbol': symbol,
                'period': period
            })
            return {'source': 'yahoo', 'data': result}
        
        return {'error': f"No historical data available for {symbol} from {source}"}


class NodeMCPClient(MCPClient):
    """MCP client for Node.js servers."""
    
    def __init__(self, server_path: str):
        """Initialize Node.js MCP client."""
        super().__init__(server_path)
        self.runtime = 'node'
    
    async def start(self):
        """Start the Node.js MCP server."""
        if self.process:
            return
            
        try:
            # Start the MCP server as a subprocess
            self.process = await asyncio.create_subprocess_exec(
                'node',
                str(self.server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.server_path.parent,
                env=os.environ.copy()
            )
            
            logger.info(f"Started Node.js MCP server at {self.server_path}")
            
            # Initialize communication
            await self._initialize()
            self._initialized = True
            
            # Start reading responses
            asyncio.create_task(self._read_responses())
            
        except Exception as e:
            logger.error(f"Failed to start Node.js MCP server: {e}")
            raise


class PythonMCPClient(MCPClient):
    """MCP client for Python servers."""
    
    def __init__(self, server_path: str):
        """Initialize Python MCP client."""
        super().__init__(server_path)
        self.runtime = 'python3'
    
    async def start(self):
        """Start the Python MCP server."""
        if self.process:
            return
            
        try:
            # Prepare environment with Alpaca credentials
            env = os.environ.copy()
            env['ALPACA_API_KEY'] = os.getenv('ALPACA_API_KEY', '')
            env['ALPACA_SECRET_KEY'] = os.getenv('ALPACA_SECRET_KEY', '')
            env['ALPACA_BASE_URL'] = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
            
            # Start the MCP server as a subprocess
            self.process = await asyncio.create_subprocess_exec(
                'python3',
                str(self.server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.server_path.parent,
                env=env
            )
            
            logger.info(f"Started Python MCP server at {self.server_path}")
            
            # Initialize communication
            await self._initialize()
            self._initialized = True
            
            # Start reading responses
            asyncio.create_task(self._read_responses())
            
        except Exception as e:
            logger.error(f"Failed to start Python MCP server: {e}")
            raise


# Global manager instance
mcp_manager = MCPManager()