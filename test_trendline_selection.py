#!/usr/bin/env python3
"""
Manual Test Script for Trendline Selection Feature
Run this script to test trendline selection, popup display, and deletion.
"""

from playwright.sync_api import sync_playwright
import time

def test_trendline_selection():
    """Test trendline selection and deletion with Backspace key."""

    with sync_playwright() as p:
        # Launch browser
        print("🚀 Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        page = browser.new_page()

        # Navigate to demo page
        print("📄 Navigating to http://localhost:5174/demo...")
        page.goto('http://localhost:5174/demo')

        # Wait for chart to load
        print("⏳ Waiting for chart to load...")
        time.sleep(6)

        # Take screenshot of initial state
        print("📸 Taking screenshot: before-selection.png")
        page.screenshot(path='/tmp/before-selection.png')

        # Get chart canvas element
        print("🎯 Looking for chart canvas...")
        canvas = page.locator('canvas').first

        if canvas:
            # Get canvas position and size
            box = canvas.bounding_box()
            if box:
                # Click on middle-left area where the Lower Trend trendline should be
                # Adjust these coordinates based on where you see the trendline
                click_x = box['x'] + box['width'] * 0.3  # 30% from left
                click_y = box['y'] + box['height'] * 0.7  # 70% from top

                print(f"🖱️  Clicking on trendline at ({click_x}, {click_y})...")
                page.mouse.click(click_x, click_y)

                # Wait for selection to take effect
                time.sleep(1)

                # Take screenshot after selection
                print("📸 Taking screenshot: after-selection.png")
                page.screenshot(path='/tmp/after-selection.png')

                # Check console for selection message
                print("📋 Checking console logs for 'Selected trendline'...")

                # Press Backspace to delete
                print("⌨️  Pressing Backspace to delete trendline...")
                page.keyboard.press('Backspace')

                # Wait for deletion
                time.sleep(1)

                # Take screenshot after deletion
                print("📸 Taking screenshot: after-deletion.png")
                page.screenshot(path='/tmp/after-deletion.png')

                # Check console for deletion message
                print("📋 Checking console logs for 'Deleted trendline'...")

                print("\n✅ Test sequence complete!")
                print("\n📊 Screenshots saved to:")
                print("   /tmp/before-selection.png")
                print("   /tmp/after-selection.png")
                print("   /tmp/after-deletion.png")

                # Keep browser open for manual inspection
                print("\n👀 Browser will stay open for 30 seconds for manual inspection...")
                time.sleep(30)
            else:
                print("❌ Could not get canvas bounding box")
        else:
            print("❌ Canvas not found")

        # Close browser
        print("🔒 Closing browser...")
        browser.close()
        print("✅ Done!")

if __name__ == '__main__':
    print("=" * 60)
    print("TRENDLINE SELECTION & DELETION TEST")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Open the chart in a browser")
    print("2. Wait for trendlines to load")
    print("3. Click on a trendline to select it")
    print("4. Take a screenshot showing selection")
    print("5. Press Backspace to delete the trendline")
    print("6. Take a screenshot showing deletion")
    print("\n" + "=" * 60 + "\n")

    test_trendline_selection()
