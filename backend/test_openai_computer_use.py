#!/usr/bin/env python3
"""
Test Trading App with OpenAI Computer Use
Uses the OpenAI API with Playwright to control browser and test the application
"""

import os
import asyncio
import json
from datetime import datetime
from openai import AsyncOpenAI
from playwright.async_api import async_playwright
import base64

class OpenAIComputerUseTester:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.browser = None
        self.page = None
        
    async def setup_browser(self):
        """Initialize Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Show browser for visual feedback
            slow_mo=500  # Slow down actions for visibility
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
    async def take_screenshot(self) -> str:
        """Take a screenshot and return base64 encoded."""
        screenshot = await self.page.screenshot()
        return base64.b64encode(screenshot).decode('utf-8')
    
    async def execute_action(self, action_type: str, **params):
        """Execute browser actions."""
        if action_type == "navigate":
            await self.page.goto(params.get("url"), wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)
        elif action_type == "click":
            x, y = params.get("x", 0), params.get("y", 0)
            await self.page.mouse.click(x, y)
        elif action_type == "type":
            text = params.get("text", "")
            await self.page.keyboard.type(text)
        elif action_type == "key":
            key = params.get("key", "Enter")
            await self.page.keyboard.press(key)
        elif action_type == "wait":
            ms = params.get("ms", 2000)
            await self.page.wait_for_timeout(ms)
        elif action_type == "screenshot":
            return await self.take_screenshot()
            
    async def get_ai_instructions(self, screenshot: str, task: str):
        """Get next action from OpenAI based on screenshot."""
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """You are testing a trading application. Analyze the screenshot and provide the next action.
                    Return a JSON object with:
                    - action: "navigate", "click", "type", "key", "wait", or "done"
                    - params: parameters for the action
                    - description: what you're doing
                    - observation: what you see in the screenshot"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Task: {task}\n\nWhat should I do next?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot}"
                            }
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        
        return json.loads(response.choices[0].message.content)
    
    async def test_trading_app(self):
        """Main test sequence for trading application."""
        print("=" * 70)
        print("🤖 OPENAI COMPUTER USE - TRADING APP TEST")
        print("=" * 70)
        
        # Setup browser
        print("\n1️⃣ Setting up browser...")
        await self.setup_browser()
        print("   ✅ Browser launched")
        
        # Navigate to app
        print("\n2️⃣ Navigating to trading app...")
        await self.execute_action("navigate", url="http://localhost:5174")
        print("   ✅ Loaded http://localhost:5174")
        
        # Take initial screenshot
        print("\n3️⃣ Taking initial screenshot...")
        screenshot = await self.take_screenshot()
        print("   ✅ Screenshot captured")
        
        # Test sequence
        test_steps = [
            "Find the Voice Assistant panel on the right side",
            "Click on the message input field",
            "Type 'Show me TSLA patterns'",
            "Press Enter to submit",
            "Wait for response and analyze results"
        ]
        
        print("\n4️⃣ Executing test sequence...")
        for i, step in enumerate(test_steps, 1):
            print(f"\n   Step {i}: {step}")
            
            # Get AI instructions
            ai_response = await self.get_ai_instructions(screenshot, step)
            
            print(f"   🤖 AI says: {ai_response.get('description', 'Processing...')}")
            print(f"   👁️ Observation: {ai_response.get('observation', 'Analyzing...')}")
            
            action = ai_response.get("action")
            params = ai_response.get("params", {})
            
            if action == "done":
                print("   ✅ Step completed")
                continue
            elif action == "navigate":
                await self.execute_action("navigate", **params)
            elif action == "click":
                # Find element coordinates if needed
                if "selector" in params:
                    element = await self.page.query_selector(params["selector"])
                    if element:
                        box = await element.bounding_box()
                        if box:
                            await self.page.mouse.click(box['x'] + box['width']/2, 
                                                      box['y'] + box['height']/2)
                else:
                    await self.execute_action("click", **params)
            elif action == "type":
                await self.execute_action("type", **params)
            elif action == "key":
                await self.execute_action("key", **params)
            elif action == "wait":
                await self.execute_action("wait", **params)
            
            # Take new screenshot after action
            await self.page.wait_for_timeout(2000)
            screenshot = await self.take_screenshot()
        
        # Final analysis
        print("\n5️⃣ Final analysis...")
        final_analysis = await self.get_ai_instructions(
            screenshot, 
            "Analyze the final state. What patterns were detected? What is the TSLA price and technical levels?"
        )
        
        print("\n📊 Final Results:")
        print(f"   {final_analysis.get('observation', 'No observation')}")
        
        # Save final screenshot
        await self.page.screenshot(path="openai_test_final.png")
        print("\n   📸 Final screenshot saved: openai_test_final.png")
        
        # Keep browser open for inspection
        print("\n⏸️  Browser will remain open for 10 seconds...")
        await self.page.wait_for_timeout(10000)
        
        # Cleanup
        await self.browser.close()
        await self.playwright.stop()
        
        print("\n✅ Test completed!")

async def main():
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY=your_key")
        return
    
    # Check if app is running
    import requests
    try:
        response = requests.get("http://localhost:5174", timeout=2)
        if response.status_code != 200:
            print("⚠️ Trading app may not be fully loaded")
    except:
        print("❌ Trading app not running on port 5174")
        print("   Start it with: cd frontend && npm run dev")
        return
    
    print("✅ Prerequisites checked")
    print("   - OpenAI API key: Set")
    print("   - Trading app: Running")
    
    # Run test
    tester = OpenAIComputerUseTester()
    await tester.test_trading_app()

if __name__ == "__main__":
    asyncio.run(main())