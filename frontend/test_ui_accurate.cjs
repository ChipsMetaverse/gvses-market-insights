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
  
  // Enhanced logging
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
  });
  
  console.log('\\n=== ACCURATE UI INTEGRATION TEST ===\\n');
  
  // Navigate to the app
  console.log('1. Navigating to app...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Verify initial UI elements
  console.log('\\n=== UI VERIFICATION ===');
  
  // Check Market Insights
  console.log('2. Checking Market Insights panel...');
  const marketInsights = await page.locator('text="MARKET INSIGHTS"').count();
  console.log(`   Market Insights header: ${marketInsights > 0 ? '✅ Found' : '❌ Not found'}`);
  
  // Count stock cards - using the actual structure
  const stockPrices = await page.locator('text=/\\$\\d+\\.\\d+/').count();
  console.log(`   Stock cards with prices: ${stockPrices}`);
  
  // Get TSLA card specifically
  const tslaCard = await page.locator('text="TSLA"').first();
  if (await tslaCard.count() > 0) {
    console.log('   ✅ TSLA card found');
    const tslaPrice = await page.locator('text=/\\$346/').first().textContent().catch(() => 'N/A');
    console.log(`   TSLA price: ${tslaPrice}`);
  }
  
  // Check Chart
  console.log('\\n3. Checking Interactive Chart...');
  const chartCanvas = await page.locator('canvas').count();
  console.log(`   Chart canvas elements: ${chartCanvas}`);
  
  // Check Technical Levels
  const qeLevel = await page.locator('text="QE Level"').count();
  const stLevel = await page.locator('text="ST Level"').count();
  const ltbLevel = await page.locator('text="LTB Level"').count();
  console.log(`   Technical levels: QE=${qeLevel > 0 ? '✅' : '❌'}, ST=${stLevel > 0 ? '✅' : '❌'}, LTB=${ltbLevel > 0 ? '✅' : '❌'}`);
  
  // Check Voice Provider Section
  console.log('\\n4. Checking Voice Provider section...');
  const voiceProviderText = await page.locator('text="VOICE PROVIDER:"').count();
  console.log(`   Voice Provider label: ${voiceProviderText > 0 ? '✅ Found' : '❌ Not found'}`);
  
  // Test ElevenLabs button
  const elevenlabsButton = await page.locator('button:has-text("ElevenLabs")');
  if (await elevenlabsButton.count() > 0) {
    console.log('   ✅ ElevenLabs button found');
    const isSelected = await elevenlabsButton.evaluate(el => 
      el.classList.contains('selected') || el.style.backgroundColor !== ''
    );
    console.log(`   ElevenLabs selected: ${isSelected ? 'Yes' : 'No'}`);
  }
  
  // Test OpenAI button
  const openaiButton = await page.locator('button:has-text("OpenAI")').filter({ hasText: 'Realtime' });
  if (await openaiButton.count() > 0) {
    console.log('   ✅ OpenAI Realtime button found');
  }
  
  // Check Voice Conversation area
  console.log('\\n5. Checking Voice Conversation area...');
  const voiceConversation = await page.locator('text="Voice Conversation"').count();
  console.log(`   Voice Conversation header: ${voiceConversation > 0 ? '✅ Found' : '❌ Not found'}`);
  
  const micIcon = await page.locator('svg').count();
  console.log(`   Mic icon (SVG elements): ${micIcon}`);
  
  const clickToConnect = await page.locator('text="Click mic to connect"').count();
  console.log(`   "Click mic to connect" text: ${clickToConnect > 0 ? '✅ Found' : '❌ Not found'}`);
  
  // Check Chart Analysis panel
  console.log('\\n6. Checking Chart Analysis panel...');
  const chartAnalysis = await page.locator('text="CHART ANALYSIS"').count();
  console.log(`   Chart Analysis header: ${chartAnalysis > 0 ? '✅ Found' : '❌ Not found'}`);
  
  // Check for news items
  const cnbcText = await page.locator('text="CNBC"').count();
  console.log(`   CNBC news items: ${cnbcText}`);
  
  console.log('\\n=== PROVIDER SWITCHING TEST ===');
  
  // Test switching to OpenAI
  console.log('7. Switching to OpenAI provider...');
  const openaiBtn = await page.locator('button').filter({ hasText: 'OpenAI' }).first();
  if (await openaiBtn.count() > 0) {
    await openaiBtn.click();
    console.log('   ✅ Clicked OpenAI button');
    await page.waitForTimeout(1000);
    
    // Check if button style changed
    const openaiSelected = await openaiBtn.evaluate(el => 
      el.style.backgroundColor !== '' || el.classList.contains('selected')
    );
    console.log(`   OpenAI button selected: ${openaiSelected ? '✅ Yes' : '❌ No'}`);
  }
  
  // Test mic click
  console.log('\\n8. Testing mic button click...');
  
  // Find the mic area (purple circle with mic icon)
  const micArea = await page.locator('svg').filter({ has: page.locator('path') }).first();
  if (await micArea.count() > 0) {
    const box = await micArea.boundingBox();
    if (box) {
      await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
      console.log('   ✅ Clicked mic icon');
      
      // Wait for connection
      await page.waitForTimeout(3000);
      
      // Check for connection status change
      const disconnectedText = await page.locator('text="Disconnected"').count();
      const connectedText = await page.locator('text="Connected"').count();
      const connectingText = await page.locator('text="Connecting"').count();
      
      console.log(`   Connection status: Disconnected=${disconnectedText}, Connected=${connectedText}, Connecting=${connectingText}`);
      
      // Check for OpenAI WebSocket
      const openaiWS = Array.from(wsConnections.keys()).find(url => 
        url.includes('realtime-relay') || url.includes('openai')
      );
      console.log(`   OpenAI WebSocket: ${openaiWS ? '✅ Created' : '❌ Not found'}`);
      
      if (openaiWS) {
        const conn = wsConnections.get(openaiWS);
        console.log(`   Messages exchanged: ${conn.messages.length}`);
        
        // Show first few message types
        const messageTypes = [...new Set(conn.messages.slice(0, 10).map(m => m.data))];
        console.log(`   Message types: ${messageTypes.join(', ')}`);
      }
    }
  }
  
  // Test switching back to ElevenLabs
  console.log('\\n9. Switching back to ElevenLabs...');
  const elBtn = await page.locator('button:has-text("ElevenLabs")').first();
  if (await elBtn.count() > 0) {
    await elBtn.click();
    console.log('   ✅ Clicked ElevenLabs button');
    await page.waitForTimeout(1000);
  }
  
  // Test symbol search
  console.log('\\n10. Testing symbol search...');
  const searchInput = await page.locator('input[placeholder*="Search"]').first();
  if (await searchInput.count() > 0) {
    await searchInput.fill('Microsoft');
    console.log('   ✅ Typed "Microsoft" in search');
    await page.waitForTimeout(1500); // Wait for debounced search
    
    // Check for dropdown results
    const dropdownItems = await page.locator('.search-dropdown').count();
    console.log(`   Search dropdown items: ${dropdownItems}`);
  }
  
  // Take final screenshot
  await page.screenshot({ path: 'test-ui-accurate-final.png' });
  
  console.log('\\n=== TEST SUMMARY ===');
  
  // Count successful checks
  const successCount = [
    marketInsights > 0,
    stockPrices > 0,
    chartCanvas > 0,
    voiceProviderText > 0,
    voiceConversation > 0,
    chartAnalysis > 0
  ].filter(Boolean).length;
  
  console.log(`\\n✅ Core UI Elements: ${successCount}/6 verified`);
  console.log(`❌ Errors encountered: ${errors.length}`);
  console.log(`🔌 WebSocket connections: ${wsConnections.size}`);
  
  // Check WebSocket health
  const healthyWS = Array.from(wsConnections.values()).filter(
    conn => conn.messages.length > 0
  ).length;
  console.log(`🔌 Healthy WebSocket connections: ${healthyWS}/${wsConnections.size}`);
  
  if (errors.length > 0) {
    console.log('\\n❌ Errors:');
    errors.forEach(err => console.log(`   ${err}`));
  }
  
  console.log('\\n=== TEST COMPLETE ===');
  console.log('Screenshot saved: test-ui-accurate-final.png');
  
  await page.waitForTimeout(2000);
  await browser.close();
})();