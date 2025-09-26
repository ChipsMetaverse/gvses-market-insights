#!/usr/bin/env python3
"""
Debug script to understand Computer Use interface structure
"""

import asyncio
from playwright.async_api import async_playwright

async def run():
    print("Analyzing Computer Use interface...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Opening localhost:8080...")
        await page.goto("http://localhost:8080", wait_until='networkidle')
        
        # Wait for page to load
        await page.wait_for_timeout(5000)
        
        print("\n=== Checking for iframes ===")
        iframes = page.frames
        print(f"Found {len(iframes)} frames")
        
        print("\n=== Looking for input elements ===")
        
        # Check main frame
        print("Main frame:")
        inputs = await page.locator('input').all()
        print(f"  Found {len(inputs)} input elements")
        
        textareas = await page.locator('textarea').all()
        print(f"  Found {len(textareas)} textarea elements")
        
        # Check Streamlit-specific elements
        streamlit_inputs = await page.locator('[data-testid*="textInput"]').all()
        print(f"  Found {len(streamlit_inputs)} Streamlit text inputs")
        
        streamlit_areas = await page.locator('[data-testid*="textArea"]').all()
        print(f"  Found {len(streamlit_areas)} Streamlit text areas")
        
        # Check for any element with contenteditable
        contenteditable = await page.locator('[contenteditable="true"]').all()
        print(f"  Found {len(contenteditable)} contenteditable elements")
        
        # Check each iframe
        for i, frame in enumerate(iframes):
            if frame != page.main_frame:
                print(f"\niframe {i}:")
                try:
                    inputs = await frame.locator('input').all()
                    print(f"  Found {len(inputs)} input elements")
                    
                    textareas = await frame.locator('textarea').all()
                    print(f"  Found {len(textareas)} textarea elements")
                except:
                    print(f"  Could not access iframe {i}")
        
        print("\n=== Taking screenshot for analysis ===")
        await page.screenshot(path="computer_use_structure.png")
        print("Screenshot saved as computer_use_structure.png")
        
        print("\n=== Trying different selectors ===")
        
        # Try to find any visible text input
        selectors_to_try = [
            'textarea',
            'input[type="text"]',
            '[data-testid="stChatInput"] textarea',
            '[data-testid="stTextArea"] textarea',
            '[data-testid="stTextInput"] input',
            '.stTextArea textarea',
            '.stTextInput input',
            'div[contenteditable="true"]',
            '[role="textbox"]',
            'iframe'
        ]
        
        for selector in selectors_to_try:
            try:
                element = page.locator(selector).first
                is_visible = await element.is_visible()
                if is_visible:
                    print(f"✓ Found visible element: {selector}")
                    
                    # Try to get more info
                    placeholder = await element.get_attribute('placeholder')
                    if placeholder:
                        print(f"  Placeholder: {placeholder}")
            except:
                pass
        
        # Keep browser open for manual inspection
        print("\nKeeping browser open for 30 seconds for manual inspection...")
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())