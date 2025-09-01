#!/usr/bin/env python3
import asyncio
import aiohttp
import json
from datetime import datetime
import sys

async def check_endpoint(session, url, name):
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            status = response.status
            if status == 200:
                try:
                    data = await response.json()
                    return f"✓ {name}: {status} - {json.dumps(data)[:100]}..."
                except:
                    text = await response.text()
                    return f"✓ {name}: {status} - {text[:100]}..."
            else:
                return f"✗ {name}: {status}"
    except asyncio.TimeoutError:
        return f"⚠ {name}: Timeout"
    except Exception as e:
        return f"✗ {name}: {str(e)[:50]}"

async def monitor_activity():
    endpoints = [
        ("http://localhost:8000/health", "Backend Health"),
        ("http://localhost:8000/api/market-overview", "Market Overview"),
        ("http://localhost:5174/", "Frontend"),
    ]
    
    print("🔍 Starting Application Activity Monitor")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] Checking endpoints...")
            
            tasks = [check_endpoint(session, url, name) for url, name in endpoints]
            results = await asyncio.gather(*tasks)
            
            for result in results:
                print(f"  {result}")
            
            # Check for recent API calls
            try:
                async with session.get("http://localhost:8000/api/stock-price?symbol=AAPL", 
                                     timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"  📊 AAPL Price: ${data.get('price', 'N/A')}")
            except:
                pass
            
            await asyncio.sleep(5)  # Check every 5 seconds

if __name__ == "__main__":
    try:
        asyncio.run(monitor_activity())
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped")
        sys.exit(0)