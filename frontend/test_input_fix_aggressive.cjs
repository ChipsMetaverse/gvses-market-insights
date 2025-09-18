const playwright = require('playwright');

async function verifyAggressiveFix() {
  console.log('🔧 AGGRESSIVE FIX VERIFICATION: Text Input Viewport Fix');
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
    
    console.log('📍 Step 4: Checking AGGRESSIVE FIX results...');
    
    const input = await page.locator('input[data-testid="message-input"]');
    const inputVisible = await input.isVisible();
    const inputBounds = await input.boundingBox();
    
    console.log(`📝 Input visible: ${inputVisible}`);
    console.log(`📦 Input bounds:`, inputBounds);
    
    // Check if input is NOW within viewport
    const viewportHeight = page.viewportSize().height;
    const isWithinViewport = inputBounds && inputBounds.y + inputBounds.height <= viewportHeight;
    const inputTop = inputBounds ? inputBounds.y : 'N/A';
    const inputBottom = inputBounds ? inputBounds.y + inputBounds.height : 'N/A';
    
    console.log(`📱 Viewport height: ${viewportHeight}px`);
    console.log(`📦 Input top edge: ${inputTop}px`);
    console.log(`📦 Input bottom edge: ${inputBottom}px`);
    console.log(`✅ Input within viewport: ${isWithinViewport}`);
    
    // Calculate how much we improved
    if (inputBounds) {
      const previousBottom = 940; // From previous test
      const currentBottom = inputBounds.y + inputBounds.height;
      const improvement = previousBottom - currentBottom;
      console.log(`📈 Improvement: ${improvement}px reduction from previous position`);
    }
    
    await page.screenshot({ path: 'aggressive-fix-result.png', fullPage: false });
    
    if (inputVisible && isWithinViewport) {
      console.log('🎉 SUCCESS: AGGRESSIVE FIX WORKED!');
      console.log('📝 Text input is now visible and within viewport!');
      
      // Test functionality
      console.log('📍 Step 5: Testing text input functionality...');
      await input.click();
      await input.type('Aggressive fix test message');
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonEnabled = await sendButton.isEnabled();
      
      console.log(`🔘 Send button enabled: ${sendButtonEnabled}`);
      
      if (sendButtonEnabled) {
        console.log('🚀 FULL SUCCESS: Input visible, within viewport, AND functional!');
        
        // Send test message
        await sendButton.click();
        console.log('📤 Test message sent successfully');
        
        await page.waitForTimeout(2000);
        
      } else {
        console.log('⚠️ Send button not enabled (may need connection)');
      }
      
    } else {
      console.log('❌ STILL NOT FIXED: Need even more aggressive changes');
      
      if (!inputVisible) {
        console.log('   - Input element not visible');
      }
      if (!isWithinViewport) {
        console.log(`   - Input still outside viewport: ${inputBottom}px > ${viewportHeight}px`);
      }
    }
    
    console.log('\n🎯 AGGRESSIVE FIX SUMMARY:');
    console.log('='.repeat(40));
    console.log(`Connection Status: ${status}`);
    console.log(`Input Visible: ${inputVisible}`);
    console.log(`Within Viewport: ${isWithinViewport}`);
    console.log(`Input Position: ${inputTop}px - ${inputBottom}px`);
    console.log(`Viewport Height: ${viewportHeight}px`);
    console.log(`Screenshot: aggressive-fix-result.png`);
    
    // Keep browser open for manual verification
    console.log('\n🔍 Browser left open for manual verification...');
    console.log('Try typing messages to confirm the fix worked!');
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Verification Error:', error.message);
    await page.screenshot({ path: 'aggressive-fix-error.png' });
  }
}

verifyAggressiveFix().catch(console.error);