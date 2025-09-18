/**
 * Quick test to verify Tailwind CSS is working and UI layout is fixed
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
  
  try {
    console.log('🚀 Testing Tailwind CSS fix...');
    
    // Navigate to the ProviderTest page
    await page.goto('http://localhost:5174/?provider-test');
    await page.waitForTimeout(2000);
    
    console.log('✅ Page loaded');
    
    // Take screenshot
    await page.screenshot({ path: 'ui-test-after-tailwind.png', fullPage: true });
    console.log('📸 Screenshot saved: ui-test-after-tailwind.png');
    
    // Check if provider cards have proper spacing
    const providerCards = await page.locator('.flex.items-center.justify-between').count();
    console.log(`Found ${providerCards} provider cards`);
    
    // Check if Tailwind classes are being applied
    const hasSpacing = await page.locator('.space-y-2').count();
    console.log(`Elements with Tailwind spacing: ${hasSpacing}`);
    
    // Check specific elements for overlap
    const firstProvider = await page.locator('p.text-sm.font-medium').first();
    const secondProvider = await page.locator('p.text-sm.font-medium').nth(1);
    
    if (await firstProvider.isVisible() && await secondProvider.isVisible()) {
      const firstBox = await firstProvider.boundingBox();
      const secondBox = await secondProvider.boundingBox();
      
      if (firstBox && secondBox) {
        const verticalGap = secondBox.y - (firstBox.y + firstBox.height);
        console.log(`Vertical gap between providers: ${verticalGap}px`);
        
        if (verticalGap > 0) {
          console.log('✅ No overlap detected - providers have proper spacing');
        } else {
          console.log('⚠️ Providers may still be overlapping');
        }
      }
    }
    
    console.log('\n✨ Test complete!');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await page.waitForTimeout(3000);
    await browser.close();
  }
})();