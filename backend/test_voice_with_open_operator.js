#!/usr/bin/env node
/**
 * Natural Language Voice Assistant Test using Open Operator
 * Tests the trading app from a new trader's perspective
 * Uses Stagehand/Browserbase for browser automation
 */

const fetch = require('node-fetch');
const fs = require('fs').promises;

class TradingAppTester {
  constructor() {
    this.openOperatorUrl = 'http://localhost:3000/api/agent';
    this.sessionUrl = 'http://localhost:3000/api/session';
    this.tradingAppUrl = 'http://localhost:5174';
    this.testResults = {
      timestamp: new Date().toISOString(),
      tests: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        accuracy_scores: []
      }
    };
  }

  // Test scenarios for a new trader
  getTestScenarios() {
    return [
      // Price Queries
      {
        category: 'price',
        question: 'What is the current price of TSLA?',
        naturalCommand: 'Click on the voice button, wait for connection, then type "What is the current price of TSLA?" in the message input and press Enter',
        expectedKeywords: ['TSLA', 'price', '$', '440'],
        waitTime: 8000
      },
      {
        category: 'price', 
        question: 'How much is Apple stock?',
        naturalCommand: 'Type "How much is Apple stock?" in the message input and press Enter',
        expectedKeywords: ['AAPL', 'Apple', '$', '255'],
        waitTime: 8000
      },
      
      // Technical Analysis
      {
        category: 'technical',
        question: 'Show me the technical levels for TSLA',
        naturalCommand: 'Type "Show me the technical levels for TSLA" in the message input and press Enter',
        expectedKeywords: ['support', 'resistance', 'level', '$'],
        waitTime: 10000
      },
      
      // Pattern Detection
      {
        category: 'patterns',
        question: 'Are there any patterns in TSLA?',
        naturalCommand: 'Type "Are there any patterns in TSLA?" in the message input and press Enter',
        expectedKeywords: ['pattern', 'TSLA'],
        waitTime: 10000
      },
      
      // News
      {
        category: 'news',
        question: "What's the latest news on Tesla?",
        naturalCommand: 'Type "What\'s the latest news on Tesla?" in the message input and press Enter',
        expectedKeywords: ['Tesla', 'TSLA', 'news'],
        waitTime: 10000
      },
      
      // Trading Recommendations
      {
        category: 'strategy',
        question: 'Should I buy TSLA now?',
        naturalCommand: 'Type "Should I buy TSLA now?" in the message input and press Enter',
        expectedKeywords: ['TSLA', 'buy', 'sell', 'recommendation'],
        waitTime: 12000
      },
      
      // Comparisons
      {
        category: 'comparison',
        question: 'Compare TSLA and NVDA',
        naturalCommand: 'Type "Compare TSLA and NVDA" in the message input and press Enter',
        expectedKeywords: ['TSLA', 'NVDA', 'compare'],
        waitTime: 12000
      },
      
      // Educational
      {
        category: 'educational',
        question: 'What does BTD mean?',
        naturalCommand: 'Type "What does BTD mean?" in the message input and press Enter',
        expectedKeywords: ['BTD', 'Buy', 'Dip'],
        waitTime: 8000
      },
      
      // Risk Management
      {
        category: 'risk',
        question: "What's a good stop loss for TSLA?",
        naturalCommand: 'Type "What\'s a good stop loss for TSLA?" in the message input and press Enter',
        expectedKeywords: ['stop', 'loss', 'TSLA', 'risk'],
        waitTime: 10000
      }
    ];
  }

  async createSession() {
    try {
      console.log('🔄 Creating Browserbase session...');
      const response = await fetch(this.sessionUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      
      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Session created:', data.sessionID);
      return data.sessionID;
    } catch (error) {
      console.error('❌ Error creating session:', error);
      throw error;
    }
  }

  async sendCommand(sessionID, goal) {
    try {
      console.log(`📤 Sending command: "${goal}"`);
      const response = await fetch(this.openOperatorUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal,
          sessionID
        })
      });
      
      if (!response.ok) {
        throw new Error(`Command failed: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('❌ Error sending command:', error);
      throw error;
    }
  }

  async wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async captureResponse(sessionID) {
    // Extract the response text from the voice assistant
    const extractCommand = 'Extract the last assistant response from the voice conversation section';
    
    try {
      const result = await this.sendCommand(sessionID, extractCommand);
      return result.extraction || '';
    } catch (error) {
      console.error('Error capturing response:', error);
      return '';
    }
  }

  auditResponse(response, expectedKeywords) {
    const responseLower = response.toLowerCase();
    const found = [];
    const missing = [];
    
    for (const keyword of expectedKeywords) {
      if (responseLower.includes(keyword.toLowerCase())) {
        found.push(keyword);
      } else {
        missing.push(keyword);
      }
    }
    
    const accuracy = expectedKeywords.length > 0 
      ? found.length / expectedKeywords.length 
      : 0;
    
    return {
      found,
      missing,
      accuracy,
      passed: accuracy >= 0.5
    };
  }

  async runTest() {
    console.log('=' .repeat(80));
    console.log('🤖 VOICE ASSISTANT TEST - NEW TRADER PERSPECTIVE');
    console.log('    Using Open Operator for Natural Language Testing');
    console.log('=' .repeat(80));
    
    const scenarios = this.getTestScenarios();
    console.log(`📋 Testing ${scenarios.length} scenarios`);
    console.log('');
    
    // Create browser session
    const sessionID = await this.createSession();
    
    try {
      // Navigate to trading app
      console.log('🌐 Opening trading app...');
      await this.sendCommand(sessionID, `Go to ${this.tradingAppUrl}`);
      await this.wait(5000); // Wait for app to load
      
      // Connect Voice Assistant
      console.log('🎤 Connecting Voice Assistant...');
      await this.sendCommand(sessionID, 'Click on the voice button in the bottom right corner');
      await this.wait(3000); // Wait for connection
      
      // Run each test scenario
      for (let i = 0; i < scenarios.length; i++) {
        const scenario = scenarios[i];
        console.log('');
        console.log(`Test ${i + 1}/${scenarios.length}: ${scenario.category.toUpperCase()}`);
        console.log(`Question: "${scenario.question}"`);
        
        const testResult = {
          test_number: i + 1,
          category: scenario.category,
          question: scenario.question,
          response: '',
          found_keywords: [],
          missing_keywords: [],
          accuracy_score: 0,
          passed: false,
          issues: []
        };
        
        try {
          // Send the command
          await this.sendCommand(sessionID, scenario.naturalCommand);
          
          // Wait for response
          console.log(`⏳ Waiting ${scenario.waitTime}ms for response...`);
          await this.wait(scenario.waitTime);
          
          // Capture response
          const response = await this.captureResponse(sessionID);
          testResult.response = response;
          
          if (response) {
            console.log(`💬 Response captured: ${response.substring(0, 100)}...`);
            
            // Audit response
            const audit = this.auditResponse(response, scenario.expectedKeywords);
            testResult.found_keywords = audit.found;
            testResult.missing_keywords = audit.missing;
            testResult.accuracy_score = audit.accuracy;
            testResult.passed = audit.passed;
            
            if (audit.found.length > 0) {
              console.log(`✅ Found keywords: ${audit.found.join(', ')}`);
            }
            if (audit.missing.length > 0) {
              console.log(`⚠️ Missing keywords: ${audit.missing.join(', ')}`);
            }
            console.log(`📊 Accuracy: ${(audit.accuracy * 100).toFixed(1)}%`);
            console.log(audit.passed ? '✅ TEST PASSED' : '❌ TEST FAILED');
            
            if (audit.passed) {
              this.testResults.summary.passed++;
            } else {
              this.testResults.summary.failed++;
              testResult.issues.push('Insufficient keyword matches');
            }
          } else {
            console.log('❌ No response captured');
            testResult.issues.push('No response received');
            this.testResults.summary.failed++;
          }
          
        } catch (error) {
          console.log(`❌ Test error: ${error.message}`);
          testResult.issues.push(`Error: ${error.message}`);
          this.testResults.summary.failed++;
        }
        
        this.testResults.tests.push(testResult);
        this.testResults.summary.accuracy_scores.push(testResult.accuracy_score);
        
        // Small pause between tests
        await this.wait(2000);
      }
      
      // Calculate summary statistics
      this.testResults.summary.total = scenarios.length;
      const avgAccuracy = this.testResults.summary.accuracy_scores.reduce((a, b) => a + b, 0) 
        / this.testResults.summary.accuracy_scores.length;
      this.testResults.summary.average_accuracy = avgAccuracy;
      
      // Take final screenshot
      console.log('\n📸 Taking final screenshot...');
      await this.sendCommand(sessionID, 'Take a screenshot of the current page');
      
    } finally {
      // Close session
      console.log('🔚 Closing browser session...');
      await this.sendCommand(sessionID, 'Close the browser');
    }
    
    // Generate report
    this.generateReport();
    
    // Save results
    const filename = `voice_test_openoperator_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    await fs.writeFile(filename, JSON.stringify(this.testResults, null, 2));
    console.log(`\n💾 Results saved to: ${filename}`);
  }

  generateReport() {
    console.log('\n' + '='.repeat(80));
    console.log('📊 TEST REPORT');
    console.log('='.repeat(80));
    
    const summary = this.testResults.summary;
    
    console.log('\n📈 OVERALL RESULTS:');
    console.log(`   Total Tests: ${summary.total}`);
    console.log(`   Passed: ${summary.passed} (${(summary.passed/summary.total*100).toFixed(1)}%)`);
    console.log(`   Failed: ${summary.failed} (${(summary.failed/summary.total*100).toFixed(1)}%)`);
    console.log(`   Average Accuracy: ${(summary.average_accuracy*100).toFixed(1)}%`);
    
    // Category breakdown
    console.log('\n📊 CATEGORY BREAKDOWN:');
    const categories = {};
    for (const test of this.testResults.tests) {
      if (!categories[test.category]) {
        categories[test.category] = { passed: 0, failed: 0, accuracy: [] };
      }
      if (test.passed) {
        categories[test.category].passed++;
      } else {
        categories[test.category].failed++;
      }
      categories[test.category].accuracy.push(test.accuracy_score);
    }
    
    for (const [cat, data] of Object.entries(categories)) {
      const total = data.passed + data.failed;
      const avgAcc = data.accuracy.reduce((a, b) => a + b, 0) / data.accuracy.length;
      const status = avgAcc >= 0.7 ? '✅' : avgAcc >= 0.5 ? '⚠️' : '❌';
      console.log(`   ${status} ${cat.toUpperCase()}: ${(avgAcc*100).toFixed(1)}% accuracy (${data.passed}/${total} passed)`);
    }
    
    // Recommendations
    console.log('\n💡 RECOMMENDATIONS:');
    const avgAcc = summary.average_accuracy;
    if (avgAcc >= 0.8) {
      console.log('   ✅ Excellent: Voice Assistant performing very well');
    } else if (avgAcc >= 0.6) {
      console.log('   ⚠️ Good: Voice Assistant working but needs improvements');
      console.log('   - Review failed tests for specific issues');
    } else {
      console.log('   ❌ Needs Improvement: Voice Assistant requires significant work');
      console.log('   - Many responses missing expected information');
    }
  }
}

// Main execution
async function main() {
  console.log('🚀 Starting Voice Assistant Test with Open Operator');
  console.log('   Make sure:');
  console.log('   1. Trading app is running on http://localhost:5174');
  console.log('   2. Open Operator is running on http://localhost:3000');
  console.log('   3. API keys are configured in Open Operator\n');
  
  const tester = new TradingAppTester();
  
  try {
    await tester.runTest();
    console.log('\n✅ TEST COMPLETE!');
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

module.exports = { TradingAppTester };