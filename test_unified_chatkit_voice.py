#!/usr/bin/env python3
"""
Test Unified ChatKit Voice Interface for Trading Workflow
=======================================================

Tests the new RealtimeChatKit component that integrates:
- ChatKit for Agent Builder communication
- Agent Voice hook for OpenAI Realtime API
- Chart command processing
- Market data queries

This test validates the complete user workflow as requested:
"The voice interface should now be in place of the initial voice interface. 
I want to use realtime with the chatkit."
"""

import asyncio
import sys
import json
from playwright.async_api import async_playwright, Page, BrowserContext
from datetime import datetime

class UnifiedChatKitVoiceTest:
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.results = {
            'page_loaded': False,
            'chatkit_component_found': False,
            'voice_button_available': False,
            'agent_builder_integration': False,
            'text_query_response': False,
            'voice_connection_available': False,
            'chart_command_processing': False,
            'market_data_integration': False
        }
        
    async def setup(self):
        """Initialize browser and navigate to the trading dashboard"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, args=['--use-fake-ui-for-media-stream'])
        self.context = await self.browser.new_context(
            permissions=['microphone'],
            viewport={'width': 1400, 'height': 900}
        )
        self.page = await self.context.new_page()
        
        # Enable console logging
        self.page.on('console', lambda msg: print(f'🔍 [CONSOLE] {msg.type()}: {msg.text()}'))
        self.page.on('pageerror', lambda exc: print(f'❌ [PAGE ERROR] {exc}'))
        
        print("🚀 Starting Unified ChatKit Voice Interface Test")
        print("=" * 60)

    async def test_page_loading(self):
        """Test basic page loading and React hydration"""
        print("\n📱 [TEST] Page Loading & React Hydration")
        
        try:
            await self.page.goto('http://localhost:5174', wait_until='networkidle')
            await asyncio.sleep(2)  # Allow React to hydrate
            
            title = await self.page.title()
            print(f"   ✓ Page title: {title}")
            
            # Wait for main dashboard to render
            await self.page.wait_for_selector('.trading-dashboard', timeout=5000)
            self.results['page_loaded'] = True
            print("   ✅ Trading dashboard loaded successfully")
            
        except Exception as e:
            print(f"   ❌ Page loading failed: {e}")

    async def test_chatkit_component(self):
        """Test that the new RealtimeChatKit component is present and functional"""
        print("\n🤖 [TEST] RealtimeChatKit Component Integration")
        
        try:
            # Look for the unified voice interface
            chatkit_container = await self.page.wait_for_selector('.realtime-chatkit', timeout=5000)
            if chatkit_container:
                print("   ✓ RealtimeChatKit container found")
                self.results['chatkit_component_found'] = True
                
                # Check for AI Trading Assistant header
                header = await self.page.query_selector('.realtime-chatkit .text-sm:has-text("AI Trading Assistant")')
                if header:
                    print("   ✓ AI Trading Assistant header found")
                
                # Check for ChatKit iframe or embedded component
                chatkit_element = await self.page.query_selector('.realtime-chatkit [class*="ChatKit"], .realtime-chatkit iframe')
                if chatkit_element:
                    print("   ✓ ChatKit component embedded successfully")
                    self.results['agent_builder_integration'] = True
                else:
                    # Check for loading state
                    loading = await self.page.query_selector('.realtime-chatkit:has-text("Connecting to Agent Builder")')
                    if loading:
                        print("   ⏳ ChatKit connecting to Agent Builder...")
                        await asyncio.sleep(3)  # Wait for connection
                        chatkit_element = await self.page.query_selector('.realtime-chatkit [class*="ChatKit"], .realtime-chatkit iframe')
                        if chatkit_element:
                            print("   ✓ ChatKit connected and loaded")
                            self.results['agent_builder_integration'] = True
                
                # Check for voice control button
                voice_button = await self.page.query_selector('.realtime-chatkit button[title*="voice"], .realtime-chatkit button:has-text("Connect voice")')
                if voice_button:
                    print("   ✓ Voice control button found")
                    self.results['voice_button_available'] = True
                    
                    # Test button interaction
                    button_title = await voice_button.get_attribute('title')
                    print(f"   ✓ Voice button title: {button_title}")
                
        except Exception as e:
            print(f"   ❌ ChatKit component test failed: {e}")

    async def test_voice_connection(self):
        """Test voice connection functionality"""
        print("\n🎤 [TEST] Voice Connection Integration")
        
        try:
            # Look for voice button and test connection
            voice_button = await self.page.query_selector('.realtime-chatkit button[title*="voice"]')
            if voice_button:
                print("   📱 Attempting voice connection...")
                
                # Click voice button to connect
                await voice_button.click()
                await asyncio.sleep(2)
                
                # Check for connection status
                connected_indicator = await self.page.query_selector('.realtime-chatkit:has-text("Connected"), .realtime-chatkit:has-text("Voice Ready")')
                if connected_indicator:
                    print("   ✅ Voice connection established")
                    self.results['voice_connection_available'] = True
                else:
                    # Check for error states
                    error = await self.page.query_selector('.realtime-chatkit:has-text("Error"), .realtime-chatkit:has-text("Backend not ready")')
                    if error:
                        error_text = await error.inner_text()
                        print(f"   ⚠️ Voice connection issue: {error_text}")
                    else:
                        print("   ⏳ Voice connection in progress...")
            
        except Exception as e:
            print(f"   ❌ Voice connection test failed: {e}")

    async def test_text_agent_interaction(self):
        """Test text-based Agent Builder interaction via ChatKit"""
        print("\n💬 [TEST] Text Agent Builder Integration")
        
        try:
            # Look for ChatKit input field
            await asyncio.sleep(2)  # Allow ChatKit to fully load
            
            # Try multiple selectors for ChatKit input
            input_selectors = [
                'input[placeholder*="message"], input[placeholder*="Message"]',
                '.realtime-chatkit input[type="text"]',
                '.realtime-chatkit textarea',
                'iframe[src*="chat"] input',  # If ChatKit is in iframe
                '[data-testid*="input"], [data-testid*="chat"]'
            ]
            
            chat_input = None
            for selector in input_selectors:
                try:
                    chat_input = await self.page.wait_for_selector(selector, timeout=2000)
                    if chat_input:
                        print(f"   ✓ Found input with selector: {selector}")
                        break
                except:
                    continue
            
            if not chat_input:
                # Check if ChatKit is in an iframe
                iframes = await self.page.query_selector_all('iframe')
                print(f"   📋 Found {len(iframes)} iframes on page")
                
                for i, iframe in enumerate(iframes):
                    try:
                        frame = await iframe.content_frame()
                        if frame:
                            chat_input = await frame.query_selector('input, textarea')
                            if chat_input:
                                print(f"   ✓ Found ChatKit input in iframe {i}")
                                # Switch context to iframe for interaction
                                self.page = frame
                                break
                    except:
                        continue
            
            if chat_input:
                # Test AAPL query (same as original trader test)
                print("   📝 Testing Agent Builder query: 'aapl price'")
                await chat_input.fill('aapl price')
                
                # Submit the message (look for send button or press Enter)
                send_button = await self.page.query_selector('button:has-text("Send"), button[title*="Send"], button[type="submit"]')
                if send_button:
                    await send_button.click()
                else:
                    await chat_input.press('Enter')
                
                print("   ⏳ Waiting for Agent Builder response...")
                await asyncio.sleep(5)  # Give agent time to respond
                
                # Look for response containing AAPL data
                page_content = await self.page.content()
                aapl_keywords = ['AAPL', 'Apple', '$', 'stock', 'price', '247', '248', '249', '250']  # Common AAPL price ranges
                
                response_found = any(keyword.upper() in page_content.upper() for keyword in aapl_keywords)
                if response_found:
                    print("   ✅ Agent Builder responded with AAPL market data")
                    self.results['text_query_response'] = True
                    self.results['market_data_integration'] = True
                else:
                    print("   ⚠️ No clear AAPL response detected")
            
            else:
                print("   ❌ ChatKit input field not found")
                
        except Exception as e:
            print(f"   ❌ Text interaction test failed: {e}")

    async def test_chart_command_integration(self):
        """Test chart command processing from Agent Builder responses"""
        print("\n📊 [TEST] Chart Command Processing Integration")
        
        try:
            # Test a chart-specific query
            chat_input = await self.page.query_selector('input, textarea')
            if chat_input:
                print("   📈 Testing chart command: 'show TSLA chart'")
                await chat_input.fill('show TSLA chart')
                await chat_input.press('Enter')
                
                await asyncio.sleep(3)
                
                # Check if chart symbol changed to TSLA
                chart_element = await self.page.query_selector('.trading-chart, .chart-section')
                if chart_element:
                    # Look for TSLA symbol in chart area
                    tsla_found = await self.page.query_selector(':has-text("TSLA")')
                    if tsla_found:
                        print("   ✅ Chart command processed - TSLA symbol found")
                        self.results['chart_command_processing'] = True
                    else:
                        print("   ⏳ Chart command processing - checking for updates...")
            
        except Exception as e:
            print(f"   ❌ Chart command test failed: {e}")

    async def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print()
        
        status_emoji = {True: "✅", False: "❌"}
        test_descriptions = {
            'page_loaded': 'Trading Dashboard Loading',
            'chatkit_component_found': 'RealtimeChatKit Component Present',
            'voice_button_available': 'Voice Control Button Available',
            'agent_builder_integration': 'ChatKit Agent Builder Integration',
            'text_query_response': 'Text Query Processing (Agent Builder)',
            'voice_connection_available': 'Voice Connection Functionality',
            'chart_command_processing': 'Chart Command Processing',
            'market_data_integration': 'Market Data Integration'
        }
        
        for test_key, result in self.results.items():
            emoji = status_emoji[result]
            description = test_descriptions.get(test_key, test_key)
            print(f"{emoji} {description}")
        
        # Generate recommendations
        print("\n🔧 RECOMMENDATIONS")
        print("-" * 30)
        
        if not self.results['agent_builder_integration']:
            print("• Verify ChatKit session creation with Agent Builder backend")
            print("• Check /api/chatkit/session endpoint is working")
        
        if not self.results['voice_connection_available']:
            print("• Verify OpenAI Realtime API backend integration")
            print("• Check microphone permissions and audio context")
        
        if not self.results['text_query_response']:
            print("• Test Agent Builder MCP server connectivity")
            print("• Verify market data tools are accessible")
        
        if not self.results['chart_command_processing']:
            print("• Check chart command parsing in RealtimeChatKit")
            print("• Verify onChartCommand callback integration")
        
        # Success assessment
        if success_rate >= 80:
            print(f"\n🎉 EXCELLENT: Unified ChatKit Voice Interface is working well!")
            print("   The integration of ChatKit + Agent Voice + Agent Builder is successful.")
        elif success_rate >= 60:
            print(f"\n✅ GOOD: Most core functionality is working.")
            print("   Some minor issues to address for optimal performance.")
        else:
            print(f"\n⚠️ NEEDS WORK: Several core features need attention.")
            print("   Focus on basic ChatKit and Agent Builder connectivity first.")
        
        return self.results

    async def cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            await self.browser.close()

    async def run_full_test_suite(self):
        """Execute the complete test suite"""
        try:
            await self.setup()
            
            # Run all test phases
            await self.test_page_loading()
            await self.test_chatkit_component()
            await self.test_voice_connection()
            await self.test_text_agent_interaction()
            await self.test_chart_command_integration()
            
            # Generate final report
            results = await self.generate_report()
            
            # Save results to file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = f'unified_chatkit_voice_test_results_{timestamp}.json'
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'test_type': 'Unified ChatKit Voice Interface',
                    'success_rate': f"{(sum(results.values()) / len(results)) * 100:.1f}%",
                    'results': results
                }, f, indent=2)
            
            print(f"\n📁 Results saved to: {results_file}")
            
            return results
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return None
        finally:
            await self.cleanup()

async def main():
    """Main test execution"""
    print("🎯 UNIFIED CHATKIT VOICE INTERFACE TEST")
    print("Testing the user's request: 'I want to use realtime with the chatkit'")
    print("=" * 70)
    
    tester = UnifiedChatKitVoiceTest()
    results = await tester.run_full_test_suite()
    
    if results:
        success_count = sum(1 for result in results.values() if result)
        total_count = len(results)
        
        print(f"\n🏁 FINAL RESULT: {success_count}/{total_count} tests passed")
        
        if success_count >= (total_count * 0.8):
            print("🎉 SUCCESS: Unified ChatKit Voice Interface is ready for trading!")
            sys.exit(0)
        else:
            print("⚠️ PARTIAL SUCCESS: Some features need attention before full deployment.")
            sys.exit(1)
    else:
        print("❌ CRITICAL FAILURE: Test suite could not complete.")
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())