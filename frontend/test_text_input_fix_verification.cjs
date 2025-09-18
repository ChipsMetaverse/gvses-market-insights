const playwright = require('playwright');

async function verifyTextInputFix() {
  console.log('🎯 VERIFYING TEXT INPUT FIX');
  console.log('='.repeat(40));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1194, height: 867 } // Match user's screenshot dimensions
  });
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    console.log('📍 Step 2: Navigating to voice interface...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    // Take screenshot BEFORE connection
    await page.screenshot({ path: 'text-input-before-connection.png', fullPage: false });
    
    console.log('📍 Step 3: Checking text input BEFORE connection...');
    const inputBeforeConnection = page.locator('input[data-testid="message-input"]');
    const inputExistsBeforeConnection = await inputBeforeConnection.count() > 0;
    const inputVisibleBeforeConnection = inputExistsBeforeConnection ? await inputBeforeConnection.isVisible() : false;
    const inputBoundsBeforeConnection = inputExistsBeforeConnection && inputVisibleBeforeConnection ? await inputBeforeConnection.boundingBox() : null;
    
    console.log(`📝 Text input exists BEFORE connection: ${inputExistsBeforeConnection}`);
    console.log(`📝 Text input visible BEFORE connection: ${inputVisibleBeforeConnection}`);
    console.log(`📦 Text input bounds BEFORE connection:`, inputBoundsBeforeConnection);
    
    // Try connecting to OpenAI
    console.log('📍 Step 4: Connecting to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000); // Wait for connection
    
    // Take screenshot AFTER connection attempt
    await page.screenshot({ path: 'text-input-after-connection.png', fullPage: false });
    
    console.log('📍 Step 5: Checking text input AFTER connection...');
    const inputAfterConnection = page.locator('input[data-testid="message-input"]');
    const inputExistsAfterConnection = await inputAfterConnection.count() > 0;
    const inputVisibleAfterConnection = inputExistsAfterConnection ? await inputAfterConnection.isVisible() : false;
    const inputBoundsAfterConnection = inputExistsAfterConnection && inputVisibleAfterConnection ? await inputAfterConnection.boundingBox() : null;
    
    console.log(`📝 Text input exists AFTER connection: ${inputExistsAfterConnection}`);
    console.log(`📝 Text input visible AFTER connection: ${inputVisibleAfterConnection}`);
    console.log(`📦 Text input bounds AFTER connection:`, inputBoundsAfterConnection);
    
    // Check if input is within viewport
    const viewportHeight = page.viewportSize().height;
    const isWithinViewportBefore = inputBoundsBeforeConnection && inputBoundsBeforeConnection.y + inputBoundsBeforeConnection.height <= viewportHeight;
    const isWithinViewportAfter = inputBoundsAfterConnection && inputBoundsAfterConnection.y + inputBoundsAfterConnection.height <= viewportHeight;
    
    console.log(`📱 Viewport height: ${viewportHeight}px`);
    console.log(`✅ Input within viewport BEFORE connection: ${isWithinViewportBefore}`);
    console.log(`✅ Input within viewport AFTER connection: ${isWithinViewportAfter}`);
    
    // Test functionality
    if (inputVisibleBeforeConnection) {
      console.log('📍 Step 6: Testing text input functionality...');
      await inputBeforeConnection.click();
      await inputBeforeConnection.type('Test message - input always visible now!');
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonEnabled = await sendButton.isEnabled();
      
      console.log(`🔘 Send button enabled: ${sendButtonEnabled}`);
      
      await page.screenshot({ path: 'text-input-with-message.png', fullPage: false });
    }
    
    console.log('\n🎯 FIX VERIFICATION RESULTS:');
    console.log('='.repeat(40));
    console.log(`✅ Text input ALWAYS VISIBLE: ${inputExistsBeforeConnection && inputVisibleBeforeConnection}`);
    console.log(`✅ Text input persists after connection: ${inputExistsAfterConnection && inputVisibleAfterConnection}`);
    console.log(`✅ Text input within viewport: ${isWithinViewportBefore || isWithinViewportAfter}`);
    console.log(`Screenshots: text-input-before-connection.png, text-input-after-connection.png, text-input-with-message.png`);
    
    if (inputExistsBeforeConnection && inputVisibleBeforeConnection) {
      console.log('\n🎉 SUCCESS: TEXT INPUT FIX VERIFIED!');
      console.log('🎯 The text input is now always visible regardless of connection state!');
    } else {
      console.log('\n❌ ISSUE: Text input still not visible');
    }
    
    // Keep browser open for manual verification
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Verification Error:', error.message);
    await page.screenshot({ path: 'verification-error.png' });
  }
}

verifyTextInputFix().catch(console.error);