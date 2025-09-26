#!/usr/bin/env python3
"""
Supabase Session Validation Script
===================================
Tests session creation via ORM and REST API to ensure compatibility.
"""

import asyncio
import os
import uuid
import time
from datetime import datetime
from typing import Optional
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class SupabaseSessionValidator:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
    def test_schema_inspection(self):
        """Inspect the sessions table schema."""
        print("\n📍 Test 1: Schema Inspection")
        print("-" * 50)
        
        try:
            # Get table information using REST API
            response = self.client.table("sessions").select("*").limit(0).execute()
            print("✅ Sessions table exists")
            
            # Try to get a sample row to understand structure
            sample = self.client.table("sessions").select("*").limit(1).execute()
            if sample.data:
                print(f"Sample row keys: {list(sample.data[0].keys())}")
            else:
                print("No existing sessions found")
                
            return True
        except Exception as e:
            print(f"❌ Schema inspection failed: {e}")
            return False
    
    def test_uuid_format(self):
        """Test various session ID formats."""
        print("\n📍 Test 2: UUID Format Validation")
        print("-" * 50)
        
        test_cases = [
            ("Valid UUID", str(uuid.uuid4()), True),
            ("Test prefix", f"test-session-{int(time.time())}", False),
            ("Custom string", "my-custom-session-123", False),
            ("Empty UUID", "", False),
        ]
        
        for name, session_id, should_pass in test_cases:
            try:
                # Attempt to create a session with this ID
                result = self.client.table("sessions").insert({
                    "id": session_id,
                    "created_at": datetime.now().isoformat()
                }).execute()
                
                if should_pass:
                    print(f"✅ {name}: {session_id[:20]}... - Created successfully")
                    # Clean up
                    self.client.table("sessions").delete().eq("id", session_id).execute()
                else:
                    print(f"⚠️  {name}: {session_id[:20]}... - Unexpectedly succeeded")
                    # Clean up
                    self.client.table("sessions").delete().eq("id", session_id).execute()
                    
            except Exception as e:
                if not should_pass:
                    print(f"✅ {name}: {session_id[:20]}... - Correctly rejected")
                else:
                    print(f"❌ {name}: {session_id[:20]}... - Failed: {str(e)[:100]}")
    
    def test_upsert_pattern(self):
        """Test the upsert pattern used in ConversationManager."""
        print("\n📍 Test 3: Upsert Pattern Testing")
        print("-" * 50)
        
        session_id = str(uuid.uuid4())
        
        try:
            # First insert
            result1 = self.client.table("sessions").upsert({
                "id": session_id,
                "created_at": datetime.now().isoformat()
            }, on_conflict="id").execute()
            print(f"✅ Initial upsert successful")
            
            # Second upsert (should update, not fail)
            time.sleep(1)
            result2 = self.client.table("sessions").upsert({
                "id": session_id,
                "created_at": datetime.now().isoformat()
            }, on_conflict="id").execute()
            print(f"✅ Second upsert successful (update)")
            
            # Clean up
            self.client.table("sessions").delete().eq("id", session_id).execute()
            print(f"✅ Cleanup successful")
            
            return True
        except Exception as e:
            print(f"❌ Upsert pattern failed: {e}")
            return False
    
    def test_conversation_creation(self):
        """Test creating a conversation with proper foreign key."""
        print("\n📍 Test 4: Conversation Creation")
        print("-" * 50)
        
        session_id = str(uuid.uuid4())
        
        try:
            # Create session first
            self.client.table("sessions").insert({
                "id": session_id,
                "created_at": datetime.now().isoformat()
            }).execute()
            print(f"✅ Session created: {session_id}")
            
            # Create conversation
            conv_result = self.client.table("conversations").insert({
                "session_id": session_id,
                "role": "user",
                "message": "Test message",
                "created_at": datetime.now().isoformat()
            }).execute()
            print(f"✅ Conversation created successfully")
            
            # Clean up (order matters - delete conversation first)
            self.client.table("conversations").delete().eq("session_id", session_id).execute()
            self.client.table("sessions").delete().eq("id", session_id).execute()
            print(f"✅ Cleanup successful")
            
            return True
        except Exception as e:
            print(f"❌ Conversation creation failed: {e}")
            # Try cleanup
            try:
                self.client.table("conversations").delete().eq("session_id", session_id).execute()
                self.client.table("sessions").delete().eq("id", session_id).execute()
            except:
                pass
            return False
    
    def test_required_fields(self):
        """Test which fields are required for sessions table."""
        print("\n📍 Test 5: Required Fields Testing")
        print("-" * 50)
        
        session_id = str(uuid.uuid4())
        
        test_cases = [
            ("ID only", {"id": session_id}),
            ("ID + created_at", {"id": session_id, "created_at": datetime.now().isoformat()}),
            ("No ID", {"created_at": datetime.now().isoformat()}),
        ]
        
        for name, data in test_cases:
            try:
                result = self.client.table("sessions").insert(data).execute()
                print(f"✅ {name}: Success")
                # Clean up if successful
                if "id" in data:
                    self.client.table("sessions").delete().eq("id", data["id"]).execute()
            except Exception as e:
                print(f"❌ {name}: Failed - {str(e)[:100]}")
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("=" * 80)
        print("SUPABASE SESSION VALIDATION")
        print("=" * 80)
        print(f"URL: {self.supabase_url}")
        
        tests = [
            self.test_schema_inspection,
            self.test_uuid_format,
            self.test_upsert_pattern,
            self.test_conversation_creation,
            self.test_required_fields,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
            time.sleep(0.5)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {passed}/{len(tests)}")
        print(f"❌ Failed: {failed}/{len(tests)}")
        
        if failed == 0:
            print("\n🎉 All tests passed! Supabase schema is properly configured.")
        else:
            print("\n⚠️  Some tests failed. Review the schema and constraints.")
        
        return failed == 0

def main():
    """Run the Supabase session validation."""
    try:
        validator = SupabaseSessionValidator()
        success = validator.run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        exit(1)

if __name__ == "__main__":
    main()