const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: false,
    slowMo: 500
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('🎨 === TESTING REDESIGNED VOICE UI === 🎨\n');
  
  const testResults = {
    passed: [],
    failed: [],
    screenshots: []
  };
  
  function logTest(name, passed, details = '') {
    const result = passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${result}: ${name}${details ? ' - ' + details : ''}`);
    
    if (passed) {
      testResults.passed.push(name);
    } else {
      testResults.failed.push({ name, details });
    }
  }
  
  try {
    // Navigate to the app
    console.log('1. Navigating to localhost:5174...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // Switch to voice tab
    console.log('2. Switching to Voice + Manual Control tab...');
    const voiceTab = await page.locator('text="Voice + Manual Control"').first();
    await voiceTab.click();
    await page.waitForTimeout(1000);
    
    // Test 1: Check for redesigned voice section
    console.log('\n📍 TESTING REDESIGNED COMPONENTS');
    
    const redesignedSection = await page.locator('.voice-section-redesigned').first();
    const isRedesignedVisible = await redesignedSection.isVisible().catch(() => false);
    logTest('Redesigned voice section visible', isRedesignedVisible);
    
    // Test 2: Check for modern toggle switch
    const toggleSwitch = await page.locator('.toggle-switch').first();
    const isToggleVisible = await toggleSwitch.isVisible().catch(() => false);
    logTest('Modern toggle switch present', isToggleVisible);
    
    // Test 3: Check for provider dropdown
    const providerDropdown = await page.locator('.provider-dropdown').first();
    const isDropdownVisible = await providerDropdown.isVisible().catch(() => false);
    logTest('Provider dropdown present', isDropdownVisible);
    
    // Test 4: Check for expanded conversation area
    const expandedMessages = await page.locator('.conversation-messages-expanded').first();
    const isExpandedVisible = await expandedMessages.isVisible().catch(() => false);
    logTest('Expanded conversation area present', isExpandedVisible);
    
    // Take screenshot of initial redesigned state
    console.log('\n📸 Taking screenshot of redesigned interface...');
    await page.screenshot({ 
      path: 'redesigned-voice-ui-initial.png', 
      fullPage: false,
      clip: {
        x: 0,
        y: 300,
        width: 1200,
        height: 700
      }
    });
    testResults.screenshots.push('redesigned-voice-ui-initial.png');
    console.log('   ✓ Screenshot saved: redesigned-voice-ui-initial.png');
    
    // Test 5: Test provider dropdown functionality
    console.log('\n📍 TESTING PROVIDER DROPDOWN');
    
    if (isDropdownVisible) {
      // Get current value
      const currentValue = await providerDropdown.inputValue();
      console.log(`   Current provider: ${currentValue}`);
      
      // Change to OpenAI
      await providerDropdown.selectOption('openai');
      await page.waitForTimeout(500);
      
      const newValue = await providerDropdown.inputValue();
      logTest('Provider dropdown functional', newValue === 'openai', `Changed to: ${newValue}`);
      
      // Change back to ElevenLabs
      await providerDropdown.selectOption('elevenlabs');
      await page.waitForTimeout(500);
    }
    
    // Test 6: Test toggle switch functionality
    console.log('\n📍 TESTING TOGGLE SWITCH');
    
    if (isToggleVisible) {
      const toggleInput = await page.locator('.toggle-switch input').first();
      const isChecked = await toggleInput.isChecked();
      console.log(`   Toggle initial state: ${isChecked ? 'ON' : 'OFF'}`);
      
      // Click the toggle
      await toggleSwitch.click();
      await page.waitForTimeout(2000); // Wait for connection attempt
      
      // Check if audio status bar appears when connected
      const audioStatusBar = await page.locator('.audio-status-bar').first();
      const isAudioBarVisible = await audioStatusBar.isVisible().catch(() => false);
      logTest('Audio status bar appears on connection', isAudioBarVisible);
    }
    
    // Test 7: Check for improved message display
    console.log('\n📍 TESTING MESSAGE DISPLAY');
    
    const welcomeText = await page.locator('.welcome-text').first();
    const isWelcomeVisible = await welcomeText.isVisible().catch(() => false);
    logTest('Welcome text in no-messages state', isWelcomeVisible);
    
    const commandsPreview = await page.locator('.commands-preview').first();
    const isCommandsVisible = await commandsPreview.isVisible().catch(() => false);
    logTest('Commands preview section visible', isCommandsVisible);
    
    // Test 8: Check enhanced text input (if connected)
    const modernTextInput = await page.locator('.text-input-modern').first();
    const isModernInputVisible = await modernTextInput.isVisible().catch(() => false);
    
    if (isModernInputVisible) {
      logTest('Modern text input present when connected', true);
      
      const sendButton = await page.locator('.send-button-modern').first();
      const isSendButtonVisible = await sendButton.isVisible().catch(() => false);
      logTest('Modern send button present', isSendButtonVisible);
    } else {
      console.log('   ℹ️  Modern text input not visible (not connected)');
    }
    
    // Take final screenshot
    console.log('\n📸 Taking final screenshot...');
    await page.screenshot({ 
      path: 'redesigned-voice-ui-final.png', 
      fullPage: false,
      clip: {
        x: 0,
        y: 300,
        width: 1200,
        height: 700
      }
    });
    testResults.screenshots.push('redesigned-voice-ui-final.png');
    console.log('   ✓ Screenshot saved: redesigned-voice-ui-final.png');
    
    // Test 9: Verify space optimization
    console.log('\n📍 TESTING SPACE OPTIMIZATION');
    
    const voiceSection = await page.locator('.voice-section-redesigned').first();
    if (voiceSection) {
      const boundingBox = await voiceSection.boundingBox();
      if (boundingBox) {
        const height = boundingBox.height;
        logTest('Voice section height optimized', height >= 400, `Height: ${height}px (target: 400px+)`);
      }
    }
    
    const conversationArea = await page.locator('.conversation-messages-expanded').first();
    if (conversationArea) {
      const boundingBox = await conversationArea.boundingBox();
      if (boundingBox) {
        const height = boundingBox.height;
        logTest('Conversation area expanded', height >= 200, `Height: ${height}px (target: 200px+)`);
      }
    }
    
  } catch (error) {
    console.error('\n💥 Test execution error:', error);
    testResults.failed.push({ name: 'Test Execution', details: error.message });
  }
  
  // === FINAL REPORT ===
  console.log('\n' + '='.repeat(60));
  console.log('📊 REDESIGNED VOICE UI TEST RESULTS');
  console.log('='.repeat(60));
  
  console.log(`\n✅ PASSED TESTS: ${testResults.passed.length}`);
  testResults.passed.forEach(test => console.log(`   ✓ ${test}`));
  
  if (testResults.failed.length > 0) {
    console.log(`\n❌ FAILED TESTS: ${testResults.failed.length}`);
    testResults.failed.forEach(test => console.log(`   ✗ ${test.name}${test.details ? ' - ' + test.details : ''}`));
  }
  
  console.log('\n📸 SCREENSHOTS SAVED:');
  testResults.screenshots.forEach(screenshot => console.log(`   - ${screenshot}`));
  
  const passRate = Math.round((testResults.passed.length / (testResults.passed.length + testResults.failed.length)) * 100);
  console.log(`\n🎯 OVERALL PASS RATE: ${passRate}%`);
  
  if (passRate >= 85) {
    console.log('🎉 REDESIGNED VOICE UI: SUCCESS! 🎉');
  } else if (passRate >= 70) {
    console.log('⚠️  REDESIGNED VOICE UI: GOOD PROGRESS');
  } else {
    console.log('❌ REDESIGNED VOICE UI: NEEDS WORK');
  }
  
  console.log('\n✨ Test completed at:', new Date().toISOString());
  
  await page.waitForTimeout(3000);
  await browser.close();
})().catch(console.error);