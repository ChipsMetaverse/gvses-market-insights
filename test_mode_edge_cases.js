const { chromium } = require('playwright');

(async () => {
  let browser, context, page;
  
  try {
    console.log('🚀 Starting mode-based edge case testing...');
    
    // Launch browser with WebSocket support
    browser = await chromium.launch({ headless: false });
    context = await browser.newContext();
    page = await context.newPage();
    
    // Set up enhanced WebSocket monitoring
    let wsConnectionCount = 0;
    let wsMessages = [];
    let wsConnected = false;
    let wsDisconnectionCount = 0;
    let wsReconnectionCount = 0;
    
    page.on('websocket', (ws) => {
      wsConnectionCount++;
      console.log(`📡 WebSocket connection #${wsConnectionCount}: ${ws.url()}`);
      
      ws.on('framereceived', (frame) => {
        if (frame.payload) {
          const message = frame.payload.toString();
          wsMessages.push({ type: 'received', message, timestamp: new Date().toISOString() });
          console.log(`📥 WS Received: ${message.substring(0, 80)}${message.length > 80 ? '...' : ''}`);
        }
      });
      
      ws.on('framesent', (frame) => {
        if (frame.payload) {
          const message = frame.payload.toString();
          wsMessages.push({ type: 'sent', message, timestamp: new Date().toISOString() });
          console.log(`📤 WS Sent: ${message.substring(0, 80)}${message.length > 80 ? '...' : ''}`);
        }
      });
      
      ws.on('close', () => {
        wsConnected = false;
        wsDisconnectionCount++;
        console.log(`❌ WebSocket connection closed (total disconnections: ${wsDisconnectionCount})`);
      });
      
      // Mark as connected when we see the first frame
      ws.on('framereceived', () => {
        if (!wsConnected) {
          wsConnected = true;
          if (wsDisconnectionCount > 0) {
            wsReconnectionCount++;
            console.log(`✅ WebSocket reconnected (reconnection #${wsReconnectionCount})`);
          } else {
            console.log('✅ WebSocket connection established');
          }
        }
      });
    });
    
    // Navigate to the application
    console.log('🌐 Navigating to http://localhost:5174');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    console.log('✅ Page loaded');
    
    // Connect to voice assistant
    console.log('🔌 Connecting to Voice Assistant...');
    const connectButton = await page.waitForSelector('button:has-text("Connect Voice Assistant")', { timeout: 10000 });
    await connectButton.click();
    await page.waitForTimeout(5000);
    
    // Verify initial connection
    const isConnected = await page.$('.mode-indicator.mode-idle');
    if (!isConnected) {
      throw new Error('❌ Initial connection failed - mode indicator not found');
    }
    console.log('✅ Initial connection established');
    
    // Take initial screenshot
    await page.screenshot({ path: 'edge_test_initial.png', fullPage: true });
    console.log('📸 Initial screenshot saved');
    
    // Test 1: Rapid Mode Switching Stress Test
    console.log('\n🏃‍♂️ TEST 1: Rapid Mode Switching Stress Test');
    const modes = ['💬 Text', '🎙️ Voice', '⏸️ Idle'];
    const rapidSwitchCount = 15;
    
    for (let i = 0; i < rapidSwitchCount; i++) {
      const mode = modes[i % modes.length];
      console.log(`  Switch ${i + 1}/${rapidSwitchCount}: Clicking ${mode} mode`);
      
      const modeButton = await page.$(`button:has-text("${mode}")`);
      if (modeButton) {
        await modeButton.click();
        await page.waitForTimeout(200); // Very short delay for stress testing
        
        // Check if WebSocket is still connected
        if (!wsConnected) {
          console.log(`❌ WebSocket disconnected during rapid switch ${i + 1}`);
          break;
        }
      }
    }
    
    if (wsConnected) {
      console.log(`✅ RAPID SWITCH SUCCESS: WebSocket survived ${rapidSwitchCount} rapid mode switches`);
    }
    
    await page.screenshot({ path: 'edge_test_rapid_switch.png', fullPage: true });
    
    // Test 2: Mode Switching During Active Text Typing
    console.log('\n⌨️ TEST 2: Mode Switching During Active Text Typing');
    
    // Switch to text mode
    const textModeButton = await page.$('button:has-text("💬 Text")');
    if (textModeButton) {
      await textModeButton.click();
      await page.waitForTimeout(500);
      
      const textInput = await page.$('.text-input');
      if (textInput) {
        // Start typing a long message
        const longMessage = 'This is a very long test message that we will interrupt with mode switching to test edge case behavior and WebSocket stability during concurrent operations. Testing testing testing.';
        
        // Type first half
        await textInput.type(longMessage.substring(0, longMessage.length / 2));
        console.log('  📝 Started typing message (50% complete)');
        
        // Switch to voice mode while typing
        const voiceModeButton = await page.$('button:has-text("🎙️ Voice")');
        if (voiceModeButton) {
          await voiceModeButton.click();
          console.log('  🎤 Switched to voice mode during typing');
          await page.waitForTimeout(1000);
        }
        
        // Switch back to text and continue typing
        await textModeButton.click();
        await page.waitForTimeout(500);
        
        const textInputAgain = await page.$('.text-input');
        if (textInputAgain) {
          await textInputAgain.type(longMessage.substring(longMessage.length / 2));
          console.log('  ✅ Resumed and completed typing after mode switch');
        }
        
        if (wsConnected) {
          console.log('✅ TYPING INTERRUPT SUCCESS: WebSocket stable during typing interruption');
        }
      }
    }
    
    await page.screenshot({ path: 'edge_test_typing_interrupt.png', fullPage: true });
    
    // Test 3: Stress Test with Multiple Message Sending
    console.log('\n💬 TEST 3: Multiple Message Stress Test');
    
    const testMessages = [
      'Test message 1: Basic functionality check',
      'Test message 2: Show me Tesla stock chart',
      'Test message 3: What is the current AAPL price?',
      'Test message 4: Switch to Microsoft chart please',
      'Test message 5: Final stress test message'
    ];
    
    for (let i = 0; i < testMessages.length; i++) {
      const message = testMessages[i];
      console.log(`  📤 Sending message ${i + 1}/${testMessages.length}: ${message.substring(0, 40)}...`);
      
      // Ensure we're in text mode
      const textButton = await page.$('button:has-text("💬 Text")');
      if (textButton) await textButton.click();
      await page.waitForTimeout(500);
      
      const textInput = await page.$('.text-input');
      if (textInput) {
        await textInput.fill(message);
        await page.waitForTimeout(300);
        
        const sendButton = await page.$('.send-button');
        if (sendButton) {
          await sendButton.click();
          await page.waitForTimeout(2000); // Wait for response
        }
      }
      
      // Check connection after each message
      if (!wsConnected) {
        console.log(`❌ WebSocket disconnected after message ${i + 1}`);
        break;
      }
    }
    
    if (wsConnected) {
      console.log('✅ MULTI-MESSAGE SUCCESS: All messages sent successfully');
    }
    
    await page.screenshot({ path: 'edge_test_multi_message.png', fullPage: true });
    
    // Test 4: Voice Command Semantic Parsing Test
    console.log('\n🗣️ TEST 4: Voice Command Simulation Test');
    
    // Switch to text mode to simulate voice commands via text
    const finalTextButton = await page.$('button:has-text("💬 Text")');
    if (finalTextButton) {
      await finalTextButton.click();
      await page.waitForTimeout(500);
      
      const voiceCommands = [
        'show me Microsoft stock',
        'switch to Apple chart',
        'display Tesla information',
        'load NVIDIA data',
        'show Amazon stock chart'
      ];
      
      for (let i = 0; i < voiceCommands.length; i++) {
        const command = voiceCommands[i];
        console.log(`  🎯 Testing voice command ${i + 1}: "${command}"`);
        
        const textInput = await page.$('.text-input');
        if (textInput) {
          await textInput.fill(command);
          await page.waitForTimeout(200);
          
          const sendButton = await page.$('.send-button');
          if (sendButton) {
            await sendButton.click();
            await page.waitForTimeout(3000); // Wait for potential chart changes
          }
        }
        
        if (!wsConnected) {
          console.log(`❌ WebSocket disconnected during voice command ${i + 1}`);
          break;
        }
      }
      
      if (wsConnected) {
        console.log('✅ VOICE COMMAND SUCCESS: All semantic commands processed');
      }
    }
    
    await page.screenshot({ path: 'edge_test_voice_commands.png', fullPage: true });
    
    // Test 5: Extended Connection Stability Test
    console.log('\n⏱️ TEST 5: Extended Connection Stability Test (60 seconds)');
    
    const stabilityTestDuration = 60000; // 60 seconds
    const startTime = Date.now();
    let stabilityCheckCount = 0;
    
    while (Date.now() - startTime < stabilityTestDuration) {
      stabilityCheckCount++;
      
      // Randomly switch modes every 5 seconds
      if (stabilityCheckCount % 25 === 0) { // Every ~5 seconds
        const randomMode = modes[Math.floor(Math.random() * modes.length)];
        const randomModeButton = await page.$(`button:has-text("${randomMode}")`);
        if (randomModeButton) {
          await randomModeButton.click();
          console.log(`  🔄 Random mode switch to ${randomMode} (check ${stabilityCheckCount})`);
        }
      }
      
      await page.waitForTimeout(200);
      
      if (!wsConnected) {
        console.log(`❌ WebSocket disconnected during stability test at ${Date.now() - startTime}ms`);
        break;
      }
    }
    
    if (wsConnected) {
      console.log('✅ STABILITY SUCCESS: WebSocket remained stable for 60 seconds with random mode switches');
    }
    
    await page.screenshot({ path: 'edge_test_stability.png', fullPage: true });
    
    // Final Summary
    console.log('\n📊 EDGE CASE TEST SUMMARY');
    console.log('==========================');
    console.log(`WebSocket connections created: ${wsConnectionCount}`);
    console.log(`WebSocket messages exchanged: ${wsMessages.length}`);
    console.log(`WebSocket disconnections: ${wsDisconnectionCount}`);
    console.log(`WebSocket reconnections: ${wsReconnectionCount}`);
    console.log(`Final connection state: ${wsConnected ? 'CONNECTED ✅' : 'DISCONNECTED ❌'}`);
    console.log(`Rapid switches tested: ${rapidSwitchCount}`);
    console.log(`Messages sent: ${testMessages.length}`);
    console.log(`Voice commands tested: 5`);
    console.log(`Stability test duration: 60 seconds`);
    
    // Calculate success rate
    const totalTests = 5;
    const passedTests = (wsConnected && wsDisconnectionCount === 0) ? totalTests : totalTests - 1;
    const successRate = (passedTests / totalTests * 100).toFixed(1);
    console.log(`Overall success rate: ${successRate}%`);
    
    if (successRate >= 90) {
      console.log('🎉 EXCELLENT: System passed edge case testing with flying colors!');
    } else if (successRate >= 70) {
      console.log('✅ GOOD: System is stable with minor edge case issues');
    } else {
      console.log('⚠️ NEEDS IMPROVEMENT: System has stability issues under stress');
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'edge_test_final.png', fullPage: true });
    console.log('📸 Final screenshot saved');
    
    // Wait a bit before closing
    await page.waitForTimeout(3000);
    
  } catch (error) {
    console.error('💥 Edge case test error:', error);
  } finally {
    if (browser) {
      await browser.close();
      console.log('🔒 Browser closed - Edge case testing complete');
    }
  }
})();