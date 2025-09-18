const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture console messages
  const logs = [];
  page.on('console', msg => {
    const text = msg.text();
    if (!text.includes('contentScript.js')) {
      logs.push(`[${msg.type()}] ${text}`);
      console.log(`[${msg.type()}] ${text}`);
    }
  });
  
  // Monitor WebSocket connections
  const wsConnections = [];
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket created:', url);
    wsConnections.push(url);
    
    ws.on('close', () => {
      console.log('❌ WebSocket closed:', url);
    });
    
    ws.on('error', error => {
      console.log('⚠️ WebSocket error:', url, error);
    });
  });
  
  console.log('\n=== TESTING OPENAI WITH FIXES ===\n');
  
  // Navigate to the app
  console.log('1. Navigating to app...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Select OpenAI provider
  console.log('\n2. Selecting OpenAI provider...');
  const openaiButton = await page.locator('button:has-text("OpenAI")').first();
  await openaiButton.click();
  console.log('   ✓ Selected OpenAI');
  await page.waitForTimeout(1000);
  
  // Click the mic button to connect
  console.log('\n3. Clicking mic button to connect...');
  const micButton = await page.locator('.mic-button, .voice-control-button svg').first();
  
  // Click on the center of the mic area
  const voiceArea = await page.locator('.voice-conversation').boundingBox();
  if (voiceArea) {
    await page.mouse.click(voiceArea.x + voiceArea.width / 2, voiceArea.y + voiceArea.height / 2);
    console.log('   ✓ Clicked mic area');
  }
  
  // Wait for connection
  console.log('\n4. Waiting for WebSocket connection...');
  await page.waitForTimeout(5000);
  
  // Test direct WebSocket with subprotocol
  console.log('\n5. Testing direct WebSocket with subprotocol...');
  const wsTest = await page.evaluate(async () => {
    const sessionId = `test_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/realtime-relay/${sessionId}`;
    
    return new Promise((resolve) => {
      const ws = new WebSocket(wsUrl, 'openai-realtime');
      const result = { url: wsUrl, status: 'unknown', error: null, messages: [] };
      
      ws.onopen = () => {
        result.status = 'connected';
        result.messages.push('Connected successfully with subprotocol');
        ws.send(JSON.stringify({ type: 'test', message: 'Hello from test' }));
        setTimeout(() => {
          ws.close();
          resolve(result);
        }, 1000);
      };
      
      ws.onmessage = (event) => {
        result.messages.push(`Received: ${event.data.substring(0, 100)}`);
      };
      
      ws.onerror = (error) => {
        result.status = 'error';
        result.error = 'Connection failed';
        resolve(result);
      };
      
      ws.onclose = (event) => {
        if (result.status === 'unknown') {
          result.status = 'closed';
          result.error = `Code: ${event.code}, Reason: ${event.reason}`;
        }
      };
      
      setTimeout(() => {
        if (result.status === 'unknown') {
          result.status = 'timeout';
          ws.close();
          resolve(result);
        }
      }, 5000);
    });
  });
  
  console.log('   WebSocket test result:', JSON.stringify(wsTest, null, 2));
  
  // Check for errors
  console.log('\n=== SUMMARY ===');
  console.log('\nWebSocket Connections Created:');
  wsConnections.forEach(url => console.log(`  - ${url}`));
  
  const errors = logs.filter(log => log.includes('error') || log.includes('Error') || log.includes('Failed'));
  if (errors.length > 0) {
    console.log('\nErrors Found:');
    errors.forEach(err => console.log(`  ${err}`));
  } else {
    console.log('\n✅ No errors detected!');
  }
  
  // Take screenshot
  await page.screenshot({ path: 'openai-fixed-test.png' });
  console.log('\nScreenshot saved as openai-fixed-test.png');
  
  console.log('\n=== TEST COMPLETE ===');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();