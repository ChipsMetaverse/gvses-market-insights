const { execSync } = require('child_process');

console.log('🔍 Finding and clicking Comet Assistant...\n');

// Method 1: Try keyboard shortcut variations
const shortcuts = [
  { name: 'Cmd+A', keys: 'keystroke "a" using {command down}' },
  { name: 'Cmd+Shift+A', keys: 'keystroke "a" using {command down, shift down}' },
  { name: 'Cmd+/', keys: 'keystroke "/" using {command down}' },
];

for (const shortcut of shortcuts) {
  try {
    console.log(`Trying ${shortcut.name}...`);
    const script = `
      tell application "System Events"
        tell process "Comet"
          set frontmost to true
          delay 0.3
          ${shortcut.keys}
        end tell
      end tell
    `;
    execSync(`osascript -e '${script}'`);
    console.log(`✅ Sent ${shortcut.name}\n`);
    
    // Wait a bit and check if it worked
    execSync('sleep 1');
    
  } catch (error) {
    console.log(`❌ ${shortcut.name} failed\n`);
  }
}

// Method 2: Click in the area where Assistant button typically is
console.log('Method 2: Clicking Assistant button area...');
try {
  const script = `
    tell application "Comet"
      activate
    end tell
    
    tell application "System Events"
      tell process "Comet"
        set frontmost to true
        delay 0.5
        
        -- Get window position and size
        set windowPosition to position of window 1
        set windowSize to size of window 1
        set windowX to item 1 of windowPosition
        set windowY to item 2 of windowPosition  
        set windowWidth to item 1 of windowSize
        set windowHeight to item 2 of windowSize
        
        -- Click in top-right area (where Assistant button usually is)
        set clickX to windowX + windowWidth - 80
        set clickY to windowY + 66
        
        log "Window: " & windowX & "," & windowY & " Size: " & windowWidth & "x" & windowHeight
        log "Clicking: " & clickX & "," & clickY
        
      end tell
    end tell
    
    -- Use cliclick or xdotool to click the coordinates
    do shell script "cliclick c:" & clickX & "," & clickY
  `;
  
  execSync(`osascript -e '${script.replace(/'/g, "\\'")}'`, { encoding: 'utf8', stdio: 'pipe' });
  console.log('✅ Clicked Assistant button area\n');
  
} catch (error) {
  console.log('⚠️  cliclick not installed or failed\n');
  console.log('💡 Install cliclick: brew install cliclick\n');
}

// Method 3: Check UI elements
console.log('Method 3: Checking available UI elements...');
try {
  const script = `
    tell application "System Events"
      tell process "Comet"
        set frontmost to true
        return name of every button of toolbar 1 of window 1
      end tell
    end tell
  `;
  
  const result = execSync(`osascript -e '${script}'`, { encoding: 'utf8' });
  console.log('Available toolbar buttons:', result.trim());
  
} catch (error) {
  console.log('Could not enumerate UI elements');
}

console.log('\n📝 Summary:');
console.log('  Tried multiple methods to open Comet Assistant');
console.log('  Check your Comet window to see if Assistant panel appeared');
console.log('\n💡 If Assistant still not open:');
console.log('  1. Click the "Assistant" button in top-right of Comet manually');
console.log('  2. Or look for an Assistant icon/button in the Comet interface');
console.log('  3. Check Comet preferences for Assistant keyboard shortcut');

