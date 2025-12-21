#!/usr/bin/env python3
"""
Comprehensive Playwright test to investigate and verify the unified ChatKit voice interface system.
Checks for console errors, API endpoints, WebSocket connections, and voice functionality.
"""

import asyncio
import json
import time
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatKitInvestigation:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "frontend_url": "http://localhost:5174",
            "backend_url": "http://localhost:8000",
            "console_errors": [],
            "api_endpoints": {},
            "websocket_tests": {},
            "react_hooks": {"violations": [], "valid": True},
            "component_loading": {},
            "screenshots": [],
            "overall_status": "unknown",
            "recommendations": []
        }
        self.browser = None
        self.page = None

    async def setup_browser(self):
        """Initialize Playwright browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=100)
        context = await self.browser.new_context(
            viewport={'width': 1400, 'height': 900},
            permissions=['microphone']
        )
        self.page = await context.new_page()
        
        # Capture console messages
        self.page.on("console", self._handle_console_message)
        self.page.on("pageerror", self._handle_page_error)
        
    async def _handle_console_message(self, msg):
        """Handle console messages from the page"""
        message_data = {
            "type": msg.type,
            "text": msg.text,
            "timestamp": datetime.now().isoformat()
        }
        
        if msg.type in ['error', 'warning']:
            self.results["console_errors"].append(message_data)
            logger.warning(f"Console {msg.type}: {msg.text}")
            
        # Check for specific React Hook violations
        if "Invalid hook call" in msg.text or "Hooks can only be called inside" in msg.text:
            self.results["react_hooks"]["violations"].append(message_data)
            self.results["react_hooks"]["valid"] = False
            
    async def _handle_page_error(self, error):
        """Handle JavaScript page errors"""
        error_data = {
            "type": "page_error",
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
        self.results["console_errors"].append(error_data)
        logger.error(f"Page error: {error}")

    async def test_api_endpoints(self):
        """Test critical API endpoints"""
        endpoints_to_test = [
            "/health",
            "/api/agent/orchestrate",
            "/api/chatkit/session", 
            "/api/technical-indicators",
            "/api/stock-price?symbol=TSLA",
            "/api/stock-news?symbol=TSLA",
            "/elevenlabs/signed-url"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints_to_test:
                url = f"http://localhost:8000{endpoint}"
                try:
                    if endpoint == "/api/agent/orchestrate":
                        # POST request with sample data
                        data = {"message": "test", "context": {}}
                        async with session.post(url, json=data, timeout=10) as response:
                            status = response.status
                            text = await response.text()
                    elif endpoint == "/api/chatkit/session":
                        # POST request to create session
                        data = {"user_id": "test_user"}
                        async with session.post(url, json=data, timeout=10) as response:
                            status = response.status
                            text = await response.text()
                    else:
                        async with session.get(url, timeout=10) as response:
                            status = response.status
                            text = await response.text()
                    
                    self.results["api_endpoints"][endpoint] = {
                        "status": status,
                        "response_preview": text[:200] if text else "",
                        "success": status < 400,
                        "error": None
                    }
                    
                    if status < 400:
                        logger.info(f"✅ {endpoint}: {status}")
                    else:
                        logger.warning(f"❌ {endpoint}: {status}")
                        
                except Exception as e:
                    self.results["api_endpoints"][endpoint] = {
                        "status": None,
                        "response_preview": "",
                        "success": False,
                        "error": str(e)
                    }
                    logger.error(f"❌ {endpoint}: {e}")

    async def test_frontend_loading(self):
        """Test frontend loading and component initialization"""
        try:
            logger.info("Loading frontend application...")
            
            # Navigate to frontend
            await self.page.goto("http://localhost:5174", wait_until="networkidle", timeout=30000)
            
            # Wait a bit for React to fully initialize
            await self.page.wait_for_timeout(3000)
            
            # Take initial screenshot
            screenshot_path = f"chatkit_initial_load_{int(time.time())}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            self.results["screenshots"].append({
                "name": "initial_load",
                "path": screenshot_path,
                "description": "Initial application load"
            })
            
            # Check if main components are present
            components_to_check = [
                {"selector": "[data-testid='trading-dashboard']", "name": "TradingDashboard"},
                {"selector": ".realtime-chat-kit", "name": "RealtimeChatKit"},
                {"selector": ".voice-interface", "name": "VoiceInterface"},
                {"selector": ".market-insights", "name": "MarketInsights"},
                {"selector": ".trading-chart", "name": "TradingChart"}
            ]
            
            for component in components_to_check:
                try:
                    element = await self.page.wait_for_selector(component["selector"], timeout=5000)
                    if element:
                        self.results["component_loading"][component["name"]] = {
                            "found": True,
                            "visible": await element.is_visible(),
                            "error": None
                        }
                        logger.info(f"✅ Component {component['name']} found and loaded")
                    else:
                        self.results["component_loading"][component["name"]] = {
                            "found": False,
                            "visible": False,
                            "error": "Element not found"
                        }
                except Exception as e:
                    self.results["component_loading"][component["name"]] = {
                        "found": False,
                        "visible": False,
                        "error": str(e)
                    }
                    logger.warning(f"⚠️  Component {component['name']} not found: {e}")
            
            self.results["component_loading"]["overall_success"] = True
            logger.info("Frontend loading test completed")
            
        except Exception as e:
            self.results["component_loading"]["overall_success"] = False
            self.results["component_loading"]["error"] = str(e)
            logger.error(f"Frontend loading failed: {e}")

    async def test_websocket_connections(self):
        """Test WebSocket connection capabilities"""
        websocket_endpoints = [
            {"url": "ws://localhost:8000/mcp", "name": "MCP WebSocket"},
            {"url": "ws://localhost:8000/ws/quotes", "name": "Quotes WebSocket"},
            {"url": "ws://localhost:8000/ws/voice-relay", "name": "Voice Relay WebSocket"}
        ]
        
        for endpoint in websocket_endpoints:
            try:
                # Test WebSocket connection from the page
                ws_test_script = f"""
                new Promise((resolve) => {{
                    try {{
                        const ws = new WebSocket('{endpoint["url"]}');
                        const timeout = setTimeout(() => {{
                            ws.close();
                            resolve({{ success: false, error: 'Connection timeout' }});
                        }}, 5000);
                        
                        ws.onopen = () => {{
                            clearTimeout(timeout);
                            ws.close();
                            resolve({{ success: true, error: null }});
                        }};
                        
                        ws.onerror = (error) => {{
                            clearTimeout(timeout);
                            resolve({{ success: false, error: error.toString() }});
                        }};
                    }} catch (error) {{
                        resolve({{ success: false, error: error.toString() }});
                    }}
                }})
                """
                
                result = await self.page.evaluate(ws_test_script)
                self.results["websocket_tests"][endpoint["name"]] = result
                
                if result["success"]:
                    logger.info(f"✅ WebSocket {endpoint['name']}: Connection successful")
                else:
                    logger.warning(f"❌ WebSocket {endpoint['name']}: {result['error']}")
                    
            except Exception as e:
                self.results["websocket_tests"][endpoint["name"]] = {
                    "success": False,
                    "error": str(e)
                }
                logger.error(f"❌ WebSocket {endpoint['name']}: {e}")

    async def test_voice_interface_interaction(self):
        """Test voice interface if available"""
        try:
            # Look for voice interface elements
            voice_button = await self.page.query_selector(".voice-toggle, .voice-start, [data-testid='voice-button']")
            
            if voice_button:
                logger.info("Voice interface button found, testing interaction...")
                
                # Take screenshot before interaction
                screenshot_path = f"voice_interface_before_{int(time.time())}.png"
                await self.page.screenshot(path=screenshot_path, full_page=True)
                self.results["screenshots"].append({
                    "name": "voice_interface_before",
                    "path": screenshot_path,
                    "description": "Voice interface before interaction"
                })
                
                # Try to click the voice button
                await voice_button.click()
                await self.page.wait_for_timeout(2000)
                
                # Take screenshot after interaction
                screenshot_path = f"voice_interface_after_{int(time.time())}.png"
                await self.page.screenshot(path=screenshot_path, full_page=True)
                self.results["screenshots"].append({
                    "name": "voice_interface_after",
                    "path": screenshot_path,
                    "description": "Voice interface after clicking"
                })
                
                self.results["voice_interface"] = {
                    "button_found": True,
                    "interaction_attempted": True,
                    "error": None
                }
                
            else:
                self.results["voice_interface"] = {
                    "button_found": False,
                    "interaction_attempted": False,
                    "error": "Voice button not found"
                }
                logger.warning("Voice interface button not found")
                
        except Exception as e:
            self.results["voice_interface"] = {
                "button_found": False,
                "interaction_attempted": False,
                "error": str(e)
            }
            logger.error(f"Voice interface test failed: {e}")

    async def analyze_network_requests(self):
        """Analyze network requests for failures"""
        # Monitor network requests
        failed_requests = []
        
        def handle_response(response):
            if response.status >= 400:
                failed_requests.append({
                    "url": response.url,
                    "status": response.status,
                    "method": response.request.method
                })
        
        self.page.on("response", handle_response)
        
        # Trigger some interactions to generate requests
        await self.page.reload(wait_until="networkidle")
        await self.page.wait_for_timeout(3000)
        
        self.results["network_failures"] = failed_requests
        if failed_requests:
            logger.warning(f"Found {len(failed_requests)} failed network requests")
        else:
            logger.info("No failed network requests detected")

    def analyze_results(self):
        """Analyze all test results and generate recommendations"""
        recommendations = []
        
        # Check console errors
        error_count = len([e for e in self.results["console_errors"] if e["type"] == "error"])
        if error_count > 0:
            recommendations.append(f"Fix {error_count} console errors for better stability")
        
        # Check React Hook violations
        if not self.results["react_hooks"]["valid"]:
            recommendations.append("Critical: Fix React Hook violations - these prevent proper component functioning")
        
        # Check API endpoints
        failed_endpoints = [k for k, v in self.results["api_endpoints"].items() if not v["success"]]
        if failed_endpoints:
            recommendations.append(f"Fix API endpoints: {', '.join(failed_endpoints)}")
        
        # Check WebSocket connections
        failed_websockets = [k for k, v in self.results["websocket_tests"].items() if not v["success"]]
        if failed_websockets:
            recommendations.append(f"Fix WebSocket connections: {', '.join(failed_websockets)}")
        
        # Check component loading
        if not self.results["component_loading"].get("overall_success", False):
            recommendations.append("Critical: Frontend components not loading properly")
        
        # Overall status
        critical_issues = any([
            not self.results["react_hooks"]["valid"],
            not self.results["component_loading"].get("overall_success", False),
            len(failed_endpoints) > 3
        ])
        
        if critical_issues:
            self.results["overall_status"] = "critical_issues"
        elif failed_endpoints or failed_websockets:
            self.results["overall_status"] = "minor_issues"
        else:
            self.results["overall_status"] = "healthy"
        
        self.results["recommendations"] = recommendations

    async def generate_report(self):
        """Generate comprehensive test report"""
        self.analyze_results()
        
        report_path = f"chatkit_investigation_report_{int(time.time())}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate human-readable summary
        summary_path = f"chatkit_investigation_summary_{int(time.time())}.md"
        
        with open(summary_path, 'w') as f:
            f.write("# ChatKit Unified Voice Interface Investigation Report\n\n")
            f.write(f"**Timestamp:** {self.results['timestamp']}\n")
            f.write(f"**Overall Status:** {self.results['overall_status'].upper()}\n\n")
            
            # Console Errors
            f.write("## Console Errors\n")
            if self.results["console_errors"]:
                for error in self.results["console_errors"][:10]:  # Show first 10
                    f.write(f"- **{error['type'].upper()}:** {error['text']}\n")
                if len(self.results["console_errors"]) > 10:
                    f.write(f"- ... and {len(self.results['console_errors']) - 10} more errors\n")
            else:
                f.write("✅ No console errors detected\n")
            f.write("\n")
            
            # React Hook Violations
            f.write("## React Hook Violations\n")
            if self.results["react_hooks"]["valid"]:
                f.write("✅ No React Hook violations detected\n")
            else:
                f.write("❌ React Hook violations found:\n")
                for violation in self.results["react_hooks"]["violations"]:
                    f.write(f"- {violation['text']}\n")
            f.write("\n")
            
            # API Endpoints
            f.write("## API Endpoints Status\n")
            for endpoint, result in self.results["api_endpoints"].items():
                status_icon = "✅" if result["success"] else "❌"
                f.write(f"{status_icon} **{endpoint}:** {result.get('status', 'Failed')} - {result.get('error', 'OK')}\n")
            f.write("\n")
            
            # WebSocket Tests
            f.write("## WebSocket Connections\n")
            for ws_name, result in self.results["websocket_tests"].items():
                status_icon = "✅" if result["success"] else "❌"
                f.write(f"{status_icon} **{ws_name}:** {result.get('error', 'Connected successfully')}\n")
            f.write("\n")
            
            # Component Loading
            f.write("## Component Loading\n")
            for component, result in self.results["component_loading"].items():
                if component == "overall_success" or component == "error":
                    continue
                status_icon = "✅" if result["found"] else "❌"
                f.write(f"{status_icon} **{component}:** {'Found and visible' if result['found'] and result['visible'] else result.get('error', 'Not found')}\n")
            f.write("\n")
            
            # Screenshots
            f.write("## Screenshots Captured\n")
            for screenshot in self.results["screenshots"]:
                f.write(f"- **{screenshot['name']}:** {screenshot['description']} (`{screenshot['path']}`)\n")
            f.write("\n")
            
            # Recommendations
            f.write("## Recommendations\n")
            if self.results["recommendations"]:
                for i, rec in enumerate(self.results["recommendations"], 1):
                    f.write(f"{i}. {rec}\n")
            else:
                f.write("✅ No critical issues found - system appears healthy\n")
        
        logger.info(f"Investigation report saved to: {report_path}")
        logger.info(f"Human-readable summary saved to: {summary_path}")
        
        return report_path, summary_path

    async def run_investigation(self):
        """Run the complete investigation"""
        try:
            logger.info("Starting ChatKit unified voice interface investigation...")
            
            await self.setup_browser()
            
            # Run all tests
            await self.test_api_endpoints()
            await self.test_frontend_loading()
            await self.test_websocket_connections()
            await self.test_voice_interface_interaction()
            await self.analyze_network_requests()
            
            # Generate final report
            report_path, summary_path = await self.generate_report()
            
            # Print summary to console
            print("\n" + "="*80)
            print("CHATKIT INVESTIGATION SUMMARY")
            print("="*80)
            print(f"Overall Status: {self.results['overall_status'].upper()}")
            print(f"Console Errors: {len(self.results['console_errors'])}")
            print(f"React Hook Valid: {self.results['react_hooks']['valid']}")
            print(f"API Endpoints Working: {len([v for v in self.results['api_endpoints'].values() if v['success']])}/{len(self.results['api_endpoints'])}")
            print(f"WebSocket Connections: {len([v for v in self.results['websocket_tests'].values() if v['success']])}/{len(self.results['websocket_tests'])}")
            
            if self.results["recommendations"]:
                print("\nTop Recommendations:")
                for i, rec in enumerate(self.results["recommendations"][:3], 1):
                    print(f"{i}. {rec}")
            
            print(f"\nDetailed reports saved:")
            print(f"- JSON: {report_path}")
            print(f"- Markdown: {summary_path}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            raise
        finally:
            if self.browser:
                await self.browser.close()

async def main():
    investigation = ChatKitInvestigation()
    await investigation.run_investigation()

if __name__ == "__main__":
    asyncio.run(main())