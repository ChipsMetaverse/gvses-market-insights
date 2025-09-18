/**
 * Complete User Flow Test
 * =======================
 * Tests the critical user journey from connection to interaction
 */

const { chromium } = require('playwright');

async function testCompleteUserFlow() {
  console.log('🚀 Testing complete user flow...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
  });
  
  const page = await browser.newPage();
  
  // Track console messages for debugging
  page.on('console', msg => {
    if (msg.type() === 'log' && (msg.text().includes('Voice') || msg.text().includes('connection') || msg.text().includes('Connected'))) {
      console.log(`📱 ${msg.text()}`);
    }
    if (msg.type() === 'error') {
      console.log(`❌ Console Error: ${msg.text()}`);
    }
  });
  
  try {
    // Step 1: Navigate to application
    console.log('📍 Step 1: Navigating to application...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Step 2: Click Voice tab
    console.log('📍 Step 2: Switching to Voice interface...');
    const voiceTab = await page.$('[data-testid="voice-tab"]');
    if (!voiceTab) {
      console.log('❌ CRITICAL: Voice tab not found!');
      return;
    }
    
    await voiceTab.click();
    await page.waitForTimeout(2000);
    console.log('✅ Voice tab activated');
    
    // Step 3: Check if voice interface is visible
    console.log('📍 Step 3: Verifying voice interface...');
    const voiceInterface = await page.$('[data-testid="voice-interface"]');
    if (!voiceInterface || !await voiceInterface.isVisible()) {
      console.log('❌ CRITICAL: Voice interface not visible!');
      return;
    }
    console.log('✅ Voice interface is visible');
    
    // Step 4: Test connection toggle
    console.log('📍 Step 4: Testing voice connection...');
    const toggleContainer = await page.$('.toggle-switch-container');
    const connectionToggle = await page.$('[data-testid="connection-toggle"]');
    
    if (!toggleContainer || !connectionToggle) {
      console.log('❌ CRITICAL: Connection toggle components missing!');
      return;
    }
    
    // Click to connect
    await toggleContainer.click();
    await page.waitForTimeout(5000); // Wait longer for connection
    
    const isConnected = await connectionToggle.isChecked();
    console.log(`🔌 Connection state: ${isConnected ? 'CONNECTED' : 'NOT CONNECTED'}`);
    
    // Step 5: Check for text input (CRITICAL)
    console.log('📍 Step 5: Verifying text input interface...');
    const messageInput = await page.$('[data-testid="message-input"]');
    const sendButton = await page.$('[data-testid="send-button"]');
    
    if (isConnected) {
      if (!messageInput || !await messageInput.isVisible()) {
        console.log('❌ CRITICAL FAILURE: Connected but no text input visible!');
        console.log('   This means users cannot interact with the AI assistant');
        
        // Debug: Check what's actually rendered
        const voiceSection = await page.$('.voice-section-redesigned');
        if (voiceSection) {
          const innerHTML = await voiceSection.innerHTML();
          console.log('🔍 Voice section content:', innerHTML.substring(0, 500) + '...');
        }
      } else {
        console.log('✅ Text input is visible and accessible');
        
        // Step 6: Test text input functionality
        console.log('📍 Step 6: Testing text input functionality...');
        await messageInput.type('What is Tesla stock price?');
        await page.waitForTimeout(1000);
        
        if (sendButton && await sendButton.isEnabled()) {
          await sendButton.click();
          console.log('✅ Text message sent successfully');
          await page.waitForTimeout(3000); // Wait for response
        } else {
          console.log('❌ Send button not enabled');
        }
      }
    } else {
      console.log('❌ CRITICAL: Connection failed - cannot test text input');
    }
    
    // Step 7: Test market insights search
    console.log('📍 Step 7: Testing market insights search...');
    const searchInput = await page.$('input[placeholder*="Search symbols"]');
    
    if (!searchInput) {
      console.log('❌ CRITICAL: Market insights search input not found!');
    } else {
      console.log('✅ Market insights search input found');
      
      // Test search functionality
      await searchInput.type('Microsoft');
      await page.waitForTimeout(2000); // Wait for dropdown
      
      // Look for search results dropdown
      const searchResults = await page.$$('.search-result-item');
      if (searchResults.length > 0) {
        console.log(`✅ Search results found: ${searchResults.length} items`);
        // Click first result
        await searchResults[0].click();
        console.log('✅ Search result selected');
      } else {
        console.log('❌ No search results appeared');
      }
    }
    
    // Step 8: Final screenshot and summary
    console.log('📍 Step 8: Capturing final state...');
    await page.screenshot({ path: `complete-user-flow-test-${Date.now()}.png` });
    
    // Summary
    console.log('\n=== USER FLOW TEST SUMMARY ===');
    console.log(`✅ Voice tab: WORKING`);
    console.log(`✅ Voice interface: WORKING`);
    console.log(`${isConnected ? '✅' : '❌'} Connection: ${isConnected ? 'WORKING' : 'FAILED'}`);
    
    if (isConnected) {
      const hasTextInput = messageInput && await messageInput.isVisible();
      console.log(`${hasTextInput ? '✅' : '❌'} Text input: ${hasTextInput ? 'WORKING' : 'MISSING'}`);
      
      if (!hasTextInput) {
        console.log('\n🚨 CRITICAL ISSUE: Users cannot interact with AI despite connection!');
      }
    }
    
    const hasSearch = searchInput !== null;
    console.log(`${hasSearch ? '✅' : '❌'} Market search: ${hasSearch ? 'WORKING' : 'MISSING'}`);
    
    console.log('\n✅ Test completed. Press Ctrl+C to close browser.');
    // Keep browser open for inspection
    await new Promise(() => {});
    
  } catch (error) {
    console.log(`\n❌ Test Error: ${error.message}`);
  } finally {
    // Browser will be closed manually
  }
}

testCompleteUserFlow().catch(console.error);