const playwright = require('playwright');

async function triggerWebSocketConnection() {
  console.log('🔗 TRIGGERING WEBSOCKET CONNECTION FOR DEBUG');
  console.log('='.repeat(50));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('📍 PHASE 2: NAVIGATE TO VOICE TAB TO TRIGGER WEBSOCKET');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(5000);  // Wait longer to see backend logs
    
    console.log('✅ Voice tab clicked, check backend logs for debug output');
    console.log('🔍 Leaving browser open for inspection...');
    
    // Keep open for manual checking
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

triggerWebSocketConnection().catch(console.error);