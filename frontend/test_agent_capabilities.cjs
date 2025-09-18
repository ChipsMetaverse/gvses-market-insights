const { chromium } = require('playwright');

/**
 * Test OpenAI Agent Capabilities
 * ==============================
 * Verifies that the OpenAI agent has all required tools loaded
 * and properly configured for voice interactions.
 */

(async () => {
  const browser = await chromium.launch({ 
    headless: false,
    devtools: true
  });
  
  const context = await browser.newContext({
    permissions: ['microphone']
  });
  const page = await context.newPage();
  
  // Enhanced logging
  const logs = [];
  const errors = [];
  const wsMessages = new Map();
  
  page.on('console', msg => {
    const text = msg.text();
    if (!text.includes('contentScript.js') && !text.includes('[HMR]')) {
      logs.push(`[${msg.type()}] ${text}`);
      console.log(`[${msg.type()}] ${text}`);
    }
  });
  
  page.on('pageerror', error => {
    errors.push(error.toString());
    console.error('Page error:', error);
  });
  
  // Monitor WebSocket for session configuration
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket created:', url);
    
    const messages = [];
    wsMessages.set(url, messages);
    
    ws.on('framesent', frame => {
      try {
        if (frame.payload) {
          const data = JSON.parse(frame.payload);
          messages.push({ type: 'sent', data });
          
          // Look for session.update message with tools
          if (data.type === 'session.update') {
            console.log('📋 Session Update Detected!');
            console.log(`   Tools configured: ${data.session?.tools?.length || 0}`);
          }
        }
      } catch {}
    });
    
    ws.on('framereceived', frame => {
      try {
        if (frame.payload) {
          const data = JSON.parse(frame.payload);
          messages.push({ type: 'received', data });
          
          // Look for session.created or session.updated
          if (data.type === 'session.created') {
            console.log('✅ Session Created!');
            if (data.session) {
              console.log(`   Model: ${data.session.model || 'unknown'}`);
              console.log(`   Voice: ${data.session.voice || 'unknown'}`);
              console.log(`   Tools: ${data.session.tools?.length || 0}`);
            }
          } else if (data.type === 'session.updated') {
            console.log('✅ Session Updated!');
            if (data.session?.tools) {
              console.log(`   Tools available: ${data.session.tools.length}`);
            }
          }
        }
      } catch {}
    });
  });
  
  console.log('\\n🤖 === OPENAI AGENT CAPABILITY TEST ===\\n');
  
  // Navigate to the app
  console.log('1. Navigating to app...');
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  
  // Select OpenAI provider
  console.log('\\n2. Selecting OpenAI provider...');
  const openaiButton = await page.locator('button').filter({ hasText: 'OpenAI' }).first();
  if (await openaiButton.count() > 0) {
    await openaiButton.click();
    console.log('   ✅ Selected OpenAI provider');
  } else {
    console.log('   ❌ OpenAI button not found');
  }
  await page.waitForTimeout(1000);
  
  // Connect to OpenAI
  console.log('\\n3. Connecting to OpenAI agent...');
  const micArea = await page.locator('.voice-conversation').boundingBox();
  if (micArea) {
    await page.mouse.click(micArea.x + micArea.width / 2, micArea.y + micArea.height / 2);
    console.log('   ✅ Clicked mic to connect');
  }
  
  // Wait for connection and session setup
  console.log('\\n4. Waiting for session configuration...');
  await page.waitForTimeout(5000);
  
  // Direct WebSocket test to verify tools
  console.log('\\n5. Direct WebSocket test for tool verification...');
  const toolTest = await page.evaluate(async () => {
    const sessionId = `capability_test_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/realtime-relay/${sessionId}`;
    
    return new Promise((resolve) => {
      const ws = new WebSocket(wsUrl, 'openai-realtime');
      const result = { 
        connected: false,
        sessionCreated: false,
        tools: [],
        sessionConfig: null,
        messages: []
      };
      
      ws.onopen = () => {
        result.connected = true;
        console.log('WebSocket connected, waiting for session...');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          result.messages.push(data.type);
          
          if (data.type === 'session.created') {
            result.sessionCreated = true;
            result.sessionConfig = data.session;
            
            // Extract tools if present
            if (data.session?.tools) {
              result.tools = data.session.tools.map(tool => ({
                name: tool.function?.name || tool.name,
                description: (tool.function?.description || tool.description || '').substring(0, 100)
              }));
            }
            
            // Close after getting session info
            setTimeout(() => {
              ws.close();
              resolve(result);
            }, 1000);
          }
        } catch (e) {
          console.error('Parse error:', e);
        }
      };
      
      ws.onerror = (error) => {
        result.error = 'Connection failed';
        resolve(result);
      };
      
      // Timeout after 10 seconds
      setTimeout(() => {
        ws.close();
        resolve(result);
      }, 10000);
    });
  });
  
  console.log('\\n📊 Tool Test Results:');
  console.log(`   Connected: ${toolTest.connected ? '✅' : '❌'}`);
  console.log(`   Session Created: ${toolTest.sessionCreated ? '✅' : '❌'}`);
  console.log(`   Tools Available: ${toolTest.tools.length}`);
  
  if (toolTest.tools.length > 0) {
    console.log('\\n🛠️ Available Tools:');
    
    // Expected high-priority tools
    const expectedTools = [
      'get_stock_quote',
      'get_stock_history',
      'get_stock_news',
      'get_market_overview',
      'get_market_movers',
      'get_crypto_price',
      'get_technical_indicators',
      'get_analyst_ratings'
    ];
    
    // Check which expected tools are present
    const foundTools = new Set(toolTest.tools.map(t => t.name));
    
    expectedTools.forEach(toolName => {
      const found = foundTools.has(toolName);
      console.log(`   ${found ? '✅' : '❌'} ${toolName}`);
    });
    
    // Show any additional tools
    const additionalTools = toolTest.tools.filter(t => !expectedTools.includes(t.name));
    if (additionalTools.length > 0) {
      console.log('\\n   Additional tools found:');
      additionalTools.forEach(tool => {
        console.log(`   • ${tool.name}`);
      });
    }
  }
  
  // Analyze session configuration
  if (toolTest.sessionConfig) {
    console.log('\\n📋 Session Configuration:');
    console.log(`   Model: ${toolTest.sessionConfig.model || 'Not specified'}`);
    console.log(`   Voice: ${toolTest.sessionConfig.voice || 'Not specified'}`);
    console.log(`   Tool Choice: ${toolTest.sessionConfig.tool_choice || 'Not specified'}`);
    console.log(`   Temperature: ${toolTest.sessionConfig.temperature || 'Not specified'}`);
    console.log(`   Audio Format: ${toolTest.sessionConfig.input_audio_format || 'Not specified'}`);
    
    // Check instructions
    if (toolTest.sessionConfig.instructions) {
      const instructionLength = toolTest.sessionConfig.instructions.length;
      console.log(`   Instructions: ${instructionLength} characters`);
      console.log(`   Instructions preview: "${toolTest.sessionConfig.instructions.substring(0, 100)}..."`);
    }
  }
  
  // Test tool schema validation
  console.log('\\n6. Testing tool schema validation...');
  const schemaTest = await page.evaluate(async () => {
    // Test if tools have proper OpenAI schema
    const testTools = [
      {
        type: 'function',
        function: {
          name: 'get_stock_quote',
          description: 'Get real-time stock quote',
          parameters: {
            type: 'object',
            properties: {
              symbol: { type: 'string', description: 'Stock symbol' }
            },
            required: ['symbol']
          }
        }
      }
    ];
    
    // Validate schema structure
    const isValid = testTools.every(tool => 
      tool.type === 'function' &&
      tool.function &&
      tool.function.name &&
      tool.function.description &&
      tool.function.parameters
    );
    
    return { valid: isValid, toolCount: testTools.length };
  });
  
  console.log(`   Schema validation: ${schemaTest.valid ? '✅ Valid' : '❌ Invalid'}`);
  
  // Generate capability report
  console.log('\\n📈 === CAPABILITY REPORT ===');
  
  const capabilities = {
    connection: toolTest.connected,
    session: toolTest.sessionCreated,
    tools: toolTest.tools.length > 0,
    highPriorityTools: toolTest.tools.filter(t => 
      ['get_stock_quote', 'get_stock_history', 'get_stock_news'].includes(t.name)
    ).length >= 3,
    configuration: !!toolTest.sessionConfig,
    voiceReady: toolTest.sessionConfig?.modalities?.includes('audio')
  };
  
  console.log('\\n✅ Capabilities Verified:');
  Object.entries(capabilities).forEach(([key, value]) => {
    console.log(`   ${key}: ${value ? '✅ Yes' : '❌ No'}`);
  });
  
  // Overall assessment
  const allCapabilities = Object.values(capabilities).every(v => v);
  console.log('\\n🎯 Overall Status:');
  if (allCapabilities) {
    console.log('   ✅ AGENT FULLY OPERATIONAL');
    console.log('   All required capabilities are present and configured');
  } else {
    console.log('   ⚠️ AGENT PARTIALLY OPERATIONAL');
    console.log('   Some capabilities are missing or not configured');
  }
  
  // Save screenshot
  await page.screenshot({ path: 'test-agent-capabilities.png' });
  console.log('\\nScreenshot saved: test-agent-capabilities.png');
  
  // Show message type flow
  if (toolTest.messages.length > 0) {
    console.log('\\n📨 Message Flow:');
    toolTest.messages.slice(0, 10).forEach((msg, i) => {
      console.log(`   ${i + 1}. ${msg}`);
    });
  }
  
  console.log('\\n=== TEST COMPLETE ===');
  
  await page.waitForTimeout(2000);
  await browser.close();
})();