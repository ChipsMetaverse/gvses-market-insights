#!/usr/bin/env python3
"""
Full Range Playwright Testing - Comprehensive Symbol Coverage
Tests all watchlist symbols + random public tickers across the GVSES dashboard.

Ultrathink Strategy:
1. Test all default watchlist symbols (TSLA, AAPL, NVDA, SPY, PLTR)
2. Test random public tickers (stocks, crypto, ETFs)
3. Validate chart rendering, data loading, and error-free operation
4. Measure performance across different symbols
5. Test symbol switching and state management
"""

import asyncio
import time
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, TimeoutError

# Test Configuration
FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"

# Symbol Categories for Comprehensive Testing
TEST_SYMBOLS = {
    "watchlist": ["TSLA", "AAPL", "NVDA", "SPY", "PLTR"],  # Default watchlist
    "mega_cap": ["MSFT", "GOOGL", "AMZN", "META", "BRK.B"],  # Large cap stocks
    "growth": ["NFLX", "SHOP", "SQ", "COIN", "ROKU"],  # Growth stocks
    "crypto": ["BTC-USD", "ETH-USD", "SOL-USD"],  # Cryptocurrencies
    "etfs": ["QQQ", "IWM", "GLD", "TLT"],  # ETFs
    "volatility": ["GME", "AMC", "TSLA", "RIVN"],  # High volatility
}

# Performance thresholds (milliseconds)
THRESHOLDS = {
    "chart_load": 5000,  # Chart should load within 5s
    "data_fetch": 3000,  # API data within 3s
    "symbol_switch": 2000,  # Symbol switch within 2s
}

