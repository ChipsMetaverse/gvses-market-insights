#!/usr/bin/env python3
"""
Update agent to use tool_ids only (no inline tools)
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Updating Agent to Use Tool IDs Only")
print("=" * 60)

# Load the tool IDs we just created
with open('tool_ids.json', 'r') as f:
    tool_data = json.load(f)
    tool_ids = tool_data['tool_ids']
    tool_names = tool_data['tool_names']

print(f"📋 Loaded {len(tool_ids)} tool IDs")
for name, tool_id in zip(tool_names, tool_ids):
    print(f"   • {name}: {tool_id}")

# Step 1: Get current agent configuration
print("\n📥 Getting current agent configuration...")
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get agent: {response.status_code}")
    exit(1)

agent_data = response.json()
current_config = agent_data.get('conversation_config', {})
current_agent = current_config.get('agent', {})
current_prompt = current_agent.get('prompt', {})

print(f"   Current LLM: {current_prompt.get('llm', 'Not set')}")
print(f"   Has inline tools: {'tools' in current_prompt}")
print(f"   Has tool_ids: {'tool_ids' in current_prompt}")

# Step 2: Build updated configuration
print("\n🔄 Building updated configuration...")

# Keep the prompt text but update tool configuration
updated_config = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": current_prompt.get('prompt', ''),
                "llm": current_prompt.get('llm', 'gpt-4o'),
                "temperature": current_prompt.get('temperature', 0.7),
                "max_tokens": current_prompt.get('max_tokens', 2000),
                "tool_ids": tool_ids  # Use only tool_ids, no inline tools
            },
            "first_message": current_agent.get('first_message', "Hello! I'm G'sves, your market insights expert."),
            "language": current_agent.get('language', 'en')
        },
        "tts": current_config.get('tts', {}),
        "asr": current_config.get('asr', {}),
        "conversation": current_config.get('conversation', {})
    },
    "name": agent_data.get('name', 'Gsves Market Insights')
}

# Make sure we're NOT including inline tools
if 'tools' in updated_config['conversation_config']['agent']['prompt']:
    del updated_config['conversation_config']['agent']['prompt']['tools']

print("   ✅ Configuration prepared")
print(f"   Tool IDs: {len(tool_ids)} tools")
print("   Inline tools: Removed")

# Step 3: Update the agent
print("\n📤 Updating agent...")
update_response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=updated_config
)

if update_response.status_code in [200, 204]:
    print("✅ Agent updated successfully!")
else:
    print(f"❌ Failed to update agent: {update_response.status_code}")
    print(f"   Error: {update_response.text[:500]}")
    exit(1)

# Step 4: Verify the update
print("\n🔍 Verifying update...")
verify_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    updated_data = verify_response.json()
    updated_prompt = updated_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    has_tool_ids = 'tool_ids' in updated_prompt
    has_inline_tools = 'tools' in updated_prompt
    num_tool_ids = len(updated_prompt.get('tool_ids', []))
    
    print(f"   Has tool_ids: {has_tool_ids} ({num_tool_ids} tools)")
    print(f"   Has inline tools: {has_inline_tools}")
    
    if has_tool_ids and not has_inline_tools and num_tool_ids == len(tool_ids):
        print("\n✅ Agent successfully configured with tool IDs only!")
        print("\n🎯 Configuration Summary:")
        print(f"   • Agent ID: {AGENT_ID}")
        print(f"   • Tool IDs: {num_tool_ids} tools properly referenced")
        print("   • Inline tools: None (removed)")
        print("   • LLM: " + updated_prompt.get('llm', 'Not set'))
        
        print("\n✨ Next steps:")
        print("1. Update local config file to match")
        print("2. Test with simulation API")
        print("3. Verify tools are being called")
    else:
        print("\n⚠️ Configuration may not be correct:")
        print(f"   Expected {len(tool_ids)} tool_ids, got {num_tool_ids}")
        print(f"   Inline tools present: {has_inline_tools}")
else:
    print(f"❌ Failed to verify: {verify_response.status_code}")

print("\n" + "=" * 60)