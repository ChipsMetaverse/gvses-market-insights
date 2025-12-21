#!/usr/bin/env python3
"""
End-to-end test for chart command polling system.
Tests the full flow: function call → CommandBus → polling endpoint
"""
import asyncio
import httpx
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"
SESSION_ID = "test-session-123"


async def test_chart_command_polling():
    """Test the complete chart command polling flow"""
    print("=" * 60)
    print("Chart Command Polling - End-to-End Test")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=10.0) as client:
        # Step 1: Check health endpoint
        print("\n1. Checking backend health...")
        try:
            resp = await client.get(f"{API_BASE}/health")
            resp.raise_for_status()
            health = resp.json()
            print(f"✓ Backend healthy: {health.get('status')}")
        except Exception as e:
            print(f"✗ Backend health check failed: {e}")
            print("  Please start backend: cd backend && uvicorn mcp_server:app --reload")
            return False

        # Step 2: Clear any existing commands (poll once to get current cursor)
        print("\n2. Getting current cursor...")
        try:
            resp = await client.get(
                f"{API_BASE}/api/chart-commands",
                params={"sessionId": SESSION_ID, "limit": 1}
            )
            resp.raise_for_status()
            data = resp.json()
            initial_cursor = data.get("cursor", 0)
            print(f"✓ Initial cursor: {initial_cursor}")
        except Exception as e:
            print(f"✗ Failed to get cursor: {e}")
            return False

        # Step 3: Trigger a chart command via function call
        print("\n3. Triggering chart command (change symbol to AAPL)...")
        try:
            resp = await client.post(
                f"{API_BASE}/api/function-call",
                json={
                    "name": "change_chart_symbol",
                    "arguments": {"symbol": "AAPL"}
                },
                headers={"X-Client-Session": SESSION_ID}
            )
            resp.raise_for_status()
            result = resp.json()
            print(f"✓ Function call result: {result}")

            if not result.get("success"):
                print(f"✗ Function call failed: {result.get('error')}")
                return False

        except Exception as e:
            print(f"✗ Function call failed: {e}")
            return False

        # Step 4: Poll for the new command
        print("\n4. Polling for new command...")
        try:
            await asyncio.sleep(0.5)  # Small delay to ensure command is published

            resp = await client.get(
                f"{API_BASE}/api/chart-commands",
                params={"sessionId": SESSION_ID, "cursor": initial_cursor, "limit": 10}
            )
            resp.raise_for_status()
            data = resp.json()
            commands = data.get("commands", [])
            new_cursor = data.get("cursor", 0)

            print(f"✓ Received {len(commands)} command(s), cursor: {new_cursor}")

            if not commands:
                print("✗ No commands received!")
                return False

            # Verify command structure
            cmd = commands[0]
            print(f"\n   Command Details:")
            print(f"   - Sequence: {cmd.get('seq')}")
            print(f"   - Timestamp: {cmd.get('timestamp')}")
            print(f"   - Type: {cmd.get('command', {}).get('type')}")
            print(f"   - Payload: {cmd.get('command', {}).get('payload')}")

            # Validate structure
            if 'seq' not in cmd:
                print("✗ Missing 'seq' field!")
                return False
            if 'timestamp' not in cmd:
                print("✗ Missing 'timestamp' field!")
                return False
            if 'command' not in cmd:
                print("✗ Missing 'command' field!")
                return False

            command_obj = cmd['command']
            if command_obj.get('type') != 'change_symbol':
                print(f"✗ Expected type 'change_symbol', got '{command_obj.get('type')}'")
                return False

            payload = command_obj.get('payload', {})
            if payload.get('symbol') != 'AAPL':
                print(f"✗ Expected symbol 'AAPL', got '{payload.get('symbol')}'")
                return False

            print("✓ Command structure validated!")

        except Exception as e:
            print(f"✗ Polling failed: {e}")
            return False

        # Step 5: Test cursor-based pagination (should get no new commands)
        print("\n5. Testing cursor-based pagination...")
        try:
            resp = await client.get(
                f"{API_BASE}/api/chart-commands",
                params={"sessionId": SESSION_ID, "cursor": new_cursor, "limit": 10}
            )
            resp.raise_for_status()
            data = resp.json()
            commands = data.get("commands", [])

            if commands:
                print(f"✗ Got {len(commands)} command(s) with cursor={new_cursor}, expected 0!")
                return False
            else:
                print("✓ No duplicate commands (cursor working correctly)")

        except Exception as e:
            print(f"✗ Cursor test failed: {e}")
            return False

        # Step 6: Test different session isolation
        print("\n6. Testing session isolation...")
        try:
            other_session = "other-session-456"
            resp = await client.get(
                f"{API_BASE}/api/chart-commands",
                params={"sessionId": other_session, "limit": 10}
            )
            resp.raise_for_status()
            data = resp.json()
            commands = data.get("commands", [])

            if commands:
                print(f"✗ Got {len(commands)} command(s) in different session, expected 0!")
                return False
            else:
                print("✓ Session isolation working correctly")

        except Exception as e:
            print(f"✗ Session isolation test failed: {e}")
            return False

        # Step 7: Test correlation ID
        print("\n7. Testing correlation ID middleware...")
        try:
            resp = await client.get(
                f"{API_BASE}/api/chart-commands",
                params={"sessionId": SESSION_ID},
                headers={"X-Request-ID": "test-correlation-123"}
            )
            resp.raise_for_status()

            correlation_id = resp.headers.get("X-Request-ID")
            if correlation_id != "test-correlation-123":
                print(f"✗ Expected correlation ID 'test-correlation-123', got '{correlation_id}'")
                return False
            else:
                print(f"✓ Correlation ID echoed correctly: {correlation_id}")

        except Exception as e:
            print(f"✗ Correlation ID test failed: {e}")
            return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_chart_command_polling())
    sys.exit(0 if result else 1)
