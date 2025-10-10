const { chromium } = require('playwright');

(async () => {
  console.log('🔌 Connecting to running Comet Browser...');
  
  try {
    // Launch a new connection to interact with the page
    const browser = await chromium.launch({
      headless: false,
      executablePath: '/Applications/Comet.app/Contents/MacOS/Comet'
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    console.log('📡 Navigating to the trading dashboard...');
    await page.goto('http://localhost:5175', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    console.log('🔍 Analyzing page for assistant interface...');
    
    // Get all elements on the page
    const pageStructure = await page.evaluate(() => {
      const result = {
        title: document.title,
        url: window.location.href,
        elements: {
          textInputs: [],
          textareas: [],
          buttons: [],
          voiceButtons: []
        }
      };
      
      // Find text inputs
      document.querySelectorAll('input[type="text"], input:not([type])').forEach((input, i) => {
        result.elements.textInputs.push({
          index: i,
          id: input.id,
          placeholder: input.placeholder,
          ariaLabel: input.getAttribute('aria-label'),
          name: input.name,
          value: input.value,
          visible: input.offsetParent !== null
        });
      });
      
      // Find textareas
      document.querySelectorAll('textarea').forEach((textarea, i) => {
        result.elements.textareas.push({
          index: i,
          id: textarea.id,
          placeholder: textarea.placeholder,
          ariaLabel: textarea.getAttribute('aria-label'),
          name: textarea.name,
          visible: textarea.offsetParent !== null
        });
      });
      
      // Find buttons
      document.querySelectorAll('button').forEach((btn, i) => {
        const text = btn.textContent?.trim();
        if (text) {
          result.elements.buttons.push({
            index: i,
            text: text.substring(0, 50),
            id: btn.id,
            ariaLabel: btn.getAttribute('aria-label'),
            className: btn.className,
            visible: btn.offsetParent !== null
          });
        }
      });
      
      // Look for voice-related buttons
      result.elements.buttons.forEach(btn => {
        if (btn.text?.toLowerCase().includes('voice') || 
            btn.text?.toLowerCase().includes('mic') ||
            btn.ariaLabel?.toLowerCase().includes('voice') ||
            btn.ariaLabel?.toLowerCase().includes('microphone')) {
          result.elements.voiceButtons.push(btn);
        }
      });
      
      return result;
    });
    
    console.log('\n📊 Dashboard Structure:');
    console.log('Title:', pageStructure.title);
    console.log('URL:', pageStructure.url);
    console.log('\n📝 Text Inputs:', pageStructure.elements.textInputs.length);
    pageStructure.elements.textInputs.forEach(input => {
      console.log(`  - ${input.placeholder || input.ariaLabel || input.id || input.name || 'Unnamed'} ${input.visible ? '(visible)' : '(hidden)'}`);
    });
    
    console.log('\n📝 Textareas:', pageStructure.elements.textareas.length);
    pageStructure.elements.textareas.forEach(textarea => {
      console.log(`  - ${textarea.placeholder || textarea.ariaLabel || textarea.id || textarea.name || 'Unnamed'} ${textarea.visible ? '(visible)' : '(hidden)'}`);
    });
    
    console.log('\n🎤 Voice Buttons:', pageStructure.elements.voiceButtons.length);
    pageStructure.elements.voiceButtons.forEach(btn => {
      console.log(`  - ${btn.text || btn.ariaLabel}`);
    });
    
    console.log('\n🔘 All Buttons (first 15):', pageStructure.elements.buttons.slice(0, 15).length);
    pageStructure.elements.buttons.slice(0, 15).forEach(btn => {
      console.log(`  - ${btn.text} ${btn.visible ? '✓' : '✗'}`);
    });
    
    // Try to send a test message
    console.log('\n💬 Attempting to send test message to assistant...');
    
    // Strategy 1: Look for visible text input
    const visibleInputs = pageStructure.elements.textInputs.filter(i => i.visible);
    const visibleTextareas = pageStructure.elements.textareas.filter(i => i.visible);
    
    if (visibleInputs.length > 0 || visibleTextareas.length > 0) {
      console.log('✅ Found input field, attempting to send message...');
      
      // Try first visible input
      const inputField = await page.locator('input[type="text"]:visible, textarea:visible').first();
      
      await inputField.click();
      await inputField.fill('What is AAPL trading at?');
      console.log('✏️  Typed: "What is AAPL trading at?"');
      
      // Take screenshot
      await page.screenshot({ path: 'message_typed.png' });
      console.log('📸 Screenshot: message_typed.png');
      
      // Try to submit - look for send/submit button
      const sendButton = await page.locator('button:has-text("Send"), button:has-text("Submit"), button[type="submit"]').first();
      const sendButtonCount = await page.locator('button:has-text("Send"), button:has-text("Submit"), button[type="submit"]').count();
      
      if (sendButtonCount > 0) {
        await sendButton.click();
        console.log('✅ Clicked send button');
      } else {
        // Try Enter key
        await page.keyboard.press('Enter');
        console.log('✅ Pressed Enter');
      }
      
      // Wait for response
      console.log('⏳ Waiting for assistant response...');
      await page.waitForTimeout(5000);
      
      // Take screenshot of response
      await page.screenshot({ path: 'assistant_response.png', fullPage: true });
      console.log('📸 Screenshot: assistant_response.png');
      
      // Try to extract response text
      const responseText = await page.evaluate(() => {
        // Look for common response selectors
        const selectors = [
          '.response',
          '.message',
          '.assistant-message',
          '[data-role="assistant"]',
          '.chat-response',
          '[class*="response"]',
          '[class*="message"]'
        ];
        
        for (const selector of selectors) {
          const elements = document.querySelectorAll(selector);
          if (elements.length > 0) {
            const last = elements[elements.length - 1];
            return {
              found: true,
              selector,
              text: last.textContent?.trim().substring(0, 500)
            };
          }
        }
        
        return { found: false };
      });
      
      if (responseText.found) {
        console.log('\n🤖 Assistant Response:');
        console.log(responseText.text);
      } else {
        console.log('\n⚠️  Could not locate response element automatically');
        console.log('Check assistant_response.png for visual confirmation');
      }
      
    } else if (pageStructure.elements.voiceButtons.length > 0) {
      console.log('🎤 This appears to be a voice-only interface');
      console.log('Voice button found:', pageStructure.elements.voiceButtons[0].text);
      
      // Take screenshot
      await page.screenshot({ path: 'voice_interface.png' });
      console.log('📸 Screenshot: voice_interface.png');
    } else {
      console.log('⚠️  No obvious input method found');
      await page.screenshot({ path: 'no_input_found.png' });
      console.log('📸 Screenshot: no_input_found.png');
    }
    
    console.log('\n✅ Analysis complete!');
    console.log('Browser will stay open for 30 seconds for manual inspection...');
    await page.waitForTimeout(30000);
    
    await browser.close();
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    console.error(error.stack);
  }
})();

