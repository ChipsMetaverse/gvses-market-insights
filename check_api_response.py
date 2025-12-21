from playwright.sync_api import sync_playwright
import json
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Track network requests
    api_responses = []
    
    def handle_response(response):
        if '/api/intraday' in response.url:
            try:
                body = response.json()
                api_responses.append({
                    'url': response.url,
                    'status': response.status,
                    'bars_count': len(body.get('bars', [])),
                    'first_bar': body['bars'][0] if body.get('bars') else None,
                    'last_bar': body['bars'][-1] if body.get('bars') else None,
                })
                print("\n=== API Response ===")
                print("URL:", response.url)
                print("Bars Count:", len(body.get('bars', [])))
                if body.get('bars'):
                    print("First Bar:", body['bars'][0])
                    print("Last Bar:", body['bars'][-1])
            except:
                pass
    
    page.on('response', handle_response)
    
    # Navigate to production
    print("Opening production site...")
    page.goto('https://gvses-market-insights.fly.dev/demo')
    
    # Wait for TSLA to load
    print("Waiting for TSLA to load...")
    page.wait_for_timeout(3000)
    
    # Click NVDA
    print("Clicking NVDA...")
    page.click('text=NVDA')
    page.wait_for_timeout(2000)
    
    # Click MAX button
    print("Clicking MAX button...")
    page.click('text=MAX')
    
    # Wait for data to load
    print("Waiting for MAX data to load...")
    page.wait_for_timeout(5000)
    
    print("\n=== Summary ===")
    print("Total API calls captured:", len(api_responses))
    for resp in api_responses:
        print("\nURL:", resp['url'])
        print("Bars:", resp['bars_count'])
    
    browser.close()
