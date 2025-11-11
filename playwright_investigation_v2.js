// Enhanced Playwright investigation script
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();
  
  // Enable request/response logging
  page.on('request', request => {
    console.log(`→ ${request.method()} ${request.url()}`);
  });
  
  page.on('response', response => {
    console.log(`← ${response.status()} ${response.url()}`);
  });
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log(`[CONSOLE ERROR] ${msg.text()}`);
    }
  });
  
  console.log('🔍 Enhanced Playwright Investigation Starting...\n');
  
  // 1. Health endpoint
  console.log('1️⃣ Testing /health endpoint...');
  try {
    const healthResponse = await page.goto('https://gvses-market-insights-api.fly.dev/health', {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    console.log(`   Status: ${healthResponse.status()}`);
    const healthText = await page.textContent('body');
    const healthJson = JSON.parse(healthText);
    console.log(`   ✅ Status: ${healthJson.status}`);
    console.log(`   ✅ Service Mode: ${healthJson.service_mode}`);
    console.log(`   ✅ MCP Available: ${healthJson.mcp_sidecars?.available}`);
  } catch (e) {
    console.log(`   ❌ Error: ${e.message}`);
  }
  
  await page.waitForTimeout(1000);
  
  // 2. Stock price API
  console.log('\n2️⃣ Testing /api/stock-price endpoint...');
  try {
    const stockResponse = await page.goto('https://gvses-market-insights-api.fly.dev/api/stock-price?symbol=TSLA', {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    console.log(`   Status: ${stockResponse.status()}`);
    const stockText = await page.textContent('body');
    const stockJson = JSON.parse(stockText);
    console.log(`   ✅ Symbol: ${stockJson.symbol}`);
    console.log(`   ✅ Price: $${stockJson.price}`);
    console.log(`   ✅ Data Source: ${stockJson.data_source}`);
  } catch (e) {
    console.log(`   ❌ Error: ${e.message}`);
  }
  
  await page.waitForTimeout(1000);
  
  // 3. OpenAPI endpoint with detailed error capture
  console.log('\n3️⃣ Testing /openapi.json endpoint...');
  try {
    const openApiResponse = await page.goto('https://gvses-market-insights-api.fly.dev/openapi.json', {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    console.log(`   Status: ${openApiResponse.status()}`);
    if (openApiResponse.status() === 500) {
      const errorText = await page.textContent('body');
      console.log(`   ❌ Error Response: ${errorText.substring(0, 500)}`);
      
      // Try to get response headers
      const headers = openApiResponse.headers();
      console.log(`   Response Headers:`, Object.keys(headers));
    } else {
      const openApiText = await page.textContent('body');
      const openApiJson = JSON.parse(openApiText);
      console.log(`   ✅ OpenAPI Schema Loaded: ${Object.keys(openApiJson).length} top-level keys`);
    }
  } catch (e) {
    console.log(`   ❌ Error: ${e.message}`);
  }
  
  await page.waitForTimeout(1000);
  
  // 4. Agent orchestrate with shorter timeout
  console.log('\n4️⃣ Testing /api/agent/orchestrate endpoint (10s timeout)...');
  try {
    const agentResponse = await page.request.post('https://gvses-market-insights-api.fly.dev/api/agent/orchestrate', {
      data: {
        query: 'What is the price of TSLA?',
        conversation_history: []
      },
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 10000  // 10 second timeout
    });
    
    console.log(`   Status: ${agentResponse.status()}`);
    const agentData = await agentResponse.json();
    console.log(`   ✅ Response received`);
    console.log(`   Text preview: ${agentData.text?.substring(0, 100)}`);
    if (agentData.error) {
      console.log(`   ⚠️ Error: ${agentData.error}`);
    }
    if (agentData.data?.error) {
      console.log(`   ⚠️ Data Error: ${agentData.data.error}`);
    }
  } catch (e) {
    if (e.message.includes('Timeout')) {
      console.log(`   ⚠️ Timeout after 10 seconds - request hanging`);
    } else {
      console.log(`   ❌ Error: ${e.message}`);
    }
  }
  
  await page.waitForTimeout(1000);
  
  // 5. Test analytics endpoint
  console.log('\n5️⃣ Testing /api/analytics/queries endpoint...');
  try {
    const analyticsResponse = await page.goto('https://gvses-market-insights-api.fly.dev/api/analytics/queries', {
      waitUntil: 'networkidle',
      timeout: 10000
    });
    console.log(`   Status: ${analyticsResponse.status()}`);
    const analyticsText = await page.textContent('body');
    const analyticsJson = JSON.parse(analyticsText);
    console.log(`   ✅ Response: ${JSON.stringify(analyticsJson)}`);
  } catch (e) {
    console.log(`   ❌ Error: ${e.message}`);
  }
  
  await page.waitForTimeout(1000);
  
  // 6. Test docs endpoint
  console.log('\n6️⃣ Testing /docs endpoint...');
  try {
    await page.goto('https://gvses-market-insights-api.fly.dev/docs', {
      waitUntil: 'domcontentloaded',
      timeout: 15000
    });
    await page.waitForTimeout(3000);  // Wait for Swagger to load
    
    const pageTitle = await page.title();
    console.log(`   Page Title: ${pageTitle}`);
    
    // Check for error messages
    const errorElements = await page.locator('text=/error|failed/i').all();
    if (errorElements.length > 0) {
      console.log(`   ⚠️ Found ${errorElements.length} error elements on page`);
      for (let i = 0; i < Math.min(3, errorElements.length); i++) {
        const text = await errorElements[i].textContent();
        console.log(`      - ${text}`);
      }
    } else {
      console.log(`   ✅ No error messages found`);
    }
  } catch (e) {
    console.log(`   ❌ Error: ${e.message}`);
  }
  
  // Take final screenshot
  console.log('\n📸 Taking final screenshot...');
  await page.screenshot({ path: 'production_investigation_v2.png', fullPage: true });
  console.log('   ✅ Screenshot saved to production_investigation_v2.png');
  
  await browser.close();
  console.log('\n✅ Enhanced investigation complete!');
})();

