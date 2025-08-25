#!/usr/bin/env python3
"""
Update ElevenLabs agent with multi-mode conversation support
"""

import os
import json
import requests
from pathlib import Path

def update_agent_prompt():
    """Update the ElevenLabs agent with the new multi-mode prompt"""
    
    # Read the structured prompt
    prompt_file = Path("agent_prompt_structured.md")
    if not prompt_file.exists():
        # Fallback to multi-mode if structured doesn't exist
        prompt_file = Path("agent_prompt_multimode.md")
        if not prompt_file.exists():
            print("❌ No prompt file found")
            return False
    
    with open(prompt_file, 'r') as f:
        prompt_content = f.read()
    
    print(f"✅ Loaded {prompt_file.name}")
    if "structured" in prompt_file.name:
        print(f"   - Quick Mode: Price card format")
        print(f"   - Analysis Mode: Summary table + insights")
        print(f"   - Overview Mode: Full technical analysis")
    else:
        print(f"   - Conversation Mode: 1-2 sentences max")
        print(f"   - Overview Mode: Full detailed analysis")
    
    # Get environment variables
    api_key = os.getenv('ELEVENLABS_API_KEY')
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    
    if not api_key or not agent_id:
        print("\n❌ Missing environment variables")
        print("   Please set ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID")
        return False
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # First, GET the current agent configuration
    print("\n📥 Fetching current agent configuration...")
    url = f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}"
    
    try:
        response = requests.get(url, headers={"xi-api-key": api_key})
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch agent: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        agent_config = response.json()
        print(f"✅ Got agent: {agent_config.get('name', 'Unknown')}")
        
        # Update the conversation_config with new prompt
        if 'conversation_config' not in agent_config:
            agent_config['conversation_config'] = {}
        
        if 'agent' not in agent_config['conversation_config']:
            agent_config['conversation_config']['agent'] = {}
        
        # Set the multi-mode prompt
        agent_config['conversation_config']['agent']['prompt'] = {
            "prompt": prompt_content
        }
        
        # Update other conversation settings for optimal performance
        agent_config['conversation_config']['agent']['language'] = 'en'
        
        # Set TTS settings for natural conversation
        if 'tts' not in agent_config['conversation_config']:
            agent_config['conversation_config']['tts'] = {}
        
        agent_config['conversation_config']['tts'].update({
            "model": "eleven_turbo_v2_5",
            "optimize_streaming_latency": 3
        })
        
        # Set LLM settings for conversation mode
        if 'llm' not in agent_config['conversation_config']:
            agent_config['conversation_config']['llm'] = {}
            
        agent_config['conversation_config']['llm'].update({
            "model": "gpt-4o-mini",
            "temperature": 0.3,
            "max_tokens": 150  # Limited for conversation mode
        })
        
        # Update the agent
        print("\n🔧 Updating agent with multi-mode configuration...")
        update_response = requests.patch(url, headers=headers, json=agent_config)
        
        if update_response.status_code == 200:
            print(f"\n✅ Agent updated successfully!")
            if "structured" in prompt_file.name:
                print(f"   - Default: QUICK MODE (price card)")
                print(f"   - Say 'analyze' for summary table")
                print(f"   - Say 'overview' for full analysis")
            else:
                print(f"   - Default mode: CONVERSATION (1-2 sentences)")
                print(f"   - Overview trigger: 'overview', 'full analysis', 'breakdown'")
            print(f"   - Agent ID: {agent_id}")
            return True
        else:
            print(f"\n❌ Failed to update agent")
            print(f"   Status: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error updating agent: {e}")
        return False

def test_configuration():
    """Test the agent configuration"""
    
    agent_id = os.getenv('ELEVENLABS_AGENT_ID')
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key or not agent_id:
        print("❌ Missing environment variables for testing")
        return
    
    url = f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}"
    headers = {"xi-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            agent_data = response.json()
            print(f"\n📊 Agent Configuration Test:")
            print(f"   - Name: {agent_data.get('name', 'Unknown')}")
            print(f"   - Status: Active")
            print(f"   - Modes: Conversation (default) | Overview (on request)")
            
            # Show example interactions
            print(f"\n💬 Example Interactions:")
            print(f"   User: 'How's Tesla?'")
            print(f"   Bot:  'TSLA at $245, up 3.2%. Near QE level.'")
            print(f"")
            print(f"   User: 'Give me full analysis'")
            print(f"   Bot:  [Switches to detailed overview mode]")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🤖 G'sves Multi-Mode Configuration")
    print("=" * 40)
    
    # Load .env if available
    from pathlib import Path
    env_file = Path("backend/.env")
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print("✅ Loaded environment from backend/.env")
    
    # Update the agent
    if update_agent_prompt():
        test_configuration()
        
        print(f"\n🎯 Next Steps:")
        print(f"   1. Restart the frontend: npm run dev")
        print(f"   2. Test conversation mode (short responses)")
        print(f"   3. Say 'give me an overview' to switch modes")
    else:
        print(f"\n⚠️  Agent update failed. Please check:")
        print(f"   1. ELEVENLABS_API_KEY is set")
        print(f"   2. ELEVENLABS_AGENT_ID is correct")
        print(f"   3. Agent exists and is accessible")