const { chromium } = require('playwright');

async function testAgentDebug() {
  console.log('\n🔍 === DEBUGGING AGENT UI ===\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream']
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    const text = msg.text();
    if (!text.includes('Download the React DevTools')) {
      console.log(`[Browser]: ${text}`);
    }
  });
  
  try {
    console.log('1️⃣ Navigating to app...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // Look for any voice-related buttons
    console.log('\n2️⃣ Looking for voice assistant controls...');
    
    const buttons = await page.locator('button').all();
    console.log(`   Found ${buttons.length} buttons:`);
    
    for (const button of buttons) {
      const text = await button.textContent();
      const isVisible = await button.isVisible();
      console.log(`   - "${text}" (visible: ${isVisible})`);
    }
    
    // Look for OpenAI provider
    const providers = await page.locator('.provider-card, .provider-option, [class*="provider"]').all();
    console.log(`\n3️⃣ Found ${providers.length} provider elements`);
    
    // Try to find OpenAI provider
    const openaiProvider = page.locator('text=/OpenAI/i').first();
    if (await openaiProvider.isVisible()) {
      console.log('   ✅ Found OpenAI provider');
      await openaiProvider.click();
      await page.waitForTimeout(1000);
      
      // Now look for start button again
      const startButtons = await page.locator('button').all();
      console.log('\n4️⃣ Buttons after selecting OpenAI:');
      for (const button of startButtons) {
        const text = await button.textContent();
        const isVisible = await button.isVisible();
        if (isVisible) {
          console.log(`   - "${text}"`);
        }
      }
      
      // Try to start the assistant
      const connectButton = page.locator('button:has-text("Connect"), button:has-text("Start")').first();
      if (await connectButton.isVisible()) {
        console.log('\n5️⃣ Clicking connect/start button...');
        await connectButton.click();
        await page.waitForTimeout(3000);
        
        // Check connection status
        const statusElements = await page.locator('[class*="status"], [class*="connection"]').all();
        console.log('\n6️⃣ Status elements:');
        for (const elem of statusElements) {
          const text = await elem.textContent();
          console.log(`   - ${text}`);
        }
      }
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-agent-debug.png', fullPage: true });
    console.log('\n📸 Screenshot saved: test-agent-debug.png');
    
  } catch (error) {
    console.error('❌ Debug failed:', error);
  } finally {
    console.log('\n🏁 Debug complete. Check browser window.');
    await page.waitForTimeout(10000);
    await browser.close();
  }
}

testAgentDebug().catch(console.error);