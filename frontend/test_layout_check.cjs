const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔍 Checking current layout...\n');
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Check left panel
  const leftPanel = await page.$('.analysis-panel-left');
  if (leftPanel) {
    const title = await leftPanel.$('.panel-title');
    if (title) {
      const titleText = await title.textContent();
      console.log(`Left panel shows: "${titleText}"`);
    }
    
    // Check if it has news or stocks
    const newsItems = await leftPanel.$$('.analysis-item');
    const stockItems = await leftPanel.$$('.stock-item');
    
    console.log(`  - News items: ${newsItems.length}`);
    console.log(`  - Stock items: ${stockItems.length}`);
  }
  
  // Check for insights panel
  const insightsPanel = await page.$('.insights-panel');
  if (insightsPanel) {
    console.log('\n✅ Found insights-panel class');
    const title = await insightsPanel.$('.panel-title');
    if (title) {
      const titleText = await title.textContent();
      console.log(`Insights panel shows: "${titleText}"`);
    }
  }
  
  // Check header
  const header = await page.$('.dashboard-header-with-tickers');
  if (header) {
    const tickers = await header.$$('.ticker-compact');
    console.log(`\nHeader has ${tickers.length} ticker cards`);
  }
  
  // Take screenshot
  await page.screenshot({ path: 'frontend/layout-check.png', fullPage: true });
  console.log('\n📸 Screenshot saved as layout-check.png');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();