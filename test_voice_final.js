const { chromium } = require('playwright');

async function testVoiceFinal() {
  console.log('🚀 Final OpenAI Voice Assistant Test...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000  // Slow for visibility
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Monitor console for all messages
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('OpenAI') || text.includes('connect') || text.includes('Connect')) {
      console.log('📝 Console:', text);
    }
  });
  
  // Monitor network
  page.on('response', async res => {
    if (res.url().includes('/openai/realtime/session')) {
      const data = await res.json().catch(() => null);
      if (data) {
        console.log('✅ Session endpoint called!');
        console.log('   Response:', data);
      }
    }
  });
  
  page.on('websocket', ws => {
    console.log('✅ WebSocket opened:', ws.url());
  });
  
  await page.goto('http://localhost:5174');
  console.log('📍 Page loaded');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  await page.click('button:has-text("Voice + Manual Control")');
  console.log('📍 Voice tab opened');
  await page.waitForTimeout(1000);
  
  // Find and click the toggle input directly
  console.log('📍 Looking for toggle switch...');
  
  // Try multiple selectors
  const selectors = [
    'input[type="checkbox"]',  // Toggle switches are often checkboxes
    '.toggle-switch input',
    '.toggle-switch-container input',
    'label:has-text("Connect")',
    '.voice-control-header input'
  ];
  
  let clicked = false;
  for (const selector of selectors) {
    const element = await page.$(selector);
    if (element) {
      console.log(`   Found element with selector: ${selector}`);
      await element.click();
      clicked = true;
      break;
    }
  }
  
  if (!clicked) {
    console.log('   No toggle input found, clicking the container...');
    await page.click('.toggle-switch-container');
  }
  
  console.log('📍 Waiting for connection...');
  await page.waitForTimeout(3000);
  
  // Take final screenshot
  await page.screenshot({ path: 'voice-final-state.png' });
  
  // Check final state
  const messages = await page.$$eval('.voice-conversation', els => 
    els.map(el => el.textContent)
  );
  console.log('📍 Conversation area:', messages);
  
  console.log('\n✅ Test complete. Check voice-final-state.png');
  console.log('📝 Manual steps to verify:');
  console.log('  1. Look at the browser window');
  console.log('  2. Toggle should be in "on" position');
  console.log('  3. Function calling indicator should be active');
  
  // Keep browser open for manual verification
  await page.waitForTimeout(5000);
  await browser.close();
}

testVoiceFinal().catch(console.error);
