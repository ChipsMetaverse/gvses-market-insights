"""
OpenAI Realtime API Relay Server
================================
Secure relay server that follows OpenAI's recommended patterns for browser environments.
Provides a WebSocket endpoint that relays to OpenAI's Realtime API without exposing API keys.
"""

import os
import json
import asyncio
import logging
from typing import Optional, Dict, Any
import websockets
from websockets.client import WebSocketClientProtocol
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from dotenv import load_dotenv
from .openai_tool_mapper import get_openai_tool_mapper

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIRealtimeRelay:
    """
    Secure relay server for OpenAI Realtime API following recommended patterns.
    Acts as a proxy between frontend RealtimeClient and OpenAI's API.
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.openai_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-realtime-preview-2024-12-17"
        self.tool_mapper = None
        self.active_sessions = {}  # Track active sessions
        
    async def handle_relay_connection(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Handle WebSocket connection from RealtimeClient and relay to OpenAI.
        This follows the official relay server pattern.
        [DEPRECATED: Use handle_relay_connection_accepted instead]
        """
        await websocket.accept()
        await self.handle_relay_connection_accepted(websocket, session_id)
    
    async def handle_relay_connection_accepted(
        self,
        websocket: WebSocket,
        session_id: str
    ):
        """
        Handle already-accepted WebSocket connection from RealtimeClient and relay to OpenAI.
        This method assumes the WebSocket has already been accepted with proper subprotocol handling.
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
            
            openai_ws = await websockets.connect(
                url_with_model,
                additional_headers=headers
            )
            
            logger.info(f"Relay connection established for session {session_id}")
            
            # Initialize tool mapper for this session
            if not self.tool_mapper:
                try:
                    self.tool_mapper = await get_openai_tool_mapper()
                    logger.info("Tool mapper initialized for relay")
                except Exception as e:
                    logger.error(f"Failed to initialize tool mapper: {e}")
                    # Continue without tools for graceful degradation
            
            # Store session info
            self.active_sessions[session_id] = {
                "websocket": websocket,
                "openai_ws": openai_ws,
                "tool_mapper": self.tool_mapper,
                "session_configured": False
            }
            
            # Wait for session.created event before configuring
            logger.info(f"Waiting for session.created from OpenAI for session {session_id}")
            
            # Start listening for session.created
            session_created = False
            for _ in range(10):  # Try up to 10 messages
                try:
                    msg = await asyncio.wait_for(openai_ws.recv(), timeout=2.0)
                    if isinstance(msg, str):
                        data = json.loads(msg)
                        # Forward to frontend
                        await websocket.send_json(data)
                        
                        if data.get("type") == "session.created":
                            logger.info(f"Received session.created for session {session_id}")
                            session_created = True
                            # NOW configure the session with tools
                            await self._configure_session(openai_ws)
                            self.active_sessions[session_id]["session_configured"] = True
                            break
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout waiting for session.created for session {session_id}")
                    break
                except Exception as e:
                    logger.error(f"Error waiting for session.created: {e}")
                    break
            
            if not session_created:
                logger.warning(f"Never received session.created for session {session_id}, sending config anyway")
                await self._configure_session(openai_ws)
            
            # Create bidirectional relay tasks
            frontend_to_openai_task = asyncio.create_task(
                self._relay_frontend_to_openai(websocket, openai_ws, session_id)
            )
            openai_to_frontend_task = asyncio.create_task(
                self._relay_openai_to_frontend(openai_ws, websocket, session_id)
            )
            
            # Wait for either connection to close
            done, pending = await asyncio.wait(
                [frontend_to_openai_task, openai_to_frontend_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                
        except Exception as e:
            logger.error(f"Error in relay connection for session {session_id}: {e}")
            
            # Send error to frontend
            try:
                await websocket.send_json({
                    "type": "error",
                    "error": {
                        "message": str(e),
                        "type": "relay_error"
                    }
                })
            except:
                pass
                
        finally:
            # Clean up session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                
            # Close connections
            if openai_ws:
                await openai_ws.close()
            try:
                await websocket.close()
            except:
                pass
            
            logger.info(f"Relay connection closed for session {session_id}")
    
    async def _configure_session(self, openai_ws: WebSocketClientProtocol):
        """Configure the OpenAI session with tools and enhanced instructions."""
        
        # Get available tools
        tools = []
        if self.tool_mapper:
            try:
                tools = self.tool_mapper.get_high_priority_tools()
                logger.info(f"Configured {len(tools)} tools for relay session")
            except Exception as e:
                logger.error(f"Failed to load tools: {e}")
        
        # Load enhanced instructions from training module
        try:
            from pathlib import Path
            import sys
            training_path = Path(__file__).parent.parent / 'agent_training'
            if training_path.exists():
                sys.path.insert(0, str(training_path.parent))
                instructions_file = training_path / 'instructions.md'
                if instructions_file.exists():
                    with open(instructions_file, 'r') as f:
                        instructions = f.read()
                    logger.info("Loaded enhanced instructions from training module")
                    
                    # Integrate technical analysis knowledge
                    try:
                        from agent_training.knowledge_integration import TechnicalAnalysisKnowledge, knowledge_enhancer
                        ta_knowledge = TechnicalAnalysisKnowledge()
                        
                        # Add technical analysis knowledge to instructions
                        knowledge_section = "\n\n## Technical Analysis Knowledge\n\n"
                        knowledge_section += "You have access to comprehensive technical analysis knowledge including:\n\n"
                        
                        # Add chart patterns
                        chart_patterns = ta_knowledge.knowledge_base['chart_patterns']
                        if chart_patterns:
                            knowledge_section += "### Chart Patterns\n"
                            for pattern_name, pattern_info in list(chart_patterns.items())[:5]:  # Top 5 patterns
                                knowledge_section += f"- **{pattern_name}**: {pattern_info.get('description', '')[:100]}...\n"
                            knowledge_section += "\n"
                        
                        # Add candlestick patterns
                        candlestick_patterns = ta_knowledge.knowledge_base['candlestick_patterns']
                        if candlestick_patterns:
                            knowledge_section += "### Candlestick Patterns\n"
                            for pattern_name, pattern_info in list(candlestick_patterns.items())[:5]:  # Top 5 patterns
                                knowledge_section += f"- **{pattern_name}**: {pattern_info.get('description', '')[:100]}...\n"
                            knowledge_section += "\n"
                        
                        # Add technical indicators
                        indicators = ta_knowledge.knowledge_base['technical_indicators']
                        if indicators:
                            knowledge_section += "### Technical Indicators\n"
                            for indicator_name, indicator_info in list(indicators.items())[:5]:  # Top 5 indicators
                                knowledge_section += f"- **{indicator_name}**: {indicator_info.get('description', '')[:100]}...\n"
                            knowledge_section += "\n"
                        
                        knowledge_section += "Use this knowledge to provide detailed technical analysis when discussing stocks, patterns, and market movements.\n"
                        instructions += knowledge_section
                        
                        logger.info(f"Integrated technical analysis knowledge: {len(chart_patterns)} chart patterns, {len(candlestick_patterns)} candlestick patterns, {len(indicators)} indicators")
                        
                    except Exception as knowledge_error:
                        logger.warning(f"Failed to load technical analysis knowledge: {knowledge_error}")
                        # Continue with basic instructions
                    
                else:
                    # Fallback to basic instructions
                    instructions = self._get_fallback_instructions()
            else:
                instructions = self._get_fallback_instructions()
        except Exception as e:
            logger.error(f"Failed to load enhanced instructions: {e}")
            instructions = self._get_fallback_instructions()
        
        # Send session configuration
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
                "tools": tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_response_output_tokens": 4096
            }
        }
        
        await openai_ws.send(json.dumps(session_config))
    
    def _get_fallback_instructions(self) -> str:
        """Get fallback instructions if enhanced ones can't be loaded."""
        return """You are MarketSage, an AI trading and market analysis assistant with real-time voice capabilities.

Your capabilities include:
- Real-time stock quotes, historical data, and technical analysis
- Market news from CNBC and Yahoo Finance
- Cryptocurrency prices and market data
- Market overview, movers, and sector performance
- Analyst ratings, earnings data, and insider trading information

Voice Guidelines:
- Keep responses concise but informative for voice delivery
- Use natural speech patterns (e.g., "Apple is trading at two hundred thirty dollars")
- Explain analysis in simple terms accessible to all users
- When showing numbers, speak them clearly and naturally
- If tools fail, acknowledge gracefully and provide general guidance
- Always specify data sources and timestamps when relevant

Tool Usage:
- Use tools proactively to get real-time data for user queries
- Chain multiple tools for comprehensive analysis when appropriate
- Always verify tool results before presenting to user

IMPORTANT: This is market data and analysis, not investment advice."""
    
    async def _relay_frontend_to_openai(
        self,
        frontend_ws: WebSocket,
        openai_ws: WebSocketClientProtocol,
        session_id: str
    ):
        """Relay messages from RealtimeClient to OpenAI API."""
        try:
            while True:
                # Receive from frontend
                data = await frontend_ws.receive()
                
                if data["type"] == "websocket.disconnect":
                    break
                
                # Forward message to OpenAI
                if "text" in data:
                    # JSON message from RealtimeClient
                    await openai_ws.send(data["text"])
                elif "bytes" in data:
                    # Binary audio data
                    await openai_ws.send(data["bytes"])
                    
        except WebSocketDisconnect:
            logger.info(f"Frontend disconnected for relay session {session_id}")
        except Exception as e:
            logger.error(f"Error relaying frontend to OpenAI for session {session_id}: {e}")
    
    async def _relay_openai_to_frontend(
        self,
        openai_ws: WebSocketClientProtocol,
        frontend_ws: WebSocket,
        session_id: str
    ):
        """Relay messages from OpenAI API to RealtimeClient with tool execution."""
        try:
            async for message in openai_ws:
                if isinstance(message, str):
                    # JSON message from OpenAI
                    data = json.loads(message)
                    
                    # Handle function calls if we have a tool mapper
                    if (data.get("type") == "response.function_call_arguments.done" and 
                        self.tool_mapper):
                        await self._handle_function_call(
                            data, openai_ws, frontend_ws, session_id
                        )
                    else:
                        # Forward message to frontend
                        await frontend_ws.send_json(data)
                        
                elif isinstance(message, bytes):
                    # Binary audio data from OpenAI
                    await frontend_ws.send_bytes(message)
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"OpenAI connection closed for relay session {session_id}")
        except Exception as e:
            logger.error(f"Error relaying OpenAI to frontend for session {session_id}: {e}")
    
    async def _handle_function_call(
        self,
        data: Dict[str, Any],
        openai_ws: WebSocketClientProtocol,
        frontend_ws: WebSocket,
        session_id: str
    ):
        """Handle function calls during relay with automatic tool execution."""
        try:
            call_id = data.get("call_id")
            tool_name = data.get("name", "")
            arguments_str = data.get("arguments", "{}")
            
            try:
                arguments = json.loads(arguments_str)
            except json.JSONDecodeError:
                arguments = {}
            
            logger.info(f"Relay executing tool {tool_name} for session {session_id}")
            
            # Notify frontend of tool execution
            await frontend_ws.send_json({
                "type": "tool_call_start",
                "call_id": call_id,
                "tool_name": tool_name,
                "arguments": arguments
            })
            
            # Execute tool
            if self.tool_mapper:
                tool_result = await self.tool_mapper.execute_tool(tool_name, arguments)
                
                # Send result back to OpenAI
                output = json.dumps(tool_result)
                
                function_output_event = {
                    "type": "conversation.item.create",
                    "item": {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": output
                    }
                }
                
                await openai_ws.send(json.dumps(function_output_event))
                
                # Trigger response
                response_create_event = {"type": "response.create"}
                await openai_ws.send(json.dumps(response_create_event))
                
                # Notify frontend of completion
                await frontend_ws.send_json({
                    "type": "tool_call_complete",
                    "call_id": call_id,
                    "tool_name": tool_name,
                    "success": tool_result.get("success", True),
                    "result": tool_result
                })
                
                logger.info(f"Relay tool execution complete: {tool_name}")
                
        except Exception as e:
            logger.error(f"Tool execution failed in relay: {e}")
            
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
                await openai_ws.send(json.dumps({"type": "response.create"}))
                
                # Notify frontend of error
                await frontend_ws.send_json({
                    "type": "tool_call_error",
                    "call_id": call_id,
                    "tool_name": tool_name,
                    "error": str(e)
                })
                
            except Exception as send_error:
                logger.error(f"Failed to send error result: {send_error}")
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an active session."""
        return self.active_sessions.get(session_id)
    
    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active relay sessions."""
        return {
            session_id: {
                "session_id": session_id,
                "tool_mapper_available": session["tool_mapper"] is not None,
                "connection_active": True
            }
            for session_id, session in self.active_sessions.items()
        }

# Create singleton instance
openai_relay_server = OpenAIRealtimeRelay()