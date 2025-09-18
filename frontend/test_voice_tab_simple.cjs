/**
 * Simple Voice Tab Test
 * ====================
 * Tests if we can click the voice tab and see the connection toggle
 */

const { chromium } = require('playwright');

async function testVoiceTab() {
  console.log('🚀 Testing voice tab accessibility...\n');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
  });
  
  const page = await browser.newPage();
  
  // Track console messages
  page.on('console', msg => {
    if (msg.type() === 'log' && msg.text().includes('Voice provider')) {
      console.log(`🎤 ${msg.text()}`);
    }
    if (msg.type() === 'error') {
      console.log(`❌ Console Error: ${msg.text()}`);
    }
  });
  
  try {
    // Navigate to the application
    console.log('📍 Navigating to application...');
    await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Take screenshot of initial state
    await page.screenshot({ path: `voice-test-initial-${Date.now()}.png` });
    console.log('📸 Initial screenshot saved');
    
    // Click on Voice tab
    console.log('\n🎤 Looking for Voice tab...');
    const voiceTab = await page.$('[data-testid="voice-tab"]');
    if (voiceTab) {
      const isVisible = await voiceTab.isVisible();
      const isEnabled = await voiceTab.isEnabled();
      console.log(`✅ Found voice tab - Visible: ${isVisible}, Enabled: ${isEnabled}`);
      
      if (isVisible && isEnabled) {
        console.log('🎯 Clicking voice tab...');
        await voiceTab.click();
        await page.waitForTimeout(2000);
        
        // Take screenshot after clicking voice tab
        await page.screenshot({ path: `voice-test-tab-clicked-${Date.now()}.png` });
        console.log('📸 Voice tab clicked screenshot saved');
        
        // Check if voice interface is visible
        console.log('\n🔍 Checking for voice interface...');
        const voiceInterface = await page.$('[data-testid="voice-interface"]');
        if (voiceInterface) {
          const interfaceVisible = await voiceInterface.isVisible();
          console.log(`✅ Voice interface found - Visible: ${interfaceVisible}`);
          
          if (interfaceVisible) {
            // Look for connection toggle (the input is hidden, check the container)
            console.log('\n🎛️ Looking for connection toggle...');
            const connectionToggle = await page.$('[data-testid="connection-toggle"]');
            const toggleContainer = await page.$('.toggle-switch-container');
            
            if (connectionToggle && toggleContainer) {
              const inputVisible = await connectionToggle.isVisible();
              const inputEnabled = await connectionToggle.isEnabled();
              const inputChecked = await connectionToggle.isChecked();
              
              const containerVisible = await toggleContainer.isVisible();
              
              console.log(`✅ Connection toggle found:`);
              console.log(`   - Input Visible: ${inputVisible} (expected false - hidden by CSS)`);
              console.log(`   - Input Enabled: ${inputEnabled}`);
              console.log(`   - Input Checked: ${inputChecked}`);
              console.log(`   - Container Visible: ${containerVisible}`);
              
              if (containerVisible && inputEnabled) {
                console.log('\n🎯 Attempting to click toggle container...');
                try {
                  // Click the visible toggle container instead of hidden input
                  await toggleContainer.click();
                  await page.waitForTimeout(3000);
                  
                  const newToggleState = await connectionToggle.isChecked();
                  console.log(`✅ Toggle clicked! New state: ${newToggleState}`);
                  
                  // Take final screenshot
                  await page.screenshot({ path: `voice-test-toggle-clicked-${Date.now()}.png` });
                  console.log('📸 Toggle clicked screenshot saved');
                  
                  // Try switching to OpenAI provider and test connection
                  console.log('\n🤖 Testing OpenAI provider...');
                  const providerDropdown = await page.$('[data-testid="provider-dropdown"]');
                  if (providerDropdown) {
                    await providerDropdown.selectOption('openai');
                    await page.waitForTimeout(2000);
                    console.log('✅ Switched to OpenAI provider');
                    
                    // Try clicking toggle again with OpenAI
                    try {
                      await toggleContainer.click();
                      await page.waitForTimeout(3000);
                      
                      const openaiToggleState = await connectionToggle.isChecked();
                      console.log(`🤖 OpenAI toggle state: ${openaiToggleState}`);
                      
                      // Take final screenshot with OpenAI
                      await page.screenshot({ path: `voice-test-openai-${Date.now()}.png` });
                      console.log('📸 OpenAI test screenshot saved');
                      
                    } catch (error) {
                      console.log(`❌ OpenAI toggle failed: ${error.message}`);
                    }
                  }
                  
                } catch (error) {
                  console.log(`❌ Failed to click toggle: ${error.message}`);
                }
              } else {
                console.log(`❌ Toggle not clickable - Container Visible: ${containerVisible}, Input Enabled: ${inputEnabled}`);
              }
            } else {
              if (!connectionToggle) console.log('❌ Connection toggle input not found');
              if (!toggleContainer) console.log('❌ Toggle container not found');
            }
          }
        } else {
          console.log('❌ Voice interface not found');
        }
      }
    } else {
      console.log('❌ Voice tab not found');
    }
    
  } catch (error) {
    console.log(`\n❌ Error: ${error.message}`);
  } finally {
    console.log('\n✅ Test completed. Press Ctrl+C to close browser.');
    // Keep browser open for inspection
    await new Promise(() => {});
  }
}

testVoiceTab().catch(console.error);