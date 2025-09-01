#!/usr/bin/env python3
"""
Debug test to see exact messages from ElevenLabs agent
"""

import asyncio
import json
import websockets
import httpx
from datetime import datetime

BACKEND_URL = "http://localhost:8000"
TEST_MESSAGE = "Hello, what is the current price of Tesla stock?"

async def test_debug():
    """Debug WebSocket messages"""
    
    print("🔍 ElevenLabs Debug Test")
    print("=" * 40)
    
    # Get signed URL
    print("📡 Getting signed URL...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/elevenlabs/signed-url")
        signed_url = response.json()['signed_url']
        print("✅ Got signed URL")
    
    # Connect to WebSocket
    print("\n📤 Connecting to ElevenLabs...")
    async with websockets.connect(signed_url) as ws:
        print("✅ Connected to WebSocket")
        
        # Send initialization
        init_msg = {"type": "conversation_initiation_client_data"}
        await ws.send(json.dumps(init_msg))
        print("✅ Sent initialization")
        
        # Wait for initialization response
        while True:
            response = await ws.recv()
            data = json.loads(response)
            print(f"\n📥 Received: {data['type']}")
            
            # Show full message for non-audio types
            if data['type'] != 'audio':
                print(f"   Full data: {json.dumps(data, indent=2)}")
            else:
                # For audio, just show summary
                audio_data = data.get('audio_event', {})
                print(f"   Audio chunk: event_id={audio_data.get('event_id')}, "
                      f"base64_length={len(audio_data.get('audio_base_64', ''))}")
            
            if data['type'] == 'conversation_initiation_metadata':
                break
        
        # Send test message
        print(f"\n💬 Sending text message: '{TEST_MESSAGE}'")
        msg = {"type": "user_message", "text": TEST_MESSAGE}
        await ws.send(json.dumps(msg))
        print(f"   Sent: {json.dumps(msg)}")
        
        # Collect all responses for 15 seconds
        print("\n🎯 Collecting responses for 15 seconds...")
        print("=" * 40)
        
        start_time = asyncio.get_event_loop().time()
        message_count = {}
        agent_text = ""
        
        while asyncio.get_event_loop().time() - start_time < 15:
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=1.0)
                data = json.loads(response)
                
                msg_type = data['type']
                message_count[msg_type] = message_count.get(msg_type, 0) + 1
                
                print(f"\n📥 Message #{sum(message_count.values())}: {msg_type}")
                
                if msg_type == 'agent_response':
                    agent_resp = data.get('agent_response_event', {})
                    agent_text = agent_resp.get('agent_response', '')
                    print(f"   Agent says: '{agent_text}'")
                    print(f"   Full event: {json.dumps(agent_resp, indent=2)}")
                    
                elif msg_type == 'agent_response_correction':
                    correction = data.get('agent_response_correction_event', {})
                    print(f"   Correction: {json.dumps(correction, indent=2)}")
                    
                elif msg_type == 'user_transcript':
                    transcript = data.get('user_transcription_event', {})
                    print(f"   User transcript: {json.dumps(transcript, indent=2)}")
                    
                elif msg_type == 'audio':
                    audio = data.get('audio_event', {})
                    print(f"   Audio: event_id={audio.get('event_id')}, "
                          f"base64_len={len(audio.get('audio_base_64', ''))}")
                    
                elif msg_type == 'interruption':
                    interruption = data.get('interruption_event', {})
                    print(f"   Interruption: {json.dumps(interruption, indent=2)}")
                    
                else:
                    # Show full data for unexpected message types
                    print(f"   Full data: {json.dumps(data, indent=2)}")
                    
            except asyncio.TimeoutError:
                print(".", end='', flush=True)
                continue
        
        print("\n\n" + "=" * 40)
        print("📊 Message Summary:")
        for msg_type, count in sorted(message_count.items()):
            print(f"   {msg_type}: {count} messages")
        
        if agent_text:
            print(f"\n✅ Agent responded with: '{agent_text}'")
        else:
            print("\n❌ No text response from agent")
            
        return bool(agent_text)

def main():
    """Run the debug test"""
    print("\n🚀 Starting ElevenLabs Debug Test\n")
    print(f"Backend: {BACKEND_URL}")
    print(f"Test message: '{TEST_MESSAGE}'")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    try:
        success = asyncio.run(test_debug())
        
        print("\n" + "=" * 40)
        if success:
            print("🎉 TEST PASSED - Agent responded!")
        else:
            print("❌ TEST FAILED - No agent response")
            print("\n📝 Troubleshooting:")
            print("1. Check agent configuration in ElevenLabs dashboard")
            print("2. Ensure LLM model is selected")
            print("3. Verify agent prompt is configured")
            
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()