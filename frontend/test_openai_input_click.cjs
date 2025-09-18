const playwright = require('playwright');

async function testOpenAIInputClick() {
  console.log('🎯 TESTING: Click directly on input element');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture ALL console messages
  page.on('console', (msg) => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      console.log('🔴 CONSOLE ERROR:', text);
    } else if (type === 'warn') {
      console.log('⚠️ CONSOLE WARN:', text);
    } else {
      console.log('📝 CONSOLE LOG:', text);
    }
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
    
    // Click the actual input element (not container)
    const toggleInput = page.locator('input[data-testid="connection-toggle"]');
    console.log('🎯 Clicking toggle input directly...');
    await toggleInput.click();
    console.log('✅ Clicked toggle input');
    
    // Wait and check for connection
    console.log('⏳ Waiting for connection...');
    await page.waitForTimeout(8000);
    
    // Check final state
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Final toggle status: "${toggleText}"`);
    
    const textInput = page.locator('input[data-testid="message-input"]');
    const inputVisible = await textInput.isVisible();
    console.log(`📝 Text input visible: ${inputVisible}`);
    
    if (inputVisible) {
      console.log('🎉 SUCCESS: OpenAI connection working!');
    } else {
      console.log('❌ Connection failed or still pending');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIInputClick().catch(console.error);