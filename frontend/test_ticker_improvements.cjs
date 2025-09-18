const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🎨 Testing Improved Ticker Card Design\n');
  console.log('=' .repeat(50));
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Check Header
  console.log('\n📊 TICKER CARD IMPROVEMENTS:');
  const headerTickers = await page.$$('.ticker-compact');
  console.log(`Found ${headerTickers.length} ticker cards`);
  
  if (headerTickers.length > 0) {
    // Analyze first ticker structure
    const firstTicker = headerTickers[0];
    
    // Check for new horizontal layout
    const leftSection = await firstTicker.$('.ticker-compact-left');
    const rightSection = await firstTicker.$('.ticker-compact-right');
    
    if (leftSection && rightSection) {
      console.log('✅ New horizontal layout detected');
      
      // Get symbol and price from left section
      const symbol = await leftSection.$eval('.ticker-symbol-compact', el => el.textContent);
      const price = await leftSection.$eval('.ticker-price-compact', el => el.textContent);
      console.log(`   Symbol: ${symbol}`);
      console.log(`   Price: ${price}`);
      
      // Get change from right section
      const changeEl = await rightSection.$('.ticker-change-compact');
      if (changeEl) {
        const change = await changeEl.textContent();
        console.log(`   Change: ${change}`);
      }
    } else {
      console.log('⚠️ Old vertical layout still in use');
    }
    
    // Check visual properties
    const styles = await firstTicker.evaluate(el => {
      const computed = window.getComputedStyle(el);
      return {
        width: el.offsetWidth,
        height: el.offsetHeight,
        borderRadius: computed.borderRadius,
        background: computed.background,
        boxShadow: computed.boxShadow
      };
    });
    
    console.log('\n📐 CARD DIMENSIONS:');
    console.log(`   Width: ${styles.width}px (Target: 110px+)`);
    console.log(`   Height: ${styles.height}px (Target: 46px)`);
    console.log(`   Border Radius: ${styles.borderRadius}`);
    
    // Test hover state
    console.log('\n🖱️ TESTING HOVER STATE:');
    await firstTicker.hover();
    await page.waitForTimeout(300);
    
    const hoverStyles = await firstTicker.evaluate(el => {
      const computed = window.getComputedStyle(el);
      return {
        transform: computed.transform,
        boxShadow: computed.boxShadow
      };
    });
    
    if (hoverStyles.transform !== 'none') {
      console.log('✅ Hover transform animation working');
    }
    
    // Test selected state
    console.log('\n🎯 TESTING SELECTED STATE:');
    await headerTickers[2].click();
    await page.waitForTimeout(300);
    
    const selectedCard = await page.$('.ticker-compact.selected');
    if (selectedCard) {
      const selectedSymbol = await selectedCard.$eval('.ticker-symbol-compact', el => el.textContent);
      console.log(`✅ Selected ticker: ${selectedSymbol}`);
      
      // Check gradient background
      const selectedBg = await selectedCard.evaluate(el => {
        return window.getComputedStyle(el).background;
      });
      
      if (selectedBg.includes('gradient')) {
        console.log('✅ Selected gradient background applied');
      }
    }
  }
  
  // Check header styling
  console.log('\n🎨 HEADER STYLING:');
  const header = await page.$('.dashboard-header-with-tickers');
  if (header) {
    const headerHeight = await header.evaluate(el => el.offsetHeight);
    console.log(`   Header height: ${headerHeight}px (Target: 68px)`);
    
    const headerBg = await header.evaluate(el => {
      return window.getComputedStyle(el).background;
    });
    
    if (headerBg.includes('gradient')) {
      console.log('✅ Header gradient background applied');
    }
  }
  
  // Take screenshots
  console.log('\n📸 CAPTURING SCREENSHOTS:');
  
  await page.screenshot({ 
    path: 'frontend/ticker-improvements-full.png', 
    fullPage: false 
  });
  console.log('   ✅ Full view: ticker-improvements-full.png');
  
  if (header) {
    await header.screenshot({ 
      path: 'frontend/ticker-improvements-header.png' 
    });
    console.log('   ✅ Header only: ticker-improvements-header.png');
  }
  
  console.log('\n' + '=' .repeat(50));
  console.log('✅ TICKER IMPROVEMENTS TEST COMPLETE');
  console.log('=' .repeat(50));
  
  await page.waitForTimeout(3000);
  await browser.close();
})();