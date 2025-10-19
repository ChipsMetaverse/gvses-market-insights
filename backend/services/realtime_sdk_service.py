"""
OpenAI Realtime SDK Service
============================

Integrates OpenAI Realtime API with Agents SDK workflow for end-to-end voice processing.

This service:
- Manages WebSocket connections to OpenAI Realtime API
- Routes audio through Agent Builder workflow
- Handles tool calls asynchronously
- Streams audio responses back to frontend

Benefits (from research.md):
- Lower latency (audio-in to audio-out through single model)
- More fluid dialogue (no STT→LLM→TTS gaps)
- Asynchronous tool calling ("Let me check that..." while processing)
- Natural conversation flow
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional, AsyncGenerator
import websockets
from datetime import datetime

logger = logging.getLogger(__name__)


class RealtimeSDKService:
    """
    Service for OpenAI Realtime API + Agents SDK integration.
    
    This handles the WebSocket connection to OpenAI's Realtime API and
    integrates it with the Agent Builder workflow for intelligent voice responses.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        
        self.realtime_api_url = "wss://api.openai.com/v1/realtime"
        self.model = "gpt-4o-realtime-preview-2024-12-17"
        
        # Active sessions
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_lock = asyncio.Lock()
        
        logger.info("🎙️ [Realtime SDK] Service initialized")
    
    async def create_session(
        self,
        workflow_id: str,
        voice: str = "marin",
        session_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a new Realtime API session configured with Agent Builder workflow.
        
        Args:
            workflow_id: Agent Builder workflow ID
            voice: Voice to use (marin, cedar, ash, etc.)
            session_id: Optional session ID (generated if not provided)
        
        Returns:
            dict with session_id and ephemeral token
        """
        if not session_id:
            session_id = f"rtc_{int(time.time() * 1000)}"
        
        async with self.session_lock:
            # Create session configuration
            session_config = {
                "session_id": session_id,
                "workflow_id": workflow_id,
                "voice": voice,
                "model": self.model,
                "created_at": datetime.utcnow().isoformat(),
                "status": "initializing"
            }
            
            self.active_sessions[session_id] = session_config
            logger.info(f"🎙️ [Realtime SDK] Session created: {session_id}")
        
        # Generate ephemeral token (in production, this would be from OpenAI)
        # For now, we'll use the API key directly in the backend connection
        return {
            "session_id": session_id,
            "token": "ephemeral_token_placeholder"  # Backend will use real API key
        }
    
    async def handle_realtime_session(
        self,
        session_id: str,
        client_ws: Any  # WebSocket connection from frontend
    ) -> None:
        """
        Handle bidirectional streaming between frontend and OpenAI Realtime API.
        
        This creates a relay:
        Frontend <-> Backend (this) <-> OpenAI Realtime API
        
        The backend can intercept messages to:
        - Log events
        - Handle tool calls via Agent Builder workflow
        - Apply guardrails
        """
        session = self.active_sessions.get(session_id)
        if not session:
            logger.error(f"❌ [Realtime SDK] Session not found: {session_id}")
            await client_ws.send(json.dumps({
                "type": "error",
                "error": {"message": "Session not found"}
            }))
            return
        
        try:
            # Connect to OpenAI Realtime API
            openai_ws = await websockets.connect(
                f"{self.realtime_api_url}?model={self.model}",
                extra_headers={
                    "Authorization": f"Bearer {self.openai_api_key}",
                    "OpenAI-Beta": "realtime=v1"
                }
            )
            
            logger.info(f"🔌 [Realtime SDK] Connected to OpenAI for session {session_id}")
            
            # Configure session with Agent Builder workflow
            await self._configure_session(openai_ws, session)
            
            # Bidirectional relay
            await asyncio.gather(
                self._relay_frontend_to_openai(client_ws, openai_ws, session_id),
                self._relay_openai_to_frontend(openai_ws, client_ws, session_id)
            )
            
        except Exception as e:
            logger.error(f"❌ [Realtime SDK] Session error: {e}")
            await client_ws.send(json.dumps({
                "type": "error",
                "error": {"message": str(e)}
            }))
        finally:
            # Cleanup
            async with self.session_lock:
                if session_id in self.active_sessions:
                    del self.active_sessions[session_id]
            logger.info(f"🔌 [Realtime SDK] Session closed: {session_id}")
    
    async def _configure_session(
        self,
        openai_ws: Any,
        session: Dict[str, Any]
    ) -> None:
        """
        Configure the Realtime API session with Agent Builder workflow settings.
        
        This sets:
        - Voice model and instructions
        - Tool definitions (from Agent Builder workflow)
        - Turn detection settings
        - Audio format preferences
        """
        # Build system instructions from workflow
        instructions = self._build_workflow_instructions(session["workflow_id"])
        
        # Get tool definitions from Agent Builder workflow
        tools = await self._get_workflow_tools(session["workflow_id"])
        
        # Session configuration
        config = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": instructions,
                "voice": session["voice"],
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
        
        await openai_ws.send(json.dumps(config))
        logger.info(f"⚙️ [Realtime SDK] Session configured with workflow {session['workflow_id']}")
    
    def _build_workflow_instructions(self, workflow_id: str) -> str:
        """
        Build system instructions based on Agent Builder workflow.
        
        This creates the prompt that guides the voice model's behavior,
        incorporating the workflow's intent classification and routing logic.
        """
        return """You are a professional trading and market analysis assistant with real-time voice capabilities.

Your workflow:
1. Listen carefully to the user's query
2. Classify the intent (educational, market_data, general, chart_command)
3. Use appropriate tools to fetch market data when needed
4. Provide clear, conversational responses suitable for voice

Guidelines:
- Be concise but informative
- Use natural conversational language
- When fetching data, say "Let me check that for you..." to maintain engagement
- Clearly state stock prices, changes, and important metrics
- For chart commands, execute them and confirm the action
- For educational queries, explain concepts clearly without jargon

Always maintain a professional yet friendly tone, as if speaking to a colleague."""
    
    async def _get_workflow_tools(self, workflow_id: str) -> list:
        """
        Get tool definitions from Agent Builder workflow.
        
        In production, this would query the Agent Builder API.
        For now, we'll return the core trading tools.
        """
        # Import tools from agents_sdk_service
        from services.agents_sdk_service import agents_sdk_service
        
        # Get MCP tool schemas
        tools = []
        for tool_name in agents_sdk_service.available_tools:
            tool_schema = agents_sdk_service._get_tool_schema(tool_name)
            if tool_schema:
                tools.append({
                    "type": "function",
                    "name": tool_name,
                    "description": tool_schema.get("description", ""),
                    "parameters": tool_schema.get("parameters", {})
                })
        
        logger.info(f"🔧 [Realtime SDK] Loaded {len(tools)} tools for workflow")
        return tools
    
    async def _relay_frontend_to_openai(
        self,
        client_ws: Any,
        openai_ws: Any,
        session_id: str
    ) -> None:
        """
        Relay messages from frontend to OpenAI Realtime API.
        """
        try:
            async for message in client_ws:
                data = json.loads(message) if isinstance(message, str) else message
                
                # Log significant events
                if data.get("type") in ["input_audio_buffer.append", "conversation.item.create"]:
                    logger.debug(f"📤 [Realtime SDK] Frontend → OpenAI: {data.get('type')}")
                
                # Forward to OpenAI
                await openai_ws.send(json.dumps(data))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 [Realtime SDK] Frontend connection closed: {session_id}")
        except Exception as e:
            logger.error(f"❌ [Realtime SDK] Frontend relay error: {e}")
    
    async def _relay_openai_to_frontend(
        self,
        openai_ws: Any,
        client_ws: Any,
        session_id: str
    ) -> None:
        """
        Relay messages from OpenAI Realtime API to frontend.
        
        This can intercept and process certain events:
        - Tool calls: Execute via Agent Builder workflow
        - Transcripts: Log for analytics
        - Errors: Handle gracefully
        """
        try:
            async for message in openai_ws:
                data = json.loads(message) if isinstance(message, str) else message
                
                # Log significant events
                msg_type = data.get("type", "")
                if msg_type in ["conversation.item.input_audio_transcription.completed",
                               "response.audio.delta",
                               "response.function_call_arguments.done"]:
                    logger.debug(f"📥 [Realtime SDK] OpenAI → Frontend: {msg_type}")
                
                # Handle tool calls
                if msg_type == "response.function_call_arguments.done":
                    await self._handle_tool_call(data, openai_ws, session_id)
                
                # Forward to frontend
                await client_ws.send(json.dumps(data))
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 [Realtime SDK] OpenAI connection closed: {session_id}")
        except Exception as e:
            logger.error(f"❌ [Realtime SDK] OpenAI relay error: {e}")
    
    async def _handle_tool_call(
        self,
        tool_call_data: Dict[str, Any],
        openai_ws: Any,
        session_id: str
    ) -> None:
        """
        Handle tool call from Realtime API via Agent Builder workflow.
        
        This executes the tool and sends the result back to OpenAI,
        which will incorporate it into the voice response.
        """
        call_id = tool_call_data.get("call_id")
        function_name = tool_call_data.get("name")
        arguments = json.loads(tool_call_data.get("arguments", "{}"))
        
        logger.info(f"🔧 [Realtime SDK] Tool call: {function_name} with {arguments}")
        
        try:
            # Execute tool via agents_sdk_service
            from services.agents_sdk_service import agents_sdk_service
            
            # Call the MCP tool
            result = await agents_sdk_service._call_mcp_tool_directly(
                function_name,
                arguments
            )
            
            # Send result back to OpenAI
            response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result)
                }
            }
            
            await openai_ws.send(json.dumps(response))
            
            # Trigger response generation with tool result
            await openai_ws.send(json.dumps({"type": "response.create"}))
            
            logger.info(f"✅ [Realtime SDK] Tool result sent for {function_name}")
            
        except Exception as e:
            logger.error(f"❌ [Realtime SDK] Tool execution failed: {e}")
            
            # Send error back to OpenAI
            error_response = {
                "type": "conversation.item.create",
                "item": {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps({"error": str(e)})
                }
            }
            await openai_ws.send(json.dumps(error_response))
    
    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a session."""
        return self.active_sessions.get(session_id)
    
    async def close_session(self, session_id: str) -> None:
        """Close a session."""
        async with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"🔌 [Realtime SDK] Session manually closed: {session_id}")


# Global instance
realtime_sdk_service = RealtimeSDKService()

