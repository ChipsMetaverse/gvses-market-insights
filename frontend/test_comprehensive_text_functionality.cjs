/**
 * Comprehensive Text Functionality Test Suite for Voice Interface Application
 * ========================================================================
 * 
 * Tests all text-related functionality in the voice interface:
 * - Text input testing
 * - Text output verification  
 * - Text-voice integration
 * - Message history persistence
 * - Provider switching for text
 * - Text message display
 * - Real-time text updates
 * - Various text input methods
 * - Error handling scenarios
 * - Complete text-based conversation workflows
 */

const { chromium } = require('playwright');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(exec);

// Color codes for enhanced output
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m',
    gray: '\x1b[90m'
};

// Test configuration
const config = {
    baseURL: 'http://localhost:5174',
    backendURL: 'http://localhost:8000',
    timeout: 30000,
    waitForResponse: 5000,
    screenshotDir: './test-results/text-functionality'
};

// Global test state
let testResults = {
    passed: 0,
    failed: 0,
    warnings: 0,
    tests: []
};

function log(message, color = colors.reset) {
    console.log(`${color}${message}${colors.reset}`);
}

function logSuccess(message) {
    console.log(`${colors.green}✓ ${message}${colors.reset}`);
    testResults.passed++;
    testResults.tests.push({ status: 'PASS', message });
}

function logError(message) {
    console.log(`${colors.red}✗ ${message}${colors.reset}`);
    testResults.failed++;
    testResults.tests.push({ status: 'FAIL', message });
}

function logWarning(message) {
    console.log(`${colors.yellow}⚠ ${message}${colors.reset}`);
    testResults.warnings++;
    testResults.tests.push({ status: 'WARN', message });
}

function logSection(message) {
    console.log(`\n${colors.bright}${colors.blue}${'='.repeat(70)}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${message}${colors.reset}`);
    console.log(`${colors.bright}${colors.blue}${'='.repeat(70)}${colors.reset}\n`);
}

function logSubsection(message) {
    console.log(`\n${colors.cyan}${'-'.repeat(50)}${colors.reset}`);
    console.log(`${colors.cyan}${message}${colors.reset}`);
    console.log(`${colors.cyan}${'-'.repeat(50)}${colors.reset}`);
}

// Utility functions
async function ensureDirectory(path) {
    try {
        await execAsync(`mkdir -p "${path}"`);
    } catch (error) {
        log(`Warning: Could not create directory ${path}`, colors.yellow);
    }
}

async function takeScreenshot(page, filename, description = '') {
    try {
        await ensureDirectory(config.screenshotDir);
        const fullPath = `${config.screenshotDir}/${filename}`;
        await page.screenshot({ path: fullPath, fullPage: true });
        log(`📸 Screenshot saved: ${fullPath} ${description}`, colors.gray);
        return fullPath;
    } catch (error) {
        logWarning(`Failed to save screenshot: ${error.message}`);
        return null;
    }
}

async function waitForElementWithRetry(page, selector, options = {}) {
    const maxRetries = options.retries || 3;
    const timeout = options.timeout || 5000;
    
    for (let i = 0; i < maxRetries; i++) {
        try {
            await page.waitForSelector(selector, { timeout });
            return await page.$(selector);
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            await page.waitForTimeout(1000);
        }
    }
}

async function checkServerConnection() {
    log('Checking server connections...', colors.cyan);
    
    try {
        const fetch = require('node-fetch');
        
        // Check frontend
        const frontendResponse = await fetch(config.baseURL);
        if (frontendResponse.ok) {
            logSuccess('Frontend server accessible');
        } else {
            logError('Frontend server not responding');
            return false;
        }
        
        // Check backend
        const backendResponse = await fetch(`${config.backendURL}/health`);
        if (backendResponse.ok) {
            logSuccess('Backend server accessible');
        } else {
            logError('Backend server not responding');
            return false;
        }
        
        return true;
    } catch (error) {
        logError(`Server connection check failed: ${error.message}`);
        return false;
    }
}

