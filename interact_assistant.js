const { chromium } = require('playwright');

(async () => {
  console.log('🔌 Connecting to Comet Browser...');
  
  try {
    // Connect to the existing browser instance
    const browser = await chromium.connectOverCDP('http://localhost:9222');
    const contexts = browser.contexts();
    
    if (contexts.length === 0) {
      console.log('❌ No browser contexts found. Please ensure Comet Browser is running.');
      process.exit(1);
    }
    
    const context = contexts[0];
    const pages = context.pages();
    
    if (pages.length === 0) {
      console.log('❌ No pages found in browser.');
      process.exit(1);
    }
    
    const page = pages[0];
    console.log('✅ Connected to page:', await page.title());
    
    // Take a screenshot to see what's on the page
    console.log('📸 Taking screenshot...');
    await page.screenshot({ path: 'assistant_screenshot.png', fullPage: true });
    console.log('✅ Screenshot saved to assistant_screenshot.png');
    
    // Look for chat input or assistant interface
    console.log('\n🔍 Looking for assistant interface...');
    
    // Wait a bit for page to load
    await page.waitForTimeout(2000);
    
    // Try to find common assistant UI elements
    const selectors = [
      'input[type="text"]',
      'textarea',
      '[placeholder*="message"]',
      '[placeholder*="ask"]',
      '[placeholder*="chat"]',
      '.chat-input',
      '#chat-input',
      '[data-testid="chat-input"]'
    ];
    
    let inputElement = null;
    for (const selector of selectors) {
      try {
        inputElement = await page.$(selector);
        if (inputElement) {
          console.log(`✅ Found input element: ${selector}`);
          break;
        }
      } catch (e) {
        // Continue to next selector
      }
    }
    
    if (inputElement) {
      console.log('💬 Typing test message to assistant...');
      await inputElement.click();
      await inputElement.fill('What is AAPL trading at?');
      console.log('✅ Message typed: "What is AAPL trading at?"');
      
      // Try to find and click submit button
      const submitSelectors = [
        'button[type="submit"]',
        'button:has-text("Send")',
        'button:has-text("Ask")',
        '[aria-label*="send"]',
        '.send-button'
      ];
      
      for (const selector of submitSelectors) {
        try {
          const button = await page.$(selector);
          if (button) {
            console.log(`✅ Found submit button: ${selector}`);
            await button.click();
            console.log('✅ Message sent to assistant!');
            break;
          }
        } catch (e) {
          // Continue
        }
      }
      
      // Wait for response
      console.log('⏳ Waiting for assistant response...');
      await page.waitForTimeout(5000);
      
      // Take another screenshot
      await page.screenshot({ path: 'assistant_response.png', fullPage: true });
      console.log('✅ Response screenshot saved to assistant_response.png');
      
    } else {
      console.log('ℹ️  Could not find text input. Getting page structure...');
      
      // Get all interactive elements
      const elements = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(btn => ({
          type: 'button',
          text: btn.textContent?.trim().substring(0, 50),
          id: btn.id,
          class: btn.className
        }));
        
        const inputs = Array.from(document.querySelectorAll('input, textarea')).map(input => ({
          type: input.type || 'textarea',
          placeholder: input.placeholder,
          id: input.id,
          class: input.className
        }));
        
        return { buttons, inputs };
      });
      
      console.log('\n📋 Found interactive elements:');
      console.log('Buttons:', JSON.stringify(elements.buttons, null, 2));
      console.log('Inputs:', JSON.stringify(elements.inputs, null, 2));
    }
    
    console.log('\n✅ Browser assistant interaction complete!');
    console.log('Check the screenshots for visual confirmation.');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    // If CDP connection fails, try launching with debugging
    console.log('\n💡 Tip: To enable remote debugging, relaunch with:');
    console.log('--remote-debugging-port=9222');
  }
})();

