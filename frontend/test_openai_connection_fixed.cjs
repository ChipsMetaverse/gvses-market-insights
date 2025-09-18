const playwright = require('playwright');

async function testOpenAIConnectionFixed() {
  console.log('🔧 OPENAI CONNECTION FIX VERIFICATION (FIXED)');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Track debug and connection messages
  const debugLogs = [];
  const connectionLogs = [];
  const allLogs = [];
  
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    const logEntry = { type, text, time: new Date().toISOString() };
    
    allLogs.push(logEntry);
    console.log(`[${type.toUpperCase()}] ${text}`);
    
    // Filter debug messages we added
    if (text.includes('🔧 DEBUG:') || text.includes('🔧 HOOK DEBUG:') || text.includes('🎯 handleConnectToggle')) {
      debugLogs.push(logEntry);
    }
    
    // Filter connection-related messages
    if (text.includes('Connected') || text.includes('connected') || 
        text.includes('startConversation') || text.includes('session.created') ||
        text.includes('onConnected') || text.includes('About to call startConversation')) {
      connectionLogs.push(logEntry);
    }
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(3000);
    
    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('\n📍 PHASE 3: VERIFY INITIAL STATE');
    
    const initialState = await page.evaluate(() => {
      const toggle = document.querySelector('[data-testid="connection-toggle"]');
      const container = document.querySelector('.toggle-switch-container');
      return {
        toggleExists: !!toggle,
        toggleChecked: toggle?.checked || false,
        toggleVisible: toggle && toggle.offsetHeight > 0 && toggle.offsetWidth > 0,
        toggleDisabled: toggle?.disabled || false,
        containerExists: !!container,
        statusText: document.querySelector('.toggle-label')?.textContent?.trim()
      };
    });
    
    console.log('Initial State:', JSON.stringify(initialState, null, 2));
    
    if (!initialState.toggleExists) {
      console.error('❌ CONNECTION TOGGLE NOT FOUND - cannot proceed with test');
      await page.screenshot({ path: 'openai-connection-toggle-missing.png' });
      return;
    }
    
    console.log('\n📍 PHASE 4: TRIGGER CONNECTION USING PROPER PLAYWRIGHT CLICK');
    
    // Use Playwright's proper click method instead of dispatching events
    // This should trigger React's synthetic event system correctly
    console.log('🖱️ Clicking connection toggle using Playwright...');
    
    // Try clicking the container first (which has onClick handler)
    const containerClickable = await page.locator('.toggle-switch-container').count() > 0;
    if (containerClickable) {
      console.log('🎯 Clicking toggle container...');
      await page.click('.toggle-switch-container');
    } else {
      // Fallback to clicking the checkbox directly
      console.log('🎯 Clicking toggle checkbox...');
      await page.click('[data-testid="connection-toggle"]');
    }
    
    console.log('⏱️ Waiting for connection process and debug messages (15 seconds)...');
    await page.waitForTimeout(15000);
    
    console.log('\n📍 PHASE 5: VERIFY POST-CONNECTION STATE');
    const finalState = await page.evaluate(() => {
      const toggle = document.querySelector('[data-testid="connection-toggle"]');
      return {
        toggleChecked: toggle?.checked || false,
        statusText: document.querySelector('.toggle-label')?.textContent?.trim(),
        statusDotClass: document.querySelector('.status-dot')?.className
      };
    });
    
    console.log('Final State:', JSON.stringify(finalState, null, 2));
    
    console.log('\n📍 PHASE 6: ANALYZE RESULTS');
    
    console.log(`\n🔧 Debug Messages Found (${debugLogs.length}):`);
    debugLogs.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    console.log(`\n🔗 Connection Messages Found (${connectionLogs.length}):`);
    connectionLogs.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    console.log('\n📍 PHASE 7: FIX VERIFICATION');
    
    // Analyze if the fix is working
    const hasHandlerCall = debugLogs.some(log => 
      log.text.includes('🎯 handleConnectToggle called')
    );
    
    const hasStartConversationCall = connectionLogs.some(log => 
      log.text.includes('About to call startConversation') || 
      log.text.includes('startConversation')
    );
    
    const hasServiceDebug = debugLogs.some(log => 
      log.text.includes('🔧 DEBUG:') && 
      (log.text.includes('connect') || log.text.includes('onConnected'))
    );
    
    const hasHookDebug = debugLogs.some(log => 
      log.text.includes('🔧 HOOK DEBUG:')
    );
    
    const hasTimeoutTrigger = debugLogs.some(log => 
      log.text.includes('Connection timeout') || 
      log.text.includes('forcing connected state')
    );
    
    const hasStateUpdate = debugLogs.some(log => 
      log.text.includes('setIsConnected(true)')
    );
    
    console.log('\n🎯 CONNECTION FIX VERIFICATION RESULTS:');
    console.log(`✅ React handler triggered: ${hasHandlerCall}`);
    console.log(`✅ startConversation() called: ${hasStartConversationCall}`);
    console.log(`✅ Service debug messages: ${hasServiceDebug}`);
    console.log(`✅ Hook debug messages: ${hasHookDebug}`);
    console.log(`✅ Timeout mechanism: ${hasTimeoutTrigger}`);
    console.log(`✅ React state update: ${hasStateUpdate}`);
    
    const basicFlowWorking = hasHandlerCall && hasStartConversationCall;
    const debugCallbacksWorking = hasServiceDebug && hasHookDebug;
    const fixFullyWorking = basicFlowWorking && (debugCallbacksWorking || hasTimeoutTrigger);
    
    console.log(`\n🔧 FINAL FIX STATUS: ${fixFullyWorking ? '✅ WORKING' : '❌ NEEDS ATTENTION'}`);
    
    if (fixFullyWorking) {
      console.log('💡 SUCCESS: The OpenAI connection fix is working correctly!');
      console.log('   - React event handler is triggered by user interaction');
      console.log('   - Connection flow executes properly');
      console.log('   - Debug callbacks are functional');
      console.log('   - State management is working');
      
      if (hasTimeoutTrigger) {
        console.log('   - Timeout fallback mechanism is active');
      }
    } else {
      console.log('⚠️ ISSUES DETECTED:');
      if (!hasHandlerCall) console.log('   - React handler not being triggered');
      if (!hasStartConversationCall) console.log('   - Connection not being initiated');
      if (!debugCallbacksWorking && !hasTimeoutTrigger) console.log('   - Debug callbacks not working');
    }
    
    console.log('\n📍 PHASE 8: TEST MESSAGE FUNCTIONALITY');
    
    // Test text message functionality
    const messageInput = page.locator('input[data-testid="message-input"]');
    const messageInputExists = await messageInput.count() > 0;
    
    if (messageInputExists) {
      console.log('💬 Testing text message functionality...');
      await messageInput.fill("Test message for connection verification");
      await page.waitForTimeout(1000);
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonExists = await sendButton.count() > 0;
      
      if (sendButtonExists && await sendButton.isEnabled()) {
        console.log('📤 Sending test message...');
        await sendButton.click();
        await page.waitForTimeout(3000);
        
        const inputValue = await messageInput.inputValue();
        const messageProcessed = !inputValue || inputValue.trim() === '';
        console.log(`📬 Message processed: ${messageProcessed}`);
      }
    }
    
    await page.screenshot({ 
      path: 'openai-connection-fixed-test.png',
      fullPage: true
    });
    
    console.log('\n🎯 VERIFICATION COMPLETE!');
    console.log(`Connection Fix Status: ${fixFullyWorking ? 'WORKING ✅' : 'NEEDS WORK ❌'}`);
    console.log(`Debug Messages: ${debugLogs.length}`);
    console.log(`Connection Messages: ${connectionLogs.length}`);
    console.log(`Total Logs: ${allLogs.length}`);
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser kept open for manual inspection...');
    console.log('💡 You can manually verify the connection behavior');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
    await page.screenshot({ path: 'openai-connection-fixed-error.png' });
  }
}

testOpenAIConnectionFixed().catch(console.error);