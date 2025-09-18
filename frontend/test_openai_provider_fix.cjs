const playwright = require('playwright');

async function testOpenAIProviderFix() {
  console.log('🚀 TESTING: OpenAI Provider Connection Fix');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console logs
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log('🔴 CONSOLE ERROR:', msg.text());
    } else if (msg.text().includes('OpenAI') || msg.text().includes('Connected') || msg.text().includes('WebSocket') || msg.text().includes('voice') || msg.text().includes('provider')) {
      console.log('📝 CONSOLE LOG:', msg.text());
    }
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');
    
    // Look for provider dropdown
    const providerDropdown = page.locator('[data-testid="provider-dropdown"]');
    
    if (await providerDropdown.isVisible()) {
      console.log('✅ Provider dropdown found');
      
      // Switch to OpenAI provider
      await providerDropdown.selectOption('openai');
      console.log('🤖 Selected OpenAI Realtime provider');
      
      await page.waitForTimeout(1000);
      
      // Find and click the toggle switch
      const toggle = page.locator('[data-testid="connection-toggle"]');
      const toggleContainer = page.locator('.toggle-switch-container');
      
      if (await toggle.isVisible()) {
        console.log('🎯 Activating OpenAI voice connection...');
        try {
          await toggleContainer.click();
          console.log('✅ Clicked toggle container');
        } catch (e) {
          await toggle.click();
          console.log('✅ Clicked toggle input');
        }
        
        // Wait for connection to establish
        console.log('⏳ Waiting for OpenAI connection...');
        await page.waitForTimeout(8000);
        
        // Check for text input visibility
        const textInput = page.locator('input[data-testid="message-input"]');
        const inputVisible = await textInput.isVisible();
        console.log(`📝 Text input visible: ${inputVisible}`);
        
        if (inputVisible) {
          console.log('🎉 SUCCESS: OpenAI connection working - text input is visible!');
          
          // Test sending a message
          await textInput.fill('What is the current Tesla stock price?');
          console.log('📝 Entered test message');
          
          const sendButton = page.locator('button[data-testid="send-button"]');
          if (await sendButton.isVisible() && !(await sendButton.isDisabled())) {
            await sendButton.click();
            console.log('📤 Sent test message to OpenAI');
            
            // Wait for response
            console.log('⏳ Waiting for OpenAI response...');
            await page.waitForTimeout(10000);
            
            // Check for messages
            const messages = page.locator('[data-testid="messages-container"] .conversation-message-enhanced');
            const messageCount = await messages.count();
            console.log(`💬 Found ${messageCount} conversation messages`);
          } else {
            console.log('⚠️ Send button not available');
          }
        } else {
          console.log('❌ PROBLEM: Text input not visible - OpenAI connection failed');
          
          // Check connection state display
          const connectionStatus = await page.textContent('.voice-controls-row');
          console.log('🔍 Connection status area:', connectionStatus);
        }
      } else {
        console.log('❌ PROBLEM: Voice toggle not found');
      }
    } else {
      console.log('❌ PROBLEM: Provider dropdown not found');
    }
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'openai-provider-test.png', fullPage: true });
    console.log('📸 Screenshot saved: openai-provider-test.png');
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIProviderFix().catch(console.error);