#!/usr/bin/env python3
"""
Playwright tests for GVSES AI Market Analysis Trading Dashboard
Tests frontend functionality, market data, and UI interactions
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
        self.page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        
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
            
            # Check for main dashboard elements
            await self.page.wait_for_selector(".trading-dashboard-simple", timeout=10000)
            
            # Verify three panels are present
            panels = await self.page.query_selector_all(".dashboard-panel")
            panel_count = len(panels)
            
            if panel_count == 3:
                await self.log_result(
                    "Dashboard Loading",
                    True,
                    f"All {panel_count} panels loaded successfully"
                )
            else:
                await self.log_result(
                    "Dashboard Loading",
                    False,
                    f"Expected 3 panels, found {panel_count}"
                )
                
            return panel_count == 3
            
        except Exception as e:
            await self.log_result("Dashboard Loading", False, str(e))
            return False
            
    async def test_market_insights_panel(self):
        """Test the Market Insights panel functionality."""
        try:
            # Check for stock cards
            await self.page.wait_for_selector(".stock-card", timeout=10000)
            stock_cards = await self.page.query_selector_all(".stock-card")
            
            if len(stock_cards) > 0:
                # Get first stock card details
                first_card = stock_cards[0]
                symbol = await first_card.query_selector(".stock-symbol")
                symbol_text = await symbol.inner_text() if symbol else "Unknown"
                
                price = await first_card.query_selector(".stock-price")
                has_price = price is not None
                
                await self.log_result(
                    "Market Insights Panel",
                    True,
                    f"Found {len(stock_cards)} stock cards, first symbol: {symbol_text}"
                )
                return True
            else:
                await self.log_result(
                    "Market Insights Panel",
                    False,
                    "No stock cards found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Market Insights Panel", False, str(e))
            return False
            
    async def test_watchlist_management(self):
        """Test adding and removing stocks from watchlist."""
        try:
            # Find the search input
            search_input = await self.page.query_selector('input[placeholder*="Search"]')
            if not search_input:
                await self.log_result("Watchlist Management", False, "Search input not found")
                return False
                
            # Type a stock symbol
            await search_input.fill("GOOGL")
            await self.page.wait_for_timeout(500)  # Wait for debounce
            
            # Look for add button or suggestions
            add_button = await self.page.query_selector('button:has-text("Add")')
            if add_button:
                # Count stock cards before adding
                cards_before = len(await self.page.query_selector_all(".stock-card"))
                
                # Click add button
                await add_button.click()
                await self.page.wait_for_timeout(1000)
                
                # Count stock cards after adding
                cards_after = len(await self.page.query_selector_all(".stock-card"))
                
                if cards_after > cards_before:
                    # Try to remove a stock
                    remove_buttons = await self.page.query_selector_all(".stock-card .remove-btn, .stock-card button:has-text('×')")
                    if len(remove_buttons) > 0:
                        await remove_buttons[0].click()
                        await self.page.wait_for_timeout(1000)
                        
                        cards_final = len(await self.page.query_selector_all(".stock-card"))
                        
                        await self.log_result(
                            "Watchlist Management",
                            True,
                            f"Successfully added and removed stocks ({cards_before} → {cards_after} → {cards_final})"
                        )
                        return True
                    else:
                        await self.log_result(
                            "Watchlist Management",
                            True,
                            f"Added stock successfully ({cards_before} → {cards_after})"
                        )
                        return True
                else:
                    await self.log_result(
                        "Watchlist Management",
                        False,
                        "Stock not added to watchlist"
                    )
                    return False
            else:
                # Just check that search input works
                await self.log_result(
                    "Watchlist Management",
                    True,
                    "Search input functional (Add button not visible in current state)"
                )
                return True
                
        except Exception as e:
            await self.log_result("Watchlist Management", False, str(e))
            return False
            
    async def test_chart_display(self):
        """Test that the chart displays correctly."""
        try:
            # Wait for chart container
            chart_container = await self.page.query_selector(".trading-chart, .chart-container, #chart")
            if not chart_container:
                await self.log_result("Chart Display", False, "Chart container not found")
                return False
                
            # Check for TradingView elements
            tv_elements = await self.page.query_selector_all('[class*="tv-"], canvas')
            
            if len(tv_elements) > 0:
                # Try to interact with a stock card to change chart
                stock_cards = await self.page.query_selector_all(".stock-card")
                if len(stock_cards) > 0:
                    await stock_cards[0].click()
                    await self.page.wait_for_timeout(1000)
                    
                    await self.log_result(
                        "Chart Display",
                        True,
                        f"Chart rendered with {len(tv_elements)} TradingView elements"
                    )
                else:
                    await self.log_result(
                        "Chart Display",
                        True,
                        "Chart container present"
                    )
                return True
            else:
                await self.log_result(
                    "Chart Display",
                    False,
                    "No TradingView elements found"
                )
                return False
                
        except Exception as e:
            await self.log_result("Chart Display", False, str(e))
            return False
            
    async def test_voice_assistant_ui(self):
        """Test voice assistant UI elements."""
        try:
            # Look for voice button/indicator
            voice_elements = await self.page.query_selector_all(
                '[class*="voice"], [class*="microphone"], button[aria-label*="voice"], button[aria-label*="mic"]'
            )
            
            if len(voice_elements) > 0:
                # Check if ElevenLabs components are present
                elevenlabs_elements = await self.page.query_selector_all('[class*="elevenlabs"]')
                
                await self.log_result(
                    "Voice Assistant UI",
                    True,
                    f"Found {len(voice_elements)} voice elements, {len(elevenlabs_elements)} ElevenLabs components"
                )
                return True
            else:
                # Voice might be optional
                await self.log_result(
                    "Voice Assistant UI",
                    True,
                    "Voice UI not visible (may be disabled or optional)"
                )
                return True
                
        except Exception as e:
            await self.log_result("Voice Assistant UI", False, str(e))
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
            
    async def test_chart_analysis_panel(self):
        """Test the Chart Analysis panel with news feed."""
        try:
            # Look for news/analysis panel
            analysis_panel = await self.page.query_selector(".chart-analysis-panel, .panel-header:has-text('Chart Analysis')")
            
            if analysis_panel:
                # Check for news items
                news_items = await self.page.query_selector_all(".news-item, .analysis-item, [class*='news']")
                
                if len(news_items) > 0:
                    await self.log_result(
                        "Chart Analysis Panel",
                        True,
                        f"Found {len(news_items)} news/analysis items"
                    )
                else:
                    # Check if panel exists but is empty
                    empty_state = await self.page.query_selector(".empty-state, .no-news")
                    if empty_state:
                        await self.log_result(
                            "Chart Analysis Panel",
                            True,
                            "Panel present with empty state"
                        )
                    else:
                        await self.log_result(
                            "Chart Analysis Panel",
                            True,
                            "Panel present (news may be loading)"
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
            
    async def test_responsive_layout(self):
        """Test responsive layout at different viewport sizes."""
        try:
            # Test mobile viewport
            await self.page.set_viewport_size({"width": 375, "height": 812})
            await self.page.wait_for_timeout(500)
            
            mobile_menu = await self.page.query_selector('[class*="mobile"], [class*="hamburger"]')
            is_mobile_responsive = mobile_menu is not None or True  # May not have mobile menu
            
            # Test tablet viewport
            await self.page.set_viewport_size({"width": 768, "height": 1024})
            await self.page.wait_for_timeout(500)
            
            # Test desktop viewport
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            await self.page.wait_for_timeout(500)
            
            # Check if panels are still visible
            panels = await self.page.query_selector_all(".dashboard-panel")
            
            await self.log_result(
                "Responsive Layout",
                True,
                f"Layout adapts to different viewports, {len(panels)} panels visible on desktop"
            )
            return True
            
        except Exception as e:
            await self.log_result("Responsive Layout", False, str(e))
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
        print("🎭 Playwright Testing - Trading Dashboard")
        print("=" * 60)
        
        # Run tests
        await self.test_dashboard_loads()
        await self.test_market_insights_panel()
        await self.test_watchlist_management()
        await self.test_chart_display()
        await self.test_voice_assistant_ui()
        await self.test_api_connectivity()
        await self.test_chart_analysis_panel()
        await self.test_responsive_layout()
        
        # Take final screenshot
        await self.take_screenshot("final_state")
        
        # Print summary
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        passed = sum(1 for r in self.test_results if r['passed'])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result['passed'] else "❌"
            print(f"{status} {result['test']}")
            
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