const playwright = require('playwright');

async function manualUICheck() {
  console.log('🔍 MANUAL UI CHECK: Text Input Visibility');
  console.log('='.repeat(50));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('📍 Step 2: Navigating to voice tab...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    console.log('📍 Step 3: Checking initial state...');
    const inputVisible = await page.locator('input[data-testid="message-input"]').isVisible();
    console.log(`📝 Text input visible BEFORE connection: ${inputVisible}`);
    
    console.log('📍 Step 4: Connecting to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    
    console.log('📍 Step 5: Waiting for connection...');
    await page.waitForTimeout(8000);
    
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    
    console.log('📍 Step 6: Checking text input after connection...');
    const inputVisibleAfter = await page.locator('input[data-testid="message-input"]').isVisible();
    console.log(`📝 Text input visible AFTER connection: ${inputVisibleAfter}`);
    
    if (inputVisibleAfter) {
      console.log('✅ TEXT INPUT IS VISIBLE!');
      console.log('📝 You can now type messages in the text field at the bottom');
    } else {
      console.log('❌ TEXT INPUT NOT VISIBLE');
      console.log('🔍 Checking connection state...');
      
      // Check if connected
      if (status?.includes('Connected')) {
        console.log('🔗 Connected but input not visible - possible CSS issue');
      } else {
        console.log('🔗 Not connected - input hidden as expected');
      }
    }
    
    console.log('\n📋 MANUAL TEST INSTRUCTIONS:');
    console.log('1. Leave this browser window open');
    console.log('2. If connected, you should see a text input at the bottom');
    console.log('3. Type a message and press Enter to test');
    console.log('4. Check the "Voice Conversation" section for messages');
    
    // Keep browser open for manual inspection
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

manualUICheck().catch(console.error);