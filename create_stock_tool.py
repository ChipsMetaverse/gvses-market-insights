#!/usr/bin/env python3
"""
Create a stock price tool for the ElevenLabs agent.
This creates a webhook tool that can fetch real-time stock prices.
"""

import os
import json
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")

def create_stock_price_tool():
    """Create a stock price fetching tool for ElevenLabs agents."""
    
    # Tool configuration - webhook type with api_schema  
    tool_config = {
        "tool_config": {
            "type": "webhook",
            "name": "get_stock_price",
            "description": "Fetches the current stock price and market data for a given stock symbol",
            "api_schema": {
                "url": "http://localhost:8000/api/stock-price",
                "method": "GET",
                "path_params_schema": {},
                "query_params_schema": {
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock ticker symbol (e.g., AAPL, GOOGL, TSLA)"
                        }
                    },
                    "required": ["symbol"]
                },
                "request_headers": {}
            }
        }
    }
    
    # Create the tool via API
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = httpx.post(
        "https://api.elevenlabs.io/v1/convai/tools",
        headers=headers,
        json=tool_config
    )
    
    if response.status_code == 200 or response.status_code == 201:
        tool_data = response.json()
        print(f"✅ Tool created successfully!")
        tool_id = tool_data.get('tool_id') or tool_data.get('id')
        print(f"Tool ID: {tool_id}")
        return tool_id
    else:
        print(f"❌ Failed to create tool: {response.status_code}")
        print(response.text)
        return None


def create_market_overview_tool():
    """Create a market overview tool for ElevenLabs agents."""
    
    tool_config = {
        "tool_config": {
            "type": "webhook", 
            "name": "get_market_overview",
            "description": "Gets an overview of major market indices and movers",
            "api_schema": {
                "url": "http://localhost:8000/api/market-overview",
                "method": "GET",
                "path_params_schema": {},
                "query_params_schema": {
                    "properties": {}
                },
                "request_headers": {}
            }
        }
    }
    
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = httpx.post(
        "https://api.elevenlabs.io/v1/convai/tools",
        headers=headers,
        json=tool_config
    )
    
    if response.status_code == 200 or response.status_code == 201:
        tool_data = response.json()
        print(f"✅ Market overview tool created!")
        print(f"Tool ID: {tool_data.get('tool_id')}")
        return tool_data.get('tool_id')
    else:
        print(f"❌ Failed to create tool: {response.status_code}")
        print(response.text)
        return None


def main():
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found in environment")
        return
    
    print("🛠️ Creating ElevenLabs tools for G'sves agent...")
    print("=" * 50)
    
    # Create tools
    stock_tool_id = create_stock_price_tool()
    market_tool_id = create_market_overview_tool()
    
    if stock_tool_id and market_tool_id:
        print(f"\n✅ Tools created successfully!")
        print(f"\nNext steps:")
        print(f"1. Add these tool IDs to your agent configuration:")
        print(f"   - Stock Price Tool: {stock_tool_id}")
        print(f"   - Market Overview Tool: {market_tool_id}")
        print(f"2. Create the webhook endpoints in your backend")
        print(f"3. Sync the agent configuration")
        
        # Save tool IDs for reference
        tool_ids = {
            "stock_price_tool": stock_tool_id,
            "market_overview_tool": market_tool_id
        }
        
        with open("tool_ids.json", "w") as f:
            json.dump(tool_ids, f, indent=2)
            print(f"\nTool IDs saved to tool_ids.json")


if __name__ == "__main__":
    main()