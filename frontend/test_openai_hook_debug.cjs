const playwright = require('playwright');

async function testOpenAIHookCallbacks() {
  console.log('🔧 OPENAI HOOK CALLBACK TEST');
  console.log('='.repeat(50));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Track console messages
  const logs = [];
  page.on('console', msg => {
    const text = msg.text();
    logs.push({ type: msg.type(), text, time: new Date().toISOString() });
    console.log(`[${msg.type().toUpperCase()}] ${text}`);
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(3000);
    
    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('\n📍 PHASE 3: INJECT CALLBACK DEBUGGING');
    
    // Inject debugging code to track React hook state and service callbacks
    await page.evaluate(() => {
      // Patch console.log to include component name
      window.originalLog = console.log;
      console.log = (...args) => {
        window.originalLog('[DEBUG]', new Date().toISOString(), ...args);
      };
      
      // Track OpenAI service callback invocations
      console.log('🔧 Callback debugging injected');
      
      // Look for React component using the hook
      const reactRoot = document.querySelector('#root');
      if (reactRoot && reactRoot._reactInternalFiber) {
        console.log('⚛️ React detected - attempting to access hook state');
      }
    });
    
    console.log('\n📍 PHASE 4: ATTEMPT CONNECTION');
    
    // Try to trigger connection via the toggle button
    const connectToggle = page.locator('[data-testid="connection-toggle"]');
    const toggleExists = await connectToggle.count() > 0;
    
    if (toggleExists) {
      console.log('🔘 Connection toggle found - clicking...');
      await connectToggle.click();
      await page.waitForTimeout(5000); // Wait for connection attempt
      
      // Check if loading state changes
      const isLoading = await page.evaluate(() => {
        const toggle = document.querySelector('[data-testid="connection-toggle"]');
        return toggle ? toggle.textContent.includes('Connecting') : false;
      });
      
      console.log(`⏳ Loading state detected: ${isLoading}`);
      
    } else {
      console.log('❌ Connection toggle not found - checking for other UI elements');
      
      // Check for any OpenAI-related buttons
      const allButtons = await page.$$eval('button', buttons => 
        buttons.map(btn => ({
          text: btn.textContent,
          disabled: btn.disabled,
          className: btn.className
        }))
      );
      
      console.log('🔍 Available buttons:', allButtons);
    }
    
    console.log('\n📍 PHASE 5: ANALYZE CALLBACK LOGS');
    
    // Wait a bit more for any delayed callbacks
    await page.waitForTimeout(3000);
    
    // Filter logs for OpenAI service activity
    const serviceActivity = logs.filter(log => 
      log.text.includes('OpenAI') || 
      log.text.includes('session.created') ||
      log.text.includes('Connected') ||
      log.text.includes('RealtimeClient') ||
      log.text.includes('onConnected') ||
      log.text.includes('onDisconnected')
    );
    
    console.log(`\n🔍 OpenAI Service Activity (${serviceActivity.length} logs):`);
    serviceActivity.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    // Check React state updates
    const reactStateUpdates = logs.filter(log => 
      log.text.includes('setIsConnected') ||
      log.text.includes('isConnected:') ||
      log.text.includes('Connection state:')
    );
    
    console.log(`\n⚛️ React State Updates (${reactStateUpdates.length} logs):`);
    reactStateUpdates.forEach((log, i) => {
      console.log(`${i + 1}. [${log.type}] ${log.text}`);
    });
    
    await page.screenshot({ 
      path: 'openai-hook-callback-test.png',
      fullPage: true
    });
    
    console.log('\n🎯 CALLBACK TEST SUMMARY:');
    console.log('1. Checked if OpenAI service callbacks are being invoked');
    console.log('2. Monitored React state updates in the hook');
    console.log('3. Analyzed the callback chain from service → hook → UI');
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser left open for manual inspection...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
    await page.screenshot({ path: 'openai-hook-error.png' });
  }
}

testOpenAIHookCallbacks().catch(console.error);