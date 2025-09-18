const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  const page = await context.newPage();
  
  // Comprehensive logging
  const logs = [];
  const errors = [];
  const wsConnections = new Map();
  
  page.on('console', msg => {
    const text = msg.text();
    if (!text.includes('contentScript.js') && !text.includes('[HMR]')) {
      logs.push(`[${msg.type()}] ${text}`);
      console.log(`[${msg.type()}] ${text}`);
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.toString());
    console.error('Page error:', error);
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket created:', url);
    wsConnections.set(url, { 
      status: 'created', 
      messages: [],
      startTime: Date.now() 
    });
    
    ws.on('framesent', frame => {
      const conn = wsConnections.get(url);
      if (conn && frame.payload) {
        try {
          const data = JSON.parse(frame.payload);
          conn.messages.push({ type: 'sent', data: data.type || 'unknown' });
        } catch {}
      }
    });
    
    ws.on('framereceived', frame => {
      const conn = wsConnections.get(url);
      if (conn && frame.payload) {
        try {
          const data = JSON.parse(frame.payload);
          conn.messages.push({ type: 'received', data: data.type || 'unknown' });
        } catch {}
      }
    });
    
    ws.on('close', () => {
      const conn = wsConnections.get(url);
      if (conn) {
        conn.status = 'closed';
        conn.duration = Date.now() - conn.startTime;
        console.log(`❌ WebSocket closed: ${url} (lasted ${conn.duration}ms)`);
      }
    });
    
    ws.on('error', error => {
      const conn = wsConnections.get(url);
      if (conn) {
        conn.status = 'error';
        conn.error = error.toString();
      }
      console.log('⚠️ WebSocket error:', url, error);
    });
  });
  
  console.log('\\n=== COMPREHENSIVE AGENT INTEGRATION TEST ===\\n');
  
  // Navigate to the app
  console.log('1. Navigating to app...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Take initial screenshot
  await page.screenshot({ path: 'test-1-initial-load.png' });
  console.log('   ✓ Initial load screenshot saved');
  
  // Test 1: ElevenLabs Provider
  console.log('\\n=== TEST 1: ElevenLabs Provider ===');
  console.log('2. Selecting ElevenLabs provider...');
  
  // Check if provider selector exists
  const providerSelector = await page.locator('.provider-selector').count();
  if (providerSelector > 0) {
    const elevenlabsButton = await page.locator('button:has-text("ElevenLabs")').first();
    await elevenlabsButton.click();
    console.log('   ✓ Selected ElevenLabs');
  } else {
    console.log('   ⚠️ Provider selector not found, using default');
  }
  
  await page.waitForTimeout(1000);
  
  // Click mic to connect ElevenLabs
  console.log('3. Clicking mic button to connect ElevenLabs...');
  const voiceArea1 = await page.locator('.voice-conversation').boundingBox();
  if (voiceArea1) {
    await page.mouse.click(voiceArea1.x + voiceArea1.width / 2, voiceArea1.y + voiceArea1.height / 2);
    console.log('   ✓ Clicked mic area for ElevenLabs');
  }
  
  // Wait for connection
  await page.waitForTimeout(5000);
  
  // Check for ElevenLabs WebSocket
  const elevenlabsWS = Array.from(wsConnections.keys()).find(url => 
    url.includes('convai.elevenlabs.io') || url.includes('elevenlabs')
  );
  console.log('   ElevenLabs WebSocket:', elevenlabsWS ? '✅ Connected' : '❌ Not found');
  
  await page.screenshot({ path: 'test-2-elevenlabs-connected.png' });
  
  // Disconnect ElevenLabs
  console.log('4. Disconnecting ElevenLabs...');
  await page.mouse.click(voiceArea1.x + voiceArea1.width / 2, voiceArea1.y + voiceArea1.height / 2);
  await page.waitForTimeout(2000);
  
  // Test 2: OpenAI Provider
  console.log('\\n=== TEST 2: OpenAI Realtime Provider ===');
  console.log('5. Switching to OpenAI provider...');
  
  const openaiButton = await page.locator('button:has-text("OpenAI")').first();
  if (await openaiButton.count() > 0) {
    await openaiButton.click();
    console.log('   ✓ Selected OpenAI');
    await page.waitForTimeout(1000);
    
    // Click mic to connect OpenAI
    console.log('6. Clicking mic button to connect OpenAI...');
    const voiceArea2 = await page.locator('.voice-conversation').boundingBox();
    if (voiceArea2) {
      await page.mouse.click(voiceArea2.x + voiceArea2.width / 2, voiceArea2.y + voiceArea2.height / 2);
      console.log('   ✓ Clicked mic area for OpenAI');
    }
    
    // Wait for connection
    await page.waitForTimeout(5000);
    
    // Check for OpenAI WebSocket with subprotocol
    const openaiWS = Array.from(wsConnections.keys()).find(url => 
      url.includes('realtime-relay') || url.includes('openai')
    );
    console.log('   OpenAI WebSocket:', openaiWS ? '✅ Connected' : '❌ Not found');
    
    if (openaiWS) {
      const conn = wsConnections.get(openaiWS);
      console.log(`   Messages exchanged: ${conn.messages.length}`);
      console.log(`   Connection status: ${conn.status}`);
    }
    
    await page.screenshot({ path: 'test-3-openai-connected.png' });
  } else {
    console.log('   ⚠️ OpenAI button not found');
  }
  
  // Test 3: Voice Command Testing (Text Input)
  console.log('\\n=== TEST 3: Voice Command Simulation ===');
  console.log('7. Testing text input commands...');
  
  // Find text input
  const textInput = await page.locator('input[type="text"][placeholder*="Type"]').first();
  if (await textInput.count() > 0) {
    // Test market query
    console.log('8. Sending market query...');
    await textInput.fill('What is the current price of Tesla?');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    // Test chart command
    console.log('9. Sending chart command...');
    await textInput.fill('Show me Apple stock chart');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    // Check if chart updated
    const chartTitle = await page.locator('.tv-lightweight-charts').count();
    console.log('   Chart present:', chartTitle > 0 ? '✅ Yes' : '❌ No');
    
    await page.screenshot({ path: 'test-4-after-commands.png' });
  } else {
    console.log('   ⚠️ Text input not found');
  }
  
  // Test 4: Market Data Loading
  console.log('\\n=== TEST 4: Market Data Verification ===');
  console.log('10. Checking market insights panel...');
  
  const stockCards = await page.locator('.stock-card').count();
  console.log(`   Stock cards found: ${stockCards}`);
  
  if (stockCards > 0) {
    // Get first stock card data
    const firstCard = await page.locator('.stock-card').first();
    const symbol = await firstCard.locator('.stock-symbol').textContent();
    const price = await firstCard.locator('.stock-price').textContent();
    console.log(`   First stock: ${symbol} - ${price}`);
  }
  
  // Test 5: News Loading
  console.log('\\n=== TEST 5: News Feed Verification ===');
  console.log('11. Checking news articles...');
  
  const newsArticles = await page.locator('.news-item').count();
  console.log(`   News articles found: ${newsArticles}`);
  
  // Test 6: Provider Switching Stability
  console.log('\\n=== TEST 6: Rapid Provider Switching ===');
  console.log('12. Testing rapid provider switching...');
  
  for (let i = 0; i < 3; i++) {
    // Switch to ElevenLabs
    const elButton = await page.locator('button:has-text("ElevenLabs")').first();
    if (await elButton.count() > 0) {
      await elButton.click();
      await page.waitForTimeout(500);
    }
    
    // Switch to OpenAI
    const oaButton = await page.locator('button:has-text("OpenAI")').first();
    if (await oaButton.count() > 0) {
      await oaButton.click();
      await page.waitForTimeout(500);
    }
  }
  
  console.log('   ✓ Rapid switching completed');
  
  // Test 7: Error Recovery
  console.log('\\n=== TEST 7: Error Recovery Testing ===');
  console.log('13. Testing WebSocket reconnection...');
  
  // Evaluate direct WebSocket test with subprotocol
  const wsTest = await page.evaluate(async () => {
    const sessionId = `test_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/realtime-relay/${sessionId}`;
    
    return new Promise((resolve) => {
      const ws = new WebSocket(wsUrl, 'openai-realtime');
      const result = { 
        url: wsUrl, 
        status: 'unknown', 
        error: null, 
        messages: [],
        subprotocol: null 
      };
      
      ws.onopen = () => {
        result.status = 'connected';
        result.subprotocol = ws.protocol;
        result.messages.push(`Connected with protocol: ${ws.protocol}`);
        
        // Send test message
        ws.send(JSON.stringify({ 
          type: 'response.create',
          response: {
            instructions: 'Test message'
          }
        }));
        
        setTimeout(() => {
          ws.close();
          resolve(result);
        }, 2000);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          result.messages.push(`Received: ${data.type || 'unknown'}`);
        } catch {
          result.messages.push('Received non-JSON message');
        }
      };
      
      ws.onerror = (error) => {
        result.status = 'error';
        result.error = 'Connection failed';
        resolve(result);
      };
      
      ws.onclose = (event) => {
        if (result.status === 'unknown') {
          result.status = 'closed';
          result.error = `Code: ${event.code}, Reason: ${event.reason || 'No reason'}`;
          resolve(result);
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
  
  // Final screenshot
  await page.screenshot({ path: 'test-8-final-state.png' });
  
  // Generate comprehensive report
  console.log('\\n=== COMPREHENSIVE TEST REPORT ===');
  
  console.log('\\n📊 Test Summary:');
  console.log(`   Total logs captured: ${logs.length}`);
  console.log(`   Errors encountered: ${errors.length}`);
  console.log(`   WebSocket connections: ${wsConnections.size}`);
  
  console.log('\\n🔌 WebSocket Analysis:');
  for (const [url, conn] of wsConnections) {
    console.log(`\\n   URL: ${url}`);
    console.log(`   Status: ${conn.status}`);
    console.log(`   Messages: ${conn.messages.length}`);
    if (conn.duration) {
      console.log(`   Duration: ${conn.duration}ms`);
    }
    if (conn.error) {
      console.log(`   Error: ${conn.error}`);
    }
    
    // Show message types
    const messageTypes = new Set(conn.messages.map(m => `${m.type}:${m.data}`));
    if (messageTypes.size > 0) {
      console.log(`   Message types: ${Array.from(messageTypes).slice(0, 5).join(', ')}`);
    }
  }
  
  if (errors.length > 0) {
    console.log('\\n❌ Errors Found:');
    errors.forEach(err => console.log(`   ${err}`));
  }
  
  // Check for specific issues
  console.log('\\n🔍 Issue Detection:');
  
  const subprotocolErrors = logs.filter(log => 
    log.includes('Sec-WebSocket-Protocol') || 
    log.includes('subprotocol')
  );
  console.log(`   Subprotocol issues: ${subprotocolErrors.length > 0 ? '❌ Yes' : '✅ None'}`);
  
  const toolErrors = logs.filter(log => 
    log.includes('tool') && 
    (log.includes('error') || log.includes('validation'))
  );
  console.log(`   Tool validation issues: ${toolErrors.length > 0 ? '❌ Yes' : '✅ None'}`);
  
  const connectionErrors = Array.from(wsConnections.values()).filter(
    conn => conn.status === 'error' || conn.error
  );
  console.log(`   Connection failures: ${connectionErrors.length > 0 ? '❌ Yes' : '✅ None'}`);
  
  // Performance metrics
  console.log('\\n⚡ Performance Metrics:');
  const successfulConnections = Array.from(wsConnections.values()).filter(
    conn => conn.messages.length > 0
  );
  if (successfulConnections.length > 0) {
    const avgDuration = successfulConnections
      .filter(c => c.duration)
      .reduce((sum, c) => sum + c.duration, 0) / successfulConnections.length;
    console.log(`   Average connection duration: ${Math.round(avgDuration)}ms`);
    
    const avgMessages = successfulConnections
      .reduce((sum, c) => sum + c.messages.length, 0) / successfulConnections.length;
    console.log(`   Average messages per connection: ${Math.round(avgMessages)}`);
  }
  
  // Overall status
  console.log('\\n📈 Overall Status:');
  const criticalIssues = errors.length + subprotocolErrors.length + connectionErrors.length;
  if (criticalIssues === 0) {
    console.log('   ✅ All systems operational!');
  } else {
    console.log(`   ⚠️ ${criticalIssues} issues detected - review logs above`);
  }
  
  console.log('\\n=== TEST COMPLETE ===');
  console.log('Screenshots saved:');
  console.log('  - test-1-initial-load.png');
  console.log('  - test-2-elevenlabs-connected.png');
  console.log('  - test-3-openai-connected.png');
  console.log('  - test-4-after-commands.png');
  console.log('  - test-8-final-state.png');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();