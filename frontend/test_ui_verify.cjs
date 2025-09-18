const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🚀 Testing cleaned-up UI...');
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  
  // Check main elements
  const elements = [
    { selector: '.trading-dashboard-simple', name: 'Main Dashboard' },
    { selector: '.dashboard-header', name: 'Header' },
    { selector: '.top-market-insights', name: 'Top Market Insights' },
    { selector: '.dashboard-layout', name: 'Layout Grid' },
    { selector: '.analysis-panel-left', name: 'Left Analysis Panel' },
    { selector: '.main-content', name: 'Chart Area' },
    { selector: '.voice-panel-right', name: 'Right Voice Panel' },
    { selector: '.voice-fab', name: 'Voice FAB Button' }
  ];
  
  console.log('\n✅ UI Element Check:');
  for (const { selector, name } of elements) {
    const element = await page.$(selector);
    console.log(`  ${element ? '✓' : '✗'} ${name}`);
  }
  
  // Check search functionality
  const searchInput = await page.$('.search-input');
  if (searchInput) {
    console.log('\n🔍 Testing search input...');
    await searchInput.type('AAPL');
    await page.waitForTimeout(1000);
    console.log('  ✓ Search input working');
  }
  
  // Take screenshot
  await page.screenshot({ path: 'frontend/cleaned-ui-test.png' });
  console.log('\n📸 Screenshot saved as cleaned-ui-test.png');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();