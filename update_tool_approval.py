#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update ElevenLabs tool to set proper approval policy.
"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
TOOL_ID = 'tool_7401k2wh9rd2fw8rpfmtzgw0x3wy'

if not API_KEY:
    print("❌ ELEVENLABS_API_KEY not found in backend/.env")
    exit(1)

# Headers for API calls
headers = {
    'xi-api-key': API_KEY,
    'Content-Type': 'application/json'
}

# Get current tool configuration
print(f"📥 Fetching current configuration for tool {TOOL_ID}...")
response = requests.get(
    f'https://api.elevenlabs.io/v1/convai/tools/{TOOL_ID}',
    headers={'xi-api-key': API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to fetch tool: {response.status_code}")
    print(response.text)
    exit(1)

tool_config = response.json()
print(f"✅ Current tool: {tool_config.get('name', 'Unknown')}")

# Update the tool with approval_required set to false for testing
# Note: In production, you might want to keep this as true for security
tool_config['approval_required'] = False  # Auto-approve for testing
tool_config['approval_timeout_secs'] = 10  # Timeout if no approval

print("\n📤 Updating tool with auto-approval settings...")
update_response = requests.patch(
    f'https://api.elevenlabs.io/v1/convai/tools/{TOOL_ID}',
    headers=headers,
    json={
        'tool_config': tool_config
    }
)

if update_response.status_code == 200:
    print("✅ Tool updated successfully with auto-approval!")
    print("\n🎯 Next steps:")
    print("1. The tool should now execute without requiring manual approval")
    print("2. Test by asking G'sves for a stock price")
    print("3. If you want manual approval, change approval_required to true")
else:
    print(f"❌ Failed to update tool: {update_response.status_code}")
    print(update_response.text)