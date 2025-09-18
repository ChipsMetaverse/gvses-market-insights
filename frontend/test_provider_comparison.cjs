const playwright = require('playwright');

async function testProviderComparison() {
  console.log('🚀 TESTING: Provider Comparison (ElevenLabs vs OpenAI)');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console logs
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log('🔴 CONSOLE ERROR:', msg.text());
    } else if (msg.type() === 'log') {
      console.log('📝 CONSOLE LOG:', msg.text());
    }
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);

    console.log('\n=== TESTING ELEVENLABS ===');
    
    // Select ElevenLabs
    const elevenLabsButton = page.locator('[data-testid="provider-elevenlabs"]');
    await elevenLabsButton.click();
    console.log('✅ Selected ElevenLabs provider');
    
    await page.waitForTimeout(1000);
    
    // Try to connect
    const connectToggle = page.locator('[data-testid="voice-toggle-switch"]');
    await connectToggle.click();
    console.log('🔄 Clicked ElevenLabs connect toggle...');
    
    // Wait and check for connection
    await page.waitForTimeout(5000);
    
    const elevenlabsTextInput = page.locator('input[data-testid="message-input"]');
    const isElevenLabsInputVisible = await elevenlabsTextInput.isVisible();
    console.log(`📝 ElevenLabs text input visible: ${isElevenLabsInputVisible}`);
    
    // Disconnect
    await connectToggle.click();
    await page.waitForTimeout(2000);
    
    console.log('\n=== TESTING OPENAI ===');
    
    // Select OpenAI Realtime
    const openAIButton = page.locator('[data-testid="provider-openai-realtime"]');
    await openAIButton.click();
    console.log('✅ Selected OpenAI Realtime provider');
    
    await page.waitForTimeout(1000);
    
    // Try to connect
    await connectToggle.click();
    console.log('🔄 Clicked OpenAI connect toggle...');
    
    // Wait and check for connection
    await page.waitForTimeout(5000);
    
    const openAITextInput = page.locator('input[data-testid="message-input"]');
    const isOpenAIInputVisible = await openAITextInput.isVisible();
    console.log(`📝 OpenAI text input visible: ${isOpenAIInputVisible}`);
    
    console.log('\n=== SUMMARY ===');
    console.log(`ElevenLabs connection success: ${isElevenLabsInputVisible}`);
    console.log(`OpenAI Realtime connection success: ${isOpenAIInputVisible}`);
    
    if (isElevenLabsInputVisible && !isOpenAIInputVisible) {
      console.log('🎯 CONFIRMED: ElevenLabs works, OpenAI doesn\'t - issue is with OpenAI integration');
    } else if (!isElevenLabsInputVisible && !isOpenAIInputVisible) {
      console.log('❌ BOTH BROKEN: Issue with overall connection logic');
    } else {
      console.log('✅ Both working or unexpected combination');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testProviderComparison().catch(console.error);