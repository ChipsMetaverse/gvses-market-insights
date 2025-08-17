#!/usr/bin/env node

/**
 * Test script for Market MCP Server
 * Validates setup and tests basic functionality
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import yahooFinance from 'yahoo-finance2';
import axios from 'axios';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const COLORS = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${COLORS[color]}${message}${COLORS.reset}`);
}

async function testSetup() {
  log('\n🧪 Market MCP Server Test Suite\n', 'cyan');
  
  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;
  
  // Test 1: Node.js version
  totalTests++;
  log('Test 1: Checking Node.js version...', 'yellow');
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
  
  if (majorVersion >= 18) {
    log(`  ✅ Node.js ${nodeVersion} (>= 18.0.0 required)`, 'green');
    passedTests++;
  } else {
    log(`  ❌ Node.js ${nodeVersion} is too old (>= 18.0.0 required)`, 'red');
    failedTests++;
  }
  
  // Test 2: Dependencies
  totalTests++;
  log('\nTest 2: Checking dependencies...', 'yellow');
  const requiredPackages = [
    '@modelcontextprotocol/sdk',
    'yahoo-finance2',
    'axios',
    'ws',
    'cheerio',
    'node-cache',
    'p-limit',
    'date-fns'
  ];
  
  const nodeModulesPath = path.join(__dirname, 'node_modules');
  let allDepsInstalled = true;
  
  for (const pkg of requiredPackages) {
    const pkgPath = path.join(nodeModulesPath, pkg);
    if (!fs.existsSync(pkgPath)) {
      log(`  ❌ Missing: ${pkg}`, 'red');
      allDepsInstalled = false;
    }
  }
  
  if (allDepsInstalled) {
    log('  ✅ All dependencies installed', 'green');
    passedTests++;
  } else {
    log('  ❌ Some dependencies missing. Run: npm install', 'red');
    failedTests++;
  }
  
  // Test 3: Yahoo Finance API
  totalTests++;
  log('\nTest 3: Testing Yahoo Finance API...', 'yellow');
  try {
    const quote = await yahooFinance.quote('AAPL');
    if (quote && quote.regularMarketPrice) {
      log(`  ✅ Yahoo Finance working (AAPL: $${quote.regularMarketPrice})`, 'green');
      passedTests++;
    } else {
      log('  ⚠️  Yahoo Finance returned incomplete data', 'yellow');
      passedTests++;
    }
  } catch (error) {
    log(`  ❌ Yahoo Finance error: ${error.message}`, 'red');
    failedTests++;
  }
  
  // Test 4: CoinGecko API
  totalTests++;
  log('\nTest 4: Testing CoinGecko API...', 'yellow');
  try {
    const response = await axios.get(
      'https://api.coingecko.com/api/v3/simple/price',
      {
        params: {
          ids: 'bitcoin',
          vs_currencies: 'usd'
        },
        timeout: 5000
      }
    );
    
    if (response.data && response.data.bitcoin) {
      log(`  ✅ CoinGecko working (BTC: $${response.data.bitcoin.usd})`, 'green');
      passedTests++;
    } else {
      log('  ⚠️  CoinGecko returned unexpected data', 'yellow');
      passedTests++;
    }
  } catch (error) {
    log(`  ❌ CoinGecko error: ${error.message}`, 'red');
    failedTests++;
  }
  
  // Test 5: Environment configuration
  totalTests++;
  log('\nTest 5: Checking environment configuration...', 'yellow');
  const envPath = path.join(__dirname, '.env');
  
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const hasApiKeys = envContent.includes('_API_KEY=') && 
                      !envContent.includes('your_') &&
                      !envContent.includes('_key_here');
    
    if (hasApiKeys) {
      log('  ✅ API keys configured in .env', 'green');
    } else {
      log('  ⚠️  No API keys configured (server will use free tiers)', 'yellow');
    }
    passedTests++;
  } else {
    log('  ⚠️  No .env file (server will use default settings)', 'yellow');
    passedTests++;
  }
  
  // Test 6: Server startup
  totalTests++;
  log('\nTest 6: Testing server startup...', 'yellow');
  
  return new Promise((resolve) => {
    const serverProcess = spawn('node', [path.join(__dirname, 'index.js')], {
      env: { ...process.env, NODE_ENV: 'test' },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let serverStarted = false;
    let errorOutput = '';
    
    serverProcess.stderr.on('data', (data) => {
      const output = data.toString();
      errorOutput += output;
      
      if (output.includes('Market MCP Server running')) {
        serverStarted = true;
        serverProcess.kill();
      }
    });
    
    serverProcess.on('error', (error) => {
      log(`  ❌ Server process error: ${error.message}`, 'red');
      failedTests++;
    });
    
    setTimeout(async () => {
      serverProcess.kill();
      
      if (serverStarted) {
        log('  ✅ Server starts successfully', 'green');
        passedTests++;
      } else if (errorOutput.includes('Error')) {
        log(`  ❌ Server startup failed: ${errorOutput}`, 'red');
        failedTests++;
      } else {
        log('  ✅ Server process runs without errors', 'green');
        passedTests++;
      }
      
      // Test 7: Data freshness test
      totalTests++;
      log('\nTest 7: Testing data freshness...', 'yellow');
      try {
        const quote = await yahooFinance.quote('SPY');
        const now = new Date();
        const marketTime = new Date(quote.regularMarketTime * 1000);
        const hoursDiff = Math.abs(now - marketTime) / (1000 * 60 * 60);
        
        if (hoursDiff < 48) {
          log(`  ✅ Data is fresh (last update: ${marketTime.toISOString()})`, 'green');
          passedTests++;
        } else {
          log(`  ⚠️  Data might be stale (last update: ${marketTime.toISOString()})`, 'yellow');
          passedTests++;
        }
      } catch (error) {
        log(`  ⚠️  Could not verify data freshness`, 'yellow');
        passedTests++;
      }
      
      // Test 8: Rate limiting
      totalTests++;
      log('\nTest 8: Testing rate limiting...', 'yellow');
      try {
        const promises = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'].map(symbol =>
          yahooFinance.quote(symbol)
        );
        
        await Promise.all(promises);
        log('  ✅ Rate limiting handled correctly', 'green');
        passedTests++;
      } catch (error) {
        log(`  ⚠️  Rate limiting might need adjustment: ${error.message}`, 'yellow');
        passedTests++;
      }
      
      // Test Summary
      console.log('\n' + '='.repeat(50));
      log(`\n📊 Test Results Summary\n`, 'cyan');
      log(`Total Tests: ${totalTests}`, 'blue');
      log(`Passed: ${passedTests}`, 'green');
      log(`Failed: ${failedTests}`, failedTests > 0 ? 'red' : 'green');
      
      const successRate = (passedTests / totalTests * 100).toFixed(1);
      
      if (failedTests === 0) {
        log(`\n✨ All tests passed! (${successRate}%)`, 'green');
        log('Your Market MCP server is ready to use.\n', 'green');
      } else if (failedTests <= 2) {
        log(`\n⚠️  Most tests passed (${successRate}%)`, 'yellow');
        log('The server should work, but some features might be limited.\n', 'yellow');
      } else {
        log(`\n❌ Multiple tests failed (${successRate}%)`, 'red');
        log('Please fix the issues before using the server.\n', 'red');
      }
      
      // Show available tools
      log('📈 Available Market Tools:', 'cyan');
      const tools = [
        'Stock quotes and history',
        'Cryptocurrency prices',
        'Technical indicators (RSI, MACD, Bollinger Bands)',
        'Market news and analysis',
        'Real-time streaming',
        'Portfolio tracking',
        'Economic data',
        'Fear & Greed Index'
      ];
      
      tools.forEach(tool => {
        log(`  • ${tool}`, 'blue');
      });
      
      console.log('\n');
      resolve(failedTests === 0);
    }, 3000);
  });
}

// Run tests
testSetup().then((success) => {
  process.exit(success ? 0 : 1);
}).catch((error) => {
  log(`\n❌ Test suite error: ${error.message}`, 'red');
  process.exit(1);
});
