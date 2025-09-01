#!/usr/bin/env python3
"""Check ElevenLabs agent history and status"""

import requests
import json
from datetime import datetime, timedelta

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
AGENT_ID = "agent_4901k2tkkq54f4mvgpndm3pgzm7g"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

def check_agent_details():
    """Get agent details"""
    print("\n=== AGENT DETAILS ===")
    url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            agent = response.json()
            print(f"Agent Name: {agent.get('name', 'N/A')}")
            print(f"Agent ID: {agent.get('agent_id', 'N/A')}")
            print(f"Status: {agent.get('status', 'N/A')}")
            print(f"Created: {agent.get('created_at', 'N/A')}")
            print(f"Last Modified: {agent.get('last_modified', 'N/A')}")
            if 'conversation_config' in agent:
                config = agent['conversation_config']
                print(f"Model: {config.get('llm', {}).get('model', 'N/A')}")
                print(f"Language: {config.get('language', 'N/A')}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error checking agent: {e}")
        return False

def check_conversations():
    """Get recent conversations"""
    print("\n=== RECENT CONVERSATIONS ===")
    url = f"https://api.elevenlabs.io/v1/convai/conversations"
    params = {
        "agent_id": AGENT_ID,
        "limit": 10
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            conversations = data.get('conversations', [])
            if conversations:
                for conv in conversations[:5]:  # Show last 5
                    print(f"\nConversation ID: {conv.get('conversation_id', 'N/A')}")
                    print(f"  Started: {conv.get('start_time', 'N/A')}")
                    print(f"  Duration: {conv.get('duration', 'N/A')} seconds")
                    print(f"  Status: {conv.get('status', 'N/A')}")
                    print(f"  Messages: {conv.get('message_count', 0)}")
            else:
                print("No recent conversations found")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error checking conversations: {e}")
        return False

def check_usage():
    """Check usage statistics"""
    print("\n=== USAGE STATISTICS ===")
    url = "https://api.elevenlabs.io/v1/usage/character-stats"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            usage = response.json()
            print(f"Character Count: {usage.get('character_count', 0):,}")
            print(f"Character Limit: {usage.get('character_limit', 0):,}")
            print(f"Characters Remaining: {usage.get('character_limit', 0) - usage.get('character_count', 0):,}")
            
            # Calculate usage percentage
            if usage.get('character_limit', 0) > 0:
                usage_percent = (usage.get('character_count', 0) / usage.get('character_limit', 0)) * 100
                print(f"Usage: {usage_percent:.1f}%")
            
            # Check if near limit
            remaining = usage.get('character_limit', 0) - usage.get('character_count', 0)
            if remaining < 10000:
                print("⚠️  WARNING: Low character count remaining!")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error checking usage: {e}")
        return False

def check_subscription():
    """Check subscription status"""
    print("\n=== SUBSCRIPTION STATUS ===")
    url = "https://api.elevenlabs.io/v1/user/subscription"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sub = response.json()
            print(f"Tier: {sub.get('tier', 'N/A')}")
            print(f"Status: {sub.get('status', 'N/A')}")
            if 'next_invoice' in sub:
                print(f"Next Invoice: {sub.get('next_invoice', {}).get('date', 'N/A')}")
            if 'character_limit' in sub:
                print(f"Monthly Character Limit: {sub.get('character_limit', 0):,}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

def test_agent_connection():
    """Test if agent can be accessed"""
    print("\n=== TESTING AGENT CONNECTION ===")
    url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}/validate"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("✅ Agent is accessible and valid")
            return True
        elif response.status_code == 404:
            print("❌ Agent not found - check agent ID")
            return False
        elif response.status_code == 401:
            print("❌ Authentication failed - check API key")
            return False
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("ELEVENLABS AGENT STATUS CHECK")
    print("=" * 50)
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print(f"Agent ID: {AGENT_ID}")
    
    # Run all checks
    test_agent_connection()
    check_agent_details()
    check_conversations()
    check_usage()
    check_subscription()
    
    print("\n" + "=" * 50)
    print("CHECK COMPLETE")
    print("=" * 50)