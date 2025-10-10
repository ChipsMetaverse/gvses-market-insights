#!/usr/bin/env python3
"""
Test script for OpenAI Realtime API via relay server
"""

import asyncio
import websockets
import json
import numpy as np

async def test_realtime_connection():
    """Test the OpenAI Realtime API connection and voice interaction."""

    # Step 1: Create session
    import requests
    print("📞 Creating session...")
    response = requests.post("http://localhost:8000/openai/realtime/session")
    session_data = response.json()
    print(f"✅ Session created: {session_data['session_id']}")
    print(f"🔗 WebSocket URL: {session_data['ws_url']}")

    # Step 2: Connect to WebSocket
    ws_url = session_data['ws_url']

    async with websockets.connect(ws_url, subprotocols=['realtime']) as websocket:
        print("✅ WebSocket connected")

        # Step 3: Wait for session.created
        print("⏳ Waiting for session.created...")
        while True:
            message = await websocket.recv()
            if isinstance(message, str):
                data = json.loads(message)
                print(f"📨 Received: {data.get('type')}")

                if data.get('type') == 'session.created':
                    print("✅ Session created event received")
                    print(f"   Session config: {json.dumps(data.get('session', {}), indent=2)[:200]}...")
                    break
                elif data.get('type') == 'session.updated':
                    print("✅ Session updated - configuration applied")
                    print(f"   Turn detection: {data.get('session', {}).get('turn_detection')}")
                    break

        # Step 4: Send a text message to test TTS
        print("\n🗣️ Sending test message for TTS...")
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
        print("📤 Sent test message")

        # Request response
        response_create = {
            "type": "response.create"
        }
        await websocket.send(json.dumps(response_create))
        print("📤 Requested response")

        # Step 5: Monitor for audio and transcript responses
        print("\n⏳ Monitoring for responses (10 seconds)...")
        audio_received = False
        transcript_received = False

        try:
            for i in range(20):  # Monitor for 10 seconds
                message = await asyncio.wait_for(websocket.recv(), timeout=0.5)

                if isinstance(message, str):
                    data = json.loads(message)
                    msg_type = data.get('type', 'unknown')

                    # Key events to watch
                    if 'audio' in msg_type or 'response' in msg_type:
                        print(f"📨 {msg_type}")

                    if msg_type == 'response.audio.delta':
                        audio_received = True
                        print(f"   🔊 Audio delta received ({len(data.get('delta', ''))} bytes)")

                    if msg_type == 'response.audio_transcript.delta':
                        transcript_received = True
                        print(f"   📝 Transcript: {data.get('delta', '')}")

                    if msg_type == 'response.done':
                        print("✅ Response complete!")
                        break

                elif isinstance(message, bytes):
                    audio_received = True
                    print(f"🔊 Binary audio chunk received: {len(message)} bytes")

        except asyncio.TimeoutError:
            pass

        # Summary
        print("\n" + "="*50)
        print("TEST SUMMARY:")
        print(f"  Audio received: {'✅' if audio_received else '❌'}")
        print(f"  Transcript received: {'✅' if transcript_received else '❌'}")
        print("="*50)

        if audio_received or transcript_received:
            print("\n🎉 Voice assistant is working!")
        else:
            print("\n⚠️ No audio or transcript received - check configuration")

if __name__ == "__main__":
    asyncio.run(test_realtime_connection())