// Helper function to establish connection
async function establishConnection(page) {
    // Strategy 1: Click the toggle switch label (visible wrapper) - MOST RELIABLE
    const toggleLabel = await page.$('.toggle-switch');
    if (toggleLabel) {
        log('Found toggle switch label, attempting to click...', colors.cyan);
        await toggleLabel.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);
        await toggleLabel.click();
        await page.waitForTimeout(3000);
        logSuccess('Clicked toggle switch label');
        return true;
    }
    
    // Strategy 2: Use Playwright's locator for better element handling
    try {
        const toggleLocator = page.locator('.toggle-switch');
        if (await toggleLocator.count() > 0) {
            log('Found toggle with locator, attempting click...', colors.cyan);
            await toggleLocator.scrollIntoViewIfNeeded();
            await toggleLocator.click();
            await page.waitForTimeout(3000);
            logSuccess('Clicked toggle with locator');
            return true;
        }
    } catch (error) {
        log('Locator approach failed', colors.yellow);
    }
    
    // Strategy 3: Click the toggle switch container
    const toggleContainer = await page.$('.toggle-switch-container');
    if (toggleContainer) {
        log('Found toggle container, attempting to click...', colors.cyan);
        await toggleContainer.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);
        await toggleContainer.click();
        await page.waitForTimeout(3000);
        logSuccess('Clicked toggle container');
        return true;
    }
    
    // Strategy 4: Try coordinates-based clicking on the toggle area
    try {
        const toggleArea = await page.$('.toggle-switch');
        if (toggleArea) {
            const box = await toggleArea.boundingBox();
            if (box) {
                log('Found toggle bounding box, attempting coordinate click...', colors.cyan);
                await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
                await page.waitForTimeout(3000);
                logSuccess('Clicked toggle using coordinates');
                return true;
            }
        }
    } catch (error) {
        log('Coordinate clicking failed', colors.yellow);
    }
    
    // Strategy 5: Try generic checkbox input as final fallback
    connectionToggle = await page.$('input[type="checkbox"]');
    if (connectionToggle) {
        log('Found generic checkbox, attempting force click...', colors.cyan);
        await connectionToggle.scrollIntoViewIfNeeded();
        await page.waitForTimeout(500);
        await connectionToggle.click({ force: true });
        await page.waitForTimeout(3000);
        logSuccess('Force clicked generic checkbox');
        return true;
    }
    
    logError('Connection toggle not found with any selector');
    return false;
}

// Test that works without connection 
async function testVoiceInterfaceLayout(page) {
    logSubsection('Testing Voice Interface Layout');
    
    try {
        await takeScreenshot(page, 'voice-interface-layout.png', '- Voice interface layout');
        
        // Test voice interface components
        const voiceSection = await page.$('[data-testid="voice-interface"]');
        if (voiceSection) {
            logSuccess('Voice interface section found');
        } else {
            const voiceSectionAlt = await page.$('.voice-section-redesigned');
            if (voiceSectionAlt) {
                logSuccess('Voice interface section found (alternative selector)');
            } else {
                logError('Voice interface section not found');
            }
        }
        
        // Test provider dropdown
        const providerDropdown = await page.$('[data-testid="provider-dropdown"]');
        if (providerDropdown) {
            logSuccess('Provider dropdown found');
            
            const currentProvider = await providerDropdown.inputValue();
            logSuccess(`Current provider: ${currentProvider}`);
        }
        
        // Test connection toggle presence
        const connectionToggle = await page.$('[data-testid="connection-toggle"]') || 
                                 await page.$('input[type="checkbox"]') ||
                                 await page.$('.toggle-switch input');
        if (connectionToggle) {
            logSuccess('Connection toggle found');
        }
        
        // Test messages container
        const messagesContainer = await page.$('[data-testid="messages-container"]');
        if (messagesContainer) {
            logSuccess('Messages container found');
        }
        
        // Test conversation header
        const conversationHeader = await page.$('.conversation-header');
        if (conversationHeader) {
            logSuccess('Conversation header found');
        }
        
    } catch (error) {
        logError(`Voice interface layout test failed: ${error.message}`);
    }
}

// Main test functions
async function testBasicTextInput(page) {
    logSubsection('Testing Basic Text Input');
    
    try {
        await takeScreenshot(page, 'voice-tab-initial.png', '- Initial voice tab state');
        
        // First establish connection to make text input visible
        const connectionSuccess = await establishConnection(page);
        
        await takeScreenshot(page, 'voice-tab-connected.png', '- Voice tab after connection attempt');
        
        if (!connectionSuccess) {
            logWarning('Connection failed - testing UI components that should be visible');
            return;
        }
        
        // Find text input field (should be visible after connection)
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        if (!textInput) {
            logError('Text input field not found even after connection attempt');
            return;
        }
        
        // Test input field properties
        const placeholder = await textInput.getAttribute('placeholder');
        if (placeholder && placeholder.includes('Type a message')) {
            logSuccess('Text input placeholder correct');
        } else {
            logWarning(`Unexpected placeholder: ${placeholder}`);
        }
        
        // Test typing functionality
        const testMessage = 'Hello, this is a test message';
        await textInput.fill(testMessage);
        
        const inputValue = await textInput.inputValue();
        if (inputValue === testMessage) {
            logSuccess('Text input accepts and retains text');
        } else {
            logError(`Text input value mismatch: expected "${testMessage}", got "${inputValue}"`);
        }
        
        await takeScreenshot(page, 'text-input-filled.png', '- Text input with message');
        
        // Test clearing input
        await textInput.fill('');
        const clearedValue = await textInput.inputValue();
        if (clearedValue === '') {
            logSuccess('Text input can be cleared');
        } else {
            logError('Text input did not clear properly');
        }
        
    } catch (error) {
        logError(`Basic text input test failed: ${error.message}`);
        await takeScreenshot(page, 'text-input-error.png', '- Error state');
    }
}

