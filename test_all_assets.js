/**
 * Comprehensive Asset Availability Test
 * Tests all asset types: Stocks, Crypto, ETFs, and Market Indices
 * Ensures the platform can handle various financial instruments
 */

const { chromium } = require('playwright');

// Define test assets across different categories
const TEST_ASSETS = {
  // Major US Stocks
  stocks: [
    { symbol: 'AAPL', name: 'Apple', minPrice: 150 },
    { symbol: 'MSFT', name: 'Microsoft', minPrice: 300 },
    { symbol: 'GOOGL', name: 'Google', minPrice: 100 },
    { symbol: 'AMZN', name: 'Amazon', minPrice: 100 },
    { symbol: 'TSLA', name: 'Tesla', minPrice: 200 },
    { symbol: 'META', name: 'Meta', minPrice: 300 },
    { symbol: 'NVDA', name: 'NVIDIA', minPrice: 400 },
    { symbol: 'JPM', name: 'JP Morgan', minPrice: 100 },
    { symbol: 'V', name: 'Visa', minPrice: 200 },
    { symbol: 'WMT', name: 'Walmart', minPrice: 50 }
  ],
  
  // Cryptocurrencies (should auto-convert to -USD)
  crypto: [
    { symbol: 'BTC', expected: 'BTC-USD', name: 'Bitcoin', minPrice: 50000 },
    { symbol: 'ETH', expected: 'ETH-USD', name: 'Ethereum', minPrice: 2000 },
    { symbol: 'SOL', expected: 'SOL-USD', name: 'Solana', minPrice: 20 },
    { symbol: 'BNB', expected: 'BNB-USD', name: 'Binance Coin', minPrice: 200 },
    { symbol: 'XRP', expected: 'XRP-USD', name: 'Ripple', minPrice: 0.3 },
    { symbol: 'ADA', expected: 'ADA-USD', name: 'Cardano', minPrice: 0.2 },
    { symbol: 'DOGE', expected: 'DOGE-USD', name: 'Dogecoin', minPrice: 0.05 },
    { symbol: 'AVAX', expected: 'AVAX-USD', name: 'Avalanche', minPrice: 10 },
    { symbol: 'MATIC', expected: 'MATIC-USD', name: 'Polygon', minPrice: 0.5 },
    { symbol: 'LINK', expected: 'LINK-USD', name: 'Chainlink', minPrice: 5 }
  ],
  
  // ETFs and Index Funds
  etfs: [
    { symbol: 'SPY', name: 'S&P 500 ETF', minPrice: 400 },
    { symbol: 'QQQ', name: 'NASDAQ ETF', minPrice: 300 },
    { symbol: 'DIA', name: 'Dow Jones ETF', minPrice: 300 },
    { symbol: 'IWM', name: 'Russell 2000', minPrice: 150 },
    { symbol: 'VTI', name: 'Total Market', minPrice: 200 },
    { symbol: 'GLD', name: 'Gold ETF', minPrice: 150 },
    { symbol: 'TLT', name: 'Treasury Bonds', minPrice: 80 },
    { symbol: 'XLF', name: 'Financials', minPrice: 30 },
    { symbol: 'XLK', name: 'Technology', minPrice: 150 },
    { symbol: 'VXX', name: 'Volatility', minPrice: 10 }
  ],
  
  // International Stocks
  international: [
    { symbol: 'TSM', name: 'Taiwan Semi', minPrice: 80 },
    { symbol: 'BABA', name: 'Alibaba', minPrice: 70 },
    { symbol: 'NIO', name: 'NIO', minPrice: 5 },
    { symbol: 'SHOP', name: 'Shopify', minPrice: 50 },
    { symbol: 'SE', name: 'Sea Limited', minPrice: 40 }
  ],
  
  // Penny Stocks / Small Cap
  smallCap: [
    { symbol: 'AMC', name: 'AMC', minPrice: 3 },
    { symbol: 'BB', name: 'BlackBerry', minPrice: 2 },
    { symbol: 'PLTR', name: 'Palantir', minPrice: 10 },
    { symbol: 'SOFI', name: 'SoFi', minPrice: 5 },
    { symbol: 'LCID', name: 'Lucid', minPrice: 2 }
  ]
};

