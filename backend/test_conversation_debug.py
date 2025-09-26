#!/usr/bin/env python3
"""
Debug script for conversation history issues.
Tests saving and retrieving messages from Supabase.
"""

import asyncio
import uuid
import json
import time
from datetime import datetime

# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_server import ConversationManager
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

async def test_conversation_flow():
    """Test the complete conversation save/retrieve flow."""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY in environment")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    
    # Initialize conversation manager
    manager = ConversationManager(supabase)
    
    # Generate a test session ID
    session_id = str(uuid.uuid4())
    print(f"🔑 Test session ID: {session_id}")
    
    # Test 1: Save a user message
    print("\n📝 Test 1: Saving user message...")
    try:
        await manager.save_message(session_id, "user", "Remember this: I like Tesla stock", user_id=None)
        print("✅ User message saved")
    except Exception as e:
        print(f"❌ Failed to save user message: {e}")
        return
    
    # Test 2: Save assistant response
    print("\n📝 Test 2: Saving assistant message...")
    try:
        await manager.save_message(session_id, "assistant", "I'll remember that you like Tesla stock.", user_id=None)
        print("✅ Assistant message saved")
    except Exception as e:
        print(f"❌ Failed to save assistant message: {e}")
        return
    
    # Wait a moment for DB to persist
    print("\n⏳ Waiting 2 seconds for DB persistence...")
    await asyncio.sleep(2)
    
    # Test 3: Retrieve history
    print("\n🔍 Test 3: Retrieving conversation history...")
    try:
        history = await manager.get_history(session_id, limit=10)
        print(f"📚 Retrieved {len(history)} messages")
        
        if history:
            print("\n📖 Conversation history:")
            for i, msg in enumerate(history, 1):
                print(f"  {i}. {msg['role']}: {msg['content'][:100]}...")
        else:
            print("⚠️ No history retrieved - this is the problem!")
            
    except Exception as e:
        print(f"❌ Failed to retrieve history: {e}")
        return
    
    # Test 4: Try retrieving again to check persistence
    print("\n🔍 Test 4: Retrieving history again...")
    try:
        history2 = await manager.get_history(session_id, limit=10)
        print(f"📚 Retrieved {len(history2)} messages on second attempt")
        
        if len(history2) != len(history):
            print("⚠️ History count changed between retrievals!")
            
    except Exception as e:
        print(f"❌ Failed to retrieve history second time: {e}")
    
    # Test 5: Raw Supabase query
    print("\n🔍 Test 5: Raw Supabase query...")
    try:
        response = manager.supabase.table("conversations").select("*").eq(
            "session_id", session_id
        ).execute()
        
        print(f"📦 Raw Supabase response count: {len(response.data) if response.data else 0}")
        if response.data:
            print("📋 Raw data (first entry):")
            print(json.dumps(response.data[0], indent=2, default=str))
        else:
            print("⚠️ No raw data returned from Supabase")
            
    except Exception as e:
        print(f"❌ Raw Supabase query failed: {e}")
    
    # Test 6: Check sessions table
    print("\n🔍 Test 6: Checking sessions table...")
    try:
        response = manager.supabase.table("sessions").select("*").eq(
            "id", session_id
        ).execute()
        
        if response.data:
            print(f"✅ Session exists in sessions table")
            print("📋 Session data:")
            print(json.dumps(response.data[0], indent=2, default=str))
        else:
            print("⚠️ Session NOT found in sessions table - this could be the issue!")
            
    except Exception as e:
        print(f"❌ Sessions table query failed: {e}")
    
    print("\n✅ Debug tests complete!")

if __name__ == "__main__":
    print("🔬 Conversation History Debug Test")
    print("=" * 50)
    asyncio.run(test_conversation_flow())