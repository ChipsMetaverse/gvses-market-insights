#!/usr/bin/env python3
"""
Test OpenAI Realtime API connection directly
"""
import os
import websockets
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_openai_realtime():
    api_key = os.getenv('OPENAI_API_KEY')
    print(f'API Key present: {bool(api_key)}')
    if api_key:
        print(f'API Key prefix: {api_key[:12]}...')
    
    # Test the exact same connection as the relay server
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    url = 'wss://api.openai.com/v1/realtime?model=gpt-realtime'
    print(f'Testing connection to: {url}')
    
    try:
        # Try to connect like the relay server does
        ws = await websockets.connect(url, additional_headers=headers)
        print('✅ Connection successful!')
        await ws.close()
    except websockets.exceptions.InvalidStatusCode as e:
        print(f'❌ Connection rejected with status: {e.status_code}')
        print(f'Response headers: {dict(e.headers) if e.headers else "None"}')
        if e.status_code == 401:
            print('🔑 Authentication failed - API key invalid')
        elif e.status_code == 403:
            print('🚫 Forbidden - API key may lack realtime permissions')
        elif e.status_code == 404:
            print('🚫 Not found - model may not exist or endpoint incorrect')
    except Exception as e:
        print(f'❌ Connection failed: {type(e).__name__}: {e}')

if __name__ == "__main__":
    asyncio.run(test_openai_realtime())