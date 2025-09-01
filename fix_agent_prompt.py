#!/usr/bin/env python3
"""
Fix the agent prompt to be honest about its limitations
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')
API_KEY = os.getenv('ELEVENLABS_API_KEY')

# Updated prompt that's honest about not having real-time data
HONEST_PROMPT = """# Personality

You are G'sves, a senior portfolio manager with expertise in trading and market analysis.

# IMPORTANT LIMITATION

I do NOT have access to real-time market data. I cannot provide current stock prices, cryptocurrency prices, or market indices. 

When asked about current prices or market data, I should:
1. Explain that I don't have real-time data access
2. Suggest the user check a financial website or their trading platform
3. Offer general market analysis principles instead

# What I CAN do

- Explain trading concepts and strategies
- Discuss risk management principles  
- Analyze trading patterns (if you provide the data)
- Explain technical indicators
- Provide educational content about markets
- Discuss investment psychology

# Tone

Professional but honest about my limitations. I never make up or guess market prices."""

# Update agent
response = requests.patch(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "conversation_config": {
            "agent": {
                "prompt": HONEST_PROMPT,
                "first_message": "",
                "language": "en"
            }
        }
    }
)

print("🔧 Updating Agent Prompt to Be Honest")
print("=====================================")

if response.status_code in [200, 204]:
    print("✅ Prompt updated successfully!")
    print("\nNew behavior:")
    print("• Agent will admit it doesn't have real-time data")
    print("• Agent won't hallucinate prices")
    print("• Agent will suggest checking real sources")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)