#!/usr/bin/env python3
"""
Test educational query support for novice traders
"""

import asyncio
import aiohttp
import json

async def test_educational_queries():
    """Test that educational queries now work"""
    print("🎓 Testing Educational Query Support\n")
    print("=" * 60)
    
    # Test queries that previously failed
    test_queries = [
        "What does buy low mean?",
        "Show me the chart for Apple",
        "What is the difference between support and resistance levels?",
        "How do I start trading stocks?",
        "What is a stop loss?",
        "Is TSLA a good buy right now?"  # This one was working, keeping for comparison
    ]
    
    base_url = "http://localhost:8000"
    
    # Wait for backend to be ready
    await asyncio.sleep(3)
    
    async with aiohttp.ClientSession() as session:
        print("Testing educational queries:\n")
        
        for query in test_queries:
            print(f"📚 Query: '{query}'")
            print("-" * 50)
            
            try:
                # Send query to backend
                async with session.post(
                    f"{base_url}/ask",
                    json={"query": query},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Debug: show raw result structure
                        print(f"   Raw response keys: {list(result.keys())}")
                        
                        # Extract key information
                        response_text = result.get("text", result.get("response", "No response text"))
                        tools_used = result.get("tools_used", [])
                        chart_commands = result.get("chart_commands", [])
                        data_type = result.get("structured_data", {}).get("type", "unknown")
                        
                        # Display results
                        print(f"✅ Status: Success")
                        print(f"   Type: {data_type}")
                        print(f"   Tools: {', '.join(tools_used) if tools_used else 'None'}")
                        
                        if chart_commands:
                            print(f"   Chart: {', '.join(chart_commands)}")
                        
                        # Show first 200 chars of response
                        response_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                        print(f"   Response: {response_preview}")
                        
                    else:
                        print(f"❌ Status: Failed (HTTP {response.status})")
                        error_text = await response.text()
                        print(f"   Error: {error_text[:100]}")
                        
            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                
            print()
    
    print("=" * 60)
    print("Educational query test complete!")
    print("\n💡 Summary:")
    print("- Educational queries should now provide helpful explanations")
    print("- 'Show me the chart for Apple' should load AAPL chart")
    print("- Basic trading concepts should be explained clearly")

if __name__ == "__main__":
    asyncio.run(test_educational_queries())