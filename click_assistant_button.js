const { execSync } = require('child_process');

console.log('🎯 Opening Comet Assistant Side Panel...\n');

// Method 1: Use the keyboard shortcut (most reliable)
console.log('Method 1: Using Cmd+A shortcut...');
try {
  const script = `
    tell application "Comet"
      activate
    end tell
    delay 0.5
    tell application "System Events"
      tell process "Comet"
        keystroke "a" using {command down}
      end tell
    end tell
  `;
  
  execSync(`osascript -e '${script}'`);
  console.log('✅ Sent Cmd+A to toggle Assistant side panel\n');
  
  // Give it a moment to open
  execSync('sleep 1');
  
} catch (error) {
  console.log('❌ Keyboard shortcut failed\n');
}

// Method 2: Try to click the button directly
console.log('Method 2: Clicking Assistant button in UI...');
try {
  const script = `
    tell application "System Events"
      tell process "Comet"
        set frontmost to true
        delay 0.5
        
        -- Try to find and click the Assistant button
        try
          click (first button whose description contains "Assistant")
        on error
          try
            -- Look for button with "Assistant" in name
            click (first button whose name contains "Assistant")
          on error
            -- Look in toolbar
            click button "Assistant" of group 1 of window 1
          end try
        end try
      end tell
    end tell
  `;
  
  execSync(`osascript -e '${script.replace(/'/g, "\\'")}'`);
  console.log('✅ Clicked Assistant button\n');
  
} catch (error) {
  console.log('⚠️  Direct button click failed (this is ok if Cmd+A worked)\n');
}

console.log('✅ Done!');
console.log('\n📱 Check your Comet window:');
console.log('   The Assistant side panel should now be visible on the right');
console.log('   You should see the Assistant interface ready for input\n');

