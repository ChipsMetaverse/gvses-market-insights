const { chromium } = require('playwright');

class TextFunctionalityDebugger {
    constructor() {
        this.browser = null;
        this.page = null;
        this.errors = [];
        this.networkIssues = [];
        this.stateChanges = [];
        this.screenshots = [];
    }

    async setupDebugEnvironment() {
        console.log('🚀 Initializing Text Functionality Debugger...\n');
        
        this.browser = await chromium.launch({
            headless: false,
            slowMo: 500, // Slow down operations for visibility
            devtools: true,
            args: ['--disable-web-security', '--disable-features=VizDisplayCompositor']
        });

        const context = await this.browser.newContext({
            viewport: { width: 1920, height: 1080 },
            recordVideo: { dir: 'debug-recordings/' },
            permissions: ['microphone']
        });

        this.page = await context.newPage();
        
        // Enable console monitoring
        this.page.on('console', msg => {
            const type = msg.type();
            const text = msg.text();
            
            if (type === 'error') {
                console.log(`🔴 CONSOLE ERROR: ${text}`);
                this.errors.push({ type: 'console', message: text, timestamp: Date.now() });
            } else if (type === 'warning') {
                console.log(`🟡 CONSOLE WARNING: ${text}`);
                this.errors.push({ type: 'warning', message: text, timestamp: Date.now() });
            } else if (text.includes('connection') || text.includes('websocket') || text.includes('provider')) {
                console.log(`🔵 CONNECTION INFO: ${text}`);
                this.stateChanges.push({ message: text, timestamp: Date.now() });
            }
        });

        // Monitor network failures
        this.page.on('requestfailed', request => {
            const failure = `${request.method()} ${request.url()} - ${request.failure().errorText}`;
            console.log(`🌐 NETWORK FAILURE: ${failure}`);
            this.networkIssues.push({ url: request.url(), error: request.failure().errorText, timestamp: Date.now() });
        });

        // Monitor WebSocket connections
        this.page.on('websocket', ws => {
            console.log(`🔗 WebSocket: ${ws.url()}`);
            
            ws.on('framereceived', frame => {
                if (frame.payload) {
                    console.log(`📥 WebSocket received: ${frame.payload.toString().substring(0, 100)}...`);
                }
            });
            
            ws.on('framesent', frame => {
                if (frame.payload) {
                    console.log(`📤 WebSocket sent: ${frame.payload.toString().substring(0, 100)}...`);
                }
            });
            
            ws.on('close', () => console.log('🔌 WebSocket closed'));
        });

        await this.page.goto('http://localhost:5174');
        await this.takeDebugScreenshot('01_initial_load');
    }

    async takeDebugScreenshot(name) {
        const filename = `debug-${name}-${Date.now()}.png`;
        await this.page.screenshot({ path: filename, fullPage: true });
        this.screenshots.push(filename);
        console.log(`📸 Screenshot saved: ${filename}`);
        return filename;
    }

    async debugProviderDropdownIssue() {
        console.log('\n🔍 DEBUGGING: Provider Dropdown Issue');
        console.log('=' .repeat(50));

        try {
            // Navigate to the correct tab
            await this.page.waitForSelector('[data-testid="tab-voice-manual"]', { timeout: 10000 });
            await this.page.click('[data-testid="tab-voice-manual"]');
            console.log('✅ Clicked Voice + Manual Control tab');
            
            await this.page.waitForTimeout(1000);
            await this.takeDebugScreenshot('02_voice_manual_tab');

            // Find provider dropdown
            const providerDropdown = this.page.locator('[data-testid="provider-dropdown"]');
            
            // Check if dropdown exists
            const dropdownExists = await providerDropdown.count() > 0;
            console.log(`📋 Provider dropdown exists: ${dropdownExists}`);
            
            if (!dropdownExists) {
                console.log('❌ Provider dropdown not found! Looking for alternative selectors...');
                
                // Look for any dropdown or select element
                const allSelects = await this.page.locator('select').count();
                const allDropdowns = await this.page.locator('[role="combobox"]').count();
                console.log(`🔍 Found ${allSelects} select elements, ${allDropdowns} combobox elements`);
                
                if (allSelects > 0) {
                    const firstSelect = this.page.locator('select').first();
                    const selectId = await firstSelect.getAttribute('id') || 'unknown';
                    console.log(`🎯 Found select element with id: ${selectId}`);
                    return await this.analyzeElement(firstSelect, 'Provider Select');
                }
                return;
            }

            return await this.analyzeElement(providerDropdown, 'Provider Dropdown');

        } catch (error) {
            console.log(`❌ Error in provider dropdown debug: ${error.message}`);
            await this.takeDebugScreenshot('02_provider_error');
        }
    }

