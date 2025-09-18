const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture all console messages and errors
  const allLogs = [];
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    if (!text.includes('contentScript.js')) {
      allLogs.push({ type, text, time: new Date().toISOString() });
      console.log(`[${type}] ${text}`);
    }
  });
  
  page.on('pageerror', error => {
    allLogs.push({ type: 'pageerror', text: error.message, time: new Date().toISOString() });
    console.log('[PAGE ERROR]', error.message);
  });
  
  // Monitor WebSocket connections
  const wsConnections = [];
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket created:', url);
    wsConnections.push({ url, status: 'created', time: new Date().toISOString() });
    
    ws.on('framesent', data => {
      const preview = data.payload?.substring(0, 200);
      console.log('📤 WS sent:', preview);
    });
    
    ws.on('framereceived', data => {
      const preview = data.payload?.substring(0, 200);
      console.log('📥 WS received:', preview);
    });
    
    ws.on('close', () => {
      console.log('❌ WebSocket closed:', url);
      const conn = wsConnections.find(c => c.url === url);
      if (conn) conn.status = 'closed';
    });
    
    ws.on('error', error => {
      console.log('⚠️ WebSocket error:', url, error);
      const conn = wsConnections.find(c => c.url === url);
      if (conn) conn.error = error;
    });
  });
  
  console.log('\n=== TESTING OPENAI MIC CONNECTION ===\n');
  
  // Navigate to the app
  console.log('1. Navigating to app...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Select OpenAI provider
  console.log('\n2. Selecting OpenAI provider...');
  const openaiButton = await page.locator('button:has-text("OpenAI")').first();
  if (await openaiButton.count() > 0) {
    await openaiButton.click();
    console.log('   ✓ Clicked OpenAI button');
    await page.waitForTimeout(1000);
  }
  
  // Look for the mic button
  console.log('\n3. Looking for mic button...');
  const micButton = await page.locator('button.mic-button, .voice-control-button, button:has(svg), button').filter({ hasText: /mic|connect/i });
  const micButtonCount = await micButton.count();
  console.log(`   Found ${micButtonCount} potential mic buttons`);
  
  // Try to find it by the voice conversation area
  const voiceArea = await page.locator('.voice-conversation, .voice-provider, .voice-control').first();
  const voiceAreaExists = await voiceArea.count() > 0;
  console.log(`   Voice area exists: ${voiceAreaExists}`);
  
  // Try clicking the mic icon/button
  console.log('\n4. Attempting to click mic button...');
  
  // Multiple strategies to find the mic button
  const selectors = [
    'button:has(path[d*="M12"])', // SVG mic icon
    'button.mic-button',
    '.voice-control button',
    'button:has-text("connect")',
    '.voice-conversation button',
    'svg[class*="mic"]',
    'button[aria-label*="mic"]'
  ];
  
  let clicked = false;
  for (const selector of selectors) {
    const element = await page.locator(selector).first();
    if (await element.count() > 0) {
      console.log(`   Found element with selector: ${selector}`);
      try {
        // Click the center of the voice conversation area
        const box = await element.boundingBox();
        if (box) {
          await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
          clicked = true;
          console.log(`   ✓ Clicked at position (${box.x + box.width / 2}, ${box.y + box.height / 2})`);
          break;
        }
      } catch (e) {
        console.log(`   Could not click ${selector}: ${e.message}`);
      }
    }
  }
  
  if (!clicked) {
    // Try clicking by coordinates in the voice area
    console.log('   Trying to click by coordinates in voice area...');
    const voiceBox = await page.locator('.voice-conversation').boundingBox();
    if (voiceBox) {
      await page.mouse.click(voiceBox.x + voiceBox.width / 2, voiceBox.y + voiceBox.height / 2);
      console.log(`   ✓ Clicked center of voice area`);
    }
  }
  
  // Wait for any WebSocket connections
  console.log('\n5. Waiting for WebSocket connections...');
  await page.waitForTimeout(5000);
  
  // Check for any error messages in the UI
  console.log('\n6. Checking for error messages in UI...');
  const errorMessages = await page.locator('.error, .error-message, [class*="error"]').allTextContents();
  if (errorMessages.length > 0) {
    console.log('   UI Errors found:');
    errorMessages.forEach(msg => console.log(`     - ${msg}`));
  } else {
    console.log('   No error messages in UI');
  }
  
  // Summary
  console.log('\n=== SUMMARY ===');
  console.log('\nWebSocket Connections:');
  wsConnections.forEach(conn => {
    console.log(`  ${conn.url}`);
    console.log(`    Status: ${conn.status}`);
    if (conn.error) console.log(`    Error: ${conn.error}`);
  });
  
  console.log('\nRelevant Console Logs:');
  const relevantLogs = allLogs.filter(log => 
    log.text.toLowerCase().includes('websocket') ||
    log.text.toLowerCase().includes('openai') ||
    log.text.toLowerCase().includes('realtime') ||
    log.text.toLowerCase().includes('relay') ||
    log.text.toLowerCase().includes('failed') ||
    log.text.toLowerCase().includes('error') ||
    log.text.toLowerCase().includes('connect')
  );
  
  relevantLogs.forEach(log => {
    console.log(`  [${log.type}] ${log.text}`);
  });
  
  // Take screenshot
  await page.screenshot({ path: 'openai-mic-test-result.png' });
  console.log('\nScreenshot saved as openai-mic-test-result.png');
  
  // Test browser console WebSocket creation
  console.log('\n7. Testing WebSocket via browser console...');
  const browserWSTest = await page.evaluate(async () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/realtime-relay/browser_test_123', 'openai-realtime');
      return new Promise((resolve) => {
        ws.onopen = () => resolve({ success: true, message: 'Connected with subprotocol' });
        ws.onerror = () => resolve({ success: false, message: 'Connection error' });
        ws.onclose = (e) => resolve({ success: false, message: `Closed: ${e.code} - ${e.reason}` });
        setTimeout(() => resolve({ success: false, message: 'Timeout' }), 3000);
      });
    } catch (e) {
      return { success: false, message: e.message };
    }
  });
  console.log('   Browser WebSocket test:', JSON.stringify(browserWSTest, null, 2));
  
  console.log('\n=== TEST COMPLETE ===');
  
  await page.waitForTimeout(5000);
  await browser.close();
})();