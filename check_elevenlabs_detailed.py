#!/usr/bin/env python3
"""Detailed ElevenLabs conversation check"""

import requests
import json
from datetime import datetime, timedelta
import time

API_KEY = "sk_280149c578aa859126d25e16c2c2b366f1b983e0a1b3f6cb"
AGENT_ID = "agent_4901k2tkkq54f4mvgpndm3pgzm7g"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

def check_conversation_details(conversation_id):
    """Get detailed info about a specific conversation"""
    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error getting conversation {conversation_id}: {e}")
        return None

def check_conversation_transcript(conversation_id):
    """Get transcript for a conversation"""
    url = f"https://api.elevenlabs.io/v1/convai/conversations/{conversation_id}/transcript"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None

def check_usage_with_dates():
    """Check usage statistics with date range"""
    # Use last 30 days
    end_time = int(time.time())
    start_time = end_time - (30 * 24 * 60 * 60)  # 30 days ago
    
    url = f"https://api.elevenlabs.io/v1/usage/character-stats?start_unix={start_time}&end_unix={end_time}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Usage error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error checking usage: {e}")
        return None

def get_all_conversations():
    """Get all conversations with pagination"""
    all_conversations = []
    url = "https://api.elevenlabs.io/v1/convai/conversations"
    params = {
        "agent_id": AGENT_ID,
        "limit": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('conversations', [])
        else:
            print(f"Error getting conversations: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def check_agent_config():
    """Get detailed agent configuration"""
    url = f"https://api.elevenlabs.io/v1/convai/agents/{AGENT_ID}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("DETAILED ELEVENLABS ANALYSIS")
    print("=" * 60)
    
    # Check agent configuration
    print("\n=== AGENT CONFIGURATION ===")
    agent = check_agent_config()
    if agent:
        print(json.dumps(agent, indent=2))
    else:
        print("Could not fetch agent configuration")
    
    # Get all conversations
    print("\n=== ALL CONVERSATIONS ===")
    conversations = get_all_conversations()
    print(f"Total conversations found: {len(conversations)}")
    
    # Analyze each conversation
    if conversations:
        print("\n=== CONVERSATION DETAILS ===")
        for i, conv in enumerate(conversations[:10], 1):  # Check first 10
            conv_id = conv.get('conversation_id')
            print(f"\n{i}. Conversation: {conv_id}")
            print(f"   Status: {conv.get('status')}")
            print(f"   Duration: {conv.get('duration', 0)} seconds")
            print(f"   Messages: {conv.get('message_count', 0)}")
            
            # Get detailed info
            details = check_conversation_details(conv_id)
            if details:
                print(f"   Start Time: {details.get('start_time', 'N/A')}")
                print(f"   End Time: {details.get('end_time', 'N/A')}")
                if 'metadata' in details:
                    print(f"   Metadata: {json.dumps(details['metadata'], indent=6)}")
            
            # Get transcript if available
            if conv.get('message_count', 0) > 0:
                transcript = check_conversation_transcript(conv_id)
                if transcript:
                    print(f"   Transcript available: {len(transcript.get('messages', []))} messages")
                    # Show first few messages
                    for msg in transcript.get('messages', [])[:3]:
                        print(f"     - {msg.get('role', 'unknown')}: {msg.get('content', '')[:50]}...")
    
    # Check usage with dates
    print("\n=== USAGE (LAST 30 DAYS) ===")
    usage = check_usage_with_dates()
    if usage:
        print(f"Characters Used: {usage.get('character_count', 0):,}")
        print(f"Character Limit: {usage.get('character_limit', 0):,}")
        remaining = usage.get('character_limit', 0) - usage.get('character_count', 0)
        print(f"Characters Remaining: {remaining:,}")
        if usage.get('character_limit', 0) > 0:
            usage_percent = (usage.get('character_count', 0) / usage.get('character_limit', 0)) * 100
            print(f"Usage: {usage_percent:.1f}%")
    
    # Check connection methods
    print("\n=== CONNECTION TEST ===")
    # Try to create a signed URL (similar to what the backend does)
    test_url = f"https://api.elevenlabs.io/v1/convai/conversation"
    test_data = {
        "agent_id": AGENT_ID
    }
    try:
        response = requests.post(test_url, headers=headers, json=test_data)
        print(f"Connection test status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if 'signed_url' in result:
                print("✅ Can generate signed URLs")
                print(f"   URL: {result['signed_url'][:50]}...")
            else:
                print("Response:", json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Connection test error: {e}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)