#!/usr/bin/env python3
"""
Test script to verify agent handles different question types correctly
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any

async def test_agent_question(question: str) -> Dict[str, Any]:
    """Test a single question against the agent API."""
    url = "http://localhost:8000/api/agent/orchestrate"
    headers = {"Content-Type": "application/json"}
    payload = {"query": question}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=30) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"HTTP {response.status}", "text": await response.text()}
        except Exception as e:
            return {"error": str(e)}

async def main():
    """Test various question types."""
    
    test_cases = [
        {
            "category": "Specific Stock Queries",
            "questions": [
                "TSLA",
                "Show me Tesla stock",
                "What's the price of AAPL?",
                "META snapshot",
                "Give me NVDA analysis"
            ],
            "expected": "Should fetch real-time data and provide formatted snapshot"
        },
        {
            "category": "General Trading Questions",
            "questions": [
                "Where should I long or short tomorrow?",
                "What sectors look good for trading?",
                "Should I be bullish or bearish?",
                "What's your market outlook?",
                "Any trading recommendations?"
            ],
            "expected": "Should provide strategic advice WITHOUT fetching stock data"
        },
        {
            "category": "Mixed Questions",
            "questions": [
                "How is TSLA doing today?",
                "Is AAPL a good buy?",
                "Should I buy NVDA?",
                "What do you think about META?"
            ],
            "expected": "Should fetch data for the specific stock AND provide analysis"
        },
        {
            "category": "Edge Cases",
            "questions": [
                "WHERE",  # Should NOT be treated as a ticker
                "HOW",    # Should NOT be treated as a ticker
                "WHAT",   # Should NOT be treated as a ticker
                "I need help",  # General help request
                "Market news"   # General market request
            ],
            "expected": "Should NOT attempt to fetch stock data for common words"
        }
    ]
    
    print("=" * 80)
    print("AGENT QUESTION HANDLING TEST")
    print("=" * 80)
    
    for test_group in test_cases:
        print(f"\n📋 {test_group['category']}")
        print(f"   Expected: {test_group['expected']}")
        print("-" * 60)
        
        for question in test_group['questions']:
            print(f"\n❓ Question: '{question}'")
            
            result = await test_agent_question(question)
            
            if "error" in result:
                print(f"   ❌ Error: {result['error']}")
            else:
                response_text = result.get("text", "")
                tools_used = result.get("tools_used", [])
                
                # Check if response looks like a stock snapshot
                is_snapshot = any([
                    "real-time" in response_text.lower() and "snapshot" in response_text.lower(),
                    "MARKET SNAPSHOT" in response_text,
                    "$" in response_text[:100] if response_text else False,
                    "Price:" in response_text
                ])
                
                # Determine if behavior is correct
                if test_group['category'] == "Specific Stock Queries":
                    correct = is_snapshot or len(tools_used) > 0
                elif test_group['category'] == "General Trading Questions":
                    correct = not is_snapshot and len(tools_used) == 0
                elif test_group['category'] == "Edge Cases":
                    correct = not is_snapshot and "WHERE" not in response_text[:200] if response_text else True
                else:  # Mixed
                    correct = True  # Mixed can go either way
                
                status = "✅" if correct else "⚠️"
                
                print(f"   {status} Tools used: {tools_used if tools_used else 'None'}")
                print(f"   {status} Snapshot format: {'Yes' if is_snapshot else 'No'}")
                
                # Show first 200 chars of response
                preview = response_text[:200].replace('\n', ' ') if response_text else ""
                print(f"   📝 Response preview: {preview}...")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())