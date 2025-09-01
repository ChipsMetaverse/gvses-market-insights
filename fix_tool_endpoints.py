#!/usr/bin/env python3
"""
Fix tool endpoint mappings and remove duplicates
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

print("🔧 Fixing Tool Endpoints and Duplicates")
print("=" * 60)

# Define correct mappings
CORRECT_MAPPINGS = {
    'get_stock_price': {
        'endpoint': '/api/stock-price',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_realtime_stock_data': {
        'endpoint': '/api/stock-price',
        'needs_params': True,
        'params': ['symbol']
    },
    'fetch_live_price': {
        'endpoint': '/api/stock-price',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_market_overview': {
        'endpoint': '/api/market-overview',
        'needs_params': False,
        'params': []
    },
    'get_stock_news': {
        'endpoint': '/api/stock-news',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_stock_history': {
        'endpoint': '/api/stock-history',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_analyst_ratings': {
        'endpoint': '/api/analyst-ratings',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_options_chain': {
        'endpoint': '/api/options-chain',
        'needs_params': True,
        'params': ['symbol']
    },
    'get_market_movers': {
        'endpoint': '/api/market-movers',
        'needs_params': False,
        'params': []
    },
    'get_comprehensive_stock_data': {
        'endpoint': '/api/comprehensive-stock-data',
        'needs_params': True,
        'params': ['symbol']
    }
}

# Step 1: Get all tools
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

# Step 2: Analyze and categorize tools
tools_by_name = {}
tools_to_fix = []
tools_to_delete = []

print("\n🔍 Analyzing tools...")
for tool in tools:
    tool_id = tool.get('id')
    config = tool.get('tool_config', {})
    name = config.get('name', '')
    api_schema = config.get('api_schema', {})
    url = api_schema.get('url', '')
    
    # Only process market-related tools
    if name in CORRECT_MAPPINGS or 'stock' in name.lower() or 'market' in name.lower():
        if name not in tools_by_name:
            tools_by_name[name] = []
        tools_by_name[name].append(tool)

# Step 3: Identify which tools to keep, fix, or delete
for name, tool_list in tools_by_name.items():
    if len(tool_list) > 1:
        print(f"\n   📊 {name}: {len(tool_list)} duplicates found")
        # Keep the first one, delete others
        tools_to_fix.append(tool_list[0])
        for duplicate in tool_list[1:]:
            tools_to_delete.append(duplicate)
            print(f"      🗑️  Will delete duplicate: {duplicate.get('id')}")
    else:
        tools_to_fix.append(tool_list[0])

# Step 4: Fix tool endpoints
print(f"\n📡 Fixing {len(tools_to_fix)} tools...")
fixed_count = 0

for tool in tools_to_fix:
    tool_id = tool.get('id')
    config = tool.get('tool_config', {})
    name = config.get('name', '')
    api_schema = config.get('api_schema', {})
    current_url = api_schema.get('url', '')
    
    if name in CORRECT_MAPPINGS:
        mapping = CORRECT_MAPPINGS[name]
        correct_url = f"{PRODUCTION_BACKEND}{mapping['endpoint']}"
        
        # Check if URL needs fixing
        needs_update = False
        if mapping['endpoint'] not in current_url:
            needs_update = True
            print(f"\n   Fixing {name} (ID: {tool_id})")
            print(f"      Current: {current_url}")
            print(f"      Correct: {correct_url}")
        
        # Check if params need fixing
        query_params = api_schema.get('query_params_schema', {})
        has_params = bool(query_params)
        
        if mapping['needs_params'] != has_params:
            needs_update = True
            if mapping['needs_params']:
                print(f"      Adding required parameters: {mapping['params']}")
            else:
                print(f"      Removing unnecessary parameters")
        
        if needs_update:
            # Build correct configuration
            updated_api_schema = {
                "url": correct_url,
                "method": "GET"
            }
            
            # Add params if needed
            if mapping['needs_params']:
                params_properties = {}
                for param in mapping['params']:
                    params_properties[param] = {
                        "type": "string",
                        "description": f"The {param} to query"
                    }
                
                updated_api_schema["query_params_schema"] = {
                    "properties": params_properties,
                    "required": mapping['params']
                }
            
            # Update tool
            update_config = {
                "tool_config": {
                    "name": config.get('name'),
                    "description": config.get('description'),
                    "type": config.get('type', 'webhook'),
                    "response_timeout_secs": config.get('response_timeout_secs', 30),
                    "api_schema": updated_api_schema
                }
            }
            
            update_response = requests.patch(
                f"{BASE_URL}/convai/tools/{tool_id}",
                headers={
                    "xi-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                json=update_config
            )
            
            if update_response.status_code in [200, 204]:
                print(f"      ✅ Fixed successfully!")
                fixed_count += 1
            else:
                print(f"      ❌ Failed to fix: {update_response.status_code}")
                print(f"         Error: {update_response.text[:200]}")

# Step 5: Delete duplicates
if tools_to_delete:
    print(f"\n🗑️  Deleting {len(tools_to_delete)} duplicate tools...")
    deleted_count = 0
    
    for tool in tools_to_delete:
        tool_id = tool.get('id')
        name = tool.get('tool_config', {}).get('name', '')
        
        delete_response = requests.delete(
            f"{BASE_URL}/convai/tools/{tool_id}",
            headers={"xi-api-key": API_KEY}
        )
        
        if delete_response.status_code in [200, 204]:
            print(f"   ✅ Deleted duplicate: {name} ({tool_id})")
            deleted_count += 1
        else:
            print(f"   ❌ Failed to delete: {name} ({tool_id})")

# Step 6: Verify final state
print("\n🔍 Verifying final configuration...")
verify_response = requests.get(
    f"{BASE_URL}/convai/tools",
    headers={"xi-api-key": API_KEY}
)

if verify_response.status_code == 200:
    final_tools = verify_response.json().get('tools', [])
    
    # Count tools by endpoint
    endpoint_count = {}
    for tool in final_tools:
        config = tool.get('tool_config', {})
        name = config.get('name', '')
        url = config.get('api_schema', {}).get('url', '')
        
        if 'stock' in name.lower() or 'market' in name.lower():
            endpoint = url.split('/api/')[-1] if '/api/' in url else 'unknown'
            if endpoint not in endpoint_count:
                endpoint_count[endpoint] = []
            endpoint_count[endpoint].append(name)
    
    print("\n📊 Final Tool Distribution:")
    for endpoint, names in sorted(endpoint_count.items()):
        print(f"   /api/{endpoint}: {len(names)} tools")
        for name in names[:3]:  # Show first 3
            print(f"      • {name}")

# Summary
print("\n" + "=" * 60)
print("📊 Fix Summary:")
print(f"   • Tools fixed: {fixed_count}")
print(f"   • Duplicates deleted: {len(tools_to_delete)}")
print(f"   • Total tools now: {len(tools) - len(tools_to_delete)}")

if fixed_count > 0 or len(tools_to_delete) > 0:
    print("\n✅ Tools configuration improved!")
    print("\n💡 Next steps:")
    print("   1. Test the agent with specific queries")
    print("   2. Monitor if tools are being called")
    print("   3. Verify correct data is returned")
else:
    print("\n✅ Tools already properly configured!")