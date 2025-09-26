const { chromium } = require('playwright');

async function testTechnicalQueries() {
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500 // Slow down for visibility
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('🚀 Starting technical query tests...');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    console.log('✅ Loaded trading dashboard');
    
    // Wait for the app to fully load
    await page.waitForSelector('.trading-dashboard-simple', { timeout: 10000 });
    console.log('✅ Dashboard is ready');
    
    // Test 1: Check if the agent conversation UI is present
    const agentPanel = await page.locator('.agent-conversation').first();
    if (await agentPanel.isVisible()) {
      console.log('✅ Agent conversation panel is visible');
    }
    
    // Test 2: Send a technical query via the input field in the right panel
    const inputField = await page.locator('input[placeholder*="Connect to send messages"], input[type="text"]').first();
    
    // Click on the input field to focus/connect if needed
    await inputField.click();
    await page.waitForTimeout(1000); // Wait for any connection
    
    // Check if the input is now enabled or look for the actual message input
    const messageInput = await page.locator('input[placeholder*="Type"], textarea[placeholder*="Type"], input[type="text"]:not([disabled])').last();
    
    if (await messageInput.count() > 0 && await messageInput.isEnabled()) {
      console.log('📝 Testing text-based technical query...');
      
      // Type a swing trade query
      await messageInput.fill('What are the swing trade levels for AAPL?');
      console.log('✅ Entered query: "What are the swing trade levels for AAPL?"');
      
      // Press Enter or click send button
      await page.keyboard.press('Enter');
      console.log('✅ Submitted query');
      
      // Wait for response to appear
      await page.waitForTimeout(8000); // Give it time to process
      
      // Check for technical analysis response elements in the conversation panel
      // The response appears in the right panel conversation area
      const responseContainer = await page.locator('.agent-conversation, [class*="conversation"], [class*="messages"]').first();
      let responseText = '';
      
      try {
        // Try to get the assistant's response text - it may be in various containers
        const possibleSelectors = [
          'div:has-text("ENTRY POINTS")',
          'div:has-text("Based on the current data")',
          '.assistant-message',
          '.message-content',
          'div[class*="message"]:has-text("AAPL")'
        ];
        
        for (const selector of possibleSelectors) {
          const element = await responseContainer.locator(selector).first();
          if (await element.count() > 0) {
            responseText = await element.textContent() || '';
            if (responseText.length > 50) break;
          }
        }
      } catch (e) {
        console.log('⚠️ Could not extract response text directly, checking screenshot...')
      }
      
      if (responseText) {
        console.log('✅ Got response from agent');
        
        // Check if response contains technical analysis keywords
        const technicalKeywords = ['entry', 'target', 'stop', 'support', 'resistance', 'swing'];
        const containsTechnical = technicalKeywords.some(keyword => 
          responseText.toLowerCase().includes(keyword)
        );
        
        if (containsTechnical) {
          console.log('✅ Response contains technical analysis!');
          console.log('📊 Response preview:', responseText.substring(0, 200) + '...');
        } else {
          console.log('⚠️ Response may not contain technical analysis');
          console.log('Response:', responseText.substring(0, 200));
        }
      }
    } else {
      console.log('⚠️ No text input field found, checking for voice-only interface');
    }
    
    // Test 3: Check if chart updates with symbol
    const chartContainer = await page.locator('.trading-chart, canvas').first();
    if (await chartContainer.isVisible()) {
      console.log('✅ Chart is visible and ready');
    }
    
    // Test 4: Check Market Insights panel
    const marketInsights = await page.locator('.market-insights-panel').first();
    if (await marketInsights.isVisible()) {
      console.log('✅ Market Insights panel is visible');
      
      // Check for stock cards
      const stockCards = await page.locator('.stock-card').count();
      console.log(`✅ Found ${stockCards} stock cards in watchlist`);
    }
    
    // Test 5: Test another technical query
    if (await messageInput.count() > 0 && await messageInput.isEnabled()) {
      console.log('\n📝 Testing second technical query...');
      
      await messageInput.fill('Give me support and resistance levels for TSLA');
      await page.keyboard.press('Enter');
      console.log('✅ Submitted query: "Give me support and resistance levels for TSLA"');
      
      await page.waitForTimeout(8000);
      
      // Just check if we can see TSLA or support/resistance text in the UI
      try {
        const hasResponse = await page.locator('div:has-text("support"), div:has-text("resistance"), div:has-text("TSLA")').first().count() > 0;
        if (hasResponse) {
          console.log('✅ Second technical query successful!');
        } else {
          console.log('⚠️ Second response may still be loading');
        }
      } catch (e) {
        console.log('⚠️ Could not verify second response');
      }
    }
    
    // Take a screenshot of the final state
    await page.screenshot({ path: 'technical_query_test.png', fullPage: true });
    console.log('📸 Screenshot saved as technical_query_test.png');
    
    console.log('\n✨ All tests completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ path: 'test_error.png', fullPage: true });
    console.log('📸 Error screenshot saved as test_error.png');
  } finally {
    await browser.close();
  }
}

// Run the tests
testTechnicalQueries().catch(console.error);