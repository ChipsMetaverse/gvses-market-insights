#!/usr/bin/env python3
"""
Browser Debug Tool - Computer Use Integration for Web Testing

This tool specifically focuses on browser-based debugging using Playwright + Computer Use.
It can interact with your running web application and help debug issues.

Usage:
    python browser_debug_tool.py --url http://localhost:5174 --debug "query not working"
    python browser_debug_tool.py --test-flow "test agent queries"
    python browser_debug_tool.py --monitor-app http://localhost:5174
"""

import os
import sys
import time
import base64
import argparse
import asyncio
from typing import Optional, Dict, Any, List
from openai import OpenAI
from playwright.async_api import async_playwright

class BrowserDebugTool:
    def __init__(self):
        self.client = OpenAI()
        self.model = "computer-use-preview"
        self.page = None
        self.browser = None
        
    async def setup_browser(self, url: str):
        """Set up Playwright browser instance."""
        playwright = await async_playwright().start()
        
        # Launch browser with debugging-friendly settings
        self.browser = await playwright.chromium.launch(
            headless=False,  # Visible for debugging
            chromium_sandbox=True,
            env={},
            args=[
                "--disable-extensions",
                "--disable-file-system",
                "--disable-web-security",  # For local development
                "--allow-running-insecure-content"
            ]
        )
        
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1280, "height": 720})
        
        # Navigate to the application
        print(f"Navigating to {url}")
        await self.page.goto(url)
        await self.page.wait_for_timeout(2000)  # Wait for page load
        
    async def take_screenshot(self) -> bytes:
        """Take a screenshot of the current page."""
        if not self.page:
            return b""
        return await self.page.screenshot(full_page=True)
    
    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information."""
        if not self.page:
            return {}
        
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "console_messages": [],  # We'll collect these separately
        }
    
    async def analyze_with_computer_use(self, screenshot_bytes: bytes, context: str, page_info: Dict) -> Dict[str, Any]:
        """Analyze screenshot using Computer Use model."""
        if not screenshot_bytes:
            return {"error": "No screenshot data"}
        
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        prompt = f"""I'm debugging a web application issue: {context}

Current page info:
- URL: {page_info.get('url', 'unknown')}
- Title: {page_info.get('title', 'unknown')}

Please analyze this browser screenshot and help me understand:
1. What's the current state of the web application?
2. Are there any visible errors, loading states, or UI issues?
3. What interactive elements are available (buttons, forms, inputs)?
4. Any console errors or network issues visible?
5. Suggestions for testing or debugging this specific issue?

