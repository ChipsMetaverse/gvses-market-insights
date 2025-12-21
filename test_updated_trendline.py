#!/usr/bin/env python3
"""Test updated trendline with better timestamp handling"""

import asyncio
from playwright.async_api import async_playwright

async def test_updated_trendline():
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
        
        print("Navigating to application...")
        await page.goto("http://localhost:5174")
        
        # Wait for chart to load
        await page.wait_for_timeout(5000)
        
        # Clear console logs from initial load
        console_logs.clear()
        
        print("\n=== Testing updated trendline with better timestamps ===")
        
        # Test trendline with current time range
        result = await page.evaluate("""
            () => {
                console.clear();
                
                // Get current time in seconds
                const now = Math.floor(Date.now() / 1000);
                const sevenDaysAgo = now - (7 * 24 * 60 * 60); // 7 days ago
                
                // Format: TRENDLINE:startPrice:startTime:endPrice:endTime
                const command = `TRENDLINE:425:${sevenDaysAgo}:445:${now}`;
                console.log('[TEST] Sending trendline command:', command);
                
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Trendline result:', result);
                            
                            // Check primitive state after command
                            const primitive = window.enhancedChartControl.drawingPrimitive;
                            if (primitive) {
                                const drawings = primitive.getDrawings();
                                console.log('[TEST] Primitive drawings after command:', drawings);
                                return { 
                                    success: true, 
                                    result,
                                    primitiveDrawings: drawings.length,
                                    drawings: drawings
                                };
                            }
                            return { success: true, result, primitiveDrawings: 0 };
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
        
        print(f"Trendline test result: {result}")
        await page.wait_for_timeout(3000)
        
        # Check drawing primitive state
        print("\n=== Final DrawingPrimitive state ===")
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
        
        print(f"Final primitive state: {primitive_state}")
        
        # Get relevant console logs
        print("\n=== Console Logs ===")
        enhanced_logs = [log for log in console_logs if 
                        '[Enhanced Chart]' in log['text'] or 
                        '[TEST]' in log['text'] or 
                        'trendline' in log['text'].lower() or
                        'Drawing' in log['text']]
        for log in enhanced_logs:
            print(f"[{log['type']}] {log['text']}")
        
        # Take screenshot
        await page.screenshot(path=".playwright-mcp/updated_trendline_test.png")
        print("\nScreenshot saved to .playwright-mcp/updated_trendline_test.png")
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_updated_trendline())