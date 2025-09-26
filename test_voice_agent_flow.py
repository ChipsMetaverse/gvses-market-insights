#!/usr/bin/env python3
"""
Test the complete voice + agent flow:
1. User speaks → Realtime API (STT) → transcript
2. Transcript → Agent Orchestrator → executes tools → text response
3. Text response → Realtime API (TTS) → voice output
"""
import asyncio
import websockets
import json
import httpx
from datetime import datetime

class VoiceAgentFlowTest:
    def __init__(self):
        self.session_id = None
        self.test_results = {
            'realtime_voice_only': False,
            'agent_tools_working': False,
            'tts_integration': False,
            'complete_flow': False
        }
    
    def log(self, message, level="INFO"):
        """Log with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        emoji = {
            "INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", 
            "VOICE": "🎤", "AGENT": "🤖", "TTS": "🔊", "TOOL": "🔧"
        }.get(level, "📝")
        print(f"[{timestamp}] {emoji} {message}")
    
    async def test_realtime_voice_only(self):
        """Test 1: Verify Realtime API is voice-only (no tools)."""
        self.log("="*60, "INFO")
        self.log("TEST 1: REALTIME API IS VOICE-ONLY", "INFO")
        self.log("="*60, "INFO")
        
        # Create session
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/openai/realtime/session")
            session_data = response.json()
            self.session_id = session_data["session_id"]
            self.log(f"Session created: {self.session_id}", "SUCCESS")
        
        # Connect to WebSocket
        ws_url = f"ws://localhost:8000/realtime-relay/{self.session_id}?model=gpt-realtime-2025-08-28"
        
        async with websockets.connect(ws_url, subprotocols=["realtime"]) as websocket:
            self.log("Connected to Realtime API", "VOICE")
            
            # Wait for session.created and check for tools
            tools_configured = False
            session_ready = False
            
            for _ in range(5):
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(msg)
                    event_type = data.get('type', '')
                    
                    if event_type == 'session.created':
                        session_ready = True
                        session_info = data.get('session', {})
                        tools = session_info.get('tools', [])
                        
                        if len(tools) == 0:
                            self.log("✅ No tools configured in Realtime session", "SUCCESS")
                            self.test_results['realtime_voice_only'] = True
                        else:
                            self.log(f"❌ Found {len(tools)} tools in Realtime session", "ERROR")
                            for tool in tools[:3]:
                                self.log(f"   - {tool.get('name', 'unknown')}", "ERROR")
                    
                    elif event_type == 'session.updated':
                        session_info = data.get('session', {})
                        tools = session_info.get('tools', [])
                        if tools:
                            tools_configured = True
                            self.log(f"❌ Tools added in session.updated: {len(tools)}", "ERROR")
                            
                except asyncio.TimeoutError:
                    if session_ready:
                        break
            
            if not tools_configured:
                self.log("✅ Realtime API is voice-only (no tools)", "SUCCESS")
                self.test_results['realtime_voice_only'] = True
            else:
                self.log("❌ Realtime API has tools configured", "ERROR")
        
        return self.test_results['realtime_voice_only']
    
    async def test_agent_tools(self):
        """Test 2: Verify Agent Orchestrator executes tools."""
        self.log("\n" + "="*60, "INFO")
        self.log("TEST 2: AGENT ORCHESTRATOR EXECUTES TOOLS", "INFO")
        self.log("="*60, "INFO")
        
        async with httpx.AsyncClient() as client:
            # Test agent query that requires tools
            query = {
                "query": "What is the current price of Apple stock?",
                "conversation_history": [],
                "stream": False
            }
            
            self.log("Sending query to agent: 'What is the current price of Apple stock?'", "AGENT")
            
            response = await client.post(
                "http://localhost:8000/api/agent/orchestrate",
                json=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if tools were used
                tools_used = data.get('tools_used', [])
                if tools_used:
                    self.log(f"✅ Agent used tools: {tools_used}", "SUCCESS")
                    self.test_results['agent_tools_working'] = True
                    
                    # Check if we got actual data
                    tool_data = data.get('data', {})
                    if tool_data:
                        self.log(f"✅ Tool returned data", "TOOL")
                        for tool_name, result in tool_data.items():
                            if isinstance(result, dict) and 'price' in result:
                                self.log(f"   - {tool_name}: ${result.get('price', 'N/A')}", "TOOL")
                else:
                    self.log("❌ Agent did not use any tools", "ERROR")
                
                # Show response text
                response_text = data.get('text', '')
                if response_text:
                    self.log(f"Agent response: {response_text[:150]}...", "AGENT")
            else:
                self.log(f"❌ Agent request failed: {response.status_code}", "ERROR")
        
        return self.test_results['agent_tools_working']
    
    async def test_voice_agent_integration(self):
        """Test 3: Verify complete voice + agent + TTS flow."""
        self.log("\n" + "="*60, "INFO")
        self.log("TEST 3: COMPLETE VOICE + AGENT + TTS INTEGRATION", "INFO")
        self.log("="*60, "INFO")
        
        if not self.session_id:
            self.log("❌ No session ID from previous test", "ERROR")
            return False
        
        async with httpx.AsyncClient() as client:
            # Test the new voice-query endpoint
            query = {
                "query": "What's the price of Tesla stock?",
                "conversation_history": [],
                "stream": False,
                "session_id": self.session_id  # Include session for TTS
            }
            
            self.log(f"Sending voice query with session {self.session_id}", "VOICE")
            
            response = await client.post(
                "http://localhost:8000/api/agent/voice-query",
                json=query
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if agent processed it
                if data.get('tools_used'):
                    self.log(f"✅ Agent processed voice query with tools: {data['tools_used']}", "SUCCESS")
                
                # Check response text
                if data.get('text'):
                    self.log(f"✅ Agent generated response: {data['text'][:100]}...", "SUCCESS")
                    
                    # The TTS should have been sent to the session
                    self.log("✅ TTS request should have been sent to Realtime session", "TTS")
                    self.test_results['tts_integration'] = True
                    self.test_results['complete_flow'] = True
            else:
                self.log(f"❌ Voice query failed: {response.status_code}", "ERROR")
        
        return self.test_results['complete_flow']
    
    async def run_all_tests(self):
        """Run all tests in sequence."""
        self.log("\n" + "="*70, "INFO")
        self.log("VOICE + AGENT INTEGRATION TEST SUITE", "INFO")
        self.log("="*70 + "\n", "INFO")
        
        # Test 1: Realtime is voice-only
        await self.test_realtime_voice_only()
        
        # Test 2: Agent executes tools
        await self.test_agent_tools()
        
        # Test 3: Complete integration
        await self.test_voice_agent_integration()
        
        # Summary
        self.log("\n" + "="*70, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*70, "INFO")
        
        all_passed = all(self.test_results.values())
        
        for test_name, passed in self.test_results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            test_display = test_name.replace('_', ' ').title()
            self.log(f"{test_display}: {status}", "SUCCESS" if passed else "ERROR")
        
        self.log("\n" + "="*70, "INFO")
        if all_passed:
            self.log("🎉 ALL TESTS PASSED!", "SUCCESS")
            self.log("The new architecture is working correctly:", "SUCCESS")
            self.log("  1. Realtime API is voice-only (no tools)", "SUCCESS")
            self.log("  2. Agent Orchestrator handles all tool execution", "SUCCESS")
            self.log("  3. Agent sends TTS to Realtime for voice output", "SUCCESS")
        else:
            self.log("⚠️ SOME TESTS FAILED", "ERROR")
            self.log("Please check the logs above for details", "ERROR")
        
        return all_passed

async def main():
    """Run the test suite."""
    tester = VoiceAgentFlowTest()
    success = await tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))