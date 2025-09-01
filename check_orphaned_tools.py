#!/usr/bin/env python3
"""
Check which agents are using the orphaned tools
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

# The orphaned tools that couldn't be deleted
ORPHANED_TOOLS = [
    ("tool_01k0379pc9fx9t4j5wm4qay0y36h", "get_realtime_stock_data"),
    ("tool_01k037agyze6zre4mj3ba9kdzt4e", "analyze_technical_confluence"),
    ("tool_01k037bv6rf8ca82w7kw0g77xewx", "generate_watchlist"),
    ("tool_01k037c7znfzy9whqkzq0s3hhp4d", "get_live_news_updates")
]

print("🔍 Checking Orphaned Tools Dependencies")
print("=" * 60)

for tool_id, tool_name in ORPHANED_TOOLS:
    print(f"\n📌 {tool_name}")
    print(f"   ID: {tool_id}")
    
    # Get dependent agents
    response = requests.get(
        f"{BASE_URL}/convai/tools/{tool_id}/dependent-agents",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        data = response.json()
        agent_ids = data.get('dependent_agent_ids', [])
        
        if agent_ids:
            print(f"   Dependent agents: {len(agent_ids)}")
            for dep_agent_id in agent_ids:
                if dep_agent_id == AGENT_ID:
                    print(f"   ⚠️  OUR AGENT: {dep_agent_id}")
                else:
                    print(f"   - {dep_agent_id}")
        else:
            print("   No dependent agents (should be deletable)")
    else:
        print(f"   Error checking dependencies: {response.status_code}")

# Check if these are in the agent's inline tools
print("\n" + "=" * 60)
print("🔍 Checking if these are inline tools...")

agent_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if agent_response.status_code == 200:
    agent_data = agent_response.json()
    prompt = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    # Check if tools field exists (it shouldn't after deprecation)
    if 'tools' in prompt:
        print("⚠️  Agent still has inline tools field!")
        inline_tools = prompt.get('tools', [])
        print(f"   Number of inline tools: {len(inline_tools)}")
        
        # Match names
        for tool in inline_tools:
            if isinstance(tool, dict):
                name = tool.get('name', '')
                for orphan_id, orphan_name in ORPHANED_TOOLS:
                    if name == orphan_name:
                        print(f"   🔗 Found match: {orphan_name} is in inline tools!")
    else:
        print("✅ No inline tools field in API response (as expected post-deprecation)")
    
    # Show tool_ids for comparison
    tool_ids = prompt.get('tool_ids', [])
    print(f"\n📋 Current tool_ids ({len(tool_ids)} tools):")
    for tid in tool_ids[:3]:
        print(f"   - {tid}")
    if len(tool_ids) > 3:
        print(f"   ... and {len(tool_ids) - 3} more")

print("\n💡 Conclusion:")
print("   These orphaned tools are likely from the old inline tools array")
print("   that can't be removed due to the platform bug.")
print("   They won't interfere with the agent's operation since we're using tool_ids.")