#!/usr/bin/env python3
"""
Final Chart Command Processing Test
Specifically tests the 9+ pending commands and useChartCommandProcessor hook
"""

import asyncio
import aiohttp
import json
import time
from playwright.async_api import async_playwright
from datetime import datetime

class ChartCommandProcessingTester:
    def __init__(self):
        self.localhost_url = "http://localhost:5174"
        self.backend_url = "http://localhost:8000"
        self.results = {}
    
    async def test_command_queue_and_processing(self):
        """Test the command queue and frontend processing"""
        print("🔄 Testing Command Queue and Frontend Processing...")
        
        # First, check the current command queue
        async with aiohttp.ClientSession() as session:
            # Get current commands
            async with session.get(f"{self.backend_url}/api/chart/commands") as resp:
                if resp.status == 200:
                    current_commands = await resp.json()
                    print(f"Current commands in queue: {len(current_commands)}")
                    
                    # Add several test commands to simulate the 9+ scenario
                    test_commands = [
                        {"action": "change_symbol", "symbol": "AAPL", "source": "test_1"},
                        {"action": "change_symbol", "symbol": "GOOGL", "source": "test_2"},
                        {"action": "change_symbol", "symbol": "MSFT", "source": "test_3"},
                        {"action": "set_timeframe", "timeframe": "1D", "source": "test_4"},
                        {"action": "change_symbol", "symbol": "TSLA", "source": "test_5"},
                    ]
                    
                    # Add commands one by one
                    added_commands = []
                    for i, cmd in enumerate(test_commands):
                        cmd["timestamp"] = time.time()
                        async with session.post(f"{self.backend_url}/api/chart/commands", json=cmd) as add_resp:
                            if add_resp.status == 200:
                                result = await add_resp.json()
                                added_commands.append(cmd)
                                print(f"✅ Added test command {i+1}: {cmd['action']} - {cmd.get('symbol', cmd.get('timeframe'))}")
                            else:
                                print(f"❌ Failed to add command {i+1}: {add_resp.status}")
                    
                    # Get updated queue
                    async with session.get(f"{self.backend_url}/api/chart/commands") as resp:
                        if resp.status == 200:
                            updated_commands = await resp.json()
                            print(f"Updated commands in queue: {len(updated_commands)}")
                            
                            self.results["command_queue"] = {
                                "initial_count": len(current_commands),
                                "commands_added": len(added_commands),
                                "final_count": len(updated_commands),
                                "recent_commands": updated_commands[-5:] if updated_commands else [],
                                "queue_working": len(updated_commands) > len(current_commands)
                            }
        
        return len(updated_commands) if 'updated_commands' in locals() else 0
    
    async def test_frontend_command_processor(self, page, expected_commands):
        """Test the useChartCommandProcessor hook with real commands"""
        print("📊 Testing Frontend Command Processor Hook...")
        
        # Navigate to the Chart Control tab
        await page.goto(self.localhost_url)
        await page.wait_for_load_state('networkidle')
        
        # Click Chart Control tab
        chart_control_tab = await page.query_selector('text=Chart Control')
        if chart_control_tab:
            await chart_control_tab.click()
            await page.wait_for_timeout(2000)
        
        # Set up comprehensive monitoring
        console_logs = []
        network_requests = []
        errors = []
        
        def handle_console(msg):
            text = msg.text
            console_logs.append({
                "timestamp": time.time(),
                "text": text,
                "type": msg.type
            })
            
            # Look for specific chart command processor messages
            keywords = [
                "useChartCommandProcessor",
                "Chart Command Processor",
                "processing command",
                "polling for commands",
                "commands fetched",
                "executing command",
                "chart symbol changed",
                "TSLA", "AAPL", "GOOGL", "MSFT"  # Our test symbols
            ]
            
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    print(f"  📝 Console: {text[:100]}...")
                    break
        
        def handle_request(request):
            if "/api/chart/commands" in request.url:
                network_requests.append({
                    "timestamp": time.time(),
                    "url": request.url,
                    "method": request.method
                })
                print(f"  🌐 API Request: {request.method} {request.url}")
        
        def handle_page_error(error):
            errors.append({
                "timestamp": time.time(),
                "message": str(error)
            })
            print(f"  ❌ Page Error: {error}")
        
        page.on("console", handle_console)
        page.on("request", handle_request)
        page.on("pageerror", handle_page_error)
        
        # Wait and observe the polling behavior
        print(f"  Waiting 15 seconds to observe command processing of {expected_commands} commands...")
        
        # Check initial state
        initial_requests = len(network_requests)
        
        # Wait for polling activity
        await page.wait_for_timeout(15000)
        
        # Check final state
        final_requests = len(network_requests)
        polling_active = final_requests > initial_requests
        
        # Try to detect React hook activity by checking DOM changes
        dom_changes = await page.evaluate("""
            () => {
                // Look for any elements that might indicate chart updates
                const elements = {
                    chartCanvas: document.querySelectorAll('canvas').length,
                    tradingChart: document.querySelector('.trading-chart-container') !== null,
                    chartAgent: document.querySelector('.chart-agent-chat') !== null,
                    mainChart: document.querySelector('.main-chart') !== null
                };
                
                // Check if any chart-related elements have recent updates
                const chartContainer = document.querySelector('.trading-chart-container');
                
                return {
                    elements: elements,
                    chartContainerExists: !!chartContainer,
                    canvasCount: document.querySelectorAll('canvas').length,
                    timestamp: Date.now()
                };
            }
        """)
        
        self.results["frontend_processing"] = {
            "console_logs": len(console_logs),
            "relevant_console_logs": len([log for log in console_logs if any(kw.lower() in log["text"].lower() for kw in ["chart", "command", "processor", "polling"])]),
            "network_requests": len(network_requests),
            "polling_detected": polling_active,
            "polling_frequency": (final_requests - initial_requests) / 15 if polling_active else 0,  # requests per second
            "dom_elements": dom_changes,
            "errors": len(errors),
            "hook_active": len(network_requests) > 0 and len(console_logs) > 0,
            "status": "completed"
        }
        
        print(f"  📊 Results:")
        print(f"    Console logs: {len(console_logs)} (relevant: {self.results['frontend_processing']['relevant_console_logs']})")
        print(f"    Network requests: {len(network_requests)}")
        print(f"    Polling detected: {'✅' if polling_active else '❌'}")
        print(f"    Hook appears active: {'✅' if self.results['frontend_processing']['hook_active'] else '❌'}")
        
        return self.results["frontend_processing"]
    
    async def test_end_to_end_command_flow(self, page):
        """Test complete command flow: API → Queue → Frontend → Processing"""
        print("🔗 Testing End-to-End Command Flow...")
        
        # Add a specific test command with unique identifier
        unique_symbol = f"SPY-{int(time.time() % 1000)}"
        test_command = {
            "action": "change_symbol",
            "symbol": "SPY",  # Use real symbol
            "timestamp": time.time(),
            "source": f"e2e_test_{int(time.time())}"
        }
        
        # Monitor network activity
        command_requests = []
        def handle_command_request(request):
            if "/api/chart/commands" in request.url:
                command_requests.append({
                    "timestamp": time.time(),
                    "method": request.method,
                    "url": request.url
                })
        
        page.on("request", handle_command_request)
        
        # Step 1: Add command via API
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.backend_url}/api/chart/commands", json=test_command) as resp:
                command_added = resp.status == 200
                if command_added:
                    print(f"  ✅ Command added via API: {test_command['source']}")
                else:
                    print(f"  ❌ Failed to add command: {resp.status}")
        
        # Step 2: Wait for frontend to poll and process
        initial_requests = len(command_requests)
        await page.wait_for_timeout(10000)  # Wait 10 seconds for polling
        final_requests = len(command_requests)
        
        # Step 3: Check if command was processed (removed from queue)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.backend_url}/api/chart/commands") as resp:
                if resp.status == 200:
                    remaining_commands = await resp.json()
                    our_command_still_there = any(
                        cmd.get("source") == test_command["source"] 
                        for cmd in remaining_commands
                    )
                    
        self.results["e2e_flow"] = {
            "command_added": command_added,
            "frontend_requests": final_requests - initial_requests,
            "command_processed": command_added and not our_command_still_there,
            "integration_working": all([
                command_added,
                final_requests > initial_requests,  # Frontend polling
                not our_command_still_there  # Command processed
            ]),
            "test_command": test_command,
            "remaining_commands": len(remaining_commands) if 'remaining_commands' in locals() else 0,
            "status": "completed"
        }
        
        print(f"  📊 E2E Results:")
        print(f"    Command added: {'✅' if command_added else '❌'}")
        print(f"    Frontend polling: {'✅' if final_requests > initial_requests else '❌'}")
        print(f"    Command processed: {'✅' if self.results['e2e_flow']['command_processed'] else '❌'}")
        print(f"    Integration working: {'✅' if self.results['e2e_flow']['integration_working'] else '❌'}")
        
        return self.results["e2e_flow"]
    
    async def run_complete_test(self):
        """Run complete chart command processing test"""
        print("🚀 Starting Complete Chart Command Processing Test")
        print(f"Frontend: {self.localhost_url}")
        print(f"Backend: {self.backend_url}")
        print("=" * 60)
        
        try:
            # Step 1: Prepare command queue
            expected_commands = await self.test_command_queue_and_processing()
            
            # Step 2: Test frontend with browser
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False, devtools=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # Test frontend command processor
                    await self.test_frontend_command_processor(page, expected_commands)
                    
                    # Test end-to-end flow
                    await self.test_end_to_end_command_flow(page)
                    
                    self.generate_final_summary()
                    
                except Exception as e:
                    print(f"❌ Browser tests failed: {e}")
                    self.results["browser_error"] = str(e)
                
                finally:
                    await browser.close()
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            self.results["suite_error"] = str(e)
        
        return self.results
    
    def generate_final_summary(self):
        """Generate final test summary"""
        print("\n" + "=" * 60)
        print("📋 CHART COMMAND PROCESSING TEST RESULTS")
        print("=" * 60)
        
        # Command Queue Results
        queue = self.results.get("command_queue", {})
        print(f"\n🔄 COMMAND QUEUE:")
        if queue:
            print(f"  • Initial commands: {queue.get('initial_count', 0)}")
            print(f"  • Commands added: {queue.get('commands_added', 0)}")
            print(f"  • Final count: {queue.get('final_count', 0)}")
            print(f"  • Queue functional: {'✅' if queue.get('queue_working') else '❌'}")
        
        # Frontend Processing Results
        frontend = self.results.get("frontend_processing", {})
        print(f"\n📊 FRONTEND PROCESSING:")
        if frontend:
            print(f"  • Console logs: {frontend.get('console_logs', 0)} (relevant: {frontend.get('relevant_console_logs', 0)})")
            print(f"  • Network requests: {frontend.get('network_requests', 0)}")
            print(f"  • Polling active: {'✅' if frontend.get('polling_detected') else '❌'}")
            print(f"  • Polling frequency: {frontend.get('polling_frequency', 0):.2f} req/sec")
            print(f"  • Hook active: {'✅' if frontend.get('hook_active') else '❌'}")
            print(f"  • Canvas elements: {frontend.get('dom_elements', {}).get('canvasCount', 0)}")
        
        # E2E Flow Results
        e2e = self.results.get("e2e_flow", {})
        print(f"\n🔗 END-TO-END FLOW:")
        if e2e:
            print(f"  • Command added via API: {'✅' if e2e.get('command_added') else '❌'}")
            print(f"  • Frontend polling: {'✅' if e2e.get('frontend_requests', 0) > 0 else '❌'}")
            print(f"  • Command processed: {'✅' if e2e.get('command_processed') else '❌'}")
            print(f"  • Full integration: {'✅' if e2e.get('integration_working') else '❌'}")
        
        print(f"\n🏁 TEST COMPLETED: {datetime.now().strftime('%H:%M:%S')}")
        
        # Overall assessment
        all_working = all([
            queue.get('queue_working', False),
            frontend.get('polling_detected', False),
            e2e.get('integration_working', False)
        ])
        
        print(f"\n🎯 OVERALL ASSESSMENT: {'✅ ALL SYSTEMS WORKING' if all_working else '❌ ISSUES DETECTED'}")
        
        # Save results
        with open('chart_command_processing_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Detailed results saved to: chart_command_processing_results.json")

async def main():
    tester = ChartCommandProcessingTester()
    results = await tester.run_complete_test()
    return results

if __name__ == "__main__":
    asyncio.run(main())