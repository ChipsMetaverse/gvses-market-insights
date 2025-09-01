#!/usr/bin/env python3
"""
Check available LLM options for ElevenLabs agents
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🔍 Checking LLM Options")
print("=" * 60)

# Test different LLM options
llm_options = [
    "gpt-4o",           # GPT-4 Optimized
    "gpt-4o-mini",      # Current
    "gpt-3.5-turbo",    # GPT-3.5
    "claude-3-5-sonnet-20241022",  # Claude 3.5 Sonnet
    "claude-3-5-haiku-20241022",   # Claude 3.5 Haiku
]

print("Testing available LLMs...")
print()

for llm in llm_options:
    print(f"Testing: {llm}")
    
    # Try to update with this LLM
    config = {
        "conversation_config": {
            "agent": {
                "prompt": {
                    "llm": llm
                }
            }
        }
    }
    
    response = requests.patch(
        f"{BASE_URL}/convai/agents/{AGENT_ID}",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json=config
    )
    
    if response.status_code in [200, 204]:
        print(f"   ✅ {llm} is supported!")
    else:
        error_data = response.json() if response.text else {}
        error_msg = error_data.get('detail', {}).get('message', 'Unknown error')
        if 'not yet supported' in str(error_msg).lower():
            print(f"   ❌ {llm} not supported")
        else:
            print(f"   ⚠️  {llm}: {response.status_code}")

print("\n" + "=" * 60)
print("\n💡 Note: The issue might not be the LLM itself")
print("   Some things to check:")
print("   1. Tool configuration format")
print("   2. Custom LLM endpoint configuration")
print("   3. Agent webhook response format")