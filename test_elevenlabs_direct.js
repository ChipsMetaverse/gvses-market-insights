#!/usr/bin/env node

/**
 * Minimal test to connect directly to ElevenLabs WebSocket
 * This isolates the WebSocket connection from React and other complexities
 */

const WebSocket = require('ws');
const fetch = require('node-fetch');

async function getSignedUrl() {
  console.log('📍 Fetching signed URL from backend...');
  const response = await fetch('http://localhost:8000/elevenlabs/signed-url');
  const data = await response.json();
  console.log('✅ Got signed URL');
  return data.signed_url;
}

async function testDirectConnection() {
  try {
    // Get signed URL
    const signedUrl = await getSignedUrl();
    console.log(`📡 Connecting to: ${signedUrl.substring(0, 80)}...`);
    
    // Create WebSocket connection
    const ws = new WebSocket(signedUrl);
    let pingCount = 0;
    let connectionTime = null;
    
    // Set up event handlers
    ws.on('open', () => {
      connectionTime = new Date();
      console.log(`✅ WebSocket connected at ${connectionTime.toISOString()}`);
      
      // Send initialization message
      const initMessage = {
        type: 'conversation_initiation_client_data'
      };
      console.log('📤 Sending init message:', JSON.stringify(initMessage));
      ws.send(JSON.stringify(initMessage));
    });
    
    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        console.log(`📨 Received: ${message.type}`);
        
        // Handle different message types
        switch (message.type) {
          case 'conversation_initiation_metadata':
            console.log('  ✅ Conversation initialized');
            console.log('  Agent ID:', message.conversation_initiation_metadata_event?.agent_id);
            break;
            
          case 'ping':
            pingCount++;
            const eventId = message.ping_event?.event_id;
            const pingMs = message.ping_event?.ping_ms || 0;
            console.log(`  🏓 Ping #${pingCount} (delay: ${pingMs}ms)`);
            
            // Respond to ping
            setTimeout(() => {
              if (ws.readyState === WebSocket.OPEN) {
                const pongMessage = {
                  type: 'pong',
                  event_id: eventId
                };
                console.log(`  📤 Sending pong for event ${eventId}`);
                ws.send(JSON.stringify(pongMessage));
              }
            }, pingMs);
            break;
            
          case 'interruption':
            console.log('  ⚠️ Interruption:', message.interruption_event?.reason);
            break;
            
          case 'error':
            console.log('  ❌ Error:', message);
            break;
            
          default:
            console.log(`  ℹ️ Other message type: ${message.type}`);
        }
      } catch (e) {
        console.log('  ⚠️ Non-JSON message:', data.toString().substring(0, 100));
      }
    });
    
    ws.on('error', (error) => {
      console.error('❌ WebSocket error:', error.message);
    });
    
    ws.on('close', (code, reason) => {
      const now = new Date();
      const duration = connectionTime ? (now - connectionTime) / 1000 : 0;
      console.log(`\n🔴 WebSocket closed`);
      console.log(`  Code: ${code}`);
      console.log(`  Reason: ${reason || 'No reason provided'}`);
      console.log(`  Duration: ${duration.toFixed(1)} seconds`);
      console.log(`  Pings received: ${pingCount}`);
      
      // Analyze disconnection
      if (code === 1000) {
        console.log('  ℹ️ Normal closure');
      } else if (code === 1001) {
        console.log('  ℹ️ Endpoint going away');
      } else if (code === 1006) {
        console.log('  ⚠️ Abnormal closure (no close frame)');
      } else if (code === 1009) {
        console.log('  ⚠️ Message too big');
      } else if (code === 1011) {
        console.log('  ❌ Server error');
      } else if (code >= 4000) {
        console.log('  ⚠️ Custom/Application error code');
      }
    });
    
    // Keep connection alive for testing
    console.log('\n⏳ Keeping connection open for 30 seconds...');
    console.log('Press Ctrl+C to stop\n');
    
    // Send a test message after 5 seconds
    setTimeout(() => {
      if (ws.readyState === WebSocket.OPEN) {
        console.log('\n📤 Sending test text message...');
        const textMessage = {
          type: 'user_message',
          text: 'Hello, this is a test message'
        };
        ws.send(JSON.stringify(textMessage));
      }
    }, 5000);
    
    // Close after 30 seconds
    setTimeout(() => {
      if (ws.readyState === WebSocket.OPEN) {
        console.log('\n📍 Closing connection after 30 seconds...');
        ws.close(1000, 'Test complete');
      }
    }, 30000);
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
console.log('🧪 ElevenLabs Direct WebSocket Connection Test\n');
testDirectConnection();