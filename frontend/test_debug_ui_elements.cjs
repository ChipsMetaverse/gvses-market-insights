const playwright = require('playwright');

async function debugUIElements() {
  console.log('🔍 DEBUGGING: UI Elements After Provider Switch');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to the app
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    console.log('✅ App loaded');
    
    // Get all elements before provider switch
    console.log('\n=== BEFORE PROVIDER SWITCH ===');
    const allInputsBefore = await page.locator('input').count();
    const allButtonsBefore = await page.locator('button').count();
    const allSelectsBefore = await page.locator('select').count();
    console.log(`📊 Elements before: ${allInputsBefore} inputs, ${allButtonsBefore} buttons, ${allSelectsBefore} selects`);
    
    // Switch to OpenAI provider
    const providerDropdown = page.locator('[data-testid="provider-dropdown"]');
    if (await providerDropdown.isVisible()) {
      await providerDropdown.selectOption('openai');
      console.log('🤖 Switched to OpenAI provider');
      await page.waitForTimeout(1000);
    }
    
    // Get all elements after provider switch
    console.log('\n=== AFTER PROVIDER SWITCH ===');
    const allInputsAfter = await page.locator('input').count();
    const allButtonsAfter = await page.locator('button').count();
    const allSelectsAfter = await page.locator('select').count();
    console.log(`📊 Elements after: ${allInputsAfter} inputs, ${allButtonsAfter} buttons, ${allSelectsAfter} selects`);
    
    // Try to find toggles with different selectors
    console.log('\n=== TOGGLE SEARCH ===');
    const toggles = [
      { name: 'connection-toggle', selector: '[data-testid="connection-toggle"]' },
      { name: 'voice-toggle-switch', selector: '[data-testid="voice-toggle-switch"]' },
      { name: 'checkbox inputs', selector: 'input[type="checkbox"]' },
      { name: 'toggle containers', selector: '.toggle-switch-container' },
      { name: 'toggle switches', selector: '.toggle-switch' },
      { name: 'toggle inputs', selector: '.toggle-switch input' }
    ];
    
    for (const toggle of toggles) {
      const elements = page.locator(toggle.selector);
      const count = await elements.count();
      const visible = count > 0 ? await elements.first().isVisible() : false;
      console.log(`🔘 ${toggle.name}: ${count} found, first visible: ${visible}`);
      
      if (count > 0 && visible) {
        // Try to get some info about this element
        const element = elements.first();
        const isEnabled = await element.isEnabled();
        const isChecked = await element.isChecked().catch(() => 'N/A');
        console.log(`   ↳ enabled: ${isEnabled}, checked: ${isChecked}`);
      }
    }
    
    // Look for voice-related elements
    console.log('\n=== VOICE ELEMENTS SEARCH ===');
    const voiceElements = [
      { name: 'voice-interface', selector: '[data-testid="voice-interface"]' },
      { name: 'voice sections', selector: '.voice-section, .voice-section-redesigned' },
      { name: 'voice controls', selector: '.voice-controls, .voice-controls-row' },
      { name: 'voice labels containing "Connect"', selector: ':has-text("Connect"):visible' }
    ];
    
    for (const element of voiceElements) {
      const elements = page.locator(element.selector);
      const count = await elements.count();
      const visible = count > 0 ? await elements.first().isVisible() : false;
      console.log(`🎤 ${element.name}: ${count} found, first visible: ${visible}`);
    }
    
    // Get all text content to see what's actually displayed
    console.log('\n=== VISIBLE TEXT CONTENT ===');
    const voiceSection = page.locator('[data-testid="voice-interface"]');
    if (await voiceSection.isVisible()) {
      const textContent = await voiceSection.textContent();
      console.log('📝 Voice interface text:', textContent);
    }
    
    // Take screenshot for visual debugging
    await page.screenshot({ path: 'ui-debug-elements.png', fullPage: true });
    console.log('📸 Screenshot saved: ui-debug-elements.png');
    
  } catch (error) {
    console.error('❌ Debug error:', error);
  } finally {
    await browser.close();
  }
}

debugUIElements().catch(console.error);