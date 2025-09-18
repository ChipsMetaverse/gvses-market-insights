const { chromium } = require('playwright');

/**
 * Test OpenAI Agent Tool Execution
 * =================================
 * Tests whether the agent can actually execute tools despite
 * them not appearing in the session.created message.
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
  const toolCalls = [];
  const toolResults = [];
  
  page.on('console', msg => {
    const text = msg.text();
    if (!text.includes('contentScript.js') && !text.includes('[HMR]')) {
      logs.push(`[${msg.type()}] ${text}`);
      console.log(`[${msg.type()}] ${text}`);
      
      // Track tool calls
      if (text.includes('tool') || text.includes('Tool')) {
        if (text.includes('called')) {
          toolCalls.push(text);
        } else if (text.includes('result')) {
          toolResults.push(text);
        }
      }
    }
  });
  
  page.on('pageerror', error => {
    console.error('Page error:', error);
  });
  
  // Monitor WebSocket for tool-related messages
  page.on('websocket', ws => {
    const url = ws.url();
    console.log('🔌 WebSocket created:', url);
    
    ws.on('framesent', frame => {
      try {
        if (frame.payload) {
          const data = JSON.parse(frame.payload);
          
          // Look for user messages that might trigger tools
          if (data.type === 'conversation.item.create' && data.item?.content) {
            const text = data.item.content[0]?.text || '';
            if (text) {
              console.log(`📤 User message: "${text}"`);
            }
          }
        }
      } catch {}
    });
    
    ws.on('framereceived', frame => {
      try {
        if (frame.payload) {
          const data = JSON.parse(frame.payload);
          
          // Track tool-related events
          if (data.type === 'response.function_call_arguments.start') {
            console.log(`🛠️ Tool call starting: ${data.name}`);
            toolCalls.push({ type: 'start', name: data.name, callId: data.call_id });
          } else if (data.type === 'response.function_call_arguments.done') {
            console.log(`✅ Tool call complete: ${data.name}`);
            toolCalls.push({ type: 'done', name: data.name, arguments: data.arguments });
          } else if (data.type === 'tool_call_start') {
            console.log(`🔧 Backend tool execution: ${data.tool_name}`);
            toolCalls.push({ type: 'backend_start', name: data.tool_name });
          } else if (data.type === 'tool_call_complete') {
            console.log(`✅ Backend tool result: ${data.tool_name}`);
            toolResults.push({ name: data.tool_name, success: data.success });
          }
        }
      } catch {}
    });
  });
  
  console.log('\\n🔧 === OPENAI AGENT TOOL EXECUTION TEST ===\\n');
  
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
  }
  await page.waitForTimeout(1000);
  
  // Connect to OpenAI
  console.log('\\n3. Connecting to OpenAI agent...');
  const micArea = await page.locator('.voice-conversation').boundingBox();
  if (micArea) {
    await page.mouse.click(micArea.x + micArea.width / 2, micArea.y + micArea.height / 2);
    console.log('   ✅ Clicked mic to connect');
  }
  
  // Wait for connection
  await page.waitForTimeout(5000);
  
  // Test tool execution with text commands
  console.log('\\n4. Testing tool execution with text commands...');
  
  // Direct WebSocket test to send tool-triggering commands
  const toolTest = await page.evaluate(async () => {
    const sessionId = `tool_exec_test_${Date.now()}`;
    const wsUrl = `ws://localhost:8000/realtime-relay/${sessionId}`;
    
    return new Promise((resolve) => {
      const ws = new WebSocket(wsUrl, 'openai-realtime');
      const result = { 
        connected: false,
        toolCalls: [],
        responses: [],
        errors: []
      };
      
      let sessionReady = false;
      
      ws.onopen = () => {
        result.connected = true;
        console.log('Connected, waiting for session...');
      };
      
      ws.onmessage = async (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'session.created') {
            sessionReady = true;
            console.log('Session ready, sending test commands...');
            
            // Test commands that should trigger tools
            const testCommands = [
              "What is Tesla's current stock price?",
              "Show me Apple's stock history",
              "Get me the latest market news"
            ];
            
            for (const command of testCommands) {
              console.log(`Sending: "${command}"`);
              
              // Send user message
              const userMessage = {
                type: "conversation.item.create",
                item: {
                  type: "message",
                  role: "user",
                  content: [{
                    type: "input_text",
                    text: command
                  }]
                }
              };
              
              await ws.send(JSON.stringify(userMessage));
              
              // Trigger response
              await ws.send(JSON.stringify({ type: "response.create" }));
              
              // Wait for response
              await new Promise(r => setTimeout(r, 3000));
            }
            
            // Wait for all responses
            setTimeout(() => {
              ws.close();
              resolve(result);
            }, 10000);
          }
          
          // Track tool-related events
          if (data.type && data.type.includes('function_call')) {
            result.toolCalls.push({
              type: data.type,
              name: data.name || data.function_name,
              callId: data.call_id
            });
          } else if (data.type === 'tool_call_start' || data.type === 'tool_call_complete') {
            result.toolCalls.push({
              type: data.type,
              name: data.tool_name,
              success: data.success
            });
          } else if (data.type === 'response.audio_transcript.done') {
            result.responses.push(data.transcript);
          } else if (data.type === 'error') {
            result.errors.push(data.error);
          }
          
        } catch (e) {
          console.error('Parse error:', e);
        }
      };
      
      ws.onerror = (error) => {
        result.errors.push('WebSocket error');
        resolve(result);
      };
      
      // Timeout after 20 seconds
      setTimeout(() => {
        ws.close();
        resolve(result);
      }, 20000);
    });
  });
  
  console.log('\\n📊 Tool Execution Test Results:');
  console.log(`   Connected: ${toolTest.connected ? '✅' : '❌'}`);
  console.log(`   Tool Calls: ${toolTest.toolCalls.length}`);
  console.log(`   Responses: ${toolTest.responses.length}`);
  console.log(`   Errors: ${toolTest.errors.length}`);
  
  if (toolTest.toolCalls.length > 0) {
    console.log('\\n🛠️ Tool Calls Made:');
    const toolCallSummary = {};
    toolTest.toolCalls.forEach(call => {
      const name = call.name || 'unknown';
      toolCallSummary[name] = (toolCallSummary[name] || 0) + 1;
      console.log(`   - ${call.type}: ${name}`);
    });
    
    console.log('\\n📈 Tool Call Summary:');
    Object.entries(toolCallSummary).forEach(([tool, count]) => {
      console.log(`   ${tool}: ${count} calls`);
    });
  }
  
  if (toolTest.responses.length > 0) {
    console.log('\\n💬 Agent Responses:');
    toolTest.responses.forEach((response, i) => {
      console.log(`   ${i + 1}. "${response.substring(0, 100)}..."`);
    });
  }
  
  if (toolTest.errors.length > 0) {
    console.log('\\n❌ Errors:');
    toolTest.errors.forEach(error => {
      console.log(`   - ${JSON.stringify(error)}`);
    });
  }
  
  // Analyze tool execution capability
  console.log('\\n🎯 === CAPABILITY ASSESSMENT ===');
  
  const capabilities = {
    connected: toolTest.connected,
    toolsTriggered: toolTest.toolCalls.length > 0,
    toolsExecuted: toolTest.toolCalls.some(c => c.type === 'tool_call_complete'),
    responsesGenerated: toolTest.responses.length > 0,
    noErrors: toolTest.errors.length === 0
  };
  
  console.log('\\n✅ Tool Execution Capabilities:');
  Object.entries(capabilities).forEach(([key, value]) => {
    console.log(`   ${key}: ${value ? '✅ Yes' : '❌ No'}`);
  });
  
  // Overall assessment
  const canExecuteTools = capabilities.toolsTriggered || capabilities.toolsExecuted;
  console.log('\\n🎯 Overall Status:');
  if (canExecuteTools) {
    console.log('   ✅ AGENT CAN EXECUTE TOOLS');
    console.log('   Despite tools not showing in session.created, the agent can call them');
  } else {
    console.log('   ❌ AGENT CANNOT EXECUTE TOOLS');
    console.log('   The agent is not calling tools when given commands');
  }
  
  // Save screenshot
  await page.screenshot({ path: 'test-agent-tool-execution.png' });
  console.log('\\nScreenshot saved: test-agent-tool-execution.png');
  
  // Show tool call logs from page
  if (toolCalls.length > 0) {
    console.log('\\n📝 Page Tool Logs:');
    toolCalls.forEach(log => console.log(`   ${log}`));
  }
  
  console.log('\\n=== TEST COMPLETE ===');
  
  await page.waitForTimeout(2000);
  await browser.close();
})();