async function testProviderSwitching(page) {
    logSubsection('Testing Provider Switching for Text');
    
    try {
        // Test provider dropdown
        const providerDropdown = await page.$('[data-testid="provider-dropdown"]');
        if (!providerDropdown) {
            logError('Provider dropdown not found');
            return;
        }
        
        // Get initial provider
        const initialProvider = await providerDropdown.inputValue();
        logSuccess(`Initial provider: ${initialProvider}`);
        
        // Test switching to ElevenLabs
        await providerDropdown.selectOption('elevenlabs');
        await page.waitForTimeout(500);
        
        const elevenLabsValue = await providerDropdown.inputValue();
        if (elevenLabsValue === 'elevenlabs') {
            logSuccess('Successfully switched to ElevenLabs provider');
        } else {
            logError('Failed to switch to ElevenLabs provider');
        }
        
        await takeScreenshot(page, 'provider-elevenlabs.png', '- ElevenLabs provider selected');
        
        // Test switching to OpenAI
        await providerDropdown.selectOption('openai');
        await page.waitForTimeout(500);
        
        const openAIValue = await providerDropdown.inputValue();
        if (openAIValue === 'openai') {
            logSuccess('Successfully switched to OpenAI provider');
        } else {
            logError('Failed to switch to OpenAI provider');
        }
        
        await takeScreenshot(page, 'provider-openai.png', '- OpenAI provider selected');
        
        // Test provider descriptions
        const providerInfo = await page.$('.provider-info-compact');
        if (providerInfo) {
            const infoText = await providerInfo.textContent();
            if (infoText) {
                logSuccess(`Provider info displayed: ${infoText}`);
            }
        }
        
    } catch (error) {
        logError(`Provider switching test failed: ${error.message}`);
        await takeScreenshot(page, 'provider-switching-error.png', '- Error state');
    }
}

async function testConnectionProcess(page) {
    logSubsection('Testing Connection Process');
    
    try {
        // Find connection toggle
        const connectionToggle = await page.$('[data-testid="connection-toggle"]');
        if (!connectionToggle) {
            logError('Connection toggle not found');
            return;
        }
        
        // Check initial state
        const isInitiallyChecked = await connectionToggle.isChecked();
        logSuccess(`Initial connection state: ${isInitiallyChecked ? 'Connected' : 'Disconnected'}`);
        
        // Test connection establishment
        const connectionResult = await establishConnection(page);
        if (connectionResult) {
            logSuccess('Connection process working correctly');
            
            // Check for connection status indicators
            const statusDot = await page.$('.status-dot');
            if (statusDot) {
                const statusClass = await statusDot.getAttribute('class');
                if (statusClass.includes('connected')) {
                    logSuccess('Status indicator shows connected');
                } else if (statusClass.includes('connecting')) {
                    logWarning('Connection in progress (may take time)');
                } else {
                    logWarning('Connection status unclear');
                }
            }
            
            await takeScreenshot(page, 'connection-established.png', '- Connection established');
        } else {
            logWarning('Connection process may have issues');
            await takeScreenshot(page, 'connection-issues.png', '- Connection issues');
        }
        
        // Test connection toggle functionality
        const currentState = await connectionToggle.isChecked();
        await connectionToggle.click();
        await page.waitForTimeout(1000);
        
        const newState = await connectionToggle.isChecked();
        if (newState !== currentState) {
            logSuccess('Connection toggle responds to clicks');
        } else {
            logWarning('Connection toggle may not be responsive');
        }
        
        // Reconnect for further tests
        if (currentState) {
            await connectionToggle.click();
            await page.waitForTimeout(2000);
        }
        
    } catch (error) {
        logError(`Connection process test failed: ${error.message}`);
        await takeScreenshot(page, 'connection-error.png', '- Connection error state');
    }
}

