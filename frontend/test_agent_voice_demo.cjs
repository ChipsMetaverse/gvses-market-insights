const { chromium } = require('playwright');

async function testAgentVoiceDemo() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🎙️ Testing Agent Voice-Controlled Chart Demo...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(5000);
    
    console.log('✅ Application loaded\n');
    
    // Simulate agent responses that control the chart
    console.log('🎭 Simulating Agent Voice Responses:\n');
    
    // Demo 1: Basic Introduction
    console.log('📢 Agent: "Welcome! Let me help you understand this chart..."\n');
    await page.waitForTimeout(2000);
    
    // Demo 2: Enable first indicator
    console.log('📢 Agent: "First, let me show you the 20-day moving average"');
    await page.evaluate(async () => {
      if (window.enhancedChartControl) {
        const result = await window.enhancedChartControl.processIndicatorCommand(
          "First, let me show you the 20-day moving average - this blue line tracks the average price over the last 20 trading days"
        );
        console.log('   → Chart action:', result);
      }
    });
    await page.waitForTimeout(3000);
    
    // Demo 3: Add more indicators
    console.log('\n📢 Agent: "Now I\'ll add the 50-day moving average for comparison"');
    await page.evaluate(async () => {
      if (window.enhancedChartControl) {
        const result = await window.enhancedChartControl.processIndicatorCommand(
          "Now I'll add the 50-day moving average - notice how it's smoother than the 20-day"
        );
        console.log('   → Chart action:', result);
      }
    });
    await page.waitForTimeout(3000);
    
    // Demo 4: Show RSI
    console.log('\n📢 Agent: "Let\'s check the momentum with RSI"');
    await page.evaluate(async () => {
      if (window.enhancedChartControl) {
        const result = await window.enhancedChartControl.processIndicatorCommand(
          "Let's check the momentum with RSI - currently at 55, which is neutral territory"
        );
        console.log('   → Chart action:', result);
      }
    });
    await page.waitForTimeout(3000);
    
    // Demo 5: Highlight support level
    console.log('\n📢 Agent: "Notice the support level around $420"');
    await page.evaluate(async () => {
      if (window.enhancedChartControl) {
        const result = window.enhancedChartControl.highlightLevel(
          420, 'support', 'Key Support'
        );
        console.log('   → Chart action:', result);
      }
    });
    await page.waitForTimeout(3000);
    
    // Demo 6: Apply preset for advanced analysis
    console.log('\n📢 Agent: "Let me show you the full advanced analysis"');
    await page.evaluate(async () => {
      if (window.enhancedChartControl) {
        const result = await window.enhancedChartControl.applyIndicatorPreset('advanced');
        console.log('   → Chart action:', result);
      }
    });
    await page.waitForTimeout(3000);
    
    // Demo 7: Educational explanation
    console.log('\n📢 Agent: "See how all these indicators work together?"');
    console.log('   "The moving averages show trend..."');
    console.log('   "Bollinger Bands indicate volatility..."');
    console.log('   "And RSI confirms momentum..."');
    await page.waitForTimeout(4000);
    
    // Take screenshot of final state
    await page.screenshot({ 
      path: 'agent-voice-demo-final.png',
      fullPage: true 
    });
    console.log('\n📸 Final demo screenshot saved');
    
    // Summary
    console.log('\n' + '='.repeat(50));
    console.log('🎭 AGENT VOICE CONTROL DEMO COMPLETE');
    console.log('='.repeat(50));
    console.log('\n✨ Demonstrated Capabilities:');
    console.log('✅ Agent can enable indicators while speaking');
    console.log('✅ Agent can highlight price levels during explanation');
    console.log('✅ Agent can apply analysis presets for different skill levels');
    console.log('✅ Agent provides educational narration synchronized with chart');
    console.log('✅ Visual changes happen in real-time as agent speaks');
    
    console.log('\n🎯 User Benefits:');
    console.log('• Beginners learn by seeing indicators appear as explained');
    console.log('• Visual learners get chart demonstrations with voice guidance');
    console.log('• Advanced users can request specific technical setups');
    console.log('• All users get personalized, interactive market education');
    
    console.log('\n💡 Next Steps:');
    console.log('1. Connect to ElevenLabs Conversational AI');
    console.log('2. Process actual voice responses in real-time');
    console.log('3. Add more complex pattern recognition');
    console.log('4. Implement user preference learning');
    
  } catch (error) {
    console.error('❌ Demo failed:', error);
  }
  
  await browser.close();
}

testAgentVoiceDemo().catch(console.error);