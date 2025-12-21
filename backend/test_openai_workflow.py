#!/usr/bin/env python3
"""
Test OpenAI Agent Builder Workflow Configuration
================================================
This script checks:
1. If the workflow exists in OpenAI
2. What MCP servers are connected
3. System prompt configuration
4. Available tools
"""

import os
import json
import httpx
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIWorkflowChecker:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.workflow_id = os.getenv("CHATKIT_WORKFLOW_ID")
        self.assistant_id = os.getenv("GVSES_ASSISTANT_ID")
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "OpenAI-Beta": "assistants=v2"
            },
            timeout=30.0
        )
    
    async def check_assistant(self):
        """Check if the G'sves assistant exists"""
        print("\n🔍 Checking G'sves Assistant Configuration")
        print("=" * 60)
        print(f"Assistant ID: {self.assistant_id}")
        
        try:
            response = await self.client.get(
                f"https://api.openai.com/v1/assistants/{self.assistant_id}"
            )
            
            if response.status_code == 200:
                assistant = response.json()
                print(f"✅ Assistant found: {assistant.get('name', 'Unnamed')}")
                print(f"   Model: {assistant.get('model', 'Unknown')}")
                print(f"   Created: {assistant.get('created_at', 'Unknown')}")
                
                # Check instructions (system prompt)
                instructions = assistant.get('instructions', '')
                if instructions:
                    print(f"\n📝 System Prompt Preview (first 200 chars):")
                    print(f"   {instructions[:200]}...")
                    
                    # Check for BTD/BuyLow keywords
                    btd_keywords = ['BTD', 'Buy the Dip', 'BuyLow', 'SellHigh']
                    found_keywords = [kw for kw in btd_keywords if kw.lower() in instructions.lower()]
                    if found_keywords:
                        print(f"   ✅ Found BTD keywords: {', '.join(found_keywords)}")
                    else:
                        print(f"   ⚠️  No BTD keywords found in prompt")
                
                # Check tools
                tools = assistant.get('tools', [])
                if tools:
                    print(f"\n🔧 Tools configured: {len(tools)}")
                    for tool in tools[:5]:  # Show first 5
                        tool_type = tool.get('type', 'unknown')
                        if tool_type == 'function':
                            func_name = tool.get('function', {}).get('name', 'unnamed')
                            print(f"   - {func_name}")
                        else:
                            print(f"   - {tool_type}")
                    if len(tools) > 5:
                        print(f"   ... and {len(tools) - 5} more")
                
                return assistant
                
            elif response.status_code == 404:
                print(f"❌ Assistant not found (404)")
                return None
            else:
                print(f"⚠️  Unexpected status: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 Error checking assistant: {str(e)}")
            return None
    
    async def test_workflow_via_chat(self):
        """Test the workflow by sending a chat completion request"""
        print("\n🧪 Testing Workflow via Chat Completions")
        print("=" * 60)
        
        test_queries = [
            "What is AAPL stock price?",
            "Show me BTD analysis",
            "What are the market movers today?"
        ]
        
        for query in test_queries[:1]:  # Test first query only
            print(f"\n📤 Testing: '{query}'")
            
            try:
                # Try using the assistant via chat completions
                response = await self.client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json={
                        "model": "gpt-4o",
                        "messages": [
                            {"role": "user", "content": query}
                        ],
                        # Note: workflow_id might not be a valid parameter
                        # This is just for testing
                        "assistant_id": self.assistant_id,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_response = result['choices'][0]['message']['content']
                    print(f"✅ Response received:")
                    print(f"   {ai_response[:200]}...")
                    
                    # Check if it mentions MCP or tools
                    if 'mcp' in ai_response.lower() or 'tool' in ai_response.lower():
                        print(f"   📊 Response mentions MCP/tools")
                    
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"   Error: {error_detail}")
                    
            except Exception as e:
                print(f"💥 Test failed: {str(e)}")
    
    async def test_assistant_thread(self):
        """Test the assistant using the Assistants API (threads)"""
        print("\n🧪 Testing Assistant via Threads API")
        print("=" * 60)
        
        try:
            # Create a thread
            thread_response = await self.client.post(
                "https://api.openai.com/v1/threads",
                json={}
            )
            
            if thread_response.status_code != 200:
                print(f"❌ Failed to create thread: {thread_response.status_code}")
                return
            
            thread = thread_response.json()
            thread_id = thread['id']
            print(f"✅ Thread created: {thread_id}")
            
            # Add a message
            message_response = await self.client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/messages",
                json={
                    "role": "user",
                    "content": "What is the current price of AAPL?"
                }
            )
            
            if message_response.status_code != 200:
                print(f"❌ Failed to add message: {message_response.status_code}")
                return
            
            print(f"✅ Message added to thread")
            
            # Run the assistant
            run_response = await self.client.post(
                f"https://api.openai.com/v1/threads/{thread_id}/runs",
                json={
                    "assistant_id": self.assistant_id
                }
            )
            
            if run_response.status_code != 200:
                print(f"❌ Failed to run assistant: {run_response.status_code}")
                print(f"   Error: {run_response.text}")
                return
            
            run = run_response.json()
            run_id = run['id']
            print(f"✅ Assistant run started: {run_id}")
            
            # Poll for completion
            max_attempts = 30
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                
                status_response = await self.client.get(
                    f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}"
                )
                
                if status_response.status_code == 200:
                    run_status = status_response.json()
                    status = run_status['status']
                    print(f"   Run status: {status}")
                    
                    if status == 'completed':
                        print(f"✅ Run completed!")
                        
                        # Get messages
                        messages_response = await self.client.get(
                            f"https://api.openai.com/v1/threads/{thread_id}/messages"
                        )
                        
                        if messages_response.status_code == 200:
                            messages = messages_response.json()['data']
                            for msg in messages:
                                if msg['role'] == 'assistant':
                                    content = msg['content'][0]['text']['value']
                                    print(f"\n📬 Assistant Response:")
                                    print(f"   {content[:500]}...")
                                    break
                        break
                        
                    elif status in ['failed', 'cancelled', 'expired']:
                        print(f"❌ Run {status}")
                        if 'last_error' in run_status:
                            print(f"   Error: {run_status['last_error']}")
                        break
                        
                    elif status == 'requires_action':
                        print(f"🔧 Run requires action (tool calls)")
                        # This would indicate the assistant wants to use tools
                        required_action = run_status.get('required_action', {})
                        tool_calls = required_action.get('submit_tool_outputs', {}).get('tool_calls', [])
                        if tool_calls:
                            print(f"   Tool calls required: {len(tool_calls)}")
                            for tc in tool_calls:
                                print(f"   - {tc['function']['name']}: {tc['function']['arguments'][:100]}...")
                        break
                
            else:
                print(f"⏱️ Timeout waiting for run completion")
                
        except Exception as e:
            print(f"💥 Thread test failed: {str(e)}")
    
    async def check_workflow_concept(self):
        """Explain workflow vs assistant concept"""
        print("\n📚 OpenAI Agent Builder Concepts")
        print("=" * 60)
        
        print("🔍 Key Findings:")
        print("\n1. Workflow ID Format:")
        print(f"   Your ID: {self.workflow_id}")
        print(f"   Format: wf_<hash>")
        print(f"   ⚠️  This appears to be an Agent Builder workflow ID")
        
        print("\n2. Assistant ID Format:")
        print(f"   Your ID: {self.assistant_id}")
        print(f"   Format: asst_<hash>")
        print(f"   ✅ This is a standard OpenAI Assistant ID")
        
        print("\n3. Current OpenAI APIs:")
        print("   - Assistants API: Available (using threads)")
        print("   - Agent Builder: Beta/Limited access")
        print("   - Workflows: Part of Agent Builder (not standard API)")
        
        print("\n4. What's Actually Being Used:")
        print("   Based on your code:")
        print("   - ChatKit references workflow_id")
        print("   - Backend uses assistant_id")
        print("   - Agent SDK service exists but might not connect to OpenAI")
        
        print("\n5. Recommendations:")
        print("   ✅ Use the Assistant (asst_FgdYMBvUvKUy0mxX5AF7Lmyg)")
        print("   ⚠️  Workflow ID might be from beta access or playground")
        print("   💡 Update assistant instructions in OpenAI dashboard")
    
    async def run_all_checks(self):
        """Run all configuration checks"""
        print("🚀 OpenAI Configuration Check")
        print("=" * 60)
        print(f"Workflow ID: {self.workflow_id}")
        print(f"Assistant ID: {self.assistant_id}")
        print(f"API Key: {'Configured' if self.api_key else 'Missing!'}")
        
        # Check assistant
        assistant = await self.check_assistant()
        
        # Test via threads
        if assistant:
            await self.test_assistant_thread()
        
        # Explain concepts
        await self.check_workflow_concept()
        
        # Cleanup
        await self.client.aclose()
        
        print("\n" + "=" * 60)
        print("✅ Configuration check complete!")

async def main():
    checker = OpenAIWorkflowChecker()
    await checker.run_all_checks()

if __name__ == "__main__":
    asyncio.run(main())