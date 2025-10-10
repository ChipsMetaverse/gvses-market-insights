const { execSync } = require('child_process');

console.log('🎯 Clicking Comet Assistant button...');

// Use AppleScript to click the Assistant button in the UI
const script = `
tell application "System Events"
  tell process "Comet"
    set frontmost to true
    delay 0.5
    
    -- Try to click the Assistant button in the toolbar
    try
      click button "Assistant" of group 1 of toolbar 1 of window 1
      log "Clicked Assistant button"
    on error
      -- If that doesn't work, try clicking by position (top right area)
      tell window 1
        set {x, y, width, height} to {position, size}
        set clickX to (item 1 of x) + width - 100
        set clickY to (item 2 of y) + 60
      end tell
      
      do shell script "cliclick c:" & clickX & "," & clickY
      log "Clicked by position"
    end try
  end tell
end tell
`;

try {
  execSync(`osascript -e '${script.replace(/'/g, "'\\''")}'`);
  console.log('✅ Attempted to click Assistant button');
  console.log('💡 Check Comet window - Assistant panel should appear');
} catch (error) {
  console.log('⚠️  Direct click failed, trying alternative method...');
  
  // Alternative: Use cliclick if available
  try {
    console.log('Installing cliclick if needed (brew install cliclick)...');
    // Click in the top-right area where Assistant button is
    execSync('cliclick c:1300,60 2>/dev/null || echo "cliclick not available"');
  } catch (e) {
    console.log('❌ Please click the Assistant button manually in Comet');
    console.log('   It\'s in the top-right corner of the window');
  }
}

