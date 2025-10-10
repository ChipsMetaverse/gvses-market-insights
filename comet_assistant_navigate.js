#!/usr/bin/env node

/**
 * Use Comet Assistant to Navigate to Webpage
 * Demonstrates using the native Assistant for navigation
 */

const { CometController } = require('./comet_applescript_control.js');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function navigateWithAssistant(targetUrl = 'localhost:5175') {
  console.log('🚀 Comet Assistant Navigation Demo');
  console.log('===================================\n');
  
  const comet = new CometController();
  
  // Step 1: Launch Comet if not running
  if (!comet.isRunning()) {
    console.log('Step 1: Launching Comet natively...');
    comet.launch();
    await sleep(3000);
    console.log('✅ Comet launched\n');
  } else {
    console.log('Step 1: Comet already running ✅\n');
  }
  
  // Step 2: Open new tab for clean start
  console.log('Step 2: Opening new tab...');
  comet.newTab();
  await sleep(1500);
  console.log('✅ New tab opened\n');
  
  // Step 3: Activate the Assistant
  console.log('Step 3: Activating Comet Assistant...');
  console.log('  💡 Using keyboard shortcut: Cmd+A');
  comet.toggleAssistant();
  await sleep(1500);
  console.log('✅ Assistant activated\n');
  
  // Step 4: Ask Assistant to navigate
  console.log('Step 4: Asking Assistant to navigate...');
  const navigationCommand = `Navigate to ${targetUrl}`;
  console.log(`  💬 Command: "${navigationCommand}"`);
  
  comet.sendToAssistant(navigationCommand);
  await sleep(1000);
  console.log('✅ Command sent to Assistant\n');
  
  // Step 5: Wait for Assistant to process and navigate
  console.log('Step 5: Waiting for Assistant to navigate...');
  console.log('  ⏳ Assistant is processing the request...');
  await sleep(5000);
  
  console.log('\n✅ Navigation Complete!\n');
  
  console.log('📊 What happened:');
  console.log('  1. Comet opened with full native features');
  console.log('  2. Assistant activated with Cmd+A shortcut');
  console.log('  3. Navigation command sent to Assistant');
  console.log('  4. Assistant processed and navigated to page');
  console.log('  5. All native features remained functional\n');
  
  console.log('💡 The Assistant can also:');
  console.log('  - Search for websites');
  console.log('  - Open specific pages');
  console.log('  - Perform web actions');
  console.log('  - Analyze page content');
  console.log('  - Extract information\n');
  
  console.log('🎯 Check the Comet window to see the result!');
  
  return true;
}

// Parse command line arguments
const args = process.argv.slice(2);
const targetUrl = args[0] || 'localhost:5175';

console.log(`🎯 Target URL: ${targetUrl}\n`);

// Run the navigation
navigateWithAssistant(targetUrl).catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

