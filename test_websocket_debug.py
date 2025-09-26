#!/usr/bin/env python3
"""
WebSocket Debug Test - Isolate the exact source of the extra_headers issue
"""
import asyncio
import websockets
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_direct_openai_connection():
    """Test direct connection to OpenAI Realtime API"""
    print("=== Testing Direct OpenAI Connection ===")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-2025-08-28"
    
    try:
        print(f"🔗 Connecting to: {url}")
        print(f"🔗 Headers: {headers}")
        print(f"🔗 Websockets version: {websockets.__version__}")
        
        # Test the exact call that works in isolation
        async with websockets.connect(url, additional_headers=headers) as ws:
            print("✅ Direct OpenAI connection successful!")
            
            # Send a simple configuration
            config = {
                "type": "session.update",
                "session": {
                    "modalities": ["text", "audio"],
                    "instructions": "You are a helpful assistant.",
                    "voice": "alloy"
                }
            }
            
            await ws.send(json.dumps(config))
            print("✅ Configuration sent successfully")
            
            # Try to receive a response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"✅ Received response type: {data.get('type', 'unknown')}")
                return True
            except asyncio.TimeoutError:
                print("⚠️  No response received (timeout)")
                return True  # Still counts as successful connection
                
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_fastapi_proxy_connection():
    """Test connection through FastAPI proxy"""
    print("\n=== Testing FastAPI Proxy Connection ===")
    
    try:
        # Test the proxy endpoint
        proxy_url = "ws://localhost:8000/openai/realtime/ws"
        print(f"🔗 Connecting to proxy: {proxy_url}")
        
        async with websockets.connect(proxy_url) as ws:
            print("✅ FastAPI proxy connection successful!")
            
            # Send a test message
            test_message = {
                "type": "session.update",
                "session": {
                    "modalities": ["text"],
                    "instructions": "Test message"
                }
            }
            
            await ws.send(json.dumps(test_message))
            print("✅ Test message sent to proxy")
            
            # Try to receive a response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=10.0)
                data = json.loads(response)
                print(f"✅ Received proxy response type: {data.get('type', 'unknown')}")
                return True
            except asyncio.TimeoutError:
                print("⚠️  No response from proxy (timeout)")
                return False
                
    except Exception as e:
        print(f"❌ FastAPI proxy connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_websockets_parameter_compatibility():
    """Test websockets library parameter compatibility"""
    print("\n=== Testing WebSockets Parameter Compatibility ===")
    
    # Test which parameters are accepted by the current websockets version
    test_url = "wss://echo.websocket.org"
    headers = {"User-Agent": "TestClient/1.0"}
    
    print(f"Websockets version: {websockets.__version__}")
    
    # Test 1: additional_headers (new syntax)
    try:
        async with websockets.connect(test_url, additional_headers=headers) as ws:
            await ws.send("test")
            response = await ws.recv()
            print("✅ additional_headers parameter works")
    except Exception as e:
        print(f"❌ additional_headers failed: {e}")
    
    # Test 2: extra_headers (old syntax)
    try:
        async with websockets.connect(test_url, extra_headers=headers) as ws:
            await ws.send("test")
            response = await ws.recv()
            print("✅ extra_headers parameter works")
    except Exception as e:
        print(f"❌ extra_headers failed: {e}")

async def main():
    """Run comprehensive WebSocket debugging"""
    print("🔍 WebSocket Connection Debug Suite")
    print("=" * 50)
    
    # Test parameter compatibility first
    await test_websockets_parameter_compatibility()
    
    # Test direct connection
    direct_success = await test_direct_openai_connection()
    
    # Test proxy connection
    proxy_success = await test_fastapi_proxy_connection()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"Direct OpenAI Connection: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"FastAPI Proxy Connection: {'✅ SUCCESS' if proxy_success else '❌ FAILED'}")
    
    if direct_success and not proxy_success:
        print("\n🎯 Issue isolated: FastAPI proxy layer is causing the problem")
        print("   The websockets library works fine, but something in the proxy is interfering")
    elif not direct_success:
        print("\n🚨 WebSockets library or OpenAI connection issue")
    elif direct_success and proxy_success:
        print("\n🎉 Both connections working! Issue may be intermittent or resolved")

if __name__ == "__main__":
    asyncio.run(main())