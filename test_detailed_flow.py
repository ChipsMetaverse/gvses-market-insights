#!/usr/bin/env python3
"""
Detailed test showing all events in the OpenAI Realtime flow.
"""
import asyncio
import websockets
import json
import httpx
from datetime import datetime

def log_event(event_type, data=None, indent=0):
    """Log an event with proper formatting."""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = "  " * indent
    
    # Color codes
    colors = {
        'session.created': '\033[92m',      # Green
        'session.updated': '\033[92m',      # Green
        'response.created': '\033[94m',     # Blue
        'response.done': '\033[94m',        # Blue
        'response.function_call_arguments.done': '\033[93m',  # Yellow
        'conversation.item.created': '\033[96m',  # Cyan
        'error': '\033[91m',                # Red
    }
    
    color = colors.get(event_type, '\033[0m')
    reset = '\033[0m'
    
    print(f"[{timestamp}] {prefix}{color}{event_type}{reset}")
    
    if data:
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ['id', 'event_id', 'previous_item_id']:
                    continue  # Skip UUIDs for clarity
                if isinstance(value, (dict, list)) and len(str(value)) > 100:
                    print(f"            {prefix}  {key}: <{type(value).__name__} with {len(value)} items>")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"            {prefix}  {key}: {value[:100]}...")
                else:
                    print(f"            {prefix}  {key}: {value}")

async def test_detailed_flow():
    """Run detailed test capturing all events."""
    
    print("\n" + "="*60)
    print("DETAILED OPENAI REALTIME FLOW TEST")
    print("="*60 + "\n")
    
    # Create session
    print("1️⃣  Creating session...")
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/openai/realtime/session")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   ✅ Session ID: {session_id}\n")
    
    # Connect WebSocket
    print("2️⃣  Connecting WebSocket...")
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-realtime-2025-08-28"
    
    async with websockets.connect(ws_url, subprotocols=["realtime"]) as websocket:
        print(f"   ✅ Connected with subprotocol: {websocket.subprotocol}\n")
        
        print("3️⃣  Listening for initialization events...\n")
        
        # Collect initialization events
        init_complete = False
        event_count = 0
        
        while not init_complete and event_count < 10:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                data = json.loads(message)
                event_type = data.get('type', 'unknown')
                event_count += 1
                
                # Log the event
                log_event(event_type)
                
                # Show details for important events
                if event_type == 'session.created':
                    session = data.get('session', {})
                    print(f"     Model: {session.get('model', 'unknown')}")
                    print(f"     Voice: {session.get('voice', 'unknown')}")
                    tools = session.get('tools', [])
                    print(f"     Tools configured: {len(tools)}")
                    if tools:
                        for tool in tools[:3]:
                            if isinstance(tool, dict):
                                print(f"       - {tool.get('name', 'unknown')}")
                    init_complete = True
                    
                elif event_type == 'session.updated':
                    session = data.get('session', {})
                    tools = session.get('tools', [])
                    if tools:
                        print(f"     Tools updated: {len(tools)} tools")
                        for tool in tools[:3]:
                            if isinstance(tool, dict):
                                print(f"       - {tool.get('name', 'unknown')}")
                    
            except asyncio.TimeoutError:
                if event_count > 0:
                    init_complete = True
                break
        
        print(f"\n4️⃣  Sending test message...\n")
        
        # Send test message
        test_message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What's the current price of Apple stock?"}
                ]
            }
        }
        await websocket.send(json.dumps(test_message))
        print("   📤 Sent: 'What's the current price of Apple stock?'\n")
        
        await asyncio.sleep(0.1)
        await websocket.send(json.dumps({"type": "response.create"}))
        print("   📤 Sent: response.create\n")
        
        print("5️⃣  Receiving response events...\n")
        
        # Collect response events
        response_complete = False
        timeout_count = 0
        transcript_parts = []
        
        while not response_complete and timeout_count < 5:
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(message)
                event_type = data.get('type', 'unknown')
                
                # Log the event
                log_event(event_type, indent=1)
                
                # Handle specific events
                if event_type == 'response.function_call_arguments.done':
                    print(f"       Tool: {data.get('name', 'unknown')}")
                    print(f"       Args: {data.get('arguments', '{}')}")
                    
                elif event_type == 'response.audio_transcript.delta':
                    delta = data.get('delta', '')
                    if delta:
                        transcript_parts.append(delta)
                        
                elif event_type == 'response.audio_transcript.done':
                    transcript = data.get('transcript', '')
                    if transcript:
                        print(f"       Transcript: {transcript[:200]}...")
                        
                elif event_type == 'response.done':
                    response_complete = True
                    status = data.get('response', {}).get('status', 'unknown')
                    print(f"       Status: {status}")
                    
                elif event_type == 'error':
                    error = data.get('error', {})
                    print(f"       ❌ Error: {error.get('message', 'unknown')}")
                    response_complete = True
                    
            except asyncio.TimeoutError:
                timeout_count += 1
                if timeout_count == 1:
                    print("   ⏱️ Waiting for more events...")
        
        # Show accumulated transcript if any
        if transcript_parts:
            full_transcript = ''.join(transcript_parts)
            print(f"\n   📝 Full response transcript:\n       {full_transcript[:500]}...")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(test_detailed_flow())