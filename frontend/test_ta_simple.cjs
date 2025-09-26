// Minimal test to verify drawing commands execution
const { chromium } = require('playwright');

(async () => {
  console.log('\n🧪 Simple TA Drawing Test');
  console.log('-------------------------');
  
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(5000); // Wait for app to load
    
    // Wait for enhancedChartControl
    const ready = await page.evaluate(() => {
      return window.enhancedChartControl && window.enhancedChartControlReady;
    });
    
    if (!ready) {
      console.log('❌ enhancedChartControl not ready after 5 seconds');
      process.exit(1);
    }
    
    console.log('✅ enhancedChartControl is ready');
    
    // Execute simple drawing commands
    const result = await page.evaluate(async () => {
      const ctrl = window.enhancedChartControl;
      
      // Check initial state
      const before = {
        drawings: ctrl.drawings ? ctrl.drawings.size : 0,
        annotations: ctrl.annotations ? ctrl.annotations.size : 0
      };
      
      // Execute a simple support level command
      try {
        await ctrl.processEnhancedResponse('SUPPORT:150.00');
      } catch (e) {
        return { error: e.message };
      }
      
      // Check after state
      const after = {
        drawings: ctrl.drawings ? ctrl.drawings.size : 0,
        annotations: ctrl.annotations ? ctrl.annotations.size : 0
      };
      
      return { before, after };
    });
    
    console.log('Result:', result);
    
    if (result.error) {
      console.log('❌ Error:', result.error);
    } else if (result.after.drawings > result.before.drawings || 
               result.after.annotations > result.before.annotations) {
      console.log('✅ Drawing commands working!');
      console.log(`   Drawings: ${result.before.drawings} → ${result.after.drawings}`);
      console.log(`   Annotations: ${result.before.annotations} → ${result.after.annotations}`);
    } else {
      console.log('❌ No drawings added');
    }
    
    // Keep browser open for inspection
    await page.waitForTimeout(10000);
    
  } catch (err) {
    console.error('💥 Error:', err.message);
  } finally {
    await browser.close();
  }
})();