#!/usr/bin/env python3
"""
Debug Computer Use to see what's actually happening
"""
import asyncio
import os
import base64
from openai import AsyncOpenAI
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json

load_dotenv()

async def test_browser():
    """Test that browser actually launches and navigates."""
    print("Testing browser launch...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        print("Navigating to localhost:5174...")
        await page.goto("http://localhost:5174", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        print("Taking screenshot...")
        screenshot = await page.screenshot()
        print(f"Screenshot size: {len(screenshot)} bytes")
        
        # Test computer use API
        print("\nTesting Computer Use API...")
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        response = await client.responses.create(
            model="computer-use-preview",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Look at this trading dashboard. Click on the query input field and type 'What is PLTR?'"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_b64}"
                    }
                ]
            }],
            tools=[{
                "type": "computer_use_preview",
                "display_width": 1280,
                "display_height": 800,
                "environment": "browser"
            }],
            truncation="auto"
        )
        
        print(f"\nResponse ID: {response.id}")
        print(f"Response output: {response.output}")
        
        # Check for computer_call items
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if hasattr(item, 'type'):
                    print(f"Output item type: {item.type}")
                    if item.type == "computer_call":
                        print(f"Computer call action: {item.action}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_browser())