#!/usr/bin/env python3
"""
Latency test script for agent orchestrator improvements.
Measures response times for various query types and phases.
"""

import asyncio
import time
import json
import aiohttp
from typing import Dict, Any
import statistics

async def test_query(query: str, endpoint: str = "http://localhost:8000/api/agent/orchestrate") -> Dict[str, Any]:
    """Test a single query and return timing information."""
    start_time = time.monotonic()
    
    async with aiohttp.ClientSession() as session:
        payload = {"query": query}
        try:
            async with session.post(endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                response = await resp.json()
                end_time = time.monotonic()
                
                return {
                    "query": query,
                    "total_time": end_time - start_time,
                    "status": resp.status,
                    "has_text": bool(response.get("text")),
                    "has_commands": bool(response.get("chart_commands")),
                    "text_length": len(response.get("text", "")),
                    "num_commands": len(response.get("chart_commands", []))
                }
        except asyncio.TimeoutError:
            return {
                "query": query,
                "total_time": 60.0,
                "status": "timeout",
                "error": "Request timed out after 60 seconds"
            }
        except Exception as e:
            return {
                "query": query,
                "total_time": time.monotonic() - start_time,
                "status": "error",
                "error": str(e)
            }

async def run_test_suite():
    """Run a suite of tests to measure latency improvements."""
    
    test_queries = [
        # Simple price queries (should be fastest)
        ("Get AAPL price", "price_simple"),
        ("What is TSLA trading at?", "price_question"),
        
        # Analysis without news (should skip news tool)
        ("Show technical analysis for NVDA", "technical_no_news"),
        ("What are the support and resistance levels for SPY", "levels_no_news"),
        
        # News queries (should include news tool)
        ("What's the latest news on MSFT", "news_explicit"),
        ("Any breaking headlines for Tesla?", "news_breaking"),
        
        # Complex technical (should use all tools + TA)
        ("Show NVDA with support resistance fibonacci and trendline", "technical_complex"),
        
        # Chart-only (could potentially skip tools)
        ("Switch chart to GOOGL", "chart_only"),
    ]
    
    print("=" * 60)
    print("AGENT ORCHESTRATOR LATENCY TEST SUITE")
    print("=" * 60)
    print()
    
    # Warm-up query
    print("Running warm-up query...")
    await test_query("Hello")
    print()
    
    results = []
    categories = {}
    
    for query, category in test_queries:
        print(f"Testing: {query[:50]}...")
        result = await test_query(query)
        results.append(result)
        
        if category not in categories:
            categories[category] = []
        categories[category].append(result["total_time"])
        
        # Print immediate result
        if result["status"] == "error" or result["status"] == "timeout":
            print(f"  ❌ {result['status']}: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✅ {result['total_time']:.2f}s - {result['text_length']} chars")
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    # Overall statistics
    successful_times = [r["total_time"] for r in results if r.get("status") == 200]
    if successful_times:
        print(f"\nOverall Statistics:")
        print(f"  Average: {statistics.mean(successful_times):.2f}s")
        print(f"  Median: {statistics.median(successful_times):.2f}s")
        print(f"  Min: {min(successful_times):.2f}s")
        print(f"  Max: {max(successful_times):.2f}s")
    
    # Category breakdown
    print(f"\nBy Category:")
    for category, times in categories.items():
        if times:
            avg_time = statistics.mean(times)
            print(f"  {category:20s}: {avg_time:.2f}s avg")
    
    # Detailed results
    print(f"\nDetailed Results:")
    print(f"{'Query':<50} {'Time':>8} {'Status':>8} {'Text':>8} {'Cmds':>8}")
    print("-" * 90)
    for result in results:
        query_short = result["query"][:47] + "..." if len(result["query"]) > 50 else result["query"]
        status = "OK" if result.get("status") == 200 else str(result.get("status", "ERR"))
        time_str = f"{result['total_time']:.2f}s"
        text_str = str(result.get("text_length", 0)) if result.get("has_text") else "-"
        cmds_str = str(result.get("num_commands", 0)) if result.get("has_commands") else "-"
        
        print(f"{query_short:<50} {time_str:>8} {status:>8} {text_str:>8} {cmds_str:>8}")
    
    # Target comparison
    print(f"\n{'='*60}")
    print("TARGET COMPARISON")
    print("=" * 60)
    print("Expected targets after optimization:")
    print("  Price queries: 3-5s (actual: {:.2f}s)".format(
        statistics.mean([r["total_time"] for r in results[:2]]) if results[:2] else 0
    ))
    print("  Technical analysis: 6-9s (actual: {:.2f}s)".format(
        statistics.mean([r["total_time"] for r in results if "technical" in test_queries[results.index(r)][1]]) 
        if any("technical" in t[1] for t in test_queries) else 0
    ))
    print("  News queries: 5-7s (actual: {:.2f}s)".format(
        statistics.mean([r["total_time"] for r in results if "news" in test_queries[results.index(r)][1]])
        if any("news" in t[1] for t in test_queries) else 0
    ))

async def check_server_logs():
    """Check if server is logging timing information."""
    print("\nChecking for timing logs in server output...")
    print("Look for these log patterns in your server console:")
    print("  - LLM#1 (plan) latency: X.XXs")
    print("  - Executed N tools in parallel via Responses API in X.XXs")
    print("  - LLM#2 (final) latency: X.XXs")
    print("  - Skipping second LLM call: using preliminary text")
    print("  - Skipping get_stock_news (no news intent detected)")
    print("\nIf you don't see these, restart the server to pick up latest changes.")

if __name__ == "__main__":
    print("Starting latency test suite...")
    print("Make sure backend is running on http://localhost:8000")
    print()
    
    asyncio.run(run_test_suite())
    asyncio.run(check_server_logs())