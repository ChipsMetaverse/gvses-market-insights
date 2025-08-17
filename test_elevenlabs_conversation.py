#!/usr/bin/env python3
"""
Test ElevenLabs conversation flow via backend signed URL.
This validates the end-to-end conversational path without microphone input.

Usage:
    python test_elevenlabs_conversation.py "What's the price of AAPL?"
"""

import asyncio
import json
import sys
import time
from typing import Optional
import aiohttp
import websockets


class ElevenLabsConversationTester:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.agent_response_received = False
        self.user_transcript = None
        self.audio_chunks_count = 0
        self.errors = []
        
    async def get_signed_url(self) -> str:
        """Fetch signed WebSocket URL from backend."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/elevenlabs/signed-url") as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to get signed URL: {resp.status}")
                data = await resp.json()
                signed_url = data.get("signed_url")
                if not signed_url:
                    raise Exception("No signed_url in response")
                print(f"✓ Got signed URL from backend")
                return signed_url
    
    async def test_conversation(self, message: str, timeout: int = 30) -> bool:
        """Test sending a message and receiving a response."""
        print(f"\n🎤 Testing ElevenLabs conversation...")
        print(f"📝 Message: '{message}'")
        
        try:
            # Get signed URL
            signed_url = await self.get_signed_url()
            
            # Connect to ElevenLabs WebSocket
            print(f"🔌 Connecting to ElevenLabs WebSocket...")
            async with websockets.connect(signed_url) as websocket:
                print(f"✓ Connected to ElevenLabs")
                
                # Send proper initialization with conversation config
                init_msg = json.dumps({
                    "type": "conversation_initiation_client_data",
                    "conversation_config_override": {
                        "agent": {
                            "language": "en"
                        }
                    }
                })
                await websocket.send(init_msg)
                print(f"✓ Sent initialization with config")
                
                # Wait for initialization response
                init_response_received = False
                timeout_start = time.time()
                while not init_response_received and time.time() - timeout_start < 5:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        if data.get("type") == "conversation_initiation_metadata":
                            print(f"✓ Received initialization metadata")
                            init_response_received = True
                    except asyncio.TimeoutError:
                        continue
                
                if not init_response_received:
                    print(f"⚠️ No initialization metadata received, continuing anyway...")
                
                await asyncio.sleep(0.2)
                
                # Send user message (corrected format)
                user_msg = json.dumps({
                    "type": "user_message",
                    "text": message
                })
                await websocket.send(user_msg)
                print(f"✓ Sent user message: '{message}'")
                
                # Listen for response
                start_time = time.time()
                print(f"\n⏳ Waiting for agent response (timeout: {timeout}s)...")
                
                while time.time() - start_time < timeout:
                    try:
                        # Wait for message with timeout
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        
                        # Handle different message types
                        msg_type = data.get("type")
                        
                        # Debug: log all message types and content
                        if msg_type not in ["ping"]:
                            if msg_type == "audio":
                                print(f"📨 Received: audio chunk #{self.audio_chunks_count + 1}")
                            else:
                                print(f"📨 Received: {msg_type}")
                                if msg_type not in ["conversation_initiation_metadata"]:
                                    print(f"   Data: {json.dumps(data, indent=2)[:500]}")
                        
                        if msg_type == "conversation_initiation_metadata":
                            print(f"🎬 Conversation initialized")
                        elif msg_type == "agent_response":
                            agent_text = data.get("agent_response_event", {}).get("agent_response")
                            if agent_text:
                                print(f"\n✅ AGENT RESPONSE: '{agent_text}'")
                                self.agent_response_received = True
                                # Continue listening for a bit more to get audio
                                
                        elif msg_type == "agent_response_correction":
                            corrected = data.get("agent_response_correction_event", {}).get("corrected_agent_response")
                            if corrected:
                                print(f"📝 Agent correction: '{corrected}'")
                                self.agent_response_received = True
                                
                        elif msg_type == "user_transcript":
                            transcript = data.get("user_transcription_event", {}).get("user_transcript")
                            if transcript:
                                print(f"🎯 User transcript: '{transcript}'")
                                self.user_transcript = transcript
                                
                        elif msg_type == "audio":
                            self.audio_chunks_count += 1
                            if self.audio_chunks_count == 1:
                                print(f"🔊 Receiving audio chunks...")
                            elif self.audio_chunks_count % 10 == 0:
                                print(f"   ... {self.audio_chunks_count} chunks received")
                                
                        elif msg_type == "ping":
                            # Respond to ping
                            event_id = data.get("ping_event", {}).get("event_id")
                            pong_msg = json.dumps({
                                "type": "pong",
                                "event_id": event_id
                            })
                            await websocket.send(pong_msg)
                            print(f"🏓 Responded to ping")
                            
                        elif msg_type == "interruption":
                            reason = data.get("interruption_event", {}).get("reason")
                            print(f"⚠️ Interruption: {reason}")
                            
                        elif msg_type == "error":
                            error = data.get("error", {})
                            print(f"❌ Error: {error}")
                            self.errors.append(error)
                            
                        # If we got a response and some audio, we can consider it successful
                        if self.agent_response_received and self.audio_chunks_count > 5:
                            print(f"\n✅ Test successful! Received response and {self.audio_chunks_count} audio chunks")
                            return True
                            
                    except asyncio.TimeoutError:
                        # Check if we should continue waiting
                        if self.agent_response_received:
                            print(f"\n✅ Test successful! Received response and {self.audio_chunks_count} audio chunks")
                            return True
                        continue
                    except Exception as e:
                        print(f"❌ Error receiving message: {e}")
                        continue
                
                # Timeout reached
                if self.agent_response_received:
                    print(f"\n✅ Test successful! Received response and {self.audio_chunks_count} audio chunks")
                    return True
                else:
                    print(f"\n❌ Timeout: No agent response received after {timeout} seconds")
                    return False
                    
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n📊 Test Summary:")
        print(f"  - Agent responded: {'✅ Yes' if self.agent_response_received else '❌ No'}")
        print(f"  - User transcript: {self.user_transcript or 'None'}")
        print(f"  - Audio chunks: {self.audio_chunks_count}")
        print(f"  - Errors: {len(self.errors)}")
        if self.errors:
            for error in self.errors:
                print(f"    - {error}")


async def main():
    # Get message from command line or use default
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = "What's the current price of Apple stock?"
    
    # Create tester
    tester = ElevenLabsConversationTester()
    
    # Run test
    success = await tester.test_conversation(message)
    
    # Print summary
    tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    print("🚀 ElevenLabs Conversation Test")
    print("=" * 50)
    asyncio.run(main())