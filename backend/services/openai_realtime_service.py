"""
[DEPRECATED] OpenAI Realtime API WebSocket Proxy Service
=========================================================
DEPRECATION NOTICE: This service is deprecated. Use openai_relay_server.py instead.
The UI now uses the relay path which properly enforces voice-only architecture.
This legacy service is kept for backward compatibility but should not be used.

Original: Provides a WebSocket proxy to OpenAI's Realtime API.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
import websockets
from websockets.client import WebSocketClientProtocol
from fastapi import WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from .openai_tool_mapper import get_openai_tool_mapper

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIRealtimeService:
    """
    Manages WebSocket connections to OpenAI's Realtime API with tool integration.
    Acts as a proxy between the frontend and OpenAI's API, handling tool calls.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.openai_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-realtime-2025-08-28"
        self.tool_mapper = None
        self.active_tool_calls = {}  # Track ongoing tool calls
        
    async def handle_websocket_connection(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Handle WebSocket connection from frontend and proxy to OpenAI.
        
        Args:
            websocket: FastAPI WebSocket connection from frontend
            session_id: Unique session identifier
        """
        await websocket.accept()
        await self._handle_connection_logic(websocket, session_id)
    
    async def handle_websocket_connection_accepted(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Handle WebSocket connection that has already been accepted.
        
        Args:
            websocket: FastAPI WebSocket connection from frontend (already accepted)
            session_id: Unique session identifier
        """
        await self._handle_connection_logic(websocket, session_id)
    
    async def _handle_connection_logic(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Shared connection logic for both connection methods.
        """
        openai_ws: Optional[WebSocketClientProtocol] = None
        
        try:
            # Connect to OpenAI Realtime API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
            
            # Add model parameter to URL
            url_with_model = f"{self.openai_url}?model={self.model}"
            
            logger.info(f"🔗 DEBUG: About to call websockets.connect() with URL: {url_with_model}")
            logger.info(f"🔗 DEBUG: Headers: {headers}")
            logger.info(f"🔗 DEBUG: Using additional_headers parameter (websockets {websockets.__version__})")
            
            # websockets v13+ uses extra_headers; also pass subprotocol for compatibility
            openai_ws = await websockets.connect(
                url_with_model,
                extra_headers=headers,
                subprotocols=["openai-realtime"]
            )
            
            logger.info(f"🔗 DEBUG: websockets.connect() successful!")
            
            logger.info(f"Connected to OpenAI Realtime API for session {session_id}")
            
            # Initialize tool mapper if not already done
            if not self.tool_mapper:
                try:
                    self.tool_mapper = await get_openai_tool_mapper()
                    logger.info("Tool mapper initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize tool mapper: {e}")
                    # Continue without tools for graceful degradation
                    
            # [DEPRECATED] No tools in voice-only architecture
            tools = []
            logger.info(f"🔍 DEPRECATED: This service path should not be used. Tools disabled for session {session_id}")
            
            logger.info(f"🔍 POST-TOOLS: After tools loading block for session {session_id}")
            
            # Enhanced instructions for market analysis
            logger.info(f"🔍 CHECKPOINT: About to start session config building for session {session_id}")
            try:
                logger.info(f"🔧 Step 1: Creating instructions string for session {session_id}")
                instructions = """You are an advanced AI trading and market analysis assistant with real-time voice capabilities and access to comprehensive market data tools.

Your capabilities include:
- Real-time stock quotes, historical data, and technical analysis
- Market news from CNBC and Yahoo Finance
- Cryptocurrency prices and market data
- Market overview, movers, and sector performance
- Analyst ratings, earnings data, and insider trading information
- Economic indicators and treasury yields

Guidelines:
- Use tools proactively to get real-time data for user queries
- Keep voice responses concise but informative
- Explain your analysis in simple terms
- When showing numbers, use natural speech patterns (e.g., "Apple is trading at two hundred and thirty dollars")
- If tools fail, acknowledge the issue and provide general guidance
- Always specify data sources and timestamps when relevant

Examples of natural interactions:
- "What's Tesla doing today?" → Use get_stock_quote tool → Provide price, change, and brief analysis
- "Show me the market overview" → Use get_market_overview tool → Summarize major indices
- "How has Apple performed this quarter?" → Use get_stock_history tool → Analyze performance trends"""
                logger.info(f"✅ Step 1 complete: Instructions string created ({len(instructions)} chars) for session {session_id}")
                
                logger.info(f"🔧 Step 2: Validating tools array for session {session_id}")
                if not isinstance(tools, list):
                    raise ValueError(f"Tools must be a list, got {type(tools)}")
                logger.info(f"✅ Step 2 complete: Tools validated ({len(tools)} tools) for session {session_id}")
                
                logger.info(f"🔧 Step 3: Building session configuration dict for session {session_id}")
                session_config = {
                    "type": "session.update",
                    "session": {
                        "modalities": ["text", "audio"],
                        "instructions": instructions,
                        "voice": "alloy",
                        "input_audio_format": "pcm16",
                        "output_audio_format": "pcm16",
                        "input_audio_transcription": {
                            "model": "whisper-1"
                        },
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 500
                        },
                        "tools": [],  # Voice-only - no tools
                        "tool_choice": "none",  # Disabled
                        "temperature": 0.7,
                        "max_response_output_tokens": 4096
                    }
                }
                logger.info(f"✅ Step 3 complete: Session configuration dict created for session {session_id}")
                
            except Exception as e:
                logger.error(f"❌ CRITICAL ERROR during session config building for session {session_id}: {e}")
                logger.error(f"   Exception type: {type(e)}")
                logger.error(f"   Tools type: {type(tools)}, length: {len(tools) if hasattr(tools, '__len__') else 'unknown'}")
                import traceback
                logger.error(f"   Full traceback: {traceback.format_exc()}")
                raise
            
            logger.info(f"📤 Sending session configuration to OpenAI for session {session_id}")
            try:
                await openai_ws.send(json.dumps(session_config))
                logger.info(f"✅ Session configuration sent successfully for session {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to send session config for session {session_id}: {e}")
                raise
            
            # Let OpenAI's native session.created message flow through to RealtimeClient
            logger.info(f"📡 Session configured - OpenAI's session.created will notify RealtimeClient for session {session_id}")
            
            # Create tasks for bidirectional message forwarding
            logger.info(f"🚀 Creating forwarding tasks for session {session_id}")
            frontend_to_openai_task = asyncio.create_task(
                self.forward_frontend_to_openai(websocket, openai_ws, session_id)
            )
            openai_to_frontend_task = asyncio.create_task(
                self.forward_openai_to_frontend(openai_ws, websocket, session_id)
            )
            logger.info(f"✅ Forwarding tasks created for session {session_id}")
            
            # Wait for either task to complete (connection closed)
            logger.info(f"🔄 Waiting for forwarding tasks to complete for session {session_id}")
            done, pending = await asyncio.wait(
                [frontend_to_openai_task, openai_to_frontend_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Log which task completed first
            for task in done:
                if task == frontend_to_openai_task:
                    logger.info(f"❌ Frontend-to-OpenAI task completed first for session {session_id}")
                    try:
                        result = await task
                        logger.info(f"❌ Task result: {result}")
                    except Exception as e:
                        logger.info(f"❌ Task exception: {e}")
                elif task == openai_to_frontend_task:
                    logger.info(f"❌ OpenAI-to-frontend task completed first for session {session_id}")
                    try:
                        result = await task
                        logger.info(f"❌ Task result: {result}")
                    except Exception as e:
                        logger.info(f"❌ Task exception: {e}")
            
            # Cancel pending tasks
            for task in pending:
                logger.info(f"🚫 Canceling pending task for session {session_id}")
                task.cancel()
                
        except Exception as e:
            import traceback
            full_traceback = traceback.format_exc()
            logger.error(f"Error in OpenAI Realtime connection for session {session_id}: {e}")
            logger.error(f"Full traceback: {full_traceback}")
            
            # Send error to frontend
            try:
                await websocket.send_json({
                    "type": "error",
                    "error": {
                        "message": str(e),
                        "type": "connection_error",
                        "traceback": full_traceback  # Include traceback for debugging
                    }
                })
            except:
                pass
                
        finally:
            # Clean up connections
            if openai_ws:
                await openai_ws.close()
            try:
                await websocket.close()
            except:
                pass
            
            logger.info(f"Closed OpenAI Realtime connection for session {session_id}")
    
    async def forward_frontend_to_openai(
        self,
        frontend_ws: WebSocket,
        openai_ws: WebSocketClientProtocol,
        session_id: str
    ):
        """
        Forward messages from frontend to OpenAI.
        """
        logger.info(f"➡️ Starting frontend-to-OpenAI forwarding for session {session_id}")
        try:
            while True:
                # Receive from frontend
                data = await frontend_ws.receive()
                
                if data["type"] == "websocket.disconnect":
                    break
                    
                # Handle different message types
                if "text" in data:
                    message = json.loads(data["text"])
                    
                    # Transform frontend messages to OpenAI format if needed
                    if message.get("type") == "input_audio_buffer.append":
                        # Audio data from frontend
                        await openai_ws.send(json.dumps(message))
                        
                    elif message.get("type") == "conversation.item.create":
                        # Text message from frontend
                        await openai_ws.send(json.dumps(message))
                        
                    elif message.get("type") == "response.create":
                        # Request for response
                        await openai_ws.send(json.dumps(message))
                        
                    elif message.get("type") == "session.update":
                        # Session configuration update
                        await openai_ws.send(json.dumps(message))
                        
                    else:
                        # Forward as-is
                        await openai_ws.send(json.dumps(message))
                        
                elif "bytes" in data:
                    # Binary audio data
                    await openai_ws.send(data["bytes"])
                    
        except WebSocketDisconnect:
            logger.info(f"🔌 Frontend disconnected for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error forwarding frontend to OpenAI for session {session_id}: {e}")
        finally:
            logger.info(f"💭 Frontend-to-OpenAI forwarding ended for session {session_id}")
    
    async def forward_openai_to_frontend(
        self,
        openai_ws: WebSocketClientProtocol,
        frontend_ws: WebSocket,
        session_id: str
    ):
        """
        Forward messages from OpenAI to frontend.
        """
        logger.info(f"⬅️ Starting OpenAI-to-frontend forwarding for session {session_id}")
        try:
            async for message in openai_ws:
                if isinstance(message, str):
                    # JSON message from OpenAI
                    data = json.loads(message)
                    
                    # Forward OpenAI events directly to RealtimeClient with minimal processing
                    message_type = data.get("type", "")
                    
                    # Only intercept tool calls for backend processing
                    if message_type == "response.function_call_arguments.delta":
                        # Handle tool calls on backend but also forward to frontend
                        await frontend_ws.send_json(data)
                        # Tool handling logic can be added here if needed
                        
                    elif message_type == "response.function_call_arguments.done":
                        # Handle completed tool calls
                        await frontend_ws.send_json(data)
                        # Tool execution logic can be added here if needed
                        
                    elif message_type == "response.audio.delta":
                        # Audio chunk from assistant
                        await frontend_ws.send_json({
                            "type": "audio",
                            "data": data.get("delta", "")
                        })
                        
                    elif message_type == "response.function_call_arguments.delta":
                        # Function call in progress
                        await frontend_ws.send_json({
                            "type": "tool_call_delta",
                            "delta": data.get("delta", "")
                        })
                        
                    elif message_type == "response.function_call_arguments.done":
                        # Function call complete - execute the tool
                        call_id = data.get("call_id")
                        tool_name = data.get("name", "")
                        arguments_str = data.get("arguments", "{}")
                        
                        try:
                            arguments = json.loads(arguments_str)
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Notify frontend that tool is being executed
                        await frontend_ws.send_json({
                            "type": "tool_call_start",
                            "call_id": call_id,
                            "tool_name": tool_name,
                            "arguments": arguments
                        })
                        
                        # Execute tool in background
                        asyncio.create_task(
                            self._execute_tool_and_respond(
                                openai_ws, frontend_ws, call_id, tool_name, arguments, session_id
                            )
                        )
                        
                    elif message_type == "error":
                        # Error from OpenAI
                        await frontend_ws.send_json({
                            "type": "error",
                            "error": data.get("error", {})
                        })
                        
                    else:
                        # Forward other messages as-is
                        await frontend_ws.send_json(data)
                        
                elif isinstance(message, bytes):
                    # Binary audio data from OpenAI
                    await frontend_ws.send_bytes(message)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 OpenAI connection closed for session {session_id}")
        except Exception as e:
            logger.error(f"❌ Error forwarding OpenAI to frontend for session {session_id}: {e}")
        finally:
            logger.info(f"💭 OpenAI-to-frontend forwarding ended for session {session_id}")
    
    async def _execute_tool_and_respond(
        self,
        openai_ws: WebSocketClientProtocol,
        frontend_ws: WebSocket,
        call_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        session_id: str
    ):
        """
        Execute a tool call and send the result back to OpenAI.
        Based on OpenAI Realtime API documentation for function calling.
        """
        try:
            logger.info(f"Executing tool {tool_name} with call_id {call_id} for session {session_id}")
            
            # Track this tool call
            self.active_tool_calls[call_id] = {
                "tool_name": tool_name,
                "arguments": arguments,
                "status": "executing",
                "start_time": asyncio.get_event_loop().time()
            }
            
            # Execute the tool via tool mapper
            if not self.tool_mapper:
                raise RuntimeError("Tool mapper not initialized")
            
            tool_result = await self.tool_mapper.execute_tool(tool_name, arguments)
            
            # Update tool call status
            self.active_tool_calls[call_id]["status"] = "completed"
            self.active_tool_calls[call_id]["result"] = tool_result
            
            # Prepare the output for OpenAI
            output = json.dumps(tool_result)
            
            # Send function_call_output to OpenAI as per the API documentation
            function_output_event = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": output
                }
            }
            
            await openai_ws.send(json.dumps(function_output_event))
            
            # Trigger a new response from OpenAI
            response_create_event = {
                "type": "response.create"
            }
            
            await openai_ws.send(json.dumps(response_create_event))
            
            # Notify frontend of successful tool execution
            await frontend_ws.send_json({
                "type": "tool_call_complete",
                "call_id": call_id,
                "tool_name": tool_name,
                "success": tool_result.get("success", True),
                "result": tool_result
            })
            
            logger.info(f"Tool {tool_name} completed successfully for call_id {call_id}")
            
        except Exception as e:
            logger.error(f"Tool execution failed for {tool_name} (call_id: {call_id}): {e}")
            
            # Update tool call status
            if call_id in self.active_tool_calls:
                self.active_tool_calls[call_id]["status"] = "failed"
                self.active_tool_calls[call_id]["error"] = str(e)
            
            # Send error result to OpenAI
            error_output = json.dumps({
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            })
            
            try:
                function_output_event = {
                    "type": "conversation.item.create", 
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": error_output
                    }
                }
                
                await openai_ws.send(json.dumps(function_output_event))
                
                # Still trigger a response even on error
                response_create_event = {
                    "type": "response.create"
                }
                
                await openai_ws.send(json.dumps(response_create_event))
                
            except Exception as send_error:
                logger.error(f"Failed to send error result to OpenAI: {send_error}")
            
            # Notify frontend of failed tool execution
            try:
                await frontend_ws.send_json({
                    "type": "tool_call_error",
                    "call_id": call_id,
                    "tool_name": tool_name,
                    "error": str(e)
                })
            except Exception as frontend_error:
                logger.error(f"Failed to notify frontend of tool error: {frontend_error}")
        
        finally:
            # Clean up old tool call records (keep last 10)
            if len(self.active_tool_calls) > 10:
                oldest_calls = sorted(
                    self.active_tool_calls.items(),
                    key=lambda x: x[1].get("start_time", 0)
                )[:len(self.active_tool_calls) - 10]
                
                for old_call_id, _ in oldest_calls:
                    del self.active_tool_calls[old_call_id]
    
    async def get_tool_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific tool call."""
        return self.active_tool_calls.get(call_id)
    
    async def get_active_tool_calls(self) -> Dict[str, Dict[str, Any]]:
        """Get all active tool calls for debugging."""
        return self.active_tool_calls.copy()

# Create singleton instance
openai_realtime_service = OpenAIRealtimeService()
