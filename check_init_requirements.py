#!/usr/bin/env python3
"""Check what initialization data ElevenLabs expects"""

import requests
import json

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
AGENT_ID = "agent_4901k2tkkq54f4mvgpndm3pgzm7g"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

# Check if we need special initialization based on agent config
url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
response = requests.get(url, headers=headers)

if response.status_code == 200:
    agent = response.json()
    config = agent.get('conversation_config', {})
    
    print("=== INITIALIZATION REQUIREMENTS ===")
    
    # Check conversation config
    conv_config = config.get('conversation', {})
    print(f"Text Only Mode: {conv_config.get('text_only', False)}")
    print(f"Client Events: {conv_config.get('client_events', [])}")
    
    # Check ASR config
    asr_config = config.get('asr', {})
    print(f"User Input Audio Format: {asr_config.get('user_input_audio_format', 'N/A')}")
    
    # Check TTS config
    tts_config = config.get('tts', {})
    print(f"Agent Output Audio Format: {tts_config.get('agent_output_audio_format', 'N/A')}")
    
    # Check if custom LLM requires extra body
    agent_config = config.get('agent', {})
    prompt_config = agent_config.get('prompt', {})
    custom_llm = prompt_config.get('custom_llm')
    print(f"Custom LLM: {custom_llm}")
    
    print("\n=== SUGGESTED INIT MESSAGE ===")
    init_message = {
        "type": "conversation_initiation_client_data",
        "custom_llm_extra_body": {},
        "conversation_config_override": {
            "agent": {
                "prompt": {
                    "prompt": agent_config.get('prompt', {}).get('prompt', ''),
                    "llm": prompt_config.get('llm', 'gpt-4o'),
                    "temperature": prompt_config.get('temperature', 0.7)
                }
            }
        } if custom_llm else None
    }
    
    # Remove None values
    init_message = {k: v for k, v in init_message.items() if v is not None}
    
    print(json.dumps(init_message, indent=2))
    
    print("\n=== AUDIO FORMAT REQUIREMENTS ===")
    print(f"Expected Input: PCM 16kHz (user_input_audio_format: {asr_config.get('user_input_audio_format')})")
    print(f"Expected Output: PCM 16kHz (agent_output_audio_format: {tts_config.get('agent_output_audio_format')})")
    
    # Check platform settings for auth
    platform = agent.get('platform_settings', {})
    auth = platform.get('auth', {})
    print(f"\n=== AUTHENTICATION ===")
    print(f"Auth Enabled: {auth.get('enable_auth', False)}")
    print(f"Allowlist: {auth.get('allowlist', [])}")
    
else:
    print(f"Error: {response.status_code} - {response.text}")