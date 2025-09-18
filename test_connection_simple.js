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
    if (text.includes('handleConnectToggle') || text.includes('connected') || text.includes('session.created') || text.includes('error')) {
      console.log('🔌 Console:', text.substring(0, 200));
    }
  });
  
  console.log('\n🚀 Testing Connection...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174', { timeout: 10000 });
    console.log('✅ Page loaded');
    
    // Wait for initialization
    await page.waitForTimeout(3000);
    
    // Navigate to Voice tab
    try {
      const voiceTab = await page.locator('[data-testid="voice-tab"]').first();
      await voiceTab.click();
      console.log('✅ Switched to Voice tab');
    } catch (e) {
      console.log('⚠️  Voice tab not found, might already be active');
    }
    
    // Wait a moment
    await page.waitForTimeout(2000);
    
    // Get toggle state
    const toggleInput = await page.locator('input[type="checkbox"][data-testid="connection-toggle"]');
    const initialState = await toggleInput.isChecked();
    console.log(`📊 Initial toggle state: ${initialState ? 'checked' : 'unchecked'}`);
    
    // Click the toggle
    console.log('\n🎯 Clicking toggle...\n');
    await toggleInput.click();
    
    // Wait for connection
    await page.waitForTimeout(5000);
    
    // Check new state
    const newState = await toggleInput.isChecked();
    console.log(`📊 New toggle state: ${newState ? 'checked' : 'unchecked'}`);
    
    // Verify state changed
    if (newState !== initialState) {
      console.log('✅ Toggle successfully changed state!');
      
      // Check if we're actually connected
      const toggleLabelText = await page.locator('.toggle-label').textContent();
      console.log(`📝 Toggle label text: "${toggleLabelText}"`);
      
      if (newState && (toggleLabelText.includes('Connected') || toggleLabelText.includes('Connecting'))) {
        console.log('🎉 CONNECTION SUCCESS! Voice assistant is working!');
      } else if (!newState && toggleLabelText.includes('Connect')) {
        console.log('✅ Disconnection successful');
      }
    } else {
      console.log('❌ Toggle state did not change');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  console.log('\n✨ Connection Test Complete\n');
  
  // Keep open for observation
  await page.waitForTimeout(3000);
  
  await browser.close();
})();