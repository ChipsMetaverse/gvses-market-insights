#!/usr/bin/env python3
"""
Test agent using the ElevenLabs simulate conversation API
This will show if tools are being called properly
"""

import requests
import json
import os
from dotenv import load_dotenv
import time

load_dotenv('backend/.env')

API_KEY = os.getenv('ELEVENLABS_API_KEY')
AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
BASE_URL = "https://api.elevenlabs.io/v1"

print("🧪 Testing Agent with Simulation API")
print("=" * 60)

# Test queries that should trigger specific tools
test_queries = [
    {
        "query": "What is the current price of Apple stock?",
        "expected_tool": "get_stock_price",
        "expected_param": "AAPL"
    },
    {
        "query": "Show me the market overview",
        "expected_tool": "get_market_overview",
        "expected_param": None
    },
    {
        "query": "Get news for Tesla",
        "expected_tool": "get_stock_news",
        "expected_param": "TSLA"
    },
    {
        "query": "What's Bitcoin trading at?",
        "expected_tool": "get_stock_price",
        "expected_param": "BTC-USD"
    }
]

def simulate_conversation(query: str):
    """Simulate a conversation with the agent"""
    
    # Prepare the simulation specification
    simulation_spec = {
        "simulated_user_config": {
            "prompt": f"You are a user interested in stock market information. Ask: {query}"
        }
    }
    
    # Send the simulation request
    response = requests.post(
        f"{BASE_URL}/convai/agents/{AGENT_ID}/simulate-conversation/stream",
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json"
        },
        json={"simulation_specification": simulation_spec},
        stream=True
    )
    
    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"   Error: {response.text[:200]}")
        return None
    
    # Process the streamed response
    conversation_data = {
        "messages": [],
        "tool_calls": [],
        "analysis": None
    }
    
    buffer = ""
    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
        if chunk:
            buffer += chunk
            
            # Process complete JSON objects from the buffer
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.strip():
                    try:
                        data = json.loads(line)
                        
                        # Check for different event types
                        if 'user_message' in data:
                            conversation_data['messages'].append({
                                "role": "user",
                                "text": data.get('user_message', '')
                            })
                        
                        elif 'agent_message' in data:
                            conversation_data['messages'].append({
                                "role": "agent",
                                "text": data.get('agent_message', '')
                            })
                        
                        elif 'tool_call' in data:
                            tool_call = data.get('tool_call', {})
                            conversation_data['tool_calls'].append({
                                "name": tool_call.get('tool_name'),
                                "parameters": tool_call.get('parameters', {}),
                                "result": tool_call.get('result')
                            })
                        
                        elif 'conversation_analysis' in data:
                            conversation_data['analysis'] = data.get('conversation_analysis')
                            
                    except json.JSONDecodeError:
                        continue
    
    return conversation_data

def analyze_results(query_info: dict, conversation_data: dict):
    """Analyze the simulation results"""
    
    print(f"\n📝 Query: '{query_info['query']}'")
    print("-" * 40)
    
    # Check if expected tool was called
    tool_called = False
    correct_tool = False
    correct_param = False
    
    if conversation_data and conversation_data['tool_calls']:
        tool_called = True
        
        for tool_call in conversation_data['tool_calls']:
            tool_name = tool_call.get('name', '')
            params = tool_call.get('parameters', {})
            
            print(f"   🔧 Tool called: {tool_name}")
            if params:
                print(f"      Parameters: {params}")
            
            # Check if it's the expected tool
            if tool_name == query_info['expected_tool']:
                correct_tool = True
                
                # Check parameters if applicable
                if query_info['expected_param']:
                    symbol = params.get('symbol', '')
                    if symbol == query_info['expected_param']:
                        correct_param = True
                else:
                    correct_param = True  # No param expected
            
            # Show tool result if available
            result = tool_call.get('result')
            if result:
                try:
                    result_data = json.loads(result) if isinstance(result, str) else result
                    if isinstance(result_data, dict):
                        if 'symbol' in result_data and 'last' in result_data:
                            print(f"      📊 Result: {result_data['symbol']} = ${result_data.get('last', 'N/A')}")
                        else:
                            print(f"      📊 Result received")
                except:
                    print(f"      📊 Result: {str(result)[:100]}")
    
    # Show agent response
    if conversation_data and conversation_data['messages']:
        for msg in conversation_data['messages']:
            if msg['role'] == 'agent':
                print(f"   💬 Agent: {msg['text'][:200]}...")
                break
    
    # Summary
    if not tool_called:
        print("   ❌ No tools were called")
    elif correct_tool and correct_param:
        print("   ✅ Correct tool called with correct parameters!")
    elif correct_tool:
        print("   ⚠️  Correct tool called but wrong parameters")
    else:
        print("   ⚠️  Wrong tool was called")
    
    return tool_called, correct_tool, correct_param

def main():
    """Run all test queries"""
    
    print(f"Agent ID: {AGENT_ID}")
    print(f"Testing {len(test_queries)} queries\n")
    
    results = {
        "total": len(test_queries),
        "tools_called": 0,
        "correct_tools": 0,
        "correct_params": 0
    }
    
    for query_info in test_queries:
        conversation_data = simulate_conversation(query_info['query'])
        
        if conversation_data:
            tool_called, correct_tool, correct_param = analyze_results(query_info, conversation_data)
            
            if tool_called:
                results['tools_called'] += 1
            if correct_tool:
                results['correct_tools'] += 1
            if correct_param:
                results['correct_params'] += 1
        else:
            print(f"\n❌ Simulation failed for: {query_info['query']}")
        
        # Small delay between tests
        time.sleep(2)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Total queries: {results['total']}")
    print(f"   Tools called: {results['tools_called']}/{results['total']}")
    print(f"   Correct tools: {results['correct_tools']}/{results['total']}")
    print(f"   Correct params: {results['correct_params']}/{results['total']}")
    
    if results['tools_called'] == results['total']:
        print("\n✅ SUCCESS: All queries triggered tool calls!")
        print("   The agent is now properly configured and calling tools.")
    elif results['tools_called'] > 0:
        print("\n⚠️  PARTIAL SUCCESS: Some queries triggered tool calls")
        print("   The agent may need prompt adjustments.")
    else:
        print("\n❌ FAILURE: No tools were called")
        print("   There may still be configuration issues.")

if __name__ == "__main__":
    main()