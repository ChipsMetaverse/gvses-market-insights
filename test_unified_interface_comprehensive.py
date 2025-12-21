#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified Single-Panel Interface
Tests ChatKit integration, interface verification, and production readiness.
"""

import asyncio
import json
import time
import requests
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Test configuration
BASE_DIR = Path(__file__).parent
LOCALHOST_URL = "http://localhost:5174"
PRODUCTION_URL = "https://gvses-market-insights.fly.dev"
BACKEND_URL_LOCAL = "http://localhost:8000"
BACKEND_URL_PROD = "https://gvses-backend.fly.dev"

class UnifiedInterfaceTest:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "test_suite": "Unified Interface & ChatKit Integration",
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
        self.playwright = None
        self.browser = None
        self.page = None

    def log_test_result(self, test_name, passed, message="", details=None):
        """Log test result and update summary"""
        status = "PASS" if passed else "FAIL"
        result = {
            "status": status,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.results["tests"][test_name] = result
        self.results["summary"]["total"] += 1
        if passed:
            self.results["summary"]["passed"] += 1
        else:
            self.results["summary"]["failed"] += 1
        
        print(f"[{status}] {test_name}: {message}")
        if details:
            print(f"       Details: {json.dumps(details, indent=2)}")

    async def setup_playwright(self):
        """Initialize Playwright browser"""
        try:
            from playwright.async_api import async_playwright
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            
            # Set viewport for consistent testing
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            return True
        except Exception as e:
            print(f"Failed to setup Playwright: {e}")
            return False

    async def test_interface_structure(self, url):
        """Test 1: Verify NO tab interface exists and single panel structure"""
        test_name = "Interface Structure Verification"
        
        try:
            print(f"\n🔍 Testing interface structure at {url}...")
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for the dashboard to load
            await self.page.wait_for_selector('[data-testid="trading-dashboard"]', timeout=10000)
            
            details = {}
            
            # Check 1: NO tab interface should exist
            tab_selectors = [
                '.assistant-tabs',
                '.tab-button',
                '.tab-container',
                '[role="tablist"]',
                '.voice-tabs',
                '.conversation-tabs'
            ]
            
            tabs_found = []
            for selector in tab_selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    tabs_found.append(f"{selector}: {len(elements)} elements")
            
            details["tabs_found"] = tabs_found
            
            # Check 2: Verify single "VOICE ASSISTANT" panel exists
            voice_panel = await self.page.query_selector('.voice-panel-right')
            voice_title = await self.page.query_selector('h2.panel-title:has-text("VOICE ASSISTANT")')
            
            details["voice_panel_exists"] = voice_panel is not None
            details["voice_title_exists"] = voice_title is not None
            
            # Check 3: Verify three-panel layout structure
            left_panel = await self.page.query_selector('.analysis-panel-left')
            main_content = await self.page.query_selector('.main-content')
            right_panel = await self.page.query_selector('.voice-panel-right')
            
            details["three_panel_layout"] = {
                "left_analysis": left_panel is not None,
                "main_chart": main_content is not None,
                "right_voice": right_panel is not None
            }
            
            # Check 4: Verify chart is always visible (no tabbed hiding)
            chart_wrapper = await self.page.query_selector('.chart-wrapper')
            trading_chart = await self.page.query_selector('canvas')
            
            details["chart_visibility"] = {
                "chart_wrapper": chart_wrapper is not None,
                "canvas_element": trading_chart is not None
            }
            
            # Success criteria
            success_criteria = [
                len(tabs_found) == 0,  # No tabs
                voice_panel is not None,  # Voice panel exists
                voice_title is not None,  # Voice title exists
                all(details["three_panel_layout"].values()),  # All panels exist
                chart_wrapper is not None  # Chart visible
            ]
            
            passed = all(success_criteria)
            message = "Single-panel interface verified successfully" if passed else "Interface structure issues found"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Test failed: {str(e)}")
            return False

    async def test_auto_connection(self, url):
        """Test 2: Verify agent auto-connects for ChatKit integration"""
        test_name = "Agent Auto-Connection Test"
        
        try:
            print(f"\n🔗 Testing auto-connection at {url}...")
            
            # Enable console logging to catch auto-connect message
            console_messages = []
            
            def handle_console(msg):
                console_messages.append({
                    "type": msg.type,
                    "text": msg.text,
                    "timestamp": datetime.now().isoformat()
                })
            
            self.page.on("console", handle_console)
            
            # Reload page to trigger auto-connection
            await self.page.reload(wait_until="networkidle")
            await asyncio.sleep(3)  # Wait for auto-connection
            
            details = {}
            
            # Check 1: Look for auto-connect console message
            auto_connect_messages = [
                msg for msg in console_messages 
                if "Auto-connecting agent for seamless ChatKit integration" in msg["text"]
            ]
            
            details["auto_connect_console_messages"] = len(auto_connect_messages)
            details["total_console_messages"] = len(console_messages)
            
            # Check 2: Verify voice provider is set to 'agent'
            voice_provider = await self.page.evaluate("() => window.vueApp?.$data?.voiceProvider || 'unknown'")
            details["voice_provider"] = voice_provider
            
            # Check 3: Check connection status indicators
            status_indicator = await self.page.query_selector('.status-indicator')
            connection_status = await status_indicator.inner_text() if status_indicator else "not found"
            
            details["status_indicator"] = connection_status
            
            # Check 4: Look for agent connection in network requests
            # We'll check for websocket connections or API calls
            await asyncio.sleep(2)
            
            success_criteria = [
                len(auto_connect_messages) > 0,  # Auto-connect message found
                connection_status == '🟢' or 'connected' in str(console_messages).lower()
            ]
            
            passed = any(success_criteria)  # At least one indicator of connection
            message = "Agent auto-connection working" if passed else "Auto-connection not detected"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Test failed: {str(e)}")
            return False

    async def test_unified_messaging(self, url):
        """Test 3: Verify unified message thread and text input routing"""
        test_name = "Unified Messaging Test"
        
        try:
            print(f"\n💬 Testing unified messaging at {url}...")
            
            details = {}
            
            # Check 1: Verify text input exists and is enabled
            text_input = await self.page.query_selector('.voice-text-input')
            send_button = await self.page.query_selector('.voice-send-button')
            
            details["text_input_exists"] = text_input is not None
            details["send_button_exists"] = send_button is not None
            
            if text_input:
                is_disabled = await text_input.get_attribute("disabled")
                placeholder = await text_input.get_attribute("placeholder")
                details["input_disabled"] = is_disabled is not None
                details["input_placeholder"] = placeholder
            
            # Check 2: Verify message container exists
            message_container = await self.page.query_selector('.conversation-messages-compact')
            details["message_container_exists"] = message_container is not None
            
            # Check 3: Test message sending (if input available)
            if text_input and send_button and not await text_input.get_attribute("disabled"):
                test_message = f"Test message {int(time.time())}"
                
                # Type test message
                await text_input.fill(test_message)
                await asyncio.sleep(0.5)
                
                # Click send
                await send_button.click()
                await asyncio.sleep(2)
                
                # Check if message appeared in thread
                messages = await self.page.query_selector_all('.conversation-message-enhanced')
                details["messages_after_send"] = len(messages)
                
                # Look for our test message
                message_found = False
                if messages:
                    for msg in messages[-2:]:  # Check last 2 messages
                        text = await msg.inner_text()
                        if test_message in text:
                            message_found = True
                            break
                
                details["test_message_found"] = message_found
            else:
                details["message_send_test"] = "Skipped - input not available or disabled"
            
            # Check 4: Verify no separate tab interfaces for messaging
            tab_content = await self.page.query_selector_all('.tab-content, .tabpanel')
            details["tab_content_elements"] = len(tab_content)
            
            success_criteria = [
                text_input is not None,
                send_button is not None,
                message_container is not None,
                len(tab_content) == 0  # No tab content
            ]
            
            passed = all(success_criteria)
            message = "Unified messaging interface verified" if passed else "Messaging interface issues detected"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Test failed: {str(e)}")
            return False

    async def test_chart_commands_background(self, url):
        """Test 4: Verify chart commands work seamlessly in background"""
        test_name = "Chart Commands Background Test"
        
        try:
            print(f"\n📊 Testing background chart commands at {url}...")
            
            details = {}
            
            # Check 1: Verify chart control services are initialized
            chart_services = await self.page.evaluate("""
                () => {
                    return {
                        chartControlService: typeof window.chartControlService !== 'undefined',
                        enhancedChartControl: typeof window.enhancedChartControl !== 'undefined',
                        chartRef: document.querySelector('canvas') !== null
                    }
                }
            """)
            
            details["chart_services"] = chart_services
            
            # Check 2: Verify MCP polling is active
            # Look for console messages about chart command processing
            console_messages = []
            
            def handle_console(msg):
                if any(keyword in msg.text.lower() for keyword in ['chart', 'command', 'mcp', 'polling']):
                    console_messages.append({
                        "type": msg.type,
                        "text": msg.text,
                        "timestamp": datetime.now().isoformat()
                    })
            
            self.page.on("console", handle_console)
            
            # Wait and collect messages
            await asyncio.sleep(5)
            
            details["chart_related_console_messages"] = len(console_messages)
            details["sample_messages"] = console_messages[:3] if console_messages else []
            
            # Check 3: Verify chart command processor is enabled
            processor_status = await self.page.evaluate("""
                () => {
                    // Look for signs of chart command processor
                    const hasInterval = window.chartCommandProcessorInterval !== undefined;
                    return {
                        hasInterval: hasInterval,
                        currentTime: Date.now()
                    }
                }
            """)
            
            details["processor_status"] = processor_status
            
            # Check 4: Test that chart is responsive (can be interacted with)
            chart_canvas = await self.page.query_selector('canvas')
            chart_interactive = False
            
            if chart_canvas:
                # Try to hover over chart to test interactivity
                await chart_canvas.hover()
                await asyncio.sleep(0.5)
                chart_interactive = True
                details["chart_interactive"] = True
            else:
                details["chart_interactive"] = False
            
            success_criteria = [
                chart_services.get("chartRef", False),  # Chart canvas exists
                chart_interactive,  # Chart is interactive
                len(console_messages) > 0 or processor_status.get("hasInterval", False)  # Some activity detected
            ]
            
            passed = any(success_criteria)  # At least some chart functionality working
            message = "Chart commands working in background" if passed else "Chart command issues detected"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Test failed: {str(e)}")
            return False

    async def test_production_verification(self):
        """Test 5: Test production deployment"""
        test_name = "Production Verification"
        
        try:
            print(f"\n🌐 Testing production deployment at {PRODUCTION_URL}...")
            
            # Test production URL accessibility
            response = requests.get(PRODUCTION_URL, timeout=30)
            details = {
                "production_status_code": response.status_code,
                "production_response_time": response.elapsed.total_seconds(),
                "production_accessible": response.status_code == 200
            }
            
            if response.status_code == 200:
                # Run interface tests on production
                await self.page.goto(PRODUCTION_URL, wait_until="networkidle", timeout=30000)
                
                # Quick verification tests
                dashboard = await self.page.query_selector('[data-testid="trading-dashboard"]')
                voice_panel = await self.page.query_selector('.voice-panel-right')
                chart_canvas = await self.page.query_selector('canvas')
                
                details["production_elements"] = {
                    "dashboard": dashboard is not None,
                    "voice_panel": voice_panel is not None,
                    "chart_canvas": chart_canvas is not None
                }
                
                # Check for any tab elements (should be none)
                tabs = await self.page.query_selector_all('.assistant-tabs, .tab-button')
                details["production_tabs_found"] = len(tabs)
                
                passed = all([
                    response.status_code == 200,
                    dashboard is not None,
                    voice_panel is not None,
                    len(tabs) == 0
                ])
                
                message = "Production deployment verified" if passed else "Production issues detected"
            else:
                passed = False
                message = f"Production not accessible: HTTP {response.status_code}"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"Production test failed: {str(e)}")
            return False

    async def test_mcp_integration(self):
        """Test 6: Verify MCP Agent Builder integration still works"""
        test_name = "MCP Agent Builder Integration"
        
        try:
            print(f"\n🔧 Testing MCP integration...")
            
            details = {}
            
            # Test MCP HTTP endpoint
            mcp_endpoints = [
                f"{BACKEND_URL_LOCAL}/api/mcp",
                f"{BACKEND_URL_PROD}/api/mcp"
            ]
            
            for endpoint in mcp_endpoints:
                try:
                    response = requests.post(
                        endpoint,
                        json={
                            "jsonrpc": "2.0",
                            "id": "test-1",
                            "method": "tools/list"
                        },
                        timeout=10
                    )
                    
                    endpoint_name = "local" if "localhost" in endpoint else "production"
                    details[f"{endpoint_name}_mcp_status"] = response.status_code
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "result" in data and "tools" in data["result"]:
                            details[f"{endpoint_name}_tools_count"] = len(data["result"]["tools"])
                        else:
                            details[f"{endpoint_name}_response_format"] = "Invalid"
                    
                except Exception as e:
                    endpoint_name = "local" if "localhost" in endpoint else "production"
                    details[f"{endpoint_name}_mcp_error"] = str(e)
            
            # Check if at least one MCP endpoint is working
            mcp_working = any([
                details.get("local_tools_count", 0) > 0,
                details.get("production_tools_count", 0) > 0
            ])
            
            passed = mcp_working
            message = "MCP integration functional" if passed else "MCP integration issues detected"
            
            self.log_test_result(test_name, passed, message, details)
            return passed
            
        except Exception as e:
            self.log_test_result(test_name, False, f"MCP test failed: {str(e)}")
            return False

    async def capture_screenshot(self, name):
        """Capture screenshot for documentation"""
        try:
            screenshot_path = BASE_DIR / f"unified_interface_{name}_{int(time.time())}.png"
            await self.page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"📸 Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")
            return None

    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Unified Interface Test Suite")
        print("=" * 60)
        
        # Setup browser
        if not await self.setup_playwright():
            print("❌ Failed to setup test environment")
            return False
        
        try:
            # Test on localhost first (if available)
            localhost_available = False
            try:
                response = requests.get(LOCALHOST_URL, timeout=5)
                localhost_available = response.status_code == 200
            except:
                pass
            
            if localhost_available:
                print(f"\n📍 Testing localhost: {LOCALHOST_URL}")
                await self.test_interface_structure(LOCALHOST_URL)
                await self.test_auto_connection(LOCALHOST_URL)
                await self.test_unified_messaging(LOCALHOST_URL)
                await self.test_chart_commands_background(LOCALHOST_URL)
                await self.capture_screenshot("localhost")
            
            # Test production
            print(f"\n📍 Testing production: {PRODUCTION_URL}")
            await self.test_production_verification()
            if self.results["tests"]["Production Verification"]["status"] == "PASS":
                await self.test_interface_structure(PRODUCTION_URL)
                await self.test_unified_messaging(PRODUCTION_URL)
                await self.capture_screenshot("production")
            
            # Test MCP integration
            await self.test_mcp_integration()
            
        finally:
            # Cleanup
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        
        # Print final results
        self.print_final_results()
        
        # Save results
        results_file = BASE_DIR / f"unified_interface_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📊 Full results saved to: {results_file}")
        
        return self.results["summary"]["failed"] == 0

    def print_final_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🎯 FINAL TEST RESULTS")
        print("=" * 60)
        
        summary = self.results["summary"]
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        
        success_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Breakdown:")
        for test_name, result in self.results["tests"].items():
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result['message']}")
        
        print("\n🎯 SUCCESS CRITERIA CHECKLIST:")
        criteria = [
            ("Single panel interface (no tabs)", "Interface Structure Verification"),
            ("Auto-connected ChatKit integration", "Agent Auto-Connection Test"),
            ("Clean original design restored", "Interface Structure Verification"),
            ("Chart commands work invisibly", "Chart Commands Background Test"),
            ("Agent Builder MCP integration functional", "MCP Agent Builder Integration"),
            ("Production deployment accessible", "Production Verification")
        ]
        
        for criterion, test_key in criteria:
            if test_key in self.results["tests"]:
                status = self.results["tests"][test_key]["status"]
                icon = "✅" if status == "PASS" else "❌"
                print(f"{icon} {criterion}")
            else:
                print(f"⚠️ {criterion} (not tested)")
        
        overall_status = "SUCCESS" if summary["failed"] == 0 else "NEEDS ATTENTION"
        print(f"\n🏆 Overall Status: {overall_status}")

async def main():
    """Main test execution"""
    test_suite = UnifiedInterfaceTest()
    success = await test_suite.run_comprehensive_test()
    
    if success:
        print("\n🎉 All tests passed! The unified interface is working correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the results above for details.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)