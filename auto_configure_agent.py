#!/usr/bin/env python3
"""
Automatically configure ElevenLabs Agent via API
No user interaction required
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

def update_agent_prompt():
    """Update only the agent prompt via API"""
    
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found")
        return False
    
    print("="*60)
    print(" Auto-Configuring ElevenLabs Agent")
    print("="*60)
    print(f"Agent ID: {AGENT_ID}")
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Minimal update - just the prompt
    prompt_update = {
        "conversation_config": {
            "agent": {
                "prompt": AGENT_PROMPT,
                "first_message": "",  # Keep empty
                "language": "en"
            }
        }
    }
    
    try:
        url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
        
        print("\n📤 Updating agent prompt...")
        with httpx.Client(timeout=30.0) as client:
            response = client.patch(url, headers=headers, json=prompt_update)
            
            if response.status_code in [200, 201, 204]:
                print("✅ Agent prompt updated successfully!")
                return True
            else:
                print(f"⚠️  API returned: {response.status_code}")
                
                # Try alternative method - update via POST
                print("\n🔄 Trying alternative update method...")
                
                # Some APIs require specific endpoints for updates
                alt_url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}/update"
                alt_response = client.post(alt_url, headers=headers, json=prompt_update)
                
                if alt_response.status_code in [200, 201, 204]:
                    print("✅ Alternative method succeeded!")
                    return True
                else:
                    print(f"⚠️  Alternative also returned: {alt_response.status_code}")
                    
                    # Final attempt - minimal config
                    print("\n🔄 Final attempt with minimal config...")
                    minimal_update = {
                        "prompt": AGENT_PROMPT
                    }
                    
                    final_response = client.patch(url, headers=headers, json=minimal_update)
                    if final_response.status_code in [200, 201, 204]:
                        print("✅ Minimal update succeeded!")
                        return True
                    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def verify_configuration():
    """Verify the agent configuration"""
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
        
        print("\n🔍 Verifying configuration...")
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            
            if response.status_code == 200:
                config = response.json()
                conv_config = config.get('conversation_config', {})
                agent_config = conv_config.get('agent', {})
                
                print("✅ Current configuration:")
                print(f"   Name: {config.get('name', 'Unknown')}")
                print(f"   First message: {'Empty (waits for user)' if not agent_config.get('first_message') else 'Has greeting'}")
                
                prompt = str(agent_config.get('prompt', ''))
                if 'G\'sves' in prompt or 'Gsves' in prompt:
                    print("   ✅ G'sves prompt is configured")
                elif prompt:
                    print("   ⚠️  Has prompt but not G'sves persona")
                else:
                    print("   ❌ No prompt configured")
                
                # Check voice
                tts_config = conv_config.get('tts', {})
                if tts_config.get('voice_id'):
                    print("   ✅ Voice is configured")
                else:
                    print("   ❌ No voice configured")
                
                return True
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    return False

def main():
    print("\n🚀 Starting automatic agent configuration...")
    
    # First verify current state
    verify_configuration()
    
    # Attempt to update
    print("\n" + "="*60)
    if update_agent_prompt():
        print("\n✅ Update process completed!")
    else:
        print("\n⚠️  Automatic update had limited success")
        print("\n📝 IMPORTANT: The ElevenLabs API has restrictions on programmatic updates.")
        print("   Some settings MUST be configured in the dashboard:\n")
        print("   1. Go to: https://elevenlabs.io/app/conversational-ai")
        print("   2. Click on 'Gsves Market Insights' agent")
        print("   3. Go to 'Voice' tab - Select a voice if not already selected")
        print("   4. Go to 'Analysis' tab - Select LLM model (GPT-4 or Claude)")
        print("   5. Make sure 'System prompt' contains the G'sves trading persona")
        print("   6. Save changes")
    
    # Final verification
    print("\n" + "="*60)
    print(" Final Configuration Check")
    print("="*60)
    verify_configuration()
    
    print("\n📊 Testing Instructions:")
    print("1. Test in ElevenLabs dashboard first:")
    print("   - Click 'Test AI agent' button")
    print("   - Say or type: 'Hello, tell me about Tesla stock'")
    print("   - You should get a response with market analysis")
    print("\n2. Then test with our app:")
    print("   - Run: python3 test_elevenlabs_conversation.py")
    print("   - All tests should pass")
    print("\n3. Finally test in the browser:")
    print("   - Open http://localhost:5174")
    print("   - Click 'Start Voice Chat'")
    print("   - Check browser console for connection logs")

if __name__ == "__main__":
    main()