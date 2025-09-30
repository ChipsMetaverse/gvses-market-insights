#!/usr/bin/env python3
"""
Comprehensive ML Pattern Detection Demonstration
Combines Playwright automation with API interactions to showcase Phase 5
"""

import asyncio
import aiohttp
import json
from playwright.async_api import async_playwright
from datetime import datetime

class MLPatternDemonstrator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5174"
        self.results = {
            "ml_status": {},
            "patterns_found": [],
            "screenshots": [],
            "api_responses": []
        }
    
    async def check_ml_health(self):
        """Check ML system health status."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/ml/health") as resp:
                data = await resp.json()
                self.results["ml_status"] = data
                return data
    
    async def trigger_pattern_detection(self, symbol="TSLA"):
        """Trigger pattern detection for a symbol."""
        async with aiohttp.ClientSession() as session:
            # Get comprehensive stock data with patterns
            url = f"{self.base_url}/api/comprehensive-stock-data"
            params = {"symbol": symbol, "indicators": "patterns"}
            
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                self.results["api_responses"].append({
                    "endpoint": "comprehensive-stock-data",
                    "symbol": symbol,
                    "response": data
                })
                return data
    
    async def seed_test_pattern(self, symbol="TSLA"):
        """Seed a test pattern to trigger ML enhancement."""
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/test-pattern"
            payload = {
                "symbol": symbol,
                "pattern_type": "bullish_engulfing",
                "confidence": 0.75,
                "timeframe": "1D"
            }
            
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        print(f"   ✅ Test pattern seeded: {data}")
                        return data
            except:
                print("   ⚠️ Test pattern endpoint not available")
                return None
    
    async def get_ml_metrics(self):
        """Fetch ML system metrics."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/ml/metrics") as resp:
                data = await resp.json()
                return data
    
    async def browser_demonstration(self):
        """Demonstrate UI interaction with Playwright."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=1500
            )
            
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Navigate to app
            print("   🌐 Opening trading application...")
            await page.goto(self.frontend_url)
            await page.wait_for_timeout(5000)
            
            # Take initial screenshot
            await page.screenshot(path='ml_demo_1_initial.png')
            self.results["screenshots"].append('ml_demo_1_initial.png')
            print("   📸 Initial state captured")
            
            # Find and interact with voice assistant input
            print("   💬 Looking for voice assistant input...")
            message_input = await page.query_selector('input[placeholder*="message"], textarea')
            
            if message_input:
                # Send pattern detection command
                await message_input.click()
                await message_input.fill("Show me ML-enhanced patterns for TSLA")
                await page.keyboard.press('Enter')
                print("   ✅ Pattern request sent")
                await page.wait_for_timeout(5000)
                
                await page.screenshot(path='ml_demo_2_request.png')
                self.results["screenshots"].append('ml_demo_2_request.png')
            
            # Check for pattern detection results in UI
            print("   🔍 Checking for pattern detection results...")
            
            # Use JavaScript to fetch patterns directly
            patterns_data = await page.evaluate("""
                async () => {
                    const response = await fetch('http://localhost:8000/api/comprehensive-stock-data?symbol=TSLA&indicators=patterns');
                    return await response.json();
                }
            """)
            
            if patterns_data and patterns_data.get('patterns'):
                detected = patterns_data['patterns'].get('detected', [])
                self.results["patterns_found"] = detected
                print(f"   📊 Found {len(detected)} patterns via API")
                
                # Check for ML enhancement
                ml_enhanced = any(p.get('ml_confidence') is not None for p in detected)
                if ml_enhanced:
                    print("   🤖 ML ENHANCEMENT DETECTED!")
                    for p in detected[:3]:
                        if p.get('ml_confidence'):
                            print(f"      - {p['type']}: ML confidence {p['ml_confidence']:.1%}")
            
            # Final screenshot
            await page.screenshot(path='ml_demo_3_final.png', full_page=True)
            self.results["screenshots"].append('ml_demo_3_final.png')
            print("   📸 Final state captured")
            
            await page.wait_for_timeout(5000)
            await browser.close()
    
    async def run_full_demonstration(self):
        """Run complete ML pattern detection demonstration."""
        print("=" * 70)
        print("🤖 ML PATTERN DETECTION DEMONSTRATION - PHASE 5")
        print("=" * 70)
        
        # Step 1: Check ML Health
        print("\n1️⃣ Checking ML System Health...")
        ml_health = await self.check_ml_health()
        print(f"   Phase 5 Enabled: {ml_health.get('phase5_enabled', False)}")
        print(f"   Model Loaded: {ml_health.get('model_loaded', False)}")
        print(f"   Predictions Made: {ml_health.get('predictions_made', 0)}")
        
        # Step 2: Seed test pattern (if needed)
        print("\n2️⃣ Seeding Test Pattern...")
        await self.seed_test_pattern("TSLA")
        
        # Step 3: Trigger pattern detection
        print("\n3️⃣ Triggering Pattern Detection...")
        patterns_response = await self.trigger_pattern_detection("TSLA")
        
        if patterns_response and patterns_response.get('patterns'):
            detected = patterns_response['patterns'].get('detected', [])
            print(f"   📊 Detected {len(detected)} patterns")
            
            # Check for ML enhancement
            for pattern in detected[:5]:
                confidence = pattern.get('confidence', 0)
                ml_confidence = pattern.get('ml_confidence')
                
                if ml_confidence is not None:
                    print(f"   🤖 {pattern['type']}:")
                    print(f"      Rule-based: {confidence}%")
                    print(f"      ML-enhanced: {ml_confidence:.1%}")
                    print(f"      Blended: {pattern.get('blended_confidence', confidence)}%")
                else:
                    print(f"   📈 {pattern['type']}: {confidence}% (no ML)")
        
        # Step 4: Browser demonstration
        print("\n4️⃣ Browser Automation Demo...")
        await self.browser_demonstration()
        
        # Step 5: Final ML metrics
        print("\n5️⃣ Final ML Metrics...")
        metrics = await self.get_ml_metrics()
        current = metrics.get('current', {})
        perf = current.get('performance', {})
        
        print(f"   Inference Count: {perf.get('inference_count', 0)}")
        print(f"   Average Latency: {perf.get('avg_latency_ms', 0):.1f}ms")
        print(f"   Error Rate: {perf.get('error_rate', 0):.1%}")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 DEMONSTRATION SUMMARY")
        print("=" * 70)
        
        print("\n✅ Completed Steps:")
        print("  1. ML health check performed")
        print("  2. Test pattern seeded")
        print("  3. Pattern detection triggered")
        print("  4. Browser automation executed")
        print("  5. ML metrics collected")
        
        print("\n🤖 ML Enhancement Status:")
        if self.results["patterns_found"]:
            ml_patterns = [p for p in self.results["patterns_found"] 
                          if p.get('ml_confidence') is not None]
            if ml_patterns:
                print(f"  ✅ {len(ml_patterns)} patterns with ML enhancement")
                print(f"  ✅ ML confidence scores applied")
                print(f"  ✅ Blended scoring active")
            else:
                print("  ⚠️ No ML-enhanced patterns found")
        else:
            print("  ⚠️ No patterns detected")
        
        print("\n📸 Screenshots Generated:")
        for screenshot in self.results["screenshots"]:
            print(f"  - {screenshot}")
        
        # Save results to file
        with open('ml_demonstration_results.json', 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print("\n💾 Results saved to: ml_demonstration_results.json")
        
        return self.results

async def main():
    demonstrator = MLPatternDemonstrator()
    await demonstrator.run_full_demonstration()

if __name__ == "__main__":
    asyncio.run(main())