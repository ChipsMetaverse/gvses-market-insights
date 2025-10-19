"""
Direct MCP Client
=================
Communicates directly with the running Node.js MCP server via subprocess.
Replaces the problematic mcp_client.py that creates resource conflicts.

This client uses the proven direct communication approach that we tested
successfully, avoiding the supervisord process conflicts.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DirectMCPClient:
    """Direct communication client for the Node.js MCP server."""
    
    def __init__(self):
        """Initialize the direct MCP client."""
        # Initialize state
        self._initialized = True
        
        # Determine MCP server path based on environment
        if os.path.exists("/app/market-mcp-server/index.js"):
            # Production path
            self.server_path = "/app/market-mcp-server/index.js"
        else:
            # Development path
            repo_root = Path(__file__).resolve().parents[2]
            self.server_path = str(repo_root / "market-mcp-server" / "index.js")
        
        logger.info(f"DirectMCPClient initialized with server path: {self.server_path}")
    
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
            logger.info(f"Retrieved {len(response.get('result', {}).get('tools', []))} tools from MCP server")
            return response
        except Exception as e:
            logger.error(f"Failed to list MCP tools: {e}")
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
            logger.info(f"Successfully called MCP tool: {name}")
            return response
        except Exception as e:
            logger.error(f"Failed to call MCP tool {name}: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Tool execution failed: {str(e)}"
                },
                "id": 1
            }
    
    async def _call_mcp_server(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a direct call to the Node.js MCP server via subprocess.
        
        This uses the same approach that worked in our manual testing:
        echo 'JSON_REQUEST' | node index.js
        
        Args:
            request: JSON-RPC 2.0 request dictionary
            
        Returns:
            JSON-RPC 2.0 response dictionary
        """
        try:
            # Prepare the JSON request
            json_request = json.dumps(request)
            logger.debug(f"Sending MCP request: {json_request}")
            
            # Create subprocess for direct Node.js communication
            process = await asyncio.create_subprocess_exec(
                'node',
                self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(self.server_path).parent
            )
            
            # Send request and get response
            stdout, stderr = await asyncio.wait_for(
                process.communicate(json_request.encode() + b'\n'),
                timeout=30.0  # 30 second timeout
            )
            
            # Check for process errors
            if process.returncode != 0:
                error_msg = stderr.decode().strip() if stderr else "Unknown error"
                raise RuntimeError(f"MCP server process failed: {error_msg}")
            
            # Parse response
            response_text = stdout.decode().strip()
            if not response_text:
                raise RuntimeError("MCP server returned empty response")
            
            # Handle multiple JSON objects in response (filter out server startup messages)
            lines = response_text.split('\n')
            for line in reversed(lines):  # Start from the end to get the actual response
                line = line.strip()
                if line and line.startswith('{'):
                    try:
                        response = json.loads(line)
                        if 'jsonrpc' in response:
                            logger.debug(f"Received MCP response: {json.dumps(response)[:200]}...")
                            return response
                    except json.JSONDecodeError:
                        continue
            
            raise RuntimeError(f"No valid JSON-RPC response found in output: {response_text}")
            
        except asyncio.TimeoutError:
            logger.error("MCP server call timed out after 30 seconds")
            raise RuntimeError("MCP server call timed out")
        except Exception as e:
            logger.error(f"Error calling MCP server: {e}")
            raise


# Global instance for backward compatibility with existing code
_direct_mcp_client = None

def get_direct_mcp_client() -> DirectMCPClient:
    """Get or create the global DirectMCPClient instance."""
    global _direct_mcp_client
    if _direct_mcp_client is None:
        _direct_mcp_client = DirectMCPClient()
    return _direct_mcp_client


# Compatibility functions for easy migration from mcp_client.py
async def get_stock_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """Get stock quote via direct MCP client."""
    client = get_direct_mcp_client()
    try:
        result = await client.call_tool("get_stock_quote", {"symbol": symbol})
        if "error" in result:
            logger.error(f"MCP stock quote error: {result['error']}")
            return None
        return result.get("result")
    except Exception as e:
        logger.error(f"Failed to get stock quote for {symbol}: {e}")
        return None


async def get_stock_history(symbol: str, period: str = "1y") -> Optional[Dict[str, Any]]:
    """Get stock history via direct MCP client."""
    client = get_direct_mcp_client()
    try:
        result = await client.call_tool("get_stock_history", {
            "symbol": symbol,
            "period": period
        })
        if "error" in result:
            logger.error(f"MCP stock history error: {result['error']}")
            return None
        return result.get("result")
    except Exception as e:
        logger.error(f"Failed to get stock history for {symbol}: {e}")
        return None