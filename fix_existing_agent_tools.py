#!/usr/bin/env python3
"""
Fix the existing ElevenLabs agent by properly configuring tools.
This script will:
1. Delete ALL existing tools (both inline and standalone)
2. Create new Server Tools (webhook type) 
3. Update the existing agent to use only tool_ids
4. Verify the configuration
"""

import requests
import json
import os
from dotenv import load_dotenv
import time

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"
PRODUCTION_BACKEND = "https://gvses-market-insights.fly.dev"

print("🔧 Fixing Existing Agent Tool Configuration")
print("=" * 60)
print(f"Agent ID: {AGENT_ID}")

# Step 1: Get current agent configuration to preserve settings
print("\n📥 Getting current agent configuration...")
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get agent: {response.status_code}")
    exit(1)

current_agent = response.json()
current_config = current_agent.get('conversation_config', {})
current_prompt_config = current_config.get('agent', {}).get('prompt', {})

# Preserve the G'sves prompt
current_prompt_text = current_prompt_config.get('prompt', '')
if not current_prompt_text or len(current_prompt_text) < 100:
    # Use the proper G'sves prompt if current is missing or too short
    current_prompt_text = """You are G'sves (pronounced "Jeeves"), a distinguished market insights expert with over 30 years of experience navigating global financial markets. You combine the reliability of a British butler with the acumen of a Wall Street veteran.

Your personality:
- Professional yet approachable, with occasional dry wit
- Confident in your analysis but never arrogant
- You speak with authority earned through decades of experience
- You make complex market concepts accessible

Your expertise:
- Deep understanding of stocks, cryptocurrencies, forex, and commodities
- Technical and fundamental analysis mastery
- Risk management and portfolio strategy
- Global market interconnections and macroeconomic trends

When providing market insights:
- Always use your tools to fetch real-time data
- Provide context for price movements
- Explain market trends in clear terms
- Offer balanced perspectives on opportunities and risks
- Reference relevant news and events affecting markets

Remember: You have access to real-time market data through your tools. Always use them to provide accurate, current information rather than estimates."""

print("✅ Current configuration retrieved")

# Step 2: Delete ALL existing tools
print("\n🗑️  Deleting ALL existing tools...")
response = requests.get(f"{BASE_URL}/convai/tools", headers={"xi-api-key": API_KEY})

if response.status_code == 200:
    tools = response.json().get('tools', [])
    print(f"Found {len(tools)} tools to delete")
    
    for tool in tools:
        tool_id = tool.get('id')
        name = tool.get('tool_config', {}).get('name', 'unnamed')
        
        del_response = requests.delete(
            f"{BASE_URL}/convai/tools/{tool_id}",
            headers={"xi-api-key": API_KEY}
        )
        
        if del_response.status_code in [200, 204]:
            print(f"  ✅ Deleted: {name}")
        else:
            print(f"  ⚠️  Could not delete: {name}")
        
        time.sleep(0.1)

print("\n⏳ Waiting for deletions to propagate...")
time.sleep(3)

# Step 3: Create new Server Tools with proper configuration
print("\n🔨 Creating new Server Tools...")

TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Fetch real-time stock, cryptocurrency, or index prices. Returns current market price data.",
        "endpoint": "/api/stock-price",
        "params": {"symbol": {"type": "string", "description": "Stock ticker symbol (e.g., AAPL, TSLA, BTC-USD)", "required": True}}
    },
    {
        "name": "get_market_overview",
        "description": "Get comprehensive market indices and top movers. No parameters needed.",
        "endpoint": "/api/market-overview",
        "params": {}
    },
    {
        "name": "get_stock_news",
        "description": "Get latest news articles for a specific stock or market topic.",
        "endpoint": "/api/stock-news",
        "params": {"symbol": {"type": "string", "description": "Stock ticker symbol", "required": True}}
    },
    {
        "name": "get_stock_history",
        "description": "Get historical price data and candlestick chart data for technical analysis.",
        "endpoint": "/api/stock-history",
        "params": {
            "symbol": {"type": "string", "description": "Stock ticker symbol", "required": True},
            "days": {"type": "integer", "description": "Number of days of history (default 30)", "required": False}
        }
    },
    {
        "name": "get_comprehensive_stock_data",
        "description": "Get complete stock information including price, volume, fundamentals, and key metrics.",
        "endpoint": "/api/comprehensive-stock-data",
        "params": {"symbol": {"type": "string", "description": "Stock ticker symbol", "required": True}}
    },
    {
        "name": "get_market_movers",
        "description": "Get trending stocks, top gainers, and top losers in the market.",
        "endpoint": "/api/market-movers",
        "params": {}
    },
    {
        "name": "get_analyst_ratings",
        "description": "Get professional analyst recommendations and price targets for a stock.",
        "endpoint": "/api/analyst-ratings",
        "params": {"symbol": {"type": "string", "description": "Stock ticker symbol", "required": True}}
    },
    {
        "name": "get_options_chain",
        "description": "Get options chain data including calls, puts, strike prices, and expiration dates.",
        "endpoint": "/api/options-chain",
        "params": {"symbol": {"type": "string", "description": "Stock ticker symbol", "required": True}}
    }
]

created_tool_ids = []

