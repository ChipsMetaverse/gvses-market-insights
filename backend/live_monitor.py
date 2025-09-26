#!/usr/bin/env python3
"""Live monitoring of backend API requests"""

import asyncio
from datetime import datetime
import aiohttp
import json

async def monitor_requests():
    """Monitor backend by periodically checking and simulating Computer Use requests"""
    
    print("🔍 Live Backend Monitor - localhost:8000")
    print("=" * 80)
    print("Watching for incoming requests from Computer Use...")
    print("Expected pattern when Computer Use interacts:")
    print("  1. OPTIONS /api/stock-price (CORS preflight from host.docker.internal)")
    print("  2. GET /api/stock-price?symbol=XXX (actual request)")
    print("  3. GET /elevenlabs/signed-url (for voice WebSocket)")
    print("=" * 80)
    
    headers_docker = {
        'Origin': 'http://host.docker.internal:5174',
        'User-Agent': 'Mozilla/5.0 (Computer Use Docker)'
    }
    
    headers_localhost = {
        'Origin': 'http://localhost:5174',
        'User-Agent': 'Mozilla/5.0 (Local Browser)'
    }
    
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                # Simulate Computer Use CORS preflight
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing Computer Use access pattern:")
                
                # 1. CORS preflight from Docker
                headers_preflight = {
                    'Origin': 'http://host.docker.internal:5174',
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'content-type',
                }
                async with session.options('http://localhost:8000/api/stock-price', 
                                          headers=headers_preflight) as resp:
                    print(f"  ✓ CORS preflight: {resp.status}")
                    cors_headers = resp.headers.get('Access-Control-Allow-Origin', 'none')
                    print(f"    Allow-Origin: {cors_headers}")
                
                # 2. Actual request with Docker origin
                async with session.get('http://localhost:8000/api/stock-price?symbol=PLTR',
                                      headers=headers_docker) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"  ✓ Stock price (PLTR): ${data.get('price', 'N/A')}")
                        print(f"    Source: {data.get('data_source', 'unknown')}")
                    else:
                        print(f"  ✗ Stock price failed: {resp.status}")
                
                # 3. Test ElevenLabs endpoint
                async with session.get('http://localhost:8000/elevenlabs/signed-url',
                                      headers=headers_docker) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"  ✓ ElevenLabs URL: ...{data.get('url', '')[-30:]}")
                    else:
                        print(f"  ✗ ElevenLabs failed: {resp.status}")
                
                # 4. Test /ask endpoint (text fallback)
                test_payload = {
                    "message": "What is the current price of PLTR?",
                    "sessionId": "computer-use-test"
                }
                async with session.post('http://localhost:8000/ask',
                                       json=test_payload,
                                       headers=headers_docker) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"  ✓ Text /ask endpoint: {resp.status}")
                        if 'response' in data:
                            print(f"    Response preview: {data['response'][:50]}...")
                    else:
                        print(f"  ✗ /ask endpoint failed: {resp.status}")
                
                print("\n" + "-" * 40)
                print("Waiting 10 seconds before next check...")
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
            
            await asyncio.sleep(10)

if __name__ == "__main__":
    print("\n📡 Starting live backend monitor...")
    print("Press Ctrl+C to stop\n")
    try:
        asyncio.run(monitor_requests())
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped")