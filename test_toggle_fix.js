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
    if (text.includes('handleConnectToggle') || text.includes('connected') || text.includes('WebSocket')) {
      console.log('🔌 Console:', text.substring(0, 200));
    }
  });
  
  console.log('\n🚀 Testing Toggle Fix...\n');
  
  try {
    // Navigate to the app
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded');
    
    // Wait for initialization
    await page.waitForTimeout(2000);
    
    // Navigate to Voice tab
    const voiceTab = await page.locator('[data-testid="voice-tab"]').first();
    await voiceTab.click();
    console.log('✅ Switched to Voice tab');
    
    // Select Agent provider (should be default)
    const providerDropdown = await page.locator('select').first();
    await providerDropdown.selectOption({ index: 0 }); // Agent is first option
    console.log('✅ Agent provider selected');
    
    // Wait a moment
    await page.waitForTimeout(1000);
    
    // Take screenshot before clicking
    await page.screenshot({ path: 'toggle-before.png' });
    console.log('📸 Screenshot before: toggle-before.png');
    
    // Get initial toggle state
    const toggleInput = await page.locator('input[type="checkbox"][data-testid="connection-toggle"]');
    const initialState = await toggleInput.isChecked();
    console.log(`📊 Initial toggle state: ${initialState ? 'checked' : 'unchecked'}`);
    
    // Click the toggle label (not the container)
    console.log('\n🎯 Clicking toggle...\n');
    const toggleLabel = await page.locator('.toggle-switch').first();
    await toggleLabel.click();
    
    // Wait for state change
    await page.waitForTimeout(2000);
    
    // Check new state
    const newState = await toggleInput.isChecked();
    console.log(`📊 New toggle state: ${newState ? 'checked' : 'unchecked'}`);
    
    // Verify state changed
    if (newState !== initialState) {
      console.log('✅ Toggle successfully changed state!');
      
      // Check if connection label updated
      const toggleLabelText = await page.locator('.toggle-label').textContent();
      console.log(`📝 Toggle label text: "${toggleLabelText}"`);
      
      if (newState && (toggleLabelText === 'Connected' || toggleLabelText === 'Connecting...')) {
        console.log('✅ Connection status updated correctly');
      } else if (!newState && toggleLabelText === 'Connect') {
        console.log('✅ Disconnection status updated correctly');
      }
    } else {
      console.log('❌ Toggle did not change state - double-trigger issue may still exist');
    }
    
    // Take screenshot after clicking
    await page.screenshot({ path: 'toggle-after.png' });
    console.log('📸 Screenshot after: toggle-after.png');
    
    // Test clicking again to disconnect
    if (newState) {
      console.log('\n🔄 Testing disconnect...\n');
      await toggleLabel.click();
      await page.waitForTimeout(2000);
      
      const finalState = await toggleInput.isChecked();
      if (!finalState) {
        console.log('✅ Successfully disconnected');
      } else {
        console.log('⚠️  Disconnect did not work as expected');
      }
    }
    
    // Check for any errors
    const errorElements = await page.locator('text=/error/i').all();
    if (errorElements.length > 0) {
      console.log('\n⚠️  Errors found on page:');
      for (const error of errorElements) {
        const errorText = await error.textContent();
        console.log('   -', errorText);
      }
    } else {
      console.log('\n✅ No error messages displayed');
    }
    
  } catch (error) {
    console.error('❌ Test error:', error.message);
  }
  
  console.log('\n✨ Toggle Fix Test Complete\n');
  
  // Keep open for observation
  await page.waitForTimeout(5000);
  
  await browser.close();
})();