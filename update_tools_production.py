#!/usr/bin/env python3
"""
Update all ElevenLabs tools to use production backend URLs
"""

import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
BASE_URL = "https://api.elevenlabs.io/v1"
PRODUCTION_BACKEND = "https://gvses-market-insights.fly.dev"

print("🔧 Updating Tools to Production Backend")
print("=" * 60)
print(f"Production URL: {PRODUCTION_BACKEND}")
print()

# Step 1: Get all existing tools
print("📋 Fetching existing tools...")
response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if response.status_code != 200:
    print(f"❌ Failed to get tools: {response.status_code}")
    exit(1)

tools = response.json().get('tools', [])
print(f"   Found {len(tools)} tools")

# Track updates
tools_to_update = []
tools_updated = 0
tools_skipped = 0

# Step 2: Check each tool and identify ones needing updates
print("\n🔍 Analyzing tools...")
for tool in tools:
    tool_id = tool.get('id')
    tool_config = tool.get('tool_config', {})
    name = tool_config.get('name', 'unnamed')
    api_schema = tool_config.get('api_schema', {})
    url = api_schema.get('url', '')
    
    # Check if URL needs updating
    if 'localhost' in url or 'http://localhost' in url:
        # Extract the endpoint path
        if '/api/' in url:
            endpoint = url.split('/api/')[-1]
            new_url = f"{PRODUCTION_BACKEND}/api/{endpoint}"
        else:
            new_url = url.replace('http://localhost:8000', PRODUCTION_BACKEND)
            new_url = new_url.replace('localhost:8000', PRODUCTION_BACKEND)
        
        tools_to_update.append({
            'id': tool_id,
            'name': name,
            'old_url': url,
            'new_url': new_url,
            'config': tool_config
        })
        print(f"   🔄 {name}: needs update")
        print(f"      Old: {url}")
        print(f"      New: {new_url}")
    elif PRODUCTION_BACKEND in url or 'fly.dev' in url:
        print(f"   ✅ {name}: already using production URL")
        tools_skipped += 1
    else:
        print(f"   ⚠️  {name}: unknown URL format - {url}")

# Step 3: Update tools that need it
if tools_to_update:
    print(f"\n📡 Updating {len(tools_to_update)} tools...")
    
    for tool_info in tools_to_update:
        tool_id = tool_info['id']
        name = tool_info['name']
        new_url = tool_info['new_url']
        config = tool_info['config']
        
        # Build updated configuration
        # Preserve all existing config but update the URL
        updated_config = {
            "tool_config": {
                "name": config.get('name'),
                "description": config.get('description'),
                "type": config.get('type', 'webhook'),
                "response_timeout_secs": config.get('response_timeout_secs', 30),
                "api_schema": {
                    **config.get('api_schema', {}),  # Keep all existing api_schema fields
                    "url": new_url  # Update only the URL
                }
            }
        }
        
        # Remove None values
        if not updated_config["tool_config"].get("response_timeout_secs"):
            updated_config["tool_config"]["response_timeout_secs"] = 30
        
        print(f"\n   Updating {name} (ID: {tool_id})...")
        
        # Send PATCH request
        update_response = requests.patch(
            f"{BASE_URL}/convai/tools/{tool_id}",
            headers={
                "xi-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=updated_config
        )
        
        if update_response.status_code in [200, 204]:
            print(f"   ✅ Updated successfully!")
            tools_updated += 1
        else:
            print(f"   ❌ Failed to update: {update_response.status_code}")
            print(f"      Error: {update_response.text[:200]}")
else:
    print("\n✅ All tools already using production URLs!")

# Step 4: Verify updates
print("\n🔍 Verifying updates...")
verify_response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    updated_tools = verify_response.json().get('tools', [])
    
    localhost_count = 0
    production_count = 0
    
    for tool in updated_tools:
        config = tool.get('tool_config', {})
        url = config.get('api_schema', {}).get('url', '')
        
        if 'localhost' in url:
            localhost_count += 1
        elif PRODUCTION_BACKEND in url or 'fly.dev' in url:
            production_count += 1
    
    print(f"   Production URLs: {production_count} tools")
    print(f"   Localhost URLs: {localhost_count} tools")
    
    if localhost_count > 0:
        print(f"   ⚠️  Warning: {localhost_count} tools still using localhost")

# Step 5: Summary
print("\n" + "=" * 60)
print("📊 Update Summary:")
print(f"   • Total tools: {len(tools)}")
print(f"   • Updated: {tools_updated}")
print(f"   • Already correct: {tools_skipped}")
print(f"   • Needing update: {len(tools_to_update)}")

if tools_updated == len(tools_to_update) and len(tools_to_update) > 0:
    print("\n✅ All tools successfully updated to production backend!")
    print(f"   Backend URL: {PRODUCTION_BACKEND}")
    print("\n💡 Next steps:")
    print("   1. Test the agent with market queries")
    print("   2. Verify tools are being called")
    print("   3. Check that real data is returned")
elif localhost_count > 0:
    print("\n⚠️  Some tools may still need attention")
else:
    print("\n✅ All tools configured correctly!")