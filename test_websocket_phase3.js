#!/usr/bin/env node

const WebSocket = require('ws');

console.log('Testing WebSocket Pattern Overlay Broadcasting...');

// Test WebSocket connection to headless chart service
const ws = new WebSocket('ws://localhost:3100/ws');

ws.on('open', function open() {
  console.log('✅ WebSocket connected to headless chart service');
  
  // Test pattern overlay message
  const testPatternOverlay = {
    type: 'pattern_overlay',
    symbol: 'AAPL',
    timeframe: '4H',
    pattern: {
      id: 'test-pattern-123',
      type: 'resistance_break',
      confidence: 0.85,
      coordinates: [
        { time: Date.now() - 3600000, price: 185.50 },
        { time: Date.now(), price: 187.25 }
      ]
    }
  };
  
  console.log('📤 Sending test pattern overlay...');
  ws.send(JSON.stringify(testPatternOverlay));
  
  // Close after test
  setTimeout(() => {
    console.log('🔚 Closing WebSocket connection');
    ws.close();
  }, 2000);
});

ws.on('message', function message(data) {
  console.log('📥 Received:', data.toString());
});

ws.on('error', function error(err) {
  console.error('❌ WebSocket error:', err.message);
});

ws.on('close', function close() {
  console.log('🔌 WebSocket connection closed');
});

// Handle script termination
process.on('SIGINT', () => {
  console.log('\n🛑 Terminating WebSocket test...');
  ws.close();
  process.exit(0);
});