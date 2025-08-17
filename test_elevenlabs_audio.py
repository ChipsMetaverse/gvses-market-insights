#!/usr/bin/env python3
"""
Test ElevenLabs conversation with audio input instead of text.
This tests if the agent responds to voice input.
"""

import asyncio
import json
import base64
import time
import aiohttp
import websockets
import numpy as np


def generate_test_audio():
    """Generate a simple test audio chunk (silence) in PCM format."""
    # Generate 0.5 seconds of silence at 16kHz, 16-bit, mono
    sample_rate = 16000
    duration = 0.5
    samples = int(sample_rate * duration)
    
    # Create silence (zeros)
    audio_data = np.zeros(samples, dtype=np.int16)
    
    # Convert to bytes
    audio_bytes = audio_data.tobytes()
    
    # Encode to base64
    return base64.b64encode(audio_bytes).decode('utf-8')


class ElevenLabsAudioTester:
    def __init__(self, backend_url: str = "http://localhost:8000"):
        self.backend_url = backend_url
        self.agent_response_received = False
        self.user_transcript = None
        self.audio_chunks_count = 0
        
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
    
    async def test_audio_conversation(self) -> bool:
        """Test sending audio and receiving a response."""
        print(f"\n🎤 Testing ElevenLabs audio conversation...")
        
        try:
            # Get signed URL
            signed_url = await self.get_signed_url()
            
            # Connect to ElevenLabs WebSocket
            print(f"🔌 Connecting to ElevenLabs WebSocket...")
            async with websockets.connect(signed_url) as websocket:
                print(f"✓ Connected to ElevenLabs")
                
                # Send initialization
                init_msg = json.dumps({
                    "type": "conversation_initiation_client_data",
                    "conversation_config_override": {
                        "agent": {
                            "language": "en"
                        }
                    }
                })
                await websocket.send(init_msg)
                print(f"✓ Sent initialization")
                
                # Wait for initialization response
                init_received = False
                timeout_start = time.time()
                while not init_received and time.time() - timeout_start < 5:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        if data.get("type") == "conversation_initiation_metadata":
                            print(f"✓ Received initialization metadata")
                            init_received = True
                    except asyncio.TimeoutError:
                        continue
                
                # Send audio chunks (simulating speech)
                print(f"🎵 Sending audio chunks...")
                for i in range(5):  # Send 5 chunks
                    audio_base64 = generate_test_audio()
                    audio_msg = json.dumps({
                        "user_audio_chunk": audio_base64
                    })
                    await websocket.send(audio_msg)
                    print(f"  Sent audio chunk {i+1}/5")
                    await asyncio.sleep(0.1)
                
                # Send silence to trigger end of speech detection
                print(f"🔇 Sending silence to trigger response...")
                for i in range(10):  # Send more silence
                    audio_base64 = generate_test_audio()
                    audio_msg = json.dumps({
                        "user_audio_chunk": audio_base64
                    })
                    await websocket.send(audio_msg)
                    await asyncio.sleep(0.1)
                
                # Listen for response
                print(f"\n⏳ Waiting for agent response...")
                start_time = time.time()
                timeout = 15
                
                while time.time() - start_time < timeout:
                    try:
                        msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(msg)
                        msg_type = data.get("type")
                        
                        if msg_type not in ["ping", "audio"]:
                            print(f"📨 Received: {msg_type}")
                        
                        if msg_type == "agent_response":
                            agent_text = data.get("agent_response_event", {}).get("agent_response")
                            if agent_text:
                                print(f"\n✅ AGENT RESPONSE: '{agent_text}'")
                                self.agent_response_received = True
                                
                        elif msg_type == "user_transcript":
                            transcript = data.get("user_transcription_event", {}).get("user_transcript")
                            if transcript:
                                print(f"🎯 User transcript: '{transcript}'")
                                self.user_transcript = transcript
                                
                        elif msg_type == "audio":
                            self.audio_chunks_count += 1
                            if self.audio_chunks_count == 1:
                                print(f"🔊 Receiving audio response...")
                                
                        elif msg_type == "ping":
                            event_id = data.get("ping_event", {}).get("event_id")
                            pong_msg = json.dumps({
                                "type": "pong",
                                "event_id": event_id
                            })
                            await websocket.send(pong_msg)
                            
                        elif msg_type == "vad_score":
                            score = data.get("vad_score_event", {}).get("score")
                            if score:
                                print(f"🎙️ VAD Score: {score}")
                                
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"Error: {e}")
                        continue
                
                if self.agent_response_received:
                    print(f"\n✅ Test successful!")
                    return True
                else:
                    print(f"\n❌ No agent response received")
                    return False
                    
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False


async def main():
    tester = ElevenLabsAudioTester()
    success = await tester.test_audio_conversation()
    
    print(f"\n📊 Test Summary:")
    print(f"  - Agent responded: {'✅ Yes' if tester.agent_response_received else '❌ No'}")
    print(f"  - User transcript: {tester.user_transcript or 'None'}")
    print(f"  - Audio chunks received: {tester.audio_chunks_count}")
    
    return success


if __name__ == "__main__":
    print("🚀 ElevenLabs Audio Conversation Test")
    print("=" * 50)
    success = asyncio.run(main())
    exit(0 if success else 1)