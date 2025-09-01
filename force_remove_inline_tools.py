#!/usr/bin/env python3
"""
Force remove inline tools from agent configuration
Uses a more explicit approach to ensure tools are removed
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔧 Force Removing Inline Tools from Agent")
print("=" * 60)

# Load the tool IDs
with open('tool_ids.json', 'r') as f:
    tool_data = json.load(f)
    tool_ids = tool_data['tool_ids']

print(f"Tool IDs to use: {len(tool_ids)} tools")

# Get current configuration
print("\n📥 Getting current configuration...")
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get agent: {response.status_code}")
    exit(1)

agent_data = response.json()

# Build a completely new prompt configuration without tools
print("\n🔨 Building clean configuration...")

# Extract current values
current_config = agent_data.get('conversation_config', {})
current_agent = current_config.get('agent', {})
current_prompt = current_agent.get('prompt', {})

# Build new prompt config with ONLY the fields we want
new_prompt_config = {
    "prompt": current_prompt.get('prompt', ''),
    "llm": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 2000,
    "tool_ids": tool_ids,
    # Explicitly set these to empty/false
    "built_in_tools": {},
    "mcp_server_ids": [],
    "native_mcp_server_ids": [],
    "knowledge_base": [],
    "ignore_default_personality": False,
    "rag": {
        "enabled": False,
        "embedding_model": "e5_mistral_7b_instruct",
        "max_vector_distance": 0.6,
        "max_documents_length": 50000,
        "max_retrieved_rag_chunks_count": 20
    }
}

# Build complete configuration
updated_config = {
    "conversation_config": {
        "agent": {
            "prompt": new_prompt_config,
            "first_message": "Hello! I'm G'sves, your market insights expert with over 30 years of experience. How can I help you today?",
            "language": "en",
            "dynamic_variables": {
                "dynamic_variable_placeholders": {}
            }
        },
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
    },
    "name": "Gsves Market Insights"
}

print("   ✅ Clean configuration prepared")
print(f"   - tool_ids: {len(tool_ids)} tools")
print("   - tools field: NOT included (removed)")
print("   - LLM: gpt-4o")

# Update the agent
print("\n📤 Updating agent with clean configuration...")
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
    print(f"❌ Failed to update: {update_response.status_code}")
    print(f"   Error: {update_response.text[:500]}")
    exit(1)

# Verify the update
print("\n🔍 Verifying configuration...")
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
    
    if has_tool_ids and not has_inline_tools:
        print("\n✅ SUCCESS: Inline tools removed, tool_ids configured!")
        print("\n🎯 Final Configuration:")
        print(f"   • Agent: Gsves Market Insights")
        print(f"   • Tool IDs: {num_tool_ids} tools properly referenced")
        print("   • Inline tools: REMOVED")
        print("   • LLM: gpt-4o")
        print("\n✨ Tools should now work properly!")
    else:
        print("\n⚠️  Configuration issues persist:")
        if has_inline_tools:
            print("   • Inline tools are STILL present")
            print("   • This is preventing tool calls")
            print("\n💡 This appears to be a platform issue.")
            print("   The ElevenLabs API may not be properly removing inline tools.")
            print("   Consider contacting ElevenLabs support.")

print("\n" + "=" * 60)