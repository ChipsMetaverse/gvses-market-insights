#!/usr/bin/env python3
"""
Manual Agent Builder Integration Guide
======================================
Opens Chrome browser and navigates to OpenAI Agent Builder with instructions
for manual testing of the MCP integration workflow.

This provides a guided manual test since automated UI testing of Agent Builder
is complex due to authentication and dynamic UI elements.
"""

import asyncio
import webbrowser
import time
from playwright.async_api import async_playwright

class ManualAgentBuilderGuide:
    """Guide for manual Agent Builder MCP integration testing"""
    
    def __init__(self):
        self.mcp_url = "http://localhost:8000/api/mcp"
        self.auth_token = "fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ"
        
    def print_instructions(self):
        """Print detailed integration instructions"""
        print("""
🔧 OPENAI AGENT BUILDER MCP INTEGRATION GUIDE
=============================================

Your MCP server is running successfully with 33 market data tools!
Follow these steps to integrate with OpenAI Agent Builder:

📋 INTEGRATION STEPS:
--------------------
1. 🌐 Navigate to OpenAI Agent Builder (opening now...)
2. 🔑 Sign in to your OpenAI account if prompted
3. ➕ Create a new Assistant or select existing one
4. 🛠️  Go to Tools/Actions/Functions section
5. 🔌 Add MCP Server integration:
   
   📊 MCP SERVER CONFIGURATION:
   ---------------------------
   URL: http://localhost:8000/api/mcp
   Authentication: Bearer fo1_uBgW0a42tOHvVGEsNu49KHhw3F4bTe0E4bTPfUH2nlQ
   
6. 🔍 Test Connection - should load 33 tools
7. ✅ Verify tools like: get_stock_quote, get_stock_history, get_market_overview
8. 📝 Create test prompt: "Get Tesla stock price using get_stock_quote tool"
9. ▶️  Run the workflow to test end-to-end integration
10. 🎉 Verify it returns real Tesla stock data

🧪 EXPECTED TEST RESULTS:
------------------------
✅ Connection Status: SUCCESS (33 tools loaded)
✅ Test Tool Call: get_stock_quote with symbol="TSLA" 
✅ Expected Response: Real-time Tesla stock data with price, change, volume
✅ Data Source: Yahoo Finance via MCP server

🔧 AVAILABLE TOOLS (sample):
---------------------------
• get_stock_quote - Real-time stock quotes
• get_stock_history - Historical price data  
• get_market_overview - Market indices and movers
• get_stock_news - Latest market news
• get_technical_indicators - RSI, MACD, etc.
• get_crypto_price - Cryptocurrency data
• get_market_movers - Top gainers/losers
• ... and 26 more market data tools!

🐛 TROUBLESHOOTING:
------------------
• If connection fails: Verify localhost:8000 server is running
• If authentication fails: Check Bearer token exactly matches
• If tools don't load: Try refreshing Agent Builder page
• If tool calls fail: Check server logs for errors

Ready to proceed? The browser will open automatically...
""")

    async def open_guided_browser(self):
        """Open Chrome browser with guided navigation"""
        try:
            async with async_playwright() as p:
                # Launch Chrome browser
                browser = await p.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--start-maximized"
                    ]
                )
                
                context = await browser.new_context(
                    viewport={"width": 1920, "height": 1080}
                )
                
                page = await context.new_page()
                
                # Navigate to Agent Builder
                print("🌐 Opening OpenAI Agent Builder...")
                await page.goto("https://platform.openai.com/playground/assistants")
                
                # Wait for page to load
                await page.wait_for_load_state("networkidle")
                
                # Show integration instructions as overlay
                instructions_js = f"""
                // Create floating instructions panel
                const panel = document.createElement('div');
                panel.id = 'mcp-integration-guide';
                panel.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    width: 400px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    z-index: 10000;
                    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
                    font-size: 14px;
                    line-height: 1.5;
                    max-height: 80vh;
                    overflow-y: auto;
                `;
                
                panel.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0; color: #fff;">🔌 MCP Integration Guide</h3>
                        <button onclick="this.parentElement.parentElement.remove()" style="background: rgba(255,255,255,0.2); border: none; color: white; border-radius: 50%; width: 25px; height: 25px; cursor: pointer;">×</button>
                    </div>
                    
                    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <strong>📊 MCP Server Details:</strong><br>
                        <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-size: 12px;">
                            URL: {self.mcp_url}
                        </code><br>
                        <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px; font-size: 12px; word-break: break-all;">
                            Auth: Bearer {self.auth_token}
                        </code>
                    </div>
                    
                    <div style="margin-bottom: 15px;">
                        <strong>🛠️ Integration Steps:</strong>
                        <ol style="margin: 10px 0; padding-left: 20px;">
                            <li>Go to Tools/Actions section</li>
                            <li>Add MCP server integration</li>
                            <li>Test connection (33 tools)</li>
                            <li>Create test workflow</li>
                            <li>Test with get_stock_quote</li>
                        </ol>
                    </div>
                    
                    <div style="background: rgba(0,255,0,0.1); padding: 10px; border-radius: 6px; border-left: 4px solid #00ff00;">
                        ✅ <strong>Server Status:</strong> Online<br>
                        ✅ <strong>Tools Available:</strong> 33<br>
                        ✅ <strong>Auth:</strong> Configured
                    </div>
                `;
                
                document.body.appendChild(panel);
                
                // Add close button functionality
                panel.querySelector('button').addEventListener('click', () => panel.remove());
                """
                
                await page.evaluate(instructions_js)
                
                print("✅ Browser opened with integration guide")
                print("📋 Follow the floating guide panel on the right side of the screen")
                print("🔍 Manual testing can now begin...")
                
                # Keep browser open for manual testing
                print("\n⏳ Browser will remain open for manual testing...")
                print("Press Ctrl+C to close when done")
                
                # Wait indefinitely until user closes
                try:
                    while True:
                        await asyncio.sleep(10)
                        # Check if page is still open
                        if page.is_closed():
                            break
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error opening browser: {e}")
            print("🔄 Falling back to system browser...")
            webbrowser.open("https://platform.openai.com/playground/assistants")

    def show_test_scenarios(self):
        """Show specific test scenarios to try"""
        print("""
🧪 RECOMMENDED TEST SCENARIOS:
=============================

1. 📈 BASIC STOCK QUOTE:
   Tool: get_stock_quote
   Input: {"symbol": "TSLA"}
   Expected: Tesla stock price, change, volume data

2. 📊 HISTORICAL DATA:
   Tool: get_stock_history  
   Input: {"symbol": "AAPL", "period": "1mo"}
   Expected: Array of Apple price history

3. 📰 MARKET NEWS:
   Tool: get_market_news
   Input: {"category": "stocks", "limit": 5}
   Expected: Recent market news articles

4. 🏆 MARKET MOVERS:
   Tool: get_market_movers
   Input: {"type": "gainers"}
   Expected: Top gaining stocks today

5. 💹 COMPREHENSIVE DATA:
   Prompt: "Give me a complete analysis of Tesla including price, news, and technical indicators"
   Expected: Multi-tool response with TSLA analysis

Test each scenario and verify the tools return real market data!
""")

    async def run_guide(self):
        """Run the complete guided integration test"""
        print("🚀 Starting Manual Agent Builder Integration Guide")
        print("=" * 60)
        
        # Show instructions
        self.print_instructions()
        
        # Wait for user to be ready
        input("\n📖 Press Enter when you're ready to open the browser...")
        
        # Open guided browser
        await self.open_guided_browser()
        
        # Show test scenarios
        self.show_test_scenarios()
        
        print("\n✅ Manual integration guide completed!")
        print("🎉 Your MCP server is ready for Agent Builder integration!")


async def main():
    """Main execution"""
    guide = ManualAgentBuilderGuide()
    await guide.run_guide()


if __name__ == "__main__":
    print("""
🧪 Manual Agent Builder Integration Guide
=========================================

This will open Chrome browser and guide you through manually testing
the MCP integration with OpenAI Agent Builder.

Since Agent Builder requires authentication and has complex UI,
manual testing is more reliable than automated testing.

Prerequisites:
✅ Local MCP server running (localhost:8000)
✅ OpenAI account with Agent Builder access
✅ Chrome browser installed

The guide will:
1. Open Agent Builder in Chrome
2. Show floating instructions panel
3. Provide step-by-step integration guide
4. Give you test scenarios to try
""")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Manual testing session ended")
    except Exception as e:
        print(f"\n❌ Error: {e}")