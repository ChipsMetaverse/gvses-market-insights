#!/usr/bin/env python3
"""
Real Trader Workflow Test
Tests the actual user experience a trader would have
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright

class TraderWorkflowTest:
    def __init__(self):
        self.browser = None
        self.page = None
        self.test_results = []
    
    async def setup(self):
        """Setup browser with realistic viewport"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=500)
        self.page = await self.browser.new_page()
        await self.page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Monitor console for errors
        self.page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        self.page.on("pageerror", lambda error: print(f"ERROR: {error}"))
    
    async def test_trader_scenario_1(self):
        """Test: Trader wants to check AAPL price and get analysis"""
        print("\n🏦 TRADER SCENARIO 1: Check AAPL price and analysis")
        
        # Navigate to app
        await self.page.goto("http://localhost:5174")
        await self.page.wait_for_load_state("networkidle")
        
        # Take screenshot of initial state
        await self.page.screenshot(path="trader_test_initial.png", full_page=True)
        print("📸 Initial state captured")
        
        # Look for the ChatKit interface
        print("🔍 Looking for ChatKit chat interface...")
        
        # Try to find chat input field
        chat_selectors = [
            ".chart-agent-chat input",
            "[data-testid*='chat'] input", 
            ".chat-input",
            "input[type='text']",
            "textarea"
        ]
        
        chat_input = None
        for selector in chat_selectors:
            try:
                chat_input = await self.page.wait_for_selector(selector, timeout=3000)
                if chat_input:
                    print(f"✅ Found chat input with selector: {selector}")
                    break
            except:
                continue
        
        if not chat_input:
            print("❌ No chat input field found!")
            await self.page.screenshot(path="trader_test_no_input.png", full_page=True)
            return False
        
        # Try typing a message like a trader would
        print("💬 Typing trader query: 'What's the current price of AAPL?'")
        await chat_input.fill("What's the current price of AAPL?")
        
        # Look for send button or try Enter
        send_button = await self.page.query_selector("button[type='submit'], .send-button, button:has-text('Send')")
        if send_button:
            await send_button.click()
            print("✅ Clicked send button")
        else:
            await chat_input.press("Enter")
            print("✅ Pressed Enter")
        
        # Wait for response
        print("⏳ Waiting for AI response...")
        await asyncio.sleep(8)  # Give time for AI to respond
        
        # Check for response messages
        message_selectors = [
            ".message", ".chat-message", ".response", 
            "[role='article']", "[data-testid*='message']"
        ]
        
        found_response = False
        for selector in message_selectors:
            messages = await self.page.query_selector_all(selector)
            if messages:
                print(f"✅ Found {len(messages)} messages with selector: {selector}")
                for i, msg in enumerate(messages):
                    text = await msg.text_content()
                    if text and len(text) > 10:
                        print(f"📝 Message {i+1}: {text[:100]}...")
                        if "aapl" in text.lower() or "apple" in text.lower():
                            found_response = True
                break
        
        await self.page.screenshot(path="trader_test_after_query.png", full_page=True)
        return found_response
    
    async def test_trader_scenario_2(self):
        """Test: Trader wants to switch chart to different symbol"""
        print("\n📈 TRADER SCENARIO 2: Switch chart to TSLA")
        
        # Find chat input again
        chat_input = await self.page.query_selector("input, textarea")
        if not chat_input:
            print("❌ Chat input not found for second test")
            return False
        
        # Clear and type new command
        await chat_input.fill("Change chart to TSLA")
        await chat_input.press("Enter")
        
        print("⏳ Waiting for chart change...")
        await asyncio.sleep(5)
        
        # Check if chart changed by looking for TSLA in the interface
        page_content = await self.page.content()
        tsla_found = "tsla" in page_content.lower() or "tesla" in page_content.lower()
        
        await self.page.screenshot(path="trader_test_chart_change.png", full_page=True)
        return tsla_found
    
    async def test_chat_functionality_directly(self):
        """Test ChatKit component directly"""
        print("\n🔧 DIRECT CHAT FUNCTIONALITY TEST")
        
        # Check if ChatKit iframe or component is loaded
        chatkit_elements = await self.page.query_selector_all(".chart-agent-chat, [class*='chatkit'], iframe")
        print(f"Found {len(chatkit_elements)} ChatKit-related elements")
        
        # Check if there are any iframes (ChatKit often uses iframes)
        iframes = await self.page.query_selector_all("iframe")
        if iframes:
            print(f"✅ Found {len(iframes)} iframes - ChatKit likely using iframe")
            for i, iframe in enumerate(iframes):
                src = await iframe.get_attribute("src")
                print(f"  Iframe {i+1}: {src}")
        
        # Take detailed screenshot
        await self.page.screenshot(path="trader_test_chatkit_analysis.png", full_page=True)
        
        return len(iframes) > 0
    
    async def run_all_tests(self):
        """Run complete trader workflow test"""
        print("🚀 Starting Real Trader Workflow Test...")
        
        await self.setup()
        
        try:
            # Test basic chat functionality
            chat_works = await self.test_chat_functionality_directly()
            
            # Test trader scenarios
            scenario1_works = await self.test_trader_scenario_1()
            scenario2_works = await self.test_trader_scenario_2()
            
            # Results
            print("\n" + "="*60)
            print("🏦 TRADER WORKFLOW TEST RESULTS")
            print("="*60)
            print(f"ChatKit Component Loaded: {'✅ YES' if chat_works else '❌ NO'}")
            print(f"AAPL Price Query Works: {'✅ YES' if scenario1_works else '❌ NO'}")
            print(f"Chart Symbol Change Works: {'✅ YES' if scenario2_works else '❌ NO'}")
            
            overall_score = sum([chat_works, scenario1_works, scenario2_works])
            print(f"\nOverall Score: {overall_score}/3")
            
            if overall_score == 3:
                print("🎉 All trader workflows working perfectly!")
            elif overall_score >= 1:
                print("⚠️  Some functionality working, but issues need fixing")
            else:
                print("❌ Critical issues - chat not functional for traders")
            
            return overall_score >= 2
            
        finally:
            if self.browser:
                await self.browser.close()

async def main():
    tester = TraderWorkflowTest()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    print("🏦 Testing interface as a real trader would use it...")
    success = asyncio.run(main())
    exit(0 if success else 1)