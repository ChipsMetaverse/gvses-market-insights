#!/usr/bin/env python3
"""
Focused test for the 3 failing intervals: 15m, 1D, MAX
"""

import asyncio
from playwright.async_api import async_playwright

async def test_button(page, button_name: str):
    """Test a single button and print the API call."""
    print(f"\n{'='*60}")
    print(f"Testing: {button_name}")
    print(f"{'='*60}")

    api_calls = []

    async def capture_request(request):
        if "/api/intraday" in request.url or "/api/stock-history" in request.url:
            api_calls.append({
                "url": request.url,
                "method": request.method
            })
            print(f"  API Request: {request.method} {request.url}")

    async def capture_response(response):
        if "/api/intraday" in response.url or "/api/stock-history" in response.url:
            try:
                data = await response.json()
                bars = data.get('bars', [])
                print(f"  API Response: {response.status} - {len(bars)} bars")
                if len(bars) > 0:
                    print(f"    First bar: {bars[0].get('timestamp')}")
                    if len(bars) > 1:
                        print(f"    Second bar: {bars[1].get('timestamp')}")
            except Exception as e:
                print(f"  Response error: {e}")

    page.on("request", capture_request)
    page.on("response", capture_response)

    # Click the button
    try:
        button = page.get_by_role("button", name=button_name, exact=True)
        await button.click(force=True)
        print(f"  Clicked {button_name}")

        # Wait for API response
        await asyncio.sleep(5)

        if not api_calls:
            print(f"  ❌ NO API CALL DETECTED")

    except Exception as e:
        print(f"  ❌ Error: {e}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        # Navigate
        print("Navigating to http://localhost:5174/demo")
        await page.goto("http://localhost:5174/demo", wait_until="networkidle")
        await asyncio.sleep(3)

        # Test each failing button
        for button in ['15m', '1D', 'MAX']:
            await test_button(page, button)
            await asyncio.sleep(2)

        print("\n" + "="*60)
        print("Test complete - check output above")
        print("="*60)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
