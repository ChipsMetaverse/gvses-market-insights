#!/usr/bin/env python3

import asyncio
import json
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.agent_orchestrator import AgentOrchestrator

async def test_swing_trade_analysis():
    """Test swing trade analysis queries"""
    
    print("=" * 60)
    print("Testing Swing Trade Analysis")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Test queries
    test_queries = [
        ("AAPL", "Give me entry points for swing trades on AAPL tomorrow"),
        ("NVDA", "What are the best support and resistance levels for NVDA swing trading?"),
        ("TSLA", "Provide swing trade setup for TSLA with entry, target, and stop loss")
    ]
    
    for symbol, query in test_queries:
        print(f"\n\nTesting: {symbol}")
        print(f"Query: {query}")
        print("-" * 40)
        
        try:
            # Get response
            response = await orchestrator.process_query(query)
            
            # Print response
            print(f"Response Type: {type(response)}")
            
            if isinstance(response, dict):
                # Pretty print the response
                print("\nFull Response:")
                print(json.dumps(response, indent=2))
                
                # Check for text field
                if 'text' in response:
                    print(f"\nText Response Length: {len(response['text'])}")
                    print(f"\nText Response (first 500 chars):\n{response['text'][:500]}")
                    
                    # Check for swing trade JSON
                    if 'swing_trade' in response['text']:
                        print("\n✓ Found 'swing_trade' in response")
                    else:
                        print("\n✗ No 'swing_trade' found in response")
                    
                    # Try to extract JSON
                    import re
                    json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', response['text'])
                    if json_match:
                        try:
                            swing_data = json.loads(json_match.group(1))
                            print("\n✓ Successfully extracted swing trade JSON:")
                            print(json.dumps(swing_data, indent=2))
                        except json.JSONDecodeError as e:
                            print(f"\n✗ Failed to parse JSON: {e}")
                    else:
                        print("\n✗ No JSON structure found in response")
                    
                    # Check for technical keywords
                    keywords = ['entry', 'target', 'stop', 'support', 'resistance', 'swing']
                    found_keywords = [kw for kw in keywords if kw.lower() in response['text'].lower()]
                    if found_keywords:
                        print(f"\n✓ Found technical keywords: {found_keywords}")
                    else:
                        print("\n✗ No technical keywords found")
                        
                    # Check if it's a templated response
                    if 'Market Snapshot' in response['text']:
                        print("\n⚠️ WARNING: Response appears to be templated!")
                    
            else:
                print(f"Response: {response}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        
        # Small delay between tests
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(test_swing_trade_analysis())