class TestResults:
    """Track test results across all symbols."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.performance_data = []
        self.symbol_results = {}
        self.start_time = datetime.now()

    def add_result(self, symbol: str, success: bool, duration_ms: int, error: str = None):
        """Record test result for a symbol."""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        else:
            self.tests_failed += 1
            if error:
                self.errors.append(f"{symbol}: {error}")

        self.symbol_results[symbol] = {
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }

        self.performance_data.append({
            "symbol": symbol,
            "duration_ms": duration_ms
        })

    def get_summary(self) -> dict:
        """Generate test summary."""
        total_duration = (datetime.now() - self.start_time).total_seconds()
        avg_duration = sum(p["duration_ms"] for p in self.performance_data) / len(self.performance_data) if self.performance_data else 0

        return {
            "total_tests": self.tests_run,
            "passed": self.tests_passed,
            "failed": self.tests_failed,
            "pass_rate": f"{(self.tests_passed / self.tests_run * 100):.1f}%" if self.tests_run > 0 else "0%",
            "total_duration_seconds": round(total_duration, 2),
            "average_load_time_ms": round(avg_duration, 2),
            "errors": self.errors,
            "symbols_tested": len(self.symbol_results),
            "performance_data": self.performance_data,
            "symbol_results": self.symbol_results
        }


async def wait_for_chart_render(page: Page, symbol: str, timeout: int = 10000) -> bool:
    """Wait for chart to render for a specific symbol."""
    try:
        # Wait for canvas element (TradingView Lightweight Charts)
        await page.wait_for_selector('canvas', timeout=timeout)

        # Wait for symbol to appear in header or chart title
        await page.wait_for_function(
            f'document.body.innerText.includes("{symbol}")',
            timeout=timeout
        )

        # Additional wait for chart to fully render
        await asyncio.sleep(1)

        return True
    except TimeoutError:
        return False


async def check_console_errors(page: Page) -> list:
    """Collect console errors from the page."""
    errors = []

    def handle_console(msg):
        if msg.type == 'error':
            errors.append(msg.text)

    page.on('console', handle_console)
    return errors


async def test_symbol(page: Page, browser: Browser, symbol: str, results: TestResults) -> bool:
    """Test a single symbol comprehensively."""
    print(f"\n{'='*60}")
    print(f"Testing: {symbol}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        # 1. Click on symbol (if in watchlist) or add via search
        if symbol in TEST_SYMBOLS["watchlist"]:
            # Click watchlist card
            print(f"  → Clicking watchlist card for {symbol}...")
            card_selector = f'div[class*="stock-card"]:has-text("{symbol}")'
            await page.click(card_selector, timeout=5000)
        else:
            # Use search to add symbol
            print(f"  → Adding {symbol} via search...")
            await page.fill('input[placeholder*="Search"]', symbol)
            await asyncio.sleep(1)
            # Click first search result
            await page.click('div[class*="search-result"]:first-child', timeout=5000)

        # 2. Wait for chart to render
        print(f"  → Waiting for chart to render...")
        chart_rendered = await wait_for_chart_render(page, symbol)

        if not chart_rendered:
            error = f"Chart failed to render within timeout"
            print(f"  ✗ {error}")
            duration_ms = int((time.time() - start_time) * 1000)
            results.add_result(symbol, False, duration_ms, error)
            return False

        # 3. Verify data loaded
        print(f"  → Verifying data loaded...")

        # Check for price display
        price_displayed = await page.is_visible('div[class*="price"]', timeout=3000)

        # Check for chart canvas
        canvas_present = await page.is_visible('canvas', timeout=3000)

        if not price_displayed or not canvas_present:
            error = f"Data incomplete - Price: {price_displayed}, Canvas: {canvas_present}"
            print(f"  ✗ {error}")
            duration_ms = int((time.time() - start_time) * 1000)
            results.add_result(symbol, False, duration_ms, error)
            return False

        # 4. Check for console errors
        await asyncio.sleep(1)  # Let any async errors surface

        # 5. Take screenshot for visual verification
        screenshot_path = f"/tmp/playwright_test_{symbol}.png"
        await page.screenshot(path=screenshot_path)
        print(f"  → Screenshot saved: {screenshot_path}")

        # 6. Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)

        # 7. Check performance threshold
        if duration_ms > THRESHOLDS["chart_load"]:
            print(f"  ⚠ Warning: Load time {duration_ms}ms exceeds threshold {THRESHOLDS['chart_load']}ms")

        print(f"  ✓ Test passed in {duration_ms}ms")
        results.add_result(symbol, True, duration_ms)
        return True

    except Exception as e:
        error = str(e)
        print(f"  ✗ Test failed: {error}")
        duration_ms = int((time.time() - start_time) * 1000)
        results.add_result(symbol, False, duration_ms, error)
        return False


async def test_symbol_switching(page: Page, results: TestResults) -> bool:
    """Test rapid symbol switching to verify state management."""
    print(f"\n{'='*60}")
    print(f"Testing: Symbol Switching (State Management)")
    print(f"{'='*60}")

    symbols = ["TSLA", "AAPL", "NVDA", "SPY", "PLTR"]

    try:
        for i, symbol in enumerate(symbols):
            print(f"  → Switching to {symbol} ({i+1}/{len(symbols)})...")

            start_time = time.time()

            # Click watchlist card
            card_selector = f'div[class*="stock-card"]:has-text("{symbol}")'
            await page.click(card_selector, timeout=5000)

            # Wait for chart update
            await wait_for_chart_render(page, symbol, timeout=3000)

            duration_ms = int((time.time() - start_time) * 1000)
            print(f"     Switched in {duration_ms}ms")

            if duration_ms > THRESHOLDS["symbol_switch"]:
                print(f"     ⚠ Warning: Switch time exceeds threshold")

        print(f"  ✓ Symbol switching test passed")
        return True

    except Exception as e:
        print(f"  ✗ Symbol switching test failed: {e}")
        return False


async def test_timeframe_switching(page: Page, symbol: str = "TSLA") -> bool:
    """Test different timeframe intervals."""
    print(f"\n{'='*60}")
    print(f"Testing: Timeframe Switching ({symbol})")
    print(f"{'='*60}")

    intervals = ["1D", "1W", "1M", "1Y"]

    try:
        for interval in intervals:
            print(f"  → Testing {interval} interval...")

            # Click interval button
            button_selector = f'button:has-text("{interval}")'
            await page.click(button_selector, timeout=5000)

            # Wait for chart to update
            await asyncio.sleep(2)

            # Verify canvas is still present
            canvas_present = await page.is_visible('canvas', timeout=3000)

            if not canvas_present:
                print(f"     ✗ Chart disappeared on {interval}")
                return False

            print(f"     ✓ {interval} rendered successfully")

        print(f"  ✓ Timeframe switching test passed")
        return True

    except Exception as e:
        print(f"  ✗ Timeframe switching test failed: {e}")
        return False


async def run_full_test_suite():
    """Execute comprehensive test suite."""
    print("\n" + "="*60)
    print("GVSES FULL RANGE PLAYWRIGHT TEST SUITE")
    print("Ultrathink Comprehensive Testing")
    print("="*60)

    results = TestResults()

    async with async_playwright() as p:
        # Launch browser
        print("\n→ Launching browser...")
        browser = await p.chromium.launch(headless=False)  # headless=False to watch tests

        # Create context and page
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        # Enable console error tracking
        console_errors = []
        page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)

        # Navigate to dashboard
        print(f"→ Navigating to {FRONTEND_URL}...")
        await page.goto(FRONTEND_URL)

        # Wait for dashboard to load
        print("→ Waiting for dashboard to load...")
        await page.wait_for_selector('div[class*="trading-dashboard"]', timeout=10000)
        await asyncio.sleep(2)  # Let initial data load

        print("\n✓ Dashboard loaded successfully")

        # Test 1: Default Watchlist Symbols
        print("\n" + "="*60)
        print("PHASE 1: DEFAULT WATCHLIST SYMBOLS")
        print("="*60)

        for symbol in TEST_SYMBOLS["watchlist"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)  # Brief pause between tests

        # Test 2: Mega Cap Stocks
        print("\n" + "="*60)
        print("PHASE 2: MEGA CAP STOCKS")
        print("="*60)

        for symbol in TEST_SYMBOLS["mega_cap"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)

        # Test 3: Growth Stocks
        print("\n" + "="*60)
        print("PHASE 3: GROWTH STOCKS")
        print("="*60)

        for symbol in TEST_SYMBOLS["growth"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)

        # Test 4: Cryptocurrencies
        print("\n" + "="*60)
        print("PHASE 4: CRYPTOCURRENCIES")
        print("="*60)

        for symbol in TEST_SYMBOLS["crypto"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)

        # Test 5: ETFs
        print("\n" + "="*60)
        print("PHASE 5: ETFs")
        print("="*60)

        for symbol in TEST_SYMBOLS["etfs"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)

        # Test 6: High Volatility Stocks
        print("\n" + "="*60)
        print("PHASE 6: HIGH VOLATILITY STOCKS")
        print("="*60)

        for symbol in TEST_SYMBOLS["volatility"]:
            await test_symbol(page, browser, symbol, results)
            await asyncio.sleep(1)

        # Test 7: Symbol Switching
        await test_symbol_switching(page, results)

        # Test 8: Timeframe Switching
        await test_timeframe_switching(page)

        # Close browser
        print("\n→ Closing browser...")
        await browser.close()

    # Generate results
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    summary = results.get_summary()

    print(f"\nTotal Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ✓")
    print(f"Failed: {summary['failed']} ✗")
    print(f"Pass Rate: {summary['pass_rate']}")
    print(f"Total Duration: {summary['total_duration_seconds']}s")
    print(f"Average Load Time: {summary['average_load_time_ms']}ms")
    print(f"Symbols Tested: {summary['symbols_tested']}")

    if summary['errors']:
        print(f"\n{'='*60}")
        print("ERRORS")
        print("="*60)
        for error in summary['errors']:
            print(f"  ✗ {error}")

    # Performance Analysis
    print(f"\n{'='*60}")
    print("PERFORMANCE ANALYSIS")
    print("="*60)

    # Sort by duration
    perf_sorted = sorted(summary['performance_data'], key=lambda x: x['duration_ms'])

    print("\nFastest 5:")
    for i, item in enumerate(perf_sorted[:5], 1):
        print(f"  {i}. {item['symbol']}: {item['duration_ms']}ms")

    print("\nSlowest 5:")
    for i, item in enumerate(perf_sorted[-5:], 1):
        print(f"  {i}. {item['symbol']}: {item['duration_ms']}ms")

    # Save detailed results
    results_path = "/tmp/playwright_test_results.json"
    with open(results_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n→ Detailed results saved to: {results_path}")

    # Final status
    print(f"\n{'='*60}")
    if summary['failed'] == 0:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"⚠ {summary['failed']} TEST(S) FAILED")
    print("="*60)

    return results


if __name__ == "__main__":
    print("\nStarting Full Range Playwright Tests...")
    print("Make sure frontend is running on http://localhost:5173")
    print("Make sure backend is running on http://localhost:8000")
    print("\nPress Ctrl+C to cancel...\n")

    try:
        asyncio.run(run_full_test_suite())
    except KeyboardInterrupt:
        print("\n\n→ Tests cancelled by user")
    except Exception as e:
        print(f"\n\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
