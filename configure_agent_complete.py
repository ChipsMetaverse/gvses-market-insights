#!/usr/bin/env python3
"""
Complete configuration of ElevenLabs agent with G'sves personality and all market tools
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Complete Agent Configuration")
print("=" * 60)
print(f"Agent ID: {AGENT_ID}")
print()

# Read the G'sves personality from idealagent.md
print("📖 Reading G'sves personality from idealagent.md...")
with open('idealagent.md', 'r') as f:
    content = f.read()
    # Extract the first section (lines 1-185) which contains the complete personality
    lines = content.split('\n')
    # Take the first 185 lines which contain the complete personality and tools documentation
    personality_lines = lines[:185]
    gsves_prompt = '\n'.join(personality_lines)

print(f"   ✅ Loaded {len(personality_lines)} lines of personality")

# Get list of existing tools to find our market tools
print("\n🔍 Finding market analysis tools...")
tools_response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

tool_ids = []
tool_mapping = {}

if tools_response.status_code == 200:
    tools = tools_response.json().get('tools', [])
    
    # Market tool names we're looking for
    market_tools = [
        'get_stock_price',
        'get_stock_history', 
        'get_comprehensive_stock_data',
        'get_market_overview',
        'get_market_movers',
        'get_stock_news',
        'get_analyst_ratings',
        'get_options_chain'
    ]
    
    for tool in tools:
        tool_config = tool.get('tool_config', {})
        tool_name = tool_config.get('name', '')
        tool_id = tool.get('id')
        
        if tool_name in market_tools:
            tool_ids.append(tool_id)
            tool_mapping[tool_name] = tool_id
            print(f"   ✅ Found: {tool_name} ({tool_id})")
    
    print(f"\n   Total market tools found: {len(tool_ids)}")
else:
    print(f"   ❌ Failed to get tools: {tools_response.status_code}")
    exit(1)

# Build the agent update configuration - simplified to avoid validation errors
print("\n🔨 Building agent configuration...")
agent_config = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": gsves_prompt,
                "llm": "gpt-4o-mini",
                "temperature": 0.7,
                "max_tokens": 2000,
                "tool_ids": tool_ids
            }
        }
    },
    "name": "Gsves Market Insights"
}

print(f"   • Prompt: {len(gsves_prompt)} characters")
print(f"   • Tools: {len(tool_ids)} market tools")
print(f"   • LLM: gpt-4o-mini")
print(f"   • Temperature: 0.7")

# Update the agent
print(f"\n📡 Updating agent {AGENT_ID}...")
update_response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=agent_config
)

if update_response.status_code in [200, 204]:
    print("   ✅ Agent updated successfully!")
else:
    print(f"   ❌ Failed to update agent: {update_response.status_code}")
    print(f"   Response: {update_response.text[:500]}")
    exit(1)

# Verify the configuration
print("\n🔍 Verifying agent configuration...")
verify_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    agent_data = verify_response.json()
    
    # Check prompt
    conv_config = agent_data.get('conversation_config', {})
    agent_config = conv_config.get('agent', {})
    prompt_config = agent_config.get('prompt', {})
    
    prompt_text = prompt_config.get('prompt', '')
    assigned_tool_ids = prompt_config.get('tool_ids', [])
    
    print("\n✅ Configuration Verified:")
    print(f"   • Name: {agent_data.get('name', 'N/A')}")
    print(f"   • Prompt configured: {'Yes' if prompt_text else 'No'}")
    print(f"   • Prompt starts with: {prompt_text[:50]}..." if prompt_text else "")
    print(f"   • Tools assigned: {len(assigned_tool_ids)}")
    print(f"   • LLM: {prompt_config.get('llm', 'N/A')}")
    
    if len(assigned_tool_ids) > 0:
        print("\n   Assigned Tools:")
        for tid in assigned_tool_ids[:5]:  # Show first 5
            # Find tool name from our mapping
            tool_name = next((name for name, id in tool_mapping.items() if id == tid), tid)
            print(f"     • {tool_name}")
        if len(assigned_tool_ids) > 5:
            print(f"     ... and {len(assigned_tool_ids) - 5} more")
else:
    print(f"   ❌ Failed to verify: {verify_response.status_code}")

print("\n" + "=" * 60)
print("🎉 Agent Configuration Complete!")
print("\n📊 Test the agent with these queries:")
print('   • "What is the current price of Bitcoin?"')
print('   • "Show me the market overview"')
print('   • "What are the LTB levels for Tesla?"')
print('   • "Get me news about Apple stock"')
print("\n💡 The agent should now:")
print("   • Respond as G'sves with 30+ years experience")
print("   • Use tools to fetch real market data")
print("   • Provide LTB/ST/QE trading levels")
print("   • Give comprehensive market analysis")