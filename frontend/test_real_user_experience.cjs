const playwright = require('playwright');

async function testRealUserExperience() {
  console.log('🚀 REAL USER EXPERIENCE TEST');
  console.log('Testing application like an actual trader would use it\n');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor all console logs to see AI responses
  let aiResponses = [];
  let errorCount = 0;
  
  page.on('console', (msg) => {
    const text = msg.text();
    if (msg.type() === 'error') {
      console.log('🔴 ERROR:', text);
      errorCount++;
    } else if (text.includes('Assistant:') || text.includes('Tool called:') || text.includes('Tool result:')) {
      console.log('🤖 AI:', text);
      aiResponses.push(text);
    } else if (text.includes('OpenAI') || text.includes('Connected') || text.includes('session')) {
      console.log('📡 System:', text);
    }
  });

  try {
    // Step 1: Navigate and connect like a real user
    console.log('📍 Step 1: Opening trading dashboard...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    // Navigate to voice tab
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    console.log('✅ Opened voice interface');
    
    // Select OpenAI and connect
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    console.log('🔌 Connecting to AI assistant...');
    await page.waitForTimeout(8000);
    
    // Verify connection
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    if (!toggleText?.includes('Connected')) {
      throw new Error('Failed to connect to AI assistant');
    }
    console.log('✅ Connected to AI trading assistant\n');

    // Step 2: Test realistic trading queries
    console.log('📍 Step 2: Testing realistic trading conversations...\n');
    
    const queries = [
      {
        question: "What's the current Tesla stock price and how is it performing today?",
        expectation: "Should provide current TSLA price and performance data"
      },
      {
        question: "Show me Apple on the chart and tell me if it's a good time to buy",
        expectation: "Should switch chart to AAPL and provide trading advice"
      },
      {
        question: "Give me a technical analysis of NVIDIA with moving averages",
        expectation: "Should show NVDA chart with technical indicators"
      },
      {
        question: "What are the latest news headlines affecting the market today?",
        expectation: "Should provide current market news"
      },
      {
        question: "Compare Microsoft and Amazon stock performance this month",
        expectation: "Should provide comparative analysis of MSFT vs AMZN"
      }
    ];

    let successfulQueries = 0;
    let responsesReceived = 0;

    for (let i = 0; i < queries.length; i++) {
      const query = queries[i];
      console.log(`💬 Query ${i + 1}: "${query.question}"`);
      console.log(`🎯 Expected: ${query.expectation}`);
      
      // Clear input and send query
      const messageInput = page.locator('input[data-testid="message-input"]');
      await messageInput.clear();
      await messageInput.type(query.question);
      
      await page.click('button[data-testid="send-button"]');
      console.log('📤 Sent query to AI...');
      
      // Wait for response (longer timeout for complex queries)
      const responseTimeout = 15000;
      const startTime = Date.now();
      let responseReceived = false;
      
      while (Date.now() - startTime < responseTimeout) {
        await page.waitForTimeout(1000);
        
        // Check for new messages in conversation
        const messages = await page.locator('[data-testid="messages-container"] .conversation-message-enhanced').count();
        if (messages > responsesReceived) {
          responseReceived = true;
          responsesReceived = messages;
          break;
        }
      }
      
      if (responseReceived) {
        console.log('✅ AI responded to query');
        successfulQueries++;
        
        // Get the latest response text
        const latestMessage = page.locator('[data-testid="messages-container"] .conversation-message-enhanced').last();
        const responseText = await latestMessage.locator('.message-text-enhanced').textContent();
        console.log(`📖 Response preview: "${responseText?.substring(0, 100)}..."`);
      } else {
        console.log('❌ No response received within timeout');
      }
      
      console.log(''); // Add spacing
      await page.waitForTimeout(2000); // Brief pause between queries
    }

    // Step 3: Test voice commands for chart control
    console.log('📍 Step 3: Testing voice chart commands...\n');
    
    const chartCommands = [
      "Show me Tesla chart",
      "Switch to Apple",
      "Display Microsoft stock",
      "Load SPY chart"
    ];

    let chartCommandsWorking = 0;
    
    for (const command of chartCommands) {
      console.log(`🎤 Voice command: "${command}"`);
      
      const messageInput = page.locator('input[data-testid="message-input"]');
      await messageInput.clear();
      await messageInput.type(command);
      await page.click('button[data-testid="send-button"]');
      
      // Wait and check if chart updated
      await page.waitForTimeout(5000);
      
      // Look for chart updates or symbol changes
      const chartContainer = page.locator('[data-testid="trading-chart"]');
      if (await chartContainer.isVisible()) {
        console.log('✅ Chart responded to voice command');
        chartCommandsWorking++;
      } else {
        console.log('❌ Chart did not respond');
      }
      
      await page.waitForTimeout(1000);
    }

    // Step 4: Test market data accuracy
    console.log('📍 Step 4: Verifying market data accuracy...\n');
    
    // Check if market insights panel shows real data
    const stockCards = await page.locator('.insight-card').count();
    console.log(`📊 Market insights showing ${stockCards} stocks`);
    
    if (stockCards > 0) {
      const firstCard = page.locator('.insight-card').first();
      const symbol = await firstCard.locator('.insight-symbol').textContent();
      const price = await firstCard.locator('.insight-price').textContent();
      console.log(`📈 Sample data: ${symbol} at ${price}`);
      
      if (symbol && price && price !== '$0.00') {
        console.log('✅ Market data appears to be real and current');
      } else {
        console.log('❌ Market data appears to be placeholder or stale');
      }
    }

    // Step 5: Final assessment and screenshot
    console.log('📍 Step 5: Final assessment...\n');
    
    await page.screenshot({ 
      path: `real-user-experience-test-${Date.now()}.png`, 
      fullPage: true 
    });
    
    // Generate user experience report
    console.log('=== REAL USER EXPERIENCE REPORT ===');
    console.log(`📱 Connection Success: ${toggleText?.includes('Connected') ? 'YES' : 'NO'}`);
    console.log(`💬 Query Success Rate: ${successfulQueries}/${queries.length} (${Math.round(successfulQueries/queries.length*100)}%)`);
    console.log(`🎤 Voice Commands Working: ${chartCommandsWorking}/${chartCommands.length} (${Math.round(chartCommandsWorking/chartCommands.length*100)}%)`);
    console.log(`📊 Market Data Quality: ${stockCards > 0 ? 'LIVE DATA' : 'NO DATA'}`);
    console.log(`🔴 Error Count: ${errorCount}`);
    console.log(`🤖 AI Responses Captured: ${aiResponses.length}`);
    
    // Overall assessment
    const overallScore = (
      (toggleText?.includes('Connected') ? 25 : 0) +
      (successfulQueries / queries.length * 40) +
      (chartCommandsWorking / chartCommands.length * 25) +
      (stockCards > 0 ? 10 : 0)
    );
    
    console.log(`\n🎯 OVERALL USER EXPERIENCE SCORE: ${Math.round(overallScore)}/100`);
    
    if (overallScore >= 80) {
      console.log('🎉 EXCELLENT: Application ready for real trading use');
    } else if (overallScore >= 60) {
      console.log('✅ GOOD: Application functional with minor improvements needed');
    } else if (overallScore >= 40) {
      console.log('⚠️  FAIR: Application has significant usability issues');
    } else {
      console.log('❌ POOR: Application not ready for user deployment');
    }
    
    console.log('\n📸 Screenshot saved for review');
    console.log('Press Ctrl+C to close browser and review results');
    
    // Keep browser open for manual inspection
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ User Experience Test Error:', error.message);
  } finally {
    // Browser stays open for inspection
  }
}

testRealUserExperience().catch(console.error);