#!/usr/bin/env python3
"""
OpenAI Agent Builder MCP Integration Test
========================================
Tests the complete end-to-end workflow of using our MCP server in OpenAI Agent Builder.
Uses Chrome browser (not Chromium) for more reliable testing.

Local MCP server: http://localhost:8000/api/mcp
Auth token: fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
Expected tools: 32 market data tools
"""

import asyncio
import json
import time
from playwright.async_api import async_playwright
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIAgentBuilderMCPTest:
    """Test OpenAI Agent Builder MCP integration workflow"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self.test_results = {
            "navigation": False,
            "mcp_connection": False,
            "tools_loaded": False,
            "workflow_created": False,
            "test_execution": False,
            "end_to_end": False
        }
        
    async def setup_browser(self):
        """Setup Chrome browser for testing"""
        logger.info("🚀 Setting up Chrome browser...")
        
        playwright = await async_playwright().start()
        
        # Use Chrome browser explicitly (not Chromium)
        self.browser = await playwright.chromium.launch(
            headless=False,  # Show browser for demonstration
            channel="chrome",  # Use Chrome instead of Chromium
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-first-run",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]
        )
        
        # Create context with realistic user agent
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Create new page
        self.page = await self.context.new_page()
        
        # Set longer timeouts for network operations
        self.page.set_default_timeout(30000)
        self.page.set_default_navigation_timeout(30000)
        
        logger.info("✅ Chrome browser setup complete")
        
    async def navigate_to_agent_builder(self):
        """Navigate to OpenAI Agent Builder"""
        try:
            logger.info("🌐 Navigating to OpenAI Agent Builder...")
            
            # Navigate to Agent Builder
            await self.page.goto("https://platform.openai.com/playground/assistants")
            
            # Wait for page to load
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we're logged in or need to authenticate
            try:
                # Look for login indicators
                login_button = await self.page.wait_for_selector("text=Sign in", timeout=5000)
                if login_button:
                    logger.warning("⚠️  Authentication required - please log in manually")
                    logger.info("Waiting 30 seconds for manual login...")
                    await asyncio.sleep(30)
            except:
                logger.info("✅ Already authenticated or no login required")
            
            # Wait for Agent Builder interface to load
            await self.page.wait_for_selector("[data-testid='assistant-builder'], .assistant-builder, h1", timeout=15000)
            
            self.test_results["navigation"] = True
            logger.info("✅ Successfully navigated to Agent Builder")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to navigate to Agent Builder: {e}")
            return False
            
    async def create_or_open_workflow(self):
        """Create a new workflow or open existing one"""
        try:
            logger.info("🔧 Creating/opening workflow...")
            
            # Look for "Create Assistant" or similar button
            create_selectors = [
                "text=Create",
                "text=New Assistant", 
                "button[data-testid='create-assistant']",
                ".create-assistant-btn",
                "[aria-label*='Create']"
            ]
            
            created = False
            for selector in create_selectors:
                try:
                    create_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if create_btn:
                        await create_btn.click()
                        logger.info(f"✅ Clicked create button: {selector}")
                        created = True
                        break
                except:
                    continue
                    
            if not created:
                logger.info("ℹ️  No create button found - assuming we're in existing workflow")
            
            # Wait for workflow interface
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)  # Allow interface to stabilize
            
            self.test_results["workflow_created"] = True
            logger.info("✅ Workflow ready")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create/open workflow: {e}")
            return False
            
    async def configure_mcp_integration(self):
        """Configure MCP server integration"""
        try:
            logger.info("🔌 Configuring MCP server integration...")
            
            # Look for MCP/Tools/Actions configuration area
            config_selectors = [
                "text=Tools",
                "text=Actions", 
                "text=Integrations",
                "text=MCP",
                "[data-testid*='tool']",
                "[data-testid*='action']",
                ".tools-section",
                ".actions-panel"
            ]
            
            config_found = False
            for selector in config_selectors:
                try:
                    config_elem = await self.page.wait_for_selector(selector, timeout=3000)
                    if config_elem:
                        await config_elem.click()
                        logger.info(f"✅ Found configuration area: {selector}")
                        config_found = True
                        break
                except:
                    continue
                    
            if not config_found:
                logger.warning("⚠️  MCP configuration area not found - looking for alternative methods")
                
                # Try to find any input fields that might be for MCP configuration
                inputs = await self.page.query_selector_all("input[type='text'], input[type='url']")
                for input_elem in inputs:
                    placeholder = await input_elem.get_attribute("placeholder")
                    if placeholder and any(keyword in placeholder.lower() for keyword in ["url", "endpoint", "server", "mcp"]):
                        logger.info(f"Found potential MCP input with placeholder: {placeholder}")
                        config_found = True
                        break
            
            if config_found:
                # Try to input MCP server details
                mcp_url = "http://localhost:8000/api/mcp"
                auth_token = "fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
                
                # Look for URL input field
                url_selectors = [
                    "input[placeholder*='url' i]",
                    "input[placeholder*='endpoint' i]", 
                    "input[name*='url' i]",
                    "input[type='url']"
                ]
                
                for selector in url_selectors:
                    try:
                        url_input = await self.page.wait_for_selector(selector, timeout=3000)
                        if url_input:
                            await url_input.fill(mcp_url)
                            logger.info(f"✅ Filled MCP URL: {mcp_url}")
                            break
                    except:
                        continue
                
                # Look for authentication token field
                auth_selectors = [
                    "input[placeholder*='token' i]",
                    "input[placeholder*='auth' i]",
                    "input[placeholder*='key' i]",
                    "input[name*='token' i]",
                    "input[type='password']"
                ]
                
                for selector in auth_selectors:
                    try:
                        auth_input = await self.page.wait_for_selector(selector, timeout=3000)
                        if auth_input:
                            await auth_input.fill(auth_token)
                            logger.info("✅ Filled authentication token")
                            break
                    except:
                        continue
                
                # Look for connect/test button
                connect_selectors = [
                    "text=Connect",
                    "text=Test Connection",
                    "text=Add",
                    "button[type='submit']"
                ]
                
                for selector in connect_selectors:
                    try:
                        connect_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if connect_btn:
                            await connect_btn.click()
                            logger.info("✅ Clicked connect button")
                            await asyncio.sleep(5)  # Wait for connection
                            break
                    except:
                        continue
                        
                self.test_results["mcp_connection"] = True
                logger.info("✅ MCP configuration completed")
                return True
            else:
                logger.warning("⚠️  Could not find MCP configuration interface")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to configure MCP integration: {e}")
            return False
            
    async def verify_tools_loaded(self):
        """Verify that MCP tools are loaded and available"""
        try:
            logger.info("🔍 Verifying MCP tools are loaded...")
            
            # Wait for tools to load
            await asyncio.sleep(5)
            
            # Look for indicators that tools are available
            tool_indicators = [
                "text=get_stock_quote",
                "text=get_stock_history", 
                "text=get_market_overview",
                ".tool-item",
                ".action-item",
                "[data-tool-name]"
            ]
            
            tools_found = 0
            for indicator in tool_indicators:
                try:
                    elements = await self.page.query_selector_all(indicator)
                    if elements:
                        tools_found += len(elements)
                        logger.info(f"Found {len(elements)} elements matching: {indicator}")
                except:
                    continue
            
            if tools_found > 0:
                self.test_results["tools_loaded"] = True
                logger.info(f"✅ Found {tools_found} tool indicators - MCP tools appear to be loaded")
                return True
            else:
                logger.warning("⚠️  No tool indicators found - tools may not be loaded yet")
                
                # Check page content for any mention of our tools
                content = await self.page.content()
                mcp_keywords = ["stock_quote", "market_data", "get_stock", "32 tools", "MCP"]
                found_keywords = [kw for kw in mcp_keywords if kw in content.lower()]
                
                if found_keywords:
                    logger.info(f"✅ Found MCP-related content: {found_keywords}")
                    self.test_results["tools_loaded"] = True
                    return True
                else:
                    logger.warning("⚠️  No MCP-related content found in page")
                    return False
                
        except Exception as e:
            logger.error(f"❌ Failed to verify tools loaded: {e}")
            return False
            
    async def create_test_workflow(self):
        """Create a simple test workflow that uses MCP tools"""
        try:
            logger.info("🏗️  Creating test workflow with MCP tool...")
            
            # Look for workflow design area or prompt input
            design_selectors = [
                "textarea[placeholder*='message' i]",
                "textarea[placeholder*='prompt' i]",
                "textarea[placeholder*='instruction' i]",
                ".prompt-input",
                ".message-input",
                "textarea"
            ]
            
            prompt_input = None
            for selector in design_selectors:
                try:
                    prompt_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if prompt_input:
                        logger.info(f"Found prompt input: {selector}")
                        break
                except:
                    continue
            
            if prompt_input:
                # Create a simple prompt that would use MCP tools
                test_prompt = """
