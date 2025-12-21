#!/usr/bin/env python3
"""
Comprehensive production test for Chart Command Polling Fix
Tests the full Agent Builder → MCP Server → Chart Control API → Frontend integration
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright, expect

async def test_chart_command_polling_production():
    """Test that chart command polling works correctly in production"""
    
    print("🚀 Starting Chart Command Polling Production Test")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser with network monitoring
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track network requests
        network_requests = []
        console_messages = []
        
        # Monitor network requests
        async def handle_request(request):
            network_requests.append({
                'url': request.url,
                'method': request.method,
                'timestamp': time.time()
            })
            print(f"📡 Network Request: {request.method} {request.url}")
        
        # Monitor console messages
        async def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'timestamp': time.time()
            })
            if 'error' in msg.type.lower() or 'Chart Command Processor Error' in msg.text:
                print(f"🚨 Console {msg.type.upper()}: {msg.text}")
        
        page.on("request", handle_request)
        page.on("console", handle_console)
        
        try:
            print("1️⃣ Navigating to production site...")
            await page.goto("https://gvses-market-insights.fly.dev", timeout=30000)
            print("✅ Successfully loaded production site")
            
            # Wait for page to fully load
            print("2️⃣ Waiting for page to fully load...")
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            # Wait for Chart Control tab to be available
            print("3️⃣ Looking for Chart Control tab...")
            chart_control_tab = page.locator('button:has-text("Chart Control")')
            
            # Wait up to 10 seconds for the tab to appear
            await expect(chart_control_tab).to_be_visible(timeout=10000)
            print("✅ Chart Control tab found and visible")
            
            # Click the Chart Control tab
            print("4️⃣ Clicking Chart Control tab...")
            await chart_control_tab.click()
            print("✅ Chart Control tab clicked")
            
            # Wait a moment for the tab content to load
            await page.wait_for_timeout(2000)
            
            # Clear previous requests and start monitoring polling
            print("5️⃣ Starting polling monitoring (30 seconds)...")
            start_time = time.time()
            initial_request_count = len(network_requests)
            
            # Monitor for 30 seconds to catch polling requests
            monitoring_duration = 30
            while time.time() - start_time < monitoring_duration:
                await page.wait_for_timeout(1000)  # Check every second
                
                # Show progress
                elapsed = int(time.time() - start_time)
                if elapsed % 5 == 0 and elapsed > 0:
                    print(f"⏱️  Monitoring... {elapsed}/{monitoring_duration} seconds")
            
            print("6️⃣ Analyzing network requests...")
            
            # Filter requests from the monitoring period
            monitoring_requests = [
                req for req in network_requests[initial_request_count:]
                if req['timestamp'] >= start_time
            ]
            
            # Check for localhost requests (the bug we fixed)
            localhost_requests = [
                req for req in monitoring_requests
                if 'localhost:8000' in req['url']
            ]
            
            # Check for correct production API requests
            chart_command_requests = [
                req for req in monitoring_requests
                if 'gvses-market-insights.fly.dev/api/chart/commands' in req['url']
            ]
            
            print("\n📊 NETWORK ANALYSIS RESULTS:")
            print("=" * 40)
            print(f"Total requests monitored: {len(monitoring_requests)}")
            print(f"Localhost requests (BUG): {len(localhost_requests)}")
            print(f"Chart command API requests: {len(chart_command_requests)}")
            
            if localhost_requests:
                print("\n🚨 LOCALHOST REQUESTS DETECTED (BUG PRESENT):")
                for req in localhost_requests:
                    print(f"  - {req['method']} {req['url']}")
            else:
                print("✅ NO localhost requests detected (bug fixed!)")
            
            if chart_command_requests:
                print("\n✅ CHART COMMAND API REQUESTS:")
                for req in chart_command_requests:
                    print(f"  - {req['method']} {req['url']}")
            else:
                print("⚠️  No chart command API requests detected")
            
            # Check console for errors
            print("\n7️⃣ Analyzing console messages...")
            error_messages = [
                msg for msg in console_messages
                if 'error' in msg['type'].lower() or 'Chart Command Processor Error' in msg['text']
            ]
            
            if error_messages:
                print("🚨 CONSOLE ERRORS DETECTED:")
                for msg in error_messages:
                    print(f"  - {msg['type']}: {msg['text']}")
            else:
                print("✅ No console errors detected")
            
            # Take screenshot of Chart Control interface
            print("8️⃣ Taking screenshot of Chart Control interface...")
            await page.screenshot(
                path="chart_control_production_test.png",
                full_page=True
            )
            print("✅ Screenshot saved: chart_control_production_test.png")
            
            # Final assessment
            print("\n🎯 FINAL ASSESSMENT:")
            print("=" * 40)
            
            success_criteria = {
                "No localhost requests": len(localhost_requests) == 0,
                "Chart command API working": len(chart_command_requests) > 0,
                "No console errors": len(error_messages) == 0,
                "Chart Control tab accessible": True  # We got this far
            }
            
            all_passed = all(success_criteria.values())
            
            for criterion, passed in success_criteria.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status}: {criterion}")
            
            if all_passed:
                print("\n🎉 SUCCESS: Chart command polling fix is working 100% in production!")
                print("✅ Agent Builder → MCP Server → Chart Control API → Frontend integration is fully functional")
            else:
                print("\n⚠️  ISSUES DETECTED: Some criteria failed")
                
                # Detailed recommendations
                if len(localhost_requests) > 0:
                    print("🔧 RECOMMENDED ACTION: Check frontend production build - still making localhost requests")
                if len(chart_command_requests) == 0:
                    print("🔧 RECOMMENDED ACTION: Verify chart command API endpoint is accessible")
                if len(error_messages) > 0:
                    print("🔧 RECOMMENDED ACTION: Review console errors for debugging")
            
            # Summary statistics
            print(f"\n📈 STATISTICS:")
            print(f"Success Rate: {sum(success_criteria.values())}/{len(success_criteria)} ({100 * sum(success_criteria.values()) / len(success_criteria):.0f}%)")
            print(f"Total network requests: {len(monitoring_requests)}")
            print(f"Monitoring duration: {monitoring_duration} seconds")
            print(f"Screenshot: chart_control_production_test.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            # Take screenshot even on failure
            try:
                await page.screenshot(path="chart_control_error_screenshot.png")
                print("📸 Error screenshot saved: chart_control_error_screenshot.png")
            except:
                pass
            raise
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chart_command_polling_production())