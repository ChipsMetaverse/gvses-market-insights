const { chromium } = require('playwright');

async function debugVoiceTab() {
  console.log('🔍 Debugging Voice Tab...\n');
  
  const browser = await chromium.launch({ 
    headless: false,  // Show browser to see what's happening
    slowMo: 500       // Slow down for visibility
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  await page.goto('http://localhost:5174');
  console.log('📍 Page loaded');
  await page.waitForTimeout(1000);
  
  // Take initial screenshot
  await page.screenshot({ path: 'debug-1-initial.png' });
  console.log('📸 Screenshot: debug-1-initial.png');
  
  // Click Voice tab
  await page.click('button:has-text("Voice + Manual Control")');
  console.log('📍 Voice tab clicked');
  await page.waitForTimeout(1000);
  
  // Take screenshot of Voice tab
  await page.screenshot({ path: 'debug-2-voice-tab.png' });
  console.log('📸 Screenshot: debug-2-voice-tab.png');
  
  // Check for OpenAI section
  const openaiSection = await page.$('text=/OpenAI.*Voice/i');
  if (openaiSection) {
    console.log('✅ Found OpenAI Voice section');
    
    // Look for any connect-related elements
    const connectElements = await page.$$eval('button, div', els => 
      els.filter(el => el.textContent?.toLowerCase().includes('connect'))
          .map(el => ({
            tag: el.tagName,
            text: el.textContent?.trim(),
            class: el.className
          }))
    );
    
    if (connectElements.length > 0) {
      console.log('Found connect-related elements:', connectElements);
    } else {
      console.log('❌ No connect-related elements found');
    }
  } else {
    console.log('❌ OpenAI Voice section not found');
    
    // Get all visible text content
    const visibleText = await page.$$eval('div', divs => 
      divs.filter(d => d.offsetHeight > 0)
          .map(d => d.textContent?.trim())
          .filter(t => t && t.length > 5 && t.length < 100)
          .slice(0, 10)
    );
    console.log('Visible content on page:', visibleText);
  }
  
  // Wait a bit to see the page
  await page.waitForTimeout(3000);
  
  await browser.close();
  console.log('\n✅ Debug complete. Check screenshots: debug-1-initial.png, debug-2-voice-tab.png');
}

debugVoiceTab().catch(console.error);