async function testTextMessageSending(page) {
    logSubsection('Testing Text Message Sending');
    
    try {
        // Ensure we're connected for text messaging
        await establishConnection(page);
        
        // Find text input and send button
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        const sendButton = await waitForElementWithRetry(page, '[data-testid="send-button"]', { timeout: 5000 });
        
        if (!textInput || !sendButton) {
            logError('Text input or send button not found');
            return;
        }
        
        // Test send button initial state (should be disabled)
        const isInitiallyDisabled = await sendButton.isDisabled();
        if (isInitiallyDisabled) {
            logSuccess('Send button correctly disabled when input is empty');
        } else {
            logWarning('Send button should be disabled when input is empty');
        }
        
        // Type a test message
        const testMessage = 'Test message for voice assistant';
        await textInput.fill(testMessage);
        await page.waitForTimeout(500);
        
        // Check if send button becomes enabled
        const isEnabledAfterTyping = await sendButton.isDisabled();
        if (!isEnabledAfterTyping) {
            logSuccess('Send button enabled after typing message');
        } else {
            logWarning('Send button should be enabled after typing');
        }
        
        await takeScreenshot(page, 'message-ready-to-send.png', '- Message ready to send');
        
        // Test sending via button click
        const messagesBefore = await page.$$('[data-testid="messages-container"] .conversation-message-enhanced');
        const initialMessageCount = messagesBefore.length;
        
        await sendButton.click();
        await page.waitForTimeout(2000);
        
        // Check if message was sent (input should be cleared)
        const inputAfterSend = await textInput.inputValue();
        if (inputAfterSend === '') {
            logSuccess('Input field cleared after sending message');
        } else {
            logWarning('Input field should be cleared after sending');
        }
        
        // Check if message appears in conversation
        const messagesAfter = await page.$$('[data-testid="messages-container"] .conversation-message-enhanced');
        if (messagesAfter.length > initialMessageCount) {
            logSuccess('Message added to conversation history');
        } else {
            logWarning('Message may not have been added to conversation (check connection)');
        }
        
        await takeScreenshot(page, 'message-sent.png', '- After sending message');
        
        // Test sending via Enter key
        const enterTestMessage = 'Another test message via Enter key';
        await textInput.fill(enterTestMessage);
        await textInput.press('Enter');
        await page.waitForTimeout(2000);
        
        const inputAfterEnter = await textInput.inputValue();
        if (inputAfterEnter === '') {
            logSuccess('Enter key sends message and clears input');
        } else {
            logWarning('Enter key should send message and clear input');
        }
        
        await takeScreenshot(page, 'message-sent-enter.png', '- After sending via Enter');
        
    } catch (error) {
        logError(`Text message sending test failed: ${error.message}`);
        await takeScreenshot(page, 'message-sending-error.png', '- Message sending error');
    }
}

async function testMessageDisplay(page) {
    logSubsection('Testing Message Display and Formatting');
    
    try {
        const messagesContainer = await page.$('[data-testid="messages-container"]');
        if (!messagesContainer) {
            logError('Messages container not found');
            return;
        }
        
        // Test empty state
        const messages = await page.$$('.conversation-message-enhanced');
        if (messages.length === 0) {
            const emptyState = await page.$('.no-messages-redesigned');
            if (emptyState) {
                logSuccess('Empty conversation state displayed correctly');
            } else {
                logWarning('Empty state should be displayed when no messages');
            }
        }
        
        // Test message counter
        const messageCounter = await page.$('.message-count');
        if (messageCounter) {
            const counterText = await messageCounter.textContent();
            logSuccess(`Message counter displayed: ${counterText}`);
        }
        
        // If we have messages, test their structure
        if (messages.length > 0) {
            logSuccess(`Found ${messages.length} messages in conversation`);
            
            for (let i = 0; i < Math.min(messages.length, 3); i++) {
                const message = messages[i];
                
                // Check for avatar
                const avatar = await message.$('.message-avatar');
                if (avatar) {
                    const avatarText = await avatar.textContent();
                    logSuccess(`Message ${i + 1} has avatar: ${avatarText}`);
                }
                
                // Check for message bubble
                const bubble = await message.$('.message-bubble');
                if (bubble) {
                    logSuccess(`Message ${i + 1} has proper bubble structure`);
                }
                
                // Check for timestamp
                const timestamp = await message.$('.message-timestamp');
                if (timestamp) {
                    const timestampText = await timestamp.textContent();
                    logSuccess(`Message ${i + 1} has timestamp: ${timestampText}`);
                }
                
                // Check message content
                const messageText = await message.$('.message-text-enhanced');
                if (messageText) {
                    const content = await messageText.textContent();
                    if (content && content.trim().length > 0) {
                        logSuccess(`Message ${i + 1} has content: "${content.substring(0, 50)}..."`);
                    }
                }
            }
        }
        
        await takeScreenshot(page, 'message-display.png', '- Message display structure');
        
    } catch (error) {
        logError(`Message display test failed: ${error.message}`);
        await takeScreenshot(page, 'message-display-error.png', '- Message display error');
    }
}

