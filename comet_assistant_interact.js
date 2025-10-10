const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Connecting to Comet Browser Assistant...');
  
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
  await page.waitForTimeout(2000);
  
  console.log('✅ Page loaded');
  
  // Take screenshot before opening assistant
  await page.screenshot({ path: 'before_assistant.png' });
  console.log('📸 Screenshot: before_assistant.png');
  
  console.log('\n🎯 Opening Comet Assistant with Cmd+A...');
  
  // Toggle Comet Assistant using keyboard shortcut
  await page.keyboard.press('Meta+A');  // Meta = Command key on Mac
  await page.waitForTimeout(1000);
  
  // Take screenshot with assistant open
  await page.screenshot({ path: 'assistant_toggled.png' });
  console.log('📸 Screenshot: assistant_toggled.png');
  
  console.log('\n💬 Typing message to Comet Assistant...');
  
  // Type a message to the assistant
  const message = 'What stocks are displayed on this trading dashboard?';
  await page.keyboard.type(message);
  await page.waitForTimeout(500);
  
  await page.screenshot({ path: 'assistant_message_typed.png' });
  console.log('📸 Screenshot: assistant_message_typed.png');
  console.log(`✏️  Message typed: "${message}"`);
  
  // Send the message (usually Enter)
  console.log('\n📤 Sending message...');
  await page.keyboard.press('Enter');
  
  console.log('⏳ Waiting for Comet Assistant response...');
  await page.waitForTimeout(5000);
  
  await page.screenshot({ path: 'assistant_response.png' });
  console.log('📸 Screenshot: assistant_response.png');
  
  console.log('\n✅ Interaction with Comet Assistant complete!');
  console.log('📋 Check the screenshots to see the conversation.');
  console.log('\n💡 Additional Comet Assistant commands:');
  console.log('  - Cmd+A: Toggle Assistant');
  console.log('  - Cmd+S: Summarize the current webpage');
  
  console.log('\n🎯 Trying page summarization (Cmd+S)...');
  await page.keyboard.press('Meta+S');
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: 'page_summarized.png' });
  console.log('📸 Screenshot: page_summarized.png');
  
  console.log('\n✅ All Comet Assistant features demonstrated!');
  console.log('Browser will stay open for 30 seconds...');
  await page.waitForTimeout(30000);
  
  await browser.close();
  console.log('👋 Browser closed');
  
})().catch(error => {
  console.error('❌ Error:', error.message);
  console.error(error.stack);
  process.exit(1);
});

