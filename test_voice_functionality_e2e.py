#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing of Voice Functionality
Tests the complete voice interface integration in the trading dashboard
"""

import asyncio
import json
import time
from pathlib import Path
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceE2ETester:
    def __init__(self):
        self.browser = None
        self.page = None
        self.test_results = {}
        self.screenshots_dir = Path(__file__).parent / "voice_test_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
    async def setup(self):
        """Initialize Playwright and browser"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # Run in visible mode for manual observation
            slow_mo=1000,   # Add delay between actions for observation
            args=['--use-fake-ui-for-media-stream', '--allow-running-insecure-content']
        )
        
        # Create a new page with permissions
        context = await self.browser.new_context(
            permissions=['microphone', 'camera'],
            viewport={'width': 1400, 'height': 900}
        )
        self.page = await context.new_page()
        
        # Enable console logging
        self.page.on('console', lambda msg: logger.info(f"Console {msg.type}: {msg.text}"))
        self.page.on('pageerror', lambda exc: logger.error(f"Page error: {exc}"))
        
    async def teardown(self):
        """Cleanup resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            
    async def take_screenshot(self, name: str):
        """Take a screenshot and save it"""
        screenshot_path = self.screenshots_dir / f"{name}_{int(time.time())}.png"
        await self.page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
        
    async def test_initial_load(self):
        """Test 1: Navigate to application and verify initial state"""
        logger.info("🧪 Test 1: Initial Application Load")
        
        try:
            # Navigate to the application
            await self.page.goto('http://localhost:5174/', wait_until='networkidle', timeout=30000)
            await asyncio.sleep(2)  # Wait for initial data load
            
            # Take initial screenshot
            await self.take_screenshot("01_initial_load")
            
            # Check if page loaded successfully
            title = await self.page.title()
            logger.info(f"Page title: {title}")
            
            # Verify main components are present
            results = {
                'page_loaded': True,
                'title': title,
                'url': self.page.url
            }
            
            # Check for key elements
            elements_to_check = [
                ('header', 'h1, .header, .title'),
                ('market_insights', '[data-testid="market-insights"], .market-insights, .watchlist'),
                ('chart_container', '[data-testid="chart-container"], .chart-container, .trading-chart'),
                ('chat_interface', '[data-testid="chat-interface"], .chat-interface, .voice-interface'),
            ]
            
            for element_name, selector in elements_to_check:
                try:
                    element = await self.page.wait_for_selector(selector, timeout=5000)
                    results[f'{element_name}_present'] = element is not None
                    if element:
                        is_visible = await element.is_visible()
                        results[f'{element_name}_visible'] = is_visible
                        logger.info(f"✅ {element_name}: Found and {'visible' if is_visible else 'hidden'}")
                    else:
                        results[f'{element_name}_visible'] = False
                        logger.warning(f"⚠️ {element_name}: Not found")
                except Exception as e:
                    results[f'{element_name}_present'] = False
                    results[f'{element_name}_visible'] = False
                    logger.warning(f"⚠️ {element_name}: {str(e)}")
            
            self.test_results['initial_load'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ Initial load test failed: {str(e)}")
            self.test_results['initial_load'] = {'error': str(e), 'success': False}
            return {'error': str(e), 'success': False}
    
    async def test_voice_interface_visibility(self):
        """Test 2: Check if voice interface components are visible and functional"""
        logger.info("🧪 Test 2: Voice Interface Visibility")
        
        try:
            results = {}
            
            # Look for voice-related elements with multiple selectors
            voice_selectors = [
                # ChatKit interface
                '[data-testid="chatkit-interface"]',
                '.chatkit-interface', 
                '.realtime-chat',
                '.voice-chat',
                
                # Voice button selectors
                '[data-testid="voice-button"]',
                '.voice-button',
                '.mic-button', 
                'button[aria-label*="voice"]',
                'button[aria-label*="microphone"]',
                'button[title*="voice"]',
                'button[title*="mic"]',
                
                # Voice interface containers
                '.voice-interface',
                '.voice-container',
                '.chat-container',
                '.realtime-interface',
                
                # Generic chat interfaces
                '.chat-interface',
                '.chat-panel',
                '.conversation-panel'
            ]
            
            found_elements = []
            for selector in voice_selectors:
                try:
                    elements = await self.page.query_selector_all(selector)
                    if elements:
                        for element in elements:
                            is_visible = await element.is_visible()
                            text_content = await element.text_content()
                            tag_name = await element.evaluate('el => el.tagName')
                            class_name = await element.get_attribute('class')
                            
                            found_elements.append({
                                'selector': selector,
                                'visible': is_visible,
                                'text': text_content[:100] if text_content else '',
                                'tag': tag_name,
                                'class': class_name
                            })
                            logger.info(f"Found element: {selector} - {tag_name} - Visible: {is_visible}")
                except:
                    continue
            
            results['voice_elements_found'] = found_elements
            results['voice_elements_count'] = len(found_elements)
            
            await self.take_screenshot("02_voice_interface_search")
            
            self.test_results['voice_interface_visibility'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ Voice interface visibility test failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['voice_interface_visibility'] = results
            return results
    
    async def test_chatkit_integration(self):
        """Test 3: Test ChatKit integration and session creation"""
        logger.info("🧪 Test 3: ChatKit Integration")
        
        try:
            results = {}
            
            # Check for network requests to ChatKit endpoints
            chatkit_requests = []
            
            def handle_response(response):
                if '/api/chatkit/' in response.url:
                    chatkit_requests.append({
                        'url': response.url,
                        'status': response.status,
                        'method': response.request.method
                    })
                    logger.info(f"ChatKit request: {response.request.method} {response.url} -> {response.status}")
            
            self.page.on('response', handle_response)
            
            # Wait for any automatic ChatKit initialization
            await asyncio.sleep(3)
            
            # Try to trigger ChatKit session creation by looking for buttons/interfaces
            chatkit_triggers = [
                'button:has-text("Start")',
                'button:has-text("Voice")', 
                'button:has-text("Chat")',
                '[data-testid="start-chat"]',
                '[data-testid="voice-button"]',
                '.voice-button',
                '.start-chat',
                '.chat-start'
            ]
            
            for trigger_selector in chatkit_triggers:
                try:
                    trigger = await self.page.query_selector(trigger_selector)
                    if trigger:
                        is_visible = await trigger.is_visible()
                        is_enabled = await trigger.is_enabled()
                        logger.info(f"Found trigger: {trigger_selector} - Visible: {is_visible}, Enabled: {is_enabled}")
                        
                        if is_visible and is_enabled:
                            logger.info(f"Clicking trigger: {trigger_selector}")
                            await trigger.click()
                            await asyncio.sleep(2)  # Wait for response
                            break
                except:
                    continue
            
            results['chatkit_requests'] = chatkit_requests
            results['chatkit_request_count'] = len(chatkit_requests)
            
            await self.take_screenshot("03_chatkit_integration")
            
            self.test_results['chatkit_integration'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ ChatKit integration test failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['chatkit_integration'] = results
            return results
    
    async def test_openai_realtime_integration(self):
        """Test 4: Test OpenAI Realtime integration"""
        logger.info("🧪 Test 4: OpenAI Realtime Integration")
        
        try:
            results = {}
            
            # Monitor for OpenAI Realtime API calls
            realtime_requests = []
            websocket_connections = []
            
            def handle_response(response):
                if '/openai/realtime/' in response.url or '/realtime-relay/' in response.url:
                    realtime_requests.append({
                        'url': response.url,
                        'status': response.status,
                        'method': response.request.method
                    })
                    logger.info(f"Realtime request: {response.request.method} {response.url} -> {response.status}")
            
            def handle_websocket(websocket):
                websocket_connections.append({
                    'url': websocket.url,
                    'timestamp': time.time()
                })
                logger.info(f"WebSocket connection: {websocket.url}")
            
            self.page.on('response', handle_response)
            self.page.on('websocket', handle_websocket)
            
            # Look for voice activation elements
            voice_triggers = [
                'button[aria-label*="microphone"]',
                'button[title*="voice"]',
                '.mic-button',
                '.voice-start',
                '[data-testid="mic-button"]'
            ]
            
            voice_button_found = False
            for trigger_selector in voice_triggers:
                try:
                    trigger = await self.page.query_selector(trigger_selector)
                    if trigger:
                        is_visible = await trigger.is_visible()
                        is_enabled = await trigger.is_enabled()
                        logger.info(f"Found voice trigger: {trigger_selector} - Visible: {is_visible}, Enabled: {is_enabled}")
                        voice_button_found = True
                        
                        if is_visible and is_enabled:
                            logger.info(f"Attempting to click voice trigger: {trigger_selector}")
                            await trigger.click()
                            await asyncio.sleep(3)  # Wait for WebSocket connection
                            break
                except Exception as trigger_error:
                    logger.warning(f"Error with trigger {trigger_selector}: {trigger_error}")
                    continue
            
            results['voice_button_found'] = voice_button_found
            results['realtime_requests'] = realtime_requests
            results['websocket_connections'] = websocket_connections
            results['realtime_request_count'] = len(realtime_requests)
            results['websocket_count'] = len(websocket_connections)
            
            await self.take_screenshot("04_openai_realtime")
            
            self.test_results['openai_realtime_integration'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ OpenAI Realtime integration test failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['openai_realtime_integration'] = results
            return results
    
    async def test_console_errors(self):
        """Test 5: Check for JavaScript console errors"""
        logger.info("🧪 Test 5: Console Error Analysis")
        
        try:
            results = {}
            console_messages = []
            
            def handle_console(msg):
                message_data = {
                    'type': msg.type,
                    'text': msg.text,
                    'timestamp': time.time()
                }
                console_messages.append(message_data)
                
                if msg.type in ['error', 'warning']:
                    logger.warning(f"Console {msg.type}: {msg.text}")
                else:
                    logger.info(f"Console {msg.type}: {msg.text}")
            
            # Clear previous handlers and add new one
            self.page.remove_all_listeners('console')
            self.page.on('console', handle_console)
            
            # Reload page to capture all console messages
            await self.page.reload(wait_until='networkidle')
            await asyncio.sleep(5)  # Wait for all async operations
            
            # Categorize messages
            errors = [msg for msg in console_messages if msg['type'] == 'error']
            warnings = [msg for msg in console_messages if msg['type'] == 'warning']
            logs = [msg for msg in console_messages if msg['type'] in ['log', 'info']]
            
            results['total_messages'] = len(console_messages)
            results['errors'] = errors
            results['warnings'] = warnings
            results['logs'] = logs
            results['error_count'] = len(errors)
            results['warning_count'] = len(warnings)
            
            await self.take_screenshot("05_console_analysis")
            
            self.test_results['console_errors'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ Console error analysis failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['console_errors'] = results
            return results
    
    async def test_api_health_checks(self):
        """Test 6: Verify backend API is responding correctly"""
        logger.info("🧪 Test 6: API Health Checks")
        
        try:
            results = {}
            
            # Test key API endpoints
            api_endpoints = [
                'http://localhost:8000/health',
                'http://localhost:8000/api/stock-price?symbol=TSLA',
                'http://localhost:8000/api/chart/commands'
            ]
            
            for endpoint in api_endpoints:
                try:
                    response = await self.page.evaluate(f"""
                        fetch('{endpoint}')
                        .then(res => res.ok ? res.json() : Promise.reject(res.status))
                        .catch(err => Promise.reject(err))
                    """)
                    results[endpoint] = {'status': 'success', 'data': response}
                    logger.info(f"✅ API endpoint working: {endpoint}")
                except Exception as api_error:
                    results[endpoint] = {'status': 'error', 'error': str(api_error)}
                    logger.error(f"❌ API endpoint failed: {endpoint} - {api_error}")
            
            await self.take_screenshot("06_api_health")
            
            self.test_results['api_health_checks'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ API health check failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['api_health_checks'] = results
            return results
    
    async def test_voice_workflow_simulation(self):
        """Test 7: Simulate complete voice workflow"""
        logger.info("🧪 Test 7: Voice Workflow Simulation")
        
        try:
            results = {}
            
            # Look for the complete voice interface
            await asyncio.sleep(2)
            
            # Try to find any interface that might handle voice
            interface_elements = await self.page.query_selector_all('.voice-interface, .chat-interface, .realtime-chat, [data-testid*="voice"], [data-testid*="chat"]')
            
            results['interface_elements_found'] = len(interface_elements)
            
            if interface_elements:
                logger.info(f"Found {len(interface_elements)} potential voice interface elements")
                
                for i, element in enumerate(interface_elements):
                    try:
                        tag_name = await element.evaluate('el => el.tagName')
                        class_name = await element.get_attribute('class') or ''
                        is_visible = await element.is_visible()
                        text_content = (await element.text_content() or '')[:200]
                        
                        logger.info(f"Interface element {i+1}: {tag_name}.{class_name} - Visible: {is_visible}")
                        logger.info(f"  Content: {text_content}")
                        
                    except Exception as elem_error:
                        logger.warning(f"Error analyzing element {i+1}: {elem_error}")
            
            # Check if there are any buttons that might start voice
            voice_buttons = await self.page.query_selector_all('button, .button, [role="button"]')
            potential_voice_buttons = []
            
            for button in voice_buttons:
                try:
                    text = (await button.text_content() or '').lower()
                    aria_label = (await button.get_attribute('aria-label') or '').lower()
                    title = (await button.get_attribute('title') or '').lower()
                    class_name = (await button.get_attribute('class') or '').lower()
                    
                    voice_keywords = ['voice', 'mic', 'microphone', 'speak', 'talk', 'chat', 'start']
                    
                    if any(keyword in text or keyword in aria_label or keyword in title or keyword in class_name 
                           for keyword in voice_keywords):
                        is_visible = await button.is_visible()
                        is_enabled = await button.is_enabled()
                        
                        potential_voice_buttons.append({
                            'text': text,
                            'aria_label': aria_label,
                            'title': title,
                            'class': class_name,
                            'visible': is_visible,
                            'enabled': is_enabled
                        })
                        
                        logger.info(f"Potential voice button: '{text}' - Visible: {is_visible}, Enabled: {is_enabled}")
                        
                except Exception as btn_error:
                    continue
            
            results['potential_voice_buttons'] = potential_voice_buttons
            results['voice_buttons_found'] = len(potential_voice_buttons)
            
            await self.take_screenshot("07_voice_workflow_simulation")
            
            self.test_results['voice_workflow_simulation'] = results
            return results
            
        except Exception as e:
            logger.error(f"❌ Voice workflow simulation failed: {str(e)}")
            results = {'error': str(e), 'success': False}
            self.test_results['voice_workflow_simulation'] = results
            return results
    
    async def run_comprehensive_test(self):
        """Run all tests in sequence"""
        logger.info("🚀 Starting Comprehensive Voice E2E Testing")
        
        await self.setup()
        
        try:
            # Run all tests
            test_functions = [
                self.test_initial_load,
                self.test_voice_interface_visibility,
                self.test_chatkit_integration,
                self.test_openai_realtime_integration,
                self.test_console_errors,
                self.test_api_health_checks,
                self.test_voice_workflow_simulation
            ]
            
            for test_func in test_functions:
                try:
                    await test_func()
                    await asyncio.sleep(1)  # Brief pause between tests
                except Exception as test_error:
                    logger.error(f"Test {test_func.__name__} failed: {test_error}")
                    continue
            
            # Generate final comprehensive screenshot
            await self.take_screenshot("99_final_state")
            
        finally:
            await self.teardown()
        
        return self.test_results
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        report = {
            'timestamp': time.time(),
            'test_results': self.test_results,
            'summary': self.analyze_results()
        }
        
        # Save report to file
        report_file = Path(__file__).parent / f"voice_e2e_test_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Test report saved: {report_file}")
        return report
    
    def analyze_results(self):
        """Analyze test results and provide summary"""
        summary = {
            'total_tests': len(self.test_results),
            'successful_tests': 0,
            'failed_tests': 0,
            'critical_issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        for test_name, results in self.test_results.items():
            if isinstance(results, dict) and 'error' not in results:
                summary['successful_tests'] += 1
            else:
                summary['failed_tests'] += 1
                summary['critical_issues'].append(f"{test_name}: {results.get('error', 'Unknown error')}")
        
        # Analyze specific issues
        if 'console_errors' in self.test_results:
            error_count = self.test_results['console_errors'].get('error_count', 0)
            if error_count > 0:
                summary['warnings'].append(f"{error_count} JavaScript console errors detected")
        
        if 'voice_interface_visibility' in self.test_results:
            voice_elements = self.test_results['voice_interface_visibility'].get('voice_elements_count', 0)
            if voice_elements == 0:
                summary['critical_issues'].append("No voice interface elements found")
                summary['recommendations'].append("Verify ChatKit integration is properly implemented")
        
        if 'chatkit_integration' in self.test_results:
            chatkit_requests = self.test_results['chatkit_integration'].get('chatkit_request_count', 0)
            if chatkit_requests == 0:
                summary['warnings'].append("No ChatKit API requests detected")
                summary['recommendations'].append("Check ChatKit session initialization")
        
        return summary

async def main():
    """Main test execution"""
    tester = VoiceE2ETester()
    
    logger.info("=" * 80)
    logger.info("🎤 VOICE FUNCTIONALITY END-TO-END TESTING")
    logger.info("=" * 80)
    
    try:
        # Run comprehensive testing
        results = await tester.run_comprehensive_test()
        
        # Generate and display report
        report = tester.generate_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        summary = report['summary']
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Successful: {summary['successful_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        
        if summary['critical_issues']:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in summary['critical_issues']:
                print(f"  ❌ {issue}")
        
        if summary['warnings']:
            print("\n⚠️ WARNINGS:")
            for warning in summary['warnings']:
                print(f"  ⚠️ {warning}")
        
        if summary['recommendations']:
            print("\n💡 RECOMMENDATIONS:")
            for rec in summary['recommendations']:
                print(f"  💡 {rec}")
        
        print("\n✅ Testing completed. Check screenshots in: voice_test_screenshots/")
        print(f"📄 Full report saved as JSON file")
        
    except Exception as e:
        logger.error(f"Testing failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())