const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Launching Comet Browser...');
  
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/Applications/Comet.app/Contents/MacOS/Comet',
    args: ['--start-maximized']
  });
  
  const context = await browser.newContext({
    viewport: null
  });
  
  const page = await context.newPage();
  
  console.log('✅ Comet Browser opened successfully!');
  console.log('🌐 Browser is ready to use');
  console.log('\n💡 The browser will stay open indefinitely.');
  console.log('Press Ctrl+C in this terminal to close it.');
  
  // Take initial screenshot
  await page.waitForTimeout(2000);
  await page.screenshot({ path: 'comet_default.png' });
  console.log('📸 Screenshot saved: comet_default.png');
  
  // Keep the browser open indefinitely
  await new Promise(() => {});
  
})().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

