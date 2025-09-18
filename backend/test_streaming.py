#!/usr/bin/env python3
"""
Test the new TRUE streaming implementation with progressive tool execution.
Phase 1 of OpenAI response format migration.
"""

import asyncio
import json
import time
from services.agent_orchestrator import get_orchestrator

async def test_streaming():
    """Test the new streaming functionality."""
    orchestrator = get_orchestrator()
    
    print("=" * 70)
    print("TESTING TRUE STREAMING WITH PROGRESSIVE TOOL EXECUTION")
    print("=" * 70)
    
    test_queries = [
        "What's the current price of AAPL?",
        "Give me a complete analysis of TSLA with news and technical levels",
        "Good morning"  # Test morning greeting trigger
    ]
    
    for query in test_queries:
        print(f"\n[QUERY]: {query}")
        print("-" * 50)
        
        start_time = time.time()
        chunks_received = []
        tool_starts = []
        tool_results = []
        content_chunks = []
        
        try:
            async for chunk in orchestrator.stream_query(query):
                chunk_type = chunk.get("type")
                
                if chunk_type == "content":
                    # Content is streaming
                    content_chunks.append(chunk.get("text", ""))
                    print(chunk.get("text", ""), end="", flush=True)
                    
                elif chunk_type == "tool_start":
                    # Tool execution started
                    tool_name = chunk.get("tool")
                    tool_starts.append(tool_name)
                    print(f"\n🔧 [TOOL START]: {tool_name}")
                    
                elif chunk_type == "tool_result":
                    # Tool completed
                    tool_name = chunk.get("tool")
                    tool_results.append(tool_name)
                    data = chunk.get("data", {})
                    
                    if "error" in data:
                        print(f"\n❌ [TOOL ERROR]: {tool_name} - {data['error']}")
                    else:
                        print(f"\n✅ [TOOL COMPLETE]: {tool_name}")
                        # Show sample of data
                        if isinstance(data, dict):
                            sample_keys = list(data.keys())[:3]
                            print(f"   Data keys: {sample_keys}")
                
                elif chunk_type == "error":
                    print(f"\n⚠️ [ERROR]: {chunk.get('message')}")
                
                elif chunk_type == "done":
                    print("\n\n✨ [STREAM COMPLETE]")
                
                chunks_received.append(chunk)
        
        except Exception as e:
            print(f"\n❌ [EXCEPTION]: {e}")
        
        elapsed = time.time() - start_time
        
        # Summary
        print(f"\n[SUMMARY]")
        print(f"  Total time: {elapsed:.2f}s")
        print(f"  Chunks received: {len(chunks_received)}")
        print(f"  Tools started: {tool_starts}")
        print(f"  Tools completed: {tool_results}")
        print(f"  Content length: {len(''.join(content_chunks))} chars")
        
        # Verify progressive execution
        if tool_starts:
            print(f"\n[PROGRESSIVE EXECUTION CHECK]")
            print(f"  ✅ Tools executed: {len(tool_starts) > 0}")
            print(f"  ✅ Progressive updates: {len(chunks_received) > len(tool_starts) + len(tool_results)}")

async def test_streaming_performance():
    """Compare old vs new streaming performance."""
    orchestrator = get_orchestrator()
    
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON: OLD VS NEW STREAMING")
    print("=" * 70)
    
    query = "Analyze NVDA stock with all available data"
    
    # Test new streaming (time to first byte)
    print("\n[NEW STREAMING - Time to First Byte]")
    start = time.time()
    first_content = None
    
    async for chunk in orchestrator.stream_query(query):
        if chunk.get("type") == "content" and not first_content:
            first_content = time.time() - start
            print(f"  First content received: {first_content:.3f}s")
        
        if chunk.get("type") == "tool_start":
            print(f"  Tool started at: {time.time() - start:.3f}s - {chunk.get('tool')}")
        
        if chunk.get("type") == "done":
            total_time = time.time() - start
            print(f"  Total streaming time: {total_time:.3f}s")
            break
    
    # Compare with old approach (full response then stream)
    print("\n[OLD APPROACH - Full Response First]")
    start = time.time()
    
    # Simulate old approach - get full response
    response = await orchestrator.process_query(query)
    response_time = time.time() - start
    print(f"  Full response generated: {response_time:.3f}s")
    
    # Then simulate streaming
    words = response["text"].split()[:10]  # Just first 10 words for comparison
    for word in words:
        await asyncio.sleep(0.05)
    
    stream_time = time.time() - start
    print(f"  Simulated streaming complete: {stream_time:.3f}s")
    
    # Performance improvement
    if first_content and response_time:
        improvement = (response_time - first_content) / response_time * 100
        print(f"\n🚀 [PERFORMANCE GAIN]")
        print(f"  Time to first byte improved by: {improvement:.1f}%")
        print(f"  Old approach: {response_time:.3f}s to first content")
        print(f"  New approach: {first_content:.3f}s to first content")

if __name__ == "__main__":
    print("Testing New TRUE Streaming Implementation")
    print("=" * 70)
    
    # Run tests
    asyncio.run(test_streaming())
    asyncio.run(test_streaming_performance())