const playwright = require('playwright');

async function testAgentChatFunctionality() {
  console.log('🤖 AGENT CHAT FUNCTIONALITY TEST');
  console.log('='.repeat(60));
  console.log('Testing AI agent responses and chat interface');
  
  const browser = await playwright.chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1600, height: 1000 }
  });
  const page = await context.newPage();

  // Track chat-specific logs and responses
  const chatLogs = [];
  const aiResponses = [];
  const audioEvents = [];
  const errors = [];

  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    
    console.log(`[${type.toUpperCase()}] ${text}`);
    
    // Track chat-specific messages
    if (text.includes('AI') || text.includes('agent') || text.includes('response') || 
        text.includes('message') || text.includes('conversation') || text.includes('transcript')) {
      chatLogs.push({ type, text, time: new Date().toISOString() });
    }
    
    // Track audio events
    if (text.includes('audio') || text.includes('Audio') || text.includes('playing') || text.includes('stream')) {
      audioEvents.push({ type, text, time: new Date().toISOString() });
    }
    
    if (type === 'error') {
      errors.push({ text, time: new Date().toISOString() });
    }
  });

  try {
    console.log('\n📍 PHASE 1: SETUP AND CONNECTION');
    
    await page.goto('http://localhost:5175');
    await page.waitForTimeout(3000);
    
    // Navigate to voice tab
    await page.click('[data-testid="voice-tab"]');
    await page.waitForTimeout(1000);
    
    console.log('✅ Navigated to voice interface');
    
    // Connect to OpenAI
    console.log('\n🔌 Connecting to OpenAI...');
    await page.click('.toggle-switch-container');
    await page.waitForTimeout(8000); // Give time for connection
    
    const connectionState = await page.evaluate(() => {
      const toggle = document.querySelector('[data-testid="connection-toggle"]');
      const status = document.querySelector('.toggle-label')?.textContent;
      return {
        connected: toggle?.checked || false,
        status: status?.trim()
      };
    });
    
    console.log(`Connection Status: ${connectionState.connected ? '✅ CONNECTED' : '❌ FAILED'} (${connectionState.status})`);
    
    if (!connectionState.connected) {
      console.log('❌ Cannot proceed with chat tests - connection failed');
      await page.screenshot({ path: 'agent-chat-connection-failed.png' });
      return;
    }
    
    console.log('\n📍 PHASE 2: INVESTOR-FOCUSED CHAT TESTS');
    
    const investorQueries = [
      {
        query: "What's the current price of Tesla stock?",
        expectedType: "stock_price",
        description: "Basic stock price query"
      },
      {
        query: "Should I buy Apple stock right now?",
        expectedType: "investment_advice", 
        description: "Investment advice request"
      },
      {
        query: "What are the top performing stocks today?",
        expectedType: "market_overview",
        description: "Market performance query"
      },
      {
        query: "Show me Tesla's chart",
        expectedType: "chart_command",
        description: "Chart visualization request"
      }
    ];
    
    for (let i = 0; i < investorQueries.length; i++) {
      const test = investorQueries[i];
      console.log(`\n💬 Test ${i + 1}: ${test.description}`);
      console.log(`Query: "${test.query}"`);
      
      // Clear any previous responses
      const preTestLogs = chatLogs.length;
      const preTestAudio = audioEvents.length;
      
      // Send message
      const messageInput = page.locator('[data-testid="message-input"]');
      await messageInput.fill(test.query);
      await page.waitForTimeout(500);
      
      const sendButton = page.locator('[data-testid="send-button"]');
      if (await sendButton.isEnabled()) {
        await sendButton.click();
        console.log('📤 Message sent successfully');
        
        // Wait for AI response with longer timeout for processing
        console.log('⏱️ Waiting for AI response (15 seconds)...');
        await page.waitForTimeout(15000);
        
        // Check for response indicators
        const responseData = await page.evaluate(() => {
          // Look for any new content that might indicate AI response
          const conversationArea = document.querySelector('.conversation-area, .chat-area, .messages');
          const messageElements = document.querySelectorAll('.message, .ai-message, .assistant-message');
          const audioElements = document.querySelectorAll('audio, [class*="audio"]');
          const statusIndicators = document.querySelectorAll('[class*="typing"], [class*="thinking"], [class*="responding"]');
          
          return {
            conversationAreaExists: !!conversationArea,
            messageCount: messageElements.length,
            audioElementCount: audioElements.length,
            statusIndicatorCount: statusIndicators.length,
            inputCleared: document.querySelector('[data-testid="message-input"]')?.value === '',
            pageTitle: document.title,
            // Check for chart updates (for chart commands)
            chartTitle: document.querySelector('.chart-header h3')?.textContent
          };
        });
        
        // Analyze new logs since message sent
        const newChatLogs = chatLogs.slice(preTestLogs);
        const newAudioEvents = audioEvents.slice(preTestAudio);
        
        console.log('\n📊 Response Analysis:');
        console.log(`• Input Cleared: ${responseData.inputCleared ? '✅' : '❌'}`);
        console.log(`• New Chat Logs: ${newChatLogs.length}`);
        console.log(`• New Audio Events: ${newAudioEvents.length}`);
        console.log(`• Message Elements: ${responseData.messageCount}`);
        console.log(`• Audio Elements: ${responseData.audioElementCount}`);
        console.log(`• Status Indicators: ${responseData.statusIndicatorCount}`);
        
        if (test.expectedType === 'chart_command' && responseData.chartTitle) {
          console.log(`• Chart Updated: ${responseData.chartTitle}`);
        }
        
        // Show recent chat logs
        if (newChatLogs.length > 0) {
          console.log('\n📝 Recent AI Activity:');
          newChatLogs.slice(-5).forEach((log, idx) => {
            console.log(`  ${idx + 1}. [${log.type}] ${log.text.substring(0, 100)}...`);
          });
        }
        
        if (newAudioEvents.length > 0) {
          console.log('\n🔊 Audio Activity:');
          newAudioEvents.slice(-3).forEach((event, idx) => {
            console.log(`  ${idx + 1}. [${event.type}] ${event.text.substring(0, 80)}...`);
          });
        }
        
        // Determine if response was successful
        const responseSuccess = responseData.inputCleared && 
                               (newChatLogs.length > 0 || newAudioEvents.length > 0 || 
                                responseData.messageCount > 0 || responseData.audioElementCount > 0);
        
        console.log(`\n🎯 Response Status: ${responseSuccess ? '✅ SUCCESS' : '❌ NO CLEAR RESPONSE'}`);
        
        if (responseSuccess) {
          aiResponses.push({
            query: test.query,
            type: test.expectedType,
            success: true,
            chatLogs: newChatLogs.length,
            audioEvents: newAudioEvents.length,
            timestamp: new Date().toISOString()
          });
        } else {
          aiResponses.push({
            query: test.query,
            type: test.expectedType,
            success: false,
            reason: 'No clear response indicators',
            timestamp: new Date().toISOString()
          });
        }
        
      } else {
        console.log('❌ Send button not enabled');
      }
      
      // Brief pause between queries
      await page.waitForTimeout(3000);
    }
    
    console.log('\n📍 PHASE 3: VOICE INTERACTION TEST');
    
    // Test voice activation if available
    const micButton = page.locator('[data-testid="mic-button"], .mic-button, [class*="mic"]');
    const micExists = await micButton.count() > 0;
    
    if (micExists) {
      console.log('🎤 Testing voice interaction...');
      try {
        await micButton.click();
        await page.waitForTimeout(2000);
        console.log('✅ Mic button activated');
      } catch (err) {
        console.log('⚠️ Mic interaction failed:', err.message);
      }
    } else {
      console.log('ℹ️ No microphone button found - text-only mode');
    }
    
    await page.screenshot({ path: 'agent-chat-functionality-test.png', fullPage: true });
    
    console.log('\n📍 PHASE 4: COMPREHENSIVE ANALYSIS');
    
    const totalQueries = investorQueries.length;
    const successfulResponses = aiResponses.filter(r => r.success).length;
    const successRate = (successfulResponses / totalQueries) * 100;
    
    console.log('\n🎯 AGENT CHAT ANALYSIS SUMMARY:');
    console.log('='.repeat(60));
    
    console.log(`\n📊 PERFORMANCE METRICS:`);
    console.log(`• Total Queries Tested: ${totalQueries}`);
    console.log(`• Successful Responses: ${successfulResponses}`);
    console.log(`• Success Rate: ${successRate.toFixed(1)}%`);
    console.log(`• Total Chat Logs: ${chatLogs.length}`);
    console.log(`• Total Audio Events: ${audioEvents.length}`);
    console.log(`• JavaScript Errors: ${errors.length}`);
    
    console.log('\n📝 QUERY BREAKDOWN:');
    aiResponses.forEach((response, i) => {
      const status = response.success ? '✅' : '❌';
      console.log(`${i + 1}. ${status} "${response.query}"`);
      if (response.success) {
        console.log(`   → Chat logs: ${response.chatLogs}, Audio events: ${response.audioEvents}`);
      } else {
        console.log(`   → ${response.reason}`);
      }
    });
    
    if (errors.length > 0) {
      console.log('\n⚠️ ERRORS DETECTED:');
      errors.forEach((error, i) => {
        console.log(`${i + 1}. ${error.text}`);
      });
    }
    
    // Overall assessment
    let overallRating;
    if (successRate >= 75) {
      overallRating = 'EXCELLENT - Agent is highly responsive';
    } else if (successRate >= 50) {
      overallRating = 'GOOD - Agent responds to most queries';  
    } else if (successRate >= 25) {
      overallRating = 'FAIR - Agent has mixed response rate';
    } else {
      overallRating = 'NEEDS IMPROVEMENT - Agent rarely responds clearly';
    }
    
    console.log(`\n🏆 OVERALL AGENT CHAT RATING: ${overallRating}`);
    
    console.log('\n📈 INVESTOR EXPERIENCE ASSESSMENT:');
    
    if (successRate >= 75) {
      console.log('💡 EXCELLENT for investors/traders:');
      console.log('   ✅ AI provides reliable market insights');
      console.log('   ✅ Natural language queries work well');
      console.log('   ✅ Real-time responses to market questions');
      console.log('   ✅ Professional-grade AI assistance');
    } else if (successRate >= 50) {
      console.log('👍 GOOD for investors with some limitations:');
      console.log('   ✅ Basic market queries work');
      console.log('   ⚠️ Some response clarity issues');
      console.log('   💡 Consider improving response visibility');
    } else {
      console.log('⚠️ NEEDS WORK for professional use:');
      console.log('   ❌ Response mechanism needs improvement');
      console.log('   ❌ Users may not realize AI is responding');
      console.log('   🛠️ Focus on response UI/UX improvements');
    }
    
    console.log('\n🔍 SPECIFIC RECOMMENDATIONS:');
    
    if (audioEvents.length > chatLogs.length) {
      console.log('• AI is responding via audio - consider adding visual transcripts');
    }
    
    if (chatLogs.length > 0 && successfulResponses < totalQueries) {
      console.log('• AI is active but response indicators need improvement');
    }
    
    if (errors.length > 0) {
      console.log('• Fix JavaScript errors to improve chat reliability');
    }
    
    console.log('\n🔍 Browser kept open for manual review...');
    await new Promise(() => {}); // Keep open for inspection
    
  } catch (error) {
    console.error('❌ Agent Chat Test Error:', error.message);
    await page.screenshot({ path: 'agent-chat-test-error.png' });
  }
}

testAgentChatFunctionality().catch(console.error);