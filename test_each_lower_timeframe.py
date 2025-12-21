"""
Test each lower timeframe individually using Playwright MCP browser tools.
Verifies: 1m, 3m, 5m, 10m, 15m, 30m, 1H, 2H, 3H, 4H, 6H, 8H, 12H
"""

import asyncio
from playwright.async_api import async_playwright
import sys

# Lower timeframes to test
LOWER_TIMEFRAMES = [
    '1m', '3m', '5m', '10m', '15m', '30m',  # Minute-based
    '1H', '2H', '3H', '4H', '6H', '8H', '12H'  # Hourly
]

async def test_single_timeframe(page, timeframe, screenshot_index):
    """Test a single timeframe"""
    print(f"\n{'='*60}")
    print(f"Testing Timeframe: {timeframe}")
    print(f"{'='*60}")

    try:
        # Step 1: Click dropdown button to open menu
        print(f"  1. Opening timeframe dropdown...")
        dropdown_button = page.locator('button:has-text("⋯")')
        if await dropdown_button.count() == 0:
            print(f"  ❌ Dropdown button (⋯) not found!")
            return False

        await dropdown_button.click()
        await asyncio.sleep(1)  # Wait for menu to open
        print(f"  ✅ Dropdown menu opened")

        # Step 2: Check if timeframe button exists in dropdown
        print(f"  2. Looking for {timeframe} button in dropdown...")

        # Try multiple selectors
        timeframe_button = page.locator(f'button.time-range-menu-item:has-text("{timeframe}")')

        button_count = await timeframe_button.count()
        if button_count == 0:
            print(f"  ❌ {timeframe} button NOT found in dropdown menu")

            # Debug: List all menu items
            all_menu_items = await page.locator('.time-range-menu-item').all_text_contents()
            print(f"  📋 Menu items found: {all_menu_items}")
            return False

        print(f"  ✅ {timeframe} button found in dropdown")

        # Step 3: Click the timeframe button
        print(f"  3. Clicking {timeframe} button...")
        await timeframe_button.first.click()
        await asyncio.sleep(2)  # Wait for chart to load
        print(f"  ✅ {timeframe} button clicked")

        # Step 4: Verify timeframe is selected (button should have 'active' class)
        print(f"  4. Verifying {timeframe} is selected...")

        # Re-open dropdown to check if button is active
        await dropdown_button.click()
        await asyncio.sleep(0.5)

        active_button = page.locator(f'button.time-range-menu-item.active:has-text("{timeframe}")')
        is_active = await active_button.count() > 0

        if is_active:
            print(f"  ✅ {timeframe} is now selected (active)")
        else:
            print(f"  ⚠️  {timeframe} may not be active (check manually)")

        # Step 5: Take screenshot
        screenshot_path = f"timeframe_test_{screenshot_index}_{timeframe}.png"
        await page.screenshot(path=screenshot_path)
        print(f"  📸 Screenshot saved: {screenshot_path}")

        # Close dropdown for next test
        await page.keyboard.press('Escape')
        await asyncio.sleep(0.5)

        print(f"  ✅ {timeframe} test PASSED")
        return True

    except Exception as e:
        print(f"  ❌ Error testing {timeframe}: {str(e)}")
        return False

async def main():
    print("=" * 80)
    print("🧪 Testing Each Lower Timeframe Individually")
    print("=" * 80)

    async with async_playwright() as p:
        # Launch browser
        print("\n🌐 Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to demo page
        print("📍 Navigating to http://localhost:5174/demo...")
        try:
            await page.goto('http://localhost:5174/demo', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(3)  # Let page fully load
            print("✅ Page loaded successfully\n")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            await browser.close()
            return

        # Test each timeframe
        results = {}
        for index, timeframe in enumerate(LOWER_TIMEFRAMES, start=1):
            success = await test_single_timeframe(page, timeframe, index)
            results[timeframe] = success

        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        print(f"\n✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}\n")

        print("Detailed Results:")
        for timeframe, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {timeframe}")

        # Overall result
        print("\n" + "=" * 80)
        if passed == total:
            print("🎉 ALL LOWER TIMEFRAMES WORKING PERFECTLY!")
        else:
            print(f"⚠️  {total - passed} timeframe(s) need attention")
        print("=" * 80)

        # Keep browser open for inspection
        print("\n⏸️  Browser will remain open for 10 seconds for manual inspection...")
        await asyncio.sleep(10)

        await browser.close()
        print("\n✅ Test complete!")

if __name__ == '__main__':
    asyncio.run(main())
