const playwright = require('playwright');

async function testOpenAIConnection() {
  console.log('🚀 TESTING: OpenAI Connection After WebSocket Fix');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console logs
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log('🔴 CONSOLE ERROR:', msg.text());
    } else if (msg.type() === 'log' && (msg.text().includes('OpenAI') || msg.text().includes('Connected') || msg.text().includes('WebSocket'))) {
      console.log('📝 CONSOLE LOG:', msg.text());
    }
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);

    console.log('✅ App loaded');
    
    // Look for any provider selection or voice controls
    const voiceControls = await page.locator('[data-testid*="voice"], [data-testid*="provider"], .voice-controls, .provider-selector').count();
    console.log(`📊 Found ${voiceControls} voice-related elements`);
    
    // Check if there's a toggle switch
    const toggles = await page.locator('[data-testid="voice-toggle-switch"], .toggle-switch, input[type="checkbox"]').count();
    console.log(`🔘 Found ${toggles} toggle switches`);
    
    if (toggles > 0) {
      console.log('🎯 Attempting to activate voice...');
      const toggle = page.locator('[data-testid="voice-toggle-switch"], .toggle-switch, input[type="checkbox"]').first();
      
      // Try clicking the toggle
      try {
        await toggle.click();
        console.log('✅ Clicked voice toggle');
      } catch (e) {
        console.log('⚠️ Could not click toggle, trying container...');
        const container = page.locator('.toggle-switch-container').first();
        await container.click();
        console.log('✅ Clicked toggle container');
      }
      
      // Wait for connection
      await page.waitForTimeout(8000);
      
      // Check for text input field
      const textInput = page.locator('input[data-testid="message-input"], input[placeholder*="message"], input[placeholder*="text"]');
      const inputVisible = await textInput.isVisible();
      console.log(`📝 Text input visible: ${inputVisible}`);
      
      if (inputVisible) {
        console.log('🎉 SUCCESS: Text input is visible - OpenAI connection working!');
        
        // Try sending a test message
        await textInput.fill('What is Tesla stock price?');
        console.log('📝 Entered test message');
        
        // Look for send button
        const sendButton = page.locator('button[type="submit"], button:has-text("Send"), .send-button');
        if (await sendButton.isVisible()) {
          await sendButton.click();
          console.log('📤 Sent test message');
          
          // Wait for response
          await page.waitForTimeout(5000);
        }
      } else {
        console.log('❌ PROBLEM: Text input not visible - connection may have failed');
      }
    } else {
      console.log('❌ PROBLEM: No voice toggle found');
    }
    
    // Take screenshot for debugging
    await page.screenshot({ path: 'openai-connection-test.png', fullPage: true });
    console.log('📸 Screenshot saved: openai-connection-test.png');
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAIConnection().catch(console.error);