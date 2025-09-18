const { chromium } = require('playwright');

async function testMessageAccumulation() {
  console.log('🔍 Testing OpenAI Message Accumulation Fix...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 100
  });
  
  const page = await browser.newContext().then(ctx => ctx.newPage());
  
  // Track message counts
  let messagesBefore = 0;
  let messagesAfter = 0;
  let fragmentedMessages = false;
  
  // Monitor console for debugging
  page.on('console', msg => {
    const text = msg.text();
    
    // Check for message saving logs
    if (text.includes('Saved') && text.includes('messages to localStorage')) {
      const match = text.match(/Saved (\d+) messages/);
      if (match) {
        const count = parseInt(match[1]);
        console.log(`📊 Message count: ${count}`);
        
        // Check for excessive messages (fragmentation)
        if (count > 100) {
          fragmentedMessages = true;
          console.log('⚠️  WARNING: Excessive messages detected (possible fragmentation)');
        }
      }
    }
    
    // Log transcript accumulation
    if (text.includes('Accumulating transcript')) {
      console.log('✅ Transcript accumulation detected');
    }
  });
  
  // Navigate to app
  console.log('📍 Loading http://localhost:5174...');
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(1000);
  
  // Click Voice tab
  console.log('📍 Activating Voice tab...');
  await page.click('button:has-text("Voice + Manual Control")');
  await page.waitForTimeout(500);
  
  // Select OpenAI provider
  console.log('📍 Selecting OpenAI provider...');
  const providerDropdown = await page.$('.provider-dropdown');
  if (providerDropdown) {
    await page.selectOption('.provider-dropdown', 'openai');
    await page.waitForTimeout(500);
  }
  
  // Get initial message count
  const initialMessages = await page.$$('.message');
  messagesBefore = initialMessages.length;
  console.log(`📝 Initial message count: ${messagesBefore}`);
  
  // Connect to OpenAI
  console.log('\n📍 Connecting to OpenAI...');
  await page.click('.toggle-switch-container');
  await page.waitForTimeout(3000); // Wait for connection
  
  // Send a text message
  console.log('📍 Sending test message...');
  const textInput = await page.$('input[placeholder*="Type a message"]');
  if (textInput) {
    await textInput.fill('What is the current price of Tesla stock?');
    await page.keyboard.press('Enter');
    console.log('✅ Message sent');
    
    // Wait for response
    console.log('⏳ Waiting for response...');
    await page.waitForTimeout(5000);
    
    // Count messages after response
    const finalMessages = await page.$$('.message');
    messagesAfter = finalMessages.length;
    console.log(`📝 Final message count: ${messagesAfter}`);
    
    // Calculate new messages
    const newMessages = messagesAfter - messagesBefore;
    console.log(`📊 New messages added: ${newMessages}`);
    
    // Check message content for fragmentation
    const lastMessages = await page.$$eval('.message', messages => {
      return messages.slice(-10).map(msg => ({
        role: msg.classList.contains('user') ? 'user' : 'assistant',
        content: msg.querySelector('.message-content')?.textContent || '',
        timestamp: msg.querySelector('.message-time')?.textContent || ''
      }));
    });
    
    console.log('\n📋 Last few messages:');
    lastMessages.forEach((msg, i) => {
      const preview = msg.content.length > 50 ? 
        msg.content.substring(0, 50) + '...' : 
        msg.content;
      console.log(`  ${i + 1}. [${msg.role}] ${preview} (${msg.timestamp})`);
      
      // Check for single-word messages (fragmentation)
      if (msg.content.split(' ').length === 1 && msg.role === 'assistant') {
        console.log('     ⚠️  Single word message detected!');
      }
      
      // Check for Invalid Date
      if (msg.timestamp === 'Invalid Date') {
        console.log('     ⚠️  Invalid timestamp detected!');
      }
    });
    
    // Take screenshot
    await page.screenshot({ path: 'message-accumulation-test.png' });
    
    // Final verdict
    console.log('\n' + '='.repeat(50));
    console.log('📊 TEST RESULTS:');
    console.log('='.repeat(50));
    
    if (newMessages === 2) {
      console.log('✅ PASS: Expected 2 messages (1 user + 1 assistant)');
    } else if (newMessages > 10) {
      console.log(`❌ FAIL: Too many messages (${newMessages}) - likely fragmented`);
    } else {
      console.log(`⚠️  WARNING: ${newMessages} messages added (expected 2)`);
    }
    
    if (fragmentedMessages) {
      console.log('❌ FAIL: Message fragmentation detected (100+ messages)');
    } else {
      console.log('✅ PASS: No excessive fragmentation detected');
    }
    
    console.log('='.repeat(50));
    console.log('📸 Screenshot saved: message-accumulation-test.png');
    
  } else {
    console.log('❌ Could not find text input field');
  }
  
  await page.waitForTimeout(2000);
  await browser.close();
}

testMessageAccumulation().catch(console.error);