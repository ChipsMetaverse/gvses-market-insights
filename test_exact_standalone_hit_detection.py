"""
Test the exact standalone hit detection implementation
Tests zoom-aware dynamic price tolerance at different zoom levels
"""
import time
from playwright.sync_api import sync_playwright, expect

def test_hit_detection_at_zoom_levels():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Navigate to test chart
        page.goto('http://localhost:5174/test-chart')
        page.wait_for_load_state('networkidle')
        time.sleep(2)

        print("✅ Page loaded")

        # Activate trendline tool
        trendline_btn = page.locator('button:has-text("↗️ Trendline")')
        trendline_btn.click()
        time.sleep(0.5)

        print("✅ Trendline tool activated")

        # Draw a trendline (two clicks in the middle of chart)
        chart_canvas = page.locator('canvas').last
        bbox = chart_canvas.bounding_box()

        # Click first point
        x1, y1 = bbox['x'] + 200, bbox['y'] + bbox['height'] - 100
        page.mouse.click(x1, y1)
        time.sleep(0.3)

        # Click second point (higher and to the right)
        x2, y2 = bbox['x'] + 500, bbox['y'] + 100
        page.mouse.click(x2, y2)
        time.sleep(0.5)

        print("✅ Trendline drawn")

        # Test 1: Selection at default zoom level
        print("\n📍 TEST 1: Selection at default zoom")
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        page.mouse.click(mid_x, mid_y)
        time.sleep(0.5)

        # Check console for selection confirmation
        console_logs = []
        page.on('console', lambda msg: console_logs.append(msg.text()))
        time.sleep(0.2)

        has_selection = any('🎯 Drawing selected' in log for log in console_logs)
        print(f"{'✅' if has_selection else '❌'} Selection detected at default zoom")

        # Test 2: Zoom in and test selection again
        print("\n📍 TEST 2: Selection after zoom in")

        # Zoom in by scrolling
        page.mouse.move(mid_x, mid_y)
        for _ in range(3):
            page.mouse.wheel(0, -100)  # Scroll up to zoom in
            time.sleep(0.2)

        # Try selecting again
        console_logs.clear()
        page.mouse.click(mid_x, mid_y)
        time.sleep(0.5)

        has_selection_zoomed = any('🎯 Drawing selected' in log for log in console_logs)
        print(f"{'✅' if has_selection_zoomed else '❌'} Selection detected after zoom in")

        # Test 3: Zoom out and test selection
        print("\n📍 TEST 3: Selection after zoom out")

        # Zoom out by scrolling
        for _ in range(6):
            page.mouse.wheel(0, 100)  # Scroll down to zoom out
            time.sleep(0.2)

        # Try selecting again
        console_logs.clear()
        page.mouse.click(mid_x, mid_y)
        time.sleep(0.5)

        has_selection_zoomed_out = any('🎯 Drawing selected' in log for log in console_logs)
        print(f"{'✅' if has_selection_zoomed_out else '❌'} Selection detected after zoom out")

        # Test 4: Delete the trendline
        print("\n📍 TEST 4: Delete trendline")

        if has_selection or has_selection_zoomed or has_selection_zoomed_out:
            # Select the trendline first
            page.mouse.click(mid_x, mid_y)
            time.sleep(0.3)

            # Press Delete key
            console_logs.clear()
            page.keyboard.press('Delete')
            time.sleep(0.5)

            has_delete = any('Deleting drawing' in log for log in console_logs)
            print(f"{'✅' if has_delete else '❌'} Delete command executed")

        # Take final screenshot
        page.screenshot(path='/tmp/hit_detection_test_final.png')
        print("\n📸 Screenshot saved to /tmp/hit_detection_test_final.png")

        # Summary
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Default Zoom Selection:  {'✅ PASS' if has_selection else '❌ FAIL'}")
        print(f"Zoomed In Selection:     {'✅ PASS' if has_selection_zoomed else '❌ FAIL'}")
        print(f"Zoomed Out Selection:    {'✅ PASS' if has_selection_zoomed_out else '❌ FAIL'}")
        print(f"Delete Functionality:    {'✅ PASS' if has_delete else '❌ FAIL'}")
        print("="*60)

        all_passed = has_selection and has_selection_zoomed and has_selection_zoomed_out and has_delete
        if all_passed:
            print("\n🎉 ALL TESTS PASSED! Zoom-aware hit detection working correctly!")
        else:
            print("\n⚠️ Some tests failed - check console logs for details")

        input("\nPress Enter to close browser...")
        browser.close()

if __name__ == '__main__':
    test_hit_detection_at_zoom_levels()
