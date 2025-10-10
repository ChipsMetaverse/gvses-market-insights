const { execSync } = require('child_process');

// Pure AppleScript control - NO automation flags, 100% native features
class CometController {
  constructor() {
    this.appName = 'Comet';
  }
  
  // Launch Comet natively
  launch() {
    console.log('🚀 Launching Comet natively...');
    const script = `
      tell application "${this.appName}"
        activate
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ Comet launched');
  }
  
  // Send text to the Assistant
  sendToAssistant(text) {
    console.log(`💬 Sending to Assistant: "${text}"`);
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          keystroke "${this.escapeText(text)}"
          delay 0.5
          keystroke return
        end tell
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ Message sent');
  }
  
  // Open Assistant with Cmd+A
  toggleAssistant() {
    console.log('🎯 Toggling Assistant...');
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          keystroke "a" using {command down}
        end tell
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ Assistant toggled');
  }
  
  // Summarize page with Cmd+S
  summarizePage() {
    console.log('📄 Summarizing page...');
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          keystroke "s" using {command down}
        end tell
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ Summarization requested');
  }
  
  // Open new tab
  newTab() {
    console.log('🆕 Opening new tab...');
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          keystroke "t" using {command down}
        end tell
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ New tab opened');
  }
  
  // Navigate to URL
  navigateTo(url) {
    console.log(`🌐 Navigating to: ${url}`);
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          keystroke "l" using {command down}
          delay 0.3
          keystroke "${this.escapeText(url)}"
          delay 0.3
          keystroke return
        end tell
      end tell
    `;
    this.runAppleScript(script);
    console.log('✅ Navigation initiated');
  }
  
  // Take screenshot using macOS screencapture
  screenshot(filename = 'comet_screenshot.png') {
    console.log(`📸 Taking screenshot: ${filename}`);
    const script = `
      tell application "${this.appName}"
        activate
      end tell
      delay 0.5
      do shell script "screencapture -l$(osascript -e 'tell app \\"${this.appName}\\" to id of window 1') ${filename}"
    `;
    try {
      this.runAppleScript(script);
      console.log(`✅ Screenshot saved: ${filename}`);
    } catch (error) {
      console.log('⚠️  Screenshot failed, using full screen capture');
      execSync(`screencapture -w ${filename}`);
    }
  }
  
  // Get window info
  getWindowInfo() {
    const script = `
      tell application "System Events"
        tell process "${this.appName}"
          set frontmost to true
          return name of windows
        end tell
      end tell
    `;
    const result = this.runAppleScript(script);
    return result.trim();
  }
  
  // Check if Comet is running
  isRunning() {
    const script = `
      tell application "System Events"
        return (name of processes) contains "${this.appName}"
      end tell
    `;
    const result = this.runAppleScript(script);
    return result.trim() === 'true';
  }
  
  // Helper methods
  runAppleScript(script) {
    try {
      return execSync(`osascript -e '${script}'`, { encoding: 'utf8' });
    } catch (error) {
      console.error('❌ AppleScript error:', error.message);
      throw error;
    }
  }
  
  escapeText(text) {
    return text.replace(/["\\]/g, '\\$&').replace(/\n/g, '\\n');
  }
  
  wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Demo usage
(async () => {
  const comet = new CometController();
  
  console.log('🎮 Comet Native Controller');
  console.log('📱 100% Native Features Preserved\n');
  
  // Check if running
  if (!comet.isRunning()) {
    comet.launch();
    await comet.wait(3000);
  } else {
    console.log('✅ Comet already running');
  }
  
  console.log('\n📋 Window Info:', comet.getWindowInfo());
  
  // Example automation sequence
  const runDemo = process.argv.includes('--demo');
  
  if (runDemo) {
    console.log('\n🎬 Running demo sequence...\n');
    
    await comet.wait(1000);
    comet.newTab();
    
    await comet.wait(1000);
    comet.navigateTo('localhost:5175');
    
    await comet.wait(3000);
    comet.screenshot('trading_dashboard.png');
    
    await comet.wait(1000);
    comet.toggleAssistant();
    
    await comet.wait(1000);
    comet.sendToAssistant('What stocks are shown on this dashboard?');
    
    await comet.wait(5000);
    comet.screenshot('assistant_response.png');
    
    console.log('\n✅ Demo complete!');
  } else {
    console.log('\n💡 Usage:');
    console.log('  node comet_applescript_control.js --demo');
    console.log('\n📚 Or use programmatically:');
    console.log('  const { CometController } = require("./comet_applescript_control.js");');
    console.log('  const comet = new CometController();');
    console.log('  comet.toggleAssistant();');
    console.log('  comet.sendToAssistant("Hello!");');
  }
})();

module.exports = { CometController };

