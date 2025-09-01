#!/usr/bin/env python3
"""
Complete cleanup and proper tool setup for ElevenLabs agent
This will:
1. Delete ALL existing tools
2. Create new tools properly
3. Assign them to the agent correctly
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

print("🧹 Complete Tools Cleanup and Setup")
print("=" * 60)

# Tool definitions
TOOL_DEFINITIONS = [
    {
        "name": "get_stock_price",
        "description": "Fetch real-time stock, cryptocurrency, or index prices",
        "endpoint": "/api/stock-price",
        "params": {"symbol": {"type": "string", "description": "Stock/crypto symbol (AAPL, BTC-USD)", "required": True}}
    },
    {
        "name": "get_market_overview", 
        "description": "Get market indices and movers",
        "endpoint": "/api/market-overview",
        "params": {}
    },
    {
        "name": "get_stock_news",
        "description": "Get latest news for a stock",
        "endpoint": "/api/stock-news",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_stock_history",
        "description": "Get historical price data",
        "endpoint": "/api/stock-history",
        "params": {
            "symbol": {"type": "string", "description": "Stock symbol", "required": True},
            "days": {"type": "integer", "description": "Number of days", "required": False}
        }
    },
    {
        "name": "get_comprehensive_stock_data",
        "description": "Get complete stock information",
        "endpoint": "/api/comprehensive-stock-data",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_market_movers",
        "description": "Get trending stocks",
        "endpoint": "/api/market-movers",
        "params": {}
    },
    {
        "name": "get_analyst_ratings",
        "description": "Get analyst recommendations",
        "endpoint": "/api/analyst-ratings",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    },
    {
        "name": "get_options_chain",
        "description": "Get options chain data",
        "endpoint": "/api/options-chain",
        "params": {"symbol": {"type": "string", "description": "Stock symbol", "required": True}}
    }
]

# Step 1: Delete ALL existing tools
print("\n🗑️  STEP 1: Deleting ALL existing tools...")
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
            print(f"  ❌ Failed to delete: {name}")
        
        time.sleep(0.1)

print("\n⏳ Waiting for deletions to propagate...")
time.sleep(2)

# Step 2: Create new tools
print("\n🔨 STEP 2: Creating fresh tools...")
created_tool_ids = []

for tool_def in TOOL_DEFINITIONS:
    # Build query params
    query_params = {}
    required = []
    
    for param_name, param_info in tool_def["params"].items():
        query_params[param_name] = {
            "type": param_info["type"],
            "description": param_info["description"]
        }
        if param_info.get("required", False):
            required.append(param_name)
    
    # Build tool config
    tool_config = {
        "tool_config": {
            "type": "webhook",
            "name": tool_def["name"],
            "description": tool_def["description"],
            "response_timeout_secs": 10,
            "api_schema": {
                "url": f"{PRODUCTION_BACKEND}{tool_def['endpoint']}",
                "method": "GET"
            }
        }
    }
    
    if query_params:
        tool_config["tool_config"]["api_schema"]["query_params_schema"] = {
            "properties": query_params,
            "required": required
        }
    
    # Create tool
    response = requests.post(
        f"{BASE_URL}/convai/tools",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json=tool_config
    )
    
    if response.status_code in [200, 201]:
        tool_data = response.json()
        tool_id = tool_data.get('id')
        created_tool_ids.append(tool_id)
        print(f"  ✅ Created: {tool_def['name']} ({tool_id})")
    else:
        print(f"  ❌ Failed: {tool_def['name']}")
        print(f"     {response.text[:100]}")
    
    time.sleep(0.2)

print(f"\n✅ Created {len(created_tool_ids)} tools")

# Step 3: Update agent to use ONLY tool_ids (no inline tools)
print("\n🔧 STEP 3: Updating agent configuration...")

# Get current agent config
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get agent: {response.status_code}")
    exit(1)

agent_data = response.json()
current_config = agent_data.get('conversation_config', {})
current_prompt = current_config.get('agent', {}).get('prompt', {})

# Build update with ONLY tool_ids
update_config = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": current_prompt.get('prompt', ''),
                "llm": "gpt-4o",
                "temperature": 0.7,
                "max_tokens": 2000,
                "tool_ids": created_tool_ids  # ONLY tool_ids, no inline tools
            },
            "first_message": "Hello! I'm G'sves, your market insights expert. How can I help you today?",
            "language": "en"
        }
    }
}

# Update agent
response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json=update_config
)

if response.status_code in [200, 204]:
    print("✅ Agent updated with tool_ids")
else:
    print(f"❌ Failed to update agent: {response.status_code}")
    print(f"   {response.text[:200]}")

# Step 4: Verify everything
print("\n🔍 STEP 4: Verification...")
time.sleep(2)

# Check tools have agent as dependent
print("\nChecking tool dependencies:")
for tool_id in created_tool_ids[:3]:  # Check first 3
    response = requests.get(
        f"{BASE_URL}/convai/tools/{tool_id}/dependent-agents",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        deps = response.json().get('dependent_agent_ids', [])
        if AGENT_ID in deps:
            print(f"  ✅ Tool {tool_id[:20]}... linked to agent")
        else:
            print(f"  ❌ Tool {tool_id[:20]}... NOT linked to agent")

# Check agent config
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    agent_data = response.json()
    prompt = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    has_tool_ids = 'tool_ids' in prompt
    has_inline = 'tools' in prompt
    num_tools = len(prompt.get('tool_ids', []))
    
    print(f"\nAgent configuration:")
    print(f"  Has tool_ids: {has_tool_ids} ({num_tools} tools)")
    print(f"  Has inline tools: {has_inline}")
    
    if has_tool_ids and not has_inline:
        print("\n✅ SUCCESS! Agent properly configured with tool_ids only!")
    else:
        print("\n⚠️  Configuration may still have issues")

# Save tool IDs
with open('fresh_tool_ids.json', 'w') as f:
    json.dump({
        "tool_ids": created_tool_ids,
        "agent_id": AGENT_ID,
        "timestamp": time.time()
    }, f, indent=2)

print(f"\n💾 Tool IDs saved to fresh_tool_ids.json")
print("\n✨ Complete! Test the agent now.")
print("=" * 60)