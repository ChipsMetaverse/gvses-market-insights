#!/usr/bin/env python3
"""
Simple text-only test for ElevenLabs agent
Sends a text message and waits for response
"""

import asyncio
import json
import websockets
import httpx
import sys
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
TEST_MESSAGE = "Hello, what is the current price of Tesla stock?"

async def test_text_conversation():
    """Test text conversation with ElevenLabs agent"""
    
    print("🧪 ElevenLabs Text-Only Test")
    print("=" * 40)
    
    # Get signed URL
    print("📡 Getting signed URL...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BACKEND_URL}/elevenlabs/signed-url")
            if response.status_code != 200:
                print(f"❌ Failed to get signed URL: {response.status_code}")
                return False
            signed_url = response.json()['signed_url']
            print("✅ Got signed URL")
        except Exception as e:
            print(f"❌ Error getting signed URL: {e}")
            return False
    
    # Connect to WebSocket
    print("\n📤 Connecting to ElevenLabs...")
    try:
        async with websockets.connect(signed_url) as ws:
            print("✅ Connected to WebSocket")
            
            # Send initialization
            init_msg = {"type": "conversation_initiation_client_data"}
            await ws.send(json.dumps(init_msg))
            print("✅ Sent initialization")
            
            # Wait for initialization response
            initialized = False
            while not initialized:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                if data['type'] == 'conversation_initiation_metadata':
                    initialized = True
                    print("✅ Conversation initialized")
            
            # Send test message
            print(f"\n💬 Sending: '{TEST_MESSAGE}'")
            msg = {"type": "user_message", "text": TEST_MESSAGE}
            await ws.send(json.dumps(msg))
            
            # Collect responses
            print("\n🎯 Waiting for agent response...")
            print("=" * 40)
            
            agent_response = None
            audio_count = 0
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < 10:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(response)
                    
                    if data['type'] == 'agent_response':
                        agent_response = data.get('message', '')
                        print(f"\n🤖 AGENT RESPONSE:")
                        print(f"   {agent_response}")
                        print()
                        
                    elif data['type'] == 'agent_response_correction':
                        correction = data.get('message', '')
                        print(f"   [Correction: {correction}]")
                        
                    elif data['type'] == 'audio':
                        audio_count += 1
                        if audio_count == 1:
                            print("🔊 Receiving audio...", end='', flush=True)
                        elif audio_count % 5 == 0:
                            print(".", end='', flush=True)
                            
                    elif data['type'] == 'user_transcript':
                        print(f"📝 User transcript: {data.get('message', '')}")
                        
                except asyncio.TimeoutError:
                    if agent_response:
                        break
                    continue
            
            print("\n" + "=" * 40)
            
            # Analyze results
            if agent_response:
                print("✅ SUCCESS: Agent responded with text")
                
                # Check if response is relevant
                keywords = ['tesla', 'tsla', 'stock', 'price', '$', 'trading']
                if any(keyword in agent_response.lower() for keyword in keywords):
                    print("✅ Response appears relevant to the query")
                else:
                    print("⚠️  Response may not be relevant to stock query")
                    
                if audio_count > 0:
                    print(f"✅ Received {audio_count} audio chunks")
                else:
                    print("⚠️  No audio received (text-only response)")
                    
                return True
            else:
                print("❌ FAILED: No response from agent")
                print("\nPossible issues:")
                print("1. Agent may not have an LLM model configured")
                print("2. Agent prompt may be incorrect")
                print("3. Connection or API issues")
                print("\nCheck agent configuration at:")
                print("https://elevenlabs.io/app/conversational-ai")
                return False
                
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run the test"""
    print("\n" + "🚀 Starting ElevenLabs Text Test" + "\n")
    print(f"Backend: {BACKEND_URL}")
    print(f"Test message: '{TEST_MESSAGE}'")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        success = asyncio.run(test_text_conversation())
        
        print("\n" + "=" * 40)
        if success:
            print("🎉 TEST PASSED - Agent is responding!")
            sys.exit(0)
        else:
            print("❌ TEST FAILED - Agent not responding")
            print("\n📝 Manual configuration needed:")
            print("1. Go to ElevenLabs dashboard")
            print("2. Select an LLM model (GPT-4 or Claude)")
            print("3. Save and test again")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()