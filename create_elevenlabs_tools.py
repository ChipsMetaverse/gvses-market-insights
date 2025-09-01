#!/usr/bin/env python3
"""
Create tools for ElevenLabs agent to access real market data
Using the ElevenLabs Tools API
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

# Base URL for ElevenLabs API
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Creating ElevenLabs Tools for Real Market Data")
print("=" * 50)

# Tool 1: Get Stock Price
def create_stock_price_tool():
    tool_config = {
        "type": "webhook",
        "name": "get_stock_price", 
        "description": "Fetch real-time stock price and market data for any symbol including stocks, crypto, and indices",
        "configuration": {
            "url": "http://localhost:8000/api/stock-price",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json"
            },
            "query_parameters": {
                "symbol": "{{symbol}}"
            }
        },
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock/crypto/index symbol (e.g., AAPL, BTC-USD, SPY)"
                }
            },
            "required": ["symbol"]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/tools.create",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=tool_config
    )
    
    if response.status_code == 200:
        tool_id = response.json().get('tool_id')
        print(f"✅ Created tool: get_stock_price (ID: {tool_id})")
        return tool_id
    else:
        print(f"❌ Failed to create get_stock_price: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

# Tool 2: Get Market Overview
def create_market_overview_tool():
    tool_config = {
        "type": "webhook",
        "name": "get_market_overview",
        "description": "Get overall market status including major indices, top gainers, and losers",
        "configuration": {
            "url": "http://localhost:8000/api/market-overview",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json"
            }
        },
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/tools.create",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=tool_config
    )
    
    if response.status_code == 200:
        tool_id = response.json().get('tool_id')
        print(f"✅ Created tool: get_market_overview (ID: {tool_id})")
        return tool_id
    else:
        print(f"❌ Failed to create get_market_overview: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

# Tool 3: Get Stock News
def create_stock_news_tool():
    tool_config = {
        "type": "webhook",
        "name": "get_stock_news",
        "description": "Get latest news and analysis for a specific stock or market",
        "configuration": {
            "url": "http://localhost:8000/api/stock-news",
            "method": "GET",
            "headers": {
                "Content-Type": "application/json"
            },
            "query_parameters": {
                "symbol": "{{symbol}}"
            }
        },
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol for news lookup"
                }
            },
            "required": ["symbol"]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/tools.create",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=tool_config
    )
    
    if response.status_code == 200:
        tool_id = response.json().get('tool_id')
        print(f"✅ Created tool: get_stock_news (ID: {tool_id})")
        return tool_id
    else:
        print(f"❌ Failed to create get_stock_news: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

# First, list existing tools
print("\n📋 Checking existing tools...")
list_response = requests.get(
    f"{BASE_URL}/tools.list",
    headers={"xi-api-key": API_KEY}
)

if list_response.status_code == 200:
    existing_tools = list_response.json().get('tools', [])
    if existing_tools:
        print(f"   Found {len(existing_tools)} existing tools:")
        for tool in existing_tools:
            print(f"   • {tool.get('name')} (ID: {tool.get('tool_id')})")
    else:
        print("   No existing tools found")
else:
    print(f"   Failed to list tools: {list_response.status_code}")

# Create the tools
print("\n🔨 Creating new tools...")
tool_ids = []

tool_id = create_stock_price_tool()
if tool_id:
    tool_ids.append(tool_id)

tool_id = create_market_overview_tool()
if tool_id:
    tool_ids.append(tool_id)

tool_id = create_stock_news_tool()
if tool_id:
    tool_ids.append(tool_id)

# Now assign tools to the agent
if tool_ids:
    print(f"\n🔗 Assigning {len(tool_ids)} tools to agent...")
    
    # Get current agent configuration
    agent_response = requests.get(
        f"{BASE_URL}/convai/agents/{AGENT_ID}",
        headers={"xi-api-key": API_KEY}
    )
    
    if agent_response.status_code == 200:
        agent_config = agent_response.json()
        
        # Update with tool IDs
        update_config = {
            "tools": tool_ids
        }
        
        update_response = requests.patch(
            f"{BASE_URL}/convai/agents/{AGENT_ID}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=update_config
        )
        
        if update_response.status_code in [200, 204]:
            print(f"✅ Successfully assigned tools to agent!")
        else:
            print(f"❌ Failed to assign tools: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
    else:
        print(f"❌ Failed to get agent config: {agent_response.status_code}")
        
print("\n" + "=" * 50)
print("📊 Summary:")
print(f"   Agent ID: {AGENT_ID}")
print(f"   Created {len(tool_ids)} tools")
print("\n⚠️  Important: Tools point to localhost:8000")
print("   Make sure your backend is running!")
print("\n🧪 Test with: 'What is the current price of Bitcoin?'")
print("   Expected: ~$111,000 (not $49!)")