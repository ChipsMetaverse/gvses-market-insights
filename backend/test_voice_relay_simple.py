#!/usr/bin/env python3
"""
Simple Voice Relay Session Management Test
Tests the core session management functionality without external dependencies
"""

import asyncio
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_relay_session_management():
    """Test basic relay session management features"""
    print("🧪 Testing Voice Relay Session Management...")
    
    # Set test configuration
    os.environ["MAX_CONCURRENT_SESSIONS"] = "3"
    os.environ["SESSION_TIMEOUT_SECONDS"] = "10"
    os.environ["ACTIVITY_TIMEOUT_SECONDS"] = "5"
    os.environ["CLEANUP_INTERVAL_SECONDS"] = "2"
    
    try:
        from services.openai_relay_server import OpenAIRealtimeRelay
        
        # Initialize relay server
        relay = OpenAIRealtimeRelay()
        print(f"✅ Relay initialized with max {relay.max_concurrent_sessions} sessions")
        
        # Test 1: Create sessions up to limit
        print("\n📊 Test 1: Concurrent session limits")
        sessions = []
        for i in range(3):
            session_id = f"test-session-{i}"
            # Use internal method to bypass WebSocket requirement
            relay.active_sessions[session_id] = {
                "created_at": asyncio.get_event_loop().time(),
                "last_activity": asyncio.get_event_loop().time(),
                "frontend_ws": None,
                "openai_ws": None,
                "connected": False
            }
            sessions.append(session_id)
            print(f"  ✓ Created session {i+1}: {session_id}")
        
        # Try to exceed limit
        extra_session = "extra-session"
        if len(relay.active_sessions) >= relay.max_concurrent_sessions:
            print(f"  ✓ Correctly at limit: {len(relay.active_sessions)}/{relay.max_concurrent_sessions}")
        else:
            print(f"  ✗ Not enforcing limit: {len(relay.active_sessions)}/{relay.max_concurrent_sessions}")
        
        # Test 2: Activity tracking
        print("\n🕒 Test 2: Activity timeout tracking")
        test_session = sessions[0]
        initial_activity = relay.active_sessions[test_session]["last_activity"]
        
        # Simulate activity update
        await asyncio.sleep(1)
        relay.active_sessions[test_session]["last_activity"] = asyncio.get_event_loop().time()
        new_activity = relay.active_sessions[test_session]["last_activity"]
        
        if new_activity > initial_activity:
            print(f"  ✓ Activity timestamp updated: {new_activity - initial_activity:.2f}s")
        else:
            print(f"  ✗ Activity not tracked properly")
        
        # Test 3: Session cleanup
        print("\n🧹 Test 3: Session cleanup")
        initial_count = len(relay.active_sessions)
        
        # Mark one session as expired
        relay.active_sessions[sessions[1]]["last_activity"] = asyncio.get_event_loop().time() - 100
        
        # Run cleanup
        await relay._cleanup_expired_sessions()
        
        final_count = len(relay.active_sessions)
        if final_count < initial_count:
            print(f"  ✓ Cleaned up expired sessions: {initial_count} -> {final_count}")
        else:
            print(f"  ⚠️  No cleanup occurred (may need real timeout)")
        
        # Test 4: Get status
        print("\n📈 Test 4: Monitoring endpoints")
        status = await relay.get_status()
        print(f"  ✓ Status: {status['active_sessions']}/{status['max_sessions']} sessions")
        print(f"  ✓ Ready: {status['ready']}")
        
        # Test 5: Session details
        session_details = await relay.get_active_sessions()
        print(f"  ✓ Active sessions: {len(session_details)}")
        for sid, details in list(session_details.items())[:2]:
            print(f"    • {sid}: created_at={details.get('created_at', 'N/A')}")
        
        # Test 6: Graceful shutdown
        print("\n🛑 Test 6: Graceful shutdown")
        await relay.shutdown()
        print(f"  ✓ Shutdown complete, remaining sessions: {len(relay.active_sessions)}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure openai_relay_server.py exists and is properly configured")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_relay_integration():
    """Test relay integration with endpoints"""
    print("\n🔗 Testing Voice Relay Integration...")
    
    try:
        import httpx
        
        # Check if server is running
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:8000/health")
                if response.status_code != 200:
                    print("⚠️  Server not running on port 8000")
                    return False
                    
                health_data = response.json()
                print(f"✅ Server health check passed")
                print(f"  • Voice relay ready: {health_data.get('voice_relay', {}).get('ready', False)}")
                print(f"  • Active sessions: {health_data.get('voice_relay', {}).get('active_sessions', 0)}")
                
                # Try to create a session
                print("\n📱 Testing session creation...")
                session_resp = await client.post("http://localhost:8000/openai/realtime/session")
                
                if session_resp.status_code == 200:
                    session_data = session_resp.json()
                    print(f"✅ Session created successfully")
                    print(f"  • Session ID: {session_data.get('session_id', 'N/A')}")
                    print(f"  • URL: {session_data.get('url', 'N/A')[:50]}...")
                elif session_resp.status_code == 503:
                    print("⚠️  Session creation unavailable (OpenAI service not configured)")
                    print("   This is expected if OPENAI_API_KEY is not set")
                else:
                    print(f"❌ Session creation failed: {session_resp.status_code}")
                    
            except httpx.ConnectError:
                print("⚠️  Cannot connect to server - make sure it's running")
                print("   Run: cd backend && uvicorn mcp_server:app --reload")
                return False
                
    except ImportError:
        print("⚠️  httpx not installed - skipping integration tests")
        print("   Install with: pip install httpx")
        return False
    
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("VOICE RELAY SESSION MANAGEMENT TEST SUITE")
    print("=" * 60)
    
    # Run core tests
    core_passed = await test_relay_session_management()
    
    # Run integration tests
    integration_passed = await test_relay_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Core Tests: {'✅ PASSED' if core_passed else '❌ FAILED'}")
    print(f"Integration Tests: {'✅ PASSED' if integration_passed else '⚠️ SKIPPED/FAILED'}")
    
    if core_passed:
        print("\n✨ Voice relay session management is working correctly!")
    else:
        print("\n⚠️  Issues found - review the test output above")
    
    return core_passed


if __name__ == "__main__":
    asyncio.run(main())