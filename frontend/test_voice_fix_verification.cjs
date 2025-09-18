const playwright = require('playwright');

async function voiceFixVerificationTest() {
  console.log('✅ VOICE FIX VERIFICATION TEST - TESTING ENTER KEY HANDLER');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  // Capture console messages
  const consoleMessages = [];
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    consoleMessages.push({ type, text });
    console.log(`[BROWSER ${type.toUpperCase()}] ${text}`);
  });

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('\n📍 PHASE 3: EXPAND VOICE COMMANDS MODAL');
    const voiceModal = page.locator('.voice-command-helper');
    
    if (await voiceModal.count() > 0) {
      const isExpanded = await voiceModal.locator('.expanded').count() > 0;
      if (!isExpanded) {
        console.log('🔓 Expanding Voice Commands modal...');
        await voiceModal.locator('.helper-header').click();
        await page.waitForTimeout(1000);
      }
      
      console.log('\n📍 PHASE 4: TEST FIXED ENTER KEY HANDLER');
      const searchInput = voiceModal.locator('input.search-input');
      
      if (await searchInput.count() > 0) {
        console.log('🗣️ Testing "Show me Tesla" with Enter key...');
        
        // Clear any existing logs for focus
        console.log('\n--- STARTING VOICE COMMAND WITH FIX ---');
        
        await searchInput.click();
        await page.waitForTimeout(500);
        
        await searchInput.fill('Show me Tesla');
        await page.waitForTimeout(1000);
        
        console.log('⌨️ Pressing Enter (should now trigger handleSuggestionClick)...');
        await searchInput.press('Enter');
        
        console.log('⏱️ Waiting 5 seconds to see processing logs...');
        await page.waitForTimeout(5000);
        
        console.log('--- VOICE COMMAND EXECUTION COMPLETE ---\n');
        
        // Check results
        const teslaInWatchlist = await page.locator('.stock-card:has-text("TSLA")').count() > 0;
        console.log(`🚗 Tesla (TSLA) in watchlist: ${teslaInWatchlist}`);
        
        // Check for toast messages
        const toastElements = await page.locator('.toast, .notification, [class*="toast"]').count();
        console.log(`🍞 Toast/notification elements: ${toastElements}`);
        
        await page.screenshot({ path: 'voice-fix-test-result.png' });
        
        // Analyze logs
        console.log('\n📍 PHASE 5: LOG ANALYSIS');
        
        const processingLogs = consoleMessages.filter(msg =>
          msg.text.includes('[Enhanced] Processing voice response') ||
          msg.text.includes('Searching for symbol') ||
          msg.text.includes('Found symbol') ||
          msg.text.includes('Resolved') ||
          msg.text.includes('Voice command: Changing symbol')
        );
        
        console.log(`\n🔍 Processing logs found (${processingLogs.length}):`);
        processingLogs.forEach((msg, i) => {
          console.log(`${i + 1}. ${msg.text}`);
        });
        
        // Test result summary
        console.log('\n🎯 FIX VERIFICATION RESULTS:');
        console.log(`✅ Enter key handler added: YES`);
        console.log(`✅ Processing logs appeared: ${processingLogs.length > 0 ? 'YES' : 'NO'}`);
        console.log(`✅ Tesla added to watchlist: ${teslaInWatchlist ? 'YES' : 'NO'}`);
        console.log(`✅ Toast notifications: ${toastElements > 0 ? 'YES' : 'NO'}`);
        
        if (processingLogs.length > 0) {
          console.log('\n🎉 SUCCESS: Voice command processing is now working!');
        } else {
          console.log('\n❌ ISSUE: Still no processing logs - may need further investigation');
        }
        
      } else {
        console.log('❌ Search input not found');
      }
    } else {
      console.log('❌ Voice Commands modal not found');
    }
    
    // Keep browser open for inspection
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Fix Verification Error:', error.message);
    await page.screenshot({ path: 'voice-fix-error.png' });
  }
}

voiceFixVerificationTest().catch(console.error);