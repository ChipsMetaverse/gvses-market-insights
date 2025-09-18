"""
MCP Client for Market Data Server
==================================
Handles communication with the market-mcp-server via stdio
"""

import subprocess
import json
import asyncio
import logging
from typing import Any, Dict, Optional, List
import os
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with MCP servers via stdio."""
    
    def __init__(self, server_path: str):
        """
        Initialize MCP client.
        
        Args:
            server_path: Path to the MCP server index.js file
        """
        self.server_path = Path(server_path)
        self.process = None
        self.reader = None
        self.writer = None
        self.request_id = 0
        self.pending_requests = {}
        self._initialized = False
        
    async def start(self):
        """Start the MCP server subprocess and initialize communication."""
        if self.process:
            return
            
        try:
            # Configure environment for production
            env = os.environ.copy()
            env['NODE_ENV'] = 'production'
            env['NODE_OPTIONS'] = '--max-old-space-size=256'  # Reduce memory usage for Docker
            
            # Log the attempt
            logger.info(f"Attempting to start MCP server at {self.server_path}")
            logger.info(f"Working directory: {self.server_path.parent}")
            logger.info(f"Node.js path check: {os.path.exists('/usr/local/bin/node')}")
            
            # Start the MCP server as a subprocess with longer startup time
            self.process = await asyncio.create_subprocess_exec(
                'node',
                str(self.server_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.server_path.parent,
                env=env,
                limit=1024*1024  # Increase buffer size to 1MB
            )
            
            logger.info(f"MCP server process started with PID: {self.process.pid}")
            
            # Give it more time to start in production
            await asyncio.sleep(2.0)
            
            # Initialize communication
            await self._initialize()
            self._initialized = True
            
            # Start reading responses
            asyncio.create_task(self._read_responses())
            
            logger.info("MCP server initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            if self.process and self.process.stderr:
                stderr_output = await self.process.stderr.read(1000)
                if stderr_output:
                    logger.error(f"MCP server stderr: {stderr_output.decode('utf-8', errors='ignore')}")
            raise
    
    async def _initialize(self):
        """Send initialization message to MCP server."""
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-01",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "market-backend",
                    "version": "1.0.0"
                }
            },
            "id": self._get_next_id()
        }
        
        response = await self._send_request(init_request)
        if response:
            logger.info("MCP server initialized successfully")
            
            # Send initialized notification
            await self._send_notification({
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            })
    
    async def stop(self):
        """Stop the MCP server subprocess."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
            self._initialized = False
            logger.info("MCP server stopped")
    
    def _get_next_id(self) -> str:
        """Generate next request ID."""
        self.request_id += 1
        return str(self.request_id)
    
    async def _send_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a request to the MCP server and wait for response."""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        request_id = request.get("id")
        
        # Create future for response
        if request_id:
            future = asyncio.Future()
            self.pending_requests[request_id] = future
        
        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        # Wait for response if this is a request (not a notification)
        if request_id:
            try:
                # Production-ready timeouts: longer for initialization, reasonable for operations
                if request_id == "1":
                    timeout = 30.0  # Initial connection
                elif "news" in str(request).lower():
                    timeout = 15.0  # News queries can be slower
                else:
                    timeout = 10.0  # Normal operations
                
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                logger.error(f"Request {request_id} timed out after {timeout}s")
                del self.pending_requests[request_id]
                return None
        
        return None
    
    async def _send_notification(self, notification: Dict[str, Any]):
        """Send a notification to the MCP server (no response expected)."""
        if not self.process:
            raise RuntimeError("MCP server not started")
        
        notification_json = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_json.encode())
        await self.process.stdin.drain()
    
    async def _read_responses(self):
        """Read responses from the MCP server."""
        while self.process and self.process.stdout:
            try:
                line = await self.process.stdout.readline()
                if not line:
                    break
                    
                try:
                    response = json.loads(line.decode())
                    
                    # Handle response
                    request_id = response.get("id")
                    if request_id and request_id in self.pending_requests:
                        future = self.pending_requests.pop(request_id)
                        if not future.done():
                            future.set_result(response)
                    
                    # Handle notifications
                    if "method" in response and not "id" in response:
                        logger.debug(f"Received notification: {response['method']}")
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON response: {line}")
                    
            except Exception as e:
                logger.error(f"Error reading MCP response: {e}")
                break
    
    async def list_tools(self) -> Optional[Dict[str, Any]]:
        """
        List available MCP tools.
        
        Returns:
            Dict containing tools list or None if error
        """
        if not self._initialized:
            await self.start()
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": self._get_next_id()
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            logger.error(f"MCP tools/list error: {response['error']}")
            return None
        else:
            logger.error("No response from MCP server for tools/list")
            return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool and return the result.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool
            
        Returns:
            Tool result or None if error
        """
        if not self._initialized:
            await self.start()
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": self._get_next_id()
        }
        
        response = await self._send_request(request)
        
        if response and "result" in response:
            result = response["result"]
            # Extract content from tool response
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    first_content = content[0]
                    if isinstance(first_content, dict) and "text" in first_content:
                        try:
                            # Try to parse as JSON
                            return json.loads(first_content["text"])
                        except json.JSONDecodeError:
                            # Return as string if not JSON
                            return first_content["text"]
            return result
        elif response and "error" in response:
            error_msg = response['error']
            logger.error(f"Tool call error: {error_msg}")
            # Return the error message so we can handle it appropriately
            return f"Error: {error_msg.get('message', str(error_msg)) if isinstance(error_msg, dict) else str(error_msg)}"
        else:
            return None


