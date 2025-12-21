#!/usr/bin/env python3
"""Test trendline with interpolation fix"""

import asyncio
from playwright.async_api import async_playwright

async def test_interpolated_trendline():
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
        
        print("\n=== Testing trendline with interpolation ===")
        
        # Test with timestamps that need interpolation
        result = await page.evaluate("""
            () => {
                console.clear();
                
                // Use timestamps that will need interpolation
                const startTime = 1760500000; // Between data points
                const endTime = 1760650000;   // Between data points
                
                const command = `TRENDLINE:430:${startTime}:450:${endTime}`;
                console.log('[TEST] Sending interpolated trendline command:', command);
                
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Command result:', result);
                            
                            // Wait a moment then check primitive state
                            return new Promise(resolve => {
                                setTimeout(() => {
                                    const primitive = window.enhancedChartControl.drawingPrimitive;
                                    if (primitive) {
                                        const drawings = primitive.getDrawings();
                                        console.log('[TEST] Primitive drawings after interpolation:', drawings);
                                        resolve({ 
                                            success: true, 
                                            result,
                                            primitiveDrawings: drawings.length,
                                            drawings: drawings
                                        });
                                    } else {
                                        resolve({ success: true, result, primitiveDrawings: 0 });
                                    }
                                }, 1000);
                            });
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
        
        print(f"Interpolated trendline result: {result}")
        await page.wait_for_timeout(3000)
        
        # Filter console logs for relevant information
        print("\n=== Interpolation Console Logs ===")
        interpolation_logs = [log for log in console_logs if 
                             '[DrawingRenderer]' in log['text'] or 
                             '[TEST]' in log['text'] or
                             'Interpolat' in log['text'] or
                             'coordinate' in log['text'].lower()]
        for log in interpolation_logs:
            print(f"[{log['type']}] {log['text']}")
        
        # Take screenshot to verify visual result
        await page.screenshot(path=".playwright-mcp/interpolated_trendline_test.png")
        print("\nScreenshot saved to .playwright-mcp/interpolated_trendline_test.png")
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_interpolated_trendline())