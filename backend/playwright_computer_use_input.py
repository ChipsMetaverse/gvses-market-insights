#!/usr/bin/env python3
"""
Playwright script to interact with Computer Use interface.
Targets the text input field at the bottom of the interface.
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def run():
    print("Starting Computer Use interaction test...")
    
    # The prompt from COMPUTER_USE_INSTRUCTIONS.md
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

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print("Navigating to Computer Use interface at localhost:8080...")
            await page.goto("http://localhost:8080", wait_until='domcontentloaded', timeout=60000)
            
            # Wait for the page to load
            await page.wait_for_timeout(3000)
            
            print("Looking for the text input field at the bottom...")
            
            # Based on the screenshot, target the input field with placeholder text
            # Try multiple selectors to find the input field
            selectors = [
                'input[placeholder*="Type a message"]',
                'textarea[placeholder*="Type a message"]',
                'input[type="text"]',
                'textarea',
                '.stTextInput input',
                '.stTextArea textarea',
                '[data-testid="stTextInput"] input',
                '[data-testid="stTextArea"] textarea'
            ]
            
            input_field = None
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=5000)
                    if element:
                        print(f"Found input field with selector: {selector}")
                        input_field = element
                        break
                except:
                    continue
            
            if not input_field:
                print("Could not find input field with standard selectors, trying to find by text...")
                # Try to find by looking for elements containing the placeholder text
                input_field = await page.get_by_placeholder("Type a message")
            
            if input_field:
                print("Clicking on the input field...")
                await input_field.click()
                await page.wait_for_timeout(500)
                
                print("Typing the test prompt...")
                # Type the prompt slowly to ensure it's captured
                await input_field.type(test_prompt, delay=50)
                
                print("Waiting a moment before submitting...")
                await page.wait_for_timeout(1000)
                
                print("Pressing Enter to submit...")
                await page.keyboard.press("Enter")
                
                print("Command sent! Waiting for Computer Use to process...")
                print("Computer Use will now:")
                print("1. Open Firefox in the virtual desktop")
                print("2. Navigate to the trading application")
                print("3. Interact with the Voice Assistant")
                print("4. Report back the results")
                
                # Keep the browser open to observe the interaction
                print("\nKeeping browser open for 2 minutes to observe Computer Use actions...")
                print("You should see activity in the Computer Use interface.")
                print("Press Ctrl+C to stop monitoring.")
                
                # Monitor for 2 minutes
                for i in range(120):
                    await page.wait_for_timeout(1000)
                    if i % 10 == 0:
                        print(f"Monitoring... {120-i} seconds remaining")
                
            else:
                print("ERROR: Could not find the input field!")
                print("Please make sure Computer Use is running at http://localhost:8080")
                
                # Take a screenshot for debugging
                await page.screenshot(path="computer_use_debug.png")
                print("Screenshot saved as computer_use_debug.png for debugging")
        
        except Exception as e:
            print(f"Error occurred: {e}")
            await page.screenshot(path="computer_use_error.png")
            print("Screenshot saved as computer_use_error.png")
        
        finally:
            print("Test complete.")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run())