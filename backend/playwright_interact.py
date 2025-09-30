#!/usr/bin/env python3
"""
Interact with the trading app as a user would
"""

import asyncio
from playwright.async_api import async_playwright

async def interact_with_app():
    async with async_playwright() as p:
        print("🎭 PLAYWRIGHT USER INTERACTION DEMO")
        print("=" * 50)
        
        # Launch browser
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=2000  # Slow for visibility
        )
        
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("\n1. Opening application...")
        await page.goto('http://localhost:5174', timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Screenshot initial state
        await page.screenshot(path='interact_1_initial.png')
        print("   📸 Initial dashboard captured")
        
        # Click on TSLA chart
        print("\n2. Clicking on TSLA in chart analysis...")
        tsla_elements = await page.query_selector_all('text=TSLA')
        if tsla_elements:
            print(f"   Found {len(tsla_elements)} TSLA elements")
            # Click the first one
            await tsla_elements[0].click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='interact_2_tsla.png')
            print("   📸 TSLA interaction captured")
        
        # Try to interact with voice assistant
        print("\n3. Looking for voice assistant...")
        voice_area = await page.query_selector('text=Click mic to start')
        if voice_area:
            print("   Found voice assistant prompt")
            # Click near it
            await voice_area.click()
            await page.wait_for_timeout(2000)
            
        # Look for text input
        print("\n4. Looking for text input...")
        inputs = await page.query_selector_all('input[type="text"], textarea')
        if inputs:
            print(f"   Found {len(inputs)} input fields")
            for i, input_field in enumerate(inputs):
                try:
                    # Try the message input
                    placeholder = await input_field.get_attribute('placeholder')
                    print(f"   Input {i+1} placeholder: {placeholder}")
                    
                    if 'message' in (placeholder or '').lower():
                        print("   📝 Typing pattern request...")
                        await input_field.click()
                        await input_field.fill("Show me patterns for TSLA")
                        await page.keyboard.press('Enter')
                        await page.wait_for_timeout(5000)
                        await page.screenshot(path='interact_3_pattern_request.png')
                        print("   📸 Pattern request captured")
                        break
                except:
                    continue
        
        # Check technical levels
        print("\n5. Checking technical levels...")
        levels = ['Sell High', 'Buy Low', 'BTD']
        for level in levels:
            element = await page.query_selector(f'text={level}')
            if element:
                text = await element.inner_text()
                print(f"   ✅ Found: {text}")
        
        # Make direct API call for patterns
        print("\n6. Making direct pattern detection call...")
        result = await page.evaluate("""
            async () => {
                const response = await fetch('http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns');
                const data = await response.json();
                return {
                    symbol: data.symbol,
                    price: data.price_data?.last,
                    patterns: data.patterns?.detected?.length || 0,
                    summary: data.patterns?.summary
                };
            }
        """)
        
        print(f"   API Response:")
        print(f"   - Symbol: {result.get('symbol')}")
        print(f"   - Price: ${result.get('price', 0):.2f}")
        print(f"   - Patterns: {result.get('patterns')}")
        print(f"   - Summary: {result.get('summary')}")
        
        # Check ML metrics
        print("\n7. Checking ML system metrics...")
        ml_status = await page.evaluate("""
            async () => {
                const health = await fetch('http://localhost:8000/api/ml/health').then(r => r.json());
                const metrics = await fetch('http://localhost:8000/api/ml/metrics').then(r => r.json());
                return {
                    ml_enabled: health.phase5_enabled,
                    model_loaded: health.model_loaded,
                    predictions: metrics.current?.performance?.inference_count || 0
                };
            }
        """)
        
        print(f"   🤖 ML Status:")
        print(f"   - Enabled: {ml_status['ml_enabled']}")
        print(f"   - Model Loaded: {ml_status['model_loaded']}")
        print(f"   - Predictions Made: {ml_status['predictions']}")
        
        # Final screenshot
        await page.screenshot(path='interact_4_final.png', full_page=True)
        print("\n📸 Final full page captured")
        
        print("\n" + "=" * 50)
        print("✅ Interaction complete!")
        print("\nScreenshots saved:")
        print("  - interact_1_initial.png")
        print("  - interact_2_tsla.png")
        print("  - interact_3_pattern_request.png")
        print("  - interact_4_final.png")
        
        print("\n⏸️ Browser closing in 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

asyncio.run(interact_with_app())