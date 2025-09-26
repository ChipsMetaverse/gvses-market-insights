#!/usr/bin/env python3
"""
Playwright script to send message to Computer Use via iframe.
The input field is inside an iframe on the left side.
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Starting Computer Use interaction via iframe...")
    
    test_prompt = """Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load completely
4. Find the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (placeholder: "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit
8. Report what information was provided"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Opening Computer Use at localhost:8080...")
        await page.goto("http://localhost:8080", wait_until='networkidle')
        
        # Wait for page and iframes to load
        await page.wait_for_timeout(5000)
        
        print("Finding iframes...")
        frames = page.frames
        print(f"Found {len(frames)} frames")
        
        # Try each iframe to find the chat input
        input_field = None
        for i, frame in enumerate(frames):
            if frame == page.main_frame:
                continue
                
            print(f"Checking iframe {i}...")
            
            try:
                # Look for textareas in this iframe
                textareas = await frame.locator('textarea').all()
                if textareas:
                    print(f"  Found {len(textareas)} textareas in iframe {i}")
                    
                    # Try the first visible textarea
                    for textarea in textareas:
                        if await textarea.is_visible():
                            print(f"  Found visible textarea in iframe {i}")
                            input_field = textarea
                            break
                
                # If no textarea, try input fields
                if not input_field:
                    inputs = await frame.locator('input[type="text"]').all()
                    if inputs:
                        print(f"  Found {len(inputs)} text inputs in iframe {i}")
                        for inp in inputs:
                            if await inp.is_visible():
                                placeholder = await inp.get_attribute('placeholder')
                                print(f"    Found visible input with placeholder: {placeholder}")
                                if placeholder and 'message' in placeholder.lower():
                                    input_field = inp
                                    break
                
                if input_field:
                    break
                    
            except Exception as e:
                print(f"  Error checking iframe {i}: {e}")
        
        if input_field:
            print("Found input field! Clicking and typing...")
            await input_field.click()
            await page.wait_for_timeout(500)
            
            print("Clearing any existing text...")
            await input_field.fill("")
            
            print("Typing the prompt...")
            await input_field.type(test_prompt, delay=50)
            
            print("Waiting before submit...")
            await page.wait_for_timeout(1000)
            
            print("Pressing Enter to submit...")
            await page.keyboard.press("Enter")
            
            print("✅ Message sent successfully!")
            print("Computer Use should now execute the test.")
            
            # Keep open to observe
            print("\nKeeping browser open for 60 seconds to observe...")
            await page.wait_for_timeout(60000)
            
        else:
            print("❌ Could not find input field in any iframe")
            print("Taking screenshot for debugging...")
            await page.screenshot(path="iframe_debug.png")
            print("Screenshot saved as iframe_debug.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())