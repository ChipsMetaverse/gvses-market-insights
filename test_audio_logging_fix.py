#!/usr/bin/env python3

import asyncio
import json
from playwright.async_api import async_playwright
import time

async def test_audio_logging_fix():
    """
    Test the audio API logging fix to verify correct API detection and reporting
    """
    async with async_playwright() as p:
        # Launch browser with console access
        browser = await p.chromium.launch(headless=False, args=['--use-fake-ui-for-media-stream'])
        
        # Create context with microphone permissions
        context = await browser.new_context(
            permissions=['microphone'],
            viewport={'width': 1400, 'height': 900}
        )
        
        page = await context.new_page()
        
        # Collect console messages
        console_messages = []
        audio_processor_messages = []
        
        def handle_console(msg):
            console_messages.append({
                'type': msg.type,
                'text': msg.text,
                'timestamp': time.time()
            })
            # Filter for audio processor specific messages
            if '🔬 [AUDIO PROCESSOR]' in msg.text:
                audio_processor_messages.append({
                    'type': msg.type,
                    'text': msg.text,
                    'timestamp': time.time()
                })
                print(f"📱 AUDIO LOG: {msg.text}")
        
        page.on('console', handle_console)
        
        print("🔍 Navigating to localhost:5174...")
        await page.goto('http://localhost:5174/')
        
        # Wait for page to load
        await page.wait_for_timeout(2000)
        
        print("🎙️ Looking for voice interface elements...")
        
        # Check if voice interface is visible
        voice_button_selector = '[data-testid="voice-button"], button[aria-label*="voice"], button:has-text("🎙️"), button:has-text("Start"), .voice-button'
        
        try:
            # Wait for any voice-related button to appear
            await page.wait_for_selector('button', timeout=5000)
            
            # Look for voice buttons
            buttons = await page.query_selector_all('button')
            voice_button = None
            
            for button in buttons:
                text = await button.inner_text()
                aria_label = await button.get_attribute('aria-label')
                class_name = await button.get_attribute('class')
                
                if any(keyword in str(item).lower() for item in [text, aria_label, class_name] for keyword in ['voice', 'mic', '🎙️', 'start']):
                    voice_button = button
                    button_text = text or aria_label or 'Voice Button'
                    print(f"🎙️ Found voice button: {button_text}")
                    break
            
            if voice_button:
                print("🔄 Clicking voice button to trigger audio initialization...")
                await voice_button.click()
                
                # Wait for audio initialization
                await page.wait_for_timeout(3000)
                
            else:
                print("⚠️ No voice button found, but checking for audio processor logs anyway...")
                
        except Exception as e:
            print(f"⚠️ Voice button interaction failed: {e}")
        
        # Wait a bit more for any delayed audio processing
        await page.wait_for_timeout(2000)
        
        # Take screenshot with console visible
        print("📸 Taking screenshot with console visible...")
        
        # Open dev tools to show console
        await page.keyboard.press('F12')
        await page.wait_for_timeout(1000)
        
        # Click on Console tab if it exists
        try:
            console_tab = await page.query_selector('text=Console')
            if console_tab:
                await console_tab.click()
                await page.wait_for_timeout(500)
        except:
            pass
        
        # Take screenshot
        screenshot_path = "/Volumes/WD My Passport 264F Media/claude-voice-mcp/audio_logging_verification.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot saved: {screenshot_path}")
        
        # Analysis
        print("\n" + "="*80)
        print("📊 AUDIO API LOGGING ANALYSIS")
        print("="*80)
        
        if audio_processor_messages:
            print(f"✅ Found {len(audio_processor_messages)} audio processor log messages:")
            
            worklet_attempt = False
            worklet_success = False
            script_processor_fallback = False
            final_api_used = None
            
            for msg in audio_processor_messages:
                print(f"  📝 {msg['text']}")
                
                # Analyze message content
                text = msg['text']
                if 'Attempting modern AudioWorkletNode' in text:
                    worklet_attempt = True
                elif 'AudioWorkletNode created successfully' in text:
                    worklet_success = True
                elif 'ScriptProcessorNode' in text and 'fallback' in text.lower():
                    script_processor_fallback = True
                elif 'Audio processor initialized' in text:
                    if 'AudioWorkletNode' in text:
                        final_api_used = 'AudioWorkletNode'
                    elif 'ScriptProcessorNode' in text:
                        final_api_used = 'ScriptProcessorNode'
            
            print(f"\n📈 ANALYSIS RESULTS:")
            print(f"  🔬 Modern API Attempt: {'✅ Yes' if worklet_attempt else '❌ No'}")
            print(f"  🎯 AudioWorkletNode Success: {'✅ Yes' if worklet_success else '❌ No'}")
            print(f"  🔄 ScriptProcessorNode Fallback: {'✅ Yes' if script_processor_fallback else '❌ No'}")
            print(f"  🎵 Final API Used: {final_api_used or '❓ Not detected'}")
            
            # Verify logging accuracy
            if final_api_used:
                print(f"\n✅ LOGGING FIX VERIFICATION:")
                if worklet_attempt and worklet_success and final_api_used == 'AudioWorkletNode':
                    print("  ✅ Modern AudioWorkletNode successfully used and correctly logged")
                elif worklet_attempt and not worklet_success and final_api_used == 'ScriptProcessorNode':
                    print("  ✅ Fallback to ScriptProcessorNode correctly detected and logged")
                elif final_api_used == 'ScriptProcessorNode' and not worklet_attempt:
                    print("  ✅ Direct ScriptProcessorNode usage correctly logged")
                else:
                    print("  ⚠️ Logging might not be fully consistent - check individual messages")
            else:
                print(f"\n⚠️ WARNING: Could not determine final API used from logs")
        
        else:
            print("❌ No audio processor log messages found!")
            print("   This could indicate:")
            print("   - Audio initialization was not triggered")
            print("   - Voice button was not found/clicked")
            print("   - Logging is not working")
        
        # Show all console messages for debugging
        print(f"\n🔍 ALL CONSOLE MESSAGES ({len(console_messages)} total):")
        for msg in console_messages:
            if msg['text'].strip():
                print(f"  [{msg['type'].upper()}] {msg['text']}")
        
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        await browser.close()
        
        return {
            'audio_processor_messages': audio_processor_messages,
            'total_console_messages': len(console_messages),
            'screenshot_path': screenshot_path,
            'final_api_used': final_api_used if 'final_api_used' in locals() else None
        }

if __name__ == "__main__":
    result = asyncio.run(test_audio_logging_fix())
    print(f"\n🎯 Test completed. Results: {result}")