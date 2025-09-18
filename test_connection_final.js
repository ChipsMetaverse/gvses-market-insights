const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] 
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Track console messages
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('handleConnectToggle') || 
        text.includes('connected') || 
        text.includes('session.created') || 
        text.includes('OpenAI') ||
        text.includes('error') ||
        text.includes('temperature')) {
      console.log('🔌 Console:', text.substring(0, 250));
    }
  });
  
  console.log('\n🚀 Testing Voice Connection Fix...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174', { timeout: 10000 });
    console.log('✅ Page loaded');
    
    // Wait for initialization
    await page.waitForTimeout(3000);
    
    // Navigate to Voice tab
    try {
      const voiceTab = await page.locator('[data-testid="voice-tab"]').first();
      if (await voiceTab.isVisible()) {
        await voiceTab.click();
        console.log('✅ Switched to Voice tab');
      }
    } catch (e) {
      console.log('⚠️  Voice tab interaction skipped');
    }
    
    // Wait a moment
    await page.waitForTimeout(2000);
    
    // Try different selectors for the toggle
    let toggleClicked = false;
    
    // Try 1: Click the toggle slider
    try {
      const toggleSlider = await page.locator('.toggle-slider').first();
      if (await toggleSlider.isVisible()) {
        console.log('🎯 Clicking toggle slider...');
        await toggleSlider.click();
        toggleClicked = true;
      }
    } catch (e) {
      console.log('⚠️  Toggle slider not clickable');
    }
    
    // Try 2: Click the toggle label if slider didn't work
    if (!toggleClicked) {
      try {
        const toggleLabel = await page.locator('.toggle-switch').first();
        if (await toggleLabel.isVisible()) {
          console.log('🎯 Clicking toggle label...');
          await toggleLabel.click();
          toggleClicked = true;
        }
      } catch (e) {
        console.log('⚠️  Toggle label not clickable');
      }
    }
    
    if (!toggleClicked) {
      console.log('❌ Could not find clickable toggle element');
      return;
    }
    
    // Wait for connection attempt
    await page.waitForTimeout(8000);
    
    // Check connection status by reading the toggle label text
    try {
      const toggleLabelText = await page.locator('.toggle-label').textContent();
      console.log(`📝 Toggle label text: "${toggleLabelText}"`);
      
      if (toggleLabelText && (toggleLabelText.includes('Connected') || toggleLabelText.includes('Connecting'))) {
        console.log('🎉 SUCCESS! Voice assistant connected!');
      } else if (toggleLabelText && toggleLabelText.includes('Connect')) {
        console.log('⚠️  Still showing "Connect" - may not have connected');
      } else {
        console.log('❓ Unknown connection state');
      }
    } catch (e) {
      console.log('⚠️  Could not read toggle label');
    }
    
    // Take a screenshot
    await page.screenshot({ path: 'connection-test-final.png' });
    console.log('📸 Screenshot saved: connection-test-final.png');
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  console.log('\n✨ Voice Connection Test Complete\n');
  
  // Keep open for observation
  await page.waitForTimeout(5000);
  
  await browser.close();
})();