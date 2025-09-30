#!/usr/bin/env python3
"""
OpenAI Computer Use Implementation - Following computeruse.md specification
Uses the Responses API with computer-use-preview model
"""

import os
import asyncio
import base64
import time
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from playwright.async_api import async_playwright, Page


class OpenAIComputerUse:
    """
    Implements OpenAI Computer Use following the official specification.
    Uses Responses API with computer-use-preview model.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.playwright = None
        self.browser = None
        self.page: Optional[Page] = None
        self.display_width = 1024
        self.display_height = 768
        
    async def setup_browser(self):
        """Initialize Playwright browser with security settings."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Show browser for demo
            chromium_sandbox=True,  # Enable sandbox for security
            env={},  # Empty env to avoid exposing host variables
            args=[
                "--disable-extensions",
                "--disable-file-system"
            ],
            slow_mo=500  # Slow down for visibility
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({
            "width": self.display_width, 
            "height": self.display_height
        })
        print("✅ Browser initialized with security settings")
        
    async def get_screenshot(self) -> bytes:
        """Take a screenshot and return raw bytes."""
        if not self.page:
            raise RuntimeError("Browser not initialized")
        return await self.page.screenshot()
    
    async def handle_model_action(self, action: Any):
        """
        Execute computer actions following the specification.
        Handles: click, scroll, keypress, type, wait, screenshot
        """
        if not self.page:
            raise RuntimeError("Browser not initialized")
            
        # Handle both dict and object forms
        if isinstance(action, dict):
            action_type = action.get("type", "")
        else:
            action_type = action.type if hasattr(action, 'type') else ""
        
        try:
            match action_type:
                case "click":
                    if isinstance(action, dict):
                        x = action.get("x", 0)
                        y = action.get("y", 0)
                        button = action.get("button", "left")
                    else:
                        x = action.x if hasattr(action, 'x') else 0
                        y = action.y if hasattr(action, 'y') else 0
                        button = action.button if hasattr(action, 'button') else "left"
                    print(f"   🖱️ Click at ({x}, {y}) with {button} button")
                    if button not in ["left", "right"]:
                        button = "left"
                    await self.page.mouse.click(x, y, button=button)
                    
                case "scroll":
                    if isinstance(action, dict):
                        x = action.get("x", 0)
                        y = action.get("y", 0)
                        scroll_x = action.get("scrollX", action.get("scroll_x", 0))
                        scroll_y = action.get("scrollY", action.get("scroll_y", 0))
                    else:
                        x = action.x if hasattr(action, 'x') else 0
                        y = action.y if hasattr(action, 'y') else 0
                        scroll_x = action.scroll_x if hasattr(action, 'scroll_x') else 0
                        scroll_y = action.scroll_y if hasattr(action, 'scroll_y') else 0
                    print(f"   📜 Scroll at ({x}, {y}) by ({scroll_x}, {scroll_y})")
                    await self.page.mouse.move(x, y)
                    await self.page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")
                    
                case "keypress":
                    if isinstance(action, dict):
                        keys = action.get("keys", [])
                    else:
                        keys = action.keys if hasattr(action, 'keys') else []
                    for key in keys:
                        print(f"   ⌨️ Keypress: {key}")
                        if "ENTER" in key.upper():
                            await self.page.keyboard.press("Enter")
                        elif "SPACE" in key.upper():
                            await self.page.keyboard.press(" ")
                        else:
                            await self.page.keyboard.press(key)
                            
                case "type":
                    if isinstance(action, dict):
                        text = action.get("text", "")
                    else:
                        text = action.text if hasattr(action, 'text') else ""
                    print(f"   ⌨️ Type: {text}")
                    await self.page.keyboard.type(text)
                    
                case "wait":
                    print(f"   ⏳ Wait 2 seconds")
                    await asyncio.sleep(2)
                    
                case "screenshot":
                    print(f"   📸 Screenshot requested")
                    # Screenshot is taken after each action anyway
                    
                case _:
                    print(f"   ❓ Unrecognized action: {action_type}")
                    
        except Exception as e:
            print(f"   ❌ Error handling action {action_type}: {e}")
    
    async def computer_use_loop(self, initial_response):
        """
        Main CUA loop following the specification:
        1. Check for computer_call in response
        2. Execute action
        3. Take screenshot
        4. Send back as computer_call_output
        5. Repeat
        """
        response = initial_response
        iteration = 0
        
        while True:
            iteration += 1
            print(f"\n🔄 Loop iteration {iteration}")
            
            # Check for computer_call items
            computer_calls = [
                item for item in response.output 
                if hasattr(item, 'type') and item.type == "computer_call"
            ]
            
            if not computer_calls:
                print("✅ No more computer calls. Task complete!")
                # Display final output
                for item in response.output:
                    if hasattr(item, 'type') and item.type == "message":
                        content = item.content if hasattr(item, 'content') else ""
                        print(f"\n📝 Final message: {content}")
                break
            
            # Process first computer_call (spec expects at most one)
            computer_call = computer_calls[0]
            call_id = computer_call.call_id if hasattr(computer_call, 'call_id') else None
            action = computer_call.action if hasattr(computer_call, 'action') else {}
            
            # Check for pending safety checks
            pending_checks = []
            if hasattr(computer_call, 'pending_safety_checks'):
                pending_checks = computer_call.pending_safety_checks or []
            if pending_checks:
                print("⚠️ Safety checks detected:")
                for check in pending_checks:
                    code = check.code if hasattr(check, 'code') else 'unknown'
                    msg = check.message if hasattr(check, 'message') else ''
                    print(f"   - {code}: {msg}")
                # In production, get user confirmation here
            
            # Execute the action
            action_type = action.type if hasattr(action, 'type') else 'unknown'
            print(f"🎯 Executing action: {action_type}")
            await self.handle_model_action(action)
            
            # Allow time for changes to take effect
            await asyncio.sleep(1)
            
            # Take screenshot after action
            screenshot_bytes = await self.get_screenshot()
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            print("📸 Screenshot captured")
            
            # Get current URL if available
            current_url = None
            try:
                current_url = self.page.url
            except:
                pass
            
            # Send screenshot back as computer_call_output
            print("📤 Sending screenshot back to model...")
            
            # Build the input for next request
            call_output = {
                "call_id": call_id,
                "type": "computer_call_output",
                "output": {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{screenshot_base64}"
                }
            }
            
            # Add acknowledged safety checks if there were any
            if pending_checks:
                call_output["acknowledged_safety_checks"] = pending_checks
            
            # Add current URL for better safety checks
            if current_url:
                call_output["current_url"] = current_url
            
            # Continue the conversation
            response = await self.client.responses.create(
                model="computer-use-preview",
                previous_response_id=response.id,  # Link to previous response
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": self.display_width,
                    "display_height": self.display_height,
                    "environment": "browser"
                }],
                input=[call_output],
                truncation="auto"
            )
        
        return response
    
    async def test_trading_app(self):
        """
        Test the trading application using Computer Use.
        """
        print("=" * 70)
        print("🤖 OPENAI COMPUTER USE - TRADING APP TEST")
        print("Following computeruse.md specification")
        print("=" * 70)
        
        # Setup browser
        print("\n1️⃣ Setting up browser environment...")
        await self.setup_browser()
        
        # Navigate to app initially
        print("\n2️⃣ Loading trading application...")
        await self.page.goto("http://localhost:5174")
        await asyncio.sleep(3)
        
        # Take initial screenshot
        initial_screenshot = await self.get_screenshot()
        initial_screenshot_base64 = base64.b64encode(initial_screenshot).decode("utf-8")
        print("📸 Initial screenshot captured")
        
        # Create initial request with computer tool
        print("\n3️⃣ Sending initial request to Computer Use model...")
        
        initial_response = await self.client.responses.create(
            model="computer-use-preview",
            tools=[{
                "type": "computer_use_preview",
                "display_width": self.display_width,
                "display_height": self.display_height,
                "environment": "browser"
            }],
            input=[{
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": """You are looking at a trading application dashboard. 
                        Please test the ML pattern detection feature by:
                        1. Find the Voice Assistant panel on the right side
                        2. Click on the message input field
                        3. Type "Show me patterns for TSLA"
                        4. Press Enter to submit
                        5. Wait for the response
                        6. Report what patterns were detected and the current TSLA price"""
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{initial_screenshot_base64}"
                    }
                ]
            }],
            reasoning={
                "summary": "concise"  # Show concise reasoning
            },
            truncation="auto"  # Required for computer use
        )
        
        print("✅ Initial response received")
        
        # Show reasoning if present
        for item in initial_response.output:
            if hasattr(item, 'type') and item.type == "reasoning":
                if hasattr(item, 'summary'):
                    for s in item.summary:
                        if hasattr(s, 'type') and s.type == "summary_text":
                            print(f"🤔 Model reasoning: {s.text}")
        
        # Run the computer use loop
        print("\n4️⃣ Starting Computer Use action loop...")
        final_response = await self.computer_use_loop(initial_response)
        
        # Save final screenshot
        print("\n5️⃣ Saving final screenshot...")
        await self.page.screenshot(path="openai_cua_final.png")
        print("📸 Final screenshot saved: openai_cua_final.png")
        
        # Keep browser open for inspection
        print("\n⏸️ Browser will remain open for 10 seconds...")
        await asyncio.sleep(10)
        
        # Cleanup
        await self.browser.close()
        await self.playwright.stop()
        
        print("\n✅ Computer Use test completed!")
        return final_response


async def main():
    """Main execution function."""
    
    # Check prerequisites
    print("🔍 Checking prerequisites...")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set!")
        print("   Set it with: export OPENAI_API_KEY=sk-...")
        return
    
    print("✅ OpenAI API key found")
    
    # Check if app is running
    import requests
    try:
        response = requests.get("http://localhost:5174", timeout=2)
        print("✅ Trading app is accessible")
    except:
        print("⚠️ Trading app may not be running on port 5174")
        print("   Start it with: cd frontend && npm run dev")
    
    # Run the test
    print("\n🚀 Starting Computer Use test...")
    print("   This follows the official OpenAI Computer Use specification")
    print("   Using: Responses API with computer-use-preview model")
    
    cua = OpenAIComputerUse()
    
    try:
        await cua.test_trading_app()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
        # Try cleanup
        try:
            if cua.browser:
                await cua.browser.close()
            if cua.playwright:
                await cua.playwright.stop()
        except:
            pass


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("OpenAI Computer Use - Correct Implementation")
    print("Following computeruse.md specification exactly")
    print("=" * 70)
    
    asyncio.run(main())