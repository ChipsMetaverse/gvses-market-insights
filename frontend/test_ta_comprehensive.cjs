// Comprehensive test with better debugging
const { chromium } = require('playwright');

async function getChartCommands(query = 'Show NVDA with support and resistance levels, fibonacci and trendline') {
  const res = await fetch('http://localhost:8000/api/agent/orchestrate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  if (!res.ok) {
    throw new Error(`Agent orchestrate failed: ${res.status} ${res.statusText}`);
  }
  const data = await res.json();
  const cmds = data.chart_commands || (data.data && data.data.chart_commands) || [];
  if (!Array.isArray(cmds) || cmds.length === 0) {
    throw new Error('No chart_commands returned from agent');
  }
  return cmds;
}

(async () => {
  console.log('\n🧪 Comprehensive TA Drawing Test');
  console.log('---------------------------------');
  
  // 1) Fetch drawing commands from backend
  let chartCommands = [];
  try {
    chartCommands = await getChartCommands();
    console.log('✅ Received chart_commands:', chartCommands);
  } catch (e) {
    console.error('❌ Failed to fetch chart_commands:', e.message);
    process.exit(1);
  }

  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Add console logging
  page.on('console', msg => {
    if (msg.text().includes('Error') || msg.text().includes('error')) {
      console.log('🔴 Browser error:', msg.text());
    }
  });
  
  try {
    console.log('\n📱 Loading app...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(7000); // Longer wait for full initialization
    
    // Wait for enhancedChartControl
    const ready = await page.evaluate(() => {
      return window.enhancedChartControl && 
             window.enhancedChartControlReady && 
             window.enhancedChartControl.getChartRef();
    });
    
    if (!ready) {
      console.log('❌ Not ready after 7 seconds');
      process.exit(1);
    }
    
    console.log('✅ Chart and control ready');
    
    // Execute commands one by one to see which ones work
    console.log('\n🎨 Executing commands one by one:');
    
    for (const cmd of chartCommands) {
      const result = await page.evaluate(async (command) => {
        const ctrl = window.enhancedChartControl;
        const before = {
          drawings: ctrl.drawings ? ctrl.drawings.size : 0,
          annotations: ctrl.annotations ? ctrl.annotations.size : 0
        };
        
        try {
          // Execute single command
          await ctrl.processEnhancedResponse(command);
        } catch (e) {
          return { command, error: e.message };
        }
        
        const after = {
          drawings: ctrl.drawings ? ctrl.drawings.size : 0,
          annotations: ctrl.annotations ? ctrl.annotations.size : 0
        };
        
        return {
          command,
          before,
          after,
          added: (after.drawings - before.drawings) + (after.annotations - before.annotations)
        };
      }, cmd);
      
      if (result.error) {
        console.log(`   ❌ ${cmd}: Error - ${result.error}`);
      } else if (result.added > 0) {
        console.log(`   ✅ ${cmd}: Added ${result.added} item(s)`);
      } else {
        console.log(`   ⚠️  ${cmd}: No change`);
      }
    }
    
    // Final totals
    const final = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      return {
        drawings: ctrl.drawings ? ctrl.drawings.size : 0,
        annotations: ctrl.annotations ? ctrl.annotations.size : 0
      };
    });
    
    console.log('\n📊 Final totals:');
    console.log(`   Drawings: ${final.drawings}`);
    console.log(`   Annotations: ${final.annotations}`);
    
    if (final.drawings > 0 || final.annotations > 0) {
      console.log('\n✅ Technical Analysis Drawing Feature is WORKING!');
      await page.screenshot({ path: 'ta-drawing-success.png', fullPage: true });
      console.log('📸 Screenshot saved: ta-drawing-success.png');
    } else {
      console.log('\n❌ No drawings were created');
      await page.screenshot({ path: 'ta-drawing-failure.png', fullPage: true });
      console.log('📸 Screenshot saved: ta-drawing-failure.png');
    }
    
    // Keep browser open for inspection
    console.log('\n⏸️ Keeping browser open for 15 seconds...');
    await page.waitForTimeout(15000);
    
  } catch (err) {
    console.error('\n💥 Test error:', err.message);
  } finally {
    await browser.close();
  }
})();