Focus on web application debugging and user interface analysis."""
        
        try:
            response = self.client.responses.create(
                model=self.model,
                tools=[{
                    "type": "computer_use_preview",
                    "display_width": 1280,
                    "display_height": 720,
                    "environment": "browser"
                }],
                input=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot_base64}"
                        }
                    ]
                }],
                reasoning={
                    "summary": "detailed"
                },
                truncation="auto"
            )
            
            return {
                "success": True,
                "analysis": response.output,
                "page_info": page_info
            }
            
        except Exception as e:
            return {
                "error": f"Failed to analyze: {e}",
                "page_info": page_info
            }
    
    async def test_agent_query(self, query: str) -> Dict[str, Any]:
        """Test a specific agent query and analyze the results."""
        if not self.page:
            return {"error": "Browser not initialized"}
        
        print(f"Testing query: '{query}'")
        
        try:
            # Look for input field (adjust selector based on your app)
            input_selectors = [
                'input[type="text"]',
                'textarea',
                '[data-testid="query-input"]',
                '.query-input',
                '#query-input'
            ]
            
            input_element = None
            for selector in input_selectors:
                try:
                    input_element = await self.page.wait_for_selector(selector, timeout=2000)
                    if input_element:
                        break
                except:
                    continue
            
            if not input_element:
                return {"error": "Could not find input field for query"}
            
            # Clear and type the query
            await input_element.clear()
            await input_element.type(query)
            
            # Look for submit button
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Send")',
                'button:has-text("Submit")',
                '[data-testid="submit-button"]'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = await self.page.wait_for_selector(selector, timeout=1000)
                    if submit_button:
                        await submit_button.click()
                        break
                except:
                    continue
            else:
                # Try pressing Enter
                await input_element.press('Enter')
            
            # Wait for response
            await self.page.wait_for_timeout(3000)
            
            # Take screenshot of result
            screenshot = await self.take_screenshot()
            page_info = await self.get_page_info()
            
            # Analyze the result
            analysis = await self.analyze_with_computer_use(
                screenshot, 
                f"testing agent query '{query}' - analyze the response and any issues",
                page_info
            )
            
            return {
                "success": True,
                "query": query,
                "analysis": analysis
            }
            
        except Exception as e:
            return {"error": f"Failed to test query: {e}"}
    
    async def monitor_application(self, url: str, interval: int = 15):
        """Monitor the application continuously."""
        await self.setup_browser(url)
        
        print(f"Monitoring application at {url} (screenshot every {interval} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print(f"\n{'='*60}")
                print(f"Monitoring at {time.strftime('%H:%M:%S')}")
                
                screenshot = await self.take_screenshot()
                page_info = await self.get_page_info()
                
                if screenshot:
                    result = await self.analyze_with_computer_use(
                        screenshot, 
                        "monitoring application state for any issues or changes",
                        page_info
                    )
                    
                    if result.get("success"):
                        print(f"Current URL: {page_info.get('url')}")
                        print("Analysis:")
                        for item in result["analysis"]:
                            if item.get("type") == "text":
                                print(item.get("text", ""))
                    else:
                        print(f"Error: {result.get('error')}")
                else:
                    print("Failed to take screenshot")
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
        finally:
            if self.browser:
                await self.browser.close()
    
    async def debug_specific_issue(self, url: str, issue_description: str):
        """Debug a specific issue with the application."""
        await self.setup_browser(url)
        
        print(f"Debugging issue: {issue_description}")
        print(f"Application URL: {url}")
        
        try:
            # Take initial screenshot
            screenshot = await self.take_screenshot()
            page_info = await self.get_page_info()
            
            result = await self.analyze_with_computer_use(
                screenshot, 
                issue_description,
                page_info
            )
            
            if result.get("success"):
                print("\n" + "="*60)
                print("DEBUGGING ANALYSIS")
                print("="*60)
                print(f"URL: {page_info.get('url')}")
                print(f"Title: {page_info.get('title')}")
                print()
                
                for item in result["analysis"]:
                    if item.get("type") == "text":
                        print(item.get("text", ""))
                    elif item.get("type") == "reasoning":
                        print("\nDetailed Reasoning:")
                        for summary_item in item.get("summary", []):
                            if summary_item.get("type") == "summary_text":
                                print(f"  - {summary_item.get('text')}")
            else:
                print(f"Error analyzing application: {result.get('error')}")
                
        finally:
            if self.browser:
                await self.browser.close()

async def main():
    parser = argparse.ArgumentParser(description="Browser Debug Tool using Computer Use")
    parser.add_argument("--url", type=str, default="http://localhost:5174",
                       help="URL of the application to debug")
    parser.add_argument("--debug", type=str, metavar="ISSUE",
                       help="Debug specific issue (e.g., 'agent queries not working')")
    parser.add_argument("--test-query", type=str, metavar="QUERY",
                       help="Test a specific agent query")
    parser.add_argument("--monitor-app", action="store_true",
                       help="Monitor application continuously")
    parser.add_argument("--interval", type=int, default=15,
                       help="Monitoring interval in seconds")
    
    args = parser.parse_args()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    tool = BrowserDebugTool()
    
    try:
        if args.debug:
            await tool.debug_specific_issue(args.url, args.debug)
        elif args.test_query:
            await tool.setup_browser(args.url)
            result = await tool.test_agent_query(args.test_query)
            if result.get("success"):
                print("Query test completed successfully")
            else:
                print(f"Query test failed: {result.get('error')}")
        elif args.monitor_app:
            await tool.monitor_application(args.url, args.interval)
        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if tool.browser:
            await tool.browser.close()

if __name__ == "__main__":
    asyncio.run(main())
