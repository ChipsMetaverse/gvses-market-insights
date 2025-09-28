#!/usr/bin/env node

/**
 * Test script for Phase 3: Frontend Integration
 * Tests chart snapshot fetching and pattern detection
 */

const fetch = require('node-fetch');

const API_URL = 'http://localhost:8000';
const TEST_SYMBOL = 'AAPL';
const TEST_TIMEFRAME = '1D';

async function testSnapshotAPI() {
  console.log('Testing Chart Snapshot API...\n');
  
  // Test 1: Fetch snapshot without image
  console.log('1. Testing snapshot fetch without image:');
  try {
    const response = await fetch(`${API_URL}/api/agent/chart-snapshot/${TEST_SYMBOL}?timeframe=${TEST_TIMEFRAME}`);
    if (response.status === 404) {
      console.log('   ✅ No snapshot available (expected for initial test)');
    } else if (response.ok) {
      const snapshot = await response.json();
      console.log('   ✅ Snapshot retrieved successfully');
      console.log(`   - Symbol: ${snapshot.symbol}`);
      console.log(`   - Timeframe: ${snapshot.timeframe}`);
      console.log(`   - Captured at: ${snapshot.captured_at}`);
      if (snapshot.analysis?.patterns) {
        console.log(`   - Patterns detected: ${snapshot.analysis.patterns.length}`);
        snapshot.analysis.patterns.forEach(p => {
          console.log(`     • ${p.type} (confidence: ${p.confidence})`);
        });
      }
      if (snapshot.analysis?.summary) {
        console.log(`   - Summary: ${snapshot.analysis.summary.substring(0, 100)}...`);
      }
    } else {
      console.log(`   ❌ Unexpected response: ${response.status}`);
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
  }
  
  // Test 2: Test with different symbols
  console.log('\n2. Testing multiple symbols:');
  const symbols = ['TSLA', 'NVDA', 'SPY'];
  for (const symbol of symbols) {
    try {
      const response = await fetch(`${API_URL}/api/agent/chart-snapshot/${symbol}`);
      if (response.status === 404) {
        console.log(`   ${symbol}: No snapshot available`);
      } else if (response.ok) {
        const snapshot = await response.json();
        console.log(`   ${symbol}: ✅ Snapshot found (${snapshot.captured_at})`);
      }
    } catch (error) {
      console.log(`   ${symbol}: ❌ Error - ${error.message}`);
    }
  }
  
  // Test 3: Test with image included
  console.log('\n3. Testing snapshot with image:');
  try {
    const response = await fetch(`${API_URL}/api/agent/chart-snapshot/${TEST_SYMBOL}?include_image=true`);
    if (response.status === 404) {
      console.log('   No snapshot available');
    } else if (response.ok) {
      const snapshot = await response.json();
      if (snapshot.image_base64) {
        console.log(`   ✅ Image included (size: ${snapshot.image_base64.length} chars)`);
      } else {
        console.log('   ⚠️ No image in snapshot');
      }
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
  }
  
  // Test 4: Test invalid symbol
  console.log('\n4. Testing invalid symbol:');
  try {
    const response = await fetch(`${API_URL}/api/agent/chart-snapshot/INVALID123`);
    if (response.status === 404) {
      console.log('   ✅ Correctly returns 404 for invalid symbol');
    } else {
      console.log(`   ⚠️ Unexpected response: ${response.status}`);
    }
  } catch (error) {
    console.log(`   ❌ Error: ${error.message}`);
  }
}

// Test agent orchestration with chart commands
async function testAgentWithChart() {
  console.log('\n\nTesting Agent Orchestration with Chart Commands...\n');
  
  const queries = [
    "Show me AAPL chart with technical indicators",
    "Analyze the current trend for TSLA",
    "Display NVDA with moving averages"
  ];
  
  for (const query of queries) {
    console.log(`Query: "${query}"`);
    try {
      const response = await fetch(`${API_URL}/api/agent/orchestrate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          stream: false,
          session_id: `test_${Date.now()}`
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log(`   ✅ Response received`);
        if (result.chart_commands && result.chart_commands.length > 0) {
          console.log(`   - Chart commands: ${result.chart_commands.join(', ')}`);
        }
        if (result.structured_output) {
          console.log(`   - Structured data included`);
        }
        console.log(`   - Response text: ${result.text.substring(0, 100)}...`);
      } else {
        console.log(`   ❌ Request failed: ${response.status}`);
      }
    } catch (error) {
      console.log(`   ❌ Error: ${error.message}`);
    }
    console.log('');
  }
}

// Run all tests
async function runTests() {
  console.log('='.repeat(60));
  console.log('PHASE 3: FRONTEND INTEGRATION TEST SUITE');
  console.log('='.repeat(60));
  
  await testSnapshotAPI();
  await testAgentWithChart();
  
  console.log('\n' + '='.repeat(60));
  console.log('TEST SUITE COMPLETE');
  console.log('='.repeat(60));
  console.log('\nNext steps:');
  console.log('1. Open http://localhost:5174 in browser');
  console.log('2. Ask a chart-related question in the voice assistant');
  console.log('3. Verify patterns appear with Accept/Reject buttons');
  console.log('4. Test validation controls and visual feedback');
}

runTests().catch(console.error);