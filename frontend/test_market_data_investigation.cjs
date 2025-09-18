const playwright = require('playwright');

async function investigateMarketDataLoading() {
  console.log('🔍 MARKET DATA LOADING INVESTIGATION');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 }
  });
  const page = await context.newPage();

  // Track all console messages and network requests
  const consoleLogs = [];
  const networkRequests = [];
  const errors = [];

  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push({ type: msg.type(), text, time: new Date().toISOString() });
    console.log(`[${msg.type().toUpperCase()}] ${text}`);
    
    if (msg.type() === 'error') {
      errors.push({ text, time: new Date().toISOString() });
    }
  });

  page.on('request', request => {
    networkRequests.push({
      url: request.url(),
      method: request.method(),
      time: new Date().toISOString()
    });
    console.log(`📡 REQUEST: ${request.method()} ${request.url()}`);
  });

  page.on('response', response => {
    console.log(`📥 RESPONSE: ${response.status()} ${response.url()}`);
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APP AND INSPECT INITIAL STATE');
    
    await page.goto('http://localhost:5175');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(5000); // Give time for market data to load
    
    console.log('\n📍 PHASE 2: INSPECT DOM STRUCTURE');
    
    const domStructure = await page.evaluate(() => {
      // Look for market data related elements
      const stockCards = Array.from(document.querySelectorAll('.stock-card, [class*="stock"], [class*="market"]'));
      const chartContainer = document.querySelector('.chart-container, [class*="chart"]');
      const marketInsights = document.querySelector('.market-insights, [class*="insight"]');
      const watchlist = document.querySelector('.watchlist, [class*="watchlist"]');
      const tabs = Array.from(document.querySelectorAll('[data-testid*="tab"], .tab, [class*="tab"]'));
      
      return {
        stockCards: stockCards.map(card => ({
          className: card.className,
          innerHTML: card.innerHTML.substring(0, 200),
          visible: card.offsetHeight > 0 && card.offsetWidth > 0,
          children: Array.from(card.children).map(child => ({
            tag: child.tagName,
            className: child.className,
            textContent: child.textContent?.substring(0, 100)
          }))
        })),
        chartContainer: {
          exists: !!chartContainer,
          className: chartContainer?.className,
          visible: chartContainer && chartContainer.offsetHeight > 0
        },
        marketInsights: {
          exists: !!marketInsights,
          className: marketInsights?.className,
          visible: marketInsights && marketInsights.offsetHeight > 0
        },
        watchlist: {
          exists: !!watchlist,
          className: watchlist?.className,
          visible: watchlist && watchlist.offsetHeight > 0
        },
        tabs: tabs.map(tab => ({
          testId: tab.getAttribute('data-testid'),
          className: tab.className,
          textContent: tab.textContent?.trim(),
          visible: tab.offsetHeight > 0
        })),
        bodyClasses: document.body.className,
        allDivs: Array.from(document.querySelectorAll('div')).length,
        totalElements: document.querySelectorAll('*').length
      };
    });
    
    console.log('\n🏗️ DOM STRUCTURE ANALYSIS:');
    console.log(`Total Elements: ${domStructure.totalElements}`);
    console.log(`Total Divs: ${domStructure.allDivs}`);
    console.log(`Body Classes: ${domStructure.bodyClasses}`);
    
    console.log('\n📱 TABS FOUND:');
    domStructure.tabs.forEach((tab, i) => {
      console.log(`${i + 1}. ${tab.testId || 'no-testid'} | "${tab.textContent}" | ${tab.visible ? 'VISIBLE' : 'HIDDEN'} | ${tab.className}`);
    });
    
    console.log('\n📊 STOCK CARDS ANALYSIS:');
    if (domStructure.stockCards.length === 0) {
      console.log('❌ NO STOCK CARDS FOUND IN DOM');
    } else {
      domStructure.stockCards.forEach((card, i) => {
        console.log(`${i + 1}. VISIBLE: ${card.visible} | CLASS: ${card.className}`);
        console.log(`   CHILDREN: ${card.children.length} elements`);
        card.children.forEach(child => {
          console.log(`     - ${child.tag}.${child.className}: "${child.textContent}"`);
        });
      });
    }
    
    console.log('\n📈 MARKET COMPONENTS:');
    console.log(`Chart Container: ${domStructure.chartContainer.exists ? 'EXISTS' : 'MISSING'} | ${domStructure.chartContainer.visible ? 'VISIBLE' : 'HIDDEN'}`);
    console.log(`Market Insights: ${domStructure.marketInsights.exists ? 'EXISTS' : 'MISSING'} | ${domStructure.marketInsights.visible ? 'VISIBLE' : 'HIDDEN'}`);
    console.log(`Watchlist: ${domStructure.watchlist.exists ? 'EXISTS' : 'MISSING'} | ${domStructure.watchlist.visible ? 'VISIBLE' : 'HIDDEN'}`);
    
    await page.screenshot({ path: 'market-data-investigation-dom.png', fullPage: true });
    
    console.log('\n📍 PHASE 3: CHECK NETWORK ACTIVITY');
    
    // Check what API calls were made
    const marketDataRequests = networkRequests.filter(req => 
      req.url.includes('stock') || 
      req.url.includes('market') || 
      req.url.includes('api') ||
      req.url.includes('price') ||
      req.url.includes('quote')
    );
    
    console.log(`\n📡 NETWORK REQUESTS (${networkRequests.length} total):`);
    networkRequests.forEach((req, i) => {
      console.log(`${i + 1}. ${req.method} ${req.url}`);
    });
    
    console.log(`\n💰 MARKET DATA REQUESTS (${marketDataRequests.length}):`);
    marketDataRequests.forEach((req, i) => {
      console.log(`${i + 1}. ${req.method} ${req.url}`);
    });
    
    console.log('\n📍 PHASE 4: MANUALLY TRIGGER MARKET DATA LOAD');
    
    // Try to manually trigger market data loading
    const manualDataLoad = await page.evaluate(async () => {
      // Look for any loadMarketData, fetchStocks, or similar functions
      const marketFunctions = [];
      
      // Check window object for market-related functions
      for (let prop in window) {
        if (prop.toLowerCase().includes('market') || 
            prop.toLowerCase().includes('stock') ||
            prop.toLowerCase().includes('fetch') ||
            prop.toLowerCase().includes('load')) {
          marketFunctions.push(prop);
        }
      }
      
      return {
        marketFunctions,
        localStorage: Object.keys(localStorage),
        sessionStorage: Object.keys(sessionStorage)
      };
    });
    
    console.log('\n🔧 AVAILABLE FUNCTIONS:');
    console.log(`Market Functions: ${manualDataLoad.marketFunctions.join(', ')}`);
    console.log(`Local Storage Keys: ${manualDataLoad.localStorage.join(', ')}`);
    console.log(`Session Storage Keys: ${manualDataLoad.sessionStorage.join(', ')}`);
    
    console.log('\n📍 PHASE 5: CHECK FOR ERRORS');
    
    const criticalErrors = errors.filter(error => 
      error.text.toLowerCase().includes('market') ||
      error.text.toLowerCase().includes('stock') ||
      error.text.toLowerCase().includes('api') ||
      error.text.toLowerCase().includes('fetch') ||
      error.text.toLowerCase().includes('data')
    );
    
    console.log(`\n⚠️ ALL ERRORS (${errors.length}):`);
    errors.forEach((error, i) => {
      console.log(`${i + 1}. ${error.text}`);
    });
    
    console.log(`\n🚨 CRITICAL DATA ERRORS (${criticalErrors.length}):`);
    criticalErrors.forEach((error, i) => {
      console.log(`${i + 1}. ${error.text}`);
    });
    
    console.log('\n📍 PHASE 6: INVESTIGATION SUMMARY');
    
    const diagnosis = {
      domLoaded: domStructure.totalElements > 100,
      tabsPresent: domStructure.tabs.length > 0,
      stockCardsFound: domStructure.stockCards.length > 0,
      stockCardsVisible: domStructure.stockCards.some(card => card.visible),
      marketDataRequests: marketDataRequests.length > 0,
      hasErrors: errors.length > 0,
      criticalDataErrors: criticalErrors.length > 0
    };
    
    console.log('\n🎯 DIAGNOSIS:');
    console.log(`✅ DOM Loaded: ${diagnosis.domLoaded}`);
    console.log(`✅ Navigation Tabs: ${diagnosis.tabsPresent} (${domStructure.tabs.length} found)`);
    console.log(`${diagnosis.stockCardsFound ? '✅' : '❌'} Stock Cards in DOM: ${domStructure.stockCards.length}`);
    console.log(`${diagnosis.stockCardsVisible ? '✅' : '❌'} Stock Cards Visible: ${domStructure.stockCards.filter(c => c.visible).length}`);
    console.log(`${diagnosis.marketDataRequests ? '✅' : '❌'} Market Data API Calls: ${marketDataRequests.length}`);
    console.log(`${!diagnosis.hasErrors ? '✅' : '⚠️'} JavaScript Errors: ${errors.length}`);
    
    // Root cause analysis
    console.log('\n🔍 ROOT CAUSE ANALYSIS:');
    
    if (!diagnosis.stockCardsFound) {
      console.log('🚨 PRIMARY ISSUE: No stock cards found in DOM');
      console.log('   - Market data components may not be rendering');
      console.log('   - Check if TradingDashboardSimple component is loaded');
      console.log('   - Verify market data service is functioning');
    } else if (!diagnosis.stockCardsVisible) {
      console.log('🚨 PRIMARY ISSUE: Stock cards exist but are not visible');
      console.log('   - CSS display/visibility issues');
      console.log('   - Layout problems with market insights panel');
      console.log('   - Data loading state blocking visibility');
    }
    
    if (!diagnosis.marketDataRequests) {
      console.log('🚨 SECONDARY ISSUE: No market data API requests');
      console.log('   - Backend API may not be called');
      console.log('   - Check useEffect hooks in market data components');
      console.log('   - Verify API endpoints are correct');
    }
    
    if (diagnosis.criticalDataErrors) {
      console.log('🚨 ERROR ISSUE: Critical data-related JavaScript errors');
      console.log('   - Fix JavaScript errors first');
      console.log('   - These may be preventing market data loading');
    }
    
    console.log('\n🛠️ RECOMMENDED FIXES:');
    if (!diagnosis.stockCardsFound && !diagnosis.marketDataRequests) {
      console.log('1. Check TradingDashboardSimple.tsx market insights rendering');
      console.log('2. Verify marketDataService.ts is being called');
      console.log('3. Check useEffect hooks for market data loading');
    }
    if (errors.length > 0) {
      console.log('4. Fix JavaScript errors in console');
    }
    if (marketDataRequests.length === 0) {
      console.log('5. Verify backend API is running and accessible');
    }
    
    console.log('\n🔍 Browser kept open for manual inspection...');
    await new Promise(() => {}); // Keep open
    
  } catch (error) {
    console.error('❌ Investigation Error:', error.message);
    await page.screenshot({ path: 'market-data-investigation-error.png' });
  }
}

investigateMarketDataLoading().catch(console.error);