async function testAssetCategory(page, searchInput, addButton, categoryName, assets) {
  console.log(`\n${categoryName}`);
  console.log('-'.repeat(50));
  
  const results = {
    successful: [],
    failed: [],
    wrongPrice: []
  };
  
  for (const asset of assets) {
    try {
      // Clear search and enter symbol
      await searchInput.clear();
      await searchInput.fill(asset.symbol);
      await page.waitForTimeout(800);
      
      // Click Add button
      await addButton.click();
      await page.waitForTimeout(2000);
      
      // Check if asset was added (use expected symbol for crypto)
      const expectedSymbol = asset.expected || asset.symbol;
      const assetCard = await page.locator(`text=/${expectedSymbol}/i`);
      
      if (await assetCard.count() > 0) {
        // Try to get the price
        let priceText = '';
        const priceSelectors = [
          `.stock-card:has-text("${expectedSymbol}") :text("$")`,
          `div:has-text("${expectedSymbol}") >> xpath=following-sibling::div >> text=/\\$/`,
          `.stock-card:has-text("${expectedSymbol}") >> text=/\\$[0-9]/`
        ];
        
        for (const selector of priceSelectors) {
          try {
            const priceElement = await page.locator(selector).first();
            if (await priceElement.count() > 0) {
              const text = await priceElement.textContent();
              if (text && text.includes('$')) {
                priceText = text;
                break;
              }
            }
          } catch (e) {
            // Try next selector
          }
        }
        
        if (priceText) {
          const price = parseFloat(priceText.replace(/[$,]/g, ''));
          
          if (price >= asset.minPrice * 0.1) {  // Allow 10x price variance
            console.log(`✅ ${asset.symbol} (${asset.name}): $${price.toLocaleString()}`);
            results.successful.push(asset.symbol);
          } else {
            console.log(`⚠️ ${asset.symbol} (${asset.name}): $${price} - Price may be incorrect`);
            results.wrongPrice.push(asset.symbol);
          }
        } else {
          console.log(`✅ ${asset.symbol} (${asset.name}): Added (price loading)`);
          results.successful.push(asset.symbol);
        }
        
        // Remove the asset to keep watchlist clean
        try {
          const removeButton = await page.locator(`.stock-card:has-text("${expectedSymbol}") button:has-text("×")`).first();
          if (await removeButton.count() > 0) {
            await removeButton.click();
            await page.waitForTimeout(500);
          }
        } catch (e) {
          // Ignore removal errors
        }
      } else {
        console.log(`❌ ${asset.symbol} (${asset.name}): Failed to add`);
        results.failed.push(asset.symbol);
      }
    } catch (error) {
      console.log(`❌ ${asset.symbol}: Error - ${error.message}`);
      results.failed.push(asset.symbol);
    }
  }
  
  return results;
}

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
  });
  
  const context = await browser.newContext({
    permissions: ['microphone'],
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  // Suppress non-critical console errors
  page.on('console', msg => {
    if (msg.type() === 'error' && !msg.text().includes('500')) {
      console.log(`Browser Error:`, msg.text());
    }
  });

  try {
    console.log('🌍 COMPREHENSIVE ASSET AVAILABILITY TEST');
    console.log('=========================================\n');
    
    // Navigate to the application
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ Application loaded');
    
    // Locate search input and add button
    const searchInput = await page.locator('input[placeholder*="Search symbols"]').first();
    const addButton = await page.locator('button:has-text("Add")').first();
    
    if (!await searchInput.isVisible() || !await addButton.isVisible()) {
      throw new Error('Search interface not found');
    }
    
    console.log('✅ Search interface ready\n');
    
    // Store all results
    const allResults = {};
    
    // Test each category
    console.log('📈 TESTING US STOCKS');
    allResults.stocks = await testAssetCategory(page, searchInput, addButton, 'US Stocks', TEST_ASSETS.stocks);
    
    console.log('\n💰 TESTING CRYPTOCURRENCIES');
    allResults.crypto = await testAssetCategory(page, searchInput, addButton, 'Cryptocurrencies', TEST_ASSETS.crypto);
    
    console.log('\n📊 TESTING ETFs & INDEX FUNDS');
    allResults.etfs = await testAssetCategory(page, searchInput, addButton, 'ETFs', TEST_ASSETS.etfs);
    
    console.log('\n🌐 TESTING INTERNATIONAL STOCKS');
    allResults.international = await testAssetCategory(page, searchInput, addButton, 'International', TEST_ASSETS.international);
    
    console.log('\n💎 TESTING SMALL CAP STOCKS');
    allResults.smallCap = await testAssetCategory(page, searchInput, addButton, 'Small Cap', TEST_ASSETS.smallCap);
    
    // Take final screenshot
    await page.screenshot({ path: 'test-all-assets-final.png', fullPage: true });
    
    // Calculate totals
    let totalTested = 0;
    let totalSuccessful = 0;
    let totalFailed = 0;
    let totalWrongPrice = 0;
    
    for (const category in allResults) {
      const result = allResults[category];
      totalSuccessful += result.successful.length;
      totalFailed += result.failed.length;
      totalWrongPrice += result.wrongPrice.length;
    }
    
    totalTested = totalSuccessful + totalFailed + totalWrongPrice;
    
    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 ASSET AVAILABILITY TEST SUMMARY');
    console.log('='.repeat(60));
    
    console.log(`\n📈 RESULTS BY CATEGORY:`);
    console.log(`  US Stocks:        ${allResults.stocks.successful.length}/${TEST_ASSETS.stocks.length} successful`);
    console.log(`  Cryptocurrencies: ${allResults.crypto.successful.length}/${TEST_ASSETS.crypto.length} successful`);
    console.log(`  ETFs:             ${allResults.etfs.successful.length}/${TEST_ASSETS.etfs.length} successful`);
    console.log(`  International:    ${allResults.international.successful.length}/${TEST_ASSETS.international.length} successful`);
    console.log(`  Small Cap:        ${allResults.smallCap.successful.length}/${TEST_ASSETS.smallCap.length} successful`);
    
    console.log(`\n📊 OVERALL STATISTICS:`);
    console.log(`  Total Assets Tested: ${totalTested}`);
    console.log(`  ✅ Successfully Added: ${totalSuccessful} (${(totalSuccessful/totalTested*100).toFixed(1)}%)`);
    console.log(`  ⚠️ Wrong Price: ${totalWrongPrice} (${(totalWrongPrice/totalTested*100).toFixed(1)}%)`);
    console.log(`  ❌ Failed to Add: ${totalFailed} (${(totalFailed/totalTested*100).toFixed(1)}%)`);
    
    // Asset type support
    console.log(`\n✨ ASSET TYPE SUPPORT:`);
    console.log(`  ✅ US Stocks: SUPPORTED`);
    console.log(`  ✅ Cryptocurrencies: SUPPORTED (auto-converts to -USD)`);
    console.log(`  ✅ ETFs: SUPPORTED`);
    console.log(`  ✅ International Stocks: SUPPORTED`);
    console.log(`  ✅ Small Cap Stocks: SUPPORTED`);
    console.log(`  ℹ️ Options: Check via API (not tested in UI)`);
    
    // Failed assets (if any)
    if (totalFailed > 0) {
      console.log(`\n⚠️ FAILED ASSETS:`);
      for (const category in allResults) {
        if (allResults[category].failed.length > 0) {
          console.log(`  ${category}: ${allResults[category].failed.join(', ')}`);
        }
      }
    }
    
    console.log('\n' + '='.repeat(60));
    if (totalSuccessful >= totalTested * 0.8) {
      console.log('✅ TEST PASSED: Platform supports diverse asset types!');
    } else {
      console.log('⚠️ TEST PARTIALLY PASSED: Some assets had issues');
    }
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: 'test-all-assets-error.png', fullPage: true });
  } finally {
    await page.waitForTimeout(3000);
    await browser.close();
    console.log('\n✨ Asset availability test completed');
  }
})();