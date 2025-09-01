#!/usr/bin/env python3
"""
Fix ElevenLabs Agent Configuration
This script ensures the agent is properly configured to respond to messages
"""

import os
import httpx
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

def check_agent_config():
    """Check current agent configuration"""
    print("Checking agent configuration...")
    
    if not ELEVENLABS_API_KEY:
        print("❌ ELEVENLABS_API_KEY not found in backend/.env")
        return False
    
    headers = {
        'xi-api-key': ELEVENLABS_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Note: ElevenLabs doesn't have a direct API to fetch agent config
    # We'll provide instructions instead
    
    print("\n📋 Manual Configuration Steps for ElevenLabs Dashboard:\n")
    print("1. Go to https://elevenlabs.io/app/conversational-ai")
    print(f"2. Find agent with ID: {AGENT_ID}")
    print("3. Click on the agent to edit")
    print("\n4. Ensure these settings are configured:")
    print("   ✅ Language: English")
    print("   ✅ LLM Model: Select a model (e.g., claude-3-sonnet or gpt-4)")
    print("   ✅ Temperature: 0.7")
    print("   ✅ First Message: Leave empty (agent waits for user)")
    print("   ✅ System Prompt: Copy from idealagent.md")
    print("\n5. Voice Settings:")
    print("   ✅ Voice: Select any voice (e.g., 'Rachel' or 'Josh')")
    print("   ✅ Stability: 0.5")
    print("   ✅ Similarity Boost: 0.75")
    print("\n6. ASR (Speech Recognition):")
    print("   ✅ Model: nova-2-general")
    print("   ✅ Language: en")
    print("\n7. Response Settings:")
    print("   ✅ Max Response Length: 2500 characters")
    print("   ✅ Response Mode: 'Always respond'")
    print("\n8. Tools (Optional):")
    print("   - You can add custom tools if needed")
    print("\n9. Save the agent configuration")
    print("\n10. Test the agent in the dashboard playground first")
    
    return True

def create_test_agent_config():
    """Generate a test agent configuration JSON"""
    config = {
        "conversation_config": {
            "agent": {
                "prompt": open('idealagent.md').read() if os.path.exists('idealagent.md') else "You are a helpful assistant.",
                "first_message": "",  # Empty = wait for user
                "language": "en"
            },
            "llm": {
                "model": "claude-3-sonnet",  # or "gpt-4"
                "temperature": 0.7,
                "max_tokens": 2500
            },
            "tts": {
                "model": "eleven_turbo_v2_5",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel voice
                "optimize_streaming_latency": 3,
                "output_format": "pcm_16000",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0,
                    "use_speaker_boost": True
                }
            },
            "asr": {
                "model": "nova-2-general",
                "language": "en"
            }
        }
    }
    
    # Save configuration for reference
    with open('agent_config_template.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Created agent_config_template.json for reference")
    print("   Use this as a guide when configuring the agent in the dashboard")
    
    return config

def main():
    print("="*60)
    print(" ElevenLabs Agent Configuration Helper")
    print("="*60)
    print(f"Agent ID: {AGENT_ID}")
    
    # Check configuration
    if check_agent_config():
        print("\n" + "="*60)
        
        # Create template config
        create_test_agent_config()
        
        print("\n" + "="*60)
        print("\n🎯 Quick Fix Actions:")
        print("\n1. The most common issue is the agent not having a voice selected")
        print("2. Make sure 'Response Mode' is set to 'Always respond'")
        print("3. Ensure an LLM model is selected (not 'None')")
        print("\n4. After making changes, test in the dashboard:")
        print("   - Click 'Test Agent' or 'Playground'")
        print("   - Type: 'Hello, can you hear me?'")
        print("   - You should get both text and audio response")
        
        print("\n5. Once it works in the dashboard, test our app again:")
        print("   python3 test_elevenlabs_conversation.py")
        
        print("\n" + "="*60)
        print("\n💡 Pro Tips:")
        print("- If agent doesn't respond, check if it's waiting for audio input")
        print("- Some voices work better than others for market analysis")
        print("- Lower latency settings improve responsiveness")
        print("- Keep temperature around 0.7 for balanced responses")

if __name__ == "__main__":
    main()