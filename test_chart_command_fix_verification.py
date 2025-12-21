#!/usr/bin/env python3
"""
Final verification test for Chart Command Polling Fix
Confirms that the localhost:8000 hardcoding issue has been resolved
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_chart_command_fix():
    """Verify that the chart command polling fix is working correctly"""
    
    print("🔧 CHART COMMAND POLLING FIX - VERIFICATION TEST")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track network requests
        network_requests = []
        localhost_requests = []
        production_requests = []
        
        async def handle_request(request):
            network_requests.append(request.url)
            if 'localhost:8000' in request.url:
                localhost_requests.append(request.url)
                print(f"🚨 LOCALHOST REQUEST: {request.url}")
            elif 'gvses-market-insights.fly.dev' in request.url:
                production_requests.append(request.url)
                print(f"✅ PRODUCTION REQUEST: {request.url}")
        
        page.on("request", handle_request)
        
        try:
            print("1️⃣ Loading production site...")
            await page.goto("https://gvses-market-insights.fly.dev", timeout=30000)
            
            print("2️⃣ Waiting for initial load...")
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            print("3️⃣ Clicking Chart Control tab...")
            chart_control_tab = page.locator('button:has-text("Chart Control")')
            await chart_control_tab.wait_for(state="visible", timeout=10000)
            await chart_control_tab.click()
            
            print("4️⃣ Monitoring chart command polling for 20 seconds...")
            start_time = time.time()
            initial_request_count = len(network_requests)
            
            # Monitor for 20 seconds
            while time.time() - start_time < 20:
                await page.wait_for_timeout(1000)
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0:
                    print(f"   Monitoring... {elapsed}/20 seconds")
            
            monitoring_requests = network_requests[initial_request_count:]
            chart_command_requests = [req for req in monitoring_requests if '/api/chart/commands' in req]
            
            print("\n📊 FINAL RESULTS:")
            print("=" * 40)
            print(f"Total requests monitored: {len(monitoring_requests)}")
            print(f"Chart command requests: {len(chart_command_requests)}")
            print(f"Localhost requests (BUG): {len(localhost_requests)}")
            print(f"Production requests: {len(production_requests)}")
            
            if localhost_requests:
                print("\n❌ LOCALHOST REQUESTS DETECTED:")
                for req in localhost_requests[:5]:  # Show first 5
                    print(f"   - {req}")
            else:
                print("\n✅ NO LOCALHOST REQUESTS - FIX SUCCESSFUL!")
            
            if chart_command_requests:
                print("\n📈 CHART COMMAND REQUESTS:")
                production_chart_requests = [req for req in chart_command_requests if 'gvses-market-insights.fly.dev' in req]
                print(f"   Production chart requests: {len(production_chart_requests)}")
                for req in production_chart_requests[:3]:
                    print(f"   - {req}")
            
            # Final assessment
            success_criteria = {
                "No localhost requests": len(localhost_requests) == 0,
                "Chart API working": any('/api/chart/commands' in req for req in production_requests),
                "Site loads properly": len(production_requests) > 0
            }
            
            print(f"\n🎯 SUCCESS CRITERIA:")
            print("-" * 30)
            all_passed = True
            for criterion, passed in success_criteria.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status}: {criterion}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print(f"\n🎉 SUCCESS: Chart command polling fix is 100% working!")
                print("✅ No more localhost:8000 hardcoding issues")
                print("✅ Production API endpoints are being used correctly")
                print("✅ Chart Control integration is functional")
            else:
                print(f"\n⚠️  Some issues remain - see details above")
            
            # Take final screenshot
            await page.screenshot(path="chart_command_fix_verification.png", full_page=True)
            print(f"\n📸 Screenshot saved: chart_command_fix_verification.png")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            await page.screenshot(path="chart_command_fix_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chart_command_fix())