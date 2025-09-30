#!/usr/bin/env python3
"""
Playwright Demo - Frontend-Backend Interaction with ML Pattern Detection
Demonstrates Phase 5 ML system by automating user interactions
"""

import asyncio
import json
from playwright.async_api import async_playwright
import time

async def demonstrate_ml_pattern_detection():
    """Demonstrate the complete flow of ML pattern detection using Playwright."""
    
    print("=" * 60)
    print("🎭 PLAYWRIGHT DEMONSTRATION - PHASE 5 ML PATTERN DETECTION")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser with visible UI
        print("\n1️⃣ Launching browser...")
        browser = await p.chromium.launch(
            headless=False,  # Show browser window
            slow_mo=500  # Slow down actions for visibility
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        
        # Navigate to application
        print("2️⃣ Navigating to application...")
        await page.goto('http://localhost:5174')
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot of initial state
        await page.screenshot(path='demo_1_initial.png')
        print("   📸 Screenshot saved: demo_1_initial.png")
        
        # Wait for market data to load
        print("\n3️⃣ Waiting for market data to load...")
        await page.wait_for_selector('.stock-card', timeout=10000)
        stock_cards = await page.query_selector_all('.stock-card')
        print(f"   ✅ Found {len(stock_cards)} stocks in watchlist")
        
        # Click on TSLA stock card
        print("\n4️⃣ Clicking on TSLA to view chart...")
        tsla_card = await page.query_selector('div.stock-card:has-text("TSLA")')
        if tsla_card:
            await tsla_card.click()
            await page.wait_for_timeout(2000)
            print("   ✅ TSLA chart displayed")
        else:
            # Fallback: click first stock card
            await stock_cards[0].click()
            print("   ✅ First stock chart displayed")
        
        await page.screenshot(path='demo_2_chart.png')
        print("   📸 Screenshot saved: demo_2_chart.png")
        
        # Check if voice assistant is available
        print("\n5️⃣ Checking for voice assistant...")
        voice_button = await page.query_selector('[aria-label*="voice"], button:has-text("Start Voice"), .voice-button')
        
        if voice_button:
            print("   ✅ Voice assistant found")
            
            # Click voice button to activate
            print("\n6️⃣ Activating voice assistant...")
            await voice_button.click()
            await page.wait_for_timeout(1000)
            
            # Simulate voice command by typing in input
            voice_input = await page.query_selector('input[placeholder*="speak"], input[placeholder*="voice"], .voice-input')
            if voice_input:
                print("   📝 Sending pattern detection command...")
                await voice_input.fill("Show me patterns for TSLA")
                await voice_input.press("Enter")
                await page.wait_for_timeout(3000)
                print("   ✅ Pattern detection command sent")
        else:
            print("   ⚠️ Voice assistant not found, trying alternative method...")
            
            # Alternative: Make direct API call
            print("\n6️⃣ Making direct API call for pattern detection...")
            response = await page.evaluate("""
                async () => {
                    const response = await fetch('http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns');
                    return await response.json();
                }
            """)
            
            if response:
                patterns = response.get('patterns', {})
                detected = patterns.get('detected', [])
                print(f"   📊 API Response: {len(detected)} patterns detected")
                if detected:
                    for pattern in detected[:3]:  # Show first 3 patterns
                        print(f"      - {pattern.get('type')}: {pattern.get('confidence')}% confidence")
        
        # Check for Chart Analysis panel updates
        print("\n7️⃣ Checking Chart Analysis panel...")
        analysis_panel = await page.query_selector('.chart-analysis, .analysis-panel, div:has-text("Chart Analysis")')
        if analysis_panel:
            analysis_text = await analysis_panel.inner_text()
            if 'pattern' in analysis_text.lower():
                print("   ✅ Pattern analysis displayed in Chart Analysis panel")
            else:
                print("   ⏳ Chart Analysis panel found but no patterns shown")
        
        await page.screenshot(path='demo_3_patterns.png')
        print("   📸 Screenshot saved: demo_3_patterns.png")
        
        # Monitor network activity for ML endpoints
        print("\n8️⃣ Monitoring ML endpoints...")
        
        # Set up network monitoring
        ml_requests = []
        
        async def log_ml_request(route):
            request = route.request
            if any(endpoint in request.url for endpoint in ['/ml/', 'pattern', 'confidence']):
                ml_requests.append({
                    'url': request.url,
                    'method': request.method
                })
            await route.continue_()
        
        await page.route('**/*', log_ml_request)
        
        # Trigger another pattern check
        print("   🔄 Triggering pattern refresh...")
        refresh_button = await page.query_selector('button:has-text("Refresh"), button:has-text("Update")')
        if refresh_button:
            await refresh_button.click()
            await page.wait_for_timeout(2000)
        
        # Display ML request summary
        if ml_requests:
            print(f"\n   📡 ML-related requests captured:")
            for req in ml_requests:
                print(f"      - {req['method']} {req['url']}")
        else:
            print("   ⚠️ No ML-specific requests captured")
        
        # Final interaction summary
        print("\n9️⃣ Interaction Summary:")
        
        # Get current stock price
        price_element = await page.query_selector('.price, .stock-price, span:has-text("$")')
        if price_element:
            price = await price_element.inner_text()
            print(f"   💵 Current price displayed: {price}")
        
        # Check for any error messages
        error_element = await page.query_selector('.error, .alert-danger')
        if error_element:
            error_text = await error_element.inner_text()
            print(f"   ❌ Error found: {error_text}")
        else:
            print("   ✅ No errors detected")
        
        # Take final screenshot
        await page.screenshot(path='demo_4_final.png', full_page=True)
        print("   📸 Full page screenshot saved: demo_4_final.png")
        
        print("\n🎬 Demo complete! Check screenshots for visual results.")
        print("   - demo_1_initial.png: Initial load")
        print("   - demo_2_chart.png: Chart display")
        print("   - demo_3_patterns.png: Pattern detection")
        print("   - demo_4_final.png: Full page final state")
        
        # Keep browser open for manual inspection
        print("\n⏸️  Browser will close in 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

async def test_ml_health():
    """Quick test to verify ML system health before demo."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Check ML health endpoint
        response = await page.goto('http://localhost:8000/api/ml/health')
        if response and response.ok:
            data = await response.json()
            print("\n📊 ML System Health Check:")
            print(f"   - Status: {data.get('status', 'unknown')}")
            print(f"   - Phase 5 Enabled: {data.get('phase5_enabled', False)}")
            print(f"   - Model Loaded: {data.get('model_loaded', False)}")
            print(f"   - Predictions Made: {data.get('predictions_made', 0)}")
            return data.get('phase5_enabled', False)
        
        await browser.close()
        return False

async def main():
    """Main demo function."""
    print("\n🔍 Pre-flight checks...")
    
    # Verify ML is enabled
    ml_enabled = await test_ml_health()
    if not ml_enabled:
        print("⚠️ Warning: Phase 5 ML is not enabled!")
        print("   Set ENABLE_PHASE5_ML=true in backend/.env")
    else:
        print("✅ Phase 5 ML is enabled and ready!")
    
    # Run the demo
    await demonstrate_ml_pattern_detection()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())