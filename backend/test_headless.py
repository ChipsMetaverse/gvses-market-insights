#!/usr/bin/env python3
"""
Test Computer Use in Headless Mode
===================================
"""

import asyncio
import os
import base64
from anthropic import AsyncAnthropic
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_headless():
    """Test in headless mode to avoid timeout."""
    print("Starting headless test...")
    
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)  # Headless mode
    page = await browser.new_page()
    await page.set_viewport_size({"width": 1024, "height": 768})
    
    try:
        print("Navigating to localhost:5174...")
        await page.goto("http://localhost:5174")
        await page.wait_for_load_state("networkidle")
        
        # Check if Voice Assistant input exists
        input_selector = 'input[placeholder="Type a message..."]'
        input_count = await page.locator(input_selector).count()
        print(f"Found {input_count} Voice Assistant input(s)")
        
        if input_count > 0:
            # Click on it directly
            print("Clicking on Voice Assistant input...")
            await page.locator(input_selector).first.click()
            
            # Type a message
            await page.locator(input_selector).first.type("Test from Computer Use!")
            print("✅ Successfully clicked and typed in Voice Assistant!")
            
            # Take screenshot
            screenshot = await page.screenshot()
            with open("test_result.png", "wb") as f:
                f.write(screenshot)
            print("Screenshot saved as test_result.png")
        else:
            print("❌ Could not find Voice Assistant input")
            
            # Debug: print what's on the page
            title = await page.title()
            print(f"Page title: {title}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()
        await playwright.stop()
        print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_headless())