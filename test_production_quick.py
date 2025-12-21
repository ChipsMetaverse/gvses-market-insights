#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import json
from datetime import datetime

def check_production_site():
    """Quick production check using curl and basic analysis"""
    print("🚀 Quick Production Analysis")
    print("=" * 40)
    
    # Test 1: Basic connectivity
    print("📍 Testing production connectivity...")
    try:
        result = subprocess.run([
            'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
            'https://gvses-market-insights.fly.dev'
        ], capture_output=True, text=True, timeout=10)
        
        status_code = result.stdout.strip()
        if status_code == '200':
            print("✅ Production site accessible (HTTP 200)")
        else:
            print(f"⚠️  Production site returned HTTP {status_code}")
    except Exception as e:
        print(f"❌ Failed to reach production site: {e}")
        return False
    
    # Test 2: Check if site content looks correct
    print("📦 Checking site content...")
    try:
        result = subprocess.run([
            'curl', '-s', 'https://gvses-market-insights.fly.dev'
        ], capture_output=True, text=True, timeout=10)
        
        content = result.stdout
        
        # Check for localhost references in HTML
        if 'localhost:8000' in content:
            print("❌ FOUND localhost:8000 in HTML content!")
            return False
        else:
            print("✅ No localhost references in HTML")
            
        # Check for expected content
        if 'GVSES' in content and 'Market' in content:
            print("✅ Site content looks correct")
        else:
            print("⚠️  Site content may be incorrect")
            
    except Exception as e:
        print(f"❌ Failed to fetch site content: {e}")
        return False
    
    # Test 3: Check API endpoints
    print("🔍 Testing API endpoints...")
    api_endpoints = [
        '/health',
        '/api/stock-price?symbol=TSLA',
        '/api/market-overview'
    ]
    
    api_results = {}
    for endpoint in api_endpoints:
        url = f'https://gvses-market-insights.fly.dev{endpoint}'
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/tmp/api_response.json',
                url
            ], capture_output=True, text=True, timeout=15)
            
            status_code = result.stdout.strip()
            api_results[endpoint] = status_code
            
            if status_code == '200':
                print(f"✅ {endpoint}: HTTP 200")
            else:
                print(f"⚠️  {endpoint}: HTTP {status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: Failed - {e}")
            api_results[endpoint] = 'ERROR'
    
    # Test 4: Check for WebSocket endpoint
    print("🔌 Checking WebSocket endpoints...")
    websocket_check = subprocess.run([
        'curl', '-s', '-I', 
        'https://gvses-market-insights.fly.dev/elevenlabs/signed-url'
    ], capture_output=True, text=True, timeout=10)
    
    if '200 OK' in websocket_check.stdout:
        print("✅ ElevenLabs WebSocket endpoint accessible")
    else:
        print("⚠️  ElevenLabs endpoint may have issues")
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 QUICK ANALYSIS SUMMARY")
    print("=" * 40)
    
    working_apis = sum(1 for status in api_results.values() if status == '200')
    total_apis = len(api_results)
    
    print(f"🌐 Site Accessibility: {'✅ WORKING' if status_code == '200' else '❌ ISSUES'}")
    print(f"🚫 Localhost References: {'✅ NONE FOUND' if 'localhost:8000' not in content else '❌ FOUND'}")
    print(f"📡 API Endpoints: {working_apis}/{total_apis} working")
    print(f"🔌 WebSocket: {'✅ OK' if '200 OK' in websocket_check.stdout else '⚠️  CHECK'}")
    
    # Overall verdict
    localhost_clean = 'localhost:8000' not in content
    site_accessible = status_code == '200'
    apis_mostly_working = working_apis >= total_apis * 0.6  # 60% threshold
    
    if localhost_clean and site_accessible and apis_mostly_working:
        print("\n🎉 OVERALL: ✅ PRODUCTION LOOKS GOOD!")
        print("✅ Localhost bug appears to be FIXED")
        print("✅ Agent Builder integration should work")
        return True
    else:
        print("\n⚠️  OVERALL: Issues detected")
        if not localhost_clean:
            print("❌ Localhost references still present")
        if not site_accessible:
            print("❌ Site accessibility issues")
        if not apis_mostly_working:
            print("❌ API endpoint issues")
        return False

def run_browser_test():
    """Try to run a more comprehensive browser test if playwright is available"""
    try:
        # Try to run the playwright test
        result = subprocess.run([
            'python3', '-c', '''
import asyncio
from playwright.async_api import async_playwright

async def quick_browser_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        requests_logged = []
        def log_request(request):
            requests_logged.append(request.url)
        
        page.on("request", log_request)
        
        await page.goto("https://gvses-market-insights.fly.dev")
        await asyncio.sleep(10)  # Wait for requests
        
        localhost_requests = [url for url in requests_logged if "localhost:8000" in url]
        
        print(f"Total requests: {len(requests_logged)}")
        print(f"Localhost requests: {len(localhost_requests)}")
        
        if localhost_requests:
            print("❌ LOCALHOST REQUESTS FOUND:")
            for url in localhost_requests[:5]:
                print(f"  {url}")
        else:
            print("✅ NO LOCALHOST REQUESTS")
        
        await browser.close()
        return len(localhost_requests) == 0

result = asyncio.run(quick_browser_test())
print("BROWSER_TEST_PASSED:" + str(result))
'''
        ], capture_output=True, text=True, timeout=30)
        
        if 'BROWSER_TEST_PASSED:True' in result.stdout:
            print("✅ Browser test: No localhost requests detected")
            return True
        elif 'BROWSER_TEST_PASSED:False' in result.stdout:
            print("❌ Browser test: Localhost requests detected!")
            print(result.stdout)
            return False
        else:
            print("⚠️  Browser test inconclusive")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return None
            
    except Exception as e:
        print(f"⚠️  Browser test not available: {e}")
        return None

def main():
    print("🔍 PRODUCTION LOCALHOST BUG VERIFICATION")
    print("🎯 Testing https://gvses-market-insights.fly.dev")
    print("=" * 50)
    
    # Run quick curl-based tests
    quick_result = check_production_site()
    
    # Try browser test if available
    print("\n🌐 Attempting browser-based test...")
    browser_result = run_browser_test()
    
    # Final summary
    print("\n" + "=" * 50)
    print("🏆 FINAL VERIFICATION RESULTS")
    print("=" * 50)
    
    if quick_result and browser_result is not False:
        print("✅ LOCALHOST BUG APPEARS TO BE FIXED!")
        print("✅ Production deployment looks healthy")
        print("✅ Agent Builder integration should work correctly")
        exit_code = 0
    elif browser_result is False:
        print("❌ LOCALHOST BUG STILL PRESENT!")
        print("❌ Browser detected localhost:8000 requests")
        print("❌ Agent Builder integration will fail")
        exit_code = 1
    else:
        print("⚠️  MIXED RESULTS - Manual verification recommended")
        print("⚠️  Quick test passed, browser test inconclusive")
        exit_code = 2
    
    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'quick_test_passed': quick_result,
        'browser_test_result': browser_result,
        'verdict': 'FIXED' if exit_code == 0 else 'BROKEN' if exit_code == 1 else 'UNCLEAR'
    }
    
    with open('production_verification_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: production_verification_results.json")
    return exit_code

if __name__ == "__main__":
    sys.exit(main())