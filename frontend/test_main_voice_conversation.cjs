const playwright = require('playwright');

async function mainVoiceConversationTest() {
  console.log('🎤 MAIN VOICE CONVERSATION TEST - TESTING TEXT INPUT');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Capture console messages for debugging
  const consoleMessages = [];
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    consoleMessages.push({ type, text });
    console.log(`[BROWSER ${type.toUpperCase()}] ${text}`);
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('\n📍 PHASE 3: CHECK CONNECTION STATUS');
    const connectionToggle = page.locator('[data-testid="connection-toggle"]');
    const isConnected = await connectionToggle.isChecked();
    console.log(`🔗 Connection status: ${isConnected ? 'Connected' : 'Not connected'}`);
    
    if (!isConnected) {
      console.log('🔗 Attempting to connect...');
      await connectionToggle.click();
      await page.waitForTimeout(3000);
      const finalConnected = await connectionToggle.isChecked();
      console.log(`🔗 Final connection status: ${finalConnected ? 'Connected' : 'Not connected'}`);
    }
    
    console.log('\n📍 PHASE 4: TEST MAIN VOICE CONVERSATION INPUT');
    
    // Look for the main conversation input (not the Voice Commands modal)
    const messageInput = page.locator('input[data-testid="message-input"]');
    const messageInputExists = await messageInput.count() > 0;
    console.log(`✅ Main message input found: ${messageInputExists}`);
    
    if (messageInputExists) {
      console.log('🗣️ Testing text input: "What is Tesla\'s current price?"');
      
      // Test typing in main conversation input
      await messageInput.click();
      await page.waitForTimeout(500);
      
      await messageInput.fill("What is Tesla's current price?");
      await page.waitForTimeout(1000);
      
      // Look for send button
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonExists = await sendButton.count() > 0;
      const sendButtonEnabled = sendButtonExists ? await sendButton.isEnabled() : false;
      
      console.log(`🔘 Send button found: ${sendButtonExists}`);
      console.log(`🔘 Send button enabled: ${sendButtonEnabled}`);
      
      if (sendButtonEnabled) {
        console.log('📤 Sending message...');
        await sendButton.click();
        await page.waitForTimeout(5000);
        
        // Check for conversation messages
        const messagesContainer = page.locator('[data-testid="messages-container"]');
        const messageCount = await messagesContainer.locator('.conversation-message-enhanced, .message, [class*="message"]').count();
        console.log(`📬 Messages in conversation: ${messageCount}`);
        
        // Check conversation status
        const conversationStatus = await page.locator('.voice-conversation, .conversation-area').textContent();
        console.log(`💬 Conversation area content: ${conversationStatus ? conversationStatus.slice(0, 200) : 'No content'}`);
        
        await page.screenshot({ path: 'main-voice-test-after-send.png' });
        
        if (messageCount > 0) {
          console.log('✅ Message sent successfully - conversation has responses!');
        } else {
          console.log('❌ No conversation messages appeared after sending');
        }
        
      } else {
        console.log('❌ Send button not enabled');
      }
      
    } else {
      console.log('❌ Main message input not found');
      
      // Debug: Look for any inputs in the voice area
      const allInputs = await page.locator('input').count();
      console.log(`🔍 Total input elements on page: ${allInputs}`);
      
      const voiceAreaInputs = await page.locator('.voice-conversation input, .conversation-area input').count();
      console.log(`🔍 Input elements in voice area: ${voiceAreaInputs}`);
    }
    
    console.log('\n📍 PHASE 5: ANALYZE WEBSOCKET LOGS');
    
    // Look for WebSocket-related logs
    const wsLogs = consoleMessages.filter(msg =>
      msg.text.includes('WebSocket') ||
      msg.text.includes('connection') ||
      msg.text.includes('RealtimeClient') ||
      msg.text.includes('openai') ||
      msg.text.includes('realtime')
    );
    
    console.log(`\n🔍 WebSocket-related logs (${wsLogs.length}):`);
    wsLogs.forEach((msg, i) => {
      console.log(`${i + 1}. [${msg.type}] ${msg.text}`);
    });
    
    await page.screenshot({ path: 'main-voice-test-final.png' });
    
    console.log('\n🎯 MAIN VOICE CONVERSATION TEST SUMMARY:');
    console.log('1. Tested main conversation interface (not Voice Commands modal)');
    console.log('2. Checked connection status and message input functionality');
    console.log('3. Analyzed WebSocket connection logs');
    console.log('4. Verified if text messages work in main conversation area');
    
    if (messageInputExists && sendButtonEnabled) {
      console.log('✅ Main conversation interface is functional for text input');
    } else {
      console.log('❌ Main conversation interface has issues with text input');
    }
    
    // Keep browser open for inspection
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Main Voice Conversation Test Error:', error.message);
    await page.screenshot({ path: 'main-voice-test-error.png' });
  }
}

mainVoiceConversationTest().catch(console.error);