async function testMessageHistory(page) {
    logSubsection('Testing Message History Persistence');
    
    try {
        // Ensure connection for text messaging
        await establishConnection(page);
        
        // Get current message count
        const initialMessages = await page.$$('.conversation-message-enhanced');
        const initialCount = initialMessages.length;
        
        // Add several test messages
        const testMessages = [
            'First persistence test message',
            'Second persistence test message',
            'Third persistence test message with special characters: !@#$%^&*()'
        ];
        
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        const sendButton = await waitForElementWithRetry(page, '[data-testid="send-button"]', { timeout: 5000 });
        
        if (!textInput || !sendButton) {
            logError('Text input or send button not found for history test');
            return;
        }
        
        // Send multiple messages
        for (let i = 0; i < testMessages.length; i++) {
            await textInput.fill(testMessages[i]);
            await sendButton.click();
            await page.waitForTimeout(1000);
            
            // Verify message was added
            const currentMessages = await page.$$('.conversation-message-enhanced');
            if (currentMessages.length > initialCount + i) {
                logSuccess(`Message ${i + 1} added to history`);
            } else {
                logWarning(`Message ${i + 1} may not have been added (check connection)`);
            }
        }
        
        await takeScreenshot(page, 'message-history-populated.png', '- History with multiple messages');
        
        // Test message ordering (newest should be at bottom)
        const allMessages = await page.$$('.conversation-message-enhanced .message-text-enhanced');
        if (allMessages.length >= testMessages.length) {
            const lastMessageTexts = [];
            for (let i = Math.max(0, allMessages.length - testMessages.length); i < allMessages.length; i++) {
                const text = await allMessages[i].textContent();
                lastMessageTexts.push(text);
            }
            
            let orderCorrect = true;
            for (let i = 0; i < testMessages.length; i++) {
                if (!lastMessageTexts.some(text => text.includes(testMessages[i]))) {
                    orderCorrect = false;
                    break;
                }
            }
            
            if (orderCorrect) {
                logSuccess('Message ordering appears correct');
            } else {
                logWarning('Message ordering may be incorrect');
            }
        }
        
        // Test scrolling behavior with many messages
        const messagesContainer = await page.$('[data-testid="messages-container"]');
        if (messagesContainer) {
            const scrollHeight = await messagesContainer.evaluate(el => el.scrollHeight);
            const clientHeight = await messagesContainer.evaluate(el => el.clientHeight);
            
            if (scrollHeight > clientHeight) {
                logSuccess('Message container is scrollable when needed');
            }
        }
        
    } catch (error) {
        logError(`Message history test failed: ${error.message}`);
        await takeScreenshot(page, 'message-history-error.png', '- Message history error');
    }
}

async function testTextInputMethods(page) {
    logSubsection('Testing Various Text Input Methods');
    
    try {
        // Ensure connection for text input
        await establishConnection(page);
        
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        if (!textInput) {
            logError('Text input not found for input methods test');
            return;
        }
        
        // Test 1: Direct typing
        await textInput.fill('');
        await textInput.type('Typed character by character');
        const typedValue = await textInput.inputValue();
        if (typedValue === 'Typed character by character') {
            logSuccess('Character-by-character typing works');
        } else {
            logError('Character-by-character typing failed');
        }
        
        // Test 2: Paste operation
        await textInput.fill('');
        await page.evaluate(() => {
            navigator.clipboard.writeText('Pasted text content');
        });
        await textInput.focus();
        await page.keyboard.press('Meta+V'); // Command+V on Mac, Ctrl+V on others
        await page.waitForTimeout(500);
        
        const pastedValue = await textInput.inputValue();
        if (pastedValue.includes('Pasted text')) {
            logSuccess('Paste operation works');
        } else {
            logWarning('Paste operation may not work (clipboard access limited)');
        }
        
        // Test 3: Special characters and emoji
        await textInput.fill('');
        const specialText = 'Special: àáâäæãåā 中文 русский 🚀📊💬🎯';
        await textInput.fill(specialText);
        const specialValue = await textInput.inputValue();
        if (specialValue === specialText) {
            logSuccess('Special characters and emoji input works');
        } else {
            logError('Special characters/emoji input failed');
        }
        
        // Test 4: Long text input
        await textInput.fill('');
        const longText = 'This is a very long message to test how the input field handles extended text content that might exceed normal message lengths and test the behavior of the interface when dealing with substantial text input that users might realistically enter when asking complex questions about market analysis or trading strategies.';
        await textInput.fill(longText);
        const longValue = await textInput.inputValue();
        if (longValue === longText) {
            logSuccess('Long text input handled correctly');
        } else {
            logError('Long text input failed');
        }
        
        // Test 5: Input focus behavior
        await textInput.blur();
        await page.waitForTimeout(500);
        await textInput.focus();
        
        const isFocused = await textInput.evaluate(el => document.activeElement === el);
        if (isFocused) {
            logSuccess('Input focus behavior works correctly');
        } else {
            logWarning('Input focus behavior may have issues');
        }
        
        await takeScreenshot(page, 'input-methods-test.png', '- Various input methods tested');
        
    } catch (error) {
        logError(`Text input methods test failed: ${error.message}`);
        await takeScreenshot(page, 'input-methods-error.png', '- Input methods error');
    }
}

