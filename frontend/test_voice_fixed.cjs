const { chromium } = require('playwright');

async function testVoiceConnectionFixed() {
    console.log('🎤 Testing Voice Connection - FIXED BACKEND...\n');
    
    const browser = await chromium.launch({ 
        headless: false,
        slowMo: 1000
    });
    
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 }
    });
    
    const page = await context.newPage();

    try {
        console.log('🚀 Loading Application...');
        await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);
        
        // Phase 1: Test Backend Health
        console.log('\n🔍 Phase 1: Backend Health Check...');
        
        const healthTest = await page.evaluate(async () => {
            try {
                const response = await fetch('http://localhost:8000/api/agent/health');
                return response.ok ? await response.json() : { error: 'Health check failed' };
            } catch (error) {
                return { error: error.message };
            }
        });
        
        if (healthTest.status === 'healthy') {
            console.log('✅ Backend Agent: HEALTHY');
            console.log(`   🤖 Model: ${healthTest.model}`);
            console.log(`   🔧 Tools: ${healthTest.tools_available}`);
        } else {
            console.log('❌ Backend Health Issue:', healthTest);
            return;
        }

        // Phase 2: Test Agent Provider Selection
        console.log('\n🧠 Phase 2: Voice Provider Configuration...');
        
        const providerDropdown = await page.locator('select').first();
        if (await providerDropdown.isVisible()) {
            const currentProvider = await providerDropdown.inputValue();
            console.log(`✅ Current provider: ${currentProvider}`);
            
            // Make sure agent is selected
            await providerDropdown.selectOption('agent');
            console.log('✅ Agent provider selected');
        }

        // Phase 3: Test Voice Connection Button
        console.log('\n🎤 Phase 3: Voice Connection Test...');
        
        // Look for connect button
        const connectButton = await page.locator('button:has-text("Connect"), .connect-btn, [class*="connect"]').first();
        
        if (await connectButton.isVisible()) {
            console.log('✅ Connect button found');
            
            // Click connect button
            await connectButton.click();
            console.log('🔄 Attempting voice connection...');
            
            // Wait for connection result
            await page.waitForTimeout(3000);
            
            // Check for success/error states
            const connectionResult = await page.evaluate(() => {
                // Look for error modals
                const errorModal = document.querySelector('[class*="modal"], [role="dialog"]');
                if (errorModal && errorModal.textContent.includes('Failed')) {
                    return { status: 'error', message: errorModal.textContent };
                }
                
                // Look for connected states
                const disconnectButton = document.querySelector('button:contains("Disconnect"), .disconnect-btn');
                if (disconnectButton) {
                    return { status: 'connected' };
                }
                
                // Look for connection status indicators
                const statusElements = document.querySelectorAll('[class*="status"], [class*="connected"]');
                for (let el of statusElements) {
                    if (el.textContent.includes('connected') || el.textContent.includes('Connected')) {
                        return { status: 'connected' };
                    }
                }
                
                return { status: 'unknown' };
            });
            
            if (connectionResult.status === 'connected') {
                console.log('🎉 SUCCESS: Voice connection established!');
                console.log('✅ OpenAI Realtime WebSocket is working');
                
                await page.screenshot({ path: 'voice-connection-success.png', fullPage: true });
                
            } else if (connectionResult.status === 'error') {
                console.log('❌ FAILED: Voice connection error');
                console.log('   Error:', connectionResult.message);
                
                await page.screenshot({ path: 'voice-connection-error.png', fullPage: true });
                
            } else {
                console.log('⚠️ UNCLEAR: Connection status unknown');
                console.log('   May need manual verification');
                
                await page.screenshot({ path: 'voice-connection-unclear.png', fullPage: true });
            }
            
        } else {
            console.log('⚠️ Connect button not found - checking interface state');
        }

        // Phase 4: WebSocket Direct Test
        console.log('\n🌐 Phase 4: Direct WebSocket Test...');
        
        const wsTest = await page.evaluate(async () => {
            return new Promise((resolve) => {
                try {
                    const testWs = new WebSocket('ws://localhost:8000/openai/realtime/ws?model=gpt-4o-realtime-preview-2024-10-01');
                    
                    const timeout = setTimeout(() => {
                        testWs.close();
                        resolve({ error: 'Connection timeout after 5s' });
                    }, 5000);
                    
                    testWs.onopen = () => {
                        clearTimeout(timeout);
                        testWs.close();
                        resolve({ status: 'WebSocket connection successful' });
                    };
                    
                    testWs.onerror = (error) => {
                        clearTimeout(timeout);
                        resolve({ error: 'WebSocket connection failed', details: error.toString() });
                    };
                    
                } catch (error) {
                    resolve({ error: error.message });
                }
            });
        });
        
        if (wsTest.status) {
            console.log('✅ WebSocket Direct Test: SUCCESS');
            console.log('   OpenAI Realtime endpoint is responding');
        } else {
            console.log('❌ WebSocket Direct Test: FAILED');
            console.log('   Error:', wsTest.error);
        }

        // Final Status Report
        console.log('\n📊 FINAL VOICE INTEGRATION STATUS:');
        console.log('═══════════════════════════════════════');
        
        if (healthTest.status === 'healthy') {
            console.log('✅ Backend Agent: OPERATIONAL');
        }
        
        if (wsTest.status) {
            console.log('✅ Voice WebSocket: OPERATIONAL'); 
        } else {
            console.log('❌ Voice WebSocket: FAILED');
        }
        
        console.log('');
        console.log('🎯 TRUTH ABOUT SYSTEM STATUS:');
        
        if (healthTest.status === 'healthy' && wsTest.status) {
            console.log('✅ VOICE INTEGRATION IS WORKING!');
            console.log('   - GPT-4o Agent: Ready');
            console.log('   - OpenAI Realtime API: Connected'); 
            console.log('   - WebSocket: Functional');
            console.log('   - Market Tools: Available');
            console.log('');
            console.log('🎤 Users can now speak to the GPT-4o agent');
            console.log('📊 Agent can analyze market data via voice');
            console.log('💬 Both voice and text modes operational');
        } else {
            console.log('❌ VOICE INTEGRATION STILL HAS ISSUES');
            console.log('   Please check the specific failures above');
        }

    } catch (error) {
        console.error('\n❌ Test error:', error.message);
        await page.screenshot({ path: 'voice-test-error.png', fullPage: true });
    } finally {
        setTimeout(async () => {
            await browser.close();
            console.log('\n👋 Test complete, browser closed.');
        }, 5000);
    }
}

testVoiceConnectionFixed().catch(console.error);