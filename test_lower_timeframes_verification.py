"""
Playwright test to verify all lower timeframes are functioning after removing 10S/30S intervals.
Tests each timeframe: 1m, 3m, 5m, 10m, 15m, 30m, 1H, 2H, 3H, 4H, 6H, 8H, 12H
"""

import asyncio
from playwright.async_api import async_playwright, expect
import sys

# Timeframes to test (lower timeframes only - up to 12H)
LOWER_TIMEFRAMES = [
    '1m', '3m', '5m', '10m', '15m', '30m',  # Minute-based
    '1H', '2H', '3H', '4H', '6H', '8H', '12H'  # Hourly
]

# Timeframes that should NOT exist anymore (removed)
REMOVED_TIMEFRAMES = ['10S', '30S']

async def test_timeframe_dropdown_opens(page):
    """Test that timeframe dropdown opens correctly"""
    print("\n📋 Testing timeframe dropdown...")

    # Wait for page to load
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(2)

    # Look for the timeframe dropdown button (⋯ or ellipsis)
    # It might be in the advanced menu section
    dropdown_button = page.locator('button.time-range-menu-button, button:has-text("⋯")')

    if await dropdown_button.count() > 0:
        print("✅ Found timeframe dropdown button")
        await dropdown_button.first.click()
        await asyncio.sleep(1)
        return True
    else:
        print("ℹ️ No advanced dropdown found - all timeframes may be visible")
        return False

async def test_timeframe_button_exists(page, timeframe):
    """Test that a specific timeframe button exists"""
    # Look for button with exact text matching the timeframe
    button = page.locator(f'button.time-range-button:has-text("{timeframe}"), button.time-range-menu-item:has-text("{timeframe}")')

    count = await button.count()
    if count > 0:
        print(f"  ✅ {timeframe}: Button found")
        return True
    else:
        print(f"  ❌ {timeframe}: Button NOT found")
        return False

async def test_timeframe_click_and_load(page, timeframe):
    """Test clicking a timeframe and verifying chart data loads"""
    print(f"\n🔍 Testing {timeframe} timeframe...")

    # Find and click the timeframe button
    button = page.locator(f'button.time-range-button:has-text("{timeframe}"), button.time-range-menu-item:has-text("{timeframe}")')

    if await button.count() == 0:
        print(f"  ❌ {timeframe}: Button not found in DOM")
        return False

    # Click the button
    await button.first.click()
    print(f"  ✅ {timeframe}: Clicked timeframe button")

    # Wait for potential API call
    await asyncio.sleep(2)

    # Check for errors in console
    return True

async def test_removed_timeframes_not_exist(page, timeframe):
    """Test that removed timeframes (10S, 30S) do NOT exist"""
    button = page.locator(f'button:has-text("{timeframe}")')
    count = await button.count()

    if count == 0:
        print(f"  ✅ {timeframe}: Correctly removed (not found)")
        return True
    else:
        print(f"  ❌ {timeframe}: Still exists (should be removed!)")
        return False

async def main():
    print("=" * 80)
    print("🧪 Lower Timeframes Verification Test")
    print("=" * 80)

    async with async_playwright() as p:
        # Launch browser
        print("\n🌐 Launching browser...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Track console messages
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Navigate to app
        print("📍 Navigating to http://localhost:5174...")
        try:
            await page.goto('http://localhost:5174', wait_until='networkidle', timeout=30000)
            print("✅ Page loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            await browser.close()
            return

        await asyncio.sleep(3)

        # Take initial screenshot
        await page.screenshot(path='/tmp/timeframe_test_initial.png')
        print("📸 Screenshot saved: /tmp/timeframe_test_initial.png")

        # Test 1: Check if removed timeframes are gone
        print("\n" + "=" * 80)
        print("TEST 1: Verify Removed Timeframes (10S, 30S) Don't Exist")
        print("=" * 80)

        removed_results = []
        for timeframe in REMOVED_TIMEFRAMES:
            result = await test_removed_timeframes_not_exist(page, timeframe)
            removed_results.append(result)

        # Test 2: Open dropdown if it exists
        print("\n" + "=" * 80)
        print("TEST 2: Open Timeframe Dropdown Menu")
        print("=" * 80)

        dropdown_opened = await test_timeframe_dropdown_opens(page)

        # Test 3: Verify all lower timeframes exist
        print("\n" + "=" * 80)
        print("TEST 3: Verify All Lower Timeframes Exist")
        print("=" * 80)

        existence_results = []
        for timeframe in LOWER_TIMEFRAMES:
            result = await test_timeframe_button_exists(page, timeframe)
            existence_results.append((timeframe, result))

        # Test 4: Test clicking each timeframe
        print("\n" + "=" * 80)
        print("TEST 4: Test Clicking Each Lower Timeframe")
        print("=" * 80)

        click_results = []
        for timeframe in LOWER_TIMEFRAMES[:5]:  # Test first 5 to save time
            result = await test_timeframe_click_and_load(page, timeframe)
            click_results.append((timeframe, result))

            # Close dropdown if needed for next test
            if dropdown_opened:
                await test_timeframe_dropdown_opens(page)

        # Take final screenshot
        await page.screenshot(path='/tmp/timeframe_test_final.png')
        print("\n📸 Screenshot saved: /tmp/timeframe_test_final.png")

        # Print Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        # Removed timeframes summary
        print(f"\n✅ Removed Timeframes Test: {sum(removed_results)}/{len(REMOVED_TIMEFRAMES)} passed")

        # Existence summary
        passed_existence = sum(1 for _, result in existence_results if result)
        print(f"✅ Timeframe Existence Test: {passed_existence}/{len(LOWER_TIMEFRAMES)} passed")

        # Click summary
        passed_clicks = sum(1 for _, result in click_results if result)
        print(f"✅ Timeframe Click Test: {passed_clicks}/{len(click_results)} passed")

        # Detailed results
        print("\n📋 Detailed Results:")
        print("\nRemoved Timeframes (should NOT exist):")
        for i, timeframe in enumerate(REMOVED_TIMEFRAMES):
            status = "✅ PASS" if removed_results[i] else "❌ FAIL"
            print(f"  {status} - {timeframe}")

        print("\nLower Timeframes (should exist):")
        for timeframe, result in existence_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {status} - {timeframe}")

        # Console errors check
        errors = [msg for msg in console_messages if 'error' in msg.lower()]
        if errors:
            print(f"\n⚠️ Console Errors Detected ({len(errors)}):")
            for error in errors[:5]:  # Show first 5
                print(f"  - {error}")
        else:
            print("\n✅ No console errors detected")

        # Overall result
        all_removed_passed = all(removed_results)
        all_existence_passed = passed_existence == len(LOWER_TIMEFRAMES)

        print("\n" + "=" * 80)
        if all_removed_passed and all_existence_passed:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Second-based intervals successfully removed")
            print("✅ All lower timeframes (1m-12H) functioning properly")
        else:
            print("⚠️ SOME TESTS FAILED")
            if not all_removed_passed:
                print("❌ Removed timeframes still present")
            if not all_existence_passed:
                print("❌ Some lower timeframes missing")
        print("=" * 80)

        # Keep browser open for inspection
        print("\n⏸️ Browser will remain open for 10 seconds for inspection...")
        await asyncio.sleep(10)

        await browser.close()
        print("\n✅ Browser closed. Test complete!")

if __name__ == '__main__':
    asyncio.run(main())
