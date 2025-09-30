#!/usr/bin/env python3
"""
Simplified Playwright Demo - Testing ML Pattern Detection
"""

import asyncio
from playwright.async_api import async_playwright
import requests
import json

def check_services():
    """Check if services are running."""
    print("🔍 Checking services...")
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding properly")
            return False
    except:
        print("❌ Backend is not running on port 8000")
        return False
    
    # Check frontend
    try:
        response = requests.get("http://localhost:5174")
        if response.status_code == 200:
            print("✅ Frontend is running")
        else:
            print("❌ Frontend not responding properly")
            return False
    except:
        print("❌ Frontend is not running on port 5174")
        return False
    
    # Check ML status
    try:
        response = requests.get("http://localhost:8000/api/ml/health")
        data = response.json()
        print(f"✅ ML System: Phase 5 {'Enabled' if data.get('phase5_enabled') else 'Disabled'}")
        print(f"   Model Loaded: {data.get('model_loaded', False)}")
        print(f"   Predictions: {data.get('predictions_made', 0)}")
    except:
        print("⚠️ ML health endpoint not available")
    
    return True

async def test_pattern_api():
    """Test pattern detection via direct API call."""
    print("\n📊 Testing Pattern Detection API...")
    
    try:
        # Test comprehensive data with patterns
        response = requests.get(
            "http://localhost:8000/api/comprehensive-stock-data",
            params={"symbol": "TSLA", "indicators": "patterns"}
        )
        
        if response.status_code == 200:
            data = response.json()
            patterns = data.get('patterns', {})
            detected = patterns.get('detected', [])
            
            print(f"✅ API Response received")
            print(f"   Symbol: {data.get('symbol')}")
            print(f"   Price: ${data.get('price_data', {}).get('last', 0):.2f}")
            print(f"   Patterns found: {len(detected)}")
            
            if detected:
                print("   Detected patterns:")
                for p in detected[:3]:
                    print(f"     - {p.get('type')}: {p.get('confidence')}% confidence")
            
            # Check for ML enhancement
            if any('ml' in str(p).lower() for p in detected):
                print("   🤖 ML enhancement detected!")
            
            return True
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

async def browser_test():
    """Simple browser test with Playwright."""
    print("\n🌐 Browser Automation Test...")
    
    async with async_playwright() as p:
        print("   Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=1000  # Slow down for visibility
        )
        
        page = await browser.new_page()
        
        try:
            print("   Navigating to app...")
            response = await page.goto('http://localhost:5174', wait_until='domcontentloaded', timeout=10000)
            
            if response and response.ok:
                print("   ✅ Page loaded successfully")
                
                # Take screenshot
                await page.screenshot(path='playwright_demo.png')
                print("   📸 Screenshot saved: playwright_demo.png")
                
                # Wait for React to render
                await page.wait_for_timeout(3000)
                
                # Check for stock cards
                stock_cards = await page.query_selector_all('.stock-card')
                if stock_cards:
                    print(f"   ✅ Found {len(stock_cards)} stock cards")
                    
                    # Click first stock
                    await stock_cards[0].click()
                    print("   ✅ Clicked on stock card")
                    await page.wait_for_timeout(2000)
                else:
                    print("   ⚠️ No stock cards found")
                
                # Try to find chart
                chart = await page.query_selector('.tv-lightweight-charts, canvas')
                if chart:
                    print("   ✅ Chart component found")
                else:
                    print("   ⚠️ Chart not found")
                
                # Take final screenshot
                await page.screenshot(path='playwright_demo_final.png', full_page=True)
                print("   📸 Final screenshot: playwright_demo_final.png")
                
            else:
                print(f"   ❌ Page load failed: {response.status if response else 'No response'}")
                
        except Exception as e:
            print(f"   ❌ Browser test error: {e}")
        
        print("   Closing browser in 5 seconds...")
        await page.wait_for_timeout(5000)
        await browser.close()

async def test_ml_trigger():
    """Test triggering ML pattern detection."""
    print("\n🤖 Testing ML Pattern Detection Trigger...")
    
    # First, seed a test pattern
    try:
        response = requests.post(
            "http://localhost:8000/api/test-pattern",
            json={
                "symbol": "TSLA",
                "pattern_type": "bullish_engulfing",
                "confidence": 0.75
            }
        )
        print("   Attempted to seed test pattern")
    except:
        print("   ⚠️ Test pattern endpoint not available")
    
    # Now check ML metrics
    try:
        response = requests.get("http://localhost:8000/api/ml/metrics")
        data = response.json()
        current = data.get('current', {})
        perf = current.get('performance', {})
        
        print(f"   ML Metrics:")
        print(f"     Inference count: {perf.get('inference_count', 0)}")
        print(f"     Avg latency: {perf.get('avg_latency_ms', 0):.1f}ms")
        print(f"     Error rate: {perf.get('error_rate', 0):.1%}")
        
        if perf.get('inference_count', 0) > 0:
            print("   ✅ ML inference has been triggered!")
        else:
            print("   ⏳ ML inference not yet triggered")
            
    except Exception as e:
        print(f"   ❌ Failed to get ML metrics: {e}")

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🎭 PLAYWRIGHT ML DEMONSTRATION")
    print("=" * 60)
    
    # Check services first
    if not check_services():
        print("\n❌ Services not running. Please start both frontend and backend.")
        return
    
    # Test API
    await test_pattern_api()
    
    # Test browser automation
    await browser_test()
    
    # Test ML trigger
    await test_ml_trigger()
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nCheck the generated screenshots:")
    print("  - playwright_demo.png")
    print("  - playwright_demo_final.png")

if __name__ == "__main__":
    asyncio.run(main())