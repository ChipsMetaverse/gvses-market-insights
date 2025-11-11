// Playwright investigation script for production app
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🔍 Investigating production app...');
  
  // Test health endpoint
  console.log('\n1. Testing /health endpoint...');
  await page.goto('https://gvses-market-insights-api.fly.dev/health');
  const healthText = await page.textContent('body');
  console.log('Health Response:', healthText.substring(0, 200));
  
  // Test stock price API
  console.log('\n2. Testing /api/stock-price endpoint...');
  const stockResponse = await page.goto('https://gvses-market-insights-api.fly.dev/api/stock-price?symbol=AAPL');
  const stockText = await page.textContent('body');
  console.log('Stock Price Response:', stockText.substring(0, 200));
  
  // Test OpenAPI endpoint
  console.log('\n3. Testing /openapi.json endpoint...');
  try {
    const openApiResponse = await page.goto('https://gvses-market-insights-api.fly.dev/openapi.json');
    console.log('OpenAPI Status:', openApiResponse.status());
    if (openApiResponse.status() === 500) {
      const errorText = await page.textContent('body');
      console.log('Error:', errorText.substring(0, 300));
    }
  } catch (e) {
    console.log('OpenAPI Error:', e.message);
  }
  
  // Check console errors
  console.log('\n4. Checking console errors...');
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('Console Error:', msg.text());
    }
  });
  
  // Test agent orchestrate endpoint
  console.log('\n5. Testing /api/agent/orchestrate endpoint...');
  try {
    const agentResponse = await page.request.post('https://gvses-market-insights-api.fly.dev/api/agent/orchestrate', {
      data: {
        query: 'What is the price of AAPL?',
        conversation_history: []
      },
      headers: {
        'Content-Type': 'application/json'
      }
    });
    const agentData = await agentResponse.json();
    console.log('Agent Response Status:', agentResponse.status());
    console.log('Agent Response:', JSON.stringify(agentData, null, 2).substring(0, 500));
  } catch (e) {
    console.log('Agent Error:', e.message);
  }
  
  // Take screenshot
  console.log('\n6. Taking screenshot...');
  await page.screenshot({ path: 'production_investigation.png', fullPage: true });
  console.log('Screenshot saved to production_investigation.png');
  
  await browser.close();
  console.log('\n✅ Investigation complete!');
})();

