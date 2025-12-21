#!/usr/bin/env python3
"""Test what chart commands are being parsed from trendline command"""

import asyncio
from playwright.async_api import async_playwright

async def test_chart_command_parsing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Navigating to application...")
        await page.goto("http://localhost:5174")
        
        # Wait for chart to load
        await page.wait_for_timeout(3000)
        
        print("\n=== Testing what chart commands are parsed from TRENDLINE ===")
        
        # Test what parseAgentResponse returns for trendline command
        result = await page.evaluate("""
            () => {
                const trendlineCommand = "TRENDLINE:430:1760500000:450:1760650000";
                console.log('[TEST] Testing parseAgentResponse for:', trendlineCommand);
                
                // Test the base service parseAgentResponse method
                if (window.chartControlService && window.chartControlService.parseAgentResponse) {
                    return window.chartControlService.parseAgentResponse(trendlineCommand)
                        .then(commands => {
                            console.log('[TEST] parseAgentResponse result:', commands);
                            return { 
                                success: true, 
                                chartCommands: commands,
                                commandCount: commands.length
                            };
                        })
                        .catch(error => {
                            console.error('[TEST] parseAgentResponse error:', error);
                            return { success: false, error: error.message };
                        });
                } else {
                    return { success: false, error: 'chartControlService.parseAgentResponse not available' };
                }
            }
        """)
        
        print(f"parseAgentResponse result: {result}")
        
        # Also test what the enhanced control parses separately  
        print("\n=== Testing parseDrawingCommands vs parseAgentResponse ===")
        
        result2 = await page.evaluate("""
            () => {
                const command = "TRENDLINE:430:1760500000:450:1760650000";
                
                if (window.enhancedChartControl) {
                    // Test drawing command parsing
                    const drawingCommands = window.enhancedChartControl.parseDrawingCommands 
                        ? window.enhancedChartControl.parseDrawingCommands(command) 
                        : 'parseDrawingCommands not accessible';
                    
                    console.log('[TEST] Drawing commands parsed:', drawingCommands);
                    
                    return { 
                        success: true,
                        drawingCommands: Array.isArray(drawingCommands) ? drawingCommands.length : drawingCommands
                    };
                } else {
                    return { success: false, error: 'enhancedChartControl not available' };
                }
            }
        """)
        
        print(f"Drawing commands result: {result2}")
        
        await page.wait_for_timeout(2000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_chart_command_parsing())