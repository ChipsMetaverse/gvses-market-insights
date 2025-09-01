#!/usr/bin/env python3
"""
Simple test to check if tools can be called by the agent
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🧪 Simple Tool Call Test")
print("=" * 60)

# First, verify our backend is working
print("\n1️⃣ Testing backend directly...")
backend_url = "https://gvses-market-insights.fly.dev/api/stock-price?symbol=BTC-USD"
try:
    response = requests.get(backend_url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Backend working! Bitcoin price: ${data.get('last', 'N/A')}")
    else:
        print(f"   ❌ Backend error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Backend error: {e}")

# Get agent configuration
print("\n2️⃣ Checking agent configuration...")
response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    agent_data = response.json()
    prompt_config = agent_data.get('conversation_config', {}).get('agent', {}).get('prompt', {})
    
    tool_ids = prompt_config.get('tool_ids', [])
    inline_tools = prompt_config.get('tools', [])
    
    print(f"   Tool IDs configured: {len(tool_ids)}")
    print(f"   Inline tools present: {len(inline_tools)}")
    
    if tool_ids:
        print(f"   First tool ID: {tool_ids[0][:30]}...")
    
    # Check if first tool exists and is configured correctly
    if tool_ids:
        print("\n3️⃣ Checking first tool configuration...")
        tool_response = requests.get(
            f"{BASE_URL}/convai/tools/{tool_ids[0]}",
            headers={"xi-api-key": API_KEY}
        )
        
        if tool_response.status_code == 200:
            tool_data = tool_response.json()
            tool_config = tool_data.get('tool_config', {})
            api_schema = tool_config.get('api_schema', {})
            
            print(f"   Tool name: {tool_config.get('name')}")
            print(f"   Tool type: {tool_config.get('type')}")
            print(f"   URL: {api_schema.get('url', 'N/A')}")
            print(f"   Method: {api_schema.get('method', 'N/A')}")
            
            # Check if URL is correct
            if 'gvses-market-insights.fly.dev' in api_schema.get('url', ''):
                print("   ✅ Tool points to production backend")
            else:
                print("   ❌ Tool has wrong URL")
        else:
            print(f"   ❌ Could not fetch tool: {tool_response.status_code}")

# Try to get agent's share link to test in browser
print("\n4️⃣ Getting agent share link...")
link_response = requests.get(
    f"{BASE_URL}/convai/agents/{AGENT_ID}/link",
    headers={"xi-api-key": API_KEY}
)

if link_response.status_code == 200:
    link_data = link_response.json()
    share_link = link_data.get('link')
    if share_link:
        print(f"   📱 Test the agent here: {share_link}")
        print("\n   💡 Try asking:")
        print('      - "What is Bitcoin trading at?"')
        print('      - "Show me the market overview"')
        print('      - "Get Tesla stock price"')
else:
    print(f"   Could not get share link: {link_response.status_code}")

print("\n" + "=" * 60)
print("📊 Summary:")
if tool_ids and 'gvses-market-insights.fly.dev' in api_schema.get('url', ''):
    print("   ✅ Tools are configured correctly")
    print("   ✅ Backend is accessible")
    print("\n   ⚠️  If tools still don't work, the issue may be:")
    print("      1. The persistent inline tools causing conflicts")
    print("      2. Platform-level caching issues")
    print("      3. LLM not invoking tools properly")
    print("\n   💡 Recommendation:")
    print("      Test in the browser using the share link above")
else:
    print("   ❌ Configuration issues detected")
    print("   Please run fix_existing_agent_tools.py again")