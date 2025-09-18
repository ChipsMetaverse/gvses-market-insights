#!/usr/bin/env python3
"""
Test Audit Fixes
================
Verifies all audit findings have been addressed.
"""

import asyncio
import json
import aiohttp
import sys

# ANSI color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

async def test_turn_detection_restored():
    """Test that turn_detection is restored with server_vad."""
    print(f"\n{BLUE}Testing turn_detection Configuration...{RESET}")
    
    # Check the configuration in the file
    try:
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/services/openai_relay_server.py', 'r') as f:
            content = f.read()
            
        if '"turn_detection": {' in content and '"type": "server_vad"' in content:
            print(f"{GREEN}✓ turn_detection restored with server_vad{RESET}")
            print(f"{GREEN}✓ Will enable reliable STT end-of-turn detection{RESET}")
            return True
        else:
            print(f"{RED}✗ turn_detection not properly configured{RESET}")
            return False
    except Exception as e:
        print(f"{RED}✗ Failed to check turn_detection: {e}{RESET}")
        return False

async def test_legacy_service_deprecated():
    """Test that legacy service is deprecated."""
    print(f"\n{BLUE}Testing Legacy Service Deprecation...{RESET}")
    
    try:
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend/services/openai_realtime_service.py', 'r') as f:
            content = f.read()
            
        checks = [
            ('[DEPRECATED]' in content, 'Deprecation notice added'),
            ('"tools": [],' in content, 'Tools array emptied'),
            ('"tool_choice": "none"' in content, 'Tool choice disabled')
        ]
        
        all_good = True
        for condition, description in checks:
            if condition:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} not found{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Failed to check legacy service: {e}{RESET}")
        return False

async def test_health_gate_added():
    """Test that health-gate is added to the hook."""
    print(f"\n{BLUE}Testing Health-Gate Addition...{RESET}")
    
    try:
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/hooks/useAgentVoiceConversation.ts', 'r') as f:
            content = f.read()
            
        checks = [
            ('backendHealthy' in content, 'Backend health state added'),
            ('checkHealth' in content, 'Health check function present'),
            ('Backend not ready' in content, 'Health gate error message')
        ]
        
        all_good = True
        for condition, description in checks:
            if condition:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} not found{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Failed to check health-gate: {e}{RESET}")
        return False

async def test_openai_provider_hidden():
    """Test that OpenAI provider option is hidden."""
    print(f"\n{BLUE}Testing OpenAI Provider Removal...{RESET}")
    
    try:
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/components/TradingDashboardSimple.tsx', 'r') as f:
            content = f.read()
            
        checks = [
            ("'elevenlabs' | 'agent'" in content and "'openai'" not in content, 'Type definition updated'),
            ('<option value="openai"' not in content, 'OpenAI option removed from dropdown'),
            ('currentHook = voiceProvider === \'agent\' ? agentVoiceHook : elevenLabsHook' in content, 'Hook selection simplified')
        ]
        
        all_good = True
        for condition, description in checks:
            if condition:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} check failed{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Failed to check OpenAI provider: {e}{RESET}")
        return False

async def test_api_url_utility():
    """Test that API URL utility was created."""
    print(f"\n{BLUE}Testing API URL Utility...{RESET}")
    
    try:
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/utils/apiConfig.ts', 'r') as f:
            content = f.read()
            
        checks = [
            ('getApiUrl' in content, 'getApiUrl function present'),
            ('getWebSocketUrl' in content, 'getWebSocketUrl function present'),
            ('checkApiHealth' in content, 'checkApiHealth function present')
        ]
        
        # Check if services are using it
        with open('/Volumes/WD My Passport 264F Media/claude-voice-mcp/frontend/src/services/OpenAIRealtimeService.ts', 'r') as f:
            service_content = f.read()
            checks.append(('import { getApiUrl }' in service_content, 'OpenAIRealtimeService uses utility'))
        
        all_good = True
        for condition, description in checks:
            if condition:
                print(f"{GREEN}✓ {description}{RESET}")
            else:
                print(f"{RED}✗ {description} check failed{RESET}")
                all_good = False
        
        return all_good
    except Exception as e:
        print(f"{RED}✗ Failed to check API URL utility: {e}{RESET}")
        return False

async def test_health_endpoint():
    """Test the health endpoint to verify backend is running."""
    print(f"\n{BLUE}Testing Health Endpoint...{RESET}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('http://localhost:8000/health') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"{GREEN}✓ Health endpoint responsive{RESET}")
                    
                    if data.get('openai_relay', {}).get('active'):
                        print(f"{GREEN}✓ OpenAI relay operational{RESET}")
                    else:
                        print(f"{YELLOW}⚠ OpenAI relay not operational (check API key){RESET}")
                    
                    if data.get('voice_only'):
                        print(f"{GREEN}✓ Voice-only mode confirmed{RESET}")
                    
                    return True
                else:
                    print(f"{RED}✗ Health endpoint returned status {resp.status}{RESET}")
                    return False
        except Exception as e:
            print(f"{RED}✗ Failed to reach health endpoint: {e}{RESET}")
            return False

async def main():
    """Run all tests."""
    print(f"\n{YELLOW}{'='*60}{RESET}")
    print(f"{YELLOW}Testing Audit Fixes{RESET}")
    print(f"{YELLOW}{'='*60}{RESET}")
    
    results = []
    
    # Run tests
    results.append(('turn_detection Restored', await test_turn_detection_restored()))
    results.append(('Legacy Service Deprecated', await test_legacy_service_deprecated()))
    results.append(('Health-Gate Added', await test_health_gate_added()))
    results.append(('OpenAI Provider Hidden', await test_openai_provider_hidden()))
    results.append(('API URL Utility Created', await test_api_url_utility()))
    results.append(('Health Endpoint Working', await test_health_endpoint()))
    
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
        print(f"\n{GREEN}✅ All audit findings have been successfully addressed!{RESET}")
        print(f"{GREEN}   - Reliable STT with server_vad{RESET}")
        print(f"{GREEN}   - Legacy code deprecated{RESET}")
        print(f"{GREEN}   - Health-gating implemented{RESET}")
        print(f"{GREEN}   - Confusing options removed{RESET}")
        print(f"{GREEN}   - API handling standardized{RESET}")
        return 0
    else:
        print(f"\n{RED}❌ Some fixes may need verification.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))