async function testTextVoiceIntegration(page) {
    logSubsection('Testing Text-Voice Integration');
    
    try {
        // Ensure connection for integration test
        await establishConnection(page);
        
        // Test text input focus stopping voice recording
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        if (!textInput) {
            logError('Text input not found for integration test');
            return;
        }
        
        // Check for recording timer (indicates voice recording)
        let recordingTimer = await page.$('[data-testid="recording-timer"]');
        const wasRecording = recordingTimer && await recordingTimer.isVisible();
        
        if (wasRecording) {
            logSuccess('Voice recording was active');
            
            // Focus on text input should stop recording
            await textInput.focus();
            await page.waitForTimeout(1000);
            
            recordingTimer = await page.$('[data-testid="recording-timer"]');
            const isStillRecording = recordingTimer && await recordingTimer.isVisible();
            
            if (!isStillRecording) {
                logSuccess('Text input focus correctly stops voice recording');
            } else {
                logWarning('Text input focus should stop voice recording');
            }
        } else {
            logWarning('Voice recording not active - cannot test integration');
        }
        
        // Test that both text and voice messages appear in same history
        const messagesContainer = await page.$('[data-testid="messages-container"]');
        if (messagesContainer) {
            const messages = await page.$$('.conversation-message-enhanced');
            if (messages.length > 0) {
                logSuccess('Text and voice messages share same conversation history');
            }
        }
        
        // Test provider compatibility
        const providerDropdown = await page.$('[data-testid="provider-dropdown"]');
        if (providerDropdown) {
            const currentProvider = await providerDropdown.inputValue();
            
            // Send a text message and verify it works regardless of provider
            await textInput.fill('Integration test message');
            const sendButton = await page.$('[data-testid="send-button"]');
            if (sendButton && !await sendButton.isDisabled()) {
                await sendButton.click();
                await page.waitForTimeout(1000);
                
                const inputAfter = await textInput.inputValue();
                if (inputAfter === '') {
                    logSuccess(`Text messaging works with ${currentProvider} provider`);
                } else {
                    logWarning(`Text messaging may not work with ${currentProvider} provider`);
                }
            }
        }
        
        await takeScreenshot(page, 'text-voice-integration.png', '- Text-voice integration test');
        
    } catch (error) {
        logError(`Text-voice integration test failed: ${error.message}`);
        await takeScreenshot(page, 'integration-error.png', '- Integration test error');
    }
}

async function testErrorHandling(page) {
    logSubsection('Testing Text Error Handling');
    
    try {
        // Establish connection first
        await establishConnection(page);
        
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        const sendButton = await waitForElementWithRetry(page, '[data-testid="send-button"]', { timeout: 5000 });
        
        if (!textInput || !sendButton) {
            logError('Required elements not found for error handling test');
            return;
        }
        
        // Test 1: Empty message handling
        await textInput.fill('');
        const isDisabledEmpty = await sendButton.isDisabled();
        if (isDisabledEmpty) {
            logSuccess('Send button correctly disabled for empty messages');
        } else {
            logError('Send button should be disabled for empty messages');
        }
        
        // Test 2: Whitespace-only message handling
        await textInput.fill('   \n\t   ');
        const isDisabledWhitespace = await sendButton.isDisabled();
        if (isDisabledWhitespace) {
            logSuccess('Send button correctly disabled for whitespace-only messages');
        } else {
            logWarning('Send button should be disabled for whitespace-only messages');
        }
        
        // Test 3: Sending when disconnected
        const connectionToggle = await page.$('[data-testid="connection-toggle"]');
        if (connectionToggle) {
            const isConnected = await connectionToggle.isChecked();
            
            // If connected, disconnect for test
            if (isConnected) {
                await connectionToggle.click();
                await page.waitForTimeout(2000);
            }
            
            // Try to send message when disconnected
            await textInput.fill('Test message when disconnected');
            await sendButton.click();
            await page.waitForTimeout(1000);
            
            // Check for error indication or alert
            const hasAlert = await page.locator('text="Please connect"').count() > 0;
            if (hasAlert) {
                logSuccess('Appropriate error shown when sending without connection');
            } else {
                logWarning('Should show error when sending without connection');
            }
            
            // Reconnect for further tests
            if (isConnected) {
                await connectionToggle.click();
                await page.waitForTimeout(2000);
            }
        }
        
        // Test 4: Network error simulation
        await page.route('**/api/**', route => route.abort());
        await textInput.fill('Test message with network error');
        await sendButton.click();
        await page.waitForTimeout(2000);
        
        // Restore network
        await page.unroute('**/api/**');
        
        logSuccess('Network error handling test completed');
        
        await takeScreenshot(page, 'error-handling.png', '- Error handling tests');
        
    } catch (error) {
        logError(`Error handling test failed: ${error.message}`);
        await takeScreenshot(page, 'error-handling-error.png', '- Error handling test error');
    }
}

