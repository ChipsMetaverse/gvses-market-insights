#!/usr/bin/env python3
"""
Create tools for ElevenLabs agent using the correct API structure
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

print("🔧 Creating ElevenLabs Tools with Correct API")
print("=" * 50)

# Tool 1: Get Stock Price
stock_price_tool = {
    "tool_config": {
        "type": "webhook",
        "name": "get_real_stock_price",
        "description": "Fetch real-time stock, crypto, or index price. ALWAYS use this for price queries.",
        "response_timeout_secs": 10,
        "api_schema": {
            "url": "http://localhost:8000/api/stock-price",
            "method": "GET",
            "query_params_schema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock/crypto symbol. Use BTC-USD for Bitcoin, AAPL for Apple, SPY for S&P 500"
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

if response.status_code == 200:
    tool_id = response.json().get('id')
    print(f"✅ Created tool: get_real_stock_price (ID: {tool_id})")
    
    # Now link the tool to the agent
    print(f"🔗 Linking tool to agent {AGENT_ID}...")
    
    # Get current agent config
    agent_resp = requests.get(
        f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
        headers={"xi-api-key": API_KEY}
    )
    
    if agent_resp.status_code == 200:
        agent_data = agent_resp.json()
        
        # Update conversation config with tool
        update_data = {
            "conversation_config": {
                **agent_data.get('conversation_config', {}),
                "tools": [tool_id]  # Add the tool ID
            }
        }
        
        # Also update the prompt to ensure tool usage
        update_data["conversation_config"]["agent"] = {
            **agent_data.get('conversation_config', {}).get('agent', {}),
            "prompt": """You are G'sves, a market analyst with access to real-time data.

CRITICAL: You MUST use the get_real_stock_price tool for ANY price query.
- For Bitcoin: Use symbol BTC-USD
- For Apple: Use symbol AAPL  
- For S&P 500: Use symbol SPY
- For Tesla: Use symbol TSLA

NEVER make up prices. ALWAYS call the tool to get current data.
If someone asks "What is the price of Bitcoin?", you MUST:
1. Call get_real_stock_price with symbol="BTC-USD"
2. Report the actual price returned (should be around $110,000+)
3. Never say $49 or any made-up number

You have real-time data access through tools. Use them!"""
        }
        
        update_resp = requests.patch(
            f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=update_data
        )
        
        if update_resp.status_code in [200, 204]:
            print(f"✅ Tool linked to agent and prompt updated!")
        else:
            print(f"❌ Failed to link tool: {update_resp.status_code}")
            print(update_resp.text)
    else:
        print(f"❌ Failed to get agent config: {agent_resp.status_code}")
else:
    print(f"❌ Failed to create tool: {response.status_code}")
    print(f"Response: {response.text}")

# Tool 2: Market Overview
market_tool = {
    "tool_config": {
        "type": "webhook",
        "name": "get_market_overview",
        "description": "Get overall market status, indices, gainers and losers",
        "response_timeout_secs": 10,
        "api_schema": {
            "url": "http://localhost:8000/api/market-overview",
            "method": "GET",
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
    json=market_tool
)

if response.status_code == 200:
    print(f"✅ Created tool: get_market_overview")
else:
    print(f"❌ Failed to create market overview: {response.status_code}")

print("\n" + "=" * 50)
print("📊 Testing Tool Creation")
print("\nNow test with these queries:")
print('1. "What is the current price of Bitcoin?"')
print('   Expected: ~$112,000 (from tool)')
print('   Not: $49 (hallucinated)')
print('\n2. "What is Apple stock trading at?"')
print('3. "Give me a market overview"')