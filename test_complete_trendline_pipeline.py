#!/usr/bin/env python3
"""Test the complete trendline pipeline manually"""

import asyncio
from playwright.async_api import async_playwright

async def test_complete_pipeline():
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
        
        print("🚀 Testing Complete Trendline Drawing Pipeline")
        print("=" * 60)
        
        await page.goto("http://localhost:5174")
        await page.wait_for_timeout(5000)
        
        # Clear initial logs
        console_logs.clear()
        
        print("\n1. Testing Agent Response Parser...")
        
        # Test the parser with the exact JSON format the agent generates
        parser_result = await page.evaluate("""
            () => {
                // Import the AgentResponseParser (assuming it's globally available or imported)
                const agentResponse = `I'll help you draw a trendline on the TSLA chart.

{"intent":"chart_command","action":"draw_trendline","symbol":"TSLA","start":{"time":"yesterday","price":425},"end":{"time":"today","price":445},"confidence":"high"}

The trendline has been added to show the upward trend from $425 to $445.`;

                console.log('[TEST] Testing AgentResponseParser with:', agentResponse);
                
                // Test containsDrawingCommands
                const containsCommands = window.AgentResponseParser ? 
                    window.AgentResponseParser.containsDrawingCommands(agentResponse) : 
                    'AgentResponseParser not available';
                
                // Test parseResponse
                const parsedCommands = window.AgentResponseParser ? 
                    window.AgentResponseParser.parseResponse(agentResponse) : 
                    'AgentResponseParser not available';
                
                console.log('[TEST] Contains commands:', containsCommands);
                console.log('[TEST] Parsed commands:', parsedCommands);
                
                return {
                    containsCommands,
                    parsedCommands,
                    parserAvailable: !!window.AgentResponseParser
                };
            }
        """)
        
        print(f"   Parser Result: {parser_result}")
        
        print("\n2. Testing Manual Chart Command Processing...")
        
        # Test manual command processing through enhancedChartControl
        manual_result = await page.evaluate("""
            () => {
                // Use the exact command format we expect from the parser
                const now = Math.floor(Date.now() / 1000);
                const yesterday = now - (24 * 60 * 60);
                const command = `TRENDLINE:425:${yesterday}:445:${now}`;
                
                console.log('[TEST] Processing manual command:', command);
                
                if (window.enhancedChartControl) {
                    return window.enhancedChartControl.processEnhancedResponse(command)
                        .then(result => {
                            console.log('[TEST] Manual command result:', result);
                            
                            // Check primitive state
                            const primitive = window.enhancedChartControl.drawingPrimitive;
                            const drawings = primitive ? primitive.getDrawings() : [];
                            
                            return {
                                success: true,
                                result: result,
                                drawingCount: drawings.length,
                                drawings: drawings
                            };
                        })
                        .catch(error => {
                            console.error('[TEST] Manual command error:', error);
                            return { success: false, error: error.message };
                        });
                } else {
                    return { success: false, error: 'enhancedChartControl not available' };
                }
            }
        """)
        
        print(f"   Manual Command Result: {manual_result}")
        
        await page.wait_for_timeout(3000)
        
        print("\n3. Testing ChatKit Integration Fix...")
        
        # Test the fixed ChatKit onMessage flow
        chatkit_result = await page.evaluate("""
            () => {
                // Simulate what ChatKit should do when it receives an agent message
                const agentMessage = {
                    role: 'assistant',
                    content: `I'll draw that trendline for you.

{"intent":"chart_command","action":"draw_trendline","symbol":"TSLA","start":{"time":"yesterday","price":430},"end":{"time":"today","price":450},"confidence":"high"}

The trendline shows the trend from $430 to $450.`
                };
                
                console.log('[TEST] Simulating ChatKit message processing...');
                
                // Check if AgentResponseParser is available
                if (!window.AgentResponseParser) {
                    return { success: false, error: 'AgentResponseParser not available' };
                }
                
                // Simulate the enhanced message processing logic
                if (window.AgentResponseParser.containsDrawingCommands(agentMessage.content)) {
                    const chartCommands = window.AgentResponseParser.parseResponse(agentMessage.content);
                    console.log('[TEST] ChatKit would send commands:', chartCommands);
                    
                    if (chartCommands.length > 0 && window.enhancedChartControl) {
                        // Process the first command
                        return window.enhancedChartControl.processEnhancedResponse(chartCommands[0])
                            .then(result => {
                                const primitive = window.enhancedChartControl.drawingPrimitive;
                                const drawings = primitive ? primitive.getDrawings() : [];
                                
                                return {
                                    success: true,
                                    commandsSent: chartCommands,
                                    processingResult: result,
                                    finalDrawingCount: drawings.length
                                };
                            });
                    }
                }
                
                return { success: false, error: 'No drawing commands found' };
            }
        """)
        
        print(f"   ChatKit Integration Result: {chatkit_result}")
        
        await page.wait_for_timeout(2000)
        
        print("\n4. Checking Final State...")
        
        # Check the final state of the drawing system
        final_state = await page.evaluate("""
            () => {
                const primitive = window.enhancedChartControl?.drawingPrimitive;
                if (primitive) {
                    const drawings = primitive.getDrawings();
                    return {
                        hasPrimitive: true,
                        drawingCount: drawings.length,
                        drawings: drawings.map(d => ({
                            id: d.id,
                            type: d.type,
                            startPrice: d.data.startPrice,
                            endPrice: d.data.endPrice
                        }))
                    };
                }
                return { hasPrimitive: false };
            }
        """)
        
        print(f"   Final Drawing State: {final_state}")
        
        # Filter and display relevant console logs
        print("\n5. Console Logs:")
        print("-" * 30)
        relevant_logs = [log for log in console_logs if 
                        '[TEST]' in log['text'] or 
                        '[ChatKit]' in log['text'] or
                        '[AgentParser]' in log['text'] or
                        '[Enhanced Chart]' in log['text'] or
                        '[DrawingRenderer]' in log['text'] or
                        'trendline' in log['text'].lower()]
        
        for log in relevant_logs[-20:]:  # Show last 20 relevant logs
            print(f"   [{log['type']}] {log['text']}")
        
        # Take final screenshot
        await page.screenshot(path=".playwright-mcp/complete_pipeline_test.png")
        print(f"\n📸 Screenshot saved: .playwright-mcp/complete_pipeline_test.png")
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 PIPELINE TEST SUMMARY:")
        print(f"   ✅ Parser Available: {parser_result.get('parserAvailable', False)}")
        print(f"   ✅ Manual Commands: {manual_result.get('success', False)}")
        print(f"   ✅ ChatKit Integration: {chatkit_result.get('success', False)}")
        print(f"   ✅ Final Drawings: {final_state.get('drawingCount', 0)} drawings")
        
        if final_state.get('drawingCount', 0) > 0:
            print("   🎉 SUCCESS: Trendlines can be drawn!")
        else:
            print("   ⚠️  ISSUE: No drawings persisted")
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())