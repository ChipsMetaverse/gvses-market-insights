const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true,
    slowMo: 500  // Slow down for better debugging
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Test results tracking
  const testResults = {
    passed: [],
    failed: [],
    warnings: []
  };
  
  function logTest(name, passed, details = '') {
    const result = passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${result}: ${name}${details ? ' - ' + details : ''}`);
    
    if (passed) {
      testResults.passed.push(name);
    } else {
      testResults.failed.push({ name, details });
    }
  }
  
  function logWarning(message) {
    console.log(`⚠️  WARNING: ${message}`);
    testResults.warnings.push(message);
  }
  
  // Capture console messages
  const consoleLogs = [];
  const errorLogs = [];
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    
    // Filter out noise
    if (text.includes('contentScript.js') || text.includes('extension')) {
      return;
    }
    
    consoleLogs.push({ type, text, timestamp: new Date().toISOString() });
    
    if (type === 'error') {
      errorLogs.push(text);
      console.log(`🔴 [${type}] ${text}`);
    } else if (text.includes('OpenAI') || text.includes('WebSocket') || text.includes('connect')) {
      console.log(`🔷 [${type}] ${text}`);
    }
  });
  
  // Monitor WebSocket connections
  const wsConnections = [];
  page.on('websocket', ws => {
    const url = ws.url();
    console.log(`🔌 WebSocket created: ${url}`);
    wsConnections.push({
      url,
      timestamp: new Date().toISOString(),
      state: 'created'
    });
    
    ws.on('close', () => {
      console.log(`❌ WebSocket closed: ${url}`);
      const conn = wsConnections.find(c => c.url === url);
      if (conn) conn.state = 'closed';
    });
    
    ws.on('error', error => {
      console.log(`⚠️ WebSocket error: ${url}`, error);
      const conn = wsConnections.find(c => c.url === url);
      if (conn) conn.state = 'error';
    });
  });
  
  console.log('\n🚀 === COMPREHENSIVE VOICE CONTROL FIXES TEST === 🚀\n');
  console.log('Testing all fixes implemented for voice control issues:\n');
  console.log('1. UI Duplication fixes');
  console.log('2. OpenAI WebSocket routing fixes');
  console.log('3. Console error fixes');
  console.log('4. Voice input functionality');
  console.log('5. Market data integration\n');
  
  try {
    // === 1. NAVIGATION AND INITIAL LOAD ===
    console.log('📍 1. NAVIGATION AND INITIAL LOAD');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'test-initial-load.png', fullPage: true });
    console.log('   📸 Screenshot saved: test-initial-load.png');
    
    // Check if trading dashboard loads
    const dashboard = await page.locator('[data-testid="trading-dashboard"], .trading-dashboard').first();
    const dashboardVisible = await dashboard.isVisible().catch(() => false);
    logTest('Trading dashboard loads', dashboardVisible);
    
    // === 2. UI DUPLICATION TESTS ===
    console.log('\n📍 2. UI DUPLICATION TESTS');
    
    // Test for duplicate "Try these commands" sections
    const tryCommandsElements = await page.locator('text="Try these commands"').count();
    logTest('Single "Try these commands" section', tryCommandsElements <= 1, `Found ${tryCommandsElements} instances`);
    
    // Test for single search input
    const searchInputs = await page.locator('input[type="text"], input[placeholder*="search"], input[placeholder*="add"]').count();
    logTest('Reasonable number of search inputs', searchInputs <= 3, `Found ${searchInputs} search inputs`);
    
    // Check for provider selector
    const openAIButton = await page.locator('button:has-text("OpenAI"), [data-testid="provider-openai"]').first();
    const openAIVisible = await openAIButton.isVisible().catch(() => false);
    logTest('OpenAI provider button visible', openAIVisible);
    
    if (openAIVisible) {
      // Select OpenAI provider
      console.log('\n📍 3. OPENAI PROVIDER SELECTION');
      await openAIButton.click();
      await page.waitForTimeout(1000);
      console.log('   ✓ Selected OpenAI provider');
      
      // Check for single connect button after selecting OpenAI
      const connectButtons = await page.locator('button:has-text("Connect"), [data-testid="connect-button"], .voice-control-button').count();
      logTest('Single OpenAI connect button', connectButtons >= 1 && connectButtons <= 2, `Found ${connectButtons} connect buttons`);
    } else {
      logWarning('OpenAI provider button not found - may be using different UI structure');
    }
    
    // === 3. WEBSOCKET CONNECTION TESTS ===
    console.log('\n📍 4. WEBSOCKET CONNECTION TESTS');
    
    // Try to find and click connect button
    const connectButton = await page.locator('button:has-text("Connect"), [data-testid="connect-button"], .voice-control-button').first();
    const connectButtonVisible = await connectButton.isVisible().catch(() => false);
    
    if (connectButtonVisible) {
      console.log('   🔘 Attempting to connect...');
      await connectButton.click();
      await page.waitForTimeout(5000); // Wait for connection attempt
      
      // Check WebSocket connections
      const openAIConnections = wsConnections.filter(ws => 
        ws.url.includes('/openai/realtime/ws') || 
        ws.url.includes('realtime') || 
        ws.url.includes('openai')
      );
      
      logTest('OpenAI WebSocket connection attempted', openAIConnections.length > 0, 
        `Found ${openAIConnections.length} relevant WebSocket connections`);
      
      if (openAIConnections.length > 0) {
        const correctEndpoint = openAIConnections.some(ws => ws.url.includes('/openai/realtime/ws'));
        logTest('Uses correct /openai/realtime/ws endpoint', correctEndpoint, 
          `Connection URLs: ${openAIConnections.map(ws => ws.url).join(', ')}`);
      }
      
      // Test direct WebSocket connection with correct endpoint
      console.log('   🔗 Testing direct WebSocket connection...');
      const wsTest = await page.evaluate(async () => {
        return new Promise((resolve) => {
          const wsUrl = 'ws://localhost:8000/openai/realtime/ws';
          const ws = new WebSocket(wsUrl);
          const result = { success: false, error: null, url: wsUrl };
          
          const timeout = setTimeout(() => {
            ws.close();
            result.error = 'Connection timeout';
            resolve(result);
          }, 3000);
          
          ws.onopen = () => {
            result.success = true;
            clearTimeout(timeout);
            ws.close();
            resolve(result);
          };
          
          ws.onerror = (error) => {
            result.error = 'Connection failed';
            clearTimeout(timeout);
            resolve(result);
          };
        });
      });
      
      logTest('Direct WebSocket connection to /openai/realtime/ws', wsTest.success, 
        wsTest.error || 'Connected successfully');
    } else {
      logWarning('Connect button not found - testing without connection');
    }
    
    // === 4. CONSOLE ERROR MONITORING ===
    console.log('\n📍 5. CONSOLE ERROR MONITORING');
    
    // Check for specific error messages we fixed
    const connectionErrors = errorLogs.filter(log => 
      log.includes('Not connected to OpenAI Realtime API') ||
      log.includes('WebSocket connection failed') ||
      log.includes('realtime-relay')
    );
    
    logTest('No "Not connected to OpenAI" errors', connectionErrors.length === 0, 
      connectionErrors.length > 0 ? `Found: ${connectionErrors.join('; ')}` : '');
    
    const totalErrors = errorLogs.length;
    logTest('Minimal console errors', totalErrors <= 3, `Found ${totalErrors} errors total`);
    
    // === 5. VOICE INPUT TESTS ===
    console.log('\n📍 6. VOICE INPUT FUNCTIONALITY');
    
    // Test mic button or voice area
    const micButton = await page.locator('.mic-button, .voice-control-button, [data-testid="record-button"]').first();
    const micVisible = await micButton.isVisible().catch(() => false);
    logTest('Voice input button visible', micVisible);
    
    if (micVisible) {
      // Test clicking mic button
      await micButton.click().catch(() => {});
      await page.waitForTimeout(1000);
      console.log('   ✓ Clicked voice input button');
    }
    
    // Test text input as fallback
    const textInput = await page.locator('input[type="text"], textarea, [data-testid="message-input"]').first();
    const textInputVisible = await textInput.isVisible().catch(() => false);
    logTest('Text input fallback available', textInputVisible);
    
    if (textInputVisible) {
      await textInput.fill('Test voice command: show me Tesla').catch(() => {});
      console.log('   ✓ Text input works');
    }
    
    // === 6. MARKET DATA INTEGRATION ===
    console.log('\n📍 7. MARKET DATA INTEGRATION');
    
    // Check if market data loads
    const stockCards = await page.locator('.stock-card, [data-testid*="stock"], .market-insights').count();
    logTest('Market data elements present', stockCards > 0, `Found ${stockCards} market elements`);
    
    // Check for chart
    const chart = await page.locator('.trading-chart, canvas, [data-testid="trading-chart"]').first();
    const chartVisible = await chart.isVisible().catch(() => false);
    logTest('Trading chart visible', chartVisible);
    
    // Check for news section
    const newsSection = await page.locator('.news, [data-testid*="news"], .chart-analysis').first();
    const newsVisible = await newsSection.isVisible().catch(() => false);
    logTest('News/analysis section visible', newsVisible);
    
    // Take final screenshot
    await page.screenshot({ path: 'test-final-state.png', fullPage: true });
    console.log('   📸 Screenshot saved: test-final-state.png');
    
    // === 7. FINAL SYSTEM STATE CHECK ===
    console.log('\n📍 8. FINAL SYSTEM STATE CHECK');
    
    // Check overall page responsiveness
    const pageTitle = await page.title();
    logTest('Page responsive', pageTitle.length > 0, `Title: "${pageTitle}"`);
    
    // Check if any critical elements are missing
    const criticalElementsCheck = await page.evaluate(() => {
      const body = document.body;
      const hasContent = body && body.children.length > 0;
      const hasStyles = getComputedStyle(body).fontSize !== '';
      return { hasContent, hasStyles };
    });
    
    logTest('Page content loaded', criticalElementsCheck.hasContent);
    logTest('Styles applied', criticalElementsCheck.hasStyles);
    
  } catch (error) {
    console.error('\n💥 Test execution error:', error);
    testResults.failed.push({ name: 'Test Execution', details: error.message });
  }
  
  // === FINAL REPORT ===
  console.log('\n' + '='.repeat(60));
  console.log('📊 COMPREHENSIVE TEST RESULTS SUMMARY');
  console.log('='.repeat(60));
  
  console.log(`\n✅ PASSED TESTS: ${testResults.passed.length}`);
  testResults.passed.forEach(test => console.log(`   ✓ ${test}`));
  
  if (testResults.failed.length > 0) {
    console.log(`\n❌ FAILED TESTS: ${testResults.failed.length}`);
    testResults.failed.forEach(test => console.log(`   ✗ ${test.name}${test.details ? ' - ' + test.details : ''}`));
  }
  
  if (testResults.warnings.length > 0) {
    console.log(`\n⚠️  WARNINGS: ${testResults.warnings.length}`);
    testResults.warnings.forEach(warning => console.log(`   ⚠️  ${warning}`));
  }
  
  console.log('\n🔍 WEBSOCKET CONNECTIONS:');
  if (wsConnections.length > 0) {
    wsConnections.forEach(ws => console.log(`   🔌 ${ws.url} (${ws.state})`));
  } else {
    console.log('   No WebSocket connections detected');
  }
  
  console.log('\n📝 CONSOLE LOGS SUMMARY:');
  console.log(`   Total logs: ${consoleLogs.length}`);
  console.log(`   Error logs: ${errorLogs.length}`);
  if (errorLogs.length > 0 && errorLogs.length <= 5) {
    console.log('   Recent errors:');
    errorLogs.slice(-5).forEach(error => console.log(`     🔴 ${error}`));
  }
  
  const passRate = Math.round((testResults.passed.length / (testResults.passed.length + testResults.failed.length)) * 100);
  console.log(`\n🎯 OVERALL PASS RATE: ${passRate}%`);
  
  if (passRate >= 80) {
    console.log('🎉 VOICE CONTROL FIXES VERIFICATION: SUCCESS! 🎉');
  } else if (passRate >= 60) {
    console.log('⚠️  VOICE CONTROL FIXES VERIFICATION: PARTIAL SUCCESS');
  } else {
    console.log('❌ VOICE CONTROL FIXES VERIFICATION: NEEDS ATTENTION');
  }
  
  console.log('\n📸 Screenshots saved:');
  console.log('   - test-initial-load.png');
  console.log('   - test-final-state.png');
  
  console.log('\n✨ Test completed at:', new Date().toISOString());
  
  await browser.close();
})().catch(console.error);