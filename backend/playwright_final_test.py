#!/usr/bin/env python3
"""
Final Playwright Test with All Fixes Applied
=============================================
Tests Computer Use with the corrected prompt using host.docker.internal.
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def run_final_test():
    """Run the final Computer Use test with all fixes."""
    
    print("=" * 60)
    print("FINAL COMPUTER USE TEST - ALL FIXES APPLIED")
    print("=" * 60)
    print()
    print("Testing with:")
    print("✓ CORS fix applied (API calls to host.docker.internal)")
    print("✓ getApiUrl import fixed")
    print("✓ Using host.docker.internal:5174")
    print()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        page = await browser.new_page(viewport={'width': 1440, 'height': 900})
        
        try:
            print("1. Opening Computer Use interface...")
            await page.goto("http://localhost:8080", wait_until="domcontentloaded", timeout=60000)
            print("   ✓ Computer Use interface loaded")
            
            # Wait for interface to stabilize
            print("2. Waiting for interface to load completely...")
            await asyncio.sleep(10)
            
            # The updated test prompt using host.docker.internal
            test_prompt = """Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load completely
4. Find the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (placeholder: "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit
8. Report what information was provided

As a professional trader with 30+ years of experience (G'sves persona), 
also provide insights on PLTR's current market position."""
            
            print("3. Sending test prompt to Computer Use...")
            print("   Prompt: Test Voice Assistant with PLTR query")
            
            # Try multiple methods to send the prompt
            success = False
            
            # Method 1: Direct typing
            try:
                await page.click('body')
                await asyncio.sleep(1)
                
                # Type character by character for reliability
                for char in test_prompt:
                    await page.keyboard.type(char, delay=3)
                
                await asyncio.sleep(1)
                await page.keyboard.press("Enter")
                print("   ✓ Prompt sent via direct typing")
                success = True
            except Exception as e:
                print(f"   Direct typing failed: {e}")
            
            if not success:
                # Method 2: Try textarea
                try:
                    textarea = await page.wait_for_selector('textarea', timeout=3000)
                    await textarea.click()
                    await textarea.fill(test_prompt)
                    await page.keyboard.press("Enter")
                    print("   ✓ Prompt sent via textarea")
                    success = True
                except:
                    print("   Textarea method not available")
            
            if not success:
                # Method 3: Try input field
                try:
                    input_field = await page.wait_for_selector('input[type="text"]', timeout=3000)
                    await input_field.click()
                    await input_field.fill(test_prompt)
                    await page.keyboard.press("Enter")
                    print("   ✓ Prompt sent via input field")
                    success = True
                except:
                    print("   Input field method not available")
            
            if success:
                print("\n4. Prompt sent successfully!")
                print("   Computer Use will now:")
                print("   • Open Firefox browser")
                print("   • Navigate to host.docker.internal:5174")
                print("   • Test the Voice Assistant")
                print("   • Report PLTR information")
            else:
                print("\n⚠️  Could not send prompt automatically")
                print("   Please paste the prompt manually in the Computer Use interface")
            
            # Monitor for results
            print("\n5. Monitoring Computer Use actions (3 minutes)...")
            print("-" * 40)
            
            start_time = time.time()
            max_duration = 180  # 3 minutes
            screenshot_count = 0
            
            while time.time() - start_time < max_duration:
                elapsed = int(time.time() - start_time)
                
                # Take screenshots periodically
                if elapsed % 30 == 0 and elapsed > 0:
                    screenshot_count += 1
                    screenshot_name = f"final_test_progress_{screenshot_count}.png"
                    await page.screenshot(path=screenshot_name, full_page=True)
                    print(f"   [{elapsed}s] Screenshot: {screenshot_name}")
                
                # Progress indicator
                if elapsed % 15 == 0:
                    print(f"   [{elapsed}s] Monitoring... (Computer Use should be interacting with app)")
                
                await asyncio.sleep(5)
            
            print("-" * 40)
            
            # Final screenshot
            print("\n6. Taking final screenshot...")
            final_screenshot = "final_test_result.png"
            await page.screenshot(path=final_screenshot, full_page=True)
            print(f"   Final screenshot saved: {final_screenshot}")
            
            print("\n" + "=" * 60)
            print("TEST COMPLETE!")
            print("=" * 60)
            print()
            print("📊 What to Check:")
            print("1. Firefox opened and navigated to host.docker.internal:5174")
            print("2. Voice Assistant input was clicked")
            print("3. 'What is the current price of PLTR?' was typed")
            print("4. A response was received (not 'Connect to send messages')")
            print("5. No CORS errors in the browser console")
            print()
            print("✅ Success Indicators:")
            print("• Voice Assistant shows PLTR price data")
            print("• Chart loads without 'Network Error'")
            print("• Market Insights panel shows real prices")
            print("• API calls go to host.docker.internal:8000")
            print()
            print("Check the screenshots to verify the results!")
            
            # Keep browser open for inspection
            print("\n⏸️  Keeping browser open for 20 seconds for inspection...")
            await asyncio.sleep(20)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                await page.screenshot(path="final_test_error.png")
                print("   Error screenshot saved")
            except:
                pass
        
        finally:
            await browser.close()
            print("\n🏁 Browser closed. Test ended.")

async def main():
    """Run the final test."""
    await run_final_test()

if __name__ == "__main__":
    print("Starting final Computer Use test with all fixes...")
    print("This will test the complete flow with CORS and import fixes applied.")
    print()
    asyncio.run(main())