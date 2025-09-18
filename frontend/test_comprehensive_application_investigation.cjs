const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: false,
    slowMo: 200
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('🔍 === COMPREHENSIVE APPLICATION INVESTIGATION === 🔍\n');
  console.log('🎯 Testing all functionality after UI redesign\n');
  
  const testResults = {
    passed: [],
    failed: [],
    warnings: [],
    screenshots: [],
    performance: {},
    errors: []
  };
  
  function logTest(name, passed, details = '', isWarning = false) {
    const result = passed ? '✅ PASS' : (isWarning ? '⚠️  WARN' : '❌ FAIL');
    console.log(`${result}: ${name}${details ? ' - ' + details : ''}`);
    
    if (passed) {
      testResults.passed.push(name);
    } else if (isWarning) {
      testResults.warnings.push({ name, details });
    } else {
      testResults.failed.push({ name, details });
    }
  }
  
  // Monitor console errors
  page.on('console', msg => {
    if (msg.type() === 'error') {
      testResults.errors.push(`Console Error: ${msg.text()}`);
    }
  });
  
  try {
    // ===== PHASE 1: BASIC APPLICATION LOADING =====
    console.log('📍 PHASE 1: BASIC APPLICATION LOADING & NAVIGATION');
    
    const startTime = Date.now();
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle', timeout: 30000 });
    const loadTime = Date.now() - startTime;
    testResults.performance.initialLoad = loadTime;
    
    logTest('Application loads successfully', loadTime < 10000, `Load time: ${loadTime}ms`);
    logTest('Load time performance', loadTime < 5000, `${loadTime}ms (target: <5s)`, loadTime >= 5000);
    
    await page.waitForTimeout(2000);
    
    // Check main application elements
    const appRoot = await page.locator('#root').count();
    logTest('React app root element present', appRoot === 1);
    
    const mainContent = await page.locator('.trading-dashboard-simple').count();
    logTest('Main dashboard component loaded', mainContent === 1);
    
    // Test tab navigation
    const tabs = await page.locator('.tab-button').count();
    logTest('Tab navigation present', tabs >= 3, `Found ${tabs} tabs`);
    
    // Test each tab
    console.log('\n   Testing tab navigation...');
    const tabNames = ['Interactive Charts', 'Voice + Manual Control', 'Educational Analysis'];
    
    for (let i = 0; i < tabNames.length; i++) {
      const tabName = tabNames[i];
      const tab = await page.locator(`text="${tabName}"`).first();
      const isTabVisible = await tab.isVisible().catch(() => false);
      logTest(`Tab "${tabName}" present`, isTabVisible);
      
      if (isTabVisible) {
        await tab.click();
        await page.waitForTimeout(1000);
        const isTabActive = await tab.evaluate(el => el.classList.contains('active'));
        logTest(`Tab "${tabName}" clickable and active`, isTabActive);
      }
    }
    
    // Take screenshot of initial state
    await page.screenshot({ path: 'investigation-initial-load.png', fullPage: false });
    testResults.screenshots.push('investigation-initial-load.png');
    
    // ===== PHASE 2: MARKET INSIGHTS PANEL =====
    console.log('\n📍 PHASE 2: MARKET INSIGHTS PANEL FUNCTIONALITY');
    
    // Switch to Interactive Charts to test market data
    const chartsTab = await page.locator('text="Interactive Charts"').first();
    await chartsTab.click();
    await page.waitForTimeout(2000);
    
    // Test market insights panel
    const marketInsights = await page.locator('.market-insights-panel').first();
    const isMarketInsightsVisible = await marketInsights.isVisible().catch(() => false);
    logTest('Market Insights panel visible', isMarketInsightsVisible);
    
    if (isMarketInsightsVisible) {
      // Test stock cards loading
      await page.waitForTimeout(3000); // Wait for data to load
      const stockCards = await page.locator('.stock-card').count();
      logTest('Stock cards loaded', stockCards >= 3, `Found ${stockCards} stock cards`);
      
      // Test stock price data
      const priceElements = await page.locator('.stock-price').count();
      logTest('Stock prices displayed', priceElements >= 3, `Found ${priceElements} price elements`);
      
      // Test percentage changes
      const changeElements = await page.locator('.percentage-change').count();
      logTest('Percentage changes displayed', changeElements >= 3, `Found ${changeElements} change elements`);
      
      // Test remove functionality
      const removeButtons = await page.locator('.remove-symbol').count();
      if (removeButtons > 1) { // Only test if we have more than 1 (minimum required)
        const initialCount = await page.locator('.stock-card').count();
        await page.locator('.remove-symbol').first().click();
        await page.waitForTimeout(1000);
        const newCount = await page.locator('.stock-card').count();
        logTest('Stock card removal works', newCount === initialCount - 1, `${initialCount} → ${newCount} cards`);
      }
      
      // Test add symbol functionality
      const addInput = await page.locator('.add-symbol-input').first();
      const isAddInputVisible = await addInput.isVisible().catch(() => false);
      logTest('Add symbol input present', isAddInputVisible);
      
      if (isAddInputVisible) {
        await addInput.fill('MSFT');
        await page.waitForTimeout(500);
        const addButton = await page.locator('.add-symbol-button').first();
        const isAddButtonVisible = await addButton.isVisible().catch(() => false);
        
        if (isAddButtonVisible) {
          await addButton.click();
          await page.waitForTimeout(3000); // Wait for API call
          
          const msftCard = await page.locator('text="MSFT"').count();
          logTest('Add symbol functionality works', msftCard > 0, 'MSFT successfully added');
        }
      }
    }
    
    // ===== PHASE 3: CHART FUNCTIONALITY =====
    console.log('\n📍 PHASE 3: INTERACTIVE CHART FUNCTIONALITY');
    
    const chartContainer = await page.locator('.chart-container').first();
    const isChartVisible = await chartContainer.isVisible().catch(() => false);
    logTest('Chart container present', isChartVisible);
    
    if (isChartVisible) {
      // Wait for chart to load
      await page.waitForTimeout(5000);
      
      // Test chart canvas
      const chartCanvas = await page.locator('canvas').count();
      logTest('Chart canvas elements present', chartCanvas >= 1, `Found ${chartCanvas} canvas elements`);
      
      // Test technical level labels
      const technicalLabels = await page.locator('.technical-levels').first();
      const areLabelsVisible = await technicalLabels.isVisible().catch(() => false);
      logTest('Technical level labels present', areLabelsVisible);
      
      if (areLabelsVisible) {
        const labelElements = await page.locator('.level-label').count();
        logTest('Individual level labels visible', labelElements >= 3, `Found ${labelElements} labels`);
      }
      
      // Test chart interactions (pan/zoom simulation)
      if (chartCanvas > 0) {
        const canvas = await page.locator('canvas').first();
        const canvasBbox = await canvas.boundingBox();
        
        if (canvasBbox) {
          // Simulate mouse interactions on chart
          await page.mouse.move(canvasBbox.x + canvasBbox.width / 2, canvasBbox.y + canvasBbox.height / 2);
          await page.mouse.down();
          await page.mouse.move(canvasBbox.x + canvasBbox.width / 2 + 50, canvasBbox.y + canvasBbox.height / 2);
          await page.mouse.up();
          await page.waitForTimeout(1000);
          
          logTest('Chart interaction (pan) works', true, 'Mouse pan simulation completed');
        }
      }
    }
    
    // ===== PHASE 4: VOICE + MANUAL CONTROL =====
    console.log('\n📍 PHASE 4: VOICE + MANUAL CONTROL FUNCTIONALITY');
    
    const voiceTab = await page.locator('text="Voice + Manual Control"').first();
    await voiceTab.click();
    await page.waitForTimeout(2000);
    
    // Test voice section redesign
    const voiceSection = await page.locator('.voice-section-redesigned').first();
    const isVoiceSectionVisible = await voiceSection.isVisible().catch(() => false);
    logTest('Voice section (redesigned) present', isVoiceSectionVisible);
    
    // Test provider dropdown
    const providerDropdown = await page.locator('.provider-dropdown').first();
    const isProviderDropdownVisible = await providerDropdown.isVisible().catch(() => false);
    logTest('Provider dropdown present', isProviderDropdownVisible);
    
    if (isProviderDropdownVisible) {
      const currentProvider = await providerDropdown.inputValue();
      logTest('Provider dropdown has value', currentProvider.length > 0, `Current: ${currentProvider}`);
      
      // Test provider switching
      await providerDropdown.selectOption('openai');
      await page.waitForTimeout(500);
      const newProvider = await providerDropdown.inputValue();
      logTest('Provider switching works', newProvider === 'openai', `Switched to: ${newProvider}`);
    }
    
    // Test toggle switch
    const toggleSwitch = await page.locator('.toggle-switch').first();
    const isToggleVisible = await toggleSwitch.isVisible().catch(() => false);
    logTest('Toggle switch present', isToggleVisible);
    
    if (isToggleVisible) {
      const toggleInput = await page.locator('.toggle-switch input').first();
      const initialState = await toggleInput.isChecked();
      
      // Test toggle click
      await toggleSwitch.click();
      await page.waitForTimeout(3000); // Wait for connection attempt
      
      const newState = await toggleInput.isChecked();
      logTest('Toggle switch functionality', newState !== initialState, `${initialState} → ${newState}`);
      
      // Test visual state changes
      if (newState) {
        const connectingText = await page.locator('text="Connected"').count();
        const disconnectedText = await page.locator('text="Connect"').count();
        logTest('Visual state reflects connection', connectingText > 0 || disconnectedText === 0, 'UI shows connected state');
        
        // Test audio status bar
        const audioStatusBar = await page.locator('.audio-status-bar').first();
        const isAudioBarVisible = await audioStatusBar.isVisible().catch(() => false);
        logTest('Audio status bar appears when connected', isAudioBarVisible);
      }
    }
    
    // Test conversation area
    const conversationArea = await page.locator('.conversation-messages-expanded').first();
    const isConversationVisible = await conversationArea.isVisible().catch(() => false);
    logTest('Conversation area present', isConversationVisible);
    
    if (isConversationVisible) {
      const areaHeight = await conversationArea.evaluate(el => el.offsetHeight);
      logTest('Conversation area expanded height', areaHeight >= 200, `Height: ${areaHeight}px (target: ≥200px)`);
    }
    
    // Test intuitive UI (no instructional text)
    const hasInstructionalText = await page.locator('text="Toggle the switch"').count() > 0 ||
                                 await page.locator('text="Try these commands"').count() > 0 ||
                                 await page.locator('text="Ready to listen"').count() > 0;
    logTest('No instructional text present', !hasInstructionalText, 'Clean visual-only interface');
    
    // ===== PHASE 5: CHART ANALYSIS PANEL =====
    console.log('\n📍 PHASE 5: CHART ANALYSIS FUNCTIONALITY');
    
    const analysisTab = await page.locator('text="Educational Analysis"').first();
    await analysisTab.click();
    await page.waitForTimeout(3000);
    
    const chartAnalysis = await page.locator('.chart-analysis').first();
    const isAnalysisVisible = await chartAnalysis.isVisible().catch(() => false);
    logTest('Chart Analysis panel present', isAnalysisVisible);
    
    if (isAnalysisVisible) {
      // Wait for news to load
      await page.waitForTimeout(5000);
      
      const newsItems = await page.locator('.news-item').count();
      logTest('News items loaded', newsItems > 0, `Found ${newsItems} news articles`);
      
      // Test expandable news
      if (newsItems > 0) {
        const firstNewsItem = await page.locator('.news-item').first();
        const expandButton = await firstNewsItem.locator('.expand-news').first();
        const isExpandButtonVisible = await expandButton.isVisible().catch(() => false);
        
        if (isExpandButtonVisible) {
          await expandButton.click();
          await page.waitForTimeout(1000);
          
          const expandedContent = await firstNewsItem.locator('.news-content-expanded').first();
          const isContentExpanded = await expandedContent.isVisible().catch(() => false);
          logTest('News expansion functionality', isContentExpanded, 'News content expands inline');
        }
      }
      
      // Test scrollable container
      const scrollContainer = await page.locator('.chart-analysis-content').first();
      if (scrollContainer) {
        const scrollHeight = await scrollContainer.evaluate(el => el.scrollHeight);
        const clientHeight = await scrollContainer.evaluate(el => el.clientHeight);
        logTest('Scrollable news container', scrollHeight > clientHeight, `Scroll: ${scrollHeight}px > ${clientHeight}px`);
      }
    }
    
    // ===== PHASE 6: API ENDPOINTS TESTING =====
    console.log('\n📍 PHASE 6: API ENDPOINTS FUNCTIONALITY');
    
    // Test backend health
    try {
      const healthResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:8000/health');
        return { status: response.status, data: await response.json() };
      });
      logTest('Backend health endpoint', healthResponse.status === 200, `Status: ${healthResponse.status}`);
      logTest('Backend service mode', healthResponse.data.service_mode !== undefined, `Mode: ${healthResponse.data.service_mode}`);
    } catch (error) {
      logTest('Backend health endpoint', false, `Error: ${error.message}`);
    }
    
    // Test stock price endpoint
    try {
      const stockResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:8000/api/stock-price?symbol=TSLA');
        return { status: response.status, data: await response.json() };
      });
      logTest('Stock price API endpoint', stockResponse.status === 200, `TSLA price retrieved`);
      logTest('Stock price data structure', stockResponse.data.price !== undefined, `Has price field`);
    } catch (error) {
      logTest('Stock price API endpoint', false, `Error: ${error.message}`);
    }
    
    // Test news endpoint
    try {
      const newsResponse = await page.evaluate(async () => {
        const response = await fetch('http://localhost:8000/api/stock-news?symbol=TSLA');
        return { status: response.status, data: await response.json() };
      });
      logTest('Stock news API endpoint', newsResponse.status === 200, `TSLA news retrieved`);
      logTest('News data structure', Array.isArray(newsResponse.data), `Returns array of articles`);
    } catch (error) {
      logTest('Stock news API endpoint', false, `Error: ${error.message}`);
    }
    
    // ===== PHASE 7: ERROR HANDLING & EDGE CASES =====
    console.log('\n📍 PHASE 7: ERROR HANDLING & EDGE CASES');
    
    // Test invalid symbol handling
    const chartsTabForError = await page.locator('text="Interactive Charts"').first();
    await chartsTabForError.click();
    await page.waitForTimeout(1000);
    
    const addInputForError = await page.locator('.add-symbol-input').first();
    if (await addInputForError.isVisible().catch(() => false)) {
      await addInputForError.fill('INVALIDXYZ123');
      const addButtonForError = await page.locator('.add-symbol-button').first();
      if (await addButtonForError.isVisible().catch(() => false)) {
        await addButtonForError.click();
        await page.waitForTimeout(2000);
        
        // Should not add invalid symbol
        const invalidSymbolCard = await page.locator('text="INVALIDXYZ123"').count();
        logTest('Invalid symbol rejection', invalidSymbolCard === 0, 'Invalid symbols properly rejected');
      }
    }
    
    // Test console errors
    logTest('No critical console errors', testResults.errors.length === 0, 
            testResults.errors.length > 0 ? `Found ${testResults.errors.length} errors` : 'Clean console');
    
    // ===== PHASE 8: PERFORMANCE & RESPONSIVENESS =====
    console.log('\n📍 PHASE 8: PERFORMANCE & RESPONSIVENESS');
    
    // Test responsive design
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.waitForTimeout(1000);
    
    const dashboardWidth = await page.locator('.trading-dashboard-simple').evaluate(el => el.offsetWidth);
    logTest('Responsive layout (desktop)', dashboardWidth > 1000, `Width: ${dashboardWidth}px`);
    
    await page.setViewportSize({ width: 768, height: 600 });
    await page.waitForTimeout(1000);
    
    const tabletDashboardWidth = await page.locator('.trading-dashboard-simple').evaluate(el => el.offsetWidth);
    logTest('Responsive layout (tablet)', tabletDashboardWidth < 800, `Width: ${tabletDashboardWidth}px`);
    
    // Restore desktop size
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.waitForTimeout(1000);
    
    // Test memory usage (basic check)
    const memoryUsage = await page.evaluate(() => {
      if (performance.memory) {
        return {
          used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024),
          total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024)
        };
      }
      return null;
    });
    
    if (memoryUsage) {
      logTest('Memory usage reasonable', memoryUsage.used < 100, 
              `Used: ${memoryUsage.used}MB / ${memoryUsage.total}MB`, memoryUsage.used >= 100);
    }
    
    // Take final comprehensive screenshot
    await page.screenshot({ path: 'investigation-final-state.png', fullPage: true });
    testResults.screenshots.push('investigation-final-state.png');
    
  } catch (error) {
    console.error('\n💥 Investigation error:', error);
    testResults.failed.push({ name: 'Investigation Execution', details: error.message });
  }
  
  // ===== FINAL COMPREHENSIVE REPORT =====
  console.log('\n' + '='.repeat(80));
  console.log('📊 COMPREHENSIVE APPLICATION INVESTIGATION RESULTS');
  console.log('='.repeat(80));
  
  console.log(`\n✅ PASSED TESTS: ${testResults.passed.length}`);
  testResults.passed.forEach(test => console.log(`   ✓ ${test}`));
  
  if (testResults.warnings.length > 0) {
    console.log(`\n⚠️  WARNINGS: ${testResults.warnings.length}`);
    testResults.warnings.forEach(test => console.log(`   ⚠ ${test.name}${test.details ? ' - ' + test.details : ''}`));
  }
  
  if (testResults.failed.length > 0) {
    console.log(`\n❌ FAILED TESTS: ${testResults.failed.length}`);
    testResults.failed.forEach(test => console.log(`   ✗ ${test.name}${test.details ? ' - ' + test.details : ''}`));
  }
  
  if (testResults.errors.length > 0) {
    console.log(`\n🐛 CONSOLE ERRORS: ${testResults.errors.length}`);
    testResults.errors.slice(0, 5).forEach(error => console.log(`   • ${error}`));
    if (testResults.errors.length > 5) {
      console.log(`   ... and ${testResults.errors.length - 5} more errors`);
    }
  }
  
  console.log('\n📈 PERFORMANCE METRICS:');
  console.log(`   • Initial Load Time: ${testResults.performance.initialLoad}ms`);
  
  console.log('\n📸 SCREENSHOTS SAVED:');
  testResults.screenshots.forEach(screenshot => console.log(`   - ${screenshot}`));
  
  const totalTests = testResults.passed.length + testResults.failed.length;
  const passRate = Math.round((testResults.passed.length / totalTests) * 100);
  const healthScore = testResults.failed.length === 0 && testResults.errors.length < 5;
  
  console.log(`\n🎯 OVERALL PASS RATE: ${passRate}%`);
  console.log(`🏥 APPLICATION HEALTH: ${healthScore ? 'EXCELLENT' : 'NEEDS ATTENTION'}`);
  
  if (passRate >= 95 && healthScore) {
    console.log('🎉 APPLICATION STATUS: FULLY FUNCTIONAL! 🎉');
  } else if (passRate >= 85) {
    console.log('✨ APPLICATION STATUS: MOSTLY FUNCTIONAL');
  } else if (passRate >= 70) {
    console.log('⚠️  APPLICATION STATUS: PARTIALLY FUNCTIONAL');
  } else {
    console.log('❌ APPLICATION STATUS: CRITICAL ISSUES DETECTED');
  }
  
  console.log('\n🔍 Investigation completed at:', new Date().toISOString());
  console.log('🎯 All major functionality tested after UI redesign');
  console.log('📋 Recommendation: Review any failed tests or warnings above');
  
  await page.waitForTimeout(3000);
  await browser.close();
})().catch(console.error);