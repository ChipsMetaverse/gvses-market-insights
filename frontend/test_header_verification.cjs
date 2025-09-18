const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🚀 Comprehensive Header Ticker Verification\n');
  console.log('=' .repeat(50));
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // 1. Check Header Structure
  console.log('\n📋 HEADER STRUCTURE CHECK:');
  const header = await page.$('.dashboard-header-with-tickers');
  if (header) {
    console.log('✅ New header with integrated tickers found');
    const headerBox = await header.boundingBox();
    console.log(`   Height: ${headerBox.height}px (Target: 60px)`);
    console.log(`   Width: ${headerBox.width}px`);
    console.log(`   Position: X=${headerBox.x}, Y=${headerBox.y}`);
  } else {
    console.log('❌ Header with tickers NOT found');
    // Check for fallback header
    const oldHeader = await page.$('.dashboard-header');
    if (oldHeader) {
      console.log('⚠️  Old header class detected - update needed');
    }
  }
  
  // 2. Check GVSES Branding
  console.log('\n🏷️  BRANDING CHECK:');
  const brand = await page.$('.brand');
  if (brand) {
    const brandText = await brand.textContent();
    console.log(`✅ Brand found: "${brandText}"`);
    const brandBox = await brand.boundingBox();
    console.log(`   Position: X=${brandBox.x}px (should be left-aligned)`);
  }
  
  // 3. Check Ticker Cards in Header
  console.log('\n📊 TICKER CARDS IN HEADER:');
  const headerTickers = await page.$$('.ticker-compact');
  console.log(`Found ${headerTickers.length} ticker cards in header`);
  
  if (headerTickers.length > 0) {
    // Analyze first ticker
    const firstTicker = headerTickers[0];
    const firstBox = await firstTicker.boundingBox();
    console.log(`\nFirst Ticker Details:`);
    console.log(`   Size: ${firstBox.width}x${firstBox.height}px`);
    console.log(`   Position: X=${firstBox.x}, Y=${firstBox.y}`);
    
    // Check ticker content
    const symbol = await firstTicker.$('.ticker-symbol-compact');
    if (symbol) {
      const symbolText = await symbol.textContent();
      console.log(`   Symbol: ${symbolText}`);
    }
    
    const price = await firstTicker.$('.ticker-price-compact');
    if (price) {
      const priceText = await price.textContent();
      console.log(`   Price: ${priceText}`);
    }
    
    // Check horizontal alignment
    if (headerTickers.length > 1) {
      const secondBox = await headerTickers[1].boundingBox();
      const verticalDiff = Math.abs(secondBox.y - firstBox.y);
      const horizontalGap = secondBox.x - (firstBox.x + firstBox.width);
      
      console.log(`\nAlignment Check:`);
      console.log(`   Vertical difference: ${verticalDiff}px`);
      console.log(`   Horizontal gap: ${horizontalGap}px`);
      
      if (verticalDiff < 5) {
        console.log('   ✅ Cards are horizontally aligned');
      } else {
        console.log('   ❌ Cards are NOT properly aligned');
      }
    }
    
    // Check all ticker positions
    console.log('\nAll Ticker Positions:');
    for (let i = 0; i < headerTickers.length; i++) {
      const box = await headerTickers[i].boundingBox();
      const symbolEl = await headerTickers[i].$('.ticker-symbol-compact');
      const symbol = symbolEl ? await symbolEl.textContent() : 'N/A';
      console.log(`   ${i + 1}. ${symbol}: X=${box.x.toFixed(0)}, Y=${box.y.toFixed(0)}`);
    }
  }
  
  // 4. Check for Removed Elements
  console.log('\n🗑️  REMOVED ELEMENTS CHECK:');
  const oldTopPanel = await page.$('.top-market-insights');
  if (oldTopPanel) {
    console.log('❌ Old top-market-insights panel still exists');
  } else {
    console.log('✅ Old top-market-insights panel removed');
  }
  
  // 5. Check Main Layout
  console.log('\n📐 MAIN LAYOUT CHECK:');
  const dashboardLayout = await page.$('.dashboard-layout');
  if (dashboardLayout) {
    const layoutBox = await dashboardLayout.boundingBox();
    console.log(`✅ Dashboard layout found`);
    console.log(`   Height: ${layoutBox.height}px`);
    console.log(`   Y-position: ${layoutBox.y}px (should be below header)`);
  }
  
  // 6. Check Chart Panel
  console.log('\n📈 CHART PANEL CHECK:');
  const chartPanel = await page.$('.chart-panel');
  if (chartPanel) {
    const chartBox = await chartPanel.boundingBox();
    console.log(`✅ Chart panel found`);
    console.log(`   Height: ${chartBox.height}px (should be maximized)`);
    console.log(`   Width: ${chartBox.width}px`);
  }
  
  // 7. Visual State Check
  console.log('\n🎨 VISUAL STATE CHECK:');
  // Check if any ticker is selected
  const selectedTicker = await page.$('.ticker-compact.selected');
  if (selectedTicker) {
    const symbolEl = await selectedTicker.$('.ticker-symbol-compact');
    const symbol = symbolEl ? await symbolEl.textContent() : 'Unknown';
    console.log(`✅ Selected ticker: ${symbol}`);
  } else {
    console.log('⚠️  No ticker currently selected');
  }
  
  // 8. Interaction Test
  console.log('\n🖱️  INTERACTION TEST:');
  if (headerTickers.length > 1) {
    // Click on second ticker
    await headerTickers[1].click();
    await page.waitForTimeout(500);
    
    const newSelected = await page.$('.ticker-compact.selected');
    if (newSelected) {
      const symbolEl = await newSelected.$('.ticker-symbol-compact');
      const symbol = symbolEl ? await symbolEl.textContent() : 'Unknown';
      console.log(`✅ Click interaction works - Selected: ${symbol}`);
    }
  }
  
  // 9. Take Screenshots
  console.log('\n📸 CAPTURING SCREENSHOTS:');
  
  // Full page screenshot
  await page.screenshot({ 
    path: 'frontend/verify-full-page.png', 
    fullPage: true 
  });
  console.log('   ✅ Full page: verify-full-page.png');
  
  // Header only screenshot
  if (header) {
    await header.screenshot({ 
      path: 'frontend/verify-header-only.png' 
    });
    console.log('   ✅ Header only: verify-header-only.png');
  }
  
  // Viewport screenshot
  await page.screenshot({ 
    path: 'frontend/verify-viewport.png', 
    fullPage: false 
  });
  console.log('   ✅ Viewport: verify-viewport.png');
  
  console.log('\n' + '=' .repeat(50));
  console.log('✅ VERIFICATION COMPLETE');
  console.log('=' .repeat(50));
  
  await page.waitForTimeout(3000);
  await browser.close();
})();