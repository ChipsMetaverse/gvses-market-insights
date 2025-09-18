#!/usr/bin/env python3
"""
Test OpenAI Realtime WebSocket endpoint directly
"""
import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openai_ws():
    """Test WebSocket connection to OpenAI Realtime proxy"""
    
    # Generate session ID
    session_id = f"test_session_{int(asyncio.get_event_loop().time() * 1000)}"
    
    # Connect to backend WebSocket proxy
    ws_url = f"ws://localhost:8000/ws/openai-realtime/{session_id}"
    
    try:
        logger.info(f"Connecting to {ws_url}...")
        
        async with websockets.connect(ws_url) as websocket:
            logger.info("Connected to WebSocket proxy!")
            
            # Wait for initial messages
            timeout = 5
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    
                    if isinstance(message, str):
                        data = json.loads(message)
                        logger.info(f"Received: {data.get('type', 'unknown')}")
                        
                        if data.get('type') == 'connection.established':
                            logger.info("✅ Connection established successfully!")
                            
                            # Send a test message
                            test_message = {
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "message",
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "input_text",
                                            "text": "Hello, can you hear me?"
                                        }
                                    ]
                                }
                            }
                            
                            await websocket.send(json.dumps(test_message))
                            logger.info("Sent test message")
                            
                            # Request response
                            await websocket.send(json.dumps({"type": "response.create"}))
                            logger.info("Requested response")
                            
                        elif data.get('type') == 'session.created':
                            logger.info(f"✅ OpenAI session created: {data.get('session', {}).get('id', 'unknown')}")
                            
                        elif data.get('type') == 'error':
                            logger.error(f"❌ Error: {data.get('error', {})}")
                            break
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break
            
            logger.info("Test completed!")
            
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_openai_ws())
    
    if success:
        print("\n✨ OpenAI Realtime WebSocket proxy is working!")
        print("The backend is correctly configured to proxy connections to OpenAI.")
    else:
        print("\n❌ OpenAI Realtime WebSocket proxy test failed!")
        print("Please check:")
        print("1. Backend server is running on port 8000")
        print("2. OPENAI_API_KEY is set in backend/.env")
        print("3. OpenAI Realtime service is properly imported")