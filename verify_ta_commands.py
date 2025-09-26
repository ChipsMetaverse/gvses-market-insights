#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple verification that Technical Analysis drawing commands are working.
Tests the API directly to confirm drawing commands are being generated.
"""

import requests
import json
import time

def verify_drawing_commands():
    """Verify that the API generates drawing commands for technical analysis queries"""
    
    print("🔬 Verifying Technical Analysis Drawing Commands")
    print("="*60)
    
    test_cases = [
        {
            "name": "NVDA Support/Resistance",
            "query": "Show NVDA with support and resistance levels",
            "expected": ["CHART:NVDA", "SUPPORT:", "RESISTANCE:"]
        },
        {
            "name": "TSLA Fibonacci", 
            "query": "Display Fibonacci retracement for Tesla",
            "expected": ["CHART:TSLA", "FIBONACCI:"]
        },
        {
            "name": "SPY Trend Lines",
            "query": "Show technical analysis with trend lines for SPY",
            "expected": ["CHART:SPY", "TRENDLINE:", "SUPPORT:"]
        }
    ]
    
    all_passed = True
    
    for test in test_cases:
        print(f"\n📊 Test: {test['name']}")
        print(f"   Query: '{test['query']}'")
        print("   " + "-"*50)
        
        try:
            # Make API request with longer timeout
            print("   ⏳ Calling API (may take 20-30 seconds)...")
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/ask",
                json={"query": test["query"]},
                timeout=60  # 60 second timeout
            )
            
            elapsed = time.time() - start_time
            print(f"   ⏱️  Response in {elapsed:.1f} seconds")
            
            if response.status_code == 200:
                data = response.json()
                chart_commands = data.get('chart_commands', [])
                
                print(f"\n   📈 Generated {len(chart_commands)} drawing commands:")
                
                # Show all commands
                for cmd in chart_commands:
                    # Identify command type
                    cmd_type = cmd.split(':')[0]
                    if cmd_type in ['SUPPORT', 'RESISTANCE', 'FIBONACCI', 'TRENDLINE', 'ENTRY', 'TARGET', 'STOPLOSS']:
                        print(f"      🎨 {cmd}")
                    else:
                        print(f"      📊 {cmd}")
                
                # Verify expected commands
                print(f"\n   ✔️  Verification:")
                test_passed = True
                for expected in test['expected']:
                    found = any(expected in cmd for cmd in chart_commands)
                    if found:
                        print(f"      ✅ Found: {expected}")
                    else:
                        print(f"      ❌ Missing: {expected}")
                        test_passed = False
                
                if test_passed:
                    print(f"\n   🎉 {test['name']} PASSED")
                else:
                    print(f"\n   ⚠️  {test['name']} FAILED")
                    all_passed = False
                    
                # Show some technical analysis data if available
                if 'tool_results' in data and 'technical_analysis' in data['tool_results']:
                    ta_data = data['tool_results']['technical_analysis']
                    print(f"\n   🔬 Technical Analysis Data:")
                    if 'support_levels' in ta_data:
                        print(f"      Support: {ta_data['support_levels']}")
                    if 'resistance_levels' in ta_data:
                        print(f"      Resistance: {ta_data['resistance_levels']}")
                    if 'fibonacci_levels' in ta_data:
                        print(f"      Fibonacci: Present")
                    if 'trend_lines' in ta_data:
                        print(f"      Trend Lines: {len(ta_data['trend_lines'])} found")
                        
            else:
                print(f"   ❌ API Error: HTTP {response.status_code}")
                print(f"      {response.text[:200]}")
                all_passed = False
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Request timed out (> 60 seconds)")
            all_passed = False
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("\nThe Technical Analysis Drawing Feature is working correctly:")
        print("- Backend generates drawing commands from market data")
        print("- Support/Resistance levels are calculated")
        print("- Fibonacci retracements are computed")
        print("- Trend lines are generated")
        print("- Commands are formatted for frontend execution")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease check:")
        print("- Backend server is running on port 8000")
        print("- MCP servers are initialized")
        print("- Market data is available for symbols")
    
    print("\n📝 Next Steps:")
    print("1. Open http://localhost:5174 in your browser")
    print("2. Find the text input in the right panel")
    print("3. Type: 'Show NVDA with support and resistance'")
    print("4. Watch the chart update with drawing overlays")

if __name__ == "__main__":
    verify_drawing_commands()