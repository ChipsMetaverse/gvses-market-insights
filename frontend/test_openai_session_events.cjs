const playwright = require('playwright');

async function testOpenAISessionEvents() {
  console.log('🔬 TESTING: OpenAI session.created event handling');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture ALL console messages with detailed filtering
  page.on('console', (msg) => {
    const type = msg.type();
    const text = msg.text();
    
    // Focus on OpenAI RealtimeClient events
    if (text.includes('RealtimeEvent') || text.includes('session.created') || text.includes('OpenAI') || text.includes('Realtime')) {
      console.log(`🎯 ${type.toUpperCase()}: ${text}`);
    } else if (type === 'error') {
      console.log(`🔴 ERROR: ${text}`);
    } else if (text.includes('toggle') || text.includes('connection') || text.includes('Connected')) {
      console.log(`📝 INFO: ${text}`);
    }
  });

  try {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');
    
    // Switch to OpenAI provider
    await page.locator('[data-testid="provider-dropdown"]').selectOption('openai');
    console.log('🤖 Selected OpenAI Realtime provider');
    await page.waitForTimeout(1000);
    
    // Click toggle container to connect
    console.log('🎯 Clicking toggle container to start connection...');
    await page.locator('.toggle-switch-container').click();
    console.log('✅ Toggle clicked - monitoring events...');
    
    // Wait longer to see all events
    console.log('⏳ Waiting for session.created event (15 seconds)...');
    await page.waitForTimeout(15000);
    
    // Check final state
    const toggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Final toggle status: "${toggleText}"`);
    
    const textInput = page.locator('input[data-testid="message-input"]');
    const inputVisible = await textInput.isVisible();
    console.log(`📝 Text input visible: ${inputVisible}`);
    
    if (inputVisible) {
      console.log('🎉 SUCCESS: OpenAI connection established!');
    } else {
      console.log('❌ ISSUE: Connection failed or event handling problem');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testOpenAISessionEvents().catch(console.error);