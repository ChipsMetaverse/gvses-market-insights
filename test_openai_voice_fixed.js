const { chromium } = require('playwright');

async function testOpenAIVoice() {
  console.log('🚀 Starting OpenAI Voice Agent Test...');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    if (type === 'error') {
      console.error('❌ Browser Error:', text);
    } else if (text.includes('OpenAI') || text.includes('Realtime') || text.includes('relay') || text.includes('session') || text.includes('tool')) {
      console.log(`📝 ${type.toUpperCase()}:`, text);
    }
  });
  
  // Monitor network requests
  page.on('request', request => {
    const url = request.url();
    if (url.includes('/openai/realtime/session') || url.includes('/realtime-relay/')) {
      console.log('🌐 Network Request:', request.method(), url);
    }
  });
  
  page.on('response', response => {
    const url = response.url();
    if (url.includes('/openai/realtime/session')) {
      console.log('✅ Session Response:', response.status(), url);
    }
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    console.log('🔌 WebSocket Created:', ws.url());
    
    ws.on('framesent', frame => {
      try {
        const payload = JSON.parse(frame.payload);
        if (payload.type === 'session.update' || payload.type === 'response.function_call_arguments.done') {
          console.log('📤 WS Send:', payload.type, payload);
        }
      } catch {}
    });
    
    ws.on('framereceived', frame => {
      try {
        const payload = JSON.parse(frame.payload);
        if (payload.type === 'session.created' || payload.type === 'response.function_call_arguments.done' || payload.type === 'conversation.item.created') {
          console.log('📥 WS Receive:', payload.type);
          if (payload.type === 'session.created') {
            console.log('✅ Session established with tools:', payload.session?.tools?.length || 0);
          }
        }
      } catch {}
    });
  });
  
  try {
    console.log('📍 Navigating to app...');
    await page.goto('http://localhost:5174');
    await page.waitForLoadState('networkidle');
    
    // Take initial screenshot
    await page.screenshot({ path: 'test-1-initial.png' });
    console.log('📸 Screenshot: test-1-initial.png');
    
    // Click on Voice tab
    console.log('🎤 Clicking Voice tab...');
    const voiceTab = await page.locator('button:has-text("Voice")').first();
    await voiceTab.click();
    await page.waitForTimeout(1000);
    
    await page.screenshot({ path: 'test-2-voice-tab.png' });
    console.log('📸 Screenshot: test-2-voice-tab.png');
    
    // Check for OpenAI provider option
    const providerExists = await page.locator('text=/OpenAI/i').count() > 0;
    console.log('Provider check:', providerExists ? 'Found OpenAI option' : 'No OpenAI option');
    
    // Try to find and click OpenAI provider if it exists
    try {
      const openaiRadio = await page.locator('input[type="radio"][value="openai"]').first();
      if (await openaiRadio.count() > 0) {
        await openaiRadio.click();
        console.log('✅ Selected OpenAI provider');
        await page.waitForTimeout(500);
      }
    } catch (e) {
      console.log('ℹ️ Could not select OpenAI provider:', e.message);
    }
    
    // Look for connect button
    const connectButton = await page.locator('button:has-text("Connect")').first();
    if (await connectButton.isVisible()) {
      console.log('🔗 Found Connect button, clicking...');
      
      // Set up promise to wait for session creation
      const sessionPromise = page.waitForResponse(
        response => response.url().includes('/openai/realtime/session'),
        { timeout: 10000 }
      ).catch(() => null);
      
      await connectButton.click();
      
      // Wait for session response
      const sessionResponse = await sessionPromise;
      if (sessionResponse) {
        const sessionData = await sessionResponse.json();
        console.log('✅ Session created:', {
          session_id: sessionData.session_id,
          ws_url: sessionData.ws_url
        });
        
        // Check if it's using the relay endpoint
        if (sessionData.ws_url && sessionData.ws_url.includes('/realtime-relay/')) {
          console.log('✅ CORRECT: Using relay endpoint for tool execution!');
        } else {
          console.log('❌ WRONG: Not using relay endpoint - tools won\'t work!');
        }
      }
      
      // Wait for connection
      await page.waitForTimeout(3000);
      
      // Check connection status
      const connectedText = await page.locator('text=/connected|active|ready/i').count();
      if (connectedText > 0) {
        console.log('✅ Voice connection established');
        
        await page.screenshot({ path: 'test-3-connected.png' });
        console.log('📸 Screenshot: test-3-connected.png');
        
        // Try to find text input for testing
        const textInput = await page.locator('input[type="text"], textarea').first();
        if (await textInput.isVisible()) {
          console.log('📝 Testing text input with market query...');
          await textInput.fill("What's Tesla's current price?");
          
          // Find and click send button
          const sendButton = await page.locator('button:has-text("Send")').first();
          if (await sendButton.isVisible()) {
            await sendButton.click();
            console.log('📤 Sent test query');
            
            // Wait for response
            await page.waitForTimeout(5000);
            
            // Check for tool execution in console
            const toolCalls = await page.locator('text=/tool|function|get_stock_price/i').count();
            if (toolCalls > 0) {
              console.log('✅ Tool execution detected!');
            }
            
            await page.screenshot({ path: 'test-4-response.png' });
            console.log('📸 Screenshot: test-4-response.png');
          }
        }
      } else {
        console.log('⚠️ Connection not established');
      }
    } else {
      console.log('⚠️ Connect button not found');
    }
    
    // Final summary
    console.log('\n📊 Test Summary:');
    console.log('1. App loaded: ✅');
    console.log('2. Voice tab accessible: ✅');
    console.log('3. OpenAI provider available:', providerExists ? '✅' : '❌');
    console.log('4. Session endpoint working: Check logs above');
    console.log('5. Relay endpoint used: Check logs above');
    console.log('6. Tools executing: Check logs above');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: 'test-error.png' });
  } finally {
    await page.waitForTimeout(5000); // Keep open for observation
    await browser.close();
    console.log('🏁 Test completed');
  }
}

// Run the test
testOpenAIVoice().catch(console.error);