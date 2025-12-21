#!/usr/bin/env python3
"""
Comprehensive Playwright Debug Test for ChatKit Integration
As requested by user: "WGCCTO should debug using playwright"

This test debugs and verifies the complete Agent Builder integration:
1. Frontend compilation and loading
2. ChatKit component rendering and connectivity  
3. "aapl" query processing through Agent Builder
4. Unified voice/agent experience
5. HTTP MCP endpoint integration
"""

import asyncio
import json
import time
import sys
from playwright.async_api import async_playwright, Page, Browser
import requests

class ChatKitIntegrationDebugger:
    def __init__(self):
        self.browser: Browser = None
        self.page: Page = None
        self.results = {
            "frontend_loading": False,
            "chatkit_component": False,
            "chatkit_session": False,
            "agent_query_processing": False,
            "http_mcp_integration": False,
            "unified_interface": False,
            "errors": []
        }
    
    async def setup(self):
        """Initialize browser and page"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False, slow_mo=1000)
        self.page = await self.browser.new_page()
        
        # Enable console logging
        self.page.on("console", lambda msg: print(f"🖥️  CONSOLE: {msg.text}"))
        self.page.on("pageerror", lambda error: print(f"❌ PAGE ERROR: {error}"))
        
        print("🚀 ChatKit Integration Debugger initialized")
    
    async def test_backend_endpoints(self):
        """Test backend endpoints before frontend testing"""
        print("\n🧪 Testing Backend Endpoints...")
        
        # Test ChatKit session endpoint
        try:
            response = requests.post(
                "http://localhost:8000/api/chatkit/session",
                json={"device_id": "debug_test_123"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ ChatKit session endpoint working: {data.get('session_id')}")
                self.results["chatkit_session"] = True
            else:
                print(f"❌ ChatKit session endpoint failed: {response.status_code}")
                self.results["errors"].append(f"ChatKit session: {response.status_code}")
        except Exception as e:
            print(f"❌ ChatKit session endpoint error: {e}")
            self.results["errors"].append(f"ChatKit session: {str(e)}")
        
        # Test HTTP MCP endpoint
        try:
            response = requests.post(
                "http://localhost:8000/api/mcp",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "get_stock_quote",
                        "arguments": {"symbol": "AAPL"}
                    }
                },
                headers={"Authorization": "Bearer fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ HTTP MCP endpoint working: AAPL data received")
                self.results["http_mcp_integration"] = True
            else:
                print(f"❌ HTTP MCP endpoint failed: {response.status_code}")
                self.results["errors"].append(f"HTTP MCP: {response.status_code}")
        except Exception as e:
            print(f"❌ HTTP MCP endpoint error: {e}")
            self.results["errors"].append(f"HTTP MCP: {str(e)}")
    
    async def test_frontend_loading(self):
        """Test if frontend loads without compilation errors"""
        print("\n🌐 Testing Frontend Loading...")
        
        try:
            # Navigate to frontend
            await self.page.goto("http://localhost:5174", timeout=10000)
            
            # Wait for main content to load
            await self.page.wait_for_selector(".trading-dashboard-simple", timeout=10000)
            
            # Check for compilation errors
            error_elements = await self.page.query_selector_all(".error, .compilation-error")
            if error_elements:
                print("❌ Frontend compilation errors detected")
                for element in error_elements:
                    text = await element.text_content()
                    self.results["errors"].append(f"Compilation: {text}")
                return False
            
            print("✅ Frontend loaded successfully without compilation errors")
            self.results["frontend_loading"] = True
            return True
            
        except Exception as e:
            print(f"❌ Frontend loading failed: {e}")
            self.results["errors"].append(f"Frontend loading: {str(e)}")
            return False
    
    async def test_chatkit_component(self):
        """Test if ChartAgentChat component is rendered and functional"""
        print("\n🎯 Testing ChatKit Component...")
        
        try:
            # Look for ChartAgentChat component or ChatKit evidence in console
            chatkit_selector = ".chart-agent-chat, .agent-chat-integration, [class*='chatkit']"
            
            # Also check console for ChatKit success message
            console_messages = []
            def handle_console(msg):
                console_messages.append(msg.text)
            self.page.on("console", handle_console)
            
            await asyncio.sleep(2)  # Wait for console messages
            
            chatkit_success = any("ChatKit session created successfully" in msg for msg in console_messages)
            if chatkit_success:
                print("✅ ChatKit session creation detected in console")
                self.results["chatkit_component"] = True
                return True
            
            try:
                await self.page.wait_for_selector(chatkit_selector, timeout=3000)
            except:
                print("⚠️ ChatKit DOM element not found, but checking console...")
            
            chatkit_element = await self.page.query_selector(chatkit_selector)
            if chatkit_element:
                print("✅ ChatKit component found in DOM")
                
                # Check if component has proper classes and structure
                classes = await chatkit_element.get_attribute("class")
                print(f"📝 ChatKit classes: {classes}")
                
                # Look for ChatKit internal elements
                chatkit_internal = await self.page.query_selector_all("[data-testid*='chatkit'], [class*='chatkit'], .chat-input, .chat-messages")
                if chatkit_internal:
                    print(f"✅ ChatKit internal elements found: {len(chatkit_internal)}")
                    self.results["chatkit_component"] = True
                else:
                    print("⚠️ ChatKit component exists but internal elements not found")
                    self.results["errors"].append("ChatKit internal elements missing")
                
                return True
            else:
                print("❌ ChatKit component not found")
                self.results["errors"].append("ChatKit component not in DOM")
                return False
                
        except Exception as e:
            print(f"❌ ChatKit component test failed: {e}")
            self.results["errors"].append(f"ChatKit component: {str(e)}")
            return False
    
    async def test_unified_interface(self):
        """Test if the interface is properly unified (no separate tabs)"""
        print("\n🔗 Testing Unified Interface...")
        
        try:
            # Check for old tab structure (should NOT exist)
            tab_buttons = await self.page.query_selector_all(".tab-button, .right-panel-tabs button")
            if tab_buttons:
                print(f"❌ Found {len(tab_buttons)} tab buttons - interface not unified")
                for tab in tab_buttons:
                    text = await tab.text_content()
                    self.results["errors"].append(f"Tab found: {text}")
                return False
            
            # Check for unified AI assistant title
            ai_title = await self.page.query_selector(".panel-title")
            if ai_title:
                title_text = await ai_title.text_content()
                if "AI ASSISTANT" in title_text:
                    print(f"✅ Unified interface confirmed: {title_text}")
                    self.results["unified_interface"] = True
                    return True
                else:
                    print(f"⚠️ Panel title found but not unified: {title_text}")
            
            print("❌ Unified interface not properly implemented")
            self.results["errors"].append("Interface not unified")
            return False
            
        except Exception as e:
            print(f"❌ Unified interface test failed: {e}")
            self.results["errors"].append(f"Unified interface: {str(e)}")
            return False
    
    async def test_agent_query_processing(self):
        """Test 'aapl' query processing through the integrated system"""
        print("\n💬 Testing Agent Query Processing...")
        
        try:
            # Look for input field
            input_selector = ".voice-text-input, input[type='text']"
            await self.page.wait_for_selector(input_selector, timeout=5000)
            
            # Type 'aapl' query
            await self.page.fill(input_selector, "aapl")
            print("✅ Typed 'aapl' into input field")
            
            # Click send button or press Enter
            send_button = await self.page.query_selector(".voice-send-button, button[title*='Send']")
            if send_button:
                await send_button.click()
                print("✅ Clicked send button")
            else:
                await self.page.press(input_selector, "Enter")
                print("✅ Pressed Enter")
            
            # Wait for response
            print("⏳ Waiting for Agent Builder response...")
            await asyncio.sleep(5)  # Give time for processing
            
            # Check for message bubbles or response content
            messages = await self.page.query_selector_all(".conversation-message-enhanced, .message-bubble, .response")
            if messages:
                print(f"✅ Found {len(messages)} messages in conversation")
                
                # Check for AAPL-specific content
                for message in messages:
                    text = await message.text_content()
                    if any(keyword in text.upper() for keyword in ["AAPL", "APPLE", "$247", "STOCK"]):
                        print(f"✅ Agent Builder response contains AAPL data: {text[:100]}...")
                        self.results["agent_query_processing"] = True
                        return True
                
                print("⚠️ Messages found but no AAPL content detected")
                self.results["errors"].append("No AAPL data in response")
            else:
                print("❌ No messages found after query")
                self.results["errors"].append("No response messages")
            
            return False
            
        except Exception as e:
            print(f"❌ Agent query processing test failed: {e}")
            self.results["errors"].append(f"Agent query: {str(e)}")
            return False
    
    async def capture_debug_screenshots(self):
        """Capture screenshots for debugging"""
        print("\n📸 Capturing Debug Screenshots...")
        
        try:
            # Full page screenshot
            await self.page.screenshot(path="chatkit_debug_full.png", full_page=True)
            print("✅ Full page screenshot saved: chatkit_debug_full.png")
            
            # Chat area screenshot
            chat_area = await self.page.query_selector(".voice-conversation-section, .right-panel")
            if chat_area:
                await chat_area.screenshot(path="chatkit_debug_chat.png")
                print("✅ Chat area screenshot saved: chatkit_debug_chat.png")
            
        except Exception as e:
            print(f"⚠️ Screenshot capture failed: {e}")
    
    async def generate_debug_report(self):
        """Generate comprehensive debug report"""
        print("\n📊 Debug Report Summary:")
        print("=" * 50)
        
        total_tests = len([k for k in self.results.keys() if k != "errors"])
        passed_tests = len([v for k, v in self.results.items() if k != "errors" and v])
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Overall Status: {'✅ PASSING' if passed_tests == total_tests else '❌ FAILING'}")
        print()
        
        for test_name, result in self.results.items():
            if test_name == "errors":
                continue
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        if self.results["errors"]:
            print("\n🚨 Errors Detected:")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        # Specific recommendations
        print("\n💡 Recommendations:")
        if not self.results["frontend_loading"]:
            print("  - Fix frontend compilation errors first")
        if not self.results["chatkit_component"]:
            print("  - Verify ChartAgentChat component integration")
        if not self.results["unified_interface"]:
            print("  - Remove remaining tab structure and unify interface")
        if not self.results["agent_query_processing"]:
            print("  - Debug Agent Builder → HTTP MCP → response flow")
        
        return passed_tests == total_tests
    
    async def cleanup(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
        print("\n🔧 Cleanup completed")

async def main():
    """Main debug execution"""
    debugger = ChatKitIntegrationDebugger()
    
    try:
        await debugger.setup()
        
        # Phase 1: Backend verification
        await debugger.test_backend_endpoints()
        
        # Phase 2: Frontend testing
        if await debugger.test_frontend_loading():
            await debugger.test_unified_interface()
            await debugger.test_chatkit_component()
            await debugger.test_agent_query_processing()
        
        # Phase 3: Debug artifacts
        await debugger.capture_debug_screenshots()
        
        # Phase 4: Report
        success = await debugger.generate_debug_report()
        
        return success
        
    except Exception as e:
        print(f"🚨 Debug execution failed: {e}")
        return False
    finally:
        await debugger.cleanup()

if __name__ == "__main__":
    print("🔍 ChatKit Integration Debugger Starting...")
    print("As requested: 'WGCCTO should debug using playwright'")
    print("=" * 60)
    
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All tests passed! ChatKit integration is working correctly.")
        sys.exit(0)
    else:
        print("\n🚨 Some tests failed. Review the debug report above.")
        sys.exit(1)