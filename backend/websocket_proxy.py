"""WebSocket proxy for ElevenLabs to bypass browser security restrictions"""

import asyncio
import websockets
import json
import logging
from fastapi import WebSocket as FastAPIWebSocket, WebSocketDisconnect
import httpx
import os

logger = logging.getLogger(__name__)

class ElevenLabsWebSocketProxy:
    """Proxy WebSocket connections to ElevenLabs"""
    
    def __init__(self):
        self.api_key = os.environ.get("ELEVENLABS_API_KEY")
        self.agent_id = os.environ.get("ELEVENLABS_AGENT_ID")
    
    async def get_signed_url(self, agent_id=None):
        """Get signed URL from ElevenLabs"""
        resolved_agent_id = agent_id or self.agent_id
        url = f"https://api.elevenlabs.io/v1/convai/conversation/get-signed-url?agent_id={resolved_agent_id}"
        headers = {"xi-api-key": self.api_key}
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=15.0)
            resp.raise_for_status()
            data = resp.json()
            return data.get("signed_url")
    
    async def proxy_connection(self, client_ws: FastAPIWebSocket, agent_id=None):
        """Proxy WebSocket messages between client and ElevenLabs"""
        elevenlabs_ws = None
        
        try:
            # Accept client connection
            await client_ws.accept()
            logger.info("Client WebSocket accepted")
            
            # Get signed URL and connect to ElevenLabs
            signed_url = await self.get_signed_url(agent_id)
            logger.info(f"Got signed URL: {signed_url[:100]}...")
            
            # Connect to ElevenLabs WebSocket
            elevenlabs_ws = await websockets.connect(signed_url)
            logger.info("Connected to ElevenLabs WebSocket")
            
            # Create tasks for bidirectional message forwarding
            client_to_elevenlabs = asyncio.create_task(
                self.forward_messages(client_ws, elevenlabs_ws, "client->elevenlabs")
            )
            elevenlabs_to_client = asyncio.create_task(
                self.forward_messages_reverse(elevenlabs_ws, client_ws, "elevenlabs->client")
            )
            
            # Wait for either task to complete (connection closed)
            done, pending = await asyncio.wait(
                [client_to_elevenlabs, elevenlabs_to_client],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            await client_ws.send_json({"error": str(e)})
        
        finally:
            # Clean up connections
            if elevenlabs_ws:
                await elevenlabs_ws.close()
            await client_ws.close()
            logger.info("Proxy connection closed")
    
    async def forward_messages(self, from_ws: FastAPIWebSocket, to_ws: websockets.WebSocketClientProtocol, direction: str):
        """Forward messages from FastAPI WebSocket to websockets client"""
        try:
            while True:
                # Receive from FastAPI WebSocket
                data = await from_ws.receive_text()
                logger.debug(f"{direction}: {data[:200]}...")
                
                # Send to websockets client
                await to_ws.send(data)
                
        except WebSocketDisconnect:
            logger.info(f"{direction}: Client disconnected")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"{direction}: ElevenLabs disconnected")
        except Exception as e:
            logger.error(f"{direction} error: {e}")
    
    async def forward_messages_reverse(self, from_ws: websockets.WebSocketClientProtocol, to_ws: FastAPIWebSocket, direction: str):
        """Forward messages from websockets client to FastAPI WebSocket"""
        try:
            async for message in from_ws:
                logger.debug(f"{direction}: {message[:200] if isinstance(message, str) else 'binary'}...")
                
                # Send to FastAPI WebSocket
                if isinstance(message, str):
                    await to_ws.send_text(message)
                else:
                    await to_ws.send_bytes(message)
                    
        except WebSocketDisconnect:
            logger.info(f"{direction}: Client disconnected")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"{direction}: ElevenLabs disconnected")
        except Exception as e:
            logger.error(f"{direction} error: {e}")

# Global proxy instance
proxy = ElevenLabsWebSocketProxy()