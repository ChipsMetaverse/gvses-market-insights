#!/usr/bin/env python3
"""
Comprehensive Production Network Traffic Analysis Test

This test verifies that the localhost:8000 polling bug has been resolved
and the production deployment is correctly configured for Agent Builder integration.

Requirements:
- pip install playwright pytest
- playwright install
"""

import asyncio
import json
import time
from datetime import datetime
try:
    from typing import Dict, List, Any
except ImportError:
    # Fallback for older Python versions
    Dict = dict
    List = list
    Any = object

from playwright.async_api import async_playwright, Page, Route, Request, Response
import pytest

class NetworkTrafficAnalyzer:
    def __init__(self):
        self.requests = []  # List[Dict[str, Any]]
        self.responses = []  # List[Dict[str, Any]]
        self.console_logs = []  # List[Dict[str, Any]]
        self.errors = []  # List[str]
        self.start_time = None
        
    def add_request(self, request):
        """Track outgoing requests"""
        if self.start_time is None:
            self.start_time = time.time()
            
        self.requests.append({
            'timestamp': time.time(),
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers),
            'relative_time': time.time() - self.start_time
        })
    
    def add_response(self, response):
        """Track response data"""
        self.responses.append({
            'timestamp': time.time(),
            'url': response.url,
            'status': response.status,
            'headers': dict(response.headers),
            'relative_time': time.time() - self.start_time
        })
    
    def add_console_log(self, msg):
        """Track console messages"""
        self.console_logs.append({
            'timestamp': time.time(),
            'type': msg.type,
            'text': msg.text,
            'relative_time': time.time() - self.start_time if self.start_time else 0
        })
    
    def analyze_traffic(self):
        """Analyze collected network traffic"""
        localhost_requests = [r for r in self.requests if 'localhost:8000' in r['url']]
        production_api_requests = [r for r in self.requests if 'gvses-market-insights.fly.dev/api' in r['url']]
        chart_command_requests = [r for r in self.requests if '/api/chart/commands' in r['url']]
        
        # Analyze console logs
        chart_processor_logs = [l for l in self.console_logs if 'Chart Command Processor' in l['text']]
        error_logs = [l for l in self.console_logs if l['type'] in ['error', 'warning']]
        
        # Calculate request frequencies
        if self.start_time:
            duration = time.time() - self.start_time
            localhost_frequency = len(localhost_requests) / duration * 60 if duration > 0 else 0
            production_frequency = len(production_api_requests) / duration * 60 if duration > 0 else 0
        else:
            localhost_frequency = 0
            production_frequency = 0
        
        return {
            'summary': {
                'test_duration_seconds': duration if self.start_time else 0,
                'total_requests': len(self.requests),
                'localhost_bug_fixed': len(localhost_requests) == 0,
                'production_api_active': len(production_api_requests) > 0,
                'chart_commands_working': len(chart_command_requests) > 0
            },
            'localhost_analysis': {
                'count': len(localhost_requests),
                'frequency_per_minute': localhost_frequency,
                'requests': localhost_requests[:5]  # First 5 for debugging
            },
            'production_analysis': {
                'count': len(production_api_requests),
                'frequency_per_minute': production_frequency,
                'chart_command_count': len(chart_command_requests),
                'requests': production_api_requests[:5]  # First 5 for debugging
            },
            'console_analysis': {
                'chart_processor_active': len(chart_processor_logs) > 0,
                'chart_processor_count': len(chart_processor_logs),
                'error_count': len(error_logs),
                'recent_logs': self.console_logs[-10:] if self.console_logs else []
            },
            'status_codes': self._analyze_status_codes(),
            'bundle_analysis': self._analyze_bundles()
        }
    
    def _analyze_status_codes(self):
        """Analyze HTTP status codes"""
        status_counts = {}
        for response in self.responses:
            status = response['status']
            status_counts[str(status)] = status_counts.get(str(status), 0) + 1
        return status_counts
    
    def _analyze_bundles(self):
        """Analyze JavaScript bundle requests"""
        js_requests = [r for r in self.requests if r['url'].endswith('.js')]
        bundle_requests = [r for r in js_requests if any(keyword in r['url'] for keyword in ['bundle', 'chunk', 'main'])]
        
        return {
            'total_js_files': len(js_requests),
            'bundle_files': len(bundle_requests),
            'bundle_urls': [r['url'] for r in bundle_requests]
        }

