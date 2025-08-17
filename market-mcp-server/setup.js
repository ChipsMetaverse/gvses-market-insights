#!/usr/bin/env node

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import readline from 'readline';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const question = (query) => new Promise((resolve) => rl.question(query, resolve));

async function setup() {
  console.log('📈 Market MCP Server Setup\n');
  
  // Check Node.js version
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
  
  if (majorVersion < 18) {
    console.error(`❌ Node.js ${nodeVersion} is too old. Please install Node.js 18 or higher.`);
    process.exit(1);
  }
  
  console.log(`✅ Node.js ${nodeVersion}\n`);
  
  // Install dependencies
  console.log('📦 Installing dependencies...\n');
  try {
    execSync('npm install', { stdio: 'inherit', cwd: __dirname });
    console.log('\n✅ Dependencies installed\n');
  } catch (error) {
    console.error('❌ Failed to install dependencies:', error.message);
    process.exit(1);
  }
  
  // Check for .env file
  const envPath = path.join(__dirname, '.env');
  const envExamplePath = path.join(__dirname, '.env.example');
  
  if (!fs.existsSync(envPath) && fs.existsSync(envExamplePath)) {
    console.log('📝 Setting up environment configuration...\n');
    
    const useApiKeys = await question('Do you have API keys for enhanced features? (y/n): ');
    
    if (useApiKeys.toLowerCase() === 'y') {
      fs.copyFileSync(envExamplePath, envPath);
      
      console.log('\nOptional API keys (press Enter to skip any):');
      console.log('Get free API keys from:');
      console.log('- Alpha Vantage: https://www.alphavantage.co/support/#api-key');
      console.log('- Finnhub: https://finnhub.io/register');
      console.log('- Polygon: https://polygon.io/dashboard/signup\n');
      
      const alphaVantage = await question('Alpha Vantage API key (or press Enter to skip): ');
      const finnhub = await question('Finnhub API key (or press Enter to skip): ');
      const polygon = await question('Polygon API key (or press Enter to skip): ');
      
      let envContent = fs.readFileSync(envPath, 'utf-8');
      
      if (alphaVantage) {
        envContent = envContent.replace('your_alphavantage_key_here', alphaVantage.trim());
      }
      if (finnhub) {
        envContent = envContent.replace('your_finnhub_key_here', finnhub.trim());
      }
      if (polygon) {
        envContent = envContent.replace('your_polygon_key_here', polygon.trim());
      }
      
      fs.writeFileSync(envPath, envContent);
      console.log('\n✅ Environment configuration saved\n');
    } else {
      console.log('\n✅ Skipping API keys - server will use free tiers\n');
    }
  }
  
  // Generate Claude Desktop configuration
  console.log('🔧 Generating Claude Desktop configuration...\n');
  
  const config = {
    market: {
      command: 'node',
      args: [path.join(__dirname, 'index.js')]
    }
  };
  
  // Add environment variables if .env exists
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const env = {};
    
    envContent.split('\n').forEach(line => {
      if (line && !line.startsWith('#')) {
        const [key, value] = line.split('=');
        if (key && value && value !== `your_${key.toLowerCase().replace(/_api_key/g, '')}_key_here`) {
          env[key] = value.trim();
        }
      }
    });
    
    if (Object.keys(env).length > 0) {
      config.market.env = env;
    }
  }
  
  console.log('Add this to your Claude Desktop configuration:\n');
  console.log('```json');
  console.log(JSON.stringify({ mcpServers: config }, null, 2));
  console.log('```\n');
  
  console.log('📍 Configuration file location:');
  if (process.platform === 'darwin') {
    console.log('   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json');
  } else if (process.platform === 'win32') {
    console.log('   Windows: %APPDATA%\\Claude\\claude_desktop_config.json');
  } else {
    console.log('   Linux: ~/.config/Claude/claude_desktop_config.json');
  }
  
  // Test the server
  console.log('\n🧪 Testing server startup...');
  
  try {
    const { spawn } = await import('child_process');
    const testProcess = spawn('node', [path.join(__dirname, 'index.js')], {
      env: { ...process.env, NODE_ENV: 'test' },
      stdio: ['pipe', 'pipe', 'pipe']
    });
    
    let serverStarted = false;
    
    testProcess.stderr.on('data', (data) => {
      const output = data.toString();
      if (output.includes('Market MCP Server running')) {
        serverStarted = true;
        testProcess.kill();
      }
    });
    
    setTimeout(() => {
      if (!serverStarted) {
        testProcess.kill();
        console.log('⚠️  Server startup timeout - but this might be normal\n');
      } else {
        console.log('✅ Server starts successfully!\n');
      }
      
      // Show example queries
      console.log('✨ Setup complete!\n');
      console.log('📊 Example queries you can use in Claude:\n');
      console.log('  • "Get the current price of Apple stock"');
      console.log('  • "Show me Bitcoin and Ethereum prices"');
      console.log('  • "What are the top gainers today?"');
      console.log('  • "Calculate RSI for Tesla"');
      console.log('  • "Stream real-time prices for SPY"');
      console.log('  • "Show me the Fear & Greed Index"');
      console.log('  • "Get the latest market news"');
      console.log('  • "Track my portfolio with AAPL and MSFT"');
      console.log('\nNext steps:');
      console.log('1. Add the configuration to Claude Desktop');
      console.log('2. Restart Claude Desktop');
      console.log('3. Start using market tools!\n');
      
      rl.close();
      process.exit(0);
    }, 3000);
    
  } catch (error) {
    console.error('❌ Server test failed:', error.message);
    rl.close();
    process.exit(1);
  }
}

setup().catch((error) => {
  console.error('❌ Setup failed:', error);
  rl.close();
  process.exit(1);
});
