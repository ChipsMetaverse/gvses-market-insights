#!/usr/bin/env python3
"""
Fix agent LLM configuration to support tool calling
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Fixing Agent LLM Configuration")
print("=" * 60)

# Step 1: Get current agent configuration
print("📋 Getting current agent configuration...")
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
print(f"   Current temperature: {current_prompt.get('temperature', 'Not set')}")
print(f"   Tool IDs: {len(current_prompt.get('tool_ids', []))} tools")

# Step 2: Update to use GPT-4 which has better tool calling support
print("\n🔄 Updating LLM configuration...")

# Keep the existing prompt and tool_ids
updated_config = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": current_prompt.get('prompt', ''),
                "llm": "gpt-4",  # Use GPT-4 for better tool calling
                "temperature": 0.7,
                "max_tokens": 2000,
                "tool_ids": current_prompt.get('tool_ids', [])
            },
            "first_message": current_agent.get('first_message', "Hello! I'm G'sves, your market insights expert. How can I help you today?"),
            "language": "en"
        }
    },
    "name": agent_data.get('name', 'Gsves Market Insights')
}

# Send update request
update_response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=updated_config
)

if update_response.status_code in [200, 204]:
    print("✅ Agent LLM updated successfully!")
    print("   New LLM: gpt-4")
    print("   This should provide better tool calling support")
else:
    print(f"❌ Failed to update agent: {update_response.status_code}")
    print(f"   Error: {update_response.text[:500]}")
    
    # Try with minimal config
    print("\n🔄 Trying with minimal configuration...")
    
    minimal_config = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": current_prompt.get('prompt', ''),
                    "llm": "gpt-4",
                    "tool_ids": current_prompt.get('tool_ids', [])
                }
            }
        }
    }
    
    retry_response = requests.patch(
        f"{BASE_URL}/convai/agents/{AGENT_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=minimal_config
    )
    
    if retry_response.status_code in [200, 204]:
        print("✅ Agent LLM updated with minimal config!")
    else:
        print(f"❌ Minimal config also failed: {retry_response.status_code}")
        print(f"   Error: {retry_response.text[:500]}")

# Step 3: Verify the update
print("\n🔍 Verifying update...")
verify_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    updated_data = verify_response.json()
    updated_prompt = updated_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    print(f"   Current LLM: {updated_prompt.get('llm', 'Not set')}")
    print(f"   Tool IDs: {len(updated_prompt.get('tool_ids', []))} tools")
    
    if updated_prompt.get('llm') == 'gpt-4':
        print("\n✅ LLM successfully updated to GPT-4!")
        print("\n💡 Note: GPT-4 has better tool calling capabilities")
        print("   This should resolve the tool calling issues")
        print("\n🧪 Test with: 'What is the current price of Apple stock?'")
    else:
        print("\n⚠️ LLM update may not have worked as expected")

print("\n" + "=" * 60)