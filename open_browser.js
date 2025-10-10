const { chromium } = require('playwright');

(async () => {
  console.log('🚀 Launching Comet Browser...');
  
  const browser = await chromium.launch({
    headless: false,
    executablePath: '/Applications/Comet.app/Contents/MacOS/Comet',
    args: [
      '--start-maximized',
      '--remote-debugging-port=9222'
    ]
  });
  
  const context = await browser.newContext({
    viewport: null,
    permissions: ['microphone']
  });
  
  const page = await context.newPage();
  
  console.log('📡 Navigating to http://localhost:5175...');
  await page.goto('http://localhost:5175');
  
  console.log('✅ Comet Browser opened successfully!');
  console.log('🎤 Voice assistant ready at http://localhost:5175');
  console.log('\n💡 Press Ctrl+C to close the browser');
  
  // Keep the browser open
  await page.waitForTimeout(3600000); // 1 hour, or until manually closed
})();

