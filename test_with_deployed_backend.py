#!/usr/bin/env python3
"""
Test ElevenLabs agent with the deployed backend tool
"""

import asyncio
import json
import websockets
import httpx
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

async def test_with_tools():
    """Test if agent uses the configured tool"""
    
    print("🧪 Testing ElevenLabs Agent with Tools")
    print("=" * 40)
    
    # Get signed URL
    print("📡 Getting signed URL...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/elevenlabs/signed-url")
        signed_url = response.json()['signed_url']
        print("✅ Got signed URL")
    
    # Test queries that require tool usage
    test_queries = [
        "What is the current price of Bitcoin?",  # Should use BTC-USD
        "What is Apple stock trading at?",        # Should use AAPL
        "How is the S&P 500 doing?"              # Should use SPY
    ]
    
    for query in test_queries:
        print(f"\n📊 Testing: '{query}'")
        print("-" * 40)
        
        async with websockets.connect(signed_url) as ws:
            # Initialize
            await ws.send(json.dumps({"type": "conversation_initiation_client_data"}))
            
            # Wait for init
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data['type'] == 'conversation_initiation_metadata':
                    break
            
            # Send query
            await ws.send(json.dumps({"type": "user_message", "text": query}))
            
            # Collect response
            agent_response = ""
            tool_calls = []
            start_time = asyncio.get_event_loop().time()
            
            while asyncio.get_event_loop().time() - start_time < 10:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                    data = json.loads(msg)
                    
                    if data['type'] == 'agent_response':
                        agent_response = data.get('agent_response_event', {}).get('agent_response', '')
                        
                    elif data['type'] == 'tool_call':
                        # Track if agent is calling tools
                        tool_calls.append(data.get('tool_name'))
                        
                except asyncio.TimeoutError:
                    if agent_response:
                        break
                    continue
            
            # Analyze response
            print(f"🤖 Response: {agent_response[:200]}...")
            
            if tool_calls:
                print(f"🔧 Tools used: {', '.join(tool_calls)}")
            
            # Check if response has real data
            if any(keyword in agent_response.lower() for keyword in ['111', '112', 'thousand', 'bitcoin']):
                print("✅ Appears to use real data (Bitcoin ~$111,000)")
            elif '49' in agent_response or 'forty-nine' in agent_response.lower():
                print("❌ Still hallucinating (Bitcoin shown as ~$49)")
            
            # Also check against deployed backend
            if 'bitcoin' in query.lower():
                print("\n🔍 Checking actual data from backend...")
                async with httpx.AsyncClient() as client:
                    actual = await client.get("https://gvses-market-insights.fly.dev/api/stock-price?symbol=BTC-USD")
                    if actual.status_code == 200:
                        btc_price = actual.json().get('last', 0)
                        print(f"   Real BTC price: ${btc_price:,.2f}")

def main():
    """Run the test"""
    print("\n🚀 Testing Agent with Configured Tools\n")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("Note: Tool is configured to use gvses-market-insights.fly.dev")
    print()
    
    try:
        asyncio.run(test_with_tools())
        
        print("\n" + "=" * 40)
        print("📋 Summary:")
        print("If agent shows Bitcoin at ~$111,000, tools are working ✅")
        print("If agent shows Bitcoin at ~$49, tools aren't being used ❌")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()