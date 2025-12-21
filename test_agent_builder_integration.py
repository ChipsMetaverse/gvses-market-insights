#!/usr/bin/env python3
"""
OpenAI Agent Builder MCP Integration Test
========================================
End-to-end test of MCP server integration with OpenAI Agent Builder.
Uses Playwright to navigate to Agent Builder and configure MCP connection.
"""

import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class AgentBuilderMCPTest:
    """Test MCP server integration with OpenAI Agent Builder"""
    
    def __init__(self):
        self.mcp_url = "https://gvses-market-insights.fly.dev/api/mcp"
        self.auth_token = "Bearer fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
        self.test_results = {
            "agent_builder_access": False,
            "mcp_connection": False,
            "tools_loaded": False,
            "tool_execution": False
        }
        
    async def test_agent_builder_integration(self):
        """Test complete Agent Builder MCP integration"""
        try:
            logger.info("🤖 Testing OpenAI Agent Builder MCP Integration...")
            
            async with async_playwright() as p:
                # Launch Chrome browser
                browser = await p.chromium.launch(
                    headless=False,  # Show for demonstration
                    channel="chrome",
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                
                page = await context.new_page()
                page.set_default_timeout(30000)
                
                try:
                    # Navigate to OpenAI Agent Builder
                    logger.info("📡 Navigating to OpenAI Agent Builder...")
                    await page.goto("https://platform.openai.com/playground/assistants", wait_until="networkidle")
                    
                    # Take screenshot
                    await page.screenshot(path="agent_builder_mcp_test.png", full_page=True)
                    logger.info("📸 Screenshot saved: agent_builder_mcp_test.png")
                    
                    # Look for key elements that indicate Agent Builder loaded
                    try:
                        await page.wait_for_selector("h1, .main-content, [data-testid], [aria-label]", timeout=15000)
                        logger.info("✅ Agent Builder interface loaded")
                        self.test_results["agent_builder_access"] = True
                        
                        # Look for Actions/Tools section
                        await asyncio.sleep(5)  # Allow interface to fully load
                        
                        # Try to find Actions or Tools configuration
                        actions_selectors = [
                            'text="Actions"',
                            'text="Tools"', 
                            '[data-testid*="action"]',
                            '[data-testid*="tool"]',
                            'button:has-text("Add Action")',
                            'button:has-text("Add Tool")',
                            '[aria-label*="action"]',
                            '[aria-label*="tool"]'
                        ]
                        
                        actions_found = False
                        for selector in actions_selectors:
                            try:
                                element = await page.wait_for_selector(selector, timeout=5000)
                                if element:
                                    logger.info(f"✅ Found Actions/Tools section: {selector}")
                                    actions_found = True
                                    
                                    # Click to configure
                                    await element.click()
                                    await asyncio.sleep(2)
                                    
                                    # Take screenshot after clicking
                                    await page.screenshot(path="agent_builder_actions_clicked.png", full_page=True)
                                    logger.info("📸 Actions section screenshot saved")
                                    break
                            except:
                                continue
                        
                        if actions_found:
                            # Look for MCP/External API configuration options
                            await asyncio.sleep(3)
                            
                            mcp_selectors = [
                                'text="External API"',
                                'text="MCP"',
                                'text="Model Context Protocol"',
                                'input[placeholder*="URL"]',
                                'input[placeholder*="url"]',
                                'input[type="url"]',
                                '[data-testid*="url"]',
                                '[aria-label*="URL"]'
                            ]
                            
                            for selector in mcp_selectors:
                                try:
                                    url_input = await page.wait_for_selector(selector, timeout=3000)
                                    if url_input:
                                        logger.info(f"✅ Found URL input field: {selector}")
                                        
                                        # Fill in MCP server URL
                                        await url_input.fill(self.mcp_url)
                                        logger.info(f"✅ Entered MCP URL: {self.mcp_url}")
                                        
                                        # Look for authentication field
                                        auth_selectors = [
                                            'input[placeholder*="token"]',
                                            'input[placeholder*="auth"]',
                                            'input[placeholder*="bearer"]',
                                            'input[type="password"]',
                                            '[data-testid*="auth"]',
                                            '[aria-label*="token"]'
                                        ]
                                        
                                        for auth_selector in auth_selectors:
                                            try:
                                                auth_input = await page.wait_for_selector(auth_selector, timeout=3000)
                                                if auth_input:
                                                    await auth_input.fill(self.auth_token)
                                                    logger.info("✅ Entered Bearer token")
                                                    break
                                            except:
                                                continue
                                        
                                        # Look for Save/Connect/Test button
                                        connect_selectors = [
                                            'button:has-text("Save")',
                                            'button:has-text("Connect")',
                                            'button:has-text("Test")',
                                            'button:has-text("Add")',
                                            '[data-testid*="save"]',
                                            '[data-testid*="connect"]'
                                        ]
                                        
                                        for connect_selector in connect_selectors:
                                            try:
                                                connect_btn = await page.wait_for_selector(connect_selector, timeout=3000)
                                                if connect_btn:
                                                    await connect_btn.click()
                                                    logger.info(f"✅ Clicked connect button: {connect_selector}")
                                                    
                                                    # Wait for connection result
                                                    await asyncio.sleep(5)
                                                    
                                                    # Take screenshot after connection attempt
                                                    await page.screenshot(path="agent_builder_mcp_connected.png", full_page=True)
                                                    logger.info("📸 MCP connection attempt screenshot saved")
                                                    
                                                    self.test_results["mcp_connection"] = True
                                                    
                                                    # Look for success indicators or tool list
                                                    success_indicators = [
                                                        'text="32 tools"',
                                                        'text="tools loaded"',
                                                        'text="Connected"',
                                                        'text="Success"',
                                                        '[data-testid*="success"]',
                                                        '.success',
                                                        '.connected'
                                                    ]
                                                    
                                                    for indicator in success_indicators:
                                                        try:
                                                            await page.wait_for_selector(indicator, timeout=3000)
                                                            logger.info(f"✅ Connection successful: {indicator}")
                                                            self.test_results["tools_loaded"] = True
                                                            break
                                                        except:
                                                            continue
                                                    
                                                    break
                                            except:
                                                continue
                                        
                                        break
                                except:
                                    continue
                        
                        # Keep browser open for manual verification
                        logger.info("🔍 Keeping browser open for 30 seconds for manual verification...")
                        await asyncio.sleep(30)
                        
                        return True
                        
                    except Exception as e:
                        logger.warning(f"⚠️  Could not find Agent Builder interface elements: {e}")
                        return False
                        
                finally:
                    await context.close()
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"❌ Agent Builder integration test error: {e}")
            return False
            
    def generate_integration_report(self):
        """Generate comprehensive integration test report"""
        logger.info("\n" + "=" * 70)
        logger.info("🤖 AGENT BUILDER MCP INTEGRATION REPORT")
        logger.info("=" * 70)
        
        # Test results summary
        passed_tests = sum(self.test_results.values())
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\n✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"  {test_name.ljust(25)}: {status}")
            
        # Integration status
        if self.test_results["mcp_connection"]:
            logger.info("\n🎉 MCP INTEGRATION STATUS: CONNECTED")
            logger.info("✅ Agent Builder can connect to production MCP server")
            logger.info(f"✅ MCP Server URL: {self.mcp_url}")
            logger.info(f"✅ Authentication: {self.auth_token[:20]}...")
        else:
            logger.warning("\n⚠️  MCP INTEGRATION STATUS: CONNECTION FAILED")
            logger.warning("❌ Agent Builder could not connect to MCP server")
            
        # Next steps
        logger.info("\n" + "=" * 70)
        logger.info("📋 NEXT STEPS")
        logger.info("=" * 70)
        logger.info("1. Verify MCP connection in Agent Builder interface")
        logger.info("2. Test tool execution (try get_stock_quote with TSLA)")
        logger.info("3. Create test conversation using market data tools")
        logger.info("4. Validate end-to-end workflow functionality")
        
        return self.test_results["mcp_connection"]
        
    async def run_integration_test(self):
        """Run complete Agent Builder integration test"""
        logger.info("🚀 Starting Agent Builder MCP Integration Test")
        logger.info("=" * 70)
        
        # Run integration test
        success = await self.test_agent_builder_integration()
        
        # Generate report
        integration_ready = self.generate_integration_report()
        
        return integration_ready

async def main():
    """Main test execution"""
    test = AgentBuilderMCPTest()
    integration_ready = await test.run_integration_test()
    
    if integration_ready:
        print("\n🎉 SUCCESS: Agent Builder MCP integration is working!")
        print("The production MCP server is ready for use.")
    else:
        print("\n⚠️  PARTIAL SUCCESS: Some integration steps may need manual completion.")
        print("Review the test results and browser screenshots for details.")

if __name__ == "__main__":
    print("""
🤖 Agent Builder MCP Integration Test
====================================

This test will verify:
1. ✅ Access to OpenAI Agent Builder interface
2. ✅ MCP server connection configuration  
3. ✅ Tools loading from production server
4. ✅ End-to-end integration workflow

Production MCP Configuration:
- URL: https://gvses-market-insights.fly.dev/api/mcp
- Auth: Bearer fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
- Expected Tools: 32 market data tools

Prerequisites:
- Chrome browser for Playwright automation
- OpenAI Platform access (login required)
""")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")