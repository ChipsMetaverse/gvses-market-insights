#!/usr/bin/env python3
"""
Manual test script to verify chart command execution.
Tests the chart control infrastructure directly.
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def test_manual_chart_commands():
    """Manually test chart command execution through browser console."""
    
    print("=" * 70)
    print("🔧 MANUAL CHART COMMAND TEST")
    print("=" * 70)
    
    # Test commands to execute directly
    test_commands = [
        {
            "name": "Support Level",
            "command": "SUPPORT:440",
            "description": "Draw support line at $440"
        },
        {
            "name": "Resistance Level",
            "command": "RESISTANCE:460",
            "description": "Draw resistance line at $460"
        },
        {
            "name": "Fibonacci",
            "command": "FIBONACCI:430:470",
            "description": "Draw Fibonacci from $430 to $470"
        },
        {
            "name": "RSI Indicator",
            "command": "INDICATOR:RSI:ON",
            "description": "Add RSI indicator"
        },
        {
            "name": "MACD Indicator",
            "command": "INDICATOR:MACD:ON",
            "description": "Add MACD indicator"
        },
        {
            "name": "Entry/Stop/Target",
            "command": "ENTRY:445 STOP:435 TARGET:465",
            "description": "Mark entry, stop loss, and target"
        }
    ]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    async with async_playwright() as p:
        # Launch browser
        print("\n1️⃣ Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=200
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to app
        print("2️⃣ Opening trading app...")
        await page.goto("http://localhost:5174")
        await page.wait_for_timeout(5000)
        
        # Wait for chart to be ready
        print("3️⃣ Waiting for chart initialization...")
        try:
            # Wait for enhanced chart control to be ready
            await page.wait_for_function(
                """() => {
                    return window.enhancedChartControl && 
                           window.enhancedChartControlReady === true;
                }""",
                timeout=10000
            )
            print("   ✅ Chart control ready")
        except Exception as e:
            print(f"   ❌ Chart control not ready: {e}")
            await browser.close()
            return
        
        # Test each command
        print("\n4️⃣ Testing chart commands...")
        
        for i, test in enumerate(test_commands, 1):
            print(f"\n📝 Test {i}: {test['name']}")
            print(f"   Command: {test['command']}")
            print(f"   Description: {test['description']}")
            
            try:
                # Execute command through browser console
                result = await page.evaluate(f"""
                    async () => {{
                        try {{
                            // Check if enhancedChartControl exists
                            if (!window.enhancedChartControl) {{
                                return {{ success: false, error: 'enhancedChartControl not found' }};
                            }}
                            
                            // Process the command
                            await window.enhancedChartControl.processEnhancedResponse("{test['command']}");
                            
                            // Check current indicators (if applicable)
                            const indicators = window.enhancedChartControl.getCurrentIndicators ? 
                                window.enhancedChartControl.getCurrentIndicators() : [];
                            
                            return {{ 
                                success: true, 
                                command: "{test['command']}",
                                indicators: indicators
                            }};
                        }} catch (error) {{
                            return {{ 
                                success: false, 
                                error: error.toString(),
                                command: "{test['command']}"
                            }};
                        }}
                    }}
                """)
                
                if result['success']:
                    print(f"   ✅ Command executed successfully")
                    if 'indicators' in result and result['indicators']:
                        print(f"   📊 Active indicators: {result['indicators']}")
                else:
                    print(f"   ❌ Command failed: {result.get('error', 'Unknown error')}")
                
                # Wait to see visual result
                await page.wait_for_timeout(2000)
                
                # Take screenshot
                screenshot_name = f"manual_test_{i}_{test['name'].replace('/', '_').replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_name)
                print(f"   📸 Screenshot: {screenshot_name}")
                
                results["tests"].append({
                    "test": test['name'],
                    "command": test['command'],
                    "result": result,
                    "screenshot": screenshot_name,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                print(f"   ❌ Error executing command: {e}")
                results["tests"].append({
                    "test": test['name'],
                    "command": test['command'],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        # Test Voice Assistant command generation
        print("\n5️⃣ Testing Voice Assistant command generation...")
        
        # Connect Voice Assistant
        try:
            voice_button = await page.wait_for_selector('.voice-fab', timeout=5000)
            await voice_button.click()
            await page.wait_for_selector('.voice-fab.active', timeout=10000)
            print("   ✅ Voice Assistant connected")
            
            await page.wait_for_timeout(3000)
            
            # Send a simple command that should generate chart commands
            test_query = "Draw support at 440 and resistance at 460 on TSLA"
            print(f"\n   Testing query: '{test_query}'")
            
            input_field = await page.query_selector('.voice-conversation-section input[type="text"], .voice-conversation-section textarea')
            if input_field:
                await input_field.click()
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Delete")
                await input_field.type(test_query)
                await page.keyboard.press("Enter")
                
                # Wait for response
                await page.wait_for_timeout(8000)
                
                # Check if chart commands were generated
                console_logs = []
                page.on("console", lambda msg: console_logs.append(msg.text()))
                
                # Take final screenshot
                await page.screenshot(path="manual_test_voice_command.png")
                print("   📸 Voice command test screenshot saved")
                
        except Exception as e:
            print(f"   ❌ Voice Assistant test failed: {e}")
        
        # Final screenshot
        print("\n6️⃣ Taking final screenshot...")
        await page.screenshot(path="manual_test_final.png", full_page=True)
        print("   📸 Final state captured")
        
        # Save results
        with open(f"manual_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved")
        
        print("\n⏸️ Browser will remain open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()
        print("✅ Manual test complete!")


if __name__ == "__main__":
    print("\n🚀 Starting Manual Chart Command Test")
    print("This will test chart commands directly through the browser console")
    asyncio.run(test_manual_chart_commands())