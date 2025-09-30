#!/usr/bin/env python3
"""
Comprehensive Educational Query Testing using Comet Browser
Tests novice trader experience with Comet's AI agent assistance
"""

import asyncio
from playwright.async_api import async_playwright, ConsoleMessage, Error
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class CometEducationalTester:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.console_logs = []
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "browser": "Comet",
            "educational_tests": [],
            "chart_tests": [],
            "journey_tests": [],
            "errors": [],
            "console_logs": [],
            "summary": {}
        }
        
    async def setup_comet_browser(self):
        """Setup Comet browser using Playwright"""
        print("🚀 Setting up Comet browser...")
        self.playwright = await async_playwright().start()
        
        # Try to launch Comet browser with its executable path
        try:
            # First try using Comet directly
            self.browser = await self.playwright.chromium.launch(
                executable_path="/Applications/Comet.app/Contents/MacOS/Comet",
                headless=False,  # Must be visible for Comet agent
                args=[
                    '--enable-automation',
                    '--disable-web-security',
                    '--allow-running-insecure-content',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            print("✅ Comet browser launched successfully")
        except Exception as e:
            print(f"⚠️ Could not launch Comet directly: {e}")
            print("Falling back to standard Chromium...")
            # Fallback to regular Chromium
            self.browser = await self.playwright.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            self.test_results["browser"] = "Chromium (Comet unavailable)"
        
        self.context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900},
            user_agent='Mozilla/5.0 (Macintosh) EducationalTester/1.0'
        )
        
        self.page = await self.context.new_page()
        
        # Setup monitoring
        await self.setup_monitoring()
        
    async def setup_monitoring(self):
        """Setup event listeners for comprehensive monitoring"""
        # Capture console messages
        async def handle_console(msg: ConsoleMessage):
            entry = {
                "type": msg.type,
                "text": msg.text,
                "timestamp": datetime.now().isoformat()
            }
            self.console_logs.append(entry)
            self.test_results["console_logs"].append(entry)
            
            # Display errors immediately
            if msg.type in ['error', 'warning']:
                print(f"   🔴 Console {msg.type}: {msg.text[:100]}")
                
        self.page.on("console", handle_console)
        
        # Capture page errors
        async def handle_error(error: Error):
            self.test_results["errors"].append({
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            })
            print(f"   🔴 Page Error: {error}")
            
        self.page.on("pageerror", handle_error)
        
    async def ensure_voice_connected(self):
        """Ensure voice assistant is connected"""
        # Check if already connected
        is_connected = await self.page.query_selector('.voice-fab.active')
        if not is_connected:
            print("   🔌 Connecting voice assistant...")
            voice_button = await self.page.query_selector('[data-testid="voice-fab"], .voice-fab')
            if voice_button:
                await voice_button.click()
                try:
                    await self.page.wait_for_selector('.voice-fab.active', timeout=10000)
                    print("   ✅ Voice assistant connected")
                    await self.page.wait_for_timeout(1000)
                    return True
                except:
                    print("   ❌ Failed to connect voice assistant")
                    return False
        return True
        
    async def clear_console_logs(self):
        """Clear console logs for fresh test"""
        self.console_logs = []
        
    async def get_response_text(self) -> Optional[str]:
        """Get the latest response text from the assistant"""
        try:
            # Look for response messages
            messages = await self.page.query_selector_all('.conversation-message-enhanced')
            if messages and len(messages) > 0:
                # Get the last assistant message
                for msg in reversed(messages):
                    text = await msg.text_content()
                    if text and "🤖" in text:  # Assistant message
                        return text.replace("🤖", "").strip()
        except:
            pass
        return None
        
    async def detect_chart_commands(self) -> List[str]:
        """Detect any chart commands that were executed"""
        # This would look for chart updates or commands in console
        chart_commands = []
        for log in self.console_logs:
            if "LOAD:" in log.get("text", "") or "CHART:" in log.get("text", ""):
                chart_commands.append(log["text"])
        return chart_commands
        
    async def test_single_query(self, query: str, expected_type: str, should_succeed: bool) -> Dict[str, Any]:
        """Test a single query and capture all results"""
        print(f"\n📝 Testing: '{query}'")
        
        # Ensure voice is connected
        if not await self.ensure_voice_connected():
            return {
                "query": query,
                "status": "failed",
                "error": "Could not connect voice assistant"
            }
        
        # Clear previous console logs
        await self.clear_console_logs()
        
        # Find and use input field
        input_field = await self.page.query_selector('.voice-text-input')
        if not input_field:
            print("   ❌ Input field not found")
            return {
                "query": query,
                "status": "failed",
                "error": "Input field not found"
            }
            
        # Check if input is enabled
        is_disabled = await input_field.evaluate('el => el.disabled')
        if is_disabled:
            print("   ❌ Input field is disabled")
            return {
                "query": query,
                "status": "failed",
                "error": "Input field disabled"
            }
            
        # Type and send query
        await input_field.click()
        await self.page.keyboard.press("Control+A")
        await self.page.keyboard.press("Delete")
        await input_field.type(query)
        await self.page.keyboard.press("Enter")
        
        print("   ⏳ Waiting for response...")
        # Wait for response
        await self.page.wait_for_timeout(5000)
        
        # Capture results
        response_text = await self.get_response_text()
        chart_commands = await self.detect_chart_commands()
        
        # Take screenshot for evidence
        screenshot_name = f"comet_test_{expected_type}_{datetime.now().strftime('%H%M%S')}.png"
        await self.page.screenshot(path=screenshot_name)
        
        result = {
            "query": query,
            "expected_type": expected_type,
            "timestamp": datetime.now().isoformat(),
            "response_received": bool(response_text),
            "response_text": response_text[:500] if response_text else None,
            "chart_commands": chart_commands,
            "console_errors": [log for log in self.console_logs if log.get("type") == "error"],
            "screenshot": screenshot_name,
            "status": "success" if response_text and should_succeed else "failed"
        }
        
        # Print summary
        status_icon = "✅" if result["status"] == "success" else "❌"
        print(f"   {status_icon} Status: {result['status']}")
        if response_text:
            print(f"   📄 Response: {response_text[:100]}...")
        if chart_commands:
            print(f"   📊 Chart commands: {chart_commands}")
        if result["console_errors"]:
            print(f"   ⚠️ Console errors: {len(result['console_errors'])}")
            
        return result
        
    async def test_educational_queries(self):
        """Test all educational queries"""
        print("\n" + "="*60)
        print("📚 TESTING EDUCATIONAL QUERIES")
        print("="*60)
        
        educational_queries = [
            # Basic concepts
            ("What does buy low mean?", "educational", True),
            ("What is a stop loss?", "educational", True),
            ("Explain support and resistance", "educational", True),
            ("What is the difference between support and resistance levels?", "educational", True),
            
            # Getting started
            ("How do I start trading stocks?", "educational", True),
            ("How much money do I need to start trading?", "educational", True),
            ("What is paper trading?", "educational", True),
            
            # Order types
            ("What is a market order?", "educational", True),
            ("What is a limit order?", "educational", True),
            ("Explain stop loss orders", "educational", True),
            
            # Market concepts
            ("What is a bull market?", "educational", True),
            ("What is a bear market?", "educational", True),
        ]
        
        for query, expected_type, should_succeed in educational_queries:
            result = await self.test_single_query(query, expected_type, should_succeed)
            self.test_results["educational_tests"].append(result)
            await self.page.wait_for_timeout(1000)  # Brief pause between queries
            
    async def test_chart_commands(self):
        """Test chart commands with company names"""
        print("\n" + "="*60)
        print("📊 TESTING CHART COMMANDS")
        print("="*60)
        
        chart_queries = [
            ("Show me the chart for Apple", "chart", True),
            ("Display Microsoft stock", "chart", True),
            ("Load Tesla chart", "chart", True),
            ("Show me chart for Amazon", "chart", True),
            ("View Netflix chart", "chart", True),
        ]
        
        for query, expected_type, should_succeed in chart_queries:
            result = await self.test_single_query(query, expected_type, should_succeed)
            self.test_results["chart_tests"].append(result)
            await self.page.wait_for_timeout(1000)
            
    async def test_novice_journey(self):
        """Test complete novice trader journey"""
        print("\n" + "="*60)
        print("🚀 TESTING NOVICE TRADER JOURNEY")
        print("="*60)
        
        journey_steps = [
            ("Hello, I'm new to trading", "greeting", True),
            ("How do I start trading stocks?", "educational", True),
            ("What does buy low sell high mean?", "educational", True),
            ("Show me Apple stock", "chart", True),
            ("What are those green and red candles?", "educational", True),
            ("What is support and resistance?", "educational", True),
            ("How do I know when to buy?", "educational", True),
            ("What is a stop loss?", "educational", True),
            ("Is AAPL a good buy right now?", "analysis", True),
            ("What are the risks?", "educational", True),
        ]
        
        for query, expected_type, should_succeed in journey_steps:
            result = await self.test_single_query(query, expected_type, should_succeed)
            self.test_results["journey_tests"].append(result)
            await self.page.wait_for_timeout(2000)  # Longer pause for context
            
    def generate_summary(self):
        """Generate test summary statistics"""
        educational_success = sum(1 for t in self.test_results["educational_tests"] if t["status"] == "success")
        educational_total = len(self.test_results["educational_tests"])
        
        chart_success = sum(1 for t in self.test_results["chart_tests"] if t["status"] == "success")
        chart_total = len(self.test_results["chart_tests"])
        
        journey_success = sum(1 for t in self.test_results["journey_tests"] if t["status"] == "success")
        journey_total = len(self.test_results["journey_tests"])
        
        console_errors = len(self.test_results["errors"])
        
        self.test_results["summary"] = {
            "educational": f"{educational_success}/{educational_total} passed",
            "chart_commands": f"{chart_success}/{chart_total} passed",
            "journey": f"{journey_success}/{journey_total} passed",
            "console_errors": console_errors,
            "total_success_rate": f"{(educational_success + chart_success + journey_success) / (educational_total + chart_total + journey_total) * 100:.1f}%"
        }
        
    async def generate_report(self):
        """Generate and save test report"""
        self.generate_summary()
        
        print("\n" + "="*60)
        print("📊 TEST REPORT")
        print("="*60)
        
        summary = self.test_results["summary"]
        print(f"\n📚 Educational Queries: {summary['educational']}")
        print(f"📊 Chart Commands: {summary['chart_commands']}")
        print(f"🚀 Journey Tests: {summary['journey']}")
        print(f"⚠️ Console Errors: {summary['console_errors']}")
        print(f"\n✨ Overall Success Rate: {summary['total_success_rate']}")
        
        # Save detailed report
        report_file = f"comet_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Print failed queries for quick reference
        all_tests = (self.test_results["educational_tests"] + 
                    self.test_results["chart_tests"] + 
                    self.test_results["journey_tests"])
        failed_tests = [t for t in all_tests if t["status"] == "failed"]
        
        if failed_tests:
            print("\n❌ Failed Queries:")
            for test in failed_tests:
                print(f"  - {test['query']}: {test.get('error', 'No response')}")
        else:
            print("\n✅ All tests passed!")
            
    async def cleanup(self):
        """Cleanup browser resources"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def run_comprehensive_test(self, mode="all"):
        """Run all tests or specific mode"""
        try:
            # Setup
            await self.setup_comet_browser()
            
            # Navigate to app
            print("🌐 Navigating to application...")
            await self.page.goto("http://localhost:5174", wait_until='networkidle')
            await self.page.wait_for_timeout(3000)
            
            # Take initial screenshot
            await self.page.screenshot(path="comet_test_initial.png")
            print("📸 Initial screenshot captured")
            
            # Run tests based on mode
            if mode == "all" or mode == "educational":
                await self.test_educational_queries()
            
            if mode == "all" or mode == "chart":
                await self.test_chart_commands()
                
            if mode == "all" or mode == "journey":
                await self.test_novice_journey()
            
            # Generate report
            await self.generate_report()
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            self.test_results["errors"].append({
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        finally:
            await self.cleanup()

async def main():
    """Main entry point"""
    import sys
    
    mode = "all"
    if len(sys.argv) > 1:
        if "--mode" in sys.argv:
            mode_index = sys.argv.index("--mode") + 1
            if mode_index < len(sys.argv):
                mode = sys.argv[mode_index]
    
    print("🧪 Comprehensive Educational Testing with Comet Browser")
    print(f"Mode: {mode}")
    print("-" * 60)
    
    tester = CometEducationalTester()
    await tester.run_comprehensive_test(mode)

if __name__ == "__main__":
    asyncio.run(main())