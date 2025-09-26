#!/usr/bin/env python3
"""
Robust Playwright Test for Computer Use
========================================
Handles slow loading and tests the backend connection fix.
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from datetime import datetime
import time

async def robust_computer_use_test():
    """Robust test that handles Computer Use's slow loading."""
    
    print("=" * 60)
    print("ROBUST COMPUTER USE TEST WITH BACKEND FIX")
    print("=" * 60)
    print()
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            print("1. Opening Computer Use interface (with extended timeout)...")
            
            # Navigate with a longer timeout
            try:
                await page.goto("http://localhost:8080", wait_until="domcontentloaded", timeout=60000)
                print("   Page loaded successfully")
            except PlaywrightTimeout:
                print("   Initial load timeout - continuing anyway")
            
            # Wait for the page to stabilize
            print("2. Waiting for interface to stabilize...")
            await asyncio.sleep(8)
            
            # Take a screenshot to see current state
            await page.screenshot(path="computer_use_initial_state.png")
            print("   Initial screenshot saved")
            
            print("3. Looking for input methods...")
            
            # Method 1: Direct typing in the window
            print("   Attempting to type directly in the window...")
            await page.click('body')  # Focus the page
            await asyncio.sleep(1)
            
            # The comprehensive test command
            test_command = """Test the Voice Assistant with the backend fix:

1. Open Firefox browser
2. Go to http://host.docker.internal:5174
3. Refresh the page (F5) to get latest updates
4. Click the Voice Assistant input (right panel)
5. Type: "What is the current price of PLTR?"
6. Press Enter
7. Report the response

Please describe what happens at each step."""
            
            print("4. Sending test command...")
            
            # Try multiple input methods
            success = False
            
            # Method 1: Type directly
            try:
                await page.keyboard.type(test_command, delay=10)
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                print("   ✓ Command typed directly")
                success = True
            except Exception as e:
                print(f"   Direct typing failed: {e}")
            
            if not success:
                # Method 2: Find any textarea
                try:
                    await page.wait_for_selector('textarea', timeout=5000)
                    await page.fill('textarea', test_command)
                    await page.keyboard.press("Enter")
                    print("   ✓ Command sent via textarea")
                    success = True
                except:
                    print("   Textarea method failed")
            
            if not success:
                # Method 3: Find any text input
                try:
                    await page.wait_for_selector('input[type="text"]', timeout=5000)
                    await page.fill('input[type="text"]', test_command)
                    await page.keyboard.press("Enter")
                    print("   ✓ Command sent via text input")
                    success = True
                except:
                    print("   Text input method failed")
            
            if not success:
                print("   ⚠️  Could not send command - may need manual input")
            else:
                print("\n5. Command sent successfully! Monitoring Computer Use...")
            
            # Extended monitoring period
            print("6. Monitoring for 3 minutes...")
            print("-" * 40)
            
            start_time = time.time()
            max_duration = 180  # 3 minutes
            screenshot_count = 0
            
            while time.time() - start_time < max_duration:
                elapsed = int(time.time() - start_time)
                
                # Take periodic screenshots
                if elapsed % 30 == 0 and elapsed > 0:
                    screenshot_count += 1
                    screenshot_name = f"computer_use_progress_{screenshot_count}.png"
                    await page.screenshot(path=screenshot_name)
                    print(f"   [{elapsed}s] Progress screenshot: {screenshot_name}")
                
                # Log progress
                if elapsed % 15 == 0:
                    print(f"   [{elapsed}s] Monitoring...")
                    
                    # Check for any visible text about PLTR or errors
                    page_text = await page.content()
                    if "PLTR" in page_text:
                        print("   🎯 PLTR mentioned in page!")
                    if "error" in page_text.lower() and "network" in page_text.lower():
                        print("   ⚠️  Network error detected")
                    if "connect to send messages" in page_text.lower():
                        print("   ⚠️  Backend connection issue detected")
                
                await asyncio.sleep(5)
            
            print("-" * 40)
            
            # Final screenshot
            print("\n7. Taking final screenshot...")
            final_screenshot = "computer_use_final_result.png"
            await page.screenshot(path=final_screenshot, full_page=True)
            print(f"   Final screenshot: {final_screenshot}")
            
            # Try to extract any messages if available
            print("\n8. Checking for Computer Use messages...")
            try:
                # Look for any divs that might contain chat messages
                messages = await page.query_selector_all('div[class*="message"], div[class*="chat"], [data-testid*="message"]')
                if messages:
                    print(f"   Found {len(messages)} potential message elements")
                    for i, msg in enumerate(messages[-3:], 1):
                        try:
                            text = await msg.inner_text()
                            if text and len(text) > 10:
                                print(f"\n   Message {i}: {text[:200]}...")
                        except:
                            pass
                else:
                    print("   No message elements found")
            except Exception as e:
                print(f"   Could not extract messages: {e}")
            
            # Check the desktop view iframe
            print("\n9. Checking desktop view...")
            iframes = await page.query_selector_all('iframe')
            print(f"   Found {len(iframes)} iframe(s)")
            
            if iframes:
                # Try to check iframe content
                for i, iframe in enumerate(iframes):
                    try:
                        frame = await iframe.content_frame()
                        if frame:
                            frame_url = frame.url
                            print(f"   Iframe {i+1} URL: {frame_url}")
                    except:
                        pass
            
            print("\n" + "=" * 60)
            print("TEST COMPLETE!")
            print("=" * 60)
            print("\nResults:")
            print("✅ Computer Use interface accessed")
            if success:
                print("✅ Test command sent")
            else:
                print("⚠️  Command may need manual input")
            print("✅ Monitored for 3 minutes")
            print("✅ Screenshots captured")
            print("\nCheck the screenshots to see if:")
            print("- Firefox opened and navigated to the app")
            print("- Voice Assistant responded to PLTR query")
            print("- Backend connection is working (no 'Connect to send messages')")
            
            # Keep browser open for manual inspection
            print("\n⏸️  Keeping browser open for 20 seconds for inspection...")
            await asyncio.sleep(20)
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            
            # Emergency screenshot
            try:
                await page.screenshot(path="computer_use_error_state.png")
                print("   Error screenshot saved")
            except:
                pass
                
        finally:
            await browser.close()
            print("\n🏁 Test ended.")

async def main():
    """Run the robust test."""
    await robust_computer_use_test()

if __name__ == "__main__":
    print("Starting robust Computer Use test...")
    print("This test handles slow loading and connection issues")
    print()
    asyncio.run(main())