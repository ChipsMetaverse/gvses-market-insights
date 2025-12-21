#!/usr/bin/env python3
"""
Production Chart Control Polling Test
=====================================

Verifies that the production frontend at https://gvses-market-insights.fly.dev
correctly polls the Chart Control API and NO LONGER makes localhost requests.

This test validates the fix for the localhost polling bug by monitoring
network traffic and ensuring all Chart Control API calls go to production.
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright

class ProductionChartControlTest:
    def __init__(self):
        self.production_url = "https://gvses-market-insights.fly.dev"
        self.localhost_requests = []
        self.production_requests = []
        self.console_errors = []
        self.start_time = None
        
    async def run_test(self):
        """Run the complete production polling test"""
        print("🚀 Starting Production Chart Control Polling Test")
        print(f"Testing: {self.production_url}")
        print("=" * 60)
        
        async with async_playwright() as p:
            # Launch browser with network monitoring
            browser = await p.chromium.launch(
                headless=False,  # Show browser for debugging
                args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Set up network and console monitoring
            await self._setup_monitoring(page)
            
            try:
                # Step 1: Navigate to production site
                await self._navigate_to_production(page)
                
                # Step 2: Wait for page to load completely
                await self._wait_for_page_load(page)
                
                # Step 3: Activate Chart Control tab
                await self._activate_chart_control(page)
                
                # Step 4: Monitor polling for 30 seconds
                await self._monitor_polling_behavior(page)
                
                # Step 5: Analyze results
                await self._analyze_results()
                
                # Step 6: Take screenshot
                await self._take_screenshot(page)
                
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                await page.screenshot(path="test_failure_screenshot.png")
                raise
            finally:
                await browser.close()
    
    async def _setup_monitoring(self, page):
        """Set up network request and console monitoring"""
        print("📡 Setting up network and console monitoring...")
        
        # Monitor network requests
        page.on("request", self._on_request)
        page.on("response", self._on_response)
        
        # Monitor console messages
        page.on("console", self._on_console_message)
        
        # Monitor page errors
        page.on("pageerror", self._on_page_error)
    
    async def _on_request(self, request):
        """Handle network requests"""
        url = request.url
        
        # Track Chart Control API requests
        if "/api/chart/commands" in url:
            request_data = {
                'url': url,
                'method': request.method,
                'timestamp': datetime.now().isoformat(),
                'headers': dict(request.headers)
            }
            
            if "localhost:8000" in url:
                self.localhost_requests.append(request_data)
                print(f"🚨 LOCALHOST REQUEST DETECTED: {url}")
            elif "gvses-market-insights.fly.dev" in url:
                self.production_requests.append(request_data)
                print(f"✅ Production request: {url}")
    
    async def _on_response(self, response):
        """Handle network responses"""
        if "/api/chart/commands" in response.url:
            status = response.status
            if status >= 400:
                print(f"⚠️  Chart Control API error: {status} - {response.url}")
    
    async def _on_console_message(self, msg):
        """Handle console messages"""
        if msg.type in ['error', 'warning']:
            error_data = {
                'type': msg.type,
                'text': msg.text,
                'timestamp': datetime.now().isoformat()
            }
            self.console_errors.append(error_data)
            print(f"🔍 Console {msg.type}: {msg.text}")
    
    async def _on_page_error(self, error):
        """Handle page errors"""
        error_data = {
            'type': 'page_error',
            'text': str(error),
            'timestamp': datetime.now().isoformat()
        }
        self.console_errors.append(error_data)
        print(f"💥 Page error: {error}")
    
    async def _navigate_to_production(self, page):
        """Navigate to the production site"""
        print(f"🌐 Navigating to {self.production_url}...")
        
        try:
            response = await page.goto(self.production_url, 
                                     wait_until='networkidle', 
                                     timeout=30000)
            
            if response.status >= 400:
                raise Exception(f"Failed to load production site: HTTP {response.status}")
            
            print(f"✅ Successfully loaded production site (HTTP {response.status})")
            
        except Exception as e:
            print(f"❌ Failed to navigate to production: {e}")
            raise
    
    async def _wait_for_page_load(self, page):
        """Wait for page to load completely"""
        print("⏳ Waiting for page to load completely...")
        
        # Wait for React to hydrate
        await page.wait_for_selector('[data-testid="trading-dashboard"]', timeout=20000)
        
        # Wait for market data to load
        await page.wait_for_selector('.market-card', timeout=15000)
        
        # Give additional time for all components to initialize
        await asyncio.sleep(3)
        
        print("✅ Page loaded successfully")
    
    async def _activate_chart_control(self, page):
        """Click on Chart Control tab to activate ChatKit"""
        print("🎯 Activating Chart Control tab...")
        
        try:
            # Look for Chart Control tab
            chart_control_tab = page.locator('text="Chart Control"').first
            
            # Check if tab exists
            if not await chart_control_tab.is_visible():
                print("⚠️  Chart Control tab not found, looking for alternative selectors...")
                # Try alternative selectors
                alternatives = [
                    '.tab:has-text("Chart Control")',
                    '[data-tab="chart-control"]',
                    'button:has-text("Chart Control")',
                    '.nav-tab:has-text("Chart Control")'
                ]
                
                for selector in alternatives:
                    if await page.locator(selector).is_visible():
                        chart_control_tab = page.locator(selector).first
                        break
                else:
                    raise Exception("Chart Control tab not found with any selector")
            
            # Click the tab
            await chart_control_tab.click()
            
            # Wait for ChatKit to initialize
            await asyncio.sleep(2)
            
            # Verify ChatKit is active
            chatkit_active = await page.locator('.chatkit-container, [data-component="chatkit"]').is_visible()
            
            if chatkit_active:
                print("✅ Chart Control tab activated successfully")
            else:
                print("⚠️  Chart Control tab clicked but ChatKit component not visible")
            
        except Exception as e:
            print(f"❌ Failed to activate Chart Control tab: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="chart_control_activation_failure.png")
            raise
    
    async def _monitor_polling_behavior(self, page):
        """Monitor polling behavior for 30 seconds"""
        print("📊 Monitoring Chart Control polling behavior for 30 seconds...")
        self.start_time = time.time()
        
        # Clear existing request logs
        self.localhost_requests.clear()
        self.production_requests.clear()
        
        print("Monitoring network requests...")
        print("- Looking for Chart Control API polling")
        print("- Checking for localhost requests (should be ZERO)")
        print("- Verifying production requests")
        
        # Monitor for 30 seconds
        for second in range(30):
            await asyncio.sleep(1)
            elapsed = second + 1
            
            if elapsed % 5 == 0:  # Progress update every 5 seconds
                print(f"  ⏱️  {elapsed}/30 seconds - "
                      f"Production requests: {len(self.production_requests)}, "
                      f"Localhost requests: {len(self.localhost_requests)}")
        
        print("✅ Monitoring complete")
    
    async def _analyze_results(self):
        """Analyze the polling behavior results"""
        print("\n" + "=" * 60)
        print("📋 POLLING BEHAVIOR ANALYSIS")
        print("=" * 60)
        
        # Localhost requests analysis
        localhost_count = len(self.localhost_requests)
        if localhost_count == 0:
            print("✅ LOCALHOST REQUESTS: 0 (PERFECT - Bug is fixed!)")
        else:
            print(f"❌ LOCALHOST REQUESTS: {localhost_count} (BUG STILL EXISTS)")
            print("   Localhost requests detected:")
            for req in self.localhost_requests[:3]:  # Show first 3
                print(f"   - {req['timestamp']}: {req['url']}")
        
        # Production requests analysis
        production_count = len(self.production_requests)
        print(f"\n✅ PRODUCTION REQUESTS: {production_count}")
        
        if production_count == 0:
            print("❌ NO PRODUCTION REQUESTS - Chart Control polling not working")
        else:
            # Calculate polling frequency
            if production_count > 1:
                time_span = 30  # seconds
                frequency = production_count / time_span
                interval = time_span / production_count if production_count > 0 else 0
                
                print(f"   Polling frequency: {frequency:.2f} requests/second")
                print(f"   Average interval: {interval:.2f} seconds")
                
                # Check if frequency is reasonable (1-2 second intervals)
                if 0.5 <= frequency <= 1.0:
                    print("   ✅ Polling frequency is optimal (1-2 second intervals)")
                elif frequency > 1.0:
                    print("   ⚠️  Polling frequency is high (< 1 second intervals)")
                else:
                    print("   ⚠️  Polling frequency is low (> 2 second intervals)")
            
            print("   Recent production requests:")
            for req in self.production_requests[-3:]:  # Show last 3
                print(f"   - {req['timestamp']}: {req['method']} {req['url']}")
        
        # Console errors analysis
        error_count = len(self.console_errors)
        if error_count == 0:
            print(f"\n✅ CONSOLE ERRORS: 0 (No errors detected)")
        else:
            print(f"\n⚠️  CONSOLE ERRORS: {error_count}")
            for error in self.console_errors[:3]:  # Show first 3
                print(f"   - {error['type']}: {error['text']}")
        
        # Overall verdict
        print("\n" + "=" * 60)
        print("🏆 TEST VERDICT")
        print("=" * 60)
        
        if localhost_count == 0 and production_count > 0:
            print("✅ SUCCESS: Localhost bug is FIXED!")
            print("   - No localhost requests detected")
            print("   - Production polling working correctly")
            print("   - Chart Control API integration successful")
        elif localhost_count > 0:
            print("❌ FAILURE: Localhost bug still exists")
            print("   - Localhost requests are still being made")
            print("   - Frontend caching or configuration issue")
        elif production_count == 0:
            print("❌ FAILURE: Chart Control polling not working")
            print("   - No polling requests detected")
            print("   - ChatKit component may not be properly initialized")
        else:
            print("⚠️  PARTIAL: Mixed results require investigation")
    
    async def _take_screenshot(self, page):
        """Take screenshot of Chart Control interface"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"production_chart_control_{timestamp}.png"
        
        print(f"📷 Taking screenshot: {screenshot_path}")
        
        try:
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"✅ Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠️  Screenshot failed: {e}")
    
    def save_results(self):
        """Save test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"chart_control_test_results_{timestamp}.json"
        
        results = {
            'test_timestamp': datetime.now().isoformat(),
            'production_url': self.production_url,
            'localhost_requests': self.localhost_requests,
            'production_requests': self.production_requests,
            'console_errors': self.console_errors,
            'summary': {
                'localhost_count': len(self.localhost_requests),
                'production_count': len(self.production_requests),
                'error_count': len(self.console_errors),
                'test_duration_seconds': 30,
                'bug_fixed': len(self.localhost_requests) == 0 and len(self.production_requests) > 0
            }
        }
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Results saved to: {results_file}")
        return results_file

async def main():
    """Main test execution"""
    test = ProductionChartControlTest()
    
    try:
        await test.run_test()
        test.save_results()
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"💥 Test failed: {e}")
        test.save_results()
        raise

if __name__ == "__main__":
    print("Production Chart Control Polling Test")
    print("====================================")
    print()
    print("This test verifies that the production frontend correctly")
    print("polls the Chart Control API without making localhost requests.")
    print()
    
    asyncio.run(main())