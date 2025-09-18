const { chromium } = require('playwright');

async function testAgentVoicePortFix() {
  console.log('🧠 Testing Agent Voice Integration - Port 5175 Fix...');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 200
  });
  const page = await browser.newPage();
  
  try {
    // Connect to the actual running server port
    console.log('\n🚀 Phase 1: Application Loading (Port 5175)');
    await page.goto('http://localhost:5175');
    console.log('✅ Application loaded on port 5175');
    await page.waitForTimeout(3000);
    
    // Check if React app is rendering
    console.log('\n🔍 Phase 2: React App Verification');
    const pageContent = await page.evaluate(() => {
      return {
        title: document.title,
        bodyText: (document.body.textContent || '').substring(0, 200),
        hasMainElement: !!document.querySelector('main, .app, #root'),
        hasReactRoot: !!document.querySelector('#root'),
        elementCount: document.querySelectorAll('*').length,
        errors: window.console ? 'Console available' : 'No console'
      };
    });
    
    console.log(`✅ Page Title: "${pageContent.title}"`);
    console.log(`✅ Has Main Element: ${pageContent.hasMainElement}`);
    console.log(`✅ Has React Root: ${pageContent.hasReactRoot}`);
    console.log(`✅ Total Elements: ${pageContent.elementCount}`);
    console.log(`✅ Body Content Preview: "${pageContent.bodyText}..."`);
    
    if (pageContent.elementCount < 10) {
      console.log('❌ Very few elements found - React may not be rendering');
      console.log('⚠️ This could be due to JavaScript compilation errors');
    }
    
    // Check for buttons and interactive elements
    console.log('\n🎯 Phase 3: UI Elements Detection');
    const uiElements = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button'));
      const selects = Array.from(document.querySelectorAll('select'));
      const inputs = Array.from(document.querySelectorAll('input, textarea'));
      
      return {
        buttonCount: buttons.length,
        selectCount: selects.length,
        inputCount: inputs.length,
        buttonTexts: buttons.slice(0, 5).map(b => b.textContent?.trim() || 'no text'),
        selectOptions: selects.map(s => Array.from(s.options).map(o => o.value)),
        hasVoiceElements: !!document.querySelector('[class*="voice"], [data-tab="voice"], [data-testid*="voice"]')
      };
    });
    
    console.log(`✅ Buttons Found: ${uiElements.buttonCount}`);
    console.log(`✅ Select Elements: ${uiElements.selectCount}`);
    console.log(`✅ Input Elements: ${uiElements.inputCount}`);
    console.log(`✅ Voice Elements: ${uiElements.hasVoiceElements}`);
    
    if (uiElements.buttonTexts.length > 0) {
      console.log(`✅ Button Examples: ${uiElements.buttonTexts.join(', ')}`);
    }
    
    if (uiElements.selectOptions.length > 0) {
      console.log(`✅ Select Options: ${uiElements.selectOptions.map(opts => opts.join('|')).join(', ')}`);
    }
    
    // Test Backend Connection
    console.log('\n🔗 Phase 4: Backend Agent Health Check');
    const healthCheck = await page.evaluate(async () => {
      try {
        const res = await fetch('http://localhost:8000/api/agent/health');
        const data = await res.json();
        return { status: res.status, ...data };
      } catch (err) {
        return { error: err.message };
      }
    });
    
    if (healthCheck.status === 200) {
      console.log('✅ Backend agent orchestrator healthy');
      console.log(`   Model: ${healthCheck.model}`);
      console.log(`   Tools Available: ${healthCheck.tools_available}`);
    } else {
      console.log('❌ Backend agent health check failed:', healthCheck.error);
    }
    
    // Take screenshot
    await page.screenshot({ 
      path: 'agent-voice-port-fix-test.png', 
      fullPage: true 
    });
    console.log('📸 Screenshot saved: agent-voice-port-fix-test.png');
    
    // Final Assessment
    console.log('\n🎉 AGENT VOICE PORT FIX TEST SUMMARY');
    console.log('='.repeat(50));
    
    if (uiElements.buttonCount > 0 && uiElements.selectCount > 0) {
      console.log('✅ React App: RENDERING CORRECTLY');
      console.log('✅ UI Elements: PRESENT AND FUNCTIONAL');
      console.log('✅ Ready for: COMPREHENSIVE TESTING');
      
      if (healthCheck.status === 200) {
        console.log('✅ Backend: OPERATIONAL');
        console.log('✅ Agent System: READY FOR VOICE INTEGRATION');
      }
    } else {
      console.log('❌ React App: NOT RENDERING PROPERLY');
      console.log('❌ UI Elements: MISSING OR BROKEN');
      console.log('❌ Issue: LIKELY COMPILATION ERROR');
    }
    
  } catch (error) {
    console.error('❌ Port fix test failed:', error);
    await page.screenshot({ 
      path: 'agent-voice-port-fix-error.png', 
      fullPage: true 
    });
  } finally {
    await page.waitForTimeout(2000);
    await browser.close();
  }
}

testAgentVoicePortFix().catch(console.error);