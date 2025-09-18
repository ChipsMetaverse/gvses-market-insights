const playwright = require('playwright');

async function voiceCommandDebugTest() {
  console.log('🔍 VOICE COMMAND DEBUG TEST - MONITOR CONSOLE LOGS');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Capture console messages from the page
  const consoleMessages = [];
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    consoleMessages.push({ type, text, timestamp: new Date().toISOString() });
    console.log(`[BROWSER ${type.toUpperCase()}] ${text}`);
  });

  // Capture page errors
  page.on('pageerror', err => {
    console.log(`[BROWSER ERROR] ${err.message}`);
  });

  // Capture network failures
  page.on('requestfailed', request => {
    console.log(`[NETWORK FAILED] ${request.url()} - ${request.failure()?.errorText}`);
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION & MONITOR INITIAL LOGS');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('\n📍 PHASE 3: EXPAND VOICE COMMANDS MODAL');
    const voiceModal = page.locator('.voice-command-helper');
    const modalExists = await voiceModal.count() > 0;
    console.log(`🎤 Voice Commands modal found: ${modalExists}`);
    
    if (modalExists) {
      const isExpanded = await voiceModal.locator('.expanded').count() > 0;
      if (!isExpanded) {
        console.log('🔓 Expanding Voice Commands modal...');
        await voiceModal.locator('.helper-header').click();
        await page.waitForTimeout(1000);
      }
      
      console.log('\n📍 PHASE 4: EXECUTE VOICE COMMAND WITH CONSOLE MONITORING');
      const searchInput = voiceModal.locator('input.search-input');
      
      if (await searchInput.count() > 0) {
        console.log('🗣️ About to enter "Show me Tesla" - monitoring console...');
        
        // Clear previous logs for focus
        console.log('\n--- STARTING VOICE COMMAND EXECUTION ---');
        
        await searchInput.click();
        await page.waitForTimeout(500);
        
        console.log('✏️ Typing "Show me Tesla"...');
        await searchInput.fill('Show me Tesla');
        await page.waitForTimeout(1000);
        
        console.log('⌨️ Pressing Enter to execute command...');
        await searchInput.press('Enter');
        
        console.log('⏱️ Waiting 5 seconds for processing...');
        await page.waitForTimeout(5000);
        
        console.log('--- VOICE COMMAND EXECUTION COMPLETE ---\n');
        
        // Check for any toast messages
        const toastElements = await page.locator('.toast, .notification, [class*="toast"], [class*="notification"]').count();
        console.log(`🍞 Toast/notification elements found: ${toastElements}`);
        
        // Check current symbol in chart or dashboard
        const chartElements = await page.locator('.chart-header, .chart-title, .trading-chart, [class*="symbol"], [class*="ticker"]').count();
        console.log(`📈 Chart-related elements found: ${chartElements}`);
        
        // Check watchlist for Tesla
        const watchlistCards = await page.locator('.stock-card').count();
        console.log(`📊 Stock cards in watchlist: ${watchlistCards}`);
        
        const teslaInWatchlist = await page.locator('.stock-card:has-text("TSLA")').count() > 0;
        console.log(`🚗 Tesla (TSLA) in watchlist: ${teslaInWatchlist}`);
        
      } else {
        console.log('❌ Search input not found in modal');
      }
    }
    
    console.log('\n📍 PHASE 5: CONSOLE LOG ANALYSIS');
    console.log(`Total console messages captured: ${consoleMessages.length}`);
    
    // Filter relevant messages
    const relevantLogs = consoleMessages.filter(msg => 
      msg.text.toLowerCase().includes('tesla') ||
      msg.text.toLowerCase().includes('voice') ||
      msg.text.toLowerCase().includes('command') ||
      msg.text.toLowerCase().includes('symbol') ||
      msg.text.toLowerCase().includes('resolved') ||
      msg.text.toLowerCase().includes('error') ||
      msg.text.toLowerCase().includes('failed')
    );
    
    console.log(`\nRelevant console messages (${relevantLogs.length}):`);
    relevantLogs.forEach((msg, i) => {
      console.log(`${i + 1}. [${msg.type}] ${msg.text}`);
    });
    
    // Look for parsing/resolution messages
    const parsingLogs = consoleMessages.filter(msg =>
      msg.text.includes('Processing voice response') ||
      msg.text.includes('Searching for symbol') ||
      msg.text.includes('Found symbol') ||
      msg.text.includes('Resolved') ||
      msg.text.includes('Could not resolve')
    );
    
    console.log(`\nParsing/Resolution logs (${parsingLogs.length}):`);
    parsingLogs.forEach((msg, i) => {
      console.log(`${i + 1}. ${msg.text}`);
    });
    
    // Look for callback execution
    const callbackLogs = consoleMessages.filter(msg =>
      msg.text.includes('Voice command: Changing symbol') ||
      msg.text.includes('Symbol change not available') ||
      msg.text.includes('executeCommand')
    );
    
    console.log(`\nCallback execution logs (${callbackLogs.length}):`);
    callbackLogs.forEach((msg, i) => {
      console.log(`${i + 1}. ${msg.text}`);
    });

    await page.screenshot({ path: 'voice-debug-final-state.png' });
    
    console.log('\n🎯 DEBUG TEST SUMMARY:');
    console.log('1. Successfully monitored console output during voice command');
    console.log('2. Command: "Show me Tesla" executed via Voice Commands modal');
    console.log('3. Console logs captured and analyzed for issues');
    console.log('4. Check parsing, resolution, and callback execution logs above');
    
    // Keep browser open for manual verification
    console.log('\n🔍 Browser left open for manual inspection...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Debug Test Error:', error.message);
    await page.screenshot({ path: 'voice-debug-error.png' });
  }
}

voiceCommandDebugTest().catch(console.error);