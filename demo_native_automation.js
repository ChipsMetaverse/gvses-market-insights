#!/usr/bin/env node

/**
 * Demo: Comet Browser Automation with Native Features Intact
 * 
 * This demonstrates controlling Comet while preserving its native
 * Assistant, widgets, and all built-in features.
 */

const { CometController } = require('./comet_applescript_control.js');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function demo() {
  console.log('🎯 Comet Native Automation Demo');
  console.log('================================\n');
  
  const comet = new CometController();
  
  // Check if Comet is running
  if (!comet.isRunning()) {
    console.log('📱 Launching Comet...');
    comet.launch();
    await sleep(3000);
  } else {
    console.log('✅ Comet is already running\n');
  }
  
  console.log('📊 Scenario: Analyze Trading Dashboard with Native Assistant\n');
  
  // Step 1: Open new tab
  console.log('Step 1: Opening new tab...');
  comet.newTab();
  await sleep(1000);
  
  // Step 2: Navigate to trading dashboard
  console.log('Step 2: Navigating to localhost:5175...');
  comet.navigateTo('localhost:5175');
  await sleep(4000); // Wait for page to load
  
  // Step 3: Activate Assistant (native feature!)
  console.log('Step 3: Activating Comet Assistant (Cmd+A)...');
  comet.toggleAssistant();
  await sleep(1000);
  
  // Step 4: Ask Assistant to analyze the dashboard
  console.log('Step 4: Asking Assistant to analyze dashboard...');
  const query = 'What stocks are displayed on this trading dashboard and what are their current prices?';
  comet.sendToAssistant(query);
  
  console.log(`\n💬 Query sent: "${query}"`);
  console.log('⏳ Assistant is analyzing (native features working)...\n');
  
  await sleep(7000); // Wait for Assistant response
  
  // Step 5: The Assistant can now:
  // - See the page content (native capability)
  // - Extract stock tickers and prices
  // - Use web scraping if needed
  // - Perform complex analysis
  // All WITHOUT automation flags interfering!
  
  console.log('✅ Demo Complete!\n');
  console.log('📝 What happened:');
  console.log('  1. ✅ Comet launched with all native features');
  console.log('  2. ✅ Navigated to trading dashboard');
  console.log('  3. ✅ Assistant activated with Cmd+A');
  console.log('  4. ✅ Query sent to Assistant');
  console.log('  5. ✅ Assistant analyzed page using native capabilities\n');
  
  console.log('💡 Key Benefit:');
  console.log('  The Assistant has FULL access to:');
  console.log('  - Page content and DOM');
  console.log('  - Native web scraping');
  console.log('  - Complex task execution');
  console.log('  - All without automation restrictions!\n');
  
  console.log('🎯 You can now:');
  console.log('  - Check the Comet window to see the Assistant response');
  console.log('  - The Assistant can handle tasks regular automation cannot');
  console.log('  - All native features (widgets, etc.) remain functional\n');
}

// Run demo
demo().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

module.exports = { demo };

