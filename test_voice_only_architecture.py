#!/usr/bin/env python3
"""
Test Voice-Only Architecture
=============================
Verifies that OpenAI Realtime is properly configured as voice I/O only,
with all intelligence and tools handled by the agent orchestrator.
"""

import asyncio
import json
import aiohttp
import sys
from datetime import datetime

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

async def test_backend_relay_config():
    """Test that the backend relay server is configured correctly."""
    print(f"\n{BLUE}Testing Backend Relay Configuration...{RESET}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create a session to check configuration
            async with session.post('http://localhost:8000/openai/realtime/session') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"{GREEN}✓ Session created: {data.get('session_id')}{RESET}")
                    
                    # The actual config is sent via WebSocket, but we can verify the endpoint works
                    print(f"{GREEN}✓ Relay server endpoint responsive{RESET}")
                    return True
                else:
                    print(f"{RED}✗ Failed to create session: {resp.status}{RESET}")
                    return False
        except Exception as e:
            print(f"{RED}✗ Backend relay error: {e}{RESET}")
            return False

async def test_agent_orchestrator():
    """Test that the agent orchestrator is working."""
    print(f"\n{BLUE}Testing Agent Orchestrator...{RESET}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test agent query endpoint
            payload = {
                "query": "What is the current price of TSLA?",
                "conversation_history": []
            }
            
            async with session.post(
                'http://localhost:8000/api/agent/orchestrate',
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"{GREEN}✓ Agent responded: {data.get('text', '')[:100]}...{RESET}")
                    if data.get('tools_used'):
                        print(f"{GREEN}✓ Tools used: {', '.join(data['tools_used'])}{RESET}")
                    return True
                else:
                    print(f"{RED}✗ Agent query failed: {resp.status}{RESET}")
                    text = await resp.text()
                    print(f"{RED}  Response: {text[:200]}{RESET}")
                    return False
        except Exception as e:
            print(f"{RED}✗ Agent orchestrator error: {e}{RESET}")
            return False

async def test_voice_query_integration():
    """Test the voice-query endpoint that integrates agent with TTS."""
    print(f"\n{BLUE}Testing Voice-Query Integration...{RESET}")
    
    async with aiohttp.ClientSession() as session:
        try:
            # First create a session
            async with session.post('http://localhost:8000/openai/realtime/session') as resp:
                if resp.status != 200:
                    print(f"{RED}✗ Failed to create session for voice-query test{RESET}")
                    return False
                
                session_data = await resp.json()
                session_id = session_data.get('session_id')
            
            # Test voice-query endpoint
            payload = {
                "query": "The price of Apple stock is currently $230",
                "session_id": session_id
            }
            
            async with session.post(
                'http://localhost:8000/api/agent/voice-query',
                json=payload
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"{GREEN}✓ Voice-query processed successfully{RESET}")
                    print(f"{GREEN}✓ Response will be sent to TTS for session: {session_id}{RESET}")
                    return True
                else:
                    print(f"{RED}✗ Voice-query failed: {resp.status}{RESET}")
                    return False
        except Exception as e:
            print(f"{RED}✗ Voice-query integration error: {e}{RESET}")
            return False

async def verify_no_tools_in_relay():
    """Verify that the relay server has no tools configured."""
    print(f"\n{BLUE}Verifying No Tools in Relay...{RESET}")
    
    # We can't directly inspect the WebSocket config, but we can check the code
    relay_file = '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/services/openai_relay_server.py'
    
    try:
        with open(relay_file, 'r') as f:
            content = f.read()
            
        checks = [
            ('"tools": []', 'Empty tools array'),
            ('"tool_choice": "none"', 'Tool choice disabled'),
            ('"turn_detection": None', 'Turn detection disabled'),
            ('Voice-only instructions', 'Voice-only instructions present')
        ]
        
        all_good = True
        for pattern, description in checks:
            if pattern in content:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} not found{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Could not verify relay configuration: {e}{RESET}")
        return False

async def verify_frontend_changes():
    """Verify that frontend changes were applied correctly."""
    print(f"\n{BLUE}Verifying Frontend Changes...{RESET}")
    
    frontend_file = '/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/services/OpenAIRealtimeService.ts'
    
    try:
        with open(frontend_file, 'r') as f:
            content = f.read()
        
        checks = [
            ('interface MarketDataTool' not in content, 'MarketDataTool interface removed'),
            ('setupMarketDataTools' not in content, 'setupMarketDataTools method removed'),
            ('tools: Map<string, MarketDataTool>' not in content, 'tools Map removed'),
            ("Don't emit assistant transcripts" in content, 'Assistant transcript filtering added'),
            ('// User transcripts: final=false during speaking' in content, 'User transcript logic documented')
        ]
        
        all_good = True
        for condition, description in checks:
            if condition:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} - check failed{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Could not verify frontend changes: {e}{RESET}")
        return False

async def main():
    """Run all tests."""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Testing Voice-Only Architecture{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    results = []
    
    # Run tests
    results.append(('Backend Relay Config', await test_backend_relay_config()))
    results.append(('Agent Orchestrator', await test_agent_orchestrator()))
    results.append(('Voice-Query Integration', await test_voice_query_integration()))
    results.append(('No Tools in Relay', await verify_no_tools_in_relay()))
    results.append(('Frontend Changes', await verify_frontend_changes()))
    
    # Summary
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Test Summary{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASSED{RESET}" if result else f"{RED}FAILED{RESET}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{YELLOW}Total: {passed}/{total} tests passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}✅ Voice-only architecture is properly configured!{RESET}")
        print(f"{GREEN}   - Realtime handles only voice I/O (STT + TTS){RESET}")
        print(f"{GREEN}   - Agent orchestrator handles all intelligence and tools{RESET}")
        print(f"{GREEN}   - No auto-responses from Realtime{RESET}")
        return 0
    else:
        print(f"\n{RED}❌ Some tests failed. Please review the configuration.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))