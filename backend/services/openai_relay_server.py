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
import time
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
            logger.warning("⚠️ OPENAI_API_KEY not found - OpenAI Realtime features will be disabled")
            self.api_key = "test-key"  # Use dummy key for CI environments

        # Log API key info (masked for security)
        masked_key = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
        logger.info(f"🔑 OpenAI API key loaded: {masked_key}")

        # Use conversational Realtime API (GA) with transcription support
        self.openai_url = "wss://api.openai.com/v1/realtime"
        # GA model - configurable via environment variable
        self.model = os.getenv("OPENAI_REALTIME_MODEL", "gpt-realtime")
        # NO TOOLS - Realtime API is voice-only, agent handles all tools

        # Thread-safe session management
        self.active_sessions = {}  # Track active sessions
        self.session_lock = asyncio.Lock()  # Protect concurrent access

        # Configurable limits for performance and stability
        self.max_concurrent_sessions = int(os.getenv("MAX_CONCURRENT_SESSIONS", "10"))  # Limit concurrent sessions
        self.session_timeout = int(os.getenv("SESSION_TIMEOUT_SECONDS", "300"))  # 5 minute timeout
        self.activity_timeout = int(os.getenv("ACTIVITY_TIMEOUT_SECONDS", "60"))  # 1 minute of inactivity
        self.cleanup_interval = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "60"))  # Cleanup every minute

        # Logging configuration
        self.enable_detailed_logging = os.getenv("VOICE_DEBUG", "false").lower() == "true"
        
        # Metrics tracking
        self.metrics = {
            "sessions_created": 0,
            "sessions_closed": 0,
            "sessions_rejected": 0,
            "sessions_timed_out": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "tts_requests": 0,
            "tts_failures": 0,
            "cleanup_runs": 0,
            "start_time": time.time()
        }
        self.metrics_lock = asyncio.Lock()

        logger.info(f"🔧 OpenAI Relay Config: max_sessions={self.max_concurrent_sessions}, timeout={self.session_timeout}s")

        # Initialize cleanup task placeholder (will start when event loop is available)
        self.cleanup_task = None

    async def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)  # Configurable cleanup interval

                async with self.session_lock:
                    current_time = asyncio.get_event_loop().time()
                    expired_sessions = []

                    for session_id, session_data in self.active_sessions.items():
                        # Check if session has expired or connections are dead
                        if current_time - session_data.get("created_at", current_time) > self.session_timeout:
                            expired_sessions.append(session_id)
                        elif current_time - session_data.get("last_activity", current_time) > self.activity_timeout:
                            expired_sessions.append(session_id)
                        else:
                            # Check connection states more safely
                            try:
                                if session_data.get("websocket") and hasattr(session_data["websocket"], 'client_state'):
                                    if session_data["websocket"].client_state != "CONNECTED":
                                        expired_sessions.append(session_id)
                            except:
                                # Connection check failed, mark as expired
                                expired_sessions.append(session_id)

                            try:
                                if session_data.get("openai_ws") and hasattr(session_data["openai_ws"], 'closed'):
                                    if session_data["openai_ws"].closed:
                                        expired_sessions.append(session_id)
                            except:
                                # Connection check failed, mark as expired
                                expired_sessions.append(session_id)

                    # Clean up expired sessions
                    for session_id in expired_sessions:
                        if session_id in self.active_sessions:
                            session_data = self.active_sessions[session_id]
                            logger.info(f"🧹 Cleaning up expired session {session_id}")

                            # Close connections
                            try:
                                if session_data.get("websocket"):
                                    await session_data["websocket"].close(code=1000, reason="Session expired")
                            except:
                                pass

                            try:
                                if session_data.get("openai_ws"):
                                    await session_data["openai_ws"].close()
                            except:
                                pass

                            del self.active_sessions[session_id]
                            
                            # Update metrics
                            async with self.metrics_lock:
                                self.metrics["sessions_closed"] += 1
                                self.metrics["sessions_timed_out"] += 1

                    if expired_sessions:
                        logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
                        async with self.metrics_lock:
                            self.metrics["cleanup_runs"] += 1

            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(60)  # Continue on error

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
        
        # Start cleanup task if not already running (lazy initialization)
        if self.cleanup_task is None:
            try:
                self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
                logger.info("Started cleanup task for expired sessions")
            except RuntimeError:
                pass  # Event loop not available, will try again later
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

        # Check concurrent session limit
        async with self.session_lock:
            if len(self.active_sessions) >= self.max_concurrent_sessions:
                logger.warning(f"🚫 Rejecting connection {session_id} - max concurrent sessions ({self.max_concurrent_sessions}) reached")
                async with self.metrics_lock:
                    self.metrics["sessions_rejected"] += 1
                await websocket.send_json({
                    "type": "error",
                    "error": {
                        "message": f"Maximum concurrent sessions ({self.max_concurrent_sessions}) reached. Please try again later.",
                        "type": "rate_limit_error"
                    }
                })
                await websocket.close(code=1013, reason="Too many concurrent sessions")
                return

        try:
            # Connect to OpenAI Transcription WebSocket (GA)
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }

            # Add model parameter to URL
            url_with_model = f"{self.openai_url}?model={self.model}"

            try:
                # websockets 13.0+ uses additional_headers parameter
                openai_ws = await websockets.connect(
                    url_with_model,
                    additional_headers=headers
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
                logger.error(f"   Note: OpenAI Realtime API requires beta access. Check https://platform.openai.com/settings")
                error_msg = {
                    "type": "error",
                    "error": {
                        "message": f"Connection failed: {str(e)}. OpenAI Realtime API requires beta access.",
                        "type": "connection_error",
                        "help": "Visit https://platform.openai.com/settings to request access"
                    }
                }
                await websocket.send_json(error_msg)
                await websocket.close(code=1011, reason="OpenAI connection failed")
                return
            
            logger.info(f"✅ OpenAI Realtime connection established for session {session_id}")
            logger.info(f"   Model: {self.model}")
            logger.info(f"   WebSocket connected successfully")

            # Store session info with timestamp
            current_time = asyncio.get_event_loop().time()
            async with self.session_lock:
                self.active_sessions[session_id] = {
                    "websocket": websocket,
                    "openai_ws": openai_ws,
                    "session_configured": False,
                    "created_at": current_time,
                    "last_activity": current_time
                }
                async with self.metrics_lock:
                    self.metrics["sessions_created"] += 1

            logger.info(f"Starting bidirectional relay for session {session_id}")
            
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
            # Clean up session with proper locking
            async with self.session_lock:
                if session_id in self.active_sessions:
                    logger.info(f"🧹 Cleaning up session {session_id} on disconnect")
                    session_data = self.active_sessions[session_id]

                    # Close connections
                    try:
                        if session_data.get("websocket"):
                            await session_data["websocket"].close(code=1000, reason="Session ended")
                    except:
                        pass

                    try:
                        if session_data.get("openai_ws"):
                            await session_data["openai_ws"].close()
                    except:
                        pass

                    del self.active_sessions[session_id]

            logger.info(f"Relay connection closed for session {session_id}")

    async def shutdown(self):
        """Clean shutdown of the relay server."""
        logger.info("🛑 Shutting down OpenAI Realtime Relay Server")

        # Cancel cleanup task if it was started
        if getattr(self, "cleanup_task", None):
            if not self.cleanup_task.done():
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass

        # Clean up all active sessions
        async with self.session_lock:
            session_ids = list(self.active_sessions.keys())
            for session_id in session_ids:
                logger.info(f"🧹 Force cleaning up session {session_id} on shutdown")
                session_data = self.active_sessions[session_id]

                # Close connections
                try:
                    if session_data.get("websocket"):
                        await session_data["websocket"].close(code=1001, reason="Server shutting down")
                except:
                    pass

                try:
                    if session_data.get("openai_ws"):
                        await session_data["openai_ws"].close()
                except:
                    pass

                del self.active_sessions[session_id]

        logger.info("✅ OpenAI Realtime Relay Server shutdown complete")

    async def _configure_session(self, openai_ws: WebSocketClientProtocol):
        """Configure OpenAI Realtime session for passive voice I/O (GA API format)."""

        # STRICT passive-only instructions: NO autonomous responses, ONLY transcription
        instructions = """You are a passive voice bridge.

Primary responsibilities:
1. Convert incoming speech to text accurately.
2. Relay agent-provided text back as spoken audio when prompted.

Do NOT initiate responses, small talk, or tool calls. Stay silent unless text-to-speech content is explicitly provided."""

        # GA (General Availability) OpenAI Realtime API configuration
        session_config = {
            "type": "session.update",
            "session": {
                "type": "realtime",
                "model": self.model,
                "instructions": instructions,
                "audio": {
                    "input": {
                        "format": {"type": "audio/pcm", "rate": 24000},
                        "transcription": {"model": "whisper-1"},
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.5,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 500
                        }
                    },
                    "output": {
                        "format": {"type": "audio/pcm", "rate": 24000},
                        "voice": "alloy"
                    }
                },
                "tools": []
            }
        }

        await openai_ws.send(json.dumps(session_config))

        logger.info("✅ GA OpenAI config applied with server_vad for automatic speech-end detection")
    
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
                
                # Forward message to OpenAI (with filtering)
                if "text" in data:
                    # JSON message from RealtimeClient
                    # Filter out client-originated session.update events
                    # The relay server handles all session configuration
                    try:
                        message = json.loads(data["text"])
                        if message.get("type") == "session.update":
                            logger.info(f"🚫 Blocked client session.update for session {session_id} - relay handles session config")
                            continue
                    except json.JSONDecodeError:
                        pass  # Not JSON, forward as-is

                    await openai_ws.send(data["text"])
                elif "bytes" in data:
                    # Binary audio data
                    await openai_ws.send(data["bytes"])

                # Update activity timestamp for any frontend activity
                async with self.session_lock:
                    if session_id in self.active_sessions:
                        self.active_sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()
                    
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
        """Relay messages from OpenAI API to RealtimeClient with session configuration."""
        try:
            async for message in openai_ws:
                if isinstance(message, str):
                    # JSON message from OpenAI
                    data = json.loads(message)

                    # Configure session when we see session.created
                    if data.get("type") == "session.created" and not self.active_sessions[session_id]["session_configured"]:
                        logger.info(f"📡 Received session.created for session {session_id}, configuring...")
                        # Forward session.created to frontend first
                        await frontend_ws.send_json(data)
                        # Then configure the session
                        await self._configure_session(openai_ws)
                        self.active_sessions[session_id]["session_configured"] = True
                        logger.info(f"✅ Session configured for {session_id}")
                    else:
                        # Forward all other messages normally
                        await frontend_ws.send_json(data)

                    # Update activity timestamp
                    async with self.session_lock:
                        if session_id in self.active_sessions:
                            self.active_sessions[session_id]["last_activity"] = asyncio.get_event_loop().time()

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
        """Get all active relay sessions with detailed status."""
        current_time = asyncio.get_event_loop().time()
        return {
            session_id: {
                "session_id": session_id,
                "connection_active": True,
                "voice_only": True,  # This is now a voice-only interface
                "session_configured": session.get("session_configured", False),
                "created_at": session.get("created_at", current_time),
                "last_activity": session.get("last_activity", current_time),
                "websocket_connected": session.get("websocket") is not None,
                "openai_connected": session.get("openai_ws") is not None,
                "idle_seconds": current_time - session.get("last_activity", current_time)
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
            
            # Request audio response (GA format)
            response_request = {
                "type": "response.create",
                "response": {
                    "output_modalities": ["audio"],  # GA parameter name
                    "instructions": "Speak this message clearly and naturally.",
                    "conversation": "none"  # Don't append GPT's response to conversation
                }
            }
            
            await openai_ws.send(json.dumps(response_request))
            
            logger.info(f"TTS request sent to session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending TTS to session {session_id}: {e}")
            async with self.metrics_lock:
                self.metrics["tts_failures"] += 1
                self.metrics["errors"] += 1
            return {"success": False, "error": str(e)}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        async with self.metrics_lock:
            uptime = time.time() - self.metrics["start_time"]
            return {
                **self.metrics,
                "uptime_seconds": uptime,
                "uptime_formatted": f"{uptime/3600:.1f} hours",
                "current_sessions": len(self.active_sessions),
                "session_utilization": f"{len(self.active_sessions)}/{self.max_concurrent_sessions}"
            }
    
    def _reset_metrics(self) -> None:
        """Reset metrics (internal use for testing)."""
        self.metrics = {
            "sessions_created": 0,
            "sessions_closed": 0,
            "sessions_rejected": 0,
            "sessions_timed_out": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "tts_requests": 0,
            "tts_failures": 0,
            "cleanup_runs": 0,
            "start_time": time.time()
        }
        logger.info("Metrics reset")
    
    def get_metrics_sync(self) -> Dict[str, Any]:
        """Synchronous version of get_metrics for non-async contexts."""
        uptime = time.time() - self.metrics["start_time"]
        return {
            **self.metrics,
            "uptime_seconds": uptime,
            "uptime_formatted": f"{uptime/3600:.1f} hours",
            "current_sessions": len(self.active_sessions),
            "session_utilization": f"{len(self.active_sessions)}/{self.max_concurrent_sessions}"
        }

# Create singleton instance
try:
    openai_relay_server = OpenAIRealtimeRelay()
except Exception as e:
    logger.error(f"Failed to initialize OpenAI Relay Server: {e}")
    openai_relay_server = None
