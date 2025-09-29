#!/usr/bin/env python3
"""
Quick Technical Analysis Test - Focus on core capabilities
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime


async def test_tech_capabilities():
    """Quick test of key technical analysis features."""
    
    print("=" * 70)
    print("🔬 QUICK TECHNICAL ANALYSIS TEST")
    print("=" * 70)
    
    # Core test questions
    test_questions = [
        {
            "name": "Support/Resistance",
            "question": "Show support and resistance levels on TSLA",
            "wait": 12000
        },
        {
            "name": "Fibonacci", 
            "question": "Draw Fibonacci retracement on TSLA",
            "wait": 12000
        },
        {
            "name": "Patterns",
            "question": "Identify any patterns on TSLA chart",
            "wait": 12000
        },
        {
            "name": "RSI Indicator",
            "question": "Show RSI indicator on TSLA",
            "wait": 10000
        },
        {
            "name": "MACD Indicator",
            "question": "Add MACD to TSLA chart",
            "wait": 10000
        },
        {
            "name": "Trade Setup",
            "question": "Mark entry at 440, stop loss at 430, and target at 460 on TSLA",
            "wait": 12000
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
            slow_mo=300
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to app
        print("2️⃣ Opening trading app...")
        await page.goto("http://localhost:5174")
        await page.wait_for_timeout(5000)
        
        # Connect Voice Assistant
        print("3️⃣ Connecting Voice Assistant...")
        try:
            voice_button = await page.wait_for_selector('.voice-fab', timeout=5000)
            await voice_button.click()
            await page.wait_for_selector('.voice-fab.active', timeout=10000)
            print("   ✅ Voice Assistant connected")
        except Exception as e:
            print(f"   ❌ Failed to connect: {e}")
            await browser.close()
            return
        
        await page.wait_for_timeout(3000)
        
        # Test each capability
        print("\n4️⃣ Testing capabilities...")
        
        for i, test in enumerate(test_questions, 1):
            print(f"\n📝 Test {i}: {test['name']}")
            print(f"   Question: {test['question']}")
            
            try:
                # Find input field
                input_field = await page.query_selector('.voice-conversation-section input[type="text"], .voice-conversation-section textarea')
                
                if input_field:
                    # Clear and type question
                    await input_field.click()
                    await page.keyboard.press("Control+A")
                    await page.keyboard.press("Delete")
                    await input_field.type(test['question'])
                    
                    # Submit
                    await page.keyboard.press("Enter")
                    
                    # Wait for response
                    await page.wait_for_timeout(test['wait'])
                    
                    # Take screenshot
                    screenshot_name = f"tech_quick_{i}_{test['name'].replace('/', '_')}.png"
                    await page.screenshot(path=screenshot_name)
                    print(f"   📸 Screenshot: {screenshot_name}")
                    
                    # Try to detect if chart was modified
                    # Look for any visual indicators that commands were executed
                    chart_element = await page.query_selector('.tv-lightweight-charts, canvas')
                    if chart_element:
                        print(f"   ✅ Chart element found")
                    
                    results["tests"].append({
                        "test": test['name'],
                        "question": test['question'],
                        "screenshot": screenshot_name,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                else:
                    print(f"   ❌ Input field not found")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Final screenshot
        print("\n5️⃣ Taking final screenshot...")
        await page.screenshot(path="tech_quick_final.png", full_page=True)
        print("   📸 Final state captured")
        
        # Save results
        with open(f"tech_quick_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
            json.dump(results, f, indent=2)
        print("\n💾 Results saved")
        
        print("\n⏸️ Browser will remain open for 15 seconds...")
        await page.wait_for_timeout(15000)
        
        await browser.close()
        print("✅ Test complete!")


if __name__ == "__main__":
    print("\n🚀 Starting Quick Technical Analysis Test")
    asyncio.run(test_tech_capabilities())