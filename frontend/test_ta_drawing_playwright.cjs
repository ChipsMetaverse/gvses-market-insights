// Playwright smoke test: verifies technical analysis drawing commands render on the chart
// Prereqs:
// - Backend running at http://localhost:8000
// - Frontend dev server running at http://localhost:5174

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
  console.log('\n🧪 TA Drawing Smoke Test (Playwright)');
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
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  try {
    await page.goto('http://localhost:5174', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(1500);

    // Wait until enhancedChartControl is available and ready
    await page.waitForFunction(() => {
      return typeof window !== 'undefined'
        && window.enhancedChartControl
        && window.enhancedChartControlReady === true
        && typeof window.enhancedChartControl.initialize === 'function';
    }, { timeout: 30000 });

    console.log('✅ enhancedChartControl is ready');

    // IMPORTANT: Wait for the chart to be fully initialized with data
    // This ensures the chart has loaded market data and has a series to draw on
    await page.waitForTimeout(5000); // Give time for market data to load
    
    // Verify chart is ready by checking if getChartRef returns a chart
    const chartReady = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      if (!ctrl) return false;
      
      // Check if chart ref exists
      const chart = ctrl.getChartRef && ctrl.getChartRef();
      return !!chart;
    });
    
    if (!chartReady) {
      console.log('⚠️ Chart not fully initialized, waiting longer...');
      await page.waitForTimeout(5000);
    }

    // 3) Execute drawing commands in the UI
    const joined = chartCommands.join(' ');
    const before = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      const d = ctrl && ctrl.drawings ? ctrl.drawings.size : 0;
      const a = ctrl && ctrl.annotations ? ctrl.annotations.size : 0;
      return { drawings: d, annotations: a };
    });
    console.log(`ℹ️  Before execution: drawings=${before.drawings}, annotations=${before.annotations}`);

    await page.evaluate(async (cmdStr) => {
      await window.enhancedChartControl.processEnhancedResponse(cmdStr);
    }, joined);

    // Give the chart a moment to render
    await page.waitForTimeout(1000);

    const after = await page.evaluate(() => {
      const ctrl = window.enhancedChartControl;
      const d = ctrl && ctrl.drawings ? ctrl.drawings.size : 0;
      const a = ctrl && ctrl.annotations ? ctrl.annotations.size : 0;
      return { drawings: d, annotations: a };
    });
    console.log(`ℹ️  After execution: drawings=${after.drawings}, annotations=${after.annotations}`);

    const drewSomething = (after.drawings > before.drawings) || (after.annotations > before.annotations);
    if (!drewSomething) {
      console.error('❌ No drawings/annotations were added by commands');
      await page.screenshot({ path: 'ta-drawing-failure.png', fullPage: true });
      console.log('📸 Saved screenshot: ta-drawing-failure.png');
      process.exit(2);
    }

    await page.screenshot({ path: 'ta-drawing-success.png', fullPage: true });
    console.log('✅ Drawing commands executed and rendered');
    console.log('📸 Saved screenshot: ta-drawing-success.png');

  } catch (err) {
    console.error('💥 Playwright test error:', err.message);
    process.exit(3);
  } finally {
    await browser.close();
  }
})();

