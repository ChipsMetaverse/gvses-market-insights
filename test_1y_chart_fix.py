#!/usr/bin/env python3
"""
Test script to verify 1Y chart fix - should show ~15 yearly candles instead of 3
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def test_1y_chart():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        print("Navigating to http://localhost:5174/demo")
        await page.goto('http://localhost:5174/demo')
        await page.wait_for_load_state('networkidle')

        # Dismiss onboarding overlay if present
        try:
            print("Attempting to dismiss onboarding overlay...")
            overlay = page.locator('.onboarding-overlay')
            if await overlay.is_visible():
                # Try to find and click close button
                close_button = page.locator('[class*="close"], [aria-label*="close"], button:has-text("Got it"), button:has-text("Skip")')
                if await close_button.first.is_visible(timeout=2000):
                    await close_button.first.click()
                    print("✅ Dismissed onboarding overlay")
                else:
                    # Force dismiss by clicking overlay
                    await overlay.click(force=True)
                    print("✅ Force dismissed onboarding overlay")
                await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"No onboarding overlay or couldn't dismiss: {e}")

        # Listen to network requests to capture API calls
        api_calls = []

        async def handle_request(request):
            if 'stock-history' in request.url:
                api_calls.append({
                    'url': request.url,
                    'timestamp': asyncio.get_event_loop().time()
                })
                print(f"📡 API Request: {request.url}")

        page.on('request', handle_request)

        # Find and click 1Y button
        print("\nLooking for 1Y timeframe button...")
        y1_button = page.locator('button:has-text("1Y")').first

        await y1_button.wait_for(state='visible', timeout=10000)
        print("✅ Found 1Y button")

        # Force click in case something is still blocking
        await y1_button.click(force=True)
        print("✅ Clicked 1Y button")

        # Wait for chart to update
        await page.wait_for_timeout(3000)

        # Try to extract candle count from chart or API response
        print("\nWaiting for API response...")
        await page.wait_for_timeout(2000)

        # Check API calls
        print(f"\n📊 Total API calls captured: {len(api_calls)}")
        for call in api_calls:
            print(f"   - {call['url']}")

        # Take screenshot
        screenshot_path = '/tmp/1y_chart_verification.png'
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")

        # Try to get chart data from page context
        chart_data = await page.evaluate('''() => {
            // Try to find chart instance or data
            const chartElement = document.querySelector('[data-testid="trading-chart"], .trading-chart, canvas');
            if (chartElement) {
                // Look for data in React fiber or global state
                const reactKey = Object.keys(chartElement).find(key => key.startsWith('__reactFiber'));
                if (reactKey) {
                    return { found: true, type: 'react-fiber' };
                }
            }

            // Check for any global chart data
            if (window.chartData) {
                return { found: true, data: window.chartData };
            }

            return { found: false };
        }''')

        print(f"\n📈 Chart data check: {json.dumps(chart_data, indent=2)}")

        # Check if we can see candles in the DOM
        candles_info = await page.evaluate('''() => {
            // Look for canvas elements (TradingView Lightweight Charts uses canvas)
            const canvases = Array.from(document.querySelectorAll('canvas'));
            return {
                canvasCount: canvases.length,
                canvasDimensions: canvases.map(c => ({ width: c.width, height: c.height }))
            };
        }''')

        print(f"\n🎨 Canvas info: {json.dumps(candles_info, indent=2)}")

        print("\n" + "="*80)
        print("VERIFICATION RESULTS")
        print("="*80)
        print(f"✅ Successfully clicked 1Y button")
        print(f"✅ API calls made: {len(api_calls)}")
        print(f"✅ Screenshot saved to: {screenshot_path}")
        print("\nTo verify the fix manually:")
        print("1. Open the screenshot: open /tmp/1y_chart_verification.png")
        print("2. Count the yearly candles visible on the chart")
        print("3. Expected: ~15 candles (2010-2024 for TSLA)")
        print("4. Previous bug: Only 3 candles (2023-2025)")
        print("="*80)

        # Keep browser open for manual inspection
        print("\n⏸️  Browser will stay open for 30 seconds for manual inspection...")
        await page.wait_for_timeout(30000)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_1y_chart())
