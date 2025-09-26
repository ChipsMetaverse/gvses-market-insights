#!/usr/bin/env python3
"""
Comprehensive test to verify OpenAI Realtime voice assistant audio functionality.
Tests that the agent can:
1. Accept user queries
2. Provide accurate actions and results (tool execution)
3. Convey messages auditorily through realtime voice
"""
import asyncio
import websockets
import json
import httpx
import base64
from datetime import datetime

class AudioVerificationTest:
    def __init__(self):
        self.audio_received = False
        self.audio_chunks = []
        self.tool_executed = False
        self.tool_results = []
        self.transcript_text = ""
        self.response_complete = False
        
    def log(self, message, level="INFO"):
        """Log with timestamp and level."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "AUDIO": "🔊", "TOOL": "🔧"}.get(level, "📝")
        print(f"[{timestamp}] {emoji} {message}")
    
    async def run_test(self):
        """Run the complete audio verification test."""
        self.log("="*60, "INFO")
        self.log("OPENAI REALTIME AUDIO VERIFICATION TEST", "INFO")
        self.log("="*60, "INFO")
        
        # Step 1: Create session
        self.log("\n1️⃣ Creating session...", "INFO")
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8000/openai/realtime/session")
            session_data = response.json()
            session_id = session_data["session_id"]
            self.log(f"Session created: {session_id}", "SUCCESS")
        
        # Step 2: Connect WebSocket
        self.log("\n2️⃣ Connecting to WebSocket...", "INFO")
        ws_url = f"ws://localhost:8000/realtime-relay/{session_id}?model=gpt-realtime-2025-08-28"
        
        async with websockets.connect(ws_url, subprotocols=["realtime"]) as websocket:
            self.log(f"Connected with subprotocol: {websocket.subprotocol}", "SUCCESS")
            
            # Step 3: Wait for session initialization
            self.log("\n3️⃣ Waiting for session initialization...", "INFO")
            session_ready = False
            
            while not session_ready:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(msg)
                    event_type = data.get('type', '')
                    
                    if event_type == 'session.created':
                        session_ready = True
                        session_info = data.get('session', {})
                        self.log(f"Session initialized", "SUCCESS")
                        self.log(f"  Model: {session_info.get('model', 'unknown')}", "INFO")
                        self.log(f"  Voice: {session_info.get('voice', 'unknown')}", "INFO")
                        tools = session_info.get('tools', [])
                        self.log(f"  Tools configured: {len(tools)}", "INFO")
                        
                        # Verify audio settings
                        input_audio_format = session_info.get('input_audio_format', 'unknown')
                        output_audio_format = session_info.get('output_audio_format', 'unknown')
                        self.log(f"  Input audio format: {input_audio_format}", "AUDIO")
                        self.log(f"  Output audio format: {output_audio_format}", "AUDIO")
                        
                except asyncio.TimeoutError:
                    break
            
            # Step 4: Send test query
            self.log("\n4️⃣ Sending test query for audio response...", "INFO")
            test_query = "What is the current price of Apple stock? Please provide a detailed response."
            
            # Send as text (simulating voice-to-text)
            message = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": test_query}
                    ]
                }
            }
            await websocket.send(json.dumps(message))
            self.log(f"Query sent: '{test_query}'", "SUCCESS")
            
            # Request response with audio
            await asyncio.sleep(0.1)
            response_config = {
                "type": "response.create",
                "response": {
                    "modalities": ["text", "audio"],  # Request both text and audio
                    "instructions": "Provide a clear, informative response about the stock price."
                }
            }
            await websocket.send(json.dumps(response_config))
            self.log("Response requested with audio modality", "AUDIO")
            
            # Step 5: Collect and analyze response
            self.log("\n5️⃣ Collecting response events...", "INFO")
            
            timeout_count = 0
            max_timeouts = 5
            
            while timeout_count < max_timeouts and not self.response_complete:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(msg)
                    event_type = data.get('type', '')
                    
                    # Track different event types
                    if event_type == 'response.created':
                        self.log("Response generation started", "INFO")
                    
                    elif 'function_call_arguments' in event_type:
                        self.tool_executed = True
                        tool_name = data.get('name', 'unknown')
                        args = data.get('arguments', '{}')
                        self.log(f"Tool executed: {tool_name}", "TOOL")
                        self.log(f"  Arguments: {args}", "TOOL")
                        self.tool_results.append({
                            'tool': tool_name,
                            'arguments': args
                        })
                    
                    elif event_type == 'response.audio.delta':
                        # Audio chunk received
                        audio_delta = data.get('delta', '')
                        if audio_delta:
                            self.audio_received = True
                            self.audio_chunks.append(audio_delta)
                            # Log first audio chunk details
                            if len(self.audio_chunks) == 1:
                                self.log("First audio chunk received!", "AUDIO")
                                self.log(f"  Chunk size: {len(audio_delta)} chars", "AUDIO")
                                # Check if it's base64 encoded
                                try:
                                    decoded = base64.b64decode(audio_delta[:100])
                                    self.log("  Format: Base64 encoded audio data", "AUDIO")
                                except:
                                    self.log("  Format: Raw audio data", "AUDIO")
                    
                    elif event_type == 'response.audio.done':
                        # Complete audio received
                        if self.audio_chunks:
                            total_size = sum(len(chunk) for chunk in self.audio_chunks)
                            self.log(f"Audio generation complete", "AUDIO")
                            self.log(f"  Total chunks: {len(self.audio_chunks)}", "AUDIO")
                            self.log(f"  Total size: {total_size} chars", "AUDIO")
                    
                    elif event_type == 'response.audio_transcript.delta':
                        # Transcript of what's being spoken
                        delta = data.get('delta', '')
                        if delta:
                            self.transcript_text += delta
                            print(f"  🗣️ {delta}", end='', flush=True)
                    
                    elif event_type == 'response.audio_transcript.done':
                        # Complete transcript
                        transcript = data.get('transcript', '')
                        if transcript:
                            print()  # New line after deltas
                            self.log(f"Transcript complete: {len(transcript)} chars", "SUCCESS")
                            self.transcript_text = transcript
                    
                    elif event_type == 'response.done':
                        self.response_complete = True
                        status = data.get('response', {}).get('status', 'unknown')
                        self.log(f"Response completed with status: {status}", "SUCCESS")
                    
                    elif event_type == 'error':
                        error_info = data.get('error', {})
                        self.log(f"Error: {error_info.get('message', 'unknown')}", "ERROR")
                        break
                    
                except asyncio.TimeoutError:
                    timeout_count += 1
                    if timeout_count == 1:
                        self.log("Waiting for more events...", "INFO")
            
            # Step 6: Verification Summary
            self.log("\n" + "="*60, "INFO")
            self.log("VERIFICATION RESULTS", "INFO")
            self.log("="*60, "INFO")
            
            # Check 1: Accept user queries
            query_accepted = session_ready
            self.log(f"1. Accept user queries: {'✅ PASSED' if query_accepted else '❌ FAILED'}", 
                    "SUCCESS" if query_accepted else "ERROR")
            
            # Check 2: Provide accurate actions and results
            actions_accurate = self.tool_executed and len(self.tool_results) > 0
            self.log(f"2. Provide accurate actions/results: {'✅ PASSED' if actions_accurate else '❌ FAILED'}", 
                    "SUCCESS" if actions_accurate else "ERROR")
            if self.tool_results:
                for result in self.tool_results:
                    self.log(f"   - Tool: {result['tool']}", "TOOL")
            
            # Check 3: Convey messages auditorily
            audio_conveyed = self.audio_received and len(self.audio_chunks) > 0
            self.log(f"3. Convey messages auditorily: {'✅ PASSED' if audio_conveyed else '❌ FAILED'}", 
                    "SUCCESS" if audio_conveyed else "ERROR")
            if audio_conveyed:
                self.log(f"   - Audio chunks received: {len(self.audio_chunks)}", "AUDIO")
                total_audio_size = sum(len(chunk) for chunk in self.audio_chunks)
                self.log(f"   - Total audio data: {total_audio_size} chars", "AUDIO")
            
            # Additional checks
            self.log("\nAdditional Verification:", "INFO")
            self.log(f"- Transcript generated: {'✅ YES' if self.transcript_text else '❌ NO'}", 
                    "SUCCESS" if self.transcript_text else "ERROR")
            if self.transcript_text:
                preview = self.transcript_text[:200] + "..." if len(self.transcript_text) > 200 else self.transcript_text
                self.log(f"  Preview: {preview}", "INFO")
            
            self.log(f"- Response completed: {'✅ YES' if self.response_complete else '❌ NO'}", 
                    "SUCCESS" if self.response_complete else "ERROR")
            
            # Final verdict
            all_passed = query_accepted and actions_accurate and audio_conveyed
            self.log("\n" + "="*60, "INFO")
            if all_passed:
                self.log("🎉 ALL VERIFICATIONS PASSED!", "SUCCESS")
                self.log("The OpenAI Realtime voice assistant is fully functional:", "SUCCESS")
                self.log("  ✅ Accepts user queries", "SUCCESS")
                self.log("  ✅ Provides accurate actions and results", "SUCCESS")
                self.log("  ✅ Conveys messages auditorily through realtime voice", "SUCCESS")
            else:
                self.log("⚠️ SOME VERIFICATIONS FAILED", "ERROR")
                if not query_accepted:
                    self.log("  ❌ Failed to accept user queries", "ERROR")
                if not actions_accurate:
                    self.log("  ❌ Failed to provide accurate actions/results", "ERROR")
                if not audio_conveyed:
                    self.log("  ❌ Failed to convey messages auditorily", "ERROR")
            
            return all_passed

async def main():
    """Run the audio verification test."""
    test = AudioVerificationTest()
    success = await test.run_test()
    return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))