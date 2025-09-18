const playwright = require('playwright');

async function investigateDuplicateResponse() {
  console.log('🔍 ULTRATHINK: INVESTIGATING DUPLICATE createResponse CALLS');
  console.log('='.repeat(70));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Track all WebSocket events with detailed logging
  let wsConnections = [];
  let messageCount = 0;
  let createResponseCount = 0;
  let errorCount = 0;
  let conversationEvents = [];

  // Capture console logs for debugging
  page.on('console', (msg) => {
    const text = msg.text();
    console.log(`📱 BROWSER: ${text}`);
    
    // Track specific events
    if (text.includes('Triggering AI response')) {
      createResponseCount++;
      console.log(`🚨 DUPLICATE ALERT: createResponse call #${createResponseCount}`);
    }
  });

  // Monitor WebSocket traffic in detail
  page.on('websocket', ws => {
    console.log(`🌐 NEW WEBSOCKET: ${ws.url()}`);
    wsConnections.push(ws);
    
    ws.on('framesent', data => {
      messageCount++;
      const parsed = JSON.parse(data.payload);
      conversationEvents.push({ 
        direction: 'SENT', 
        type: parsed.type, 
        timestamp: Date.now(),
        eventId: parsed.event_id || 'none'
      });
      
      console.log(`📤 SENT #${messageCount}: ${parsed.type} (ID: ${parsed.event_id || 'none'})`);
      
      // Track createResponse calls specifically
      if (parsed.type === 'response.create') {
        console.log(`🎯 RESPONSE.CREATE DETECTED: ${parsed.event_id}`);
        console.log(`   - Total createResponse calls so far: ${conversationEvents.filter(e => e.type === 'response.create').length}`);
      }
    });
    
    ws.on('framereceived', data => {
      messageCount++;
      const parsed = JSON.parse(data.payload);
      conversationEvents.push({ 
        direction: 'RECEIVED', 
        type: parsed.type, 
        timestamp: Date.now(),
        eventId: parsed.event_id || 'none'
      });
      
      console.log(`📥 RECEIVED #${messageCount}: ${parsed.type} (ID: ${parsed.event_id || 'none'})`);
      
      // Track errors specifically
      if (parsed.type === 'error') {
        errorCount++;
        console.log(`🔴 ERROR #${errorCount}: ${parsed.error?.code || 'unknown'}`);
        console.log(`   - Message: ${parsed.error?.message || 'no message'}`);
        
        if (parsed.error?.code === 'conversation_already_has_active_response') {
          console.log('🚨 DUPLICATE RESPONSE ERROR DETECTED!');
          console.log('   - Analyzing recent events...');
          
          const recentEvents = conversationEvents.slice(-10);
          console.log('📊 LAST 10 WEBSOCKET EVENTS:');
          recentEvents.forEach((event, i) => {
            console.log(`   ${i+1}. ${event.direction}: ${event.type} (${event.eventId})`);
          });
        }
      }
    });
  });

  try {
    console.log('📍 Step 1: Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('📍 Step 2: Navigating to voice interface...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    console.log('📍 Step 3: Setting provider to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.waitForTimeout(500);
    
    console.log('📍 Step 4: Connecting to OpenAI Realtime...');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000); // Wait for full connection
    
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    
    if (!status?.includes('Connected')) {
      throw new Error('Failed to connect to OpenAI');
    }
    
    console.log('📍 Step 5: Sending test message to trigger duplicate issue...');
    const messageInput = page.locator('input[data-testid="message-input"]');
    const sendButton = page.locator('button[data-testid="send-button"]');
    
    await messageInput.clear();
    await messageInput.type('What is Tesla stock price?');
    
    console.log('📍 Step 6: Clicking send button and monitoring for duplicates...');
    
    // Reset counters before the critical action
    createResponseCount = 0;
    const beforeCount = conversationEvents.filter(e => e.type === 'response.create').length;
    
    await sendButton.click();
    
    // Wait and monitor for duplicates
    await page.waitForTimeout(5000);
    
    const afterCount = conversationEvents.filter(e => e.type === 'response.create').length;
    const duplicateCount = afterCount - beforeCount;
    
    console.log('\n🔍 DUPLICATE RESPONSE ANALYSIS:');
    console.log('='.repeat(50));
    console.log(`📊 response.create calls before send: ${beforeCount}`);
    console.log(`📊 response.create calls after send: ${afterCount}`);
    console.log(`🚨 Total duplicates detected: ${duplicateCount}`);
    console.log(`❌ Error events: ${errorCount}`);
    
    if (duplicateCount > 1) {
      console.log('\n🚨 DUPLICATE RESPONSE CONFIRMED!');
      console.log('📋 Full conversation flow:');
      
      const responseEvents = conversationEvents.filter(e => e.type === 'response.create');
      responseEvents.forEach((event, i) => {
        console.log(`   ${i+1}. ${event.direction}: ${event.type} (ID: ${event.eventId}) at ${new Date(event.timestamp).toISOString()}`);
      });
      
      // Analyze timing between duplicates
      if (responseEvents.length >= 2) {
        const timeDiff = responseEvents[1].timestamp - responseEvents[0].timestamp;
        console.log(`⏱️  Time between duplicates: ${timeDiff}ms`);
      }
    }
    
    console.log('\n📊 COMPLETE WEBSOCKET EVENT LOG:');
    console.log('='.repeat(50));
    conversationEvents.forEach((event, i) => {
      console.log(`${i+1}. [${event.direction}] ${event.type} (${event.eventId})`);
    });
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Investigation complete. Browser will remain open for manual inspection...');
    await new Promise(() => {}); // Keep alive
    
  } catch (error) {
    console.error('❌ Investigation Error:', error.message);
    console.log('\n📊 Events captured before error:');
    conversationEvents.forEach((event, i) => {
      console.log(`${i+1}. [${event.direction}] ${event.type}`);
    });
  } finally {
    // Don't close browser for manual inspection
  }
}

investigateDuplicateResponse().catch(console.error);