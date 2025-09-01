#!/usr/bin/env python3
"""
Configure ElevenLabs agent with tools to fetch real market data from backend
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Define tools that call our backend API
TOOLS_CONFIG = {
    "tools": [
        {
            "type": "webhook",
            "name": "get_stock_price",
            "description": "Get real-time stock price for a given symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, TSLA, BTC-USD)"
                    }
                },
                "required": ["symbol"]
            },
            "url": "http://localhost:8000/api/stock-price",
            "method": "GET",
            "query_parameters": ["symbol"]
        },
        {
            "type": "webhook",
            "name": "get_market_overview",
            "description": "Get market overview including major indices",
            "parameters": {
                "type": "object",
                "properties": {}
            },
            "url": "http://localhost:8000/api/market-overview",
            "method": "GET"
        },
        {
            "type": "webhook", 
            "name": "get_stock_news",
            "description": "Get latest news for a stock symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            },
            "url": "http://localhost:8000/api/stock-news",
            "method": "GET",
            "query_parameters": ["symbol"]
        }
    ]
}

# Update agent with tools
response = requests.patch(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=TOOLS_CONFIG
)

print("🔧 Configuring ElevenLabs Agent Tools")
print("=====================================")

if response.status_code in [200, 204]:
    print("✅ Tools configured successfully!")
    print("\nConfigured tools:")
    for tool in TOOLS_CONFIG['tools']:
        print(f"  • {tool['name']}: {tool['description']}")
        print(f"    URL: {tool['url']}")
else:
    print(f"❌ Failed to configure tools: {response.status_code}")
    print(f"Response: {response.text}")

# Verify configuration
verify = requests.get(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify.status_code == 200:
    agent_data = verify.json()
    tools = agent_data.get('tools', [])
    
    print("\n📋 Current Tools Configuration:")
    if tools:
        print(f"   {len(tools)} tools configured")
        for tool in tools:
            if isinstance(tool, dict):
                print(f"   • {tool.get('name', 'unnamed')}")
    else:
        print("   ❌ No tools configured")
        
    # Check if webhook tools are supported
    print("\n⚠️  Note: ElevenLabs may require tool configuration via dashboard")
    print("   If tools don't work, you may need to:")
    print("   1. Use the ElevenLabs dashboard to configure tools")
    print("   2. Or use a custom LLM endpoint that handles tool calls")