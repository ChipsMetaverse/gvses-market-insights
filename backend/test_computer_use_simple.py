#!/usr/bin/env python3
"""
Simple Computer Use Verification
=================================
Uses Anthropic's Computer Use API with Claude to verify UI behavior.
"""

import asyncio
import os
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import json
from datetime import datetime

# Load environment variables
load_dotenv()

class SimpleComputerUseVerifier:
    """Simple Computer Use verification using Playwright and Anthropic's Computer Use API."""
    
    def __init__(self):
        self.client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tunnel_url = "http://localhost:5174"  # Use localhost directly
        self.browser = None
        self.page = None
        self.reports_dir = Path("verification_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    async def setup_browser(self):
        """Initialize Playwright browser."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=["--disable-extensions", "--disable-file-system"]
        )
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1024, "height": 768})
        
    async def take_screenshot(self) -> str:
        """Take screenshot and return as base64."""
        screenshot_bytes = await self.page.screenshot()
        return base64.b64encode(screenshot_bytes).decode("utf-8")
    
    async def handle_action(self, action_type: str, **params):
        """Execute computer action on the page based on Anthropic's format."""
        print(f"  Executing action: {action_type}")
        
        if action_type == "screenshot":
            # Screenshot is handled separately
            print("  Taking screenshot...")
            return await self.take_screenshot()
            
        elif action_type == "click":
            # Anthropic uses coordinate: [x, y]
            coord = params.get("coordinate", [0, 0])
            x, y = coord[0], coord[1]
            print(f"  Clicking at ({x}, {y})")
            await self.page.mouse.click(x, y)
            
        elif action_type == "type":
            text = params.get("text", "")
            print(f"  Typing: '{text}'")
            await self.page.keyboard.type(text)
            
        elif action_type == "key":
            # Single key press
            key = params.get("key", "")
            if key.lower() == "return" or key.lower() == "enter":
                await self.page.keyboard.press("Enter")
            else:
                await self.page.keyboard.press(key)
            print(f"  Pressed key: {key}")
                    
        elif action_type == "scroll":
            coord = params.get("coordinate", [640, 360])
            direction = params.get("direction", "down")
            amount = params.get("amount", 3)
            
            x, y = coord[0], coord[1]
            delta_y = -amount * 100 if direction == "up" else amount * 100
            
            await self.page.mouse.move(x, y)
            await self.page.mouse.wheel(0, delta_y)
            print(f"  Scrolled {direction} by {amount} at ({x}, {y})")
            
        elif action_type == "wait":
            print("  Waiting 2 seconds...")
            await asyncio.sleep(2)
            
        elif action_type == "screenshot":
            print("  Taking screenshot...")
            # Screenshot is taken after each action anyway
            
        else:
            print(f"  Unknown action: {action_type}")
    
    async def verify_scenario(self, scenario_name: str, instructions: str) -> Dict[str, Any]:
        """Run a single verification scenario using Anthropic's Computer Use."""
        print(f"\n{'='*60}")
        print(f"Testing: {scenario_name}")
        print(f"{'='*60}")
        
        results = {
            "scenario": scenario_name,
            "timestamp": datetime.now().isoformat(),
            "status": "running",
            "screenshots": [],
            "actions": [],
            "findings": []
        }
        
        try:
            # Navigate to the app
            print(f"\nNavigating to {self.tunnel_url}...")
            await self.page.goto(self.tunnel_url)
            await asyncio.sleep(3)  # Wait for app to load
            
            # Take initial screenshot
            initial_screenshot = await self.take_screenshot()
            results["screenshots"].append({
                "name": "initial",
                "base64": initial_screenshot[:100] + "..."  # Truncate for storage
            })
            
            # Build the input with trader persona and instructions
            input_text = f"""You are G'sves, a seasoned portfolio manager with 30+ years of experience.
            
{instructions}

Current screenshot shows the trading application interface. Use the computer tool to interact with it."""
            
            # Create initial request to Anthropic Computer Use
            print("\nSending instructions to Anthropic Computer Use...")
            
            messages = [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": input_text
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
            
            response = await self.client.beta.messages.create(
                model="claude-3-7-sonnet-20250219",  # Latest Claude model with Computer Use
                max_tokens=4096,
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
            
            # Process the response loop
            max_iterations = 10
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                print(f"\nIteration {iteration}:")
                
                # Check for tool use in response
                tool_uses = []
                for content in response.content:
                    if content.type == "tool_use":
                        tool_uses.append(content)
                        print(f"Tool use found: {content.name}")
                
                if not tool_uses:
                    # No more tool use, extract final message
                    print("No tool use requested, extracting final response...")
                    for content in response.content:
                        if content.type == "text":
                            findings = content.text
                            results["findings"].append(findings)
                            print(f"\nFindings: {findings[:500]}...")
                    break
                
                # Process tool uses
                tool_results = []
                for tool_use in tool_uses:
                    if tool_use.name == "computer":
                        # Extract action from tool input
                        action_type = tool_use.input.get("action", "")
                        print(f"Computer action requested: {action_type}")
                        results["actions"].append(f"{action_type}: {tool_use.input}")
                        
                        # Execute the action
                        if action_type == "screenshot":
                            screenshot = await self.take_screenshot()
                            tool_results.append({
                                "tool_use_id": tool_use.id,
                                "type": "tool_result",
                                "content": [{
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": screenshot
                                    }
                                }]
                            })
                            results["screenshots"].append({
                                "name": f"iteration_{iteration}",
                                "base64": screenshot[:100] + "..."
                            })
                        else:
                            # Execute other actions (click, type, scroll, etc.)
                            await self.handle_action(action_type, **tool_use.input)
                            await asyncio.sleep(1)  # Allow UI to update
                            
                            # Take screenshot after action
                            screenshot = await self.take_screenshot()
                            tool_results.append({
                                "tool_use_id": tool_use.id,
                                "type": "tool_result",
                                "content": [{
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": screenshot
                                    }
                                }]
                            })
                            results["screenshots"].append({
                                "name": f"after_{action_type}_{iteration}",
                                "base64": screenshot[:100] + "..."
                            })
                
                # If we have tool results, send them back to Claude
                if tool_results:
                    # Add assistant message with tool use to conversation
                    messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Add tool results as user message
                    messages.append({
                        "role": "user",
                        "content": tool_results
                    })
                    
                    # Continue the conversation
                    response = await self.client.beta.messages.create(
                        model="claude-3-7-sonnet-20250219",
                        max_tokens=4096,
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
                else:
                    # No tool results to send back
                    break
            
            results["status"] = "completed"
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            results["status"] = "failed"
            results["error"] = str(e)
        
        # Save report
        report_file = self.reports_dir / f"{scenario_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nReport saved to: {report_file}")
        
        return results
    
    async def run_verification(self):
        """Run all verification scenarios."""
        await self.setup_browser()
        
        scenarios = [
            {
                "name": "PLTR_Company_Info",
                "instructions": """You are testing a trading dashboard application. Please:
1. Find the Voice Assistant panel on the RIGHT side of the screen
2. Look for the text input field in the Voice Assistant panel (it has placeholder "Type a message...")
3. Click on the input field to focus it
4. Type exactly: "What is PLTR?"
5. Press Enter to submit
6. Wait for the response to appear
7. Check if the response explains that PLTR is Palantir Technologies, a data analytics company
8. Check if the chart in the center switched to show PLTR symbol
9. Report what you found - did it show company information or just trading data?"""
            },
            {
                "name": "Chart_Synchronization",
                "instructions": """You are testing chart synchronization. Please:
1. Find the Voice Assistant panel on the RIGHT side of the screen
2. Look for the text input field in the Voice Assistant panel (placeholder: "Type a message...")
3. Click on the input field to focus it
4. Type exactly: "Show me Microsoft"
5. Press Enter to submit
6. Wait for the response and chart update
7. Check if the chart header in the center now shows MSFT
8. Report whether the chart successfully switched to Microsoft"""
            },
            {
                "name": "General_Query",
                "instructions": """You are testing general query handling. Please:
1. Find the Voice Assistant panel on the RIGHT side of the screen
2. Look for the text input field (with placeholder "Type a message...")
3. Click on the input field to focus it
4. Type exactly: "What is artificial intelligence?"
5. Press Enter to submit
6. Wait for the response
7. Check if you get an educational explanation about AI
8. Report if you got a proper AI explanation or trading-related data"""
            }
        ]
        
        all_results = []
        
        for scenario in scenarios:
            result = await self.verify_scenario(
                scenario["name"],
                scenario["instructions"]
            )
            all_results.append(result)
            
            # Brief pause between scenarios
            await asyncio.sleep(2)
        
        # Generate summary
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        
        for result in all_results:
            status_icon = "✅" if result["status"] == "completed" else "❌"
            print(f"\n{status_icon} {result['scenario']}: {result['status']}")
            if result.get("findings"):
                print(f"   Findings: {str(result['findings'][0])[:200]}...")
        
        await self.browser.close()
        
        return all_results

async def main():
    """Main entry point."""
    print("="*60)
    print("COMPUTER USE VERIFICATION (Anthropic)")
    print("="*60)
    
    # Check environment
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not set")
        return
    
    tunnel_url = os.getenv("TUNNEL_URL", "http://localhost:5174")
    print(f"\nTarget URL: {tunnel_url}")
    
    if "localhost" in tunnel_url:
        print("⚠️  Warning: Using localhost URL.")
        print("   Computer Use should still work with localhost.")
    
    # Run verification
    verifier = SimpleComputerUseVerifier()
    await verifier.run_verification()

if __name__ == "__main__":
    asyncio.run(main())