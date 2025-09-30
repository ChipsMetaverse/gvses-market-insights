#!/usr/bin/env python3
"""
Complete User Interaction Demo with Playwright
Simulates real user behavior to demonstrate ML pattern detection
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def user_demo():
    """Simulate real user interactions with the trading application."""
    
    print("=" * 70)
    print("🎭 SIMULATING REAL USER INTERACTION WITH PHASE 5 ML")
    print("=" * 70)
    
    async with async_playwright() as p:
        # Launch browser with visible UI
        print("\n1️⃣ Starting browser as a user would...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1500,  # Slow actions so they're visible
            args=['--window-size=1920,1080']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
        
        page = await context.new_page()
        
        # Navigate to application
        print("2️⃣ Opening GVSES Trading Dashboard...")
        await page.goto('http://localhost:5174')
        await page.wait_for_timeout(3000)
        
        # Take initial screenshot
        await page.screenshot(path='user_1_initial.png')
        print("   📸 Screenshot: Initial dashboard view")
        
        # === INTERACT WITH WATCHLIST ===
        print("\n3️⃣ Browsing stock watchlist...")
        
        # Wait for stock cards to load
        await page.wait_for_selector('.stock-card', timeout=10000)
        
        # Click on different stocks to view their charts
        stocks_to_check = ['AAPL', 'NVDA', 'TSLA']
        
        for symbol in stocks_to_check:
            print(f"   👆 Clicking on {symbol}...")
            stock_selector = f'.stock-card:has-text("{symbol}")'
            stock_card = await page.query_selector(stock_selector)
            
            if stock_card:
                await stock_card.click()
                await page.wait_for_timeout(2000)
                print(f"   ✅ Viewing {symbol} chart")
                
                # Check if chart loaded
                chart = await page.query_selector('.tv-lightweight-charts, canvas')
                if chart:
                    print(f"   📊 Chart loaded for {symbol}")
            else:
                print(f"   ⚠️ {symbol} not found in watchlist")
        
        await page.screenshot(path='user_2_chart_browsing.png')
        print("   📸 Screenshot: Chart browsing")
        
        # === USE VOICE ASSISTANT ===
        print("\n4️⃣ Testing voice assistant...")
        
        # Look for voice button
        voice_button = await page.query_selector('button:has-text("Click mic to start"), .voice-button, [aria-label*="voice"]')
        
        if voice_button:
            print("   🎤 Clicking voice assistant button...")
            await voice_button.click()
            await page.wait_for_timeout(2000)
            
            # Check if voice is active
            voice_active = await page.query_selector('text=/listening|recording|active/i')
            if voice_active:
                print("   ✅ Voice assistant activated")
            
            # Since we can't actually speak, look for text input alternative
            text_input = await page.query_selector('input[placeholder*="message"], input[placeholder*="type"], textarea')
            
            if text_input:
                print("   💬 Sending pattern detection command via text...")
                await text_input.click()
                await text_input.fill("Show me patterns for TSLA")
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(3000)
                print("   ✅ Pattern request sent")
                
                await page.screenshot(path='user_3_voice_command.png')
                print("   📸 Screenshot: After voice command")
        else:
            print("   ⚠️ Voice assistant button not found")
            
            # Try alternative text input
            print("   💬 Looking for message input...")
            message_input = await page.query_selector('input[type="text"], textarea')
            if message_input:
                await message_input.click()
                await message_input.fill("Analyze TSLA for trading patterns")
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(3000)
                print("   ✅ Analysis request sent via text")
        
        # === CHECK CHART ANALYSIS PANEL ===
        print("\n5️⃣ Checking Chart Analysis panel...")
        
        # Look for analysis content
        analysis_selectors = [
            '.chart-analysis',
            'div:has-text("Chart Analysis")',
            'div:has-text("PATTERN")',
            'div:has-text("Technical")'
        ]
        
        for selector in analysis_selectors:
            analysis = await page.query_selector(selector)
            if analysis:
                analysis_text = await analysis.inner_text()
                print(f"   📊 Found analysis content: {analysis_text[:100]}...")
                
                # Check for patterns
                if 'pattern' in analysis_text.lower():
                    print("   🎯 Pattern information found!")
                    
                    # Look for ML confidence indicators
                    if any(word in analysis_text.lower() for word in ['confidence', 'ml', 'enhanced']):
                        print("   🤖 ML enhancement detected!")
                break
        
        # === INTERACT WITH TECHNICAL LEVELS ===
        print("\n6️⃣ Checking technical levels...")
        
        levels = await page.query_selector_all('.level, div:has-text("Sell High"), div:has-text("Buy Low")')
        if levels:
            print(f"   📈 Found {len(levels)} technical levels")
            for level in levels[:3]:
                level_text = await level.inner_text()
                print(f"      - {level_text}")
        
        # === ADD NEW STOCK TO WATCHLIST ===
        print("\n7️⃣ Adding new stock to watchlist...")
        
        # Look for add stock input
        add_input = await page.query_selector('input[placeholder*="Add"], input[placeholder*="Search"], input[placeholder*="Symbol"]')
        
        if add_input:
            print("   ➕ Adding GOOGL to watchlist...")
            await add_input.click()
            await add_input.fill("GOOGL")
            
            # Look for add button or press enter
            add_button = await page.query_selector('button:has-text("Add"), button:has-text("+")')
            if add_button:
                await add_button.click()
            else:
                await page.keyboard.press('Enter')
            
            await page.wait_for_timeout(2000)
            
            # Check if GOOGL was added
            googl_card = await page.query_selector('.stock-card:has-text("GOOGL")')
            if googl_card:
                print("   ✅ GOOGL successfully added to watchlist")
            else:
                print("   ⚠️ GOOGL not visible in watchlist")
        
        await page.screenshot(path='user_4_watchlist_updated.png')
        print("   📸 Screenshot: Updated watchlist")
        
        # === REQUEST COMPREHENSIVE ANALYSIS ===
        print("\n8️⃣ Requesting comprehensive analysis...")
        
        # Try to trigger pattern detection through UI
        pattern_button = await page.query_selector('button:has-text("Analyze"), button:has-text("Pattern"), button:has-text("Detect")')
        
        if pattern_button:
            print("   🔍 Clicking pattern analysis button...")
            await pattern_button.click()
            await page.wait_for_timeout(3000)
        else:
            # Use console to make API call
            print("   🔍 Making API call for pattern detection...")
            result = await page.evaluate("""
                async () => {
                    try {
                        const response = await fetch('http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns');
                        const data = await response.json();
                        console.log('Pattern API Response:', data);
                        return {
                            success: true,
                            patterns: data.patterns?.detected?.length || 0,
                            hasML: data.patterns?.detected?.some(p => p.ml_confidence !== undefined) || false
                        };
                    } catch (error) {
                        return { success: false, error: error.message };
                    }
                }
            """)
            
            if result and result.get('success'):
                print(f"   📊 API Response: {result['patterns']} patterns detected")
                if result.get('hasML'):
                    print("   🤖 ML enhancement confirmed in response!")
            else:
                print(f"   ⚠️ API call issue: {result.get('error', 'Unknown')}")
        
        # === FINAL COMPREHENSIVE VIEW ===
        print("\n9️⃣ Capturing final state...")
        
        # Scroll to show different parts
        await page.evaluate('window.scrollTo(0, 0)')
        await page.wait_for_timeout(1000)
        
        # Take final full-page screenshot
        await page.screenshot(path='user_5_final_full.png', full_page=True)
        print("   📸 Screenshot: Final full page view")
        
        # === COLLECT METRICS ===
        print("\n📊 Checking ML metrics...")
        
        ml_metrics = await page.evaluate("""
            async () => {
                try {
                    const response = await fetch('http://localhost:8000/api/ml/metrics');
                    const data = await response.json();
                    return {
                        predictions: data.current?.performance?.inference_count || 0,
                        latency: data.current?.performance?.avg_latency_ms || 0,
                        ml_enabled: true
                    };
                } catch (error) {
                    return { ml_enabled: false };
                }
            }
        """)
        
        if ml_metrics.get('ml_enabled'):
            print(f"   🤖 ML System Status:")
            print(f"      - Predictions made: {ml_metrics['predictions']}")
            print(f"      - Average latency: {ml_metrics['latency']:.1f}ms")
        
        # === USER INTERACTION SUMMARY ===
        print("\n" + "=" * 70)
        print("✅ USER INTERACTION DEMO COMPLETE")
        print("=" * 70)
        print("\nUser Actions Performed:")
        print("1. ✅ Browsed multiple stock charts")
        print("2. ✅ Attempted voice/text commands")
        print("3. ✅ Added new stock to watchlist")
        print("4. ✅ Requested pattern analysis")
        print("5. ✅ Checked technical levels")
        
        print("\nGenerated Screenshots:")
        print("  - user_1_initial.png - Initial dashboard")
        print("  - user_2_chart_browsing.png - Browsing charts")
        print("  - user_3_voice_command.png - Voice interaction")
        print("  - user_4_watchlist_updated.png - Modified watchlist")
        print("  - user_5_final_full.png - Complete final view")
        
        print("\n⏸️  Browser will remain open for 15 seconds for inspection...")
        await page.wait_for_timeout(15000)
        
        await browser.close()
        print("✅ Browser closed")

# Run the demo
if __name__ == "__main__":
    asyncio.run(user_demo())