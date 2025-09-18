/**
 * Test sending a message to the voice agent
 * ==========================================
 * Simulates a user sending a text message to the AI assistant
 */

const { chromium } = require('playwright');

async function sendMessageToAgent() {
    console.log('🚀 Starting message send test...\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream']
    });
    
    const page = await browser.newPage();
    
    // Track console messages
    page.on('console', msg => {
        if (msg.type() === 'error') {
            console.log(`❌ Console Error: ${msg.text()}`);
        }
    });
    
    try {
        // Navigate to the application
        console.log('📍 Navigating to application...');
        await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);
        
        // Click on Voice tab
        console.log('🎤 Clicking Voice tab...');
        const voiceTab = await page.$('button:has-text("Voice"), [data-testid="voice-tab"]');
        if (voiceTab) {
            await voiceTab.click();
            await page.waitForTimeout(1000);
        }
        
        // Try to connect first
        console.log('🔌 Attempting to connect to voice service...');
        const connectionToggle = await page.$('[data-testid="connection-toggle"]');
        if (connectionToggle) {
            const isVisible = await connectionToggle.isVisible();
            if (isVisible) {
                await connectionToggle.click();
                console.log('✅ Clicked connection toggle');
                await page.waitForTimeout(3000);
            } else {
                console.log('⚠️ Connection toggle not visible, trying alternative approach...');
                
                // Try clicking the connect button directly
                const connectButton = await page.$('button:has-text("Connect")');
                if (connectButton) {
                    await connectButton.click();
                    console.log('✅ Clicked Connect button');
                    await page.waitForTimeout(3000);
                }
            }
        }
        
        // Now try to send a message
        console.log('\n📝 Looking for message input field...');
        
        // Try multiple selectors for the message input
        const inputSelectors = [
            '[data-testid="message-input"]',
            'input[placeholder*="Type a message"]',
            'input[placeholder*="Type your message"]',
            'textarea[placeholder*="Type"]',
            '.text-input-modern',
            'input[type="text"]:not([placeholder*="Search"])'
        ];
        
        let messageInput = null;
        for (const selector of inputSelectors) {
            messageInput = await page.$(selector);
            if (messageInput && await messageInput.isVisible()) {
                console.log(`✅ Found message input using selector: ${selector}`);
                break;
            }
        }
        
        if (messageInput) {
            // Type a test message
            const testMessage = "What is the current price of Apple stock?";
            console.log(`\n💬 Typing message: "${testMessage}"`);
            
            await messageInput.click();
            await messageInput.fill(''); // Clear any existing text
            await messageInput.type(testMessage, { delay: 50 });
            
            // Take screenshot of typed message
            await page.screenshot({ 
                path: `message-typed-${Date.now()}.png`,
                fullPage: false 
            });
            console.log('📸 Screenshot saved of typed message');
            
            // Try to send the message
            console.log('\n🚀 Attempting to send message...');
            
            // Try multiple ways to send
            const sendMethods = [
                async () => {
                    // Method 1: Click send button
                    const sendButton = await page.$('button[type="submit"], button:has-text("Send"), button[aria-label*="send"]');
                    if (sendButton && await sendButton.isEnabled()) {
                        await sendButton.click();
                        return 'Send button clicked';
                    }
                    return null;
                },
                async () => {
                    // Method 2: Press Enter
                    await messageInput.press('Enter');
                    return 'Enter key pressed';
                },
                async () => {
                    // Method 3: Submit form
                    const form = await page.$('form');
                    if (form) {
                        await form.evaluate(f => f.submit());
                        return 'Form submitted';
                    }
                    return null;
                }
            ];
            
            for (const method of sendMethods) {
                const result = await method();
                if (result) {
                    console.log(`✅ Message sent using: ${result}`);
                    break;
                }
            }
            
            // Wait for response
            console.log('\n⏳ Waiting for AI response...');
            await page.waitForTimeout(5000);
            
            // Check for response
            const responseSelectors = [
                '.message-assistant',
                '.ai-response',
                '.response-text',
                '[data-testid="ai-message"]',
                '.message:last-child'
            ];
            
            for (const selector of responseSelectors) {
                const response = await page.$(selector);
                if (response) {
                    const text = await response.textContent();
                    if (text && text.length > 0) {
                        console.log(`\n🤖 AI Response received: "${text.substring(0, 100)}..."`);
                        break;
                    }
                }
            }
            
            // Final screenshot
            await page.screenshot({ 
                path: `final-state-${Date.now()}.png`,
                fullPage: true 
            });
            console.log('📸 Final screenshot saved');
            
        } else {
            console.log('❌ Could not find message input field');
            console.log('   Possible reasons:');
            console.log('   - Voice connection not established');
            console.log('   - UI not fully loaded');
            console.log('   - Element selector changed');
            
            // Debug: List all visible input fields
            const allInputs = await page.$$('input, textarea');
            console.log(`\n🔍 Found ${allInputs.length} input fields on page:`);
            for (const input of allInputs) {
                const placeholder = await input.getAttribute('placeholder');
                const type = await input.getAttribute('type');
                const testId = await input.getAttribute('data-testid');
                const isVisible = await input.isVisible();
                if (isVisible) {
                    console.log(`   - Type: ${type}, Placeholder: "${placeholder}", TestId: ${testId}`);
                }
            }
        }
        
    } catch (error) {
        console.log(`\n❌ Error: ${error.message}`);
    } finally {
        console.log('\n✅ Test completed. Browser will remain open for inspection.');
        console.log('Press Ctrl+C to exit when ready.\n');
        
        // Keep browser open
        await new Promise(() => {});
    }
}

sendMessageToAgent().catch(console.error);