#!/usr/bin/env python3
"""
Production Bundle Analysis and Chart Command Processing Test
Focuses on the key findings from comprehensive test
"""

import asyncio
import aiohttp
import json
import time
import re
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from datetime import datetime

class ProductionBundleAnalyzer:
    def __init__(self):
        self.production_url = "https://gvses-market-insights.fly.dev"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "bundle_localhost_analysis": {},
            "chart_command_processing": {},
            "api_integration": {},
            "frontend_polling": {}
        }
    
    async def analyze_bundle_localhost_references(self):
        """Analyze JavaScript bundle for localhost references"""
        print("🔍 Analyzing Production Bundle for Localhost References...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Get the main page to find script URLs
                async with session.get(self.production_url) as resp:
                    if resp.status == 200:
                        html_content = await resp.text()
                        
                        # Extract script src URLs
                        script_matches = re.findall(r'<script[^>]*src="([^"]*)"[^>]*></script>', html_content)
                        
                        bundle_analysis = []
                        for script_src in script_matches:
                            if 'index-' in script_src or 'main-' in script_src:
                                full_url = urljoin(self.production_url, script_src)
                                print(f"Downloading bundle: {full_url}")
                                
                                async with session.get(full_url) as bundle_resp:
                                    if bundle_resp.status == 200:
                                        bundle_content = await bundle_resp.text()
                                        
                                        # Analyze localhost references
                                        localhost_patterns = [
                                            r'localhost:8000',
                                            r'localhost:5174',
                                            r'127\.0\.0\.1',
                                            r'http://localhost'
                                        ]
                                        
                                        localhost_findings = {}
                                        for pattern in localhost_patterns:
                                            matches = re.findall(pattern, bundle_content)
                                            if matches:
                                                localhost_findings[pattern] = {
                                                    "count": len(matches),
                                                    "examples": matches[:3]
                                                }
                                        
                                        # Look for production references
                                        prod_patterns = [
                                            r'gvses-market-insights\.fly\.dev',
                                            r'claude-voice-mcp\.fly\.dev'
                                        ]
                                        
                                        prod_findings = {}
                                        for pattern in prod_patterns:
                                            matches = re.findall(pattern, bundle_content)
                                            if matches:
                                                prod_findings[pattern] = {
                                                    "count": len(matches),
                                                    "examples": matches[:3]
                                                }
                                        
                                        # Look for API endpoint patterns
                                        api_patterns = [
                                            r'/api/[a-zA-Z-]+',
                                            r'api\..*?/',
                                            r'VITE_API_URL'
                                        ]
                                        
                                        api_findings = {}
                                        for pattern in api_patterns:
                                            matches = re.findall(pattern, bundle_content)
                                            if matches:
                                                api_findings[pattern] = {
                                                    "count": len(matches),
                                                    "examples": list(set(matches[:10]))  # Unique examples
                                                }
                                        
                                        bundle_analysis.append({
                                            "url": full_url,
                                            "size_kb": len(bundle_content) // 1024,
                                            "localhost_references": localhost_findings,
                                            "production_references": prod_findings,
                                            "api_references": api_findings,
                                            "has_localhost_issue": len(localhost_findings) > 0
                                        })
                        
                        self.results["bundle_localhost_analysis"] = {
                            "bundles_analyzed": len(bundle_analysis),
                            "bundles": bundle_analysis,
                            "critical_issue": any(b["has_localhost_issue"] for b in bundle_analysis),
                            "status": "completed"
                        }
                        
                        print(f"✅ Analyzed {len(bundle_analysis)} bundles")
                        for bundle in bundle_analysis:
                            print(f"  {bundle['url']}: {bundle['size_kb']}KB")
                            if bundle["has_localhost_issue"]:
                                print(f"    ⚠️  Contains localhost references: {bundle['localhost_references']}")
                            else:
                                print(f"    ✅ No localhost references found")
            
        except Exception as e:
            print(f"❌ Bundle analysis failed: {e}")
            self.results["bundle_localhost_analysis"]["error"] = str(e)
    
    async def test_chart_command_processing_production(self, page):
        """Test chart command processing on production with correct selectors"""
        print("📊 Testing Chart Command Processing (Production)...")
        
        try:
            # Navigate to production site
            await page.goto(self.production_url)
            await page.wait_for_load_state('networkidle')
            
            # Click Chart Control tab (it's already active based on previous test)
            chart_control_tab = await page.query_selector('text=Chart Control')
            if chart_control_tab:
                await chart_control_tab.click()
                await page.wait_for_timeout(2000)
            
            # Monitor console logs
            console_logs = []
            def handle_console(msg):
                if any(keyword in msg.text.lower() for keyword in ['chart', 'command', 'processor', 'polling']):
                    console_logs.append({
                        "timestamp": time.time(),
                        "text": msg.text,
                        "type": msg.type
                    })
            
            page.on("console", handle_console)
            
            # Wait for chart elements using correct selectors
            chart_found = False
            try:
                # Try the actual selectors found in DOM analysis
                await page.wait_for_selector('.trading-chart-container', timeout=10000)
                print("✅ Found .trading-chart-container")
                chart_found = True
            except:
                try:
                    await page.wait_for_selector('.main-chart', timeout=5000)
                    print("✅ Found .main-chart")
                    chart_found = True
                except:
                    print("⚠️  Chart containers not found within timeout")
            
            # Wait for canvas elements (actual chart rendering)
            canvas_elements = await page.query_selector_all('canvas')
            print(f"Found {len(canvas_elements)} canvas elements")
            
            # Check if chart command processor is active
            await page.wait_for_timeout(5000)
            
            # Test Chart Agent Chat component
            chart_agent = await page.query_selector('.chart-agent-chat')
            if chart_agent:
                print("✅ Chart Agent Chat component found")
                
                # Try to interact with it
                chat_input = await page.query_selector('.chart-agent-chat input')
                if chat_input:
                    await chat_input.fill("change chart to AAPL")
                    await page.keyboard.press('Enter')
                    print("✅ Sent test command to Chart Agent")
                    await page.wait_for_timeout(3000)
            
            self.results["chart_command_processing"] = {
                "chart_container_found": chart_found,
                "canvas_elements_count": len(canvas_elements),
                "chart_agent_found": chart_agent is not None,
                "console_logs": console_logs,
                "logs_captured": len(console_logs),
                "status": "completed"
            }
            
            print(f"Console logs captured: {len(console_logs)}")
            print("✅ Chart command processing test completed")
            
        except Exception as e:
            print(f"❌ Chart command processing test failed: {e}")
            self.results["chart_command_processing"]["error"] = str(e)
    
    async def test_api_integration_and_polling(self, page):
        """Test API integration and frontend polling"""
        print("🔄 Testing API Integration and Polling...")
        
        try:
            # Set up network request monitoring
            api_requests = []
            def handle_request(request):
                if any(endpoint in request.url for endpoint in ['/api/chart/commands', '/api/mcp', '/api/stock-price']):
                    api_requests.append({
                        "url": request.url,
                        "method": request.method,
                        "timestamp": time.time()
                    })
            
            page.on("request", handle_request)
            
            # Test direct API calls
            async with aiohttp.ClientSession() as session:
                # 1. Check command queue
                queue_url = f"{self.production_url}/api/chart/commands"
                async with session.get(queue_url) as resp:
                    commands_response = None
                    if resp.status == 200:
                        commands_response = await resp.json()
                        print(f"Current command queue: {len(commands_response)} commands")
                    
                # 2. Add a test command via MCP
                mcp_payload = {
                    "jsonrpc": "2.0",
                    "id": "bundle-test",
                    "method": "tools/call",
                    "params": {
                        "name": "change_chart_symbol",
                        "arguments": {"symbol": "TSLA"}
                    }
                }
                
                mcp_url = f"{self.production_url}/api/mcp"
                mcp_response = None
                try:
                    async with session.post(mcp_url, json=mcp_payload) as resp:
                        if resp.status == 200:
                            mcp_response = await resp.json()
                            print("✅ MCP command sent successfully")
                        else:
                            print(f"⚠️  MCP command failed: {resp.status}")
                except Exception as e:
                    print(f"⚠️  MCP request failed: {e}")
                
                # 3. Wait and check if command was queued
                await asyncio.sleep(2)
                async with session.get(queue_url) as resp:
                    updated_commands = None
                    if resp.status == 200:
                        updated_commands = await resp.json()
                        print(f"Updated command queue: {len(updated_commands)} commands")
            
            # Wait for frontend polling activity
            initial_request_count = len(api_requests)
            await page.wait_for_timeout(10000)  # 10 seconds for polling
            final_request_count = len(api_requests)
            
            polling_detected = final_request_count > initial_request_count
            
            # Count different types of requests
            request_types = {}
            for req in api_requests:
                endpoint = req['url'].split('/')[-1].split('?')[0]
                request_types[endpoint] = request_types.get(endpoint, 0) + 1
            
            self.results["api_integration"] = {
                "initial_commands": len(commands_response) if commands_response else 0,
                "mcp_success": mcp_response is not None,
                "updated_commands": len(updated_commands) if updated_commands else 0,
                "polling_detected": polling_detected,
                "total_requests": len(api_requests),
                "request_types": request_types,
                "status": "completed"
            }
            
            print(f"API requests captured: {len(api_requests)}")
            print(f"Polling detected: {'✅' if polling_detected else '❌'}")
            print(f"Request types: {request_types}")
            print("✅ API integration test completed")
            
        except Exception as e:
            print(f"❌ API integration test failed: {e}")
            self.results["api_integration"]["error"] = str(e)
    
    async def run_production_analysis(self):
        """Run comprehensive production analysis"""
        print("🚀 Starting Production Bundle and Integration Analysis")
        print(f"Target: {self.production_url}")
        print("=" * 60)
        
        # First, analyze bundle without browser
        await self.analyze_bundle_localhost_references()
        
        # Then test with browser
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # Use headless for production testing
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await self.test_chart_command_processing_production(page)
                await self.test_api_integration_and_polling(page)
                
                self.generate_production_summary()
                
            except Exception as e:
                print(f"❌ Browser tests failed: {e}")
                self.results["browser_error"] = str(e)
            
            finally:
                await browser.close()
        
        return self.results
    
    def generate_production_summary(self):
        """Generate production analysis summary"""
        print("\n" + "=" * 60)
        print("📋 PRODUCTION ANALYSIS SUMMARY")
        print("=" * 60)
        
        # Bundle Analysis
        bundle = self.results.get("bundle_localhost_analysis", {})
        if "bundles" in bundle:
            print(f"\n🔍 JAVASCRIPT BUNDLE ANALYSIS:")
            total_size = sum(b.get("size_kb", 0) for b in bundle["bundles"])
            print(f"  • Bundles analyzed: {len(bundle['bundles'])}")
            print(f"  • Total size: {total_size}KB")
            print(f"  • Critical localhost issue: {'❌ YES' if bundle.get('critical_issue') else '✅ NO'}")
            
            for i, b in enumerate(bundle["bundles"]):
                print(f"    Bundle {i+1}: {b['size_kb']}KB")
                if b.get("localhost_references"):
                    for pattern, details in b["localhost_references"].items():
                        print(f"      ⚠️  {pattern}: {details['count']} occurrences")
        
        # Chart Processing
        chart = self.results.get("chart_command_processing", {})
        print(f"\n📊 CHART PROCESSING:")
        print(f"  • Chart container found: {'✅' if chart.get('chart_container_found') else '❌'}")
        print(f"  • Canvas elements: {chart.get('canvas_elements_count', 0)}")
        print(f"  • Chart agent found: {'✅' if chart.get('chart_agent_found') else '❌'}")
        print(f"  • Console logs: {chart.get('logs_captured', 0)}")
        
        # API Integration
        api = self.results.get("api_integration", {})
        print(f"\n🔄 API INTEGRATION:")
        print(f"  • MCP endpoint working: {'✅' if api.get('mcp_success') else '❌'}")
        print(f"  • Frontend polling active: {'✅' if api.get('polling_detected') else '❌'}")
        print(f"  • Total API requests: {api.get('total_requests', 0)}")
        if api.get("request_types"):
            for endpoint, count in api["request_types"].items():
                print(f"    {endpoint}: {count} requests")
        
        print(f"\n🏁 ANALYSIS COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
        
        # Save results
        with open('production_analysis_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: production_analysis_results.json")

async def main():
    analyzer = ProductionBundleAnalyzer()
    results = await analyzer.run_production_analysis()
    
    # Print critical findings
    print("\n🎯 CRITICAL FINDINGS:")
    
    bundle = results.get("bundle_localhost_analysis", {})
    if bundle.get("critical_issue"):
        print("❌ LOCALHOST REFERENCES FOUND IN PRODUCTION BUNDLE")
        print("   This explains why the frontend may be trying to connect to localhost:8000")
        print("   instead of the production backend.")
    else:
        print("✅ No localhost references in production bundles")
    
    chart = results.get("chart_command_processing", {})
    if chart.get("chart_container_found") and chart.get("canvas_elements_count", 0) > 0:
        print("✅ Chart rendering is working correctly")
    else:
        print("❌ Chart rendering issues detected")
    
    api = results.get("api_integration", {})
    if api.get("mcp_success") and api.get("polling_detected"):
        print("✅ Complete integration chain is functional")
    else:
        print("❌ Integration chain has issues")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())