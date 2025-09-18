const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Collect console messages and errors
  const consoleLogs = [];
  const consoleErrors = [];
  
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    
    if (type === 'error') {
      consoleErrors.push(text);
      console.log('❌ Console Error:', text);
    } else if (type === 'warning') {
      console.log('⚠️  Console Warning:', text);
    } else {
      consoleLogs.push(text);
    }
  });
  
  // Also catch page errors
  page.on('pageerror', error => {
    consoleErrors.push(error.toString());
    console.log('❌ Page Error:', error);
  });
  
  console.log('\n📱 Opening Voice Assistant Application...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded successfully');
    
    // Wait for the app to initialize
    await page.waitForTimeout(2000);
    
    // Check if main elements are present
    console.log('\n🔍 Checking UI Elements...\n');
    
    // Check for Voice + Manual Control tab (use data-testid for precision)
    const voiceTab = await page.locator('[data-testid="voice-tab"]').first();
    if (await voiceTab.isVisible()) {
      console.log('✅ Voice + Manual Control tab is visible');
    } else {
      console.log('❌ Voice + Manual Control tab not found');
    }
    
    // Click on Voice tab
    await voiceTab.click();
    console.log('✅ Clicked on Voice tab');
    
    // Check for provider dropdown
    const providerDropdown = await page.locator('select').first();
    if (await providerDropdown.isVisible()) {
      console.log('✅ Provider dropdown is visible');
      
      // Get all options
      const options = await providerDropdown.locator('option').allTextContents();
      console.log('   Available providers:', options);
      
      // Verify OpenAI option is NOT present (as per our fix)
      if (!options.some(opt => opt.includes('OpenAI Realtime'))) {
        console.log('✅ OpenAI provider option correctly removed');
      } else {
        console.log('❌ OpenAI provider option still present (should be removed)');
      }
      
      // Verify Agent option is present
      if (options.some(opt => opt.includes('Agent'))) {
        console.log('✅ Agent provider option is present');
      } else {
        console.log('❌ Agent provider option not found');
      }
    }
    
    // Check for Connect toggle
    const connectToggle = await page.locator('text=Connect').first();
    if (await connectToggle.isVisible()) {
      console.log('✅ Connect toggle is visible');
    } else {
      console.log('❌ Connect toggle not found');
    }
    
    // Check for any error messages
    const errorElements = await page.locator('text=/error/i').all();
    if (errorElements.length > 0) {
      for (const error of errorElements) {
        const errorText = await error.textContent();
        if (errorText.includes('Backend not ready')) {
          console.log('❌ Health-gate error still showing:', errorText);
        } else {
          console.log('⚠️  Other error found:', errorText);
        }
      }
    } else {
      console.log('✅ No error messages displayed');
    }
    
    console.log('\n🎤 Testing Voice Connection...\n');
    
    // Wait a moment before connecting
    await page.waitForTimeout(1000);
    
    // Try to connect
    await connectToggle.click();
    console.log('✅ Clicked Connect toggle');
    
    // Wait for connection
    await page.waitForTimeout(3000);
    
    // Check if connected (toggle should change)
    const isConnected = await page.locator('text=Disconnect').isVisible().catch(() => false) ||
                       await page.locator('[aria-checked="true"]').isVisible().catch(() => false);
    
    if (isConnected) {
      console.log('✅ Successfully connected to voice assistant');
      
      // Check for any connection-related console messages
      const connectionLogs = consoleLogs.filter(log => 
        log.includes('connected') || 
        log.includes('WebSocket') || 
        log.includes('session')
      );
      
      if (connectionLogs.length > 0) {
        console.log('\n📋 Connection logs:');
        connectionLogs.forEach(log => console.log('   ', log.substring(0, 100)));
      }
      
      // Send a test message via text input
      const textInput = await page.locator('input[type="text"], textarea').filter({ hasText: '' }).first();
      if (await textInput.isVisible()) {
        console.log('\n💬 Testing text message...');
        await textInput.fill('What is the current price of Apple?');
        await textInput.press('Enter');
        console.log('✅ Test message sent');
        
        // Wait for response
        await page.waitForTimeout(3000);
        
        // Check if response appeared
        const messages = await page.locator('.message, [role="log"]').allTextContents();
        if (messages.some(msg => msg.toLowerCase().includes('apple') || msg.includes('AAPL'))) {
          console.log('✅ Response received for test query');
        }
      }
      
    } else {
      console.log('⚠️  Could not verify connection status');
    }
    
    // Take a screenshot
    await page.screenshot({ path: 'voice-assistant-test.png', fullPage: true });
    console.log('📸 Screenshot saved as voice-assistant-test.png');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  }
  
  // Final console error report
  console.log('\n📊 Console Error Summary:\n');
  if (consoleErrors.length === 0) {
    console.log('✅ No console errors detected');
  } else {
    console.log(`❌ Found ${consoleErrors.length} console errors:`);
    consoleErrors.forEach((error, i) => {
      // Filter out known benign errors
      if (!error.includes('contentScript.js') && 
          !error.includes('BrowserTools MCP') &&
          !error.includes('Failed to load resource: the server responded with a status of 404')) {
        console.log(`   ${i + 1}. ${error.substring(0, 200)}`);
      }
    });
  }
  
  console.log('\n✨ Test Complete\n');
  
  // Keep browser open for 5 seconds to observe
  await page.waitForTimeout(5000);
  
  await browser.close();
})();