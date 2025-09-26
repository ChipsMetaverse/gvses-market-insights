const fetch = require('node-fetch');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[36m',
  bold: '\x1b[1m'
};

async function testChartCommands() {
  const baseUrl = 'http://localhost:8000';
  
  console.log(`${colors.bold}${colors.blue}🎯 Testing Chart Command Generation${colors.reset}\n`);
  
  const testCases = [
    {
      name: 'Chart with Symbol Change',
      query: 'Show me the NVDA chart with technical analysis',
      expectedCommands: ['CHART:NVDA'],
      expectedInResponse: ['NVDA', 'chart']
    },
    {
      name: 'Timeframe Change',
      query: 'Display the daily chart for AAPL with support levels',
      expectedCommands: ['CHART:AAPL', 'TIMEFRAME:1D'],
      expectedInResponse: ['AAPL', 'daily', 'support']
    },
    {
      name: 'Weekly Timeframe',
      query: 'Show me Tesla weekly chart with trend lines',
      expectedCommands: ['CHART:TSLA', 'TIMEFRAME:1W'],
      expectedInResponse: ['Tesla', 'weekly', 'trend']
    },
    {
      name: 'Company Name Resolution',
      query: 'Display Microsoft chart with one month timeframe',
      expectedCommands: ['CHART:MSFT', 'TIMEFRAME:1M'],
      expectedInResponse: ['Microsoft', 'month']
    },
    {
      name: 'Indicators and Patterns',
      query: 'Show SPY chart with fibonacci retracement and support resistance',
      expectedCommands: ['CHART:SPY'],
      expectedInResponse: ['SPY', 'fibonacci', 'support', 'resistance']
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
      
      // Check for chart commands in the response
      const responseText = data.response || '';
      let chartCommands = [];
      
      // Extract chart commands from tool_results if available
      if (data.tool_results && data.tool_results.chart_commands) {
        chartCommands = data.tool_results.chart_commands;
      }
      
      // Also check for commands embedded in the response text
      const chartMatches = responseText.match(/CHART:[A-Z]+/g) || [];
      const timeframeMatches = responseText.match(/TIMEFRAME:\w+/g) || [];
      const embeddedCommands = [...chartMatches, ...timeframeMatches];
      
      // Combine all found commands
      const allCommands = [...new Set([...chartCommands, ...embeddedCommands])];
      
      console.log(`  Response time: ${responseTime}ms`);
      console.log(`  Found commands: ${allCommands.length > 0 ? allCommands.join(', ') : 'None'}`);
      
      // Check if expected commands were generated
      let commandsFound = 0;
      for (const expectedCmd of testCase.expectedCommands) {
        const found = allCommands.some(cmd => 
          cmd.toUpperCase() === expectedCmd.toUpperCase()
        );
        if (found) {
          commandsFound++;
          console.log(`  ${colors.green}✓ Found: ${expectedCmd}${colors.reset}`);
        } else {
          console.log(`  ${colors.red}✗ Missing: ${expectedCmd}${colors.reset}`);
        }
      }
      
      // Check if response contains expected keywords
      const keywordsFound = testCase.expectedInResponse.filter(keyword =>
        responseText.toLowerCase().includes(keyword.toLowerCase())
      );
      
      // Determine pass/fail
      const commandSuccess = commandsFound >= testCase.expectedCommands.length * 0.5;
      const keywordSuccess = keywordsFound.length >= testCase.expectedInResponse.length * 0.5;
      
      if (commandSuccess || (allCommands.length > 0 && keywordSuccess)) {
        console.log(`${colors.green}✅ PASSED${colors.reset}`);
        passed++;
        
        // Show response preview
        if (responseText.length > 0) {
          const preview = responseText.substring(0, 200);
          console.log(`  Preview: "${preview}..."`);
        }
      } else {
        console.log(`${colors.red}❌ FAILED${colors.reset}`);
        console.log(`  Expected commands: ${testCase.expectedCommands.join(', ')}`);
        console.log(`  Found commands: ${allCommands.join(', ') || 'None'}`);
        failed++;
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
testChartCommands()
  .then(success => {
    process.exit(success ? 0 : 1);
  })
  .catch(error => {
    console.error(`${colors.red}Fatal error:${colors.reset}`, error);
    process.exit(1);
  });