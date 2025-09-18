const playwright = require('playwright');

async function testOpenAIDirectConnection() {
  console.log('🔬 TESTING: Direct OpenAI connection with full debugging');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture ALL console messages and errors
  page.on('console', (msg) => {
    const type = msg.type();
    const text = msg.text();
    console.log(`🎯 ${type.toUpperCase()}: ${text}`);
  });

  page.on('pageerror', (error) => {
    console.log('💥 PAGE ERROR:', error.message);
  });

  page.on('requestfailed', (request) => {
    console.log('🚫 REQUEST FAILED:', request.url(), request.failure()?.errorText);
  });

  try {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');
    
    // Switch to OpenAI provider
    console.log('🔄 Switching to OpenAI provider...');
    await page.locator('[data-testid="provider-dropdown"]').selectOption('openai');
    await page.waitForTimeout(1000);
    
    // Click toggle to connect
    console.log('🎯 Clicking toggle to connect...');
    await page.locator('.toggle-switch-container').click();
    
    // Wait and observe
    console.log('⏳ Waiting for connection attempt...');
    await page.waitForTimeout(20000);
    
    // Check final state
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Final toggle status: "${toggleText}"`);
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIDirectConnection().catch(console.error);