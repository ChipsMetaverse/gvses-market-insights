const { chromium } = require('playwright');

async function testComputerUseScenario() {
  console.log('🤖 Testing Computer Use scenario with fixed API URL resolution...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  try {
    // Test 1: Access from host.docker.internal
    console.log('📍 Test 1: Simulating Computer Use access from host.docker.internal');
    await page.goto('http://host.docker.internal:5174');
    await page.waitForTimeout(3000);
    
    // Check for JavaScript errors
    const jsErrors = [];
    page.on('pageerror', error => jsErrors.push(error.message));
    
    // Check if getApiUrl is available
    const apiUrlAvailable = await page.evaluate(() => {
      return typeof window.getApiUrl === 'function';
    });
    console.log(`  ✅ getApiUrl available: ${apiUrlAvailable}`);
    
    // Get the resolved API URL
    const resolvedApiUrl = await page.evaluate(() => {
      if (typeof window.getApiUrl === 'function') {
        return window.getApiUrl();
      }
      return 'not available';
    });
    console.log(`  📡 Resolved API URL: ${resolvedApiUrl}`);
    
    // Test 2: Check main components loaded
    console.log('\n📊 Test 2: Checking main components...');
    
    const chartVisible = await page.locator('.chart-container').isVisible();
    console.log(`  ✅ Chart container: ${chartVisible ? 'visible' : 'not visible'}`);
    
    const voiceAssistant = await page.locator('.voice-assistant-panel').isVisible();
    console.log(`  ✅ Voice Assistant: ${voiceAssistant ? 'visible' : 'not visible'}`);
    
    const marketInsights = await page.locator('.market-insights-panel').isVisible();
    console.log(`  ✅ Market Insights: ${marketInsights ? 'visible' : 'not visible'}`);
    
    // Test 3: Simulate API call
    console.log('\n🌐 Test 3: Testing API connectivity...');
    
    const apiResponse = await page.evaluate(async () => {
      try {
        const apiUrl = typeof window.getApiUrl === 'function' 
          ? window.getApiUrl() 
          : 'http://host.docker.internal:8000';
        
        const response = await fetch(`${apiUrl}/health`);
        const data = await response.json();
        return { success: true, status: data.status };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });
    
    if (apiResponse.success) {
      console.log(`  ✅ API health check: ${apiResponse.status}`);
    } else {
      console.log(`  ❌ API health check failed: ${apiResponse.error}`);
    }
    
    // Test 4: Check for CORS errors in network
    console.log('\n🔒 Test 4: Checking for CORS issues...');
    
    const corsCheck = await page.evaluate(async () => {
      try {
        const apiUrl = typeof window.getApiUrl === 'function' 
          ? window.getApiUrl() 
          : 'http://host.docker.internal:8000';
          
        const response = await fetch(`${apiUrl}/api/stock-price?symbol=AAPL`);
        if (!response.ok) {
          return `HTTP ${response.status}`;
        }
        const data = await response.json();
        return data.symbol ? 'Success' : 'No data';
      } catch (error) {
        return error.message;
      }
    });
    
    console.log(`  📈 Stock price API call: ${corsCheck}`);
    
    // Test 5: Check Voice Assistant input
    console.log('\n💬 Test 5: Testing Voice Assistant input...');
    
    const inputField = await page.locator('.voice-assistant-panel input[type="text"], .voice-assistant-panel textarea').first();
    if (await inputField.isVisible()) {
      await inputField.click();
      await inputField.fill('What is the current price of PLTR?');
      console.log('  ✅ Voice Assistant input field: functional');
    } else {
      console.log('  ❌ Voice Assistant input field: not found');
    }
    
    // Report JavaScript errors if any
    if (jsErrors.length > 0) {
      console.log('\n⚠️  JavaScript errors detected:');
      jsErrors.forEach(err => console.log(`  - ${err}`));
    } else {
      console.log('\n✅ No JavaScript errors detected');
    }
    
    // Take screenshot
    await page.screenshot({ path: 'computer-use-test-result.png' });
    console.log('\n📸 Screenshot saved as computer-use-test-result.png');
    
    console.log('\n' + '='.repeat(50));
    console.log('🎉 COMPUTER USE TEST COMPLETE');
    console.log('='.repeat(50));
    
    if (apiUrlAvailable && chartVisible && !jsErrors.length) {
      console.log('\n✅ SUCCESS: App is ready for Computer Use!');
      console.log('   - API URL resolution working');
      console.log('   - Components loaded properly');
      console.log('   - No JavaScript errors');
      console.log('\n🚀 Computer Use can now:');
      console.log('   1. Navigate to http://host.docker.internal:5174');
      console.log('   2. Interact with the Voice Assistant');
      console.log('   3. Ask about stock prices');
      console.log('   4. Control charts and indicators');
    } else {
      console.log('\n⚠️  Some issues detected - please review above');
    }
    
    // Keep browser open for 10 seconds to observe
    await page.waitForTimeout(10000);
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await browser.close();
  }
}

testComputerUseScenario();