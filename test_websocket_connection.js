const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Track WebSocket connections
  const websocketConnections = [];
  const websocketMessages = [];
  
  // Monitor console for WebSocket activity
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('WebSocket') || text.includes('connected') || text.includes('session')) {
      console.log('🔌 Console:', text.substring(0, 150));
      websocketMessages.push(text);
    }
  });
  
  // Monitor network for WebSocket connections
  page.on('websocket', ws => {
    console.log('🌐 WebSocket opened:', ws.url());
    websocketConnections.push(ws.url());
    
    ws.on('framesent', frameData => {
      try {
        const data = JSON.parse(frameData.payload.toString());
        if (data.type) {
          console.log('📤 WS Send:', data.type);
        }
      } catch {}
    });
    
    ws.on('framereceived', frameData => {
      try {
        const data = JSON.parse(frameData.payload.toString());
        if (data.type) {
          console.log('📥 WS Receive:', data.type);
          
          // Check for key events
          if (data.type === 'session.created') {
            console.log('✅ Session created successfully');
            console.log('   - Tools configured:', data.session?.tools?.length || 0);
            console.log('   - Turn detection:', data.session?.turn_detection?.type || 'none');
            console.log('   - Voice:', data.session?.voice || 'unknown');
          }
        }
      } catch {}
    });
    
    ws.on('close', () => {
      console.log('🔴 WebSocket closed');
    });
  });
  
  console.log('\n🚀 Starting WebSocket Connection Test...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded');
    
    // Wait for initialization
    await page.waitForTimeout(2000);
    
    // Navigate to Voice tab
    const voiceTab = await page.locator('[data-testid="voice-tab"]').first();
    await voiceTab.click();
    console.log('✅ Switched to Voice tab');
    
    // Select Agent provider (should be default)
    const providerDropdown = await page.locator('select').first();
    await providerDropdown.selectOption({ index: 0 }); // Agent is first option
    console.log('✅ Agent provider selected');
    
    // Wait a moment
    await page.waitForTimeout(1000);
    
    // Click Connect
    console.log('\n🎤 Initiating connection...\n');
    const connectToggle = await page.locator('text=Connect').first();
    await connectToggle.click();
    
    // Wait for WebSocket connection
    await page.waitForTimeout(5000);
    
    // Check connection status
    if (websocketConnections.length > 0) {
      console.log(`\n✅ WebSocket connections established: ${websocketConnections.length}`);
      websocketConnections.forEach(url => {
        console.log('   -', url);
        
        // Verify it's the correct relay endpoint
        if (url.includes('/realtime-relay/')) {
          console.log('   ✅ Correct relay endpoint');
        }
        if (url.includes('model=gpt-4o-realtime')) {
          console.log('   ✅ Correct model specified');
        }
      });
    } else {
      console.log('⚠️  No WebSocket connections detected');
    }
    
    // Summary
    console.log('\n📊 Connection Summary:');
    console.log(`   - WebSocket connections: ${websocketConnections.length}`);
    console.log(`   - Console messages about WebSocket: ${websocketMessages.length}`);
    
    // Test sending a message
    console.log('\n💬 Testing message sending...\n');
    const textInput = await page.locator('input[type="text"]').nth(1); // Second input (first is search)
    if (await textInput.isVisible()) {
      await textInput.fill('Hello, can you hear me?');
      await textInput.press('Enter');
      console.log('✅ Test message sent');
      
      // Wait for potential response
      await page.waitForTimeout(3000);
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  console.log('\n✨ WebSocket Test Complete\n');
  
  // Keep open for observation
  await page.waitForTimeout(5000);
  
  await browser.close();
})();