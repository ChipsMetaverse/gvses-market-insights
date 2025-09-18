const playwright = require('playwright');

async function simpleVoiceTextTest() {
  console.log('💬 SIMPLE VOICE TEXT TEST - BYPASS CONNECTION TOGGLE');
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
    
    console.log('\n📍 PHASE 3: TEST MAIN MESSAGE INPUT DIRECTLY');
    
    // Skip connection toggle - test the main input field directly
    const messageInput = page.locator('input[data-testid="message-input"]');
    const messageInputExists = await messageInput.count() > 0;
    console.log(`✅ Main message input found: ${messageInputExists}`);
    
    if (messageInputExists) {
      console.log('💬 Testing text input: "What is Tesla\'s current stock price?"');
      
      await messageInput.click();
      await page.waitForTimeout(500);
      
      await messageInput.fill("What is Tesla's current stock price?");
      await page.waitForTimeout(1000);
      
      // Check for send button
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonExists = await sendButton.count() > 0;
      const sendButtonEnabled = sendButtonExists ? await sendButton.isEnabled() : false;
      
      console.log(`📤 Send button found: ${sendButtonExists}`);
      console.log(`📤 Send button enabled: ${sendButtonEnabled}`);
      
      if (sendButtonEnabled) {
        console.log('⚡ Attempting to send message...');
        await sendButton.click();
        await page.waitForTimeout(3000);
        
        // Check for conversation messages or response
        const messagesContainer = page.locator('[data-testid="messages-container"]');
        const conversationArea = page.locator('.voice-conversation, .conversation-area');
        
        const messageCount = await messagesContainer.count() > 0 ? 
          await messagesContainer.locator('.message, [class*="message"]').count() : 0;
        
        console.log(`📬 Messages in conversation: ${messageCount}`);
        
        // Check if input cleared (indicates message was processed)
        const inputValue = await messageInput.inputValue();
        const inputCleared = !inputValue || inputValue.trim() === '';
        console.log(`🗑️ Input cleared after send: ${inputCleared}`);
        
        if (messageCount > 0 || inputCleared) {
          console.log('✅ Text message appears to have been processed!');
        } else {
          console.log('❌ No indication that message was processed');
        }
        
      } else {
        console.log('❌ Send button not enabled - may require connection');
      }
      
    } else {
      console.log('❌ Main message input not found');
      
      // Debug: Look for alternative input fields
      const allInputs = await page.locator('input').count();
      console.log(`🔍 Total input elements on page: ${allInputs}`);
      
      // Check if it's a textarea instead
      const textareaInputs = await page.locator('textarea[placeholder*="message"], textarea[placeholder*="speak"]').count();
      console.log(`🔍 Textarea message inputs: ${textareaInputs}`);
    }
    
    console.log('\n📍 PHASE 4: ANALYZE WEBSOCKET LOGS');
    
    const wsLogs = consoleMessages.filter(msg =>
      msg.text.toLowerCase().includes('websocket') ||
      msg.text.toLowerCase().includes('realtime') ||
      msg.text.toLowerCase().includes('openai') ||
      msg.text.toLowerCase().includes('connection')
    );
    
    console.log(`\n🔍 WebSocket-related logs (${wsLogs.length}):`);
    wsLogs.forEach((msg, i) => {
      console.log(`${i + 1}. [${msg.type}] ${msg.text}`);
    });
    
    await page.screenshot({ path: 'simple-voice-text-test.png' });
    
    console.log('\n🎯 SIMPLE VOICE TEXT TEST SUMMARY:');
    console.log('1. Tested main Voice Conversation text input without connection toggle');
    console.log('2. Bypassed WebSocket connection issues to test basic functionality');
    console.log('3. Checked if send button works and message processing occurs');
    
    // Keep browser open for inspection
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Simple Voice Text Test Error:', error.message);
    await page.screenshot({ path: 'simple-voice-text-error.png' });
  }
}

simpleVoiceTextTest().catch(console.error);