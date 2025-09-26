#!/usr/bin/env python3
"""
Find and use the correct chat input in Computer Use interface
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Finding correct chat input in Computer Use...")
    
    test_prompt = """Please help me test the Voice Assistant feature of the trading application:

1. Open Firefox browser in the desktop
2. Navigate to http://host.docker.internal:5174
3. Wait for the trading application to load completely
4. Find the Voice Assistant panel on the RIGHT side of the page
5. Click on the text input field (placeholder: "Type a message...")
6. Type: "What is the current price of PLTR?"
7. Press Enter to submit
8. Report what information was provided"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Opening localhost:8080...")
        await page.goto("http://localhost:8080", wait_until='networkidle')
        await page.wait_for_timeout(5000)
        
        frames = page.frames
        print(f"Found {len(frames)} frames")
        
        # Look for the chat input more carefully
        chat_input = None
        
        for i, frame in enumerate(frames):
            if frame == page.main_frame:
                continue
            
            print(f"\nChecking iframe {i}...")
            
            try:
                # Look for all textareas and inputs
                all_inputs = []
                
                # Get textareas
                textareas = await frame.locator('textarea').all()
                for textarea in textareas:
                    placeholder = await textarea.get_attribute('placeholder') or ""
                    aria_label = await textarea.get_attribute('aria-label') or ""
                    is_visible = await textarea.is_visible()
                    print(f"  Textarea - placeholder: '{placeholder}', aria-label: '{aria_label}', visible: {is_visible}")
                    
                    # Look for chat-related inputs
                    if is_visible and ('chat' in placeholder.lower() or 
                                      'message' in placeholder.lower() or 
                                      'type' in placeholder.lower() or
                                      'chat' in aria_label.lower() or
                                      placeholder == ""):  # Sometimes chat inputs have no placeholder
                        # Skip config fields
                        if 'system' not in aria_label.lower() and 'prompt' not in aria_label.lower():
                            all_inputs.append(('textarea', textarea, placeholder, aria_label))
                
                # Get text inputs
                inputs = await frame.locator('input[type="text"]').all()
                for inp in inputs:
                    placeholder = await inp.get_attribute('placeholder') or ""
                    aria_label = await inp.get_attribute('aria-label') or ""
                    is_visible = await inp.is_visible()
                    print(f"  Input - placeholder: '{placeholder}', aria-label: '{aria-label}', visible: {is_visible}")
                    
                    if is_visible and ('chat' in placeholder.lower() or 
                                      'message' in placeholder.lower() or
                                      'type' in placeholder.lower()):
                        all_inputs.append(('input', inp, placeholder, aria_label))
                
                # If we found potential inputs, use the most likely one
                if all_inputs:
                    # Prefer inputs with message/chat in placeholder
                    for inp_type, element, placeholder, aria_label in all_inputs:
                        if 'message' in placeholder.lower() or 'chat' in placeholder.lower():
                            print(f"  ✓ Selected {inp_type} with placeholder: '{placeholder}'")
                            chat_input = element
                            break
                    
                    # If no good match, use the last visible one (usually bottom of page)
                    if not chat_input:
                        chat_input = all_inputs[-1][1]
                        print(f"  ✓ Selected last {all_inputs[-1][0]} as fallback")
                
                if chat_input:
                    break
                    
            except Exception as e:
                print(f"  Error: {e}")
        
        if chat_input:
            print("\n✅ Found chat input! Sending message...")
            
            # Scroll into view first
            await chat_input.scroll_into_view_if_needed()
            await page.wait_for_timeout(500)
            
            # Click and clear
            await chat_input.click()
            await chat_input.fill("")
            
            # Type message
            await chat_input.type(test_prompt, delay=30)
            
            # Submit
            await page.wait_for_timeout(1000)
            await page.keyboard.press("Enter")
            
            print("✅ Message sent!")
            print("Keeping browser open for observation...")
            await page.wait_for_timeout(60000)
            
        else:
            print("\n❌ Could not find chat input")
            await page.screenshot(path="no_chat_input.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())