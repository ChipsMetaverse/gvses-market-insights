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
    }\n    \n    // Test 6: Test toggle switch functionality\n    console.log('\n📍 TESTING TOGGLE SWITCH');\n    \n    if (isToggleVisible) {\n      const toggleInput = await page.locator('.toggle-switch input').first();\n      const isChecked = await toggleInput.isChecked();\n      console.log(`   Toggle initial state: ${isChecked ? 'ON' : 'OFF'}`);\n      \n      // Click the toggle\n      await toggleSwitch.click();\n      await page.waitForTimeout(2000); // Wait for connection attempt\n      \n      // Check if audio status bar appears when connected\n      const audioStatusBar = await page.locator('.audio-status-bar').first();\n      const isAudioBarVisible = await audioStatusBar.isVisible().catch(() => false);\n      logTest('Audio status bar appears on connection', isAudioBarVisible);\n    }\n    \n    // Test 7: Check for improved message display\n    console.log('\n📍 TESTING MESSAGE DISPLAY');\n    \n    const welcomeText = await page.locator('.welcome-text').first();\n    const isWelcomeVisible = await welcomeText.isVisible().catch(() => false);\n    logTest('Welcome text in no-messages state', isWelcomeVisible);\n    \n    const commandsPreview = await page.locator('.commands-preview').first();\n    const isCommandsVisible = await commandsPreview.isVisible().catch(() => false);\n    logTest('Commands preview section visible', isCommandsVisible);\n    \n    // Test 8: Check enhanced text input (if connected)\n    const modernTextInput = await page.locator('.text-input-modern').first();\n    const isModernInputVisible = await modernTextInput.isVisible().catch(() => false);\n    \n    if (isModernInputVisible) {\n      logTest('Modern text input present when connected', true);\n      \n      const sendButton = await page.locator('.send-button-modern').first();\n      const isSendButtonVisible = await sendButton.isVisible().catch(() => false);\n      logTest('Modern send button present', isSendButtonVisible);\n    } else {\n      console.log('   ℹ️  Modern text input not visible (not connected)');\n    }\n    \n    // Take final screenshot\n    console.log('\n📸 Taking final screenshot...');\n    await page.screenshot({ \n      path: 'redesigned-voice-ui-final.png', \n      fullPage: false,\n      clip: {\n        x: 0,\n        y: 300,\n        width: 1200,\n        height: 700\n      }\n    });\n    testResults.screenshots.push('redesigned-voice-ui-final.png');\n    console.log('   ✓ Screenshot saved: redesigned-voice-ui-final.png');\n    \n    // Test 9: Verify space optimization\n    console.log('\n📍 TESTING SPACE OPTIMIZATION');\n    \n    const voiceSection = await page.locator('.voice-section-redesigned').first();\n    if (voiceSection) {\n      const boundingBox = await voiceSection.boundingBox();\n      if (boundingBox) {\n        const height = boundingBox.height;\n        logTest('Voice section height optimized', height >= 400, `Height: ${height}px (target: 400px+)`);\n      }\n    }\n    \n    const conversationArea = await page.locator('.conversation-messages-expanded').first();\n    if (conversationArea) {\n      const boundingBox = await conversationArea.boundingBox();\n      if (boundingBox) {\n        const height = boundingBox.height;\n        logTest('Conversation area expanded', height >= 200, `Height: ${height}px (target: 200px+)`);\n      }\n    }\n    \n  } catch (error) {\n    console.error('\\n💥 Test execution error:', error);\n    testResults.failed.push({ name: 'Test Execution', details: error.message });\n  }\n  \n  // === FINAL REPORT ===\n  console.log('\\n' + '='.repeat(60));\n  console.log('📊 REDESIGNED VOICE UI TEST RESULTS');\n  console.log('='.repeat(60));\n  \n  console.log(`\\n✅ PASSED TESTS: ${testResults.passed.length}`);\n  testResults.passed.forEach(test => console.log(`   ✓ ${test}`));\n  \n  if (testResults.failed.length > 0) {\n    console.log(`\\n❌ FAILED TESTS: ${testResults.failed.length}`);\n    testResults.failed.forEach(test => console.log(`   ✗ ${test.name}${test.details ? ' - ' + test.details : ''}`));\n  }\n  \n  console.log('\\n📸 SCREENSHOTS SAVED:');\n  testResults.screenshots.forEach(screenshot => console.log(`   - ${screenshot}`));\n  \n  const passRate = Math.round((testResults.passed.length / (testResults.passed.length + testResults.failed.length)) * 100);\n  console.log(`\\n🎯 OVERALL PASS RATE: ${passRate}%`);\n  \n  if (passRate >= 85) {\n    console.log('🎉 REDESIGNED VOICE UI: SUCCESS! 🎉');\n  } else if (passRate >= 70) {\n    console.log('⚠️  REDESIGNED VOICE UI: GOOD PROGRESS');\n  } else {\n    console.log('❌ REDESIGNED VOICE UI: NEEDS WORK');\n  }\n  \n  console.log('\\n✨ Test completed at:', new Date().toISOString());\n  \n  await page.waitForTimeout(3000);\n  await browser.close();\n})().catch(console.error);