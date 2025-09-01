#!/usr/bin/env python3
"""
Remove all tools that are not being used by any agents
This will clean up orphaned tools from previous attempts
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

print("🧹 Cleaning Up Unused Tools")
print("=" * 60)

# Step 1: Get all tools
print("\n📥 Fetching all tools...")
response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get tools: {response.status_code}")
    exit(1)

all_tools = response.json().get('tools', [])
print(f"Found {len(all_tools)} total tools")

# Step 2: Get agent's current tool_ids
print("\n🔍 Getting agent's active tools...")
agent_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

active_tool_ids = []
if agent_response.status_code == 200:
    agent_data = agent_response.json()
    prompt = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    active_tool_ids = prompt.get('tool_ids', [])
    print(f"Agent is using {len(active_tool_ids)} tools")

# Step 3: Identify unused tools
unused_tools = []
used_tools = []

for tool in all_tools:
    tool_id = tool.get('id')
    tool_name = tool.get('tool_config', {}).get('name', 'unnamed')
    
    # Check if tool is in agent's active list
    if tool_id in active_tool_ids:
        used_tools.append((tool_id, tool_name))
    else:
        # Also check if tool has any dependent agents
        dep_response = requests.get(
            f"{BASE_URL}/convai/tools/{tool_id}/dependent-agents",
            headers={"xi-api-key": API_KEY}
        )
        
        has_dependents = False
        if dep_response.status_code == 200:
            deps = dep_response.json().get('dependent_agent_ids', [])
            if deps:
                has_dependents = True
        
        if not has_dependents:
            unused_tools.append((tool_id, tool_name))
        else:
            used_tools.append((tool_id, tool_name))

print(f"\n📊 Tool Analysis:")
print(f"   Active tools: {len(used_tools)}")
print(f"   Unused tools: {len(unused_tools)}")

if used_tools:
    print("\n✅ Tools in use (will be kept):")
    for tool_id, name in used_tools:
        print(f"   - {name} ({tool_id[:20]}...)")

if unused_tools:
    print(f"\n🗑️  Unused tools to delete:")
    for tool_id, name in unused_tools:
        print(f"   - {name} ({tool_id[:20]}...)")
    
    # Step 4: Delete unused tools
    print(f"\n🗑️  Deleting {len(unused_tools)} unused tools...")
    deleted_count = 0
    failed_count = 0
    
    for tool_id, name in unused_tools:
        del_response = requests.delete(
            f"{BASE_URL}/convai/tools/{tool_id}",
            headers={"xi-api-key": API_KEY}
        )
        
        if del_response.status_code in [200, 204]:
            print(f"   ✅ Deleted: {name}")
            deleted_count += 1
        else:
            print(f"   ❌ Failed to delete: {name}")
            print(f"      Reason: {del_response.text[:100]}")
            failed_count += 1
        
        time.sleep(0.1)  # Be nice to the API
    
    print(f"\n📊 Deletion Summary:")
    print(f"   Successfully deleted: {deleted_count}")
    print(f"   Failed to delete: {failed_count}")
else:
    print("\n✅ No unused tools found - nothing to clean up!")

# Step 5: Final verification
print("\n🔍 Final Tool Count:")
final_response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if final_response.status_code == 200:
    final_tools = final_response.json().get('tools', [])
    print(f"   Total tools remaining: {len(final_tools)}")
    
    # Show what's left
    if final_tools:
        print("\n📋 Remaining tools:")
        for tool in final_tools:
            tool_name = tool.get('tool_config', {}).get('name', 'unnamed')
            tool_id = tool.get('id')
            is_active = tool_id in active_tool_ids
            status = "✅ ACTIVE" if is_active else "⚠️  ORPHANED"
            print(f"   - {tool_name}: {status}")

print("\n" + "=" * 60)
print("✨ Cleanup complete!")