#!/usr/bin/env python3

import asyncio
import json
import httpx

async def test_drawing_commands():
    """Test if technical analysis drawing commands are generated"""
    
    test_queries = [
        "Show me support and resistance levels for NVDA",
        "Display Tesla chart with Fibonacci retracement",
        "Show technical analysis for AAPL with trend lines",
        "Mark the key support levels on SPY chart",
    ]
    
    print("🎯 Testing Technical Analysis Drawing Commands\n")
    
    for query in test_queries:
        print(f"Query: {query}")
        print("-" * 50)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    "http://localhost:8000/ask",
                    json={"query": query}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for chart commands
                    chart_commands = data.get('chart_commands', [])
                    
                    print(f"✅ Response received")
                    print(f"Chart Commands: {len(chart_commands)} commands")
                    
                    # Display drawing commands
                    drawing_commands = [
                        cmd for cmd in chart_commands 
                        if any(cmd.startswith(prefix) for prefix in [
                            'SUPPORT:', 'RESISTANCE:', 'FIBONACCI:', 
                            'TRENDLINE:', 'PATTERN:', 'ENTRY:', 
                            'TARGET:', 'STOPLOSS:'
                        ])
                    ]
                    
                    if drawing_commands:
                        print(f"🎨 Drawing Commands Found:")
                        for cmd in drawing_commands:
                            print(f"  - {cmd}")
                    else:
                        print("⚠️ No drawing commands found")
                    
                    # Show basic commands too
                    basic_commands = [
                        cmd for cmd in chart_commands 
                        if cmd not in drawing_commands
                    ]
                    if basic_commands:
                        print(f"📊 Basic Commands:")
                        for cmd in basic_commands:
                            print(f"  - {cmd}")
                    
                    # Check if technical analysis data is in tool_results
                    tool_results = data.get('tool_results', {})
                    if 'technical_analysis' in tool_results:
                        ta_data = tool_results['technical_analysis']
                        print(f"🔬 Technical Analysis Data Found:")
                        if 'support_levels' in ta_data:
                            print(f"  - Support Levels: {ta_data['support_levels']}")
                        if 'resistance_levels' in ta_data:
                            print(f"  - Resistance Levels: {ta_data['resistance_levels']}")
                        if 'fibonacci_levels' in ta_data:
                            print(f"  - Fibonacci: High={ta_data['fibonacci_levels']['high']}, Low={ta_data['fibonacci_levels']['low']}")
                    
                else:
                    print(f"❌ Error: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
        
        print("\n")
    
    print("✨ Test Complete")

if __name__ == "__main__":
    asyncio.run(test_drawing_commands())