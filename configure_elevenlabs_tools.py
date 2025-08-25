#!/usr/bin/env python3
"""
Configure ElevenLabs agent with webhook tools for stock data.
"""

import os
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
    print("❌ Missing ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID in backend/.env")
    exit(1)

# Tool configuration
tools_config = [
    {
        "type": "webhook",
        "name": "get_stock_price",
        "description": "Fetches the current stock price and comprehensive market data for a given stock symbol. Use this whenever the user asks about stock prices, market data, or wants information about a specific company's stock.",
        "webhook": {
            "url": "https://gvses-market-insights.fly.dev/api/stock-price",
            "method": "GET",
            "headers": {},
            "query_parameters": {
                "symbol": {
                    "type": "string",
                    "required": True,
                    "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA, NVDA)"
                }
            }
        }
    }
]

async def update_agent_tools():
    """Update the ElevenLabs agent with the tools configuration."""
    
    async with httpx.AsyncClient() as client:
        # First, get the current agent configuration
        print(f"📥 Fetching current agent configuration...")
        response = await client.get(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch agent: {response.status_code} - {response.text}")
            return False
        
        agent_config = response.json()
        print(f"✅ Got agent: {agent_config.get('name', 'Unknown')}")
        
        # Update the conversation_config with tools
        if 'conversation_config' not in agent_config:
            agent_config['conversation_config'] = {}
        
        if 'agent' not in agent_config['conversation_config']:
            agent_config['conversation_config']['agent'] = {}
        
        # Set the tools
        agent_config['conversation_config']['agent']['tools'] = tools_config
        
        # Also ensure the agent has a good prompt for using tools
        current_prompt = agent_config['conversation_config']['agent'].get('prompt', {})
        if isinstance(current_prompt, dict):
            prompt_text = current_prompt.get('prompt', '')
        else:
            prompt_text = current_prompt or ''
        
        # Add tool usage instructions if not present
        if 'get_stock_price' not in prompt_text:
            tool_instructions = """

## Tool Usage
You have access to the get_stock_price tool. Use it whenever users ask about:
- Current stock prices
- Market data for specific companies
- Stock performance
- Company valuations

Always call the tool to get real-time data rather than saying you cannot access it.
"""
            prompt_text = prompt_text + tool_instructions
            agent_config['conversation_config']['agent']['prompt'] = {
                "prompt": prompt_text
            }
        
        # Update the agent
        print(f"🔧 Updating agent with tools configuration...")
        update_response = await client.patch(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json=agent_config
        )
        
        if update_response.status_code == 200:
            print(f"✅ Successfully updated agent with tools!")
            
            # Verify the update
            verify_response = await client.get(
                f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
                headers={"xi-api-key": ELEVENLABS_API_KEY}
            )
            
            if verify_response.status_code == 200:
                updated_config = verify_response.json()
                tools = updated_config.get('conversation_config', {}).get('agent', {}).get('tools', [])
                print(f"📋 Agent now has {len(tools)} tool(s) configured:")
                for tool in tools:
                    print(f"   - {tool.get('name', 'Unknown')}: {tool.get('type', 'Unknown type')}")
            
            return True
        else:
            print(f"❌ Failed to update agent: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False

if __name__ == "__main__":
    import asyncio
    print("🔧 ElevenLabs Tools Configuration")
    print("=" * 50)
    asyncio.run(update_agent_tools())