#!/usr/bin/env node

/**
 * Navigate using Comet Assistant and keep it open
 * Handles the Assistant panel closing after navigation
 */

const { execSync } = require('child_process');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function navigateWithAssistant(url, reopenDelay = 3000) {
  console.log(`🚀 Navigating to: ${url}\n`);
  
  // Step 1: Open Assistant if not already open
  console.log('Step 1: Opening Assistant panel...');
  execSync(`osascript << 'EOF'
tell application "Comet" to activate
delay 0.5

tell application "System Events"
    tell process "Comet"
        set windowPosition to position of window 1
        set windowSize to size of window 1
        set windowX to item 1 of windowPosition
        set windowY to item 2 of windowPosition
        set windowWidth to item 1 of windowSize
        
        set clickX to windowX + windowWidth - 100
        set clickY to windowY + 66
        
        do shell script "cliclick c:" & clickX & "," & clickY
    end tell
end tell
EOF`);
  console.log('✅ Assistant opened\n');
  
  await sleep(1000);
  
  // Step 2: Send navigation command
  console.log(`Step 2: Sending navigation command...`);
  execSync(`osascript << 'EOF'
tell application "System Events"
    tell process "Comet"
        set frontmost to true
        delay 0.3
        
        keystroke "Navigate to @${url}"
        delay 0.5
        keystroke return
    end tell
end tell
EOF`);
  console.log('✅ Navigation command sent\n');
  
  // Step 3: Wait for page to load
  console.log(`Step 3: Waiting ${reopenDelay/1000}s for page to load...`);
  await sleep(reopenDelay);
  
  // Step 4: Reopen Assistant panel (it closes after navigation)
  console.log('Step 4: Reopening Assistant panel...');
  execSync(`osascript << 'EOF'
tell application "System Events"
    tell process "Comet"
        set frontmost to true
        delay 0.5
        
        set windowPosition to position of window 1
        set windowSize to size of window 1
        set windowX to item 1 of windowPosition
        set windowY to item 2 of windowPosition
        set windowWidth to item 1 of windowSize
        
        set clickX to windowX + windowWidth - 100
        set clickY to windowY + 66
        
        do shell script "cliclick c:" & clickX & "," & clickY
    end tell
end tell
EOF`);
  console.log('✅ Assistant reopened\n');
  
  console.log('🎉 Navigation complete with Assistant ready!');
  console.log(`📍 Current page: ${url}`);
  console.log('💬 Assistant panel is open and ready for commands\n');
}

async function sendMessageToAssistant(message, pressEnter = true) {
  console.log(`💬 Sending message: "${message}"\n`);
  
  const script = pressEnter 
    ? `keystroke "${message.replace(/"/g, '\\"')}"\ndelay 0.5\nkeystroke return`
    : `keystroke "${message.replace(/"/g, '\\"')}"`;
  
  execSync(`osascript << 'EOF'
tell application "System Events"
    tell process "Comet"
        set frontmost to true
        delay 0.3
        ${script}
    end tell
end tell
EOF`);
  
  console.log('✅ Message sent\n');
}

// CLI
const args = process.argv.slice(2);
const command = args[0];

(async () => {
  if (command === 'navigate') {
    const url = args[1];
    if (!url) {
      console.log('❌ Usage: node comet_navigate_with_assistant.js navigate <url>');
      process.exit(1);
    }
    await navigateWithAssistant(url);
    
  } else if (command === 'message') {
    const message = args.slice(1).join(' ');
    if (!message) {
      console.log('❌ Usage: node comet_navigate_with_assistant.js message <text>');
      process.exit(1);
    }
    await sendMessageToAssistant(message);
    
  } else {
    console.log('🎯 Comet Assistant Navigation Tool\n');
    console.log('Usage:');
    console.log('  node comet_navigate_with_assistant.js navigate <url>');
    console.log('  node comet_navigate_with_assistant.js message <text>\n');
    console.log('Examples:');
    console.log('  node comet_navigate_with_assistant.js navigate https://platform.openai.com/agent-builder');
    console.log('  node comet_navigate_with_assistant.js message "Summarize this page"');
  }
})();

module.exports = { navigateWithAssistant, sendMessageToAssistant };

