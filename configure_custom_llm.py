#!/usr/bin/env python3
"""
Configure ElevenLabs agent to use a custom LLM endpoint
This allows us to inject real market data into responses
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Configure agent to use custom LLM endpoint that routes through our backend
config = {
    "conversation_config": {
        "agent": {
            "prompt": """You are G'sves, a market analyst. 

IMPORTANT: When asked about current prices, you should:
1. Say you'll check the current market data
2. Use the get_stock_price tool if available
3. If no tools are available, explain you don't have real-time access

Never make up or guess prices. Always be honest about data availability.""",
            "first_message": "",
            "language": "en"
        }
    },
    "custom_llm_endpoint": {
        "url": "http://localhost:8000/api/llm-proxy",
        "headers": {
            "Content-Type": "application/json"
        }
    }
}

print("🔧 Configuring Custom LLM Endpoint")
print("=" * 40)

response = requests.patch(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json=config
)

if response.status_code in [200, 204]:
    print("✅ Configuration updated!")
    print("\nNew setup:")
    print("• Agent will route through custom endpoint")
    print("• Backend can inject real market data")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)

# Verify
verify = requests.get(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if verify.status_code == 200:
    data = verify.json()
    custom_llm = data.get('custom_llm_endpoint')
    if custom_llm:
        print(f"\n✅ Custom LLM endpoint configured:")
        print(f"   URL: {custom_llm.get('url')}")
    else:
        print("\n❌ Custom LLM endpoint not set")