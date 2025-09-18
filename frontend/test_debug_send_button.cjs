const playwright = require('playwright');

async function debugSendButton() {
  console.log('🔍 DEBUGGING SEND BUTTON CLICK');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture all console logs
  page.on('console', (msg) => {
    console.log(`📱 BROWSER: ${msg.text()}`);
  });

  try {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    // Navigate to voice tab
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    // Connect to OpenAI
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000);
    
    // Check connection status
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    
    if (!status?.includes('Connected')) {
      throw new Error('Not connected');
    }
    
    // Find and debug the message input and send button
    const messageInput = page.locator('input[data-testid="message-input"]');
    const sendButton = page.locator('button[data-testid="send-button"]');
    
    console.log('🔍 Checking input visibility...');
    const inputVisible = await messageInput.isVisible();
    console.log(`📝 Message input visible: ${inputVisible}`);
    
    console.log('🔍 Checking button visibility...');
    const buttonVisible = await sendButton.isVisible();
    console.log(`🔘 Send button visible: ${buttonVisible}`);
    
    if (inputVisible) {
      console.log('⌨️ Typing test message...');
      await messageInput.clear();
      await messageInput.type('Hello AI, what is 2+2?');
      
      console.log('🔍 Checking button enabled state...');
      const buttonEnabled = await sendButton.isEnabled();
      console.log(`🔘 Send button enabled: ${buttonEnabled}`);
      
      if (buttonEnabled) {
        console.log('👆 Clicking send button...');
        await sendButton.click();
        console.log('✅ Send button clicked');
        
        // Wait for any console logs
        await page.waitForTimeout(5000);
      } else {
        console.log('❌ Send button is disabled');
      }
    } else {
      console.log('❌ Message input not visible');
    }
    
    // Keep browser open for manual inspection
    console.log('🔍 Keeping browser open for manual inspection...');
    await new Promise(() => {}); // Keep alive
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    // Browser stays open
  }
}

debugSendButton().catch(console.error);