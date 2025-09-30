#!/usr/bin/env python3
"""Quick Playwright navigation and screenshot demo"""

import asyncio
from playwright.async_api import async_playwright

async def navigate_and_screenshot():
    async with async_playwright() as p:
        # Launch browser with visible UI
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        print("🌐 Opening application...")
        await page.goto('http://localhost:5174', timeout=60000, wait_until='domcontentloaded')
        
        # Wait for initial load
        await page.wait_for_timeout(5000)
        
        # Screenshot 1: Initial dashboard
        await page.screenshot(path='1_dashboard.png')
        print("📸 Screenshot 1: Dashboard saved")
        
        # Click on TSLA stock card
        print("🖱️ Clicking on TSLA...")
        tsla = await page.query_selector('text=TSLA')
        if tsla:
            await tsla.click()
            await page.wait_for_timeout(3000)
            await page.screenshot(path='2_tsla_selected.png')
            print("📸 Screenshot 2: TSLA selected")
        
        # Look for voice button and click it
        print("🎤 Looking for voice assistant...")
        voice_btn = await page.query_selector('button:has-text("Voice"), button:has-text("Start")')
        if voice_btn:
            await voice_btn.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='3_voice_activated.png')
            print("📸 Screenshot 3: Voice activated")
        
        # Check chart analysis panel
        print("📊 Checking chart analysis...")
        analysis = await page.query_selector('text=Chart Analysis')
        if analysis:
            await analysis.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path='4_chart_analysis.png')
            print("📸 Screenshot 4: Chart analysis")
        
        # Full page screenshot
        await page.screenshot(path='5_full_page.png', full_page=True)
        print("📸 Screenshot 5: Full page")
        
        print("\n✅ Navigation complete! Browser will close in 10 seconds...")
        print("   Check these screenshots:")
        print("   - 1_dashboard.png")
        print("   - 2_tsla_selected.png") 
        print("   - 3_voice_activated.png")
        print("   - 4_chart_analysis.png")
        print("   - 5_full_page.png")
        
        await page.wait_for_timeout(10000)
        await browser.close()

asyncio.run(navigate_and_screenshot())