#!/usr/bin/env python3
"""
Computer Use Browser Adapter
=============================
Adapts Anthropic's Computer Use protocol to work with browser automation via Playwright.
This bridges the gap between Computer Use's desktop-oriented API and browser control.
"""

import asyncio
import base64
import json
from typing import Dict, List, Any, Optional
from anthropic import AsyncAnthropic
from playwright.async_api import async_playwright, Page
from dotenv import load_dotenv
import os

load_dotenv()

class ComputerUseBrowserAdapter:
    """Adapts Computer Use API to control browsers instead of desktop environments."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.page: Optional[Page] = None
        self.playwright = None
        self.browser = None
        
    async def setup_browser(self, headless: bool = False):
        """Initialize browser with Playwright."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=headless)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1024, "height": 768})
        
    async def navigate_to(self, url: str):
        """Navigate to URL and wait for load."""
        await self.page.goto(url)
        await self.page.wait_for_load_state("networkidle")
        
    async def take_screenshot(self) -> str:
        """Take screenshot and return base64 encoded."""
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode("utf-8")
        
    async def execute_action(self, action: str, **params) -> Dict[str, Any]:
        """Execute Computer Use action on the browser."""
        result = {"success": True}
        
        try:
            if action == "screenshot":
                screenshot = await self.take_screenshot()
                result["screenshot"] = screenshot
                
            elif action == "left_click" or action == "click":
                coord = params.get("coordinate", [0, 0])
                await self.page.mouse.click(coord[0], coord[1])
                result["action"] = f"Clicked at ({coord[0]}, {coord[1]})"
                
            elif action == "type":
                text = params.get("text", "")
                await self.page.keyboard.type(text)
                result["action"] = f"Typed: {text}"
                
            elif action == "key":
                key = params.get("key", "")
                if key.lower() in ["return", "enter"]:
                    await self.page.keyboard.press("Enter")
                else:
                    await self.page.keyboard.press(key)
                result["action"] = f"Pressed key: {key}"
                
            elif action == "scroll":
                coord = params.get("coordinate", [512, 384])
                direction = params.get("direction", "down")
                amount = params.get("amount", 3)
                
                delta_y = -amount * 100 if direction == "up" else amount * 100
                await self.page.mouse.move(coord[0], coord[1])
                await self.page.mouse.wheel(0, delta_y)
                result["action"] = f"Scrolled {direction} by {amount}"
                
            elif action == "wait":
                duration = params.get("duration", 2)
                await asyncio.sleep(duration)
                result["action"] = f"Waited {duration} seconds"
                
            else:
                result["success"] = False
                result["error"] = f"Unknown action: {action}"
                
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)
            
        return result
        
    async def process_tool_calls(self, response) -> List[Dict[str, Any]]:
        """Process tool calls from Claude's response."""
        tool_results = []
        
        for content in response.content:
            if content.type == "tool_use" and content.name == "computer":
                action = content.input.get("action")
                print(f"Processing action: {action}")
                
                # Execute the action
                result = await self.execute_action(action, **content.input)
                
                # Format tool result for Claude
                if action == "screenshot":
                    # Return screenshot as image
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": [{
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": result.get("screenshot", "")
                            }
                        }]
                    }
                else:
                    # Return action result as text
                    tool_result = {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": json.dumps(result),
                        "is_error": not result.get("success", True)
                    }
                    
                tool_results.append(tool_result)
                
        return tool_results
        
    async def run_task(self, task_description: str, url: str = "http://localhost:5174", max_iterations: int = 10):
        """Run a complete task using Computer Use protocol."""
        print(f"Starting task: {task_description}")
        
        # Setup browser and navigate
        await self.setup_browser(headless=False)
        await self.navigate_to(url)
        await asyncio.sleep(2)  # Let page fully load
        
        # Take initial screenshot
        initial_screenshot = await self.take_screenshot()
        
        # Initialize conversation with task
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Task: {task_description}\n\nI'll help you interact with the application shown in the screenshot."
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": initial_screenshot
                    }
                }
            ]
        }]
        
        # Computer Use tool definition
        tools = [{
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
            "display_number": 1
        }]
        
        # Agent loop
        for iteration in range(max_iterations):
            print(f"\n--- Iteration {iteration + 1} ---")
            
            # Call Claude with tools
            response = await self.client.beta.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=messages,
                tools=tools,
                betas=["computer-use-2025-01-24"]
            )
            
            # Add Claude's response to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Process tool calls
            tool_results = await self.process_tool_calls(response)
            
            if not tool_results:
                # No more tools needed, task complete
                print("\nTask complete!")
                for content in response.content:
                    if content.type == "text":
                        print(f"Final response: {content.text}")
                break
                
            # Add tool results to conversation
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Add delay for UI updates
            await asyncio.sleep(0.5)
            
        # Keep browser open to see results
        print("\nKeeping browser open for 10 seconds...")
        await asyncio.sleep(10)
        
    async def cleanup(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    """Test Computer Use browser adapter."""
    adapter = ComputerUseBrowserAdapter()
    
    try:
        # Test task: Click on Voice Assistant and type a message
        await adapter.run_task(
            task_description="""
            Find the Voice Assistant panel on the RIGHT side of the trading application.
            Click on the text input field (it has placeholder "Type a message...").
            Type "What is PLTR?" and press Enter.
            Wait for the response to appear.
            Report what information was provided about PLTR.
            """,
            url="http://localhost:5174"
        )
        
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    print("=" * 60)
    print("COMPUTER USE BROWSER ADAPTER TEST")
    print("=" * 60)
    asyncio.run(main())