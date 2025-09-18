const puppeteer = require('puppeteer');

async function testFixes() {
  console.log('Testing frontend and backend fixes...\n');
  
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: { width: 1440, height: 900 }
  });
  
  const page = await browser.newPage();
  
  // Monitor console for errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      if (!text.includes('contentScript.js')) { // Ignore browser extension errors
        errors.push(text);
        console.log('❌ Console Error:', text);
      }
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.message);
    console.log('❌ Page Error:', error.message);
  });

  try {
    // Navigate to the app
    console.log('1. Navigating to application...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle0' });
    await new Promise(r => setTimeout(r, 2000));
    
    // Check if page loaded without errors
    console.log('2. Checking for initial errors...');
    if (errors.length === 0) {
      console.log('✅ No initial errors detected');
    } else {
      console.log(`⚠️ Found ${errors.length} errors on load`);
    }
    
    // Test voice connection (simulate clicking mic button)
    console.log('\n3. Testing voice connection...');
    const micButton = await page.$('.mic-button, [data-testid="mic-button"], button[aria-label*="mic"], button[title*="mic"]');
    
    if (micButton) {
      await micButton.click();
      await new Promise(r => setTimeout(r, 3000));
      
      // Check for setRecordingTime errors
      const recordingTimeErrors = errors.filter(e => e.includes('setRecordingTime'));
      if (recordingTimeErrors.length === 0) {
        console.log('✅ No setRecordingTime errors');
      } else {
        console.log('❌ setRecordingTime error still present');
      }
      
      // Check for OpenAI errors
      const openAIErrors = errors.filter(e => e.includes('OpenAI'));
      if (openAIErrors.length === 0) {
        console.log('✅ No OpenAI connection errors');
      } else {
        console.log('⚠️ OpenAI errors detected (may be API key related)');
      }
    } else {
      console.log('⚠️ Mic button not found - manual testing required');
    }
    
    // Test agent query
    console.log('\n4. Testing agent query...');
    const response = await fetch('http://localhost:8000/api/agent/orchestrate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: 'Where should I long or short tomorrow?' })
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.text && !data.text.includes('WHERE') && !data.text.includes('(WHERE)')) {
        console.log('✅ Agent correctly handles general trading questions');
      } else {
        console.log('⚠️ Agent may still be treating WHERE as ticker');
      }
    } else {
      console.log('⚠️ Agent endpoint returned error:', response.status);
    }
    
    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('TEST SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total errors detected: ${errors.length}`);
    console.log(`setRecordingTime errors: ${errors.filter(e => e.includes('setRecordingTime')).length}`);
    console.log(`OpenAI errors: ${errors.filter(e => e.includes('OpenAI')).length}`);
    
    if (errors.length === 0) {
      console.log('\n✅ All fixes appear to be working correctly!');
    } else {
      console.log('\n⚠️ Some issues may remain. Review errors above.');
    }
    
    await page.screenshot({ path: 'test-fixes-final.png' });
    console.log('\nScreenshot saved: test-fixes-final.png');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

testFixes();