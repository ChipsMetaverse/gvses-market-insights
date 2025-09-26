#!/usr/bin/env python3
"""Test script to verify Responses API fix with output_text property."""

import asyncio
import os
import sys
import time
from dotenv import load_dotenv

# Add backend to path
sys.path.insert(0, '/Volumes/WD My Passport 264F Media/claude-voice-mcp/backend')

# Load environment variables
load_dotenv()

async def test_responses_api():
    """Test the Responses API with the fixed text extraction."""
    from services.agent_orchestrator import AgentOrchestrator
    
    print("=" * 60)
    print("Testing Responses API Fix")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Test queries that previously caused issues with reasoning-only responses
    test_queries = [
        "What is the price of AAPL?",
        "Show me technical analysis for NVDA",
        "What's the latest news on TSLA?",
        "Analyze the market trend for SPY"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        try:
            start = time.time()
            result = await orchestrator.process_query(query)
            elapsed = time.time() - start
            
            # Extract text from result
            text = result.get('text', '')
            
            print(f"Response time: {elapsed:.2f}s")
            print(f"Response length: {len(text)} chars")
            print(f"Has chart commands: {bool(result.get('chart_commands'))}")
            
            # Show first 200 chars of response
            if text:
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"Response preview: {preview}")
            else:
                print("WARNING: No text in response!")
                
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("Check logs for 'SDK output_text property' to verify fix is working")
    print("=" * 60)

if __name__ == "__main__":
    print("Starting Responses API test...")
    asyncio.run(test_responses_api())