    async analyzeElement(element, name) {
        console.log(`\n🔬 ANALYZING: ${name}`);
        console.log('-'.repeat(30));

        try {
            const isVisible = await element.isVisible();
            const isEnabled = await element.isEnabled();
            const isAttached = await element.count() > 0;
            
            console.log(`👁️  Visible: ${isVisible}`);
            console.log(`⚡ Enabled: ${isEnabled}`);
            console.log(`🔗 Attached: ${isAttached}`);

            if (isAttached) {
                const tagName = await element.first().evaluate(el => el.tagName);
                const className = await element.first().getAttribute('class') || 'none';
                const disabled = await element.first().getAttribute('disabled');
                const ariaDisabled = await element.first().getAttribute('aria-disabled');
                
                console.log(`🏷️  Tag: ${tagName}`);
                console.log(`🎨 Classes: ${className}`);
                console.log(`🚫 Disabled attr: ${disabled}`);
                console.log(`🔒 Aria-disabled: ${ariaDisabled}`);

                // Check for parent container issues
                const parentClasses = await element.first().evaluate(el => 
                    el.parentElement ? el.parentElement.className : 'no parent'
                );
                console.log(`👨‍👧‍👦 Parent classes: ${parentClasses}`);

                // Check computed styles
                const computedStyle = await element.first().evaluate(el => {
                    const style = window.getComputedStyle(el);
                    return {
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        pointerEvents: style.pointerEvents
                    };
                });
                console.log(`💅 Computed styles:`, computedStyle);

                if (!isEnabled) {
                    console.log(`\n🔧 POTENTIAL FIXES for ${name}:`);
                    console.log('1. Check connection state - dropdown might be disabled when connected');
                    console.log('2. Look for conditional rendering based on provider state');
                    console.log('3. Verify event handlers are properly attached');
                    console.log('4. Check for CSS that might be preventing interactions');
                }
            }

        } catch (error) {
            console.log(`❌ Error analyzing ${name}: ${error.message}`);
        }
    }

    async debugConnectionProcess() {
        console.log('\n🔍 DEBUGGING: Connection Process');
        console.log('=' .repeat(50));

        try {
            // Look for connection button
            const connectBtn = this.page.locator('[data-testid="connect-btn"]');
            const connectBtnExists = await connectBtn.count() > 0;
            
            if (!connectBtnExists) {
                console.log('❌ Connect button not found! Looking for alternatives...');
                
                // Look for any button with "connect" text
                const connectButtons = this.page.locator('button').filter({ hasText: /connect/i });
                const count = await connectButtons.count();
                console.log(`🔍 Found ${count} buttons with "connect" text`);
                
                if (count > 0) {
                    const firstConnectBtn = connectButtons.first();
                    await this.analyzeElement(firstConnectBtn, 'Connect Button');
                    
                    // Try to click it
                    const isClickable = await firstConnectBtn.isEnabled() && await firstConnectBtn.isVisible();
                    if (isClickable) {
                        console.log('🖱️  Attempting to click connect button...');
                        await firstConnectBtn.click();
                        await this.page.waitForTimeout(2000);
                        await this.takeDebugScreenshot('03_after_connect');
                        
                        // Monitor state changes after connection
                        await this.monitorConnectionState();
                    }
                }
                return;
            }

            await this.analyzeElement(connectBtn, 'Connect Button');

        } catch (error) {
            console.log(`❌ Error in connection debug: ${error.message}`);
            await this.takeDebugScreenshot('03_connection_error');
        }
    }

