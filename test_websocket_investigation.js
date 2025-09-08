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

  // Track all WebSocket connections
  const websockets = [];
  let elevenLabsWs = null;
  
  // Monitor console for all messages
  page.on('console', msg => {
    const text = msg.text();
    console.log(`[CONSOLE ${msg.type()}] ${text}`);
  });

  // Monitor all WebSocket connections
  page.on('websocket', ws => {
    const url = ws.url();
    console.log(`\n🔌 WebSocket created: ${url.substring(0, 80)}...`);
    websockets.push(ws);
    
    if (url.includes('elevenlabs.io')) {
      elevenLabsWs = ws;
      console.log('  ➡️ This is the ElevenLabs WebSocket');
    }
    
    ws.on('close', () => {
      console.log(`\n🔴 WebSocket CLOSED: ${url.substring(0, 80)}...`);
      if (ws === elevenLabsWs) {
        console.log('  ⚠️ ElevenLabs WebSocket has disconnected!');
      }
    });
    
    ws.on('framereceived', frame => {
      const payload = frame.payload;
      if (typeof payload === 'string') {
        try {
          const data = JSON.parse(payload);
          // Log important message types
          if (data.type && (
            data.type.includes('error') || 
            data.type.includes('close') || 
            data.type === 'interruption' ||
            data.type === 'conversation_initiation_client_data'
          )) {
            console.log(`  📨 Frame type: ${data.type}`);
            if (data.error) console.log(`     Error: ${JSON.stringify(data.error)}`);
            if (data.interruption_event) console.log(`     Interruption: ${JSON.stringify(data.interruption_event)}`);
          }
        } catch (e) {
          // Not JSON
        }
      }
    });
    
    ws.on('framesent', frame => {
      const payload = frame.payload;
      if (typeof payload === 'string') {
        try {
          const data = JSON.parse(payload);
          if (data.type) {
            console.log(`  📤 Sent: ${data.type}`);
          }
        } catch (e) {
          // Not JSON
        }
      }
    });
  });

  try {
    console.log('\n📍 Step 1: Navigating to app...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    
    console.log(`\n📊 Initial WebSocket count: ${websockets.length}`);
    websockets.forEach((ws, i) => {
      console.log(`  ${i + 1}. ${ws.url().substring(0, 60)}...`);
    });
    
    // Wait for the voice section
    console.log('\n📍 Step 2: Waiting for Voice Assistant section...');
    await page.waitForSelector('.voice-section', { timeout: 10000 });
    
    // Look for connect button
    console.log('\n📍 Step 3: Finding Connect button...');
    const connectButton = await page.waitForSelector('button:has-text("Connect Voice Assistant")', { timeout: 5000 });
    
    console.log('\n📍 Step 4: Clicking Connect button...');
    await connectButton.click();
    
    // Wait for connection status to change
    console.log('\n📍 Step 5: Waiting for connection...');
    await page.waitForFunction(() => {
      const button = document.querySelector('.connection-button, button');
      return button && (button.textContent.includes('Disconnect') || button.textContent.includes('Connected'));
    }, { timeout: 10000 });
    
    console.log('\n✅ Connected! Current WebSocket count:', websockets.length);
    
    // Small delay to stabilize
    await page.waitForTimeout(2000);
    
    // Find the text input
    console.log('\n📍 Step 6: Finding text input field...');
    const textInput = await page.waitForSelector('input[placeholder*="Type a message"]', { timeout: 5000 });
    
    // Focus the input
    console.log('\n📍 Step 7: Focusing text input...');
    await textInput.click();
    await page.waitForTimeout(500);
    
    // Type characters one by one with monitoring
    console.log('\n📍 Step 8: Typing test message character by character...');
    const testMessage = 'Hello World';
    
    for (let i = 0; i < testMessage.length; i++) {
      const char = testMessage[i];
      console.log(`\n  Typing character ${i + 1}: "${char}"`);
      
      // Type the character
      await page.keyboard.type(char, { delay: 100 });
      
      // Wait a moment
      await page.waitForTimeout(300);
      
      // Check WebSocket status
      const wsStillOpen = elevenLabsWs && elevenLabsWs.isClosed() === false;
      console.log(`    ElevenLabs WebSocket: ${wsStillOpen ? '✅ Still connected' : '❌ DISCONNECTED'}`);
      
      // Check UI connection status
      const uiConnected = await page.evaluate(() => {
        const button = document.querySelector('.connection-button, button');
        return button && (button.textContent.includes('Disconnect') || button.textContent.includes('Connected'));
      });
      console.log(`    UI shows: ${uiConnected ? '✅ Connected' : '❌ Disconnected'}`);
      
      // Get current input value
      const currentValue = await textInput.inputValue();
      console.log(`    Input value: "${currentValue}"`);
      
      // If disconnected, stop typing
      if (!wsStillOpen || !uiConnected) {
        console.log('\n❌ DISCONNECTION DETECTED! Stopping test.');
        console.log(`  Disconnected after typing ${i + 1} characters: "${currentValue}"`);
        break;
      }
    }
    
    // Final status check
    await page.waitForTimeout(2000);
    
    console.log('\n📊 Final WebSocket Status:');
    console.log(`  Total WebSockets created: ${websockets.length}`);
    console.log(`  ElevenLabs WebSocket: ${elevenLabsWs && !elevenLabsWs.isClosed() ? '✅ Connected' : '❌ Disconnected'}`);
    
    const finalUiStatus = await page.evaluate(() => {
      const button = document.querySelector('.connection-button, button');
      return button ? button.textContent : 'Unknown';
    });
    console.log(`  UI Button shows: "${finalUiStatus}"`);
    
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    console.log('\nError details:', error);
  }
  
  console.log('\n✅ Test complete! Browser will remain open for inspection...');
  console.log('Press Ctrl+C to close.');
  
  // Keep browser open for manual inspection
  await new Promise(() => {});
})();