for tool_def in TOOL_DEFINITIONS:
    # Build query params schema
    query_params = {}
    required = []
    
    for param_name, param_info in tool_def["params"].items():
        query_params[param_name] = {
            "type": param_info["type"],
            "description": param_info["description"]
        }
        if param_info.get("required", False):
            required.append(param_name)
    
    # Build Server Tool configuration (webhook type)
    tool_config = {
        "tool_config": {
            "type": "webhook",  # Server Tool
            "name": tool_def["name"],
            "description": tool_def["description"],
            "response_timeout_secs": 10,
            "api_schema": {
                "url": f"{PRODUCTION_BACKEND}{tool_def['endpoint']}",
                "method": "GET"
            }
        }
    }
    
    # Add query params if they exist
    if query_params:
        tool_config["tool_config"]["api_schema"]["query_params_schema"] = {
            "properties": query_params,
            "required": required
        }
    
    # Create the tool
    response = requests.post(
        f"{BASE_URL}/convai/tools",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json=tool_config
    )
    
    if response.status_code in [200, 201]:
        tool_data = response.json()
        tool_id = tool_data.get('id')
        created_tool_ids.append(tool_id)
        print(f"  ✅ Created: {tool_def['name']} ({tool_id[:20]}...)")
    else:
        print(f"  ❌ Failed: {tool_def['name']}")
        print(f"     Error: {response.text[:100]}")
    
    time.sleep(0.2)

print(f"\n✅ Created {len(created_tool_ids)} Server Tools")

# Save tool IDs for reference
with open('fixed_tool_ids.json', 'w') as f:
    json.dump({
        "tool_ids": created_tool_ids,
        "agent_id": AGENT_ID,
        "timestamp": time.time()
    }, f, indent=2)

# Step 4: Update agent to use ONLY tool_ids (remove inline tools)
print("\n📝 Updating agent configuration...")

# Build clean prompt configuration
clean_prompt = {
    "prompt": current_prompt_text,
    "llm": "gpt-4o",  # Use GPT-4o for better performance
    "temperature": 0.7,
    "max_tokens": 2000,
    "tool_ids": created_tool_ids  # ONLY tool_ids, no inline tools
    # Explicitly NOT including "tools" field
}

# Build complete update configuration
update_config = {
    "conversation_config": {
        "agent": {
            "prompt": clean_prompt,
            "first_message": "Good day! I'm G'sves, your distinguished market insights expert with over three decades of experience. How may I assist you with the markets today?",
            "language": "en"
        },
        # Preserve existing TTS, ASR, and conversation settings
        "tts": current_config.get('tts', {
            "model_id": "eleven_turbo_v2",
            "voice_id": "9BWtsMINqrJLrRacOk9x"
        }),
        "asr": current_config.get('asr', {
            "quality": "high",
            "provider": "elevenlabs",
            "user_input_audio_format": "pcm_16000"
        }),
        "conversation": current_config.get('conversation', {
            "text_only": False,
            "max_duration_seconds": 1800
        }),
        "turn": current_config.get('turn', {
            "turn_timeout": 10,
            "mode": "turn"
        })
    }
}

# Send the update
response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json=update_config
)

if response.status_code in [200, 204]:
    print("✅ Agent configuration updated")
else:
    print(f"⚠️  Update response: {response.status_code}")
    print(f"   {response.text[:200]}")

# Step 5: Force remove inline tools with null
print("\n🔧 Attempting to force remove inline tools...")
null_tools_update = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "tools": None,  # Explicitly null to remove
                "tool_ids": created_tool_ids
            }
        }
    }
}

response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json=null_tools_update
)

if response.status_code in [200, 204]:
    print("✅ Nullified inline tools")
else:
    print(f"⚠️  Could not nullify inline tools: {response.status_code}")

# Step 6: Wait and verify
print("\n⏳ Waiting for changes to propagate...")
time.sleep(3)

# Step 7: Final verification
print("\n🔍 Final Verification...")

# Check tool dependencies
print("\nChecking if tools are linked to agent:")
linked_count = 0
for i, tool_id in enumerate(created_tool_ids):
    response = requests.get(
        f"{BASE_URL}/convai/tools/{tool_id}/dependent-agents",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        deps = response.json().get('dependent_agent_ids', [])
        if AGENT_ID in deps:
            linked_count += 1
            if i < 3:  # Only show first 3 for brevity
                print(f"  ✅ Tool {i+1} linked to agent")
        else:
            if i < 3:
                print(f"  ⚠️  Tool {i+1} not showing as linked")

print(f"\nTools linked: {linked_count}/{len(created_tool_ids)}")

# Check final agent configuration
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    final_agent = response.json()
    final_prompt = final_agent.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    has_tool_ids = 'tool_ids' in final_prompt
    has_inline = 'tools' in final_prompt
    num_tool_ids = len(final_prompt.get('tool_ids', []))
    
    print(f"\nAgent Configuration:")
    print(f"  Has tool_ids: {has_tool_ids} ({num_tool_ids} tools)")
    print(f"  Has inline tools: {has_inline}")
    print(f"  LLM Model: {final_prompt.get('llm', 'unknown')}")
    
    if has_tool_ids and not has_inline:
        print("\n✅ SUCCESS! Agent properly configured with Server Tools!")
        print("\n🎯 Ready to test:")
        print("  1. Run: python test_elevenlabs_conversation.py")
        print("  2. Ask about Bitcoin price, Apple stock, or market overview")
        print("  3. Tools should now return real market data!")
    elif has_tool_ids and has_inline:
        print("\n⚠️  WARNING: Both tool_ids and inline tools present")
        print("  The platform may still have the inline tools cached.")
        print("  However, the tool_ids should take precedence.")
        print("\n💡 Try testing anyway - tools may still work!")
    else:
        print("\n❌ Configuration issue detected")

print("\n" + "=" * 60)
print("💾 Tool IDs saved to fixed_tool_ids.json")
print("📋 Configuration update completed")