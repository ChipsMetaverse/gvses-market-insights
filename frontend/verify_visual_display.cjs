const playwright = require('playwright');

async function verifyDrawings() {
  console.log('🔍 VERIFYING FRONTEND DRAWING DISPLAY');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ 
    headless: false,
    args: ['--no-sandbox']
  });
  
  const page = await browser.newPage();
  
  try {
    // Navigate to app
    console.log('\n📍 Navigating to http://localhost:5174...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Take initial screenshot
    await page.screenshot({ path: 'verify_initial.png', fullPage: true });
    console.log('📸 Initial screenshot: verify_initial.png');
    
    // Check if chart exists
    const chartExists = await page.locator('canvas').first().isVisible();
    console.log(`\n✅ Chart canvas: ${chartExists ? 'VISIBLE' : 'NOT FOUND'}`);
    
    // Check for pattern cards (these trigger drawings)
    const patternCount = await page.locator('[class*="pattern"]').count();
    console.log(`📊 Pattern cards found: ${patternCount}`);
    
    // Try to hover over a pattern to trigger drawing
    if (patternCount > 0) {
      console.log('\n🖱️  Hovering over first pattern to trigger drawing...');
      await page.locator('[class*="pattern"]').first().hover();
      await page.waitForTimeout(2000);
      
      await page.screenshot({ path: 'verify_pattern_hover.png', fullPage: true });
      console.log('📸 Pattern hover screenshot: verify_pattern_hover.png');
    }
    
    // Check for SVG elements (drawings might be SVG)
    const svgCount = await page.locator('svg').count();
    console.log(`\n🎨 SVG elements found: ${svgCount}`);
    
    // Check for canvas overlays (drawings might be on canvas)
    const canvasCount = await page.locator('canvas').count();
    console.log(`🖼️  Canvas elements found: ${canvasCount}`);
    
    // Try to find any line elements
    const lineElements = await page.evaluate(() => {
      // Check for various line-related elements
      const svgLines = document.querySelectorAll('line, path[stroke]');
      const canvases = document.querySelectorAll('canvas');
      
      return {
        svgLines: svgLines.length,
        canvasElements: canvases.length,
        chartContainer: !!document.querySelector('[class*="tv-lightweight-charts"]')
      };
    });
    
    console.log(`\n📏 SVG lines/paths: ${lineElements.svgLines}`);
    console.log(`📊 Lightweight Charts container: ${lineElements.chartContainer ? 'FOUND' : 'NOT FOUND'}`);
    
    // Check if DrawingPrimitive is being used
    const drawingInfo = await page.evaluate(() => {
      // Try to access window objects
      return {
        hasEnhancedControl: typeof window.enhancedChartControl !== 'undefined',
        hasDrawingPrimitive: typeof window.DrawingPrimitive !== 'undefined'
      };
    });
    
    console.log(`\n🔧 Enhanced Chart Control: ${drawingInfo.hasEnhancedControl ? 'AVAILABLE' : 'NOT EXPOSED'}`);
    console.log(`🔧 Drawing Primitive: ${drawingInfo.hasDrawingPrimitive ? 'AVAILABLE' : 'NOT EXPOSED'}`);
    
    // Wait a bit and take final screenshot
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'verify_final.png', fullPage: true });
    console.log('\n📸 Final screenshot: verify_final.png');
    
    console.log('\n' + '='.repeat(60));
    console.log('🎯 ASSESSMENT:');
    console.log('='.repeat(60));
    
    if (chartExists && patternCount > 0) {
      console.log('✅ Chart is displaying');
      console.log('✅ Patterns are detected');
      console.log('⚠️  Check screenshots to verify if lines are visible');
      console.log('\n💡 Drawings may be:');
      console.log('   1. On canvas (not easily inspectable)');
      console.log('   2. Rendered by Lightweight Charts internally');
      console.log('   3. Visible but not as DOM elements');
    } else {
      console.log('❌ Chart or patterns not found');
    }
    
    console.log('\n📖 NEXT STEPS:');
    console.log('   1. Review screenshots (verify_*.png)');
    console.log('   2. Look for colored horizontal lines');
    console.log('   3. Look for trendlines on chart');
    console.log('   4. Check if pattern boundary boxes are visible');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await browser.close();
  }
}

verifyDrawings();
