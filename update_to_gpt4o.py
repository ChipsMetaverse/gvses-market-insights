#!/usr/bin/env python3
"""
Update agent to use gpt-4o (optimized) for better tool calling
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Updating Agent to GPT-4o")
print("=" * 60)

# Get current configuration
print("📋 Getting current configuration...")
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
print(f"   Tool IDs: {len(current_prompt.get('tool_ids', []))} tools")

# Update to GPT-4o
print("\n🔄 Updating to GPT-4o...")

# Build updated configuration
updated_config = {
    "conversation_config": {
        "agent": {
            "prompt": {
                "prompt": current_prompt.get('prompt', ''),
                "llm": "gpt-4o",  # Use GPT-4 Optimized
                "temperature": 0.7,
                "max_tokens": 2000,
                "tool_ids": current_prompt.get('tool_ids', [])
            },
            "first_message": "Hello! I'm G'sves, your market insights expert with over 30 years of experience. How can I help you today?",
            "language": "en"
        }
    },
    "name": "Gsves Market Insights"
}

# Send update
update_response = requests.patch(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=updated_config
)

if update_response.status_code in [200, 204]:
    print("✅ Successfully updated to GPT-4o!")
else:
    print(f"❌ Failed to update: {update_response.status_code}")
    print(f"   Error: {update_response.text[:500]}")
    exit(1)

# Verify the update
print("\n🔍 Verifying update...")
verify_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    updated_data = verify_response.json()
    updated_prompt = updated_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    new_llm = updated_prompt.get('llm', 'Not set')
    
    print(f"   New LLM: {new_llm}")
    print(f"   Tool IDs: {len(updated_prompt.get('tool_ids', []))} tools")
    
    if new_llm == 'gpt-4o':
        print("\n✅ Agent successfully updated to GPT-4o!")
        print("\n💡 Benefits of GPT-4o:")
        print("   • Better tool calling capabilities")
        print("   • More accurate responses")
        print("   • Optimized for conversational AI")
        print("\n🧪 Test commands:")
        print('   • "What is the current price of Apple?"')
        print('   • "Show me the market overview"')
        print('   • "Get news for Tesla"')
    else:
        print(f"\n⚠️ LLM is {new_llm}, expected gpt-4o")

print("\n" + "=" * 60)