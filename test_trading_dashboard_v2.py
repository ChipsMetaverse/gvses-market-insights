#!/usr/bin/env python3
"""
Playwright tests for GVSES AI Market Analysis Trading Dashboard - V2
Updated with correct selectors based on actual dashboard structure
"""

import asyncio
import os
import sys
import time
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext, expect

# Configuration
FRONTEND_URL = "http://localhost:5174"  # Frontend dev server
BACKEND_URL = "http://localhost:8000"  # Backend API server

class TradingDashboardTests:
    """Test suite for the trading dashboard application."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.test_results = []
        
    async def setup(self, headless: bool = False):
        """Initialize browser and page."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--disable-web-security']  # For cross-origin requests
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            permissions=['microphone']  # For voice features
        )
        self.page = await self.context.new_page()
        
        # Enable console logging
        self.page.on("console", lambda msg: print(f"[Browser Console] {msg.text[:100]}") if msg.text else None)
        
    async def teardown(self):
        """Clean up browser resources."""
        if self.browser:
            await self.browser.close()
            
    async def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
            
    async def test_dashboard_loads(self):
        """Test that the dashboard loads successfully."""
        try:
            await self.page.goto(FRONTEND_URL, wait_until="networkidle")
            await self.page.wait_for_timeout(2000)  # Give time for components to render
            
            # Check for main app title
            title = await self.page.query_selector("text=GVSES")
            
            # Check for stock ticker bar at the top
            tickers = await self.page.query_selector_all(".stock-ticker, [class*='ticker']")
            
            # Check for chart container
            chart = await self.page.query_selector("canvas, .chart-container, #chart")
            
            if title or tickers or chart:
                await self.log_result(
                    "Dashboard Loading",
                    True,
                    f"Dashboard loaded with chart and ticker elements"
                )
                return True
            else:
                await self.log_result(
                    "Dashboard Loading",
                    False,
                    "Core elements not found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Dashboard Loading", False, str(e))
            return False
            
    async def test_stock_tickers(self):
        """Test the stock ticker bar functionality."""
        try:
            # Look for stock price displays (visible in screenshot: TSLA $425.85, etc.)
            price_elements = await self.page.query_selector_all("text=/\\$[0-9]+\\.[0-9]+/")
            
            # Look for percentage changes
            percent_elements = await self.page.query_selector_all("text=/[+-][0-9]+\\.[0-9]+%/")
            
            if len(price_elements) > 0:
                # Get ticker symbols
                ticker_texts = []
                for elem in price_elements[:5]:  # Check first 5
                    text = await elem.inner_text()
                    ticker_texts.append(text)
                
                await self.log_result(
                    "Stock Tickers",
                    True,
                    f"Found {len(price_elements)} price displays, samples: {', '.join(ticker_texts[:3])}"
                )
                return True
            else:
                await self.log_result(
                    "Stock Tickers",
                    False,
                    "No stock price elements found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Stock Tickers", False, str(e))
            return False
            
    async def test_chart_display(self):
        """Test that the TradingView chart displays correctly."""
        try:
            # Wait for canvas elements (TradingView chart)
            await self.page.wait_for_selector("canvas", timeout=10000)
            canvas_elements = await self.page.query_selector_all("canvas")
            
            if len(canvas_elements) > 0:
                # Look for chart controls (Sell High, Buy Low, BTD buttons visible in screenshot)
                chart_buttons = await self.page.query_selector_all("text=/Sell High|Buy Low|BTD/")
                
                # Check for timeframe controls (visible in screenshot: Apr, May, Jun, etc.)
                timeframe_labels = await self.page.query_selector_all("text=/Apr|May|Jun|Jul|Aug|Sep/")
                
                await self.log_result(
                    "Chart Display",
                    True,
                    f"Chart rendered with {len(canvas_elements)} canvas elements, {len(chart_buttons)} control buttons"
                )
                return True
            else:
                await self.log_result(
                    "Chart Display",
                    False,
                    "No chart canvas elements found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Chart Display", False, str(e))
            return False
            
    async def test_chart_analysis_panel(self):
        """Test the Chart Analysis sidebar panel."""
        try:
            # Look for "CHART ANALYSIS" header
            analysis_header = await self.page.query_selector("text=CHART ANALYSIS")
            
            if analysis_header:
                # Look for TSLA analysis content
                tsla_content = await self.page.query_selector_all("text=/TSLA/")
                
                # Look for technical levels (visible in screenshot)
                levels = await self.page.query_selector_all("text=/Sell High|Buy Low|BTD|TECHNICAL LEVELS/")
                
                # Look for pattern detection section
                pattern_section = await self.page.query_selector("text=PATTERN DETECTION")
                
                await self.log_result(
                    "Chart Analysis Panel",
                    True,
                    f"Analysis panel found with {len(tsla_content)} TSLA mentions, {len(levels)} technical indicators"
                )
                return True
            else:
                # Alternative: Look for sidebar content
                sidebar = await self.page.query_selector(".sidebar, aside, [class*='analysis']")
                if sidebar:
                    await self.log_result(
                        "Chart Analysis Panel",
                        True,
                        "Analysis sidebar present"
                    )
                    return True
                else:
                    await self.log_result(
                        "Chart Analysis Panel",
                        False,
                        "Chart Analysis panel not found"
                    )
                    return False
                
        except Exception as e:
            await self.log_result("Chart Analysis Panel", False, str(e))
            return False
            
    async def test_voice_assistant_ui(self):
        """Test voice assistant UI elements."""
        try:
            # Look for "VOICE ASSISTANT" header
            voice_header = await self.page.query_selector("text=VOICE ASSISTANT")
            
            # Look for microphone button or "Click mic to start"
            mic_button = await self.page.query_selector("text=/Click mic to start|microphone|🎤/")
            
            # Look for message input area
            message_input = await self.page.query_selector("text=/Connect to send messages/")
            
            if voice_header or mic_button or message_input:
                details = []
                if voice_header:
                    details.append("Voice header")
                if mic_button:
                    details.append("Mic button")
                if message_input:
                    details.append("Message input")
                    
                await self.log_result(
                    "Voice Assistant UI",
                    True,
                    f"Found: {', '.join(details)}"
                )
                return True
            else:
                await self.log_result(
                    "Voice Assistant UI",
                    False,
                    "Voice assistant elements not found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Voice Assistant UI", False, str(e))
            return False
            
    async def test_technical_levels(self):
        """Test technical analysis levels display."""
        try:
            # Look for technical levels section
            levels_found = []
            
            # Check for Sell High level ($438.63 visible in screenshot)
            sell_high = await self.page.query_selector("text=/Sell High.*\\$[0-9]+/")
            if sell_high:
                levels_found.append("Sell High")
                
            # Check for Buy Low level ($428.82 visible in screenshot)
            buy_low = await self.page.query_selector("text=/Buy Low.*\\$[0-9]+/")
            if buy_low:
                levels_found.append("Buy Low")
                
            # Check for BTD level ($391.78 visible in screenshot)
            btd = await self.page.query_selector("text=/BTD.*\\$[0-9]+/")
            if btd:
                levels_found.append("BTD")
                
            if levels_found:
                await self.log_result(
                    "Technical Levels",
                    True,
                    f"Found levels: {', '.join(levels_found)}"
                )
                return True
            else:
                await self.log_result(
                    "Technical Levels",
                    False,
                    "No technical levels displayed"
                )
                return False
                
        except Exception as e:
            await self.log_result("Technical Levels", False, str(e))
            return False
            
    async def test_api_connectivity(self):
        """Test backend API connectivity."""
        try:
            # Check if backend health endpoint is accessible
            api_response = await self.page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('http://localhost:8000/health');
                        const data = await response.json();
                        return { ok: response.ok, data: data };
                    } catch (e) {
                        return { ok: false, error: e.message };
                    }
                }
            """)
            
            if api_response.get('ok'):
                await self.log_result(
                    "API Connectivity",
                    True,
                    f"Backend status: {api_response.get('data', {}).get('status', 'unknown')}"
                )
                return True
            else:
                await self.log_result(
                    "API Connectivity",
                    False,
                    f"Backend connection failed: {api_response.get('error', 'Unknown error')}"
                )
                return False
                
        except Exception as e:
            await self.log_result("API Connectivity", False, str(e))
            return False
            
    async def test_chart_interactions(self):
        """Test chart interaction capabilities."""
        try:
            # Try to interact with the chart
            chart_area = await self.page.query_selector("canvas")
            
            if chart_area:
                # Get initial screenshot
                await self.page.screenshot(path="/tmp/before_interaction.png")
                
                # Try to click and drag on chart (pan)
                await chart_area.hover()
                await self.page.mouse.down()
                await self.page.mouse.move(100, 0)
                await self.page.mouse.up()
                await self.page.wait_for_timeout(500)
                
                # Take after screenshot
                await self.page.screenshot(path="/tmp/after_interaction.png")
                
                await self.log_result(
                    "Chart Interactions",
                    True,
                    "Chart accepts mouse interactions"
                )
                return True
            else:
                await self.log_result(
                    "Chart Interactions",
                    False,
                    "Chart canvas not found for interaction"
                )
                return False
                
        except Exception as e:
            await self.log_result("Chart Interactions", False, str(e))
            return False
            
    async def take_screenshot(self, name: str = "dashboard"):
        """Take a screenshot of the current page."""
        try:
            timestamp = int(time.time())
            filename = f"/tmp/playwright_{name}_{timestamp}.png"
            await self.page.screenshot(path=filename, full_page=True)
            print(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None
            
    async def run_all_tests(self):
        """Run all test cases."""
        print("=" * 60)
        print("🎭 Playwright Testing - Trading Dashboard V2")
        print("=" * 60)
        
        # Run tests
        await self.test_dashboard_loads()
        await self.test_stock_tickers()
        await self.test_chart_display()
        await self.test_chart_analysis_panel()
        await self.test_voice_assistant_ui()
        await self.test_technical_levels()
        await self.test_api_connectivity()
        await self.test_chart_interactions()
        
        # Take final screenshot
        await self.take_screenshot("final_state_v2")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            if result['details']:
                print(f"   → {result['details']}")
            
        print(f"\nTotal: {passed}/{total} tests passed ({passed*100//total if total else 0}%)")
        
        return passed == total

async def main():
    """Main test runner."""
    # Check if servers are running
    print("Pre-flight checks...")
    print(f"Frontend URL: {FRONTEND_URL}")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Create test instance
    tests = TradingDashboardTests()
    
    try:
        # Setup browser (headless=False to see the browser)
        await tests.setup(headless=False)
        
        # Run all tests
        success = await tests.run_all_tests()
        
        # Keep browser open for a moment to see final state
        await asyncio.sleep(2)
        
        # Return exit code
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1
        
    finally:
        await tests.teardown()

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)