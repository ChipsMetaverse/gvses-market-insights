#!/usr/bin/env python3
"""
Check the correct format for knowledge base in ElevenLabs agents
"""

import requests
import json

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
headers = {"xi-api-key": API_KEY}

# Get all agents
url = "https://api.elevenlabs.io/v1/convai/agents"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    agents = response.json().get("agents", [])
    
    # Find an agent with knowledge base
    for agent in agents:
        conv_config = agent.get("conversation_config", {})
        agent_config = conv_config.get("agent", {})
        prompt_config = agent_config.get("prompt", {})
        kb = prompt_config.get("knowledge_base", [])
        
        if kb:
            print(f"Agent with Knowledge Base: {agent.get('name')}")
            print(f"Knowledge Base Format:")
            print(json.dumps(kb, indent=2))
            print("\nFirst item structure:")
            if kb:
                print(json.dumps(kb[0], indent=2))
            break
    else:
        print("No agents with knowledge base found")
        print("\nTrying alternative format based on error message...")
        print("Expected format appears to be objects, not strings")
        print("\nPossible format:")
        print(json.dumps([
            {"id": "lsBT1M95ifxCezXb8Zx9"},
            {"id": "TyDQIY5A3ajYhabxsVQX"}
        ], indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)