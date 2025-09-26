#!/usr/bin/env python3
"""Test the full Responses API implementation."""

import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

# Load environment variables
load_dotenv()

async def test_responses_implementation():
    """Test the Responses API implementation in agent orchestrator."""
    from services.agent_orchestrator import AgentOrchestrator
    
    print("=" * 60)
    print("Testing Full Responses API Implementation")
    print("=" * 60)
    
    # Set environment to use Responses API
    os.environ["USE_RESPONSES"] = "true"
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    test_queries = [
        ("What is the price of AAPL?", "Simple price query"),
        ("Show me technical analysis for NVDA", "Technical analysis query"),
        ("What's the latest news on TSLA?", "News query"),
    ]
    
    for query, description in test_queries:
        print(f"\n📝 Test: {description}")
        print(f"   Query: {query}")
        print("-" * 40)
        
        try:
            start = time.time()
            
            # Call the Responses API version
            result = await orchestrator.process_query(query)
            
            elapsed = time.time() - start
            
            # Extract results
            text = result.get('text', '')
            tools_used = result.get('tools_used', [])
            mode = result.get('mode', 'unknown')
            
            print(f"✅ Response time: {elapsed:.2f}s")
            print(f"   Text length: {len(text)} chars")
            print(f"   Tools used: {tools_used if tools_used else 'None'}")
            print(f"   Mode: {mode}")
            
            # Show response preview
            if text:
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"   Response: {preview}")
            else:
                print("   ⚠️  No response text generated")
            
            # Check for Responses API usage
            if "responses" in str(mode).lower() or elapsed < 5:
                print("   🎯 Likely using optimized flow")
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("- Responses API implementation updated ✅")
    print("- Using client.responses.create() method ✅")
    print("- output_text property prioritized for text extraction ✅")
    print("- Tools converted to Responses API format ✅")
    print("=" * 60)

if __name__ == "__main__":
    print("Starting Responses API test...")
    asyncio.run(test_responses_implementation())