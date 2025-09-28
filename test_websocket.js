#!/usr/bin/env node

/**
 * WebSocket Test for Headless Chart Service
 * Tests real-time job updates via WebSocket connection
 */

const WebSocket = require('ws');
const fetch = require('node-fetch');

const API_URL = 'http://localhost:3100';
const WS_URL = 'ws://localhost:3100/ws';

async function testWebSocket() {
  console.log('\n=== WebSocket Real-time Updates Test ===\n');
  
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(WS_URL);
    const events = [];
    let jobId = null;
    
    ws.on('open', async () => {
      console.log('✅ WebSocket connected');
      
      ws.on('message', (data) => {
        const message = JSON.parse(data.toString());
        console.log(`📨 Received: ${message.type}`, message.eventType || '');
        events.push(message);
        
        if (message.type === 'connected') {
          // Create a test job after connection
          createTestJob();
        } else if (message.type === 'job_update' && message.job) {
          console.log(`   Job ${message.job.id.substring(0, 8)}: ${message.job.status} (${message.eventType})`);
          
          if (message.job.status === 'succeeded' || message.job.status === 'failed') {
            // Job completed, test is done
            setTimeout(() => {
              ws.close();
            }, 1000);
          }
        }
      });
      
      async function createTestJob() {
        console.log('\n📝 Creating test render job...');
        
        const response = await fetch(`${API_URL}/render`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            symbol: 'TEST',
            timeframe: '1M',
            commands: ['LOAD:TEST', 'TIMEFRAME:1M', 'INDICATOR:MA20'],
            metadata: { test: 'websocket' }
          })
        });
        
        const result = await response.json();
        jobId = result.jobId;
        console.log(`✅ Job created: ${jobId}`);
        
        // Subscribe to this job
        ws.send(JSON.stringify({
          type: 'subscribe',
          jobId: jobId
        }));
      }
    });
    
    ws.on('close', () => {
      console.log('\n📊 WebSocket Test Results:');
      console.log(`   Total events received: ${events.length}`);
      
      const jobUpdates = events.filter(e => e.type === 'job_update');
      console.log(`   Job updates: ${jobUpdates.length}`);
      
      const eventTypes = jobUpdates.map(e => e.eventType);
      console.log(`   Event types: ${[...new Set(eventTypes)].join(', ')}`);
      
      if (eventTypes.includes('created') && 
          eventTypes.includes('updated') && 
          (eventTypes.includes('completed') || eventTypes.includes('failed'))) {
        console.log('\n✅ WebSocket real-time updates working!');
        resolve(true);
      } else {
        console.log('\n⚠️ Some events may be missing');
        resolve(false);
      }
    });
    
    ws.on('error', (error) => {
      console.error('❌ WebSocket error:', error.message);
      reject(error);
    });
    
    // Timeout after 30 seconds
    setTimeout(() => {
      console.log('\n⏱️ Test timeout reached');
      ws.close();
    }, 30000);
  });
}

async function testWebSocketStats() {
  console.log('\n=== WebSocket Stats Test ===\n');
  
  try {
    const response = await fetch(`${API_URL}/ws/stats`);
    const stats = await response.json();
    
    console.log('📊 WebSocket Statistics:');
    console.log(`   Connected clients: ${stats.connectedClients}`);
    console.log(`   Total subscriptions: ${stats.totalSubscriptions}`);
    console.log(`   Active jobs: ${stats.activeJobs}`);
    
    return true;
  } catch (error) {
    console.error('❌ Stats error:', error.message);
    return false;
  }
}

async function runTests() {
  try {
    // Test stats endpoint
    await testWebSocketStats();
    
    // Test WebSocket real-time updates
    await testWebSocket();
    
    console.log('\n🎉 All WebSocket tests completed!\n');
  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    process.exit(1);
  }
}

runTests();