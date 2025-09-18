const { chromium } = require('playwright');

async function testAgentMarketCapabilities() {
  console.log('\n🚀 === TESTING AGENT MARKET CAPABILITIES ===\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream']
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    const text = msg.text();
    if (text.includes('Tool') || text.includes('tool') || 
        text.includes('session') || text.includes('OpenAI')) {
      console.log(`[Browser]: ${text}`);
    }
  });
  
  try {
    console.log('1️⃣ Navigating to app...');
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    console.log('2️⃣ Starting voice assistant...');
    await page.click('button:has-text("Start Voice Assistant")');
    await page.waitForTimeout(3000);
    
    // Wait for connection
    const connectionStatus = await page.textContent('.connection-status');
    console.log(`   Connection status: ${connectionStatus}`);
    
    // Check session info for tools
    console.log('\n3️⃣ Checking for market analysis tools...');
    
    // Test with text mode first (more reliable for testing)
    const textModeButton = page.locator('button:has-text("Text Mode")');
    if (await textModeButton.isVisible()) {
      console.log('   Switching to text mode for testing...');
      await textModeButton.click();
      await page.waitForTimeout(1000);
    }
    
    // Send a market query that requires tools
    console.log('\n4️⃣ Testing market query requiring tools...');
    const input = page.locator('input[placeholder*="Type"]');
    
    if (await input.isVisible()) {
      await input.fill("What's the current price of Tesla stock?");
      await page.keyboard.press('Enter');
      console.log('   Sent: "What\'s the current price of Tesla stock?"');
      
      // Wait for response
      await page.waitForTimeout(5000);
      
      // Check for tool execution in console
      console.log('\n5️⃣ Checking for tool execution...');
      
      // Look for tool-related UI updates
      const transcriptItems = await page.locator('.transcript-item').all();
      console.log(`   Transcript items: ${transcriptItems.length}`);
      
      for (const item of transcriptItems) {
        const text = await item.textContent();
        console.log(`   - ${text.substring(0, 100)}...`);
        
        if (text.includes('tool') || text.includes('Tool') || 
            text.includes('stock') || text.includes('price')) {
          console.log('   ✅ Found tool-related response!');
        }
      }
      
      // Try another query
      console.log('\n6️⃣ Testing another market query...');
      await input.fill("Get me the latest market overview");
      await page.keyboard.press('Enter');
      console.log('   Sent: "Get me the latest market overview"');
      
      await page.waitForTimeout(5000);
      
      // Check final transcript
      const finalTranscript = await page.locator('.transcript-container').textContent();
      
      console.log('\n📊 === RESULTS ===');
      console.log('Tool-related keywords found:');
      console.log('- "get_stock": ' + (finalTranscript.includes('get_stock') ? '✅' : '❌'));
      console.log('- "market_overview": ' + (finalTranscript.includes('market_overview') ? '✅' : '❌'));
      console.log('- "tool": ' + (finalTranscript.toLowerCase().includes('tool') ? '✅' : '❌'));
      console.log('- Stock data present: ' + (finalTranscript.includes('$') || finalTranscript.includes('price') ? '✅' : '❌'));
      
      // Take screenshot
      await page.screenshot({ path: 'test-agent-market-capabilities.png', fullPage: true });
      console.log('\n📸 Screenshot saved: test-agent-market-capabilities.png');
      
    } else {
      console.log('❌ Could not find text input field');
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    console.log('\n🏁 Test complete. Check browser window and console output.');
    await page.waitForTimeout(5000);
    await browser.close();
  }
}

testAgentMarketCapabilities().catch(console.error);