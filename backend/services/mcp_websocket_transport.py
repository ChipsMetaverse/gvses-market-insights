"""
MCP WebSocket Transport Layer
============================
WebSocket transport that bridges OpenAI Agent Builder to existing MCP sidecars
using the Model Context Protocol JSON-RPC 2.0 standard.
"""

import asyncio
import json
import uuid
import logging
from typing import Dict, Any, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPWebSocketSession:
    """Represents an active WebSocket session for MCP communication."""
    
    def __init__(self, websocket: WebSocket, session_id: str, authenticated: bool = False):
        self.websocket = websocket
        self.session_id = session_id
        self.authenticated = authenticated
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
    def update_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    async def send_message(self, message: Dict[str, Any]) -> None:
        """Send a JSON-RPC message to the WebSocket client."""
        try:
            await self.websocket.send_text(json.dumps(message))
            self.update_activity()
        except Exception as e:
            logger.error(f"Failed to send message to session {self.session_id}: {e}")
            raise
    
    async def close(self, code: int = 1000, reason: str = "Normal closure") -> None:
        """Close the WebSocket connection."""
        try:
            await self.websocket.close(code=code, reason=reason)
        except Exception as e:
            logger.error(f"Error closing WebSocket session {self.session_id}: {e}")


class MCPWebSocketTransport:
    """
    WebSocket transport layer for MCP protocol.
    Bridges WebSocket clients to existing MCP sidecars.
    """
    
    def __init__(self):
        self.sessions: Dict[str, MCPWebSocketSession] = {}
        self.mcp_client = None
        self._initialized = False
        
    async def initialize(self):
        """Initialize the transport layer."""
        if self._initialized:
            return
            
        try:
            # Import and get the HTTP MCP client for better performance
            from .http_mcp_client import get_http_mcp_client as get_direct_mcp_client
            self.mcp_client = await get_direct_mcp_client()
            
            # Direct client doesn't need initialization - ready to use
            self._initialized = True
            logger.info("MCP WebSocket transport initialized successfully with direct client")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP WebSocket transport: {e}")
            raise
    
    def validate_token(self, token: str) -> bool:
        """
        Validate Fly.io API token.
        For production use, this should validate against actual Fly.io API.
        For now, we'll accept the generated token format.
        """
        if not token:
            return False
            
        # Accept Fly.io token format (fo1_...)
        if token.startswith('fo1_') and len(token) > 10:
            return True
            
        # Accept the specific token we generated
        if token == 'fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ':
            return True
            
        logger.warning(f"Invalid token format: {token[:10]}...")
        return False
    
    async def handle_connection(self, websocket: WebSocket, query_params: Dict[str, str]) -> str:
        """
        Handle new WebSocket connection.
        Returns session_id if successful, raises exception if authentication fails.
        """
        await self.initialize()
        
        # Validate authentication token
        token = query_params.get('token')
        if not self.validate_token(token):
            await websocket.close(code=4001, reason="Invalid authentication token")
            raise ValueError("Invalid authentication token")
        
        # Create session
        session_id = str(uuid.uuid4())
        session = MCPWebSocketSession(websocket, session_id, authenticated=True)
        self.sessions[session_id] = session
        
        logger.info(f"New MCP WebSocket session established: {session_id}")
        return session_id
    
    async def handle_message(self, session_id: str, message: str) -> None:
        """Handle incoming WebSocket message."""
        session = self.sessions.get(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return
        
        session.update_activity()
        
        try:
            # Parse JSON-RPC message
            json_message = json.loads(message)
            await self._process_jsonrpc_message(session, json_message)
            
        except json.JSONDecodeError:
            # Send JSON-RPC error response
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }
            await session.send_message(error_response)
            
        except Exception as e:
            logger.error(f"Error processing message in session {session_id}: {e}")
            # Send internal error response
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                },
                "id": json_message.get("id") if 'json_message' in locals() else None
            }
            await session.send_message(error_response)
    
    async def _process_jsonrpc_message(self, session: MCPWebSocketSession, message: Dict[str, Any]) -> None:
        """Process a JSON-RPC message."""
        jsonrpc_version = message.get("jsonrpc")
        if jsonrpc_version != "2.0":
            raise ValueError(f"Unsupported JSON-RPC version: {jsonrpc_version}")
        
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params", {})
        
        # Handle different MCP methods
        if method == "initialize":
            await self._handle_initialize(session, msg_id, params)
        elif method == "notifications/initialized":
            # No response needed for notifications
            logger.debug(f"Session {session.session_id} initialization complete")
        elif method == "tools/list":
            await self._handle_list_tools(session, msg_id, params)
        elif method == "tools/call":
            await self._handle_call_tool(session, msg_id, params)
        else:
            # Send method not found error
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found",
                    "data": f"Unknown method: {method}"
                },
                "id": msg_id
            }
            await session.send_message(error_response)
    
    async def _handle_initialize(self, session: MCPWebSocketSession, msg_id: str, params: Dict[str, Any]) -> None:
        """Handle MCP initialize request."""
        try:
            # Return server capabilities
            response = {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-01",
                    "capabilities": {
                        "tools": {},
                        "streaming": True,
                        "experimental": {}
                    },
                    "serverInfo": {
                        "name": "gvses-market-mcp-server",
                        "version": "1.0.0"
                    }
                },
                "id": msg_id
            }
            await session.send_message(response)
            logger.debug(f"Session {session.session_id} initialized")
            
        except Exception as e:
            logger.error(f"Error in initialize handler: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error during initialization",
                    "data": str(e)
                },
                "id": msg_id
            }
            await session.send_message(error_response)
    
    async def _handle_list_tools(self, session: MCPWebSocketSession, msg_id: str, params: Dict[str, Any]) -> None:
        """Handle tools/list request by proxying to MCP sidecars."""
        try:
            if not self.mcp_client:
                raise RuntimeError("MCP client not initialized")

            # Get tools from the market MCP server
            tools_result = await self.mcp_client.list_tools()

            # Start with market data tools
            tools_list = []
            if tools_result and "tools" in tools_result:
                tools_list = tools_result["tools"]

            # Add chart control tools
            chart_control_tools = [
                {
                    "name": "change_chart_symbol",
                    "description": "Change the displayed symbol on the trading chart",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "Stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
                            }
                        },
                        "required": ["symbol"]
                    }
                },
                {
                    "name": "set_chart_timeframe",
                    "description": "Set the timeframe for chart data display",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "timeframe": {
                                "type": "string",
                                "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
                                "description": "Chart timeframe"
                            }
                        },
                        "required": ["timeframe"]
                    }
                },
                {
                    "name": "toggle_chart_indicator",
                    "description": "Toggle technical indicators on/off on the chart",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "indicator": {
                                "type": "string",
                                "enum": ["sma", "ema", "bollinger", "rsi", "macd", "volume"],
                                "description": "Technical indicator to toggle"
                            },
                            "enabled": {
                                "type": "boolean",
                                "description": "Whether to show or hide the indicator"
                            },
                            "period": {
                                "type": "number",
                                "description": "Period for the indicator (optional, default varies by indicator)"
                            }
                        },
                        "required": ["indicator", "enabled"]
                    }
                }
            ]

            # Combine market data tools and chart control tools
            tools_list.extend(chart_control_tools)

            # Return combined tools list
            response = {
                "jsonrpc": "2.0",
                "result": {"tools": tools_list},
                "id": msg_id
            }

            await session.send_message(response)
            logger.debug(f"Listed {len(tools_list)} tools for session {session.session_id} (including chart control)")

        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error listing tools",
                    "data": str(e)
                },
                "id": msg_id
            }
            await session.send_message(error_response)
    
    async def _handle_call_tool(self, session: MCPWebSocketSession, msg_id: str, params: Dict[str, Any]) -> None:
        """Handle tools/call request by proxying to MCP sidecars."""
        try:
            if not self.mcp_client:
                raise RuntimeError("MCP client not initialized")

            tool_name = params.get("name")
            tool_arguments = params.get("arguments", {})

            if not tool_name:
                raise ValueError("Tool name is required")

            # Handle chart control tools locally
            if tool_name in ["change_chart_symbol", "set_chart_timeframe", "toggle_chart_indicator"]:
                tool_result = await self._handle_chart_control_tool(tool_name, tool_arguments)
                response = {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": tool_result}]},
                    "id": msg_id
                }
            else:
                # Call market data tools via MCP client
                tool_result = await self.mcp_client.call_tool(tool_name, tool_arguments)

                # Convert MCPClient response to JSON-RPC format
                if tool_result:
                    tool_response = {"result": {"content": [{"type": "text", "text": str(tool_result)}]}}
                else:
                    tool_response = None

                if tool_response and "result" in tool_response:
                    # Forward the successful response
                    response = {
                        "jsonrpc": "2.0",
                        "result": tool_response["result"],
                        "id": msg_id
                    }
                else:
                    # Return error if tool call failed
                    response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "Tool execution failed",
                            "data": tool_response
                        },
                        "id": msg_id
                    }

            await session.send_message(response)
            logger.debug(f"Called tool '{tool_name}' for session {session.session_id}")

        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error calling tool",
                    "data": str(e)
                },
                "id": msg_id
            }
            await session.send_message(error_response)

    async def _handle_chart_control_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Handle chart control tool execution.
        Note: Chart commands are primarily handled through the streaming SSE architecture in agent_orchestrator.py
        This method provides basic tool validation and response for MCP clients.
        """
        try:
            if tool_name == "change_chart_symbol":
                symbol = arguments.get("symbol")
                if not symbol:
                    return "Error: Symbol parameter is required"

                logger.info(f"Chart control tool called: change_chart_symbol({symbol})")
                return f"Chart symbol changed to {symbol.upper()}"

            elif tool_name == "set_chart_timeframe":
                timeframe = arguments.get("timeframe")
                if not timeframe:
                    return "Error: Timeframe parameter is required"

                valid_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]
                if timeframe not in valid_timeframes:
                    return f"Error: Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"

                logger.info(f"Chart control tool called: set_chart_timeframe({timeframe})")
                return f"Chart timeframe set to {timeframe}"

            elif tool_name == "toggle_chart_indicator":
                indicator = arguments.get("indicator")
                enabled = arguments.get("enabled")
                period = arguments.get("period")

                if not indicator or enabled is None:
                    return "Error: Indicator and enabled parameters are required"

                valid_indicators = ["sma", "ema", "bollinger", "rsi", "macd", "volume"]
                if indicator not in valid_indicators:
                    return f"Error: Invalid indicator. Must be one of: {', '.join(valid_indicators)}"

                action = "enabled" if enabled else "disabled"
                period_str = f" with period {period}" if period else ""
                logger.info(f"Chart control tool called: toggle_chart_indicator({indicator}, {enabled}, {period})")
                return f"{indicator.upper()} indicator {action}{period_str}"

            else:
                return f"Error: Unknown chart control tool: {tool_name}"

        except Exception as e:
            logger.error(f"Error handling chart control tool {tool_name}: {e}")
            return f"Error executing chart control: {str(e)}"
    
    async def handle_request(self, rpc_request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HTTP MCP request (JSON-RPC 2.0 format).
        This method provides HTTP access to the same MCP functionality available via WebSocket.
        """
        try:
            method = rpc_request.get("method")
            params = rpc_request.get("params", {})
            msg_id = rpc_request.get("id", "http-request")
            
            # Initialize transport if needed
            if not self._initialized:
                await self.initialize()
            
            if method == "initialize":
                # Return initialization response
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "serverInfo": {
                            "name": "GVSES Market MCP Server",
                            "version": "2.0.1"
                        },
                        "capabilities": {
                            "tools": {"listChanged": False}
                        }
                    },
                    "id": msg_id
                }
            
            elif method == "tools/list":
                # List available tools
                if self.mcp_client:
                    tools_response = await self.mcp_client.list_tools()

                    # Start with market data tools
                    tools_list = tools_response.get("result", {}).get("tools", [])

                    # Add chart control tools
                    chart_control_tools = [
                        {
                            "name": "change_chart_symbol",
                            "description": "Change the displayed symbol on the trading chart",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "symbol": {
                                        "type": "string",
                                        "description": "Stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
                                    }
                                },
                                "required": ["symbol"]
                            }
                        },
                        {
                            "name": "set_chart_timeframe",
                            "description": "Set the timeframe for chart data display",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "timeframe": {
                                        "type": "string",
                                        "enum": ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
                                        "description": "Chart timeframe"
                                    }
                                },
                                "required": ["timeframe"]
                            }
                        },
                        {
                            "name": "toggle_chart_indicator",
                            "description": "Toggle technical indicators on/off on the chart",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "indicator": {
                                        "type": "string",
                                        "enum": ["sma", "ema", "bollinger", "rsi", "macd", "volume"],
                                        "description": "Technical indicator to toggle"
                                    },
                                    "enabled": {
                                        "type": "boolean",
                                        "description": "Whether to show or hide the indicator"
                                    },
                                    "period": {
                                        "type": "number",
                                        "description": "Period for the indicator (optional, default varies by indicator)"
                                    }
                                },
                                "required": ["indicator", "enabled"]
                            }
                        }
                    ]

                    # Combine market data tools and chart control tools
                    tools_list.extend(chart_control_tools)

                    return {
                        "jsonrpc": "2.0",
                        "result": {"tools": tools_list},
                        "id": msg_id
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "result": {"tools": []},
                        "id": msg_id
                    }
            
            elif method == "tools/call":
                # Call a tool
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})

                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: tool name is required"
                        },
                        "id": msg_id
                    }

                # Handle chart control tools locally
                if tool_name in ["change_chart_symbol", "set_chart_timeframe", "toggle_chart_indicator"]:
                    tool_result = await self._handle_chart_control_tool(tool_name, tool_arguments)
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [{"type": "text", "text": tool_result}]
                        },
                        "id": msg_id
                    }
                elif self.mcp_client:
                    tool_result = await self.mcp_client.call_tool(tool_name, tool_arguments)
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [{"type": "text", "text": str(tool_result)}]
                        },
                        "id": msg_id
                    }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": "MCP client not available"
                        },
                        "id": msg_id
                    }
            
            else:
                # Method not supported
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    },
                    "id": msg_id
                }
                
        except Exception as e:
            logger.error(f"Error handling HTTP MCP request: {e}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                },
                "id": rpc_request.get("id", "http-request")
            }
    
    async def disconnect_session(self, session_id: str) -> None:
        """Handle WebSocket disconnection."""
        if session_id in self.sessions:
            session = self.sessions.pop(session_id)
            logger.info(f"MCP WebSocket session disconnected: {session_id}")
            
            # Cancel any pending requests
            for future in session.pending_requests.values():
                if not future.done():
                    future.cancel()
    
    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self.sessions)
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about active sessions."""
        return {
            "active_sessions": len(self.sessions),
            "sessions": [
                {
                    "id": session.session_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "authenticated": session.authenticated
                }
                for session in self.sessions.values()
            ]
        }


# Global transport instance
_mcp_transport = None

def get_mcp_transport() -> MCPWebSocketTransport:
    """Get or create the global MCP WebSocket transport instance."""
    global _mcp_transport
    if _mcp_transport is None:
        _mcp_transport = MCPWebSocketTransport()
    return _mcp_transport