const { chromium } = require('playwright');

class UserQueryFlowTester {
    constructor() {
        this.browser = null;
        this.page = null;
        this.errors = [];
        this.websocketEvents = [];
        this.networkRequests = [];
        this.consoleMessages = [];
        this.screenshots = [];
    }

    async setupTestEnvironment() {
        console.log('🚀 Starting Comprehensive User Query Flow Test...\n');
        
        this.browser = await chromium.launch({
            headless: false,
            slowMo: 1000,
            devtools: true,
            args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
        });

        const context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            recordVideo: { dir: 'test-recordings/' },
            permissions: ['microphone']
        });

        this.page = await context.newPage();
        
        // Monitor console messages
        this.page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            
            this.consoleMessages.push({ type, text, timestamp: Date.now() });
            
            if (type === 'error') {
                console.log(`🔴 CONSOLE ERROR: ${text}`);
                this.errors.push({ type: 'console', message: text, timestamp: Date.now() });
            } else if (type === 'warning') {
                console.log(`🟡 CONSOLE WARNING: ${text}`);
            } else if (text.includes('WebSocket') || text.includes('OpenAI') || text.includes('Realtime')) {
                console.log(`🔵 REALTIME INFO: ${text}`);
            }
        });

        // Monitor network requests
        this.page.on('request', request => {
            const url = request.url();
            const method = request.method();
            
            this.networkRequests.push({
                method,
                url,
                timestamp: Date.now(),
                type: 'request'
            });
            
            if (url.includes('symbol-search') || url.includes('openai') || url.includes('ask')) {
                console.log(`📤 API REQUEST: ${method} ${url}`);
            }
        });

        this.page.on('response', response => {
            const url = response.url();
            const status = response.status();
            
            if (url.includes('symbol-search') || url.includes('openai') || url.includes('ask')) {
                console.log(`📥 API RESPONSE: ${status} ${url}`);
                if (status >= 400) {
                    this.errors.push({ 
                        type: 'api_error', 
                        message: `${status} error for ${url}`, 
                        timestamp: Date.now() 
                    });
                }
            }
        });

        // Monitor WebSocket connections specifically
        this.page.on('websocket', ws => {
            const url = ws.url();
            console.log(`🔗 WebSocket Connection: ${url}`);
            
            this.websocketEvents.push({
                event: 'connection',
                url,
                timestamp: Date.now()
            });
            
            ws.on('framereceived', frame => {
                if (frame.payload) {
                    const payload = frame.payload.toString();
                    console.log(`📥 WebSocket Received: ${payload.substring(0, 100)}...`);
                    this.websocketEvents.push({
                        event: 'received',
                        payload: payload.substring(0, 200),
                        timestamp: Date.now()
                    });
                }
            });
            
            ws.on('framesent', frame => {
                if (frame.payload) {
                    const payload = frame.payload.toString();
                    console.log(`📤 WebSocket Sent: ${payload.substring(0, 100)}...`);
                    this.websocketEvents.push({
                        event: 'sent',
                        payload: payload.substring(0, 200),
                        timestamp: Date.now()
                    });
                }
            });
            
            ws.on('close', () => {
                console.log('🔌 WebSocket Closed');
                this.websocketEvents.push({
                    event: 'close',
                    timestamp: Date.now()
                });
            });
        });

        await this.page.goto('http://localhost:5174');
        await this.takeScreenshot('01_initial_load');
        await this.page.waitForTimeout(3000); // Let page stabilize
    }

    async takeScreenshot(name) {
        const filename = `test-${name}-${Date.now()}.png`;
        await this.page.screenshot({ path: filename, fullPage: true });
        this.screenshots.push(filename);
        console.log(`📸 Screenshot: ${filename}`);
        return filename;
    }

    async testBasicPageLoad() {
        console.log('\n🔍 TESTING: Basic Page Load');
        console.log('=' .repeat(40));

        // Check if page loaded correctly
        const title = await this.page.title();
        console.log(`📄 Page Title: ${title}`);

        // Look for main application elements
        const mainElements = [
            '.trading-dashboard',
            '.insights-panel', 
            '.chart-section',
            '.analysis-panel'
        ];

        for (const selector of mainElements) {
            const element = await this.page.$(selector);
            if (element) {
                console.log(`✅ Found: ${selector}`);
            } else {
                console.log(`❌ Missing: ${selector}`);
                this.errors.push({ type: 'missing_element', message: `Missing ${selector}`, timestamp: Date.now() });
            }
        }

        await this.takeScreenshot('02_page_elements');
    }

    async testTabNavigation() {
        console.log('\n🔍 TESTING: Tab Navigation');
        console.log('=' .repeat(40));

        try {
            // Find the voice tab with correct selector
            const voiceTab = this.page.locator('[data-testid="voice-tab"]');
            const voiceTabExists = await voiceTab.count() > 0;
            
            console.log(`🎭 Voice tab exists: ${voiceTabExists}`);
            
            if (voiceTabExists) {
                const isVisible = await voiceTab.isVisible();
                const isEnabled = await voiceTab.isEnabled();
                
                console.log(`👁️  Voice tab visible: ${isVisible}`);
                console.log(`⚡ Voice tab enabled: ${isEnabled}`);
                
                if (isVisible && isEnabled) {
                    console.log('🖱️  Clicking Voice + Manual Control tab...');
                    await voiceTab.click();
                    await this.page.waitForTimeout(1000);
                    await this.takeScreenshot('03_voice_tab_active');
                    console.log('✅ Successfully navigated to Voice tab');
                } else {
                    this.errors.push({ type: 'tab_interaction', message: 'Voice tab not clickable', timestamp: Date.now() });
                }
            } else {
                this.errors.push({ type: 'missing_tab', message: 'Voice tab not found', timestamp: Date.now() });
            }
        } catch (error) {
            console.log(`❌ Tab navigation error: ${error.message}`);
            this.errors.push({ type: 'tab_error', message: error.message, timestamp: Date.now() });
        }
    }

    async testVoiceConnectionFlow() {
        console.log('\n🔍 TESTING: Voice Connection Flow');
        console.log('=' .repeat(40));

        try {
            // Look for connection toggle
            const connectionToggle = this.page.locator('[data-testid="connection-toggle"]');
            const toggleExists = await connectionToggle.count() > 0;
            
            console.log(`🔘 Connection toggle exists: ${toggleExists}`);
            
            if (toggleExists) {
                const isChecked = await connectionToggle.isChecked();
                console.log(`🔘 Toggle current state: ${isChecked ? 'ON' : 'OFF'}`);
                
                // If not connected, try to connect
                if (!isChecked) {
                    console.log('🔌 Attempting to connect...');
                    
                    // Clear any existing errors before testing
                    this.websocketEvents = [];
                    const errorsBefore = this.errors.length;
                    
                    // Click the toggle to connect
                    await connectionToggle.click();
                    await this.page.waitForTimeout(3000); // Wait for connection attempt
                    
                    await this.takeScreenshot('04_connection_attempt');
                    
                    // Check if connection was successful
                    const isNowChecked = await connectionToggle.isChecked();
                    console.log(`🔘 Toggle after click: ${isNowChecked ? 'ON' : 'OFF'}`);
                    
                    // Analyze WebSocket events
                    const wsConnections = this.websocketEvents.filter(e => e.event === 'connection');
                    const wsErrors = this.errors.slice(errorsBefore);
                    
                    console.log(`🔗 WebSocket connections attempted: ${wsConnections.length}`);
                    console.log(`❌ New errors after connection: ${wsErrors.length}`);
                    
                    if (wsErrors.length > 0) {
                        console.log('\n📋 Connection Errors:');
                        wsErrors.forEach(error => {
                            console.log(`   - ${error.message}`);
                        });
                    }
                    
                    if (wsConnections.length > 0) {
                        console.log('\n📋 WebSocket Connection URLs:');
                        wsConnections.forEach(conn => {
                            console.log(`   - ${conn.url}`);
                        });
                    }
                }
            } else {
                this.errors.push({ type: 'missing_toggle', message: 'Connection toggle not found', timestamp: Date.now() });
            }
        } catch (error) {
            console.log(`❌ Voice connection error: ${error.message}`);
            this.errors.push({ type: 'connection_error', message: error.message, timestamp: Date.now() });
        }
    }

    async testTextInputFlow() {
        console.log('\n🔍 TESTING: Voice Conversation Text Input Flow');
        console.log('=' .repeat(40));

        try {
            // First ensure we're on the Voice + Manual Control tab
            const voiceTab = this.page.locator('[data-testid="tab-voice-manual"]');
            if (await voiceTab.count() > 0) {
                if (!(await voiceTab.getAttribute('class'))?.includes('active')) {
                    console.log('🎭 Switching to Voice + Manual Control tab...');
                    await voiceTab.click();
                    await this.page.waitForTimeout(1000);
                    await this.takeScreenshot('04_voice_tab_activated');
                }
            }

            // Look specifically for voice conversation input (NOT Market Insights search)
            const voiceInputSelectors = [
                '[data-testid="message-input"]',  // The correct voice conversation input
                'input[placeholder*="Type a message"]',
                '.text-input-modern',
                '[data-testid="voice-interface"] input[type="text"]'
            ];

            let textInput = null;
            let inputSelector = null;

            console.log('🔍 Searching for voice conversation input field...');
            for (const selector of voiceInputSelectors) {
                const element = this.page.locator(selector);
                const count = await element.count();
                if (count > 0) {
                    const isVisible = await element.isVisible();
                    console.log(`   Checking ${selector}: found=${count}, visible=${isVisible}`);
                    if (isVisible) {
                        textInput = element;
                        inputSelector = selector;
                        console.log(`✅ Found voice conversation input: ${selector}`);
                        break;
                    }
                }
            }

            // If voice input not found, check if we need to connect first
            if (!textInput) {
                console.log('❌ Voice conversation input not found!');
                console.log('💡 Note: Voice input only appears when connected to voice service');
                
                // Check connection state
                const connectionToggle = this.page.locator('[data-testid="connection-toggle"]');
                if (await connectionToggle.count() > 0 && await connectionToggle.isVisible()) {
                    console.log('🔌 Attempting to connect to voice service first...');
                    try {
                        await connectionToggle.click();
                        await this.page.waitForTimeout(3000);
                        
                        // Try finding voice input again after connection
                        textInput = this.page.locator('[data-testid="message-input"]');
                        if (await textInput.count() > 0 && await textInput.isVisible()) {
                            inputSelector = '[data-testid="message-input"]';
                            console.log('✅ Voice input now visible after connection');
                        }
                    } catch (connectError) {
                        console.log(`❌ Connection failed: ${connectError.message}`);
                    }
                }
                
                if (!textInput || !(await textInput.isVisible())) {
                    console.log('❌ Voice conversation input still not available');
                    this.errors.push({ 
                        type: 'missing_voice_input', 
                        message: 'Voice conversation input not found - may need connection', 
                        timestamp: Date.now() 
                    });
                    return;
                }
            }

            // Test text input functionality
            const testMessage = 'What is the current price of Apple stock?';
            
            console.log(`⌨️  Testing text input with: "${testMessage}"`);
            
            // Clear any existing errors
            const errorsBefore = this.errors.length;
            const requestsBefore = this.networkRequests.length;
            
            await textInput.fill(testMessage);
            await this.takeScreenshot('05_text_input_filled');
            
            // Look for send button
            const sendButtonSelectors = [
                '[data-testid="send-btn"]',
                'button[type="submit"]',
                'button:has-text("Send")',
                '.send-button'
            ];

            let sendButton = null;
            for (const selector of sendButtonSelectors) {
                const element = this.page.locator(selector);
                if (await element.count() > 0 && await element.isVisible()) {
                    sendButton = element;
                    console.log(`✅ Found send button: ${selector}`);
                    break;
                }
            }

            if (sendButton && await sendButton.isEnabled()) {
                console.log('📤 Clicking send button...');
                await sendButton.click();
                await this.page.waitForTimeout(3000); // Wait for response
                
                await this.takeScreenshot('06_after_send');
                
                // Analyze what happened
                const newErrors = this.errors.slice(errorsBefore);
                const newRequests = this.networkRequests.slice(requestsBefore);
                
                console.log(`📡 New API requests: ${newRequests.length}`);
                console.log(`❌ New errors: ${newErrors.length}`);
                
                if (newRequests.length > 0) {
                    console.log('\n📋 API Requests Made:');
                    newRequests.forEach(req => {
                        console.log(`   - ${req.method} ${req.url}`);
                    });
                }
                
                if (newErrors.length > 0) {
                    console.log('\n📋 Errors During Text Input:');
                    newErrors.forEach(error => {
                        console.log(`   - ${error.message}`);
                    });
                }
                
                // Look for response
                await this.checkForResponse();
                
            } else {
                console.log('❌ Send button not found or not enabled');
                this.errors.push({ type: 'send_button', message: 'Send button not available', timestamp: Date.now() });
            }

        } catch (error) {
            console.log(`❌ Text input error: ${error.message}`);
            this.errors.push({ type: 'text_input_error', message: error.message, timestamp: Date.now() });
        }
    }

    async checkForResponse() {
        console.log('\n🔍 CHECKING: Response Handling');
        console.log('-'.repeat(30));

        try {
            // Wait a bit more for potential responses
            await this.page.waitForTimeout(2000);

            // Look for response areas
            const responseSelectors = [
                '[data-testid="response"]',
                '.response',
                '.message',
                '.chat-message',
                '.ai-response',
                '.conversation-area'
            ];

            let foundResponses = 0;
            for (const selector of responseSelectors) {
                const elements = this.page.locator(selector);
                const count = await elements.count();
                if (count > 0) {
                    foundResponses += count;
                    console.log(`💬 Found ${count} responses with selector: ${selector}`);
                    
                    // Get text content of first few responses
                    for (let i = 0; i < Math.min(count, 3); i++) {
                        const element = elements.nth(i);
                        const text = await element.textContent();
                        if (text && text.trim()) {
                            console.log(`   Response ${i + 1}: ${text.substring(0, 100)}...`);
                        }
                    }
                }
            }

            if (foundResponses === 0) {
                console.log('❌ No response elements found');
                this.errors.push({ type: 'no_response', message: 'No response areas found', timestamp: Date.now() });
            } else {
                console.log(`✅ Found ${foundResponses} total response elements`);
            }

        } catch (error) {
            console.log(`❌ Error checking response: ${error.message}`);
            this.errors.push({ type: 'response_check_error', message: error.message, timestamp: Date.now() });
        }
    }

    async generateDetailedReport() {
        console.log('\n📊 COMPREHENSIVE TEST REPORT');
        console.log('=' .repeat(50));

        // Basic stats
        console.log(`\n📈 STATISTICS:`);
        console.log(`- Total Errors: ${this.errors.length}`);
        console.log(`- Console Messages: ${this.consoleMessages.length}`);
        console.log(`- Network Requests: ${this.networkRequests.length}`);
        console.log(`- WebSocket Events: ${this.websocketEvents.length}`);
        console.log(`- Screenshots: ${this.screenshots.length}`);

        // Error breakdown
        if (this.errors.length > 0) {
            console.log(`\n❌ ERROR BREAKDOWN:`);
            const errorTypes = this.errors.reduce((acc, error) => {
                acc[error.type] = (acc[error.type] || 0) + 1;
                return acc;
            }, {});
            
            Object.entries(errorTypes).forEach(([type, count]) => {
                console.log(`   ${type}: ${count}`);
            });

            console.log(`\n📋 DETAILED ERRORS:`);
            this.errors.forEach((error, index) => {
                console.log(`   ${index + 1}. [${error.type}] ${error.message}`);
            });
        }

        // WebSocket analysis
        if (this.websocketEvents.length > 0) {
            console.log(`\n🔗 WEBSOCKET ANALYSIS:`);
            const wsEventTypes = this.websocketEvents.reduce((acc, event) => {
                acc[event.event] = (acc[event.event] || 0) + 1;
                return acc;
            }, {});
            
            Object.entries(wsEventTypes).forEach(([event, count]) => {
                console.log(`   ${event}: ${count}`);
            });
        }

        // Console error analysis
        const consoleErrors = this.consoleMessages.filter(msg => msg.type === 'error');
        if (consoleErrors.length > 0) {
            console.log(`\n🔴 CONSOLE ERRORS (${consoleErrors.length}):`);
            consoleErrors.forEach((error, index) => {
                console.log(`   ${index + 1}. ${error.text}`);
            });
        }

        // Network analysis
        const apiRequests = this.networkRequests.filter(req => 
            req.url.includes('api/') || req.url.includes('openai') || req.url.includes('ask')
        );
        
        if (apiRequests.length > 0) {
            console.log(`\n📡 API REQUESTS (${apiRequests.length}):`);
            apiRequests.forEach((req, index) => {
                console.log(`   ${index + 1}. ${req.method} ${req.url}`);
            });
        }

        // Recommendations
        console.log(`\n💡 RECOMMENDATIONS:`);
        
        if (this.errors.some(e => e.message.includes('WebSocket'))) {
            console.log(`   🔧 WebSocket Issues:`);
            console.log(`      - Check OpenAI API key configuration`);
            console.log(`      - Verify WebSocket endpoint is running`);
            console.log(`      - Check for CORS or protocol mismatch issues`);
        }
        
        if (this.errors.some(e => e.type === 'missing_element')) {
            console.log(`   🔧 UI Element Issues:`);
            console.log(`      - Check component rendering`);
            console.log(`      - Verify CSS classes and selectors`);
            console.log(`      - Check for JavaScript errors preventing rendering`);
        }
        
        if (this.errors.some(e => e.type === 'api_error')) {
            console.log(`   🔧 API Issues:`);
            console.log(`      - Check backend server status`);
            console.log(`      - Verify API endpoint implementations`);
            console.log(`      - Check network connectivity`);
        }

        console.log(`\n📸 Screenshots saved: ${this.screenshots.join(', ')}`);
    }

    async runFullTest() {
        try {
            await this.setupTestEnvironment();
            
            await this.testBasicPageLoad();
            await this.testTabNavigation();
            await this.testVoiceConnectionFlow();
            await this.testTextInputFlow();
            
            await this.generateDetailedReport();
            
            console.log('\n✅ Test completed! Browser remaining open for manual inspection...');
            console.log('Press Ctrl+C to exit when ready.');
            
            // Keep browser open for manual inspection
            await new Promise(() => {});

        } catch (error) {
            console.log(`❌ Test execution error: ${error.message}`);
            await this.takeScreenshot('99_final_error');
        } finally {
            // Don't auto-close - let user inspect
        }
    }
}

// Run the comprehensive test
async function runTest() {
    const tester = new UserQueryFlowTester();
    await tester.runFullTest();
}

runTest().catch(console.error);