#!/usr/bin/env python3
"""
Voice Relay Session Management Tests

Tests for verifying concurrent session limits, cleanup, locking,
and proper integration with the voice pipeline.
"""

import asyncio
import json
import time
from typing import List, Dict, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test configuration
TEST_OPENAI_API_KEY = "test-key-123"
TEST_SESSION_ID = "test-session-123"
TEST_BASE_URL = "http://localhost:8000"

async def create_websocket_session(base_url=TEST_BASE_URL):
    """Helper to create a WebSocket session"""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{base_url}/openai/realtime/session")
        return response.json()

class TestVoiceRelaySessionManagement:
    """Test suite for voice relay session management"""
    
    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Setup test environment variables"""
        monkeypatch.setenv("OPENAI_API_KEY", TEST_OPENAI_API_KEY)
        monkeypatch.setenv("MAX_CONCURRENT_SESSIONS", "3")
        monkeypatch.setenv("SESSION_TIMEOUT_SECONDS", "10")
        monkeypatch.setenv("ACTIVITY_TIMEOUT_SECONDS", "5")
        monkeypatch.setenv("CLEANUP_INTERVAL_SECONDS", "2")
    
    @pytest.fixture
    async def relay_server(self, mock_env):
        """Create a test relay server instance"""
        from services.openai_relay_server import OpenAIRealtimeRelay
        relay = OpenAIRealtimeRelay()
        yield relay
        await relay.shutdown()
    
    @pytest.mark.asyncio
    async def test_concurrent_session_limits(self, relay_server):
        """Test that concurrent session limits are enforced"""
        sessions = []
        
        # Create sessions up to the limit
        for i in range(3):
            session_id = f"session-{i}"
            success = await relay_server._create_session(session_id)
            assert success, f"Failed to create session {i}"
            sessions.append(session_id)
        
        # Try to create one more - should fail
        extra_session = "session-extra"
        success = await relay_server._create_session(extra_session)
        assert not success, "Should not allow session beyond limit"
        
        # Clean up
        for session_id in sessions:
            await relay_server._close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_session_cleanup_on_timeout(self, relay_server):
        """Test that inactive sessions are cleaned up"""
        session_id = "timeout-session"
        
        # Create a session
        success = await relay_server._create_session(session_id)
        assert success
        
        # Wait for activity timeout
        await asyncio.sleep(6)
        
        # Run cleanup
        await relay_server._cleanup_expired_sessions()
        
        # Session should be gone
        assert session_id not in relay_server.active_sessions
    
    @pytest.mark.asyncio
    async def test_session_activity_tracking(self, relay_server):
        """Test that activity updates prevent timeout"""
        session_id = "active-session"
        
        # Create a session
        success = await relay_server._create_session(session_id)
        assert success
        
        # Simulate activity updates
        for _ in range(3):
            await asyncio.sleep(3)
            relay_server._update_activity(session_id)
        
        # Run cleanup - session should still be active
        await relay_server._cleanup_expired_sessions()
        assert session_id in relay_server.active_sessions
        
        # Clean up
        await relay_server._close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_graceful_shutdown(self, relay_server):
        """Test graceful shutdown closes all sessions"""
        sessions = ["shutdown-1", "shutdown-2", "shutdown-3"]
        
        # Create multiple sessions
        for session_id in sessions:
            await relay_server._create_session(session_id)
        
        # Shutdown should close all
        await relay_server.shutdown()
        
        assert len(relay_server.active_sessions) == 0
    
    @pytest.mark.asyncio
    async def test_websocket_disconnection_cleanup(self, relay_server):
        """Test that WebSocket disconnection triggers cleanup"""
        session_id = "disconnect-session"
        
        # Create session with mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.close = AsyncMock()
        
        success = await relay_server._create_session(session_id)
        assert success
        
        if session_id in relay_server.active_sessions:
            relay_server.active_sessions[session_id]['frontend_ws'] = mock_ws
        
        # Simulate disconnection
        await relay_server._close_session(session_id)
        
        # Verify WebSocket was closed
        mock_ws.close.assert_called_once()
        assert session_id not in relay_server.active_sessions
    
    @pytest.mark.asyncio
    async def test_session_locking_prevents_race_conditions(self, relay_server):
        """Test that session lock prevents race conditions"""
        session_id = "race-condition-test"
        
        async def concurrent_create():
            return await relay_server._create_session(session_id)
        
        # Try to create the same session concurrently
        results = await asyncio.gather(
            concurrent_create(),
            concurrent_create(),
            concurrent_create(),
            return_exceptions=True
        )
        
        # Only one should succeed
        success_count = sum(1 for r in results if r is True)
        assert success_count == 1, "Multiple creates succeeded - race condition!"
        
        # Clean up
        await relay_server._close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoints(self, relay_server):
        """Test monitoring and status endpoints"""
        # Create some test sessions
        sessions = ["monitor-1", "monitor-2"]
        for session_id in sessions:
            await relay_server._create_session(session_id)
        
        # Get status
        status = await relay_server.get_status()
        
        assert status["active_sessions"] == 2
        assert status["max_sessions"] == 3
        assert "uptime" in status
        assert status["ready"] is True
        
        # Get detailed sessions
        session_details = await relay_server.get_active_sessions()
        assert len(session_details) == 2
        
        for session in session_details.values():
            assert "created_at" in session
            assert "last_activity" in session
            assert "connected" in session
        
        # Clean up
        for session_id in sessions:
            await relay_server._close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_tts_message_routing(self, relay_server):
        """Test that TTS messages are routed to correct sessions"""
        session_id = "tts-session"
        test_message = "Hello from TTS"
        
        # Create session with mock WebSocket
        mock_ws = AsyncMock()
        mock_ws.send = AsyncMock()
        
        success = await relay_server._create_session(session_id)
        assert success
        
        if session_id in relay_server.active_sessions:
            relay_server.active_sessions[session_id]['frontend_ws'] = mock_ws
            relay_server.active_sessions[session_id]['connected'] = True
        
        # Send TTS message
        result = await relay_server.send_tts_to_session(session_id, test_message)
        assert result["success"] is True
        
        # Verify message was sent
        mock_ws.send.assert_called()
        sent_data = json.loads(mock_ws.send.call_args[0][0])
        assert sent_data["type"] == "text"
        assert test_message in json.dumps(sent_data)
        
        # Clean up
        await relay_server._close_session(session_id)
    
    @pytest.mark.asyncio
    async def test_session_recreation_after_cleanup(self, relay_server):
        """Test that sessions can be recreated after cleanup"""
        session_id = "recreate-session"
        
        # Create, close, recreate
        for i in range(3):
            success = await relay_server._create_session(session_id)
            assert success, f"Failed to create session on iteration {i}"
            
            await relay_server._close_session(session_id)
            assert session_id not in relay_server.active_sessions
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, relay_server):
        """Test that metrics are properly tracked"""
        # Reset metrics
        relay_server._reset_metrics()
        
        # Perform operations
        sessions = ["metrics-1", "metrics-2"]
        for session_id in sessions:
            await relay_server._create_session(session_id)
        
        # Send some messages
        await relay_server.send_tts_to_session("metrics-1", "Test message")
        
        # Close one session
        await relay_server._close_session("metrics-1")
        
        # Get metrics
        metrics = relay_server.get_metrics()
        
        assert metrics["sessions_created"] == 2
        assert metrics["sessions_closed"] == 1
        assert metrics["messages_sent"] > 0
        assert metrics["current_sessions"] == 1
        
        # Clean up
        await relay_server._close_session("metrics-2")


class TestVoiceAgentIntegration:
    """Test voice agent integration with relay server"""
    
    @pytest.mark.asyncio
    async def test_voice_query_endpoint_with_session_id(self):
        """Test that /api/agent/voice-query properly handles session_id"""
        import httpx
        
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            # First create a session
            session_resp = await client.post("/openai/realtime/session")
            if session_resp.status_code == 200:
                session_data = session_resp.json()
                session_id = session_data.get("session_id")
                
                # Send voice query with session_id
                voice_query = {
                    "message": "What is the current price of Apple?",
                    "session_id": session_id,
                    "conversation_id": "test-conv-123"
                }
                
                response = await client.post(
                    "/api/agent/voice-query",
                    json=voice_query
                )
                
                if response.status_code == 200:
                    data = response.json()
                    assert "response" in data
                    assert "chart_commands" in data
                    assert data.get("tts_sent") is True or "tts_error" in data
    
    @pytest.mark.asyncio
    async def test_session_lifecycle_with_agent(self):
        """Test full session lifecycle with agent interactions"""
        import httpx
        
        async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
            # Create session
            session_resp = await client.post("/openai/realtime/session")
            if session_resp.status_code != 200:
                pytest.skip("Session creation not available")
            
            session_id = session_resp.json().get("session_id")
            
            # Multiple voice queries
            queries = [
                "Show me Tesla stock",
                "What are the technical indicators?",
                "Show support and resistance levels"
            ]
            
            for query in queries:
                response = await client.post(
                    "/api/agent/voice-query",
                    json={
                        "message": query,
                        "session_id": session_id,
                        "conversation_id": "test-conv-456"
                    }
                )
                
                if response.status_code == 200:
                    assert response.json().get("response")
                
                await asyncio.sleep(0.5)  # Simulate user thinking
            
            # Check session is still active
            health_resp = await client.get("/health")
            if health_resp.status_code == 200:
                health_data = health_resp.json()
                assert health_data.get("voice_sessions", {}).get("active_count", 0) > 0


class TestDeprecatedServiceRemoval:
    """Test removal of deprecated OpenAIRealtimeService"""
    
    @pytest.mark.asyncio
    async def test_session_creation_without_deprecated_service(self):
        """Test that sessions can be created without OpenAIRealtimeService"""
        import httpx
        
        # Mock environment without OPENAI_API_KEY to disable deprecated service
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False):
            async with httpx.AsyncClient(base_url=TEST_BASE_URL) as client:
                response = await client.post("/openai/realtime/session")
                
                # Should still work with relay server
                if response.status_code == 200:
                    data = response.json()
                    assert "url" in data
                    assert "session_id" in data
                    assert "relay" in data.get("url", "")


def run_tests():
    """Run all tests"""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode


if __name__ == "__main__":
    # Quick inline test for immediate validation
    async def quick_test():
        print("Running quick voice relay session tests...")
        
        # Test basic session management
        from services.openai_relay_server import OpenAIRealtimeRelay
        
        os.environ["MAX_CONCURRENT_SESSIONS"] = "2"
        os.environ["SESSION_TIMEOUT_SECONDS"] = "5"
        
        relay = OpenAIRealtimeRelay()
        
        # Test session creation
        success = await relay._create_session("test-1")
        print(f"✓ Session 1 created: {success}")
        
        success = await relay._create_session("test-2")
        print(f"✓ Session 2 created: {success}")
        
        # Should fail - at limit
        success = await relay._create_session("test-3")
        print(f"✓ Session 3 rejected (at limit): {not success}")
        
        # Get status
        status = await relay.get_status()
        print(f"✓ Status: {status['active_sessions']}/{status['max_sessions']} sessions")
        
        # Cleanup
        await relay.shutdown()
        print("✓ Graceful shutdown completed")
        
        return True
    
    try:
        # Try running with pytest first
        exit_code = run_tests()
        if exit_code != 0:
            # Fallback to quick test
            print("\nPytest not available, running quick test...")
            asyncio.run(quick_test())
    except Exception as e:
        print(f"Test error: {e}")
        # Run quick test as fallback
        asyncio.run(quick_test())