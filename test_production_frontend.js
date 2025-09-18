const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Testing production OpenAI relay...');
  console.log('1. Opening production app...');
  await page.goto('https://gvses-market-insights.fly.dev', { waitUntil: 'networkidle' });
  
  // Wait for page to load
  await page.waitForTimeout(3000);
  
  console.log('2. Looking for OpenAI connect button...');
  
  // Check if OpenAI button exists
  const openaiButton = await page.locator('button:has-text("OpenAI")').first();
  if (await openaiButton.isVisible()) {
    console.log('✓ OpenAI button found');
    
    // Take screenshot before clicking
    await page.screenshot({ path: 'production-openai-before.png', fullPage: true });
    
    console.log('3. Clicking OpenAI connect button...');
    await openaiButton.click();
    
    // Wait for connection
    await page.waitForTimeout(5000);
    
    // Check for connection status
    const statusIndicator = await page.locator('.status-indicator').first();
    if (await statusIndicator.isVisible()) {
      const statusText = await statusIndicator.textContent();
      console.log(`   Status: ${statusText}`);
    }
    
    // Take screenshot after connection
    await page.screenshot({ path: 'production-openai-after.png', fullPage: true });
    
    // Check console for tool configuration
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('tools') || text.includes('MarketSage') || text.includes('session.created')) {
        console.log(`   Console: ${text}`);
      }
    });
    
    // Try a voice command
    console.log('4. Testing voice command...');
    const micButton = await page.locator('[data-testid="mic-button"], button:has-text("🎤"), .microphone-button').first();
    if (await micButton.isVisible()) {
      console.log('✓ Microphone button found');
      // Just check it exists, don't actually click (would need mic permissions)
    }
    
    console.log('✓ Production test completed');
    console.log('   Check screenshots: production-openai-before.png and production-openai-after.png');
    
  } else {
    console.log('✗ OpenAI button not found');
  }
  
  await browser.close();
})();