#!/usr/bin/env python3
"""
Configure ALL tools for ElevenLabs agent based on idealagent.md specifications
This script creates or updates all market analysis tools via the ElevenLabs API
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Configuring ALL ElevenLabs Agent Tools")
print("=" * 60)

# Define all tools based on idealagent.md specifications
TOOLS_DEFINITIONS = [
    # Market Data Tools
    {
        "name": "get_stock_price",
        "description": "Fetches real-time stock, cryptocurrency, or index prices with current market data",
        "endpoint": "/api/stock-price",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock/crypto/index symbol (e.g., AAPL, BTC-USD, SPY)",
                "required": True
            }
        }
    },
    {
        "name": "get_stock_history",
        "description": "Retrieves historical price data and candlestick information for technical analysis",
        "endpoint": "/api/stock-history",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            },
            "days": {
                "type": "integer",
                "description": "Number of days of history (default 100)",
                "required": False
            }
        }
    },
    {
        "name": "get_comprehensive_stock_data",
        "description": "Provides complete stock information including fundamentals, technicals, and key metrics",
        "endpoint": "/api/comprehensive-stock-data",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    },
    {
        "name": "get_market_overview",
        "description": "Gets overall market status including major indices and market movers",
        "endpoint": "/api/market-overview",
        "parameters": {}
    },
    {
        "name": "get_market_movers",
        "description": "Identifies trending stocks and unusual market activity",
        "endpoint": "/api/market-movers",
        "parameters": {}
    },
    
    # News & Analysis Tools
    {
        "name": "get_stock_news",
        "description": "Retrieves latest news for specific stocks using hybrid CNBC + Yahoo Finance sources",
        "endpoint": "/api/stock-news",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol for news lookup",
                "required": True
            }
        }
    },
    {
        "name": "get_analyst_ratings",
        "description": "Gets professional analyst recommendations and price targets",
        "endpoint": "/api/analyst-ratings",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    },
    
    # Options Trading Tools
    {
        "name": "get_options_chain",
        "description": "Retrieves complete options chain with strikes, expiries, and Greeks",
        "endpoint": "/api/options-chain",
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    },
]

def create_tool_config(tool_def: Dict) -> Dict:
    """Create ElevenLabs tool configuration from our definition"""
    
    # Build parameters schema
    properties = {}
    required = []
    
    for param_name, param_info in tool_def.get("parameters", {}).items():
        properties[param_name] = {
            "type": param_info["type"],
            "description": param_info["description"]
        }
        if param_info.get("required", False):
            required.append(param_name)
    
    # Build the tool configuration
    config = {
        "name": tool_def["name"],
        "description": tool_def["description"],
        "type": "webhook",
        "response_timeout_secs": 30,
        "api_schema": {
            "url": f"{BACKEND_URL}{tool_def['endpoint']}",
            "method": "GET"
        }
    }
    
    # Add query params schema only if there are parameters
    if properties:
        config["api_schema"]["query_params_schema"] = {
            "properties": properties,
            "required": required
        }
    
    return config

def create_tool(tool_config: Dict) -> Optional[str]:
    """Create a single tool via ElevenLabs API"""
    
    # Create tool endpoint
    response = requests.post(
        f"{BASE_URL}/convai/tools",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={"tool_config": tool_config}
    )
    
    if response.status_code in [200, 201]:
        tool_data = response.json()
        tool_id = tool_data.get('id')
        print(f"  ✅ Created: {tool_config['name']} (ID: {tool_id})")
        return tool_id
    else:
        print(f"  ❌ Failed: {tool_config['name']}")
        print(f"     Status: {response.status_code}")
        print(f"     Error: {response.text[:200]}")
        return None

def list_existing_tools() -> List[Dict]:
    """List all existing tools in the workspace"""
    
    response = requests.get(
        f"{BASE_URL}/convai/tools",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('tools', [])
    else:
        print(f"Failed to list existing tools: {response.status_code}")
        return []

def delete_tool(tool_id: str, tool_name: str) -> bool:
    """Delete a tool by ID"""
    
    response = requests.delete(
        f"{BASE_URL}/convai/tools/{tool_id}",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code in [200, 204]:
        print(f"  🗑️  Deleted: {tool_name}")
        return True
    else:
        print(f"  ❌ Failed to delete: {tool_name}")
        return False

def assign_tools_to_agent(tool_ids: List[str]) -> bool:
    """Assign tools to the agent"""
    
    # Update agent with tool IDs
    response = requests.patch(
        f"{BASE_URL}/convai/agents/{AGENT_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={"tool_ids": tool_ids}
    )
    
    if response.status_code in [200, 204]:
        print(f"\n✅ Successfully assigned {len(tool_ids)} tools to agent!")
        return True
    else:
        print(f"\n❌ Failed to assign tools to agent")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {response.text[:200]}")
        return False

def main():
    """Main configuration flow"""
    
    # Step 1: List existing tools
    print("\n📋 Checking existing tools...")
    existing_tools = list_existing_tools()
    
    if existing_tools:
        print(f"Found {len(existing_tools)} existing tools:")
        existing_names = {}
        for tool in existing_tools:
            tool_config = tool.get('tool_config', {})
            name = tool_config.get('name', 'unnamed')
            tool_id = tool.get('id')
            existing_names[name] = tool_id
            print(f"  • {name} (ID: {tool_id})")
        
        # Default to keeping existing tools and adding missing ones
        print("\n⚠️  Existing tools found!")
        print("→ Keeping existing tools and adding missing ones...")
        
        # Uncomment the following to delete all existing tools first:
        # print("\n🗑️  Deleting existing tools...")
        # for tool in existing_tools:
        #     tool_id = tool.get('id')
        #     tool_name = tool.get('tool_config', {}).get('name', 'unnamed')
        #     delete_tool(tool_id, tool_name)
        # existing_names = {}
    else:
        print("No existing tools found.")
        existing_names = {}
    
    # Step 2: Create tools
    print(f"\n🔨 Creating tools...")
    created_tool_ids = []
    
    for tool_def in TOOLS_DEFINITIONS:
        tool_name = tool_def["name"]
        
        # Skip if tool already exists and we're keeping existing
        if tool_name in existing_names:
            print(f"  ⏭️  Skipping: {tool_name} (already exists)")
            created_tool_ids.append(existing_names[tool_name])
            continue
        
        # Create tool configuration
        tool_config = create_tool_config(tool_def)
        
        # Create the tool
        tool_id = create_tool(tool_config)
        if tool_id:
            created_tool_ids.append(tool_id)
    
    # Step 3: Assign tools to agent
    if created_tool_ids:
        print(f"\n🔗 Assigning {len(created_tool_ids)} tools to agent...")
        assign_tools_to_agent(created_tool_ids)
    
    # Step 4: Verify configuration
    print("\n📊 Final Configuration Summary:")
    print("=" * 60)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Total Tools Configured: {len(created_tool_ids)}")
    
    print("\n📝 Tool Categories:")
    print("  • Market Data: 5 tools")
    print("  • News & Analysis: 2 tools")
    print("  • Options Trading: 1 tool")
    
    print("\n⚠️  Important Notes:")
    print("  1. Ensure backend is running at", BACKEND_URL)
    print("  2. Some tools may require additional backend endpoints")
    print("  3. Technical analysis tools need backend implementation")
    print("  4. Alpaca tools require ALPACA_API_KEY configuration")
    
    print("\n🧪 Test Commands:")
    print('  • "What is the current price of Bitcoin?"')
    print('  • "Show me the market overview"')
    print('  • "Get news for Tesla"')
    print('  • "Analyze AAPL options chain"')
    
    print("\n✨ Configuration complete!")

if __name__ == "__main__":
    main()