const fetch = require('node-fetch');

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  bold: '\x1b[1m'
};

async function testTechnicalQueries() {
  const baseUrl = 'http://localhost:8000';
  
  console.log(`${colors.bold}${colors.blue}🚀 Testing Technical Query Handling${colors.reset}\n`);
  
  const testCases = [
    {
      name: 'TSLA Swing Trade Levels',
      query: 'What are the swing trade levels for TSLA?',
      expectedKeywords: ['entry', 'target', 'stop', 'support', 'resistance', 'swing_trade']
    },
    {
      name: 'NVDA Entry/Exit Points',
      query: 'Give me entry and exit points for a swing trade on NVDA',
      expectedKeywords: ['entry_points', 'targets', 'stop_loss', 'risk_reward']
    },
    {
      name: 'AAPL Support/Resistance',
      query: 'What are the support and resistance levels for AAPL?',
      expectedKeywords: ['support', 'resistance', 'level']
    },
    {
      name: 'SPY Technical Analysis',
      query: 'Provide technical analysis with entry points for SPY',
      expectedKeywords: ['technical', 'entry', 'analysis']
    }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const testCase of testCases) {
    console.log(`${colors.bold}Test: ${testCase.name}${colors.reset}`);
    console.log(`Query: "${testCase.query}"`);
    
    try {
      const startTime = Date.now();
      
      const response = await fetch(`${baseUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: testCase.query
        })
      });
      
      const responseTime = Date.now() - startTime;
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${data.detail || 'Unknown error'}`);
      }
      
      // Check if response contains expected content
      const responseText = data.response || '';
      const responseLength = responseText.length;
      
      // Check for generic error response
      if (responseText.includes("I'm sorry, I couldn't generate a response")) {
        console.log(`${colors.red}❌ FAILED: Got generic error response${colors.reset}`);
        failed++;
      } else if (responseLength < 100) {
        console.log(`${colors.red}❌ FAILED: Response too short (${responseLength} chars)${colors.reset}`);
        failed++;
      } else {
        // Check for expected keywords
        const foundKeywords = testCase.expectedKeywords.filter(keyword => 
          responseText.toLowerCase().includes(keyword.toLowerCase())
        );
        
        if (foundKeywords.length >= Math.ceil(testCase.expectedKeywords.length * 0.6)) {
          console.log(`${colors.green}✅ PASSED${colors.reset}`);
          console.log(`  Response time: ${responseTime}ms`);
          console.log(`  Response length: ${responseLength} chars`);
          console.log(`  Found keywords: ${foundKeywords.join(', ')}`);
          
          // Check for JSON structure
          if (responseText.includes('```json')) {
            console.log(`  ${colors.green}✓ Contains JSON structure${colors.reset}`);
            
            // Extract and validate JSON
            const jsonMatch = responseText.match(/```json\n([\s\S]*?)\n```/);
            if (jsonMatch) {
              try {
                const jsonData = JSON.parse(jsonMatch[1]);
                if (jsonData.swing_trade) {
                  console.log(`  ${colors.green}✓ Valid swing trade JSON with:`);
                  if (jsonData.swing_trade.entry_points) 
                    console.log(`    - Entry points: ${jsonData.swing_trade.entry_points.join(', ')}`);
                  if (jsonData.swing_trade.targets) 
                    console.log(`    - Targets: ${jsonData.swing_trade.targets.join(', ')}`);
                  if (jsonData.swing_trade.stop_loss) 
                    console.log(`    - Stop loss: ${jsonData.swing_trade.stop_loss}`);
                  console.log(colors.reset);
                }
              } catch (e) {
                console.log(`  ${colors.yellow}⚠ JSON present but couldn't parse${colors.reset}`);
              }
            }
          }
          
          // Show response preview
          console.log(`  Preview: "${responseText.substring(0, 150)}..."`);
          passed++;
        } else {
          console.log(`${colors.red}❌ FAILED: Missing expected keywords${colors.reset}`);
          console.log(`  Found only: ${foundKeywords.join(', ')}`);
          console.log(`  Expected: ${testCase.expectedKeywords.join(', ')}`);
          failed++;
        }
      }
      
    } catch (error) {
      console.log(`${colors.red}❌ ERROR: ${error.message}${colors.reset}`);
      failed++;
    }
    
    console.log(''); // Empty line between tests
  }
  
  // Summary
  console.log(`${colors.bold}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.bold}Test Summary:${colors.reset}`);
  console.log(`${colors.green}Passed: ${passed}${colors.reset}`);
  console.log(`${colors.red}Failed: ${failed}${colors.reset}`);
  
  const successRate = (passed / testCases.length * 100).toFixed(1);
  if (passed === testCases.length) {
    console.log(`${colors.bold}${colors.green}✨ All tests passed! (${successRate}%)${colors.reset}`);
  } else if (passed > 0) {
    console.log(`${colors.bold}${colors.yellow}⚠ Partial success (${successRate}%)${colors.reset}`);
  } else {
    console.log(`${colors.bold}${colors.red}❌ All tests failed${colors.reset}`);
  }
  
  return passed === testCases.length;
}

// Run tests
testTechnicalQueries()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error(`${colors.red}Fatal error:${colors.reset}`, error);
    process.exit(1);
  });