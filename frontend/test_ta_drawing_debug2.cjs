// Debug test to understand what's happening with drawing commands
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
  console.log('\n🧪 TA Drawing Debug Test v2');
  console.log('-------------------------------------');
  
  // 1) Fetch drawing commands from backend
  let chartCommands = [];
  try {
    chartCommands = await getChartCommands();
    console.log('✅ Received chart_commands from backend:');
    chartCommands.forEach(cmd => console.log(`   - ${cmd}`));
  } catch (e) {
    console.error('❌ Failed to fetch chart_commands:', e.message);
    process.exit(1);
  }

  // 2) Launch browser
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  const page = await browser.newPage();
  
  // Add console logging
  page.on('console', msg => {
    console.log('🔵 Browser console:', msg.text());
  });
  
  try {
    console.log('\n📱 Loading frontend...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Wait for enhancedChartControl
    await page.waitForFunction(() => {
      return typeof window !== 'undefined' && 
             window.enhancedChartControl && 
             window.enhancedChartControlReady === true;
    }, { timeout: 30000 });
    console.log('✅ enhancedChartControl is ready');
    
    // Check initial state
    const initialState = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      return {
        hasControl: !!ctrl,
        hasProcessMethod: !!(ctrl && ctrl.processEnhancedResponse),
        hasDrawings: !!(ctrl && ctrl.drawings),
        hasAnnotations: !!(ctrl && ctrl.annotations),
        drawingsCount: ctrl && ctrl.drawings ? ctrl.drawings.size : 'N/A',
        annotationsCount: ctrl && ctrl.annotations ? ctrl.annotations.size : 'N/A',
        chartRef: !!(ctrl && ctrl.getChartRef && ctrl.getChartRef())
      };
    });
    console.log('\n📊 Initial state:');
    Object.entries(initialState).forEach(([key, value]) => {
      console.log(`   ${key}: ${value}`);
    });
    
    // Execute commands one by one and log results
    console.log('\n🎨 Executing commands one by one:');
    const joined = chartCommands.join(' ');
    
    const executionResult = await page.evaluate(async (cmdStr) => {
      const ctrl = window.enhancedChartControl;
      const results = [];
      
      try {
        // Execute the commands
        console.log('Calling processEnhancedResponse with:', cmdStr);
        const commandResults = await ctrl.processEnhancedResponse(cmdStr);
        console.log('processEnhancedResponse returned:', commandResults);
        
        // Check the state after execution
        const afterState = {
          drawingsCount: ctrl.drawings ? ctrl.drawings.size : 0,
          annotationsCount: ctrl.annotations ? ctrl.annotations.size : 0,
          commandResultsLength: commandResults ? commandResults.length : 0
        };
        
        return {
          success: true,
          commandResults: commandResults || [],
          afterState
        };
      } catch (error) {
        return {
          success: false,
          error: error.message,
          stack: error.stack
        };
      }
    }, joined);
    
    console.log('\n📋 Execution result:');
    if (executionResult.success) {
      console.log('   ✅ Commands executed successfully');
      console.log('   Command results:', executionResult.commandResults);
      console.log('   After state:', executionResult.afterState);
    } else {
      console.log('   ❌ Execution failed');
      console.log('   Error:', executionResult.error);
      console.log('   Stack:', executionResult.stack);
    }
    
    // Wait for rendering
    await page.waitForTimeout(2000);
    
    // Final check
    const finalState = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      return {
        drawingsCount: ctrl && ctrl.drawings ? ctrl.drawings.size : 0,
        annotationsCount: ctrl && ctrl.annotations ? ctrl.annotations.size : 0
      };
    });
    
    console.log('\n📊 Final state:');
    console.log('   Drawings:', finalState.drawingsCount);
    console.log('   Annotations:', finalState.annotationsCount);
    
    // Take screenshot
    await page.screenshot({ path: 'ta-drawing-debug2.png', fullPage: true });
    console.log('\n📸 Screenshot saved: ta-drawing-debug2.png');
    
    console.log('\n⏸️ Keeping browser open for 30 seconds...');
    console.log('   Check DevTools console for errors');
    console.log('   Try running: window.enhancedChartControl.processEnhancedResponse("SUPPORT:150")');
    await page.waitForTimeout(30000);
    
  } catch (err) {
    console.error('\n💥 Test error:', err.message);
  } finally {
    await browser.close();
  }
})();