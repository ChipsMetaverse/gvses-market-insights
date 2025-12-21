#!/usr/bin/env python3
"""
Test the modernized audio processor implementation
Checks for AudioWorkletNode vs ScriptProcessorNode usage
"""

import asyncio
import json
from playwright.async_api import async_playwright
import time
from datetime import datetime

async def test_audio_processor():
    """Test the modernized audio processor and check console logs"""
    
    async with async_playwright() as p:
        # Launch browser with audio permissions
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--allow-running-insecure-content',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        context = await browser.new_context(
            permissions=['microphone'],
            viewport={'width': 1200, 'height': 800}
        )
        
        page = await context.new_page()
        
        # Collect console logs
        console_logs = []
        audio_processor_logs = []
        errors = []
        
        def handle_console(msg):
            console_logs.append({
                'type': msg.type,
                'text': msg.text,
                'timestamp': datetime.now().isoformat()
            })
            
            # Filter for audio processor related messages
            text = msg.text.lower()
            if any(keyword in text for keyword in [
                'audioworklet', 'scriptprocessor', 'audio processor', 
                'attempting modern', 'fallback', 'worklet'
            ]):
                audio_processor_logs.append({
                    'type': msg.type,
                    'text': msg.text,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"[AUDIO LOG] {msg.type.upper()}: {msg.text}")
        
        def handle_page_error(error):
            errors.append({
                'error': str(error),
                'timestamp': datetime.now().isoformat()
            })
            print(f"[PAGE ERROR]: {error}")
        
        page.on('console', handle_console)
        page.on('pageerror', handle_page_error)
        
        print("🚀 Navigating to localhost:5174...")
        
        try:
            # Navigate to the app
            await page.goto('http://localhost:5174/', wait_until='networkidle', timeout=30000)
            print("✅ Page loaded successfully")
            
            # Wait for the app to initialize
            await page.wait_for_timeout(3000)
            
            # Take initial screenshot
            await page.screenshot(path='audio_processor_test_initial.png', full_page=True)
            print("📸 Initial screenshot taken")
            
            # Look for voice interface elements
            voice_button = page.locator('[data-testid="voice-button"], .voice-button, button:has-text("Start"), button:has-text("Voice")')
            
            if await voice_button.count() > 0:
                print("🎤 Voice button found, attempting to activate voice interface...")
                
                # Click the voice button to trigger audio processor initialization
                await voice_button.first.click()
                print("✅ Voice button clicked")
                
                # Wait for audio processor initialization
                await page.wait_for_timeout(5000)
                
                # Take screenshot after voice activation
                await page.screenshot(path='audio_processor_test_voice_active.png', full_page=True)
                print("📸 Voice active screenshot taken")
                
            else:
                print("⚠️ No voice button found, checking for automatic audio processor initialization...")
                
                # Wait longer for potential automatic initialization
                await page.wait_for_timeout(8000)
            
            # Check for specific audio processor related elements
            audio_elements = await page.evaluate("""
                () => {
                    const result = {
                        audioContext: !!window.AudioContext || !!window.webkitAudioContext,
                        audioWorkletSupported: !!(window.AudioContext && AudioContext.prototype.audioWorklet),
                        mediaStreamSupported: !!navigator.mediaDevices && !!navigator.mediaDevices.getUserMedia,
                        voiceElements: document.querySelectorAll('[class*="voice"], [class*="audio"], [data-testid*="voice"]').length
                    };
                    console.log('Audio environment check:', result);
                    return result;
                }
            """)
            
            print(f"🔍 Audio Environment Check:")
            print(f"   AudioContext supported: {audio_elements['audioContext']}")
            print(f"   AudioWorklet supported: {audio_elements['audioWorkletSupported']}")
            print(f"   MediaStream supported: {audio_elements['mediaStreamSupported']}")
            print(f"   Voice elements found: {audio_elements['voiceElements']}")
            
            # Try to manually trigger audio processor setup if no automatic initialization
            if not audio_processor_logs:
                print("🔧 Attempting to manually trigger audio processor...")
                await page.evaluate("""
                    () => {
                        // Try to trigger audio processor initialization manually
                        if (window.audioProcessor || window.voiceInterface) {
                            console.log('Manual audio processor trigger attempt');
                        }
                        
                        // Look for any audio-related methods on window
                        const audioMethods = Object.keys(window).filter(key => 
                            key.toLowerCase().includes('audio') || 
                            key.toLowerCase().includes('voice')
                        );
                        
                        if (audioMethods.length > 0) {
                            console.log('Found audio methods on window:', audioMethods);
                        }
                    }
                """)
                
                await page.wait_for_timeout(3000)
            
            # Final screenshot
            await page.screenshot(path='audio_processor_test_final.png', full_page=True)
            print("📸 Final screenshot taken")
            
            # Analyze results
            print("\n" + "="*60)
            print("🎯 AUDIO PROCESSOR TEST RESULTS")
            print("="*60)
            
            print(f"\n📊 Console Logs Collected: {len(console_logs)}")
            print(f"🎵 Audio Processor Logs: {len(audio_processor_logs)}")
            print(f"❌ Errors: {len(errors)}")
            
            # Determine audio API being used
            audio_api_used = "Unknown"
            modern_worklet_attempted = False
            fallback_used = False
            
            for log in audio_processor_logs:
                text = log['text'].lower()
                if 'attempting modern audioworkletnode' in text or 'audioworklet' in text:
                    modern_worklet_attempted = True
                    if 'successfully' in text or 'using' in text:
                        audio_api_used = "AudioWorkletNode (Modern)"
                elif 'fallback' in text and 'scriptprocessor' in text:
                    fallback_used = True
                    audio_api_used = "ScriptProcessorNode (Legacy Fallback)"
                elif 'scriptprocessor' in text and not 'fallback' in text:
                    audio_api_used = "ScriptProcessorNode (Direct)"
            
            print(f"\n🎵 Audio API Analysis:")
            print(f"   Modern AudioWorkletNode attempted: {modern_worklet_attempted}")
            print(f"   Fallback to ScriptProcessorNode: {fallback_used}")
            print(f"   Final Audio API Used: {audio_api_used}")
            
            # Show relevant audio logs
            if audio_processor_logs:
                print(f"\n🎤 Audio Processor Console Logs:")
                for log in audio_processor_logs:
                    print(f"   [{log['type'].upper()}] {log['text']}")
            else:
                print(f"\n⚠️ No specific audio processor logs found")
                print(f"   This might indicate the audio processor isn't initializing")
                print(f"   or the logging has changed.")
            
            # Show errors if any
            if errors:
                print(f"\n❌ Page Errors:")
                for error in errors:
                    print(f"   {error['error']}")
            
            # Show some general console logs for context
            print(f"\n📋 Recent Console Activity (last 5 messages):")
            for log in console_logs[-5:]:
                print(f"   [{log['type'].upper()}] {log['text'][:100]}...")
            
            # Save detailed results
            test_results = {
                'timestamp': datetime.now().isoformat(),
                'audio_api_used': audio_api_used,
                'modern_worklet_attempted': modern_worklet_attempted,
                'fallback_used': fallback_used,
                'audio_environment': audio_elements,
                'audio_processor_logs': audio_processor_logs,
                'all_console_logs': console_logs,
                'errors': errors,
                'summary': {
                    'total_logs': len(console_logs),
                    'audio_logs': len(audio_processor_logs),
                    'errors': len(errors),
                    'voice_interface_working': audio_elements['voiceElements'] > 0
                }
            }
            
            with open('audio_processor_test_results.json', 'w') as f:
                json.dump(test_results, f, indent=2)
            
            print(f"\n💾 Detailed results saved to: audio_processor_test_results.json")
            print(f"📸 Screenshots saved:")
            print(f"   - audio_processor_test_initial.png")
            print(f"   - audio_processor_test_voice_active.png (if voice activated)")
            print(f"   - audio_processor_test_final.png")
            
            return test_results
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            
            # Still try to take a screenshot for debugging
            try:
                await page.screenshot(path='audio_processor_test_error.png', full_page=True)
                print("📸 Error screenshot taken: audio_processor_test_error.png")
            except:
                pass
            
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'console_logs': console_logs,
                'audio_processor_logs': audio_processor_logs,
                'errors': errors
            }
        
        finally:
            await browser.close()

if __name__ == "__main__":
    print("🎵 Testing Modernized Audio Processor")
    print("="*50)
    
    asyncio.run(test_audio_processor())