@pytest.mark.asyncio
async def test_production_network_traffic_analysis():
    """
    Comprehensive test to verify production deployment and localhost bug fix
    """
    analyzer = NetworkTrafficAnalyzer()
    
    async with async_playwright() as p:
        # Launch browser with network events enabled
        browser = await p.chromium.launch(headless=False)  # Keep visible for debugging
        context = await browser.new_context()
        page = await context.new_page()
        
        # Set up network monitoring
        page.on('request', analyzer.add_request)
        page.on('response', analyzer.add_response)
        page.on('console', analyzer.add_console_log)
        
        try:
            print("🚀 Starting Production Network Traffic Analysis...")
            print("=" * 60)
            
            # Phase 1: Navigate to Production
            print("📍 Phase 1: Loading production site...")
            await page.goto('https://gvses-market-insights.fly.dev', wait_until='networkidle')
            await asyncio.sleep(5)  # Allow initial page load
            
            # Phase 2: Check JavaScript Bundles
            print("📦 Phase 2: Analyzing JavaScript bundles...")
            bundle_content = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script[src]'));
                    return scripts.map(script => ({
                        src: script.src,
                        hasLocalhost: script.src.includes('localhost'),
                        isBundle: script.src.includes('bundle') || script.src.includes('chunk')
                    }));
                }
            """)
            
            print(f"Found {len(bundle_content)} script tags")
            for script in bundle_content:
                if script['hasLocalhost']:
                    analyzer.errors.append(f"JavaScript bundle contains localhost: {script['src']}")
                    print(f"❌ LOCALHOST DETECTED: {script['src']}")
                else:
                    print(f"✅ Production bundle: {script['src']}")
            
            # Phase 3: Activate Chart Control
            print("🎯 Phase 3: Activating Chart Control...")
            
            # Wait for the page to load completely
            await page.wait_for_selector('[data-testid="chart-control-tab"], .tab-button:has-text("Chart Control")', timeout=10000)
            
            # Try multiple selectors for the Chart Control tab
            chart_control_activated = False
            selectors_to_try = [
                '[data-testid="chart-control-tab"]',
                '.tab-button:has-text("Chart Control")',
                'button:has-text("Chart Control")',
                '.tab:has-text("Chart Control")'
            ]
            
            for selector in selectors_to_try:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        await element.click()
                        print(f"✅ Chart Control activated using selector: {selector}")
                        chart_control_activated = True
                        break
                except Exception as e:
                    print(f"❌ Failed to click {selector}: {e}")
            
            if not chart_control_activated:
                print("❌ Could not activate Chart Control - trying JavaScript click")
                await page.evaluate("""
                    () => {
                        const buttons = Array.from(document.querySelectorAll('button, .tab-button, .tab'));
                        const chartButton = buttons.find(btn => 
                            btn.textContent && btn.textContent.includes('Chart Control')
                        );
                        if (chartButton) {
                            chartButton.click();
                            return true;
                        }
                        return false;
                    }
                """)
            
            await asyncio.sleep(3)  # Allow chart control to initialize
            
            # Phase 4: Monitor Network Traffic
            print("🔍 Phase 4: Monitoring network traffic for 60 seconds...")
            monitor_start = time.time()
            
            # Send some test commands to trigger polling
            await page.evaluate("""
                () => {
                    // Try to trigger chart command processing
                    if (window.chartCommandProcessor) {
                        console.log('Chart Command Processor found - sending test command');
                        window.chartCommandProcessor.processCommand('show TSLA');
                    } else {
                        console.log('Chart Command Processor not found in window');
                    }
                }
            """)
            
            # Monitor for 60 seconds with periodic checks
            for i in range(12):  # 12 iterations * 5 seconds = 60 seconds
                await asyncio.sleep(5)
                elapsed = time.time() - monitor_start
                print(f"⏱️  Monitoring... {elapsed:.1f}s elapsed")
                
                # Check for localhost requests periodically
                localhost_count = len([r for r in analyzer.requests if 'localhost:8000' in r['url']])
                if localhost_count > 0:
                    print(f"❌ LOCALHOST REQUESTS DETECTED: {localhost_count}")
                
                # Trigger more chart activity
                if i % 3 == 0:  # Every 15 seconds
                    await page.evaluate("""
                        () => {
                            console.log('Chart Command Processor: Periodic activity check');
                            // Try to trigger polling
                            if (window.location.hash !== '#chart-control') {
                                window.location.hash = 'chart-control';
                            }
                        }
                    """)
            
            print("✅ 60-second monitoring complete")
            
            # Phase 5: Final Analysis
            print("📊 Phase 5: Analyzing results...")
            results = analyzer.analyze_traffic()
            
            # Print comprehensive results
            print("\n" + "=" * 60)
            print("🎯 PRODUCTION NETWORK TRAFFIC ANALYSIS RESULTS")
            print("=" * 60)
            
            summary = results['summary']
            print(f"📈 Test Duration: {summary['test_duration_seconds']:.1f} seconds")
            print(f"📊 Total Network Requests: {summary['total_requests']}")
            print(f"🎯 Localhost Bug Fixed: {'✅ YES' if summary['localhost_bug_fixed'] else '❌ NO'}")
            print(f"🌐 Production API Active: {'✅ YES' if summary['production_api_active'] else '❌ NO'}")
            print(f"🎮 Chart Commands Working: {'✅ YES' if summary['chart_commands_working'] else '❌ NO'}")
            
            print("\n🔍 LOCALHOST ANALYSIS:")
            localhost_analysis = results['localhost_analysis']
            print(f"  • Localhost requests: {localhost_analysis['count']}")
            print(f"  • Request frequency: {localhost_analysis['frequency_per_minute']:.2f}/minute")
            if localhost_analysis['requests']:
                print("  • Sample requests:")
                for req in localhost_analysis['requests']:
                    print(f"    - {req['method']} {req['url']} (t+{req['relative_time']:.1f}s)")
            
            print("\n🌐 PRODUCTION ANALYSIS:")
            prod_analysis = results['production_analysis']
            print(f"  • Production API requests: {prod_analysis['count']}")
            print(f"  • Request frequency: {prod_analysis['frequency_per_minute']:.2f}/minute")
            print(f"  • Chart command requests: {prod_analysis['chart_command_count']}")
            
            print("\n💻 CONSOLE ANALYSIS:")
            console_analysis = results['console_analysis']
            print(f"  • Chart processor active: {'✅ YES' if console_analysis['chart_processor_active'] else '❌ NO'}")
            print(f"  • Chart processor logs: {console_analysis['chart_processor_count']}")
            print(f"  • Console errors: {console_analysis['error_count']}")
            
            if console_analysis['recent_logs']:
                print("  • Recent console activity:")
                for log in console_analysis['recent_logs'][-5:]:
                    print(f"    - [{log['type']}] {log['text'][:100]}... (t+{log['relative_time']:.1f}s)")
            
            print("\n📦 BUNDLE ANALYSIS:")
            bundle_analysis = results['bundle_analysis']
            print(f"  • Total JS files loaded: {bundle_analysis['total_js_files']}")
            print(f"  • Bundle files: {bundle_analysis['bundle_files']}")
            for url in bundle_analysis['bundle_urls']:
                localhost_in_bundle = 'localhost' in url
                print(f"    - {'❌' if localhost_in_bundle else '✅'} {url}")
            
            print("\n🔢 HTTP STATUS CODES:")
            for status, count in results['status_codes'].items():
                status_emoji = "✅" if status.startswith('2') else "⚠️" if status.startswith('3') else "❌"
                print(f"  • {status_emoji} {status}: {count} requests")
            
            # Final verdict
            print("\n" + "=" * 60)
            print("🏆 FINAL VERDICT:")
            
            localhost_bug_fixed = results['summary']['localhost_bug_fixed']
            production_active = results['summary']['production_api_active']
            
            if localhost_bug_fixed and production_active:
                print("✅ SUCCESS: Localhost bug is FIXED, production deployment is WORKING!")
                print("✅ Agent Builder integration should be functional")
            elif localhost_bug_fixed and not production_active:
                print("⚠️  PARTIAL: Localhost bug fixed, but no production API activity detected")
                print("   This might be normal if Chart Control wasn't properly activated")
            elif not localhost_bug_fixed:
                print("❌ FAILURE: Localhost bug is NOT fixed - still polling localhost:8000")
                print(f"   Found {localhost_analysis['count']} localhost requests")
            else:
                print("⚠️  MIXED RESULTS: Review detailed analysis above")
            
            print("=" * 60)
            
            # Save detailed results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"/Volumes/WD My Passport 264F Media/claude-voice-mcp/production_test_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            print(f"📄 Detailed results saved to: {results_file}")
            
            # Assertions for pytest
            assert localhost_bug_fixed, f"Localhost bug not fixed - found {localhost_analysis['count']} localhost requests"
            assert summary['total_requests'] > 0, "No network requests detected"
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            raise
        
        finally:
            # Keep browser open for manual inspection if needed
            print("\n🔍 Browser will remain open for manual inspection...")
            print("Press Enter to close browser and complete test...")
            # input()  # Comment out for automated runs
            await browser.close()

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_production_network_traffic_analysis())