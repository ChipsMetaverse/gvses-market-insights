#!/usr/bin/env python3
"""
Test websockets connection directly to isolate the issue
"""

import asyncio
import websockets
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openai_connection():
    """Test direct connection to OpenAI Realtime API"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OPENAI_API_KEY found")
        return
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2025-08-28"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    print(f"🔗 Testing direct OpenAI connection with websockets {websockets.__version__}")
    print(f"🌐 URL: {url}")
    print(f"📋 Headers: {headers}")
    
    try:
        print("🎯 Testing with additional_headers...")
        async with websockets.connect(url, additional_headers=headers) as ws:
            print("✅ Connection successful with additional_headers!")
            
            # Try to receive initial message
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(message)
                print(f"📨 Received: {data.get('type', 'unknown type')}")
            except asyncio.TimeoutError:
                print("⏰ Timeout waiting for initial message")
            except Exception as e:
                print(f"📨 Message error: {e}")
                
    except Exception as e:
        print(f"❌ Connection failed with additional_headers: {e}")
        
        # Try with no headers to isolate the issue
        try:
            print("🎯 Testing with no headers...")
            async with websockets.connect(url) as ws:
                print("✅ Connection successful with no headers!")
        except Exception as e2:
            print(f"❌ Connection failed with no headers too: {e2}")

if __name__ == "__main__":
    asyncio.run(test_openai_connection())