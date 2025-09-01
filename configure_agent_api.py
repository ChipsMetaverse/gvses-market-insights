#!/usr/bin/env python3
"""
Configure ElevenLabs Agent via API
Updates the agent configuration programmatically
"""

import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

# Load the ideal agent prompt
with open('idealagent.md', 'r') as f:
    AGENT_PROMPT = f.read()

def update_agent_configuration():
    """Update agent configuration via ElevenLabs API"""
    
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found in backend/.env")
        return False
    
    print(f"🔧 Configuring agent: {AGENT_ID}")
    print(f"📝 Using API key: {ELEVENLABS_API_KEY[:20]}...")
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Agent configuration payload
    agent_config = {
        "name": "Gsves Market Insights",
        "conversation_config": {
            "agent": {
                "prompt": {
                    "prompt": AGENT_PROMPT,
                    "llm": "gpt-4o-mini",  # or "claude-3-5-sonnet"
                    "temperature": 0.7,
                    "max_tokens": 2500
                },
                "first_message": "",  # Empty = wait for user
                "language": "en"
            },
            "tts": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                },
                "pronunciation_dictionary_locators": []
            },
            "stt": {
                "model": "nova-2",
                "language": "en"
            },
            "turn": {
                "mode": "system_response_required",  # Always respond
                "threshold": 500
            },
            "client_events": ["audio", "text"],
            "custom_llm_data": {}
        },
        "platform_settings": {
            "auth": {
                "mode": "whitelist",
                "whitelist": ["localhost", "127.0.0.1", "*.fly.dev"]
            },
            "widget": {
                "variant": "modal"
            }
        },
        "privacy": {
            "mode": "default"
        }
    }
    
    # Try to update the agent
    try:
        print("\n📡 Sending configuration to ElevenLabs API...")
        
        # ElevenLabs API endpoint for updating agent
        url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
        
        with httpx.Client(timeout=30.0) as client:
            # First, try to get current agent config
            print("📥 Fetching current agent configuration...")
            get_response = client.get(url, headers=headers)
            
            if get_response.status_code == 200:
                print("✅ Successfully fetched current configuration")
                current_config = get_response.json()
                print(f"   Current name: {current_config.get('name', 'Unknown')}")
            else:
                print(f"⚠️  Could not fetch current config: {get_response.status_code}")
                print(f"   Response: {get_response.text[:200]}")
            
            # Try PATCH to update the agent
            print("\n📤 Updating agent configuration...")
            patch_response = client.patch(
                url,
                headers=headers,
                json=agent_config
            )
            
            if patch_response.status_code in [200, 201, 204]:
                print("✅ Agent configuration updated successfully!")
                return True
            else:
                print(f"❌ Failed to update agent: {patch_response.status_code}")
                print(f"   Response: {patch_response.text[:500]}")
                
                # Try alternative approach
                print("\n🔄 Trying alternative configuration method...")
                
                # Simplified config for conversation update
                conversation_update = {
                    "conversation_config": {
                        "agent": {
                            "prompt": AGENT_PROMPT,
                            "first_message": "",
                            "language": "en"
                        }
                    }
                }
                
                alt_response = client.patch(
                    url,
                    headers=headers,
                    json=conversation_update
                )
                
                if alt_response.status_code in [200, 201, 204]:
                    print("✅ Agent prompt updated successfully!")
                    return True
                else:
                    print(f"❌ Alternative method also failed: {alt_response.status_code}")
                    print(f"   Response: {alt_response.text[:500]}")
                    
    except Exception as e:
        print(f"❌ Error updating agent: {e}")
        return False
    
    return False

def verify_agent_settings():
    """Verify agent settings via API"""
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print("\n🔍 Verifying agent settings...")
        url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
        
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            
            if response.status_code == 200:
                config = response.json()
                print("✅ Agent configuration retrieved:")
                print(f"   Name: {config.get('name', 'Unknown')}")
                print(f"   ID: {config.get('agent_id', AGENT_ID)}")
                
                # Check conversation config
                conv_config = config.get('conversation_config', {})
                agent_config = conv_config.get('agent', {})
                
                if agent_config:
                    prompt = agent_config.get('prompt', '')
                    first_msg = agent_config.get('first_message', '')
                    
                    print(f"   First message: {'[Empty - waits for user]' if not first_msg else first_msg[:50]}")
                    print(f"   Prompt configured: {'Yes' if prompt else 'No'}")
                    
                    if prompt and 'G\'sves' in str(prompt):
                        print("   ✅ Correct G'sves prompt detected")
                    elif prompt:
                        print("   ⚠️  Prompt exists but may need updating")
                    else:
                        print("   ❌ No prompt configured")
                
                # Check TTS config
                tts_config = conv_config.get('tts', {})
                if tts_config:
                    voice_id = tts_config.get('voice_id', '')
                    print(f"   Voice configured: {'Yes' if voice_id else 'No'}")
                
                return True
            else:
                print(f"❌ Failed to verify: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying agent: {e}")
        return False

def main():
    print("="*60)
    print(" ElevenLabs Agent API Configuration")
    print("="*60)
    print(f"Agent ID: {AGENT_ID}")
    print(f"API Key: {ELEVENLABS_API_KEY[:20]}..." if ELEVENLABS_API_KEY else "API Key: Not found")
    
    if not ELEVENLABS_API_KEY:
        print("\n❌ Cannot proceed without API key")
        print("   Please set ELEVENLABS_API_KEY in backend/.env")
        return
    
    # First verify current settings
    verify_agent_settings()
    
    # Ask user if they want to update
    print("\n" + "="*60)
    print("⚠️  WARNING: This will update your agent configuration")
    print("   The script will:")
    print("   1. Set the system prompt from idealagent.md")
    print("   2. Clear the first message (agent waits for user)")
    print("   3. Configure voice and language settings")
    print("\n   Note: Some settings may need manual configuration in the dashboard")
    print("         as the API has limited update capabilities")
    
    response = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        print("\n🚀 Updating agent configuration...")
        if update_agent_configuration():
            print("\n✅ Configuration update attempted!")
            print("\n📝 Next steps:")
            print("1. Go to https://elevenlabs.io/app/conversational-ai")
            print(f"2. Open agent: {AGENT_ID}")
            print("3. Verify these settings:")
            print("   - Voice is selected (Rachel or similar)")
            print("   - LLM model is selected (GPT-4 or Claude)")
            print("   - System prompt contains G'sves persona")
            print("   - First message is empty")
            print("4. Test in the dashboard playground")
            print("5. Run: python3 test_elevenlabs_conversation.py")
        else:
            print("\n⚠️  Automatic configuration had issues")
            print("   Please configure manually in the dashboard:")
            print("   https://elevenlabs.io/app/conversational-ai")
    else:
        print("\n❌ Configuration cancelled")
        print("   Please configure manually in the dashboard")

if __name__ == "__main__":
    main()