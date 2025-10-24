"""
HTTP MCP Client
================
Communicates with the Node.js MCP server via HTTP for better performance.
Replaces the subprocess-based direct_mcp_client.py approach.

Benefits over subprocess approach:
- 10-50x faster (no process creation overhead)
- Connection pooling and reuse
- Better error handling with HTTP status codes
- Lower memory usage (single Node.js instance)
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, AsyncIterator
import httpx

logger = logging.getLogger(__name__)


class HTTPMCPClient:
    """HTTP-based communication client for the Node.js MCP server."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:3001/mcp"):
        """
        Initialize the HTTP MCP client for StreamableHTTP transport.
        
        Args:
            base_url: Base URL of the MCP server (default: http://127.0.0.1:3001/mcp)
        """
        self.base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None
        self._initialized = False
        self._session_id: Optional[str] = None  # MCP session ID
        self._session_lock = asyncio.Lock()      # Lock for session initialization
        self._api_key = os.getenv("MCP_API_KEY")  # API key for authentication
        
        logger.info(f"HTTPMCPClient initialized with StreamableHTTP endpoint: {self.base_url}")
        if self._api_key:
            logger.info("API key configured for MCP authentication")
    
    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=5.0),
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
            )
            self._initialized = True
            logger.info("HTTP client initialized with connection pooling")
    
    async def close(self):
        """Close the HTTP client, terminate session, and cleanup resources."""
        if self._session_id:
            try:
                logger.info(f"Terminating MCP session: {self._session_id}")
                await self._client.delete(
                    self.base_url,
                    headers={"Mcp-Session-Id": self._session_id}
                )
            except Exception as e:
                logger.warning(f"Failed to terminate session gracefully: {e}")
            finally:
                self._session_id = None
        
        if self._client is not None:
            await self._client.aclose()
            self._client = None
            self._initialized = False
            logger.info("HTTP client closed")
    
    async def initialize(self) -> Dict[str, Any]:
        """
        Initialize MCP session with the server.
        Must be called before any tool operations.
        
        Returns:
            Dict containing initialization result
        """
        async with self._session_lock:
            if self._session_id:
                logger.info(f"Session already initialized: {self._session_id}")
                return {"result": {"protocolVersion": "2024-11-05", "sessionId": self._session_id}}
            
            await self._ensure_client()
            
            request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "gvses-backend",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            try:
                logger.info("Initializing MCP session...")
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
                
                # Add API key for authentication
                if self._api_key:
                    headers["X-API-Key"] = self._api_key
                
                response = await self._client.post(
                    self.base_url,
                    json=request,
                    headers=headers
                )
                response.raise_for_status()
                
                # Extract session ID from response headers
                session_id = response.headers.get('mcp-session-id') or response.headers.get('Mcp-Session-Id')
                
                if not session_id:
                    raise RuntimeError("Server did not return session ID in headers")
                
                self._session_id = session_id
                logger.info(f"MCP session initialized successfully: {session_id}")
                
                result = response.json()
                return result
                
            except Exception as e:
                logger.error(f"Failed to initialize MCP session: {e}")
                raise
    
    async def list_tools(self) -> Dict[str, Any]:
        """
        Get available tools from the MCP server.
        
        Returns:
            Dict containing tools list in MCP format
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list", 
            "params": {},
            "id": 1
        }
        
        try:
            response = await self._call_mcp_server(request)
            tools_count = len(response.get('result', {}).get('tools', []))
            logger.info(f"Retrieved {tools_count} tools from MCP server via HTTP")
            return response
        except Exception as e:
            logger.error(f"Failed to list MCP tools via HTTP: {e}")
            # Return empty tools list as fallback
            return {"result": {"tools": []}}
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool with the provided arguments.
        
        Args:
            name: Tool name to call
            arguments: Tool arguments dictionary
            
        Returns:
            Dict containing tool execution result
        """
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            response = await self._call_mcp_server(request)
            logger.info(f"Successfully called MCP tool via HTTP: {name}")
            return response
        except Exception as e:
            logger.error(f"Failed to call MCP tool {name} via HTTP: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                },
                "id": 1
            }
    
    async def call_tool_streaming(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Call a tool and stream results via SSE.
        
        Args:
            tool_name: Tool name to call (e.g., 'stream_market_news')
            arguments: Tool arguments (should include stream=True)
            
        Yields:
            Dict containing SSE event data (JSON-RPC notifications or results)
        """
        await self._ensure_client()
        
        if not self._session_id:
            await self.initialize()
        
        # Add stream flag
        arguments['stream'] = True
        
        request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "Mcp-Session-Id": self._session_id
        }
        
        if self._api_key:
            headers["X-API-Key"] = self._api_key
        
        try:
            logger.info(f"Starting SSE stream for tool: {tool_name}")
            async with self._client.stream(
                "POST",
                self.base_url,
                json=request,
                headers=headers,
                timeout=None  # No timeout for streaming
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        try:
                            event = json.loads(data)
                            logger.debug(f"Received SSE event: {event.get('method', 'result')}")
                            yield event
                        except json.JSONDecodeError as e:
                            logger.warning(f"Invalid JSON in SSE: {data[:100]}... Error: {e}")
                    elif line.startswith('id: '):
                        # Event ID line (can be used for resumability)
                        continue
                    elif line == '':
                        # Empty line (end of event)
                        continue
                        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during streaming: {e.response.status_code}")
            raise RuntimeError(f"Streaming HTTP error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Timeout during streaming")
            raise RuntimeError("Streaming timeout")
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {e}")
            raise
    
    async def _call_mcp_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an HTTP POST request to the MCP server with session management.
        
        Args:
            request: JSON-RPC 2.0 request dictionary
            
        Returns:
            JSON-RPC 2.0 response dictionary
            
        Raises:
            RuntimeError: If session not initialized
            httpx.HTTPError: If HTTP request fails
            json.JSONDecodeError: If response is not valid JSON
        """
        await self._ensure_client()
        
        # Ensure session is initialized (unless this IS an initialize request)
        if request.get("method") != "initialize" and not self._session_id:
            logger.info("No active session, initializing...")
            await self.initialize()
        
        try:
            logger.debug(f"Sending HTTP request to {self.base_url}: {request.get('method')}")
            
            # Build headers with session ID and API key if available
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            # Add API key for authentication
            if self._api_key:
                headers["X-API-Key"] = self._api_key
            
            # Add session ID for stateful requests
            if self._session_id and request.get("method") != "initialize":
                headers["Mcp-Session-Id"] = self._session_id
                logger.debug(f"Using session ID: {self._session_id}")
            
            # Send POST request to MCP server
            response = await self._client.post(
                self.base_url,
                json=request,
                headers=headers
            )
            
            # Check HTTP status
            response.raise_for_status()
            
            # Parse JSON response
            result = response.json()
            
            # Check for JSON-RPC errors
            if "error" in result:
                error = result["error"]
                error_msg = f"MCP server error: {error.get('message', 'Unknown error')}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)
            
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling MCP server: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"MCP HTTP error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error(f"Timeout calling MCP server at {self.base_url}")
            raise RuntimeError("MCP request timeout")
        except httpx.ConnectError:
            logger.error(f"Failed to connect to MCP server at {self.base_url}")
            raise RuntimeError(f"Cannot connect to MCP server at {self.base_url}. Is it running?")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from MCP server: {e}")
            raise RuntimeError("Invalid JSON response from MCP server")
        except Exception as e:
            logger.error(f"Unexpected error calling MCP server: {e}")
            raise


# Singleton instance for reusing sessions across requests
_global_client: Optional[HTTPMCPClient] = None
_client_lock = asyncio.Lock()


async def get_http_mcp_client() -> HTTPMCPClient:
    """
    Get or create singleton HTTP MCP client instance with persistent session.
    This avoids repeated initialize handshakes for every request.
    
    Returns:
        HTTPMCPClient instance with active session
    """
    global _global_client
    
    async with _client_lock:
        if _global_client is None:
            # Determine MCP server URL based on environment
            if os.getenv("FLY_APP_NAME"):
                # Production on Fly.io - use localhost
                base_url = "http://127.0.0.1:3001/mcp"
            else:
                # Development - use localhost
                base_url = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:3001/mcp")
            
            logger.info("Creating new global HTTP MCP client")
            _global_client = HTTPMCPClient(base_url=base_url)
            await _global_client.initialize()
        elif not _global_client._session_id:
            logger.info("Re-initializing expired session")
            await _global_client.initialize()
    
    return _global_client


async def reset_http_mcp_client():
    """Reset the global client (useful for testing or error recovery)."""
    global _global_client
    async with _client_lock:
        if _global_client:
            await _global_client.close()
            _global_client = None