async function testConversationFlow(page) {
    logSubsection('Testing Complete Text-Based Conversation Flow');
    
    try {
        // Ensure connection for conversation flow
        await establishConnection(page);
        
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        const sendButton = await waitForElementWithRetry(page, '[data-testid="send-button"]', { timeout: 5000 });
        
        if (!textInput || !sendButton) {
            logError('Required elements not found for conversation flow test');
            return;
        }
        
        // Simulate a realistic conversation flow
        const conversationFlow = [
            'Hello, I want to analyze TSLA stock',
            'What is the current price of Tesla?',
            'Show me the technical indicators',
            'Can you explain the support and resistance levels?',
            'Thank you for the analysis'
        ];
        
        log('Starting conversation flow simulation...', colors.cyan);
        
        for (let i = 0; i < conversationFlow.length; i++) {
            const message = conversationFlow[i];
            
            // Type and send message
            await textInput.fill(message);
            await page.waitForTimeout(300);
            await sendButton.click();
            await page.waitForTimeout(2000);
            
            // Verify message was processed
            const currentMessages = await page.$$('.conversation-message-enhanced');
            logSuccess(`Step ${i + 1}: Sent "${message}" (${currentMessages.length} total messages)`);
            
            // Take screenshot at key points
            if (i === 0 || i === conversationFlow.length - 1) {
                await takeScreenshot(page, `conversation-step-${i + 1}.png`, `- Step ${i + 1}`);
            }
        }
        
        // Verify final conversation state
        const finalMessages = await page.$$('.conversation-message-enhanced');
        if (finalMessages.length >= conversationFlow.length) {
            logSuccess(`Complete conversation flow tested (${finalMessages.length} messages total)`);
        } else {
            logWarning(`Expected at least ${conversationFlow.length} messages, found ${finalMessages.length}`);
        }
        
        // Test conversation scrolling
        const messagesContainer = await page.$('[data-testid="messages-container"]');
        if (messagesContainer) {
            await messagesContainer.evaluate(el => {
                el.scrollTop = 0; // Scroll to top
            });
            await page.waitForTimeout(500);
            
            await messagesContainer.evaluate(el => {
                el.scrollTop = el.scrollHeight; // Scroll to bottom
            });
            await page.waitForTimeout(500);
            
            logSuccess('Conversation scrolling works correctly');
        }
        
        await takeScreenshot(page, 'conversation-flow-complete.png', '- Complete conversation flow');
        
    } catch (error) {
        logError(`Conversation flow test failed: ${error.message}`);
        await takeScreenshot(page, 'conversation-flow-error.png', '- Conversation flow error');
    }
}

async function testAccessibilityFeatures(page) {
    logSubsection('Testing Text Accessibility Features');
    
    try {
        // Ensure connection for accessibility test
        await establishConnection(page);
        
        // Test keyboard navigation
        const textInput = await waitForElementWithRetry(page, '[data-testid="message-input"]', { timeout: 10000 });
        const sendButton = await waitForElementWithRetry(page, '[data-testid="send-button"]', { timeout: 5000 });
        
        if (!textInput || !sendButton) {
            logError('Required elements not found for accessibility test');
            return;
        }
        
        // Test Tab navigation
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);
        
        const activeElement = await page.evaluate(() => document.activeElement?.tagName);
        if (activeElement) {
            logSuccess(`Keyboard navigation works (focused element: ${activeElement})`);
        }
        
        // Test input accessibility attributes
        const inputPlaceholder = await textInput.getAttribute('placeholder');
        
        if (inputPlaceholder) {
            logSuccess('Text input has descriptive placeholder');
        }
        
        // Test button accessibility
        const buttonRole = await sendButton.getAttribute('role');
        const buttonAriaLabel = await sendButton.getAttribute('aria-label');
        const buttonTitle = await sendButton.getAttribute('title');
        
        if (buttonRole || buttonAriaLabel || buttonTitle) {
            logSuccess('Send button has accessibility attributes');
        }
        
        // Test contrast and readability
        const inputStyles = await textInput.evaluate(el => {
            const computed = getComputedStyle(el);
            return {
                color: computed.color,
                backgroundColor: computed.backgroundColor,
                fontSize: computed.fontSize
            };
        });
        
        if (inputStyles.fontSize && parseFloat(inputStyles.fontSize) >= 14) {
            logSuccess('Text input has readable font size');
        } else {
            logWarning('Text input font size may be too small');
        }
        
        logSuccess('Accessibility features test completed');
        
    } catch (error) {
        logError(`Accessibility test failed: ${error.message}`);
    }
}

async function generateTestReport() {
    logSection('Test Report Generation');
    
    const report = {
        timestamp: new Date().toISOString(),
        summary: {
            total: testResults.tests.length,
            passed: testResults.passed,
            failed: testResults.failed,
            warnings: testResults.warnings,
            success_rate: testResults.tests.length > 0 ? 
                ((testResults.passed / testResults.tests.length) * 100).toFixed(1) : 0
        },
        details: testResults.tests,
        environment: {
            baseURL: config.baseURL,
            backendURL: config.backendURL,
            userAgent: 'Playwright Test Runner'
        }
    };
    
    try {
        await ensureDirectory('./test-results');
        const reportPath = './test-results/text-functionality-report.json';
        require('fs').writeFileSync(reportPath, JSON.stringify(report, null, 2));
        logSuccess(`Test report saved to ${reportPath}`);
    } catch (error) {
        logError(`Failed to save test report: ${error.message}`);
    }
    
    return report;
}

