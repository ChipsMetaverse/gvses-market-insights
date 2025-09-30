#!/usr/bin/env python3
"""
Final Playwright Demo - Robust user interaction simulation
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def demo_user_interaction():
    """Demonstrate user interaction with the trading app."""
    
    print("=" * 60)
    print("🎭 PLAYWRIGHT USER INTERACTION DEMONSTRATION")
    print("=" * 60)
    
    async with async_playwright() as p:
        # Launch browser visibly
        print("\n1️⃣ Starting browser...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=2000  # Slow down for visibility
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to app
        print("2️⃣ Opening GVSES Trading Dashboard...")
        await page.goto('http://localhost:5174')
        await page.wait_for_timeout(5000)
        
        # Screenshot 1: Initial state
        await page.screenshot(path='demo_1_initial.png')
        print("   📸 Captured initial dashboard")
        
        # Look for stock cards in Market Insights
        print("\n3️⃣ Exploring Market Insights panel...")
        
        # Try clicking on a stock card (more specific selector)
        stock_cards = await page.query_selector_all('.stock-card')
        if stock_cards:
            print(f"   Found {len(stock_cards)} stock cards")
            # Try to click the first stock card
            try:
                # Use force click to bypass intercepting elements
                await stock_cards[0].click(force=True)
                print("   ✅ Clicked on first stock card")
                await page.wait_for_timeout(3000)
            except:
                print("   ⚠️ Could not click stock card, continuing...")
        
        await page.screenshot(path='demo_2_stock_selected.png')
        print("   📸 Captured after stock selection")
        
        # Try text input for pattern request
        print("\n4️⃣ Looking for message input...")
        
        # Look for any text input field
        inputs = await page.query_selector_all('input[type="text"], textarea')
        if inputs:
            print(f"   Found {len(inputs)} input fields")
            for i, input_field in enumerate(inputs):
                try:
                    placeholder = await input_field.get_attribute('placeholder')
                    if placeholder:
                        print(f"   Input {i+1}: {placeholder}")
                        
                        # Try the message input
                        if 'message' in placeholder.lower() or 'type' in placeholder.lower():
                            print("   💬 Typing pattern analysis request...")
                            await input_field.click(force=True)
                            await input_field.fill("analyze TSLA patterns")
                            await page.keyboard.press('Enter')
                            await page.wait_for_timeout(5000)
                            
                            await page.screenshot(path='demo_3_pattern_request.png')
                            print("   📸 Captured after pattern request")
                            break
                except Exception as e:
                    continue
        
        # Make direct API call to verify ML system
        print("\n5️⃣ Checking ML system via API...")
        
        try:
            ml_result = await page.evaluate("""
                async () => {
                    try {
                        // Check ML health
                        const health = await fetch('http://localhost:8000/api/ml/health').then(r => r.json());
                        
                        // Get pattern data
                        const patterns = await fetch('http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns').then(r => r.json());
                        
                        return {
                            ml_enabled: health.phase5_enabled,
                            model_loaded: health.model_loaded,
                            patterns_detected: patterns.patterns?.detected?.length || 0,
                            has_ml_confidence: patterns.patterns?.detected?.some(p => p.ml_confidence !== undefined) || false
                        };
                    } catch (error) {
                        return { error: error.message };
                    }
                }
            """)
            
            if ml_result and not ml_result.get('error'):
                print("   🤖 ML System Status:")
                print(f"      Phase 5 Enabled: {ml_result.get('ml_enabled', False)}")
                print(f"      Model Loaded: {ml_result.get('model_loaded', False)}")
                print(f"      Patterns Detected: {ml_result.get('patterns_detected', 0)}")
                print(f"      Has ML Confidence: {ml_result.get('has_ml_confidence', False)}")
            else:
                print(f"   ⚠️ API check error: {ml_result.get('error', 'Unknown')}")
        except Exception as e:
            print(f"   ⚠️ Could not check ML system: {e}")
        
        # Check chart analysis panel
        print("\n6️⃣ Checking Chart Analysis panel...")
        
        # Look for technical levels
        levels = await page.query_selector_all('text=/Sell High|Buy Low|BTD/')
        if levels:
            print(f"   📊 Found {len(levels)} technical levels")
            for level in levels[:3]:
                try:
                    text = await level.inner_text()
                    print(f"      - {text}")
                except:
                    continue
        
        # Look for pattern detection status
        pattern_status = await page.query_selector('text=/No patterns detected|Pattern detected|PATTERN/')
        if pattern_status:
            status_text = await pattern_status.inner_text()
            print(f"   📈 Pattern Status: {status_text}")
        
        # Final full-page screenshot
        print("\n7️⃣ Capturing final state...")
        await page.screenshot(path='demo_4_final_full.png', full_page=True)
        print("   📸 Captured full page view")
        
        # Get ML metrics one more time
        print("\n8️⃣ Final ML metrics check...")
        
        try:
            metrics_result = await page.evaluate("""
                async () => {
                    const response = await fetch('http://localhost:8000/api/ml/metrics');
                    const data = await response.json();
                    return {
                        predictions: data.current?.performance?.inference_count || 0,
                        latency: data.current?.performance?.avg_latency_ms || 0
                    };
                }
            """)
            
            if metrics_result:
                print(f"   📊 ML Metrics:")
                print(f"      Predictions Made: {metrics_result['predictions']}")
                print(f"      Average Latency: {metrics_result['latency']:.1f}ms")
        except:
            print("   ⚠️ Could not fetch ML metrics")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ USER INTERACTION DEMONSTRATION COMPLETE")
        print("=" * 60)
        print("\nGenerated Screenshots:")
        print("  📸 demo_1_initial.png - Initial dashboard state")
        print("  📸 demo_2_stock_selected.png - After stock selection")
        print("  📸 demo_3_pattern_request.png - After pattern request")
        print("  📸 demo_4_final_full.png - Final full page view")
        
        print("\n⏸️  Browser will remain open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()
        print("✅ Browser closed")

if __name__ == "__main__":
    asyncio.run(demo_user_interaction())