#!/usr/bin/env python3
"""Test mobile tab swipe gesture restriction"""

from playwright.sync_api import sync_playwright
import time

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 375, 'height': 812},
            has_touch=True
        )
        page = context.new_page()

        # Enable console logging
        page.on('console', lambda msg: print(f'Console [{msg.type}]: {msg.text}'))

        print('🌐 Navigating to dashboard (already authenticated)...')
        page.goto('http://localhost:5174/dashboard', wait_until='networkidle')
        time.sleep(3)

        print('📸 Current state: Chart + Voice tab active')
        page.screenshot(path='.playwright-mcp/mobile-chart-tab-active.png')

        # Test 1: Swipe on the chart area (should NOT switch tabs)
        print('\n🧪 TEST 1: Swipe LEFT on chart area (should NOT switch tabs)')
        # Swipe in the middle of the screen (chart area)
        start_x = 200
        start_y = 300  # Above the tab bar

        page.mouse.move(start_x, start_y)
        page.mouse.down()
        page.mouse.move(start_x - 100, start_y)  # Swipe left
        page.mouse.up()

        time.sleep(1)
        page.screenshot(path='.playwright-mcp/after-chart-swipe.png')

        # Check if still on Chart + Voice tab
        active_button = page.locator('button[aria-pressed="true"]')
        active_text = active_button.text_content()
        print(f'Active tab after chart swipe: {active_text}')

        if 'Chart + Voice' in active_text:
            print('✅ PASS: Tab did NOT switch (correct behavior)')
        else:
            print('❌ FAIL: Tab switched when it should not have')

        # Test 2: Swipe on the tab bar (should switch tabs)
        print('\n🧪 TEST 2: Swipe LEFT on tab bar (SHOULD switch tabs)')
        tab_bar = page.locator('nav[aria-label="Dashboard navigation"]')
        tab_box = tab_bar.bounding_box()

        if tab_box:
            # Swipe left on tab bar
            start_x = tab_box['x'] + tab_box['width'] * 0.7
            start_y = tab_box['y'] + tab_box['height'] / 2

            page.mouse.move(start_x, start_y)
            page.mouse.down()
            page.mouse.move(start_x - 100, start_y)  # Swipe left
            page.mouse.up()

            time.sleep(1)
            page.screenshot(path='.playwright-mcp/after-tabbar-swipe.png')

            # Check if switched to Analysis tab
            active_button = page.locator('button[aria-pressed="true"]')
            active_text = active_button.text_content()
            print(f'Active tab after tab bar swipe: {active_text}')

            if 'Analysis' in active_text:
                print('✅ PASS: Tab switched (correct behavior)')
            else:
                print('❌ FAIL: Tab did not switch when it should have')

        # Test 3: Swipe right on tab bar (should switch back)
        print('\n🧪 TEST 3: Swipe RIGHT on tab bar (SHOULD switch back)')
        if tab_box:
            start_x = tab_box['x'] + tab_box['width'] * 0.3
            start_y = tab_box['y'] + tab_box['height'] / 2

            page.mouse.move(start_x, start_y)
            page.mouse.down()
            page.mouse.move(start_x + 100, start_y)  # Swipe right
            page.mouse.up()

            time.sleep(1)
            page.screenshot(path='.playwright-mcp/after-tabbar-swipe-back.png')

            active_button = page.locator('button[aria-pressed="true"]')
            active_text = active_button.text_content()
            print(f'Active tab after swipe back: {active_text}')

            if 'Chart + Voice' in active_text:
                print('✅ PASS: Tab switched back (correct behavior)')
            else:
                print('❌ FAIL: Tab did not switch back')

        print('\n✅ All tests complete!')
        time.sleep(2)
        browser.close()

if __name__ == '__main__':
    main()
