#!/usr/bin/env python3
"""
Test Computer Use Click Action
===============================
Simple test to verify clicking works.
"""

import asyncio
import os
import base64
from anthropic import AsyncAnthropic
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def test_click():
    """Test a simple click action."""
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Setup browser
    print("Opening browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.set_viewport_size({"width": 1024, "height": 768})
    
    try:
        # Navigate
        print("Navigating to localhost:5174...")
        await page.goto("http://localhost:5174")
        await asyncio.sleep(2)
        
        # Take screenshot
        screenshot_bytes = await page.screenshot()
        screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
        print("Screenshot taken")
        
        # Ask Claude to click on Voice Assistant input
        print("\nAsking Claude to click on Voice Assistant input...")
        response = await client.beta.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1024,
            tools=[{
                "type": "computer_20250124",
                "name": "computer",
                "display_width_px": 1024,
                "display_height_px": 768,
                "display_number": 1
            }],
            betas=["computer-use-2025-01-24"],
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please click on the Voice Assistant text input field on the RIGHT side of the screen. It has placeholder text 'Type a message...'"
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot
                        }
                    }
                ]
            }]
        )
        
        # Process response
        print(f"Stop reason: {response.stop_reason}")
        
        # Execute first tool use
        for content in response.content:
            if content.type == "tool_use":
                action = content.input.get("action")
                print(f"Action: {action}")
                
                if action == "click":
                    coord = content.input.get("coordinate", [0, 0])
                    print(f"Clicking at {coord}")
                    await page.mouse.click(coord[0], coord[1])
                    print("✅ Click executed!")
                    
                    # Type something to verify it worked
                    await asyncio.sleep(1)
                    await page.keyboard.type("Test message from Computer Use!")
                    print("✅ Text typed!")
                    break
                    
                elif action == "screenshot":
                    print("Claude wants a screenshot first")
                    # We already provided one, so this is unexpected
                    
        print("\nKeeping browser open for 5 seconds...")
        await asyncio.sleep(5)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(test_click())