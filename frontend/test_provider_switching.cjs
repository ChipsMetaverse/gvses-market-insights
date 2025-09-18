const playwright = require('playwright');

async function testProviderSwitching() {
  console.log('🚀 TESTING: Voice Provider Switching (ElevenLabs ↔ OpenAI)');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor console logs
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      console.log('🔴 CONSOLE ERROR:', msg.text());
    } else if (msg.text().includes('voice') || msg.text().includes('provider') || msg.text().includes('OpenAI') || msg.text().includes('ElevenLabs') || msg.text().includes('Connected') || msg.text().includes('Connection')) {
      console.log('📝 CONSOLE LOG:', msg.text());
    }
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');

    console.log('\n=== TESTING ELEVENLABS PROVIDER ===');
    
    // Select ElevenLabs from dropdown
    const providerDropdown = page.locator('[data-testid="provider-dropdown"]');
    await providerDropdown.selectOption('elevenlabs');
    console.log('🎤 Selected ElevenLabs provider');
    await page.waitForTimeout(1000);
    
    // Click connect toggle
    const toggleContainer = page.locator('.toggle-switch-container');
    await toggleContainer.click();
    console.log('🔄 Clicked ElevenLabs connect toggle...');
    
    // Wait and check for connection
    await page.waitForTimeout(5000);
    
    const elevenlabsToggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 ElevenLabs status: "${elevenlabsToggleText}"`);
    
    const elevenlabsTextInput = page.locator('input[data-testid="message-input"]');
    const isElevenLabsInputVisible = await elevenlabsTextInput.isVisible();
    console.log(`📝 ElevenLabs text input visible: ${isElevenLabsInputVisible}`);
    
    // Disconnect ElevenLabs
    if (elevenlabsToggleText?.includes('Connected')) {
      await toggleContainer.click();
      await page.waitForTimeout(2000);
      console.log('🔌 Disconnected ElevenLabs');
    }

    console.log('\n=== TESTING OPENAI REALTIME PROVIDER ===');
    
    // Select OpenAI Realtime from dropdown
    await providerDropdown.selectOption('openai');
    console.log('🤖 Selected OpenAI Realtime provider');
    await page.waitForTimeout(1000);
    
    // Click connect toggle
    await toggleContainer.click();
    console.log('🔄 Clicked OpenAI connect toggle...');
    
    // Wait and check for connection
    await page.waitForTimeout(8000);
    
    const openAIToggleText = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 OpenAI status: "${openAIToggleText}"`);
    
    const openAITextInput = page.locator('input[data-testid="message-input"]');
    const isOpenAIInputVisible = await openAITextInput.isVisible();
    console.log(`📝 OpenAI text input visible: ${isOpenAIInputVisible}`);
    
    console.log('\n=== PROVIDER SWITCHING TEST RESULTS ===');
    console.log(`ElevenLabs connection success: ${isElevenLabsInputVisible}`);
    console.log(`OpenAI Realtime connection success: ${isOpenAIInputVisible}`);
    
    if (isElevenLabsInputVisible && isOpenAIInputVisible) {
      console.log('🎉 SUCCESS: Both providers work correctly!');
    } else if (isOpenAIInputVisible && !isElevenLabsInputVisible) {
      console.log('✅ OpenAI working, ElevenLabs may need configuration');
    } else if (isElevenLabsInputVisible && !isOpenAIInputVisible) {
      console.log('✅ ElevenLabs working, OpenAI may need configuration');
    } else {
      console.log('❌ ISSUE: Neither provider connected successfully');
    }

    // Test quick switching between providers
    console.log('\n=== TESTING RAPID PROVIDER SWITCHING ===');
    
    // Switch back to ElevenLabs
    await providerDropdown.selectOption('elevenlabs');
    await page.waitForTimeout(500);
    console.log('🔄 Switched back to ElevenLabs');
    
    // Switch to OpenAI again
    await providerDropdown.selectOption('openai');
    await page.waitForTimeout(500);
    console.log('🔄 Switched back to OpenAI');
    
    console.log('✅ Rapid switching test completed');
    
    // Take final screenshot
    await page.screenshot({ path: 'provider-switching-test.png', fullPage: true });
    console.log('📸 Screenshot saved: provider-switching-test.png');
    
  } catch (error) {
    console.error('❌ Test error:', error);
  } finally {
    await browser.close();
  }
}

testProviderSwitching().catch(console.error);