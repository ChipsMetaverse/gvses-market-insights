/**
 * Check console errors in the application
 */

const { chromium } = require('playwright');

async function testConsoleErrors() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture console messages
  const consoleLogs = [];
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    consoleLogs.push({ type, text });
    
    if (type === 'error') {
      console.log('❌ Console Error:', text);
    } else if (type === 'warning') {
      console.log('⚠️ Console Warning:', text);
    }
  });

  // Capture page errors
  page.on('pageerror', error => {
    console.log('🔴 Page Error:', error.message);
  });

  console.log('🚀 Checking for console errors...');
  
  try {
    // Navigate to the application
    await page.goto('http://localhost:5175', { waitUntil: 'domcontentloaded' });
    console.log('✅ Page loaded');
    
    // Wait for potential async errors
    await page.waitForTimeout(3000);
    
    // Check page content
    const title = await page.title();
    console.log('📄 Page title:', title);
    
    const bodyHTML = await page.content();
    if (bodyHTML.includes('root')) {
      console.log('✅ React root element found');
    }
    
    // Try to evaluate some basic info
    const pageInfo = await page.evaluate(() => {
      return {
        hasReactRoot: !!document.getElementById('root'),
        rootContent: document.getElementById('root')?.innerHTML?.substring(0, 200),
        scripts: Array.from(document.querySelectorAll('script')).map(s => s.src),
        errors: window.errors || []
      };
    });
    
    console.log('\n📊 Page Analysis:');
    console.log('Has React root:', pageInfo.hasReactRoot);
    console.log('Root content preview:', pageInfo.rootContent || 'Empty');
    console.log('Scripts loaded:', pageInfo.scripts.length);
    
    // Summary
    const errors = consoleLogs.filter(log => log.type === 'error');
    const warnings = consoleLogs.filter(log => log.type === 'warning');
    
    console.log('\n📋 Summary:');
    console.log('Errors found:', errors.length);
    console.log('Warnings found:', warnings.length);
    
    if (errors.length > 0) {
      console.log('\n❌ Errors detail:');
      errors.forEach(e => console.log(' -', e.text));
    }

  } catch (error) {
    console.error('❌ Test failed:', error);
  }

  await browser.close();
}

// Run the test
testConsoleErrors().catch(console.error);