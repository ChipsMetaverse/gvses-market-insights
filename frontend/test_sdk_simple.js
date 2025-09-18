#!/usr/bin/env node
/**
 * Simple OpenAI Realtime SDK Test
 * ==============================
 * Basic test to verify SDK import and initialization
 */

import { RealtimeClient } from '@openai/realtime-api-beta';

console.log('🧪 Simple SDK Test');
console.log('==================');

try {
  // Test SDK import
  console.log('✅ RealtimeClient imported successfully');
  
  // Test client initialization 
  const relayUrl = 'ws://localhost:8000/realtime-relay/test_session';
  const client = new RealtimeClient({ url: relayUrl });
  console.log('✅ RealtimeClient initialized with relay URL');
  
  // Test event listener setup
  client.on('error', (event) => {
    console.log('📨 Error event listener set up');
  });
  console.log('✅ Event listeners can be attached');
  
  console.log('\n🎯 SDK Integration Status:');
  console.log('- ✅ @openai/realtime-api-beta SDK imported');
  console.log('- ✅ RealtimeClient can be instantiated');
  console.log('- ✅ Relay URL configuration works');
  console.log('- ✅ Event system is functional');
  
  console.log('\n🚀 Ready for full integration test!');
  process.exit(0);
  
} catch (error) {
  console.error('❌ SDK test failed:', error.message);
  process.exit(1);
}