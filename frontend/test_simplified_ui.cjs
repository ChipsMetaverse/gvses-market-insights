const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: false,
    slowMo: 300
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  console.log('🎯 Testing simplified voice interface UI...\n');
  
  try {
    // Navigate to the app
    console.log('1. Navigating to localhost:5174...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // Switch to voice tab to see the new interface
    console.log('2. Switching to Voice + Manual Control tab...');
    const voiceTab = await page.locator('text="Voice + Manual Control"').first();
    await voiceTab.click();
    await page.waitForTimeout(1000);
    
    // Take a screenshot of the new simplified interface
    console.log('3. Taking screenshot of simplified voice interface...');
    await page.screenshot({ 
      path: 'simplified-voice-ui-test.png', 
      fullPage: false,
      clip: {
        x: 0,
        y: 400, // Focus on the voice section
        width: 1200,
        height: 600
      }
    });
    
    console.log('✅ Screenshot saved: simplified-voice-ui-test.png');
    
    // Test clicking the OpenAI button to see the interaction
    console.log('4. Testing OpenAI direct connect button...');
    const openAIButton = await page.locator('[data-testid="provider-openai"]').first();
    const isVisible = await openAIButton.isVisible().catch(() => false);
    
    if (isVisible) {
      console.log('   ✓ OpenAI direct connect button is visible');
      
      // Hover over the button to see hover effects
      await openAIButton.hover();
      await page.waitForTimeout(500);
      
      console.log('   ✓ Hover effect tested');
    } else {
      console.log('   ❌ OpenAI button not found');
    }
    
    // Test ElevenLabs interface
    console.log('5. Testing ElevenLabs selection...');
    const elevenLabsButton = await page.locator('[data-testid="provider-elevenlabs"]').first();
    const isElevenLabsVisible = await elevenLabsButton.isVisible().catch(() => false);
    
    if (isElevenLabsVisible) {
      await elevenLabsButton.click();
      await page.waitForTimeout(1000);
      console.log('   ✓ ElevenLabs selected, checking for connect button...');
      
      const connectButton = await page.locator('text="Connect"').first();
      const isConnectVisible = await connectButton.isVisible().catch(() => false);
      
      if (isConnectVisible) {
        console.log('   ✓ Connect button appears for ElevenLabs (two-step process working)');
      } else {
        console.log('   ❌ Connect button not found for ElevenLabs');
      }
    }
    
    // Take final screenshot
    await page.screenshot({ 
      path: 'simplified-voice-ui-final.png', 
      fullPage: false,
      clip: {
        x: 0,
        y: 400,
        width: 1200,
        height: 600
      }
    });
    
    console.log('✅ Final screenshot saved: simplified-voice-ui-final.png');
    
  } catch (error) {
    console.error('❌ Test error:', error);
  }
  
  console.log('\n🎉 Simplified voice UI test completed!');
  console.log('Screenshots saved for review.');
  
  await page.waitForTimeout(2000);
  await browser.close();
})().catch(console.error);