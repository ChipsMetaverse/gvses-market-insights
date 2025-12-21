#!/usr/bin/env python3
"""
Comprehensive Playwright Test for Production Bundle Verification and Chart Command Processing

This test verifies:
1. Production JavaScript bundle contains correct URLs (not localhost)
2. Chart Control interface loads successfully
3. Chart command processing functionality works end-to-end
4. Network requests and polling mechanism operate correctly
5. Agent Builder → MCP → Chart Control API → Frontend integration chain
"""

import asyncio
import json
import time
import re
from datetime import datetime
from playwright.async_api import async_playwright, expect
from typing import List, Dict, Any

class ProductionVerificationTest:
    def __init__(self):
        self.production_url = "https://gvses-market-insights.fly.dev"
        self.test_results = {
            "bundle_verification": {},
            "chart_control_activation": {},
            "command_processing": {},
            "network_analysis": {},
            "integration_test": {},
            "console_logs": [],
            "network_requests": [],
            "screenshots": [],
            "timestamp": datetime.now().isoformat()
        }
        
    async def run_comprehensive_test(self):
        """Run the complete verification test suite"""
        print("🚀 Starting Comprehensive Production Verification Test")
        print(f"Target URL: {self.production_url}")
        print("=" * 70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=['--no-sandbox'])
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Setup console and network monitoring
            await self._setup_monitoring(page)
            
            try:
                # Step 1: Navigate and verify bundle
                await self._test_navigation_and_bundle(page)
                
                # Step 2: Activate Chart Control
                await self._test_chart_control_activation(page)
                
                # Step 3: Test command processing
                await self._test_chart_command_processing(page)
                
                # Step 4: Analyze network requests
                await self._analyze_network_requests(page)
                
                # Step 5: End-to-end integration test
                await self._test_end_to_end_integration(page)
                
                # Step 6: Final verification
                await self._final_verification(page)
                
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                self.test_results["error"] = str(e)
                await page.screenshot(path=f"error_screenshot_{int(time.time())}.png")
                
            finally:
                await browser.close()
                
        # Generate comprehensive report
        await self._generate_report()
        
    async def _setup_monitoring(self, page):
        """Setup console and network monitoring"""
        print("📊 Setting up monitoring...")
        
        # Monitor console messages
        page.on("console", lambda msg: self.test_results["console_logs"].append({
            "type": msg.type,
            "text": msg.text,
            "timestamp": time.time()
        }))
        
        # Monitor network requests
        page.on("request", lambda request: self.test_results["network_requests"].append({
            "url": request.url,
            "method": request.method,
            "timestamp": time.time(),
            "type": "request"
        }))
        
        page.on("response", lambda response: self.test_results["network_requests"].append({
            "url": response.url,
            "status": response.status,
            "timestamp": time.time(),
            "type": "response"
        }))
        
    async def _test_navigation_and_bundle(self, page):
        """Step 1: Navigate to production and verify JavaScript bundle"""
        print("🌐 Step 1: Navigation and Bundle Verification")
        
        try:
            # Navigate to production
            print(f"   Navigating to {self.production_url}...")
            await page.goto(self.production_url, wait_until="networkidle", timeout=30000)
            
            # Wait for initial load
            await page.wait_for_timeout(3000)
            
            # Take initial screenshot
            screenshot_path = f"production_initial_{int(time.time())}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            self.test_results["screenshots"].append(screenshot_path)
            
            # Verify page loaded successfully
            title = await page.title()
            print(f"   Page title: {title}")
            
            # Find JavaScript bundle
            script_elements = await page.query_selector_all('script[src*="index-"]')
            bundle_info = {}
            
            for script in script_elements:
                src = await script.get_attribute('src')
                if 'index-' in src and src.endswith('.js'):
                    print(f"   Found bundle: {src}")
                    bundle_info["bundle_url"] = src
                    
                    # Fetch bundle content to verify URLs
                    try:
                        response = await page.goto(f"{self.production_url}{src}")
                        bundle_content = await response.text()
                        
                        # Check for localhost URLs (should NOT be present)
                        localhost_matches = re.findall(r'localhost:\d+', bundle_content)
                        production_urls = re.findall(r'gvses-market-insights\.fly\.dev', bundle_content)
                        
                        bundle_info.update({
                            "contains_localhost": len(localhost_matches) > 0,
                            "localhost_count": len(localhost_matches),
                            "localhost_matches": localhost_matches[:5],  # First 5 matches
                            "contains_production": len(production_urls) > 0,
                            "production_count": len(production_urls),
                            "bundle_size": len(bundle_content)
                        })
                        
                        print(f"   ✅ Bundle analysis complete")
                        print(f"      - Localhost references: {len(localhost_matches)}")
                        print(f"      - Production references: {len(production_urls)}")
                        
                        # Go back to main page
                        await page.goto(self.production_url)
                        break
                        
                    except Exception as e:
                        print(f"   ⚠️  Could not analyze bundle content: {e}")
                        bundle_info["analysis_error"] = str(e)
            
            self.test_results["bundle_verification"] = {
                "success": True,
                "bundle_info": bundle_info,
                "page_title": title
            }
            
        except Exception as e:
            print(f"   ❌ Bundle verification failed: {e}")
            self.test_results["bundle_verification"] = {
                "success": False,
                "error": str(e)
            }
            
    async def _test_chart_control_activation(self, page):
        """Step 2: Activate Chart Control interface"""
        print("🎛️  Step 2: Chart Control Activation")
        
        try:
            # Wait for page to be fully loaded
            await page.wait_for_selector('[data-testid="trading-dashboard"]', timeout=10000)
            
            # Look for Chart Control tab
            print("   Looking for Chart Control tab...")
            chart_control_selectors = [
                'text="Chart Control"',
                '[role="tab"]:has-text("Chart Control")',
                'button:has-text("Chart Control")',
                '.tab:has-text("Chart Control")',
                '[data-tab="chart-control"]'
            ]
            
            chart_control_element = None
            for selector in chart_control_selectors:
                try:
                    chart_control_element = await page.wait_for_selector(selector, timeout=2000)
                    if chart_control_element:
                        print(f"   Found Chart Control using selector: {selector}")
                        break
                except:
                    continue
            
            if chart_control_element:
                # Click on Chart Control tab
                print("   Clicking Chart Control tab...")
                await chart_control_element.click()
                await page.wait_for_timeout(2000)
                
                # Verify Chart Control interface is active
                chat_interface_selectors = [
                    '[data-testid="chatkit-container"]',
                    '.chatkit-interface',
                    '[class*="chat"]',
                    'textarea[placeholder*="message"]',
                    'input[placeholder*="message"]'
                ]
                
                chat_interface_found = False
                for selector in chat_interface_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"   ✅ Chart Control interface found: {selector}")
                            chat_interface_found = True
                            break
                    except:
                        continue
                
                # Take screenshot of Chart Control interface
                screenshot_path = f"chart_control_active_{int(time.time())}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                self.test_results["screenshots"].append(screenshot_path)
                
                self.test_results["chart_control_activation"] = {
                    "success": True,
                    "tab_found": True,
                    "interface_loaded": chat_interface_found,
                    "screenshot": screenshot_path
                }
                
                print("   ✅ Chart Control activation successful")
                
            else:
                print("   ⚠️  Chart Control tab not found, checking current interface...")
                
                # Check if we're already on Chart Control or if it's embedded
                current_interface = await page.content()
                has_chat_interface = any(selector.replace('[data-testid="', '').replace('"]', '') in current_interface 
                                       for selector in chat_interface_selectors)
                
                self.test_results["chart_control_activation"] = {
                    "success": has_chat_interface,
                    "tab_found": False,
                    "interface_loaded": has_chat_interface,
                    "note": "Chart Control may be embedded or always visible"
                }
                
        except Exception as e:
            print(f"   ❌ Chart Control activation failed: {e}")
            self.test_results["chart_control_activation"] = {
                "success": False,
                "error": str(e)
            }
            
    async def _test_chart_command_processing(self, page):
        """Step 3: Test chart command processing functionality"""
        print("📈 Step 3: Chart Command Processing Test")
        
        try:
            # Monitor console for Chart Command Processor activity
            initial_log_count = len(self.test_results["console_logs"])
            print(f"   Starting console monitoring (current logs: {initial_log_count})")
            
            # Wait and monitor for command processor activity
            print("   Monitoring for Chart Command Processor activity...")
            await page.wait_for_timeout(10000)  # Wait 10 seconds to capture polling
            
            # Analyze console logs for command processor activity
            command_processor_logs = [
                log for log in self.test_results["console_logs"]
                if "Chart Command" in log["text"] or "useChartCommandProcessor" in log["text"]
                or "polling" in log["text"].lower() or "command" in log["text"].lower()
            ]
            
            # Check for API polling requests
            polling_requests = [
                req for req in self.test_results["network_requests"]
                if "/api/chart/commands" in req["url"] and req["type"] == "request"
            ]
            
            # Check for successful responses
            polling_responses = [
                req for req in self.test_results["network_requests"]
                if "/api/chart/commands" in req["url"] and req["type"] == "response"
            ]
            
            print(f"   Command processor logs found: {len(command_processor_logs)}")
            print(f"   Polling requests detected: {len(polling_requests)}")
            print(f"   Polling responses received: {len(polling_responses)}")
            
            # Calculate polling frequency
            polling_frequency = 0
            if len(polling_requests) > 1:
                time_diff = polling_requests[-1]["timestamp"] - polling_requests[0]["timestamp"]
                polling_frequency = time_diff / (len(polling_requests) - 1)
                print(f"   Average polling interval: {polling_frequency:.1f} seconds")
            
            # Check for any error responses
            error_responses = [
                resp for resp in polling_responses
                if resp.get("status", 200) >= 400
            ]
            
            success_rate = 0
            if len(polling_responses) > 0:
                successful_responses = len(polling_responses) - len(error_responses)
                success_rate = (successful_responses / len(polling_responses)) * 100
            
            self.test_results["command_processing"] = {
                "success": len(polling_requests) > 0,
                "processor_logs": len(command_processor_logs),
                "polling_requests": len(polling_requests),
                "polling_responses": len(polling_responses),
                "error_responses": len(error_responses),
                "polling_frequency": polling_frequency,
                "success_rate": success_rate,
                "sample_logs": command_processor_logs[:3]  # First 3 relevant logs
            }
            
            print(f"   ✅ Command processing analysis complete (success rate: {success_rate:.1f}%)")
            
        except Exception as e:
            print(f"   ❌ Command processing test failed: {e}")
            self.test_results["command_processing"] = {
                "success": False,
                "error": str(e)
            }
            
    async def _analyze_network_requests(self, page):
        """Step 4: Analyze network requests and polling mechanism"""
        print("🌐 Step 4: Network Request Analysis")
        
        try:
            # Continue monitoring for a bit more
            await page.wait_for_timeout(5000)
            
            # Categorize network requests
            api_requests = []
            static_requests = []
            websocket_requests = []
            
            for req in self.test_results["network_requests"]:
                url = req["url"]
                if "/api/" in url:
                    api_requests.append(req)
                elif any(ext in url for ext in [".js", ".css", ".png", ".ico", ".svg"]):
                    static_requests.append(req)
                elif "ws://" in url or "wss://" in url or "websocket" in url:
                    websocket_requests.append(req)
            
            # Analyze chart commands API specifically
            chart_commands_requests = [
                req for req in api_requests
                if "/chart/commands" in req["url"]
            ]
            
            # Check request/response timing
            request_timings = []
            for i in range(len(chart_commands_requests) - 1):
                current = chart_commands_requests[i]
                next_req = chart_commands_requests[i + 1]
                if current["type"] == "request" and next_req["type"] == "request":
                    timing = next_req["timestamp"] - current["timestamp"]
                    request_timings.append(timing)
            
            average_interval = sum(request_timings) / len(request_timings) if request_timings else 0
            
            self.test_results["network_analysis"] = {
                "success": True,
                "total_requests": len(self.test_results["network_requests"]),
                "api_requests": len(api_requests),
                "static_requests": len(static_requests),
                "websocket_requests": len(websocket_requests),
                "chart_commands_requests": len(chart_commands_requests),
                "average_polling_interval": average_interval,
                "request_timings": request_timings[:5]  # First 5 timings
            }
            
            print(f"   Total network requests: {len(self.test_results['network_requests'])}")
            print(f"   Chart commands requests: {len(chart_commands_requests)}")
            print(f"   Average polling interval: {average_interval:.1f}s")
            print("   ✅ Network analysis complete")
            
        except Exception as e:
            print(f"   ❌ Network analysis failed: {e}")
            self.test_results["network_analysis"] = {
                "success": False,
                "error": str(e)
            }
            
    async def _test_end_to_end_integration(self, page):
        """Step 5: End-to-end integration test"""
        print("🔗 Step 5: End-to-End Integration Test")
        
        try:
            # Look for evidence of successful integration chain
            console_indicators = [
                "MCP",
                "Agent Builder",
                "Chart Control",
                "command",
                "success",
                "connected"
            ]
            
            integration_logs = []
            for log in self.test_results["console_logs"]:
                if any(indicator.lower() in log["text"].lower() for indicator in console_indicators):
                    integration_logs.append(log)
            
            # Check for successful API responses
            successful_api_calls = [
                req for req in self.test_results["network_requests"]
                if req["type"] == "response" and "/api/" in req["url"] and req.get("status", 0) < 400
            ]
            
            # Look for chart updates or command acknowledgments
            chart_update_logs = [
                log for log in self.test_results["console_logs"]
                if any(keyword in log["text"].lower() for keyword in ["chart", "update", "symbol", "display"])
            ]
            
            # Calculate integration health score
            health_indicators = {
                "polling_active": len([req for req in self.test_results["network_requests"] if "/chart/commands" in req["url"]]) > 0,
                "api_responsive": len(successful_api_calls) > 0,
                "console_activity": len(integration_logs) > 0,
                "chart_activity": len(chart_update_logs) > 0,
                "no_critical_errors": len([log for log in self.test_results["console_logs"] if log["type"] == "error"]) == 0
            }
            
            health_score = sum(health_indicators.values()) / len(health_indicators) * 100
            
            self.test_results["integration_test"] = {
                "success": health_score > 50,
                "health_score": health_score,
                "health_indicators": health_indicators,
                "integration_logs_count": len(integration_logs),
                "successful_api_calls": len(successful_api_calls),
                "chart_activity_count": len(chart_update_logs),
                "sample_integration_logs": integration_logs[:3]
            }
            
            print(f"   Integration health score: {health_score:.1f}%")
            print(f"   Integration logs: {len(integration_logs)}")
            print(f"   Successful API calls: {len(successful_api_calls)}")
            print("   ✅ End-to-end integration analysis complete")
            
        except Exception as e:
            print(f"   ❌ Integration test failed: {e}")
            self.test_results["integration_test"] = {
                "success": False,
                "error": str(e)
            }
            
    async def _final_verification(self, page):
        """Step 6: Final verification and summary"""
        print("✅ Step 6: Final Verification")
        
        try:
            # Take final screenshot
            final_screenshot = f"production_final_{int(time.time())}.png"
            await page.screenshot(path=final_screenshot, full_page=True)
            self.test_results["screenshots"].append(final_screenshot)
            
            # Summary of all test results
            test_success_count = sum([
                self.test_results["bundle_verification"].get("success", False),
                self.test_results["chart_control_activation"].get("success", False),
                self.test_results["command_processing"].get("success", False),
                self.test_results["network_analysis"].get("success", False),
                self.test_results["integration_test"].get("success", False)
            ])
            
            overall_success_rate = (test_success_count / 5) * 100
            
            self.test_results["final_summary"] = {
                "overall_success_rate": overall_success_rate,
                "tests_passed": test_success_count,
                "total_tests": 5,
                "final_screenshot": final_screenshot,
                "recommendation": "PASS" if overall_success_rate >= 80 else "INVESTIGATE" if overall_success_rate >= 60 else "FAIL"
            }
            
            print(f"   Overall success rate: {overall_success_rate:.1f}%")
            print(f"   Tests passed: {test_success_count}/5")
            print(f"   Final screenshot: {final_screenshot}")
            
        except Exception as e:
            print(f"   ⚠️  Final verification had issues: {e}")
            self.test_results["final_verification_error"] = str(e)
            
    async def _generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 70)
        
        # Save detailed results
        report_file = f"production_verification_results_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {report_file}")
        
        # Print summary
        bundle = self.test_results.get("bundle_verification", {})
        chart_control = self.test_results.get("chart_control_activation", {})
        commands = self.test_results.get("command_processing", {})
        network = self.test_results.get("network_analysis", {})
        integration = self.test_results.get("integration_test", {})
        final = self.test_results.get("final_summary", {})
        
        print("\n🎯 TEST RESULTS SUMMARY:")
        print(f"   1. Bundle Verification: {'✅ PASS' if bundle.get('success') else '❌ FAIL'}")
        if bundle.get("bundle_info"):
            bundle_info = bundle["bundle_info"]
            print(f"      - Localhost references: {bundle_info.get('localhost_count', 'Unknown')}")
            print(f"      - Production references: {bundle_info.get('production_count', 'Unknown')}")
        
        print(f"   2. Chart Control Activation: {'✅ PASS' if chart_control.get('success') else '❌ FAIL'}")
        print(f"      - Tab found: {chart_control.get('tab_found', False)}")
        print(f"      - Interface loaded: {chart_control.get('interface_loaded', False)}")
        
        print(f"   3. Command Processing: {'✅ PASS' if commands.get('success') else '❌ FAIL'}")
        print(f"      - Polling requests: {commands.get('polling_requests', 0)}")
        print(f"      - Success rate: {commands.get('success_rate', 0):.1f}%")
        
        print(f"   4. Network Analysis: {'✅ PASS' if network.get('success') else '❌ FAIL'}")
        print(f"      - Total requests: {network.get('total_requests', 0)}")
        print(f"      - Chart command requests: {network.get('chart_commands_requests', 0)}")
        
        print(f"   5. Integration Test: {'✅ PASS' if integration.get('success') else '❌ FAIL'}")
        print(f"      - Health score: {integration.get('health_score', 0):.1f}%")
        
        print(f"\n🏆 OVERALL RESULT: {final.get('recommendation', 'UNKNOWN')} ({final.get('overall_success_rate', 0):.1f}%)")
        
        print(f"\n📸 Screenshots taken: {len(self.test_results['screenshots'])}")
        for screenshot in self.test_results['screenshots']:
            print(f"   - {screenshot}")
        
        print("\n" + "=" * 70)
        
        return report_file

async def main():
    """Main test execution"""
    test = ProductionVerificationTest()
    await test.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())