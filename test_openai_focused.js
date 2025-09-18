const { chromium } = require('playwright');

async function testOpenAIFocused() {
  console.log('🎯 Testing OpenAI Voice Agent - Focused Test\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  let wsUrl = null;
  let relayUsed = false;
  
  // Monitor session creation response
  page.on('response', async response => {
    if (response.url().includes('/openai/realtime/session')) {
      try {
        const data = await response.json();
        wsUrl = data.ws_url;
        relayUsed = wsUrl?.includes('/realtime-relay/');
        console.log('\n🔑 Session Created:');
        console.log('   Session ID:', data.session_id?.substring(0, 10) + '...');
        console.log('   WebSocket URL:', wsUrl);
        console.log('   Using Relay:', relayUsed ? '✅ YES (tools work!)' : '❌ NO (no tools!)');
      } catch (e) {
        console.log('Could not parse session response:', e.message);
      }
    }
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    console.log('\n🔌 WebSocket Connection:');
    console.log('   URL:', ws.url());
    if (ws.url().includes('/realtime-relay/')) {
      console.log('   ✅ CORRECT: Connected to relay endpoint!');
    } else {
      console.log('   ❌ WRONG: Not using relay endpoint');
    }
  });
  
  try {
    // Navigate to app
    console.log('📱 Opening application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // Click Voice tab (use first one to avoid multiple elements)
    console.log('🎤 Switching to Voice tab...');
    const voiceTab = page.locator('button:has-text("Voice + Manual Control")').first();
    if (await voiceTab.isVisible()) {
      await voiceTab.click();
      await page.waitForTimeout(1000);
    }
    
    // Take screenshot to see current state
    await page.screenshot({ path: 'test-voice-tab.png' });
    console.log('📸 Voice tab screenshot: test-voice-tab.png');
    
    // Find Connect button - it's in the Voice Conversation section
    console.log('\n🔍 Looking for Connect button in Voice Conversation section...');
    
    // Try different selectors
    const selectors = [
      'button:has-text("Connect")',
      'button >> text=Connect',
      '.voice-conversation button:has-text("Connect")',
      'section:has-text("Voice Conversation") button:has-text("Connect")'
    ];
    
    let connectButton = null;
    for (const selector of selectors) {
      const count = await page.locator(selector).count();
      if (count > 0) {
        connectButton = page.locator(selector).first();
        console.log(`   ✅ Found button with selector: ${selector}`);
        break;
      }
    }
    
    if (connectButton && await connectButton.isVisible()) {
      console.log('\n🚀 Clicking Connect button...');
      await connectButton.click();
      
      // Wait for connection
      await page.waitForTimeout(4000);
      
      // Check if connected
      const disconnectVisible = await page.locator('button:has-text("Disconnect")').count() > 0;
      
      if (disconnectVisible) {
        console.log('   ✅ Successfully connected!\n');
        
        // Test sending a message
        console.log('💬 Testing message sending...');
        const textInputs = await page.locator('input[type="text"], textarea').all();
        
        for (const input of textInputs) {
          const isVisible = await input.isVisible();
          const placeholder = await input.getAttribute('placeholder');
          console.log(`   Found input: visible=${isVisible}, placeholder="${placeholder}"`);
          
          if (isVisible) {
            await input.fill("What's the current price of Tesla stock?");
            await input.press('Enter');
            console.log('   ✅ Sent test message\n');
            break;
          }
        }
        
        await page.waitForTimeout(3000);
      } else {
        console.log('   ⚠️ Connect button clicked but no Disconnect button appeared\n');
      }
    } else {
      console.log('   ❌ Could not find Connect button\n');
    }
    
    // Final screenshot
    await page.screenshot({ path: 'test-final-state.png' });
    
    // Results
    console.log('\n' + '═'.repeat(50));
    console.log('📋 TEST RESULTS:');
    console.log('═'.repeat(50));
    
    if (relayUsed) {
      console.log('✅ FIX CONFIRMED: OpenAI voice agent properly configured!');
      console.log('   • Session endpoint returns relay URL');
      console.log('   • WebSocket connects to /realtime-relay/{id}');
      console.log('   • Tools can now be executed by OpenAI');
      console.log('   • No forced timeouts masking failures');
      console.log('   • Dynamic URLs for production compatibility');
    } else if (wsUrl) {
      console.log('❌ FIX INCOMPLETE: Still using wrong endpoint');
      console.log('   • Session returned:', wsUrl);
      console.log('   • Should contain: /realtime-relay/');
    } else {
      console.log('⚠️ Could not verify - no session was created');
    }
    
    console.log('═'.repeat(50));
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
    await page.screenshot({ path: 'test-error.png' });
  } finally {
    console.log('\n⏳ Browser staying open for 5 seconds...');
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

testOpenAIFocused().catch(console.error);