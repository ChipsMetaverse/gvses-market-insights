#!/usr/bin/env node

/**
 * Focused test to investigate WebSocket disconnection when typing in text input
 * This test specifically monitors what happens when typing characters
 */

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
  
  // Enable comprehensive console logging
  page.on('console', msg => {
    const text = msg.text();
    // Filter out noisy Vite HMR messages
    if (!text.includes('[vite]') && !text.includes('Download the React DevTools')) {
      console.log(`📋 Console: ${text}`);
    }
  });
  
  // Track WebSocket connections and messages
  let websocketCount = 0;
  const websockets = new Map();
  let frameCountPerWs = new Map();
  
  page.on('websocket', ws => {
    websocketCount++;
    const wsId = websocketCount;
    websockets.set(wsId, ws);
    frameCountPerWs.set(wsId, 0);
    
    const url = ws.url();
    const isElevenLabs = url.includes('elevenlabs.io');
    
    console.log(`\n🔌 [WS-${wsId}] WebSocket CREATED ${isElevenLabs ? '(ElevenLabs)' : ''}`);
    console.log(`   URL: ${url.substring(0, 80)}...`);
    console.log(`   Time: ${new Date().toISOString()}`);
    
    // Track frames sent
    ws.on('framesent', frameData => {
      const frameCount = frameCountPerWs.get(wsId) + 1;
      frameCountPerWs.set(wsId, frameCount);
      
      const payload = frameData.payload;
      console.log(`\n📤 [WS-${wsId}] Frame SENT #${frameCount}`);
      console.log(`   Time: ${new Date().toISOString()}`);
      
      // Try to parse as JSON
      if (typeof payload === 'string') {
        try {
          const data = JSON.parse(payload);
          console.log(`   Type: ${data.type}`);
          
          // Log important message types
          if (data.type === 'user_message') {
            console.log(`   🔴 TEXT MESSAGE SENT: "${data.text}"`);
          } else if (data.type === 'conversation_initiation_client_data') {
            console.log(`   ✅ Initialization message sent`);
          } else if (data.type === 'pong') {
            console.log(`   🏓 Pong sent for event: ${data.event_id}`);
          } else if (data.user_audio_chunk) {
            console.log(`   🎤 Audio chunk sent (base64 length: ${data.user_audio_chunk.length})`);
          }
        } catch (e) {
          console.log(`   Raw data (first 200 chars): ${payload.substring(0, 200)}`);
        }
      }
    });
    
    // Track frames received
    ws.on('framereceived', frameData => {
      const payload = frameData.payload;
      if (typeof payload === 'string') {
        try {
          const data = JSON.parse(payload);
          
          // Log important received messages
          if (data.type === 'ping') {
            console.log(`   🏓 [WS-${wsId}] Ping received`);
          } else if (data.type === 'error') {
            console.log(`   ❌ [WS-${wsId}] ERROR from server:`, JSON.stringify(data));
          } else if (data.type === 'conversation_initiation_metadata') {
            console.log(`   ✅ [WS-${wsId}] Conversation initialized`);
          } else if (data.type === 'interruption') {
            console.log(`   ⚠️ [WS-${wsId}] INTERRUPTION:`, data.interruption_event?.reason);
          }
        } catch (e) {
          // Not JSON
        }
      }
    });
    
    // Track WebSocket close
    ws.on('close', () => {
      const totalFrames = frameCountPerWs.get(wsId);
      console.log(`\n🔴 [WS-${wsId}] WebSocket CLOSED ${isElevenLabs ? '(ElevenLabs)' : ''}`);
      console.log(`   Time: ${new Date().toISOString()}`);
      console.log(`   Total frames sent: ${totalFrames}`);
    });
    
    ws.on('error', error => {
      console.log(`\n❌ [WS-${wsId}] WebSocket ERROR:`, error);
    });
  });

  console.log('\n🌐 Navigating to application...');
  await page.goto('http://localhost:5174');
  
  // Wait for page to load
  await page.waitForTimeout(3000);
  
  console.log('\n🔍 Looking for Connect button...');
  
  try {
    // Find and click the Connect button - try different selectors
    let connectButton = await page.locator('button:has-text("Connect")').first();
    
    if (!await connectButton.isVisible()) {
      connectButton = await page.locator('button:has-text("Connect Voice Assistant")').first();
    }
    
    if (await connectButton.isVisible()) {
      console.log('✅ Found Connect button, clicking...');
      await connectButton.click();
      
      // Wait for connection
      await page.waitForTimeout(2000);
      
      console.log('\n🔍 Looking for text input field...');
      
      // Find the text input - try different selectors
      let textInput = await page.locator('input[type="text"][placeholder*="Type"]').first();
      
      if (!await textInput.isVisible()) {
        textInput = await page.locator('input[placeholder="Type a message (or just speak)..."]').first();
      }
      
      if (await textInput.isVisible()) {
        console.log('✅ Found text input field');
        
        // Click to focus
        await textInput.click();
        console.log('   Focused on input field');
        
        // Type characters one by one slowly
        console.log('\n📝 Starting to type characters one by one...');
        
        const testText = 'Hello';
        let disconnectedAt = -1;
        
        for (let i = 0; i < testText.length; i++) {
          const char = testText[i];
          console.log(`\n⌨️  Typing character ${i + 1}: "${char}"`);
          console.log(`   Time: ${new Date().toISOString()}`);
          
          // Type the character
          await textInput.type(char, { delay: 500 });
          
          // Wait a bit to see if disconnection happens
          await page.waitForTimeout(1000);
          
          // Check if WebSocket is still connected (specifically ElevenLabs)
          const activeWS = Array.from(websockets.values()).filter(ws => !ws.isClosed());
          const activeElevenLabs = activeWS.filter(ws => ws.url().includes('elevenlabs.io'));
          console.log(`   Active WebSockets: ${activeWS.length} (ElevenLabs: ${activeElevenLabs.length})`);
          
          // Check button status
          const buttonText = await page.evaluate(() => {
            const button = document.querySelector('.connection-button') || 
                          document.querySelector('button');
            return button ? button.textContent : 'No button found';
          });
          console.log(`   Button text: "${buttonText}"`);
          
          if (activeElevenLabs.length === 0) {
            console.log(`\n🔴 ElevenLabs WebSocket disconnected after typing ${i + 1} character(s)!`);
            console.log(`   Last character typed: "${char}"`);
            console.log(`   Text typed so far: "${testText.substring(0, i + 1)}"`);
            disconnectedAt = i + 1;
            break;
          }
        }
        
        if (disconnectedAt === -1) {
          console.log('\n✅ Successfully typed all characters without disconnection!');
          
          // Try pressing Enter to send the message
          console.log('\n⏎ Pressing Enter to send message...');
          await textInput.press('Enter');
          
          // Wait to see what happens
          await page.waitForTimeout(2000);
        }
        
        // Final status
        console.log('\n📊 Final Status:');
        const finalActiveWS = Array.from(websockets.values()).filter(ws => !ws.isClosed());
        console.log(`   Active WebSockets: ${finalActiveWS.length}`);
        console.log(`   Total WebSockets created: ${websocketCount}`);
        
        // Log frame counts for each WebSocket
        frameCountPerWs.forEach((count, wsId) => {
          console.log(`   WS-${wsId} total frames sent: ${count}`);
        });
        
        if (disconnectedAt > 0) {
          console.log(`\n❗ ISSUE CONFIRMED: WebSocket disconnects after typing ${disconnectedAt} character(s)`);
        } else {
          console.log('\n✅ No disconnection issue detected during typing');
        }
        
      } else {
        console.log('❌ Could not find text input field');
      }
    } else {
      console.log('❌ Could not find Connect button');
    }
  } catch (error) {
    console.error('\n❌ Test error:', error.message);
  }
  
  // Keep browser open for inspection
  console.log('\n⏸️  Keeping browser open for 10 seconds for inspection...');
  await page.waitForTimeout(10000);
  
  await browser.close();
})();