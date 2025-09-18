const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: false,
    slowMo: 300
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('🎨 === TESTING INTUITIVE UI REDESIGN === 🎨\n');
  
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
    
    // Test 1: Verify NO instructional text exists
    console.log('\n📍 TESTING REMOVAL OF INSTRUCTIONAL TEXT');
    
    const welcomeText = await page.locator('text="Toggle the switch above to start voice conversation"').count();
    logTest('Welcome text removed', welcomeText === 0, `Found ${welcomeText} instances (should be 0)`);
    
    const commandsText = await page.locator('text="Try these commands:"').count();
    logTest('Commands text removed', commandsText === 0, `Found ${commandsText} instances (should be 0)`);
    
    const readyText = await page.locator('text="Ready to listen - speak anytime!"').count();
    logTest('Ready text removed', readyText === 0, `Found ${readyText} instances (should be 0)`);
    
    // Test 2: Verify visual-only elements exist
    console.log('\n📍 TESTING VISUAL-ONLY INTERFACE');
    
    const emptyStateVisual = await page.locator('.empty-state-visual').first();
    const isEmptyStateVisible = await emptyStateVisual.isVisible().catch(() => false);
    logTest('Empty state visual container present', isEmptyStateVisible);
    
    const voiceIndicatorOff = await page.locator('.voice-indicator-off').first();
    const isVoiceIndicatorVisible = await voiceIndicatorOff.isVisible().catch(() => false);
    logTest('Voice indicator (off state) present', isVoiceIndicatorVisible);
    
    const microphoneIcon = await page.locator('.microphone-icon-large').first();
    const isMicrophoneVisible = await microphoneIcon.isVisible().catch(() => false);
    logTest('Large microphone icon present', isMicrophoneVisible);
    
    const toggleHintAnimation = await page.locator('.toggle-hint-animation').first();
    const isToggleHintVisible = await toggleHintAnimation.isVisible().catch(() => false);
    logTest('Toggle hint animation present', isToggleHintVisible);
    
    // Take screenshot of initial intuitive state
    console.log('\n📸 Taking screenshot of intuitive interface...');
    await page.screenshot({ 
      path: 'intuitive-ui-off-state.png', 
      fullPage: false,
      clip: {
        x: 0,
        y: 300,
        width: 1200,
        height: 700
      }
    });
    testResults.screenshots.push('intuitive-ui-off-state.png');
    console.log('   ✓ Screenshot saved: intuitive-ui-off-state.png');
    
    // Test 3: Test toggle switch interaction (visual state change)
    console.log('\n📍 TESTING VISUAL STATE TRANSITIONS');
    
    const toggleSwitch = await page.locator('.toggle-switch').first();
    const isToggleSwitchVisible = await toggleSwitch.isVisible().catch(() => false);
    
    if (isToggleSwitchVisible) {
      console.log('   Clicking toggle switch...');
      await toggleSwitch.click();
      await page.waitForTimeout(3000); // Wait for connection and visual change
      
      // Check for ready state visual elements
      const voiceIndicatorReady = await page.locator('.voice-indicator-ready').first();
      const isReadyStateVisible = await voiceIndicatorReady.isVisible().catch(() => false);
      logTest('Voice indicator (ready state) appears', isReadyStateVisible);
      
      const listeningWaves = await page.locator('.listening-waves').first();
      const isListeningWavesVisible = await listeningWaves.isVisible().catch(() => false);
      logTest('Listening waves animation present', isListeningWavesVisible);
      
      const animatePulse = await page.locator('.animate-pulse').first();
      const isPulseAnimationVisible = await animatePulse.isVisible().catch(() => false);
      logTest('Pulse animation on microphone present', isPulseAnimationVisible);
      
      // Take screenshot of connected state
      console.log('\n📸 Taking screenshot of connected state...');
      await page.screenshot({ 
        path: 'intuitive-ui-ready-state.png', 
        fullPage: false,
        clip: {
          x: 0,
          y: 300,
          width: 1200,
          height: 700
        }
      });
      testResults.screenshots.push('intuitive-ui-ready-state.png');
      console.log('   ✓ Screenshot saved: intuitive-ui-ready-state.png');
    }
    
    // Test 4: Verify no text instructions anywhere in voice section
    console.log('\n📍 TESTING COMPLETE TEXT REMOVAL');
    
    const voiceSection = await page.locator('.voice-section-redesigned').first();
    if (voiceSection) {
      const sectionText = await voiceSection.textContent();
      const hasInstructionalPhrases = sectionText.includes('Toggle') || 
                                     sectionText.includes('Try these') || 
                                     sectionText.includes('Ready to listen') ||
                                     sectionText.includes('speak anytime');
      logTest('No instructional phrases in voice section', !hasInstructionalPhrases, 
              hasInstructionalPhrases ? 'Found instructional text' : 'Clean visual-only interface');
    }
    
    // Test 5: Verify CSS animations are working
    console.log('\n📍 TESTING CSS ANIMATIONS');
    
    const animationElements = await page.locator('[class*="animation"], [class*="animate"], [class*="pulse"], [class*="waves"]').count();
    logTest('Animation classes present', animationElements > 0, `Found ${animationElements} animated elements`);
    
    // Test 6: Verify microphone icon interactions
    console.log('\n📍 TESTING MICROPHONE ICON INTERACTIONS');
    
    if (isMicrophoneVisible) {
      const micBoundingBox = await microphoneIcon.boundingBox();
      if (micBoundingBox) {
        const fontSize = await page.evaluate((el) => {
          return getComputedStyle(el).fontSize;
        }, await microphoneIcon.elementHandle());
        
        logTest('Large microphone icon sizing', fontSize === '48px', `Font size: ${fontSize} (should be 48px)`);
      }
    }
    
  } catch (error) {
    console.error('\n💥 Test execution error:', error);
    testResults.failed.push({ name: 'Test Execution', details: error.message });
  }
  
  // === FINAL REPORT ===
  console.log('\n' + '='.repeat(60));
  console.log('📊 INTUITIVE UI REDESIGN TEST RESULTS');
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
  
  if (passRate >= 90) {
    console.log('🎉 INTUITIVE UI REDESIGN: EXCELLENT! 🎉');
  } else if (passRate >= 80) {
    console.log('✨ INTUITIVE UI REDESIGN: VERY GOOD!');
  } else if (passRate >= 70) {
    console.log('⚠️  INTUITIVE UI REDESIGN: GOOD PROGRESS');
  } else {
    console.log('❌ INTUITIVE UI REDESIGN: NEEDS WORK');
  }
  
  console.log('\n✨ Zero-instruction visual interface test completed at:', new Date().toISOString());
  console.log('🎯 Goal: Professional UI that requires no text explanation');
  
  await page.waitForTimeout(3000);
  await browser.close();
})().catch(console.error);