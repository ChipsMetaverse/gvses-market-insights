#!/usr/bin/env python3
"""Test agent's handling of technical analysis queries with detailed logging."""

import requests
import json
import logging
import asyncio
import sys
import os

# Set up detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from services.agent_orchestrator import get_orchestrator

async def test_direct_orchestrator():
    """Test the orchestrator directly to see what it's doing."""
    
    orchestrator = get_orchestrator()
    
    test_queries = [
        "Give me entry points for swing trades on AAPL tomorrow",
        "What are the key support and resistance levels for AAPL for swing trading?",
        "Analyze AAPL for swing trade opportunities"
    ]
    
    print("=" * 60)
    print("TESTING ORCHESTRATOR DIRECTLY")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n📊 Query: '{query}'")
        print("-" * 40)
        
        try:
            # Process the query
            result = await orchestrator.process_query(
                query=query,
                conversation_history=None,
                stream=False
            )
            
            # Log the tools used
            tools_used = result.get('tools_used', [])
            print(f"🔧 Tools Used: {tools_used}")
            
            # Check the response
            text = result.get('text', '')
            print(f"📝 Response Length: {len(text)} chars")
            
            # Check for templated keywords
            templated_keywords = [
                "real-time", "snapshot", "Market Snapshot", 
                "Key Headlines", "Technical Overview", "Broader Trends"
            ]
            
            found_templates = [k for k in templated_keywords if k in text]
            if found_templates:
                print(f"⚠️  Found Template Keywords: {found_templates}")
            else:
                print("✅ No Template Keywords Found")
            
            # Check if response addresses technical analysis
            ta_keywords = [
                "entry", "exit", "swing", "support", "resistance", 
                "buy", "sell", "target", "stop", "level"
            ]
            
            found_ta = [k for k in ta_keywords if k.lower() in text.lower()]
            if found_ta:
                print(f"✅ Found Technical Analysis Terms: {found_ta}")
            else:
                print("❌ No Technical Analysis Terms Found")
            
            # Show first 500 chars of response
            print("\n📄 Response Preview:")
            print(text[:500] + "..." if len(text) > 500 else text)
            
            # Check data returned
            data = result.get('data', {})
            if data:
                print(f"\n📊 Data Keys: {list(data.keys())}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

def test_api_endpoint():
    """Test via API endpoint to see the full flow."""
    
    print("\n" + "=" * 60)
    print("TESTING VIA API ENDPOINT")
    print("=" * 60)
    
    test_queries = [
        "Give me entry points for swing trades on AAPL tomorrow",
        "AAPL",  # Compare with simple ticker query
    ]
    
    for query in test_queries:
        print(f"\n📊 Query: '{query}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={
                    "query": query,
                    "session_id": f"test_{query[:10]}"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get('response', data.get('text', ''))
                tools = data.get('tools_used', [])
                
                print(f"🔧 Tools Used: {tools}")
                print(f"📝 Response Length: {len(text)} chars")
                
                # Show response
                print(f"\n📄 Response Preview:")
                print(text[:500] + "..." if len(text) > 500 else text)
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting Agent Technical Analysis Test\n")
    
    # Test direct orchestrator
    asyncio.run(test_direct_orchestrator())
    
    # Test API endpoint
    test_api_endpoint()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n💡 Key Findings:")
    print("1. Check if the agent is using get_comprehensive_stock_data for all queries")
    print("2. Verify if the system prompt needs enhancement for technical analysis")
    print("3. Consider if additional tools are needed for swing trade analysis")
    print("4. Check if knowledge base retrieval is working for technical patterns")