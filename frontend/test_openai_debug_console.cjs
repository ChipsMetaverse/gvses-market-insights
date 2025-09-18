const playwright = require('playwright');

async function testOpenAIDebugConsole() {
  console.log('🔍 DEBUG: OpenAI Connection Console Logs');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture ALL console messages
  page.on('console', (msg) => {
    const type = msg.type();
    const text = msg.text();
    
    // Show all console messages for debugging
    if (type === 'error') {
      console.log('🔴 CONSOLE ERROR:', text);
    } else if (type === 'warn') {
      console.log('⚠️ CONSOLE WARN:', text);
    } else {
      console.log('📝 CONSOLE LOG:', text);
    }
  });

  // Capture network errors
  page.on('pageerror', (error) => {
    console.log('💥 PAGE ERROR:', error.message);
  });

  // Capture request failures
  page.on('requestfailed', (request) => {
    console.log('🚫 REQUEST FAILED:', request.url(), request.failure()?.errorText);
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');
    
    // Switch to OpenAI provider
    const providerDropdown = page.locator('[data-testid="provider-dropdown"]');
    await providerDropdown.selectOption('openai');
    console.log('🤖 Selected OpenAI Realtime provider');
    await page.waitForTimeout(1000);
    
    // Click the toggle container
    const toggleContainer = page.locator('.toggle-switch-container');
    console.log('🎯 Clicking toggle container...');
    await toggleContainer.click();
    console.log('✅ Clicked toggle container');
    
    // Wait longer and watch for any connection attempts
    console.log('⏳ Waiting for connection attempt...');
    await page.waitForTimeout(10000);
    
    // Check final state
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Final toggle status: "${toggleText}"`);
    
    const textInput = page.locator('input[data-testid="message-input"]');
    const inputVisible = await textInput.isVisible();
    console.log(`📝 Text input visible: ${inputVisible}`);
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIDebugConsole().catch(console.error);