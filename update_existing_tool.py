#!/usr/bin/env python3
"""
Update the existing ElevenLabs tool configuration via API
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
TOOL_ID = "tool_3301k2v1d9gsed6tw97jsrpj84as"  # From the screenshot

print("🔧 Updating ElevenLabs Tool Configuration")
print("=" * 50)

# Update the tool configuration to ensure proper parameters
tool_update = {
    "name": "get_stock_price",
    "description": "Fetches the current stock price and market data for a given stock symbol. Use this for ANY price query including stocks (AAPL, TSLA), crypto (BTC-USD), and indices (SPY).",
    "configuration": {
        "url": "https://gvses-market-insights.fly.dev/api/stock-price",
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
                "description": "Stock/crypto/index symbol (e.g., AAPL for Apple, BTC-USD for Bitcoin, SPY for S&P 500)",
                "examples": ["AAPL", "BTC-USD", "TSLA", "SPY"]
            }
        },
        "required": ["symbol"]
    }
}

# Try to update via PATCH
response = requests.patch(
    f"https://api.elevenlabs.io/v1/tools/{TOOL_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=tool_update
)

if response.status_code in [200, 204]:
    print("✅ Tool updated successfully!")
else:
    print(f"❌ Update failed: {response.status_code}")
    print(f"Response: {response.text}")

# Now let's create additional tools for market overview and news
print("\n📊 Creating additional market tools...")

# Tool 2: Market Overview
market_tool = {
    "name": "get_market_overview",
    "description": "Get overall market status including major indices (S&P 500, NASDAQ, DOW), top gainers, and losers",
    "configuration": {
        "url": "https://gvses-market-insights.fly.dev/api/market-overview",
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
    "https://api.elevenlabs.io/v1/tools",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=market_tool
)

if response.status_code == 200:
    print("✅ Created get_market_overview tool")
else:
    print(f"❌ Failed to create market overview tool: {response.status_code}")

# Tool 3: Stock News
news_tool = {
    "name": "get_stock_news",
    "description": "Get latest news and analysis for a specific stock or the general market",
    "configuration": {
        "url": "https://gvses-market-insights.fly.dev/api/stock-news",
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
                "description": "Stock symbol for news (e.g., TSLA, AAPL)"
            }
        },
        "required": ["symbol"]
    }
}

response = requests.post(
    "https://api.elevenlabs.io/v1/tools",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=news_tool
)

if response.status_code == 200:
    print("✅ Created get_stock_news tool")
else:
    print(f"❌ Failed to create news tool: {response.status_code}")

# Now update the agent's prompt to use these tools
print("\n📝 Updating agent prompt to use tools...")

agent_prompt = """You are G'sves, a senior market analyst with real-time data access.

IMPORTANT: You have access to real market data through these tools:
- get_stock_price: Use this for ANY price query (stocks, crypto, indices)
- get_market_overview: Use for market status and major indices
- get_stock_news: Use for latest news on specific stocks

When asked about prices or market data:
1. ALWAYS use the appropriate tool
2. For Bitcoin, use symbol: BTC-USD
3. For stocks, use standard symbols (AAPL, TSLA, etc.)
4. For S&P 500, use symbol: SPY

Never guess or make up prices. Always use the tools to get real data."""

response = requests.patch(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "conversation_config": {
            "agent": {
                "prompt": agent_prompt,
                "first_message": "",
                "language": "en"
            }
        }
    }
)

if response.status_code in [200, 204]:
    print("✅ Agent prompt updated!")
else:
    print(f"❌ Failed to update prompt: {response.status_code}")

print("\n" + "=" * 50)
print("🎯 Configuration Complete!")
print("\nYour agent should now:")
print("• Use the deployed backend at gvses-market-insights.fly.dev")
print("• Fetch real Bitcoin prices (~$111,000, not $49)")
print("• Access real stock and crypto data")
print("\n🧪 Test with: 'What is the current price of Bitcoin?'")