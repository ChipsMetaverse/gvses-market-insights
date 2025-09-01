#!/usr/bin/env python3
"""
Link tools to agent using the correct API approach
The issue is that tools aren't showing the agent as a dependent
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

print("🔗 Linking Tools to Agent")
print("=" * 60)

# Load the fresh tool IDs
with open('fresh_tool_ids.json', 'r') as f:
    data = json.load(f)
    tool_ids = data['tool_ids']

print(f"Agent ID: {AGENT_ID}")
print(f"Tool IDs: {len(tool_ids)} tools")

# Method 1: Update agent with ONLY tool_ids (no other fields)
print("\n📝 Method 1: Minimal update with only tool_ids...")

minimal_update = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "tool_ids": tool_ids
            }
        }
    }
}

response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json=minimal_update
)

if response.status_code in [200, 204]:
    print("   ✅ Agent updated with tool_ids")
else:
    print(f"   ❌ Failed: {response.status_code}")
    print(f"      {response.text[:200]}")

time.sleep(2)

# Method 2: Get agent, modify, and PUT back
print("\n📝 Method 2: Full replacement approach...")

# Get current agent
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    agent_data = response.json()
    
    # Remove inline tools if present
    if 'conversation_config' in agent_data:
        if 'agent' in agent_data['conversation_config']:
            if 'prompt' in agent_data['conversation_config']['agent']:
                prompt = agent_data['conversation_config']['agent']['prompt']
                
                # Remove tools field if it exists
                if 'tools' in prompt:
                    del prompt['tools']
                    print("   🗑️ Removed inline tools")
                
                # Update tool_ids
                prompt['tool_ids'] = tool_ids
                print(f"   ✅ Set tool_ids: {len(tool_ids)} tools")
    
    # Try to update with full data
    response = requests.patch(
        f"{BASE_URL}/convai/agents/{AGENT_ID}",
        headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
        json=agent_data
    )
    
    if response.status_code in [200, 204]:
        print("   ✅ Agent updated successfully")
    else:
        print(f"   ❌ Update failed: {response.status_code}")

time.sleep(2)

# Method 3: Force update by setting tools to null/empty
print("\n📝 Method 3: Explicitly nullify tools field...")

nullify_update = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "tools": None,  # Explicitly set to null
                "tool_ids": tool_ids
            }
        }
    }
}

response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY, "Content-Type": "application/json"},
    json=nullify_update
)

if response.status_code in [200, 204]:
    print("   ✅ Agent updated with nullified tools")
else:
    print(f"   ❌ Failed: {response.status_code}")

time.sleep(2)

# Verify the linking
print("\n🔍 Verification...")

# Check if tools now show agent as dependent
print("\nChecking tool dependencies:")
tools_linked = 0
for tool_id in tool_ids[:3]:  # Check first 3
    response = requests.get(
        f"{BASE_URL}/convai/tools/{tool_id}/dependent-agents",
        headers={"xi-api-key": API_KEY}
    )
    
    if response.status_code == 200:
        deps = response.json().get('dependent_agent_ids', [])
        if AGENT_ID in deps:
            print(f"   ✅ Tool {tool_id[:20]}... linked to agent")
            tools_linked += 1
        else:
            print(f"   ❌ Tool {tool_id[:20]}... NOT linked")
            # Try to understand why
            print(f"      Dependencies: {deps[:2] if deps else 'None'}")

# Check final agent state
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    agent_data = response.json()
    prompt = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    has_tool_ids = 'tool_ids' in prompt
    has_inline = 'tools' in prompt
    num_tool_ids = len(prompt.get('tool_ids', []))
    num_inline = len(prompt.get('tools', []))
    
    print(f"\nFinal agent configuration:")
    print(f"   Has tool_ids: {has_tool_ids} ({num_tool_ids} tools)")
    print(f"   Has inline tools: {has_inline} ({num_inline} tools)")
    
    if tools_linked > 0:
        print(f"\n✅ SUCCESS: {tools_linked} tools are now linked!")
    else:
        print("\n❌ Tools still not linked as dependents")
        print("\n💡 Possible solutions:")
        print("   1. The tools may need to be created WITH the agent_id")
        print("   2. There may be a separate API to add dependencies")
        print("   3. The agent may need to be recreated from scratch")

print("\n" + "=" * 60)