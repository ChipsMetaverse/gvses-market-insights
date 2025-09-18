const playwright = require('playwright');

async function investigateCurrentUIState() {
  console.log('🔍 ULTRATHINK INVESTIGATION: Current UI State Analysis');
  console.log('='.repeat(60));
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1194, height: 867 } // Match user's screenshot dimensions
  });
  const page = await context.newPage();

  try {
    console.log('📍 Step 1: Loading application...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(3000);
    
    console.log('📍 Step 2: Navigating to voice interface...');
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(2000);
    
    console.log('📍 Step 3: Analyzing current UI state...');
    
    // Take screenshot of current state
    await page.screenshot({ path: 'current-ui-investigation.png', fullPage: false });
    
    // Check for text input field
    const input = page.locator('input[data-testid="message-input"]');
    const inputExists = await input.count() > 0;
    const inputVisible = inputExists ? await input.isVisible() : false;
    const inputBounds = inputExists && inputVisible ? await input.boundingBox() : null;
    
    console.log(`📝 Text input exists in DOM: ${inputExists}`);
    console.log(`📝 Text input visible: ${inputVisible}`);
    console.log(`📦 Text input bounds:`, inputBounds);
    
    // Check voice conversation container
    const voiceContainer = page.locator('.voice-conversation-redesigned');
    const voiceContainerExists = await voiceContainer.count() > 0;
    const voiceContainerBounds = voiceContainerExists ? await voiceContainer.boundingBox() : null;
    
    console.log(`📦 Voice container exists: ${voiceContainerExists}`);
    console.log(`📦 Voice container bounds:`, voiceContainerBounds);
    
    // Check text input section specifically
    const textInputSection = page.locator('.text-input-section-redesigned');
    const textInputSectionExists = await textInputSection.count() > 0;
    const textInputSectionVisible = textInputSectionExists ? await textInputSection.isVisible() : false;
    const textInputSectionBounds = textInputSectionExists && textInputSectionVisible ? await textInputSection.boundingBox() : null;
    
    console.log(`📝 Text input section exists: ${textInputSectionExists}`);
    console.log(`📝 Text input section visible: ${textInputSectionVisible}`);
    console.log(`📦 Text input section bounds:`, textInputSectionBounds);
    
    // Get all elements with height in the voice conversation area
    const elements = await page.evaluate(() => {
      const container = document.querySelector('.voice-conversation-redesigned');
      if (!container) return { error: 'No voice container found' };
      
      const rect = container.getBoundingClientRect();
      const children = Array.from(container.children);
      
      return {
        container: {
          top: rect.top,
          bottom: rect.bottom,
          height: rect.height,
          clientHeight: container.clientHeight,
          scrollHeight: container.scrollHeight
        },
        children: children.map(child => ({
          className: child.className,
          tagName: child.tagName,
          bounds: child.getBoundingClientRect(),
          display: window.getComputedStyle(child).display,
          visibility: window.getComputedStyle(child).visibility
        }))
      };
    });
    
    console.log('\n📊 DETAILED CONTAINER ANALYSIS:');
    console.log('Container details:', elements.container);
    console.log('\nChild elements:');
    elements.children?.forEach((child, i) => {
      console.log(`  ${i + 1}. ${child.tagName}.${child.className}`);
      console.log(`     Bounds: ${child.bounds.top}-${child.bounds.bottom}px (h=${child.bounds.height})`);
      console.log(`     Display: ${child.display}, Visibility: ${child.visibility}`);
    });
    
    // Check viewport information
    const viewportInfo = await page.evaluate(() => ({
      windowHeight: window.innerHeight,
      documentHeight: document.documentElement.scrollHeight,
      scrollY: window.scrollY
    }));
    
    console.log('\n📱 VIEWPORT INFO:');
    console.log(`Window height: ${viewportInfo.windowHeight}px`);
    console.log(`Document height: ${viewportInfo.documentHeight}px`);
    console.log(`Current scroll: ${viewportInfo.scrollY}px`);
    
    // Check if we need to scroll to see the input
    if (inputExists && !inputVisible) {
      console.log('\n🔍 INPUT EXISTS BUT NOT VISIBLE - Investigating...');
      
      // Try to scroll to the input
      await input.scrollIntoView();
      await page.waitForTimeout(500);
      
      const inputVisibleAfterScroll = await input.isVisible();
      const inputBoundsAfterScroll = inputVisibleAfterScroll ? await input.boundingBox() : null;
      
      console.log(`📝 Input visible after scroll: ${inputVisibleAfterScroll}`);
      console.log(`📦 Input bounds after scroll:`, inputBoundsAfterScroll);
      
      await page.screenshot({ path: 'current-ui-after-scroll.png', fullPage: false });
    }
    
    // Final analysis
    console.log('\n🎯 ANALYSIS SUMMARY:');
    console.log('='.repeat(40));
    console.log(`Browser viewport: ${context._options.viewport.width}x${context._options.viewport.height}`);
    console.log(`Window inner height: ${viewportInfo.windowHeight}px`);
    console.log(`Voice container: ${voiceContainerExists ? 'EXISTS' : 'MISSING'}`);
    console.log(`Text input: ${inputExists ? 'EXISTS' : 'MISSING'} | Visible: ${inputVisible}`);
    console.log(`Text input section: ${textInputSectionExists ? 'EXISTS' : 'MISSING'} | Visible: ${textInputSectionVisible}`);
    
    if (inputBounds) {
      const isWithinViewport = inputBounds.y + inputBounds.height <= viewportInfo.windowHeight;
      console.log(`Input position: ${inputBounds.y}-${inputBounds.y + inputBounds.height}px`);
      console.log(`Within viewport: ${isWithinViewport}`);
    }
    
    if (voiceContainerBounds) {
      console.log(`Container position: ${voiceContainerBounds.y}-${voiceContainerBounds.y + voiceContainerBounds.height}px`);
    }
    
    // Keep browser open for manual inspection
    console.log('\n🔍 Browser left open for manual inspection...');
    console.log('Screenshots saved: current-ui-investigation.png, current-ui-after-scroll.png');
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Investigation Error:', error.message);
    await page.screenshot({ path: 'investigation-error.png' });
  }
}

investigateCurrentUIState().catch(console.error);