# Singleton instance
_mcp_client = None
_mcp_manager = None


def get_mcp_client() -> MCPClient:
    """Get or create the singleton MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        # Check if running in production (Docker)
        if os.path.exists("/app/market-mcp-server/index.js"):
            # Production path in Docker
            server_path = "/app/market-mcp-server/index.js"
        else:
            # Development path - use repo-relative path
            from pathlib import Path
            repo_root = Path(__file__).resolve().parents[1]
            server_path = str(repo_root / "market-mcp-server" / "index.js")
        _mcp_client = MCPClient(server_path)
    return _mcp_client


def get_mcp_manager():
    """Get or create the singleton MCP manager instance."""
    global _mcp_manager
    if _mcp_manager is None:
        from mcp_manager import mcp_manager
        _mcp_manager = mcp_manager
    return _mcp_manager


# Convenience functions for common market data operations
async def get_stock_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """Get stock quote via MCP."""
    client = get_mcp_client()
    return await client.call_tool("get_stock_quote", {"symbol": symbol})


async def get_stock_history(symbol: str, period: str = "1mo", interval: str = "1d") -> Optional[Dict[str, Any]]:
    """Get stock history via MCP."""
    client = get_mcp_client()
    return await client.call_tool("get_stock_history", {
        "symbol": symbol,
        "period": period,
        "interval": interval
    })


async def get_market_news(keywords: Optional[List[str]] = None, limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    """Get market news via MCP."""
    client = get_mcp_client()
    params = {"limit": limit}
    if keywords:
        params["keywords"] = keywords
    return await client.call_tool("get_market_news", params)


async def get_technical_indicators(symbol: str, indicators: List[str]) -> Optional[Dict[str, Any]]:
    """Get technical indicators via MCP."""
    client = get_mcp_client()
    return await client.call_tool("get_technical_indicators", {
        "symbol": symbol,
        "indicators": indicators
    })


async def get_market_overview() -> Optional[Dict[str, Any]]:
    """Get market overview via MCP."""
    client = get_mcp_client()
    return await client.call_tool("get_market_overview", {})


async def get_market_movers() -> Optional[Dict[str, Any]]:
    """Get market movers via MCP."""
    client = get_mcp_client()
    return await client.call_tool("get_market_movers", {})