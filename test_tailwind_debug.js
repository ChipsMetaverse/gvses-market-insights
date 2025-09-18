/**
 * Debug Tailwind CSS issue using Playwright
 * Check if styles are actually being loaded and applied
 */

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true // Open DevTools to inspect
  });
  
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  // Capture console messages and errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error('❌ Browser Error:', msg.text());
    } else if (msg.type() === 'warning') {
      console.warn('⚠️ Browser Warning:', msg.text());
    }
  });

  // Capture network failures
  page.on('requestfailed', request => {
    console.error('❌ Request failed:', request.url(), request.failure().errorText);
  });

  try {
    console.log('🔍 Debugging Tailwind CSS issue...\n');
    
    // Navigate to the page
    await page.goto('http://localhost:5174/?provider-test');
    await page.waitForTimeout(2000);
    
    // Check if Tailwind CSS is loaded
    console.log('📋 Checking loaded stylesheets:');
    const stylesheets = await page.evaluate(() => {
      const sheets = Array.from(document.styleSheets);
      return sheets.map(sheet => ({
        href: sheet.href,
        rules: sheet.cssRules ? sheet.cssRules.length : 0
      }));
    });
    console.log('Stylesheets:', stylesheets);
    
    // Check if @tailwind directives were processed
    console.log('\n🎨 Checking for Tailwind CSS:');
    const hasTailwindBase = await page.evaluate(() => {
      // Check if any Tailwind reset styles are applied
      const bodyStyles = window.getComputedStyle(document.body);
      return {
        margin: bodyStyles.margin,
        padding: bodyStyles.padding,
        boxSizing: bodyStyles.boxSizing
      };
    });
    console.log('Body styles:', hasTailwindBase);
    
    // Check specific Tailwind classes
    console.log('\n🔍 Checking Tailwind utility classes:');
    const testElement = await page.locator('.space-y-2').first();
    if (await testElement.count() > 0) {
      const computedStyles = await testElement.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          display: styles.display,
          gap: styles.gap,
          marginTop: styles.marginTop,
          '--tw-space-y-reverse': styles.getPropertyValue('--tw-space-y-reverse')
        };
      });
      console.log('Element with .space-y-2:', computedStyles);
    } else {
      console.log('❌ No elements with .space-y-2 found');
    }
    
    // Check for flexbox classes
    const flexElement = await page.locator('.flex').first();
    if (await flexElement.count() > 0) {
      const flexStyles = await flexElement.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          display: styles.display,
          flexDirection: styles.flexDirection
        };
      });
      console.log('Element with .flex:', flexStyles);
    }
    
    // Check if CSS variables are defined (Tailwind v3 vs v4)
    console.log('\n🔧 Checking CSS variables:');
    const cssVars = await page.evaluate(() => {
      const rootStyles = window.getComputedStyle(document.documentElement);
      const vars = {};
      // Check for Tailwind CSS variables
      ['--tw-ring-offset-shadow', '--tw-ring-shadow', '--tw-shadow'].forEach(varName => {
        vars[varName] = rootStyles.getPropertyValue(varName) || 'not defined';
      });
      return vars;
    });
    console.log('CSS Variables:', cssVars);
    
    // Get the actual CSS content
    console.log('\n📄 Checking index.css content:');
    const responses = [];
    page.on('response', response => {
      if (response.url().includes('.css')) {
        responses.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    await page.reload();
    await page.waitForTimeout(2000);
    
    console.log('CSS files loaded:', responses);
    
    // Check the computed styles of a provider card
    console.log('\n🎯 Checking provider card styles:');
    const providerCard = await page.locator('.bg-white.rounded-lg.p-4').first();
    if (await providerCard.count() > 0) {
      const cardStyles = await providerCard.evaluate(el => {
        const styles = window.getComputedStyle(el);
        return {
          backgroundColor: styles.backgroundColor,
          borderRadius: styles.borderRadius,
          padding: styles.padding,
          className: el.className
        };
      });
      console.log('Provider card styles:', cardStyles);
    } else {
      console.log('❌ No provider cards with expected classes found');
    }
    
    // Take screenshot with annotations
    await page.screenshot({ path: 'tailwind-debug-screenshot.png', fullPage: true });
    console.log('\n📸 Screenshot saved: tailwind-debug-screenshot.png');
    
    // Final diagnosis
    console.log('\n📊 Diagnosis:');
    if (hasTailwindBase.margin === '0px' && hasTailwindBase.padding === '0px') {
      console.log('✅ Tailwind base styles are being applied');
    } else {
      console.log('❌ Tailwind base styles are NOT being applied');
      console.log('   This suggests @tailwind directives are not being processed');
    }
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  } finally {
    console.log('\n🔚 Debug complete - check browser DevTools for more details');
    await page.waitForTimeout(10000); // Keep browser open for inspection
    await browser.close();
  }
})();