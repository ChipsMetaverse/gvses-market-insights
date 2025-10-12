#!/usr/bin/env python3
"""
Test Agent Builder MCP Integration with Production Server
Tests the MCP configuration at https://chatgpt.com/g/gog-builder/
"""

import asyncio
import time
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import os
from pathlib import Path

class AgentBuilderMCPTest:
    def __init__(self):
        self.screenshots_dir = Path("screenshots/agent_builder")
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.test_config = {
            "url": "https://gvses-market-insights.fly.dev/api/mcp",
            "label": "GVSES Market Data", 
            "token": "fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
        }
        
    async def take_screenshot(self, page: Page, name: str, description: str = ""):
        """Take screenshot with timestamp and description"""
        timestamp = int(time.time())
        filename = f"{timestamp}_{name}.png"
        filepath = self.screenshots_dir / filename
        
        await page.screenshot(path=str(filepath), full_page=True)
        print(f"📸 Screenshot: {filename}")
        if description:
            print(f"   Description: {description}")
        return filepath
        
    async def wait_for_page_load(self, page: Page, timeout: int = 10000):
        """Wait for page to fully load"""
        try:
            await page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception as e:
            print(f"⚠️  Page load timeout: {e}")
            
    async def test_agent_builder_navigation(self, page: Page):
        """Test navigation to Agent Builder"""
        print("\n🔍 Step 1: Navigating to Agent Builder...")
        
        try:
            # Navigate to Agent Builder
            await page.goto("https://chatgpt.com/g/gog-builder/", timeout=30000)
            await self.wait_for_page_load(page)
            
            # Take screenshot of initial page
            await self.take_screenshot(page, "01_agent_builder_landing", 
                                     "Agent Builder landing page")
            
            # Check if we're logged in or need to log in
            if "login" in page.url.lower() or await page.locator("text=Log in").count() > 0:
                print("🔐 Login required - please log in manually")
                await self.take_screenshot(page, "02_login_required", 
                                         "Login page detected")
                return False
                
            # Look for Agent Builder interface elements
            builder_indicators = [
                "text=MCP",
                "text=node", 
                "text=connection",
                "text=configure",
                "[data-testid*='mcp']",
                "[class*='mcp']"
            ]
            
            found_builder = False
            for indicator in builder_indicators:
                if await page.locator(indicator).count() > 0:
                    found_builder = True
                    print(f"✅ Found builder indicator: {indicator}")
                    break
                    
            if not found_builder:
                print("❌ Agent Builder interface not detected")
                
            return found_builder
            
        except Exception as e:
            print(f"❌ Navigation failed: {e}")
            await self.take_screenshot(page, "navigation_error", 
                                     f"Navigation error: {e}")
            return False
            
    async def test_mcp_configuration(self, page: Page):
        """Test MCP node configuration"""
        print("\n🔧 Step 2: Configuring MCP Node...")
        
        try:
            # Look for MCP configuration elements
            mcp_selectors = [
                "button:has-text('Add MCP')",
                "button:has-text('+ MCP')", 
                "[data-testid='add-mcp']",
                "text=Add MCP Server",
                "text=MCP Configuration",
                "input[placeholder*='mcp']",
                "input[placeholder*='URL']",
                "input[placeholder*='server']"
            ]
            
            config_button = None
            for selector in mcp_selectors:
                element = page.locator(selector).first
                if await element.count() > 0:
                    config_button = element
                    print(f"✅ Found MCP config element: {selector}")
                    break
                    
            await self.take_screenshot(page, "03_mcp_config_search", 
                                     "Searching for MCP configuration elements")
            
            if config_button:
                # Click to add/configure MCP
                await config_button.click()
                await asyncio.sleep(2)
                
                await self.take_screenshot(page, "04_mcp_config_opened", 
                                         "MCP configuration dialog opened")
                
                # Try to fill in the configuration
                await self.fill_mcp_configuration(page)
                
            else:
                print("❌ Could not find MCP configuration elements")
                # Try alternative approaches
                await self.try_alternative_mcp_config(page)
                
        except Exception as e:
            print(f"❌ MCP configuration failed: {e}")
            await self.take_screenshot(page, "mcp_config_error", 
                                     f"MCP config error: {e}")
            
    async def fill_mcp_configuration(self, page: Page):
        """Fill in MCP configuration details"""
        print("📝 Filling MCP configuration...")
        
        try:
            # Look for URL input field
            url_selectors = [
                "input[placeholder*='URL']",
                "input[placeholder*='url']",
                "input[placeholder*='endpoint']",
                "input[name*='url']",
                "input[id*='url']"
            ]
            
            for selector in url_selectors:
                url_field = page.locator(selector).first
                if await url_field.count() > 0:
                    print(f"✅ Found URL field: {selector}")
                    await url_field.fill(self.test_config["url"])
                    break
            else:
                print("❌ Could not find URL input field")
                
            # Look for label/name field
            label_selectors = [
                "input[placeholder*='label']",
                "input[placeholder*='name']", 
                "input[name*='label']",
                "input[name*='name']",
                "input[id*='label']"
            ]
            
            for selector in label_selectors:
                label_field = page.locator(selector).first
                if await label_field.count() > 0:
                    print(f"✅ Found label field: {selector}")
                    await label_field.fill(self.test_config["label"])
                    break
            else:
                print("❌ Could not find label input field")
                
            # Look for token/auth field
            auth_selectors = [
                "input[placeholder*='token']",
                "input[placeholder*='bearer']",
                "input[placeholder*='auth']",
                "input[name*='token']",
                "input[type='password']"
            ]
            
            for selector in auth_selectors:
                auth_field = page.locator(selector).first
                if await auth_field.count() > 0:
                    print(f"✅ Found auth field: {selector}")
                    await auth_field.fill(self.test_config["token"])
                    break
            else:
                print("❌ Could not find authentication input field")
                
            await self.take_screenshot(page, "05_mcp_fields_filled", 
                                     "MCP configuration fields filled")
            
            # Try to submit/test the configuration
            await self.test_mcp_connection(page)
            
        except Exception as e:
            print(f"❌ Failed to fill MCP configuration: {e}")
            
    async def test_mcp_connection(self, page: Page):
        """Test the MCP connection"""
        print("🔗 Testing MCP connection...")
        
        try:
            # Look for test/connect/save buttons
            action_selectors = [
                "button:has-text('Test')",
                "button:has-text('Connect')",
                "button:has-text('Save')", 
                "button:has-text('Apply')",
                "[data-testid*='test']",
                "[data-testid*='connect']"
            ]
            
            for selector in action_selectors:
                button = page.locator(selector).first
                if await button.count() > 0:
                    print(f"✅ Found action button: {selector}")
                    await button.click()
                    await asyncio.sleep(3)  # Wait for connection attempt
                    
                    await self.take_screenshot(page, "06_mcp_connection_attempt", 
                                             "MCP connection attempt")
                    break
            else:
                print("❌ Could not find test/connect button")
                
            # Check for success/error messages
            await self.check_connection_result(page)
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            
    async def check_connection_result(self, page: Page):
        """Check for connection success or error messages"""
        print("📊 Checking connection results...")
        
        await asyncio.sleep(5)  # Wait for potential error messages
        
        # Look for success indicators
        success_selectors = [
            "text=Success",
            "text=Connected", 
            "text=✅",
            "[class*='success']",
            "[data-testid*='success']"
        ]
        
        # Look for error indicators  
        error_selectors = [
            "text=Error",
            "text=Failed",
            "text=❌",
            "[class*='error']",
            "[data-testid*='error']",
            ".error",
            ".alert"
        ]
        
        success_found = False
        error_found = False
        
        for selector in success_selectors:
            if await page.locator(selector).count() > 0:
                success_found = True
                message = await page.locator(selector).first.text_content()
                print(f"✅ Success message: {message}")
                break
                
        for selector in error_selectors:
            if await page.locator(selector).count() > 0:
                error_found = True
                message = await page.locator(selector).first.text_content()
                print(f"❌ Error message: {message}")
                
        if not success_found and not error_found:
            print("⚠️  No clear success/error messages found")
            
        await self.take_screenshot(page, "07_connection_result", 
                                 "Final connection result")
        
    async def try_alternative_mcp_config(self, page: Page):
        """Try alternative methods to find MCP configuration"""
        print("🔍 Trying alternative MCP configuration methods...")
        
        # Try right-click context menu
        try:
            await page.click("body", button="right")
            await asyncio.sleep(1)
            await self.take_screenshot(page, "08_context_menu", 
                                     "Right-click context menu")
        except:
            pass
            
        # Try keyboard shortcuts
        try:
            await page.keyboard.press("Control+Shift+M")  # Common MCP shortcut
            await asyncio.sleep(1)
        except:
            pass
            
        # Look for any buttons or links with MCP-related text
        all_buttons = await page.locator("button, a, [role='button']").all()
        for button in all_buttons:
            try:
                text = await button.text_content()
                if text and any(keyword in text.lower() for keyword in ["mcp", "server", "config", "connect"]):
                    print(f"🔍 Found potential MCP element: {text}")
            except:
                pass
                
    async def run_test(self):
        """Run the complete Agent Builder MCP test"""
        print("🚀 Starting Agent Builder MCP Integration Test")
        print(f"Target URL: {self.test_config['url']}")
        print(f"Target Label: {self.test_config['label']}")
        print("=" * 60)
        
        async with async_playwright() as playwright:
            # Launch Chrome browser (not Chromium)
            browser = await playwright.chromium.launch(
                headless=False,  # Show browser for debugging
                channel="chrome",  # Use Chrome specifically
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-web-security",
                    "--allow-running-insecure-content"
                ]
            )
            
            # Create context with proper user agent
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            try:
                # Step 1: Navigate to Agent Builder
                if await self.test_agent_builder_navigation(page):
                    # Step 2: Configure MCP node
                    await self.test_mcp_configuration(page)
                    
                # Keep browser open for manual inspection
                print("\n⏳ Test complete. Browser will stay open for 30 seconds for manual inspection...")
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                await self.take_screenshot(page, "test_failure", f"Test failure: {e}")
                
            finally:
                await browser.close()
                
        print(f"\n📁 Screenshots saved to: {self.screenshots_dir}")
        print("🏁 Agent Builder MCP Integration Test Complete")

if __name__ == "__main__":
    test = AgentBuilderMCPTest()
    asyncio.run(test.run_test())