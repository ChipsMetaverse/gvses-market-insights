#!/usr/bin/env node

/**
 * Comet Assistant Task Automation
 * Use the native Assistant for various web tasks
 */

const { CometController } = require('./comet_applescript_control.js');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

class CometAssistantAutomation {
  constructor() {
    this.comet = new CometController();
  }
  
  async ensureRunning() {
    if (!this.comet.isRunning()) {
      console.log('🚀 Launching Comet...');
      this.comet.launch();
      await sleep(3000);
    }
  }
  
  async navigateToPage(url) {
    console.log(`\n📍 Task: Navigate to ${url}`);
    console.log('─────────────────────────────\n');
    
    await this.ensureRunning();
    
    this.comet.newTab();
    await sleep(1000);
    
    this.comet.toggleAssistant();
    await sleep(1000);
    
    this.comet.sendToAssistant(`Navigate to ${url}`);
    await sleep(4000);
    
    console.log('✅ Navigation complete\n');
  }
  
  async analyzePage(question) {
    console.log(`\n🔍 Task: Analyze current page`);
    console.log('─────────────────────────────\n');
    console.log(`Question: ${question}\n`);
    
    await this.ensureRunning();
    
    this.comet.toggleAssistant();
    await sleep(1000);
    
    this.comet.sendToAssistant(question);
    await sleep(6000);
    
    console.log('✅ Analysis complete\n');
  }
  
  async extractData(instruction) {
    console.log(`\n📊 Task: Extract data from page`);
    console.log('─────────────────────────────\n');
    console.log(`Instruction: ${instruction}\n`);
    
    await this.ensureRunning();
    
    this.comet.toggleAssistant();
    await sleep(1000);
    
    this.comet.sendToAssistant(instruction);
    await sleep(6000);
    
    console.log('✅ Extraction complete\n');
  }
  
  async summarizeCurrentPage() {
    console.log(`\n📄 Task: Summarize current page`);
    console.log('─────────────────────────────\n');
    
    await this.ensureRunning();
    
    console.log('Using Cmd+S shortcut...');
    this.comet.summarizePage();
    await sleep(4000);
    
    console.log('✅ Summary complete\n');
  }
  
  async performWebAction(action) {
    console.log(`\n⚡ Task: Perform web action`);
    console.log('─────────────────────────────\n');
    console.log(`Action: ${action}\n`);
    
    await this.ensureRunning();
    
    this.comet.toggleAssistant();
    await sleep(1000);
    
    this.comet.sendToAssistant(action);
    await sleep(6000);
    
    console.log('✅ Action complete\n');
  }
  
  async captureScreenshot(filename) {
    console.log(`\n📸 Task: Capture screenshot`);
    console.log('─────────────────────────────\n');
    
    await this.ensureRunning();
    
    this.comet.screenshot(filename);
    await sleep(1000);
    
    console.log(`✅ Screenshot saved: ${filename}\n`);
  }
}

// Example workflows
async function exampleWorkflows() {
  const assistant = new CometAssistantAutomation();
  
  console.log('🎯 Comet Assistant Task Automation');
  console.log('===================================\n');
  
  // Workflow 1: Navigate and Analyze
  console.log('📋 Workflow 1: Navigate to trading dashboard and analyze\n');
  
  await assistant.navigateToPage('localhost:5175');
  await assistant.captureScreenshot('dashboard_initial.png');
  await assistant.analyzePage('What stocks are shown and what are their current prices?');
  await assistant.captureScreenshot('dashboard_analysis.png');
  
  console.log('✅ Workflow 1 complete!\n');
  
  // Workflow 2: Extract specific data
  console.log('📋 Workflow 2: Extract stock data\n');
  
  await assistant.extractData('List all stock tickers visible on this page with their prices');
  
  console.log('✅ Workflow 2 complete!\n');
  
  // Workflow 3: Summarize
  console.log('📋 Workflow 3: Summarize the dashboard\n');
  
  await assistant.summarizeCurrentPage();
  
  console.log('✅ Workflow 3 complete!\n');
  
  console.log('🎉 All workflows completed!');
  console.log('📊 Check Comet window for Assistant responses');
  console.log('📸 Check screenshots: dashboard_initial.png, dashboard_analysis.png');
}

// Command line interface
async function cli() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  const assistant = new CometAssistantAutomation();
  
  switch (command) {
    case 'navigate':
      const url = args[1] || 'localhost:5175';
      await assistant.navigateToPage(url);
      break;
      
    case 'analyze':
      const question = args.slice(1).join(' ') || 'What is on this page?';
      await assistant.analyzePage(question);
      break;
      
    case 'extract':
      const instruction = args.slice(1).join(' ') || 'Extract all text from this page';
      await assistant.extractData(instruction);
      break;
      
    case 'summarize':
      await assistant.summarizeCurrentPage();
      break;
      
    case 'action':
      const action = args.slice(1).join(' ');
      if (!action) {
        console.log('❌ Please provide an action');
        process.exit(1);
      }
      await assistant.performWebAction(action);
      break;
      
    case 'screenshot':
      const filename = args[1] || 'screenshot.png';
      await assistant.captureScreenshot(filename);
      break;
      
    case 'workflow':
      await exampleWorkflows();
      break;
      
    default:
      console.log('🎯 Comet Assistant Task Automation');
      console.log('===================================\n');
      console.log('Usage:');
      console.log('  node comet_assistant_tasks.js navigate [url]');
      console.log('  node comet_assistant_tasks.js analyze [question]');
      console.log('  node comet_assistant_tasks.js extract [instruction]');
      console.log('  node comet_assistant_tasks.js summarize');
      console.log('  node comet_assistant_tasks.js action [action]');
      console.log('  node comet_assistant_tasks.js screenshot [filename]');
      console.log('  node comet_assistant_tasks.js workflow\n');
      console.log('Examples:');
      console.log('  node comet_assistant_tasks.js navigate localhost:5175');
      console.log('  node comet_assistant_tasks.js analyze "What stocks are shown?"');
      console.log('  node comet_assistant_tasks.js extract "List all stock prices"');
      console.log('  node comet_assistant_tasks.js summarize');
      console.log('  node comet_assistant_tasks.js screenshot trading.png');
      console.log('  node comet_assistant_tasks.js workflow');
  }
}

// Run
cli().catch(error => {
  console.error('❌ Error:', error.message);
  process.exit(1);
});

module.exports = { CometAssistantAutomation };

