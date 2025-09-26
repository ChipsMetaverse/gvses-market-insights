#!/usr/bin/env python3
"""
Minimal Computer Use Browser Test
==================================
Simple test to verify Anthropic Computer Use can control the browser.
"""

import asyncio
import os
import base64
from anthropic import AsyncAnthropic
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_minimal_computer_use():
    """Run a minimal Computer Use test with browser."""
    client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    # Setup browser
    print("Setting up browser...")
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.set_viewport_size({"width": 1024, "height": 768})
    
    try:
        # Navigate directly to localhost
        url = "http://localhost:5174"
        print(f"Navigating to {url}...")
        await page.goto(url)
        await asyncio.sleep(3)  # Wait for load
        
        # Take screenshot
        screenshot_bytes = await page.screenshot()
        screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
        print(f"Screenshot taken: {len(screenshot)} chars")
        
        # Ask Claude to describe what it sees
        print("\nAsking Claude to analyze the screen...")
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
                        "text": """Look at this trading application screen. 
                        Can you see the Voice Assistant panel on the RIGHT side? 
                        Please click on the text input field in the Voice Assistant panel.
                        The input field has placeholder text "Type a message..."
                        Use the computer tool to click on it."""
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
        
        # Check response
        print(f"\nResponse stop_reason: {response.stop_reason}")
        print(f"Response content blocks: {len(response.content)}")
        
        # Process tool use in a loop
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Look at this trading application screen. 
                    Can you see the Voice Assistant panel on the RIGHT side? 
                    Please click on the text input field in the Voice Assistant panel.
                    The input field has placeholder text "Type a message..."
                    Use the computer tool to click on it."""
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
        
        max_iterations = 5
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Look for tool use in response
            tool_used = False
            for content in response.content:
                if content.type == "tool_use" and content.name == "computer":
                    tool_used = True
                    action = content.input.get("action")
                    print(f"Tool action requested: {action}")
                    
                    # Handle the action
                    if action == "screenshot":
                        # Take screenshot
                        screenshot_bytes = await page.screenshot()
                        new_screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
                        print("Screenshot taken")
                        
                        # Send tool result back
                        messages.append({
                            "role": "assistant",
                            "content": response.content
                        })
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": [{
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": new_screenshot
                                    }
                                }]
                            }]
                        })
                        
                    elif action == "click":
                        coord = content.input.get("coordinate", [0, 0])
                        print(f"Clicking at {coord}")
                        await page.mouse.click(coord[0], coord[1])
                        await asyncio.sleep(1)
                        
                        # Take screenshot after click
                        screenshot_bytes = await page.screenshot()
                        new_screenshot = base64.b64encode(screenshot_bytes).decode("utf-8")
                        
                        # Send result
                        messages.append({
                            "role": "assistant",
                            "content": response.content
                        })
                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": [{
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": new_screenshot
                                    }
                                }]
                            }]
                        })
                        print("Click executed and screenshot taken")
                        
            if not tool_used:
                # No tool use, we're done
                print("\nNo more tool actions requested.")
                for content in response.content:
                    if content.type == "text":
                        print(f"Final response: {content.text[:300]}...")
                break
                
            # Continue conversation
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
                messages=messages
            )
        
        print("\n✅ Test completed! Check if the input was clicked.")
        await asyncio.sleep(5)  # Keep browser open to see result
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(test_minimal_computer_use())