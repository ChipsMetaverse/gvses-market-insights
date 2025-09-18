const playwright = require('playwright');

async function correctedUserFlowTest() {
  console.log('🎯 CORRECTED USER FLOW TEST - PROPER INPUT FIELDS');
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
    await page.screenshot({ path: 'corrected-test-01-initial.png' });
    console.log('✅ Application loaded');

    console.log('\n📍 PHASE 2: TEST TICKER SYMBOL ADDITION (MARKET INSIGHTS)');
    console.log('Using correct search symbols input field...');
    
    // Find the Market Insights search input (not the voice input!)
    const searchInput = page.locator('input[placeholder*="Search symbols"]');
    const searchInputExists = await searchInput.count() > 0;
    console.log(`✅ Search symbols input found: ${searchInputExists}`);
    
    if (searchInputExists) {
      // Test adding NVDA
      console.log('📊 Testing NVDA addition via Market Insights...');
      await searchInput.click();
      await searchInput.fill('NVDA');
      await page.waitForTimeout(1000);
      
      // Check Add button state
      const addButton = page.locator('button:has-text("Add")');
      const addButtonExists = await addButton.count() > 0;
      const addButtonEnabled = addButtonExists ? await addButton.isEnabled() : false;
      
      console.log(`🔘 Add button exists: ${addButtonExists}`);
      console.log(`🔘 Add button enabled: ${addButtonEnabled}`);
      
      if (addButtonEnabled) {
        await addButton.click();
        await page.waitForTimeout(2000);
        
        // Check if NVDA was added to watchlist
        const nvdaCard = await page.locator('.stock-card:has-text("NVDA")').count() > 0;
        console.log(`✅ NVDA added to watchlist: ${nvdaCard}`);
        
        await page.screenshot({ path: 'corrected-test-02-nvda-added.png' });
      } else {
        console.log(`❌ Add button not enabled for NVDA`);
      }
    } else {
      console.log('❌ Search symbols input not found');
    }

    console.log('\n📍 PHASE 3: TEST VOICE CONVERSATION (SEPARATE INPUT)');
    console.log('Switching to Voice tab and using message input...');
    
    // Navigate to voice tab
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    // Connect to OpenAI
    const connectToggle = page.locator('[data-testid="connection-toggle"]');
    const isConnected = await connectToggle.isChecked();
    
    if (!isConnected) {
      console.log('🔗 Connecting to OpenAI...');
      await connectToggle.click();
      await page.waitForTimeout(3000);
    }
    
    const finalConnected = await connectToggle.isChecked();
    console.log(`🔗 Connection status: ${finalConnected ? 'Connected' : 'Not connected'}`);
    
    if (finalConnected) {
      // Use the VOICE CONVERSATION input (not the search input!)
      const messageInput = page.locator('input[data-testid="message-input"]');
      const messageInputExists = await messageInput.count() > 0;
      console.log(`✅ Voice message input found: ${messageInputExists}`);
      
      if (messageInputExists) {
        console.log('🗣️ Testing voice command via text input...');
        
        // Send a test message
        await messageInput.click();
        await messageInput.fill('What is the current price of Tesla?');
        
        const sendButton = page.locator('button[data-testid="send-button"]');
        const sendButtonEnabled = await sendButton.isEnabled();
        console.log(`🔘 Send button enabled: ${sendButtonEnabled}`);
        
        if (sendButtonEnabled) {
          await sendButton.click();
          await page.waitForTimeout(5000);
          
          // Check for messages
          const messagesContainer = page.locator('[data-testid="messages-container"]');
          const messageCount = await messagesContainer.locator('.conversation-message-enhanced').count();
          console.log(`📬 Messages in conversation: ${messageCount}`);
          
          await page.screenshot({ path: 'corrected-test-03-voice-response.png' });
          
          if (messageCount > 0) {
            console.log('✅ Voice response received and displayed!');
          } else {
            console.log('❌ No voice response received');
          }
        }
      }
    }

    console.log('\n📍 PHASE 4: FINAL STATE VERIFICATION');
    await page.screenshot({ path: 'corrected-test-04-final-state.png' });
    
    // Summary
    console.log('\n🎯 CORRECTED TEST SUMMARY:');
    console.log('1. Market Insights: Used search symbols input for ticker addition');
    console.log('2. Voice Conversation: Used message input for voice commands');
    console.log('3. Separated the two different functionalities properly');
    
    // Keep browser open for inspection
    console.log('\n🔍 Browser left open for manual verification...');
    await new Promise(() => {}); // Keep open indefinitely
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
    await page.screenshot({ path: 'corrected-test-error.png' });
  }
}

correctedUserFlowTest().catch(console.error);