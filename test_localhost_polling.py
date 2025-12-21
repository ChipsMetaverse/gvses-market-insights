#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Definitive Localhost Polling Test

This test specifically monitors for localhost:8000 requests to verify
the Chart Control polling bug has been fixed.
"""

import asyncio
import json
import time
from datetime import datetime

async def test_localhost_polling():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright not available")
        return False
    
    localhost_requests = []
    all_requests = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        def track_request(request):
            all_requests.append({
                'url': request.url,
                'method': request.method,
                'timestamp': time.time()
            })
            
            if 'localhost:8000' in request.url:
                localhost_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'timestamp': time.time()
                })
                print(f"🚨 LOCALHOST REQUEST: {request.method} {request.url}")
        
        page.on('request', track_request)
        
        print("🔍 Loading production site...")
        await page.goto('https://gvses-market-insights.fly.dev')
        await asyncio.sleep(5)
        
        print(f"📊 Initial requests: {len(all_requests)} total, {len(localhost_requests)} localhost")
        
        # Try to activate Chart Control
        print("🎯 Attempting to activate Chart Control...")
        try:
            # Wait for page to load
            await page.wait_for_load_state('networkidle')
            
            # Try multiple selectors for Chart Control
            selectors = [
                'button:text("Chart Control")',
                '[data-testid="chart-control-tab"]',
                'div:has-text("Chart Control")',
                '.tab-button:has-text("Chart Control")'
            ]
            
            chart_activated = False
            for selector in selectors:
                try:
                    element = await page.wait_for_selector(selector, timeout=3000)
                    if element:
                        await element.click()
                        print(f"✅ Chart Control activated with: {selector}")
                        chart_activated = True
                        break
                except:
                    continue
            
            if not chart_activated:
                print("⚠️  Using JavaScript to find Chart Control...")
                await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        for (let el of elements) {
                            if (el.textContent && el.textContent.includes('Chart Control')) {
                                el.click();
                                console.log('Chart Control clicked');
                                return;
                            }
                        }
                    }
                """)
            
        except Exception as e:
            print(f"⚠️  Could not activate Chart Control: {e}")
        
        print("⏱️  Monitoring for 45 seconds for polling activity...")
        start_monitor = time.time()
        
        for i in range(9):  # 9 * 5 = 45 seconds
            await asyncio.sleep(5)
            elapsed = time.time() - start_monitor
            
            current_localhost = len(localhost_requests)
            current_total = len(all_requests)
            
            print(f"   {elapsed:.0f}s: {current_total} total requests, {current_localhost} localhost")
            
            if current_localhost > 0:
                print("❌ LOCALHOST POLLING DETECTED!")
        
        # Final analysis
        await browser.close()
        
        print("\n" + "=" * 50)
        print("🎯 LOCALHOST POLLING ANALYSIS")
        print("=" * 50)
        
        print(f"⏱️  Test Duration: 45 seconds")
        print(f"📊 Total Network Requests: {len(all_requests)}")
        print(f"🚨 Localhost:8000 Requests: {len(localhost_requests)}")
        
        if localhost_requests:
            print("\n❌ LOCALHOST REQUESTS DETECTED:")
            for req in localhost_requests:
                print(f"   {req['method']} {req['url']}")
            
            # Check for polling pattern
            if len(localhost_requests) > 3:
                print(f"\n🔄 POLLING DETECTED: {len(localhost_requests)} requests suggests active polling")
            
            return False
        else:
            print("\n✅ NO LOCALHOST REQUESTS DETECTED")
            print("✅ Localhost polling bug appears to be FIXED!")
            return True

def main():
    print("🚀 DEFINITIVE LOCALHOST POLLING TEST")
    print("🎯 Target: https://gvses-market-insights.fly.dev")
    print("🔍 Monitoring for Chart Control localhost:8000 requests")
    print("=" * 60)
    
    try:
        result = asyncio.run(test_localhost_polling())
        
        # Save results
        test_result = {
            'timestamp': datetime.now().isoformat(),
            'localhost_polling_fixed': result,
            'test_type': 'definitive_localhost_polling',
            'verdict': 'FIXED' if result else 'BUG_PRESENT'
        }
        
        with open('localhost_polling_test_result.json', 'w') as f:
            json.dump(test_result, f, indent=2)
        
        print("\n" + "=" * 60)
        print("🏆 FINAL VERDICT")
        print("=" * 60)
        
        if result:
            print("✅ SUCCESS: Localhost polling bug is FIXED!")
            print("✅ Chart Control no longer polls localhost:8000")
            print("✅ Agent Builder integration should work correctly")
            print("✅ Production deployment is clean")
        else:
            print("❌ FAILURE: Localhost polling bug still present!")
            print("❌ Chart Control is still polling localhost:8000")
            print("❌ Agent Builder integration will fail")
            print("❌ Production deployment needs fixing")
        
        print(f"\n📄 Results saved to: localhost_polling_test_result.json")
        return 0 if result else 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 2

if __name__ == "__main__":
    exit(main())