    async monitorConnectionState() {
        console.log('\n📊 MONITORING: Connection State Changes');
        console.log('-'.repeat(40));

        try {
            // Wait for potential state changes
            await this.page.waitForTimeout(3000);

            // Check for connection status indicators
            const statusSelectors = [
                '[data-testid="connection-status"]',
                '.connection-status',
                '.status-indicator',
                '[data-connection-status]'
            ];

            for (const selector of statusSelectors) {
                const element = this.page.locator(selector);
                if (await element.count() > 0) {
                    const text = await element.textContent();
                    console.log(`📍 Status (${selector}): ${text}`);
                }
            }

            // Check for WebSocket connection indicators
            const wsIndicators = await this.page.evaluate(() => {
                // Check for common WebSocket variable names
                const wsVars = ['websocket', 'ws', 'connection', 'socket'];
                const found = [];
                
                wsVars.forEach(varName => {
                    if (window[varName]) {
                        found.push({
                            name: varName,
                            readyState: window[varName].readyState,
                            url: window[varName].url
                        });
                    }
                });
                
                return found;
            });

            console.log('🔌 WebSocket connections found:', wsIndicators);

            // Re-check provider dropdown state after connection
            await this.debugProviderDropdownIssue();

        } catch (error) {
            console.log(`❌ Error monitoring connection state: ${error.message}`);
        }
    }

    async testTextInputOutput() {
        console.log('\n🔍 DEBUGGING: Text Input/Output Functionality');
        console.log('=' .repeat(50));

        try {
            // Look for text input field
            const textInputSelectors = [
                '[data-testid="text-input"]',
                'textarea',
                'input[type="text"]',
                '.text-input',
                '[placeholder*="message"]',
                '[placeholder*="text"]'
            ];

            let textInput = null;
            for (const selector of textInputSelectors) {
                const element = this.page.locator(selector);
                if (await element.count() > 0 && await element.isVisible()) {
                    textInput = element;
                    console.log(`✅ Found text input: ${selector}`);
                    break;
                }
            }

            if (!textInput) {
                console.log('❌ No text input field found!');
                await this.takeDebugScreenshot('04_no_text_input');
                return;
            }

            await this.analyzeElement(textInput, 'Text Input Field');

            // Test typing in the input
            if (await textInput.isEnabled()) {
                console.log('⌨️  Testing text input...');
                await textInput.fill('Test message for debugging');
                await this.takeDebugScreenshot('04_text_input_filled');
                
                // Look for send button
                const sendBtnSelectors = [
                    '[data-testid="send-btn"]',
                    'button[type="submit"]',
                    'button:has-text("Send")',
                    '.send-button'
                ];

                for (const selector of sendBtnSelectors) {
                    const sendBtn = this.page.locator(selector);
                    if (await sendBtn.count() > 0) {
                        console.log(`🚀 Found send button: ${selector}`);
                        await this.analyzeElement(sendBtn, 'Send Button');
                        
                        if (await sendBtn.isEnabled()) {
                            console.log('📤 Testing message send...');
                            await sendBtn.click();
                            await this.page.waitForTimeout(2000);
                            await this.takeDebugScreenshot('05_after_send');
                            
                            // Monitor for response
                            await this.monitorTextResponse();
                        }
                        break;
                    }
                }
            }

        } catch (error) {
            console.log(`❌ Error testing text input/output: ${error.message}`);
            await this.takeDebugScreenshot('04_text_io_error');
        }
    }

