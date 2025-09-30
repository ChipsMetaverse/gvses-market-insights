#!/usr/bin/env python3
"""
Run OpenAI Computer Use to test the trading application
Uses the existing Computer Use Verifier service
"""

import os
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Set environment variables
os.environ["USE_COMPUTER_USE"] = "true"
os.environ["TUNNEL_URL"] = "http://localhost:5174"
os.environ["COMPUTER_USE_HEADLESS"] = "false"  # Show browser
os.environ["COMPUTER_USE_SLOWMO_MS"] = "500"  # Slow actions for visibility

async def run_computer_use_test():
    """Run Computer Use verification on trading app."""
    
    print("=" * 70)
    print("🤖 OPENAI COMPUTER USE - TRADING APP VERIFICATION")
    print("=" * 70)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n❌ OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY=sk-...")
        return
    
    print("\n✅ OpenAI API key detected")
    
    # Import the verifier
    try:
        from services.computer_use_verifier import ComputerUseVerifier
        print("✅ Computer Use Verifier imported")
    except ImportError as e:
        print(f"❌ Cannot import Computer Use Verifier: {e}")
        print("   Make sure you're in the backend directory")
        return
    
    # Create test scenario
    test_scenario = {
        "name": "Test ML Pattern Detection",
        "priority": "High",
        "steps": [
            {
                "action": "navigate",
                "description": "Open trading application",
                "url": "http://localhost:5174"
            },
            {
                "action": "wait",
                "description": "Wait for page to load",
                "duration": 3000
            },
            {
                "action": "screenshot",
                "description": "Capture initial state"
            },
            {
                "action": "find_element",
                "description": "Find Voice Assistant input",
                "selector": "input[placeholder*='message'], textarea"
            },
            {
                "action": "click",
                "description": "Click on message input"
            },
            {
                "action": "type",
                "description": "Type pattern request",
                "text": "Show me TSLA patterns"
            },
            {
                "action": "key",
                "description": "Press Enter to submit",
                "key": "Enter"
            },
            {
                "action": "wait",
                "description": "Wait for response",
                "duration": 5000
            },
            {
                "action": "screenshot",
                "description": "Capture final state"
            }
        ],
        "expected": {
            "elements_visible": [
                "TSLA chart",
                "Technical levels",
                "Voice Assistant panel"
            ],
            "actions_completed": [
                "Message typed in input",
                "Response received"
            ],
            "validation": {
                "tsla_price_visible": True,
                "technical_levels_shown": True,
                "message_sent": True
            }
        }
    }
    
    # Initialize verifier
    print("\n📋 Initializing Computer Use Verifier...")
    verifier = ComputerUseVerifier()
    
    # Generate session ID
    session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"   Session ID: {session_id}")
    
    # Run verification
    print("\n🚀 Starting verification...")
    print("   A browser window will open and perform automated testing")
    print("   Watch as it:")
    print("   • Navigates to the app")
    print("   • Finds the Voice Assistant")
    print("   • Types a message")
    print("   • Captures results")
    
    try:
        # Run the verification
        result = await verifier.run_verification(
            scenarios=[test_scenario],
            session_id=session_id
        )
        
        print("\n✅ Verification completed!")
        
        # Display results
        if result.get("success"):
            print("\n📊 Results:")
            issues = result.get("issues", [])
            if issues:
                print(f"   ⚠️ Issues found: {len(issues)}")
                for issue in issues[:3]:
                    print(f"      - {issue}")
            else:
                print("   ✅ No issues found!")
            
            # Save report
            report_file = Path(f"verification_reports/{session_id}.json")
            report_file.parent.mkdir(exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n   📄 Full report saved: {report_file}")
            
        else:
            print(f"\n❌ Verification failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()

async def simple_browser_test():
    """Simpler fallback test using Playwright directly."""
    
    print("\n" + "=" * 70)
    print("🎯 SIMPLE BROWSER TEST (Fallback)")
    print("=" * 70)
    
    try:
        from playwright.async_api import async_playwright
        
        print("\n1️⃣ Launching browser...")
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=1000
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("2️⃣ Navigating to app...")
        await page.goto("http://localhost:5174")
        await page.wait_for_timeout(5000)
        
        print("3️⃣ Taking screenshot...")
        await page.screenshot(path="openai_test_1_initial.png")
        print("   📸 Saved: openai_test_1_initial.png")
        
        print("4️⃣ Looking for message input...")
        input_field = await page.query_selector('input[placeholder*="message"], textarea')
        
        if input_field:
            print("5️⃣ Typing message...")
            await input_field.click()
            await input_field.fill("Show me TSLA patterns")
            await page.keyboard.press("Enter")
            
            print("6️⃣ Waiting for response...")
            await page.wait_for_timeout(5000)
            
            print("7️⃣ Taking final screenshot...")
            await page.screenshot(path="openai_test_2_final.png")
            print("   📸 Saved: openai_test_2_final.png")
        else:
            print("   ⚠️ Could not find message input")
        
        print("\n⏸️  Browser will close in 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()
        await playwright.stop()
        
        print("✅ Simple test completed!")
        
    except Exception as e:
        print(f"❌ Simple test failed: {e}")

async def main():
    """Main execution."""
    
    # Try Computer Use Verifier first
    try:
        await run_computer_use_test()
    except Exception as e:
        print(f"\n⚠️ Computer Use Verifier failed: {e}")
        print("   Falling back to simple browser test...")
        await simple_browser_test()

if __name__ == "__main__":
    print("\n🚀 OpenAI Computer Use Test")
    print("   This will control a browser to test your trading app")
    print("   Make sure:")
    print("   ✓ Trading app is running (port 5174)")
    print("   ✓ Backend is running (port 8000)")
    print("   ✓ OPENAI_API_KEY is set")
    
    asyncio.run(main())