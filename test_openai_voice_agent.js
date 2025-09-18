const { chromium } = require('playwright');

async function testOpenAIVoiceAgent() {
  console.log('🚀 Testing OpenAI Voice Agent with Tool Execution...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Monitor console for debugging
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('OpenAI') || text.includes('Realtime') || 
        text.includes('session') || text.includes('tool') || 
        text.includes('relay')) {
      console.log('🔧 Console:', text);
    }
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket Connected:', url);
    
    // Check if using the correct relay endpoint
    if (url.includes('/realtime-relay/')) {
      console.log('✅ CORRECT: Using relay endpoint - tools will work!');
    } else if (url.includes('/openai/realtime/ws')) {
      console.log('❌ WRONG: Using direct endpoint - tools won\'t work!');
    }
    
    // Monitor for tool calls
    ws.on('framereceived', frame => {
      try {
        const data = JSON.parse(frame.payload);
        if (data.type === 'response.function_call_arguments.done' || 
            data.type === 'tool_call_start' ||
            data.type === 'tool_call_complete') {
          console.log('🔧 TOOL EXECUTION DETECTED:', data.type, data.name || data.tool_name || '');
        }
      } catch {}
    });
  });
  
  // Monitor network requests
  page.on('response', async response => {
    const url = response.url();
    if (url.includes('/openai/realtime/session')) {
      try {
        const data = await response.json();
        console.log('📍 Session Created:', {
          session_id: data.session_id?.substring(0, 8) + '...',
          ws_url: data.ws_url,
          correct_endpoint: data.ws_url?.includes('/realtime-relay/') ? 'YES ✅' : 'NO ❌'
        });
      } catch {}
    }
  });
  
  try {
    // Navigate to app
    console.log('1️⃣ Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForLoadState('networkidle');
    console.log('   ✅ App loaded\n');
    
    // Click Voice tab
    console.log('2️⃣ Navigating to Voice tab...');
    await page.click('button:has-text("Voice + Manual Control")');
    await page.waitForTimeout(1000);
    console.log('   ✅ Voice tab active\n');
    
    // Find the Connect button (it's visible in the Voice Conversation section)
    console.log('3️⃣ Looking for Connect button...');
    
    // The Connect button is in the Voice Conversation section
    const connectButton = page.locator('button:has-text("Connect")');
    const connectCount = await connectButton.count();
    console.log('   Found', connectCount, 'Connect button(s)');
    
    if (connectCount > 0) {
      console.log('4️⃣ Clicking Connect button...');
      await connectButton.first().click();
      console.log('   Clicked Connect button');
      
      // Wait for connection
      await page.waitForTimeout(3000);
      
      // Check if connected (button should change to Disconnect)
      const disconnectButton = await page.locator('button:has-text("Disconnect")').count();
      if (disconnectButton > 0) {
        console.log('   ✅ Successfully connected!\n');
        
        // Test text input for market query
        console.log('5️⃣ Testing market query...');
        
        // Look for text input field
        const textInput = page.locator('input[type="text"], textarea').last();
        if (await textInput.isVisible()) {
          await textInput.fill("What is Tesla's current stock price?");
          console.log('   Typed query: "What is Tesla\'s current stock price?"');
          
          // Find send button (might be an icon button)
          const sendButton = page.locator('button').filter({ hasText: /Send|→|➤/ }).first();
          const iconButton = page.locator('button svg').first().locator('..');
          
          if (await sendButton.isVisible()) {
            await sendButton.click();
            console.log('   Sent query via Send button');
          } else if (await iconButton.isVisible()) {
            await iconButton.click();
            console.log('   Sent query via icon button');
          } else {
            // Try pressing Enter
            await textInput.press('Enter');
            console.log('   Sent query via Enter key');
          }
          
          // Wait for response and tool execution
          console.log('   Waiting for response and tool execution...');
          await page.waitForTimeout(5000);
          
          // Check for response in conversation
          const messages = await page.locator('.message, [class*="message"]').count();
          console.log('   Messages in conversation:', messages);
          
          if (messages > 0) {
            console.log('   ✅ Response received!\n');
          }
        } else {
          console.log('   ⚠️ Text input not found\n');
        }
      } else {
        console.log('   ⚠️ Connection not established\n');
      }
    } else {
      console.log('   ❌ Connect button not found\n');
    }
    
    // Final summary
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('📊 TEST SUMMARY:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('Check the console output above for:');
    console.log('1. Session creation with relay URL');
    console.log('2. WebSocket connection to relay endpoint');
    console.log('3. Tool execution events');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    await page.screenshot({ path: 'test-openai-final.png' });
    console.log('\n📸 Final screenshot: test-openai-final.png');
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
    await page.screenshot({ path: 'test-openai-error.png' });
  } finally {
    console.log('\n🔄 Keeping browser open for observation...');
    await page.waitForTimeout(10000);
    await browser.close();
    console.log('✅ Test complete!');
  }
}

testOpenAIVoiceAgent().catch(console.error);