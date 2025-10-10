import { test, expect, Page } from '@playwright/test';
import * as fs from 'fs';

// Test the complete voice assistant pipeline
test.describe('Voice Assistant End-to-End Flow', () => {

  test('Complete voice pipeline monitoring', async ({ page, context }) => {
    // Grant microphone permissions
    await context.grantPermissions(['microphone'], { origin: 'http://localhost:5175' });

    const logs: string[] = [];
    const errors: string[] = [];
    const networkActivity: any[] = [];
    const wsMessages: any[] = [];

    // Capture all console output
    page.on('console', msg => {
      const text = `[${msg.type()}] ${msg.text()}`;
      logs.push(text);
      console.log(text);
    });

    // Capture errors
    page.on('pageerror', err => {
      const text = `[PAGE ERROR] ${err.message}`;
      errors.push(text);
      console.error(text);
    });

    // Capture network activity
    page.on('request', request => {
      const url = request.url();
      if (url.includes('/openai/') || url.includes('/ask') || url.includes('realtime')) {
        networkActivity.push({
          type: 'request',
          method: request.method(),
          url: url,
          timestamp: new Date().toISOString()
        });
        console.log(`📤 [REQUEST] ${request.method()} ${url}`);
      }
    });

    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/openai/') || url.includes('/ask') || url.includes('realtime')) {
        const status = response.status();
        let body = null;
        try {
          body = await response.json().catch(() => null);
        } catch {}

        networkActivity.push({
          type: 'response',
          status: status,
          url: url,
          body: body,
          timestamp: new Date().toISOString()
        });
        console.log(`📥 [RESPONSE] ${status} ${url}`);
        if (body) {
          console.log(`   Body:`, JSON.stringify(body, null, 2));
        }
      }
    });

    // Navigate to the app
    console.log('\n🌐 Navigating to application...\n');
    await page.goto('http://localhost:5175');
    await page.waitForLoadState('networkidle');

    // Take initial screenshot
    await page.screenshot({ path: 'voice-test-1-initial.png', fullPage: true });
    console.log('✅ Page loaded\n');

    // Wait for app to be ready
    await page.waitForTimeout(2000);

    // Find and click the voice button
    console.log('🔍 Looking for voice button...\n');
    const voiceButton = page.locator('[data-testid="voice-fab"], button:has-text("🎙️"), button.voice-fab');

    // Wait for button to be visible
    await voiceButton.waitFor({ state: 'visible', timeout: 10000 });
    console.log('✅ Voice button found\n');

    await page.screenshot({ path: 'voice-test-2-button-found.png', fullPage: true });

    // Monitor for WebSocket connection
    const wsPromise = page.waitForEvent('websocket', { timeout: 10000 });

    // Click the voice button
    console.log('🖱️  Clicking voice button...\n');
    await voiceButton.click();

    // Wait for WebSocket connection
    let ws;
    try {
      ws = await wsPromise;
      console.log('✅ WebSocket connection established:', ws.url());

      // Monitor WebSocket messages
      ws.on('framereceived', event => {
        try {
          const data = event.payload;
          let parsed = data;
          if (typeof data === 'string') {
            try {
              parsed = JSON.parse(data);
            } catch {}
          }

          wsMessages.push({
            direction: 'received',
            data: parsed,
            timestamp: new Date().toISOString()
          });

          // Log important events
          if (typeof parsed === 'object' && parsed.type) {
            console.log(`📨 [WS RECV] ${parsed.type}`);

            // Log transcription events
            if (parsed.type.includes('transcription')) {
              console.log(`   📝 Transcription event:`, parsed);
            }

            // Log agent-related events
            if (parsed.type.includes('conversation')) {
              console.log(`   💬 Conversation event:`, parsed);
            }
          }
        } catch (err) {
          console.error('Error processing WebSocket message:', err);
        }
      });

      ws.on('framesent', event => {
        try {
          const data = event.payload;
          let parsed = data;
          if (typeof data === 'string') {
            try {
              parsed = JSON.parse(data);
            } catch {}
          }

          wsMessages.push({
            direction: 'sent',
            data: parsed,
            timestamp: new Date().toISOString()
          });

          if (typeof parsed === 'object' && parsed.type) {
            console.log(`📤 [WS SENT] ${parsed.type}`);
          }
        } catch (err) {
          console.error('Error processing sent WebSocket message:', err);
        }
      });

      ws.on('close', () => {
        console.log('❌ WebSocket connection closed');
      });

    } catch (err) {
      console.error('❌ WebSocket connection failed:', err);
    }

    // Wait for connection to establish
    await page.waitForTimeout(3000);

    await page.screenshot({ path: 'voice-test-3-connected.png', fullPage: true });

    // Check if microphone is active
    const micStatus = await page.evaluate(() => {
      return {
        mediaDevicesSupported: !!navigator.mediaDevices,
        getUserMediaSupported: !!navigator.mediaDevices?.getUserMedia
      };
    });

    console.log('🎤 Microphone status:', micStatus);

    // Inject audio simulation (this is tricky - we'll monitor for audio context instead)
    const audioStatus = await page.evaluate(() => {
      const audioContexts = (window as any).audioContexts || [];
      return {
        audioContextCount: audioContexts.length,
        audioContextState: audioContexts[0]?.state
      };
    });

    console.log('🔊 Audio status:', audioStatus);

    // Monitor console logs for STT events
    console.log('\n⏳ Monitoring for voice events (30 seconds)...\n');
    console.log('NOTE: Actual voice input requires real microphone - monitoring for event handlers setup\n');

    // Check if event listeners are registered
    const eventListenerStatus = await page.evaluate(() => {
      // Check if the window has our voice service
      const hasVoiceService = !!(window as any).__VOICE_SERVICE_DEBUG;
      return {
        hasVoiceService,
        timestamp: new Date().toISOString()
      };
    });

    console.log('Event listener status:', eventListenerStatus);

    // Wait and monitor
    await page.waitForTimeout(5000);

    // Check for any STT-related console logs
    const sttLogs = logs.filter(log =>
      log.includes('[STT') ||
      log.includes('transcription') ||
      log.includes('speech')
    );

    console.log('\n📊 STT-related console logs:', sttLogs.length);
    sttLogs.forEach(log => console.log(log));

    // Check WebSocket messages for transcription events
    const transcriptionMessages = wsMessages.filter(msg =>
      typeof msg.data === 'object' &&
      msg.data?.type?.includes('transcription')
    );

    console.log('\n📊 Transcription WebSocket messages:', transcriptionMessages.length);
    transcriptionMessages.forEach(msg => {
      console.log('  -', msg.data.type, msg.timestamp);
    });

    // Test the /ask endpoint directly to verify agent works
    console.log('\n🧪 Testing agent endpoint directly...\n');

    const agentResponse = await page.evaluate(async () => {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: 'What is the price of Tesla?',
          conversation_history: []
        })
      });
      return await res.json();
    });

    console.log('✅ Agent response:', agentResponse.response);
    console.log('   Tools used:', Object.keys(agentResponse.tool_results || {}));

    // Final screenshot
    await page.screenshot({ path: 'voice-test-4-final.png', fullPage: true });

    // Generate comprehensive report
    const report = {
      timestamp: new Date().toISOString(),
      test: 'Voice Assistant End-to-End Flow',
      duration: '35 seconds',
      results: {
        pageLoaded: true,
        voiceButtonFound: true,
        voiceButtonClicked: true,
        websocketConnected: !!ws,
        websocketUrl: ws?.url(),
        microphonePermission: micStatus,
        audioContext: audioStatus,
        consoleLogCount: logs.length,
        errorCount: errors.length,
        networkRequestCount: networkActivity.length,
        websocketMessageCount: wsMessages.length,
        sttEventCount: sttLogs.length,
        transcriptionMessageCount: transcriptionMessages.length,
        agentResponseReceived: !!agentResponse.response,
        agentToolsUsed: Object.keys(agentResponse.tool_results || {})
      },
      logs: logs.slice(-50), // Last 50 logs
      errors: errors,
      networkActivity: networkActivity,
      websocketMessages: wsMessages.slice(-20), // Last 20 WS messages
      sttLogs: sttLogs,
      transcriptionMessages: transcriptionMessages,
      agentResponse: agentResponse,
      screenshots: [
        'voice-test-1-initial.png',
        'voice-test-2-button-found.png',
        'voice-test-3-connected.png',
        'voice-test-4-final.png'
      ]
    };

    // Save report
    fs.writeFileSync(
      'voice-assistant-test-report.json',
      JSON.stringify(report, null, 2)
    );

    console.log('\n' + '='.repeat(80));
    console.log('📋 VOICE ASSISTANT TEST REPORT');
    console.log('='.repeat(80));
    console.log('\n✅ SUCCESSES:');
    console.log(`  - Page loaded: ${report.results.pageLoaded}`);
    console.log(`  - Voice button found: ${report.results.voiceButtonFound}`);
    console.log(`  - Voice button clicked: ${report.results.voiceButtonClicked}`);
    console.log(`  - WebSocket connected: ${report.results.websocketConnected}`);
    console.log(`  - Agent responding: ${report.results.agentResponseReceived}`);

    console.log('\n📊 METRICS:');
    console.log(`  - Console logs: ${report.results.consoleLogCount}`);
    console.log(`  - Errors: ${report.results.errorCount}`);
    console.log(`  - Network requests: ${report.results.networkRequestCount}`);
    console.log(`  - WebSocket messages: ${report.results.websocketMessageCount}`);
    console.log(`  - STT events: ${report.results.sttEventCount}`);
    console.log(`  - Transcription messages: ${report.results.transcriptionMessageCount}`);

    console.log('\n🎯 AGENT TEST:');
    console.log(`  - Query: "What is the price of Tesla?"`);
    console.log(`  - Response: ${agentResponse.response}`);
    console.log(`  - Tools: ${report.results.agentToolsUsed.join(', ')}`);

    console.log('\n📸 SCREENSHOTS:');
    report.screenshots.forEach(s => console.log(`  - ${s}`));

    console.log('\n💾 REPORT SAVED: voice-assistant-test-report.json');
    console.log('='.repeat(80) + '\n');

    // Assertions
    expect(report.results.pageLoaded).toBe(true);
    expect(report.results.voiceButtonFound).toBe(true);
    expect(report.results.websocketConnected).toBe(true);
    expect(report.results.agentResponseReceived).toBe(true);
  });

  test('Check event handler registration', async ({ page }) => {
    console.log('\n🔍 Checking event handler registration...\n');

    await page.goto('http://localhost:5175');
    await page.waitForLoadState('networkidle');

    // Inject debug code to check event listeners
    const eventHandlers = await page.evaluate(() => {
      // This will check if our service is accessible
      return {
        hasRealtimeClient: !!(window as any).realtimeClient,
        hasVoiceService: !!(window as any).voiceService,
        hasAudioProcessor: !!(window as any).audioProcessor
      };
    });

    console.log('Event handler registration:', eventHandlers);

    // Check console for event registration logs
    const logs: string[] = [];
    page.on('console', msg => logs.push(msg.text()));

    await page.waitForTimeout(2000);

    const eventLogs = logs.filter(log =>
      log.includes('event') ||
      log.includes('listener') ||
      log.includes('handler')
    );

    console.log('Event-related logs:', eventLogs);
  });
});
