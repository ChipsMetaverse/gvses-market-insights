#!/usr/bin/env python3
"""
Update ElevenLabs agent webhook URLs to use the deployed backend.
"""

import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')

if not ELEVENLABS_API_KEY or not ELEVENLABS_AGENT_ID:
    print("❌ Missing ELEVENLABS_API_KEY or ELEVENLABS_AGENT_ID in backend/.env")
    exit(1)

# New production backend URL
PRODUCTION_BACKEND_URL = "https://gvses-market-insights.fly.dev"

async def update_agent_webhook_urls():
    """Update all webhook URLs to use the production backend."""
    
    async with httpx.AsyncClient() as client:
        # Get current agent configuration
        print(f"📥 Fetching agent configuration...")
        response = await client.get(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={"xi-api-key": ELEVENLABS_API_KEY}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch agent: {response.status_code}")
            return False
        
        agent_config = response.json()
        print(f"✅ Got agent: {agent_config.get('name', 'Unknown')}")
        
        # Get current tools
        tools = agent_config.get('conversation_config', {}).get('agent', {}).get('tools', [])
        print(f"\n📋 Found {len(tools)} tools configured")
        
        # Update webhook URLs
        updated_count = 0
        for tool in tools:
            if tool.get('type') == 'webhook':
                old_url = tool.get('webhook', {}).get('url', '')
                tool_name = tool.get('name', 'Unknown')
                
                # Check if it's using the old loca.lt URL
                if 'loca.lt' in old_url or 'localhost' in old_url:
                    # Extract the API path
                    if '/api/stock-price' in old_url:
                        new_url = f"{PRODUCTION_BACKEND_URL}/api/stock-price"
                    else:
                        # Keep the same path structure
                        path = old_url.split('/api/')[-1] if '/api/' in old_url else 'stock-price'
                        new_url = f"{PRODUCTION_BACKEND_URL}/api/{path}"
                    
                    tool['webhook']['url'] = new_url
                    updated_count += 1
                    print(f"   ✏️  {tool_name}: Updated URL")
                    print(f"      Old: {old_url}")
                    print(f"      New: {new_url}")
                else:
                    print(f"   ✓ {tool_name}: Already using correct URL ({old_url})")
        
        if updated_count == 0:
            print("\n✅ All webhook URLs are already correctly configured!")
            return True
        
        # Update the agent configuration
        print(f"\n🔧 Updating agent with {updated_count} URL changes...")
        update_response = await client.patch(
            f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
            headers={
                "xi-api-key": ELEVENLABS_API_KEY,
                "Content-Type": "application/json"
            },
            json=agent_config
        )
        
        if update_response.status_code == 200:
            print(f"✅ Successfully updated agent webhook URLs!")
            
            # Verify the update
            verify_response = await client.get(
                f"https://api.elevenlabs.io/v1/convai/agents/{ELEVENLABS_AGENT_ID}",
                headers={"xi-api-key": ELEVENLABS_API_KEY}
            )
            
            if verify_response.status_code == 200:
                updated_config = verify_response.json()
                updated_tools = updated_config.get('conversation_config', {}).get('agent', {}).get('tools', [])
                
                print(f"\n📋 Verification - Current webhook URLs:")
                for tool in updated_tools:
                    if tool.get('type') == 'webhook':
                        url = tool.get('webhook', {}).get('url', 'N/A')
                        print(f"   - {tool.get('name')}: {url}")
            
            return True
        else:
            print(f"❌ Failed to update agent: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False

if __name__ == "__main__":
    print("🔧 ElevenLabs Webhook URL Updater")
    print("=" * 50)
    print(f"Target Backend: {PRODUCTION_BACKEND_URL}")
    print("=" * 50)
    
    success = asyncio.run(update_agent_webhook_urls())
    
    if success:
        print("\n🎉 All done! Your ElevenLabs agent is now configured to use the production backend.")
        print("Try asking about stock prices again!")
    else:
        print("\n❌ Update failed. Please check the errors above.")