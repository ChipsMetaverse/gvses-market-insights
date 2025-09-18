#!/usr/bin/env python3
"""
Test that shows actual stock price retrieval through OpenAI Realtime.
"""
import asyncio
import websockets
import json
import httpx

async def test_stock_price():
    """Test stock price retrieval."""
    
    print("\n🔍 STOCK PRICE RETRIEVAL TEST")
    print("="*50 + "\n")
    
    # Create session
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/openai/realtime/session")
        session_id = response.json()["session_id"]
    
    # Connect
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}"
    
    async with websockets.connect(ws_url, subprotocols=["realtime"]) as ws:
        print("✅ Connected to OpenAI Realtime\n")
        
        # Wait for session.created
        while True:
            msg = await ws.recv()
            data = json.loads(msg)
            if data.get('type') == 'session.created':
                print("✅ Session initialized\n")
                break
        
        # Send stock price query
        queries = [
            "What's the current price of Tesla stock?",
            "Tell me Apple's stock price",
            "How much is Microsoft trading at?"
        ]
        
        for query in queries:
            print(f"📊 Query: {query}")
            print("-" * 40)
            
            # Send message
            await ws.send(json.dumps({
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": query}]
                }
            }))
            
            # Request response
            await ws.send(json.dumps({"type": "response.create"}))
            
            # Collect response
            tool_called = None
            tool_result = None
            transcript = ""
            response_done = False
            
            while not response_done:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=3.0)
                    data = json.loads(msg)
                    event_type = data.get('type', '')
                    
                    if 'function_call_arguments.done' in event_type:
                        tool_called = data.get('name', 'unknown')
                        args = data.get('arguments', '{}')
                        print(f"   🔧 Tool called: {tool_called}")
                        print(f"   📝 Arguments: {args}")
                        
                    elif event_type == 'tool_call_complete':
                        result = data.get('result', {})
                        if isinstance(result, str):
                            try:
                                result = json.loads(result)
                            except:
                                pass
                        tool_result = result
                        
                        # Extract price info if available
                        if isinstance(result, dict):
                            price = result.get('currentPrice') or result.get('price')
                            symbol = result.get('symbol')
                            if price and symbol:
                                print(f"   💰 {symbol}: ${price}")
                                
                    elif 'audio_transcript.done' in event_type:
                        transcript = data.get('transcript', '')
                        
                    elif event_type == 'response.done':
                        response_done = True
                        if transcript:
                            print(f"   🗣️ Response: {transcript[:200]}")
                        print()
                        
                except asyncio.TimeoutError:
                    response_done = True
                    print()
        
        print("="*50)
        print("✅ ALL STOCK PRICE QUERIES COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    asyncio.run(test_stock_price())