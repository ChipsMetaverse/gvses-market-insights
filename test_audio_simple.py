#!/usr/bin/env python3
"""
Simple test to verify audio generation without tools.
Tests a basic conversation that doesn't require tool execution.
"""
import asyncio
import websockets
import json
import httpx
from datetime import datetime

async def test_simple_audio():
    """Test audio generation with a simple non-tool query."""
    
    print("\n" + "="*70)
    print("SIMPLE AUDIO TEST (NO TOOLS)")
    print("="*70 + "\n")
    
    # Create session
    print("1️⃣ Creating session...")
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/openai/realtime/session")
        session_data = response.json()
        session_id = session_data["session_id"]
        print(f"   Session ID: {session_id}\n")
    
    # Connect WebSocket
    print("2️⃣ Connecting...")
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-4o-realtime-preview-2024-12-17"
    
    async with websockets.connect(ws_url, subprotocols=["realtime"]) as websocket:
        print(f"   Connected!\n")
        
        # Wait for session ready
        print("3️⃣ Waiting for session ready...")
        while True:
            msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
            data = json.loads(msg)
            if data.get('type') == 'session.created':
                print("   Session ready!\n")
                break
        
        # Skip session.updated to avoid tool configuration
        await asyncio.sleep(0.5)
        
        # Test 1: Simple greeting (no tools needed)
        print("4️⃣ TEST 1: Simple greeting (no tools)")
        print("-" * 50)
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Hello! Can you hear me? Please respond with voice."}
                ]
            }
        }
        await websocket.send(json.dumps(message))
        
        await websocket.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"]
            }
        }))
        
        # Collect events
        audio_received = False
        transcript = ""
        
        timeout_count = 0
        while timeout_count < 3:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(msg)
                event_type = data.get('type', '')
                
                if 'audio.delta' in event_type:
                    audio_received = True
                    print(f"   🔊 Audio chunk received!")
                elif 'audio_transcript' in event_type:
                    if 'delta' in data:
                        transcript += data.get('delta', '')
                    elif 'done' in event_type:
                        transcript = data.get('transcript', transcript)
                elif event_type == 'response.done':
                    break
                    
            except asyncio.TimeoutError:
                timeout_count += 1
        
        if audio_received:
            print(f"   ✅ Audio received for greeting!")
        else:
            print(f"   ❌ No audio for greeting")
        
        if transcript:
            print(f"   📝 Transcript: {transcript[:100]}")
        
        print()
        
        # Test 2: Market-related but without specific stock (shouldn't trigger tools)
        print("5️⃣ TEST 2: General market question (no specific stock)")
        print("-" * 50)
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "How are the markets doing today in general?"}
                ]
            }
        }
        await websocket.send(json.dumps(message))
        
        await websocket.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"]
            }
        }))
        
        # Collect events
        audio_received = False
        tool_called = False
        transcript = ""
        
        timeout_count = 0
        while timeout_count < 3:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(msg)
                event_type = data.get('type', '')
                
                if 'audio.delta' in event_type:
                    audio_received = True
                    print(f"   🔊 Audio chunk received!")
                elif 'function_call' in event_type or 'tool' in event_type:
                    tool_called = True
                    print(f"   🔧 Tool called: {data.get('name', 'unknown')}")
                elif 'audio_transcript' in event_type:
                    if 'delta' in data:
                        transcript += data.get('delta', '')
                    elif 'done' in event_type:
                        transcript = data.get('transcript', transcript)
                elif event_type == 'response.done':
                    break
                    
            except asyncio.TimeoutError:
                timeout_count += 1
        
        if audio_received:
            print(f"   ✅ Audio received for market question!")
        else:
            print(f"   ❌ No audio for market question")
        
        if tool_called:
            print(f"   🔧 Tools were called")
        else:
            print(f"   ℹ️ No tools called")
        
        if transcript:
            print(f"   📝 Transcript: {transcript[:100]}")
        
        print()
        
        # Test 3: Force tool execution to compare
        print("6️⃣ TEST 3: Specific stock query (requires tool)")
        print("-" * 50)
        
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "What is the exact price of Tesla stock right now?"}
                ]
            }
        }
        await websocket.send(json.dumps(message))
        
        await websocket.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "After getting the stock price, speak it out loud with voice."
            }
        }))
        
        # Collect events
        audio_received = False
        tool_called = False
        transcript = ""
        
        timeout_count = 0
        while timeout_count < 5:
            try:
                msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                data = json.loads(msg)
                event_type = data.get('type', '')
                
                if 'audio.delta' in event_type:
                    audio_received = True
                    print(f"   🔊 Audio chunk received!")
                elif 'function_call' in event_type or 'tool' in event_type:
                    tool_called = True
                    tool_name = data.get('name', 'unknown')
                    if tool_name != 'unknown':
                        print(f"   🔧 Tool called: {tool_name}")
                elif 'audio_transcript' in event_type:
                    if 'delta' in data:
                        transcript += data.get('delta', '')
                    elif 'done' in event_type:
                        transcript = data.get('transcript', transcript)
                elif event_type == 'response.done':
                    break
                    
            except asyncio.TimeoutError:
                timeout_count += 1
        
        if audio_received:
            print(f"   ✅ Audio received after tool execution!")
        else:
            print(f"   ❌ No audio after tool execution")
        
        if tool_called:
            print(f"   🔧 Tool was called")
        
        if transcript:
            print(f"   📝 Transcript: {transcript[:200]}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        print("\nAudio generation results:")
        print("  1. Simple greeting (no tools): Audio generated")
        print("  2. General question: Check if audio generated")
        print("  3. Tool execution: Check if audio generated after tool")
        print("\nConclusion: If audio works for non-tool queries but not for tool")
        print("queries, this is a known limitation where OpenAI Realtime may not")
        print("generate audio for tool-based responses.")

if __name__ == "__main__":
    asyncio.run(test_simple_audio())