// Test script to verify singleton WebSocket connection behavior
// Run this in the browser console to test

console.log('=== Testing ElevenLabs Connection Singleton ===');

// Function to monitor network requests
const monitorNetworkRequests = () => {
  const originalFetch = window.fetch;
  let signedUrlRequestCount = 0;
  
  window.fetch = function(...args) {
    const url = args[0];
    if (url && url.includes('/elevenlabs/signed-url')) {
      signedUrlRequestCount++;
      console.log(`[Network Monitor] Signed URL request #${signedUrlRequestCount}:`, url);
    }
    return originalFetch.apply(this, args);
  };
  
  console.log('Network monitoring started. Signed URL requests will be logged.');
  
  return () => {
    window.fetch = originalFetch;
    console.log(`Total signed URL requests: ${signedUrlRequestCount}`);
    return signedUrlRequestCount;
  };
};

// Function to monitor WebSocket connections
const monitorWebSocketConnections = () => {
  const originalWebSocket = window.WebSocket;
  let websocketCount = 0;
  const connections = [];
  
  window.WebSocket = function(...args) {
    websocketCount++;
    const ws = new originalWebSocket(...args);
    const connectionInfo = {
      id: websocketCount,
      url: args[0],
      readyState: ws.readyState,
      timestamp: new Date().toISOString()
    };
    connections.push(connectionInfo);
    console.log(`[WebSocket Monitor] New WebSocket #${websocketCount}:`, connectionInfo);
    
    // Monitor state changes
    ws.addEventListener('open', () => {
      console.log(`[WebSocket Monitor] WebSocket #${connectionInfo.id} opened`);
      connectionInfo.readyState = ws.readyState;
    });
    
    ws.addEventListener('close', () => {
      console.log(`[WebSocket Monitor] WebSocket #${connectionInfo.id} closed`);
      connectionInfo.readyState = ws.readyState;
    });
    
    return ws;
  };
  
  console.log('WebSocket monitoring started. All connections will be logged.');
  
  return () => {
    window.WebSocket = originalWebSocket;
    console.log(`Total WebSocket connections: ${websocketCount}`);
    console.log('Connection details:', connections);
    return { count: websocketCount, connections };
  };
};

// Start monitoring
console.log('Starting network and WebSocket monitoring...');
console.log('Please click the "Connect Voice Assistant" button to test.');
console.log('Expected behavior:');
console.log('  - Only 1 signed URL request');
console.log('  - Only 1 WebSocket connection');
console.log('  - Connection should persist across component re-renders');

const stopNetworkMonitor = monitorNetworkRequests();
const stopWebSocketMonitor = monitorWebSocketConnections();

// Instructions for testing
console.log('\n=== Test Instructions ===');
console.log('1. Click "Connect Voice Assistant" button');
console.log('2. Wait for connection to establish');
console.log('3. Navigate between tabs (Charts/Voice)');
console.log('4. Run the following to see results:');
console.log('   stopNetworkMonitor()');
console.log('   stopWebSocketMonitor()');

// Export functions for manual testing
window.testResults = {
  stopNetworkMonitor,
  stopWebSocketMonitor,
  checkSingleton: () => {
    const networkCount = stopNetworkMonitor();
    const wsData = stopWebSocketMonitor();
    
    console.log('\n=== Test Results ===');
    console.log(`Signed URL requests: ${networkCount} (expected: 1)`);
    console.log(`WebSocket connections: ${wsData.count} (expected: 1)`);
    
    if (networkCount === 1 && wsData.count === 1) {
      console.log('✅ PASSED: Singleton pattern is working correctly!');
    } else {
      console.log('❌ FAILED: Multiple connections detected');
      console.log('This indicates the singleton pattern is not working properly');
    }
    
    return { networkCount, websocketCount: wsData.count, connections: wsData.connections };
  }
};

console.log('\nTo check results at any time, run: window.testResults.checkSingleton()');