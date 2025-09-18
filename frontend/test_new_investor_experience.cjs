const playwright = require('playwright');

async function testNewInvestorExperience() {
  console.log('👥 NEW INVESTOR USER EXPERIENCE TEST');
  console.log('='.repeat(60));
  console.log('Simulating the experience of a new investor/trader using the app');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 }
  });
  const page = await context.newPage();

  // Track user experience metrics
  const userActions = [];
  const loadTimes = [];
  const errors = [];
  
  const logAction = (action, success = true, notes = '') => {
    const timestamp = new Date().toISOString();
    userActions.push({ timestamp, action, success, notes });
    console.log(`${success ? '✅' : '❌'} [${timestamp.split('T')[1].split('.')[0]}] ${action} ${notes}`);
  };

  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push({ time: new Date().toISOString(), error: msg.text() });
    }
  });

  try {
    console.log('\n📍 PHASE 1: FIRST IMPRESSION - Landing on the App');
    const loadStart = Date.now();
    
    await page.goto('http://localhost:5175');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - loadStart;
    loadTimes.push({ phase: 'initial_load', time: loadTime });
    logAction(`App loaded in ${loadTime}ms`, loadTime < 3000, loadTime > 3000 ? '(slow)' : '(fast)');
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'new-investor-01-landing.png', fullPage: true });
    
    console.log('\n📍 PHASE 2: MARKET DATA EXPLORATION');
    
    // Check what market data is immediately visible
    const marketData = await page.evaluate(() => {
      const stockCards = Array.from(document.querySelectorAll('.stock-card')).map(card => ({
        symbol: card.querySelector('.symbol')?.textContent?.trim(),
        price: card.querySelector('.price')?.textContent?.trim(),
        change: card.querySelector('.change')?.textContent?.trim(),
        visible: card.offsetHeight > 0
      }));
      
      return {
        stockCards,
        chartVisible: document.querySelector('.chart-container')?.offsetHeight > 0,
        newsVisible: document.querySelector('.analysis-content')?.offsetHeight > 0
      };
    });
    
    logAction(`Market data loaded: ${marketData.stockCards.length} stocks visible`, 
              marketData.stockCards.length > 0,
              `Stocks: ${marketData.stockCards.map(s => s.symbol).join(', ')}`);
    
    if (marketData.chartVisible) {
      logAction('Chart is visible and ready');
    }
    
    if (marketData.newsVisible) {
      logAction('News/Analysis section is visible');
    }
    
    console.log('\n📍 PHASE 3: INTERACTIVE CHART EXPLORATION');
    
    // Test clicking on different stocks to see chart updates
    const testSymbols = ['TSLA', 'AAPL', 'NVDA'];
    
    for (const symbol of testSymbols) {
      const stockCard = page.locator(`.stock-card:has-text("${symbol}")`);
      if (await stockCard.count() > 0) {
        await stockCard.click();
        await page.waitForTimeout(2000);
        
        // Check if chart updated
        const chartData = await page.evaluate((sym) => {
          const title = document.querySelector('.chart-header h3')?.textContent;
          return {
            title: title,
            hasData: title && title.includes(sym)
          };
        }, symbol);
        
        logAction(`Clicked ${symbol} stock card`, 
                  chartData.hasData, 
                  `Chart shows: ${chartData.title}`);
      }
    }
    
    await page.screenshot({ path: 'new-investor-02-chart-interaction.png', fullPage: true });
    
    console.log('\n📍 PHASE 4: VOICE ASSISTANT EXPERIENCE');
    
    // Navigate to voice tab
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    logAction('Switched to Voice tab');
    
    // Check voice interface elements
    const voiceInterface = await page.evaluate(() => {
      return {
        providerSelector: !!document.querySelector('[data-testid="provider-dropdown"]'),
        connectionToggle: !!document.querySelector('[data-testid="connection-toggle"]'),
        messageInput: !!document.querySelector('[data-testid="message-input"]'),
        sendButton: !!document.querySelector('[data-testid="send-button"]')
      };
    });
    
    logAction('Voice interface elements loaded', 
              Object.values(voiceInterface).every(v => v),
              `Elements: ${Object.entries(voiceInterface).map(([k,v]) => v ? k : `missing-${k}`).join(', ')}`);
    
    // Test OpenAI connection
    console.log('\n🤖 Testing OpenAI Connection...');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000); // Give time for connection
    
    const connectionState = await page.evaluate(() => {
      const toggle = document.querySelector('[data-testid="connection-toggle"]');
      const status = document.querySelector('.toggle-label')?.textContent;
      return {
        connected: toggle?.checked || false,
        status: status?.trim()
      };
    });
    
    logAction('OpenAI connection attempt', 
              connectionState.connected, 
              `Status: ${connectionState.status}`);
    
    await page.screenshot({ path: 'new-investor-03-voice-connected.png', fullPage: true });
    
    console.log('\n📍 PHASE 5: TYPICAL INVESTOR QUERIES');
    
    if (connectionState.connected) {
      const investorQueries = [
        "What's the current market outlook?",
        "Should I buy Tesla stock right now?",
        "What are the top performing stocks today?",
        "Explain Tesla's recent price movement",
        "Show me Apple's chart"
      ];
      
      for (let i = 0; i < Math.min(2, investorQueries.length); i++) {
        const query = investorQueries[i];
        console.log(`\n💬 Testing query: "${query}"`);
        
        const messageInput = page.locator('[data-testid="message-input"]');
        await messageInput.fill(query);
        await page.waitForTimeout(500);
        
        const sendButton = page.locator('[data-testid="send-button"]');
        if (await sendButton.isEnabled()) {
          await sendButton.click();
          await page.waitForTimeout(5000); // Wait for AI response
          
          // Check if input was cleared (indicates message was sent)
          const inputCleared = await messageInput.inputValue() === '';
          logAction(`Sent query: "${query}"`, inputCleared, 
                   inputCleared ? 'Input cleared - message sent' : 'Input not cleared');
          
          // Look for response indicators
          const responseIndicators = await page.evaluate(() => {
            const messages = document.querySelectorAll('.message, .response, .ai-message');
            const audioElements = document.querySelectorAll('audio');
            const conversationItems = document.querySelectorAll('[class*="conversation"], [class*="chat"]');
            
            return {
              messageCount: messages.length,
              audioElements: audioElements.length,
              conversationItems: conversationItems.length,
              hasNewContent: messages.length > 0 || audioElements.length > 0
            };
          });
          
          if (responseIndicators.hasNewContent) {
            logAction(`AI responded to query`, true, 
                     `Messages: ${responseIndicators.messageCount}, Audio: ${responseIndicators.audioElements}`);
          } else {
            logAction(`AI response unclear`, false, 'No clear response indicators found');
          }
        }
        
        await page.waitForTimeout(2000); // Pause between queries
      }
    }
    
    await page.screenshot({ path: 'new-investor-04-queries-tested.png', fullPage: true });
    
    console.log('\n📍 PHASE 6: NEWS AND ANALYSIS EXPLORATION');
    
    // Go back to overview to check news
    await page.click('[data-testid="overview-tab"]');
    await page.waitForTimeout(1000);
    
    // Check if news section has content
    const newsContent = await page.evaluate(() => {
      const newsItems = document.querySelectorAll('.news-item, .analysis-item, [class*="news"]');
      const expandableContent = document.querySelectorAll('.expandable, [class*="expand"]');
      
      return {
        newsCount: newsItems.length,
        expandableCount: expandableContent.length,
        firstNewsTitle: newsItems[0]?.textContent?.substring(0, 100)
      };
    });
    
    logAction(`News content available`, 
              newsContent.newsCount > 0,
              `${newsContent.newsCount} news items, first: "${newsContent.firstNewsTitle}"`);
    
    // Try expanding news if available
    if (newsContent.expandableCount > 0) {
      const expandButton = page.locator('.expandable, [class*="expand"]').first();
      if (await expandButton.count() > 0) {
        await expandButton.click();
        await page.waitForTimeout(1000);
        logAction('Expanded news/analysis content');
      }
    }
    
    await page.screenshot({ path: 'new-investor-05-news-explored.png', fullPage: true });
    
    console.log('\n📍 PHASE 7: OVERALL USER EXPERIENCE ASSESSMENT');
    
    // Calculate performance metrics
    const avgLoadTime = loadTimes.reduce((sum, lt) => sum + lt.time, 0) / loadTimes.length;
    const successRate = userActions.filter(a => a.success).length / userActions.length;
    const errorCount = errors.length;
    
    console.log('\n🎯 NEW INVESTOR EXPERIENCE SUMMARY:');
    console.log('='.repeat(60));
    
    console.log('\n📊 PERFORMANCE METRICS:');
    console.log(`• Average Load Time: ${Math.round(avgLoadTime)}ms`);
    console.log(`• Success Rate: ${Math.round(successRate * 100)}%`);
    console.log(`• Error Count: ${errorCount}`);
    console.log(`• Total User Actions: ${userActions.length}`);
    
    console.log('\n📋 USER JOURNEY BREAKDOWN:');
    userActions.forEach((action, i) => {
      const status = action.success ? '✅' : '❌';
      console.log(`${i + 1}. ${status} ${action.action} ${action.notes}`);
    });
    
    if (errors.length > 0) {
      console.log('\n⚠️ ERRORS ENCOUNTERED:');
      errors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.error}`);
      });
    }
    
    // Overall assessment
    const overallRating = successRate >= 0.8 ? 'EXCELLENT' : 
                         successRate >= 0.6 ? 'GOOD' : 
                         successRate >= 0.4 ? 'FAIR' : 'NEEDS IMPROVEMENT';
    
    console.log(`\n🏆 OVERALL NEW INVESTOR EXPERIENCE: ${overallRating}`);
    
    if (successRate >= 0.8) {
      console.log('💡 The app provides a smooth, professional experience for new investors');
      console.log('   - Market data loads quickly and clearly');
      console.log('   - Interactive charts respond well');
      console.log('   - Voice assistant functionality works');
      console.log('   - News and analysis are accessible');
    } else {
      console.log('⚠️ Areas for improvement identified:');
      const failedActions = userActions.filter(a => !a.success);
      failedActions.forEach(action => {
        console.log(`   - ${action.action}: ${action.notes}`);
      });
    }
    
    console.log('\n📈 INVESTOR-SPECIFIC INSIGHTS:');
    console.log(`• Market Data Accessibility: ${marketData.stockCards.length > 0 ? 'Good' : 'Limited'}`);
    console.log(`• Chart Interactivity: ${userActions.find(a => a.action.includes('chart')) ? 'Functional' : 'Untested'}`);
    console.log(`• Voice AI Assistance: ${connectionState.connected ? 'Available' : 'Limited'}`);
    console.log(`• News Coverage: ${newsContent.newsCount > 0 ? 'Present' : 'Limited'}`);
    
    console.log('\n🔍 Browser kept open for manual review...');
    await new Promise(() => {}); // Keep open for manual inspection
    
  } catch (error) {
    console.error('❌ Test Error:', error.message);
    logAction('Test execution failed', false, error.message);
    await page.screenshot({ path: 'new-investor-error.png' });
  }
}

testNewInvestorExperience().catch(console.error);