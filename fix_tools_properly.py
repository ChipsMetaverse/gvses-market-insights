#!/usr/bin/env python3
"""
Fix ElevenLabs tools properly by:
1. Deleting all existing tools
2. Creating new tools with correct configuration
3. Returning the tool IDs for agent configuration
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import time

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
BASE_URL = "https://api.elevenlabs.io/v1"
PRODUCTION_BACKEND = "https://gvses-market-insights.fly.dev"

print("🔧 Fixing ElevenLabs Tools Properly")
print("=" * 60)

# Define the correct tool configurations
TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Fetch real-time stock, cryptocurrency, or index prices. Use BTC-USD for Bitcoin, AAPL for stocks, SPY for indices.",
        "endpoint": "/api/stock-price",
        "timeout": 10,
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock/crypto/index symbol (e.g., AAPL, BTC-USD, SPY)",
                "required": True
            }
        }
    },
    {
        "name": "get_market_overview",
        "description": "Get overall market status including major indices and market movers",
        "endpoint": "/api/market-overview",
        "timeout": 10,
        "parameters": {}
    },
    {
        "name": "get_stock_news",
        "description": "Retrieve latest news for specific stocks from CNBC and Yahoo Finance",
        "endpoint": "/api/stock-news",
        "timeout": 10,
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol for news lookup",
                "required": True
            }
        }
    },
    {
        "name": "get_stock_history",
        "description": "Retrieve historical price data for technical analysis",
        "endpoint": "/api/stock-history",
        "timeout": 15,
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
        "description": "Get complete stock information including fundamentals and technicals",
        "endpoint": "/api/comprehensive-stock-data",
        "timeout": 20,
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    },
    {
        "name": "get_market_movers",
        "description": "Identify trending stocks and unusual market activity",
        "endpoint": "/api/market-movers",
        "timeout": 15,
        "parameters": {}
    },
    {
        "name": "get_analyst_ratings",
        "description": "Get professional analyst recommendations and price targets",
        "endpoint": "/api/analyst-ratings",
        "timeout": 15,
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    },
    {
        "name": "get_options_chain",
        "description": "Retrieve complete options chain with strikes and expiries",
        "endpoint": "/api/options-chain",
        "timeout": 20,
        "parameters": {
            "symbol": {
                "type": "string",
                "description": "Stock symbol",
                "required": True
            }
        }
    }
]

def delete_all_existing_tools():
    """Delete all existing market-related tools"""
    print("\n🗑️  Step 1: Cleaning up existing tools...")
    
    # Get all tools
    response = requests.get(
        f"{BASE_URL}/convai/tools",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get tools: {response.status_code}")
        return False
    
    tools = response.json().get('tools', [])
    deleted_count = 0
    
    for tool in tools:
        tool_id = tool.get('id')
        config = tool.get('tool_config', {})
        name = config.get('name', '')
        
        # Delete if it's a market-related tool
        if any(keyword in name.lower() for keyword in ['stock', 'market', 'analyst', 'options']):
            delete_response = requests.delete(
                f"{BASE_URL}/convai/tools/{tool_id}",
                headers={"xi-api-key": API_KEY}
            )
            
            if delete_response.status_code in [200, 204]:
                print(f"   ✅ Deleted: {name} ({tool_id})")
                deleted_count += 1
            else:
                print(f"   ❌ Failed to delete: {name}")
            
            # Small delay to avoid rate limiting
            time.sleep(0.2)
    
    print(f"   Total deleted: {deleted_count} tools")
    return True

def create_tool(tool_def: Dict) -> Optional[str]:
    """Create a single tool and return its ID"""
    
    # Build query parameters schema
    query_params = {}
    required_params = []
    
    for param_name, param_info in tool_def.get("parameters", {}).items():
        query_params[param_name] = {
            "type": param_info["type"],
            "description": param_info["description"]
        }
        if param_info.get("required", False):
            required_params.append(param_name)
    
    # Build tool configuration
    tool_config = {
        "tool_config": {
            "type": "webhook",
            "name": tool_def["name"],
            "description": tool_def["description"],
            "response_timeout_secs": tool_def["timeout"],
            "api_schema": {
                "url": f"{PRODUCTION_BACKEND}{tool_def['endpoint']}",
                "method": "GET"
            }
        }
    }
    
    # Add query parameters only if there are any
    if query_params:
        tool_config["tool_config"]["api_schema"]["query_params_schema"] = {
            "properties": query_params,
            "required": required_params
        }
    
    # Create the tool
    response = requests.post(
        f"{BASE_URL}/convai/tools",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=tool_config
    )
    
    if response.status_code in [200, 201]:
        tool_data = response.json()
        tool_id = tool_data.get('id')
        print(f"   ✅ Created: {tool_def['name']} (ID: {tool_id})")
        return tool_id
    else:
        print(f"   ❌ Failed: {tool_def['name']}")
        print(f"      Status: {response.status_code}")
        print(f"      Error: {response.text[:200]}")
        return None

def create_all_tools() -> List[str]:
    """Create all tools and return their IDs"""
    print("\n🔨 Step 2: Creating new tools...")
    
    tool_ids = []
    for tool_def in TOOL_DEFINITIONS:
        tool_id = create_tool(tool_def)
        if tool_id:
            tool_ids.append(tool_id)
        
        # Small delay to avoid rate limiting
        time.sleep(0.3)
    
    return tool_ids

def verify_tools(tool_ids: List[str]):
    """Verify the created tools"""
    print("\n🔍 Step 3: Verifying created tools...")
    
    for tool_id in tool_ids:
        response = requests.get(
            f"{BASE_URL}/convai/tools/{tool_id}",
            headers={"xi-api-key": API_KEY}
        )
        
        if response.status_code == 200:
            tool_data = response.json()
            config = tool_data.get('tool_config', {})
            name = config.get('name')
            url = config.get('api_schema', {}).get('url', '')
            
            # Check if URL is correct
            if PRODUCTION_BACKEND in url:
                print(f"   ✅ {name}: Correct URL")
            else:
                print(f"   ❌ {name}: Wrong URL - {url}")
        else:
            print(f"   ❌ Failed to verify tool {tool_id}")

def main():
    """Main execution flow"""
    
    # Step 1: Delete existing tools
    if not delete_all_existing_tools():
        print("\n❌ Failed to clean up existing tools")
        return
    
    # Step 2: Create new tools
    tool_ids = create_all_tools()
    
    if not tool_ids:
        print("\n❌ No tools were created")
        return
    
    print(f"\n✅ Successfully created {len(tool_ids)} tools")
    
    # Step 3: Verify tools
    verify_tools(tool_ids)
    
    # Step 4: Save tool IDs for agent configuration
    tool_ids_file = "tool_ids.json"
    with open(tool_ids_file, 'w') as f:
        json.dump({
            "tool_ids": tool_ids,
            "tool_names": [tool_def["name"] for tool_def in TOOL_DEFINITIONS]
        }, f, indent=2)
    
    print(f"\n💾 Tool IDs saved to {tool_ids_file}")
    
    # Step 5: Display tool IDs for agent configuration
    print("\n📋 Tool IDs for agent configuration:")
    print("=" * 60)
    print("tool_ids = [")
    for tool_id in tool_ids:
        print(f'    "{tool_id}",')
    print("]")
    
    print("\n✨ Next steps:")
    print("1. Update agent configuration with these tool IDs")
    print("2. Remove inline tools from agent config")
    print("3. Sync via ConvAI CLI")
    print("4. Test with simulation API")

if __name__ == "__main__":
    main()