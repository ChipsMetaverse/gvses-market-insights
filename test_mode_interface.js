const { chromium } = require('playwright');

(async () => {
  let browser, context, page;
  
  try {
    console.log('🚀 Starting mode-based interface test...');
    
    // Launch browser with WebSocket support
    browser = await chromium.launch({ headless: false });
    context = await browser.newContext();
    page = await context.newPage();
    
    // Set up WebSocket monitoring
    let wsConnectionCount = 0;
    let wsMessages = [];
    let wsConnected = false;
    
    page.on('websocket', (ws) => {
      wsConnectionCount++;
      console.log(`📡 WebSocket connection #${wsConnectionCount}: ${ws.url()}`);
      
      ws.on('framereceived', (frame) => {
        if (frame.payload) {
          const message = frame.payload.toString();
          wsMessages.push({ type: 'received', message, timestamp: new Date().toISOString() });
          console.log(`📥 WS Received: ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}`);
        }
      });
      
      ws.on('framesent', (frame) => {
        if (frame.payload) {
          const message = frame.payload.toString();
          wsMessages.push({ type: 'sent', message, timestamp: new Date().toISOString() });
          console.log(`📤 WS Sent: ${message.substring(0, 100)}${message.length > 100 ? '...' : ''}`);
        }
      });
      
      ws.on('close', () => {
        wsConnected = false;
        console.log('❌ WebSocket connection closed');
      });
      
      // Mark as connected when we see the first frame
      ws.on('framereceived', () => {
        if (!wsConnected) {
          wsConnected = true;
          console.log('✅ WebSocket connection established');
        }
      });
    });
    
    // Navigate to the application
    console.log('🌐 Navigating to http://localhost:5174');
    await page.goto('http://localhost:5174');
    
    // Wait for page to load
    await page.waitForTimeout(2000);
    console.log('✅ Page loaded');
    
    // Take a screenshot of initial state
    await page.screenshot({ path: 'mode_test_initial.png', fullPage: true });
    console.log('📸 Initial screenshot saved');
    
    // Look for tabs in the header - may need to click Voice tab first
    const voiceTab = await page.$('button[data-tab="voice"]');
    if (voiceTab) {
      console.log('🎯 Clicking Voice tab...');
      await voiceTab.click();
      await page.waitForTimeout(1000);
    } else {
      console.log('📝 No voice tab found - might be on single page');
    }
    
    // Take a screenshot after navigation
    await page.screenshot({ path: 'mode_test_after_nav.png', fullPage: true });
    console.log('📸 After navigation screenshot saved');
    
    // Click Connect Voice Assistant button
    console.log('🔌 Clicking Connect Voice Assistant button...');
    const connectButton = await page.waitForSelector('button:has-text("Connect Voice Assistant")', { timeout: 10000 });
    await connectButton.click();
    await page.waitForTimeout(5000); // Wait for connection to establish
    
    // Take a screenshot after connecting
    await page.screenshot({ path: 'mode_test_connected.png', fullPage: true });
    console.log('📸 Connected screenshot saved');
    
    // Verify connection is established
    const isConnected = await page.$('.mode-indicator.mode-idle');
    if (isConnected) {
      console.log('✅ Connection established - Mode indicator shows idle');
    } else {
      console.log('❌ Connection not established or mode indicator not found');
    }
    
    // Test Text Mode Button
    console.log('📝 Testing Text Mode...');
    const textModeButton = await page.$('button:has-text("💬 Text")');
    if (textModeButton) {
      await textModeButton.click();
      await page.waitForTimeout(1000);
      console.log('✅ Text mode button clicked');
      
      // Verify text input appears
      const textInput = await page.$('.text-input');
      if (textInput) {
        console.log('✅ Text input field is visible in text mode');
        
        // Test typing in text mode
        console.log('⌨️  Testing text input in text mode...');
        const testMessage = 'Hello, this is a test message for the new mode-based interface!';
        
        for (let i = 0; i < testMessage.length; i++) {
          const char = testMessage[i];
          await textInput.type(char);
          await page.waitForTimeout(100); // Slow typing to observe behavior
          
          // Check if WebSocket is still connected after each character
          if (!wsConnected && i > 5) {
            console.log(`❌ WebSocket disconnected after typing ${i} characters: "${testMessage.substring(0, i)}"`);
            break;
          } else if (i % 10 === 0 && i > 0) {
            console.log(`✅ WebSocket still connected after ${i} characters`);
          }
        }
        
        if (wsConnected) {
          console.log(`🎉 SUCCESS! WebSocket remained connected for all ${testMessage.length} characters`);
          
          // Take screenshot of successful text input
          await page.screenshot({ path: 'mode_test_text_success.png', fullPage: true });
          console.log('📸 Text success screenshot saved');
          
          // Test sending the message
          console.log('📤 Testing message send...');
          await page.click('.send-button');
          await page.waitForTimeout(2000);
          console.log('✅ Message sent');
          
        } else {
          console.log('❌ WebSocket disconnected during text input');
        }
        
      } else {
        console.log('❌ Text input field not found in text mode');
      }
    } else {
      console.log('❌ Text mode button not found');
    }
    
    // Test Voice Mode Button
    console.log('🎤 Testing Voice Mode...');
    const voiceModeButton = await page.$('button:has-text("🎙️ Voice")');
    if (voiceModeButton) {
      await voiceModeButton.click();
      await page.waitForTimeout(1000);
      console.log('✅ Voice mode button clicked');
      
      // Verify voice status appears
      const voiceStatus = await page.$('.voice-status-section');
      if (voiceStatus) {
        console.log('✅ Voice status section is visible in voice mode');
        
        // Take screenshot of voice mode
        await page.screenshot({ path: 'mode_test_voice_mode.png', fullPage: true });
        console.log('📸 Voice mode screenshot saved');
        
      } else {
        console.log('❌ Voice status section not found in voice mode');
      }
    } else {
      console.log('❌ Voice mode button not found');
    }
    
    // Test Idle Mode Button
    console.log('⏸️ Testing Idle Mode...');
    const idleModeButton = await page.$('button:has-text("⏸️ Idle")');
    if (idleModeButton) {
      await idleModeButton.click();
      await page.waitForTimeout(1000);
      console.log('✅ Idle mode button clicked');
      
      // Verify idle status appears
      const idleStatus = await page.$('.idle-status-section');
      if (idleStatus) {
        console.log('✅ Idle status section is visible in idle mode');
        
        // Take screenshot of idle mode
        await page.screenshot({ path: 'mode_test_idle_mode.png', fullPage: true });
        console.log('📸 Idle mode screenshot saved');
        
      } else {
        console.log('❌ Idle status section not found in idle mode');
      }
    } else {
      console.log('❌ Idle mode button not found');
    }
    
    // Final test - verify connection is still active
    if (wsConnected) {
      console.log('🎉 FINAL SUCCESS: WebSocket connection remained stable throughout all mode tests');
    } else {
      console.log('❌ FINAL FAILURE: WebSocket disconnected during testing');
    }
    
    // Summary
    console.log('\n📊 TEST SUMMARY');
    console.log('================');
    console.log(`WebSocket connections created: ${wsConnectionCount}`);
    console.log(`WebSocket messages exchanged: ${wsMessages.length}`);
    console.log(`Final connection state: ${wsConnected ? 'CONNECTED' : 'DISCONNECTED'}`);
    
    // Take final screenshot
    await page.screenshot({ path: 'mode_test_final.png', fullPage: true });
    console.log('📸 Final screenshot saved');
    
    // Wait a bit before closing
    await page.waitForTimeout(2000);
    
  } catch (error) {
    console.error('💥 Test error:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Browser closed');
    }
  }
})();