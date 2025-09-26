#!/usr/bin/env python3
"""
Playwright Test for CORS Fix Verification
==========================================
Tests that Computer Use can now access the backend without CORS errors.
"""

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import time
import json

async def test_cors_fix():
    """Test Computer Use with the CORS fix applied."""
    
    print("=" * 60)
    print("TESTING CORS FIX WITH COMPUTER USE")
    print("=" * 60)
    print()
    print("This test verifies:")
    print("✓ Frontend uses host.docker.internal for API calls")
    print("✓ No CORS errors occur")
    print("✓ Voice Assistant can receive responses")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        page = await context.new_page()
        
        try:
            print("1. Opening Computer Use interface...")
            await page.goto("http://localhost:8080", wait_until="domcontentloaded", timeout=60000)
            print("   ✓ Interface loaded")
            
            # Wait for stabilization
            print("2. Waiting for interface to stabilize...")
            await asyncio.sleep(10)
            
            # The comprehensive test command focusing on CORS
            test_command = """Test if CORS fix is working:

1. Open Firefox browser
2. Navigate to http://host.docker.internal:5174
3. Press F5 to refresh the page (important: gets latest code with CORS fix)
4. Open browser console (F12) to watch for errors
5. Click on Voice Assistant input field (right panel)
6. Type: "What is the current price of PLTR?"
7. Press Enter
8. Watch the console - check if there are any CORS errors
9. Report:
   - Whether you received a response
   - Whether console shows CORS errors
   - Whether API calls go to host.docker.internal:8000

Please describe what happens at each step, especially any errors."""
            
            print("3. Sending CORS test command...")
            
            # Try to send the command
            success = False
            
            # Method 1: Direct typing
            try:
                await page.click('body')
                await asyncio.sleep(1)
                
                # Type slowly for better reliability
                for char in test_command:
                    await page.keyboard.type(char, delay=5)
                    
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                print("   ✓ Command sent via direct typing")
                success = True
            except Exception as e:
                print(f"   Direct typing failed: {e}")
            
            if not success:
                # Method 2: Try textarea if available
                try:
                    textarea = await page.wait_for_selector('textarea', timeout=3000)
                    await textarea.click()
                    await textarea.fill(test_command)
                    await page.keyboard.press("Enter")
                    print("   ✓ Command sent via textarea")
                    success = True
                except:
                    print("   Textarea method not available")
            
            if success:
                print("\n4. Command sent! Monitoring Computer Use response...")
                print("   Computer Use should now:")
                print("   • Open Firefox and navigate to the app")
                print("   • Refresh to get CORS fix")
                print("   • Test Voice Assistant")
                print("   • Report if backend connection works")
            
            # Extended monitoring
            print("\n5. Monitoring for 4 minutes...")
            print("-" * 40)
            
            start_time = time.time()
            max_duration = 240  # 4 minutes for thorough testing
            screenshot_count = 0
            
            while time.time() - start_time < max_duration:
                elapsed = int(time.time() - start_time)
                
                # Take periodic screenshots
                if elapsed % 45 == 0 and elapsed > 0:
                    screenshot_count += 1
                    screenshot_name = f"cors_test_progress_{screenshot_count}.png"
                    await page.screenshot(path=screenshot_name, full_page=True)
                    print(f"   [{elapsed}s] Screenshot saved: {screenshot_name}")
                
                # Check page content for indicators
                if elapsed % 20 == 0:
                    page_content = await page.content()
                    
                    # Check for key indicators
                    checks = {
                        "PLTR mentioned": "PLTR" in page_content,
                        "CORS error": "CORS" in page_content and "error" in page_content.lower(),
                        "host.docker.internal": "host.docker.internal" in page_content,
                        "Network error": "network error" in page_content.lower(),
                        "Price data": "$" in page_content and any(x in page_content for x in ["245", "189", "421"])
                    }
                    
                    print(f"   [{elapsed}s] Status check:")
                    for check, result in checks.items():
                        if result:
                            emoji = "⚠️" if "error" in check.lower() else "✓"
                            print(f"       {emoji} {check}")
                
                await asyncio.sleep(5)
            
            print("-" * 40)
            
            # Final analysis
            print("\n6. Taking final screenshot...")
            final_screenshot = "cors_test_final_result.png"
            await page.screenshot(path=final_screenshot, full_page=True)
            print(f"   Final screenshot: {final_screenshot}")
            
            # Try to extract messages
            print("\n7. Checking for Computer Use responses...")
            try:
                # Look for any text mentioning CORS or success
                all_text = await page.inner_text('body')
                
                if "CORS" in all_text and "error" not in all_text.lower():
                    print("   ✓ CORS mentioned without errors - likely success!")
                elif "CORS" in all_text and "error" in all_text.lower():
                    print("   ⚠️ CORS errors detected - fix may not be working")
                elif "successfully" in all_text.lower() or "working" in all_text.lower():
                    print("   ✓ Success indicators found")
                
                # Check for price data
                if any(price in all_text for price in ["$245", "$189", "$421", "PLTR"]):
                    print("   ✓ Stock price data detected - API likely working!")
                
            except Exception as e:
                print(f"   Could not extract text: {e}")
            
            print("\n" + "=" * 60)
            print("CORS TEST COMPLETE!")
            print("=" * 60)
            
            print("\n📊 Results Summary:")
            print("✓ Test command sent to Computer Use")
            print("✓ Monitored for 4 minutes")
            print("✓ Screenshots captured")
            print()
            print("Check screenshots to verify:")
            print("1. Firefox navigated to host.docker.internal:5174")
            print("2. Page refreshed to get CORS fix")
            print("3. Voice Assistant received response (no CORS errors)")
            print("4. API calls go to host.docker.internal:8000")
            print()
            print("🎯 Key Success Indicator:")
            print("   Voice Assistant shows PLTR price instead of")
            print("   'Connect to send messages' or CORS errors")
            
            # Keep open for inspection
            print("\n⏸️  Keeping browser open for 15 seconds...")
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                await page.screenshot(path="cors_test_error.png")
                print("   Error screenshot saved")
            except:
                pass
                
        finally:
            await browser.close()
            print("\n🏁 Test completed.")

async def main():
    """Run the CORS fix test."""
    await test_cors_fix()

if __name__ == "__main__":
    print("Starting CORS fix verification test...")
    print("This will test if Computer Use can now access the backend")
    print("without CORS errors after our fixes.")
    print()
    asyncio.run(main())