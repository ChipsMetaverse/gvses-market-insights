const { chromium } = require('playwright');

async function testConsoleErrors() {
  console.log('🔍 Capturing console errors when clicking Connect...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Capture ALL console messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      console.log('❌ ERROR:', text);
      // Get stack trace if available
      msg.args().forEach(async arg => {
        try {
          const val = await arg.jsonValue();
          if (val && val.stack) {
            console.log('   Stack:', val.stack);
          }
        } catch {}
      });
    } else if (type === 'warning') {
      console.log('⚠️ WARNING:', text);
    } else if (text.includes('handleConnectToggle') || text.includes('startConversation') || text.includes('voiceProvider')) {
      console.log('📝 LOG:', text);
    }
  });
  
  // Also capture page errors
  page.on('pageerror', error => {
    console.log('💥 PAGE ERROR:', error.message);
    console.log('   Stack:', error.stack);
  });
  
  await page.goto('http://localhost:5174');
  console.log('📍 Page loaded\n');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  await page.click('button:has-text("Voice + Manual Control")');
  console.log('📍 Voice tab clicked\n');
  await page.waitForTimeout(1000);
  
  // First, check what the current provider is
  const provider = await page.evaluate(() => {
    const dropdown = document.querySelector('.provider-dropdown');
    return dropdown ? dropdown.value : 'unknown';
  });
  console.log('📍 Current provider:', provider, '\n');
  
  // Now click the Connect toggle
  console.log('📍 Clicking Connect toggle...\n');
  await page.click('.toggle-switch-container');
  
  // Wait to capture any errors
  await page.waitForTimeout(2000);
  
  // Check if startConversation exists in the current hook
  const hookInfo = await page.evaluate(() => {
    // This will be undefined in production, but let's try
    return {
      provider: document.querySelector('.provider-dropdown')?.value,
      isConnected: document.querySelector('input[type="checkbox"]')?.checked
    };
  });
  
  console.log('\n📊 Final state:', hookInfo);
  
  await page.waitForTimeout(1000);
  await browser.close();
}

testConsoleErrors().catch(console.error);
