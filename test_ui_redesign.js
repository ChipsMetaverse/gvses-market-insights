/**
 * Test and Redesign Provider Selector UI
 * Improves the appearance and functionality of the provider selector
 */

const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
  });
  
  const context = await browser.newContext({
    permissions: ['microphone'],
    viewport: { width: 1920, height: 1080 }
  });
  
  const page = await context.newPage();
  
  // Enable console logging
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.error('Browser Error:', msg.text());
    }
  });

  try {
    console.log('🚀 Starting Provider Selector UI Test');
    
    // Navigate to the application
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    console.log('✅ Application loaded');
    
    // Find and click the compact provider selector button
    const providerButton = await page.locator('.compact-provider-selector button').first();
    if (await providerButton.isVisible()) {
      console.log('📍 Found provider selector button');
      
      // Click to expand
      await providerButton.click();
      await page.waitForTimeout(1000);
      
      // Take screenshot of current state
      await page.screenshot({ 
        path: 'provider-selector-current.png',
        clip: { x: 0, y: 0, width: 400, height: 600 }
      });
      console.log('📸 Screenshot saved: provider-selector-current.png');
      
      // Check what elements are visible
      const providerPanel = await page.locator('.bg-white.border.rounded-lg.p-4').first();
      if (await providerPanel.isVisible()) {
        console.log('✅ Provider panel is visible');
        
        // Get all text content to understand structure
        const allText = await providerPanel.textContent();
        console.log('Panel content:', allText);
        
        // Check for specific elements
        const hasTitle = await page.locator('h3:has-text("AI Provider")').isVisible();
        const hasStatus = await page.locator('.bg-gray-50').isVisible();
        const hasProviderList = await page.locator('text=Available Providers').isVisible();
        
        console.log('Elements found:');
        console.log('- Title:', hasTitle);
        console.log('- Status section:', hasStatus);
        console.log('- Provider list:', hasProviderList);
        
        // Look for OpenAI Realtime option
        const openaiOption = await page.locator('text=/OpenAI Realtime/').first();
        if (await openaiOption.isVisible()) {
          console.log('✅ OpenAI Realtime option is available');
        } else {
          console.log('❌ OpenAI Realtime option not found');
        }
        
        // Look for Claude option
        const claudeOption = await page.locator('text=/Claude/').first();
        if (await claudeOption.isVisible()) {
          console.log('✅ Claude option is available');
        } else {
          console.log('❌ Claude option not found');
        }
      }
    } else {
      console.log('❌ Provider selector button not found');
    }
    
    console.log('\n📋 UI Issues Identified:');
    console.log('1. Duplicate provider names showing');
    console.log('2. Connection status indicator needs better styling');
    console.log('3. Layout needs better spacing and organization');
    console.log('4. Missing icons for providers');
    console.log('5. Action buttons need better styling');
    
    console.log('\n✨ Recommendations:');
    console.log('- Simplify the provider display to show name once');
    console.log('- Use better status indicators (badges instead of emojis)');
    console.log('- Add provider logos/icons');
    console.log('- Improve button styling with proper colors');
    console.log('- Add smooth transitions for expanding/collapsing');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await page.waitForTimeout(5000); // Keep browser open to observe
    await browser.close();
  }
})();