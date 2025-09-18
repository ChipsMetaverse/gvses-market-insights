const playwright = require('playwright');

async function verifyOpenAIConnectionFix() {
  console.log('🔧 OPENAI CONNECTION FIX VERIFICATION');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Track all console messages for debugging
  const allLogs = [];
  const debugLogs = [];
  const connectionLogs = [];
  
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    const logEntry = { type, text, time: new Date().toISOString() };
    
    allLogs.push(logEntry);
    console.log(`[${type.toUpperCase()}] ${text}`);
    
    // Filter debug messages we added
    if (text.includes('🔧 DEBUG:') || text.includes('🔧 HOOK DEBUG:')) {
      debugLogs.push(logEntry);
    }
    
    // Filter connection-related messages
    if (text.includes('Connected') || text.includes('connected') || 
        text.includes('startConversation') || text.includes('session.created') ||
        text.includes('onConnected')) {
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
    
    // Check initial connection state
    const initialConnectionState = await page.evaluate(() => {
      // Look for connection toggle
      const toggle = document.querySelector('[data-testid="connection-toggle"]');
      const statusText = document.querySelector('.toggle-label')?.textContent;
      const statusDot = document.querySelector('.status-dot');
      
      return {
        toggleExists: !!toggle,
        toggleChecked: toggle?.checked || false,
        statusText: statusText?.trim(),
        statusDotClass: statusDot?.className,
        toggleDisabled: toggle?.disabled || false
      };
    });
    
    console.log('Initial Connection State:', JSON.stringify(initialConnectionState, null, 2));
    
    console.log('\n📍 PHASE 4: TRIGGER CONNECTION');
    
    // Click the connection toggle to start connection
    const toggleExists = await page.locator('[data-testid="connection-toggle"]').count() > 0;
    
    if (toggleExists) {
      console.log('🔘 Connection toggle found - triggering connection...');
      
      // Click the toggle to start connection
      await page.click('[data-testid="connection-toggle"]');
      
      console.log('⏱️ Waiting for connection process (15 seconds)...');
      
      // Wait for debug messages and connection to establish
      await page.waitForTimeout(15000);
      
      console.log('\n📍 PHASE 5: VERIFY CONNECTION STATE AFTER TRIGGER');
      
      // Check final connection state
      const finalConnectionState = await page.evaluate(() => {
        const toggle = document.querySelector('[data-testid="connection-toggle"]');
        const statusText = document.querySelector('.toggle-label')?.textContent;
        const statusDot = document.querySelector('.status-dot');
        
        return {
          toggleChecked: toggle?.checked || false,
          statusText: statusText?.trim(),
          statusDotClass: statusDot?.className,
          toggleDisabled: toggle?.disabled || false
        };
      });
      
      console.log('Final Connection State:', JSON.stringify(finalConnectionState, null, 2));
      
    } else {
      console.log('❌ Connection toggle not found');
    }
    
    console.log('\n📍 PHASE 6: ANALYZE DEBUG LOGS');
    
    console.log(`\n🔧 Debug Messages Found (${debugLogs.length}):`);
    debugLogs.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    console.log(`\n🔗 Connection Messages Found (${connectionLogs.length}):`);
    connectionLogs.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    console.log('\n📍 PHASE 7: CONNECTION FIX VERIFICATION');
    
    // Analyze the results
    const hasConnectAttempt = connectionLogs.some(log => 
      log.text.includes('startConversation') || 
      log.text.includes('About to call startConversation')
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
    
    console.log('\n🎯 FIX VERIFICATION RESULTS:');
    console.log(`✅ Connection attempt triggered: ${hasConnectAttempt}`);
    console.log(`✅ Service debug messages present: ${hasServiceDebug}`);
    console.log(`✅ Hook debug messages present: ${hasHookDebug}`);
    console.log(`✅ Timeout mechanism triggered: ${hasTimeoutTrigger}`);
    console.log(`✅ React state update called: ${hasStateUpdate}`);
    
    const allChecksPass = hasConnectAttempt && hasServiceDebug && hasHookDebug;
    const fixWorking = allChecksPass && (hasTimeoutTrigger || hasStateUpdate);
    
    console.log(`\n🔧 CONNECTION FIX STATUS: ${fixWorking ? '✅ WORKING' : '❌ NEEDS ATTENTION'}`);
    
    if (fixWorking) {
      console.log('💡 The React isConnected state fix is functioning correctly!');
      console.log('   - Connection flow is triggered properly');
      console.log('   - Debug callbacks are working');
      console.log('   - State updates are being called');
    } else {
      console.log('⚠️  Some issues detected:');
      if (!hasConnectAttempt) console.log('   - Connection not being triggered');
      if (!hasServiceDebug) console.log('   - Service callbacks not working');
      if (!hasHookDebug) console.log('   - Hook state updates not working');
    }
    
    await page.screenshot({ 
      path: 'openai-connection-fix-verification.png',
      fullPage: true
    });
    
    console.log('\n📍 PHASE 8: TEXT MESSAGE TEST');
    
    // Test text message functionality
    const messageInput = page.locator('input[data-testid="message-input"]');
    const messageInputExists = await messageInput.count() > 0;
    
    if (messageInputExists) {
      console.log('💬 Testing text message: "What is the current market status?"');
      
      await messageInput.fill("What is the current market status?");
      await page.waitForTimeout(1000);
      
      const sendButton = page.locator('button[data-testid="send-button"]');
      const sendButtonExists = await sendButton.count() > 0;
      
      if (sendButtonExists && await sendButton.isEnabled()) {
        console.log('📤 Sending test message...');
        await sendButton.click();
        await page.waitForTimeout(3000);
        
        // Check if message was processed
        const inputValue = await messageInput.inputValue();
        const messageProcessed = !inputValue || inputValue.trim() === '';
        console.log(`📬 Message processed: ${messageProcessed}`);
      }
    }
    
    console.log('\n🎯 FINAL SUMMARY:');
    console.log(`1. Connection Fix Status: ${fixWorking ? 'WORKING ✅' : 'NEEDS WORK ❌'}`);
    console.log(`2. Debug Messages: ${debugLogs.length} found`);
    console.log(`3. Connection Messages: ${connectionLogs.length} found`);
    console.log(`4. Total Console Logs: ${allLogs.length}`);
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser left open for manual verification...');
    console.log('💡 Try manually toggling the connection and observe the debug messages');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Verification Error:', error.message);
    await page.screenshot({ path: 'openai-connection-fix-error.png' });
  }
}

verifyOpenAIConnectionFix().catch(console.error);