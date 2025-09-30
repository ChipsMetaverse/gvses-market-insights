#!/usr/bin/env python3
"""
Quick test for voice assistant connection
"""

import asyncio
from playwright.async_api import async_playwright

async def test_voice_connection():
    """Test voice assistant connection flow"""
    print("🚀 Testing Voice Assistant Connection\n")
    print("=" * 60)
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(viewport={'width': 1280, 'height': 800})
    page = await context.new_page()
    
    try:
        # Navigate to the app
        print("1️⃣ Loading application...")
        await page.goto("http://localhost:5174", wait_until='networkidle')
        await page.wait_for_timeout(2000)
        
        # Take initial screenshot
        await page.screenshot(path="test_voice_1_initial.png")
        print("📸 Initial screenshot saved")
        
        # Find the voice button
        print("\n2️⃣ Looking for voice button...")
        voice_button = await page.query_selector('[data-testid="voice-fab"]')
        if not voice_button:
            voice_button = await page.query_selector('.voice-fab')
        
        if voice_button:
            print("✅ Found voice button")
            
            # Click to connect
            print("\n3️⃣ Clicking voice button to connect...")
            await voice_button.click()
            
            # Wait for connection (button gets 'active' class)
            try:
                await page.wait_for_selector('.voice-fab.active', timeout=10000)
                print("✅ Voice assistant connected!")
                await page.screenshot(path="test_voice_2_connected.png")
            except:
                print("❌ Voice assistant failed to connect")
                await page.screenshot(path="test_voice_2_failed.png")
                
            # Check if input is now active
            print("\n4️⃣ Checking input field...")
            input_field = await page.query_selector('.voice-text-input')
            if input_field:
                is_disabled = await input_field.evaluate('el => el.disabled')
                placeholder = await input_field.evaluate('el => el.placeholder')
                print(f"  Input found - Disabled: {is_disabled}, Placeholder: '{placeholder}'")
                
                if not is_disabled:
                    print("\n5️⃣ Sending test message...")
                    await input_field.click()
                    await input_field.type("What is AAPL trading at?")
                    await page.keyboard.press("Enter")
                    
                    # Wait for response
                    await page.wait_for_timeout(5000)
                    await page.screenshot(path="test_voice_3_message_sent.png")
                    print("✅ Message sent")
                    
                    # Check for response
                    messages = await page.query_selector_all('.conversation-message-enhanced')
                    print(f"  Found {len(messages)} messages in conversation")
                    
                    # Check message contents
                    for i, msg in enumerate(messages):
                        text = await msg.text_content()
                        role = "user" if "👤" in text else "assistant" if "🤖" in text else "unknown"
                        print(f"    Message {i+1} ({role}): {text[:100]}...")
                else:
                    print("❌ Input field is disabled")
            else:
                print("❌ Input field not found")
        else:
            print("❌ Voice button not found")
            
        print("\n" + "=" * 60)
        print("Test complete. Check screenshots for visual results.")
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(test_voice_connection())