const { chromium } = require('playwright');

async function testOpenAILocalhost() {
  console.log('🔍 Verifying OpenAI Voice Assistant on localhost...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 300
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Track all important events
  const events = {
    apiKeyStatus: null,
    sessionCreated: false,
    wsConnected: false,
    wsUrl: null,
    errors: [],
    logs: []
  };
  
  // Monitor console for errors and key messages
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      events.errors.push(text);
      console.log('❌ Console Error:', text);
    } else if (text.includes('OPENAI') || text.includes('OpenAI') || text.includes('session') || text.includes('WebSocket')) {
      events.logs.push(text);
      console.log('📝 Relevant Log:', text);
    }
  });
  
  // Monitor API responses
  page.on('response', async res => {
    const url = res.url();
    
    // Check session creation endpoint
    if (url.includes('/openai/realtime/session')) {
      try {
        const data = await res.json();
        events.sessionCreated = true;
        events.wsUrl = data.ws_url;
        console.log('\n✅ Session Endpoint Response:');
        console.log('   Status:', res.status());
        console.log('   Session ID:', data.session_id);
        console.log('   WS URL:', data.ws_url);
        console.log('   Using Relay:', data.ws_url?.includes('/realtime-relay/') ? 'YES ✅' : 'NO ❌');
      } catch (e) {
        console.log('❌ Failed to parse session response:', e.message);
      }
    }
    
    // Check health endpoint for API key status
    if (url.includes('/health')) {
      try {
        const data = await res.json();
        events.apiKeyStatus = data.openai_configured ? 'configured' : 'missing';
      } catch (e) {}
    }
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    events.wsConnected = true;
    console.log('\n🔌 WebSocket Connection:');
    console.log('   URL:', ws.url());
    console.log('   Protocol:', ws.url().startsWith('wss://') ? 'Secure (wss)' : 'Insecure (ws)');
    
    // Listen for first few frames
    let frameCount = 0;
    ws.on('framesent', ({ payload }) => {
      if (frameCount++ < 3 && payload) {
        try {
          const data = JSON.parse(payload);
          console.log('   → Sent:', data.type || 'unknown type');
        } catch {}
      }
    });
    
    ws.on('framereceived', ({ payload }) => {
      if (frameCount++ < 3 && payload) {
        try {
          const data = JSON.parse(payload);
          console.log('   ← Received:', data.type || 'unknown type');
          if (data.type === 'session.created') {
            console.log('   ✅ Session established with OpenAI!');
          }
        } catch {}
      }
    });
    
    ws.on('close', () => {
      console.log('   🔌 WebSocket closed');
    });
  });
  
  // Navigate to app
  console.log('📍 Loading http://localhost:5174...');
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(1000);
  
  // Check health status first
  console.log('\n📍 Checking backend health...');
  await page.goto('http://localhost:8000/health');
  await page.waitForTimeout(500);
  const healthText = await page.textContent('body');
  console.log('   Backend Health:', healthText);
  
  // Go back to main app
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  console.log('\n📍 Activating Voice tab...');
  await page.click('button:has-text("Voice + Manual Control")');
  await page.waitForTimeout(500);
  
  // Check current provider
  const provider = await page.inputValue('.provider-dropdown');
  console.log('   Current Provider:', provider);
  
  // Select OpenAI if not already selected
  if (provider !== 'openai') {
    console.log('   Switching to OpenAI provider...');
    await page.selectOption('.provider-dropdown', 'openai');
    await page.waitForTimeout(500);
  }
  
  // Take screenshot before connection
  await page.screenshot({ path: 'openai-verify-before.png' });
  
  // Click Connect
  console.log('\n📍 Clicking Connect button...');
  await page.click('.toggle-switch-container');
  
  // Wait for connection
  await page.waitForTimeout(3000);
  
  // Take screenshot after connection
  await page.screenshot({ path: 'openai-verify-after.png' });
  
  // Check UI state
  const isConnected = await page.isChecked('input[type="checkbox"]');
  const hasDisconnectButton = await page.$('button:has-text("Disconnect")');
  
  // Final report
  console.log('\n' + '='.repeat(50));
  console.log('📊 VERIFICATION RESULTS:');
  console.log('='.repeat(50));
  console.log('✓ Backend Health:', events.apiKeyStatus === 'configured' ? '✅ API Key Configured' : '❌ API Key Missing');
  console.log('✓ Session Created:', events.sessionCreated ? '✅ Yes' : '❌ No');
  console.log('✓ WebSocket Connected:', events.wsConnected ? '✅ Yes' : '❌ No');
  console.log('✓ Using Relay Server:', events.wsUrl?.includes('/realtime-relay/') ? '✅ Yes' : '❌ No');
  console.log('✓ UI Shows Connected:', isConnected ? '✅ Yes' : '❌ No');
  console.log('✓ Console Errors:', events.errors.length === 0 ? '✅ None' : `❌ ${events.errors.length} errors`);
  
  if (events.errors.length > 0) {
    console.log('\n❌ Errors Found:');
    events.errors.forEach(e => console.log('   -', e));
  }
  
  if (events.wsConnected && events.sessionCreated && isConnected) {
    console.log('\n🎉 SUCCESS: OpenAI Voice Assistant is fully operational!');
    console.log('📸 Screenshots saved: openai-verify-before.png, openai-verify-after.png');
  } else {
    console.log('\n⚠️  Some components not working. Check the details above.');
  }
  
  console.log('='.repeat(50));
  
  await page.waitForTimeout(2000);
  await browser.close();
}

testOpenAILocalhost().catch(console.error);