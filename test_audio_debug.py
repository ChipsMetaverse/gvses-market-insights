#!/usr/bin/env python3
"""
Debug test to capture ALL events and understand why audio isn't being generated.
"""
import asyncio
import websockets
import json
import httpx
from datetime import datetime

def log_event(event_type, data=None, level="INFO"):
    """Log event with detailed data."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    emoji = {
        "INFO": "📝", "SUCCESS": "✅", "ERROR": "❌", 
        "AUDIO": "🔊", "TOOL": "🔧", "SESSION": "🔐",
        "TEXT": "💬", "CONFIG": "⚙️"
    }.get(level, "📌")
    
    print(f"[{timestamp}] {emoji} {event_type}")
    
    if data:
        # Show relevant fields
        if isinstance(data, dict):
            # For session events, show configuration
            if 'session' in data:
                session = data['session']
                print(f"            Session config:")
                print(f"              - modalities: {session.get('modalities', 'not set')}")
                print(f"              - voice: {session.get('voice', 'not set')}")
                print(f"              - tools: {len(session.get('tools', []))} configured")
                print(f"              - input_audio_format: {session.get('input_audio_format', 'not set')}")
                print(f"              - output_audio_format: {session.get('output_audio_format', 'not set')}")
                if session.get('tools'):
                    print(f"              - tool names: {[t.get('name', 'unknown') for t in session.get('tools', [])[:3]]}")
            
            # For response configuration
            if 'response' in data and event_type == 'response.created':
                response = data['response']
                print(f"            Response config:")
                print(f"              - modalities: {response.get('modalities', 'not set')}")
                print(f"              - status: {response.get('status', 'not set')}")
            
            # For audio events
            if 'audio' in event_type.lower():
                if 'delta' in data:
                    print(f"            Audio delta size: {len(data.get('delta', ''))}")
                if 'transcript' in data:
                    print(f"            Transcript: {data.get('transcript', '')[:100]}")

async def test_audio_debug():
    """Run comprehensive audio debug test."""
    
    print("\n" + "="*70)
    print("OPENAI REALTIME AUDIO DEBUG TEST")
    print("="*70 + "\n")
    
    # Create session
    print("1️⃣ Creating session...")
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/openai/realtime/session")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   Session ID: {session_id}\n")
    
    # Connect WebSocket
    print("2️⃣ Connecting WebSocket...")
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-realtime-2025-08-28"
    
    async with websockets.connect(ws_url, subprotocols=["realtime"]) as websocket:
        print(f"   Connected with subprotocol: {websocket.subprotocol}\n")
        
        print("3️⃣ Capturing ALL events for 5 seconds...")
        print("-" * 70)
        
        # Capture all initialization events
        event_count = 0
        session_ready = False
        tools_configured = False
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 5:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                data = json.loads(msg)
                event_type = data.get('type', 'unknown')
                event_count += 1
                
                # Log based on event type
                if 'session' in event_type:
                    log_event(event_type, data, "SESSION")
                    if event_type == 'session.created':
                        session_ready = True
                    elif event_type == 'session.updated':
                        session = data.get('session', {})
                        if session.get('tools'):
                            tools_configured = True
                elif 'audio' in event_type:
                    log_event(event_type, data, "AUDIO")
                elif 'tool' in event_type or 'function' in event_type:
                    log_event(event_type, data, "TOOL")
                else:
                    log_event(event_type, data, "INFO")
                    
            except asyncio.TimeoutError:
                continue
        
        print("-" * 70)
        print(f"Captured {event_count} initialization events")
        print(f"Session ready: {session_ready}")
        print(f"Tools configured: {tools_configured}\n")
        
        # Send test message with explicit audio request
        print("4️⃣ Sending test message with explicit audio modality...")
        
        # First, ensure session is configured for audio
        session_update = {
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "voice": "alloy",
                "output_audio_format": "pcm16"
            }
        }
        await websocket.send(json.dumps(session_update))
        print("   Sent session.update to ensure audio is enabled")
        
        await asyncio.sleep(0.5)
        
        # Send message
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What is Apple stock price? Please respond with voice."}
                ]
            }
        }
        await websocket.send(json.dumps(message))
        print("   Sent user message")
        
        # Request response with explicit audio
        response_request = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "Respond with both text and audio. Say the stock price clearly."
            }
        }
        await websocket.send(json.dumps(response_request))
        print("   Requested response with text and audio modalities\n")
        
        # Capture response events
        print("5️⃣ Capturing response events for 10 seconds...")
        print("-" * 70)
        
        response_events = []
        audio_events = 0
        text_events = 0
        tool_events = 0
        
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 10:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=0.5)
                data = json.loads(msg)
                event_type = data.get('type', 'unknown')
                response_events.append(event_type)
                
                # Count event types
                if 'audio' in event_type:
                    audio_events += 1
                    log_event(event_type, data, "AUDIO")
                elif 'text' in event_type or 'transcript' in event_type:
                    text_events += 1
                    log_event(event_type, data, "TEXT")
                elif 'function' in event_type or 'tool' in event_type:
                    tool_events += 1
                    log_event(event_type, data, "TOOL")
                elif 'response' in event_type:
                    log_event(event_type, data, "CONFIG")
                else:
                    log_event(event_type, data, "INFO")
                
                # Break on response.done
                if event_type == 'response.done':
                    print("\n   Response completed!")
                    break
                    
            except asyncio.TimeoutError:
                continue
        
        print("-" * 70)
        print(f"\nEvent Summary:")
        print(f"  Total events: {len(response_events)}")
        print(f"  Audio events: {audio_events}")
        print(f"  Text events: {text_events}")
        print(f"  Tool events: {tool_events}")
        print(f"  Unique event types: {set(response_events)}")
        
        # Analysis
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        if audio_events > 0:
            print("✅ Audio generation is working!")
            print(f"   Received {audio_events} audio events")
        else:
            print("❌ No audio events received")
            print("\nPossible issues:")
            print("  1. Session not configured for audio modality")
            print("  2. OpenAI API not generating audio for this request")
            print("  3. Audio events not being forwarded by relay")
            print("  4. Model doesn't support audio for tool responses")
            
            if not tools_configured:
                print("  5. ⚠️ Tools were not configured - this might affect audio generation")

if __name__ == "__main__":
    asyncio.run(test_audio_debug())