const playwright = require('playwright');

async function diagnosticInputVisibility() {
  console.log('🔍 COMPREHENSIVE DIAGNOSTIC: Text Input Visibility Issue');
  console.log('='.repeat(70));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1400, height: 900 }
  });
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Loading application and taking baseline screenshot...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'diagnostic-01_initial_load.png', fullPage: true });
    
    console.log('📍 Step 2: Navigating to voice interface...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'diagnostic-02_voice_tab.png', fullPage: true });
    
    console.log('📍 Step 3: Checking DOM structure BEFORE connection...');
    
    // Check if input element exists in DOM
    const inputExists = await page.locator('input[data-testid="message-input"]').count();
    console.log(`📝 Input element count in DOM: ${inputExists}`);
    
    const textSection = await page.locator('.text-input-section-redesigned').count();
    console.log(`📝 Text input section count: ${textSection}`);
    
    // Check voice conversation container
    const voiceContainer = await page.locator('.voice-conversation-redesigned');
    const containerBounds = await voiceContainer.boundingBox();
    console.log(`📦 Voice container bounds:`, containerBounds);
    
    console.log('📍 Step 4: Connecting to OpenAI...');
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000);
    
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    await page.screenshot({ path: 'diagnostic-03_connected.png', fullPage: true });
    
    console.log('📍 Step 5: Detailed DOM analysis AFTER connection...');
    
    // Check input visibility and properties
    const inputAfter = await page.locator('input[data-testid="message-input"]');
    const inputCount = await inputAfter.count();
    console.log(`📝 Input element count after connection: ${inputCount}`);
    
    if (inputCount > 0) {
      const isVisible = await inputAfter.isVisible();
      const isEnabled = await inputAfter.isEnabled();
      const bounds = await inputAfter.boundingBox();
      
      console.log(`📝 Input visible: ${isVisible}`);
      console.log(`📝 Input enabled: ${isEnabled}`);
      console.log(`📦 Input bounds:`, bounds);
      
      // Get computed styles
      const styles = await inputAfter.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          display: computed.display,
          visibility: computed.visibility,
          opacity: computed.opacity,
          zIndex: computed.zIndex,
          position: computed.position,
          overflow: computed.overflow,
          height: computed.height,
          width: computed.width
        };
      });
      console.log(`🎨 Input computed styles:`, styles);
      
      // Check parent container styles
      const parentStyles = await page.locator('.text-input-section-redesigned').evaluate(el => {
        if (!el) return 'Not found';
        const computed = window.getComputedStyle(el);
        return {
          display: computed.display,
          visibility: computed.visibility,
          opacity: computed.opacity,
          overflow: computed.overflow,
          height: computed.height,
          maxHeight: computed.maxHeight
        };
      });
      console.log(`🎨 Text section styles:`, parentStyles);
      
      // Check voice conversation container
      const containerStyles = await voiceContainer.evaluate(el => {
        const computed = window.getComputedStyle(el);
        return {
          display: computed.display,
          overflow: computed.overflow,
          overflowY: computed.overflowY,
          height: computed.height,
          maxHeight: computed.maxHeight,
          minHeight: computed.minHeight
        };
      });
      console.log(`🎨 Voice container styles:`, containerStyles);
      
    } else {
      console.log('❌ Input element not found in DOM');
    }
    
    console.log('📍 Step 6: Checking viewport and scroll position...');
    const viewportSize = page.viewportSize();
    console.log(`📱 Viewport size:`, viewportSize);
    
    const scrollY = await page.evaluate(() => window.scrollY);
    const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);
    const clientHeight = await page.evaluate(() => document.documentElement.clientHeight);
    
    console.log(`📜 Scroll Y: ${scrollY}`);
    console.log(`📜 Scroll height: ${scrollHeight}`);
    console.log(`📜 Client height: ${clientHeight}`);
    
    // Try scrolling to bottom
    console.log('📍 Step 7: Scrolling to bottom to find input...');
    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'diagnostic-04_scrolled_bottom.png', fullPage: true });
    
    const inputVisibleAfterScroll = await inputAfter.isVisible();
    console.log(`📝 Input visible after scroll: ${inputVisibleAfterScroll}`);
    
    // Check all elements with text-input classes
    console.log('📍 Step 8: Finding all text input related elements...');
    const allInputElements = await page.$$eval('[class*="text-input"]', elements => 
      elements.map(el => ({
        tagName: el.tagName,
        className: el.className,
        visible: el.offsetParent !== null,
        bounds: el.getBoundingClientRect()
      }))
    );
    console.log(`🔍 All text-input elements:`, allInputElements);
    
    // Take final diagnostic screenshot
    await page.screenshot({ path: 'diagnostic-05_final_analysis.png', fullPage: true });
    
    console.log('\n🔍 DIAGNOSTIC SUMMARY:');
    console.log('='.repeat(50));
    console.log(`Connection Status: ${status}`);
    console.log(`Input elements in DOM: ${inputCount}`);
    if (inputCount > 0) {
      console.log(`Input visible: ${await inputAfter.isVisible()}`);
      console.log(`Input bounds available: ${(await inputAfter.boundingBox()) !== null}`);
    }
    console.log('\n📸 Screenshots saved for analysis:');
    console.log('- diagnostic-01_initial_load.png');
    console.log('- diagnostic-02_voice_tab.png'); 
    console.log('- diagnostic-03_connected.png');
    console.log('- diagnostic-04_scrolled_bottom.png');
    console.log('- diagnostic-05_final_analysis.png');
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser left open for manual inspection...');
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Diagnostic Error:', error.message);
    await page.screenshot({ path: 'diagnostic-error.png', fullPage: true });
  }
}

diagnosticInputVisibility().catch(console.error);