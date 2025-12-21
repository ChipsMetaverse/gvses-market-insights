#!/usr/bin/env python3
"""
Test candlestick interval accuracy for all 8 timeframe buttons.
Verifies that API responses match expected bar spacing.
"""

import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright
from typing import Dict, List, Optional

# Expected intervals for each button
EXPECTED_INTERVALS = {
    "1m": {"seconds": 60, "api_param": "1m"},
    "5m": {"seconds": 300, "api_param": "5m"},
    "15m": {"seconds": 900, "api_param": "15m"},
    "1H": {"seconds": 3600, "api_param": "1h"},
    "1D": {"seconds": 86400, "api_param": "1d"},  # 1 day
    "1Y": {"seconds": 86400, "api_param": "1d"},  # Uses daily bars
    "YTD": {"seconds": 86400, "api_param": "1d"},  # Uses daily bars
    "MAX": {"seconds": 86400, "api_param": "1d"},  # Uses daily bars
}

class IntervalTester:
    def __init__(self):
        self.results = []
        self.api_responses = {}

    async def parse_timestamp(self, ts_str: str) -> datetime:
        """Parse ISO timestamp string to datetime."""
        # Handle both 'Z' and '+00:00' timezone formats
        if ts_str.endswith('Z'):
            ts_str = ts_str[:-1] + '+00:00'
        return datetime.fromisoformat(ts_str)

    async def calculate_bar_spacing(self, bars: List[Dict], expected_seconds: int) -> Optional[Dict]:
        """Calculate average spacing between consecutive bars."""
        if len(bars) < 2:
            return None

        gaps = []
        intraday_gaps = []  # Gaps within same trading day (for hourly data)
        timestamps = []

        for i in range(min(20, len(bars) - 1)):  # Check first 20 bars for better sampling
            try:
                t1 = await self.parse_timestamp(bars[i]["timestamp"])
                t2 = await self.parse_timestamp(bars[i + 1]["timestamp"])
                gap_seconds = abs((t2 - t1).total_seconds())
                gaps.append(gap_seconds)
                timestamps.append((bars[i]["timestamp"], bars[i + 1]["timestamp"]))

                # For intraday intervals (< 1 day), track gaps that are close to expected
                # This filters out weekend/holiday gaps for hourly data
                if expected_seconds < 86400:
                    # Accept gaps within 2x of expected (e.g., 1H-2H for hourly)
                    if gap_seconds <= expected_seconds * 2:
                        intraday_gaps.append(gap_seconds)
            except Exception as e:
                print(f"Error parsing timestamps: {e}")
                continue

        if not gaps:
            return None

        # Use intraday gaps for better accuracy if we have enough samples
        relevant_gaps = intraday_gaps if len(intraday_gaps) >= 5 else gaps

        avg_gap = sum(relevant_gaps) / len(relevant_gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)

        return {
            "average": avg_gap,
            "min": min_gap,
            "max": max_gap,
            "count": len(gaps),
            "intraday_count": len(intraday_gaps),
            "sample_timestamps": timestamps[:5]  # Show 5 samples
        }

    async def test_interval(self, page, button_text: str) -> Dict:
        """Test a single interval button."""
        print(f"\n{'='*60}")
        print(f"Testing: {button_text}")
        print(f"{'='*60}")

        expected = EXPECTED_INTERVALS[button_text]

        # Set up request interception
        api_response = None

        async def handle_response(response):
            nonlocal api_response
            if "/api/intraday" in response.url or "/api/stock-history" in response.url:
                try:
                    data = await response.json()
                    api_response = {
                        "url": response.url,
                        "status": response.status,
                        "data": data
                    }
                except Exception as e:
                    print(f"Error capturing response: {e}")

        page.on("response", handle_response)

        # Click the button using exact text match
        try:
            # Use get_by_role for exact text matching
            button = page.get_by_role("button", name=button_text, exact=True)
            await button.wait_for(state="visible", timeout=5000)

            # Force click to bypass any overlays
            await button.click(force=True)
            print(f"Clicked {button_text} button")
        except Exception as e:
            print(f"Error clicking button: {e}")
            return {
                "button": button_text,
                "status": "❌ BUTTON_NOT_FOUND",
                "error": str(e)
            }

        # Wait for API response (increased timeout)
        for i in range(100):  # Wait up to 10 seconds
            if api_response:
                break
            if i % 10 == 0 and i > 0:
                print(f"  Still waiting for API response... ({i/10}s)")
            await asyncio.sleep(0.1)

        if not api_response:
            return {
                "button": button_text,
                "expected_interval": f"{expected['seconds']}s",
                "api_param": expected['api_param'],
                "status": "❌ NO_API_RESPONSE"
            }

        # Extract interval parameter from URL
        url = api_response["url"]
        actual_api_param = None
        if "interval=" in url:
            actual_api_param = url.split("interval=")[1].split("&")[0]

        # Analyze bar spacing
        bars = api_response["data"].get("bars", [])
        if not bars:
            return {
                "button": button_text,
                "expected_interval": f"{expected['seconds']}s",
                "api_param": expected['api_param'],
                "actual_api_param": actual_api_param,
                "status": "❌ NO_BARS_IN_RESPONSE",
                "bar_count": 0
            }

        spacing = await self.calculate_bar_spacing(bars, expected['seconds'])

        if not spacing:
            return {
                "button": button_text,
                "expected_interval": f"{expected['seconds']}s",
                "api_param": expected['api_param'],
                "actual_api_param": actual_api_param,
                "status": "❌ COULD_NOT_CALCULATE_SPACING",
                "bar_count": len(bars)
            }

        # Check if spacing matches expected (within 10% tolerance for intraday, exact for daily)
        avg_gap = spacing["average"]
        expected_seconds = expected["seconds"]

        # For daily bars, allow for weekend gaps (2-3 days)
        if expected_seconds == 86400:  # Daily bars
            # Accept gaps of 1-4 days (accounts for weekends)
            tolerance = 3 * 86400  # 3 days
            is_correct = 86400 <= avg_gap <= 4 * 86400
        else:
            # For intraday, use 10% tolerance
            tolerance = expected_seconds * 0.1
            is_correct = abs(avg_gap - expected_seconds) <= tolerance

        # Check API parameter matches
        api_param_correct = actual_api_param == expected['api_param']

        status = "✅ PASS" if (is_correct and api_param_correct) else "❌ FAIL"

        result = {
            "button": button_text,
            "expected_interval": f"{expected_seconds}s",
            "api_param": expected['api_param'],
            "actual_api_param": actual_api_param,
            "actual_bar_spacing": f"{avg_gap:.1f}s",
            "spacing_details": {
                "average": f"{avg_gap:.1f}s",
                "min": f"{spacing['min']:.1f}s",
                "max": f"{spacing['max']:.1f}s",
                "sample_count": spacing['count']
            },
            "sample_timestamps": spacing['sample_timestamps'],
            "bar_count": len(bars),
            "api_param_match": "✅" if api_param_correct else "❌",
            "spacing_match": "✅" if is_correct else "❌",
            "status": status
        }

        # Store API response for debugging
        self.api_responses[button_text] = api_response

        print(f"\nResults for {button_text}:")
        print(f"  Expected: {expected_seconds}s interval")
        print(f"  API Param: {actual_api_param} (expected: {expected['api_param']}) {result['api_param_match']}")
        print(f"  Actual Spacing: {avg_gap:.1f}s (min: {spacing['min']:.1f}s, max: {spacing['max']:.1f}s) {result['spacing_match']}")
        if spacing.get('intraday_count', 0) > 0:
            print(f"  Intraday Samples: {spacing['intraday_count']} (filtered from {spacing['count']} total)")
        print(f"  Bar Count: {len(bars)}")
        print(f"  Sample Timestamps:")
        for ts1, ts2 in spacing['sample_timestamps']:
            t1 = await self.parse_timestamp(ts1)
            t2 = await self.parse_timestamp(ts2)
            gap = (t2 - t1).total_seconds()
            print(f"    {ts1} → {ts2} ({gap:.0f}s)")
        print(f"  Status: {status}")

        return result

    async def run_all_tests(self):
        """Run tests for all intervals."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            # Navigate to demo page
            print("Navigating to http://localhost:5174/demo")
            await page.goto("http://localhost:5174/demo", wait_until="networkidle")
            await asyncio.sleep(2)  # Wait for initial load

            # Dismiss onboarding overlay if present
            try:
                # Try clicking "Got it" or "Next" button
                got_it_button = page.locator('button:has-text("Got it"), button:has-text("Next"), button:has-text("Skip")')
                if await got_it_button.count() > 0:
                    print("Dismissing onboarding overlay...")
                    await got_it_button.first.click()
                    await asyncio.sleep(0.5)

                # If there's an overlay div, try pressing Escape
                overlay = page.locator('.onboarding-overlay, .onboarding-tooltip')
                if await overlay.count() > 0:
                    print("Pressing Escape to dismiss overlay...")
                    await page.keyboard.press('Escape')
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Note: Could not dismiss overlay (may not exist): {e}")

            # Test each interval
            for button_text in EXPECTED_INTERVALS.keys():
                result = await self.test_interval(page, button_text)
                self.results.append(result)
                await asyncio.sleep(1)  # Brief pause between tests

            await browser.close()

    def print_summary_table(self):
        """Print results in a formatted table."""
        print("\n" + "="*120)
        print("INTERVAL ACCURACY VERIFICATION RESULTS")
        print("="*120)
        print(f"{'Button':<8} {'Expected':<15} {'API Param':<12} {'Actual Spacing':<20} {'Bars':<8} {'API ✓':<8} {'Spacing ✓':<12} {'Status':<10}")
        print("-"*120)

        for result in self.results:
            button = result.get("button", "?")
            expected = result.get("expected_interval", "?")
            api_param = result.get("actual_api_param", "?")
            spacing = result.get("actual_bar_spacing", "?")
            bars = result.get("bar_count", 0)
            api_match = result.get("api_param_match", "?")
            spacing_match = result.get("spacing_match", "?")
            status = result.get("status", "?")

            print(f"{button:<8} {expected:<15} {api_param:<12} {spacing:<20} {bars:<8} {api_match:<8} {spacing_match:<12} {status:<10}")

        print("="*120)

        # Summary statistics
        passed = sum(1 for r in self.results if "PASS" in r.get("status", ""))
        failed = sum(1 for r in self.results if "FAIL" in r.get("status", ""))

        print(f"\nSummary: {passed} PASSED, {failed} FAILED out of {len(self.results)} tests")
        print("="*120)

    def save_detailed_report(self, filename="interval_test_report.json"):
        """Save detailed results to JSON file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if "PASS" in r.get("status", "")),
                "failed": sum(1 for r in self.results if "FAIL" in r.get("status", ""))
            },
            "results": self.results
        }

        filepath = f"/Volumes/WD My Passport 264F Media/claude-voice-mcp/{filename}"
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nDetailed report saved to: {filename}")

async def main():
    """Main test execution."""
    tester = IntervalTester()

    print("Starting interval accuracy verification...")
    print("This will test all 8 timeframe buttons (1m, 5m, 15m, 1H, 1D, 1Y, YTD, MAX)")
    print("\nMake sure:")
    print("  1. Frontend is running on http://localhost:5174")
    print("  2. Backend is running on http://localhost:8000")
    print("  3. /demo page is accessible\n")

    await tester.run_all_tests()
    tester.print_summary_table()
    tester.save_detailed_report()

if __name__ == "__main__":
    asyncio.run(main())
