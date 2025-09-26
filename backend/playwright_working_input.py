#!/usr/bin/env python3
"""
Working script to send message to Computer Use
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Sending message to Computer Use...")
    
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
        
        print("Opening localhost:8080...")
        await page.goto("http://localhost:8080", wait_until='networkidle')
        await page.wait_for_timeout(3000)
        
        # Get the first iframe (Streamlit chat)
        frames = page.frames
        if len(frames) < 2:
            print("Error: Expected at least 2 frames")
            await browser.close()
            return
        
        # The chat is in iframe 1 (index 1)
        chat_frame = frames[1]
        
        print("Finding chat input in iframe...")
        
        # Find the textarea with the specific placeholder
        chat_input = await chat_frame.wait_for_selector(
            'textarea[placeholder*="Type a message to send to Claude"]',
            timeout=10000
        )
        
        if chat_input:
            print("✓ Found chat input!")
            
            # Scroll into view
            await chat_input.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            
            # Click and clear
            print("Clicking input field...")
            await chat_input.click()
            await chat_input.fill("")
            
            # Type the message
            print("Typing message...")
            await chat_input.type(test_prompt, delay=20)
            
            # Submit
            print("Pressing Enter to submit...")
            await page.wait_for_timeout(1000)
            await chat_input.press("Enter")
            
            print("\n✅ SUCCESS! Message sent to Computer Use!")
            print("Computer Use should now:")
            print("  1. Open Firefox")
            print("  2. Navigate to the trading app")
            print("  3. Test the Voice Assistant")
            
            # Keep browser open to observe
            print("\nKeeping browser open for 90 seconds to observe Computer Use actions...")
            for i in range(9):
                await page.wait_for_timeout(10000)
                print(f"  {90 - (i+1)*10} seconds remaining...")
            
        else:
            print("❌ Could not find chat input")
        
        await browser.close()
        print("\nTest complete!")

if __name__ == "__main__":
    asyncio.run(run())