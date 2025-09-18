const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true  // Open DevTools to see console errors
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Capture console messages
  const consoleLogs = [];
  const errors = [];
  
  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push(`[${msg.type()}] ${text}`);
    if (msg.type() === 'error') {
      errors.push(text);
    }
  });
  
  page.on('pageerror', error => {
    errors.push(`Page Error: ${error.message}`);
  });
  
  // Monitor WebSocket connections
  page.on('websocket', ws => {
    console.log('WebSocket created:', ws.url());
    
    ws.on('framesent', data => {
      console.log('WebSocket sent:', data.payload?.substring(0, 100));
    });
    
    ws.on('framereceived', data => {
      console.log('WebSocket received:', data.payload?.substring(0, 100));
    });
    
    ws.on('close', () => {
      console.log('WebSocket closed:', ws.url());
    });
    
    ws.on('error', error => {
      console.log('WebSocket error:', ws.url(), error);
    });
  });
  
  console.log('=== INVESTIGATING OPENAI WEBSOCKET ISSUES ===\n');
  
  // Navigate to the app
  console.log('1. Navigating to http://localhost:5174...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Check initial state
  console.log('\n2. Checking initial page state...');
  const title = await page.title();
  console.log('   Page title:', title);
  
  // Look for provider selector
  const providerSelector = await page.locator('[data-testid="provider-selector"]');
  const providerExists = await providerSelector.count() > 0;
  console.log('   Provider selector exists:', providerExists);
  
  if (providerExists) {
    const currentProvider = await providerSelector.textContent();
    console.log('   Current provider:', currentProvider);
  }
  
  // Switch to OpenAI provider
  console.log('\n3. Attempting to switch to OpenAI provider...');
  const openaiButton = await page.locator('button:has-text("OpenAI")').first();
  const openaiButtonExists = await openaiButton.count() > 0;
  
  if (openaiButtonExists) {
    console.log('   Found OpenAI button, clicking...');
    await openaiButton.click();
    await page.waitForTimeout(1000);
    
    // Check if provider switched
    const selectedProvider = await page.locator('.provider-option.selected').textContent().catch(() => 'Unknown');
    console.log('   Selected provider after click:', selectedProvider);
  } else {
    console.log('   OpenAI button not found!');
  }
  
  // Try to connect
  console.log('\n4. Attempting to connect to OpenAI voice...');
  const connectButton = await page.locator('[data-testid="voice-connect-toggle"]');
  const connectExists = await connectButton.count() > 0;
  
  if (connectExists) {
    const buttonText = await connectButton.textContent();
    console.log('   Connect button text:', buttonText);
    
    if (buttonText.includes('Connect')) {
      console.log('   Clicking connect button...');
      await connectButton.click();
      
      // Wait for connection attempt
      await page.waitForTimeout(3000);
      
      // Check connection status
      const statusAfterConnect = await connectButton.textContent();
      console.log('   Button text after connect attempt:', statusAfterConnect);
      
      // Check for connection indicator
      const isConnected = await page.locator('.status-indicator.connected').count() > 0;
      console.log('   Connection indicator shows connected:', isConnected);
    }
  } else {
    console.log('   Connect button not found!');
  }
  
  // Print console errors
  console.log('\n5. Console Errors Captured:');
  if (errors.length > 0) {
    errors.forEach(err => {
      // Filter out browser extension errors
      if (!err.includes('contentScript.js')) {
        console.log('   ERROR:', err);
      }
    });
  } else {
    console.log('   No errors captured');
  }
  
  // Print relevant console logs
  console.log('\n6. Relevant Console Logs:');
  const relevantLogs = consoleLogs.filter(log => 
    log.includes('WebSocket') || 
    log.includes('OpenAI') || 
    log.includes('realtime') ||
    log.includes('Relay') ||
    log.includes('Failed') ||
    log.includes('Error')
  );
  
  relevantLogs.forEach(log => {
    if (!log.includes('contentScript.js')) {
      console.log('   ', log);
    }
  });
  
  // Test direct WebSocket connection to relay endpoint
  console.log('\n7. Testing direct WebSocket connection to relay endpoint...');
  const wsTestResult = await page.evaluate(async () => {
    const sessionId = `test_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/realtime-relay/${sessionId}`;
    
    return new Promise((resolve) => {
      const ws = new WebSocket(wsUrl);
      const result = { url: wsUrl, status: 'unknown', error: null };
      
      ws.onopen = () => {
        result.status = 'connected';
        ws.close();
        resolve(result);
      };
      
      ws.onerror = (error) => {
        result.status = 'error';
        result.error = 'Connection failed';
        resolve(result);
      };
      
      ws.onclose = (event) => {
        if (result.status === 'unknown') {
          result.status = 'closed';
          result.error = `Code: ${event.code}, Reason: ${event.reason}`;
          resolve(result);
        }
      };
      
      // Timeout after 5 seconds
      setTimeout(() => {
        if (result.status === 'unknown') {
          result.status = 'timeout';
          ws.close();
          resolve(result);
        }
      }, 5000);
    });
  });
  
  console.log('   Direct WebSocket test result:', JSON.stringify(wsTestResult, null, 2));
  
  // Take a screenshot
  console.log('\n8. Taking screenshot...');
  await page.screenshot({ path: 'openai-websocket-investigation.png' });
  console.log('   Screenshot saved as openai-websocket-investigation.png');
  
  console.log('\n=== INVESTIGATION COMPLETE ===');
  
  // Keep browser open for 5 seconds to observe
  await page.waitForTimeout(5000);
  await browser.close();
})();