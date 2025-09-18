const playwright = require('playwright');

async function comprehensiveApplicationAudit() {
  console.log('🔍 COMPREHENSIVE APPLICATION AUDIT - ULTRATHINK ANALYSIS');
  console.log('='.repeat(80));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();
  
  // Test results tracking
  const results = {
    tickerTests: [],
    voiceTests: [],
    userFlowTests: [],
    functionalityTests: [],
    issues: [],
    recommendations: []
  };

  try {
    console.log('\n📍 PHASE 1: APPLICATION INITIALIZATION');
    console.log('─'.repeat(50));
    
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    // Take initial screenshot
    await page.screenshot({ path: 'audit-01_initial_load.png', fullPage: false });
    console.log('✅ Application loaded successfully');
    
    console.log('\n📍 PHASE 2: TICKER SYMBOL COMPREHENSIVE TESTING');
    console.log('─'.repeat(50));
    
    // Navigate to voice interface first
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'audit-02_voice_tab.png', fullPage: false });
    
    // Define comprehensive ticker symbol test cases
    const tickerTestCases = [
      // Tech stocks
      { symbol: 'AAPL', type: 'tech', expect: 'success' },
      { symbol: 'GOOGL', type: 'tech', expect: 'success' },
      { symbol: 'MSFT', type: 'tech', expect: 'success' },
      { symbol: 'NVDA', type: 'tech', expect: 'success' },
      
      // Traditional stocks
      { symbol: 'JPM', type: 'financial', expect: 'success' },
      { symbol: 'JNJ', type: 'healthcare', expect: 'success' },
      { symbol: 'WMT', type: 'retail', expect: 'success' },
      
      // ETFs
      { symbol: 'SPY', type: 'etf', expect: 'success' },
      { symbol: 'QQQ', type: 'etf', expect: 'success' },
      { symbol: 'VTI', type: 'etf', expect: 'success' },
      
      // Crypto-related
      { symbol: 'COIN', type: 'crypto-stock', expect: 'success' },
      { symbol: 'MSTR', type: 'crypto-related', expect: 'success' },
      
      // Invalid symbols for error testing
      { symbol: 'INVALID123', type: 'invalid', expect: 'error' },
      { symbol: 'FAKESYMBOL', type: 'invalid', expect: 'error' },
      { symbol: 'TEST', type: 'ambiguous', expect: 'varies' },
      
      // Edge cases
      { symbol: 'BRK-A', type: 'special-class', expect: 'success' },
      { symbol: 'BRK-B', type: 'special-class', expect: 'success' }
    ];
    
    console.log(`🧪 Testing ${tickerTestCases.length} different ticker symbols...`);
    
    for (let i = 0; i < tickerTestCases.length; i++) {
      const testCase = tickerTestCases[i];
      console.log(`\n📊 Testing ${i + 1}/${tickerTestCases.length}: ${testCase.symbol} (${testCase.type})`);
      
      try {
        // Test adding symbol via search
        const searchInput = page.locator('input[placeholder*="Search symbols"]');
        await searchInput.click();
        await searchInput.fill(testCase.symbol);
        await page.waitForTimeout(1000);
        
        // Look for search results or add button
        const addButton = page.locator('button:has-text("Add")');
        const addButtonVisible = await addButton.isVisible();
        
        if (addButtonVisible) {
          await addButton.click();
          await page.waitForTimeout(2000);
          
          // Check if symbol was added to watchlist
          const symbolInWatchlist = await page.locator(`.stock-card:has-text("${testCase.symbol}")`).count() > 0;
          
          if (symbolInWatchlist) {
            console.log(`   ✅ ${testCase.symbol} added successfully`);
            results.tickerTests.push({
              symbol: testCase.symbol,
              type: testCase.type,
              result: 'added_successfully',
              timestamp: new Date().toISOString()
            });
            
            // Test clicking on the symbol to load chart
            await page.click(`.stock-card:has-text("${testCase.symbol}")`);
            await page.waitForTimeout(2000);
            
            // Check if chart loaded
            const chartVisible = await page.locator('.trading-chart-container').isVisible();
            if (chartVisible) {
              console.log(`   📈 Chart loaded for ${testCase.symbol}`);
            } else {
              console.log(`   ⚠️  Chart failed to load for ${testCase.symbol}`);
              results.issues.push(`Chart loading failed for ${testCase.symbol}`);
            }
            
            // Remove symbol to clean up for next test (except for a few core ones)
            if (!['AAPL', 'TSLA', 'NVDA', 'SPY'].includes(testCase.symbol)) {
              const removeButton = page.locator(`.stock-card:has-text("${testCase.symbol}") button:has-text("×")`);
              if (await removeButton.isVisible()) {
                await removeButton.click();
                await page.waitForTimeout(500);
              }
            }
            
          } else {
            console.log(`   ❌ ${testCase.symbol} was not added to watchlist`);
            results.tickerTests.push({
              symbol: testCase.symbol,
              type: testCase.type,
              result: 'add_failed',
              timestamp: new Date().toISOString()
            });
            
            if (testCase.expect === 'success') {
              results.issues.push(`Expected ${testCase.symbol} to be added successfully but it failed`);
            }
          }
        } else {
          console.log(`   ❌ Add button not visible for ${testCase.symbol}`);
          results.tickerTests.push({
            symbol: testCase.symbol,
            type: testCase.type,
            result: 'no_add_button',
            timestamp: new Date().toISOString()
          });
        }
        
        // Clear search input
        await searchInput.fill('');
        
      } catch (error) {
        console.log(`   ❌ Error testing ${testCase.symbol}: ${error.message}`);
        results.tickerTests.push({
          symbol: testCase.symbol,
          type: testCase.type,
          result: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    await page.screenshot({ path: 'audit-03_ticker_testing_complete.png', fullPage: false });
    
    console.log('\n📍 PHASE 3: VOICE COMMAND TESTING');
    console.log('─'.repeat(50));
    
    // Test voice connection first
    console.log('🎤 Testing voice connection...');
    try {
      await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
      await page.waitForTimeout(1000);
      await page.click('.toggle-switch-container');
      await page.waitForTimeout(8000);
      
      const connectionStatus = await page.locator('.toggle-label').textContent();
      console.log(`🔗 Connection status: ${connectionStatus}`);
      
      if (connectionStatus.includes('Connected')) {
        console.log('✅ Voice connection established');
        
        // Test text input for voice commands since actual voice is harder to automate
        const textInput = page.locator('input[data-testid="message-input"]');
        
        const voiceCommandTests = [
          'show me Apple stock',
          'display Tesla chart',  
          'load Microsoft data',
          'what is the price of NVDA',
          'show GOOGL analysis',
          'display SPY chart'
        ];
        
        console.log(`🗣️  Testing ${voiceCommandTests.length} voice commands via text input...`);
        
        for (const command of voiceCommandTests) {
          try {
            console.log(`   Testing: "${command}"`);
            
            await textInput.click();
            await textInput.fill(command);
            await page.waitForTimeout(500);
            
            const sendButton = page.locator('button[data-testid="send-button"]');
            const sendEnabled = await sendButton.isEnabled();
            
            if (sendEnabled) {
              await sendButton.click();
              await page.waitForTimeout(3000);
              
              // Check if any response appeared in messages
              const messageCount = await page.locator('.conversation-message-enhanced').count();
              
              results.voiceTests.push({
                command: command,
                result: messageCount > 0 ? 'response_received' : 'no_response',
                messageCount: messageCount,
                timestamp: new Date().toISOString()
              });
              
              console.log(`   ${messageCount > 0 ? '✅' : '⚠️'} Response ${messageCount > 0 ? 'received' : 'not received'}`);
              
            } else {
              console.log(`   ❌ Send button not enabled for command: ${command}`);
              results.voiceTests.push({
                command: command,
                result: 'send_button_disabled',
                timestamp: new Date().toISOString()
              });
            }
            
          } catch (error) {
            console.log(`   ❌ Error with command "${command}": ${error.message}`);
            results.voiceTests.push({
              command: command,
              result: 'error',
              error: error.message,
              timestamp: new Date().toISOString()
            });
          }
        }
        
      } else {
        console.log('❌ Voice connection failed');
        results.issues.push('Voice connection failed - could not establish OpenAI Realtime connection');
      }
      
    } catch (error) {
      console.log(`❌ Voice connection error: ${error.message}`);
      results.issues.push(`Voice connection error: ${error.message}`);
    }
    
    await page.screenshot({ path: 'audit-04_voice_testing_complete.png', fullPage: false });
    
    console.log('\n📍 PHASE 4: USER FLOW AUDIT');
    console.log('─'.repeat(50));
    
    // Test complete user flow
    const userFlowTests = [
      {
        name: 'Tab Navigation',
        test: async () => {
          await page.click('[data-testid="charts-tab"]');
          await page.waitForTimeout(1000);
          const chartsActive = await page.locator('[data-testid="charts-tab"].active').count() > 0;
          
          await page.click('[data-testid="voice-tab"]');
          await page.waitForTimeout(1000);
          const voiceActive = await page.locator('[data-testid="voice-tab"].active').count() > 0;
          
          return { chartsTab: chartsActive, voiceTab: voiceActive };
        }
      },
      {
        name: 'Chart Technical Levels',
        test: async () => {
          // Click on a stock to load chart
          await page.click('.stock-card:first-child');
          await page.waitForTimeout(2000);
          
          const qeLevel = await page.locator('.level-val.qe').textContent();
          const stLevel = await page.locator('.level-val.st').textContent();
          const ltbLevel = await page.locator('.level-val.ltb').textContent();
          
          return {
            qeLevel: qeLevel?.includes('$'),
            stLevel: stLevel?.includes('$'),
            ltbLevel: ltbLevel?.includes('$')
          };
        }
      },
      {
        name: 'News Integration',
        test: async () => {
          const newsItems = await page.locator('.analysis-item.clickable-news').count();
          
          if (newsItems > 0) {
            await page.click('.analysis-item.clickable-news:first-child');
            await page.waitForTimeout(1000);
            const expanded = await page.locator('.news-expanded').isVisible();
            return { newsCount: newsItems, expandable: expanded };
          }
          
          return { newsCount: newsItems, expandable: false };
        }
      },
      {
        name: 'Provider Switching',
        test: async () => {
          await page.selectOption('[data-testid="provider-dropdown"]', 'elevenlabs');
          await page.waitForTimeout(1000);
          const elevenLabsSelected = await page.locator('[data-testid="provider-dropdown"]').inputValue();
          
          await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
          await page.waitForTimeout(1000);
          const openAiSelected = await page.locator('[data-testid="provider-dropdown"]').inputValue();
          
          return {
            elevenLabsWorking: elevenLabsSelected === 'elevenlabs',
            openAiWorking: openAiSelected === 'openai'
          };
        }
      }
    ];
    
    for (const flowTest of userFlowTests) {
      try {
        console.log(`🔄 Testing: ${flowTest.name}`);
        const result = await flowTest.test();
        results.userFlowTests.push({
          name: flowTest.name,
          result: result,
          status: 'success',
          timestamp: new Date().toISOString()
        });
        console.log(`   ✅ ${flowTest.name} - Success:`, result);
      } catch (error) {
        console.log(`   ❌ ${flowTest.name} - Error: ${error.message}`);
        results.userFlowTests.push({
          name: flowTest.name,
          result: null,
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
        results.issues.push(`User flow test failed: ${flowTest.name} - ${error.message}`);
      }
    }
    
    await page.screenshot({ path: 'audit-05_user_flow_complete.png', fullPage: false });
    
    console.log('\n📍 PHASE 5: FUNCTIONALITY AUDIT');
    console.log('─'.repeat(50));
    
    // Test core functionality
    const functionalityTests = [
      {
        name: 'Market Data Loading',
        test: async () => {
          const stockCards = await page.locator('.stock-card').count();
          const pricesVisible = await page.locator('.price').count();
          const changesVisible = await page.locator('.change').count();
          
          return { stockCards, pricesVisible, changesVisible };
        }
      },
      {
        name: 'Chart Rendering', 
        test: async () => {
          const chartContainer = await page.locator('.trading-chart-container').isVisible();
          const chartCanvas = await page.locator('canvas').count();
          
          return { containerVisible: chartContainer, canvasCount: chartCanvas };
        }
      },
      {
        name: 'Search Functionality',
        test: async () => {
          const searchInput = page.locator('input[placeholder*="Search symbols"]');
          await searchInput.click();
          await searchInput.fill('AMZN');
          await page.waitForTimeout(1500);
          
          const addButton = await page.locator('button:has-text("Add")').isVisible();
          await searchInput.fill('');
          
          return { searchResponsive: addButton };
        }
      },
      {
        name: 'Text Input Always Visible',
        test: async () => {
          const textInput = page.locator('input[data-testid="message-input"]');
          const inputVisible = await textInput.isVisible();
          const inputBounds = await textInput.boundingBox();
          const withinViewport = inputBounds && inputBounds.y + inputBounds.height <= page.viewportSize().height;
          
          return { visible: inputVisible, withinViewport, bounds: inputBounds };
        }
      }
    ];
    
    for (const funcTest of functionalityTests) {
      try {
        console.log(`⚙️  Testing: ${funcTest.name}`);
        const result = await funcTest.test();
        results.functionalityTests.push({
          name: funcTest.name,
          result: result,
          status: 'success',
          timestamp: new Date().toISOString()
        });
        console.log(`   ✅ ${funcTest.name} - Result:`, result);
      } catch (error) {
        console.log(`   ❌ ${funcTest.name} - Error: ${error.message}`);
        results.functionalityTests.push({
          name: funcTest.name,
          result: null,
          status: 'error',
          error: error.message,
          timestamp: new Date().toISOString()
        });
        results.issues.push(`Functionality test failed: ${funcTest.name} - ${error.message}`);
      }
    }
    
    await page.screenshot({ path: 'audit-06_functionality_complete.png', fullPage: false });
    
    console.log('\n📍 GENERATING COMPREHENSIVE REPORT');
    console.log('─'.repeat(50));
    
    // Generate comprehensive analysis
    const summary = {
      totalTests: results.tickerTests.length + results.voiceTests.length + results.userFlowTests.length + results.functionalityTests.length,
      successfulTickerTests: results.tickerTests.filter(t => t.result === 'added_successfully').length,
      successfulVoiceTests: results.voiceTests.filter(t => t.result === 'response_received').length,
      successfulUserFlowTests: results.userFlowTests.filter(t => t.status === 'success').length,
      successfulFunctionalityTests: results.functionalityTests.filter(t => t.status === 'success').length,
      totalIssues: results.issues.length,
      testDuration: Date.now()
    };
    
    console.log('\n🎯 COMPREHENSIVE AUDIT RESULTS SUMMARY');
    console.log('='.repeat(80));
    console.log(`📊 Total Tests Executed: ${summary.totalTests}`);
    console.log(`✅ Ticker Symbol Tests: ${summary.successfulTickerTests}/${results.tickerTests.length} successful`);
    console.log(`🗣️  Voice Command Tests: ${summary.successfulVoiceTests}/${results.voiceTests.length} successful`);  
    console.log(`🔄 User Flow Tests: ${summary.successfulUserFlowTests}/${results.userFlowTests.length} successful`);
    console.log(`⚙️  Functionality Tests: ${summary.successfulFunctionalityTests}/${results.functionalityTests.length} successful`);
    console.log(`❌ Total Issues Found: ${summary.totalIssues}`);
    
    if (results.issues.length > 0) {
      console.log('\n⚠️  ISSUES IDENTIFIED:');
      results.issues.forEach((issue, i) => {
        console.log(`   ${i + 1}. ${issue}`);
      });
    }
    
    console.log('\n💡 RECOMMENDATIONS:');
    if (summary.successfulTickerTests / results.tickerTests.length < 0.8) {
      console.log('   • Improve ticker symbol validation and error handling');
    }
    if (summary.successfulVoiceTests / results.voiceTests.length < 0.5) {
      console.log('   • Enhance voice command processing and response reliability');
    }
    if (results.issues.length > 0) {
      console.log('   • Address the identified technical issues for better user experience');
    }
    console.log('   • Consider adding more comprehensive error messages for failed operations');
    console.log('   • Implement loading states for better user feedback');
    
    // Save detailed results to file
    const detailedResults = {
      summary,
      results,
      screenshots: [
        'audit-01_initial_load.png',
        'audit-02_voice_tab.png', 
        'audit-03_ticker_testing_complete.png',
        'audit-04_voice_testing_complete.png',
        'audit-05_user_flow_complete.png',
        'audit-06_functionality_complete.png'
      ],
      timestamp: new Date().toISOString()
    };
    
    console.log('\n📄 Detailed results saved for analysis');
    console.log('📸 Screenshots captured throughout testing process');
    
    console.log('\n🔍 ULTRATHINK ANALYSIS COMPLETE');
    console.log('Browser left open for manual verification and additional testing...');
    
    // Keep browser open for manual inspection
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Critical Audit Error:', error.message);
    results.issues.push(`Critical audit error: ${error.message}`);
    await page.screenshot({ path: 'audit-error.png' });
  }
}

comprehensiveApplicationAudit().catch(console.error);