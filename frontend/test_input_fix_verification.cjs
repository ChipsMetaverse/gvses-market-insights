const playwright = require('playwright');

async function verifyInputFix() {
  console.log('🔍 VERIFICATION TEST: Text Input Visibility Fix');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('📍 Step 2: Navigating to voice interface...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    console.log('📍 Step 3: Connecting to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000);
    
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    
    console.log('📍 Step 4: Checking text input visibility and position...');
    
    const input = await page.locator('input[data-testid="message-input"]');
    const inputVisible = await input.isVisible();
    const inputBounds = await input.boundingBox();
    
    console.log(`📝 Input visible: ${inputVisible}`);
    console.log(`📦 Input bounds:`, inputBounds);
    
    // Check if input is within viewport
    const viewportHeight = page.viewportSize().height;
    const isWithinViewport = inputBounds && inputBounds.y + inputBounds.height <= viewportHeight;
    
    console.log(`📱 Viewport height: ${viewportHeight}`);
    console.log(`📦 Input bottom edge: ${inputBounds ? inputBounds.y + inputBounds.height : 'N/A'}`);
    console.log(`✅ Input within viewport: ${isWithinViewport}`);
    
    await page.screenshot({ path: 'verification-input-fix.png', fullPage: false });
    
    if (inputVisible && isWithinViewport) {
      console.log('📍 Step 5: Testing text input functionality...');
      
      await input.click();
      await input.type('Test message after fix');
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonEnabled = await sendButton.isEnabled();
      
      console.log(`🔘 Send button enabled: ${sendButtonEnabled}`);
      
      if (sendButtonEnabled) {
        console.log('🎯 SUCCESS: Text input is visible, within viewport, and functional!');
        
        // Test sending the message
        await sendButton.click();
        console.log('📤 Test message sent successfully');
        
        // Wait a moment for response
        await page.waitForTimeout(3000);
        
        const messageCount = await page.locator('[data-testid="messages-container"] .conversation-message-enhanced').count();
        console.log(`💬 Messages in conversation: ${messageCount}`);
        
      } else {
        console.log('⚠️ Send button not enabled');
      }
      
    } else {
      console.log('❌ ISSUE STILL EXISTS: Input not visible or outside viewport');
    }
    
    console.log('\n🎯 FIX VERIFICATION SUMMARY:');
    console.log('='.repeat(40));
    console.log(`Connection Status: ${status}`);
    console.log(`Input Visible: ${inputVisible}`);
    console.log(`Within Viewport: ${isWithinViewport}`);
    console.log(`Screenshot saved: verification-input-fix.png`);
    
    // Keep browser open for manual testing
    console.log('\n🔍 Browser left open for manual testing...');
    console.log('Try typing a message and sending it!');
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Verification Error:', error.message);
    await page.screenshot({ path: 'verification-error.png' });
  }
}

verifyInputFix().catch(console.error);