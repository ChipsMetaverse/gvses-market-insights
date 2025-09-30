#!/usr/bin/env python3
"""
Novice Trader Experience Tester
Tests the Claude Voice Assistant as a beginner trader would use it
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from playwright.async_api import async_playwright, Page, ConsoleMessage, Error
import subprocess

class NoviceTraderTester:
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "errors": [],
            "console_logs": [],
            "network_errors": [],
            "ui_issues": []
        }
        self.browser = None
        self.page = None
        self.context = None
        
    async def setup(self):
        """Setup browser with proper monitoring"""
        playwright = await async_playwright().start()
        
        # Launch in visible mode so we can see what's happening
        self.browser = await playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Novice Trader) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = await self.context.new_page()
        
        # Setup comprehensive monitoring
        await self.setup_monitoring()
        
    async def setup_monitoring(self):
        """Setup event listeners for comprehensive monitoring"""
        
        # Capture console messages
        async def handle_console(msg: ConsoleMessage):
            entry = {
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat()
            }
            self.test_results["console_logs"].append(entry)
            
            # Flag errors
            if msg.type in ['error', 'warning']:
                print(f"🔴 Console {msg.type}: {msg.text}")
                
        self.page.on("console", handle_console)
        
        # Capture page errors
        async def handle_error(error: Error):
            self.test_results["errors"].append({
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            })
            print(f"🔴 Page Error: {error}")
            
        self.page.on("pageerror", handle_error)
        
        # Monitor network failures
        async def handle_request_failed(request):
            self.test_results["network_errors"].append({
                "url": request.url,
                "failure": request.failure,
                "timestamp": datetime.now().isoformat()
            })
            print(f"🔴 Network Error: {request.url}")
            
        self.page.on("requestfailed", handle_request_failed)
        
    async def wait_and_screenshot(self, name: str, wait_time: int = 2000):
        """Wait and take a screenshot"""
        await self.page.wait_for_timeout(wait_time)
        await self.page.screenshot(path=f"test_{name}.png")
        print(f"📸 Screenshot: test_{name}.png")
        
    async def test_novice_journey(self, url: str = "http://localhost:5174"):
        """Test the complete novice trader journey"""
        print("\n🚀 Starting Novice Trader Experience Test\n")
        print("=" * 60)
        
        # 1. First Visit - What does a beginner see?
        await self.test_first_visit(url)
        
        # 2. Basic Questions - What beginners ask
        await self.test_beginner_questions()
        
        # 3. Educational Queries - Learning the basics
        await self.test_educational_queries()
        
        # 4. Market Exploration - Looking around
        await self.test_market_exploration()
        
        # 5. Chart Interaction - Visual learning
        await self.test_chart_interaction()
        
        # 6. Voice Assistant - Conversational help
        await self.test_voice_assistant()
        
        # 7. Error Recovery - When things go wrong
        await self.test_error_recovery()
        
    async def test_first_visit(self, url: str):
        """Test what a first-time visitor experiences"""
        print("\n📍 TEST 1: First Visit Experience")
        print("-" * 40)
        
        await self.page.goto(url, wait_until='networkidle')
        await self.wait_and_screenshot("1_initial_load")
        
        # Check if the page loaded properly
        try:
            # Look for main UI elements
            dashboard = await self.page.query_selector('.trading-dashboard')
            if not dashboard:
                self.record_issue("UI", "Dashboard did not load on first visit")
                
            # Check for onboarding or help
            help_visible = await self.page.query_selector('[aria-label*="help"], .help-button, .tutorial')
            if not help_visible:
                self.record_issue("UX", "No visible help or onboarding for new users")
                
            print("✅ Page loaded successfully")
            
        except Exception as e:
            self.record_issue("Load", f"Page failed to load: {e}")
            
    async def test_beginner_questions(self):
        """Test basic questions a beginner would ask"""
        print("\n📍 TEST 2: Beginner Questions")
        print("-" * 40)
        
        # Connect voice assistant first
        if not await self.ensure_voice_connected():
            print("⚠️ Skipping beginner questions - voice assistant connection failed")
            return
        
        beginner_queries = [
            "What is AAPL?",
            "Show me Tesla stock",
            "What is the S&P 500?"
        ]
        
        for query in beginner_queries:
            await self.send_query_and_wait(query, f"beginner_{query[:20].replace(' ', '_')}")
            
    async def test_educational_queries(self):
        """Test educational queries for learning"""
        print("\n📍 TEST 3: Educational Queries")
        print("-" * 40)
        
        educational_queries = [
            "What does buy low sell high mean?",
            "Explain support and resistance",
            "What is a bull market?",
            "What are dividends?",
            "What is market cap?",
            "How do I read a chart?"
        ]
        
        for query in educational_queries:
            await self.send_query_and_wait(query, f"education_{query[:20]}")
            
    async def test_market_exploration(self):
        """Test market exploration features"""
        print("\n📍 TEST 4: Market Exploration")
        print("-" * 40)
        
        # Try to explore the market
        exploration_queries = [
            "Show me top gainers",
            "What's trending today?",
            "Show me tech stocks",
            "Compare AAPL and MSFT",
            "What is the S&P 500 doing?"
        ]
        
        for query in exploration_queries:
            await self.send_query_and_wait(query, f"explore_{query[:20]}")
            
        # Try to interact with the market insights panel
        await self.check_market_insights_panel()
        
    async def test_chart_interaction(self):
        """Test chart interaction and visual features"""
        print("\n📍 TEST 5: Chart Interaction")
        print("-" * 40)
        
        chart_commands = [
            "Show me Apple chart",
            "Add moving average",
            "Show support levels",
            "Zoom in on today",
            "Show me 1 year chart"
        ]
        
        for command in chart_commands:
            await self.send_query_and_wait(command, f"chart_{command[:20]}")
            
            # Check if chart updated
            await self.verify_chart_update()
            
    async def test_voice_assistant(self):
        """Test voice assistant functionality"""
        print("\n📍 TEST 6: Voice Assistant")
        print("-" * 40)
        
        # Look for voice button using data-testid
        voice_button = await self.page.query_selector('[data-testid="voice-fab"], .voice-fab')
        
        if voice_button:
            print("🎤 Found voice button, connecting...")
            await voice_button.click()
            
            # Wait for connection to establish (button gets 'active' class)
            await self.page.wait_for_selector('.voice-fab.active', timeout=10000)
            print("✅ Voice assistant connected")
            
            await self.wait_and_screenshot("6_voice_connected")
            
            # Now the input field should be active
            input_field = await self.page.query_selector('.voice-text-input')
            if input_field:
                # Check if it's enabled
                is_disabled = await input_field.evaluate('el => el.disabled')
                if not is_disabled:
                    print("✅ Input field is active")
                    await input_field.click()
                    await input_field.type("What is the market doing today?")
                    await self.page.keyboard.press("Enter")
                    await self.wait_and_screenshot("6_voice_query_sent")
                    
                    # Wait for response
                    await self.wait_for_response()
                    await self.wait_and_screenshot("6_voice_response_received")
                else:
                    self.record_issue("Voice", "Input field is disabled despite connection")
            else:
                self.record_issue("Voice", "Voice input field not found")
        else:
            self.record_issue("Voice", "No voice button found")
            
    async def test_error_recovery(self):
        """Test how the app handles errors and edge cases"""
        print("\n📍 TEST 7: Error Recovery")
        print("-" * 40)
        
        error_queries = [
            "INVALIDTICKER",
            "Show me XYZABC123",
            "Buy 1000000 shares of AAPL",
            "What is everything down?",  # The problematic query
            "!@#$%^&*()",
            ""  # Empty query
        ]
        
        for query in error_queries:
            await self.send_query_and_wait(query or "[empty]", f"error_{query[:10] if query else 'empty'}")
            
            # Check for error handling
            error_message = await self.page.query_selector('.error-message, .alert-danger, [role="alert"]')
            if not error_message and query:
                self.record_issue("Error Handling", f"No error message for invalid query: {query}")
                
    async def ensure_voice_connected(self):
        """Ensure voice assistant is connected before testing"""
        # Check if already connected
        is_connected = await self.page.query_selector('.voice-fab.active')
        if not is_connected:
            print("🔌 Connecting voice assistant...")
            voice_button = await self.page.query_selector('[data-testid="voice-fab"], .voice-fab')
            if voice_button:
                await voice_button.click()
                try:
                    await self.page.wait_for_selector('.voice-fab.active', timeout=10000)
                    print("✅ Voice assistant connected")
                    await self.page.wait_for_timeout(1000)  # Let connection stabilize
                except:
                    self.record_issue("Connection", "Failed to connect voice assistant")
                    return False
        return True
    
    async def send_query_and_wait(self, query: str, screenshot_name: str):
        """Send a query and wait for response"""
        print(f"\n🔍 Testing: '{query}'")
        
        # Ensure voice is connected first
        if not await self.ensure_voice_connected():
            return
        
        # The ONLY input field is the voice assistant input
        input_field = await self.page.query_selector('.voice-text-input')
                
        if not input_field:
            self.record_issue("Input", "Voice input field not found")
            return
            
        # Clear and type the query
        await input_field.click()
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Delete")
        await input_field.type(query)
        
        # Send the query
        await self.page.keyboard.press("Enter")
        
        # Wait for response with multiple strategies
        await self.wait_for_response()
        
        # Take screenshot
        await self.wait_and_screenshot(screenshot_name)
        
        # Check if we got a response
        await self.verify_response_received()
        
    async def wait_for_response(self):
        """Wait for response with multiple strategies"""
        try:
            # Wait for any of these indicators
            await self.page.wait_for_selector(
                '.message-assistant, .response-text, .chat-message:last-child',
                timeout=10000,
                state='visible'
            )
        except:
            # Fallback: just wait a bit
            await self.page.wait_for_timeout(5000)
            
    async def verify_response_received(self):
        """Check if a response was actually received"""
        # Look for response indicators
        response_selectors = [
            '.message-assistant:last-child',
            '.chat-message.assistant:last-child',
            '.response-content:last-child'
        ]
        
        response_found = False
        for selector in response_selectors:
            response = await self.page.query_selector(selector)
            if response:
                text = await response.text_content()
                if text and len(text) > 10:
                    print(f"✅ Response received: {text[:100]}...")
                    response_found = True
                    break
                    
        if not response_found:
            print("⚠️ No response detected")
            self.record_issue("Response", "No response received for query")
            
    async def verify_chart_update(self):
        """Check if chart actually updated"""
        chart = await self.page.query_selector('.trading-chart, canvas')
        if chart:
            print("✅ Chart element found")
            # Could add more sophisticated checks here
        else:
            self.record_issue("Chart", "Chart did not update or render")
            
    async def check_market_insights_panel(self):
        """Check the market insights panel"""
        panel = await self.page.query_selector('.market-insights-container')
        if panel:
            # Check for stock cards
            cards = await self.page.query_selector_all('.market-card')
            print(f"✅ Found {len(cards)} stock cards in market insights")
            
            # Try to add a symbol
            add_button = await self.page.query_selector('button:has-text("Add")')
            if add_button:
                print("✅ Add symbol button found")
        else:
            self.record_issue("Market Panel", "Market insights panel not found")
            
    def record_issue(self, category: str, description: str):
        """Record a UI/UX issue"""
        issue = {
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results["ui_issues"].append(issue)
        print(f"⚠️ {category} Issue: {description}")
        
    async def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT")
        print("=" * 60)
        
        # Summary
        print(f"\n📈 Summary:")
        print(f"  • Tests Run: {len(self.test_results['tests'])}")
        print(f"  • UI Issues Found: {len(self.test_results['ui_issues'])}")
        print(f"  • Console Errors: {len([e for e in self.test_results['console_logs'] if e['type'] == 'error'])}")
        print(f"  • Network Errors: {len(self.test_results['network_errors'])}")
        
        # Critical Issues
        if self.test_results['ui_issues']:
            print(f"\n🔴 Critical Issues:")
            for issue in self.test_results['ui_issues']:
                print(f"  • [{issue['category']}] {issue['description']}")
                
        # Console Errors
        errors = [e for e in self.test_results['console_logs'] if e['type'] == 'error']
        if errors:
            print(f"\n⚠️ Console Errors:")
            for error in errors[:5]:  # Show first 5
                print(f"  • {error['text'][:100]}")
                
        # Save full report
        report_file = f"novice_trader_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Full report saved to: {report_file}")
        
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
            
    async def run(self):
        """Run the complete test suite"""
        try:
            await self.setup()
            await self.test_novice_journey()
            await self.generate_report()
        finally:
            await self.cleanup()

async def main():
    """Main entry point"""
    tester = NoviceTraderTester()
    await tester.run()

if __name__ == "__main__":
    print("🎯 Claude Voice Assistant - Novice Trader Experience Test")
    print("This test simulates how a beginner would use the application")
    print("-" * 60)
    asyncio.run(main())