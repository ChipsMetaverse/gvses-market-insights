#!/usr/bin/env python3
"""
Comprehensive Frontend Integration Test
Tests JavaScript bundle analysis, chart command processing, and end-to-end integration
"""

import asyncio
import aiohttp
import json
import time
import re
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright
import subprocess
import os
from datetime import datetime

class FrontendIntegrationTester:
    def __init__(self):
        self.production_url = "https://gvses-market-insights.fly.dev"
        self.localhost_url = "http://localhost:5174"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "bundle_analysis": {},
            "chart_processing": {},
            "api_commands": {},
            "e2e_integration": {},
            "selector_investigation": {}
        }
        self.test_url = None
    
    async def determine_test_url(self):
        """Determine which URL to use for testing"""
        # Try production first
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.production_url}/health", timeout=5) as resp:
                    if resp.status == 200:
                        self.test_url = self.production_url
                        print(f"✅ Using production URL: {self.production_url}")
                        return
        except:
            pass
        
        # Fallback to localhost
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.localhost_url}", timeout=5) as resp:
                    if resp.status == 200:
                        self.test_url = self.localhost_url
                        print(f"✅ Using localhost URL: {self.localhost_url}")
                        return
        except:
            pass
        
        # Default to localhost if nothing works
        self.test_url = self.localhost_url
        print(f"⚠️  Using default localhost URL: {self.localhost_url}")
        
    async def test_javascript_bundle_analysis(self, page):
        """Analyze the JavaScript bundle served by production site"""
        print("🔍 Testing JavaScript Bundle Analysis...")
        
        try:
            # Navigate to test site
            response = await page.goto(self.test_url)
            print(f"Production site loaded: {response.status}")
            
            # Wait for page to fully load
            await page.wait_for_load_state('networkidle')
            
            # Find all script tags with src attributes
            script_urls = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[src]'));
                    return scripts.map(script => script.src);
                }
            """)
            
            print(f"Found {len(script_urls)} script URLs")
            
            # Analyze each bundle
            bundle_details = []
            for script_url in script_urls:
                if script_url and ('index' in script_url or 'main' in script_url):
                    print(f"Analyzing bundle: {script_url}")
                    
                    # Download bundle content
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(script_url) as resp:
                                if resp.status == 200:
                                    bundle_content = await resp.text()
                                    
                                    # Check for localhost references
                                    localhost_refs = len(re.findall(r'localhost:8000', bundle_content))
                                    prod_refs = len(re.findall(r'claude-voice-mcp\.fly\.dev', bundle_content))
                                    api_refs = len(re.findall(r'/api/', bundle_content))
                                    
                                    bundle_info = {
                                        "url": script_url,
                                        "size_kb": len(bundle_content) // 1024,
                                        "localhost_references": localhost_refs,
                                        "production_references": prod_refs,
                                        "api_references": api_refs,
                                        "contains_localhost": localhost_refs > 0
                                    }
                                    
                                    bundle_details.append(bundle_info)
                                    print(f"  Size: {bundle_info['size_kb']}KB")
                                    print(f"  Localhost refs: {localhost_refs}")
                                    print(f"  Production refs: {prod_refs}")
                                    
                    except Exception as e:
                        print(f"Error downloading bundle {script_url}: {e}")
            
            # Check current environment variables in the browser
            env_check = await page.evaluate("""
                () => {
                    // Try to access any exposed environment variables
                    return {
                        baseURL: window.location.origin,
                        hasViteEnv: typeof import !== 'undefined',
                        userAgent: navigator.userAgent
                    };
                }
            """)
            
            self.results["bundle_analysis"] = {
                "bundles": bundle_details,
                "total_bundles": len(bundle_details),
                "has_localhost_refs": any(b.get("contains_localhost", False) for b in bundle_details),
                "environment_check": env_check,
                "status": "completed"
            }
            
            print("✅ Bundle analysis completed")
            
        except Exception as e:
            print(f"❌ Bundle analysis failed: {e}")
            self.results["bundle_analysis"]["error"] = str(e)
    
    async def test_chart_command_processing(self, page):
        """Test chart command processing functionality"""
        print("📊 Testing Chart Command Processing...")
        
        try:
            # Navigate to Chart Control tab
            await page.click('text=Chart Control')
            await page.wait_for_timeout(2000)
            
            # Set up console log monitoring
            console_logs = []
            def handle_console(msg):
                if "Chart Command Processor" in msg.text:
                    console_logs.append({
                        "timestamp": time.time(),
                        "text": msg.text,
                        "type": msg.type
                    })
            
            page.on("console", handle_console)
            
            # Wait for chart to load
            await page.wait_for_selector('.chart-container', timeout=10000)
            
            # Check for chart command processor activity
            await page.wait_for_timeout(5000)  # Wait for potential command processing
            
            # Test chart element existence
            chart_elements = await page.evaluate("""
                () => {
                    const elements = {
                        tradingChart: document.querySelector('.trading-chart'),
                        chartContainer: document.querySelector('.chart-container'),
                        chartCanvas: document.querySelector('canvas'),
                        chartDiv: document.querySelector('#chart'),
                        anyChartElement: document.querySelector('[class*="chart"]')
                    };
                    
                    return {
                        elements: Object.keys(elements).reduce((acc, key) => {
                            acc[key] = elements[key] !== null;
                            return acc;
                        }, {}),
                        chartClasses: Array.from(document.querySelectorAll('[class*="chart"]')).map(el => ({
                            tagName: el.tagName,
                            className: el.className,
                            id: el.id
                        }))
                    };
                }
            """)
            
            # Test if useChartCommandProcessor hook is active
            hook_activity = await page.evaluate("""
                () => {
                    // Try to detect React hook activity
                    const reactFiber = document.querySelector('#root')?._reactInternalFiber ||
                                     document.querySelector('#root')?._reactInternals;
                    return {
                        reactDetected: !!reactFiber,
                        timestamp: Date.now()
                    };
                }
            """)
            
            self.results["chart_processing"] = {
                "console_logs": console_logs,
                "chart_elements": chart_elements,
                "hook_activity": hook_activity,
                "logs_detected": len(console_logs) > 0,
                "status": "completed"
            }
            
            print(f"Console logs captured: {len(console_logs)}")
            print(f"Chart elements found: {chart_elements}")
            print("✅ Chart command processing test completed")
            
        except Exception as e:
            print(f"❌ Chart command processing test failed: {e}")
            self.results["chart_processing"]["error"] = str(e)
    
    async def test_api_command_queue(self):
        """Test API command queue functionality"""
        print("🔄 Testing API Command Queue...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Check current command queue
                queue_url = f"{self.test_url}/api/chart/commands"
                async with session.get(queue_url) as resp:
                    if resp.status == 200:
                        commands = await resp.json()
                        print(f"Current command queue: {len(commands)} commands")
                        
                        # Add a test command
                        test_command = {
                            "action": "change_symbol",
                            "symbol": "AAPL",
                            "timestamp": time.time(),
                            "source": "integration_test"
                        }
                        
                        add_url = f"{self.test_url}/api/chart/commands"
                        async with session.post(add_url, json=test_command) as add_resp:
                            add_result = await add_resp.json() if add_resp.status == 200 else None
                            
                            # Check queue again
                            async with session.get(queue_url) as check_resp:
                                updated_commands = await check_resp.json() if check_resp.status == 200 else []
                                
                                self.results["api_commands"] = {
                                    "initial_queue_size": len(commands),
                                    "initial_commands": commands[:3],  # First 3 for brevity
                                    "test_command_added": add_resp.status == 200,
                                    "updated_queue_size": len(updated_commands),
                                    "queue_processing": len(updated_commands) != len(commands) + 1,
                                    "status": "completed"
                                }
                    else:
                        print(f"Failed to get command queue: {resp.status}")
                        self.results["api_commands"]["error"] = f"HTTP {resp.status}"
            
            print("✅ API command queue test completed")
            
        except Exception as e:
            print(f"❌ API command queue test failed: {e}")
            self.results["api_commands"]["error"] = str(e)
    
    async def test_e2e_integration(self, page):
        """Test end-to-end integration flow"""
        print("🔗 Testing End-to-End Integration...")
        
        try:
            # Simulate Agent Builder → MCP → Chart Control API flow
            
            # 1. Test MCP endpoint directly
            async with aiohttp.ClientSession() as session:
                mcp_payload = {
                    "jsonrpc": "2.0",
                    "id": "test-e2e",
                    "method": "tools/call",
                    "params": {
                        "name": "change_chart_symbol",
                        "arguments": {"symbol": "MSFT"}
                    }
                }
                
                mcp_url = f"{self.test_url}/api/mcp"
                async with session.post(mcp_url, json=mcp_payload) as mcp_resp:
                    mcp_result = await mcp_resp.json() if mcp_resp.status == 200 else None
                    
                    # 2. Check if command was added to queue
                    await asyncio.sleep(1)  # Brief delay
                    
                    queue_url = f"{self.test_url}/api/chart/commands"
                    async with session.get(queue_url) as queue_resp:
                        queue_commands = await queue_resp.json() if queue_resp.status == 200 else []
                        
                        # Look for recent MSFT command
                        recent_msft_command = None
                        for cmd in queue_commands:
                            if cmd.get("symbol") == "MSFT" and cmd.get("action") == "change_symbol":
                                if time.time() - cmd.get("timestamp", 0) < 60:  # Within last minute
                                    recent_msft_command = cmd
                                    break
            
            # 3. Test frontend command processing
            # Navigate back to Chart Control and monitor for activity
            await page.click('text=Chart Control')
            await page.wait_for_timeout(3000)
            
            # Monitor network requests for command polling
            network_requests = []
            def handle_request(request):
                if "/api/chart/commands" in request.url:
                    network_requests.append({
                        "url": request.url,
                        "method": request.method,
                        "timestamp": time.time()
                    })
            
            page.on("request", handle_request)
            await page.wait_for_timeout(10000)  # Wait for polling activity
            
            self.results["e2e_integration"] = {
                "mcp_response": mcp_result,
                "mcp_success": mcp_result is not None,
                "command_in_queue": recent_msft_command is not None,
                "frontend_polling": len(network_requests) > 0,
                "polling_requests": len(network_requests),
                "integration_complete": all([
                    mcp_result is not None,
                    recent_msft_command is not None,
                    len(network_requests) > 0
                ]),
                "status": "completed"
            }
            
            print(f"MCP response: {'✅' if mcp_result else '❌'}")
            print(f"Command queued: {'✅' if recent_msft_command else '❌'}")
            print(f"Frontend polling: {'✅' if len(network_requests) > 0 else '❌'}")
            print("✅ End-to-end integration test completed")
            
        except Exception as e:
            print(f"❌ End-to-end integration test failed: {e}")
            self.results["e2e_integration"]["error"] = str(e)
    
    async def investigate_missing_selector(self, page):
        """Investigate why .trading-chart selector is missing"""
        print("🔍 Investigating Missing .trading-chart Selector...")
        
        try:
            # Navigate to Chart Control tab
            await page.click('text=Chart Control')
            await page.wait_for_timeout(3000)
            
            # Comprehensive DOM analysis
            dom_analysis = await page.evaluate("""
                () => {
                    const analysis = {
                        allChartSelectors: [],
                        tradingElements: [],
                        chartContainers: [],
                        canvasElements: [],
                        reactComponents: []
                    };
                    
                    // Find all elements with 'chart' in class or id
                    document.querySelectorAll('*').forEach(el => {
                        const className = el.className?.toString() || '';
                        const id = el.id || '';
                        
                        if (className.includes('chart') || id.includes('chart')) {
                            analysis.allChartSelectors.push({
                                tagName: el.tagName,
                                className: className,
                                id: id,
                                textContent: el.textContent?.substring(0, 50)
                            });
                        }
                        
                        if (className.includes('trading') || id.includes('trading')) {
                            analysis.tradingElements.push({
                                tagName: el.tagName,
                                className: className,
                                id: id
                            });
                        }
                    });
                    
                    // Find canvas elements (likely chart renderers)
                    document.querySelectorAll('canvas').forEach(canvas => {
                        analysis.canvasElements.push({
                            width: canvas.width,
                            height: canvas.height,
                            className: canvas.className,
                            parentClass: canvas.parentElement?.className
                        });
                    });
                    
                    // Look for React component indicators
                    const root = document.querySelector('#root');
                    if (root) {
                        const reactKeys = Object.keys(root).filter(key => key.startsWith('_react'));
                        analysis.reactComponents = reactKeys;
                    }
                    
                    return analysis;
                }
            """)
            
            # Check current page title and URL
            page_info = {
                "title": await page.title(),
                "url": page.url,
                "current_tab": await page.evaluate("document.querySelector('.tab-button.active')?.textContent")
            }
            
            # Test specific selectors that should exist
            selector_tests = {}
            selectors_to_test = [
                '.trading-chart',
                '.chart-container', 
                '#chart',
                '[data-testid="chart"]',
                'canvas',
                '.lightweight-charts'
            ]
            
            for selector in selectors_to_test:
                try:
                    element = await page.query_selector(selector)
                    selector_tests[selector] = element is not None
                except:
                    selector_tests[selector] = False
            
            self.results["selector_investigation"] = {
                "dom_analysis": dom_analysis,
                "page_info": page_info,
                "selector_tests": selector_tests,
                "missing_trading_chart": not selector_tests.get('.trading-chart', False),
                "chart_elements_found": len(dom_analysis["allChartSelectors"]),
                "canvas_elements_found": len(dom_analysis["canvasElements"]),
                "status": "completed"
            }
            
            print(f"Chart elements found: {len(dom_analysis['allChartSelectors'])}")
            print(f"Canvas elements: {len(dom_analysis['canvasElements'])}")
            print(f"Trading chart selector exists: {selector_tests.get('.trading-chart', False)}")
            print("✅ Selector investigation completed")
            
        except Exception as e:
            print(f"❌ Selector investigation failed: {e}")
            self.results["selector_investigation"]["error"] = str(e)
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Frontend Integration Test")
        
        # Determine which URL to use
        await self.determine_test_url()
        print(f"Target: {self.test_url}")
        print("=" * 60)
        
        async with async_playwright() as p:
            # Use Chromium for better debugging capabilities
            browser = await p.chromium.launch(headless=False, devtools=True)
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (compatible; IntegrationTester/1.0)'
            )
            page = await context.new_page()
            
            try:
                # Run all test phases
                await self.test_javascript_bundle_analysis(page)
                await self.test_api_command_queue()
                await self.test_chart_command_processing(page)
                await self.test_e2e_integration(page)
                await self.investigate_missing_selector(page)
                
                # Generate summary
                self.generate_summary()
                
            except Exception as e:
                print(f"❌ Test suite failed: {e}")
                self.results["suite_error"] = str(e)
            
            finally:
                await browser.close()
        
        return self.results
    
    def generate_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        # Bundle Analysis Summary
        bundle = self.results.get("bundle_analysis", {})
        print(f"\n🔍 BUNDLE ANALYSIS:")
        if bundle.get("bundles"):
            total_size = sum(b.get("size_kb", 0) for b in bundle["bundles"])
            localhost_found = bundle.get("has_localhost_refs", False)
            print(f"  • Total bundles: {len(bundle['bundles'])}")
            print(f"  • Total size: {total_size}KB")
            print(f"  • Contains localhost refs: {'❌ YES' if localhost_found else '✅ NO'}")
        
        # Chart Processing Summary
        chart = self.results.get("chart_processing", {})
        print(f"\n📊 CHART PROCESSING:")
        print(f"  • Console logs captured: {len(chart.get('console_logs', []))}")
        print(f"  • Chart elements found: {'✅' if chart.get('chart_elements', {}).get('elements', {}).get('chartContainer') else '❌'}")
        
        # API Commands Summary
        api = self.results.get("api_commands", {})
        print(f"\n🔄 API COMMANDS:")
        if "initial_queue_size" in api:
            print(f"  • Initial queue size: {api['initial_queue_size']}")
            print(f"  • Test command added: {'✅' if api.get('test_command_added') else '❌'}")
        
        # E2E Integration Summary
        e2e = self.results.get("e2e_integration", {})
        print(f"\n🔗 E2E INTEGRATION:")
        if "integration_complete" in e2e:
            print(f"  • MCP response: {'✅' if e2e.get('mcp_success') else '❌'}")
            print(f"  • Command queued: {'✅' if e2e.get('command_in_queue') else '❌'}")
            print(f"  • Frontend polling: {'✅' if e2e.get('frontend_polling') else '❌'}")
            print(f"  • Integration complete: {'✅' if e2e.get('integration_complete') else '❌'}")
        
        # Selector Investigation Summary
        selector = self.results.get("selector_investigation", {})
        print(f"\n🔍 SELECTOR INVESTIGATION:")
        if "selector_tests" in selector:
            tests = selector["selector_tests"]
            print(f"  • .trading-chart exists: {'✅' if tests.get('.trading-chart') else '❌'}")
            print(f"  • .chart-container exists: {'✅' if tests.get('.chart-container') else '❌'}")
            print(f"  • Canvas elements: {'✅' if tests.get('canvas') else '❌'}")
        
        print(f"\n🏁 TEST COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
        
        # Save detailed results
        with open('comprehensive_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: comprehensive_test_results.json")

async def main():
    tester = FrontendIntegrationTester()
    results = await tester.run_comprehensive_test()
    
    # Print final status
    print("\n🎯 FINAL STATUS:")
    success_count = sum(1 for test in results.values() 
                       if isinstance(test, dict) and test.get("status") == "completed")
    total_tests = len([k for k in results.keys() if k != "timestamp"])
    print(f"Tests completed: {success_count}/{total_tests}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())