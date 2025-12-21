"""
Comprehensive test to verify trendline drawing functionality
Tests that the rebuilt TradingChart.tsx correctly creates trendlines
"""
import time
from playwright.sync_api import sync_playwright

def test_trendline_drawing():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Collect console logs
        console_logs = []
        page.on('console', lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # Navigate to test chart
        print("🌐 Loading test chart...")
        page.goto('http://localhost:5174/test-chart')
        page.wait_for_load_state('networkidle')
        time.sleep(3)

        # Take initial screenshot
        page.screenshot(path='/tmp/trendline_test_1_initial.png')
        print("📸 Screenshot 1: Initial state saved")

        # Activate trendline drawing mode
        print("\n🎨 Activating trendline drawing mode...")
        trendline_btn = page.locator('button:has-text("Trendline")')
        trendline_btn.click()
        time.sleep(0.5)

        # Verify drawing mode activated
        button_text = trendline_btn.text_content()
        print(f"✅ Button text after activation: '{button_text}'")

        # Take screenshot of activated mode
        page.screenshot(path='/tmp/trendline_test_2_activated.png')
        print("📸 Screenshot 2: Drawing mode activated")

        # Get chart canvas and its bounding box
        chart_canvas = page.locator('canvas').last
        bbox = chart_canvas.bounding_box()

        print(f"\n📊 Chart dimensions: {bbox['width']}x{bbox['height']}")

        # Click first point (left side, lower area)
        x1 = bbox['x'] + bbox['width'] * 0.25  # 25% from left
        y1 = bbox['y'] + bbox['height'] * 0.75  # 75% down (near bottom)

        print(f"\n🖱️  Click 1: ({x1:.0f}, {y1:.0f})")
        page.mouse.click(x1, y1)
        time.sleep(0.5)

        # Check for first click console log
        first_click_logs = [log for log in console_logs if 'Drawing point 1' in log or 'drawingPoints' in log]
        print(f"Console after first click: {len(first_click_logs)} drawing-related logs")

        # Take screenshot after first click
        page.screenshot(path='/tmp/trendline_test_3_first_point.png')
        print("📸 Screenshot 3: After first point")

        # Click second point (right side, upper area)
        x2 = bbox['x'] + bbox['width'] * 0.75  # 75% from left
        y2 = bbox['y'] + bbox['height'] * 0.25  # 25% down (near top)

        print(f"🖱️  Click 2: ({x2:.0f}, {y2:.0f})")
        page.mouse.click(x2, y2)
        time.sleep(1)

        # Check for trendline creation log
        creation_logs = [log for log in console_logs if 'Created trendline' in log]
        print(f"\n✅ Trendline creation logs: {len(creation_logs)}")
        if creation_logs:
            print(f"   {creation_logs[-1]}")

        # Take screenshot after second click
        page.screenshot(path='/tmp/trendline_test_4_trendline_created.png')
        print("📸 Screenshot 4: After trendline creation")

        # Verify drawing mode deactivated
        button_text_after = trendline_btn.text_content()
        print(f"Button text after second click: '{button_text_after}'")

        # Try to select the trendline by clicking near the middle
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        print(f"\n🖱️  Clicking middle of trendline: ({mid_x:.0f}, {mid_y:.0f})")
        page.mouse.click(mid_x, mid_y)
        time.sleep(0.5)

        # Check for selection log
        selection_logs = [log for log in console_logs if 'Selected trendline' in log]
        print(f"Selection logs: {len(selection_logs)}")
        if selection_logs:
            print(f"   {selection_logs[-1]}")

        # Take screenshot of selected state
        page.screenshot(path='/tmp/trendline_test_5_selected.png')
        print("📸 Screenshot 5: Trendline selected (should be gold/thicker)")

        # Test delete functionality
        print("\n🗑️  Testing delete with Delete key...")
        page.keyboard.press('Delete')
        time.sleep(0.5)

        # Check for deletion log
        deletion_logs = [log for log in console_logs if 'Deleted trendline' in log]
        print(f"Deletion logs: {len(deletion_logs)}")
        if deletion_logs:
            print(f"   {deletion_logs[-1]}")

        # Take final screenshot
        page.screenshot(path='/tmp/trendline_test_6_after_delete.png')
        print("📸 Screenshot 6: After deletion")

        # Summary
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        print(f"Drawing Mode Activated:   {'✅ PASS' if 'click 2 points' in button_text else '❌ FAIL'}")
        print(f"Trendline Created:        {'✅ PASS' if creation_logs else '❌ FAIL'}")
        print(f"Trendline Selected:       {'✅ PASS' if selection_logs else '❌ FAIL'}")
        print(f"Trendline Deleted:        {'✅ PASS' if deletion_logs else '❌ FAIL'}")
        print("="*70)

        print("\n📁 All screenshots saved to /tmp/trendline_test_*.png")

        # Print relevant console logs
        print("\n📝 Relevant Console Logs:")
        for log in console_logs:
            if any(keyword in log for keyword in ['trendline', 'drawing', 'Selected', 'Deleted', 'Created']):
                print(f"   {log}")

        all_passed = creation_logs and selection_logs and deletion_logs
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! Trendline functionality working correctly!")
        else:
            print("\n⚠️  Some tests failed - check screenshots and console logs")

        input("\n\nPress Enter to close browser...")
        browser.close()

if __name__ == '__main__':
    test_trendline_drawing()