    async monitorTextResponse() {
        console.log('\n📥 MONITORING: Text Response');
        console.log('-'.repeat(30));

        try {
            // Wait for potential response
            await this.page.waitForTimeout(5000);

            // Look for response/message containers
            const responseSelectors = [
                '[data-testid="response"]',
                '.response',
                '.message',
                '.chat-message',
                '.ai-response'
            ];

            for (const selector of responseSelectors) {
                const elements = this.page.locator(selector);
                const count = await elements.count();
                if (count > 0) {
                    console.log(`💬 Found ${count} responses with selector: ${selector}`);
                    
                    for (let i = 0; i < Math.min(count, 3); i++) {
                        const element = elements.nth(i);
                        const text = await element.textContent();
                        console.log(`  Response ${i + 1}: ${text?.substring(0, 100)}...`);
                    }
                }
            }

        } catch (error) {
            console.log(`❌ Error monitoring text response: ${error.message}`);
        }
    }

    async generateFixRecommendations() {
        console.log('\n🛠️  FIX RECOMMENDATIONS');
        console.log('=' .repeat(50));

        console.log('\n📋 Based on debugging analysis:');

        if (this.errors.some(e => e.message.includes('provider'))) {
            console.log('\n🔧 PROVIDER DROPDOWN FIXES:');
            console.log('1. Check if dropdown is conditionally disabled based on connection state');
            console.log('2. Verify provider state management in React components');
            console.log('3. Look for useEffect dependencies that might cause re-renders');
            console.log('4. Check CSS classes that might override enabled state');
        }

        if (this.errors.some(e => e.message.includes('websocket') || e.message.includes('connection'))) {
            console.log('\n🔌 CONNECTION FIXES:');
            console.log('1. Verify WebSocket connection URL and authentication');
            console.log('2. Check connection state management in React context');
            console.log('3. Ensure proper cleanup of WebSocket connections');
            console.log('4. Add connection retry logic for failed attempts');
        }

        if (this.networkIssues.length > 0) {
            console.log('\n🌐 NETWORK FIXES:');
            console.log('1. Check API endpoint availability and CORS configuration');
            console.log('2. Verify authentication tokens and headers');
            console.log('3. Add proper error handling for network failures');
            console.log('4. Implement request retry mechanisms');
        }

        console.log('\n📊 ERROR SUMMARY:');
        console.log(`- Console Errors: ${this.errors.filter(e => e.type === 'console').length}`);
        console.log(`- Warnings: ${this.errors.filter(e => e.type === 'warning').length}`);
        console.log(`- Network Issues: ${this.networkIssues.length}`);
        console.log(`- State Changes: ${this.stateChanges.length}`);
        console.log(`- Screenshots: ${this.screenshots.length}`);

        // Show specific error patterns
        const errorPatterns = this.errors.reduce((patterns, error) => {
            const key = error.message.split(' ')[0];
            patterns[key] = (patterns[key] || 0) + 1;
            return patterns;
        }, {});

        console.log('\n🏷️  ERROR PATTERNS:');
        Object.entries(errorPatterns).forEach(([pattern, count]) => {
            console.log(`  ${pattern}: ${count} occurrences`);
        });
    }

    async runDebugSession() {
        try {
            await this.setupDebugEnvironment();
            
            console.log('\n⏱️  Waiting for application to stabilize...');
            await this.page.waitForTimeout(3000);

            // Run debug tests in sequence
            await this.debugProviderDropdownIssue();
            await this.debugConnectionProcess();
            await this.testTextInputOutput();

            // Generate recommendations
            await this.generateFixRecommendations();

            console.log('\n✅ Debug session completed!');
            console.log(`📸 Screenshots saved: ${this.screenshots.join(', ')}`);
            
            // Keep browser open for manual inspection
            console.log('\n🔍 Browser will remain open for manual inspection...');
            console.log('Press Ctrl+C to exit when ready.');
            
            // Wait indefinitely until user closes
            await new Promise(() => {});

        } catch (error) {
            console.log(`❌ Debug session error: ${error.message}`);
            await this.takeDebugScreenshot('99_final_error');
        } finally {
            if (this.browser) {
                // Don't close automatically - let user inspect
                // await this.browser.close();
            }
        }
    }
}

// Run the debug session
async function runDebug() {
    const debugInstance = new TextFunctionalityDebugger();
    await debugInstance.runDebugSession();
}

runDebug().catch(console.error);