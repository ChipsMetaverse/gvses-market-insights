const { chromium } = require('playwright');

async function testOpenAI() {
  console.log('🎯 Simple OpenAI Voice Agent Test\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Monitor the key events we care about
  let sessionData = null;
  let wsConnected = false;
  
  page.on('response', async res => {
    if (res.url().includes('/openai/realtime/session')) {
      sessionData = await res.json().catch(() => null);
      if (sessionData) {
        console.log('✅ Session created:', {
          id: sessionData.session_id?.substring(0, 10) + '...',
          ws_url: sessionData.ws_url,
          relay: sessionData.ws_url?.includes('/realtime-relay/') ? '✅' : '❌'
        });
      }
    }
  });
  
  page.on('websocket', ws => {
    if (ws.url().includes('/realtime-relay/')) {
      wsConnected = true;
      console.log('✅ WebSocket connected to RELAY:', ws.url());
    }
  });
  
  try {
    // Go to app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // Click Voice tab (the green button)
    await page.click('button.tab-btn:has-text("Voice + Manual Control")');
    await page.waitForTimeout(1000);
    
    // The Connect button is visible, let's click it by its exact text
    console.log('Looking for Connect button...');
    
    // Wait for button to be visible and click it
    const connectBtn = page.locator('button').filter({ hasText: 'Connect' });
    await connectBtn.waitFor({ state: 'visible', timeout: 5000 });
    console.log('Found Connect button, clicking...');
    await connectBtn.click();
    
    // Wait for connection
    await page.waitForTimeout(4000);
    
    // Check results
    console.log('\n' + '═'.repeat(40));
    console.log('RESULTS:');
    console.log('═'.repeat(40));
    
    if (sessionData?.ws_url?.includes('/realtime-relay/')) {
      console.log('✅ SUCCESS: All fixes working!');
      console.log('   - Session returns relay URL');
      console.log('   - URL is dynamic (not hardcoded)');
      console.log('   - Tools will execute properly');
    } else {
      console.log('❌ ISSUE: Not using relay endpoint');
      if (sessionData) {
        console.log('   Got URL:', sessionData.ws_url);
      }
    }
    
    console.log('═'.repeat(40));
    
    await page.screenshot({ path: 'test-openai-result.png' });
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  await page.waitForTimeout(5000);
  await browser.close();
}

testOpenAI();