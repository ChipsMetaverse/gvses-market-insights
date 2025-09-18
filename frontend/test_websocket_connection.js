const { test, expect } = require('@playwright/test');

test('OpenAI WebSocket Connection Test', async ({ page }) => {
  console.log('Testing OpenAI WebSocket connection...');
  
  // Set up console and network monitoring
  const consoleMessages = [];
  const networkRequests = [];
  const websocketConnections = [];
  
  page.on('console', msg => {
    console.log(`Console: ${msg.text()}`);
    consoleMessages.push(msg.text());
  });
  
  page.on('request', request => {
    console.log(`Request: ${request.method()} ${request.url()}`);
    networkRequests.push(`${request.method()} ${request.url()}`);
  });
  
  page.on('websocket', ws => {
    console.log(`WebSocket connection: ${ws.url()}`);
    websocketConnections.push(ws.url());
    
    ws.on('framesent', event => console.log(`WS Sent: ${JSON.stringify(event.payload)}`));
    ws.on('framereceived', event => console.log(`WS Received: ${JSON.stringify(event.payload)}`));
  });

  // Navigate to the app
  await page.goto('http://localhost:5174/');
  
  // Wait for the app to load
  await page.waitForTimeout(3000);
  
  try {
    // Switch to voice tab
    const voiceTab = page.locator('[data-testid="voice-tab"]');
    if (await voiceTab.count() > 0) {
      await voiceTab.click();
      console.log('✅ Switched to voice tab');
      
      // Switch to OpenAI provider
      const openAIProvider = page.locator('[data-testid="provider-openai"]');
      if (await openAIProvider.count() > 0) {
        await openAIProvider.click();
        console.log('✅ Switched to OpenAI provider');
        
        // Try to connect
        const connectButton = page.locator('[data-testid="connect-button"]');
        if (await connectButton.count() > 0) {
          console.log('Found connect button, attempting to connect...');
          await connectButton.click();
          
          // Wait for connection attempt
          await page.waitForTimeout(5000);
          
          // Log results
          console.log('\n=== RESULTS ===');
          console.log('WebSocket Connections:', websocketConnections);
          console.log('Network Requests:', networkRequests.filter(req => req.includes('realtime') || req.includes('websocket')));
          console.log('Console Messages:', consoleMessages.filter(msg => msg.includes('WebSocket') || msg.includes('OpenAI') || msg.includes('connect')));
          
          // Check if any WebSocket connections to realtime-relay were made
          const realtimeConnections = websocketConnections.filter(url => url.includes('realtime-relay'));
          if (realtimeConnections.length > 0) {
            console.log('✅ Found realtime-relay WebSocket connections:', realtimeConnections);
          } else {
            console.log('❌ No realtime-relay WebSocket connections found');
            console.log('All WebSocket connections:', websocketConnections);
          }
          
        } else {
          console.log('❌ Connect button not found');
        }
      } else {
        console.log('❌ OpenAI provider button not found');
      }
    } else {
      console.log('❌ Voice tab not found');
    }
  } catch (error) {
    console.error('Test error:', error);
  }
  
  // Log final state
  console.log('\n=== FINAL STATE ===');
  console.log('Total console messages:', consoleMessages.length);
  console.log('Total network requests:', networkRequests.length);
  console.log('Total WebSocket connections:', websocketConnections.length);
});