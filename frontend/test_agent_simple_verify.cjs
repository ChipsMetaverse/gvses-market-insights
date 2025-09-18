/**
 * Simple verification test to check agent indicator controls
 */

const { chromium } = require('playwright');

async function testAgentIndicatorSimple() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('🚀 Starting Simple Agent Indicator Verification');
  
  try {
    // Navigate to the application
    await page.goto('http://localhost:5176');
    console.log('✅ Navigated to app');
    
    // Wait for any content
    await page.waitForTimeout(3000);
    
    // Take screenshot to see what's loaded
    await page.screenshot({ 
      path: 'agent-test-initial.png',
      fullPage: true 
    });
    console.log('📸 Initial screenshot saved');
    
    // Try to find any main element
    const hasApp = await page.$('#root');
    if (hasApp) {
      console.log('✅ React app root found');
    }
    
    // Check if there's an error
    const bodyText = await page.textContent('body');
    if (bodyText.includes('Error') || bodyText.includes('error')) {
      console.log('⚠️ Error detected on page:', bodyText.substring(0, 200));
    }
    
    // Try to find the Voice tab
    const voiceTab = await page.$('button:has-text("Voice")');
    if (voiceTab) {
      console.log('✅ Voice tab found');
      await voiceTab.click();
      console.log('✅ Voice tab clicked');
      
      await page.waitForTimeout(1000);
      
      // Take screenshot after clicking Voice
      await page.screenshot({ 
        path: 'agent-test-voice-tab.png',
        fullPage: true 
      });
      console.log('📸 Voice tab screenshot saved');
    } else {
      console.log('❌ Voice tab not found');
    }
    
    // Check localStorage for indicator state
    const indicatorState = await page.evaluate(() => {
      return localStorage.getItem('indicatorState');
    });
    
    if (indicatorState) {
      console.log('✅ Indicator state found in localStorage');
      const state = JSON.parse(indicatorState);
      console.log('  Symbol:', state.symbol);
      console.log('  Timeframe:', state.timeframe);
    } else {
      console.log('ℹ️ No indicator state in localStorage yet');
    }
    
    console.log('\n✅ Basic verification complete');
    console.log('Check screenshots: agent-test-initial.png and agent-test-voice-tab.png');

  } catch (error) {
    console.error('❌ Test failed:', error);
    await page.screenshot({ 
      path: 'agent-test-error.png',
      fullPage: true 
    });
  }

  await browser.close();
}

// Run the test
testAgentIndicatorSimple().catch(console.error);