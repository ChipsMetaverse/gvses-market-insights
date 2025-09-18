const playwright = require('playwright');

async function voiceCommandsModalTest() {
  console.log('🎤 VOICE COMMANDS MODAL TEST - CORRECT INTERFACE');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('\n📍 PHASE 1: LOAD APPLICATION');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'voice-modal-01-initial.png' });
    console.log('✅ Application loaded');

    console.log('\n📍 PHASE 2: NAVIGATE TO VOICE TAB');
    // Navigate to voice tab to make Voice Commands modal visible
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'voice-modal-02-voice-tab.png' });
    console.log('✅ Voice tab activated');

    console.log('\n📍 PHASE 3: LOCATE VOICE COMMANDS MODAL');
    // Look for the Voice Commands modal
    const voiceCommandsModal = page.locator('.voice-command-helper');
    const modalExists = await voiceCommandsModal.count() > 0;
    console.log(`🎤 Voice Commands modal found: ${modalExists}`);
    
    if (modalExists) {
      // Check if modal is expanded or collapsed
      const isExpanded = await voiceCommandsModal.locator('.expanded').count() > 0;
      console.log(`📋 Modal expanded: ${isExpanded}`);
      
      // If collapsed, expand it
      if (!isExpanded) {
        console.log('🔓 Expanding Voice Commands modal...');
        await voiceCommandsModal.locator('.helper-header').click();
        await page.waitForTimeout(1000);
      }
      
      await page.screenshot({ path: 'voice-modal-03-expanded.png' });
      
      console.log('\n📍 PHASE 4: LOCATE VOICE COMMANDS SEARCH INPUT');
      // Look for the search input within the modal
      const searchInput = voiceCommandsModal.locator('input.search-input');
      const searchInputExists = await searchInput.count() > 0;
      console.log(`🔍 Voice Commands search input found: ${searchInputExists}`);
      
      if (searchInputExists) {
        const placeholder = await searchInput.getAttribute('placeholder');
        console.log(`📝 Input placeholder: "${placeholder}"`);
        
        console.log('\n📍 PHASE 5: TEST VOICE COMMANDS');
        
        // Test 1: Stock symbol command
        console.log('📊 Testing stock symbol command: "Show me Tesla"');
        await searchInput.click();
        await searchInput.fill('Show me Tesla');
        await page.waitForTimeout(1000);
        
        // Check for suggestions
        const suggestions = voiceCommandsModal.locator('.suggestions-dropdown .suggestion-item');
        const suggestionsCount = await suggestions.count();
        console.log(`💡 Suggestions displayed: ${suggestionsCount}`);
        
        if (suggestionsCount > 0) {
          // Click first suggestion
          await suggestions.first().click();
          await page.waitForTimeout(2000);
          console.log('✅ Clicked first suggestion');
        } else {
          // If no suggestions, try pressing Enter
          await searchInput.press('Enter');
          await page.waitForTimeout(2000);
          console.log('⌨️ Pressed Enter to execute command');
        }
        
        await page.screenshot({ path: 'voice-modal-04-tesla-command.png' });
        
        // Check if chart changed to Tesla
        const chartTitle = await page.locator('.chart-header, .chart-title, .trading-chart').textContent();
        console.log(`📈 Chart area content: ${chartTitle ? chartTitle.slice(0, 100) : 'No content found'}`);
        
        // Test 2: Market overview command
        console.log('\n📊 Testing market overview command: "Show market overview"');
        await searchInput.click();
        await searchInput.fill('Show market overview');
        await page.waitForTimeout(1000);
        
        const newSuggestions = await voiceCommandsModal.locator('.suggestions-dropdown .suggestion-item').count();
        console.log(`💡 New suggestions displayed: ${newSuggestions}`);
        
        if (newSuggestions > 0) {
          await voiceCommandsModal.locator('.suggestions-dropdown .suggestion-item').first().click();
        } else {
          await searchInput.press('Enter');
        }
        
        await page.waitForTimeout(2000);
        await page.screenshot({ path: 'voice-modal-05-market-overview.png' });
        
        // Test 3: Example command from the modal
        console.log('\n🎯 Testing example command from modal');
        const exampleCommands = voiceCommandsModal.locator('.example-command');
        const exampleCount = await exampleCommands.count();
        console.log(`📋 Example commands available: ${exampleCount}`);
        
        if (exampleCount > 0) {
          const firstExample = exampleCommands.first();
          const exampleText = await firstExample.textContent();
          console.log(`🎯 Clicking example: ${exampleText}`);
          await firstExample.click();
          await page.waitForTimeout(2000);
          await page.screenshot({ path: 'voice-modal-06-example-command.png' });
        }
        
        console.log('\n📍 PHASE 6: CHECK COMMAND HISTORY');
        // Check if commands appear in history
        const historyItems = voiceCommandsModal.locator('.command-history-item');
        const historyCount = await historyItems.count();
        console.log(`📜 Commands in history: ${historyCount}`);
        
        // Check context status
        const contextStatus = voiceCommandsModal.locator('.context-status .status-value');
        const contextCount = await contextStatus.count();
        if (contextCount > 0) {
          for (let i = 0; i < contextCount; i++) {
            const statusText = await contextStatus.nth(i).textContent();
            console.log(`📊 Context status ${i + 1}: ${statusText}`);
          }
        }
        
      } else {
        console.log('❌ Voice Commands search input not found in modal');
      }
    } else {
      console.log('❌ Voice Commands modal not found');
      
      // Take screenshot to see what's visible
      await page.screenshot({ path: 'voice-modal-debug-no-modal.png' });
    }

    console.log('\n📍 PHASE 7: FINAL STATE');
    await page.screenshot({ path: 'voice-modal-07-final.png' });
    
    // Summary
    console.log('\n🎤 VOICE COMMANDS MODAL TEST SUMMARY:');
    console.log('1. Tested proper Voice Commands modal interface');
    console.log('2. Used modal search input (not main conversation input)');
    console.log('3. Tested suggestions and example commands');
    console.log('4. Checked command history and context tracking');
    
    // Keep browser open for inspection
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
    await page.screenshot({ path: 'voice-modal-error.png' });
  }
}

voiceCommandsModalTest().catch(console.error);