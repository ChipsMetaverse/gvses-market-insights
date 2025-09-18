const playwright = require('playwright');

async function testOpenAIFinal() {
  console.log('🚀 FINAL TEST: OpenAI Connection via Container Click');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console logs
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log('🔴 CONSOLE ERROR:', msg.text());
    } else if (msg.text().includes('OpenAI') || msg.text().includes('Connected') || msg.text().includes('WebSocket') || msg.text().includes('voice') || msg.text().includes('realtime') || msg.text().includes('connection')) {
      console.log('📝 CONSOLE LOG:', msg.text());
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
    
    // Click the visible toggle container (not the hidden input)
    const toggleContainer = page.locator('.toggle-switch-container');
    console.log('🎯 Clicking toggle container...');
    await toggleContainer.click();
    console.log('✅ Clicked toggle container');
    
    // Wait for connection to establish
    console.log('⏳ Waiting for OpenAI WebSocket connection...');
    await page.waitForTimeout(8000);
    
    // Check connection status by looking at toggle text
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Toggle status: "${toggleText}"`);
    
    // Check if text input is now visible
    const textInput = page.locator('input[data-testid="message-input"]');
    const inputVisible = await textInput.isVisible();
    console.log(`📝 Text input visible: ${inputVisible}`);
    
    if (inputVisible) {
      console.log('🎉 SUCCESS: OpenAI connection established! Text input is visible!');
      
      // Send test message
      await textInput.fill('What is the Tesla stock price?');
      console.log('📝 Entered test message');
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      if (await sendButton.isVisible() && !(await sendButton.isDisabled())) {
        await sendButton.click();
        console.log('📤 Sent test message to OpenAI Realtime');
        
        // Wait and check for response
        console.log('⏳ Waiting for OpenAI response...');
        await page.waitForTimeout(10000);
        
        // Check messages
        const messagesContainer = page.locator('[data-testid="messages-container"]');
        const messages = messagesContainer.locator('.conversation-message-enhanced');
        const messageCount = await messages.count();
        console.log(`💬 Conversation messages: ${messageCount}`);
        
        if (messageCount > 0) {
          console.log('🎊 COMPLETE SUCCESS: OpenAI Realtime conversation working!');
          
          // Get first message text for verification
          const firstMessageText = await messages.first().locator('.message-text-enhanced').textContent();
          console.log(`📖 First message: "${firstMessageText}"`);
        } else {
          console.log('⏳ No messages yet - response may take longer');
        }
      }
    } else {
      console.log('❌ Text input still not visible - connection may have failed');
      
      // Check if there are any error messages
      const errorElements = page.locator('.error, .alert, [class*="error"]');
      const errorCount = await errorElements.count();
      if (errorCount > 0) {
        const errorText = await errorElements.first().textContent();
        console.log(`🚨 Error detected: "${errorText}"`);
      }
    }
    
    // Take screenshot
    await page.screenshot({ path: 'openai-final-test.png', fullPage: true });
    console.log('📸 Screenshot saved: openai-final-test.png');
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIFinal().catch(console.error);