#!/usr/bin/env python3
"""
Check the trading app from Computer Use perspective
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def run():
    print("Checking trading app from Computer Use perspective...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"Page error: {err}"))
        
        # Monitor network requests
        def log_request(request):
            if 'api' in request.url or 'stock' in request.url:
                print(f"Request: {request.method} {request.url}")
        
        def log_response(response):
            if 'api' in response.url or 'stock' in response.url:
                print(f"Response: {response.status} {response.url}")
        
        page.on("request", log_request)
        page.on("response", log_response)
        
        print("\n1. Loading app from host.docker.internal...")
        await page.goto("http://host.docker.internal:5174", wait_until='networkidle')
        
        await page.wait_for_timeout(3000)
        
        print("\n2. Checking page structure...")
        
        # Check if main components loaded
        trading_dashboard = await page.query_selector('.trading-dashboard')
        if trading_dashboard:
            print("✓ Trading dashboard loaded")
        else:
            print("✗ Trading dashboard NOT loaded")
        
        # Check chart
        chart_container = await page.query_selector('.chart-container')
        if chart_container:
            print("✓ Chart container present")
            # Check for error messages
            error_msg = await page.query_selector('.error-message')
            if error_msg:
                error_text = await error_msg.text_content()
                print(f"  ✗ Chart error: {error_text}")
        else:
            print("✗ Chart container missing")
        
        # Check Voice Assistant
        voice_panel = await page.query_selector('.voice-assistant-panel')
        if voice_panel:
            print("✓ Voice Assistant panel present")
        else:
            print("✗ Voice Assistant panel missing")
        
        # Check Market Insights
        market_insights = await page.query_selector('.market-insights-panel')
        if market_insights:
            print("✓ Market Insights panel present")
            # Count stock cards
            stock_cards = await page.query_selector_all('.stock-card')
            print(f"  Found {len(stock_cards)} stock cards")
        else:
            print("✗ Market Insights panel missing")
        
        print("\n3. Checking API calls...")
        
        # Try to make an API call directly
        api_url = await page.evaluate("""
            () => {
                if (window.getApiUrl) {
                    return window.getApiUrl();
                } else if (typeof getApiUrl !== 'undefined') {
                    return getApiUrl();
                } else {
                    return 'getApiUrl not found';
                }
            }
        """)
        print(f"API URL from page context: {api_url}")
        
        # Check window.location
        location = await page.evaluate("() => window.location.href")
        print(f"Current location: {location}")
        
        print("\n4. Testing API endpoint directly from browser...")
        
        # Try to fetch from the API
        api_response = await page.evaluate("""
            async () => {
                try {
                    const response = await fetch('http://host.docker.internal:8000/api/stock-price?symbol=PLTR');
                    const data = await response.json();
                    return { success: true, data: data };
                } catch (error) {
                    return { success: false, error: error.toString() };
                }
            }
        """)
        
        if api_response['success']:
            print(f"✓ API call successful: PLTR price = ${api_response['data'].get('price', 'N/A')}")
        else:
            print(f"✗ API call failed: {api_response['error']}")
        
        print("\n5. Checking console errors...")
        
        # Get all console errors
        console_errors = await page.evaluate("""
            () => {
                const errors = [];
                // Check if there are any error messages in the DOM
                document.querySelectorAll('.error-message, .error, [class*="error"]').forEach(el => {
                    if (el.textContent) errors.push(el.textContent);
                });
                return errors;
            }
        """)
        
        if console_errors:
            print("Found errors in UI:")
            for error in console_errors:
                print(f"  - {error}")
        
        print("\n6. Taking screenshot for analysis...")
        await page.screenshot(path="app_state_check.png")
        print("Screenshot saved as app_state_check.png")
        
        # Keep browser open for observation
        print("\nKeeping browser open for 30 seconds...")
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())