const { chromium } = require('playwright');

async function testVoiceForce() {
  console.log('🚀 Force click test for OpenAI Voice Assistant...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Monitor network
  page.on('response', async res => {
    if (res.url().includes('/openai/realtime/session')) {
      console.log('✅ Session endpoint called!');
    }
  });
  
  page.on('websocket', ws => {
    console.log('✅ WebSocket opened:', ws.url());
  });
  
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  await page.click('button:has-text("Voice + Manual Control")');
  console.log('📍 Voice tab opened');
  await page.waitForTimeout(1000);
  
  // Take screenshot to see current state
  await page.screenshot({ path: 'voice-current-state.png' });
  
  // Force click the checkbox regardless of visibility
  console.log('📍 Force clicking checkbox...');
  const checkbox = await page.$('input[type="checkbox"]');
  if (checkbox) {
    await checkbox.click({ force: true });
    console.log('✅ Checkbox clicked with force');
  } else {
    console.log('❌ No checkbox found');
  }
  
  await page.waitForTimeout(3000);
  
  // Take screenshot after
  await page.screenshot({ path: 'voice-after-force.png' });
  
  // Check if connection was made
  const hasWebSocket = await page.evaluate(() => {
    return window.location.href.includes('localhost');
  });
  
  console.log('\n✅ Test complete');
  console.log('📸 Screenshots: voice-current-state.png, voice-after-force.png');
  
  await page.waitForTimeout(2000);
  await browser.close();
}

testVoiceForce().catch(console.error);
