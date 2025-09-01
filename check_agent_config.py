#!/usr/bin/env python3
"""
Check and display the current ElevenLabs agent configuration
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID', 'agent_4901k2tkkq54f4mvgpndm3pgzm7g')

print("🔍 ElevenLabs Agent Configuration Check")
print("=" * 60)
print(f"Agent ID: {AGENT_ID}")
print()

# Get agent details
response = requests.get(
    f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}",
    headers={"xi-api-key": API_KEY}
)

if response.status_code == 200:
    agent = response.json()
    
    print("📋 Agent Details:")
    print(f"   Name: {agent.get('name', 'N/A')}")
    print(f"   Language: {agent.get('language', 'N/A')}")
    
    # Check prompt
    prompt = agent.get('prompt', {})
    if isinstance(prompt, dict):
        prompt_text = prompt.get('prompt', '')
    else:
        prompt_text = str(prompt)
    
    if prompt_text:
        print(f"\n📝 Prompt Configuration:")
        # Show first 500 chars of prompt
        display_prompt = prompt_text[:500] + "..." if len(prompt_text) > 500 else prompt_text
        print(f"   {display_prompt}")
    else:
        print("\n⚠️  No prompt configured!")
    
    # Check tools
    tool_ids = agent.get('tool_ids', [])
    if tool_ids:
        print(f"\n🔧 Tools Assigned: {len(tool_ids)} tools")
        for tool_id in tool_ids[:10]:  # Show first 10
            print(f"   • {tool_id}")
    else:
        print("\n⚠️  No tools assigned to agent!")
    
    # Check custom LLM
    custom_llm = agent.get('custom_llm', {})
    if custom_llm:
        print(f"\n🤖 Custom LLM Configuration:")
        print(f"   URL: {custom_llm.get('url', 'N/A')}")
        print(f"   Model: {custom_llm.get('model', 'N/A')}")
        print(f"   Max Tokens: {custom_llm.get('max_tokens', 'N/A')}")
    else:
        print("\n🤖 Using default ElevenLabs LLM")
    
    # Check knowledge base
    knowledge_base = agent.get('knowledge_base', {})
    if knowledge_base:
        print(f"\n📚 Knowledge Base:")
        files = knowledge_base.get('files', [])
        print(f"   Files: {len(files)}")
    
    # Check conversation config
    conv_config = agent.get('conversation_config', {})
    if conv_config:
        print(f"\n💬 Conversation Config:")
        print(f"   Mode: {conv_config.get('mode', 'N/A')}")
        print(f"   Max Duration: {conv_config.get('max_duration_seconds', 'N/A')}s")
    
    print("\n" + "=" * 60)
    
    # Recommendations
    print("📊 Analysis:")
    
    issues = []
    if not prompt_text or "Market Insights" not in prompt_text:
        issues.append("Prompt may not be configured with market analysis personality")
    
    if not tool_ids:
        issues.append("No tools assigned to agent")
    
    if not custom_llm:
        issues.append("Using default LLM (may not support tool calls properly)")
    
    if issues:
        print("\n⚠️  Potential Issues:")
        for issue in issues:
            print(f"   • {issue}")
        
        print("\n💡 Recommendations:")
        print("   1. Update agent prompt with idealagent.md content")
        print("   2. Ensure tools are properly assigned")
        print("   3. Consider using custom LLM endpoint for better tool support")
    else:
        print("   ✅ Agent appears to be configured correctly")
    
else:
    print(f"❌ Failed to get agent configuration: {response.status_code}")
    print(f"   Error: {response.text}")