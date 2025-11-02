const playwright = require('playwright');

async function debugDrawingPrimitive() {
  console.log('🐛 DEBUGGING DRAWING PRIMITIVE INITIALIZATION');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ 
    headless: false,
    args: ['--no-sandbox']
  });
  
  const page = await browser.newPage();
  
  // Listen to console logs from the page
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('DrawingPrimitive') || text.includes('trendline') || text.includes('Enhanced Chart')) {
      console.log(`[BROWSER] ${text}`);
    }
  });
  
  try {
    console.log('\n📍 Navigating to http://localhost:5174...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Check if DrawingPrimitive is initialized
    const drawingState = await page.evaluate(() => {
      const chartControl = window.enhancedChartControl;
      return {
        enhancedControlExists: !!chartControl,
        drawingPrimitiveExists: chartControl && chartControl.drawingPrimitive !== null && chartControl.drawingPrimitive !== undefined,
        chartRefExists: chartControl && chartControl.chartRef !== null && chartControl.chartRef !== undefined
      };
    });
    
    console.log('\n🔍 DRAWING STATE:');
    console.log(`   enhancedChartControl: ${drawingState.enhancedControlExists ? '✅ EXISTS' : '❌ NOT FOUND'}`);
    console.log(`   drawingPrimitive: ${drawingState.drawingPrimitiveExists ? '✅ INITIALIZED' : '❌ NULL/UNDEFINED'}`);
    console.log(`   chartRef: ${drawingState.chartRefExists ? '✅ EXISTS' : '❌ NOT FOUND'}`);
    
    // Try manual drawing test
    const manualTest = await page.evaluate(() => {
      const chartControl = window.enhancedChartControl;
      
      // Try to manually call a drawing function
      let manualDrawResult = null;
      if (chartControl && chartControl.drawingPrimitive) {
        try {
          chartControl.drawingPrimitive.addHorizontalLine(150, 'TEST SUPPORT', '#4CAF50');
          manualDrawResult = 'SUCCESS';
        } catch (e) {
          manualDrawResult = `ERROR: ${e.message}`;
        }
      } else {
        manualDrawResult = 'NO DRAWING PRIMITIVE';
      }
      
      return {
        manualDrawResult,
        drawingPrimitiveType: chartControl && chartControl.drawingPrimitive ? chartControl.drawingPrimitive.constructor.name : 'unknown'
      };
    });
    
    console.log('\n🧪 MANUAL DRAWING TEST (Direct API):');
    console.log(`   Result: ${manualTest.manualDrawResult}`);
    console.log(`   DrawingPrimitive type: ${manualTest.drawingPrimitiveType}`);
    
    // Take screenshot
    await page.screenshot({ path: 'debug_drawing_manual.png', fullPage: true });
    console.log('\n📸 Screenshot (after manual test): debug_drawing_manual.png');
    
    console.log('\n' + '='.repeat(60));
    console.log('🎯 DIAGNOSIS:');
    if (!drawingState.drawingPrimitiveExists) {
      console.log('❌ ROOT CAUSE: DrawingPrimitive is NOT initialized!');
      console.log('');
      console.log('💡 FIX REQUIRED:');
      console.log('   Check TradingChart.tsx line ~495:');
      console.log('   enhancedChartControl.setDrawingPrimitive(drawingPrimitive)');
      console.log('');
      console.log('   Verify DrawingPrimitive is created and attached.');
    } else {
      console.log('✅ DrawingPrimitive IS initialized');
      console.log(`📊 Manual test result: ${manualTest.manualDrawResult}`);
      if (manualTest.manualDrawResult === 'SUCCESS') {
        console.log('✅ Manual drawing WORKS! Issue is likely in command flow.');
      } else {
        console.log('❌ Manual drawing FAILED! Issue in DrawingPrimitive implementation.');
      }
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

debugDrawingPrimitive();
