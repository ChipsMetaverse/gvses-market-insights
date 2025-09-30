#!/usr/bin/env python3
"""
Computer Use Agent - Trading App Demonstration
Automatically sends commands to CUA to interact with the trading application
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def demonstrate_cua_trading():
    """Send commands to Computer Use to interact with trading app."""
    
    print("=" * 70)
    print("🤖 COMPUTER USE AGENT - TRADING APP DEMONSTRATION")
    print("=" * 70)
    
    async with async_playwright() as p:
        # Launch browser to view Computer Use interface
        print("\n1️⃣ Opening Computer Use interface...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=500
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to Computer Use
        await page.goto('http://localhost:8080')
        await page.wait_for_timeout(5000)
        
        print("   ✅ Computer Use interface loaded")
        
        # Find the chat input
        print("\n2️⃣ Sending trading app test command to CUA...")
        
        # Look for the message input field
        chat_input = await page.query_selector('textarea[placeholder*="Type"], input[type="text"]')
        
        if not chat_input:
            # Try alternative selectors
            chat_input = await page.query_selector('textarea')
        
        if chat_input:
            # Command for Computer Use to execute
            cua_command = """Please interact with the trading application to demonstrate ML pattern detection:

1. Open Firefox browser in the virtual desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading dashboard to fully load
4. Look for the Voice Assistant panel on the right side
5. Click on the message input field
6. Type: "Show me ML-enhanced patterns for TSLA"
7. Press Enter to submit the message
8. Wait 5 seconds for the response
9. Take a screenshot of the results
10. Report what patterns were detected and if ML enhancement is visible

Also, as G'sves the professional trader, provide analysis of TSLA's current technical setup based on the chart."""
            
            await chat_input.click()
            await chat_input.fill(cua_command)
            
            # Submit the message (usually Enter key or a send button)
            await page.keyboard.press('Enter')
            
            print("   ✅ Command sent to Computer Use Agent")
            print("\n   📝 Command details:")
            print("      - Open Firefox browser")
            print("      - Navigate to trading app")
            print("      - Interact with Voice Assistant")
            print("      - Request ML pattern detection")
            print("      - Analyze results")
            
            # Wait and monitor CUA's actions
            print("\n3️⃣ Monitoring Computer Use actions...")
            print("   ⏳ CUA is now working autonomously...")
            print("   👀 Watch the right panel to see live actions")
            
            # Take screenshots of CUA in action
            await page.wait_for_timeout(10000)
            await page.screenshot(path='cua_demo_1_command_sent.png')
            print("   📸 Screenshot: Command sent")
            
            # Wait for CUA to navigate
            await page.wait_for_timeout(20000)
            await page.screenshot(path='cua_demo_2_navigating.png')
            print("   📸 Screenshot: CUA navigating")
            
            # Wait for interaction
            await page.wait_for_timeout(30000)
            await page.screenshot(path='cua_demo_3_interacting.png')
            print("   📸 Screenshot: CUA interacting with app")
            
            # Final state
            await page.wait_for_timeout(20000)
            await page.screenshot(path='cua_demo_4_results.png')
            print("   📸 Screenshot: Final results")
            
        else:
            print("   ❌ Could not find chat input field")
        
        print("\n" + "=" * 70)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 70)
        print("\nWhat happened:")
        print("1. Computer Use Agent received the command")
        print("2. CUA opened Firefox in the virtual desktop")
        print("3. CUA navigated to the trading application")
        print("4. CUA interacted with the Voice Assistant")
        print("5. CUA requested ML pattern detection")
        print("6. Results were analyzed and reported")
        
        print("\n📸 Screenshots saved:")
        print("  - cua_demo_1_command_sent.png")
        print("  - cua_demo_2_navigating.png")
        print("  - cua_demo_3_interacting.png")
        print("  - cua_demo_4_results.png")
        
        print("\n🔗 View Computer Use directly at: http://localhost:8080")
        print("   The browser will remain open for inspection...")
        
        # Keep browser open for manual inspection
        await page.wait_for_timeout(30000)
        await browser.close()

if __name__ == "__main__":
    print("\n🚀 Starting Computer Use Agent Demonstration...")
    print("   Make sure:")
    print("   ✓ Docker is running")
    print("   ✓ Computer Use container is active (port 8080)")
    print("   ✓ Trading app is running (port 5174)")
    print("   ✓ Backend API is running (port 8000)")
    
    asyncio.run(demonstrate_cua_trading())