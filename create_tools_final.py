#!/usr/bin/env python3
"""
Create tools for ElevenLabs agent with proper schema
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

print("🔧 Creating ElevenLabs Tools - Final Attempt")
print("=" * 50)

# Tool 1: Get Stock Price with proper schema
stock_price_tool = {
    "tool_config": {
        "type": "webhook",
        "name": "fetch_live_price",
        "description": "Get real-time price for stocks, crypto, or indices. Use BTC-USD for Bitcoin.",
        "response_timeout_secs": 10,
        "api_schema": {
            "url": "http://localhost:8000/api/stock-price",
            "method": "GET",
            "query_params_schema": {
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Symbol to query (BTC-USD for Bitcoin, AAPL for Apple)"
                    }
                },
                "required": ["symbol"]
            },
            "request_headers": {
                "Content-Type": "application/json"
            }
        }
    }
}

response = requests.post(
    "https://api.elevenlabs.io/v1/convai/tools",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=stock_price_tool
)

print(f"Response status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    tool_data = response.json()
    tool_id = tool_data.get('id')
    print(f"\n✅ Created tool: fetch_live_price")
    print(f"   Tool ID: {tool_id}")
    
    # Update agent to use this tool
    print(f"\n🔗 Updating agent to use tool...")
    
    # Update agent configuration
    agent_update = {
        "conversation_config": {
            "agent": {
                "prompt": f"""You are G'sves, a market analyst.

IMPORTANT: You have access to the fetch_live_price tool (ID: {tool_id}).

When asked about ANY price (Bitcoin, stocks, etc):
1. You MUST call fetch_live_price with the appropriate symbol
2. For Bitcoin, use symbol: BTC-USD (current price is around $112,000)
3. For Apple, use symbol: AAPL
4. For S&P 500, use symbol: SPY

NEVER guess prices. The tool gives you real data.
If you say Bitcoin is $49, you are wrong. Use the tool!""",
                "first_message": "",
                "language": "en"
            }
        }
    }
    
    update_resp = requests.patch(
        f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=agent_update
    )
    
    if update_resp.status_code in [200, 204]:
        print("✅ Agent prompt updated to reference tool!")
    else:
        print(f"❌ Failed to update agent: {update_resp.status_code}")
    
    # List all tools to verify
    print("\n📋 Listing all tools...")
    list_resp = requests.get(
        "https://api.elevenlabs.io/v1/convai/tools",
        headers={"xi-api-key": API_KEY}
    )
    
    if list_resp.status_code == 200:
        tools = list_resp.json().get('tools', [])
        print(f"Found {len(tools)} tools:")
        for tool in tools[:5]:  # Show first 5
            print(f"  • {tool.get('tool_config', {}).get('name')} (ID: {tool.get('id')})")
    
else:
    print(f"❌ Failed to create tool: {response.status_code}")

print("\n" + "=" * 50)
print("🧪 Next Steps:")
print("1. Test: 'What is the current price of Bitcoin?'")
print("2. Expected: ~$112,000 (from localhost:8000)")
print("3. Not: $49 (hallucinated)")
print("\nIf still showing $49:")
print("• Check dashboard for tool permissions")
print("• Ensure tool is enabled for the agent")
print("• Verify LLM model supports tool calling")