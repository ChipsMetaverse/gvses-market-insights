const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true 
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Listen for console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      console.error('❌ Console Error:', text);
    } else if (type === 'warning') {
      console.warn('⚠️ Console Warning:', text);
    } else {
      console.log(`📝 Console ${type}:`, text);
    }
  });

  // Listen for page errors
  page.on('pageerror', error => {
    console.error('🔴 Page Error:', error.message);
    console.error('Stack:', error.stack);
  });

  // Listen for failed requests
  page.on('requestfailed', request => {
    console.error('❌ Request Failed:', request.url(), '-', request.failure().errorText);
  });

  try {
    console.log('🚀 Navigating to http://localhost:5174...');
    
    // Navigate with network activity logging
    const response = await page.goto('http://localhost:5174', { 
      waitUntil: 'networkidle',
      timeout: 30000 
    });
    
    console.log('📊 Response status:', response.status());
    
    // Wait a bit for any async errors
    await page.waitForTimeout(2000);
    
    // Check if main app container exists
    const appContainer = await page.$('.trading-dashboard-simple');
    if (appContainer) {
      console.log('✅ Main app container found');
    } else {
      console.log('❌ Main app container NOT found');
      
      // Check what's actually on the page
      const bodyContent = await page.evaluate(() => document.body.innerHTML);
      console.log('📄 Body content length:', bodyContent.length);
      
      // Check for React root
      const reactRoot = await page.$('#root');
      if (reactRoot) {
        const rootContent = await page.evaluate(el => el.innerHTML, reactRoot);
        console.log('📦 React root content:', rootContent.substring(0, 200));
      }
    }
    
    // Check for specific elements
    const elements = [
      { selector: '.dashboard-header', name: 'Header' },
      { selector: '.top-market-insights', name: 'Market Insights' },
      { selector: '.dashboard-layout', name: 'Dashboard Layout' },
      { selector: '.chart-wrapper', name: 'Chart' },
      { selector: '.voice-fab', name: 'Voice FAB' }
    ];
    
    console.log('\n🔍 Checking for UI elements:');
    for (const { selector, name } of elements) {
      const element = await page.$(selector);
      console.log(`  ${element ? '✅' : '❌'} ${name} (${selector})`);
    }
    
    // Get all network errors
    const failedRequests = [];
    page.on('response', response => {
      if (!response.ok() && response.status() !== 304) {
        failedRequests.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });
    
    // Check for any JavaScript errors in evaluation
    try {
      const hasErrors = await page.evaluate(() => {
        return window.__REACT_DEVTOOLS_GLOBAL_HOOK__ && 
               window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers &&
               window.__REACT_DEVTOOLS_GLOBAL_HOOK__.renderers.size > 0;
      });
      console.log('\n🔧 React DevTools detected:', hasErrors);
    } catch (e) {
      console.log('⚠️ Could not check React DevTools:', e.message);
    }
    
    // Check for specific error patterns
    const pageContent = await page.content();
    if (pageContent.includes('TypeError')) {
      console.log('\n⚠️ TypeError found in page content');
    }
    if (pageContent.includes('SyntaxError')) {
      console.log('\n⚠️ SyntaxError found in page content');
    }
    
    // Try to get the actual error from the page
    const errorMessage = await page.evaluate(() => {
      const errorElement = document.querySelector('.error-message, .error, [data-error]');
      return errorElement ? errorElement.textContent : null;
    });
    
    if (errorMessage) {
      console.log('\n🔴 Error message on page:', errorMessage);
    }
    
    // Take a screenshot
    await page.screenshot({ path: 'frontend/investigation-result.png', fullPage: true });
    console.log('\n📸 Screenshot saved as investigation-result.png');
    
    // Keep browser open for manual inspection
    console.log('\n⏸️ Browser will stay open for 60 seconds for manual inspection...');
    await page.waitForTimeout(60000);
    
  } catch (error) {
    console.error('🔥 Test error:', error);
  } finally {
    await browser.close();
  }
})();