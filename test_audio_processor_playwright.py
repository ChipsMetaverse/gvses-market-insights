#!/usr/bin/env python3
"""
Test the modernized audio processor using Playwright
"""
import asyncio
from playwright.async_api import async_playwright
import time
import json
from datetime import datetime
import os

async def test_audio_processor():
    async with async_playwright() as p:
        # Launch browser with console logging enabled
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox', 
                '--disable-setuid-sandbox',
                '--use-fake-ui-for-media-stream',  # Allow microphone access without prompt
                '--use-fake-device-for-media-stream'
            ]
        )
        
        context = await browser.new_context(
            permissions=['microphone']  # Grant microphone permission
        )
        page = await context.new_page()
        
        # Collect console logs
        console_logs = []
        def handle_console(msg):
            console_logs.append({
                'timestamp': datetime.now().isoformat(),
                'type': msg.type,
                'text': msg.text,
                'location': str(msg.location) if hasattr(msg, 'location') and msg.location else None
            })
            print(f"[{msg.type.upper()}] {msg.text}")
        
        page.on('console', handle_console)
        
        # Navigate to the application
        print("🌐 Navigating to http://localhost:5174/")
        try:
            await page.goto('http://localhost:5174/', wait_until='networkidle', timeout=30000)
            print("✅ Page loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load page: {e}")
            await browser.close()
            return
        
        # Wait for the application to initialize
        print("⏳ Waiting for application initialization...")
        await page.wait_for_timeout(5000)
        
        # Open Chrome DevTools console
        print("🔧 Opening Chrome DevTools...")
        await page.keyboard.press('F12')
        await page.wait_for_timeout(2000)
        
        # Click on Console tab to ensure it's visible
        try:
            # Try different selectors for console tab
            console_selectors = [
                '[aria-label*="Console"]',
                'text=Console',
                '[title="Console"]',
                '.console-tab'
            ]
            
            for selector in console_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.is_visible(timeout=1000):
                        await element.click()
                        print("📋 Console tab activated")
                        break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ Could not activate console tab: {e}")
        
        await page.wait_for_timeout(1000)
        
        # Look for and interact with voice/audio elements
        print("🔍 Looking for voice interface elements...")
        try:
            # Wait for voice interface to load
            await page.wait_for_selector('button, [role="button"]', timeout=10000)
            
            # Look for common voice interface patterns
            voice_selectors = [
                'button:has-text("Start")',
                'button:has-text("Connect")', 
                'button[aria-label*="microphone"]',
                'button[title*="voice"]',
                '[data-testid*="voice"]',
                '[data-testid*="mic"]',
                'button:has([data-lucide="mic"])',
                'button:has(.mic-icon)'
            ]
            
            voice_button_found = False
            for selector in voice_selectors:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=2000):
                        print(f"🎤 Found voice button with selector: {selector}")
                        await button.click()
                        print("🎤 Clicked voice button to trigger audio initialization...")
                        voice_button_found = True
                        await page.wait_for_timeout(3000)
                        break
                except Exception as e:
                    continue
            
            if not voice_button_found:
                print("⚠️ No specific voice button found, checking all buttons...")
                # Fallback: check all buttons for voice-related text
                buttons = await page.locator('button').all()
                for i, button in enumerate(buttons[:10]):  # Check first 10 buttons
                    try:
                        text = await button.text_content()
                        aria_label = await button.get_attribute('aria-label')
                        title = await button.get_attribute('title')
                        
                        text_content = ' '.join(filter(None, [text, aria_label, title])).lower()
                        
                        if any(keyword in text_content for keyword in ['mic', 'voice', 'audio', 'speak', 'listen', 'start', 'connect']):
                            print(f"🎤 Found potential voice button {i}: {text_content}")
                            await button.click()
                            print("🎤 Clicked button to trigger audio...")
                            await page.wait_for_timeout(3000)
                            break
                    except Exception as e:
                        continue
                        
        except Exception as e:
            print(f"⚠️ Error interacting with voice elements: {e}")
        
        # Wait additional time for audio initialization
        print("⏳ Waiting for audio processor initialization...")
        await page.wait_for_timeout(5000)
        
        # Scroll console to bottom to see latest logs
        try:
            await page.keyboard.press('End')
            await page.wait_for_timeout(1000)
        except:
            pass
        
        # Take screenshot with console visible
        print("📸 Taking screenshot...")
        timestamp = int(time.time())
        screenshot_path = f"audio_processor_test_{timestamp}.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"📸 Screenshot saved as: {screenshot_path}")
        
        # Analyze audio processor logs
        print("\n🔬 ANALYZING AUDIO PROCESSOR LOGS:")
        print("=" * 50)
        
        # Filter for audio-related logs
        audio_keywords = ['audio', 'processor', 'worklet', 'microphone', 'webaudio', 'scriptprocessor', 'audiocontext']
        audio_logs = [
            log for log in console_logs 
            if any(keyword in log['text'].lower() for keyword in audio_keywords)
        ]
        
        modern_api_used = False
        legacy_fallback = False
        errors = []
        success_messages = []
        specific_audio_logs = []
        
        print(f"📋 Total console logs: {len(console_logs)}")
        print(f"🎵 Audio-related logs: {len(audio_logs)}")
        
        for log in console_logs:
            text = log['text']
            
            # Check for specific audio processor messages
            if "🔬 [AUDIO PROCESSOR]" in text:
                specific_audio_logs.append(text)
                print(f"🎯 AUDIO PROCESSOR LOG: {text}")
                
                if "Attempting modern AudioWorkletNode" in text:
                    print("   → Modern AudioWorkletNode initialization attempt detected")
                elif "Using legacy ScriptProcessorNode" in text:
                    print("   → Legacy ScriptProcessorNode fallback detected")
                    legacy_fallback = True
                elif "AudioWorklet successfully" in text or "Modern audio processing initialized" in text:
                    print("   → AudioWorklet success confirmed")
                    modern_api_used = True
                elif "AudioWorklet failed" in text or "Falling back to legacy" in text:
                    print("   → AudioWorklet failed, falling back to legacy")
                    legacy_fallback = True
            
            # Check for WebAudio API related logs
            if any(keyword in text.lower() for keyword in ['audioworklet', 'scriptprocessor', 'audiocontext', 'webaudio']):
                print(f"🎵 WEBAUDIO LOG: {text}")
                if log['type'] == 'error':
                    errors.append(text)
                else:
                    success_messages.append(text)
            
            # Check for audio-related errors
            if log['type'] == 'error':
                if any(keyword in text.lower() for keyword in ['audio', 'processor', 'worklet', 'microphone']):
                    errors.append(text)
                    print(f"❌ AUDIO ERROR: {text}")
        
        # Print all audio logs for debugging
        if audio_logs:
            print("\n🎵 ALL AUDIO-RELATED LOGS:")
            for i, log in enumerate(audio_logs, 1):
                print(f"{i:2d}. [{log['type'].upper()}] {log['text']}")
        
        print("\n📊 ANALYSIS SUMMARY:")
        print("=" * 30)
        
        if modern_api_used:
            print("✅ Modern AudioWorkletNode is being used")
        elif legacy_fallback:
            print("⚠️ Fell back to legacy ScriptProcessorNode")
        elif specific_audio_logs:
            print("❓ Audio processor logs found but status unclear")
        else:
            print("❓ Could not determine which audio API is being used")
            print("   (No specific audio processor logs detected)")
        
        if specific_audio_logs:
            print(f"📋 Found {len(specific_audio_logs)} specific audio processor log entries")
        
        if errors:
            print(f"❌ Found {len(errors)} audio-related errors:")
            for error in errors[:5]:  # Show first 5 errors
                print(f"   - {error}")
            if len(errors) > 5:
                print(f"   ... and {len(errors) - 5} more errors")
        else:
            print("✅ No audio-related errors detected")
        
        if success_messages:
            print(f"✅ Found {len(success_messages)} audio success messages")
        
        # Save detailed logs
        log_file = f"audio_processor_logs_{timestamp}.json"
        with open(log_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'all_logs': console_logs,
                'audio_logs': audio_logs,
                'specific_audio_logs': specific_audio_logs,
                'analysis': {
                    'modern_api_used': modern_api_used,
                    'legacy_fallback': legacy_fallback,
                    'errors': errors,
                    'success_messages': success_messages
                }
            }, f, indent=2)
        print(f"💾 Detailed logs saved to: {log_file}")
        
        print(f"\n🖼️ Screenshot available at: {screenshot_path}")
        
        await browser.close()
        
        return {
            'modern_api_used': modern_api_used,
            'legacy_fallback': legacy_fallback,
            'errors': errors,
            'screenshot_path': screenshot_path,
            'log_file': log_file,
            'total_logs': len(console_logs),
            'audio_logs_count': len(audio_logs),
            'specific_audio_logs': specific_audio_logs
        }

if __name__ == "__main__":
    print("🚀 Starting Audio Processor Test...")
    result = asyncio.run(test_audio_processor())
    print(f"\n🏁 Test completed. Results: {result}")