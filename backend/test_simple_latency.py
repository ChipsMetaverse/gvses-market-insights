#!/usr/bin/env python3
"""Simple latency test to verify improvements are working."""

import asyncio
import time
import sys
import os

# Add backend to path
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

async def test_direct():
    """Test orchestrator directly."""
    from services.agent_orchestrator import AgentOrchestrator
    
    print("Testing AgentOrchestrator directly...")
    print("-" * 50)
    
    orchestrator = AgentOrchestrator()
    
    # Test 1: Simple price query
    print("\n1. Testing simple price query...")
    start = time.monotonic()
    result = await orchestrator.process_query("What is AAPL price?")
    elapsed = time.monotonic() - start
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Text length: {len(result.get('text', ''))}")
    print(f"   Has chart commands: {bool(result.get('chart_commands'))}")
    
    # Test 2: Analysis query (no news)
    print("\n2. Testing analysis query (should skip news)...")
    start = time.monotonic()
    result = await orchestrator.process_query("Show technical analysis for NVDA")
    elapsed = time.monotonic() - start
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Text length: {len(result.get('text', ''))}")
    print(f"   Chart commands: {len(result.get('chart_commands', []))}")
    
    # Test 3: News query (should include news)
    print("\n3. Testing news query...")
    start = time.monotonic()
    result = await orchestrator.process_query("What's the latest news on TSLA?")
    elapsed = time.monotonic() - start
    print(f"   Time: {elapsed:.2f}s")
    print(f"   Text length: {len(result.get('text', ''))}")
    
    print("\n" + "=" * 50)
    print("Check /tmp/backend_new.log for timing logs:")
    print("  grep 'LLM#1\\|parallel\\|Skipping' /tmp/backend_new.log | tail -20")

if __name__ == "__main__":
    print("Starting direct orchestrator test...")
    asyncio.run(test_direct())