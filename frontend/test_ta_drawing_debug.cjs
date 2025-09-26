// Enhanced Playwright test with debugging for TA drawing verification
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
  console.log('\n🧪 TA Drawing Debug Test (Playwright)');
  console.log('-------------------------------------');
  
  // 1) Fetch drawing commands from backend
  let chartCommands = [];
  try {
    chartCommands = await getChartCommands();
    console.log('✅ Received chart_commands from backend:', chartCommands);
  } catch (e) {
    console.error('❌ Failed to fetch chart_commands:', e.message);
    process.exit(1);
  }

  // 2) Launch browser and open frontend
  const browser = await chromium.launch({ 
    headless: false,  // Show browser for debugging
    devtools: true    // Open devtools
  });
  const page = await browser.newPage();
  
  // Add console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('🔴 Browser console error:', msg.text());
    }
  });
  
  page.on('pageerror', error => {
    console.log('🔴 Page error:', error.message);
  });

  try {
    console.log('\n📱 Loading frontend at http://localhost:5174...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded');
    
    // Wait a bit for React to initialize
    await page.waitForTimeout(3000);
    
    // Check what's available on window
    const windowProps = await page.evaluate(() => {
      const props = Object.keys(window).filter(key => 
        key.includes('chart') || key.includes('Chart') || 
        key.includes('enhanced') || key.includes('Enhanced') ||
        key.includes('control') || key.includes('Control')
      );
      return {
        props: props,
        hasEnhanced: typeof window.enhancedChartControl !== 'undefined',
        hasChartControl: typeof window.chartControlService !== 'undefined',
        hasWindow: typeof window !== 'undefined'
      };
    });
    
    console.log('\n🔍 Window analysis:');
    console.log('   Window defined:', windowProps.hasWindow);
    console.log('   enhancedChartControl:', windowProps.hasEnhanced);
    console.log('   chartControlService:', windowProps.hasChartControl);
    console.log('   Related properties:', windowProps.props);
    
    // Try to wait for enhancedChartControl with a longer timeout
    console.log('\n⏳ Waiting for enhancedChartControl (30s timeout)...');
    
    try {
      await page.waitForFunction(() => {
        return typeof window !== 'undefined' && 
               window.enhancedChartControl && 
               typeof window.enhancedChartControl.initialize === 'function';
      }, { timeout: 30000 });
      console.log('✅ enhancedChartControl is available');
    } catch (e) {
      console.log('⚠️ enhancedChartControl not found after 30s');
      
      // Check if we need to manually initialize it
      const initResult = await page.evaluate(() => {
        // Check if the service exists but needs initialization
        if (window.enhancedChartControl && !window.enhancedChartControl.initialize) {
          return 'Service exists but initialize method missing';
        }
        if (!window.enhancedChartControl) {
          // Try to find it in other locations
          if (window.chartControlService) {
            window.enhancedChartControl = window.chartControlService;
            return 'Found as chartControlService';
          }
          return 'Service not found anywhere';
        }
        return 'Unknown state';
      });
      console.log('   Init check result:', initResult);
    }

    // Try to execute commands anyway
    console.log('\n🎨 Attempting to execute drawing commands...');
    const joined = chartCommands.join(' ');
    
    const execResult = await page.evaluate(async (cmdStr) => {
      try {
        // Try different possible service names
        if (window.enhancedChartControl && window.enhancedChartControl.processEnhancedResponse) {
          await window.enhancedChartControl.processEnhancedResponse(cmdStr);
          return { success: true, method: 'enhancedChartControl.processEnhancedResponse' };
        }
        if (window.chartControlService && window.chartControlService.parseAgentResponse) {
          await window.chartControlService.parseAgentResponse(cmdStr);
          return { success: true, method: 'chartControlService.parseAgentResponse' };
        }
        return { success: false, error: 'No suitable method found' };
      } catch (e) {
        return { success: false, error: e.message };
      }
    }, joined);
    
    console.log('   Execution result:', execResult);
    
    // Wait for rendering
    await page.waitForTimeout(2000);
    
    // Check for drawings
    const drawingInfo = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl || window.chartControlService || {};
      return {
        drawings: ctrl.drawings ? ctrl.drawings.size : 'N/A',
        annotations: ctrl.annotations ? ctrl.annotations.size : 'N/A',
        hasChart: !!ctrl.getChartRef?.()
      };
    });
    
    console.log('\n📊 Drawing info:');
    console.log('   Drawings:', drawingInfo.drawings);
    console.log('   Annotations:', drawingInfo.annotations);
    console.log('   Chart available:', drawingInfo.hasChart);
    
    // Take screenshot
    await page.screenshot({ path: 'ta-drawing-debug.png', fullPage: true });
    console.log('\n📸 Screenshot saved: ta-drawing-debug.png');
    
    console.log('\n⏸️ Keeping browser open for 30 seconds for manual inspection...');
    console.log('   Check DevTools console for any errors');
    console.log('   Try running in console: window.enhancedChartControl');
    await page.waitForTimeout(30000);
    
  } catch (err) {
    console.error('\n💥 Test error:', err.message);
    console.error('Stack:', err.stack);
  } finally {
    await browser.close();
  }
})();