const { chromium } = require('playwright');
const readline = require('readline');

(async () => {
  console.log('🚀 Launching Comet Browser with Interactive Assistant...');
  
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/Applications/Comet.app/Contents/MacOS/Comet',
    args: ['--start-maximized']
  });
  
  const context = await browser.newContext({
    viewport: null,
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  console.log('📡 Navigating to http://localhost:5175...');
  await page.goto('http://localhost:5175', { waitUntil: 'networkidle' });
  
  console.log('✅ Comet Browser opened successfully!');
  console.log('🎤 Voice assistant ready at http://localhost:5175');
  
  // Wait for page to fully load
  await page.waitForTimeout(3000);
  
  // Take initial screenshot
  await page.screenshot({ path: 'dashboard_loaded.png', fullPage: false });
  console.log('📸 Screenshot saved: dashboard_loaded.png');
  
  // Find all interactive elements
  console.log('\n🔍 Analyzing page structure...');
  const pageInfo = await page.evaluate(() => {
    const buttons = Array.from(document.querySelectorAll('button')).map((btn, i) => ({
      index: i,
      text: btn.textContent?.trim().substring(0, 60),
      id: btn.id,
      ariaLabel: btn.getAttribute('aria-label'),
      class: btn.className.substring(0, 100)
    }));
    
    const inputs = Array.from(document.querySelectorAll('input, textarea')).map((input, i) => ({
      index: i,
      type: input.type || 'textarea',
      placeholder: input.placeholder,
      id: input.id,
      name: input.name,
      ariaLabel: input.getAttribute('aria-label')
    }));
    
    return { 
      title: document.title,
      buttons: buttons.filter(b => b.text || b.ariaLabel),
      inputs 
    };
  });
  
  console.log('\n📋 Page Information:');
  console.log('Title:', pageInfo.title);
  console.log('\n🎯 Found Buttons:', pageInfo.buttons.length);
  pageInfo.buttons.forEach(btn => {
    console.log(`  [${btn.index}] ${btn.text || btn.ariaLabel || btn.id || 'Unknown'}`);
  });
  
  console.log('\n📝 Found Inputs:', pageInfo.inputs.length);
  pageInfo.inputs.forEach(input => {
    console.log(`  [${input.index}] ${input.type}: ${input.placeholder || input.ariaLabel || input.id || input.name || 'Unknown'}`);
  });
  
  // Look for chat/assistant input
  console.log('\n🤖 Looking for assistant interface...');
  
  // Try to find chat input with various strategies
  const chatInput = await page.locator('input[type="text"], textarea').first();
  const chatInputCount = await page.locator('input[type="text"], textarea').count();
  
  if (chatInputCount > 0) {
    console.log(`✅ Found ${chatInputCount} text input field(s)`);
    
    // Create interactive prompt
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    console.log('\n💬 Interactive Assistant Mode');
    console.log('Type your message and press Enter to send to the assistant.');
    console.log('Type "screenshot" to take a screenshot.');
    console.log('Type "exit" to close.\n');
    
    const askQuestion = () => {
      rl.question('You: ', async (answer) => {
        if (answer.toLowerCase() === 'exit') {
          console.log('👋 Closing browser...');
          await browser.close();
          rl.close();
          process.exit(0);
        } else if (answer.toLowerCase() === 'screenshot') {
          const filename = `screenshot_${Date.now()}.png`;
          await page.screenshot({ path: filename });
          console.log(`📸 Screenshot saved: ${filename}\n`);
          askQuestion();
        } else if (answer.trim()) {
          try {
            console.log('⏳ Sending message to assistant...');
            
            // Click and fill the input
            await chatInput.first().click();
            await chatInput.first().fill(answer);
            
            // Try to find and click send button
            const sendButton = await page.locator('button:has-text("Send"), button[type="submit"], button:has([aria-label*="send"])').first();
            if (await sendButton.count() > 0) {
              await sendButton.click();
              console.log('✅ Message sent! Waiting for response...\n');
              await page.waitForTimeout(2000);
            } else {
              // Try pressing Enter
              await page.keyboard.press('Enter');
              console.log('✅ Message sent! Waiting for response...\n');
              await page.waitForTimeout(2000);
            }
            
            // Get the latest response
            const response = await page.evaluate(() => {
              const responses = document.querySelectorAll('.response, .message, .chat-message, [class*="response"], [class*="message"]');
              if (responses.length > 0) {
                const last = responses[responses.length - 1];
                return last.textContent?.trim().substring(0, 500) || 'No text found';
              }
              return 'Could not detect response element';
            });
            
            console.log('🤖 Assistant:', response);
            console.log();
            
          } catch (error) {
            console.log('❌ Error sending message:', error.message);
          }
          askQuestion();
        } else {
          askQuestion();
        }
      });
    };
    
    askQuestion();
    
  } else {
    console.log('⚠️  No text input found. The page may need voice interaction.');
    console.log('💡 Browser will stay open. Press Ctrl+C to close.');
    
    // Keep browser open
    await new Promise(() => {});
  }
  
})().catch(error => {
  console.error('❌ Error:', error);
  process.exit(1);
});

