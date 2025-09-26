#!/usr/bin/env python3
"""
Simple Playwright script to send message to Computer Use.
The input field is on the LEFT side in the chat interface.
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Starting Computer Use interaction...")
    
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
        
        # Wait for page to fully load
        await page.wait_for_timeout(2000)
        
        print("Finding input field on the LEFT side (chat area)...")
        
        # The input is likely a Streamlit text area on the left side
        # Try to find it by role or common Streamlit patterns
        input_field = page.locator('textarea').first
        
        print("Clicking and typing the prompt...")
        await input_field.click()
        await input_field.fill(test_prompt)
        
        print("Submitting the message...")
        await page.keyboard.press("Enter")
        
        print("Message sent! Computer Use should now execute the test.")
        
        # Keep open to observe
        await page.wait_for_timeout(60000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())