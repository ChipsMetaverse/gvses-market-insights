#!/usr/bin/env python3
"""Simple test of agent's handling of technical analysis queries."""

import requests
import json

def test_api_queries():
    """Test queries through the API."""
    
    test_queries = [
        ("Give me entry points for swing trades on AAPL tomorrow", "swing_entry"),
        ("What are the key support and resistance levels for AAPL?", "support_resistance"),
        ("AAPL", "simple_ticker"),
        ("Analyze AAPL for swing trading opportunities", "swing_analysis")
    ]
    
    print("=" * 60)
    print("TESTING AGENT RESPONSES FOR TECHNICAL ANALYSIS")
    print("=" * 60)
    
    for query, test_type in test_queries:
        print(f"\n[{test_type}] Query: '{query}'")
        print("-" * 40)
        
        try:
            response = requests.post(
                "http://localhost:8000/ask",
                json={
                    "query": query,
                    "session_id": f"test_{test_type}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data.get('response', data.get('text', ''))
                tools = data.get('tools_used', [])
                
                print(f"Tools Used: {tools}")
                print(f"Response Length: {len(text)} chars")
                
                # Check for templated keywords
                templated_keywords = [
                    "real-time", "snapshot", "Market Snapshot", 
                    "Key Headlines", "Technical Overview", "Broader Trends"
                ]
                
                found_templates = [k for k in templated_keywords if k in text]
                if found_templates:
                    print(f"⚠️  Template Keywords Found: {found_templates}")
                else:
                    print(f"✅ No Template Keywords")
                
                # Check if response addresses technical analysis
                ta_keywords = [
                    "entry", "exit", "swing", "support", "resistance", 
                    "buy", "sell", "target", "stop", "level", "position",
                    "breakout", "pullback", "trend", "momentum"
                ]
                
                found_ta = [k for k in ta_keywords if k.lower() in text.lower()]
                if found_ta:
                    print(f"✅ Technical Terms Found: {found_ta[:5]}")  # First 5 to keep it concise
                else:
                    print(f"❌ No Technical Analysis Terms")
                
                # Show response preview
                print(f"\nResponse Preview (first 400 chars):")
                preview = text[:400] + "..." if len(text) > 400 else text
                print(preview)
                
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                print(response.text[:200])
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\n🚀 Starting Technical Analysis Response Test\n")
    test_api_queries()
    
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print("""
The agent appears to be returning templated stock snapshots instead of 
specific technical analysis. This indicates:

1. The system prompt needs enhancement for technical analysis
2. The agent may need specialized tools for swing trade analysis
3. The knowledge base retrieval might not be working for TA queries
""")