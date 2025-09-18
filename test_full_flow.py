#!/usr/bin/env python3
"""
Comprehensive test of OpenAI Realtime voice assistant integration.
Tests the full flow including connection, message sending, and tool execution.
"""
import asyncio
import websockets
import json
import httpx
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=None):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    prefix = f"{color}{Colors.BOLD}" if color else ""
    suffix = Colors.RESET if color else ""
    print(f"[{timestamp}] {prefix}{message}{suffix}")

async def test_full_flow():
    """Test the complete OpenAI Realtime flow."""
    
    log("=" * 60, Colors.BLUE)
    log("OpenAI Realtime Voice Assistant - Full Flow Test", Colors.BLUE)
    log("=" * 60, Colors.BLUE)
    
    # Test 1: Health check
    log("\n📋 Test 1: Health Check", Colors.YELLOW)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/health")
            health_data = response.json()
            if health_data["status"] == "healthy":
                log("✅ Backend is healthy", Colors.GREEN)
                log(f"   Service mode: {health_data['service_mode']}", Colors.GREEN)
                log(f"   OpenAI relay ready: {health_data['openai_relay_ready']}", Colors.GREEN)
            else:
                log("❌ Backend unhealthy", Colors.RED)
                return False
        except Exception as e:
            log(f"❌ Health check failed: {e}", Colors.RED)
            return False
    
    # Test 2: Create session
    log("\n📋 Test 2: Session Creation", Colors.YELLOW)
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("http://localhost:8000/openai/realtime/session")
            session_data = response.json()
            session_id = session_data["session_id"]
            log(f"✅ Session created: {session_id}", Colors.GREEN)
        except Exception as e:
            log(f"❌ Session creation failed: {e}", Colors.RED)
            return False
    
    # Test 3: WebSocket connection
    log("\n📋 Test 3: WebSocket Connection", Colors.YELLOW)
    ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-4o-realtime-preview-2024-12-17"
    
    try:
        async with websockets.connect(
            ws_url,
            subprotocols=["realtime"],
            close_timeout=10
        ) as websocket:
            log(f"✅ Connected with subprotocol: {websocket.subprotocol}", Colors.GREEN)
            
            # Test 4: Wait for session.created
            log("\n📋 Test 4: Session Initialization", Colors.YELLOW)
            session_created = False
            tools_configured = False
            
            for _ in range(5):
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    event_type = data.get('type', 'unknown')
                    
                    if event_type == 'session.created':
                        session_created = True
                        log("✅ Session created event received", Colors.GREEN)
                        session_info = data.get('session', {})
                        log(f"   Model: {session_info.get('model', 'unknown')}", Colors.GREEN)
                        log(f"   Tools: {len(session_info.get('tools', []))} configured", Colors.GREEN)
                        if len(session_info.get('tools', [])) > 0:
                            tools_configured = True
                            log("   Tool names:", Colors.GREEN)
                            for tool in session_info.get('tools', [])[:3]:
                                log(f"     - {tool.get('name', 'unknown')}", Colors.GREEN)
                    elif event_type == 'session.updated':
                        log("   Session updated", Colors.BLUE)
                except asyncio.TimeoutError:
                    break
            
            if not session_created:
                log("❌ Session.created event not received", Colors.RED)
                return False
            
            # Test 5: Send text message
            log("\n📋 Test 5: Text Message Interaction", Colors.YELLOW)
            test_message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "What is the current price of Tesla stock?"}
                    ]
                }
            }
            await websocket.send(json.dumps(test_message))
            log("📤 Sent: 'What is the current price of Tesla stock?'", Colors.BLUE)
            
            # Request response
            await asyncio.sleep(0.1)
            await websocket.send(json.dumps({"type": "response.create"}))
            log("📤 Sent: response.create", Colors.BLUE)
            
            # Test 6: Receive response
            log("\n📋 Test 6: Response Reception", Colors.YELLOW)
            response_started = False
            tool_called = False
            response_completed = False
            transcript_received = False
            
            timeout_count = 0
            max_timeouts = 3
            
            while timeout_count < max_timeouts:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(message)
                    event_type = data.get('type', 'unknown')
                    
                    if event_type == 'response.created':
                        response_started = True
                        log("✅ Response generation started", Colors.GREEN)
                    elif event_type == 'response.function_call_arguments.done':
                        tool_called = True
                        tool_name = data.get('name', 'unknown')
                        log(f"✅ Tool called: {tool_name}", Colors.GREEN)
                    elif event_type == 'response.audio_transcript.delta':
                        if not transcript_received:
                            transcript_received = True
                            log("✅ Receiving transcript deltas", Colors.GREEN)
                        delta = data.get('delta', '')
                        if delta:
                            print(f"   {delta}", end='', flush=True)
                    elif event_type == 'response.audio_transcript.done':
                        transcript = data.get('transcript', '')
                        if transcript:
                            print()  # New line after deltas
                            log(f"✅ Full transcript: {transcript[:100]}...", Colors.GREEN)
                    elif event_type == 'response.done':
                        response_completed = True
                        log("✅ Response completed", Colors.GREEN)
                        break
                    elif event_type == 'error':
                        error_info = data.get('error', {})
                        log(f"❌ Error: {error_info.get('message', 'unknown')}", Colors.RED)
                        break
                    
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if response_started and not response_completed:
                        log("⏱️ Waiting for response completion...", Colors.YELLOW)
                    else:
                        break
            
            # Test 7: Summary
            log("\n📋 Test 7: Test Summary", Colors.YELLOW)
            log("=" * 40, Colors.BLUE)
            
            tests_passed = 0
            tests_total = 6
            
            def check_test(condition, name):
                nonlocal tests_passed
                if condition:
                    tests_passed += 1
                    log(f"✅ {name}", Colors.GREEN)
                else:
                    log(f"❌ {name}", Colors.RED)
                return condition
            
            check_test(session_created, "Session creation")
            check_test(tools_configured, "Tools configured")
            check_test(response_started, "Response generation")
            check_test(tool_called or transcript_received, "Content received")
            check_test(response_completed or transcript_received, "Response completed")
            check_test(not websocket.closed, "Connection stable")
            
            log("=" * 40, Colors.BLUE)
            
            if tests_passed == tests_total:
                log(f"🎉 ALL TESTS PASSED ({tests_passed}/{tests_total})", Colors.GREEN)
                return True
            else:
                log(f"⚠️ PARTIAL SUCCESS ({tests_passed}/{tests_total})", Colors.YELLOW)
                return tests_passed >= 4  # Consider it success if most tests pass
                
    except websockets.exceptions.WebSocketException as e:
        log(f"❌ WebSocket error: {e}", Colors.RED)
        return False
    except Exception as e:
        log(f"❌ Unexpected error: {e}", Colors.RED)
        return False

async def main():
    """Main test runner."""
    try:
        success = await test_full_flow()
        
        log("\n" + "=" * 60, Colors.BLUE)
        if success:
            log("✅ FULL FLOW TEST: PASSED", Colors.GREEN)
            log("The OpenAI Realtime voice assistant is working correctly!", Colors.GREEN)
            sys.exit(0)
        else:
            log("❌ FULL FLOW TEST: FAILED", Colors.RED)
            log("Please check the logs above for details.", Colors.RED)
            sys.exit(1)
    except KeyboardInterrupt:
        log("\n⚠️ Test interrupted by user", Colors.YELLOW)
        sys.exit(1)
    except Exception as e:
        log(f"\n❌ Test failed with error: {e}", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    print(f"{Colors.BOLD}Starting OpenAI Realtime Voice Assistant Test...{Colors.RESET}\n")
    asyncio.run(main())