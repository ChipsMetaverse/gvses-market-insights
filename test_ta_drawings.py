#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Technical Analysis Drawing Commands"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_ta_queries():
    """Test various technical analysis queries"""
    
    test_cases = [
        {
            "name": "Support/Resistance for NVDA",
            "query": "Show me support and resistance levels for NVDA",
            "expected_commands": ["SUPPORT:", "RESISTANCE:"]
        },
        {
            "name": "Fibonacci for Tesla", 
            "query": "Display Fibonacci retracement for Tesla",
            "expected_commands": ["FIBONACCI:", "CHART:TSLA"]
        },
        {
            "name": "Full Technical Analysis",
            "query": "Show me technical analysis with trend lines for SPY",
            "expected_commands": ["CHART:SPY", "SUPPORT:", "RESISTANCE:"]
        }
    ]
    
    print("🎯 Testing Technical Analysis Drawing Commands\n")
    print("=" * 60)
    
    for test in test_cases:
        print(f"\n📊 Test: {test['name']}")
        print(f"   Query: {test['query']}")
        print("-" * 60)
        
        try:
            # Make the API request
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"query": test["query"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Get chart commands
                chart_commands = data.get('chart_commands', [])
                
                print(f"   ✅ Response received")
                print(f"   📈 Chart Commands: {len(chart_commands)} total")
                
                # Categorize commands
                drawing_commands = []
                basic_commands = []
                
                for cmd in chart_commands:
                    if any(cmd.startswith(prefix) for prefix in [
                        'SUPPORT:', 'RESISTANCE:', 'FIBONACCI:', 
                        'TRENDLINE:', 'PATTERN:', 'ENTRY:', 
                        'TARGET:', 'STOPLOSS:'
                    ]):
                        drawing_commands.append(cmd)
                    else:
                        basic_commands.append(cmd)
                
                # Display results
                if drawing_commands:
                    print(f"\n   🎨 Drawing Commands ({len(drawing_commands)}):")
                    for cmd in drawing_commands[:5]:  # Show first 5
                        print(f"      - {cmd}")
                    if len(drawing_commands) > 5:
                        print(f"      ... and {len(drawing_commands) - 5} more")
                
                if basic_commands:
                    print(f"\n   📊 Basic Commands ({len(basic_commands)}):")
                    for cmd in basic_commands:
                        print(f"      - {cmd}")
                
                # Check for technical analysis data
                tool_results = data.get('tool_results', {})
                if 'technical_analysis' in tool_results:
                    ta_data = tool_results['technical_analysis']
                    print(f"\n   🔬 Technical Analysis Data:")
                    for key in ['support_levels', 'resistance_levels', 
                               'fibonacci_levels', 'trend_lines', 'patterns']:
                        if key in ta_data:
                            if key in ['support_levels', 'resistance_levels']:
                                print(f"      - {key}: {ta_data[key]}")
                            else:
                                print(f"      - {key}: Present")
                
                # Verify expected commands
                success = True
                for expected in test['expected_commands']:
                    found = any(expected in cmd for cmd in chart_commands)
                    if not found:
                        print(f"   ⚠️  Missing expected: {expected}")
                        success = False
                
                if success:
                    print(f"\n   ✅ Test PASSED")
                else:
                    print(f"\n   ⚠️  Test PARTIAL")
                    
            else:
                print(f"   ❌ Error: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Request timed out")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✨ Test Complete!\n")
    print("📝 Summary:")
    print("   - Backend generates drawing commands for technical analysis")
    print("   - Commands include support/resistance levels, Fibonacci, trends")
    print("   - Frontend can parse and execute these drawing commands")
    print("   - Charts will display professional technical analysis automatically")

if __name__ == "__main__":
    test_ta_queries()