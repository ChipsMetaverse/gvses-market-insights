const playwright = require('playwright');

async function manualUserTest() {
  console.log('🎯 MANUAL USER VERIFICATION TEST');
  console.log('Testing real-world trading conversation quality\n');
  
  const browser = await playwright.chromium.launch({ 
    headless: false,
    slowMo: 1000  // Slow down for easier observation
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Monitor for AI responses and tool calls
  let responseCount = 0;
  let toolCalls = 0;
  
  page.on('console', (msg) => {
    const text = msg.text();
    if (text.includes('Tool called:') || text.includes('tool_call_start')) {
      toolCalls++;
      console.log(`🔧 Tool Call ${toolCalls}: ${text.substring(0, 100)}...`);
    } else if (text.includes('Item completed:') || text.includes('conversation.updated')) {
      responseCount++;
      console.log(`💬 Response Event ${responseCount}`);
    }
  });

  try {
    console.log('📍 Setting up trading environment...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // Navigate to voice interface
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    // Connect to OpenAI
    await page.selectOption('[data-testid="provider-dropdown"]', 'openai');
    await page.click('.toggle-switch-container');
    console.log('🔌 Connecting to AI trading assistant...');
    await page.waitForTimeout(10000); // Give connection time
    
    // Check connection status
    const status = await page.locator('.toggle-switch-container .toggle-label').textContent();
    console.log(`🔍 Connection Status: "${status}"`);
    
    if (!status?.includes('Connected')) {
      throw new Error('Failed to establish AI connection');
    }
    
    console.log('\n🎯 READY FOR MANUAL TESTING');
    console.log('═══════════════════════════════════════');
    console.log('👨‍💼 You are now connected to the AI trading assistant');
    console.log('📱 Try these realistic queries:');
    console.log('   1. "What\'s Tesla\'s current stock price?"');
    console.log('   2. "Show me Apple on the chart"');
    console.log('   3. "Give me the latest market news"');
    console.log('   4. "What are your thoughts on NVIDIA?"');
    console.log('   5. "Compare Microsoft vs Google stock"');
    console.log('');
    console.log('🔍 Watch for:');
    console.log('   • Real stock prices and data');
    console.log('   • Professional trading advice');
    console.log('   • Chart updates when requested');
    console.log('   • Current market insights');
    console.log('');
    console.log('⚡ This window will stay open for manual testing...');
    console.log('   Press Ctrl+C when finished testing');
    
    // Keep monitoring while user tests manually
    let lastToolCount = 0;
    let lastResponseCount = 0;
    
    const monitorInterval = setInterval(() => {
      if (toolCalls > lastToolCount) {
        console.log(`📊 Active: ${toolCalls - lastToolCount} new tool calls detected`);
        lastToolCount = toolCalls;
      }
      if (responseCount > lastResponseCount) {
        console.log(`🤖 Active: ${responseCount - lastResponseCount} new AI responses`);
        lastResponseCount = responseCount;
      }
    }, 5000);
    
    // Test one automatic query to demonstrate functionality
    console.log('\n🚀 AUTOMATED DEMO QUERY...');
    const input = page.locator('input[data-testid="message-input"]');
    await input.type('What is the current Tesla stock price and how is it trending?');
    await page.click('button[data-testid="send-button"]');
    console.log('📤 Sent demo query about Tesla...');
    
    // Wait for demo response
    await page.waitForTimeout(15000);
    
    // Check if conversation has any messages
    const messageCount = await page.locator('[data-testid="messages-container"] .conversation-message-enhanced').count();
    console.log(`\n📊 DEMO RESULTS:`);
    console.log(`   Messages in conversation: ${messageCount}`);
    console.log(`   Tool calls detected: ${toolCalls}`);
    console.log(`   Response events: ${responseCount}`);
    
    if (messageCount > 0) {
      console.log('✅ AI conversation system is working!');
      // Get a sample of the latest message
      const latestMessage = await page.locator('[data-testid="messages-container"] .conversation-message-enhanced').last().locator('.message-text-enhanced').textContent();
      console.log(`📖 Sample response: "${latestMessage?.substring(0, 150)}..."`);
    } else {
      console.log('⚠️  No messages visible in UI - check conversation system');
    }
    
    console.log('\n🎯 MANUAL TESTING ACTIVE');
    console.log('═══════════════════════════════════════');
    console.log('The application is ready for your testing...');
    
    // Keep running for manual testing
    await new Promise(() => {}); // Keep alive indefinitely
    
  } catch (error) {
    console.error('❌ Setup Error:', error.message);
  } finally {
    // This won't execute due to infinite wait above
  }
}

manualUserTest().catch(console.error);