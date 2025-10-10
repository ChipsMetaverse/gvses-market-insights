const { chromium } = require('playwright');
const { spawn } = require('child_process');

(async () => {
  console.log('🚀 Launching Comet with Native Features + Monitoring...');
  
  // Strategy: Launch Comet with remote debugging but WITHOUT automation flags
  // This preserves native features while enabling monitoring
  
  const cometPath = '/Applications/Comet.app/Contents/MacOS/Comet';
  const debugPort = 9223; // Use different port to avoid conflicts
  
  console.log('📡 Starting Comet with remote debugging enabled...');
  
  // Launch Comet natively with only debugging port (no automation flags)
  const cometProcess = spawn(cometPath, [
    `--remote-debugging-port=${debugPort}`,
    '--user-data-dir=/tmp/comet-monitored', // Separate profile to avoid conflicts
  ], {
    detached: true,
    stdio: 'ignore'
  });
  
  cometProcess.unref(); // Allow process to run independently
  
  console.log('⏳ Waiting for Comet to start...');
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  try {
    console.log('🔌 Connecting to Comet via CDP...');
    
    // Connect to the browser via CDP (this doesn't disable native features)
    const browser = await chromium.connectOverCDP(`http://localhost:${debugPort}`);
    
    console.log('✅ Connected to Comet!');
    console.log('🎯 Native features should be intact\n');
    
    const contexts = browser.contexts();
    if (contexts.length === 0) {
      console.log('⚠️  No contexts found yet. Comet may still be starting...');
      console.log('💡 Try opening a new tab in Comet manually.');
      return;
    }
    
    const context = contexts[0];
    const pages = context.pages();
    
    console.log(`📄 Found ${pages.length} page(s)`);
    
    // Monitor all pages
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const title = await page.title();
      const url = page.url();
      console.log(`  Page ${i + 1}: "${title}" - ${url}`);
    }
    
    // Listen for new pages (tabs)
    context.on('page', async (newPage) => {
      console.log('\n🆕 New page opened!');
      await newPage.waitForLoadState('domcontentloaded');
      const title = await newPage.title();
      const url = newPage.url();
      console.log(`  Title: "${title}"`);
      console.log(`  URL: ${url}`);
      
      // Monitor the Assistant on this page
      await monitorAssistant(newPage);
    });
    
    // Monitor existing pages
    if (pages.length > 0) {
      console.log('\n🔍 Setting up monitoring on active page...');
      await monitorAssistant(pages[0]);
    }
    
    console.log('\n✅ Monitoring active!');
    console.log('💡 Comet is running with full native features');
    console.log('📊 This script is monitoring the Assistant');
    console.log('⚠️  Press Ctrl+C to stop monitoring (Comet will keep running)\n');
    
    // Keep monitoring
    await new Promise(() => {});
    
  } catch (error) {
    console.error('❌ Connection error:', error.message);
    console.log('\n💡 Troubleshooting:');
    console.log('  1. Make sure no other Comet instances are running');
    console.log('  2. Try: pkill -9 Comet && node comet_native_with_monitoring.js');
  }
})();

async function monitorAssistant(page) {
  console.log('  🤖 Installing Assistant monitor...');
  
  try {
    // Inject a monitor script that watches for Assistant activity
    await page.addInitScript(() => {
      // Monitor Assistant input
      const monitorInput = () => {
        const inputs = document.querySelectorAll('input, textarea');
        inputs.forEach(input => {
          if (!input.dataset.monitored) {
            input.dataset.monitored = 'true';
            
            input.addEventListener('input', (e) => {
              if (e.target.value.length > 0) {
                console.log('[ASSISTANT] Input:', e.target.value);
              }
            });
            
            input.addEventListener('keydown', (e) => {
              if (e.key === 'Enter') {
                console.log('[ASSISTANT] Message sent:', e.target.value);
              }
            });
          }
        });
      };
      
      // Run immediately and on DOM changes
      monitorInput();
      
      const observer = new MutationObserver(() => {
        monitorInput();
      });
      
      observer.observe(document.body || document.documentElement, {
        childList: true,
        subtree: true
      });
      
      console.log('[MONITOR] Assistant monitoring active');
    });
    
    // Listen for console messages from the page
    page.on('console', async (msg) => {
      const text = msg.text();
      if (text.includes('[ASSISTANT]') || text.includes('[MONITOR]')) {
        console.log(`  ${text}`);
      }
    });
    
    // Monitor DOM mutations for Assistant responses
    await page.evaluate(() => {
      const checkForAssistantMessages = () => {
        // Look for common Assistant message patterns
        const possibleSelectors = [
          '[class*="assistant"]',
          '[class*="response"]',
          '[class*="message"]',
          '[role="article"]',
          '[data-message]'
        ];
        
        possibleSelectors.forEach(selector => {
          document.querySelectorAll(selector).forEach(el => {
            if (!el.dataset.logged && el.textContent.trim().length > 0) {
              el.dataset.logged = 'true';
              console.log('[ASSISTANT] Response detected:', el.textContent.trim().substring(0, 100));
            }
          });
        });
      };
      
      setInterval(checkForAssistantMessages, 1000);
    });
    
    console.log('  ✅ Monitor installed');
    
  } catch (error) {
    console.log('  ⚠️  Could not install monitor:', error.message);
  }
}

