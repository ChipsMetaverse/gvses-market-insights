const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔍 Testing Voice Assistant Text Input\n');
  console.log('=' .repeat(50));
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Check for Voice Assistant panel
  console.log('\n📊 VOICE ASSISTANT PANEL CHECK:');
  const voicePanel = await page.$('.voice-conversation-section');
  if (voicePanel) {
    console.log('✅ Voice Assistant panel found');
  } else {
    console.log('❌ Voice Assistant panel NOT found');
  }
  
  // Check for text input field
  console.log('\n📝 TEXT INPUT FIELD CHECK:');
  const textInput = await page.$('.voice-text-input');
  if (textInput) {
    console.log('✅ Text input field found');
    
    // Check placeholder text
    const placeholder = await textInput.getAttribute('placeholder');
    console.log(`   Placeholder: "${placeholder}"`);
    
    // Check if enabled
    const isDisabled = await textInput.isDisabled();
    console.log(`   Enabled: ${!isDisabled ? '✅ Yes' : '❌ No'}`);
  } else {
    console.log('❌ Text input field NOT found');
  }
  
  // Check for send button
  console.log('\n🚀 SEND BUTTON CHECK:');
  const sendButton = await page.$('.voice-send-button');
  if (sendButton) {
    console.log('✅ Send button found');
    
    // Check if initially disabled (no text)
    const isDisabled = await sendButton.isDisabled();
    console.log(`   Initially disabled: ${isDisabled ? '✅ Yes (correct)' : '❌ No'}`);
  } else {
    console.log('❌ Send button NOT found');
  }
  
  // Test typing in the input field
  console.log('\n⌨️  TESTING TEXT INPUT:');
  if (textInput) {
    await textInput.fill('Test message from Playwright');
    await page.waitForTimeout(500);
    
    const value = await textInput.inputValue();
    console.log(`   Typed text: "${value}"`);
    
    // Check if send button is now enabled
    if (sendButton) {
      const isDisabled = await sendButton.isDisabled();
      console.log(`   Send button enabled: ${!isDisabled ? '✅ Yes' : '❌ No'}`);
    }
  }
  
  // Test sending a message
  console.log('\n📤 TESTING MESSAGE SEND:');
  if (textInput && sendButton) {
    // Type a message
    await textInput.fill('Hello from text input!');
    await page.waitForTimeout(300);
    
    // Click send button
    await sendButton.click();
    await page.waitForTimeout(1000);
    
    // Check if input was cleared
    const valueAfterSend = await textInput.inputValue();
    console.log(`   Input cleared after send: ${valueAfterSend === '' ? '✅ Yes' : '❌ No'}`);
    
    // Check if message appears in chat
    const messages = await page.$$('.conversation-message-enhanced');
    console.log(`   Messages in chat: ${messages.length}`);
    
    if (messages.length > 0) {
      // Get last message text
      const lastMessage = messages[messages.length - 1];
      const messageText = await lastMessage.textContent();
      console.log(`   Last message: "${messageText.substring(0, 50)}..."`);
    }
  }
  
  // Test Enter key to send
  console.log('\n⏎  TESTING ENTER KEY:');
  if (textInput) {
    await textInput.fill('Testing Enter key');
    await page.waitForTimeout(300);
    
    // Press Enter
    await textInput.press('Enter');
    await page.waitForTimeout(1000);
    
    // Check if input was cleared
    const valueAfterEnter = await textInput.inputValue();
    console.log(`   Input cleared after Enter: ${valueAfterEnter === '' ? '✅ Yes' : '❌ No'}`);
  }
  
  // Check connection status
  console.log('\n🔌 CONNECTION STATUS:');
  const fab = await page.$('.voice-fab');
  if (fab) {
    const isActive = await fab.evaluate(el => el.classList.contains('active'));
    console.log(`   Voice connected: ${isActive ? '✅ Yes' : '❌ No'}`);
    
    if (!isActive) {
      console.log('   ⚠️  Voice is disconnected - messages will show offline notice');
    }
  }
  
  // Take screenshot
  console.log('\n📸 CAPTURING SCREENSHOT:');
  await page.screenshot({ 
    path: 'frontend/text-input-test.png', 
    fullPage: false 
  });
  console.log('   ✅ Screenshot saved: text-input-test.png');
  
  console.log('\n' + '=' .repeat(50));
  console.log('✅ TEXT INPUT TEST COMPLETE');
  console.log('=' .repeat(50));
  
  await page.waitForTimeout(3000);
  await browser.close();
})();