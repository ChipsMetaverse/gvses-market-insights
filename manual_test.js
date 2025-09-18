const { chromium } = require('playwright');

async function manualTest() {
  console.log('Opening browser for manual testing...\n');
  console.log('MANUAL TEST INSTRUCTIONS:');
  console.log('1. Click the green "Voice + Manual Control" tab');
  console.log('2. Click the "Connect" button in Voice Conversation section');
  console.log('3. Watch the console output below\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 0
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Monitor everything
  page.on('response', async res => {
    if (res.url().includes('/openai/realtime/session')) {
      const data = await res.json().catch(() => null);
      if (data) {
        console.log('\n🎉 SESSION CREATED:');
        console.log('   Session ID:', data.session_id);
        console.log('   WebSocket URL:', data.ws_url);
        
        if (data.ws_url?.includes('/realtime-relay/')) {
          console.log('   ✅ CORRECT: Using relay endpoint - tools will work!');
        } else {
          console.log('   ❌ WRONG: Not using relay endpoint - tools won\'t work!');
        }
        
        if (!data.ws_url?.includes('localhost:8000')) {
          console.log('   ✅ CORRECT: Dynamic URL (not hardcoded localhost)');
        } else {
          console.log('   ⚠️  WARNING: Still using hardcoded localhost');
        }
      }
    }
  });
  
  page.on('websocket', ws => {
    console.log('\n🔌 WEBSOCKET CONNECTED:');
    console.log('   URL:', ws.url());
    
    if (ws.url().includes('/realtime-relay/')) {
      console.log('   ✅ SUCCESS: Connected to relay endpoint!');
    } else if (ws.url().includes('/openai/realtime/ws')) {
      console.log('   ❌ FAILURE: Connected to wrong endpoint!');
    }
  });
  
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('session created') || text.includes('Session established')) {
      console.log('\n✅ Frontend confirmed: Session established');
    }
    if (text.includes('DEBUG') && text.includes('timeout')) {
      console.log('\n❌ ERROR: Forced timeout still present!');
    }
  });
  
  await page.goto('http://localhost:5174');
  
  console.log('\nBrowser is open. Please test manually and watch this console.\n');
  console.log('Press Ctrl+C when done to close the browser.\n');
  
  // Keep browser open
  await new Promise(() => {});
}

manualTest();
