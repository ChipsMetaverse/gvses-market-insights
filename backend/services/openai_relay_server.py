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
# NO TOOL IMPORTS - Voice interface only

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
            logger.error("❌ OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Log API key info (masked for security)
        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
        logger.info(f"🔑 OpenAI API key loaded: {masked_key}")
        
        self.openai_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-realtime-preview-2024-12-17"
        # NO TOOLS - Realtime API is voice-only, agent handles all tools
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
            
            try:
                # Note: OpenAI Realtime API doesn't use WebSocket subprotocols
                openai_ws = await websockets.connect(
                    url_with_model,
                    extra_headers=headers
                )
            except websockets.exceptions.InvalidStatusCode as e:
                logger.error(f"❌ OpenAI WebSocket connection rejected with status {e.status_code}")
                if e.status_code == 401:
                    logger.error("🔑 Authentication failed - check OPENAI_API_KEY is valid")
                    error_msg = {"type": "error", "error": {"message": "Authentication failed - invalid API key", "type": "auth_error"}}
                elif e.status_code == 403:
                    logger.error("🚫 Forbidden - API key may lack realtime permissions")
                    error_msg = {"type": "error", "error": {"message": "API key lacks realtime permissions", "type": "auth_error"}}
                else:
                    error_msg = {"type": "error", "error": {"message": f"Connection rejected with status {e.status_code}", "type": "connection_error"}}
                logger.error(f"Response headers: {e.headers}")
                await websocket.send_json(error_msg)
                await websocket.close(code=1008, reason="Policy violation")
                return
            except Exception as e:
                logger.error(f"❌ Failed to connect to OpenAI: {type(e).__name__}: {e}")
                error_msg = {"type": "error", "error": {"message": f"Connection failed: {str(e)}", "type": "connection_error"}}
                await websocket.send_json(error_msg)
                await websocket.close(code=1011, reason="Server error")
                return
            
            logger.info(f"Relay connection established for session {session_id}")
            
            # Store session info - NO TOOLS (voice-only)
            self.active_sessions[session_id] = {
                "websocket": websocket,
                "openai_ws": openai_ws,
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
        """Configure the OpenAI session for voice-only interaction (no tools)."""
        
        # NO TOOLS - Voice interface only
        # The agent orchestrator handles all tool execution
        tools = []
        
        # Voice-only instructions - just transcribe and speak what's provided
        instructions = "You are a voice interface only. Transcribe user speech accurately. Only speak text that is explicitly provided to you. Do not generate responses, answer questions, or call tools."
        
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
                # Voice-only configuration - no turn detection to avoid server errors
                # Combined with empty tools and tool_choice: "none", this enforces voice-only I/O
                "tools": [],  # Explicitly empty
                "tool_choice": "none",  # CRITICAL: Disable tool usage
                "temperature": 0.6,  # Minimum allowed temperature for OpenAI Realtime API
                "max_response_output_tokens": 10  # Absolute minimum - we don't want any generated text
            }
        }
        
        await openai_ws.send(json.dumps(session_config))
    
    def _get_fallback_instructions(self) -> str:
        """Get fallback instructions for voice-only interface."""
        return """You are a voice interface assistant. Your role is to:

1. Convert speech to text accurately
2. Relay user queries clearly 
3. Speak responses naturally

Voice Guidelines:
- Keep responses natural and conversational
- Use clear speech patterns for numbers (e.g., "two hundred thirty" not "230")
- Speak at a moderate pace for clarity
- Acknowledge when you receive input

IMPORTANT: You are ONLY a voice interface. You do not execute tools or analyze data.
All intelligence and tool execution is handled by the separate agent system."""
    
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
                    
        except WebSocketDisconnect as e:
            # Log close code and reason for debugging
            code = getattr(e, 'code', 'unknown')
            reason = getattr(e, 'reason', 'no reason provided')
            logger.info(f"📱 Client WebSocket closed for session {session_id} - Code: {code}, Reason: {reason}")
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
                    
                    # NO TOOL HANDLING - Just forward all messages
                    # Tools are handled by the agent orchestrator
                    await frontend_ws.send_json(data)
                        
                elif isinstance(message, bytes):
                    # Binary audio data from OpenAI
                    await frontend_ws.send_bytes(message)
                    
        except websockets.exceptions.ConnectionClosed as e:
            # Log close code and reason for debugging
            logger.info(f"🔌 OpenAI WebSocket closed for session {session_id} - Code: {e.code}, Reason: {e.reason}")
        except Exception as e:
            logger.error(f"Error relaying OpenAI to frontend for session {session_id}: {e}")
    
    # REMOVED: _handle_function_call method
    # Tools are NOT handled by Realtime API - voice interface only
    # The agent orchestrator handles all tool execution
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an active session."""
        return self.active_sessions.get(session_id)
    
    async def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active relay sessions."""
        return {
            session_id: {
                "session_id": session_id,
                "connection_active": True,
                "voice_only": True  # This is now a voice-only interface
            }
            for session_id, session in self.active_sessions.items()
        }
    
    async def send_tts_to_session(self, session_id: str, text: str) -> bool:
        """
        Send text to a specific session for TTS output.
        Used by the agent orchestrator to speak responses.
        
        Args:
            session_id: The session to send TTS to
            text: The text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = self.active_sessions.get(session_id)
            if not session or not session.get("openai_ws"):
                logger.error(f"Session {session_id} not found or not connected")
                return False
            
            openai_ws = session["openai_ws"]
            
            # Create a conversation item with the text to speak
            tts_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "assistant",
                    "content": [
                        {"type": "input_text", "text": text}
                    ]
                }
            }
            
            await openai_ws.send(json.dumps(tts_message))
            
            # Request audio response
            response_request = {
                "type": "response.create",
                "response": {
                    "modalities": ["audio"],  # Audio only for TTS
                    "instructions": "Speak this message clearly and naturally."
                }
            }
            
            await openai_ws.send(json.dumps(response_request))
            
            logger.info(f"TTS request sent to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending TTS to session {session_id}: {e}")
            return False

# Create singleton instance
openai_relay_server = OpenAIRealtimeRelay()
