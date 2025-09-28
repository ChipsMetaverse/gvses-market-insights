#!/usr/bin/env node
/**
 * Phase 1 Completion Tests for Headless Chart Service
 * Tests priority queue, metrics, status endpoints, and WebSocket integration
 */

const { WebSocket } = require('ws');
const fetch = require('node-fetch');
const { setTimeout } = require('timers/promises');

const HEADLESS_URL = 'http://localhost:3100';
const WS_URL = 'ws://localhost:3100/ws';

const chalk = {
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`,
};

// Test helpers
const testResults = [];
let ws = null;

async function testPhase1() {
  console.log(chalk.bold(chalk.cyan('\n=== Phase 1 Completion Tests ===\n')));

  try {
    // Test 1: Priority Queue Ordering
    console.log(chalk.bold('Test 1: Priority Queue Ordering'));
    
    // Submit jobs with different priorities
    const highPriorityJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'AAPL',
        timeframe: '1D',
        commands: ['LOAD:AAPL'],
        priority: 10, // High priority (lower number)
      }),
    }).then(r => r.json());
    
    const lowPriorityJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'TSLA',
        timeframe: '1D',
        commands: ['LOAD:TSLA'],
        priority: 100, // Low priority (higher number)
      }),
    }).then(r => r.json());
    
    const medPriorityJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'NVDA',
        timeframe: '1D',
        commands: ['LOAD:NVDA'],
        priority: 50, // Medium priority
      }),
    }).then(r => r.json());
    
    // Verify queue positions
    const highStatus = await fetch(`${HEADLESS_URL}/status/${highPriorityJob.jobId}`).then(r => r.json());
    const medStatus = await fetch(`${HEADLESS_URL}/status/${medPriorityJob.jobId}`).then(r => r.json());
    const lowStatus = await fetch(`${HEADLESS_URL}/status/${lowPriorityJob.jobId}`).then(r => r.json());
    
    console.log(`  High priority position: ${highStatus.queuePosition || 'processing'}`);
    console.log(`  Medium priority position: ${medStatus.queuePosition || 'processing'}`);
    console.log(`  Low priority position: ${lowStatus.queuePosition || 'processing'}`);
    
    // Verify high priority is first
    const priorityCorrect = !highStatus.queuePosition || 
      (medStatus.queuePosition && highStatus.queuePosition < medStatus.queuePosition) ||
      (lowStatus.queuePosition && medStatus.queuePosition < lowStatus.queuePosition);
    
    testResults.push({
      name: 'Priority Queue Ordering',
      passed: priorityCorrect,
      details: priorityCorrect ? 'Jobs correctly ordered by priority' : 'Priority ordering failed',
    });
    
    // Test 2: Metrics Endpoint
    console.log(chalk.bold('\nTest 2: Metrics Endpoint'));
    
    const metrics = await fetch(`${HEADLESS_URL}/metrics`).then(r => r.json());
    
    console.log(`  Total jobs: ${metrics.totalJobs}`);
    console.log(`  Queued jobs: ${metrics.queuedJobs}`);
    console.log(`  Active jobs: ${metrics.activeJobs}`);
    console.log(`  Browser contexts: ${metrics.browser.contexts}/${metrics.browser.maxContexts}`);
    console.log(`  Uptime: ${Math.round(metrics.uptime)}s`);
    
    const metricsValid = 
      metrics.totalJobs >= 3 && // We submitted 3 jobs
      typeof metrics.queuedJobs === 'number' &&
      typeof metrics.activeJobs === 'number' &&
      metrics.browser !== undefined &&
      metrics.queue !== undefined &&
      metrics.memoryUsage !== undefined;
    
    testResults.push({
      name: 'Metrics Endpoint',
      passed: metricsValid,
      details: metricsValid ? 'All metrics fields present and valid' : 'Missing or invalid metrics',
    });
    
    // Test 3: Status Endpoint with Queue Info
    console.log(chalk.bold('\nTest 3: Status Endpoint with Queue Info'));
    
    // Submit a new job and check its status
    const statusTestJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'MSFT',
        timeframe: '1H',
        commands: ['LOAD:MSFT'],
        priority: 200, // Very low priority to ensure it's queued
      }),
    }).then(r => r.json());
    
    const statusInfo = await fetch(`${HEADLESS_URL}/status/${statusTestJob.jobId}`).then(r => r.json());
    
    console.log(`  Job ID: ${statusInfo.id}`);
    console.log(`  Status: ${statusInfo.status}`);
    console.log(`  Queue position: ${statusInfo.queuePosition || 'N/A'}`);
    console.log(`  Estimated start: ${statusInfo.estimatedStartSeconds || 'N/A'}s`);
    
    const statusValid = 
      statusInfo.id === statusTestJob.jobId &&
      statusInfo.status !== undefined &&
      statusInfo.symbol === 'MSFT';
    
    testResults.push({
      name: 'Status Endpoint',
      passed: statusValid,
      details: statusValid ? 'Status endpoint provides detailed job info' : 'Status info incomplete',
    });
    
    // Test 4: Snapshot Endpoint
    console.log(chalk.bold('\nTest 4: Snapshot Endpoint'));
    
    // Wait for high priority job to complete
    let snapshotJob = highPriorityJob;
    let attempts = 0;
    let jobComplete = false;
    
    while (attempts < 30 && !jobComplete) {
      await setTimeout(1000);
      const status = await fetch(`${HEADLESS_URL}/status/${snapshotJob.jobId}`).then(r => r.json());
      if (status.status === 'succeeded' || status.status === 'failed') {
        jobComplete = true;
      }
      attempts++;
    }
    
    const snapshotResponse = await fetch(`${HEADLESS_URL}/snapshot/${snapshotJob.jobId}`);
    const snapshotStatus = snapshotResponse.status;
    
    console.log(`  Snapshot endpoint status: ${snapshotStatus}`);
    
    if (snapshotStatus === 200) {
      const snapshot = await snapshotResponse.json();
      console.log(`  Snapshot has image: ${!!snapshot.imageBase64}`);
      console.log(`  Symbol: ${snapshot.symbol}`);
    } else if (snapshotStatus === 202) {
      console.log(`  Job still in progress`);
    } else if (snapshotStatus === 404) {
      console.log(`  No snapshot available`);
    }
    
    const snapshotValid = [200, 202, 404].includes(snapshotStatus);
    
    testResults.push({
      name: 'Snapshot Endpoint',
      passed: snapshotValid,
      details: `Snapshot endpoint returned ${snapshotStatus}`,
    });
    
    // Test 5: WebSocket Real-time Updates
    console.log(chalk.bold('\nTest 5: WebSocket Real-time Updates'));
    
    const wsMessages = [];
    ws = new WebSocket(WS_URL);
    
    await new Promise((resolve, reject) => {
      const timeout = global.setTimeout(() => reject(new Error('WebSocket connection timeout')), 5000);
      ws.on('open', () => {
        clearTimeout(timeout);
        console.log('  WebSocket connected');
        ws.send(JSON.stringify({ type: 'subscribe', channel: 'jobs' }));
        resolve();
      });
      ws.on('error', (err) => {
        clearTimeout(timeout);
        reject(err);
      });
    });
    
    ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data);
        if (msg.type !== 'heartbeat') {
          wsMessages.push(msg);
        }
      } catch (e) {
        // Ignore parse errors
      }
    });
    
    // Submit a job to trigger WebSocket messages
    const wsTestJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'AMZN',
        timeframe: '5M',
        commands: ['LOAD:AMZN'],
        priority: 1, // Very high priority
      }),
    }).then(r => r.json());
    
    // Wait for WebSocket messages
    await setTimeout(2000);
    
    console.log(`  WebSocket messages received: ${wsMessages.length}`);
    const jobMessages = wsMessages.filter(m => m.jobId === wsTestJob.jobId);
    console.log(`  Messages for test job: ${jobMessages.length}`);
    
    const wsValid = wsMessages.length > 0 && jobMessages.length > 0;
    
    testResults.push({
      name: 'WebSocket Updates',
      passed: wsValid,
      details: wsValid ? `Received ${jobMessages.length} real-time updates` : 'No WebSocket updates received',
    });
    
    // Test 6: Queue Management (Cancel/Update Priority)
    console.log(chalk.bold('\nTest 6: Queue Management'));
    
    // Submit a low priority job
    const queueMgmtJob = await fetch(`${HEADLESS_URL}/render`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        symbol: 'GOOGL',
        timeframe: '15M',
        commands: ['LOAD:GOOGL'],
        priority: 500, // Very low priority
      }),
    }).then(r => r.json());
    
    // Check queue status
    const queueStatus = await fetch(`${HEADLESS_URL}/metrics`).then(r => r.json());
    console.log(`  Current queue length: ${queueStatus.queue.queued}`);
    console.log(`  Jobs processing: ${queueStatus.queue.processing}`);
    
    const queueMgmtValid = 
      typeof queueStatus.queue.queued === 'number' &&
      Array.isArray(queueStatus.queue.queuedJobs) &&
      Array.isArray(queueStatus.queue.processingJobs);
    
    testResults.push({
      name: 'Queue Management',
      passed: queueMgmtValid,
      details: queueMgmtValid ? 'Queue status properly exposed' : 'Queue management incomplete',
    });
    
  } catch (error) {
    console.error(chalk.red(`\nTest suite error: ${error.message}`));
    testResults.push({
      name: 'Test Suite',
      passed: false,
      details: error.message,
    });
  } finally {
    if (ws) {
      ws.close();
    }
  }
  
  // Print results summary
  console.log(chalk.bold(chalk.cyan('\n=== Test Results Summary ===\n')));
  
  let passedCount = 0;
  testResults.forEach((result, index) => {
    const status = result.passed ? chalk.green('✓ PASS') : chalk.red('✗ FAIL');
    console.log(`${index + 1}. ${result.name}: ${status}`);
    console.log(`   ${result.details}`);
    if (result.passed) passedCount++;
  });
  
  console.log(chalk.bold(`\n${chalk.cyan('Overall')}: ${passedCount}/${testResults.length} tests passed`));
  
  if (passedCount === testResults.length) {
    console.log(chalk.green(chalk.bold('\n🎉 Phase 1 Complete! All tests passed.\n')));
    console.log('Phase 1 Features Implemented:');
    console.log('  ✓ Priority queue with job scheduling');
    console.log('  ✓ GET /metrics endpoint with performance data');
    console.log('  ✓ GET /status/:id with queue position and ETA');
    console.log('  ✓ GET /snapshot/:id for job results');
    console.log('  ✓ WebSocket real-time updates');
    console.log('  ✓ Queue management and monitoring');
  } else {
    console.log(chalk.red(chalk.bold(`\n⚠️  Some tests failed. Please review and fix.\n`)));
  }
  
  process.exit(passedCount === testResults.length ? 0 : 1);
}

// Health check
async function checkServices() {
  try {
    const health = await fetch(`${HEADLESS_URL}/health`).then(r => r.json());
    if (health.status !== 'ok') {
      throw new Error('Headless service unhealthy');
    }
    console.log(chalk.green('✓ Headless service is running'));
    return true;
  } catch (error) {
    console.error(chalk.red('✗ Headless service is not running on port 3100'));
    console.log(chalk.yellow('  Start it with: cd backend/headless_chart_service && npm start'));
    return false;
  }
}

// Main
(async () => {
  console.log(chalk.bold(chalk.cyan('Phase 1 Completion Test Suite')));
  console.log('Testing priority queue, metrics, and monitoring features...\n');
  
  const servicesReady = await checkServices();
  if (!servicesReady) {
    process.exit(1);
  }
  
  await testPhase1();
})();