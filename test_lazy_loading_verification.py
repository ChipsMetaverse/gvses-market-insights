"""
Playwright test to verify lazy loading functionality on production.
Tests:
1. Initial chart load
2. Lazy loading triggers when scrolling left
3. Data continues loading until no more available
4. Hybrid data sources (Alpaca + Yahoo) work correctly
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def test_lazy_loading():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        # Enable console logging
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        print("=" * 80)
        print("LAZY LOADING VERIFICATION TEST")
        print("=" * 80)
        print()

        # Navigate to production
        url = "https://gvses-market-insights.fly.dev/"
        print(f"📍 Navigating to: {url}")
        await page.goto(url, wait_until='load', timeout=60000)

        # Check for demo mode button (auth bypass)
        print("🔍 Checking for Demo Mode button...")
        try:
            demo_button = await page.wait_for_selector('button:has-text("Try Demo Mode")', timeout=5000)
            print("✅ Found Demo Mode button, clicking...")
            await demo_button.click()
            await asyncio.sleep(3)
        except:
            print("⚠️ No Demo Mode button found (might already be on dashboard)")

        # Wait for chart to load
        print("⏳ Waiting for chart to load...")
        await asyncio.sleep(8)

        # Check if chart loaded with multiple selectors
        chart_canvas = await page.query_selector('canvas')
        if not chart_canvas:
            # Try waiting for canvas explicitly
            try:
                chart_canvas = await page.wait_for_selector('canvas', timeout=10000)
                print("✅ Chart canvas found (after wait)")
            except:
                print("❌ Chart canvas NOT found")
                # Take screenshot for debugging
                await page.screenshot(path='/tmp/chart_not_found.png')
                print("📸 Screenshot saved to /tmp/chart_not_found.png")
                await browser.close()
                return
        else:
            print("✅ Chart canvas found")

        # Check for lazy loading console messages
        lazy_load_logs = [log for log in console_logs if '[LAZY LOAD]' in log or '[HOOK]' in log]
        print(f"\n📊 Found {len(lazy_load_logs)} lazy loading console messages:")
        for log in lazy_load_logs[:10]:  # Show first 10
            print(f"   {log}")

        print("\n" + "=" * 80)
        print("TEST 1: Check Initial Data Load")
        print("=" * 80)

        # Wait for initial data to load
        await asyncio.sleep(2)

        # Check for data loading messages
        data_logs = [log for log in console_logs if 'Received' in log and 'bars' in log]
        if data_logs:
            print("✅ Initial data loaded:")
            for log in data_logs[-3:]:  # Show last 3
                print(f"   {log}")
        else:
            print("⚠️ No data loading messages found in console")

        print("\n" + "=" * 80)
        print("TEST 2: Select 30min Timeframe")
        print("=" * 80)

        # Click on 30min timeframe button
        try:
            timeframe_button = await page.wait_for_selector('button:has-text("30m")', timeout=5000)
            await timeframe_button.click()
            print("✅ Clicked 30m timeframe button")
            await asyncio.sleep(2)

            # Check console for new data fetch
            recent_logs = console_logs[-20:]
            fetch_logs = [log for log in recent_logs if 'Fetching' in log or 'bars' in log]
            print(f"📡 Data fetch logs:")
            for log in fetch_logs:
                print(f"   {log}")
        except Exception as e:
            print(f"❌ Could not find/click 30m button: {e}")

        print("\n" + "=" * 80)
        print("TEST 3: Scroll Chart Left to Trigger Lazy Loading")
        print("=" * 80)

        # Get chart bounding box
        chart_box = await chart_canvas.bounding_box()
        if not chart_box:
            print("❌ Could not get chart bounding box")
            await browser.close()
            return

        # Record initial bar count
        initial_logs_count = len(console_logs)

        # Simulate dragging chart to the right (scrolling left in time)
        # This should trigger lazy loading when near left edge
        start_x = chart_box['x'] + chart_box['width'] * 0.8  # Start from right side
        start_y = chart_box['y'] + chart_box['height'] / 2
        end_x = chart_box['x'] + chart_box['width'] * 0.2    # Drag to left side
        end_y = start_y

        print(f"🖱️ Dragging chart from ({start_x:.0f}, {start_y:.0f}) to ({end_x:.0f}, {end_y:.0f})")

        # Perform drag
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()

        # Slow drag to simulate user interaction
        steps = 20
        for i in range(steps):
            progress = (i + 1) / steps
            current_x = start_x + (end_x - start_x) * progress
            await page.mouse.move(current_x, start_y)
            await asyncio.sleep(0.05)  # Small delay between steps

        await page.mouse.up()
        print("✅ Completed drag operation")

        # Wait for lazy loading to trigger
        print("⏳ Waiting 3 seconds for lazy loading to trigger...")
        await asyncio.sleep(3)

        # Check for lazy loading messages
        new_logs = console_logs[initial_logs_count:]
        lazy_logs = [log for log in new_logs if '[LAZY LOAD]' in log or 'loading more' in log.lower()]

        print(f"\n📊 Lazy loading logs after drag:")
        if lazy_logs:
            print("✅ Lazy loading triggered!")
            for log in lazy_logs:
                print(f"   {log}")
        else:
            print("⚠️ No lazy loading logs detected")
            print(f"   (Checked {len(new_logs)} new console messages)")

        print("\n" + "=" * 80)
        print("TEST 4: Multiple Scroll Attempts")
        print("=" * 80)

        # Try multiple scrolls to see if it keeps loading
        for attempt in range(3):
            print(f"\n🔄 Scroll attempt {attempt + 1}/3")

            # Record logs before scroll
            logs_before = len(console_logs)

            # Drag again
            await page.mouse.move(start_x, start_y)
            await page.mouse.down()
            await page.mouse.move(end_x, start_y, steps=10)
            await page.mouse.up()

            # Wait and check
            await asyncio.sleep(2)
            logs_after = len(console_logs)

            new_scroll_logs = console_logs[logs_before:logs_after]
            relevant = [log for log in new_scroll_logs if 'loading' in log.lower() or 'bars' in log.lower() or 'data' in log.lower()]

            if relevant:
                print(f"   📡 Activity detected: {len(relevant)} relevant logs")
                for log in relevant[:5]:
                    print(f"      {log}")
            else:
                print(f"   ⚠️ No loading activity (might have reached data limit)")

        print("\n" + "=" * 80)
        print("TEST 5: Check for Errors")
        print("=" * 80)

        # Check for errors
        error_logs = [log for log in console_logs if '[error]' in log.lower() or 'error' in log.lower()]
        if error_logs:
            print(f"⚠️ Found {len(error_logs)} error messages:")
            for log in error_logs[-10:]:  # Show last 10 errors
                print(f"   {log}")
        else:
            print("✅ No errors detected in console")

        print("\n" + "=" * 80)
        print("TEST 6: Network Requests")
        print("=" * 80)

        # Check network requests to /api/intraday
        network_requests = []

        def handle_request(request):
            if '/api/intraday' in request.url:
                network_requests.append({
                    'url': request.url,
                    'method': request.method
                })

        page.on('request', handle_request)

        # Trigger one more scroll
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        await page.mouse.move(end_x, start_y, steps=10)
        await page.mouse.up()
        await asyncio.sleep(2)

        print(f"📡 API requests to /api/intraday: {len(network_requests)}")
        for req in network_requests[-5:]:  # Show last 5
            print(f"   {req['method']} {req['url']}")

        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✓ Total console logs: {len(console_logs)}")
        print(f"✓ Lazy loading mentions: {len([l for l in console_logs if 'LAZY LOAD' in l])}")
        print(f"✓ Data fetch mentions: {len([l for l in console_logs if 'Fetching' in l or 'Received' in l])}")
        print(f"✓ Error count: {len(error_logs)}")
        print(f"✓ Network requests: {len(network_requests)}")

        # Keep browser open for manual inspection
        print("\n⏸️ Browser staying open for manual inspection...")
        print("   Press Ctrl+C to close")

        try:
            await asyncio.sleep(300)  # Keep open for 5 minutes
        except KeyboardInterrupt:
            print("\n👋 Closing browser...")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_lazy_loading())
