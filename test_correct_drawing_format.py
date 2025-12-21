#!/usr/bin/env python3
"""Test correct drawing command format through ChatKit"""

import asyncio
from playwright.async_api import async_playwright

async def test_correct_drawing_format():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console messages
        console_logs = []
        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text,
            "location": msg.location
        }))
        
        # Navigate to app
        print("Navigating to application...")
        await page.goto("http://localhost:5174")
        
        # Wait for chart to load
        await page.wait_for_timeout(3000)
        
        # Clear console logs from initial load
        console_logs.clear()
        
        print("\n=== Testing correct command formats ===")
        
        # Test 1: TRENDLINE command with proper format
        print("\n1. Testing TRENDLINE command format...")
        result1 = await page.evaluate("""
            () => {
                // Clear logs
                console.clear();
                
                // Get current time
                const now = Date.now() / 1000;
                const oneDayAgo = now - 86400; // 1 day ago
                
                // Format: TRENDLINE:startPrice:startTime:endPrice:endTime
                const command = `TRENDLINE:420:${oneDayAgo}:450:${now}`;
                console.log('[TEST] Sending command:', command);
                
                // Test enhancedChartControl.processEnhancedResponse directly
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Command result:', result);
                            return { success: true, result };
                        })
                        .catch(error => {
                            console.error('[TEST] Command error:', error);
                            return { success: false, error: error.message };
                        });
                } else {
                    return { success: false, error: 'enhancedChartControl not available' };
                }
            }
        """)
        
        print(f"Result 1: {result1}")
        await page.wait_for_timeout(2000)
        
        # Test 2: SUPPORT command
        print("\n2. Testing SUPPORT command format...")
        result2 = await page.evaluate("""
            () => {
                const command = 'SUPPORT:425';
                console.log('[TEST] Sending command:', command);
                
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Command result:', result);
                            return { success: true, result };
                        })
                        .catch(error => {
                            console.error('[TEST] Command error:', error);
                            return { success: false, error: error.message };
                        });
                }
                return { success: false, error: 'enhancedChartControl not available' };
            }
        """)
        
        print(f"Result 2: {result2}")
        await page.wait_for_timeout(2000)
        
        # Test 3: RESISTANCE command
        print("\n3. Testing RESISTANCE command format...")
        result3 = await page.evaluate("""
            () => {
                const command = 'RESISTANCE:445';
                console.log('[TEST] Sending command:', command);
                
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Command result:', result);
                            return { success: true, result };
                        })
                        .catch(error => {
                            console.error('[TEST] Command error:', error);
                            return { success: false, error: error.message };
                        });
                }
                return { success: false, error: 'enhancedChartControl not available' };
            }
        """)
        
        print(f"Result 3: {result3}")
        await page.wait_for_timeout(2000)
        
        # Check drawing primitive state
        print("\n=== Checking DrawingPrimitive state ===")
        primitive_state = await page.evaluate("""
            () => {
                const primitive = window.enhancedChartControl?.drawingPrimitive;
                if (primitive) {
                    const drawings = primitive.getDrawings();
                    return {
                        hasPrimitive: true,
                        drawingCount: drawings.length,
                        drawings: drawings
                    };
                }
                return { hasPrimitive: false };
            }
        """)
        
        print(f"Primitive state: {primitive_state}")
        
        # Get relevant console logs
        print("\n=== Console Logs ===")
        drawing_logs = [log for log in console_logs if '[TEST]' in log['text'] or 'Drawing' in log['text'] or 'trendline' in log['text'].lower()]
        for log in drawing_logs:
            print(f"[{log['type']}] {log['text']}")
        
        # Take screenshot
        await page.screenshot(path=".playwright-mcp/correct_format_test.png")
        print("\nScreenshot saved to .playwright-mcp/correct_format_test.png")
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_correct_drawing_format())