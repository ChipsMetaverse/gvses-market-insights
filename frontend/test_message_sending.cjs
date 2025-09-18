const playwright = require('playwright');

async function testMessageSending() {
  console.log('🔍 TESTING MESSAGE SENDING TO AI');
  console.log('Verifying text messages reach the AI backend\n');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor WebSocket activity
  let wsMessages = [];
  
  page.on('websocket', ws => {
    console.log('🌐 WebSocket connection detected:', ws.url());
    
    ws.on('framesent', data => {
      const frame = data.payload?.toString();
      if (frame && frame.includes('type')) {
        try {
          const parsed = JSON.parse(frame);
          console.log('📤 SENT:', parsed.type, frame.length < 200 ? frame : `${frame.substring(0, 100)}...`);
          wsMessages.push({ direction: 'sent', data: parsed });
        } catch (e) {
          console.log('📤 SENT (non-JSON):', frame.substring(0, 100));
        }
      }
    });
    
    ws.on('framereceived', data => {
      const frame = data.payload?.toString();
      if (frame && frame.includes('type')) {
        try {
          const parsed = JSON.parse(frame);
          console.log('📥 RECEIVED:', parsed.type, frame.length < 200 ? frame : `${frame.substring(0, 100)}...`);
          wsMessages.push({ direction: 'received', data: parsed });
        } catch (e) {
          console.log('📥 RECEIVED (non-JSON):', frame.substring(0, 100));
        }
      }
    });
  });

  try {
    console.log('📍 Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // Navigate to voice interface
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    // Connect to OpenAI
    console.log('🔌 Connecting to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000);
    
    // Verify connection
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`✅ Connection status: "${status}"`);
    
    if (!status?.includes('Connected')) {
      throw new Error('Connection failed');
    }
    
    console.log('\n🎯 TESTING MESSAGE TRANSMISSION...');
    
    // Send a simple test message
    const testMessage = 'Hello AI, what is 2+2?';
    console.log(`📝 Typing message: "${testMessage}"`);
    
    const input = page.locator('input[data-testid="message-input"]');
    await input.clear();
    await input.type(testMessage);
    
    console.log('📤 Clicking send button...');
    await page.click('button[data-testid="send-button"]');
    
    // Wait and monitor for WebSocket activity
    console.log('⏳ Monitoring WebSocket traffic for 10 seconds...');
    await page.waitForTimeout(10000);
    
    console.log('\n📊 WEBSOCKET ANALYSIS:');
    console.log(`Total messages captured: ${wsMessages.length}`);
    
    const sentMessages = wsMessages.filter(m => m.direction === 'sent');
    const receivedMessages = wsMessages.filter(m => m.direction === 'received');
    
    console.log(`Messages sent to AI: ${sentMessages.length}`);
    console.log(`Messages received from AI: ${receivedMessages.length}`);
    
    // Look for our test message
    const testMessageSent = sentMessages.some(m => 
      JSON.stringify(m.data).includes('2+2') || 
      JSON.stringify(m.data).includes('Hello AI')
    );
    
    console.log(`Test message found in WebSocket: ${testMessageSent ? '✅ YES' : '❌ NO'}`);
    
    // Check for any responses
    const hasResponse = receivedMessages.some(m => 
      m.data.type === 'response.audio_transcript.delta' ||
      m.data.type === 'response.text.delta' ||
      m.data.type === 'response.done'
    );
    
    console.log(`AI response received: ${hasResponse ? '✅ YES' : '❌ NO'}`);
    
    // Look for conversation updates in UI
    const messageCount = await page.locator('[data-testid="messages-container"] .conversation-message-enhanced').count();
    console.log(`Messages visible in UI: ${messageCount}`);
    
    console.log('\n🔍 DETAILED WEBSOCKET MESSAGES:');
    wsMessages.slice(-5).forEach((msg, i) => {
      console.log(`${i + 1}. ${msg.direction.toUpperCase()}: ${msg.data.type || 'unknown'}`);
    });
    
    // Final assessment
    console.log('\n🎯 DIAGNOSIS:');
    if (testMessageSent && hasResponse && messageCount > 0) {
      console.log('✅ PERFECT: Message sent, AI responded, UI updated');
    } else if (testMessageSent && hasResponse) {
      console.log('⚠️  PARTIAL: Message sent, AI responded, but UI not updating');
    } else if (testMessageSent) {
      console.log('⚠️  PARTIAL: Message sent but no AI response detected');
    } else {
      console.log('❌ BROKEN: Message not reaching AI through WebSocket');
    }
    
    await page.screenshot({ path: 'message-sending-test.png' });
    console.log('📸 Screenshot saved: message-sending-test.png');
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
  } finally {
    await browser.close();
  }
}

testMessageSending().catch(console.error);