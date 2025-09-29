#!/usr/bin/env python3
"""
Test Enhanced Chart Command Extraction
Tests that Voice Assistant responses now generate chart commands.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def test_chart_command_extraction():
    """Test that technical analysis queries generate chart commands."""
    
    print("=" * 70)
    print("🔬 TESTING ENHANCED CHART COMMAND EXTRACTION")
    print("=" * 70)
    
    # Test queries that should generate chart commands
    test_queries = [
        {
            "name": "Support/Resistance",
            "query": "Show support and resistance levels for TSLA",
            "expected_commands": ["SUPPORT", "RESISTANCE"]
        },
        {
            "name": "Fibonacci",
            "query": "Draw Fibonacci retracement on TSLA",
            "expected_commands": ["FIBONACCI"]
        },
        {
            "name": "Indicators",
            "query": "Add RSI and MACD indicators to TSLA chart",
            "expected_commands": ["INDICATOR:RSI", "INDICATOR:MACD"]
        },
        {
            "name": "Trade Setup",
            "query": "Mark entry at 440, stop loss at 430, and target at 460 on TSLA",
            "expected_commands": ["ENTRY", "STOP", "TARGET"]
        },
        {
            "name": "Technical Analysis",
            "query": "Do technical analysis on TSLA and show key levels",
            "expected_commands": ["SUPPORT", "RESISTANCE"]
        }
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    async with aiohttp.ClientSession() as session:
        for test in test_queries:
            print(f"\n📝 Testing: {test['name']}")
            print(f"   Query: {test['query']}")
            
            try:
                # Send query to agent orchestrator
                async with session.post(
                    "http://localhost:8000/api/agent/orchestrate",
                    json={"query": test['query']},
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check if chart_commands were generated
                        chart_commands = data.get("chart_commands", [])
                        
                        if chart_commands:
                            print(f"   ✅ Generated {len(chart_commands)} commands:")
                            for cmd in chart_commands:
                                print(f"      • {cmd}")
                            
                            # Check if expected commands are present
                            commands_str = " ".join(chart_commands)
                            found_expected = []
                            for expected in test['expected_commands']:
                                if expected in commands_str:
                                    found_expected.append(expected)
                            
                            if found_expected:
                                print(f"   ✅ Found expected commands: {', '.join(found_expected)}")
                            else:
                                print(f"   ⚠️ Expected commands not found")
                        else:
                            print(f"   ❌ No chart commands generated")
                        
                        # Extract some data from response
                        response_text = data.get("text", "")
                        if "$" in response_text:
                            # Response contains price levels
                            import re
                            prices = re.findall(r'\$?([\d,]+\.?\d*)', response_text)
                            if prices:
                                print(f"   📊 Found {len(prices)} price levels in response")
                        
                        results["tests"].append({
                            "test": test['name'],
                            "query": test['query'],
                            "chart_commands": chart_commands,
                            "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                            "success": len(chart_commands) > 0
                        })
                    else:
                        print(f"   ❌ HTTP {response.status}: {await response.text()}")
                        results["tests"].append({
                            "test": test['name'],
                            "query": test['query'],
                            "error": f"HTTP {response.status}",
                            "success": False
                        })
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results["tests"].append({
                    "test": test['name'],
                    "query": test['query'],
                    "error": str(e),
                    "success": False
                })
            
            # Brief delay between requests
            await asyncio.sleep(2)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    successful_tests = sum(1 for test in results["tests"] if test.get("success", False))
    total_tests = len(results["tests"])
    
    print(f"✅ Successful: {successful_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - successful_tests}/{total_tests}")
    
    # Save results
    results_file = f"enhanced_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Results saved to: {results_file}")
    
    return successful_tests == total_tests


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Chart Command Extraction Test")
    success = asyncio.run(test_chart_command_extraction())
    exit(0 if success else 1)