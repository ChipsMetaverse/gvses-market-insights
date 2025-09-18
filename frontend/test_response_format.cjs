const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('🔍 Testing Response Formatting\n');
  console.log('=' .repeat(60));
  
  await page.goto('http://localhost:5174', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  
  // Step 1: Check if Voice Assistant panel exists
  console.log('\n📊 STEP 1: Locating Voice Assistant Panel');
  const voicePanel = await page.$('.voice-conversation-section');
  if (voicePanel) {
    console.log('✅ Voice Assistant panel found');
  } else {
    console.log('❌ Voice Assistant panel NOT found');
    await browser.close();
    return;
  }
  
  // Step 2: Connect to Voice Assistant (click FAB)
  console.log('\n🔌 STEP 2: Connecting to Voice Assistant');
  const fab = await page.$('.voice-fab');
  if (fab) {
    console.log('Found FAB button, clicking to connect...');
    await fab.click();
    await page.waitForTimeout(3000); // Wait for connection
    
    // Check if connected
    const isActive = await fab.evaluate(el => el.classList.contains('active'));
    if (isActive) {
      console.log('✅ Successfully connected to Voice Assistant');
    } else {
      console.log('⚠️  Connection might have failed, continuing anyway...');
    }
  }
  
  // Step 3: Send a test query about Tesla
  console.log('\n📝 STEP 3: Sending Test Query');
  const textInput = await page.$('.voice-text-input');
  const sendButton = await page.$('.voice-send-button');
  
  if (textInput && sendButton) {
    const testQuery = "Give me a full analysis of Tesla with all technical levels and news";
    console.log(`Query: "${testQuery}"`);
    
    await textInput.fill(testQuery);
    await page.waitForTimeout(500);
    await sendButton.click();
    console.log('✅ Message sent');
    
    // Wait for response (longer timeout for API calls and backend agent)
    console.log('⏳ Waiting for responses (including backend agent)...');
    await page.waitForTimeout(12000);
  } else {
    console.log('❌ Could not find text input or send button');
  }
  
  // Step 4: Analyze the response structure
  console.log('\n📋 STEP 4: Analyzing Response Structure');
  
  // Get all messages
  const messages = await page.$$('.conversation-message-enhanced');
  console.log(`Total messages: ${messages.length}`);
  
  // Check all assistant messages to find the formatted one
  if (messages.length > 0) {
    let assistantResponse = null;
    let formattedFound = false;
    
    // Check all assistant messages for the best formatted one
    for (let i = messages.length - 1; i >= 0; i--) {
      const messageRole = await messages[i].$eval('.message-avatar', el => el.textContent);
      if (messageRole === '🤖') {
        const structuredEl = await messages[i].$('.structured-response');
        if (structuredEl) {
          const content = await structuredEl.textContent();
          // Look for formatted content with tables or market snapshot
          if (content.includes('Market Snapshot') || content.includes('HERE\'S YOUR')) {
            assistantResponse = messages[i];
            formattedFound = true;
            console.log('✅ Found formatted response at message index:', i);
            break;
          } else if (!assistantResponse) {
            // Keep the first assistant message as fallback
            assistantResponse = messages[i];
          }
        }
      }
    }
    
    if (assistantResponse) {
      console.log('\n✅ Found assistant response, analyzing structure...\n');
      
      // Check for structured response container
      const structuredResponse = await assistantResponse.$('.structured-response');
      if (structuredResponse) {
        console.log('✅ Structured response container found');
        
        // Check for key formatting elements
        const checks = {
          'Price Highlight': '.price-highlight',
          'H1 Headers': '.response-h1',
          'H2 Headers': '.response-h2',
          'H3 Headers': '.response-h3',
          'Tables': '.market-data-table',
          'Table Headers': '.table-header-cell',
          'Lists': '.response-list',
          'List Items': '.response-list-item',
          'Paragraphs': '.response-paragraph',
          'Bold Text': '.response-bold',
          'Percentage Changes': '.percentage-change',
          'Positive Changes': '.percentage-change.positive',
          'Negative Changes': '.percentage-change.negative',
          'Dividers': '.response-divider',
          'Sources': '.response-source',
          'Quotes': '.response-quote'
        };
        
        console.log('Checking formatting elements:');
        console.log('-'.repeat(40));
        
        for (const [name, selector] of Object.entries(checks)) {
          const elements = await structuredResponse.$$(selector);
          const status = elements.length > 0 ? '✅' : '❌';
          console.log(`${status} ${name}: ${elements.length} found`);
          
          // Show sample content for some key elements
          if (elements.length > 0) {
            if (selector === '.price-highlight') {
              const price = await elements[0].textContent();
              console.log(`   → Price displayed: ${price}`);
            }
            if (selector === '.response-h1' || selector === '.response-h2') {
              const heading = await elements[0].textContent();
              console.log(`   → Heading: "${heading}"`);
            }
            if (selector === '.percentage-change') {
              const change = await elements[0].textContent();
              console.log(`   → Change: ${change}`);
            }
          }
        }
        
        // Get the full text content to check overall structure
        const fullContent = await structuredResponse.textContent();
        
        console.log('\n📄 Content Analysis:');
        console.log('-'.repeat(40));
        
        // Check for key content patterns
        const contentChecks = {
          'Real-time snapshot': fullContent.includes('snapshot') || fullContent.includes('Snapshot'),
          'Price with $': fullContent.match(/\$[\d,]+\.?\d*/),
          'Percentage with %': fullContent.match(/[+-]?\d+\.?\d*%/),
          'Market Snapshot section': fullContent.includes('Market Snapshot'),
          'Key Headlines': fullContent.includes('Headlines') || fullContent.includes('headlines'),
          'Technical Overview': fullContent.includes('Technical') || fullContent.includes('technical'),
          'Summary Table': fullContent.includes('Summary') || fullContent.includes('Category'),
          'Strategic Insights': fullContent.includes('Strategic') || fullContent.includes('Insights'),
          'Volume data': fullContent.includes('Volume') || fullContent.includes('volume'),
          'Moving Averages': fullContent.includes('MA') || fullContent.includes('Moving Average')
        };
        
        for (const [check, found] of Object.entries(contentChecks)) {
          console.log(`${found ? '✅' : '❌'} ${check}`);
        }
        
        // Check CSS styling
        console.log('\n🎨 Style Analysis:');
        console.log('-'.repeat(40));
        
        const styles = await structuredResponse.evaluate(el => {
          const computed = window.getComputedStyle(el);
          return {
            background: computed.backgroundColor,
            color: computed.color,
            padding: computed.padding,
            borderRadius: computed.borderRadius,
            fontFamily: computed.fontFamily
          };
        });
        
        console.log('Container styles:');
        console.log(`  Background: ${styles.background}`);
        console.log(`  Text color: ${styles.color}`);
        console.log(`  Padding: ${styles.padding}`);
        console.log(`  Border radius: ${styles.borderRadius}`);
        
        // Check for dark theme
        const isDarkTheme = styles.background.includes('26, 26, 26') || 
                           styles.background.includes('rgb(26') ||
                           styles.background.includes('#1a1a1a');
        console.log(`\n${isDarkTheme ? '✅' : '❌'} Dark theme detected`);
        
      } else {
        console.log('❌ No structured response container found');
        
        // Check if there's any response at all
        const messageContent = await assistantResponse.$('.message-text-enhanced');
        if (messageContent) {
          const text = await messageContent.textContent();
          console.log('\nRaw message content (first 200 chars):');
          console.log(text.substring(0, 200) + '...');
        }
      }
    } else {
      console.log('❌ No assistant response found');
    }
  }
  
  // Step 5: Take screenshots for visual comparison
  console.log('\n📸 STEP 5: Capturing Screenshots');
  
  // Full page screenshot
  await page.screenshot({ 
    path: 'frontend/response-format-test-full.png', 
    fullPage: true 
  });
  console.log('✅ Full page: response-format-test-full.png');
  
  // Voice panel only
  if (voicePanel) {
    await voicePanel.screenshot({ 
      path: 'frontend/response-format-test-panel.png' 
    });
    console.log('✅ Voice panel: response-format-test-panel.png');
  }
  
  // Try another simpler query
  console.log('\n📝 STEP 6: Testing Simple Price Query');
  if (textInput && sendButton) {
    await textInput.fill("What's the price of Apple?");
    await page.waitForTimeout(500);
    await sendButton.click();
    console.log('✅ Simple query sent');
    
    await page.waitForTimeout(5000);
    
    // Take another screenshot
    await page.screenshot({ 
      path: 'frontend/response-format-test-simple.png', 
      fullPage: false 
    });
    console.log('✅ Simple query screenshot: response-format-test-simple.png');
  }
  
  console.log('\n' + '=' .repeat(60));
  console.log('📊 TEST SUMMARY');
  console.log('=' .repeat(60));
  console.log('\nCompare the screenshots with the ideal format in:');
  console.log('/Volumes/WD My Passport 264F Media/claude-voice-mcp/idealresponseformat/');
  console.log('\nKey things to verify:');
  console.log('1. Dark theme background (#1a1a1a)');
  console.log('2. Large price display (32px font)');
  console.log('3. Tables with proper styling');
  console.log('4. Bullet points with blue markers');
  console.log('5. Section headers with underlines');
  console.log('6. Color-coded percentage changes');
  console.log('=' .repeat(60));
  
  await page.waitForTimeout(5000);
  await browser.close();
})();