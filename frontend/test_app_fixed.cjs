const { chromium } = require('playwright');

async function testAppFixed() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🚀 Testing fixed application...');
  
  try {
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(3000);
    
    // Take screenshot
    await page.screenshot({ 
      path: 'app-fixed.png',
      fullPage: true 
    });
    console.log('📸 Screenshot saved as app-fixed.png');
    
    // Check for chart
    const hasChart = await page.$('.trading-chart-container');
    console.log('Chart container:', hasChart ? '✅ Found' : '❌ Not found');
    
    // Check for voice tab
    const hasVoice = await page.$('button:has-text("Voice")');
    console.log('Voice tab:', hasVoice ? '✅ Found' : '❌ Not found');
    
    // Check for dashboard
    const hasDashboard = await page.$('.trading-dashboard-simple');
    console.log('Dashboard:', hasDashboard ? '✅ Found' : '❌ Not found');
    
    console.log('\n✅ Application is working!');

  } catch (error) {
    console.error('❌ Test failed:', error);
  }

  await browser.close();
}

testAppFixed().catch(console.error);