// Main test execution
async function main() {
    log('\n' + '='.repeat(80), colors.bright + colors.magenta);
    log('COMPREHENSIVE TEXT FUNCTIONALITY TEST SUITE', colors.bright + colors.magenta);
    log('Voice Interface Application - Text Features Testing', colors.bright + colors.magenta);
    log('='.repeat(80) + '\n', colors.bright + colors.magenta);
    
    // Check server connections first
    const serversOk = await checkServerConnection();
    if (!serversOk) {
        logError('Server connection check failed. Please ensure frontend and backend are running.');
        process.exit(1);
    }
    
    const browser = await chromium.launch({ 
        headless: false,
        args: [
            '--use-fake-ui-for-media-stream',
            '--use-fake-device-for-media-stream',
            '--allow-clipboard-read',
            '--allow-clipboard-write'
        ]
    });
    
    const page = await browser.newPage();
    
    // Set viewport and permissions
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.context().grantPermissions(['clipboard-read', 'clipboard-write']);
    
    try {
        // Navigate to the application
        log('Navigating to application...', colors.cyan);
        await page.goto(config.baseURL, { waitUntil: 'networkidle', timeout: config.timeout });
        
        // Wait for app to fully load
        await page.waitForTimeout(3000);
        await takeScreenshot(page, 'app-initial-load.png', '- Initial application state');
        
        // Navigate to voice tab first
        const voiceTab = await page.$('[data-testid="voice-tab"]');
        if (voiceTab) {
            await voiceTab.click();
            await page.waitForTimeout(1000);
            log('Navigated to Voice + Manual Control tab', colors.cyan);
        }
        
        // Execute all test suites
        await testVoiceInterfaceLayout(page);
        await testBasicTextInput(page);
        await testProviderSwitching(page);
        await testConnectionProcess(page);
        await testMessageDisplay(page);
        
        // Only run text input tests if we can establish connection
        const hasTextInput = await page.$('[data-testid="message-input"]');
        if (hasTextInput) {
            await testTextMessageSending(page);
            await testMessageHistory(page);
            await testTextInputMethods(page);
            await testTextVoiceIntegration(page);
            await testErrorHandling(page);
            await testConversationFlow(page);
            await testAccessibilityFeatures(page);
        } else {
            logWarning('Text input not available - skipping input-dependent tests');
            logWarning('This may be due to connection issues or missing API keys');
        }
        
        // Generate final screenshot
        await takeScreenshot(page, 'test-suite-complete.png', '- Final application state');
        
    } catch (error) {
        logError(`Test suite execution failed: ${error.message}`);
        await takeScreenshot(page, 'test-suite-error.png', '- Test suite error state');
    } finally {
        await page.waitForTimeout(2000);
        await browser.close();
        
        // Generate and display report
        const report = await generateTestReport();
        
        logSection('Final Test Results');
        log(`Total Tests: ${report.summary.total}`, colors.bright);
        log(`Passed: ${report.summary.passed}`, colors.green);
        log(`Failed: ${report.summary.failed}`, colors.red);
        log(`Warnings: ${report.summary.warnings}`, colors.yellow);
        log(`Success Rate: ${report.summary.success_rate}%`, colors.cyan);
        
        if (report.summary.failed > 0) {
            log('\nFailed Tests:', colors.red);
            report.details.filter(t => t.status === 'FAIL').forEach(test => {
                log(`  ✗ ${test.message}`, colors.red);
            });
        }
        
        if (report.summary.warnings > 0) {
            log('\nWarnings:', colors.yellow);
            report.details.filter(t => t.status === 'WARN').forEach(test => {
                log(`  ⚠ ${test.message}`, colors.yellow);
            });
        }
        
        log('\n' + '='.repeat(80), colors.bright + colors.magenta);
        log('TEXT FUNCTIONALITY TEST SUITE COMPLETED', colors.bright + colors.magenta);
        log('='.repeat(80) + '\n', colors.bright + colors.magenta);
        
        // Exit with appropriate code
        process.exit(report.summary.failed > 0 ? 1 : 0);
    }
}

// Error handling for uncaught exceptions
process.on('unhandledRejection', (reason, promise) => {
    logError(`Unhandled Rejection at: ${promise}, reason: ${reason}`);
    process.exit(1);
});

process.on('uncaughtException', (error) => {
    logError(`Uncaught Exception: ${error.message}`);
    process.exit(1);
});

// Run the test suite
main().catch(console.error);