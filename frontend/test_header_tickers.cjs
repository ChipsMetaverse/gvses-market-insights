const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🚀 Testing header with integrated ticker cards...');
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Check if header exists with new class
  const header = await page.$('.dashboard-header-with-tickers');
  if (header) {
    console.log('✅ New header with tickers found');
    
    // Check header height
    const headerBox = await header.boundingBox();
    console.log(`📏 Header height: ${headerBox.height}px (should be ~60px)`);
    
    // Check for ticker cards in header
    const headerTickers = await page.$$('.ticker-compact');
    console.log(`📊 Found ${headerTickers.length} ticker cards in header`);
    
    if (headerTickers.length > 0) {
      // Check positioning of first ticker
      const firstTicker = await headerTickers[0].boundingBox();
      console.log(`📍 First ticker position - X: ${firstTicker.x}px, Y: ${firstTicker.y}px`);
      
      // Check if they're horizontally aligned
      if (headerTickers.length > 1) {
        const secondTicker = await headerTickers[1].boundingBox();
        if (Math.abs(secondTicker.y - firstTicker.y) < 5) {
          console.log('✅ Ticker cards are horizontally aligned in header');
        } else {
          console.log('❌ Ticker cards are NOT aligned horizontally');
        }
      }
    }
  } else {
    console.log('❌ New header not found - checking for old header');
    const oldHeader = await page.$('.dashboard-header');
    if (oldHeader) {
      console.log('⚠️ Old header still present - class name not updated');
    }
  }
  
  // Check that old top-market-insights is removed
  const oldTopPanel = await page.$('.top-market-insights');
  if (oldTopPanel) {
    console.log('❌ Old top-market-insights panel still exists - should be removed');
  } else {
    console.log('✅ Old top-market-insights panel successfully removed');
  }
  
  // Check chart space
  const chart = await page.$('.chart-panel');
  if (chart) {
    const chartBox = await chart.boundingBox();
    console.log(`\n📈 Chart dimensions - Height: ${chartBox.height}px (should be maximized)`);
  }
  
  // Take screenshot
  await page.screenshot({ path: 'frontend/header-tickers-test.png', fullPage: true });
  console.log('\n📸 Screenshot saved as header-tickers-test.png');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();