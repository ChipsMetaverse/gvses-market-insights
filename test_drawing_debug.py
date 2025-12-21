#!/usr/bin/env python3
"""Test drawing functionality with debug logging using Playwright"""

import asyncio
import json
from playwright.async_api import async_playwright

async def test_drawing_with_debug():
    async with async_playwright() as p:
        # Launch browser
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
        initial_logs = console_logs.copy()
        console_logs.clear()
        
        # Click on ChatKit input
        print("Opening ChatKit...")
        # Use the correct selector for ChatKit
        chatkit_selector = '.chat-bubble, .floating-chat-bubble, [data-testid="chatkit-toggle"]'
        try:
            await page.click(chatkit_selector, timeout=5000)
        except:
            print("ChatKit toggle not found, trying direct input...")
            # Try to find any visible textarea
            pass
        
        await page.wait_for_timeout(500)
        
        # Send trendline command - find the textarea that's visible
        print("Sending trendline command...")
        textarea = await page.query_selector('textarea:visible, input[type="text"]:visible')
        if textarea:
            await textarea.fill('Draw a trendline from $420 to $450')
            await page.keyboard.press('Enter')
        else:
            print("No input field found, skipping command...")
        
        # Wait for agent response
        print("Waiting for agent to process...")
        await page.wait_for_timeout(5000)
        
        # Check if drawing primitive logs appear
        print("\n=== Console Logs Related to Drawing ===")
        drawing_logs = [log for log in console_logs if 'Drawing' in log['text'] or 'trendline' in log['text'].lower()]
        for log in drawing_logs:
            print(f"[{log['type']}] {log['text']}")
        
        # Try to manually trigger a drawing via console
        print("\n=== Manually adding drawing via console ===")
        
        # First check if everything is available
        check_result = await page.evaluate("""
            () => {
                const results = {
                    hasEnhancedControl: !!window.enhancedChartControl,
                    hasDrawingPrimitive: !!(window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive),
                    chartRef: !!window.chartRef
                };
                console.log('[TEST] Availability check:', results);
                return results;
            }
        """)
        print(f"Availability: {json.dumps(check_result, indent=2)}")
        
        # Now try to add a drawing
        result = await page.evaluate("""
            () => {
                // Try different ways to access the chart
                let chart = window.chartRef || (window.enhancedChartControl && window.enhancedChartControl.chart);
                let primitive = window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive;
                
                if (!primitive) {
                    // Try to get it from the series
                    const series = window.candlestickSeriesRef;
                    if (series && series._primitives) {
                        primitive = series._primitives[0];
                    }
                }
                
                if (primitive && chart) {
                    console.log('[TEST] Found primitive and chart');
                    
                    // Use hardcoded timestamps for testing
                    const now = Date.now() / 1000;
                    const startTime = now - 86400; // 1 day ago
                    const endTime = now;
                    
                    // Add a test trendline
                    const id = primitive.addTrendline(420, startTime, 450, endTime);
                    console.log('[TEST] Added trendline with ID:', id);
                    
                    // Check drawings
                    const drawings = primitive.getDrawings();
                    console.log('[TEST] Current drawings:', drawings);
                    
                    // Force multiple update attempts
                    if (chart.applyOptions) {
                        chart.applyOptions({});
                        console.log('[TEST] Called applyOptions');
                    }
                    
                    // Try to force series update
                    const series = window.candlestickSeriesRef;
                    if (series && series.update) {
                        const lastData = series.dataByIndex(series.data().length - 1);
                        if (lastData) {
                            series.update(lastData);
                            console.log('[TEST] Forced series update');
                        }
                    }
                    
                    return {
                        success: true,
                        drawingId: id,
                        drawingCount: drawings.length
                    };
                }
                
                return { 
                    success: false, 
                    error: 'Missing components',
                    hasChart: !!chart,
                    hasPrimitive: !!primitive
                };
            }
        """)
        
        print(f"\nManual drawing result: {json.dumps(result, indent=2)}")
        
        # Wait to see console output
        await page.wait_for_timeout(2000)
        
        # Print all DrawingPrimitive logs
        print("\n=== All DrawingPrimitive Console Logs ===")
        final_logs = [log for log in console_logs if '[Drawing' in log['text'] or '[TEST]' in log['text']]
        for log in final_logs:
            print(f"[{log['type']}] {log['text']}")
        
        # Take screenshot
        await page.screenshot(path=".playwright-mcp/drawing_debug_test.png")
        print("\nScreenshot saved to .playwright-mcp/drawing_debug_test.png")
        
        # Keep browser open for a bit to see results
        print("\nWaiting 5 seconds to observe results...")
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_drawing_with_debug())