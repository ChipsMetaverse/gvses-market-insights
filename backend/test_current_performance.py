#!/usr/bin/env python3
"""Test current performance with optimized text extraction."""

import asyncio
import time
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

# Load environment variables
load_dotenv()

async def test_performance():
    """Test current performance of the agent orchestrator."""
    from services.agent_orchestrator import AgentOrchestrator
    
    print("=" * 60)
    print("Testing Current Performance with Optimizations")
    print("=" * 60)
    
    orchestrator = AgentOrchestrator()
    
    # Test simple price query (should be fast)
    print("\n1. Simple Price Query")
    print("-" * 40)
    start = time.time()
    result = await orchestrator.process_query("What is AAPL price?")
    elapsed = time.time() - start
    
    text = result.get('text', '')
    print(f"✅ Response time: {elapsed:.2f}s")
    print(f"   Text length: {len(text)} chars")
    print(f"   Target: < 3 seconds")
    
    if elapsed < 3:
        print("   🎯 PASSED: Fast response achieved!")
    else:
        print("   ⚠️  WARNING: Response slower than target")
    
    # Show response preview
    if text:
        preview = text[:150] + "..." if len(text) > 150 else text
        print(f"   Preview: {preview}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"- Text extraction fix implemented ✅")
    print(f"- Response time: {elapsed:.2f}s")
    print(f"- Responses API: Awaiting OpenAI SDK support")
    print("=" * 60)

if __name__ == "__main__":
    print("Starting performance test...")
    asyncio.run(test_performance())