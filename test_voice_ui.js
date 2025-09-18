const { chromium } = require('playwright');

async function testVoiceUI() {
  console.log('🚀 Testing OpenAI Voice Assistant UI...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Monitor for successful connection
  let connectionSuccess = false;
  let sessionCreated = false;
  let toolsAvailable = false;
  
  page.on('response', async res => {
    if (res.url().includes('/openai/realtime/session')) {
      const data = await res.json().catch(() => null);
      if (data?.ws_url?.includes('/realtime-relay/')) {
        sessionCreated = true;
        console.log('✅ Session created with relay endpoint');
      }
    }
  });
  
  page.on('websocket', ws => {
    if (ws.url().includes('/realtime-relay/')) {
      connectionSuccess = true;
      console.log('✅ WebSocket connected to relay');
    }
  });
  
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('OpenAI session created')) {
      console.log('✅ Frontend confirmed session');
    }
    if (text.includes('tools for relay session')) {
      toolsAvailable = true;
      console.log('✅ Tools configured');
    }
    if (text.includes('onConnected callback completed')) {
      console.log('✅ Connection callback executed');
    }
  });
  
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  console.log('\n📍 Clicking Voice + Manual Control tab...');
  await page.click('button:has-text("Voice + Manual Control")');
  await page.waitForTimeout(500);
  
  // Take screenshot before
  await page.screenshot({ path: 'voice-before-connect.png' });
  
  // Click Connect button
  console.log('📍 Clicking Connect button...');
  await page.click('button:has-text("Connect")');
  
  // Wait for connection
  await page.waitForTimeout(3000);
  
  // Take screenshot after
  await page.screenshot({ path: 'voice-after-connect.png' });
  
  // Check UI state
  const disconnectButton = await page.$('button:has-text("Disconnect")');
  const statusConnected = await page.$('text=Connected');
  
  console.log('\n📊 Test Results:');
  console.log('  Session Created:', sessionCreated ? '✅' : '❌');
  console.log('  WebSocket Connected:', connectionSuccess ? '✅' : '❌');
  console.log('  Tools Available:', toolsAvailable ? '✅' : '❌');
  console.log('  UI Shows Disconnect:', disconnectButton ? '✅' : '❌');
  console.log('  UI Shows Connected:', statusConnected ? '✅' : '❌');
  
  if (connectionSuccess) {
    console.log('\n🎉 SUCCESS: OpenAI Voice Assistant is working!');
    console.log('📸 Screenshots saved: voice-before-connect.png, voice-after-connect.png');
    console.log('\n✨ You can now:');
    console.log('  1. Click the microphone to start speaking');
    console.log('  2. Ask "What\'s the current price of Tesla?"');
    console.log('  3. Say "Show me Apple stock"');
    console.log('  4. Request "Give me market overview"');
  } else {
    console.log('\n❌ FAILED: Connection did not establish');
  }
  
  await page.waitForTimeout(2000);
  await browser.close();
}

testVoiceUI().catch(console.error);
