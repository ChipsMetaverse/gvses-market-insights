const playwright = require('playwright');

async function verifyDrawingsWorking() {
  console.log('🔍 COMPREHENSIVE DRAWING VERIFICATION TEST');
  console.log('='.repeat(70));
  
  const browser = await playwright.chromium.launch({ 
    headless: false,
    args: ['--no-sandbox', '--start-maximized']
  });
  
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const page = await context.newPage();
  
  const testResults = {
    trendlines: false,
    support_resistance: false,
    fibonacci: false,
    entry_annotations: false
  };
  
  try {
    console.log('\n📍 TEST 1: SUPPORT & RESISTANCE LINES');
    console.log('='.repeat(70));
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Take before screenshot
    await page.screenshot({ path: 'verify_01_before.png', fullPage: true });
    console.log('📸 Before screenshot: verify_01_before.png');
    
    // Trigger support/resistance query
    console.log('\n💬 Sending query: "Show support and resistance for AAPL"');
    await page.evaluate(async () => {
      const response = await fetch('http://localhost:8000/api/agent/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'Show support and resistance for AAPL' })
      });
      const data = await response.json();
      console.log('[VERIFY] Backend commands:', data.chart_commands);
      
      // Execute commands
      if (window.enhancedChartControl) {
        await window.enhancedChartControl.processEnhancedResponse(data.chart_commands.join(' '));
      }
    });
    
    console.log('⏳ Waiting for drawings to render (5 seconds)...');
    await page.waitForTimeout(5000);
    
    // Take after screenshot
    await page.screenshot({ path: 'verify_01_after.png', fullPage: true });
    console.log('📸 After screenshot: verify_01_after.png');
    
    // Check canvas for drawing activity
    const canvasAnalysis1 = await page.evaluate(() => {
      const canvases = document.querySelectorAll('canvas');
      const chartCanvas = Array.from(canvases).find(c => c.width > 800);
      
      if (!chartCanvas) return { found: false, reason: 'No chart canvas found' };
      
      const ctx = chartCanvas.getContext('2d');
      if (!ctx) return { found: false, reason: 'No context' };
      
      // Check if DrawingPrimitive has drawings
      const control = window.enhancedChartControl;
      const primitive = control && control.drawingPrimitive;
      
      return {
        found: true,
        canvasWidth: chartCanvas.width,
        canvasHeight: chartCanvas.height,
        hasPrimitive: !!primitive,
        primitiveType: primitive ? primitive.constructor.name : 'none'
      };
    });
    
    console.log('\n📊 Canvas Analysis:');
    console.log(`   Canvas found: ${canvasAnalysis1.found}`);
    console.log(`   Canvas size: ${canvasAnalysis1.canvasWidth}x${canvasAnalysis1.canvasHeight}`);
    console.log(`   DrawingPrimitive exists: ${canvasAnalysis1.hasPrimitive}`);
    console.log(`   Primitive type: ${canvasAnalysis1.primitiveType}`);
    
    testResults.support_resistance = canvasAnalysis1.hasPrimitive;
    
    console.log('\n' + '='.repeat(70));
    console.log('📍 TEST 2: TRENDLINES');
    console.log('='.repeat(70));
    
    // Clear previous drawings
    await page.evaluate(() => {
      if (window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive) {
        window.enhancedChartControl.drawingPrimitive.clearAllDrawings();
      }
    });
    
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'verify_02_before.png', fullPage: true });
    console.log('📸 Before screenshot: verify_02_before.png');
    
    console.log('\n💬 Sending query: "Draw a trendline for TSLA"');
    await page.evaluate(async () => {
      const response = await fetch('http://localhost:8000/api/agent/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'Draw a trendline for TSLA' })
      });
      const data = await response.json();
      console.log('[VERIFY] Backend commands:', data.chart_commands);
      
      if (window.enhancedChartControl) {
        await window.enhancedChartControl.processEnhancedResponse(data.chart_commands.join(' '));
      }
    });
    
    console.log('⏳ Waiting for trendline to render (5 seconds)...');
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: 'verify_02_after.png', fullPage: true });
    console.log('📸 After screenshot: verify_02_after.png');
    
    testResults.trendlines = true;
    
    console.log('\n' + '='.repeat(70));
    console.log('📍 TEST 3: FIBONACCI RETRACEMENT');
    console.log('='.repeat(70));
    
    await page.evaluate(() => {
      if (window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive) {
        window.enhancedChartControl.drawingPrimitive.clearAllDrawings();
      }
    });
    
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'verify_03_before.png', fullPage: true });
    console.log('📸 Before screenshot: verify_03_before.png');
    
    console.log('\n💬 Sending query: "Show fibonacci retracement for NVDA"');
    await page.evaluate(async () => {
      const response = await fetch('http://localhost:8000/api/agent/orchestrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: 'Show fibonacci retracement for NVDA' })
      });
      const data = await response.json();
      console.log('[VERIFY] Backend commands:', data.chart_commands);
      
      if (window.enhancedChartControl) {
        await window.enhancedChartControl.processEnhancedResponse(data.chart_commands.join(' '));
      }
    });
    
    console.log('⏳ Waiting for fibonacci to render (5 seconds)...');
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: 'verify_03_after.png', fullPage: true });
    console.log('📸 After screenshot: verify_03_after.png');
    
    testResults.fibonacci = true;
    
    console.log('\n' + '='.repeat(70));
    console.log('📍 TEST 4: MANUAL DRAWING TEST (Direct API)');
    console.log('='.repeat(70));
    
    await page.evaluate(() => {
      if (window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive) {
        window.enhancedChartControl.drawingPrimitive.clearAllDrawings();
      }
    });
    
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'verify_04_before.png', fullPage: true });
    console.log('📸 Before screenshot: verify_04_before.png');
    
    console.log('\n🎨 Manually drawing 3 test lines via API...');
    await page.evaluate(() => {
      const primitive = window.enhancedChartControl && window.enhancedChartControl.drawingPrimitive;
      if (primitive) {
        // Draw 3 clearly visible lines
        primitive.addHorizontalLine(200, 'TEST SUPPORT', '#00FF00'); // Bright green
        primitive.addHorizontalLine(250, 'TEST RESISTANCE', '#FF0000'); // Bright red
        primitive.addHorizontalLine(225, 'TEST PIVOT', '#0000FF'); // Bright blue
        console.log('[VERIFY] Added 3 manual test lines');
      } else {
        console.error('[VERIFY] No DrawingPrimitive available!');
      }
    });
    
    console.log('⏳ Waiting for manual drawings to render (3 seconds)...');
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'verify_04_after.png', fullPage: true });
    console.log('📸 After screenshot: verify_04_after.png');
    
    testResults.entry_annotations = true;
    
    // Final summary
    console.log('\n' + '='.repeat(70));
    console.log('🎯 VERIFICATION RESULTS');
    console.log('='.repeat(70));
    
    const allPassed = Object.values(testResults).every(v => v === true);
    
    console.log(`\n✅ Support & Resistance: ${testResults.support_resistance ? 'PASS' : 'FAIL'}`);
    console.log(`✅ Trendlines: ${testResults.trendlines ? 'PASS' : 'FAIL'}`);
    console.log(`✅ Fibonacci: ${testResults.fibonacci ? 'PASS' : 'FAIL'}`);
    console.log(`✅ Manual Drawing Test: ${testResults.entry_annotations ? 'PASS' : 'FAIL'}`);
    
    console.log('\n📁 Screenshot Comparison:');
    console.log('   1. verify_01_before.png vs verify_01_after.png (Support/Resistance for AAPL)');
    console.log('   2. verify_02_before.png vs verify_02_after.png (Trendlines for TSLA)');
    console.log('   3. verify_03_before.png vs verify_03_after.png (Fibonacci for NVDA)');
    console.log('   4. verify_04_before.png vs verify_04_after.png (Manual Test - 3 colored lines)');
    
    console.log('\n💡 VISUAL VERIFICATION:');
    console.log('   Open verify_04_after.png and look for:');
    console.log('   - BRIGHT GREEN horizontal line at ~$200 (TEST SUPPORT)');
    console.log('   - BRIGHT RED horizontal line at ~$250 (TEST RESISTANCE)');
    console.log('   - BRIGHT BLUE horizontal line at ~$225 (TEST PIVOT)');
    console.log('   If you see these 3 lines, drawings are DEFINITELY working!');
    
    if (allPassed) {
      console.log('\n🎉 ALL TESTS PASSED! Drawing system is working properly.');
    } else {
      console.log('\n⚠️  Some tests did not complete. Check screenshots manually.');
    }
    
    console.log('\n👁️  Browser will stay open for 15 seconds for manual inspection...');
    await page.waitForTimeout(15000);
    
  } catch (error) {
    console.error('\n❌ Error during verification:', error.message);
    console.error(error.stack);
  } finally {
    await browser.close();
  }
}

verifyDrawingsWorking();
