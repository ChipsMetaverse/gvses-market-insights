const { chromium } = require('playwright');

async function testAgentToolsWorking() {
  console.log('\n🛠️ === TESTING AGENT TOOLS FUNCTIONALITY ===\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream']
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Track tool-related console messages
  let toolCallsDetected = 0;
  let sessionUpdatedWithTools = false;
  
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('Tool') || text.includes('tool')) {
      console.log(`[Tool Activity]: ${text}`);
      if (text.includes('Tool called') || text.includes('Tool completed')) {
        toolCallsDetected++;
      }
    }
    if (text.includes('session.updated')) {
      console.log(`[Session]: ${text}`);
      sessionUpdatedWithTools = true;
    }
    if (text.includes('function_call')) {
      console.log(`[Function Call]: ${text}`);
      toolCallsDetected++;
    }
  });
  
  try {
    console.log('1️⃣ Navigating to app...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    console.log('2️⃣ Selecting OpenAI provider...');
    const openaiProvider = page.locator('text=/OpenAI Realtime/i').first();
    await openaiProvider.click();
    await page.waitForTimeout(1000);
    
    console.log('3️⃣ Connecting voice assistant...');
    await page.click('button:has-text("Connect Voice Assistant")');
    await page.waitForTimeout(3000);
    
    // Verify connection
    const statusText = await page.locator('.connection-status, [class*="status"]').first().textContent();
    console.log(`   Connection status: ${statusText}`);
    
    // Switch to text mode for reliable testing
    console.log('\n4️⃣ Switching to text mode...');
    const textModeButton = page.locator('button:has-text("Text Mode")');
    if (await textModeButton.isVisible()) {
      await textModeButton.click();
      await page.waitForTimeout(1000);
      console.log('   ✅ Switched to text mode');
    }
    
    // Find the input field
    const input = page.locator('input[type="text"]').first();
    if (!await input.isVisible()) {
      console.log('   ❌ No text input visible');
      return;
    }
    
    console.log('\n5️⃣ Testing market data queries...');
    
    // Test 1: Stock price query
    console.log('\n   📊 Test 1: Stock price query');
    await input.fill("What's Tesla's current stock price?");
    await page.keyboard.press('Enter');
    console.log('   Sent: "What\'s Tesla\'s current stock price?"');
    await page.waitForTimeout(5000);
    
    // Test 2: Market overview
    console.log('\n   📊 Test 2: Market overview');
    await input.fill("Give me a market overview");
    await page.keyboard.press('Enter');
    console.log('   Sent: "Give me a market overview"');
    await page.waitForTimeout(5000);
    
    // Test 3: Technical analysis
    console.log('\n   📊 Test 3: Technical analysis');
    await input.fill("What are the technical indicators for Apple?");
    await page.keyboard.press('Enter');
    console.log('   Sent: "What are the technical indicators for Apple?"');
    await page.waitForTimeout(5000);
    
    // Check transcript for responses
    console.log('\n6️⃣ Analyzing responses...');
    const transcript = await page.locator('.transcript-container, [class*="transcript"]').first();
    const transcriptText = await transcript.textContent();
    
    // Look for evidence of tool usage
    const hasStockData = transcriptText.includes('$') || transcriptText.includes('price') || transcriptText.includes('trading');
    const hasMarketData = transcriptText.includes('S&P') || transcriptText.includes('Dow') || transcriptText.includes('NASDAQ');
    const hasTechnicalData = transcriptText.includes('RSI') || transcriptText.includes('moving average') || transcriptText.includes('indicator');
    
    console.log('\n📊 === RESULTS ===');
    console.log(`Session updated with tools: ${sessionUpdatedWithTools ? '✅' : '❌'}`);
    console.log(`Tool calls detected: ${toolCallsDetected} ${toolCallsDetected > 0 ? '✅' : '❌'}`);
    console.log(`Stock data in responses: ${hasStockData ? '✅' : '❌'}`);
    console.log(`Market data in responses: ${hasMarketData ? '✅' : '❌'}`);
    console.log(`Technical data in responses: ${hasTechnicalData ? '✅' : '❌'}`);
    
    if (toolCallsDetected > 0) {
      console.log('\n🎉 SUCCESS! Agent is using market analysis tools!');
    } else if (hasStockData || hasMarketData) {
      console.log('\n⚠️  PARTIAL SUCCESS: Agent provided market data but tool calls not detected in console');
    } else {
      console.log('\n❌ FAILURE: Agent does not appear to have market capabilities');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'test-agent-tools-working.png', fullPage: true });
    console.log('\n📸 Screenshot saved: test-agent-tools-working.png');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    console.log('\n🏁 Test complete. Leaving browser open for inspection.');
    await page.waitForTimeout(15000);
    await browser.close();
  }
}

testAgentToolsWorking().catch(console.error);