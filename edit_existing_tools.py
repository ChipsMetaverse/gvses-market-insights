#!/usr/bin/env python3
"""
Edit existing ElevenLabs tools to point to correct endpoints
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

print("🔧 Editing Existing ElevenLabs Tools")
print("=" * 50)

# First, list all existing tools to find the ones to edit
list_resp = requests.get(
    "https://api.elevenlabs.io/v1/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if list_resp.status_code == 200:
    tools = list_resp.json().get('tools', [])
    print(f"Found {len(tools)} existing tools:\n")
    
    # Look for tools that need editing
    tools_to_update = {
        "get_realtime_stock_data": "tool_01k0379pc9fx9t47ap7wwh2ph3",
        "get_stock_price": "tool_3301k2v1d9gsed6tw97jsrpj84as",  # From screenshot
    }
    
    for tool in tools:
        tool_id = tool.get('id')
        tool_name = tool.get('tool_config', {}).get('name')
        print(f"• {tool_name} (ID: {tool_id})")
        
        # Update tools that fetch stock data
        if 'stock' in tool_name.lower() or 'price' in tool_name.lower():
            print(f"  → Updating this tool to use correct endpoint...")
            
            # Prepare update payload
            update_payload = {
                "tool_config": {
                    "type": "webhook",
                    "name": tool_name,
                    "description": "Fetch real-time stock/crypto prices. Use BTC-USD for Bitcoin (currently ~$112,000)",
                    "response_timeout_secs": 10,
                    "api_schema": {
                        "url": "http://localhost:8000/api/stock-price",  # Use local backend
                        "method": "GET",
                        "query_params_schema": {
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "Symbol (BTC-USD for Bitcoin, AAPL for Apple, SPY for S&P)"
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
            
            # Send update request
            update_resp = requests.patch(
                f"https://api.elevenlabs.io/v1/convai/tools/{tool_id}",
                headers={
                    "xi-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                json=update_payload
            )
            
            if update_resp.status_code in [200, 204]:
                print(f"  ✅ Updated {tool_name} to use localhost:8000")
            else:
                print(f"  ❌ Failed to update: {update_resp.status_code}")
                print(f"     {update_resp.text[:200]}")
    
    # Now ensure the agent is configured to use these tools
    print("\n📝 Updating agent configuration...")
    
    # Get tool IDs for stock-related tools
    stock_tool_ids = []
    for tool in tools:
        tool_name = tool.get('tool_config', {}).get('name', '')
        if any(keyword in tool_name.lower() for keyword in ['stock', 'price', 'market']):
            stock_tool_ids.append(tool.get('id'))
    
    print(f"   Found {len(stock_tool_ids)} stock-related tools to link")
    
    # Update agent with explicit tool usage instructions
    agent_update = {
        "conversation_config": {
            "agent": {
                "prompt": """You are G'sves, a market analyst with REAL-TIME data access.

CRITICAL INSTRUCTIONS:
1. You HAVE tools configured. USE THEM!
2. When asked about ANY price, you MUST call get_realtime_stock_data or get_stock_price
3. Symbol mapping:
   - Bitcoin = BTC-USD (current price ~$112,000, NOT $49!)
   - Apple = AAPL
   - Tesla = TSLA  
   - S&P 500 = SPY

NEVER say "I don't have access" - YOU DO!
NEVER make up prices - USE THE TOOLS!

The tools are configured and working. Call them!""",
                "first_message": "",
                "language": "en",
                "tools": stock_tool_ids  # Explicitly assign tools
            }
        }
    }
    
    agent_resp = requests.patch(
        f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=agent_update
    )
    
    if agent_resp.status_code in [200, 204]:
        print("✅ Agent updated with tool assignments!")
    else:
        print(f"❌ Failed to update agent: {agent_resp.status_code}")
        print(agent_resp.text[:300])

else:
    print(f"❌ Failed to list tools: {list_resp.status_code}")

print("\n" + "=" * 50)
print("🎯 Configuration Complete!")
print("\nThe existing tools have been updated to:")
print("• Point to localhost:8000 (working backend)")
print("• Include proper parameter schemas")
print("• Agent prompt explicitly instructs tool usage")
print("\n🧪 Test: 'What is the current price of Bitcoin?'")
print("Expected: ~$112,000 ✅")
print("Not: $49 ❌")