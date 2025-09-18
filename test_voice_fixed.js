const { chromium } = require('playwright');

async function testVoiceConnection() {
  console.log('🎯 Testing voice assistant connection after fixes...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 500
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Capture console messages
  const consoleMessages = [];
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    consoleMessages.push({ type, text });
    
    if (type === 'error') {
      console.log('❌ ERROR:', text);
    } else if (type === 'warning') {
      console.log('⚠️ WARNING:', text);
    } else if (text.includes('connect') || text.includes('WebSocket') || text.includes('OpenAI')) {
      console.log('📝 LOG:', text);
    }
  });
  
  // Capture network WebSocket activity
  page.on('websocket', ws => {
    console.log('🔌 WebSocket created:', ws.url());
    ws.on('close', () => console.log('🔌 WebSocket closed'));
    ws.on('framereceived', (data) => {
      if (data.payload && data.payload.includes('session.created')) {
        console.log('✅ WebSocket session created successfully!');
      }
    });
  });
  
  await page.goto('http://localhost:5174');
  console.log('📍 Page loaded\n');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  await page.click('button:has-text("Voice + Manual Control")');
  console.log('📍 Voice tab activated\n');
  await page.waitForTimeout(1000);
  
  // Test each provider
  const providers = ['openai', 'agent', 'elevenlabs'];
  
  for (const provider of providers) {
    console.log(`\n🧪 Testing ${provider.toUpperCase()} provider...`);
    
    // Select provider from dropdown
    await page.selectOption('.provider-dropdown', provider);
    console.log(`   Selected ${provider} from dropdown`);
    await page.waitForTimeout(500);
    
    // Click the Connect toggle
    const toggleBefore = await page.isChecked('input[type="checkbox"]');
    console.log(`   Toggle state before: ${toggleBefore}`);
    
    await page.click('.toggle-switch-container');
    console.log('   Clicked Connect toggle');
    
    // Wait for connection attempt
    await page.waitForTimeout(3000);
    
    const toggleAfter = await page.isChecked('input[type="checkbox"]');
    console.log(`   Toggle state after: ${toggleAfter}`);
    
    // Check for errors
    const recentErrors = consoleMessages
      .filter(m => m.type === 'error')
      .slice(-5);
    
    if (recentErrors.length > 0) {
      console.log(`   ⚠️ Recent errors detected:`);
      recentErrors.forEach(e => console.log(`      ${e.text}`));
    } else {
      console.log(`   ✅ No errors detected!`);
    }
    
    // Disconnect before testing next provider
    if (toggleAfter) {
      await page.click('.toggle-switch-container');
      console.log('   Disconnected');
      await page.waitForTimeout(1000);
    }
    
    // Clear console messages for next test
    consoleMessages.length = 0;
  }
  
  console.log('\n✅ All provider tests completed!');
  
  // Take final screenshot
  await page.screenshot({ path: 'voice-test-completed.png' });
  console.log('📸 Screenshot saved: voice-test-completed.png');
  
  await browser.close();
}

testVoiceConnection().catch(console.error);