#!/usr/bin/env python3
"""
Test full Computer Use loop with proper action execution
"""
import asyncio
import os
import base64
from openai import AsyncOpenAI
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import json

load_dotenv()

async def execute_action(page, action):
    """Execute a computer_call action on the page."""
    action_type = action.type if hasattr(action, 'type') else action.get('type')
    
    if action_type == 'click':
        x = action.x if hasattr(action, 'x') else action.get('x')
        y = action.y if hasattr(action, 'y') else action.get('y')
        print(f"Clicking at ({x}, {y})")
        await page.mouse.click(x, y)
    elif action_type == 'type':
        text = action.text if hasattr(action, 'text') else action.get('text')
        print(f"Typing: {text}")
        await page.keyboard.type(text)
    elif action_type == 'key' or action_type == 'keypress':
        key = action.key if hasattr(action, 'key') else action.get('key', 'Enter')
        print(f"Pressing key: {key}")
        await page.keyboard.press(key)
    elif action_type == 'wait':
        print("Waiting 2 seconds...")
        await page.wait_for_timeout(2000)
    elif action_type == 'scroll':
        x = action.x if hasattr(action, 'x') else action.get('x', 0)
        y = action.y if hasattr(action, 'y') else action.get('y', 0)
        scroll_y = action.scroll_y if hasattr(action, 'scroll_y') else action.get('scroll_y', 0)
        print(f"Scrolling at ({x}, {y}) by {scroll_y}")
        await page.mouse.move(x, y)
        await page.evaluate(f"window.scrollBy(0, {scroll_y})")
    elif action_type == 'drag':
        print(f"Drag action (not implemented)")
    elif action_type == 'screenshot':
        print("Screenshot requested")
    else:
        print(f"Unknown action type: {action_type}")

async def computer_use_loop():
    """Full Computer Use loop."""
    print("Starting Computer Use loop...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        print("Navigating to localhost:5174...")
        await page.goto("http://localhost:5174", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)
        
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initial screenshot and request
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        response = await client.responses.create(
            model="computer-use-preview",
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """Please test the trading dashboard:
1. Find the query input field (should be in Market Insights panel on the left)
2. Click on it
3. Type: What is PLTR?
4. Press Enter
5. Wait for response and observe what happens"""
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
            truncation="auto",
            reasoning={"summary": "concise"}
        )
        
        # Process responses in a loop
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n=== Iteration {iteration} ===")
            
            # Check for computer_call items in output
            computer_calls = []
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    if hasattr(item, 'type') and item.type == 'computer_call':
                        computer_calls.append(item)
            
            if not computer_calls:
                print("No more computer_call actions")
                # Print final output
                if hasattr(response, 'output'):
                    for item in response.output:
                        if hasattr(item, 'type') and item.type == 'text':
                            print(f"Final response: {item}")
                break
            
            # Execute all computer_call actions
            for call in computer_calls:
                print(f"Executing: {call}")
                if hasattr(call, 'action'):
                    await execute_action(page, call.action)
                await page.wait_for_timeout(1000)  # Wait for UI to update
            
            # Take new screenshot
            screenshot = await page.screenshot()
            screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
            
            # Send screenshot back as computer_call_output
            call_id = computer_calls[0].call_id if hasattr(computer_calls[0], 'call_id') else 'unknown'
            
            response = await client.responses.create(
                model="computer-use-preview",
                previous_response_id=response.id,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1280,
                    "display_height": 800,
                    "environment": "browser"
                }],
                input=[{
                    "call_id": call_id,
                    "type": "computer_call_output",
                    "output": {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{screenshot_b64}"
                    },
                    "current_url": page.url
                }],
                truncation="auto"
            )
        
        print("\n=== Test Complete ===")
        await page.wait_for_timeout(5000)  # Keep browser open to see results
        await browser.close()

if __name__ == "__main__":
    asyncio.run(computer_use_loop())