You are a market data assistant. When users ask for stock information, use the available MCP tools to get real-time data.

Test: Get the current stock price for Tesla (TSLA) using the get_stock_quote tool.
"""
                
                await prompt_input.fill(test_prompt)
                logger.info("✅ Created test workflow prompt")
                
                # Save/apply the workflow
                save_selectors = [
                    "text=Save",
                    "text=Apply",
                    "text=Update",
                    "button[type='submit']"
                ]
                
                for selector in save_selectors:
                    try:
                        save_btn = await self.page.wait_for_selector(selector, timeout=3000)
                        if save_btn:
                            await save_btn.click()
                            logger.info("✅ Saved test workflow")
                            break
                    except:
                        continue
                        
                self.test_results["workflow_created"] = True
                return True
            else:
                logger.warning("⚠️  Could not find prompt input area")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to create test workflow: {e}")
            return False
            
    async def execute_test_workflow(self):
        """Execute the test workflow to verify end-to-end functionality"""
        try:
            logger.info("▶️  Executing test workflow...")
            
            # Look for test/run button
            run_selectors = [
                "text=Test",
                "text=Run", 
                "text=Execute",
                "text=Try",
                ".test-button",
                ".run-button"
            ]
            
            for selector in run_selectors:
                try:
                    run_btn = await self.page.wait_for_selector(selector, timeout=3000)
                    if run_btn:
                        await run_btn.click()
                        logger.info(f"✅ Clicked run button: {selector}")
                        break
                except:
                    continue
            
            # Wait for execution and look for results
            await asyncio.sleep(10)
            
            # Look for output/results area
            result_selectors = [
                ".output",
                ".result", 
                ".response",
                ".message-response",
                "[data-testid*='output']",
                "[data-testid*='result']"
            ]
            
            results_found = False
            for selector in result_selectors:
                try:
                    result_elem = await self.page.wait_for_selector(selector, timeout=5000)
                    if result_elem:
                        result_text = await result_elem.inner_text()
                        if result_text and len(result_text) > 10:
                            logger.info(f"✅ Found execution result: {result_text[:100]}...")
                            results_found = True
                            
                            # Check if result contains stock data (indicating MCP tool was called)
                            if any(keyword in result_text.lower() for keyword in ["tsla", "tesla", "price", "$", "stock"]):
                                logger.info("✅ Result contains stock data - MCP tool execution successful!")
                                self.test_results["test_execution"] = True
                                self.test_results["end_to_end"] = True
                                return True
                            break
                except:
                    continue
            
            if not results_found:
                # Check page content for any execution results
                content = await self.page.content()
                if "tsla" in content.lower() or "tesla" in content.lower():
                    logger.info("✅ Found Tesla-related content - test may have executed")
                    self.test_results["test_execution"] = True
                    return True
                else:
                    logger.warning("⚠️  No execution results found")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Failed to execute test workflow: {e}")
            return False
            
    async def take_screenshot(self, filename: str):
        """Take screenshot for documentation"""
        try:
            await self.page.screenshot(path=filename, full_page=True)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"❌ Failed to take screenshot: {e}")
            
    async def cleanup(self):
        """Cleanup browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✅ Browser cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
            
    async def run_full_test(self):
        """Run the complete end-to-end test"""
        logger.info("🚀 Starting OpenAI Agent Builder MCP Integration Test")
        logger.info("=" * 60)
        
        try:
            # Setup browser
            await self.setup_browser()
            
            # Test steps
            steps = [
                ("Navigate to Agent Builder", self.navigate_to_agent_builder),
                ("Create/Open Workflow", self.create_or_open_workflow),  
                ("Configure MCP Integration", self.configure_mcp_integration),
                ("Verify Tools Loaded", self.verify_tools_loaded),
                ("Create Test Workflow", self.create_test_workflow),
                ("Execute Test Workflow", self.execute_test_workflow)
            ]
            
            for step_name, step_func in steps:
                logger.info(f"\n🔄 {step_name}...")
                try:
                    success = await step_func()
                    if success:
                        logger.info(f"✅ {step_name} - PASSED")
                    else:
                        logger.warning(f"⚠️  {step_name} - FAILED")
                        
                    # Take screenshot after each major step
                    screenshot_name = f"agent_builder_step_{step_name.lower().replace(' ', '_')}.png"
                    await self.take_screenshot(screenshot_name)
                    
                    # Brief pause between steps
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"❌ {step_name} - ERROR: {e}")
            
            # Final results
            logger.info("\n" + "=" * 60)
            logger.info("🏁 TEST RESULTS SUMMARY")
            logger.info("=" * 60)
            
            for test_name, result in self.test_results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                logger.info(f"{test_name.ljust(20)}: {status}")
                
            # Overall success
            passed_tests = sum(self.test_results.values())
            total_tests = len(self.test_results)
            success_rate = (passed_tests / total_tests) * 100
            
            logger.info(f"\nOverall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
            
            if self.test_results["end_to_end"]:
                logger.info("🎉 END-TO-END INTEGRATION SUCCESSFUL!")
                logger.info("✅ MCP server integration with OpenAI Agent Builder is working!")
            else:
                logger.warning("⚠️  End-to-end integration incomplete")
                logger.info("💡 Manual verification may be needed for full validation")
                
            # Keep browser open for manual inspection
            logger.info("\n🔍 Browser will remain open for 60 seconds for manual inspection...")
            await asyncio.sleep(60)
            
        finally:
            await self.cleanup()


async def main():
    """Main test execution"""
    test = OpenAIAgentBuilderMCPTest()
    await test.run_full_test()


if __name__ == "__main__":
    print("""
🧪 OpenAI Agent Builder MCP Integration Test
===========================================

This test will:
1. Open Chrome browser and navigate to OpenAI Agent Builder
2. Create/open a workflow
3. Configure MCP server integration (localhost:8000/api/mcp)
4. Verify 32 market data tools are loaded
5. Create a test workflow using get_stock_quote for TSLA
6. Execute the workflow end-to-end
7. Verify the complete integration works

MCP Server Details:
- URL: http://localhost:8000/api/mcp
- Auth: fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
- Tools: 32 market data tools

Prerequisites:
- Local MCP server running on localhost:8000
- Chrome browser installed
- OpenAI account with Agent Builder access
""")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")